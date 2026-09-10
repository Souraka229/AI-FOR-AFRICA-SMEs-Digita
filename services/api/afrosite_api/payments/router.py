"""HTTP routes for payment webhooks (signature verified before normalize)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from afrosite_api.common.settings import Settings, get_settings
from afrosite_api.payments.providers.geniuspay import GeniusPayError, GeniusPayProvider
from afrosite_api.payments.types import WebhookEvent

router = APIRouter(prefix="/payments", tags=["payments"])

# In-process idempotency for webhook event_ids (ledger persistence comes later).
_seen_events: set[str] = set()


def get_geniuspay_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> GeniusPayProvider:
    try:
        return GeniusPayProvider(settings)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/webhooks/geniuspay")
async def geniuspay_webhook(
    request: Request,
    provider: Annotated[GeniusPayProvider, Depends(get_geniuspay_provider)],
    x_geniuspay_signature: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    if not x_geniuspay_signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature")
    body = await request.body()
    try:
        event: WebhookEvent = await provider.handle_webhook(body, x_geniuspay_signature)
    except GeniusPayError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if event.event_id in _seen_events:
        return {"status": "duplicate", "event_id": event.event_id}
    _seen_events.add(event.event_id)
    return {"status": "accepted", "event_id": event.event_id, "provider_ref": event.provider_ref}
