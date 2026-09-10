"""Smoke du déclencheur de preview Coolify, contre un faux serveur local.

Aucun secret réel, aucune instance Coolify : le contrat HTTP est rejoué en
local (`http.server`) sur un port éphémère.
"""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deploy_preview import (  # noqa: E402
    CoolifyError,
    SkipDeploy,
    read_settings,
    trigger_deploy,
    wait_for_status,
)

CALLS: list[tuple[str, str, dict[str, list[str]]]] = []
STATUSES = ["in_progress", "in_progress", "finished"]


class Handler(BaseHTTPRequestHandler):
    def _dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        CALLS.append((method, parsed.path, parse_qs(parsed.query)))
        if self.headers.get("Authorization") != "Bearer jeton-de-test":
            return self._json(401, {"message": "Unauthenticated."})
        if method == "POST" and parsed.path == "/api/v1/deploy":
            return self._json(
                200,
                {
                    "deployments": [
                        {
                            "message": "Deployment request queued.",
                            "resource_uuid": "app-preview",
                            "deployment_uuid": "dep-123",
                        }
                    ]
                },
            )
        if method == "GET" and parsed.path.startswith("/api/v1/deployments/"):
            return self._json(200, {"status": STATUSES.pop(0) if STATUSES else "finished"})
        return self._json(404, {"message": "Not found."})

    def do_POST(self) -> None:  # noqa: N802 - imposé par BaseHTTPRequestHandler
        self._dispatch("POST")

    def do_GET(self) -> None:  # noqa: N802 - imposé par BaseHTTPRequestHandler
        self._dispatch("GET")

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args) -> None:
        return


def expect_error(run, fragment: str, label: str) -> None:
    try:
        run()
    except (CoolifyError, SkipDeploy) as error:
        assert fragment in str(error), f"{label}: message inattendu -> {error}"
        return
    raise AssertionError(f"{label}: aucun refus alors qu'il en fallait un")


def main() -> None:
    server = HTTPServer(("127.0.0.1", 0), Handler)
    base_url = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = {
            "COOLIFY_URL": base_url,
            "COOLIFY_API_TOKEN": "jeton-de-test",
            "COOLIFY_PREVIEW_APP_UUID": "app-preview",
        }
        settings = read_settings(env)
        assert settings["base_url"] == base_url

        expect_error(
            lambda: read_settings({"COOLIFY_URL": base_url}),
            "secrets Coolify absents",
            "secrets absents",
        )
        expect_error(
            lambda: read_settings({**env, "COOLIFY_PRODUCTION_APP_UUID": "app-preview"}),
            "production",
            "uuid de production",
        )
        expect_error(
            lambda: read_settings({**env, "COOLIFY_URL": "http://coolify.example"}),
            "https",
            "url non chiffree",
        )

        deployment = trigger_deploy(settings, pr=42)
        assert deployment["deployment_uuid"] == "dep-123"
        method, path, query = CALLS[-1]
        assert (method, path) == ("POST", "/api/v1/deploy"), (method, path)
        assert query["uuid"] == ["app-preview"]
        assert query["pr"] == ["42"]
        assert query["force"] == ["false"]

        expect_error(lambda: trigger_deploy(settings, pr=0), "positif", "pr invalide")

        status = wait_for_status(settings, "dep-123", interval=0, sleep=lambda _seconds: None)
        assert status == "finished", status
        assert [call[1] for call in CALLS].count("/api/v1/deployments/dep-123") == 3

        expect_error(
            lambda: trigger_deploy({**settings, "token": "mauvais-jeton"}, pr=1),
            "401",
            "jeton refuse",
        )

        expect_error(
            lambda: wait_for_status(
                settings, "dep-123", timeout=0, interval=0, sleep=lambda _seconds: None
            ),
            "apres 0s",
            "timeout borne",
        )
    finally:
        server.shutdown()
        server.server_close()

    print(
        "check:coolify OK - deploy pr=42 - suivi statut - secrets absents - "
        "prod refusee - http refuse - 401 - timeout borne"
    )


if __name__ == "__main__":
    main()
