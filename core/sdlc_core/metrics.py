"""metrics.py: Query runner for experiment.db; writes metrics_report.json.

Usage:
    python -m sdlc_core.metrics --db logs/experiment.db
    python -m sdlc_core.metrics --db logs/experiment.db --out logs/metrics_report.json

All metrics are derived at query time from the raw tables.
No pre-computed values are stored in the database.

Metric keys in the output JSON mirror the names defined in metrics.md exactly.
If a metric requires data from a phase that was not reached, the value is ``null``
(JSON) rather than a number; callers should treat ``null`` as N/A and exclude
it from cross-approach averages.
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
# Connection
# ---------------------------------------------------------------------------

def _open(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _q(
    conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()
) -> list[sqlite3.Row]:
    return conn.execute(sql, params).fetchall()


def _scalar(
    conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()
) -> Any:  # noqa: ANN401
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else None


# ---------------------------------------------------------------------------
# Phase reach rate (metrics.md §2)
# ---------------------------------------------------------------------------

def _phase_reach_rate(conn: sqlite3.Connection) -> dict[str, Any]:
    completed_rows = _q(
        conn,
        "SELECT phase_number FROM phase_progress WHERE status = 'completed' ORDER BY phase_number",
    )
    completed_phases = [r["phase_number"] for r in completed_rows]

    partial_rows = _q(
        conn,
        "SELECT phase_number FROM phase_progress"
        " WHERE status = 'in_progress' ORDER BY phase_number",
    )
    partial_phases = [r["phase_number"] for r in partial_rows]

    terminal = max(completed_phases) if completed_phases else None
    phases_272_8 = list(range(2, 9))
    profile: dict[int, str] = {}
    for p in phases_272_8:
        if p in completed_phases:
            profile[p] = "Completed"
        elif p in partial_phases:
            profile[p] = "Partially reached"
        else:
            profile[p] = "Not reached"

    # Count of phases 2-8 fully completed
    count_completed = sum(1 for p in phases_272_8 if profile[p] == "Completed")
    rate = round(count_completed / 7 * 100, 2) if count_completed else 0.0

    return {
        "terminal_phase": terminal,
        "phase_reach_count": count_completed,
        "phase_reach_rate_pct": rate,
        "phase_reach_profile": {str(k): v for k, v in profile.items()},
    }


# ---------------------------------------------------------------------------
# Traceability (metrics.md §3)
# ---------------------------------------------------------------------------

def _traceability(conn: sqlite3.Connection) -> dict[str, Any]:
    total_artifacts = _scalar(conn, "SELECT COUNT(*) FROM artifacts") or 0

    # Artifacts with at least one upstream link (traceability_links.from_artifact_id = artifact.id)
    with_links = _scalar(
        conn,
        """
        SELECT COUNT(DISTINCT a.id)
        FROM artifacts a
        JOIN traceability_links tl
            ON tl.from_artifact_id = a.id AND tl.run_id = a.run_id
        """,
    ) or 0

    coverage = round(with_links / total_artifacts * 100, 2) if total_artifacts else None

    # Requirement-to-design linkage: REQ-* linked to any ARCH-* or DESIGN-* artifact
    total_req = _scalar(
        conn, "SELECT COUNT(*) FROM artifacts WHERE artifact_type LIKE '%Requirement%'"
    ) or 0
    req_to_design = _scalar(
        conn,
        """
        SELECT COUNT(DISTINCT a.id) FROM artifacts a
        JOIN traceability_links tl ON tl.from_artifact_id = a.id AND tl.run_id = a.run_id
        JOIN artifacts a2 ON a2.id = tl.to_artifact_id AND a2.run_id = a.run_id
        WHERE a.artifact_type LIKE '%Requirement%'
          AND (a2.artifact_type LIKE '%Architecture%' OR a2.artifact_type LIKE '%Design%')
        """,
    ) or 0
    req_to_design_rate = round(req_to_design / total_req * 100, 2) if total_req else None

    # Requirement-to-test linkage: REQ-* linked to any TEST-* artifact
    req_to_test = _scalar(
        conn,
        """
        SELECT COUNT(DISTINCT a.id) FROM artifacts a
        JOIN traceability_links tl ON tl.from_artifact_id = a.id AND tl.run_id = a.run_id
        JOIN artifacts a2 ON a2.id = tl.to_artifact_id AND a2.run_id = a.run_id
        WHERE a.artifact_type LIKE '%Requirement%'
          AND a2.artifact_type LIKE '%Test%'
        """,
    ) or 0
    req_to_test_rate = round(req_to_test / total_req * 100, 2) if total_req else None

    return {
        "traceability_coverage_rate_pct": coverage,
        "requirement_to_design_linkage_rate_pct": req_to_design_rate,
        "requirement_to_test_linkage_rate_pct": req_to_test_rate,
    }


# ---------------------------------------------------------------------------
# Governance rules (metrics.md §4)
# ---------------------------------------------------------------------------

def _governance(conn: sqlite3.Connection) -> dict[str, Any]:
    total_artifacts = _scalar(conn, "SELECT COUNT(*) FROM artifacts") or 0

    # Compliant = has no violation linked to it
    artifacts_with_violations = _scalar(
        conn,
        "SELECT COUNT(DISTINCT artifact_id) FROM violations WHERE artifact_id IS NOT NULL",
    ) or 0
    compliant = total_artifacts - artifacts_with_violations
    compliance_rate = round(compliant / total_artifacts * 100, 2) if total_artifacts else None

    # Per-type violation counts
    by_type_rows = _q(
        conn,
        "SELECT violation_type, COUNT(*) AS cnt FROM violations GROUP BY violation_type",
    )
    violations_by_type = {r["violation_type"]: r["cnt"] for r in by_type_rows}
    total_violations = _scalar(conn, "SELECT COUNT(*) FROM violations") or 0
    violations_per_artifact = (
        round(total_violations / total_artifacts, 4) if total_artifacts else None
    )

    return {
        "governance_compliance_rate_pct": compliance_rate,
        "total_violations": total_violations,
        "violations_per_artifact": violations_per_artifact,
        "violations_by_type": violations_by_type,
    }


# ---------------------------------------------------------------------------
# Human effort (metrics.md §5)
# ---------------------------------------------------------------------------

def _human_effort(conn: sqlite3.Connection) -> dict[str, Any]:
    total_artifacts = _scalar(conn, "SELECT COUNT(*) FROM artifacts") or 0
    total_req = _scalar(
        conn, "SELECT COUNT(*) FROM artifacts WHERE artifact_type LIKE '%Requirement%'"
    ) or 0

    total_interventions = _scalar(conn, "SELECT COUNT(*) FROM interventions") or 0

    per_phase_rows = _q(
        conn,
        "SELECT sdlc_phase, COUNT(*) AS cnt FROM interventions"
        " GROUP BY sdlc_phase ORDER BY sdlc_phase",
    )
    per_phase = {r["sdlc_phase"]: r["cnt"] for r in per_phase_rows}

    per_cat_rows = _q(
        conn,
        "SELECT category, COUNT(*) AS cnt FROM interventions GROUP BY category",
    )
    per_category = {r["category"]: r["cnt"] for r in per_cat_rows}

    per_sev_rows = _q(
        conn,
        "SELECT severity, COUNT(*) AS cnt FROM interventions GROUP BY severity",
    )
    per_severity = {r["severity"]: r["cnt"] for r in per_sev_rows}

    return {
        "total_intervention_count": total_interventions,
        "intervention_count_per_requirement": (
            round(total_interventions / total_req, 4) if total_req else None
        ),
        "intervention_count_per_artifact": (
            round(total_interventions / total_artifacts, 4) if total_artifacts else None
        ),
        "intervention_count_per_sdlc_phase": per_phase,
        "intervention_count_by_category": per_category,
        "intervention_count_by_severity": per_severity,
    }


# ---------------------------------------------------------------------------
# Time effort (metrics.md §6)
# ---------------------------------------------------------------------------

def _time_effort(conn: sqlite3.Connection) -> dict[str, Any]:
    total_artifacts = _scalar(conn, "SELECT COUNT(*) FROM artifacts") or 0
    total_req = _scalar(
        conn, "SELECT COUNT(*) FROM artifacts WHERE artifact_type LIKE '%Requirement%'"
    ) or 0

    # Returns NULL if no interventions have been logged yet
    total_time = _scalar(
        conn, "SELECT SUM(time_spent_minutes) FROM interventions"
    )

    per_phase_rows = _q(
        conn,
        """
        SELECT sdlc_phase, SUM(time_spent_minutes) AS total_min
        FROM interventions
        GROUP BY sdlc_phase
        ORDER BY sdlc_phase
        """,
    )
    per_phase = {r["sdlc_phase"]: r["total_min"] for r in per_phase_rows}

    # time_to_first_accepted_artifact_per_phase uses min(interactions.timestamp) per phase
    # Derived from artifacts.created_at minus phase_progress.entered_at in minutes
    first_accepted_rows = _q(
        conn,
        """
        SELECT a.phase,
               MIN(CAST((julianday(a.created_at) - julianday(pp.entered_at)) * 1440 AS INTEGER))
                   AS minutes_to_first
        FROM artifacts a
        JOIN phase_progress pp ON pp.run_id = a.run_id AND pp.phase_number = a.phase
        WHERE a.status = 'accepted'
          AND pp.entered_at IS NOT NULL
        GROUP BY a.phase
        ORDER BY a.phase
        """,
    )
    time_to_first = {r[0]: r[1] for r in first_accepted_rows}

    return {
        "total_human_time_minutes": total_time,
        "time_per_sdlc_phase_minutes": per_phase,
        "time_per_requirement_minutes": (
            round(total_time / total_req, 4) if (total_time and total_req) else None
        ),
        "time_per_artifact_minutes": (
            round(total_time / total_artifacts, 4) if (total_time and total_artifacts) else None
        ),
        "time_to_first_accepted_artifact_per_phase_minutes": time_to_first,
    }


# ---------------------------------------------------------------------------
# Defects (metrics.md §7)
# ---------------------------------------------------------------------------

def _defects(conn: sqlite3.Connection) -> dict[str, Any]:
    total_artifacts = _scalar(conn, "SELECT COUNT(*) FROM artifacts") or 0
    total_req = _scalar(
        conn, "SELECT COUNT(*) FROM artifacts WHERE artifact_type LIKE '%Requirement%'"
    ) or 0
    total_defects = _scalar(conn, "SELECT COUNT(*) FROM defects") or 0

    by_sev_rows = _q(conn, "SELECT severity, COUNT(*) AS cnt FROM defects GROUP BY severity")
    by_severity = {r["severity"]: r["cnt"] for r in by_sev_rows}

    by_phase_rows = _q(
        conn,
        "SELECT sdlc_phase_detected, COUNT(*) AS cnt FROM defects GROUP BY sdlc_phase_detected",
    )
    detection_phase_distribution = {r["sdlc_phase_detected"]: r["cnt"] for r in by_phase_rows}

    # Resolution time: resolved_at - detected_at in minutes
    resolution_times = _q(
        conn,
        """
        SELECT CAST((julianday(resolved_at) - julianday(detected_at)) * 1440 AS INTEGER)
               AS resolution_minutes
        FROM defects
        WHERE resolved_at IS NOT NULL
        """,
    )
    times = [
        r["resolution_minutes"]
        for r in resolution_times
        if r["resolution_minutes"] is not None
    ]
    mean_resolution = round(sum(times) / len(times), 2) if times else None

    return {
        "defect_density_per_requirement": (
            round(total_defects / total_req, 4) if total_req else None
        ),
        "defect_density_per_artifact": (
            round(total_defects / total_artifacts, 4) if total_artifacts else None
        ),
        "total_defects": total_defects,
        "defect_severity_distribution": by_severity,
        "defect_detection_phase_distribution": detection_phase_distribution,
        "mean_defect_resolution_time_minutes": mean_resolution,
    }


# ---------------------------------------------------------------------------
# Prompt refinements (metrics.md §8)
# ---------------------------------------------------------------------------

def _prompt_refinements(conn: sqlite3.Connection) -> dict[str, Any]:
    # Iteration count per artifact
    iter_rows = _q(
        conn,
        """
        SELECT artifact_id, MAX(iteration) AS max_iter
        FROM interactions
        WHERE artifact_id IS NOT NULL
        GROUP BY artifact_id
        """,
    )
    iter_per_artifact = {r["artifact_id"]: r["max_iter"] for r in iter_rows}

    # Average iteration count per phase
    avg_iter_rows = _q(
        conn,
        """
        SELECT sdlc_phase, AVG(max_iter) AS avg_iter
        FROM (
            SELECT artifact_id, sdlc_phase, MAX(iteration) AS max_iter
            FROM interactions
            WHERE artifact_id IS NOT NULL
            GROUP BY artifact_id, sdlc_phase
        ) sub
        GROUP BY sdlc_phase
        ORDER BY sdlc_phase
        """,
    )
    avg_iter_per_phase = {r["sdlc_phase"]: round(r["avg_iter"], 2) for r in avg_iter_rows}

    total_interactions = _scalar(conn, "SELECT COUNT(*) FROM interactions") or 0
    total_rejected = _scalar(
        conn, "SELECT COUNT(*) FROM interactions WHERE outcome = 'rejected'"
    ) or 0
    rejection_rate = (
        round(total_rejected / total_interactions * 100, 2) if total_interactions else None
    )

    # Human-modified accepted outputs
    total_accepted = _scalar(
        conn, "SELECT COUNT(*) FROM interactions WHERE outcome = 'accepted'"
    ) or 0
    human_modified_accepted = _scalar(
        conn,
        "SELECT COUNT(*) FROM interactions WHERE outcome = 'accepted' AND human_modified = 1",
    ) or 0
    modification_rate = (
        round(human_modified_accepted / total_accepted * 100, 2) if total_accepted else None
    )

    return {
        "iteration_count_per_artifact": iter_per_artifact,
        "average_iteration_count_per_phase": avg_iter_per_phase,
        "rejection_rate_pct": rejection_rate,
        "modification_rate_pct": modification_rate,
    }


# ---------------------------------------------------------------------------
# Defect-origin mappings (metrics.md §13)
# ---------------------------------------------------------------------------

def _defect_origin(conn: sqlite3.Connection) -> dict[str, Any]:
    # total_defects is available for future use, compute from defects table if needed
    origin_rows = _q(
        conn,
        """
        SELECT origin_phase, COUNT(*) AS cnt
        FROM defects
        WHERE origin_phase IS NOT NULL
        GROUP BY origin_phase
        ORDER BY origin_phase
        """,
    )
    origin_distribution = {r["origin_phase"]: r["cnt"] for r in origin_rows}

    # Error propagation depth = sdlc_phase_detected - origin_phase
    depth_rows = _q(
        conn,
        """
        SELECT sdlc_phase_detected - origin_phase AS depth
        FROM defects
        WHERE origin_phase IS NOT NULL
        """,
    )
    depths = [r["depth"] for r in depth_rows if r["depth"] is not None and r["depth"] >= 0]
    mean_depth = round(sum(depths) / len(depths), 2) if depths else None
    late_count = sum(1 for d in depths if d >= 2)
    late_rate = round(late_count / len(depths) * 100, 2) if depths else None

    return {
        "defect_origin_distribution": origin_distribution,
        "mean_error_propagation_depth": mean_depth,
        "late_detection_rate_pct": late_rate,
    }


# ---------------------------------------------------------------------------
# Deployment rate and client acceptance ratio (metrics.md §14)
# ---------------------------------------------------------------------------

def _deployment(conn: sqlite3.Connection) -> dict[str, Any]:
    # TRANS artifact holds deployment info
    trans_rows = _q(
        conn,
        """
        SELECT a.id, a.artifact_type, a.phase, a.run_id
        FROM artifacts a
        WHERE a.artifact_type LIKE '%TRANS%' OR a.artifact_type LIKE '%Deploy%'
        ORDER BY a.created_at
        """,
    )

    # pipeline_events for deployment step
    # gate_pass means step succeeded and gate_fail means step failed
    deploy_attempts: int = (
        _scalar(
            conn,
            "SELECT COUNT(*) FROM pipeline_events WHERE step LIKE '%deploy%'",
        )
        or 0
    )
    deploy_successes: int = (
        _scalar(
            conn,
            "SELECT COUNT(*) FROM pipeline_events"
            " WHERE step LIKE '%deploy%' AND event_type = 'gate_pass'",
        )
        or 0
    )
    successful_rate = (
        round(deploy_successes / deploy_attempts * 100, 2)
        if deploy_attempts
        else None
    )

    return {
        "deployment_artifact_count": len(trans_rows),
        "deployment_attempt_count": deploy_attempts,
        "successful_deployment_rate_pct": successful_rate,
    }


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def collect_all_metrics(conn: sqlite3.Connection) -> dict[str, Any]:
    """Run every metric query against *conn* and return the results.

    All values are derived at query time from the raw tables.  Nothing is
    pre-computed or cached.  Keys mirror the section names in
    ``protocol/metrics.md`` exactly.  Metric values for phases that were not
    reached are ``None`` (serialises as JSON ``null``).

    Args:
        conn: Open SQLite connection to ``experiment.db``.

    Returns:
        Dict with a ``generated_at`` timestamp key and one nested dict per
        metric category.

    """
    return {
        "generated_at": _now_iso(),
        "phase_reach_rate": _phase_reach_rate(conn),
        "traceability": _traceability(conn),
        "governance_rules": _governance(conn),
        "human_effort": _human_effort(conn),
        "time_effort": _time_effort(conn),
        "defects": _defects(conn),
        "prompt_refinements": _prompt_refinements(conn),
        "defect_origin_mappings": _defect_origin(conn),
        "deployment": _deployment(conn),
    }


def write_report(metrics: dict[str, Any], out_path: Path) -> None:
    """Serialise *metrics* to a pretty-printed JSON file at *out_path*.

    Args:
        metrics:  Dict as returned by :func:`collect_all_metrics`.
        out_path: Destination path.  Parent directories are created
                  automatically.

    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")


def main() -> None:
    """Parse command-line arguments and write the metrics report."""
    parser = argparse.ArgumentParser(
        description="Compute metrics from experiment.db and write metrics_report.json"
    )
    parser.add_argument(
        "--db",
        default="logs/experiment.db",
        help="Path to experiment.db (default: logs/experiment.db)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path (default: same dir as --db, metrics_report.json)",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[sdlc_core.metrics] ERROR: database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out) if args.out else db_path.parent / "metrics_report.json"

    conn = _open(db_path)
    try:
        metrics = collect_all_metrics(conn)
    finally:
        conn.close()

    write_report(metrics, out_path)
    print(f"[sdlc_core.metrics] Report written to {out_path}")


if __name__ == "__main__":
    main()
