"""Déclenche un déploiement de preview Coolify. Jamais la production.

Contrat API vérifié sur `coollabsio/coolify` tag `v4.3.18` (openapi.json) :

    POST {base}/api/v1/deploy?uuid=<uuid>&pr=<n>&force=<bool>
        -> 200 {"deployments": [{"message", "resource_uuid", "deployment_uuid"}]}
    GET  {base}/api/v1/deployments/{deployment_uuid}
        -> 200 ApplicationDeploymentQueue (champ "status")

Authentification : en-tête `Authorization: Bearer <token>` (permission `deploy`).
Aucun secret n'est écrit dans le dépôt : tout vient de l'environnement.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_PREFIX = "/api/v1"
TERMINAL_STATUS = frozenset({"finished", "failed", "cancelled", "cancelled-by-user"})


class CoolifyError(RuntimeError):
    """Coolify a refusé la demande, ou la garde-fou preview l'a bloquée."""


class SkipDeploy(RuntimeError):
    """Secrets absents : on ne déploie pas, et ce n'est pas une erreur."""


def read_settings(env: dict[str, str]) -> dict[str, str]:
    """Lit les réglages depuis l'environnement, sans jamais les journaliser."""
    base_url = (env.get("COOLIFY_URL") or "").strip().rstrip("/")
    token = (env.get("COOLIFY_API_TOKEN") or "").strip()
    app_uuid = (env.get("COOLIFY_PREVIEW_APP_UUID") or "").strip()
    missing = [
        name
        for name, value in (
            ("COOLIFY_URL", base_url),
            ("COOLIFY_API_TOKEN", token),
            ("COOLIFY_PREVIEW_APP_UUID", app_uuid),
        )
        if not value
    ]
    if missing:
        raise SkipDeploy(f"secrets Coolify absents: {', '.join(missing)}")

    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise CoolifyError("COOLIFY_URL doit etre en https (http autorise seulement en local)")

    production_uuid = (env.get("COOLIFY_PRODUCTION_APP_UUID") or "").strip()
    if production_uuid and production_uuid == app_uuid:
        raise CoolifyError("refus: COOLIFY_PREVIEW_APP_UUID pointe sur l'application de production")
    return {"base_url": base_url, "token": token, "app_uuid": app_uuid}


def _request(url: str, token: str, *, method: str) -> dict:
    request = urllib.request.Request(url, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8") or "{}"
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise CoolifyError(f"Coolify a repondu {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise CoolifyError(f"Coolify injoignable: {error.reason}") from error
    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        raise CoolifyError("reponse Coolify illisible (JSON attendu)") from error


def trigger_deploy(settings: dict[str, str], *, pr: int | None, force: bool = False) -> dict:
    """Déclenche le déploiement et renvoie le premier déploiement créé."""
    query: dict[str, str] = {"uuid": settings["app_uuid"], "force": "true" if force else "false"}
    if pr is not None:
        if pr <= 0:
            raise CoolifyError("le numero de PR doit etre positif")
        query["pr"] = str(pr)
    url = f"{settings['base_url']}{API_PREFIX}/deploy?{urllib.parse.urlencode(query)}"
    payload = _request(url, settings["token"], method="POST")
    deployments = payload.get("deployments") or []
    if not deployments:
        raise CoolifyError("Coolify n'a cree aucun deploiement")
    return deployments[0]


def wait_for_status(
    settings: dict[str, str],
    deployment_uuid: str,
    *,
    timeout: float = 600.0,
    interval: float = 10.0,
    sleep=time.sleep,
) -> str:
    """Suit le déploiement jusqu'à un statut terminal, sans boucle infinie."""
    url = f"{settings['base_url']}{API_PREFIX}/deployments/{deployment_uuid}"
    deadline = time.monotonic() + timeout
    status = "unknown"
    while time.monotonic() < deadline:
        status = str(_request(url, settings["token"], method="GET").get("status") or "unknown")
        if status in TERMINAL_STATUS:
            return status
        sleep(interval)
    raise CoolifyError(f"deploiement toujours '{status}' apres {timeout:.0f}s")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deploie une preview Coolify (jamais la prod).")
    parser.add_argument("--pr", type=int, default=None, help="numero de pull request")
    parser.add_argument("--force", action="store_true", help="rebuild sans cache")
    parser.add_argument("--wait", action="store_true", help="attendre un statut terminal")
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args(argv)

    try:
        settings = read_settings(dict(os.environ))
    except SkipDeploy as skip:
        print(f"preview Coolify ignoree ({skip}).")
        return 0
    except CoolifyError as error:
        print(f"preview Coolify refusee: {error}", file=sys.stderr)
        return 1

    try:
        deployment = trigger_deploy(settings, pr=args.pr, force=args.force)
        deployment_uuid = deployment.get("deployment_uuid", "")
        print(f"deploiement preview demande: {deployment_uuid} ({deployment.get('message', '')})")
        if args.wait and deployment_uuid:
            status = wait_for_status(settings, deployment_uuid, timeout=args.timeout)
            print(f"statut final: {status}")
            if status != "finished":
                return 1
    except CoolifyError as error:
        print(f"preview Coolify en echec: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
