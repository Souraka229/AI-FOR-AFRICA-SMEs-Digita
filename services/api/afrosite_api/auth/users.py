"""User persistence helpers backed by SQLAlchemy async sessions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from afrosite_api.auth.passwords import hash_password
from afrosite_api.auth.roles import Role
from afrosite_api.common.settings import Settings
from afrosite_api.db.models.tenant import Tenant
from afrosite_api.db.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def ensure_bootstrap_users(session: AsyncSession, settings: Settings) -> None:
    """Idempotently seed demo tenant + owner/cashier from env credentials."""
    tenant = await session.get(Tenant, settings.bootstrap_tenant_id)
    if tenant is None:
        session.add(Tenant(id=settings.bootstrap_tenant_id, name=settings.bootstrap_tenant_name))
        await session.flush()

    owner_email = settings.bootstrap_owner_email.lower()
    owner = await get_user_by_email(session, owner_email)
    if owner is None:
        session.add(
            User(
                id="user-owner-1",
                tenant_id=settings.bootstrap_tenant_id,
                email=owner_email,
                password_hash=hash_password(settings.bootstrap_owner_password),
                role=Role.OWNER.value,
            )
        )

    cashier_email = settings.bootstrap_cashier_email.lower()
    cashier = await get_user_by_email(session, cashier_email)
    if cashier is None:
        session.add(
            User(
                id="user-cashier-1",
                tenant_id=settings.bootstrap_tenant_id,
                email=cashier_email,
                password_hash=hash_password(settings.bootstrap_cashier_password),
                role=Role.CASHIER.value,
            )
        )

    await session.commit()
