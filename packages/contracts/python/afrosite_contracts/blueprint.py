"""Miroir Pydantic du schéma Zod v0.1.0 — à régénérer si le Zod change."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

SCHEMA_VERSION = "0.1.0"
Vertical = Literal["commerce", "restaurant", "services"]
Role = Literal["owner", "cashier", "kitchen", "customer", "staff"]
CoreModule = Literal[
    "onboarding",
    "catalog",
    "orders",
    "payments",
    "reconciliation",
    "crm",
    "dashboard",
    "notifications",
    "exports",
]


class CatalogItem(BaseModel):
    sku: str
    name: str
    price_xof: int = Field(ge=0)
    category: str
    available: bool
    unit: str | None = None


class Tenant(BaseModel):
    name: str
    slug: str
    city: str
    neighborhood: str
    country: Literal["BJ"]
    phone: str | None = None
    activity_description: str


class Integration(BaseModel):
    category: Literal["payment", "whatsapp", "sms", "email"]
    mode: Literal["sandbox", "production"]
    provider_candidates: list[str]


class Seo(BaseModel):
    title: str
    description: str
    schema_org_type: Literal[
        "LocalBusiness", "Store", "Restaurant", "ProfessionalService"
    ]


class Modules(BaseModel):
    core: list[CoreModule]
    extra: list[str]


class Gates(BaseModel):
    budget_credits_max: int = Field(gt=0)
    contains_sensitive_data: bool


class Blueprint(BaseModel):
    schema_version: Literal["0.1.0"]
    vertical: Vertical
    project_type: str
    country: Literal["BJ"]
    currency: Literal["XOF"]
    locale: Literal["fr-BJ"]
    tenant: Tenant
    roles: list[Role]
    modules: Modules
    catalog: list[CatalogItem]
    integrations: list[Integration]
    seo: Seo
    security_level: Literal["standard", "elevated"]
    deployment_target: Literal["preview", "production"]
    estimated_cost_credits: int = Field(ge=0, le=100)
    requires_confirmation: list[str]
    gates: Gates

    @model_validator(mode="after")
    def gate_one(self) -> Blueprint:
        if self.estimated_cost_credits > self.gates.budget_credits_max:
            raise ValueError("budget IA au-dessus du plafond (gate 1)")
        if self.gates.contains_sensitive_data:
            raise ValueError("données sensibles détectées (gate 1)")
        if self.vertical == "restaurant" and "kitchen" not in self.roles:
            raise ValueError("le blueprint restaurant exige le rôle kitchen")
        return self
