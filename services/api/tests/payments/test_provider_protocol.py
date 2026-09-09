"""PaymentProvider protocol smoke tests."""

from decimal import Decimal

import pytest

from afrosite_api.payments.provider import PaymentProvider
from afrosite_api.payments.types import (
    CreateTransactionRequest,
    CreateTransactionResult,
    PaymentStatus,
    VerifyTransactionRequest,
    VerifyTransactionResult,
    Currency,
)


class _StubProvider:
    name = "stub"

    async def create_transaction(self, request: CreateTransactionRequest) -> CreateTransactionResult:
        return CreateTransactionResult(
            provider_ref=f"stub-{request.idempotency_key}",
            status=PaymentStatus.REQUIRES_ACTION,
            checkout_url="https://example.test/checkout",
        )

    async def verify(self, request: VerifyTransactionRequest) -> VerifyTransactionResult:
        return VerifyTransactionResult(
            provider_ref=request.provider_ref,
            status=PaymentStatus.SUCCEEDED,
            amount_xof=request.expected_amount_xof,
            currency=request.expected_currency,
        )


@pytest.mark.asyncio
async def test_stub_satisfies_protocol() -> None:
    provider: PaymentProvider = _StubProvider()
    created = await provider.create_transaction(
        CreateTransactionRequest(
            order_id="ord-1",
            amount_xof=Decimal("1500"),
            idempotency_key="idem-key-001",
        )
    )
    assert created.status == PaymentStatus.REQUIRES_ACTION
    verified = await provider.verify(
        VerifyTransactionRequest(
            provider_ref=created.provider_ref,
            expected_amount_xof=Decimal("1500"),
            expected_currency=Currency.XOF,
        )
    )
    assert verified.status == PaymentStatus.SUCCEEDED
