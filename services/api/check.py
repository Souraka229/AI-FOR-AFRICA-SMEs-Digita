"""Smoke Gate 1 côté API — à lancer depuis services/api : python check.py"""

from __future__ import annotations

import os
import time
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from fastapi.testclient import TestClient

os.environ.setdefault("AFROSITE_AUTH_SECRET", "test-only-auth-secret-32-bytes-minimum")
os.environ.setdefault("AFROSITE_AUTH_BOOTSTRAP_KEY", "test-only-bootstrap-key")
os.environ.pop("DATABASE_URL", None)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auth.service import ALGORITHM, AUDIENCE, ISSUER  # noqa: E402
from dashboard import service as dashboard_service  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)

VALID = {
    "schema_version": "0.1.0",
    "vertical": "commerce",
    "project_type": "retail_storefront",
    "country": "BJ",
    "currency": "XOF",
    "locale": "fr-BJ",
    "tenant": {
        "name": "Wax Cadjehoun",
        "slug": "cadjehoun-wax",
        "city": "Cotonou",
        "neighborhood": "Cadjehoun",
        "country": "BJ",
        "activity_description": "Boutique de tissus wax à Cadjehoun, paiement Mobile Money.",
    },
    "roles": ["owner", "cashier", "customer"],
    "modules": {
        "core": [
            "onboarding",
            "catalog",
            "orders",
            "payments",
            "reconciliation",
            "crm",
            "dashboard",
            "notifications",
            "exports",
        ],
        "extra": ["stock"],
    },
    "catalog": [
        {
            "sku": "wax-cadjehoun-6y",
            "name": "Pagne wax 6 yards",
            "price_xof": 12500,
            "category": "tissus",
            "available": True,
        }
    ],
    "integrations": [
        {
            "category": "payment",
            "mode": "sandbox",
            "provider_candidates": ["geniuspay"],
        }
    ],
    "seo": {
        "title": "Wax Cadjehoun — tissus wax à Cotonou",
        "description": "Boutique de pagnes wax à Cadjehoun. Paiement Mobile Money en FCFA.",
        "schema_org_type": "Store",
    },
    "security_level": "standard",
    "deployment_target": "preview",
    "estimated_cost_credits": 8,
    "requires_confirmation": [
        "production_deploy",
        "payment_live_activation",
        "database_deletion",
    ],
    "gates": {"budget_credits_max": 20, "contains_sensitive_data": False},
}


def main() -> None:
    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json()["ok"] is True
    assert health.json()["blueprint_schema"] == "0.1.0"

    ok = client.post("/blueprints/validate", json=VALID)
    assert ok.status_code == 200, ok.text
    assert ok.json()["slug"] == "cadjehoun-wax"

    usd = {**VALID, "currency": "USD"}
    bad_currency = client.post("/blueprints/validate", json=usd)
    assert bad_currency.status_code == 422, bad_currency.text

    kitchen = {
        **VALID,
        "vertical": "restaurant",
        "roles": ["owner", "customer"],
        "seo": {
            **VALID["seo"],
            "schema_org_type": "Restaurant",
        },
    }
    bad_roles = client.post("/blueprints/validate", json=kitchen)
    assert bad_roles.status_code == 422, bad_roles.text

    over_budget = {
        **VALID,
        "estimated_cost_credits": 99,
        "gates": {"budget_credits_max": 20, "contains_sensitive_data": False},
    }
    bad_budget = client.post("/blueprints/validate", json=over_budget)
    assert bad_budget.status_code == 422, bad_budget.text

    assert health.json()["ledger"] == "memory"

    stamp = str(int(time.time() * 1000))
    created = client.post(
        "/payments",
        json={
            "tenant_slug": "cadjehoun-wax",
            "amount_xof": 24500,
            "channel": "mtn_momo",
            "idem_key": f"api-wax-24500-{stamp}",
        },
    )
    assert created.status_code == 200, created.text
    ref = created.json()["entry"]["reference"]
    replay = client.post(
        "/payments",
        json={
            "tenant_slug": "cadjehoun-wax",
            "amount_xof": 24500,
            "channel": "mtn_momo",
            "idem_key": f"api-wax-24500-{stamp}",
        },
    )
    assert replay.json()["entry"]["reference"] == ref

    verified = client.post(f"/payments/{ref}/verify")
    assert verified.status_code == 200
    assert verified.json()["entry"]["status"] == "confirmed"
    assert verified.json()["entry"]["verifiedServer"] is True

    again = client.post(f"/payments/{ref}/verify")
    assert again.json()["entry"]["status"] == "confirmed"

    failed = client.post(
        "/payments",
        json={
            "tenant_slug": "cadjehoun-wax",
            "amount_xof": 4000,
            "channel": "cash",
            "idem_key": f"api-fail-{stamp}",
        },
    )
    fail_ref = failed.json()["entry"]["reference"]
    client.post(f"/payments/{fail_ref}/fail")
    still = client.post(f"/payments/{fail_ref}/verify")
    assert still.json()["entry"]["status"] == "failed"

    forbidden = client.post(
        f"/payments/{ref}/refund",
        json={"amount_xof": 1000, "reason": "test cashier"},
        headers={"X-Afrosite-Role": "cashier"},
    )
    assert forbidden.status_code == 403, forbidden.text

    partial = client.post(
        f"/payments/{ref}/refund",
        json={"amount_xof": 4500, "reason": "geste commercial"},
        headers={"X-Afrosite-Role": "owner"},
    )
    assert partial.status_code == 200, partial.text
    assert partial.json()["entry"]["refundedAmountXof"] == 4500

    ledger = client.get("/ledger/cadjehoun-wax")
    assert ledger.status_code == 200
    assert any(row["reference"] == ref for row in ledger.json()["entries"])

    no_bootstrap = client.post(
        "/auth/token",
        json={
            "subject": "souraka",
            "tenant_slug": "cadjehoun-wax",
            "role": "owner",
        },
    )
    assert no_bootstrap.status_code == 401, no_bootstrap.text

    issued = client.post(
        "/auth/token",
        json={
            "subject": "souraka",
            "tenant_slug": "cadjehoun-wax",
            "role": "owner",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    assert issued.status_code == 201, issued.text
    owner_token = issued.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    me = client.get("/auth/me", headers=owner_headers)
    assert me.status_code == 200, me.text
    assert me.json()["role"] == "owner"
    assert "tenant:manage" in me.json()["permissions"]

    own_tenant = client.get("/tenants/cadjehoun-wax/access", headers=owner_headers)
    assert own_tenant.status_code == 200, own_tenant.text
    crossed = client.get("/tenants/maquis-fidjrosse/access", headers=owner_headers)
    assert crossed.status_code == 403, crossed.text

    customer = client.post(
        "/auth/token",
        json={
            "subject": "client-001",
            "tenant_slug": "cadjehoun-wax",
            "role": "customer",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    assert customer.status_code == 201, customer.text
    customer_headers = {
        "Authorization": f"Bearer {customer.json()['access_token']}"
    }
    forbidden_settings = client.get(
        "/tenants/cadjehoun-wax/settings",
        headers=customer_headers,
    )
    assert forbidden_settings.status_code == 403, forbidden_settings.text
    owner_settings = client.get(
        "/tenants/cadjehoun-wax/settings",
        headers=owner_headers,
    )
    assert owner_settings.status_code == 200, owner_settings.text

    now = datetime.now(timezone.utc)
    expired_token = jwt.encode(
        {
            "sub": "expired",
            "tenant": "cadjehoun-wax",
            "role": "owner",
            "iat": now - timedelta(minutes=10),
            "nbf": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
            "iss": ISSUER,
            "aud": AUDIENCE,
        },
        os.environ["AFROSITE_AUTH_SECRET"],
        algorithm=ALGORITHM,
    )
    expired = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired.status_code == 401, expired.text

    anonymous = client.get("/tenants/cadjehoun-wax")
    assert anonymous.status_code == 401, anonymous.text
    own = client.get("/tenants/cadjehoun-wax", headers=owner_headers)
    assert own.status_code == 200, own.text
    assert own.json()["name"] == "Wax Cadjehoun"
    leak = client.get("/tenants/maquis-fidjrosse", headers=owner_headers)
    assert leak.status_code == 403, leak.text

    created = client.post(
        "/tenants",
        json={
            "slug": "depot-akogbato",
            "name": "Dépôt Akogbato",
            "vertical": "commerce",
            "neighborhood": "Akogbato",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    assert created.status_code == 201, created.text
    again = client.post(
        "/tenants",
        json={
            "slug": "depot-akogbato",
            "name": "Dépôt Akogbato",
            "vertical": "commerce",
            "neighborhood": "Akogbato",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    assert again.status_code == 409, again.text

    depot_token = client.post(
        "/auth/token",
        json={
            "subject": "gerant-depot",
            "tenant_slug": "depot-akogbato",
            "role": "owner",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    depot_headers = {
        "Authorization": f"Bearer {depot_token.json()['access_token']}"
    }
    patched = client.patch(
        "/tenants/depot-akogbato",
        json={"name": "Dépôt Akogbato Express"},
        headers=depot_headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["name"] == "Dépôt Akogbato Express"
    customer_patch = client.patch(
        "/tenants/cadjehoun-wax",
        json={"name": "Hijack"},
        headers=customer_headers,
    )
    assert customer_patch.status_code == 403, customer_patch.text

    catalog = client.get("/tenants/cadjehoun-wax/catalog", headers=customer_headers)
    assert catalog.status_code == 200, catalog.text
    assert sum(item["price_xof"] for item in catalog.json()) == 24500
    assert all(item["currency"] == "XOF" for item in catalog.json())
    hijack_price = client.put(
        "/tenants/cadjehoun-wax/catalog/wax-cadjehoun-6y",
        json={
            "sku": "wax-cadjehoun-6y",
            "name": "Pagne",
            "price_xof": 1,
            "category": "tissus",
        },
        headers=customer_headers,
    )
    assert hijack_price.status_code == 403, hijack_price.text
    other_menu = client.get("/tenants/maquis-fidjrosse/catalog", headers=customer_headers)
    assert other_menu.status_code == 403, other_menu.text

    wax_order = client.post(
        "/tenants/cadjehoun-wax/orders",
        json={
            "idem_key": f"wax-24500-{stamp}",
            "items": [
                {"sku": "wax-cadjehoun-6y", "qty": 1},
                {"sku": "wax-fidjrosse-6y", "qty": 1},
                {"sku": "livraison-quartier", "qty": 1},
            ],
        },
        headers=customer_headers,
    )
    assert wax_order.status_code == 201, wax_order.text
    assert wax_order.json()["amount_xof"] == 24500
    replay_order = client.post(
        "/tenants/cadjehoun-wax/orders",
        json={
            "idem_key": f"wax-24500-{stamp}",
            "items": [{"sku": "wax-cadjehoun-6y", "qty": 9}],
        },
        headers=customer_headers,
    )
    assert replay_order.json()["id"] == wax_order.json()["id"]
    assert replay_order.json()["amount_xof"] == 24500
    unknown = client.post(
        "/tenants/cadjehoun-wax/orders",
        json={
            "idem_key": f"unknown-{stamp}",
            "items": [{"sku": "does-not-exist", "qty": 1}],
        },
        headers=customer_headers,
    )
    assert unknown.status_code == 400, unknown.text

    other_customer = client.post(
        "/auth/token",
        json={
            "subject": "client-002",
            "tenant_slug": "cadjehoun-wax",
            "role": "customer",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    other_headers = {
        "Authorization": f"Bearer {other_customer.json()['access_token']}"
    }
    hidden = client.get(
        f"/tenants/cadjehoun-wax/orders/{wax_order.json()['id']}",
        headers=other_headers,
    )
    assert hidden.status_code == 404, hidden.text
    owner_sees = client.get(
        f"/tenants/cadjehoun-wax/orders/{wax_order.json()['id']}",
        headers=owner_headers,
    )
    assert owner_sees.status_code == 200, owner_sees.text
    cancelled = client.post(
        f"/tenants/cadjehoun-wax/orders/{wax_order.json()['id']}/cancel",
        headers=owner_headers,
    )
    assert cancelled.json()["status"] == "cancelled"

    cashier = client.post(
        "/auth/token",
        json={
            "subject": "caisse-cadjehoun",
            "tenant_slug": "cadjehoun-wax",
            "role": "cashier",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    cashier_headers = {
        "Authorization": f"Bearer {cashier.json()['access_token']}"
    }
    phone = "22997001234"
    created_client = client.put(
        f"/tenants/cadjehoun-wax/crm/customers/{phone}",
        json={"display_name": "Aïcha Cadjehoun"},
        headers=cashier_headers,
    )
    assert created_client.status_code == 200, created_client.text
    assert created_client.json()["phone"] == "+22997001234"
    assert created_client.json()["loyalty_count"] == 0
    visit = client.post(
        f"/tenants/cadjehoun-wax/crm/customers/{phone}/visits",
        json={
            "idem_key": f"visit-wax-{stamp}",
            "order_id": wax_order.json()["id"],
        },
        headers=cashier_headers,
    )
    assert visit.status_code == 201, visit.text
    assert visit.json()["loyalty_count"] == 1
    assert visit.json()["visits"][0]["amount_xof"] == 24500
    replay_visit = client.post(
        f"/tenants/cadjehoun-wax/crm/customers/{phone}/visits",
        json={
            "idem_key": f"visit-wax-{stamp}",
            "order_id": wax_order.json()["id"],
        },
        headers=cashier_headers,
    )
    assert replay_visit.json()["loyalty_count"] == 1
    walk_in = client.post(
        f"/tenants/cadjehoun-wax/crm/customers/{phone}/visits",
        json={"idem_key": f"visit-walkin-{stamp}"},
        headers=cashier_headers,
    )
    assert walk_in.json()["loyalty_count"] == 2
    customer_crm = client.get(
        f"/tenants/cadjehoun-wax/crm/customers/{phone}",
        headers=customer_headers,
    )
    assert customer_crm.status_code == 403, customer_crm.text
    leak_crm = client.get(
        "/tenants/maquis-fidjrosse/crm/customers",
        headers=cashier_headers,
    )
    assert leak_crm.status_code == 403, leak_crm.text
    bad_phone = client.put(
        "/tenants/cadjehoun-wax/crm/customers/33123456789",
        json={"display_name": "Paris"},
        headers=cashier_headers,
    )
    assert bad_phone.status_code == 400, bad_phone.text

    live_order = client.post(
        "/tenants/cadjehoun-wax/orders",
        json={
            "idem_key": f"dash-wax-{stamp}",
            "items": [
                {"sku": "wax-cadjehoun-6y", "qty": 1},
                {"sku": "wax-fidjrosse-6y", "qty": 1},
                {"sku": "livraison-quartier", "qty": 1},
            ],
        },
        headers=customer_headers,
    )
    assert live_order.status_code == 201, live_order.text
    dash = client.get("/tenants/cadjehoun-wax/dashboard", headers=cashier_headers)
    assert dash.status_code == 200, dash.text
    body = dash.json()
    assert body["currency"] == "XOF"
    assert body["timezone"] == "Africa/Porto-Novo"
    assert "payé" not in str(body).lower()
    assert "paid" not in str(body).lower()
    assert body["activity_count"] == 1
    assert body["activity_xof"] == 24500
    assert body["average_basket_xof"] == 24500
    assert body["collected_xof"] == 20000
    assert body["top_items"][0]["sku"] == "wax-cadjehoun-6y"
    assert body["top_items"][0]["amount_xof"] == 12500
    assert body["late_orders"] == []
    previous_late = dashboard_service.LATE_AFTER
    dashboard_service.LATE_AFTER = timedelta(seconds=0)
    late = dashboard_service.snapshot("cadjehoun-wax")
    dashboard_service.LATE_AFTER = previous_late
    assert late["late_orders"][0]["id"] == live_order.json()["id"]
    customer_dash = client.get(
        "/tenants/cadjehoun-wax/dashboard",
        headers=customer_headers,
    )
    assert customer_dash.status_code == 403, customer_dash.text
    kitchen = client.post(
        "/auth/token",
        json={
            "subject": "cuisine",
            "tenant_slug": "cadjehoun-wax",
            "role": "kitchen",
        },
        headers={"X-Afrosite-Bootstrap-Key": "test-only-bootstrap-key"},
    )
    kitchen_dash = client.get(
        "/tenants/cadjehoun-wax/dashboard",
        headers={"Authorization": f"Bearer {kitchen.json()['access_token']}"},
    )
    assert kitchen_dash.status_code == 403, kitchen_dash.text
    leak_dash = client.get(
        "/tenants/maquis-fidjrosse/dashboard",
        headers=cashier_headers,
    )
    assert leak_dash.status_code == 403, leak_dash.text

    print(
        "check:api OK · Gate 1 + tenants + catalogue + commande 24500 FCFA + CRM + dashboard"
    )


if __name__ == "__main__":
    main()
