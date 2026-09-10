from dataclasses import dataclass, field


def provision_workflow_id(tenant_slug: str) -> str:
    return f"provision-tenant:{tenant_slug}"


@dataclass
class CatalogLine:
    sku: str
    name: str
    price_xof: int


@dataclass
class ProvisionTenantInput:
    tenant_slug: str
    tenant_name: str
    vertical: str
    city: str
    neighborhood: str
    human_approved: bool
    deployment_target: str = "preview"
    country: str = "BJ"
    currency: str = "XOF"
    environment: str = "sandbox"
    channel: str = "mtn_momo"
    catalog: list[CatalogLine] = field(default_factory=list)


@dataclass
class TenantSnapshot:
    tenant_id: str
    slug: str
    duplicated: bool
    status: str


@dataclass
class PreviewSnapshot:
    href: str
    environment: str


@dataclass
class ProvisionTenantResult:
    outcome: str
    tenant_slug: str
    preview_href: str | None = None
    payment_mode: str | None = None
    catalog_count: int = 0
    audit_count: int = 0
    reason: str = ""
