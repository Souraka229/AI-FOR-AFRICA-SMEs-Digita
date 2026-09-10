"""Commandes — montant recalculé depuis le catalogue, jamais depuis le client."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from uuid import uuid4

from catalog.store import get_catalog_store
from db.repo import now_iso


@dataclass
class OrderLine:
    sku: str
    name: str
    qty: int
    unit_price_xof: int
    line_total_xof: int


@dataclass
class Order:
    id: str
    tenant_slug: str
    created_by: str
    status: str
    amount_xof: int
    created_at: str
    idem_key: str | None = None
    lines: list[OrderLine] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_slug": self.tenant_slug,
            "created_by": self.created_by,
            "status": self.status,
            "amount_xof": self.amount_xof,
            "currency": "XOF",
            "created_at": self.created_at,
            "lines": [
                {
                    "sku": line.sku,
                    "name": line.name,
                    "qty": line.qty,
                    "unit_price_xof": line.unit_price_xof,
                    "line_total_xof": line.line_total_xof,
                }
                for line in self.lines
            ],
        }


def quote_lines(tenant_slug: str, items: list[tuple[str, int]]) -> list[OrderLine]:
    catalog = get_catalog_store()
    lines: list[OrderLine] = []
    for sku, qty in items:
        product = catalog.get(tenant_slug, sku)
        if not product:
            raise ValueError(f"SKU inconnu : {sku}")
        if not product.available:
            raise ValueError(f"SKU indisponible : {sku}")
        unit = product.price_xof
        lines.append(
            OrderLine(
                sku=sku,
                name=product.name,
                qty=qty,
                unit_price_xof=unit,
                line_total_xof=unit * qty,
            )
        )
    if not lines:
        raise ValueError("Panier vide.")
    return lines


class MemoryOrderStore:
    def __init__(self) -> None:
        self._rows: dict[str, Order] = {}

    def create(
        self,
        tenant_slug: str,
        created_by: str,
        items: list[tuple[str, int]],
        idem_key: str,
    ) -> Order:
        for row in self._rows.values():
            if row.tenant_slug == tenant_slug and row.idem_key == idem_key:
                return row
        lines = quote_lines(tenant_slug, items)
        amount = sum(line.line_total_xof for line in lines)
        if amount <= 0:
            raise ValueError("Montant recalculé serveur invalide.")
        order = Order(
            id=str(uuid4()),
            tenant_slug=tenant_slug,
            created_by=created_by,
            status="placed",
            amount_xof=amount,
            created_at=now_iso(),
            idem_key=idem_key,
            lines=lines,
        )
        self._rows[order.id] = order
        return order

    def get(self, tenant_slug: str, order_id: str) -> Order | None:
        order = self._rows.get(order_id)
        if not order or order.tenant_slug != tenant_slug:
            return None
        return order

    def list_for(self, tenant_slug: str, subject: str | None) -> list[Order]:
        rows = [row for row in self._rows.values() if row.tenant_slug == tenant_slug]
        if subject is not None:
            rows = [row for row in rows if row.created_by == subject]
        return sorted(rows, key=lambda row: row.created_at, reverse=True)

    def cancel(self, tenant_slug: str, order_id: str) -> Order | None:
        order = self.get(tenant_slug, order_id)
        if not order:
            return None
        if order.status == "cancelled":
            return order
        order.status = "cancelled"
        return order


class PostgresOrderStore:
    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self._dsn = dsn
        self._psycopg = psycopg
        self._dict_row = dict_row

    def _connect(self):
        return self._psycopg.connect(self._dsn, row_factory=self._dict_row)

    def _hydrate(self, raw: dict, lines: list[dict]) -> Order:
        return Order(
            id=str(raw["id"]),
            tenant_slug=raw["tenant_slug"],
            created_by=raw["created_by"],
            status=raw["status"],
            amount_xof=int(raw["amount_xof"]),
            created_at=raw["created_at"].isoformat()
            if hasattr(raw["created_at"], "isoformat")
            else str(raw["created_at"]),
            idem_key=raw.get("idem_key"),
            lines=[
                OrderLine(
                    sku=line["sku"],
                    name=line["name"],
                    qty=int(line["qty"]),
                    unit_price_xof=int(line["unit_price_xof"]),
                    line_total_xof=int(line["line_total_xof"]),
                )
                for line in lines
            ],
        )

    def _lines(self, cur, order_id: str) -> list[dict]:
        cur.execute(
            """
            SELECT sku, name, qty, unit_price_xof, line_total_xof
            FROM order_lines WHERE order_id = %s
            """,
            (order_id,),
        )
        return list(cur.fetchall())

    def create(
        self,
        tenant_slug: str,
        created_by: str,
        items: list[tuple[str, int]],
        idem_key: str,
    ) -> Order:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM orders
                WHERE tenant_slug = %s AND idem_key = %s
                """,
                (tenant_slug, idem_key),
            )
            existing = cur.fetchone()
            if existing:
                return self._hydrate(existing, self._lines(cur, str(existing["id"])))
            lines = quote_lines(tenant_slug, items)
            amount = sum(line.line_total_xof for line in lines)
            if amount <= 0:
                raise ValueError("Montant recalculé serveur invalide.")
            order_id = str(uuid4())
            created = now_iso()
            cur.execute(
                """
                INSERT INTO orders
                  (id, tenant_slug, created_by, status, amount_xof, currency, idem_key, created_at)
                VALUES (%s, %s, %s, 'placed', %s, 'XOF', %s, %s)
                RETURNING *
                """,
                (order_id, tenant_slug, created_by, amount, idem_key, created),
            )
            raw = cur.fetchone()
            for line in lines:
                cur.execute(
                    """
                    INSERT INTO order_lines
                      (order_id, sku, name, qty, unit_price_xof, line_total_xof)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        line.sku,
                        line.name,
                        line.qty,
                        line.unit_price_xof,
                        line.line_total_xof,
                    ),
                )
            conn.commit()
            return self._hydrate(raw, [line.__dict__ for line in lines])

    def get(self, tenant_slug: str, order_id: str) -> Order | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM orders WHERE id = %s AND tenant_slug = %s",
                (order_id, tenant_slug),
            )
            raw = cur.fetchone()
            if not raw:
                return None
            return self._hydrate(raw, self._lines(cur, order_id))

    def list_for(self, tenant_slug: str, subject: str | None) -> list[Order]:
        with self._connect() as conn, conn.cursor() as cur:
            if subject is None:
                cur.execute(
                    """
                    SELECT * FROM orders WHERE tenant_slug = %s
                    ORDER BY created_at DESC
                    """,
                    (tenant_slug,),
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM orders
                    WHERE tenant_slug = %s AND created_by = %s
                    ORDER BY created_at DESC
                    """,
                    (tenant_slug, subject),
                )
            rows = list(cur.fetchall())
            return [self._hydrate(row, self._lines(cur, str(row["id"]))) for row in rows]

    def cancel(self, tenant_slug: str, order_id: str) -> Order | None:
        order = self.get(tenant_slug, order_id)
        if not order:
            return None
        if order.status == "cancelled":
            return order
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE orders SET status = 'cancelled'
                WHERE id = %s AND tenant_slug = %s
                RETURNING *
                """,
                (order_id, tenant_slug),
            )
            raw = cur.fetchone()
            conn.commit()
            return self._hydrate(raw, self._lines(cur, order_id)) if raw else None


_memory = MemoryOrderStore()
_postgres: PostgresOrderStore | None = None


def get_order_store() -> MemoryOrderStore | PostgresOrderStore:
    global _postgres
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres"):
        if _postgres is None:
            _postgres = PostgresOrderStore(url)
        return _postgres
    return _memory
