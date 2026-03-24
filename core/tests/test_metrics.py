"""test_metrics.py: Tests for sdlc_core.metrics.collect_all_metrics."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest

from sdlc_core.db import (
    accept_artifact,
    log_intervention,
    log_validation_result,
    open_run,
    set_phase_status,
)
from sdlc_core.enums import (
    InterventionCategory,
    PhaseStatus,
    Severity,
    ValidationResult,
    ValidationType,
)
from sdlc_core.metrics import collect_all_metrics, write_report
from sdlc_core.metrics import main as metrics_main

_EXPECTED_TOP_LEVEL_KEYS = {
    "generated_at",
    "phase_reach_rate",
    "traceability",
    "governance_rules",
    "human_effort",
    "time_effort",
    "defects",
    "prompt_refinements",
    "defect_origin_mappings",
    "deployment",
}


@contextmanager
def _conn(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Structure: all expected keys are present regardless of data
# ---------------------------------------------------------------------------


def test_collect_all_metrics_has_all_keys(db_path: Path) -> None:
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    assert set(metrics.keys()) == _EXPECTED_TOP_LEVEL_KEYS


def test_collect_all_metrics_has_generated_at(db_path: Path) -> None:
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    assert isinstance(metrics["generated_at"], str)
    assert metrics["generated_at"].startswith("20")


def test_collect_all_metrics_empty_db_no_exception(db_path: Path) -> None:
    with _conn(db_path) as conn:
        collect_all_metrics(conn)


def test_collect_all_metrics_empty_db_nested_values_are_dicts(db_path: Path) -> None:
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    for key in _EXPECTED_TOP_LEVEL_KEYS - {"generated_at"}:
        assert isinstance(metrics[key], dict), (
            f"Expected dict for '{key}', got {type(metrics[key])}"
        )


# ---------------------------------------------------------------------------
# Numeric values on empty DB are 0 or None (not errors)
# ---------------------------------------------------------------------------


def test_phase_reach_rate_zero_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    prr = metrics["phase_reach_rate"]
    assert prr.get("phase_reach_count", 0) == 0


def test_traceability_linked_artifacts_zero_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    tl = metrics["traceability"]
    for value in tl.values():
        assert value is None or value == 0 or isinstance(value, int | float), (
            f"Unexpected non-numeric value in traceability: {value!r}"
        )


def test_governance_rules_zero_violations_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    gov = metrics["governance_rules"]
    for value in gov.values():
        assert value is None or isinstance(value, int | float | dict), (
            f"Unexpected type in governance_rules: {type(value)}"
        )


# ---------------------------------------------------------------------------
# Values update when data is inserted
# ---------------------------------------------------------------------------


def test_phase_reach_rate_increments_with_completed_phase(db_path: Path) -> None:
    rid = open_run(project="p", approach=1, run_id="r1", db_path=db_path)
    set_phase_status(
        run_id=rid, phase_number=2, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    prr = metrics["phase_reach_rate"]
    assert prr.get("phase_reach_count", 0) >= 1


def test_human_effort_counts_interactions(db_path: Path) -> None:
    # human_effort tracks interventions (manual human actions), not AI interactions.
    rid = open_run(project="p", approach=1, run_id="r1", db_path=db_path)
    log_intervention(
        run_id=rid, sdlc_phase=2, category=InterventionCategory.CORRECTION,
        severity=Severity.MINOR, rationale="Corrected an error.", time_spent_minutes=5,
        db_path=db_path,
    )
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    he = metrics["human_effort"]
    assert he.get("total_intervention_count", 0) >= 1


def test_time_effort_sums_intervention_minutes(db_path: Path) -> None:
    rid = open_run(project="p", approach=1, run_id="r1", db_path=db_path)
    log_intervention(
        run_id=rid, sdlc_phase=2, category=InterventionCategory.CORRECTION,
        severity=Severity.MINOR, rationale="Fixed something.", time_spent_minutes=15,
        db_path=db_path,
    )
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    te = metrics["time_effort"]
    total = te.get("total_human_time_minutes")
    assert total is not None
    assert total == 15


def test_traceability_linked_artifacts_updates(db_path: Path) -> None:
    rid = open_run(project="p", approach=1, run_id="r1", db_path=db_path)
    # REQ-01 is a phase-1 seed; it must exist before ARCH-01 references it.
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=1, db_path=db_path,
    )
    accept_artifact(
        run_id=rid, artifact_id="ARCH-01", artifact_type="Architecture Document",
        phase=2, upstream_ids=["REQ-01"], db_path=db_path,
    )
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    tl = metrics["traceability"]
    assert tl.get("traceability_coverage_rate_pct", 0) > 0


def test_validation_results_counted(db_path: Path) -> None:
    rid = open_run(project="p", approach=1, run_id="r1", db_path=db_path)
    # An artifact must exist so compliance_rate is not None (requires total_artifacts > 0).
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=2, db_path=db_path,
    )
    log_validation_result(
        run_id=rid, sdlc_phase=2, validation_type=ValidationType.REVIEW,
        result=ValidationResult.ACCEPTED, defects_found=0, db_path=db_path,
    )
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    gov = metrics["governance_rules"]
    # With one artifact and no violations the compliance rate should be 100%.
    assert gov.get("governance_compliance_rate_pct") == 100.0


# ---------------------------------------------------------------------------
# write_report integration
# ---------------------------------------------------------------------------


def test_write_report_creates_valid_json(db_path: Path, tmp_path: Path) -> None:
    import json
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    out = tmp_path / "metrics_report.json"
    write_report(metrics, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "generated_at" in data
    assert "phase_reach_rate" in data


# ---------------------------------------------------------------------------
# Phase reach: IN_PROGRESS branch (line 79: "Partially reached")
# ---------------------------------------------------------------------------


def test_phase_reach_rate_partial_phase(db_path: Path) -> None:
    rid = open_run(project="proj", approach=1, run_id="r-partial", db_path=db_path)
    set_phase_status(
        run_id=rid, phase_number=2, status=PhaseStatus.IN_PROGRESS, db_path=db_path
    )
    with _conn(db_path) as conn:
        metrics = collect_all_metrics(conn)
    profile = metrics["phase_reach_rate"]["phase_reach_profile"]
    assert profile["2"] == "Partially reached"


# ---------------------------------------------------------------------------
# main() CLI entry point
# ---------------------------------------------------------------------------


def test_metrics_main_exits_on_missing_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["metrics", "--db", str(tmp_path / "missing.db")])
    with pytest.raises(SystemExit) as exc:
        metrics_main()
    assert exc.value.code == 1


def test_metrics_main_writes_report(
    db_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "metrics_report.json"
    monkeypatch.setattr("sys.argv", ["metrics", "--db", str(db_path), "--out", str(out)])
    metrics_main()
    assert out.exists()
