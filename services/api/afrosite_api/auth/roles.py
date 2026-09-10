"""RBAC roles for Afrosite tenants."""

from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    CASHIER = "cashier"
    KITCHEN = "kitchen"
    CUSTOMER = "customer"
