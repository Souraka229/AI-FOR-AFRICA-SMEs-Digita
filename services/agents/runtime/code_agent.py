"""Code Agent OpenHands : copie éphémère, Docker, overlay contrôlé."""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from pydantic import SecretStr


OPENHANDS_IMAGE = (
    "ghcr.io/openhands/agent-server"
    "@sha256:d98aabf32c29de5d4e78040fe2b80e44dc7513ebd8678a19cc05bc0b79eb7ed6"
)
ALLOWED_SUFFIXES = {".css", ".json", ".md", ".svg", ".ts", ".tsx"}
DENIED_PARTS = {".env", ".git", ".github", ".next", "node_modules"}
MAX_ARTIFACT_BYTES = 2_000_000


@dataclass(frozen=True)
class GeneratedOverlay:
    branch: str
    files: tuple[str, ...]
    diff: str
    bytes: int
    image: str = OPENHANDS_IMAGE


def _safe_run_id(run_id: str) -> str:
    safe = re.sub(r"[^a-z0-9-]+", "-", run_id.lower()).strip("-")[:48]
    if not safe:
        raise ValueError("run_id invalide")
    return safe


def _eligible(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return (
        path.is_file()
        and not path.is_symlink()
        and path.suffix in ALLOWED_SUFFIXES
        and not any(part in DENIED_PARTS or part.startswith(".env") for part in relative.parts)
        and path.name not in {"package.json", "pnpm-lock.yaml"}
    )


def _snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if _eligible(path, root):
            result[path.relative_to(root).as_posix()] = path.read_text(
                encoding="utf-8"
            )
    return result


def _overlay(before: dict[str, str], root: Path, branch: str) -> GeneratedOverlay:
    after = _snapshot(root)
    changed = sorted(
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    )
    byte_count = sum(len(after.get(key, "").encode("utf-8")) for key in changed)
    if byte_count > MAX_ARTIFACT_BYTES:
        raise ValueError("overlay OpenHands trop volumineux")
    chunks: list[str] = []
    for key in changed:
        chunks.extend(
            difflib.unified_diff(
                before.get(key, "").splitlines(keepends=True),
                after.get(key, "").splitlines(keepends=True),
                fromfile=f"a/{key}",
                tofile=f"b/{key}",
            )
        )
    return GeneratedOverlay(branch, tuple(changed), "".join(chunks), byte_count)


def generate_overlay(
    *,
    blueprint: dict,
    run_id: str,
    template_root: Path,
) -> GeneratedOverlay:
    """Exécute OpenHands sans monter le dépôt et ne renvoie qu'un diff."""
    api_key = os.environ.get("OPENHANDS_LLM_API_KEY")
    base_url = os.environ.get("OPENHANDS_LLM_BASE_URL")
    model = os.environ.get("OPENHANDS_LLM_MODEL")
    if not api_key or not base_url or not model:
        raise RuntimeError(
            "OPENHANDS_LLM_API_KEY, OPENHANDS_LLM_BASE_URL et "
            "OPENHANDS_LLM_MODEL sont requis (jeton LiteLLM limité)."
        )

    from openhands.sdk import Agent, Conversation, LLM, Tool
    from openhands.tools.file_editor import FileEditorTool
    from openhands.tools.task_tracker import TaskTrackerTool
    from openhands.workspace import DockerWorkspace

    branch = f"feature/generated-{_safe_run_id(run_id)}"
    with tempfile.TemporaryDirectory(prefix="afrosite-overlay-") as temporary:
        workspace_root = Path(temporary) / "workspace"
        shutil.copytree(
            template_root,
            workspace_root,
            ignore=shutil.ignore_patterns(
                ".env*",
                ".git",
                ".next",
                "node_modules",
                "pnpm-lock.yaml",
            ),
        )
        (workspace_root / "blueprint.generated.json").write_text(
            json.dumps(blueprint, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        before = _snapshot(workspace_root)

        llm = LLM(
            model=model,
            base_url=base_url,
            api_key=SecretStr(api_key),
            service_id="afrosite-code-agent",
        )
        agent = Agent(
            llm=llm,
            tools=[
                Tool(name=FileEditorTool.name),
                Tool(name=TaskTrackerTool.name),
            ],
        )
        volume = f"{workspace_root.resolve()}:/workspace:rw"
        with DockerWorkspace(
            server_image=OPENHANDS_IMAGE,
            volumes=[volume],
            forward_env=[],
        ) as docker_workspace:
            conversation = Conversation(agent=agent, workspace=docker_workspace)
            try:
                conversation.send_message(
                    "Lis blueprint.generated.json. Personnalise uniquement les "
                    "fichiers TS/TSX/CSS/JSON/MD/SVG présents. Ne crée ni paiement, "
                    "ni secret, ni dépendance, ni migration. Reste en preview et "
                    "termine quand les textes et styles correspondent au Blueprint."
                )
                conversation.run()
            finally:
                conversation.close()

        return _overlay(before, workspace_root, branch)


def overlay_fingerprint(overlay: GeneratedOverlay) -> str:
    payload = json.dumps(asdict(overlay), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
