"""Append-only ledger API + daily reconcile summary."""

from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from afrosite_api.auth.deps import require_roles
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import UserPublic
from afrosite_api.db.models.ledger_entry import LedgerEntry
from afrosite_api.db.session import get_db_session

router = APIRouter(prefix="/ledger", tags=["ledger"])


class LedgerAppend(BaseModel):
    order_id: str | None = None
    provider_ref: str | None = None
    direction: str = Field(pattern="^(credit|debit)$")
    amount_xof: Decimal = Field(gt=0)
    channel: str = "momo"
    note: str | None = None


class LedgerEntryPublic(BaseModel):
    id: str
    tenant_id: str
    order_id: str | None
    provider_ref: str | None
    direction: str
    amount_xof: Decimal
    channel: str
    created_at: datetime


class ReconcileSummary(BaseModel):
    day: date
    tenant_id: str
    credits_xof: Decimal
    debits_xof: Decimal
    net_xof: Decimal
    entry_count: int


@router.post("/entries", status_code=status.HTTP_201_CREATED)
async def append_entry(
    body: LedgerAppend,
    user: Annotated[UserPublic, Depends(require_roles(Role.OWNER, Role.CASHIER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LedgerEntryPublic:
    entry = LedgerEntry(
        id=f"led-{uuid4().hex[:12]}",
        tenant_id=user.tenant_id,
        order_id=body.order_id,
        provider_ref=body.provider_ref,
        direction=body.direction,
        amount_xof=body.amount_xof,
        channel=body.channel,
        note=body.note,
    )
    session.add(entry)
    await session.commit()
    return LedgerEntryPublic(
        id=entry.id,
        tenant_id=entry.tenant_id,
        order_id=entry.order_id,
        provider_ref=entry.provider_ref,
        direction=entry.direction,
        amount_xof=entry.amount_xof,
        channel=entry.channel,
        created_at=entry.created_at,
    )


@router.get("/entries")
async def list_entries(
    user: Annotated[UserPublic, Depends(require_roles(Role.OWNER, Role.CASHIER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[LedgerEntryPublic]:
    result = await session.execute(
        select(LedgerEntry)
        .where(LedgerEntry.tenant_id == user.tenant_id)
        .order_by(LedgerEntry.created_at)
    )
    return [
        LedgerEntryPublic(
            id=e.id,
            tenant_id=e.tenant_id,
            order_id=e.order_id,
            provider_ref=e.provider_ref,
            direction=e.direction,
            amount_xof=e.amount_xof,
            channel=e.channel,
            created_at=e.created_at,
        )
        for e in result.scalars().all()
    ]


@router.get("/reconcile/{day}")
async def reconcile_day(
    day: date,
    user: Annotated[UserPublic, Depends(require_roles(Role.OWNER))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReconcileSummary:
    start = datetime.combine(day, time.min, tzinfo=UTC)
    end = datetime.combine(day, time.max, tzinfo=UTC)
    result = await session.execute(
        select(LedgerEntry).where(
            LedgerEntry.tenant_id == user.tenant_id,
            LedgerEntry.created_at >= start,
            LedgerEntry.created_at <= end,
        )
    )
    entries = list(result.scalars().all())
    if not entries and day > date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Future day")
    credits = sum((e.amount_xof for e in entries if e.direction == "credit"), Decimal("0"))
    debits = sum((e.amount_xof for e in entries if e.direction == "debit"), Decimal("0"))
    return ReconcileSummary(
        day=day,
        tenant_id=user.tenant_id,
        credits_xof=credits,
        debits_xof=debits,
        net_xof=credits - debits,
        entry_count=len(entries),
    )
