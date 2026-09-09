"""Payment DTOs shared by providers."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class Currency(StrEnum):
    XOF = "XOF"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    REQUIRES_ACTION = "requires_action"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreateTransactionRequest(BaseModel):
    """Server-side transaction creation input (amounts always recalculated by caller)."""

    order_id: str
    amount_xof: Decimal = Field(gt=0)
    currency: Currency = Currency.XOF
    customer_phone: str | None = None
    description: str | None = None
    idempotency_key: str = Field(min_length=8)
    return_url: str | None = None


class CreateTransactionResult(BaseModel):
    provider_ref: str
    status: PaymentStatus
    checkout_url: str | None = None
    raw: dict[str, object] = Field(default_factory=dict)


class VerifyTransactionRequest(BaseModel):
    provider_ref: str
    expected_amount_xof: Decimal = Field(gt=0)
    expected_currency: Currency = Currency.XOF


class VerifyTransactionResult(BaseModel):
    provider_ref: str
    status: PaymentStatus
    amount_xof: Decimal
    currency: Currency
    raw: dict[str, object] = Field(default_factory=dict)
