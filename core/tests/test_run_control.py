"""test_run_control.py: Tests for sdlc_core.run_control commands."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import cast
from unittest.mock import patch

from sdlc_core.db import close_run, open_run, open_session, setup_db
from sdlc_core.run_control import abandon_main, pause_main, resume_main


def _row(db_path: Path, sql: str, params: tuple[object, ...]) -> sqlite3.Row | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(sql, params).fetchone()
        return cast(sqlite3.Row | None, row)
    finally:
        conn.close()


def test_pause_close_session_closes_open_session_and_logs_violation(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-rc-01", db_path=db_path)
    open_session(run_id=run_id, session_number=1, db_path=db_path)

    argv = [
        "sdlc-pause",
        "--run-id",
        run_id,
        "--reason",
        "free shared machine",
        "--close-session",
        "--db",
        str(db_path),
    ]
    with patch("sys.argv", argv):
        pause_main()

    session = _row(
        db_path,
        "SELECT ended_at FROM sessions WHERE run_id = ? AND session_number = 1",
        (run_id,),
    )
    assert session is not None
    assert session["ended_at"] is not None

    note = _row(
        db_path,
        "SELECT detail FROM violations WHERE run_id = ? ORDER BY id DESC LIMIT 1",
        (run_id,),
    )
    assert note is not None
    assert "Run paused" in str(note["detail"])


def test_pause_default_keeps_session_open(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-rc-01b", db_path=db_path)
    open_session(run_id=run_id, session_number=1, db_path=db_path)

    with patch(
        "sys.argv",
        ["sdlc-pause", "--run-id", run_id, "--db", str(db_path)],
    ):
        pause_main()

    session = _row(
        db_path,
        "SELECT ended_at FROM sessions WHERE run_id = ? AND session_number = 1",
        (run_id,),
    )
    assert session is not None
    assert session["ended_at"] is None


def test_resume_opens_next_session_and_logs_violation(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-rc-02", db_path=db_path)
    open_session(run_id=run_id, session_number=1, db_path=db_path)

    with patch(
        "sys.argv",
        ["sdlc-pause", "--run-id", run_id, "--close-session", "--db", str(db_path)],
    ):
        pause_main()

    with patch(
        "sys.argv",
        ["sdlc-resume", "--run-id", run_id, "--db", str(db_path)],
    ):
        resume_main()

    session2 = _row(
        db_path,
        "SELECT started_at, ended_at FROM sessions WHERE run_id = ? AND session_number = 2",
        (run_id,),
    )
    assert session2 is not None
    assert session2["started_at"] is not None
    assert session2["ended_at"] is None

    note = _row(
        db_path,
        "SELECT detail FROM violations WHERE run_id = ? ORDER BY id DESC LIMIT 1",
        (run_id,),
    )
    assert note is not None
    assert "Run resumed" in str(note["detail"])


def test_resume_with_open_session_logs_violation_and_keeps_session(
    tmp_path: Path,
) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-rc-02b", db_path=db_path)
    open_session(run_id=run_id, session_number=1, db_path=db_path)

    with patch(
        "sys.argv",
        ["sdlc-resume", "--run-id", run_id, "--db", str(db_path)],
    ):
        resume_main()

    open_count = _row(
        db_path,
        "SELECT COUNT(*) AS c FROM sessions WHERE run_id = ? AND ended_at IS NULL",
        (run_id,),
    )
    assert open_count is not None
    assert int(open_count["c"]) == 1

    note = _row(
        db_path,
        "SELECT detail FROM violations WHERE run_id = ? ORDER BY id DESC LIMIT 1",
        (run_id,),
    )
    assert note is not None
    assert "Run resumed" in str(note["detail"])


def test_abandon_closes_run_and_logs_violation(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-rc-03", db_path=db_path)
    open_session(run_id=run_id, session_number=1, db_path=db_path)

    argv = [
        "sdlc-abandon-run",
        "--run-id",
        run_id,
        "--reason",
        "invalid baseline setup",
        "--terminal-phase",
        "2",
        "--db",
        str(db_path),
    ]
    with patch("sys.argv", argv):
        abandon_main()

    run_row = _row(
        db_path,
        "SELECT ended_at, terminal_phase FROM runs WHERE id = ?",
        (run_id,),
    )
    assert run_row is not None
    assert run_row["ended_at"] is not None
    assert run_row["terminal_phase"] == 2

    note = _row(
        db_path,
        "SELECT detail FROM violations WHERE run_id = ? ORDER BY id DESC LIMIT 1",
        (run_id,),
    )
    assert note is not None
    assert "Run abandoned" in str(note["detail"])


def test_resume_fails_when_run_closed(tmp_path: Path) -> None:
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-rc-04", db_path=db_path)
    close_run(run_id=run_id, terminal_phase=2, db_path=db_path)

    with patch(
        "sys.argv",
        ["sdlc-resume", "--run-id", run_id, "--db", str(db_path)],
    ):
        try:
            resume_main()
            raised = False
        except SystemExit:
            raised = True

    assert raised
