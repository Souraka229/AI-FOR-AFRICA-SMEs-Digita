"""Smoke tests for core schema models."""

import importlib.util
from pathlib import Path

from afrosite_api.db.base import Base
from afrosite_api.db.models import CatalogItem, LedgerEntry, Order, Tenant, User


def test_models_registered_on_metadata() -> None:
    table_names = set(Base.metadata.tables)
    assert "tenants" in table_names
    assert "users" in table_names
    assert "catalog_items" in table_names
    assert "orders" in table_names
    assert "ledger_entries" in table_names
    assert Tenant.__tablename__ == "tenants"
    assert User.__tablename__ == "users"
    assert CatalogItem.__tablename__ == "catalog_items"
    assert Order.__tablename__ == "orders"
    assert LedgerEntry.__tablename__ == "ledger_entries"


def test_alembic_revision_modules_load() -> None:
    versions = Path(__file__).resolve().parents[2] / "migrations" / "versions"
    for name, rev in (
        ("0001_core_schema.py", "0001_core_schema"),
        ("0002_catalog_orders_ledger.py", "0002_catalog_orders_ledger"),
    ):
        path = versions / name
        spec = importlib.util.spec_from_file_location(f"rev_{rev}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.revision == rev
        assert callable(module.upgrade)
        assert callable(module.downgrade)
