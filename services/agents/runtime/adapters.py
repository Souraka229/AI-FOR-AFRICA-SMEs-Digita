"""Outils réels du graphe : web pour générer, Python pour revalider."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "packages" / "contracts" / "python"))

from afrosite_contracts import (  # noqa: E402
    Blueprint,
    scan_generated_artifact,
)

from runtime.code_agent import generate_overlay  # noqa: E402

DEFAULT_QA_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("pnpm", "--filter", "@afrosite/contracts", "check"),
    ("pnpm", "--filter", "web", "eval:agents"),
    ("pnpm", "--filter", "web", "eval:llm"),
    ("pnpm", "--filter", "web", "lint"),
)


class StudioError(RuntimeError):
    """Le Studio a refusé ou interrompu la génération."""


@dataclass
class StudioClient:
    """Client NDJSON du Studio. Aucune clé PSP ne transite ici."""

    base_url: str = "http://127.0.0.1:3000"
    access_key: str | None = None
    timeout: float = 180.0
    transport: httpx.BaseTransport | None = None

    @classmethod
    def from_env(cls) -> StudioClient:
        return cls(
            base_url=os.environ.get("STUDIO_BASE_URL", "http://127.0.0.1:3000"),
            access_key=os.environ.get("AFROSITE_STUDIO_ACCESS_KEY"),
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_key:
            headers["Authorization"] = f"Bearer {self.access_key}"
        return headers

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=self.transport,
            headers=self._headers(),
        )

    def run_pipeline(self, prompt: str) -> dict:
        """Consomme /api/studio/run et renvoie l'événement `result`."""
        with (
            self._client() as client,
            client.stream("POST", "/api/studio/run", json={"prompt": prompt}) as response,
        ):
            if response.status_code != 200:
                response.read()
                raise StudioError(f"Studio HTTP {response.status_code}: {response.text}")
            result: dict | None = None
            for line in response.iter_lines():
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("type") == "error":
                    raise StudioError(event.get("message", "erreur Studio"))
                if event.get("type") == "result":
                    result = event
        if result is None:
            raise StudioError("le Studio n'a produit aucun résultat")
        return result

    def create_preview(self, blueprint: dict) -> dict:
        with self._client() as client:
            response = client.post(
                "/api/studio/preview",
                json={"blueprint": blueprint, "capture": True},
            )
            if response.status_code != 200:
                raise StudioError(f"preview refusée ({response.status_code}): {response.text}")
            return response.json()


@dataclass
class StudioTools:
    """Implémente le protocole AgentTools sans jamais toucher à l'argent."""

    client: StudioClient
    template_root: Path
    repo_root: Path = REPO_ROOT
    qa_commands: tuple[tuple[str, ...], ...] = DEFAULT_QA_COMMANDS
    qa_timeout: float = 900.0
    _runs: dict[str, dict] = field(default_factory=dict, repr=False)

    def classify_intent(self, prompt: str) -> dict:
        run = self.client.run_pipeline(prompt)
        self._runs[prompt] = run
        intent = dict(run["intent"])
        intent["run_id"] = run["runId"]
        return intent

    def build_blueprint(self, intent: dict) -> dict:
        run = self._runs.get(intent["raw_prompt"])
        if run is None:
            raise StudioError("aucun run Studio pour cette intention")
        return run["blueprint"]

    def validate_blueprint(self, blueprint: dict) -> dict:
        """Second avis Python : le miroir Pydantic porte aussi Gate 1."""
        try:
            parsed = Blueprint.model_validate(blueprint)
        except ValidationError as error:
            return {
                "passed": False,
                "errors": [
                    f"{'.'.join(str(part) for part in issue['loc'])}: {issue['msg']}"
                    for issue in error.errors()
                ],
            }
        if parsed.deployment_target != "preview":
            return {
                "passed": False,
                "errors": ["seule la cible preview est autorisée sans approbation"],
            }
        return {"passed": True, "errors": []}

    def generate_overlay(self, blueprint: dict) -> dict:
        run_id = next(
            (
                run["runId"]
                for run in self._runs.values()
                if run["blueprint"]["tenant"]["slug"] == blueprint["tenant"]["slug"]
            ),
            blueprint["tenant"]["slug"],
        )
        overlay = generate_overlay(
            blueprint=blueprint,
            run_id=run_id,
            template_root=self.template_root,
        )
        return {
            "branch": overlay.branch,
            "files": list(overlay.files),
            "diff": overlay.diff,
            "bytes": overlay.bytes,
            "image": overlay.image,
            "blueprint": blueprint,
        }

    def scan_generated(self, artifact: dict) -> dict:
        check = scan_generated_artifact(files=artifact["files"], diff=artifact["diff"])
        return {"passed": check.passed, "errors": list(check.errors)}

    def run_checks(self, artifact: dict) -> dict:
        results: list[dict] = []
        for command in self.qa_commands:
            executable = shutil.which(command[0])
            if executable is None:
                results.append({"command": " ".join(command), "exit_code": None, "passed": False})
                continue
            completed = subprocess.run(  # noqa: S603 — commandes fixes, sans shell
                [executable, *command[1:]],
                cwd=self.repo_root,
                capture_output=True,
                timeout=self.qa_timeout,
                check=False,
            )
            results.append(
                {
                    "command": " ".join(command),
                    "exit_code": completed.returncode,
                    "passed": completed.returncode == 0,
                }
            )
        return {
            "passed": bool(results) and all(row["passed"] for row in results),
            "results": results,
            "branch": artifact["branch"],
        }

    def create_preview(self, artifact: dict) -> dict:
        blueprint = artifact["blueprint"]
        if blueprint["deployment_target"] != "preview":
            raise StudioError("le graphe ne déploie jamais en production")
        created = self.client.create_preview(blueprint)
        preview = {
            "url": created["href"],
            "slug": created.get("slug"),
            "version": created.get("version"),
            "production": False,
        }
        if created.get("captures"):
            preview["captures"] = created["captures"]
        if created.get("captureError"):
            preview["captureError"] = created["captureError"]
        return preview
