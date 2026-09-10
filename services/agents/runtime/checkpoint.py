"""Checkpointer : mémoire en test, Postgres en environnement durable."""

from __future__ import annotations

import os
from contextlib import contextmanager

from langgraph.checkpoint.memory import MemorySaver


@contextmanager
def checkpointer():
    url = os.environ.get("AGENTS_DATABASE_URL", "")
    if not url.startswith("postgres"):
        yield MemorySaver()
        return

    from langgraph.checkpoint.postgres import PostgresSaver

    with PostgresSaver.from_conn_string(url) as saver:
        saver.setup()
        yield saver
