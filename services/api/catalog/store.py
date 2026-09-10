"""Catalogue par tenant — prix XOF serveur."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CatalogItem:
    sku: str
    name: str
    price_xof: int
    category: str
    available: bool
    unit: str | None = None

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.name,
            "price_xof": self.price_xof,
            "category": self.category,
            "available": self.available,
            "unit": self.unit,
            "currency": "XOF",
        }


SEEDS: dict[str, dict[str, CatalogItem]] = {
    "cadjehoun-wax": {
        "wax-cadjehoun-6y": CatalogItem(
            "wax-cadjehoun-6y",
            "Pagne wax 6 yards — motif Cadjehoun",
            12500,
            "tissus",
            True,
            "pièce",
        ),
        "wax-fidjrosse-6y": CatalogItem(
            "wax-fidjrosse-6y",
            "Pagne wax 6 yards — motif Fidjrossè",
            8000,
            "tissus",
            True,
            "pièce",
        ),
        "livraison-quartier": CatalogItem(
            "livraison-quartier",
            "Livraison quartier",
            4000,
            "livraison",
            True,
            "course",
        ),
    },
    "maquis-fidjrosse": {
        "poisson-braise": CatalogItem(
            "poisson-braise", "Poisson braisé", 4500, "grillades", True
        ),
        "alloco-poulet": CatalogItem(
            "alloco-poulet", "Poulet + alloco", 3500, "grillades", True
        ),
        "jus-bissap": CatalogItem("jus-bissap", "Jus bissap", 500, "boissons", True),
    },
    "salon-awa-cadjehoun": {
        "tresses-medium": CatalogItem(
            "tresses-medium", "Tresses moyennes", 8000, "coiffure", True
        ),
        "locking": CatalogItem("locking", "Locking", 12000, "coiffure", True),
        "soin-capillaire": CatalogItem(
            "soin-capillaire", "Soin capillaire", 4000, "soins", True
        ),
    },
}


class MemoryCatalogStore:
    def __init__(self) -> None:
        self._rows: dict[str, dict[str, CatalogItem]] = {
            slug: dict(items) for slug, items in SEEDS.items()
        }

    def list(self, tenant_slug: str) -> list[CatalogItem]:
        return list(self._rows.get(tenant_slug, {}).values())

    def get(self, tenant_slug: str, sku: str) -> CatalogItem | None:
        return self._rows.get(tenant_slug, {}).get(sku)

    def upsert(self, tenant_slug: str, item: CatalogItem) -> CatalogItem:
        self._rows.setdefault(tenant_slug, {})[item.sku] = item
        return item

    def patch(self, tenant_slug: str, sku: str, **fields) -> CatalogItem | None:
        current = self.get(tenant_slug, sku)
        if not current:
            return None
        data = {
            "sku": current.sku,
            "name": fields.get("name", current.name),
            "price_xof": fields.get("price_xof", current.price_xof),
            "category": fields.get("category", current.category),
            "available": fields.get("available", current.available),
            "unit": fields["unit"] if "unit" in fields else current.unit,
        }
        updated = CatalogItem(**data)
        self._rows[tenant_slug][sku] = updated
        return updated


class PostgresCatalogStore:
    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self._dsn = dsn
        self._psycopg = psycopg
        self._dict_row = dict_row

    def _connect(self):
        return self._psycopg.connect(self._dsn, row_factory=self._dict_row)

    @staticmethod
    def _map(raw: dict) -> CatalogItem:
        return CatalogItem(
            sku=raw["sku"],
            name=raw["name"],
            price_xof=int(raw["price_xof"]),
            category=raw["category"],
            available=bool(raw["available"]),
            unit=raw.get("unit"),
        )

    def list(self, tenant_slug: str) -> list[CatalogItem]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT sku, name, price_xof, category, available, unit
                FROM catalog_items WHERE tenant_slug = %s ORDER BY sku
                """,
                (tenant_slug,),
            )
            return [self._map(row) for row in cur.fetchall()]

    def get(self, tenant_slug: str, sku: str) -> CatalogItem | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT sku, name, price_xof, category, available, unit
                FROM catalog_items WHERE tenant_slug = %s AND sku = %s
                """,
                (tenant_slug, sku),
            )
            row = cur.fetchone()
            return self._map(row) if row else None

    def upsert(self, tenant_slug: str, item: CatalogItem) -> CatalogItem:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO catalog_items
                  (tenant_slug, sku, name, price_xof, category, available, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tenant_slug, sku) DO UPDATE SET
                  name = EXCLUDED.name,
                  price_xof = EXCLUDED.price_xof,
                  category = EXCLUDED.category,
                  available = EXCLUDED.available,
                  unit = EXCLUDED.unit
                RETURNING sku, name, price_xof, category, available, unit
                """,
                (
                    tenant_slug,
                    item.sku,
                    item.name,
                    item.price_xof,
                    item.category,
                    item.available,
                    item.unit,
                ),
            )
            row = cur.fetchone()
            conn.commit()
            return self._map(row)

    def patch(self, tenant_slug: str, sku: str, **fields) -> CatalogItem | None:
        current = self.get(tenant_slug, sku)
        if not current:
            return None
        updated = CatalogItem(
            sku=current.sku,
            name=fields.get("name", current.name),
            price_xof=fields.get("price_xof", current.price_xof),
            category=fields.get("category", current.category),
            available=fields.get("available", current.available),
            unit=fields["unit"] if "unit" in fields else current.unit,
        )
        return self.upsert(tenant_slug, updated)


_memory = MemoryCatalogStore()
_postgres: PostgresCatalogStore | None = None


def get_catalog_store() -> MemoryCatalogStore | PostgresCatalogStore:
    global _postgres
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres"):
        if _postgres is None:
            _postgres = PostgresCatalogStore(url)
        return _postgres
    return _memory
