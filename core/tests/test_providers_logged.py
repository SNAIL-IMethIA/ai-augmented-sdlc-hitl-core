"""test_providers_logged.py: Tests for sdlc_core.providers.logged."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from sdlc_core.db import accept_artifact, open_run, setup_db
from sdlc_core.providers.logged import LoggedProvider
from sdlc_core.session import Session
from tests.conftest import q_count, q_one

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(tmp_path: Path) -> tuple[Path, Session]:
    """Create a fresh test database and return (db_path, session)."""
    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=2, run_id="run-log-01", db_path=db_path)
    return db_path, Session(run_id=run_id, approach=2, active_phase=3, db_path=db_path)


def _mock_provider(response: str = "model output") -> MagicMock:
    provider = MagicMock()
    provider.complete.return_value = response
    provider._model_id = "test-model"  # pyright: ignore[reportPrivateUsage]
    return provider


def _make_inputs(*responses: str) -> Callable[[str], str]:
    it = iter(responses)
    return lambda _: next(it)


def _register_artifact(db_path: Path, run_id: str, artifact_id: str) -> None:
    accept_artifact(
        run_id=run_id,
        artifact_id=artifact_id,
        artifact_type="test_artifact",
        phase=3,
        db_path=db_path,
    )


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------


def test_complete_returns_provider_response(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider("hello"), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    assert provider.complete("prompt", agent_role="developer") == "hello"


def test_complete_calls_underlying_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    mock = _mock_provider()
    provider = LoggedProvider(mock, session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("my prompt", agent_role="architect", system="be brief")
    mock.complete.assert_called_once_with("my prompt", system="be brief")


def test_complete_forwards_kwargs_to_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    mock = _mock_provider()
    provider = LoggedProvider(mock, session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("prompt", agent_role="developer", temperature=0.7)
    _, kwargs = mock.complete.call_args
    assert kwargs.get("temperature") == 0.7


# ---------------------------------------------------------------------------
# DB writes
# ---------------------------------------------------------------------------


def test_complete_writes_one_interaction_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider("resp"), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("the prompt", agent_role="developer")
    assert q_count(db_path, "interactions") == 1


def test_complete_writes_correct_core_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider("resp"), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("the prompt", agent_role="developer")
    row = q_one(db_path, "SELECT * FROM interactions")
    assert row is not None
    assert row["prompt"] == "the prompt"
    assert row["response"] == "resp"
    assert row["agent_role"] == "developer"
    assert row["model"] == "test-model"
    assert row["sdlc_phase"] == 3
    assert row["approach"] == 2
    assert row["artifact_id"] is None
    assert row["outcome"] == "accepted"
    assert row["human_modified"] == 0
    assert row["human_modification_notes"] is None


def test_complete_records_non_negative_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(db_path, "SELECT duration_seconds FROM interactions")
    assert row is not None
    assert row["duration_seconds"] >= 0


def test_complete_records_human_review_seconds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(db_path, "SELECT human_review_seconds FROM interactions")
    assert row is not None
    assert row["human_review_seconds"] >= 0


# ---------------------------------------------------------------------------
# Outcome handling
# ---------------------------------------------------------------------------


def test_outcome_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("r"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(db_path, "SELECT outcome FROM interactions")
    assert row is not None
    assert row["outcome"] == "rejected"


def test_outcome_modified_writes_notes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("m", "Fixed the variable name"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(
        db_path,
        "SELECT outcome, human_modified, human_modification_notes FROM interactions",
    )
    assert row is not None
    assert row["outcome"] == "accepted_with_modifications"
    assert row["human_modified"] == 1
    assert row["human_modification_notes"] == "Fixed the variable name"


def test_outcome_reprompts_on_invalid_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("x", "z", "a"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(db_path, "SELECT outcome FROM interactions")
    assert row is not None
    assert row["outcome"] == "accepted"


def test_notes_reprompts_on_empty_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("m", "", "", "final notes"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(db_path, "SELECT human_modification_notes FROM interactions")
    assert row is not None
    assert row["human_modification_notes"] == "final notes"


def test_outcome_case_insensitive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("R"))
    provider.complete("prompt", agent_role="developer")
    row = q_one(db_path, "SELECT outcome FROM interactions")
    assert row is not None
    assert row["outcome"] == "rejected"


# ---------------------------------------------------------------------------
# Iteration tracking
# ---------------------------------------------------------------------------


def test_iteration_starts_at_one_for_registered_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    _register_artifact(db_path, session.run_id, "ARCH-01")
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("prompt", agent_role="architect", artifact_id="ARCH-01")
    row = q_one(db_path, "SELECT iteration FROM interactions")
    assert row is not None
    assert row["iteration"] == 1


def test_iteration_increments_on_same_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    _register_artifact(db_path, session.run_id, "ARCH-01")
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a", "a"))
    provider.complete("p1", agent_role="architect", artifact_id="ARCH-01")
    provider.complete("p2", agent_role="architect", artifact_id="ARCH-01")
    assert q_count(db_path, "interactions", "iteration = 1") == 1
    assert q_count(db_path, "interactions", "iteration = 2") == 1


def test_iteration_independent_across_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    _register_artifact(db_path, session.run_id, "ARCH-01")
    _register_artifact(db_path, session.run_id, "IMPL-01")
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a", "a"))
    provider.complete("p1", agent_role="architect", artifact_id="ARCH-01")
    provider.complete("p2", agent_role="developer", artifact_id="IMPL-01")
    assert q_count(db_path, "interactions", "artifact_id = 'ARCH-01' AND iteration = 1") == 1
    assert q_count(db_path, "interactions", "artifact_id = 'IMPL-01' AND iteration = 1") == 1


def test_exploratory_prompt_uses_iteration_one_and_null_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path, session = _make_session(tmp_path)
    provider = LoggedProvider(_mock_provider(), session=session)
    monkeypatch.setattr("builtins.input", _make_inputs("a"))
    provider.complete("exploratory prompt", agent_role="developer", artifact_id=None)
    row = q_one(db_path, "SELECT iteration, artifact_id FROM interactions")
    assert row is not None
    assert row["iteration"] == 1
    assert row["artifact_id"] is None


# ---------------------------------------------------------------------------
# model_id property
# ---------------------------------------------------------------------------


def test_model_id_reads_from_provider_attribute(tmp_path: Path) -> None:
    db_path, session = _make_session(tmp_path)
    mock = MagicMock()
    mock._model_id = "my-model-42"  # pyright: ignore[reportPrivateUsage]
    provider = LoggedProvider(mock, session=session)
    assert provider.model_id == "my-model-42"


def test_model_id_falls_back_to_class_name(tmp_path: Path) -> None:
    db_path, session = _make_session(tmp_path)

    class _NoModelId:
        def complete(self, prompt: str, system: str | None = None, **kwargs: Any) -> str:
            return ""

    provider = LoggedProvider(_NoModelId(), session=session)
    assert provider.model_id == "_NoModelId"
