from afrosite_workflows.provision_tenant.ports import (
    AuditPort,
    CatalogPort,
    PaymentSetupPort,
    PreviewPort,
    TenantPort,
)

_bound: "Ports | None" = None


class Ports:
    def __init__(
        self,
        tenants: TenantPort,
        catalog: CatalogPort,
        payments: PaymentSetupPort,
        preview: PreviewPort,
        audit: AuditPort,
    ) -> None:
        self.tenants = tenants
        self.catalog = catalog
        self.payments = payments
        self.preview = preview
        self.audit = audit


def bind_ports(ports: Ports) -> None:
    global _bound
    _bound = ports


def require_ports() -> Ports:
    if _bound is None:
        raise RuntimeError("Ports ProvisionTenant non liés (worker ou test).")
    return _bound
