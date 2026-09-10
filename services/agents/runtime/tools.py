"""Contrats d'outils injectés : aucun agent ne reçoit un shell généraliste."""

from __future__ import annotations

from typing import Protocol

TOOL_WHITELISTS: dict[str, frozenset[str]] = {
    "intent": frozenset({"classify_intent"}),
    "architect": frozenset({"build_blueprint"}),
    "gate1": frozenset({"validate_blueprint"}),
    "code": frozenset({"generate_overlay"}),
    "security": frozenset({"scan_generated"}),
    "qa": frozenset({"run_checks"}),
    "preview": frozenset({"create_preview"}),
    "deployment": frozenset({"prepare_release"}),
}


class AgentTools(Protocol):
    def classify_intent(self, prompt: str) -> dict: ...

    def build_blueprint(self, intent: dict) -> dict: ...

    def validate_blueprint(self, blueprint: dict) -> dict: ...

    def generate_overlay(self, blueprint: dict) -> dict: ...

    def scan_generated(self, artifact: dict) -> dict: ...

    def run_checks(self, artifact: dict) -> dict: ...

    def create_preview(self, artifact: dict) -> dict: ...

    def prepare_release(self, payload: dict) -> dict: ...
