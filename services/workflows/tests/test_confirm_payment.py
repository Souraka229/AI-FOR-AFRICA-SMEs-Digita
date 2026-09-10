from datetime import timedelta

import pytest
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowFailureError
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from afrosite_workflows.confirm_payment.activities import (
    TASK_QUEUE,
    append_paid_ledger,
    append_refund_ledger,
    notify_whatsapp_paid,
    record_audit,
    verify_payment,
)
from afrosite_workflows.confirm_payment.models import (
    ConfirmPaymentInput,
    ConfirmPaymentResult,
    confirm_workflow_id,
)
from afrosite_workflows.confirm_payment.ports import (
    InMemoryAudit,
    InMemoryLedger,
    InMemoryWhatsApp,
    ScriptedPaymentPort,
)
from afrosite_workflows.confirm_payment.runtime import Ports, bind_ports
from afrosite_workflows.confirm_payment.workflow import ConfirmPaymentWorkflow

ACTIVITIES = [
    record_audit,
    verify_payment,
    append_paid_ledger,
    append_refund_ledger,
    notify_whatsapp_paid,
]


def _payload(**overrides: object) -> ConfirmPaymentInput:
    base = ConfirmPaymentInput(
        tenant_id="ten_wax",
        order_id="ord_wax",
        provider_ref="gp_tx_wax",
        expected_amount_xof=24500,
        webhook_event_id="evt_1",
        event_type="payment.success",
        currency="XOF",
        channel="mtn_momo",
        environment="sandbox",
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


@pytest.fixture
def stores() -> Ports:
    ports = Ports(
        payment=ScriptedPaymentPort(sequence=[{"status": "succeeded", "amount_xof": 24500}]),
        ledger=InMemoryLedger(),
        whatsapp=InMemoryWhatsApp(),
        audit=InMemoryAudit(),
    )
    bind_ports(ports)
    return ports


async def _start(client: Client, payload: ConfirmPaymentInput):
    workflow_id = confirm_workflow_id(payload.provider_ref, payload.event_type)
    try:
        handle = await client.start_workflow(
            ConfirmPaymentWorkflow.run,
            payload,
            id=workflow_id,
            task_queue=TASK_QUEUE,
            execution_timeout=timedelta(seconds=30),
            result_type=ConfirmPaymentResult,
        )
    except WorkflowAlreadyStartedError:
        handle = client.get_workflow_handle(
            workflow_id,
            result_type=ConfirmPaymentResult,
        )
    return handle


async def _run(env: WorkflowEnvironment, payload: ConfirmPaymentInput):
    async with Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[ConfirmPaymentWorkflow],
        activities=ACTIVITIES,
    ):
        handle = await _start(env.client, payload)
        return await handle.result()


@pytest.mark.asyncio
async def test_success_verify_then_ledger_and_whatsapp(stores: Ports) -> None:
    async with await WorkflowEnvironment.start_time_skipping() as env:
        result = await _run(env, _payload())
    assert result.outcome == "paid"
    assert result.whatsapp_sent is True
    assert stores.ledger.entries[0]["direction"] == "credit"
    assert stores.ledger.entries[0]["amount_xof"] == 24500
    assert stores.whatsapp.messages[0]["provider_ref"] == "gp_tx_wax"
    assert any(event.action == "paid" for event in stores.audit.events)
    assert stores.payment.calls >= 1


@pytest.mark.asyncio
async def test_psp_failure_writes_no_ledger(stores: Ports) -> None:
    stores.payment.sequence = [{"status": "failed", "amount_xof": 24500}]
    async with await WorkflowEnvironment.start_time_skipping() as env:
        result = await _run(env, _payload(event_type="payment.failed"))
    assert result.outcome == "rejected"
    assert stores.ledger.entries == []
    assert stores.whatsapp.messages == []


@pytest.mark.asyncio
async def test_double_webhook_single_whatsapp(stores: Ports) -> None:
    payload = _payload()
    async with (
        await WorkflowEnvironment.start_time_skipping() as env,
        Worker(
            env.client,
            task_queue=TASK_QUEUE,
            workflows=[ConfirmPaymentWorkflow],
            activities=ACTIVITIES,
        ),
    ):
        first_handle = await _start(env.client, payload)
        second_handle = await _start(env.client, payload)
        first = await first_handle.result()
        second = await second_handle.result()
        desc = await first_handle.describe()
    assert first.outcome == "paid"
    assert second.outcome == "paid"
    assert first_handle.id == second_handle.id
    assert desc.status == WorkflowExecutionStatus.COMPLETED
    assert len(stores.whatsapp.messages) == 1
    assert len([row for row in stores.ledger.entries if row["direction"] == "credit"]) == 1


@pytest.mark.asyncio
async def test_late_webhook_retries_verify(stores: Ports) -> None:
    stores.payment.sequence = [
        {"status": "pending", "amount_xof": 24500},
        {"status": "pending", "amount_xof": 24500},
        {"status": "succeeded", "amount_xof": 24500},
    ]
    async with await WorkflowEnvironment.start_time_skipping() as env:
        result = await _run(env, _payload(webhook_event_id="evt_late"))
    assert result.outcome == "paid"
    assert stores.payment.calls >= 3
    assert stores.ledger.entries[0]["amount_xof"] == 24500


@pytest.mark.asyncio
async def test_refund_appends_debit_not_update(stores: Ports) -> None:
    paid = _payload()
    refund = _payload(
        event_type="payment.refunded",
        webhook_event_id="evt_refund",
        refund_amount_xof=24500,
        reason="annulation cliente",
    )
    async with await WorkflowEnvironment.start_time_skipping() as env:
        stores.payment.sequence = [{"status": "succeeded", "amount_xof": 24500}]
        await _run(env, paid)
        stores.payment.sequence = [{"status": "refunded", "amount_xof": 24500}]
        stores.payment.calls = 0
        refunded = await _run(env, refund)
    assert refunded.outcome == "refunded"
    directions = [row["direction"] for row in stores.ledger.entries]
    assert directions == ["credit", "debit"]
    assert all("UPDATE" not in str(row) for row in stores.ledger.entries)


@pytest.mark.asyncio
async def test_live_environment_is_rejected(stores: Ports) -> None:
    async with await WorkflowEnvironment.start_time_skipping() as env:
        with pytest.raises(WorkflowFailureError):
            await _run(env, _payload(environment="live"))
    assert stores.ledger.entries == []
