"""Smoke : graphe, interruption humaine, reprise et blocage des gates."""

from __future__ import annotations

import tempfile
from pathlib import Path

from langgraph.types import Command

from runtime.code_agent import OPENHANDS_IMAGE, _overlay, _snapshot
from runtime.graph import build_graph
from runtime.tools import TOOL_WHITELISTS


class FakeTools:
    def classify_intent(self, prompt: str) -> dict:
        return {"vertical": "commerce", "summary": prompt}

    def build_blueprint(self, intent: dict) -> dict:
        return {
            "vertical": intent["vertical"],
            "country": "BJ",
            "currency": "XOF",
            "deployment_target": "preview",
        }

    def validate_blueprint(self, blueprint: dict) -> dict:
        return {
            "passed": blueprint["country"] == "BJ"
            and blueprint["currency"] == "XOF"
        }

    def generate_overlay(self, blueprint: dict) -> dict:
        return {"branch": "feature/generated-check", "files": ["copy.json"]}

    def scan_generated(self, artifact: dict) -> dict:
        return {"passed": artifact["files"] == ["copy.json"]}

    def run_checks(self, artifact: dict) -> dict:
        return {"passed": artifact["branch"].startswith("feature/generated-")}

    def create_preview(self, artifact: dict) -> dict:
        return {"url": "https://preview.invalid/check", "production": False}


def main() -> None:
    assert TOOL_WHITELISTS["code"] == frozenset({"generate_overlay"})
    graph = build_graph(FakeTools())
    config = {"configurable": {"thread_id": "smoke-approved"}}
    paused = graph.invoke({"prompt": "Boutique wax à Cadjehoun"}, config)
    assert paused["stage"] == "gate1"
    assert paused["__interrupt__"][0].value["type"] == "blueprint_approval"

    finished = graph.invoke(Command(resume=True), config)
    assert finished["stage"] == "preview"
    assert finished["preview"]["production"] is False

    rejected_config = {"configurable": {"thread_id": "smoke-rejected"}}
    graph.invoke({"prompt": "Maquis à Fidjrossè"}, rejected_config)
    rejected = graph.invoke(Command(resume=False), rejected_config)
    assert rejected["stage"] == "rejected"
    assert "artifact" not in rejected

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "page.tsx").write_text(
            "export const title = 'Avant';\n", encoding="utf-8"
        )
        (root / "package.json").write_text(
            '{"scripts":{"bad":"ignored"}}', encoding="utf-8"
        )
        before = _snapshot(root)
        (root / "page.tsx").write_text(
            "export const title = 'Après';\n", encoding="utf-8"
        )
        overlay = _overlay(before, root, "feature/generated-smoke")
        assert overlay.files == ("page.tsx",)
        assert "Après" in overlay.diff
        assert OPENHANDS_IMAGE.endswith(
            "sha256:d98aabf32c29de5d4e78040fe2b80e44dc7513ebd8678a19cc05bc0b79eb7ed6"
        )

    print(
        "check:agents OK · checkpoint · interrupt · reprise · overlay · preview"
    )


if __name__ == "__main__":
    main()
