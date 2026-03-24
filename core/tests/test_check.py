"""test_check.py: Tests for all semantic integrity checks in sdlc_core.check."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest

from sdlc_core.check import (
    g1_artifact_upstream_links,
    g2_impl_has_ver,
    g3_defect_count_matches,
    g4_no_accepted_with_open_critical,
    g5_all_sessions_closed,
    g6_unique_artifact_ids_per_run,
    g7_monotonic_pks,
    p1_seed_artifacts_registered,
    run_all_checks,
    write_report,
)
from sdlc_core.check import (
    main as check_main,
)
from sdlc_core.db import (
    accept_artifact,
    close_run,
    log_defect,
    log_interaction,
    log_validation_result,
    open_run,
    open_session,
    set_phase_status,
)
from sdlc_core.enums import (
    Outcome,
    PhaseStatus,
    Severity,
    ValidationResult,
    ValidationType,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@contextmanager
def _conn(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _open_run(db_path: Path, rid: str = "run-001") -> str:
    return open_run(project="p", approach=1, run_id=rid, db_path=db_path)


# ---------------------------------------------------------------------------
# P1 - Phase 1 baseline was seeded (pre-experiment seed check)
# ---------------------------------------------------------------------------


def test_p1_fails_on_empty_db(db_path: Path) -> None:
    # No phase-1 artifacts; P1 should fail.
    with _conn(db_path) as conn:
        result = p1_seed_artifacts_registered(conn)
    assert not result["passed"]


def test_p1_passes_when_seed_artifact_registered(db_path: Path) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=1, db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = p1_seed_artifacts_registered(conn)
    assert result["passed"]


def test_p1_detail_mentions_accept_artifact_on_fail(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = p1_seed_artifacts_registered(conn)
    assert "accept_artifact" in result["detail"]


# ---------------------------------------------------------------------------
# G1 - every artifact (phase > 1) has >= 1 upstream traceability link
# ---------------------------------------------------------------------------


def test_g1_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g1_artifact_upstream_links(conn)
    assert result["passed"]


def test_g1_passes_for_phase_1_seed(db_path: Path) -> None:
    # Phase-1 artifacts are pre-run seeds; G1 uses WHERE phase > 1 so they are exempt.
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="CHARTER-01", artifact_type="Project Charter", phase=1,
        db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g1_artifact_upstream_links(conn)
    assert result["passed"]


def test_g1_fails_artifact_phase2_no_upstream(db_path: Path) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="ARCH-01", artifact_type="Architecture Document",
        phase=2, upstream_ids=None, db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g1_artifact_upstream_links(conn)
    assert not result["passed"]
    assert "ARCH-01" in result["detail"]


def test_g1_passes_when_upstream_provided(db_path: Path) -> None:
    rid = _open_run(db_path)
    # REQ-01 is a phase-1 seed (exempt from G1); ARCH-01 links to it and passes G1.
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=1, db_path=db_path,
    )
    accept_artifact(
        run_id=rid, artifact_id="ARCH-01", artifact_type="Architecture Document",
        phase=2, upstream_ids=["REQ-01"], db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g1_artifact_upstream_links(conn)
    assert result["passed"]


# ---------------------------------------------------------------------------
# G2 - every IMPL-* artifact is referenced by at least one VER-* artifact
# ---------------------------------------------------------------------------


def test_g2_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g2_impl_has_ver(conn)
    assert result["passed"]


def test_g2_fails_when_impl_has_no_ver(db_path: Path) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="IMPL-01", artifact_type="Implementation", phase=4,
        db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g2_impl_has_ver(conn)
    assert not result["passed"]
    assert "IMPL-01" in result["detail"]


def test_g2_passes_when_ver_links_to_impl(db_path: Path) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="IMPL-01", artifact_type="Implementation", phase=4,
        db_path=db_path,
    )
    accept_artifact(
        run_id=rid, artifact_id="VER-01", artifact_type="Verification Report", phase=5,
        upstream_ids=["IMPL-01"], db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g2_impl_has_ver(conn)
    assert result["passed"]


# ---------------------------------------------------------------------------
# G3 - defects_found matches actual defect row count
# ---------------------------------------------------------------------------


def test_g3_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g3_defect_count_matches(conn)
    assert result["passed"]


def test_g3_fails_when_defect_count_declared_but_none_logged(db_path: Path) -> None:
    rid = _open_run(db_path)
    log_validation_result(
        run_id=rid, sdlc_phase=2, validation_type=ValidationType.REVIEW,
        result=ValidationResult.REJECTED, defects_found=1, db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g3_defect_count_matches(conn)
    assert not result["passed"]


def test_g3_passes_when_counts_match(db_path: Path) -> None:
    rid = _open_run(db_path)
    val_id = log_validation_result(
        run_id=rid, sdlc_phase=2, validation_type=ValidationType.REVIEW,
        result=ValidationResult.REJECTED, defects_found=1, db_path=db_path,
    )
    log_defect(
        run_id=rid, validation_result_id=val_id, sdlc_phase_detected=2,
        severity=Severity.MINOR, description="A defect.", db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g3_defect_count_matches(conn)
    assert result["passed"]


# ---------------------------------------------------------------------------
# G4 - no accepted artifact has an open critical defect
# ---------------------------------------------------------------------------


def test_g4_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g4_no_accepted_with_open_critical(conn)
    assert result["passed"]


def test_g4_fails_when_accepted_with_open_critical(db_path: Path) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=2, db_path=db_path,
    )
    val_id = log_validation_result(
        run_id=rid, sdlc_phase=2, validation_type=ValidationType.REVIEW,
        result=ValidationResult.ACCEPTED, defects_found=1, artifact_id="REQ-01",
        db_path=db_path,
    )
    log_defect(
        run_id=rid, validation_result_id=val_id, sdlc_phase_detected=2,
        severity=Severity.CRITICAL, description="Critical flaw.", artifact_id="REQ-01",
        db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g4_no_accepted_with_open_critical(conn)
    assert not result["passed"]
    assert "REQ-01" in result["detail"]


# ---------------------------------------------------------------------------
# G5 - all sessions are closed for closed runs
# ---------------------------------------------------------------------------


def test_g5_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g5_all_sessions_closed(conn)
    assert result["passed"]


def test_g5_passes_when_run_still_open(db_path: Path) -> None:
    rid = _open_run(db_path)
    open_session(run_id=rid, session_number=1, db_path=db_path)
    with _conn(db_path) as conn:
        result = g5_all_sessions_closed(conn)
    assert result["passed"]


def test_g5_fails_when_closed_run_has_unclosed_session(db_path: Path) -> None:
    rid = _open_run(db_path)
    open_session(run_id=rid, session_number=1, db_path=db_path)
    close_run(run_id=rid, terminal_phase=2, db_path=db_path)
    with _conn(db_path) as conn:
        result = g5_all_sessions_closed(conn)
    assert not result["passed"]
    assert "session 1" in result["detail"]


# ---------------------------------------------------------------------------
# G6 - artifact IDs are unique within each run (double-check beyond PK)
# ---------------------------------------------------------------------------


def test_g6_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g6_unique_artifact_ids_per_run(conn)
    assert result["passed"]


def test_g6_passes_with_data(db_path: Path) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=1, db_path=db_path,
    )
    with _conn(db_path) as conn:
        result = g6_unique_artifact_ids_per_run(conn)
    assert result["passed"]


# ---------------------------------------------------------------------------
# G7 - integer PKs are monotonically increasing (tamper check)
# ---------------------------------------------------------------------------


def test_g7_passes_on_empty_db(db_path: Path) -> None:
    with _conn(db_path) as conn:
        result = g7_monotonic_pks(conn)
    assert result["passed"]


def test_g7_passes_with_multiple_rows(db_path: Path) -> None:
    rid = _open_run(db_path)
    for i in range(3):
        log_interaction(
            run_id=rid, sdlc_phase=2, approach=1, agent_role="analyst",
            model="gpt-4", prompt=f"prompt {i}", response=f"response {i}",
            iteration=i + 1, outcome=Outcome.ACCEPTED, human_modified=False,
            db_path=db_path,
        )
    with _conn(db_path) as conn:
        result = g7_monotonic_pks(conn)
    assert result["passed"]


# ---------------------------------------------------------------------------
# P2-P5 phase exit criteria (artifact presence)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("phase,artifact_type,check_id", [
    (2, "Requirements Document", "P2"),
    (3, "Architecture Document", "P3"),
    (4, "Design Document", "P4"),
    (5, "Implementation", "P5"),
])
def test_phase_check_skipped_when_not_completed(
    db_path: Path, phase: int, artifact_type: str, check_id: str
) -> None:
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == check_id)
    assert entry["passed"]
    assert "skipped" in entry["detail"]


@pytest.mark.parametrize("phase,artifact_type,check_id", [
    (2, "Requirements Document", "P2"),
    (3, "Architecture Document", "P3"),
    (4, "Design Document", "P4"),
    (5, "Implementation", "P5"),
])
def test_phase_check_fails_when_completed_but_no_artifact(
    db_path: Path, phase: int, artifact_type: str, check_id: str
) -> None:
    rid = _open_run(db_path)
    set_phase_status(
        run_id=rid, phase_number=phase, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == check_id)
    assert not entry["passed"]


@pytest.mark.parametrize("phase,artifact_type,check_id", [
    (2, "Requirements Document", "P2"),
    (3, "Architecture Document", "P3"),
    (4, "Design Document", "P4"),
    (5, "Implementation", "P5"),
])
def test_phase_check_passes_when_artifact_present(
    db_path: Path, phase: int, artifact_type: str, check_id: str
) -> None:
    rid = _open_run(db_path)
    set_phase_status(
        run_id=rid, phase_number=phase, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    accept_artifact(
        run_id=rid, artifact_id=f"ART-0{phase}", artifact_type=artifact_type,
        phase=phase, db_path=db_path,
    )
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == check_id)
    assert entry["passed"]


# ---------------------------------------------------------------------------
# P6-P7 phase exit criteria (validation_results required)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("phase,check_id", [(6, "P6"), (7, "P7")])
def test_p6_p7_skipped_when_not_completed(db_path: Path, phase: int, check_id: str) -> None:
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == check_id)
    assert entry["passed"]
    assert "skipped" in entry["detail"]


@pytest.mark.parametrize("phase,check_id", [(6, "P6"), (7, "P7")])
def test_p6_p7_fails_when_completed_but_no_validation(
    db_path: Path, phase: int, check_id: str
) -> None:
    rid = _open_run(db_path)
    set_phase_status(
        run_id=rid, phase_number=phase, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == check_id)
    assert not entry["passed"]


@pytest.mark.parametrize("phase,check_id", [(6, "P6"), (7, "P7")])
def test_p6_p7_passes_when_validation_result_exists(
    db_path: Path, phase: int, check_id: str
) -> None:
    rid = _open_run(db_path)
    set_phase_status(
        run_id=rid, phase_number=phase, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    log_validation_result(
        run_id=rid, sdlc_phase=phase, validation_type=ValidationType.TESTING,
        result=ValidationResult.ACCEPTED, defects_found=0, db_path=db_path,
    )
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == check_id)
    assert entry["passed"]


# ---------------------------------------------------------------------------
# P8 phase exit criteria (TRANS evidence + accepted acceptance test)
# ---------------------------------------------------------------------------


def test_p8_skipped_when_not_completed(db_path: Path) -> None:
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == "P8")
    assert entry["passed"]
    assert "skipped" in entry["detail"]


def test_p8_fails_when_completed_but_transition_evidence_missing(db_path: Path) -> None:
    rid = _open_run(db_path)
    set_phase_status(
        run_id=rid, phase_number=8, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == "P8")
    assert not entry["passed"]
    assert "TRANS-*" in entry["detail"]


def test_p8_passes_with_trans_artifact_and_accepted_acceptance_test(db_path: Path) -> None:
    rid = _open_run(db_path)
    set_phase_status(
        run_id=rid, phase_number=8, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    accept_artifact(
        run_id=rid,
        artifact_id="TRANS-01",
        artifact_type="Transition Record",
        phase=8,
        db_path=db_path,
    )
    log_validation_result(
        run_id=rid,
        sdlc_phase=8,
        validation_type=ValidationType.ACCEPTANCE_TEST,
        result=ValidationResult.ACCEPTED,
        defects_found=0,
        artifact_id="TRANS-01",
        db_path=db_path,
    )
    results = run_all_checks(db_path)
    entry = next(r for r in results if r["id"] == "P8")
    assert entry["passed"]


# ---------------------------------------------------------------------------
# run_all_checks smoke test
# ---------------------------------------------------------------------------


def test_run_all_checks_returns_15_results(db_path: Path) -> None:
    results = run_all_checks(db_path)
    assert len(results) == 15


def test_run_all_checks_all_pass_on_seeded_db(db_path: Path) -> None:
    # P1 requires at least one phase-1 artifact; seed it first.
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=1, db_path=db_path,
    )
    results = run_all_checks(db_path)
    failed = [r for r in results if not r["passed"]]
    assert failed == [], f"Unexpected failures on seeded DB: {failed}"


def test_run_all_checks_result_keys(db_path: Path) -> None:
    results = run_all_checks(db_path)
    for r in results:
        assert {"id", "description", "passed", "detail"} == set(r.keys())


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------


def test_write_report_creates_json(db_path: Path, tmp_path: Path) -> None:
    results = run_all_checks(db_path)
    out = tmp_path / "report.json"
    write_report(results, out)
    assert out.exists()


def test_write_report_json_structure(db_path: Path, tmp_path: Path) -> None:
    import json
    # Seed a phase-1 artifact so P1 passes and all 15 checks pass.
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid, artifact_id="REQ-01", artifact_type="Requirements Document",
        phase=1, db_path=db_path,
    )
    results = run_all_checks(db_path)
    out = tmp_path / "report.json"
    write_report(results, out)
    data = json.loads(out.read_text())
    assert "summary" in data
    assert "checks" in data
    assert data["summary"]["total"] == 15
    assert data["summary"]["passed"] == 15
    assert data["summary"]["failed"] == 0


# ---------------------------------------------------------------------------
# main() CLI entry point
# ---------------------------------------------------------------------------


def test_check_main_exits_on_missing_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["check", "--db", str(tmp_path / "missing.db")])
    with pytest.raises(SystemExit) as exc:
        check_main()
    assert exc.value.code == 1


def test_check_main_writes_report_when_all_pass(
    db_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rid = _open_run(db_path)
    accept_artifact(
        run_id=rid,
        artifact_id="REQ-01",
        artifact_type="Requirements Document",
        phase=1,
        db_path=db_path,
    )
    out = tmp_path / "check_report.json"
    monkeypatch.setattr("sys.argv", ["check", "--db", str(db_path), "--out", str(out)])
    check_main()  # should return without sys.exit
    assert out.exists()


def test_check_main_exits_when_checks_fail(
    db_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Empty DB → P1 fails → main() should sys.exit(1)
    out = tmp_path / "check_report.json"
    monkeypatch.setattr("sys.argv", ["check", "--db", str(db_path), "--out", str(out)])
    with pytest.raises(SystemExit) as exc:
        check_main()
    assert exc.value.code == 1
    assert out.exists()
