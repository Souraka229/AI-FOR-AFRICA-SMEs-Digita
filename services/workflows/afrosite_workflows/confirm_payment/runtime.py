from afrosite_workflows.confirm_payment.ports import (
    AuditPort,
    LedgerPort,
    PaymentPort,
    WhatsAppPort,
)

_bound: "Ports | None" = None


class Ports:
    def __init__(
        self,
        payment: PaymentPort,
        ledger: LedgerPort,
        whatsapp: WhatsAppPort,
        audit: AuditPort,
    ) -> None:
        self.payment = payment
        self.ledger = ledger
        self.whatsapp = whatsapp
        self.audit = audit


def bind_ports(ports: Ports) -> None:
    global _bound
    _bound = ports


def require_ports() -> Ports:
    if _bound is None:
        raise RuntimeError("Ports ConfirmPayment non liés (worker ou test).")
    return _bound
