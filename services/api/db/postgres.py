"""Ledger Postgres — activé seulement si DATABASE_URL est défini."""

from __future__ import annotations

from typing import Literal
from uuid import uuid4

from .repo import Channel, LedgerEntry, LedgerEvent, now_iso

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None  # type: ignore[assignment]
    dict_row = None  # type: ignore[assignment]


def _row(raw: dict) -> LedgerEntry:
    return LedgerEntry(
        id=str(raw["id"]),
        reference=raw["reference"],
        tenant_slug=raw["tenant_slug"],
        amount_xof=int(raw["amount_xof"]),
        channel=raw["channel"],
        status=raw["status"],
        created_at=raw["created_at"].isoformat()
        if hasattr(raw["created_at"], "isoformat")
        else str(raw["created_at"]),
        verified_server=bool(raw["verified_server"]),
        idem_key=raw.get("idem_key"),
        confirmed_at=raw["confirmed_at"].isoformat()
        if raw.get("confirmed_at") and hasattr(raw["confirmed_at"], "isoformat")
        else (str(raw["confirmed_at"]) if raw.get("confirmed_at") else None),
        refunded_amount_xof=int(raw.get("refunded_amount_xof") or 0),
        events=[],
    )


class PostgresLedgerRepo:
    backend: Literal["postgres"] = "postgres"

    def __init__(self, dsn: str) -> None:
        if psycopg is None:
            raise RuntimeError("psycopg manquant — pip install psycopg[binary]")
        self._dsn = dsn

    def _connect(self):
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def ensure_tenant(self, slug: str) -> None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tenants (slug, name, vertical, neighborhood)
                VALUES (%s, %s, 'commerce', 'Cadjehoun')
                ON CONFLICT (slug) DO NOTHING
                """,
                (slug, slug),
            )
            conn.commit()

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
        with self._connect() as conn, conn.cursor() as cur:
            if idem_key:
                cur.execute(
                    "SELECT * FROM ledger_entries WHERE idem_key = %s",
                    (idem_key,),
                )
                existing = cur.fetchone()
                if existing:
                    return _row(existing)
            entry_id = str(uuid4())
            ref = reference or f"MTX-API-{uuid4().hex[:8].upper()}"
            created = now_iso()
            cur.execute(
                """
                INSERT INTO ledger_entries (
                  id, reference, tenant_slug, amount_xof, channel, status,
                  verified_server, idem_key, refunded_amount_xof, created_at
                ) VALUES (%s, %s, %s, %s, %s, 'pending', false, %s, 0, %s)
                RETURNING *
                """,
                (entry_id, ref, tenant_slug, amount_xof, channel, idem_key, created),
            )
            row = cur.fetchone()
            cur.execute(
                """
                INSERT INTO ledger_events (id, reference, type, amount_xof, at)
                VALUES (%s, %s, 'created', %s, %s)
                """,
                (str(uuid4()), ref, amount_xof, created),
            )
            conn.commit()
            return _row(row)

    def get(self, reference: str) -> LedgerEntry | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM ledger_entries WHERE reference = %s", (reference,))
            row = cur.fetchone()
            return _row(row) if row else None

    def verify(self, reference: str) -> LedgerEntry | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM ledger_entries WHERE reference = %s", (reference,))
            row = cur.fetchone()
            if not row:
                return None
            entry = _row(row)
            if entry.status in {"confirmed", "refunded", "failed", "expired"}:
                return entry
            stamp = now_iso()
            cur.execute(
                """
                UPDATE ledger_entries
                SET status = 'confirmed', verified_server = true, confirmed_at = %s
                WHERE reference = %s
                RETURNING *
                """,
                (stamp, reference),
            )
            updated = cur.fetchone()
            cur.execute(
                """
                INSERT INTO ledger_events (id, reference, type, amount_xof, at)
                VALUES (%s, %s, 'verified', %s, %s)
                """,
                (str(uuid4()), reference, entry.amount_xof, stamp),
            )
            conn.commit()
            return _row(updated)

    def fail(self, reference: str, reason: str = "échec PSP") -> LedgerEntry | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM ledger_entries WHERE reference = %s", (reference,))
            row = cur.fetchone()
            if not row:
                return None
            entry = _row(row)
            if entry.status in {"confirmed", "refunded", "failed"}:
                return entry
            cur.execute(
                """
                UPDATE ledger_entries
                SET status = 'failed', verified_server = true
                WHERE reference = %s
                RETURNING *
                """,
                (reference,),
            )
            updated = cur.fetchone()
            cur.execute(
                """
                INSERT INTO ledger_events (id, reference, type, reason, at)
                VALUES (%s, %s, 'failed', %s, %s)
                """,
                (str(uuid4()), reference, reason, now_iso()),
            )
            conn.commit()
            return _row(updated)

    def expire(self, reference: str) -> LedgerEntry | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM ledger_entries WHERE reference = %s", (reference,))
            row = cur.fetchone()
            if not row:
                return None
            entry = _row(row)
            if entry.status != "pending":
                return entry
            cur.execute(
                """
                UPDATE ledger_entries
                SET status = 'expired', verified_server = true
                WHERE reference = %s
                RETURNING *
                """,
                (reference,),
            )
            updated = cur.fetchone()
            cur.execute(
                """
                INSERT INTO ledger_events (id, reference, type, reason, at)
                VALUES (%s, %s, 'expired', 'expiration sandbox', %s)
                """,
                (str(uuid4()), reference, now_iso()),
            )
            conn.commit()
            return _row(updated)

    def refund(self, reference: str, amount_xof: int, reason: str) -> LedgerEntry | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM ledger_entries WHERE reference = %s", (reference,))
            row = cur.fetchone()
            if not row:
                return None
            entry = _row(row)
            if entry.status not in {"confirmed", "refunded"}:
                return None
            remaining = entry.amount_xof - entry.refunded_amount_xof
            if amount_xof <= 0 or amount_xof > remaining:
                return None
            new_refunded = entry.refunded_amount_xof + amount_xof
            status = "refunded" if new_refunded >= entry.amount_xof else entry.status
            cur.execute(
                """
                UPDATE ledger_entries
                SET refunded_amount_xof = %s, status = %s
                WHERE reference = %s
                RETURNING *
                """,
                (new_refunded, status, reference),
            )
            updated = cur.fetchone()
            cur.execute(
                """
                INSERT INTO ledger_events (id, reference, type, amount_xof, reason, at)
                VALUES (%s, %s, 'refunded', %s, %s, %s)
                """,
                (str(uuid4()), reference, amount_xof, reason, now_iso()),
            )
            conn.commit()
            return _row(updated)

    def list_for_tenant(self, slug: str) -> list[LedgerEntry]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM ledger_entries
                WHERE tenant_slug = %s
                ORDER BY created_at DESC
                """,
                (slug,),
            )
            return [_row(row) for row in cur.fetchall()]
