"""CRM léger : clients par téléphone Bénin, visites, fidélité.

Revision ID: 0002_crm
Revises: 0001_core_schema
Create Date: 2026-09-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_crm"
down_revision = "0001_core_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column(
            "tenant_slug",
            sa.Text(),
            sa.ForeignKey("tenants.slug", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("phone", sa.Text(), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column(
            "loyalty_count",
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
        sa.CheckConstraint("loyalty_count >= 0", name="ck_customers_loyalty"),
        sa.CheckConstraint("phone LIKE '+229%'", name="ck_customers_phone_bj"),
    )
    op.create_table(
        "customer_visits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_slug",
            sa.Text(),
            nullable=False,
        ),
        sa.Column("phone", sa.Text(), nullable=False),
        sa.Column(
            "order_id",
            sa.Uuid(),
            sa.ForeignKey("orders.id", ondelete="SET NULL"),
        ),
        sa.Column("amount_xof", sa.Integer()),
        sa.Column("currency", sa.Text()),
        sa.Column("idem_key", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_slug", "phone"],
            ["customers.tenant_slug", "customers.phone"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "amount_xof IS NULL OR amount_xof >= 0",
            name="ck_visits_amount_xof",
        ),
        sa.CheckConstraint(
            "(amount_xof IS NULL AND currency IS NULL) OR "
            "(amount_xof IS NOT NULL AND currency = 'XOF')",
            name="ck_visits_currency",
        ),
    )
    op.create_index(
        "customer_visits_idem_uidx",
        "customer_visits",
        ["tenant_slug", "idem_key"],
        unique=True,
    )
    op.create_index(
        "customer_visits_phone_idx",
        "customer_visits",
        ["tenant_slug", "phone", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("customer_visits_phone_idx", table_name="customer_visits")
    op.drop_index("customer_visits_idem_uidx", table_name="customer_visits")
    op.drop_table("customer_visits")
    op.drop_table("customers")
