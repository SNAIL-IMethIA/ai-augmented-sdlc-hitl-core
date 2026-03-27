"""test_providers_intervention.py: Tests for sdlc_core.providers.intervention."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from sdlc_core.db import accept_artifact, open_run, setup_db
from sdlc_core.providers.intervention import InterventionLogger
from sdlc_core.session import Session
from tests.conftest import q_count, q_one

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(tmp_path: Path) -> tuple[Path, Session]:
    """Create a fresh test database and return (db_path, session)."""
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-int-01", db_path=db_path)
    return db_path, Session(run_id=run_id, approach=1, active_phase=3, db_path=db_path)


def _make_inputs(*responses: str) -> Callable[[str], str]:
    it = iter(responses)
    return lambda _: next(it)


def _register_artifact(db_path: Path, run_id: str, artifact_id: str) -> None:
    """Insert a minimal accepted artifact so FK constraints pass."""
    accept_artifact(
        run_id=run_id,
        artifact_id=artifact_id,
        artifact_type="test_artifact",
        phase=3,
        db_path=db_path,
    )


def _happy_inputs(
    *,
    category: str = "1",
    severity: str = "1",
    artifact: str = "",
    rationale: str = "needed fixing",
    minutes: str = "5",
) -> Callable[[str], str]:
    """Return an input mock for the standard happy-path flow (artifact prompt included)."""
    return _make_inputs(category, severity, artifact, rationale, minutes)


def _happy_inputs_preset(
    *,
    category: str = "1",
    severity: str = "1",
    rationale: str = "needed fixing",
    minutes: str = "5",
) -> Callable[[str], str]:
    """Return an input mock when artifact_id is pre-supplied (no artifact prompt)."""
    return _make_inputs(category, severity, rationale, minutes)


# ---------------------------------------------------------------------------
# Happy path - row written
# ---------------------------------------------------------------------------


def test_log_writes_one_intervention_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs())
    logger.log()
    assert q_count(db_path, "interventions") == 1


def test_log_returns_positive_row_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs())
    row_id = logger.log()
    assert isinstance(row_id, int)
    assert row_id > 0


# ---------------------------------------------------------------------------
# Field values stored correctly
# ---------------------------------------------------------------------------


def test_log_stores_category(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    # category index 6 = "manual_edit"
    monkeypatch.setattr("builtins.input", _happy_inputs(category="6"))
    logger.log()
    row = q_one(db_path, "SELECT category FROM interventions")
    assert row is not None
    assert row["category"] == "manual_edit"


def test_log_stores_severity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    # severity index 3 = "critical"
    monkeypatch.setattr("builtins.input", _happy_inputs(severity="3"))
    logger.log()
    row = q_one(db_path, "SELECT severity FROM interventions")
    assert row is not None
    assert row["severity"] == "critical"


def test_log_stores_rationale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs(rationale="Model output was wrong"))
    logger.log()
    row = q_one(db_path, "SELECT rationale FROM interventions")
    assert row is not None
    assert row["rationale"] == "Model output was wrong"


def test_log_stores_time_spent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs(minutes="15"))
    logger.log()
    row = q_one(db_path, "SELECT time_spent_minutes FROM interventions")
    assert row is not None
    assert row["time_spent_minutes"] == 15


def test_log_stores_sdlc_phase_from_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs())
    logger.log()
    row = q_one(db_path, "SELECT sdlc_phase FROM interventions")
    assert row is not None
    assert row["sdlc_phase"] == session.active_phase


# ---------------------------------------------------------------------------
# Artifact ID handling
# ---------------------------------------------------------------------------


def test_log_null_artifact_when_empty_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs(artifact=""))
    logger.log()
    row = q_one(db_path, "SELECT artifact_id FROM interventions")
    assert row is not None
    assert row["artifact_id"] is None


def test_log_stores_typed_artifact_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    _register_artifact(db_path, session.run_id, "IMPL-07")
    logger = InterventionLogger(session)
    monkeypatch.setattr("builtins.input", _happy_inputs(artifact="IMPL-07"))
    logger.log()
    row = q_one(db_path, "SELECT artifact_id FROM interventions")
    assert row is not None
    assert row["artifact_id"] == "IMPL-07"


def test_log_preset_artifact_skips_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    _register_artifact(db_path, session.run_id, "ARCH-04")
    logger = InterventionLogger(session)
    # Preset: no artifact prompt; only category + severity + rationale + minutes
    monkeypatch.setattr("builtins.input", _happy_inputs_preset())
    logger.log(artifact_id="ARCH-04")
    row = q_one(db_path, "SELECT artifact_id FROM interventions")
    assert row is not None
    assert row["artifact_id"] == "ARCH-04"


# ---------------------------------------------------------------------------
# Re-prompting on invalid input
# ---------------------------------------------------------------------------


def test_log_reprompts_on_invalid_category(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    # "0" and "9" and "x" are all invalid for 8 options; "2" is correction
    monkeypatch.setattr(
        "builtins.input",
        _make_inputs("0", "9", "x", "2", "1", "", "needed it", "3"),
    )
    logger.log()
    row = q_one(db_path, "SELECT category FROM interventions")
    assert row is not None
    assert row["category"] == "correction"


def test_log_reprompts_on_invalid_severity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    # valid category, invalid severity twice, then "2" (moderate)
    monkeypatch.setattr(
        "builtins.input",
        _make_inputs("1", "4", "0", "2", "", "needed it", "3"),
    )
    logger.log()
    row = q_one(db_path, "SELECT severity FROM interventions")
    assert row is not None
    assert row["severity"] == "moderate"


def test_log_reprompts_on_empty_rationale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    monkeypatch.setattr(
        "builtins.input",
        _make_inputs("1", "1", "", "", "", "finally a rationale", "5"),
    )
    logger.log()
    row = q_one(db_path, "SELECT rationale FROM interventions")
    assert row is not None
    assert row["rationale"] == "finally a rationale"


def test_log_reprompts_on_invalid_minutes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    logger = InterventionLogger(session)
    # "0", "abc", and "-1" are invalid; "10" is valid
    monkeypatch.setattr(
        "builtins.input",
        _make_inputs("1", "1", "", "rationale", "0", "abc", "-1", "10"),
    )
    logger.log()
    row = q_one(db_path, "SELECT time_spent_minutes FROM interventions")
    assert row is not None
    assert row["time_spent_minutes"] == 10
