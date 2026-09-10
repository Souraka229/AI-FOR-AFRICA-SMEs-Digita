from temporalio import activity
from temporalio.exceptions import ApplicationError

from afrosite_workflows.provision_tenant.models import (
    PreviewSnapshot,
    ProvisionTenantInput,
    TenantSnapshot,
)
from afrosite_workflows.provision_tenant.ports import AuditEvent, now_iso
from afrosite_workflows.provision_tenant.runtime import require_ports

TASK_QUEUE = "afrosite-tenants"


def _guard(payload: ProvisionTenantInput) -> None:
    if payload.environment.lower() == "live":
        raise ApplicationError("Provisioning live refusé avant gate 6.", non_retryable=True)
    if payload.country != "BJ" or payload.currency != "XOF":
        raise ApplicationError("MVP Bénin : BJ / XOF uniquement.", non_retryable=True)
    if payload.deployment_target == "production":
        raise ApplicationError("Cible production interdite (gate 6).", non_retryable=True)
    if payload.vertical not in {"commerce", "restaurant", "services"}:
        raise ApplicationError("Vertical hors périmètre MVP.", non_retryable=True)
    if not payload.human_approved:
        raise ApplicationError("Accord humain explicite requis.", non_retryable=True)


@activity.defn
async def record_audit(payload: ProvisionTenantInput, action: str, result: str) -> int:
    ports = require_ports()
    return await ports.audit.record(
        AuditEvent(
            at=now_iso(),
            agent="provisioning",
            action=action,
            result=result,
            tool="provision_tenant",
        )
    )


@activity.defn
async def assert_approved(payload: ProvisionTenantInput) -> None:
    _guard(payload)


@activity.defn
async def create_tenant(payload: ProvisionTenantInput) -> TenantSnapshot:
    _guard(payload)
    ports = require_ports()
    row = await ports.tenants.upsert(
        payload.tenant_slug,
        payload.tenant_name,
        payload.vertical,
        payload.city,
        payload.neighborhood,
    )
    return TenantSnapshot(
        tenant_id=str(row["tenant_id"]),
        slug=str(row["slug"]),
        duplicated=bool(row.get("duplicated")),
        status=str(row.get("status", "provisioning")),
    )


@activity.defn
async def seed_catalog(payload: ProvisionTenantInput) -> int:
    _guard(payload)
    ports = require_ports()
    lines = [
        {"sku": line.sku, "name": line.name, "price_xof": line.price_xof}
        for line in payload.catalog
    ]
    return await ports.catalog.seed(payload.tenant_slug, lines)


@activity.defn
async def enable_sandbox_payments(payload: ProvisionTenantInput) -> str:
    _guard(payload)
    ports = require_ports()
    return await ports.payments.enable_sandbox(payload.tenant_slug, payload.channel)


@activity.defn
async def allocate_preview(payload: ProvisionTenantInput) -> PreviewSnapshot:
    _guard(payload)
    ports = require_ports()
    row = await ports.preview.allocate(payload.tenant_slug, payload.deployment_target)
    return PreviewSnapshot(href=row["href"], environment=row["environment"])


@activity.defn
async def compensate_failed_preview(payload: ProvisionTenantInput) -> None:
    """Compensation : tenant sandbox marqué failed, aucun paiement live."""
    ports = require_ports()
    await ports.tenants.mark_status(payload.tenant_slug, "failed")
    await ports.audit.record(
        AuditEvent(
            at=now_iso(),
            agent="provisioning",
            action="compensate",
            result="preview échouée — tenant sandbox failed, pas de prod",
        )
    )
