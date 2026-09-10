from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from afrosite_workflows.confirm_payment.models import (
    ConfirmPaymentInput,
    ConfirmPaymentResult,
    LedgerSnapshot,
    VerifySnapshot,
)

with workflow.unsafe.imports_passed_through():
    from afrosite_workflows.confirm_payment import activities as acts

_VERIFY_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_attempts=5,
    maximum_interval=timedelta(seconds=20),
)

_FAST = timedelta(seconds=15)


@workflow.defn
class ConfirmPaymentWorkflow:
    """Orchestration seule : verify serveur, puis ledger append-only, puis WhatsApp."""

    @workflow.run
    async def run(self, payload: ConfirmPaymentInput) -> ConfirmPaymentResult:
        await workflow.execute_activity(
            acts.record_audit,
            args=[payload, "start", payload.event_type],
            start_to_close_timeout=_FAST,
        )

        snapshot: VerifySnapshot = await workflow.execute_activity(
            acts.verify_payment,
            payload,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_VERIFY_RETRY,
        )

        if payload.event_type == "payment.refunded" or snapshot.status == "refunded":
            ledger: LedgerSnapshot = await workflow.execute_activity(
                acts.append_refund_ledger,
                payload,
                start_to_close_timeout=_FAST,
            )
            audit_count = await workflow.execute_activity(
                acts.record_audit,
                args=[payload, "refund", f"debit {ledger.amount_xof} XOF"],
                start_to_close_timeout=_FAST,
            )
            return ConfirmPaymentResult(
                outcome="refunded",
                provider_ref=payload.provider_ref,
                ledger_entry_id=ledger.entry_id,
                audit_count=audit_count,
            )

        if snapshot.status != "succeeded":
            audit_count = await workflow.execute_activity(
                acts.record_audit,
                args=[payload, "reject", snapshot.status],
                start_to_close_timeout=_FAST,
            )
            return ConfirmPaymentResult(
                outcome="rejected",
                provider_ref=payload.provider_ref,
                audit_count=audit_count,
                reason=snapshot.status,
            )

        ledger = await workflow.execute_activity(
            acts.append_paid_ledger,
            payload,
            start_to_close_timeout=_FAST,
        )
        sent = await workflow.execute_activity(
            acts.notify_whatsapp_paid,
            payload,
            start_to_close_timeout=_FAST,
        )
        audit_count = await workflow.execute_activity(
            acts.record_audit,
            args=[payload, "paid", f"credit {ledger.amount_xof} XOF"],
            start_to_close_timeout=_FAST,
        )
        return ConfirmPaymentResult(
            outcome="paid",
            provider_ref=payload.provider_ref,
            ledger_entry_id=ledger.entry_id,
            whatsapp_sent=sent,
            audit_count=audit_count,
        )
