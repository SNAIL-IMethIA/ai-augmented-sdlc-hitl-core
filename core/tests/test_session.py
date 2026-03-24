"""test_session.py: Tests for sdlc_core.session."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from sdlc_core.session import Session

# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_session_required_fields() -> None:
    s = Session(run_id="r1", approach=2, active_phase=3)
    assert s.run_id == "r1"
    assert s.approach == 2
    assert s.active_phase == 3
    assert s.db_path is None


def test_session_with_db_path(tmp_path: Path) -> None:
    p = tmp_path / "experiment.db"
    s = Session(run_id="r1", approach=1, active_phase=2, db_path=p)
    assert s.db_path == p


def test_session_iterations_not_in_constructor() -> None:
    sig = inspect.signature(Session.__init__)
    assert "_iterations" not in sig.parameters


# ---------------------------------------------------------------------------
# next_iteration
# ---------------------------------------------------------------------------


def test_next_iteration_starts_at_one() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    assert s.next_iteration("ARCH-01") == 1


def test_next_iteration_increments_on_repeated_calls() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    s.next_iteration("ARCH-01")
    assert s.next_iteration("ARCH-01") == 2


def test_next_iteration_tracks_separate_artifacts_independently() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    assert s.next_iteration("ARCH-01") == 1
    assert s.next_iteration("IMPL-01") == 1
    assert s.next_iteration("ARCH-01") == 2
    assert s.next_iteration("IMPL-01") == 2


def test_next_iteration_many_calls_same_artifact() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    for expected in range(1, 6):
        assert s.next_iteration("DSGN-01") == expected


# ---------------------------------------------------------------------------
# set_phase
# ---------------------------------------------------------------------------


def test_set_phase_updates_active_phase() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    s.set_phase(5)
    assert s.active_phase == 5


def test_set_phase_accepts_all_valid_phases() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    for phase in range(2, 9):
        s.set_phase(phase)
        assert s.active_phase == phase


def test_set_phase_raises_for_phase_one() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    with pytest.raises(ValueError, match="phase must be between 2 and 8"):
        s.set_phase(1)


def test_set_phase_raises_for_phase_nine() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    with pytest.raises(ValueError, match="phase must be between 2 and 8"):
        s.set_phase(9)


def test_set_phase_raises_for_zero() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    with pytest.raises(ValueError, match="phase must be between 2 and 8"):
        s.set_phase(0)


def test_set_phase_raises_for_negative() -> None:
    s = Session(run_id="r", approach=1, active_phase=2)
    with pytest.raises(ValueError, match="phase must be between 2 and 8"):
        s.set_phase(-1)


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------


def test_session_manager_opens_and_closes_session(tmp_path: Path) -> None:
    from sdlc_core.db import open_run, setup_db
    from sdlc_core.session import SessionManager

    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-sm-01", db_path=db_path)
    session = Session(run_id=run_id, approach=1, active_phase=2, db_path=db_path)

    with SessionManager(session, session_number=1) as sess:
        assert sess is session

    import sqlite3
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT started_at, ended_at FROM sessions WHERE run_id = ? AND session_number = 1",
        (run_id,),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[0] is not None
    assert row[1] is not None


def test_session_manager_returns_session_from_enter(tmp_path: Path) -> None:
    from sdlc_core.db import open_run, setup_db
    from sdlc_core.session import SessionManager

    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-sm-02", db_path=db_path)
    session = Session(run_id=run_id, approach=1, active_phase=3, db_path=db_path)

    with SessionManager(session, session_number=2) as s:
        assert s.run_id == run_id
        assert s.active_phase == 3


def test_session_manager_invalid_session_number_raises() -> None:
    from sdlc_core.session import SessionManager

    session = Session(run_id="r", approach=1, active_phase=2)
    with pytest.raises(ValueError, match="session_number must be 1, 2, or 3"):
        SessionManager(session, session_number=0)


def test_session_manager_does_not_suppress_exceptions(tmp_path: Path) -> None:
    from sdlc_core.db import open_run, setup_db
    from sdlc_core.session import SessionManager

    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-sm-03", db_path=db_path)
    session = Session(run_id=run_id, approach=1, active_phase=2, db_path=db_path)

    with pytest.raises(RuntimeError, match="test error"):
        with SessionManager(session, session_number=1):
            raise RuntimeError("test error")
