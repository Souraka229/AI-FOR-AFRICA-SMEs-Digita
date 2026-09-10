from dataclasses import dataclass


def confirm_workflow_id(provider_ref: str, event_type: str = "payment.success") -> str:
    """Idempotence Temporal : un rejeu webhook reprend le même workflow."""
    if event_type == "payment.refunded":
        return f"refund-payment:{provider_ref}"
    return f"confirm-payment:{provider_ref}"


@dataclass
class ConfirmPaymentInput:
    tenant_id: str
    order_id: str
    provider_ref: str
    expected_amount_xof: int
    webhook_event_id: str
    event_type: str
    currency: str = "XOF"
    channel: str = "mtn_momo"
    environment: str = "sandbox"
    refund_amount_xof: int = 0
    reason: str = ""


@dataclass
class VerifySnapshot:
    provider_ref: str
    status: str
    amount_xof: int
    currency: str
    verified_server: bool


@dataclass
class LedgerSnapshot:
    entry_id: str
    direction: str
    amount_xof: int
    duplicated: bool


@dataclass
class ConfirmPaymentResult:
    outcome: str
    provider_ref: str
    ledger_entry_id: str | None = None
    whatsapp_sent: bool = False
    audit_count: int = 0
    reason: str = ""
