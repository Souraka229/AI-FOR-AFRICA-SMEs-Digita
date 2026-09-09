"""House PaymentProvider contract — business code never talks to a PSP SDK directly."""

from typing import Protocol, runtime_checkable

from afrosite_api.payments.types import (
    CreateTransactionRequest,
    CreateTransactionResult,
    VerifyTransactionRequest,
    VerifyTransactionResult,
)


@runtime_checkable
class PaymentProvider(Protocol):
    """PSP adapter contract (Genius Pay, FedaPay, KKiaPay, …)."""

    name: str

    async def create_transaction(self, request: CreateTransactionRequest) -> CreateTransactionResult:
        """Create a server-side transaction. Caller supplies recalculated amount + idempotency key."""

    async def verify(self, request: VerifyTransactionRequest) -> VerifyTransactionResult:
        """Confirm payment status server-side. Browser redirect alone proves nothing."""
