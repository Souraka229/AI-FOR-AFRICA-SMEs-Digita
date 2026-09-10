"""Garde-fous de génération — lit le même JSON que la version TypeScript."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

GUARDRAILS_FILE = (
    Path(__file__).resolve().parents[2] / "generation-guardrails.json"
)


@dataclass(frozen=True)
class QualityCheck:
    passed: bool
    errors: tuple[str, ...]


@cache
def _guardrails() -> dict:
    return json.loads(GUARDRAILS_FILE.read_text(encoding="utf-8"))


def guardrails_version() -> str:
    return _guardrails()["schema_version"]


def scan_generated_artifact(
    *, files: tuple[str, ...] | list[str], diff: str
) -> QualityCheck:
    rules = _guardrails()
    errors: list[str] = []
    denied_path = re.compile(rules["denied_path_pattern"], re.IGNORECASE)
    for path in files:
        if denied_path.search(path.replace("\\", "/")):
            errors.append(f"{rules['denied_path_message']}: {path}")
    for entry in rules["denied_diff_patterns"]:
        if re.search(entry["pattern"], diff, re.IGNORECASE):
            errors.append(entry["message"])
    return QualityCheck(passed=not errors, errors=tuple(errors))
