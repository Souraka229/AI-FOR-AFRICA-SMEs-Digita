from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from temporalio.exceptions import ApplicationError


@dataclass
class AuditEvent:
    at: str
    agent: str
    action: str
    result: str
    tool: str = "provision_tenant"


class TenantPort(Protocol):
    async def upsert(
        self, slug: str, name: str, vertical: str, city: str, neighborhood: str
    ) -> dict[str, object]: ...

    async def mark_status(self, slug: str, status: str) -> None: ...


class CatalogPort(Protocol):
    async def seed(self, slug: str, lines: list[dict[str, object]]) -> int: ...


class PaymentSetupPort(Protocol):
    async def enable_sandbox(self, slug: str, channel: str) -> str: ...


class PreviewPort(Protocol):
    async def allocate(self, slug: str, deployment_target: str) -> dict[str, str]: ...


class AuditPort(Protocol):
    async def record(self, event: AuditEvent) -> int: ...


@dataclass
class InMemoryTenants:
    rows: dict[str, dict[str, object]] = field(default_factory=dict)

    async def upsert(
        self, slug: str, name: str, vertical: str, city: str, neighborhood: str
    ) -> dict[str, object]:
        existing = self.rows.get(slug)
        if existing is not None:
            return {**existing, "duplicated": True}
        row = {
            "tenant_id": f"ten_{slug}",
            "slug": slug,
            "name": name,
            "vertical": vertical,
            "city": city,
            "neighborhood": neighborhood,
            "country": "BJ",
            "status": "provisioning",
            "duplicated": False,
        }
        self.rows[slug] = row
        return row

    async def mark_status(self, slug: str, status: str) -> None:
        row = self.rows.get(slug)
        if row is None:
            return
        row["status"] = status


@dataclass
class InMemoryCatalog:
    by_slug: dict[str, list[dict[str, object]]] = field(default_factory=dict)

    async def seed(self, slug: str, lines: list[dict[str, object]]) -> int:
        bucket = self.by_slug.setdefault(slug, [])
        known = {str(item["sku"]) for item in bucket}
        for line in lines:
            sku = str(line["sku"])
            if sku in known:
                continue
            if int(line["price_xof"]) < 0:
                raise ApplicationError("Prix catalogue invalide.", non_retryable=True)
            bucket.append(dict(line))
            known.add(sku)
        return len(bucket)


@dataclass
class InMemoryPaymentSetup:
    modes: dict[str, str] = field(default_factory=dict)

    async def enable_sandbox(self, slug: str, channel: str) -> str:
        if channel not in {"mtn_momo", "moov_money", "cash"}:
            raise ApplicationError("Canal paiement inconnu.", non_retryable=True)
        self.modes[slug] = "sandbox"
        return "sandbox"


@dataclass
class InMemoryPreview:
    fail: bool = False
    allocations: list[dict[str, str]] = field(default_factory=list)

    async def allocate(self, slug: str, deployment_target: str) -> dict[str, str]:
        if deployment_target == "production":
            raise ApplicationError("Provisioning production interdit (gate 6).", non_retryable=True)
        if self.fail:
            raise ApplicationError("Preview indisponible.", non_retryable=True)
        for existing in self.allocations:
            if existing.get("slug") == slug:
                return {"href": existing["href"], "environment": existing["environment"]}
        row = {"href": f"/t/{slug}", "environment": "preview", "slug": slug}
        self.allocations.append(row)
        return {"href": row["href"], "environment": row["environment"]}


@dataclass
class InMemoryAudit:
    events: list[AuditEvent] = field(default_factory=list)

    async def record(self, event: AuditEvent) -> int:
        self.events.append(event)
        return len(self.events)


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
