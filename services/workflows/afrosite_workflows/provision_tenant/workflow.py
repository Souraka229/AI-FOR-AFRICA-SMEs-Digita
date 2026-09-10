from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

from afrosite_workflows.provision_tenant.models import (
    PreviewSnapshot,
    ProvisionTenantInput,
    ProvisionTenantResult,
)

with workflow.unsafe.imports_passed_through():
    from afrosite_workflows.provision_tenant import activities as acts

_FAST = timedelta(seconds=15)
_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_attempts=3,
    maximum_interval=timedelta(seconds=10),
)


@workflow.defn
class ProvisionTenantWorkflow:
    """Orchestration : accord humain, tenant sandbox, catalogue, preview."""

    @workflow.run
    async def run(self, payload: ProvisionTenantInput) -> ProvisionTenantResult:
        await workflow.execute_activity(
            acts.record_audit,
            args=[payload, "start", payload.tenant_slug],
            start_to_close_timeout=_FAST,
        )
        await workflow.execute_activity(
            acts.assert_approved,
            payload,
            start_to_close_timeout=_FAST,
        )
        await workflow.execute_activity(
            acts.create_tenant,
            payload,
            start_to_close_timeout=_FAST,
        )
        catalog_count = await workflow.execute_activity(
            acts.seed_catalog,
            payload,
            start_to_close_timeout=_FAST,
        )
        payment_mode = await workflow.execute_activity(
            acts.enable_sandbox_payments,
            payload,
            start_to_close_timeout=_FAST,
        )
        try:
            preview: PreviewSnapshot = await workflow.execute_activity(
                acts.allocate_preview,
                payload,
                start_to_close_timeout=_FAST,
                retry_policy=_RETRY,
            )
        except ActivityError:
            await workflow.execute_activity(
                acts.compensate_failed_preview,
                payload,
                start_to_close_timeout=_FAST,
            )
            audit_count = await workflow.execute_activity(
                acts.record_audit,
                args=[payload, "failed", "preview"],
                start_to_close_timeout=_FAST,
            )
            return ProvisionTenantResult(
                outcome="compensated",
                tenant_slug=payload.tenant_slug,
                payment_mode=payment_mode,
                catalog_count=catalog_count,
                audit_count=audit_count,
                reason="preview_failed",
            )

        audit_count = await workflow.execute_activity(
            acts.record_audit,
            args=[payload, "ready", preview.href],
            start_to_close_timeout=_FAST,
        )
        return ProvisionTenantResult(
            outcome="ready",
            tenant_slug=payload.tenant_slug,
            preview_href=preview.href,
            payment_mode=payment_mode,
            catalog_count=catalog_count,
            audit_count=audit_count,
        )
