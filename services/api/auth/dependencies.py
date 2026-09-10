"""Dépendances FastAPI : authentifier, isoler le tenant, autoriser."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from auth.schemas import Principal
from auth.service import AuthConfigurationError, decode_token

bearer = HTTPBearer(auto_error=False)


def current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token requis.")
    try:
        return decode_token(credentials.credentials)
    except AuthConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except InvalidTokenError as error:
        raise HTTPException(status_code=401, detail="Bearer token invalide ou expiré.") from error


def require_access(permission: str) -> Callable:
    def dependency(
        request: Request,
        principal: Principal = Depends(current_principal),
    ) -> Principal:
        tenant_slug = request.path_params.get("tenant_slug")
        if tenant_slug and principal.tenant_slug != tenant_slug:
            raise HTTPException(status_code=403, detail="Accès tenant croisé refusé.")
        if permission not in principal.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission requise : {permission}.",
            )
        return principal

    return dependency


def require_any(*permissions: str) -> Callable:
    needed = tuple(permissions)

    def dependency(
        request: Request,
        principal: Principal = Depends(current_principal),
    ) -> Principal:
        tenant_slug = request.path_params.get("tenant_slug")
        if tenant_slug and principal.tenant_slug != tenant_slug:
            raise HTTPException(status_code=403, detail="Accès tenant croisé refusé.")
        if not any(item in principal.permissions for item in needed):
            raise HTTPException(
                status_code=403,
                detail=f"Permission requise : {' ou '.join(needed)}.",
            )
        return principal

    return dependency
