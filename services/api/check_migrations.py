"""Vérifie Alembic : upgrade → schéma → downgrade → upgrade.

Usage (base jetable, jamais la base démo) :

  set DATABASE_URL=postgresql://afrosite:<password>@127.0.0.1:5432/afrosite_migration_test
  python check_migrations.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent
EXPECTED_TABLES = {
    "tenants",
    "principals",
    "memberships",
    "catalog_items",
    "orders",
    "order_lines",
    "ledger_entries",
    "ledger_events",
    "whatsapp_messages",
    "cost_events",
    "audit_events",
    "customers",
    "customer_visits",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def url() -> str:
    value = os.environ.get("DATABASE_URL", "")
    if "migration_test" not in value:
        fail("DATABASE_URL doit pointer vers une base *migration_test* (jetable).")
    if not value.startswith("postgresql"):
        fail("DATABASE_URL Postgres obligatoire.")
    return value


def alembic(*args: str) -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = url()
    completed = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        fail(f"alembic {' '.join(args)} a échoué.")


def tables(conn: psycopg.Connection) -> set[str]:
    rows = conn.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name <> 'alembic_version'
        """
    ).fetchall()
    return {row[0] for row in rows}


def main() -> None:
    dsn = url()
    alembic("upgrade", "head")
    with psycopg.connect(dsn) as conn:
        found = tables(conn)
        if found != EXPECTED_TABLES:
            fail(f"Tables après upgrade : {sorted(found)} ≠ {sorted(EXPECTED_TABLES)}")
        wax = conn.execute(
            "SELECT SUM(price_xof) FROM catalog_items WHERE tenant_slug = 'cadjehoun-wax'"
        ).fetchone()
        if wax is None or int(wax[0] or 0) != 24500:
            fail(f"Seed wax attendu 24500 FCFA, obtenu {wax}.")

    alembic("downgrade", "base")
    with psycopg.connect(dsn) as conn:
        leftover = tables(conn)
        if leftover:
            fail(f"Downgrade incomplet : {sorted(leftover)}")

    alembic("upgrade", "head")
    with psycopg.connect(dsn) as conn:
        if tables(conn) != EXPECTED_TABLES:
            fail("Second upgrade incomplet.")
        version = conn.execute("SELECT version_num FROM alembic_version").fetchone()
        if not version or version[0] != "0002_crm":
            fail(f"Révision inattendue : {version}")

    print("check:migrations OK · upgrade / downgrade / upgrade · 24500 FCFA")


if __name__ == "__main__":
    main()
