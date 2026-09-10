"""Endpoints d'amorçage local et inspection de session."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from auth.bootstrap import require_bootstrap_key
from auth.dependencies import current_principal, require_access
from auth.schemas import IssueTokenBody, Principal, TokenResponse
from auth.service import AuthConfigurationError, issue_token

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/token",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_token(
    body: IssueTokenBody,
    _: None = Depends(require_bootstrap_key),
) -> TokenResponse:
    try:
        token = issue_token(
            subject=body.subject,
            tenant_slug=body.tenant_slug,
            role=body.role,
            ttl_seconds=body.ttl_seconds,
        )
    except AuthConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return TokenResponse(access_token=token, expires_in=body.ttl_seconds)


@router.get("/auth/me", response_model=Principal)
def me(principal: Principal = Depends(current_principal)) -> Principal:
    return principal


@router.get("/tenants/{tenant_slug}/access", response_model=Principal)
def tenant_access(
    principal: Principal = Depends(require_access("tenant:read")),
) -> Principal:
    return principal


@router.get("/tenants/{tenant_slug}/settings")
def tenant_settings_access(
    tenant_slug: str,
    principal: Principal = Depends(require_access("tenant:manage")),
) -> dict:
    """Permission tenant:manage — le registre est dans GET/PATCH /tenants/{slug}."""
    return {
        "ok": True,
        "tenant": tenant_slug,
        "editable": True,
        "actor": principal.subject,
    }
