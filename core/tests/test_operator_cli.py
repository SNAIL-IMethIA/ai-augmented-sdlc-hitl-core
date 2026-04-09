"""test_operator_cli.py: Tests for operator-facing status and diff summary commands."""

from __future__ import annotations

import json
from pathlib import Path

from sdlc_core.db import (
    accept_artifact,
    log_interaction,
    log_intervention,
    open_run,
    set_phase_status,
    setup_db,
)
from sdlc_core.diff_summary import _artifact_ids_from_paths, _summary
from sdlc_core.status import _status_snapshot


def test_status_snapshot_returns_expected_fields(tmp_path: Path) -> None:
    db_path = tmp_path / "experiment.db"
    setup_db(db_path)
    run_id = open_run(project="project1", approach=1, db_path=db_path)

    set_phase_status(run_id=run_id, phase_number=2, status="completed", db_path=db_path)
    set_phase_status(run_id=run_id, phase_number=3, status="in_progress", db_path=db_path)

    accept_artifact(
        run_id=run_id,
        artifact_id="REQ-01",
        artifact_type="system_requirement",
        phase=2,
        db_path=db_path,
    )

    snapshot = _status_snapshot(db_path)

    assert snapshot["has_run"] is True
    assert snapshot["run"]["id"] == run_id
    assert snapshot["active_phase"] == 3
    assert snapshot["last_accepted_artifact"]["id"] == "REQ-01"
    assert 3 in snapshot["pending_checkpoints"]


def test_artifact_ids_from_paths_extracts_expected_values() -> None:
    paths = [
        "artifacts/phase2/REQ-01.md",
        "artifacts/phase5/IMPL-03.py",
        "README.md",
    ]
    artifact_ids = _artifact_ids_from_paths(paths)
    assert artifact_ids == {"REQ-01", "IMPL-03"}


def test_diff_summary_classifies_human_modified_artifact(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "experiment.db"
    setup_db(db_path)
    run_id = open_run(project="project1", approach=1, db_path=db_path)

    accept_artifact(
        run_id=run_id,
        artifact_id="REQ-01",
        artifact_type="system_requirement",
        phase=2,
        db_path=db_path,
    )

    log_interaction(
        run_id=run_id,
        artifact_id="REQ-01",
        sdlc_phase=2,
        approach=1,
        agent_role="requirements_analyst",
        model="llama3-local",
        prompt="p",
        response="r",
        iteration=1,
        outcome="accepted_with_modifications",
        human_modified=True,
        human_modification_notes="edited for clarity",
        db_path=db_path,
    )

    log_intervention(
        run_id=run_id,
        artifact_id="REQ-01",
        sdlc_phase=2,
        category="manual_edit",
        severity="minor",
        rationale="manual correction",
        time_spent_minutes=2,
        db_path=db_path,
    )

    def fake_run_git(repo: Path, args: list[str]) -> str:
        if args[0] == "diff":
            return "artifacts/phase2/REQ-01.md\nREADME.md"
        if args[0] == "log":
            return "Researcher\nResearcher"
        raise AssertionError(f"Unexpected git args: {args}")

    monkeypatch.setattr("sdlc_core.diff_summary._run_git", fake_run_git)

    result = _summary(repo=tmp_path, db_path=db_path, since="abc123")
    assert result["latest_run_id"] == run_id
    assert result["artifact_classification"]["REQ-01"] == "human-modified"
    assert result["authors"] == {"Researcher": 2}
    assert "README.md" in result["unlinked_files"]


def test_status_snapshot_json_serializable(tmp_path: Path) -> None:
    db_path = tmp_path / "experiment.db"
    setup_db(db_path)
    payload = _status_snapshot(db_path)
    encoded = json.dumps(payload)
    assert "No runs found" in encoded


def test_status_snapshot_handles_missing_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "empty.db"
    db_path.touch()

    payload = _status_snapshot(db_path)

    assert payload["has_run"] is False
    assert "Run poetry run sdlc-setup first" in payload["message"]
