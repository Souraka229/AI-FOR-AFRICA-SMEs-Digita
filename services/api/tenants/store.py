"""Registre tenants — mémoire par défaut, Postgres si DATABASE_URL."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from tenants.schemas import TenantRecord, Vertical


@dataclass
class TenantRow:
    slug: str
    name: str
    vertical: Vertical
    city: str
    neighborhood: str
    country: Literal["BJ"] = "BJ"

    def to_record(self) -> TenantRecord:
        return TenantRecord(
            slug=self.slug,
            name=self.name,
            vertical=self.vertical,
            city=self.city,
            neighborhood=self.neighborhood,
            country=self.country,
        )


SEEDS = (
    TenantRow("cadjehoun-wax", "Wax Cadjehoun", "commerce", "Cotonou", "Cadjehoun"),
    TenantRow("maquis-fidjrosse", "Maquis Fidjrossè", "restaurant", "Cotonou", "Fidjrossè"),
    TenantRow("salon-awa-cadjehoun", "Salon Awa Cadjehoun", "services", "Cotonou", "Cadjehoun"),
)


class MemoryTenantStore:
    backend: Literal["memory"] = "memory"

    def __init__(self) -> None:
        self._rows = {row.slug: row for row in SEEDS}

    def get(self, slug: str) -> TenantRow | None:
        return self._rows.get(slug)

    def create(self, row: TenantRow) -> TenantRow:
        if row.slug in self._rows:
            raise ValueError("slug_exists")
        self._rows[row.slug] = row
        return row

    def update(self, slug: str, **fields: str) -> TenantRow | None:
        current = self._rows.get(slug)
        if not current:
            return None
        data = {
            "slug": current.slug,
            "name": fields.get("name", current.name),
            "vertical": current.vertical,
            "city": fields.get("city", current.city),
            "neighborhood": fields.get("neighborhood", current.neighborhood),
            "country": current.country,
        }
        updated = TenantRow(**data)
        self._rows[slug] = updated
        return updated


class PostgresTenantStore:
    backend: Literal["postgres"] = "postgres"

    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self._dsn = dsn
        self._psycopg = psycopg
        self._dict_row = dict_row

    def _connect(self):
        return self._psycopg.connect(self._dsn, row_factory=self._dict_row)

    @staticmethod
    def _map(raw: dict) -> TenantRow:
        return TenantRow(
            slug=raw["slug"],
            name=raw["name"],
            vertical=raw["vertical"],
            city=raw.get("city") or "Cotonou",
            neighborhood=raw["neighborhood"],
        )

    def get(self, slug: str) -> TenantRow | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM tenants WHERE slug = %s", (slug,))
            row = cur.fetchone()
            return self._map(row) if row else None

    def create(self, row: TenantRow) -> TenantRow:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT slug FROM tenants WHERE slug = %s", (row.slug,))
            if cur.fetchone():
                raise ValueError("slug_exists")
            cur.execute(
                """
                INSERT INTO tenants (slug, name, vertical, city, neighborhood)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (row.slug, row.name, row.vertical, row.city, row.neighborhood),
            )
            created = cur.fetchone()
            conn.commit()
            return self._map(created)

    def update(self, slug: str, **fields: str) -> TenantRow | None:
        current = self.get(slug)
        if not current:
            return None
        name = fields.get("name", current.name)
        city = fields.get("city", current.city)
        neighborhood = fields.get("neighborhood", current.neighborhood)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tenants
                SET name = %s, city = %s, neighborhood = %s
                WHERE slug = %s
                RETURNING *
                """,
                (name, city, neighborhood, slug),
            )
            updated = cur.fetchone()
            conn.commit()
            return self._map(updated) if updated else None


_memory = MemoryTenantStore()
_postgres: PostgresTenantStore | None = None


def get_tenant_store() -> MemoryTenantStore | PostgresTenantStore:
    global _postgres
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres"):
        if _postgres is None:
            _postgres = PostgresTenantStore(url)
        return _postgres
    return _memory
