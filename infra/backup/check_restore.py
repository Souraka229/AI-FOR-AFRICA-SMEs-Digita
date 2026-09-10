"""Smoke DoD §13.3 : dump Postgres puis restauration dans une base jetable.

Utilise pg_dump/pg_restore du conteneur compose `postgres` (image postgres:16.6).
Aucun mot de passe n'est imprimé.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

COMPOSE_FILE = Path(__file__).resolve().parents[1] / "docker-compose.yml"
SERVICE = "postgres"
USER = "afrosite"
SOURCE_DB = "afrosite"
RESTORE_DB = "afrosite_restore_smoke"
DUMP_PATH = "/tmp/afrosite_restore_smoke.dump"
CANARY_TABLE = "_backup_canary"


class BackupError(RuntimeError):
    """Le dump ou la restauration a échoué."""


def run_psql(database: str, sql: str) -> str:
    completed = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(COMPOSE_FILE),
            "exec",
            "-T",
            SERVICE,
            "psql",
            "-U",
            USER,
            "-d",
            database,
            "-v",
            "ON_ERROR_STOP=1",
            "-tAc",
            sql,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise BackupError(completed.stderr.strip() or completed.stdout.strip() or "psql a échoué")
    return completed.stdout.strip()


def run_in_postgres(args: list[str]) -> None:
    completed = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "exec", "-T", SERVICE, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise BackupError(
            completed.stderr.strip() or completed.stdout.strip() or "commande postgres"
        )


def main() -> int:
    try:
        ready = run_psql("postgres", "SELECT 1")
        if ready != "1":
            raise BackupError("postgres ne répond pas")

        run_psql(
            SOURCE_DB,
            f"DROP TABLE IF EXISTS {CANARY_TABLE};"
            f"CREATE TABLE {CANARY_TABLE} (id int PRIMARY KEY, note text NOT NULL);"
            f"INSERT INTO {CANARY_TABLE}(id, note) VALUES (1, 'restore-smoke');",
        )
        run_in_postgres(["pg_dump", "-U", USER, "-d", SOURCE_DB, "-Fc", "-f", DUMP_PATH])
        run_psql("postgres", f"DROP DATABASE IF EXISTS {RESTORE_DB};")
        run_psql("postgres", f"CREATE DATABASE {RESTORE_DB};")
        run_in_postgres(["pg_restore", "-U", USER, "-d", RESTORE_DB, "--no-owner", DUMP_PATH])
        note = run_psql(RESTORE_DB, f"SELECT note FROM {CANARY_TABLE} WHERE id = 1;")
        if note != "restore-smoke":
            raise BackupError(f"canari absent après restore (reçu {note!r})")
    except BackupError as error:
        print(f"check:backup FAIL — {error}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("check:backup FAIL — docker introuvable", file=sys.stderr)
        return 1
    finally:
        try:
            run_psql("postgres", f"DROP DATABASE IF EXISTS {RESTORE_DB};")
            run_psql(SOURCE_DB, f"DROP TABLE IF EXISTS {CANARY_TABLE};")
            run_in_postgres(["rm", "-f", DUMP_PATH])
        except BackupError:
            pass

    print("check:backup OK — pg_dump -Fc — restore base jetable — canari restore-smoke — nettoyage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
