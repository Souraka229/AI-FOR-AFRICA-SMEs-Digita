from datetime import timedelta

import pytest
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowFailureError
from temporalio.common import WorkflowIDReusePolicy
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from afrosite_workflows.provision_tenant.activities import (
    TASK_QUEUE,
    allocate_preview,
    assert_approved,
    compensate_failed_preview,
    create_tenant,
    enable_sandbox_payments,
    record_audit,
    seed_catalog,
)
from afrosite_workflows.provision_tenant.models import (
    CatalogLine,
    ProvisionTenantInput,
    ProvisionTenantResult,
    provision_workflow_id,
)
from afrosite_workflows.provision_tenant.ports import (
    InMemoryAudit,
    InMemoryCatalog,
    InMemoryPaymentSetup,
    InMemoryPreview,
    InMemoryTenants,
)
from afrosite_workflows.provision_tenant.runtime import Ports, bind_ports
from afrosite_workflows.provision_tenant.workflow import ProvisionTenantWorkflow

ACTIVITIES = [
    record_audit,
    assert_approved,
    create_tenant,
    seed_catalog,
    enable_sandbox_payments,
    allocate_preview,
    compensate_failed_preview,
]


def _payload(**overrides: object) -> ProvisionTenantInput:
    base = ProvisionTenantInput(
        tenant_slug="cadjehoun-wax-demo",
        tenant_name="Wax Cadjehoun Demo",
        vertical="commerce",
        city="Cotonou",
        neighborhood="Cadjehoun",
        human_approved=True,
        deployment_target="preview",
        country="BJ",
        currency="XOF",
        environment="sandbox",
        catalog=[
            CatalogLine(sku="wax-pagne", name="Pagne wax", price_xof=12500),
            CatalogLine(sku="wax-coupon", name="Coupon 3 yards", price_xof=8000),
        ],
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


@pytest.fixture
def stores() -> Ports:
    ports = Ports(
        tenants=InMemoryTenants(),
        catalog=InMemoryCatalog(),
        payments=InMemoryPaymentSetup(),
        preview=InMemoryPreview(),
        audit=InMemoryAudit(),
    )
    bind_ports(ports)
    return ports


async def _start(client: Client, payload: ProvisionTenantInput):
    workflow_id = provision_workflow_id(payload.tenant_slug)
    try:
        return await client.start_workflow(
            ProvisionTenantWorkflow.run,
            payload,
            id=workflow_id,
            task_queue=TASK_QUEUE,
            execution_timeout=timedelta(seconds=30),
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            result_type=ProvisionTenantResult,
        )
    except WorkflowAlreadyStartedError:
        return client.get_workflow_handle(workflow_id, result_type=ProvisionTenantResult)


async def _run(env: WorkflowEnvironment, payload: ProvisionTenantInput):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ProvisionTenantWorkflow],
        activities=ACTIVITIES,
    ):
        handle = await _start(env.client, payload)
        return await handle.result()


@pytest.mark.asyncio
async def test_ready_sandbox_preview(stores: Ports) -> None:
    async with await WorkflowEnvironment.start_time_skipping() as env:
        result = await _run(env, _payload())
    assert result.outcome == "ready"
    assert result.preview_href == "/t/cadjehoun-wax-demo"
    assert result.payment_mode == "sandbox"
    assert result.catalog_count == 2
    assert stores.tenants.rows["cadjehoun-wax-demo"]["country"] == "BJ"
    assert stores.payments.modes["cadjehoun-wax-demo"] == "sandbox"


@pytest.mark.asyncio
async def test_rejects_without_human_approval(stores: Ports) -> None:
    async with await WorkflowEnvironment.start_time_skipping() as env:
        with pytest.raises(WorkflowFailureError):
            await _run(env, _payload(human_approved=False))
    assert stores.tenants.rows == {}
    assert stores.preview.allocations == []


@pytest.mark.asyncio
async def test_rejects_production_target(stores: Ports) -> None:
    async with await WorkflowEnvironment.start_time_skipping() as env:
        with pytest.raises(WorkflowFailureError):
            await _run(env, _payload(deployment_target="production"))
    assert stores.tenants.rows == {}


@pytest.mark.asyncio
async def test_duplicate_start_is_idempotent(stores: Ports) -> None:
    payload = _payload()
    async with (
        await WorkflowEnvironment.start_time_skipping() as env,
        Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[ProvisionTenantWorkflow],
            activities=ACTIVITIES,
        ),
    ):
        first = await (await _start(env.client, payload)).result()
        second_handle = await _start(env.client, payload)
        second = await second_handle.result()
        desc = await second_handle.describe()
    assert first.outcome == second.outcome == "ready"
    assert desc.status == WorkflowExecutionStatus.COMPLETED
    assert len(stores.tenants.rows) == 1
    assert len(stores.preview.allocations) == 1


@pytest.mark.asyncio
async def test_preview_failure_compensates(stores: Ports) -> None:
    stores.preview.fail = True
    async with await WorkflowEnvironment.start_time_skipping() as env:
        result = await _run(env, _payload())
    assert result.outcome == "compensated"
    assert result.preview_href is None
    assert stores.tenants.rows["cadjehoun-wax-demo"]["status"] == "failed"
    assert stores.payments.modes["cadjehoun-wax-demo"] == "sandbox"
    assert any(event.action == "compensate" for event in stores.audit.events)
