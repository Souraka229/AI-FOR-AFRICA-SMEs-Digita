"""Contrat PaymentProvider — playbook §10.2. Ne pas modifier sans ADR."""

from __future__ import annotations

from typing import Literal, Protocol


class PaymentOrder(dict):
    """tenant_slug, amount_xof, channel, idem_key, customer_country=BJ."""


class PaymentProvider(Protocol):
    id: Literal["geniuspay", "demo"]

    def create_transaction(self, order: PaymentOrder) -> dict: ...
    def verify(self, reference: str) -> dict | None: ...
    def handle_webhook(self, raw_body: str, signature: str, timestamp: str) -> dict | None: ...
    def refund(self, reference: str, amount_xof: int, reason: str) -> dict: ...
    def reconcile(self, date_from: str, date_to: str) -> dict: ...
