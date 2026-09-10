"""QA Agent : unitaires + Playwright + Gate 5, jamais la production."""

from __future__ import annotations

REQUIRED_E2E = ("studio", "storefront")
REQUIRED_VIEWPORTS = ("desktop", "mobile")


def run_qa_agent(artifact: dict) -> dict:
    errors: list[str] = []
    if artifact.get("production") or artifact.get("deployment_target") == "production":
        errors.append("QA Agent refuse une cible production (gate 6).")
    if not str(artifact.get("branch", "")).startswith("feature/generated-"):
        errors.append("branche générée hors feature/generated-*")
    if not artifact.get("unit_passed", False):
        errors.append("tests unitaires en échec")

    e2e = artifact.get("e2e") or {}
    for spec in REQUIRED_E2E:
        if not e2e.get(spec):
            errors.append(f"Playwright en échec : {spec}")
    for viewport in REQUIRED_VIEWPORTS:
        if not e2e.get(viewport):
            errors.append(f"Playwright viewport manquant : {viewport}")

    gate5 = artifact.get("gate5") or {}
    if not gate5.get("migrationOnCopy"):
        errors.append("Gate 5 : migration non testée sur une copie")
    if not gate5.get("backupVerified"):
        errors.append("Gate 5 : backup non vérifié")
    if not gate5.get("rollbackReady"):
        errors.append("Gate 5 : rollback non prêt")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "gate": "g5",
        "specs": list(REQUIRED_E2E),
    }
