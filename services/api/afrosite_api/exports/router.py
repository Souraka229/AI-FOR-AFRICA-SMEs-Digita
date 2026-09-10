"""Export CSV libre-service : ventes, transactions, clients. Jamais de secret."""

from __future__ import annotations

import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from afrosite_api.auth.deps import require_roles
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import UserPublic
from afrosite_api.db.models.ledger_entry import LedgerEntry
from afrosite_api.db.models.order import Order
from afrosite_api.db.models.user import User
from afrosite_api.db.session import get_db_session

router = APIRouter(prefix="/exports", tags=["exports"])


def _csv_file(filename: str, headers: list[str], rows: list[list[str]]) -> Response:
    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return Response(
        content=buffer.getvalue().encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{kind}.csv")
async def export_csv(
    kind: str,
    user: Annotated[UserPublic, Depends(require_roles(Role.OWNER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    if kind not in {"ventes", "transactions", "clients"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export inconnu")
    tenant = user.tenant_id
    if kind == "ventes":
        result = await session.execute(
            select(Order).where(Order.tenant_id == tenant).order_by(Order.created_at)
        )
        rows = [
            [
                order.id,
                order.catalog_item_id,
                str(order.quantity),
                str(order.unit_price_xof),
                str(order.total_xof),
                order.status,
                order.created_at.isoformat(),
            ]
            for order in result.scalars().all()
        ]
        return _csv_file(
            "ventes.csv",
            [
                "id",
                "catalog_item_id",
                "quantity",
                "unit_price_xof",
                "total_xof",
                "status",
                "created_at",
            ],
            rows,
        )
    if kind == "transactions":
        result = await session.execute(
            select(LedgerEntry)
            .where(LedgerEntry.tenant_id == tenant)
            .order_by(LedgerEntry.created_at)
        )
        rows = [
            [
                entry.id,
                entry.order_id or "",
                entry.provider_ref or "",
                entry.direction,
                str(entry.amount_xof),
                entry.channel,
                entry.created_at.isoformat(),
            ]
            for entry in result.scalars().all()
        ]
        return _csv_file(
            "transactions.csv",
            [
                "id",
                "order_id",
                "provider_ref",
                "direction",
                "amount_xof",
                "channel",
                "created_at",
            ],
            rows,
        )
    result = await session.execute(
        select(User).where(User.tenant_id == tenant).order_by(User.created_at)
    )
    rows = [
        [account.id, account.email, account.role, account.created_at.isoformat()]
        for account in result.scalars().all()
    ]
    return _csv_file(
        "clients.csv",
        ["id", "email", "role", "created_at"],
        rows,
    )
