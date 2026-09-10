"""Repository ledger — même sémantique que apps/web/src/lib/demo/store.ts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Protocol
from uuid import uuid4

Channel = Literal["mtn_momo", "moov_money", "cash"]
Status = Literal["pending", "confirmed", "failed", "expired", "refunded"]
EventType = Literal["created", "verified", "failed", "expired", "refunded"]
Audience = Literal["customer", "owner"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LedgerEvent:
    at: str
    type: EventType
    amount_xof: int | None = None
    reason: str | None = None


@dataclass
class LedgerEntry:
    id: str
    reference: str
    tenant_slug: str
    amount_xof: int
    channel: Channel
    status: Status
    created_at: str
    verified_server: bool
    idem_key: str | None = None
    confirmed_at: str | None = None
    refunded_amount_xof: int = 0
    events: list[LedgerEvent] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "reference": self.reference,
            "tenantSlug": self.tenant_slug,
            "amountXof": self.amount_xof,
            "channel": self.channel,
            "status": self.status,
            "createdAt": self.created_at,
            "confirmedAt": self.confirmed_at,
            "verifiedServer": self.verified_server,
            "idemKey": self.idem_key,
            "refundedAmountXof": self.refunded_amount_xof,
            "events": [
                {
                    "at": event.at,
                    "type": event.type,
                    "amountXof": event.amount_xof,
                    "reason": event.reason,
                }
                for event in self.events
            ],
        }


class LedgerRepo(Protocol):
    backend: Literal["memory", "postgres"]

    def ensure_tenant(self, slug: str) -> None: ...
    def create_pending(
        self,
        tenant_slug: str,
        amount_xof: int,
        channel: Channel,
        idem_key: str | None = None,
        reference: str | None = None,
    ) -> LedgerEntry: ...
    def get(self, reference: str) -> LedgerEntry | None: ...
    def verify(self, reference: str) -> LedgerEntry | None: ...
    def fail(self, reference: str, reason: str = "échec PSP") -> LedgerEntry | None: ...
    def expire(self, reference: str) -> LedgerEntry | None: ...
    def refund(self, reference: str, amount_xof: int, reason: str) -> LedgerEntry | None: ...
    def list_for_tenant(self, slug: str) -> list[LedgerEntry]: ...


class MemoryLedgerRepo:
    backend: Literal["memory"] = "memory"

    def __init__(self) -> None:
        self._tenants = {
            "cadjehoun-wax": "Wax Cadjehoun",
            "maquis-fidjrosse": "Maquis Fidjrossè",
            "salon-awa-cadjehoun": "Salon Awa Cadjehoun",
        }
        self._rows: dict[str, LedgerEntry] = {}

    def ensure_tenant(self, slug: str) -> None:
        self._tenants.setdefault(slug, slug)

    def _name(self, slug: str) -> str:
        return self._tenants.get(slug, slug)

    def create_pending(
        self,
        tenant_slug: str,
        amount_xof: int,
        channel: Channel,
        idem_key: str | None = None,
        reference: str | None = None,
    ) -> LedgerEntry:
        if amount_xof <= 0:
            raise ValueError("Montant recalculé serveur invalide.")
        self.ensure_tenant(tenant_slug)
        if idem_key:
            for row in self._rows.values():
                if row.idem_key == idem_key:
                    return row
        created = now_iso()
        entry = LedgerEntry(
            id=str(uuid4()),
            reference=reference or f"MTX-API-{uuid4().hex[:8].upper()}",
            tenant_slug=tenant_slug,
            amount_xof=amount_xof,
            channel=channel,
            status="pending",
            created_at=created,
            verified_server=False,
            idem_key=idem_key,
            events=[LedgerEvent(at=created, type="created", amount_xof=amount_xof)],
        )
        self._rows[entry.reference] = entry
        return entry

    def get(self, reference: str) -> LedgerEntry | None:
        return self._rows.get(reference)

    def verify(self, reference: str) -> LedgerEntry | None:
        entry = self._rows.get(reference)
        if not entry:
            return None
        if entry.status in {"confirmed", "refunded", "failed", "expired"}:
            return entry
        stamp = now_iso()
        entry.status = "confirmed"
        entry.verified_server = True
        entry.confirmed_at = stamp
        entry.events.append(
            LedgerEvent(at=stamp, type="verified", amount_xof=entry.amount_xof)
        )
        return entry

    def fail(self, reference: str, reason: str = "échec PSP") -> LedgerEntry | None:
        entry = self._rows.get(reference)
        if not entry:
            return None
        if entry.status in {"confirmed", "refunded", "failed"}:
            return entry
        entry.status = "failed"
        entry.verified_server = True
        entry.events.append(LedgerEvent(at=now_iso(), type="failed", reason=reason))
        return entry

    def expire(self, reference: str) -> LedgerEntry | None:
        entry = self._rows.get(reference)
        if not entry:
            return None
        if entry.status != "pending":
            return entry
        entry.status = "expired"
        entry.verified_server = True
        entry.events.append(
            LedgerEvent(at=now_iso(), type="expired", reason="expiration sandbox")
        )
        return entry

    def refund(self, reference: str, amount_xof: int, reason: str) -> LedgerEntry | None:
        entry = self._rows.get(reference)
        if not entry or entry.status not in {"confirmed", "refunded"}:
            return None
        remaining = entry.amount_xof - entry.refunded_amount_xof
        if amount_xof <= 0 or amount_xof > remaining:
            return None
        entry.refunded_amount_xof += amount_xof
        if entry.refunded_amount_xof >= entry.amount_xof:
            entry.status = "refunded"
        entry.events.append(
            LedgerEvent(at=now_iso(), type="refunded", amount_xof=amount_xof, reason=reason)
        )
        return entry

    def list_for_tenant(self, slug: str) -> list[LedgerEntry]:
        return [row for row in self._rows.values() if row.tenant_slug == slug]


_memory = MemoryLedgerRepo()
_postgres: LedgerRepo | None = None


def get_repo() -> LedgerRepo:
    import os

    global _postgres
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres"):
        if _postgres is None:
            from .postgres import PostgresLedgerRepo

            _postgres = PostgresLedgerRepo(url)
        return _postgres
    return _memory
