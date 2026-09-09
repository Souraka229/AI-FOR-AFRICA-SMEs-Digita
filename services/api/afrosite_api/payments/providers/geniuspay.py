"""Genius Pay sandbox adapter behind PaymentProvider.

Endpoint paths and JSON field names are driven by environment configuration.
They must be remapped to the official Genius Pay docs once ADR 0001 / vendor
docs are confirmed — do not treat the default path strings as vendor gospel.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from afrosite_api.common.settings import Settings
from afrosite_api.payments.types import (
    CreateTransactionRequest,
    CreateTransactionResult,
    Currency,
    PaymentStatus,
    VerifyTransactionRequest,
    VerifyTransactionResult,
)


class GeniusPayError(RuntimeError):
    """Raised when Genius Pay sandbox returns an unexpected response."""


def _map_status(value: str) -> PaymentStatus:
    normalized = value.strip().lower()
    mapping = {
        "pending": PaymentStatus.PENDING,
        "requires_action": PaymentStatus.REQUIRES_ACTION,
        "redirect": PaymentStatus.REQUIRES_ACTION,
        "succeeded": PaymentStatus.SUCCEEDED,
        "success": PaymentStatus.SUCCEEDED,
        "paid": PaymentStatus.SUCCEEDED,
        "failed": PaymentStatus.FAILED,
        "cancelled": PaymentStatus.CANCELLED,
        "canceled": PaymentStatus.CANCELLED,
    }
    if normalized not in mapping:
        raise GeniusPayError(f"Unknown payment status from provider: {value}")
    return mapping[normalized]


class GeniusPayProvider:
    """Sandbox PaymentProvider implementation using httpx + env-configured base URL."""

    name = "geniuspay"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.geniuspay_base_url:
            raise ValueError("GENIUSPAY_BASE_URL is required for GeniusPayProvider")
        if not settings.geniuspay_api_key:
            raise ValueError("GENIUSPAY_API_KEY is required for GeniusPayProvider")
        self._settings = settings
        self._client = client
        self._owns_client = client is None
        self._idempotency_cache: dict[str, CreateTransactionResult] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._settings.geniuspay_base_url.rstrip("/"),
                timeout=self._settings.geniuspay_timeout_seconds,
                headers={
                    "Authorization": f"Bearer {self._settings.geniuspay_api_key}",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def create_transaction(self, request: CreateTransactionRequest) -> CreateTransactionResult:
        if request.currency != Currency.XOF:
            raise GeniusPayError("Only XOF is supported")
        cached = self._idempotency_cache.get(request.idempotency_key)
        if cached is not None:
            return cached

        client = await self._get_client()
        payload: dict[str, Any] = {
            "order_id": request.order_id,
            "amount": str(request.amount_xof),
            "currency": request.currency.value,
            "customer_phone": request.customer_phone,
            "description": request.description,
            "return_url": request.return_url,
        }
        response = await client.post(
            self._settings.geniuspay_create_path,
            json=payload,
            headers={"Idempotency-Key": request.idempotency_key},
        )
        if response.status_code >= 400:
            raise GeniusPayError(f"create_transaction failed: HTTP {response.status_code}")
        data = response.json()
        result = CreateTransactionResult(
            provider_ref=str(data["provider_ref"]),
            status=_map_status(str(data.get("status", "requires_action"))),
            checkout_url=data.get("checkout_url"),
            raw=dict(data),
        )
        self._idempotency_cache[request.idempotency_key] = result
        return result

    async def verify(self, request: VerifyTransactionRequest) -> VerifyTransactionResult:
        if request.expected_currency != Currency.XOF:
            raise GeniusPayError("Only XOF is supported")
        client = await self._get_client()
        path = self._settings.geniuspay_verify_path.format(provider_ref=request.provider_ref)
        response = await client.get(path)
        if response.status_code >= 400:
            raise GeniusPayError(f"verify failed: HTTP {response.status_code}")
        data = response.json()
        amount = Decimal(str(data["amount"]))
        currency = Currency(str(data.get("currency", "XOF")))
        if amount != request.expected_amount_xof or currency != request.expected_currency:
            raise GeniusPayError("Amount/currency mismatch on verify")
        return VerifyTransactionResult(
            provider_ref=str(data.get("provider_ref", request.provider_ref)),
            status=_map_status(str(data["status"])),
            amount_xof=amount,
            currency=currency,
            raw=dict(data),
        )
