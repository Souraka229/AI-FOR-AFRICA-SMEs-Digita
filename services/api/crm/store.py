"""Clients par téléphone — mémoire par défaut, Postgres si DATABASE_URL."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from uuid import uuid4

from crm.phone import normalize_bj_phone
from db.repo import now_iso
from orders.store import get_order_store


@dataclass
class Visit:
    id: str
    tenant_slug: str
    phone: str
    order_id: str | None
    amount_xof: int | None
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "phone": self.phone,
            "order_id": self.order_id,
            "amount_xof": self.amount_xof,
            "currency": "XOF" if self.amount_xof is not None else None,
            "created_at": self.created_at,
        }


@dataclass
class Customer:
    tenant_slug: str
    phone: str
    display_name: str
    loyalty_count: int
    created_at: str
    visits: list[Visit] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tenant_slug": self.tenant_slug,
            "phone": self.phone,
            "display_name": self.display_name,
            "loyalty_count": self.loyalty_count,
            "created_at": self.created_at,
            "visits": [visit.to_dict() for visit in self.visits],
        }


def _stamp(value) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


class MemoryCrmStore:
    def __init__(self) -> None:
        self._customers: dict[tuple[str, str], Customer] = {}
        self._visits: dict[str, Visit] = {}
        self._idem: dict[tuple[str, str], str] = {}

    def upsert(self, tenant_slug: str, phone_raw: str, display_name: str) -> Customer:
        phone = normalize_bj_phone(phone_raw)
        key = (tenant_slug, phone)
        current = self._customers.get(key)
        if current:
            current.display_name = display_name
            return current
        row = Customer(
            tenant_slug=tenant_slug,
            phone=phone,
            display_name=display_name,
            loyalty_count=0,
            created_at=now_iso(),
        )
        self._customers[key] = row
        return row

    def get(self, tenant_slug: str, phone_raw: str) -> Customer | None:
        phone = normalize_bj_phone(phone_raw)
        row = self._customers.get((tenant_slug, phone))
        if not row:
            return None
        visits = [
            visit
            for visit in self._visits.values()
            if visit.tenant_slug == tenant_slug and visit.phone == phone
        ]
        row.visits = sorted(visits, key=lambda item: item.created_at, reverse=True)
        return row

    def list(self, tenant_slug: str) -> list[Customer]:
        rows = [row for row in self._customers.values() if row.tenant_slug == tenant_slug]
        return sorted(rows, key=lambda row: row.phone)

    def add_visit(
        self,
        tenant_slug: str,
        phone_raw: str,
        idem_key: str,
        order_id: str | None,
    ) -> Customer:
        phone = normalize_bj_phone(phone_raw)
        customer = self._customers.get((tenant_slug, phone))
        if not customer:
            raise ValueError("client_inconnu")
        replay = self._idem.get((tenant_slug, idem_key))
        if replay:
            stored = self._visits[replay]
            if stored.phone != phone:
                raise ValueError("idempotence_conflit")
            return self.get(tenant_slug, phone) or customer
        amount: int | None = None
        if order_id:
            order = get_order_store().get(tenant_slug, order_id)
            if not order:
                raise ValueError("commande_inconnue")
            amount = order.amount_xof
        visit = Visit(
            id=str(uuid4()),
            tenant_slug=tenant_slug,
            phone=phone,
            order_id=order_id,
            amount_xof=amount,
            created_at=now_iso(),
        )
        self._visits[visit.id] = visit
        self._idem[(tenant_slug, idem_key)] = visit.id
        customer.loyalty_count += 1
        return self.get(tenant_slug, phone) or customer


class PostgresCrmStore:
    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self._dsn = dsn
        self._psycopg = psycopg
        self._dict_row = dict_row

    def _connect(self):
        return self._psycopg.connect(self._dsn, row_factory=self._dict_row)

    def upsert(self, tenant_slug: str, phone_raw: str, display_name: str) -> Customer:
        phone = normalize_bj_phone(phone_raw)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO customers (tenant_slug, phone, display_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (tenant_slug, phone)
                DO UPDATE SET display_name = EXCLUDED.display_name
                RETURNING *
                """,
                (tenant_slug, phone, display_name),
            )
            raw = cur.fetchone()
            conn.commit()
        return self.get(tenant_slug, phone) if raw else Customer(
            tenant_slug=tenant_slug,
            phone=phone,
            display_name=display_name,
            loyalty_count=0,
            created_at=now_iso(),
        )

    def get(self, tenant_slug: str, phone_raw: str) -> Customer | None:
        phone = normalize_bj_phone(phone_raw)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM customers
                WHERE tenant_slug = %s AND phone = %s
                """,
                (tenant_slug, phone),
            )
            raw = cur.fetchone()
            if not raw:
                return None
            cur.execute(
                """
                SELECT * FROM customer_visits
                WHERE tenant_slug = %s AND phone = %s
                ORDER BY created_at DESC
                """,
                (tenant_slug, phone),
            )
            visits = [
                Visit(
                    id=str(row["id"]),
                    tenant_slug=row["tenant_slug"],
                    phone=row["phone"],
                    order_id=str(row["order_id"]) if row["order_id"] else None,
                    amount_xof=int(row["amount_xof"]) if row["amount_xof"] is not None else None,
                    created_at=_stamp(row["created_at"]),
                )
                for row in cur.fetchall()
            ]
        return Customer(
            tenant_slug=raw["tenant_slug"],
            phone=raw["phone"],
            display_name=raw["display_name"],
            loyalty_count=int(raw["loyalty_count"]),
            created_at=_stamp(raw["created_at"]),
            visits=visits,
        )

    def list(self, tenant_slug: str) -> list[Customer]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM customers
                WHERE tenant_slug = %s
                ORDER BY phone
                """,
                (tenant_slug,),
            )
            rows = list(cur.fetchall())
        return [
            Customer(
                tenant_slug=row["tenant_slug"],
                phone=row["phone"],
                display_name=row["display_name"],
                loyalty_count=int(row["loyalty_count"]),
                created_at=_stamp(row["created_at"]),
            )
            for row in rows
        ]

    def add_visit(
        self,
        tenant_slug: str,
        phone_raw: str,
        idem_key: str,
        order_id: str | None,
    ) -> Customer:
        phone = normalize_bj_phone(phone_raw)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM customer_visits
                WHERE tenant_slug = %s AND idem_key = %s
                """,
                (tenant_slug, idem_key),
            )
            existing = cur.fetchone()
            if existing:
                if existing["phone"] != phone:
                    raise ValueError("idempotence_conflit")
                conn.commit()
                found = self.get(tenant_slug, phone)
                if not found:
                    raise ValueError("client_inconnu")
                return found
            cur.execute(
                """
                SELECT 1 FROM customers
                WHERE tenant_slug = %s AND phone = %s
                """,
                (tenant_slug, phone),
            )
            if not cur.fetchone():
                raise ValueError("client_inconnu")
            amount: int | None = None
            if order_id:
                order = get_order_store().get(tenant_slug, order_id)
                if not order:
                    raise ValueError("commande_inconnue")
                amount = order.amount_xof
            cur.execute(
                """
                INSERT INTO customer_visits
                  (id, tenant_slug, phone, order_id, amount_xof, currency, idem_key)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid4()),
                    tenant_slug,
                    phone,
                    order_id,
                    amount,
                    "XOF" if amount is not None else None,
                    idem_key,
                ),
            )
            cur.execute(
                """
                UPDATE customers
                SET loyalty_count = loyalty_count + 1
                WHERE tenant_slug = %s AND phone = %s
                """,
                (tenant_slug, phone),
            )
            conn.commit()
        found = self.get(tenant_slug, phone)
        if not found:
            raise ValueError("client_inconnu")
        return found


_memory = MemoryCrmStore()
_postgres: PostgresCrmStore | None = None


def get_crm_store() -> MemoryCrmStore | PostgresCrmStore:
    global _postgres
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres"):
        if _postgres is None:
            _postgres = PostgresCrmStore(url)
        return _postgres
    return _memory
