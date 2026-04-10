"""test_phase_status.py: Tests for sdlc_core.phase_status CLI."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from sdlc_core.db import open_run, setup_db
from sdlc_core.phase_status import main


def _status_for_phase(db_path: Path, run_id: str, phase: int) -> str | None:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            """
            SELECT status
            FROM phase_progress
            WHERE run_id = ? AND phase_number = ?
            """,
            (run_id, phase),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return str(row[0])


def test_phase_status_sets_value_for_explicit_run(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-phase-01", db_path=db_path)

    with patch(
        "sys.argv",
        [
            "sdlc-phase-status",
            "--run-id",
            run_id,
            "--phase",
            "2",
            "--status",
            "in_progress",
            "--db",
            str(db_path),
        ],
    ):
        main()

    assert _status_for_phase(db_path, run_id, 2) == "in_progress"


def test_phase_status_defaults_to_latest_run(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    open_run(project="proj", approach=1, run_id="run-phase-old", db_path=db_path)
    run_id = open_run(project="proj", approach=1, run_id="run-phase-new", db_path=db_path)

    with patch(
        "sys.argv",
        [
            "sdlc-phase-status",
            "--phase",
            "3",
            "--status",
            "completed",
            "--db",
            str(db_path),
        ],
    ):
        main()

    assert _status_for_phase(db_path, run_id, 3) == "completed"


def test_phase_status_fails_when_no_runs(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")

    with patch(
        "sys.argv",
        [
            "sdlc-phase-status",
            "--phase",
            "2",
            "--status",
            "in_progress",
            "--db",
            str(db_path),
        ],
    ):
        with pytest.raises(SystemExit):
            main()
