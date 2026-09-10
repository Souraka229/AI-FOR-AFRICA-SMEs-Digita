from temporalio import activity
from temporalio.exceptions import ApplicationError

from afrosite_workflows.confirm_payment.models import (
    ConfirmPaymentInput,
    LedgerSnapshot,
    VerifySnapshot,
)
from afrosite_workflows.confirm_payment.ports import AuditEvent, now_iso
from afrosite_workflows.confirm_payment.runtime import require_ports

TASK_QUEUE = "afrosite-payments"


def _guard_sandbox(payload: ConfirmPaymentInput) -> None:
    if payload.environment.lower() == "live":
        raise ApplicationError("Paiement live refusé avant audit + gate 6.", non_retryable=True)
    if payload.currency != "XOF":
        raise ApplicationError("MVP Bénin : XOF uniquement.", non_retryable=True)
    if payload.expected_amount_xof <= 0:
        raise ApplicationError("Montant serveur invalide.", non_retryable=True)


@activity.defn
async def record_audit(payload: ConfirmPaymentInput, action: str, result: str) -> int:
    ports = require_ports()
    return await ports.audit.record(
        AuditEvent(
            at=now_iso(),
            agent="payment",
            action=action,
            result=result,
            tool="confirm_payment",
        )
    )


@activity.defn
async def verify_payment(payload: ConfirmPaymentInput) -> VerifySnapshot:
    _guard_sandbox(payload)
    ports = require_ports()
    raw = await ports.payment.verify(
        payload.provider_ref,
        payload.expected_amount_xof,
        payload.currency,
    )
    snapshot = VerifySnapshot(
        provider_ref=str(raw.get("provider_ref", payload.provider_ref)),
        status=str(raw.get("status", "pending")),
        amount_xof=int(raw.get("amount_xof", 0)),
        currency=str(raw.get("currency", "")),
        verified_server=bool(raw.get("verified_server", False)),
    )
    if not snapshot.verified_server:
        raise ApplicationError(
            "verify() serveur obligatoire avant écriture payé.",
            non_retryable=True,
        )
    if snapshot.currency != "XOF":
        raise ApplicationError("Devise PSP hors XOF.", non_retryable=True)
    if snapshot.status == "pending":
        raise ApplicationError("PSP encore pending — nouvel essai verify().")
    if (
        snapshot.status == "succeeded"
        and snapshot.amount_xof != payload.expected_amount_xof
    ):
        raise ApplicationError("Montant PSP ≠ montant commande serveur.", non_retryable=True)
    return snapshot


@activity.defn
async def append_paid_ledger(payload: ConfirmPaymentInput) -> LedgerSnapshot:
    _guard_sandbox(payload)
    ports = require_ports()
    row = await ports.ledger.append(
        tenant_id=payload.tenant_id,
        order_id=payload.order_id,
        provider_ref=payload.provider_ref,
        direction="credit",
        amount_xof=payload.expected_amount_xof,
        channel=payload.channel,
        note="payé après verify() serveur",
        idempotency_key=f"paid:{payload.provider_ref}",
    )
    return LedgerSnapshot(
        entry_id=str(row["entry_id"]),
        direction=str(row["direction"]),
        amount_xof=int(row["amount_xof"]),
        duplicated=bool(row.get("duplicated")),
    )


@activity.defn
async def append_refund_ledger(payload: ConfirmPaymentInput) -> LedgerSnapshot:
    _guard_sandbox(payload)
    amount = payload.refund_amount_xof or payload.expected_amount_xof
    if amount <= 0 or amount > payload.expected_amount_xof:
        raise ApplicationError("Remboursement hors reste.", non_retryable=True)
    ports = require_ports()
    row = await ports.ledger.append(
        tenant_id=payload.tenant_id,
        order_id=payload.order_id,
        provider_ref=payload.provider_ref,
        direction="debit",
        amount_xof=amount,
        channel=payload.channel,
        note=payload.reason or "remboursement sandbox",
        idempotency_key=f"refund:{payload.provider_ref}:{amount}",
    )
    return LedgerSnapshot(
        entry_id=str(row["entry_id"]),
        direction=str(row["direction"]),
        amount_xof=int(row["amount_xof"]),
        duplicated=bool(row.get("duplicated")),
    )


@activity.defn
async def notify_whatsapp_paid(payload: ConfirmPaymentInput) -> bool:
    ports = require_ports()
    return await ports.whatsapp.notify_paid(
        payload.tenant_id,
        payload.provider_ref,
        payload.expected_amount_xof,
    )
