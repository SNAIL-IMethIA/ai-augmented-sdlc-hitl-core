"""check.py: Semantic integrity checker for experiment.db.

Usage:
    python -m sdlc_core.check --db logs/experiment.db

Exits with code 0 if all checks pass, 1 if any check fails.
A JSON report is written to logs/check_report.json (same directory as the DB
unless overridden with --out).

Checks performed
----------------
These are semantic checks that the schema's CHECK constraints cannot enforce.
They are intended to be run as a pre-commit hook or at run close.

General (all approaches):
  G1  Every artifact row has at least one upstream traceability link.
      Exception: phase-1 seed artifacts are explicitly excluded.
  G2  Every artifact id that starts with "IMPL-" has at least one "VER-"
      artifact linked to it in traceability_links.
  G3  For every validation_results row: defects_found equals the actual count
      of defect rows with the same (run_id, validation_result_id).
  G4  No validation_results row has result='accepted' while any open (unresolved)
      defect of severity='critical' exists for the same artifact_id + run_id.
  G5  No session row has ended_at IS NULL at run close (runs.ended_at IS NOT NULL).
  G6  Artifact ids are unique within a run (enforced by PK, but we double-check).
  G7  All integer PKs in every table are monotonically increasing (tamper check).

Phase exit criteria (from sdlc.md):
  P1  Phase 1 baseline seeded (pre-experiment): at least one phase-1 artifact is
      registered in the artifacts table before the run begins.  Phase 1 is
      conducted once per project by the human overseer and is excluded from the
      time budget; its completion evidence is the presence of seed artifacts,
      NOT a phase_progress row (which only covers Phases 2-8).
  P2  Phase 2 complete → at least one artifact of type 'Requirements Document'.
  P3  Phase 3 complete → at least one artifact of type 'Architecture Document'.
    P4  Phase 4 complete → at least one artifact of type 'Design'.
    P5  Phase 5 complete → at least one artifact of type 'Implementation'.
    P6  Phase 6 complete → at least one validation_results row.
    P7  Phase 7 complete → at least one validation_results row.
    P8  Phase 8 complete → at least one TRANS-* artifact and one accepted
            acceptance_test validation_results row for phase 8.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# Shape: {id, description, passed, detail}
CheckResult = dict[str, Any]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _open(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check(check_id: str, description: str, passed: bool, detail: str = "") -> CheckResult:
    """Build a :data:`CheckResult` dict."""
    return {
        "id": check_id,
        "description": description,
        "passed": passed,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# Phase exit criteria
# ---------------------------------------------------------------------------

def p1_seed_artifacts_registered(conn: sqlite3.Connection) -> CheckResult:
    """Phase 1 baseline was seeded before this run began.

    Phase 1 (Stakeholder Requirements Definition) is conducted once per project
    by the human overseer, prior to and independently of all timed experiment
    runs.  It is excluded from the 24-hour time budget tracked by
    ``phase_progress`` (which only covers Phases 2-8).  Its completion is
    evidenced by the presence of at least one phase-1 artifact registered via
    ``accept_artifact(phase=1, ...)`` before ``open_run()`` is called.

    This check fails if no phase-1 artifact exists, which indicates the
    requirements baseline was not seeded before work began.
    """
    desc = "Phase 1 baseline seeded: >=1 phase-1 (pre-experiment) artifact registered"
    count = conn.execute(
        "SELECT COUNT(*) FROM artifacts WHERE phase = 1"
    ).fetchone()[0]
    if count == 0:
        return _check(
            "P1",
            desc,
            False,
            "No phase-1 artifacts found; call accept_artifact(phase=1, ...) "
            "with the approved requirements before starting the run",
        )
    return _check("P1", desc, True)


def g1_artifact_upstream_links(conn: sqlite3.Connection) -> CheckResult:
    """Every artifact (except phase-1 seeds) has ≥1 upstream link."""
    rows = conn.execute(
        """
        SELECT a.id, a.run_id, a.phase
        FROM artifacts a
        LEFT JOIN traceability_links tl
            ON tl.from_artifact_id = a.id AND tl.run_id = a.run_id
        WHERE a.phase > 1
          AND tl.from_artifact_id IS NULL
        """
    ).fetchall()
    if not rows:
        return _check("G1", "All non-seed artifacts have ≥1 upstream link", True)
    detail = "; ".join(f"{r['run_id']}/{r['id']} (phase {r['phase']})" for r in rows)
    return _check("G1", "All non-seed artifacts have ≥1 upstream link", False,
                  f"Missing upstream links: {detail}")


def g2_impl_has_ver(conn: sqlite3.Connection) -> CheckResult:
    """Every IMPL-NN artifact has ≥1 VER-NN linked to it."""
    rows = conn.execute(
        """
        SELECT a.id, a.run_id
        FROM artifacts a
        WHERE a.id LIKE 'IMPL-%'
          AND NOT EXISTS (
              SELECT 1 FROM traceability_links tl
              JOIN artifacts a2
                  ON a2.id = tl.from_artifact_id AND a2.run_id = tl.run_id
              WHERE tl.to_artifact_id = a.id
                AND tl.run_id = a.run_id
                AND a2.id LIKE 'VER-%'
          )
        """
    ).fetchall()
    if not rows:
        return _check("G2", "All IMPL artifacts are linked to ≥1 VER artifact", True)
    detail = "; ".join(f"{r['run_id']}/{r['id']}" for r in rows)
    return _check("G2", "All IMPL artifacts are linked to ≥1 VER artifact", False,
                  f"Unverified IMPL artifacts: {detail}")


def g3_defect_count_matches(conn: sqlite3.Connection) -> CheckResult:
    """validation_results.defects_found equals actual defect row count."""
    rows = conn.execute(
        """
        SELECT vr.id, vr.run_id, vr.defects_found,
               COUNT(d.id) AS actual_count
        FROM validation_results vr
        LEFT JOIN defects d
            ON d.validation_result_id = vr.id AND d.run_id = vr.run_id
        GROUP BY vr.id, vr.run_id
        HAVING vr.defects_found <> actual_count
        """
    ).fetchall()
    if not rows:
        return _check("G3", "defects_found matches actual defect row count", True)
    detail = "; ".join(
        f"vr.id={r['id']} run={r['run_id']} "
        f"declared={r['defects_found']} actual={r['actual_count']}"
        for r in rows
    )
    return _check("G3", "defects_found matches actual defect row count", False,
                  f"Mismatches: {detail}")


def g4_no_accepted_with_open_critical(conn: sqlite3.Connection) -> CheckResult:
    """No accepted artifact has an open critical defect."""
    rows = conn.execute(
        """
        SELECT vr.artifact_id, vr.run_id
        FROM validation_results vr
        JOIN defects d
            ON d.artifact_id = vr.artifact_id AND d.run_id = vr.run_id
        WHERE vr.result = 'accepted'
          AND d.severity = 'critical'
          AND d.resolved_at IS NULL
        GROUP BY vr.artifact_id, vr.run_id
        """
    ).fetchall()
    if not rows:
        return _check("G4", "No accepted artifact has an open critical defect", True)
    detail = "; ".join(f"{r['run_id']}/{r['artifact_id']}" for r in rows)
    return _check("G4", "No accepted artifact has an open critical defect", False,
                  f"Violations: {detail}")


def g5_all_sessions_closed(conn: sqlite3.Connection) -> CheckResult:
    """All sessions are closed for closed runs."""
    rows = conn.execute(
        """
        SELECT s.run_id, s.session_number
        FROM sessions s
        JOIN runs r ON r.id = s.run_id
        WHERE r.ended_at IS NOT NULL
          AND s.ended_at IS NULL
        """
    ).fetchall()
    if not rows:
        return _check("G5", "All sessions closed for closed runs", True)
    detail = "; ".join(f"{r['run_id']} session {r['session_number']}" for r in rows)
    return _check("G5", "All sessions closed for closed runs", False,
                  f"Unclosed sessions: {detail}")


def g6_unique_artifact_ids_per_run(conn: sqlite3.Connection) -> CheckResult:
    """Artifact IDs are unique within each run (double-check beyond the PK constraint)."""
    rows = conn.execute(
        """
        SELECT run_id, id, COUNT(*) AS cnt
        FROM artifacts
        GROUP BY run_id, id
        HAVING cnt > 1
        """
    ).fetchall()
    if not rows:
        return _check("G6", "Artifact IDs are unique within each run", True)
    detail = "; ".join(
        f"{r['run_id']}/{r['id']} (count={r['cnt']})"
        for r in rows
    )
    return _check(
        "G6",
        "Artifact IDs are unique within each run",
        False,
        f"Duplicate artifact IDs: {detail}",
    )


def g7_monotonic_pks(conn: sqlite3.Connection) -> CheckResult:
    """All integer PKs are monotonically increasing (tamper check)."""
    tables = {
        "interactions": "id",
        "interventions": "id",
        "validation_results": "id",
        "defects": "id",
        "pipeline_events": "id",
        "violations": "id",
    }
    failures = []
    for table, pk in tables.items():
        rows = conn.execute(
            f"SELECT {pk} FROM {table} ORDER BY rowid"
        ).fetchall()
        ids = [r[0] for r in rows]
        for i in range(1, len(ids)):
            if ids[i] <= ids[i - 1]:
                failures.append(f"{table}.{pk}: {ids[i-1]} → {ids[i]}")
                break
    if not failures:
        return _check("G7", "All integer PKs are monotonically increasing", True)
    return _check("G7", "All integer PKs are monotonically increasing", False,
                  f"Non-monotonic sequences: {'; '.join(failures)}")


def _phase_artifact_check(
    conn: sqlite3.Connection,
    check_id: str,
    phase: int,
    artifact_type_like: str,
) -> CheckResult:
    desc = f"Phase {phase} completion: ≥1 artifact of type '{artifact_type_like}'"
    completed = conn.execute(
        "SELECT COUNT(*) FROM phase_progress WHERE phase_number = ? AND status = 'completed'",
        (phase,),
    ).fetchone()[0]
    if completed == 0:
        # Phase not yet completed in any run
        # Skip this check
        return _check(check_id, desc, True, "Phase not yet completed; check skipped")

    rows = conn.execute(
        """
        SELECT COUNT(*) FROM artifacts a
        JOIN phase_progress pp ON pp.run_id = a.run_id AND pp.phase_number = ?
        WHERE a.phase = ?
          AND a.artifact_type LIKE ?
          AND pp.status = 'completed'
        """,
        (phase, phase, f"%{artifact_type_like}%"),
    ).fetchone()[0]
    passed = rows > 0
    detail = (
        ""
        if passed
        else f"No '{artifact_type_like}' artifact found for completed phase {phase}"
    )
    return _check(check_id, desc, passed, detail)


def _phase_validation_check(
    conn: sqlite3.Connection,
    check_id: str,
    phase: int,
) -> CheckResult:
    desc = f"Phase {phase} completion: ≥1 validation_results row"
    completed = conn.execute(
        "SELECT COUNT(*) FROM phase_progress WHERE phase_number = ? AND status = 'completed'",
        (phase,),
    ).fetchone()[0]
    if completed == 0:
        return _check(check_id, desc, True, "Phase not yet completed; check skipped")

    count = conn.execute(
        "SELECT COUNT(*) FROM validation_results WHERE sdlc_phase = ?",
        (phase,),
    ).fetchone()[0]
    return _check(
        check_id,
        desc,
        count > 0,
        "" if count > 0 else f"No validation_results for phase {phase}",
    )


def p8_transition_evidence(conn: sqlite3.Connection) -> CheckResult:
    """Phase 8 completion requires TRANS evidence and accepted acceptance test."""
    desc = (
        "Phase 8 completion: ≥1 TRANS-* transition artifact and "
        "≥1 accepted acceptance_test validation_results row"
    )
    completed = conn.execute(
        "SELECT COUNT(*) FROM phase_progress WHERE phase_number = 8 AND status = 'completed'"
    ).fetchone()[0]
    if completed == 0:
        return _check("P8", desc, True, "Phase not yet completed; check skipped")

    trans_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM artifacts a
        JOIN phase_progress pp ON pp.run_id = a.run_id AND pp.phase_number = 8
        WHERE pp.status = 'completed'
          AND a.phase = 8
          AND a.id LIKE 'TRANS-%'
          AND a.artifact_type LIKE '%Transition%'
        """
    ).fetchone()[0]

    acceptance_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM validation_results vr
        JOIN phase_progress pp ON pp.run_id = vr.run_id AND pp.phase_number = 8
        WHERE pp.status = 'completed'
          AND vr.sdlc_phase = 8
          AND vr.validation_type = 'acceptance_test'
          AND vr.result = 'accepted'
        """
    ).fetchone()[0]

    if trans_count > 0 and acceptance_count > 0:
        return _check("P8", desc, True)

    missing = []
    if trans_count == 0:
        missing.append("no TRANS-* phase-8 artifact with artifact_type containing 'Transition'")
    if acceptance_count == 0:
        missing.append("no accepted phase-8 acceptance_test validation result")
    return _check("P8", desc, False, "; ".join(missing))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_checks(db_path: Path) -> list[CheckResult]:
    """Run all semantic integrity checks against *db_path*.

    Args:
        db_path: Path to the ``experiment.db`` file to check.

    Returns:
        List of :data:`CheckResult` dicts, one per check, each containing
        ``id``, ``description``, ``passed``, and ``detail`` keys.

    """
    conn = _open(db_path)
    results: list[CheckResult] = []
    try:
        results.append(g1_artifact_upstream_links(conn))
        results.append(g2_impl_has_ver(conn))
        results.append(g3_defect_count_matches(conn))
        results.append(g4_no_accepted_with_open_critical(conn))
        results.append(g5_all_sessions_closed(conn))
        results.append(g6_unique_artifact_ids_per_run(conn))
        results.append(g7_monotonic_pks(conn))
        results.append(p1_seed_artifacts_registered(conn))
        results.append(_phase_artifact_check(conn, "P2", 2, "Requirements"))
        results.append(_phase_artifact_check(conn, "P3", 3, "Architecture"))
        results.append(_phase_artifact_check(conn, "P4", 4, "Design"))
        results.append(_phase_artifact_check(conn, "P5", 5, "Implementation"))
        results.append(_phase_validation_check(conn, "P6", 6))
        results.append(_phase_validation_check(conn, "P7", 7))
        results.append(p8_transition_evidence(conn))
    finally:
        conn.close()
    return results


def write_report(results: list[CheckResult], out_path: Path) -> None:
    """Serialise *results* to a JSON report file at *out_path*.

    Args:
        results:  List of :data:`CheckResult` dicts as returned by
                  :func:`run_all_checks`.
        out_path: Destination path for the JSON report.  Parent directories
                  are created automatically.

    """
    passed = sum(1 for r in results if r["passed"])
    report = {
        "generated_at": _now_iso(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
        },
        "checks": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    """Parse command-line arguments and run the integrity checker."""
    parser = argparse.ArgumentParser(
        description="Semantic integrity check for experiment.db"
    )
    parser.add_argument(
        "--db",
        default="logs/experiment.db",
        help="Path to experiment.db (default: logs/experiment.db)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Path for check_report.json (default: same dir as --db)",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[sdlc_core.check] ERROR: database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out) if args.out else db_path.parent / "check_report.json"

    results = run_all_checks(db_path)
    write_report(results, out_path)

    failed = [r for r in results if not r["passed"]]
    passed = len(results) - len(failed)

    print(f"[sdlc_core.check] {passed}/{len(results)} checks passed")
    for r in failed:
        print(f"  FAIL [{r['id']}] {r['description']}: {r['detail']}")

    if failed:
        print(f"[sdlc_core.check] Report written to {out_path}")
        sys.exit(1)

    print(f"[sdlc_core.check] All checks passed. Report written to {out_path}")


if __name__ == "__main__":
    main()
