"""Smoke tests for core schema models."""

import importlib.util
from pathlib import Path

from afrosite_api.db.base import Base
from afrosite_api.db.models import Tenant, User


def test_models_registered_on_metadata() -> None:
    table_names = set(Base.metadata.tables)
    assert "tenants" in table_names
    assert "users" in table_names
    assert Tenant.__tablename__ == "tenants"
    assert User.__tablename__ == "users"


def test_alembic_revision_module_loads() -> None:
    path = Path(__file__).resolve().parents[2] / "migrations" / "versions" / "0001_core_schema.py"
    spec = importlib.util.spec_from_file_location("rev_0001", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.revision == "0001_core_schema"
    assert callable(module.upgrade)
    assert callable(module.downgrade)
