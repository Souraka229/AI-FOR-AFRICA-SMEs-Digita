"""Smoke des outils réels : NDJSON Studio, Gate 1 Python, garde-fous, QA."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import httpx
from runtime.adapters import StudioClient, StudioError, StudioTools


def blueprint(**overrides) -> dict:
    base = {
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
            "activity_description": "Boutique de tissus wax à Cadjehoun.",
        },
        "roles": ["owner", "cashier", "customer"],
        "modules": {
            "core": [
                "onboarding",
                "catalog",
                "orders",
                "payments",
                "reconciliation",
            ],
            "extra": ["stock"],
        },
        "catalog": [
            {
                "sku": "wax-6y",
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
            "title": "Wax Cadjehoun",
            "description": "Pagnes wax à Cotonou, paiement Mobile Money.",
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
    base.update(overrides)
    return base


PROMPT = "boutique de tissus wax à Cadjehoun, livraison quartier"
INTENT = {
    "raw_prompt": PROMPT,
    "vertical": "commerce",
    "confidence": 0.93,
    "city": "Cotonou",
    "neighborhood": "Cadjehoun",
    "wants_mobile_money": True,
    "wants_delivery": True,
    "wants_whatsapp": True,
    "activity_summary": "Boutique de tissus wax à Cadjehoun.",
    "suggested_name": "Wax Cadjehoun",
    "flags": ["payment_native"],
}


def ndjson(*events: dict) -> bytes:
    return "".join(f"{json.dumps(event)}\n" for event in events).encode("utf-8")


def studio_transport(*, fail: bool = False) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/studio/run":
            if fail:
                return httpx.Response(
                    200,
                    content=ndjson(
                        {"type": "step", "id": "intent", "status": "running"},
                        {"type": "error", "message": "LLM non configuré"},
                    ),
                )
            return httpx.Response(
                200,
                content=ndjson(
                    {"type": "step", "id": "intent", "status": "done"},
                    {
                        "type": "result",
                        "runId": "run-smoke",
                        "promptHash": "hash",
                        "intent": INTENT,
                        "blueprint": blueprint(),
                        "gate1": {
                            "passed": True,
                            "errors": [],
                            "credits": 8,
                            "budget_credits_max": 20,
                        },
                        "audit": [],
                        "usage": {},
                    },
                ),
            )
        if request.url.path == "/api/studio/preview":
            return httpx.Response(
                200,
                json={
                    "href": "/t/cadjehoun-wax",
                    "slug": "cadjehoun-wax",
                    "version": "v1",
                },
            )
        return httpx.Response(404, json={"error": "route inconnue"})

    return httpx.MockTransport(handler)


def tools(*, fail: bool = False, qa: tuple[tuple[str, ...], ...] | None = None):
    return StudioTools(
        client=StudioClient(access_key="cle-de-test", transport=studio_transport(fail=fail)),
        template_root=Path(tempfile.gettempdir()),
        qa_commands=qa if qa is not None else ((sys.executable, "-c", "pass"),),
    )


def main() -> None:
    real = tools()
    intent = real.classify_intent(PROMPT)
    assert intent["run_id"] == "run-smoke"
    assert intent["vertical"] == "commerce"

    generated = real.build_blueprint(intent)
    assert generated["tenant"]["slug"] == "cadjehoun-wax"
    assert real.validate_blueprint(generated) == {"passed": True, "errors": []}

    production = real.validate_blueprint(blueprint(deployment_target="production"))
    assert production["passed"] is False

    sensitive = real.validate_blueprint(
        blueprint(gates={"budget_credits_max": 20, "contains_sensitive_data": True})
    )
    assert sensitive["passed"] is False
    assert any("gate 1" in message for message in sensitive["errors"])

    over_budget = real.validate_blueprint(
        blueprint(
            estimated_cost_credits=40,
            gates={"budget_credits_max": 20, "contains_sensitive_data": False},
        )
    )
    assert over_budget["passed"] is False

    blocked = real.scan_generated(
        {
            "files": [".github/workflows/backdoor.yml", "src/app/page.tsx"],
            "diff": "+ paymentStatus = 'confirmed'",
        }
    )
    assert blocked["passed"] is False
    assert len(blocked["errors"]) == 2

    clean = real.scan_generated({"files": ["src/app/page.tsx"], "diff": "+ const title = 'Wax';"})
    assert clean["passed"] is True

    qa_ok = real.run_checks({"branch": "feature/generated-smoke"})
    assert qa_ok["passed"] is True
    qa_ko = tools(qa=((sys.executable, "-c", "raise SystemExit(1)"),)).run_checks(
        {"branch": "feature/generated-smoke"}
    )
    assert qa_ko["passed"] is False

    preview = real.create_preview({"blueprint": generated})
    assert preview == {
        "url": "/t/cadjehoun-wax",
        "slug": "cadjehoun-wax",
        "version": "v1",
        "production": False,
    }

    try:
        real.create_preview({"blueprint": blueprint(deployment_target="production")})
    except StudioError:
        pass
    else:  # pragma: no cover - garde-fou
        raise AssertionError("production non bloquée")

    release = real.prepare_release(
        {
            "artifact": {"branch": "feature/generated-smoke", "blueprint": generated},
            "preview": preview,
            "blueprint": generated,
        }
    )
    assert release["production"] is False
    assert release["coolify"] is False
    assert release["gate6"]["passed"] is False
    assert release["preview_url"] == "/t/cadjehoun-wax"

    try:
        real.prepare_release(
            {
                "artifact": {"branch": "feature/generated-smoke"},
                "preview": preview,
                "blueprint": blueprint(deployment_target="production"),
            }
        )
    except StudioError:
        pass
    else:  # pragma: no cover - garde-fou
        raise AssertionError("prepare_release production non bloquée")

    try:
        real.prepare_release(
            {
                "artifact": {"branch": "feature/generated-smoke"},
                "preview": {"url": "/t/cadjehoun-wax", "production": True},
                "blueprint": generated,
            }
        )
    except StudioError:
        pass
    else:  # pragma: no cover - garde-fou
        raise AssertionError("preview production non bloquée")

    try:
        tools(fail=True).classify_intent(PROMPT)
    except StudioError as error:
        assert "LLM non configuré" in str(error)
    else:  # pragma: no cover - garde-fou
        raise AssertionError("erreur Studio non propagée")

    print(
        "check:adapters OK · NDJSON · Gate 1 Pydantic · garde-fous partagés · QA · preview · release"
    )


if __name__ == "__main__":
    main()
