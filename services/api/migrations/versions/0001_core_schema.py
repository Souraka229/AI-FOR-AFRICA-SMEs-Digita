"""Socle commun Phase 1 : tenants, RBAC, catalogue, commandes, ledger, audit.

Revision ID: 0001_core_schema
Revises:
Create Date: 2026-09-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_core_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("slug", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("vertical", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False, server_default="Cotonou"),
        sa.Column("neighborhood", sa.Text(), nullable=False),
        sa.Column("country", sa.Text(), nullable=False, server_default="BJ"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "vertical IN ('commerce', 'restaurant', 'services')",
            name="ck_tenants_vertical",
        ),
        sa.CheckConstraint("country = 'BJ'", name="ck_tenants_country"),
    )

    op.create_table(
        "principals",
        sa.Column("subject", sa.Text(), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_table(
        "memberships",
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "subject",
            sa.Text(),
            sa.ForeignKey("principals.subject", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("role", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "role IN ('owner', 'cashier', 'kitchen', 'customer')",
            name="ck_memberships_role",
        ),
    )

    op.create_table(
        "catalog_items",
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("sku", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("price_xof", sa.Integer(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("unit", sa.Text()),
        sa.CheckConstraint("price_xof >= 0", name="ck_catalog_price_xof"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("amount_xof", sa.Integer(), nullable=False),
        sa.Column("currency", sa.Text(), nullable=False, server_default="XOF"),
        sa.Column("idem_key", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('placed', 'cancelled')",
            name="ck_orders_status",
        ),
        sa.CheckConstraint("amount_xof > 0", name="ck_orders_amount_xof"),
        sa.CheckConstraint("currency = 'XOF'", name="ck_orders_currency"),
    )
    op.create_index(
        "orders_idem_uidx",
        "orders",
        ["tenant_slug", "idem_key"],
        unique=True,
        postgresql_where=sa.text("idem_key IS NOT NULL"),
    )
    op.create_index("orders_tenant_created_idx", "orders", ["tenant_slug", "created_at"])

    op.create_table(
        "order_lines",
        sa.Column(
            "order_id",
            sa.Uuid(),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("sku", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("unit_price_xof", sa.Integer(), nullable=False),
        sa.Column("line_total_xof", sa.Integer(), nullable=False),
        sa.CheckConstraint("qty > 0", name="ck_order_lines_qty"),
        sa.CheckConstraint(
            "unit_price_xof >= 0",
            name="ck_order_lines_unit_price_xof",
        ),
        sa.CheckConstraint(
            "line_total_xof = unit_price_xof * qty",
            name="ck_order_lines_total_xof",
        ),
    )

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("reference", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount_xof", sa.Integer(), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("verified_server", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("idem_key", sa.Text()),
        sa.Column(
            "refunded_amount_xof",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("amount_xof >= 0", name="ck_ledger_amount_xof"),
        sa.CheckConstraint(
            "channel IN ('mtn_momo', 'moov_money', 'cash')",
            name="ck_ledger_channel",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'confirmed', 'failed', 'expired', 'refunded')",
            name="ck_ledger_status",
        ),
        sa.CheckConstraint(
            "refunded_amount_xof BETWEEN 0 AND amount_xof",
            name="ck_ledger_refunded_amount_xof",
        ),
    )
    op.create_index(
        "ledger_idem_key_uidx",
        "ledger_entries",
        ["idem_key"],
        unique=True,
        postgresql_where=sa.text("idem_key IS NOT NULL"),
    )
    op.create_index(
        "ledger_tenant_created_idx",
        "ledger_entries",
        ["tenant_slug", "created_at"],
    )

    op.create_table(
        "ledger_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "reference",
            sa.Text(),
            sa.ForeignKey("ledger_entries.reference", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("amount_xof", sa.Integer()),
        sa.Column("reason", sa.Text()),
        sa.Column(
            "at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "type IN ('created', 'verified', 'failed', 'expired', 'refunded')",
            name="ck_ledger_events_type",
        ),
    )
    op.create_index("ledger_events_ref_idx", "ledger_events", ["reference", "at"])

    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("audience", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("payment_ref", sa.Text()),
        sa.Column(
            "at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "audience IN ('customer', 'owner')",
            name="ck_whatsapp_audience",
        ),
    )

    op.create_table(
        "cost_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("agent", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column(
            "at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("credits >= 0", name="ck_cost_events_credits"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="RESTRICT"),
        ),
        sa.Column("actor", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "audit_tenant_at_idx",
        "audit_events",
        ["tenant_slug", "at"],
    )

    tenants = sa.table(
        "tenants",
        sa.column("slug", sa.Text()),
        sa.column("name", sa.Text()),
        sa.column("vertical", sa.Text()),
        sa.column("city", sa.Text()),
        sa.column("neighborhood", sa.Text()),
        sa.column("country", sa.Text()),
    )
    op.bulk_insert(
        tenants,
        [
            {
                "slug": "cadjehoun-wax",
                "name": "Wax Cadjehoun",
                "vertical": "commerce",
                "city": "Cotonou",
                "neighborhood": "Cadjehoun",
                "country": "BJ",
            },
            {
                "slug": "maquis-fidjrosse",
                "name": "Maquis Fidjrossè",
                "vertical": "restaurant",
                "city": "Cotonou",
                "neighborhood": "Fidjrossè",
                "country": "BJ",
            },
            {
                "slug": "salon-awa-cadjehoun",
                "name": "Salon Awa Cadjehoun",
                "vertical": "services",
                "city": "Cotonou",
                "neighborhood": "Cadjehoun",
                "country": "BJ",
            },
        ],
    )

    catalog = sa.table(
        "catalog_items",
        sa.column("tenant_slug", sa.Text()),
        sa.column("sku", sa.Text()),
        sa.column("name", sa.Text()),
        sa.column("price_xof", sa.Integer()),
        sa.column("category", sa.Text()),
        sa.column("available", sa.Boolean()),
        sa.column("unit", sa.Text()),
    )
    op.bulk_insert(
        catalog,
        [
            {
                "tenant_slug": "cadjehoun-wax",
                "sku": "wax-cadjehoun-6y",
                "name": "Pagne wax 6 yards — motif Cadjehoun",
                "price_xof": 12500,
                "category": "tissus",
                "available": True,
                "unit": "pièce",
            },
            {
                "tenant_slug": "cadjehoun-wax",
                "sku": "wax-fidjrosse-6y",
                "name": "Pagne wax 6 yards — motif Fidjrossè",
                "price_xof": 8000,
                "category": "tissus",
                "available": True,
                "unit": "pièce",
            },
            {
                "tenant_slug": "cadjehoun-wax",
                "sku": "livraison-quartier",
                "name": "Livraison quartier",
                "price_xof": 4000,
                "category": "livraison",
                "available": True,
                "unit": "course",
            },
            {
                "tenant_slug": "maquis-fidjrosse",
                "sku": "poisson-braise",
                "name": "Poisson braisé",
                "price_xof": 4500,
                "category": "grillades",
                "available": True,
                "unit": None,
            },
            {
                "tenant_slug": "maquis-fidjrosse",
                "sku": "alloco-poulet",
                "name": "Poulet + alloco",
                "price_xof": 3500,
                "category": "grillades",
                "available": True,
                "unit": None,
            },
            {
                "tenant_slug": "maquis-fidjrosse",
                "sku": "jus-bissap",
                "name": "Jus bissap",
                "price_xof": 500,
                "category": "boissons",
                "available": True,
                "unit": None,
            },
            {
                "tenant_slug": "salon-awa-cadjehoun",
                "sku": "tresses-medium",
                "name": "Tresses moyennes",
                "price_xof": 8000,
                "category": "coiffure",
                "available": True,
                "unit": None,
            },
            {
                "tenant_slug": "salon-awa-cadjehoun",
                "sku": "locking",
                "name": "Locking",
                "price_xof": 12000,
                "category": "coiffure",
                "available": True,
                "unit": None,
            },
            {
                "tenant_slug": "salon-awa-cadjehoun",
                "sku": "soin-capillaire",
                "name": "Soin capillaire",
                "price_xof": 4000,
                "category": "soins",
                "available": True,
                "unit": None,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("audit_tenant_at_idx", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("cost_events")
    op.drop_table("whatsapp_messages")
    op.drop_index("ledger_events_ref_idx", table_name="ledger_events")
    op.drop_table("ledger_events")
    op.drop_index("ledger_tenant_created_idx", table_name="ledger_entries")
    op.drop_index("ledger_idem_key_uidx", table_name="ledger_entries")
    op.drop_table("ledger_entries")
    op.drop_table("order_lines")
    op.drop_index("orders_tenant_created_idx", table_name="orders")
    op.drop_index("orders_idem_uidx", table_name="orders")
    op.drop_table("orders")
    op.drop_table("catalog_items")
    op.drop_table("memberships")
    op.drop_table("principals")
    op.drop_table("tenants")
