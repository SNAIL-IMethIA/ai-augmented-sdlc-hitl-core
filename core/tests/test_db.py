"""test_db.py: Tests for all write helpers in sdlc_core.db."""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from sdlc_core.db import (
    accept_artifact,
    close_run,
    close_session,
    get_model_assignment,
    log_defect,
    log_interaction,
    log_intervention,
    log_pipeline_event,
    log_validation_result,
    log_violation,
    open_run,
    open_session,
    resolve_defect,
    seed_model_assignments,
    set_model_assignment,
    set_phase_status,
    setup_db,
)
from sdlc_core.enums import (
    InterventionCategory,
    Outcome,
    PhaseStatus,
    PipelineEventType,
    Severity,
    ValidationResult,
    ValidationType,
    ViolationType,
)
from tests.conftest import q_count, q_one

_EXPECTED_TABLES = {
    "runs",
    "sessions",
    "phase_progress",
    "model_assignments",
    "artifacts",
    "interactions",
    "interventions",
    "traceability_links",
    "validation_results",
    "defects",
    "pipeline_events",
    "violations",
}


# ---------------------------------------------------------------------------
# setup_db
# ---------------------------------------------------------------------------


def test_setup_db_creates_file(tmp_path: Path) -> None:
    path = setup_db(tmp_path / "experiment.db")
    assert path.exists()


def test_setup_db_returns_path(tmp_path: Path) -> None:
    path = setup_db(tmp_path / "experiment.db")
    assert isinstance(path, Path)


def test_setup_db_is_idempotent(tmp_path: Path) -> None:
    p = tmp_path / "experiment.db"
    setup_db(p)
    setup_db(p)


def test_setup_db_creates_all_tables(tmp_path: Path) -> None:
    path = setup_db(tmp_path / "experiment.db")
    import sqlite3
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    finally:
        conn.close()
    existing = {r[0] for r in rows}
    assert _EXPECTED_TABLES <= existing


# ---------------------------------------------------------------------------
# open_run / close_run
# ---------------------------------------------------------------------------


def test_open_run_returns_explicit_id(db_path: Path) -> None:
    rid = open_run(project="p", approach=2, run_id="my-run", db_path=db_path)
    assert rid == "my-run"


def test_open_run_generates_id_when_omitted(db_path: Path) -> None:
    rid = open_run(project="p", approach=1, db_path=db_path)
    assert rid.startswith("run-p-approach1-")


def test_open_run_inserts_row(db_path: Path) -> None:
    open_run(project="p", approach=1, run_id="r1", db_path=db_path)
    row = q_one(db_path, "SELECT * FROM runs WHERE id = ?", ("r1",))
    assert row is not None
    assert row["project"] == "p"
    assert row["approach"] == 1
    assert row["started_at"] is not None
    assert row["ended_at"] is None


def test_open_run_invalid_approach_zero(db_path: Path) -> None:
    with pytest.raises(ValueError, match="approach must be 1 or 2"):
        open_run(project="p", approach=0, db_path=db_path)


def test_open_run_invalid_approach_five(db_path: Path) -> None:
    with pytest.raises(ValueError, match="approach must be 1 or 2"):
        open_run(project="p", approach=5, db_path=db_path)


def test_close_run_sets_ended_at(db_path: Path, run_id: str) -> None:
    close_run(run_id=run_id, terminal_phase=3, db_path=db_path)
    row = q_one(db_path, "SELECT * FROM runs WHERE id = ?", (run_id,))
    assert row is not None
    assert row["ended_at"] is not None
    assert row["terminal_phase"] == 3


# ---------------------------------------------------------------------------
# open_session / close_session
# ---------------------------------------------------------------------------


def test_open_session_inserts_row(db_path: Path, run_id: str) -> None:
    open_session(run_id=run_id, session_number=1, db_path=db_path)
    count = q_count(db_path, "sessions", "run_id = ? AND session_number = 1", (run_id,))
    assert count == 1


def test_close_session_sets_ended_at(db_path: Path, run_id: str) -> None:
    open_session(run_id=run_id, session_number=1, db_path=db_path)
    close_session(run_id=run_id, session_number=1, db_path=db_path)
    row = q_one(
        db_path,
        "SELECT ended_at FROM sessions WHERE run_id = ? AND session_number = 1",
        (run_id,),
    )
    assert row is not None
    assert row["ended_at"] is not None


# ---------------------------------------------------------------------------
# set_phase_status
# ---------------------------------------------------------------------------


def test_set_phase_status_in_progress(db_path: Path, run_id: str) -> None:
    set_phase_status(
        run_id=run_id, phase_number=2, status=PhaseStatus.IN_PROGRESS, db_path=db_path
    )
    row = q_one(
        db_path,
        "SELECT * FROM phase_progress WHERE run_id = ? AND phase_number = 2",
        (run_id,),
    )
    assert row is not None
    assert row["status"] == "in_progress"
    assert row["entered_at"] is not None
    assert row["completed_at"] is None


def test_set_phase_status_completed(db_path: Path, run_id: str) -> None:
    set_phase_status(
        run_id=run_id, phase_number=2, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    row = q_one(
        db_path,
        "SELECT * FROM phase_progress WHERE run_id = ? AND phase_number = 2",
        (run_id,),
    )
    assert row is not None
    assert row["status"] == "completed"
    assert row["completed_at"] is not None


def test_set_phase_status_upsert_no_duplicate(db_path: Path, run_id: str) -> None:
    set_phase_status(
        run_id=run_id, phase_number=2, status=PhaseStatus.IN_PROGRESS, db_path=db_path
    )
    set_phase_status(
        run_id=run_id, phase_number=2, status=PhaseStatus.COMPLETED, db_path=db_path
    )
    count = q_count(db_path, "phase_progress", "run_id = ?", (run_id,))
    assert count == 1


# ---------------------------------------------------------------------------
# model_assignments
# ---------------------------------------------------------------------------


def test_seed_model_assignments_inserts_phase_rows(db_path: Path, run_id: str) -> None:
    seed_model_assignments(
        run_id=run_id,
        phase_map={2: "llama3-local", 3: "llama3-local"},
        db_path=db_path,
    )
    count = q_count(db_path, "model_assignments", "run_id = ?", (run_id,))
    assert count == 2


def test_seed_model_assignments_does_not_overwrite_by_default(
    db_path: Path, run_id: str
) -> None:
    seed_model_assignments(run_id=run_id, phase_map={2: "a"}, db_path=db_path)
    seed_model_assignments(run_id=run_id, phase_map={2: "b"}, db_path=db_path)

    row = q_one(
        db_path,
        "SELECT model, source FROM model_assignments WHERE run_id = ? AND phase_number = 2",
        (run_id,),
    )
    assert row is not None
    assert row["model"] == "a"
    assert row["source"] == "setup"


def test_set_model_assignment_upserts_and_marks_reassignment(
    db_path: Path, run_id: str
) -> None:
    seed_model_assignments(run_id=run_id, phase_map={2: "a"}, db_path=db_path)
    set_model_assignment(run_id=run_id, phase_number=2, model="b", db_path=db_path)

    row = q_one(
        db_path,
        "SELECT model, source FROM model_assignments WHERE run_id = ? AND phase_number = 2",
        (run_id,),
    )
    assert row is not None
    assert row["model"] == "b"
    assert row["source"] == "reassignment"


def test_get_model_assignment_returns_none_when_missing(db_path: Path, run_id: str) -> None:
    result = get_model_assignment(run_id=run_id, phase_number=2, db_path=db_path)
    assert result is None


def test_get_model_assignment_returns_model_when_present(db_path: Path, run_id: str) -> None:
    seed_model_assignments(run_id=run_id, phase_map={2: "llama3-local"}, db_path=db_path)
    result = get_model_assignment(run_id=run_id, phase_number=2, db_path=db_path)
    assert result == "llama3-local"


# ---------------------------------------------------------------------------
# accept_artifact
# ---------------------------------------------------------------------------


def test_accept_artifact_inserts_row(db_path: Path, run_id: str) -> None:
    accept_artifact(
        run_id=run_id,
        artifact_id="REQ-01",
        artifact_type="Requirements Document",
        phase=2,
        db_path=db_path,
    )
    count = q_count(db_path, "artifacts", "id = ? AND run_id = ?", ("REQ-01", run_id))
    assert count == 1


def test_accept_artifact_status_is_accepted(db_path: Path, run_id: str) -> None:
    accept_artifact(
        run_id=run_id,
        artifact_id="REQ-01",
        artifact_type="Requirements Document",
        phase=2,
        db_path=db_path,
    )
    row = q_one(db_path, "SELECT status FROM artifacts WHERE id = ?", ("REQ-01",))
    assert row is not None
    assert row["status"] == "accepted"


def test_accept_artifact_upsert_no_duplicate(db_path: Path, run_id: str) -> None:
    for _ in range(3):
        accept_artifact(
            run_id=run_id,
            artifact_id="REQ-01",
            artifact_type="Requirements Document",
            phase=2,
            db_path=db_path,
        )
    count = q_count(db_path, "artifacts", "id = ?", ("REQ-01",))
    assert count == 1


def test_accept_artifact_writes_traceability_links(db_path: Path, run_id: str) -> None:
    # Pre-insert upstream artifacts so the FK on traceability_links is satisfied.
    accept_artifact(
        run_id=run_id, artifact_id="REQ-01",
        artifact_type="Requirements Document", phase=2, db_path=db_path,
    )
    accept_artifact(
        run_id=run_id, artifact_id="REQ-02",
        artifact_type="Requirements Document", phase=2, db_path=db_path,
    )
    accept_artifact(
        run_id=run_id,
        artifact_id="ARCH-01",
        artifact_type="Architecture Document",
        phase=3,
        upstream_ids=["REQ-01", "REQ-02"],
        db_path=db_path,
    )
    count = q_count(
        db_path, "traceability_links", "from_artifact_id = ?", ("ARCH-01",)
    )
    assert count == 2


def test_accept_artifact_no_traceability_links_by_default(db_path: Path, run_id: str) -> None:
    accept_artifact(
        run_id=run_id,
        artifact_id="SEED-01",
        artifact_type="Project Charter",
        phase=2,
        db_path=db_path,
    )
    count = q_count(
        db_path, "traceability_links", "from_artifact_id = ?", ("SEED-01",)
    )
    assert count == 0


# ---------------------------------------------------------------------------
# log_interaction
# ---------------------------------------------------------------------------


def test_log_interaction_returns_int(db_path: Path, run_id: str) -> None:
    rowid = log_interaction(
        run_id=run_id,
        sdlc_phase=2,
        approach=1,
        agent_role="analyst",
        model="gpt-4",
        prompt="Write requirements.",
        response="Here are the requirements.",
        iteration=1,
        outcome=Outcome.ACCEPTED,
        human_modified=False,
        db_path=db_path,
    )
    assert isinstance(rowid, int)
    assert rowid > 0


def test_log_interaction_inserts_row(db_path: Path, run_id: str) -> None:
    log_interaction(
        run_id=run_id,
        sdlc_phase=2,
        approach=1,
        agent_role="architect",
        model="gpt-4",
        prompt="Design the system.",
        response="Here is the architecture.",
        iteration=1,
        outcome=Outcome.ACCEPTED,
        human_modified=False,
        db_path=db_path,
    )
    count = q_count(db_path, "interactions", "run_id = ?", (run_id,))
    assert count == 1


def test_log_interaction_human_modified_requires_notes(db_path: Path, run_id: str) -> None:
    with pytest.raises(ValueError, match="human_modification_notes"):
        log_interaction(
            run_id=run_id,
            sdlc_phase=2,
            approach=1,
            agent_role="analyst",
            model="gpt-4",
            prompt="Write requirements.",
            response="Here are the requirements.",
            iteration=1,
            outcome=Outcome.ACCEPTED_WITH_MODIFICATIONS,
            human_modified=True,
            human_modification_notes=None,
            db_path=db_path,
        )


def test_log_interaction_human_modified_with_notes_succeeds(db_path: Path, run_id: str) -> None:
    rowid = log_interaction(
        run_id=run_id,
        sdlc_phase=2,
        approach=1,
        agent_role="analyst",
        model="gpt-4",
        prompt="Write requirements.",
        response="Here are the requirements.",
        iteration=1,
        outcome=Outcome.ACCEPTED_WITH_MODIFICATIONS,
        human_modified=True,
        human_modification_notes="Fixed grammar issues.",
        db_path=db_path,
    )
    assert rowid > 0


# ---------------------------------------------------------------------------
# log_intervention
# ---------------------------------------------------------------------------


def test_log_intervention_returns_int(db_path: Path, run_id: str) -> None:
    rowid = log_intervention(
        run_id=run_id,
        sdlc_phase=2,
        category=InterventionCategory.CORRECTION,
        severity=Severity.MINOR,
        rationale="Minor correction needed.",
        time_spent_minutes=5,
        db_path=db_path,
    )
    assert isinstance(rowid, int)
    assert rowid > 0


def test_log_intervention_inserts_row(db_path: Path, run_id: str) -> None:
    log_intervention(
        run_id=run_id,
        sdlc_phase=3,
        category=InterventionCategory.STRATEGIC_DECISION,
        severity=Severity.MODERATE,
        rationale="Changed the approach.",
        time_spent_minutes=20,
        db_path=db_path,
    )
    count = q_count(db_path, "interventions", "run_id = ?", (run_id,))
    assert count == 1


# ---------------------------------------------------------------------------
# log_validation_result
# ---------------------------------------------------------------------------


def test_log_validation_result_returns_int(db_path: Path, run_id: str) -> None:
    rowid = log_validation_result(
        run_id=run_id,
        sdlc_phase=2,
        validation_type=ValidationType.REVIEW,
        result=ValidationResult.ACCEPTED,
        defects_found=0,
        db_path=db_path,
    )
    assert isinstance(rowid, int)
    assert rowid > 0


def test_log_validation_result_inserts_row(db_path: Path, run_id: str) -> None:
    log_validation_result(
        run_id=run_id,
        sdlc_phase=5,
        validation_type=ValidationType.TESTING,
        result=ValidationResult.REJECTED,
        defects_found=2,
        db_path=db_path,
    )
    count = q_count(db_path, "validation_results", "run_id = ?", (run_id,))
    assert count == 1


# ---------------------------------------------------------------------------
# log_defect / resolve_defect
# ---------------------------------------------------------------------------


def test_log_defect_returns_int(db_path: Path, run_id: str) -> None:
    val_id = log_validation_result(
        run_id=run_id,
        sdlc_phase=2,
        validation_type=ValidationType.REVIEW,
        result=ValidationResult.REJECTED,
        defects_found=1,
        db_path=db_path,
    )
    defect_id = log_defect(
        run_id=run_id,
        validation_result_id=val_id,
        sdlc_phase_detected=2,
        severity=Severity.CRITICAL,
        description="Requirement is ambiguous.",
        db_path=db_path,
    )
    assert isinstance(defect_id, int)
    assert defect_id > 0


def test_resolve_defect_sets_resolved_at(db_path: Path, run_id: str) -> None:
    val_id = log_validation_result(
        run_id=run_id,
        sdlc_phase=2,
        validation_type=ValidationType.REVIEW,
        result=ValidationResult.REJECTED,
        defects_found=1,
        db_path=db_path,
    )
    defect_id = log_defect(
        run_id=run_id,
        validation_result_id=val_id,
        sdlc_phase_detected=2,
        severity=Severity.MINOR,
        description="Typo in a requirement.",
        db_path=db_path,
    )
    resolve_defect(defect_id=defect_id, db_path=db_path)
    row = q_one(db_path, "SELECT resolved_at FROM defects WHERE id = ?", (defect_id,))
    assert row is not None
    assert row["resolved_at"] is not None


# ---------------------------------------------------------------------------
# log_pipeline_event
# ---------------------------------------------------------------------------


def test_log_pipeline_event_returns_int(db_path: Path, run_id: str) -> None:
    rowid = log_pipeline_event(
        run_id=run_id,
        pipeline_id="pipe-001",
        step="arch_review",
        agent_role="reviewer",
        event_type=PipelineEventType.GATE_PASS,
        detail="Review passed.",
        db_path=db_path,
    )
    assert isinstance(rowid, int)
    assert rowid > 0


def test_log_pipeline_event_inserts_row(db_path: Path, run_id: str) -> None:
    log_pipeline_event(
        run_id=run_id,
        pipeline_id="pipe-001",
        step="req_review",
        agent_role="reviewer",
        event_type=PipelineEventType.GATE_FAIL,
        detail="Review failed.",
        db_path=db_path,
    )
    count = q_count(db_path, "pipeline_events", "run_id = ?", (run_id,))
    assert count == 1


# ---------------------------------------------------------------------------
# log_violation
# ---------------------------------------------------------------------------


def test_log_violation_returns_int(db_path: Path, run_id: str) -> None:
    rowid = log_violation(
        violation_type=ViolationType.TRACEABILITY_GAP,
        detail="Artifact lacks upstream link.",
        run_id=run_id,
        db_path=db_path,
    )
    assert isinstance(rowid, int)
    assert rowid > 0


def test_log_violation_inserts_row(db_path: Path, run_id: str) -> None:
    log_violation(
        violation_type=ViolationType.MISSING_REQUIRED_FIELD,
        detail="Required field 'outcome' is missing.",
        run_id=run_id,
        db_path=db_path,
    )
    count = q_count(db_path, "violations", "run_id = ?", (run_id,))
    assert count == 1


# ---------------------------------------------------------------------------
# Unknown enum value: warning emitted, violations row written
# ---------------------------------------------------------------------------


def test_unknown_enum_emits_warning_and_writes_violation(db_path: Path, run_id: str) -> None:
    with pytest.warns(UserWarning, match="unexpected value"):
        log_intervention(
            run_id=run_id,
            sdlc_phase=2,
            category="not_a_valid_category",
            severity=Severity.MINOR,
            rationale="Testing unknown enum handling.",
            time_spent_minutes=1,
            db_path=db_path,
        )
    count = q_count(db_path, "interventions", "run_id = ?", (run_id,))
    assert count == 1


def test_unknown_enum_does_not_block_write(db_path: Path, run_id: str) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rowid = log_interaction(
            run_id=run_id,
            sdlc_phase=2,
            approach=1,
            agent_role="analyst",
            model="gpt-4",
            prompt="Write requirements.",
            response="Here are the requirements.",
            iteration=1,
            outcome="not_a_valid_outcome",
            human_modified=False,
            db_path=db_path,
        )
    assert rowid > 0


# ---------------------------------------------------------------------------
# SDLC_DB_PATH environment variable (db.py lines 46-47)
# ---------------------------------------------------------------------------


def test_sdlc_db_path_env_var_is_used(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """open_run uses SDLC_DB_PATH when no db_path argument is supplied."""
    import sqlite3 as _sqlite3

    custom_db = tmp_path / "custom.db"
    setup_db(custom_db)
    monkeypatch.setenv("SDLC_DB_PATH", str(custom_db))
    rid = open_run(project="p", approach=1, run_id="env-run")  # no db_path
    assert rid == "env-run"
    conn = _sqlite3.connect(custom_db)
    row = conn.execute("SELECT id FROM runs WHERE id = ?", ("env-run",)).fetchone()
    conn.close()
    assert row is not None


# ---------------------------------------------------------------------------
# Rollback path on integrity error (db.py lines 60-62)
# ---------------------------------------------------------------------------


def test_connect_rollback_on_duplicate_run_id(db_path: Path) -> None:
    """A second open_run with the same run_id triggers the rollback branch."""
    import sqlite3 as _sqlite3

    open_run(project="p", approach=1, run_id="dup", db_path=db_path)
    with pytest.raises(_sqlite3.IntegrityError):
        open_run(project="p", approach=1, run_id="dup", db_path=db_path)
    conn = _sqlite3.connect(db_path)
    count = conn.execute(
        "SELECT COUNT(*) FROM runs WHERE id = 'dup'"
    ).fetchone()[0]
    conn.close()
    assert count == 1
