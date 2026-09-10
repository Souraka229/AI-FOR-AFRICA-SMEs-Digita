import asyncio
import logging
import os

from temporalio.client import Client
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
from afrosite_workflows.provision_tenant.ports import (
    InMemoryAudit,
    InMemoryCatalog,
    InMemoryPaymentSetup,
    InMemoryPreview,
    InMemoryTenants,
)
from afrosite_workflows.provision_tenant.runtime import Ports, bind_ports
from afrosite_workflows.provision_tenant.workflow import ProvisionTenantWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("afrosite_workflows")


def _sandbox_ports() -> Ports:
    return Ports(
        tenants=InMemoryTenants(),
        catalog=InMemoryCatalog(),
        payments=InMemoryPaymentSetup(),
        preview=InMemoryPreview(),
        audit=InMemoryAudit(),
    )


async def run_worker() -> None:
    target = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.environ.get("TEMPORAL_NAMESPACE", "default")
    bind_ports(_sandbox_ports())
    client = await Client.connect(target, namespace=namespace)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ProvisionTenantWorkflow],
        activities=[
            record_audit,
            assert_approved,
            create_tenant,
            seed_catalog,
            enable_sandbox_payments,
            allocate_preview,
            compensate_failed_preview,
        ],
    )
    logger.info("Worker ProvisionTenant sur %s / %s", target, TASK_QUEUE)
    await worker.run()


async def main() -> None:
    logger.info("Afrosite Temporal Worker — ProvisionTenant (sandbox).")
    await run_worker()


if __name__ == "__main__":
    asyncio.run(main())
