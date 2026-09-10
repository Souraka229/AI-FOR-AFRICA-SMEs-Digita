"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr, Field

from afrosite_api.auth.roles import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    role: Role
    tenant_id: str
