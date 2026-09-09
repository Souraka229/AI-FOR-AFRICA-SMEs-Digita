"""FastAPI dependencies for JWT auth and RBAC."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from afrosite_api.auth.jwt import decode_access_token
from afrosite_api.auth.roles import Role
from afrosite_api.auth.schemas import UserPublic
from afrosite_api.common.settings import Settings, get_settings

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserPublic:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials, settings)
        return UserPublic(
            id=str(payload["sub"]),
            email=str(payload["email"]),
            role=Role(payload["role"]),
            tenant_id=str(payload["tenant_id"]),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def require_roles(*allowed: Role) -> Callable[[UserPublic], UserPublic]:
    allowed_set = set(allowed)

    def _checker(user: Annotated[UserPublic, Depends(get_current_user)]) -> UserPublic:
        if user.role not in allowed_set:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _checker
