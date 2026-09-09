"""GeniusPayProvider sandbox tests with mocked HTTP (no live network)."""

from decimal import Decimal

import httpx
import pytest

from afrosite_api.common.settings import Settings
from afrosite_api.payments.providers.geniuspay import GeniusPayError, GeniusPayProvider
from afrosite_api.payments.types import (
    CreateTransactionRequest,
    Currency,
    PaymentStatus,
    VerifyTransactionRequest,
)


def _settings() -> Settings:
    return Settings(
        geniuspay_base_url="https://sandbox.geniuspay.test",
        geniuspay_api_key="test-key",
        geniuspay_create_path="/v1/transactions",
        geniuspay_verify_path="/v1/transactions/{provider_ref}",
    )


@pytest.mark.asyncio
async def test_create_and_verify_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/transactions":
            assert request.headers.get("Idempotency-Key") == "idem-abc-001"
            return httpx.Response(
                200,
                json={
                    "provider_ref": "gp_tx_1",
                    "status": "requires_action",
                    "checkout_url": "https://sandbox.geniuspay.test/checkout/gp_tx_1",
                },
            )
        if request.method == "GET" and request.url.path == "/v1/transactions/gp_tx_1":
            return httpx.Response(
                200,
                json={
                    "provider_ref": "gp_tx_1",
                    "status": "succeeded",
                    "amount": "2500",
                    "currency": "XOF",
                },
            )
        return httpx.Response(404, json={"error": "not found"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://sandbox.geniuspay.test",
        headers={"Authorization": "Bearer test-key"},
    ) as client:
        provider = GeniusPayProvider(_settings(), client=client)
        created = await provider.create_transaction(
            CreateTransactionRequest(
                order_id="ord-42",
                amount_xof=Decimal("2500"),
                idempotency_key="idem-abc-001",
            )
        )
        assert created.provider_ref == "gp_tx_1"
        assert created.status == PaymentStatus.REQUIRES_ACTION
        # Idempotent replay
        again = await provider.create_transaction(
            CreateTransactionRequest(
                order_id="ord-42",
                amount_xof=Decimal("2500"),
                idempotency_key="idem-abc-001",
            )
        )
        assert again.provider_ref == created.provider_ref
        verified = await provider.verify(
            VerifyTransactionRequest(
                provider_ref="gp_tx_1",
                expected_amount_xof=Decimal("2500"),
                expected_currency=Currency.XOF,
            )
        )
        assert verified.status == PaymentStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_verify_amount_mismatch_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "provider_ref": "gp_tx_2",
                "status": "succeeded",
                "amount": "999",
                "currency": "XOF",
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://sandbox.geniuspay.test",
        headers={"Authorization": "Bearer test-key"},
    ) as client:
        provider = GeniusPayProvider(_settings(), client=client)
        with pytest.raises(GeniusPayError):
            await provider.verify(
                VerifyTransactionRequest(
                    provider_ref="gp_tx_2",
                    expected_amount_xof=Decimal("2500"),
                    expected_currency=Currency.XOF,
                )
            )
