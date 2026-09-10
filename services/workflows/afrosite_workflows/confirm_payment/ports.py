"""Ports métier — le SDK Temporal n'appelle jamais le PSP directement."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


@dataclass
class AuditEvent:
    at: str
    agent: str
    action: str
    result: str
    tool: str = "confirm_payment"


class PaymentPort(Protocol):
    async def verify(
        self, provider_ref: str, expected_amount_xof: int, currency: str
    ) -> dict[str, object]:
        """Statut serveur. La redirection navigateur n'est pas une preuve."""


class LedgerPort(Protocol):
    async def append(
        self,
        *,
        tenant_id: str,
        order_id: str,
        provider_ref: str,
        direction: str,
        amount_xof: int,
        channel: str,
        note: str,
        idempotency_key: str,
    ) -> dict[str, object]:
        """Append-only. Un rejeu avec la même clé renvoie l'écriture existante."""


class WhatsAppPort(Protocol):
    async def notify_paid(self, tenant_id: str, provider_ref: str, amount_xof: int) -> bool:
        """True si un nouveau message part, False si déjà notifié pour cette ref."""


class AuditPort(Protocol):
    async def record(self, event: AuditEvent) -> int:
        """Retourne le nombre d'événements après insertion."""


@dataclass
class InMemoryLedger:
    entries: list[dict[str, object]] = field(default_factory=list)
    _keys: dict[str, dict[str, object]] = field(default_factory=dict)

    async def append(
        self,
        *,
        tenant_id: str,
        order_id: str,
        provider_ref: str,
        direction: str,
        amount_xof: int,
        channel: str,
        note: str,
        idempotency_key: str,
    ) -> dict[str, object]:
        existing = self._keys.get(idempotency_key)
        if existing is not None:
            return {**existing, "duplicated": True}
        row = {
            "entry_id": f"led_{len(self.entries) + 1}",
            "tenant_id": tenant_id,
            "order_id": order_id,
            "provider_ref": provider_ref,
            "direction": direction,
            "amount_xof": amount_xof,
            "channel": channel,
            "note": note,
            "duplicated": False,
        }
        self.entries.append(row)
        self._keys[idempotency_key] = row
        return row


@dataclass
class InMemoryWhatsApp:
    messages: list[dict[str, object]] = field(default_factory=list)

    async def notify_paid(self, tenant_id: str, provider_ref: str, amount_xof: int) -> bool:
        if any(row["provider_ref"] == provider_ref for row in self.messages):
            return False
        self.messages.append(
            {
                "tenant_id": tenant_id,
                "provider_ref": provider_ref,
                "amount_xof": amount_xof,
            }
        )
        return True


@dataclass
class InMemoryAudit:
    events: list[AuditEvent] = field(default_factory=list)

    async def record(self, event: AuditEvent) -> int:
        self.events.append(event)
        return len(self.events)


@dataclass
class ScriptedPaymentPort:
    """PSP de test : séquence de statuts, puis le dernier se répète."""

    sequence: list[dict[str, object]]
    calls: int = 0

    async def verify(
        self, provider_ref: str, expected_amount_xof: int, currency: str
    ) -> dict[str, object]:
        self.calls += 1
        index = min(self.calls - 1, len(self.sequence) - 1)
        row = dict(self.sequence[index])
        row.setdefault("provider_ref", provider_ref)
        row.setdefault("amount_xof", expected_amount_xof)
        row.setdefault("currency", currency)
        row.setdefault("verified_server", True)
        return row


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
