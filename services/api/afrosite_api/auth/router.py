"""Auth HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from afrosite_api.auth.deps import get_current_user, require_roles
from afrosite_api.auth.jwt import create_access_token
from afrosite_api.auth.passwords import verify_password
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import LoginRequest, TokenResponse, UserPublic
from afrosite_api.auth.users import UserRecord, build_bootstrap_users
from afrosite_api.common.settings import Settings, get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _users(settings: Settings) -> dict[str, UserRecord]:
    return build_bootstrap_users(settings)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    user = _users(settings).get(body.email.lower())
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(
        subject=user.id,
        email=user.email,
        role=user.role,
        tenant_id=user.tenant_id,
        settings=settings,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(user: Annotated[UserPublic, Depends(get_current_user)]) -> UserPublic:
    return user


@router.get("/owner-only")
async def owner_only(
    _user: Annotated[UserPublic, Depends(require_roles(Role.OWNER))],
) -> dict[str, str]:
    return {"status": "ok", "scope": "owner"}
