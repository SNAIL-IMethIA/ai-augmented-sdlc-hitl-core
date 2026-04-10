"""phase_status.py: CLI for recording SDLC phase progress state."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from sdlc_core import db
from sdlc_core.enums import PhaseStatus


def _die(message: str) -> None:
    print(f"[phase-status] ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def _db_path(path_arg: str | None) -> Path:
    return Path(path_arg) if path_arg else Path("logs") / "experiment.db"


def _resolve_run_id(conn: sqlite3.Connection, run_id: str | None) -> str:
    if run_id is not None:
        row = conn.execute("SELECT id FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            _die(f"Run ID {run_id!r} not found.")
        return run_id

    row = conn.execute("SELECT id FROM runs ORDER BY started_at DESC LIMIT 1").fetchone()
    if row is None:
        _die("No run found. Pass --run-id explicitly.")
    return str(row[0])


def main() -> None:
    """Parse arguments and set a phase status row for a run."""
    parser = argparse.ArgumentParser(
        prog="sdlc-phase-status",
        description="Set phase progress status for a run.",
    )
    parser.add_argument("--run-id", default=None, help="Run ID. Defaults to latest run.")
    parser.add_argument("--phase", type=int, required=True, choices=range(2, 9))
    parser.add_argument(
        "--status",
        required=True,
        choices=[status.value for status in PhaseStatus],
        help="Phase status value.",
    )
    parser.add_argument("--db", default=None, help="Path to experiment.db.")
    args = parser.parse_args()

    path = _db_path(args.db)
    conn = sqlite3.connect(path)
    try:
        run_id = _resolve_run_id(conn, args.run_id)
    except sqlite3.OperationalError:
        _die("Database schema is missing. Run sdlc-setup first.")
    finally:
        conn.close()

    db.set_phase_status(
        run_id=run_id,
        phase_number=args.phase,
        status=args.status,
        db_path=path,
    )

    print(
        f"[phase-status] Run {run_id!r}: phase {args.phase} set to {args.status!r}."
    )


if __name__ == "__main__":
    main()
