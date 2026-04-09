"""status.py: Show a compact run status snapshot for operators."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, cast


def _db_path(raw: str) -> Path:
    return Path(raw)


def _fetch_latest_run(conn: sqlite3.Connection) -> sqlite3.Row | None:
    row = conn.execute(
        """
        SELECT id, project, approach, started_at, ended_at, terminal_phase
        FROM runs
        ORDER BY started_at DESC
        LIMIT 1
        """
    ).fetchone()
    return cast(sqlite3.Row | None, row)


def _fetch_active_phase(conn: sqlite3.Connection, run_id: str) -> int | None:
    row = conn.execute(
        """
        SELECT phase_number
        FROM phase_progress
        WHERE run_id = ? AND status = 'in_progress'
        ORDER BY phase_number DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    if row is not None:
        return int(row[0])

    row = conn.execute(
        """
        SELECT phase_number
        FROM phase_progress
        WHERE run_id = ? AND status IN ('completed', 'partially_reached')
        ORDER BY phase_number DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    if row is None:
        return None
    return int(row[0])


def _fetch_pending_checkpoints(conn: sqlite3.Connection, run_id: str) -> list[int]:
    rows = conn.execute(
        """
        SELECT phase_number
        FROM phase_progress
        WHERE run_id = ? AND status != 'completed'
        ORDER BY phase_number ASC
        """,
        (run_id,),
    ).fetchall()
    if rows:
        return [int(row[0]) for row in rows]

    all_rows = conn.execute(
        """
        SELECT phase_number, status
        FROM phase_progress
        WHERE run_id = ?
        ORDER BY phase_number ASC
        """,
        (run_id,),
    ).fetchall()
    if not all_rows:
        return list(range(2, 9))

    completed = {int(row[0]) for row in all_rows if str(row[1]) == "completed"}
    return [phase for phase in range(2, 9) if phase not in completed]


def _fetch_last_accepted_artifact(conn: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT id, phase, created_at
        FROM artifacts
        WHERE run_id = ? AND status = 'accepted'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    if row is None:
        return None
    return {"id": str(row[0]), "phase": int(row[1]), "created_at": str(row[2])}


def _fetch_open_violations(conn: sqlite3.Connection, run_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE run_id = ?",
        (run_id,),
    ).fetchone()
    return int(row[0]) if row is not None else 0


def _status_snapshot(db_path: Path) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        run = _fetch_latest_run(conn)
        if run is None:
            return {
                "database": db_path.as_posix(),
                "has_run": False,
                "message": "No runs found in database.",
            }

        run_id = str(run["id"])
        return {
            "database": db_path.as_posix(),
            "has_run": True,
            "run": {
                "id": run_id,
                "project": str(run["project"]),
                "approach": int(run["approach"]),
                "started_at": str(run["started_at"]),
                "ended_at": None if run["ended_at"] is None else str(run["ended_at"]),
                "terminal_phase": (
                    None if run["terminal_phase"] is None else int(run["terminal_phase"])
                ),
            },
            "active_phase": _fetch_active_phase(conn, run_id),
            "pending_checkpoints": _fetch_pending_checkpoints(conn, run_id),
            "last_accepted_artifact": _fetch_last_accepted_artifact(conn, run_id),
            "open_violations": _fetch_open_violations(conn, run_id),
        }
    finally:
        conn.close()


def _print_human(snapshot: dict[str, Any]) -> None:
    if not snapshot["has_run"]:
        print(snapshot["message"])
        return

    run = snapshot["run"]
    print(f"run_id: {run['id']}")
    print(f"project: {run['project']}")
    print(f"approach: {run['approach']}")
    print(f"active_phase: {snapshot['active_phase']}")
    print(f"pending_checkpoints: {snapshot['pending_checkpoints']}")
    print(f"open_violations: {snapshot['open_violations']}")

    artifact = snapshot["last_accepted_artifact"]
    if artifact is None:
        print("last_accepted_artifact: none")
    else:
        print(
            "last_accepted_artifact: "
            f"{artifact['id']} (phase {artifact['phase']}, {artifact['created_at']})"
        )


def main() -> None:
    """Parse CLI arguments and print the current run status snapshot."""
    parser = argparse.ArgumentParser(description="Show current run status.")
    parser.add_argument("--db", default="logs/experiment.db", help="Path to experiment DB.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    snapshot = _status_snapshot(_db_path(args.db))
    if args.json:
        print(json.dumps(snapshot, indent=2))
        return
    _print_human(snapshot)


if __name__ == "__main__":
    main()
