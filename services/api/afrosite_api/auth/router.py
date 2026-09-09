"""Auth HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from afrosite_api.auth.deps import get_current_user, require_roles
from afrosite_api.auth.jwt import create_access_token
from afrosite_api.auth.passwords import verify_password
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import LoginRequest, TokenResponse, UserPublic
from afrosite_api.auth.users import ensure_bootstrap_users, get_user_by_email
from afrosite_api.common.settings import Settings, get_settings
from afrosite_api.db.session import get_db_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    body: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    await ensure_bootstrap_users(session, settings)
    user = await get_user_by_email(session, body.email)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(
        subject=user.id,
        email=user.email,
        role=Role(user.role),
        tenant_id=user.tenant_id,
        settings=settings,
    )
    return TokenResponse(access_token=token)


@router.get("/me")
async def me(user: Annotated[UserPublic, Depends(get_current_user)]) -> UserPublic:
    return user


@router.get("/owner-only")
async def owner_only(
    _user: Annotated[UserPublic, Depends(require_roles(Role.OWNER))],
) -> dict[str, str]:
    return {"status": "ok", "scope": "owner"}
