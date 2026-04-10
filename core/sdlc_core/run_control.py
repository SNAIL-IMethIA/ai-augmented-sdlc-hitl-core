"""run_control.py: Pause, resume, and abandon controls for experiment runs.

These commands are built for shared machines where runs may need to stop at
any moment and continue later without data loss.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from sdlc_core import db
from sdlc_core.enums import ViolationType

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _die(message: str) -> None:
    print(f"[run-control] ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def _db_path(path_arg: str | None) -> Path:
    return Path(path_arg) if path_arg else Path("logs") / "experiment.db"


def _resolve_run_id(
    conn: sqlite3.Connection,
    run_id: str | None,
    *,
    require_open: bool,
) -> str:
    if run_id is not None:
        row = conn.execute(
            "SELECT id, ended_at FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            _die(f"Run ID {run_id!r} not found.")
        if require_open and row[1] is not None:
            _die(f"Run ID {run_id!r} is already closed.")
        return run_id

    where = "WHERE ended_at IS NULL" if require_open else ""
    row = conn.execute(
        f"SELECT id FROM runs {where} ORDER BY started_at DESC LIMIT 1"
    ).fetchone()
    if row is None:
        if require_open:
            _die("No open run found. Pass --run-id explicitly.")
        _die("No run found. Pass --run-id explicitly.")
    return str(row[0])


def _last_phase(conn: sqlite3.Connection, run_id: str) -> int:
    row = conn.execute(
        "SELECT MAX(sdlc_phase) FROM interactions WHERE run_id = ?",
        (run_id,),
    ).fetchone()
    if row is None or row[0] is None:
        return 2
    return int(row[0])


def _open_session_numbers(conn: sqlite3.Connection, run_id: str) -> list[int]:
    rows = conn.execute(
        "SELECT session_number FROM sessions WHERE run_id = ? AND ended_at IS NULL",
        (run_id,),
    ).fetchall()
    return [int(r[0]) for r in rows]


def _next_session_number(conn: sqlite3.Connection, run_id: str) -> int:
    row = conn.execute(
        "SELECT MAX(session_number) FROM sessions WHERE run_id = ?",
        (run_id,),
    ).fetchone()
    latest = int(row[0]) if row and row[0] is not None else 0
    return latest + 1


def _log_note(run_id: str, note: str, db_path: Path) -> None:
    db.log_violation(
        violation_type=ViolationType.OTHER,
        detail=note,
        run_id=run_id,
        db_path=db_path,
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def pause_main() -> None:
    """Pause a run safely and optionally close active sessions."""
    parser = argparse.ArgumentParser(prog="sdlc-pause", description="Pause an active run.")
    parser.add_argument("--run-id", default=None, help="Run ID. Defaults to latest open run.")
    parser.add_argument("--reason", default="manual pause", help="Reason recorded in logs.")
    parser.add_argument(
        "--close-session",
        action="store_true",
        help="Close currently open session(s) when pausing.",
    )
    parser.add_argument("--db", default=None, help="Path to experiment.db.")
    args = parser.parse_args()

    path = _db_path(args.db)
    conn = sqlite3.connect(path)
    try:
        run_id = _resolve_run_id(conn, args.run_id, require_open=True)
        open_sessions = _open_session_numbers(conn, run_id)
    finally:
        conn.close()

    closed_sessions: list[int] = []
    if args.close_session:
        for session_number in open_sessions:
            db.close_session(run_id=run_id, session_number=session_number, db_path=path)
            closed_sessions.append(session_number)

    _log_note(run_id, f"Run paused: {args.reason}", path)
    print(
        f"[run-control] Paused run {run_id!r}. "
        f"Closed sessions: {closed_sessions}."
    )


def resume_main() -> None:
    """Resume a run by opening the next session and writing an audit note."""
    parser = argparse.ArgumentParser(prog="sdlc-resume", description="Resume a paused run.")
    parser.add_argument("--run-id", default=None, help="Run ID. Defaults to latest open run.")
    parser.add_argument(
        "--session-number",
        type=int,
        default=None,
        help="Session number to open. Defaults to next available.",
    )
    parser.add_argument("--reason", default="manual resume", help="Reason recorded in logs.")
    parser.add_argument("--db", default=None, help="Path to experiment.db.")
    args = parser.parse_args()

    path = _db_path(args.db)
    conn = sqlite3.connect(path)
    try:
        run_id = _resolve_run_id(conn, args.run_id, require_open=True)
        open_sessions = _open_session_numbers(conn, run_id)
        if open_sessions:
            _log_note(run_id, f"Run resumed: {args.reason}", path)
            print(
                f"[run-control] Resumed run {run_id!r}. "
                f"Session already open: {open_sessions}."
            )
            return
        session_number = args.session_number or _next_session_number(conn, run_id)
    finally:
        conn.close()

    if session_number not in (1, 2, 3):
        _die(
            "No valid session number left. Pass --session-number 1, 2, or 3 if needed."
        )

    db.open_session(run_id=run_id, session_number=session_number, db_path=path)
    _log_note(run_id, f"Run resumed: {args.reason}", path)
    print(
        f"[run-control] Resumed run {run_id!r}. "
        f"Opened session {session_number}."
    )


def abandon_main() -> None:
    """Abandon a run safely without deleting any evidence."""
    parser = argparse.ArgumentParser(
        prog="sdlc-abandon-run",
        description="Abandon a run and close it with an audit note.",
    )
    parser.add_argument("--run-id", default=None, help="Run ID. Defaults to latest open run.")
    parser.add_argument("--reason", required=True, help="Reason for abandoning this run.")
    parser.add_argument(
        "--terminal-phase",
        type=int,
        default=None,
        help="Terminal phase override. Defaults to last logged phase.",
    )
    parser.add_argument("--db", default=None, help="Path to experiment.db.")
    args = parser.parse_args()

    path = _db_path(args.db)
    conn = sqlite3.connect(path)
    try:
        run_id = _resolve_run_id(conn, args.run_id, require_open=True)
        open_sessions = _open_session_numbers(conn, run_id)
        terminal_phase = args.terminal_phase or _last_phase(conn, run_id)
    finally:
        conn.close()

    for session_number in open_sessions:
        db.close_session(run_id=run_id, session_number=session_number, db_path=path)

    db.close_run(run_id=run_id, terminal_phase=terminal_phase, db_path=path)
    _log_note(run_id, f"Run abandoned: {args.reason}", path)

    print(
        f"[run-control] Abandoned run {run_id!r}. "
        f"Terminal phase set to {terminal_phase}."
    )


if __name__ == "__main__":
    _die("Use one of the scripts: sdlc-pause, sdlc-resume, or sdlc-abandon-run.")
