"""conftest.py: Shared pytest fixtures and query helpers for sdlc_core tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from sdlc_core.db import open_run, setup_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    """Freshly initialised experiment.db in a per-test temp directory."""
    return setup_db(tmp_path / "experiment.db")


@pytest.fixture()
def run_id(db_path: Path) -> str:
    """Open a run inside the test database and return its ID."""
    return open_run(project="proj", approach=1, run_id="run-001", db_path=db_path)


# ---------------------------------------------------------------------------
# Query helpers (used by multiple test modules)
# ---------------------------------------------------------------------------


def q_one(db_path: Path, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    """Run *sql* and return the first row, or None."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchone()  # type: ignore[no-any-return]
    finally:
        conn.close()


def q_count(db_path: Path, table: str, where: str = "1=1", params: tuple[Any, ...] = ()) -> int:
    """Return the row count from *table* filtered by *where*."""
    conn = sqlite3.connect(db_path)
    try:
        result = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {where}", params
        ).fetchone()
        return int(result[0])
    finally:
        conn.close()
