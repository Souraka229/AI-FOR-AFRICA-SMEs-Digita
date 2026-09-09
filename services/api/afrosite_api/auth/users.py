"""In-memory user store for auth smoke (replaced by DB in core-schema)."""

from dataclasses import dataclass

from afrosite_api.auth.passwords import hash_password
from afrosite_api.auth.roles import Role
from afrosite_api.common.settings import Settings


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: str
    email: str
    password_hash: str
    role: Role
    tenant_id: str


def build_bootstrap_users(settings: Settings) -> dict[str, UserRecord]:
    owner = UserRecord(
        id="user-owner-1",
        email=settings.bootstrap_owner_email.lower(),
        password_hash=hash_password(settings.bootstrap_owner_password),
        role=Role.OWNER,
        tenant_id="tenant-demo-1",
    )
    cashier = UserRecord(
        id="user-cashier-1",
        email="cashier@afrosite.example",
        password_hash=hash_password("change-me-cashier"),
        role=Role.CASHIER,
        tenant_id="tenant-demo-1",
    )
    return {owner.email: owner, cashier.email: cashier}
