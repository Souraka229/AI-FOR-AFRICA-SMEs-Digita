"""Genius Pay sandbox adapter behind PaymentProvider.

Provisional paths/fields per ADR 0001 — override via GENIUSPAY_* env vars until
official vendor docs are recorded in the ADR.
"""

from __future__ import annotations

import hashlib
import hmac
import json
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
    WebhookEvent,
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

    async def create_transaction(
        self, request: CreateTransactionRequest
    ) -> CreateTransactionResult:
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

    def _verify_signature(self, payload: bytes, signature: str) -> None:
        secret = self._settings.geniuspay_webhook_secret
        if not secret:
            raise GeniusPayError("GENIUSPAY_WEBHOOK_SECRET is required for webhooks")
        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature.strip().lower()):
            raise GeniusPayError("Invalid webhook signature")

    async def handle_webhook(self, payload: bytes, signature: str) -> WebhookEvent:
        self._verify_signature(payload, signature)
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GeniusPayError("Invalid webhook JSON") from exc
        if not isinstance(data, dict):
            raise GeniusPayError("Webhook payload must be an object")
        event_id = str(data.get("event_id") or data.get("id") or "")
        provider_ref = str(data.get("provider_ref") or "")
        if not event_id or not provider_ref:
            raise GeniusPayError("Webhook missing event_id or provider_ref")
        amount = data.get("amount")
        currency_raw = data.get("currency")
        return WebhookEvent(
            event_id=event_id,
            provider_ref=provider_ref,
            status=_map_status(str(data.get("status", "pending"))),
            amount_xof=Decimal(str(amount)) if amount is not None else None,
            currency=Currency(str(currency_raw)) if currency_raw else None,
            raw=dict(data),
        )
