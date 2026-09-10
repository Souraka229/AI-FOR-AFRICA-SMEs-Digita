import asyncio
import logging
import os

from temporalio.client import Client
from temporalio.worker import Worker

from afrosite_workflows.confirm_payment.activities import (
    TASK_QUEUE,
    append_paid_ledger,
    append_refund_ledger,
    notify_whatsapp_paid,
    record_audit,
    verify_payment,
)
from afrosite_workflows.confirm_payment.ports import (
    InMemoryAudit,
    InMemoryLedger,
    InMemoryWhatsApp,
    ScriptedPaymentPort,
)
from afrosite_workflows.confirm_payment.runtime import Ports, bind_ports
from afrosite_workflows.confirm_payment.workflow import ConfirmPaymentWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("afrosite_workflows")


def _sandbox_ports() -> Ports:
    """Ports locaux : pas de clé PSP. Le worker prod injecte Genius Pay sandbox."""
    return Ports(
        payment=ScriptedPaymentPort(sequence=[{"status": "pending"}]),
        ledger=InMemoryLedger(),
        whatsapp=InMemoryWhatsApp(),
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
        workflows=[ConfirmPaymentWorkflow],
        activities=[
            record_audit,
            verify_payment,
            append_paid_ledger,
            append_refund_ledger,
            notify_whatsapp_paid,
        ],
    )
    logger.info("Worker ConfirmPayment sur %s / %s", target, TASK_QUEUE)
    await worker.run()


async def main() -> None:
    logger.info("Afrosite Temporal Worker — ConfirmPayment (sandbox).")
    await run_worker()


if __name__ == "__main__":
    asyncio.run(main())
