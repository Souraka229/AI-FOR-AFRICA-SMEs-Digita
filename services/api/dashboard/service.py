"""Dashboard du jour — activité commandes ≠ encaissé (verify serveur)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from db.repo import get_repo
from orders.store import get_order_store

PORTO_NOVO = ZoneInfo("Africa/Porto-Novo")
LATE_AFTER = timedelta(minutes=30)


def _parse(stamp: str) -> datetime:
    value = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def _on_day(stamp: str, day, zone: ZoneInfo) -> bool:
    return _parse(stamp).astimezone(zone).date() == day


def snapshot(tenant_slug: str, *, now: datetime | None = None) -> dict:
    moment = now or datetime.now(timezone.utc)
    local = moment.astimezone(PORTO_NOVO)
    day = local.date()
    orders = get_order_store().list_for(tenant_slug, None)
    active = [
        order
        for order in orders
        if order.status == "placed" and _on_day(order.created_at, day, PORTO_NOVO)
    ]
    activity_xof = sum(order.amount_xof for order in active)
    activity_count = len(active)
    average = activity_xof // activity_count if activity_count else 0

    qty: dict[str, int] = defaultdict(int)
    amount: dict[str, int] = defaultdict(int)
    names: dict[str, str] = {}
    for order in active:
        for line in order.lines:
            qty[line.sku] += line.qty
            amount[line.sku] += line.line_total_xof
            names[line.sku] = line.name
    top_items = sorted(
        (
            {
                "sku": sku,
                "name": names[sku],
                "qty": qty[sku],
                "amount_xof": amount[sku],
            }
            for sku in qty
        ),
        key=lambda row: (-row["amount_xof"], row["sku"]),
    )[:5]

    late = []
    for order in orders:
        if order.status != "placed":
            continue
        created = _parse(order.created_at)
        if moment - created < LATE_AFTER:
            continue
        late.append(
            {
                "id": order.id,
                "amount_xof": order.amount_xof,
                "created_at": order.created_at,
                "age_seconds": int((moment - created).total_seconds()),
            }
        )
    late.sort(key=lambda row: row["age_seconds"], reverse=True)

    collected = 0
    for entry in get_repo().list_for_tenant(tenant_slug):
        if not entry.verified_server or entry.status not in {"confirmed", "refunded"}:
            continue
        stamp = entry.confirmed_at or entry.created_at
        if not _on_day(stamp, day, PORTO_NOVO):
            continue
        collected += entry.amount_xof - entry.refunded_amount_xof

    return {
        "tenant_slug": tenant_slug,
        "timezone": "Africa/Porto-Novo",
        "day": day.isoformat(),
        "currency": "XOF",
        "activity_count": activity_count,
        "activity_xof": activity_xof,
        "average_basket_xof": average,
        "collected_xof": collected,
        "top_items": top_items,
        "late_orders": late,
    }
