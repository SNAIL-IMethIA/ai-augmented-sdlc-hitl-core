"""test_assign_model.py: Tests for sdlc_core.assign_model."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sdlc_core.db import open_run, setup_db

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_models(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# _die
# ---------------------------------------------------------------------------


def test_die_exits_with_message(capsys: pytest.CaptureFixture[str]) -> None:
    from sdlc_core.assign_model import _die

    with pytest.raises(SystemExit):
        _die("bad input")

    assert "bad input" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _load_models_toml
# ---------------------------------------------------------------------------


def test_load_models_toml_reads_env_var_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "custom_models.toml"
    toml.write_text('[models.m]\nprovider = "ollama"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))

    from sdlc_core.assign_model import _load_models_toml

    data = _load_models_toml()
    assert "m" in data["models"]


def test_load_models_toml_missing_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SDLC_MODELS_TOML", str(tmp_path / "ghost.toml"))

    from sdlc_core.assign_model import _load_models_toml

    with pytest.raises(SystemExit):
        _load_models_toml()


def test_load_models_toml_default_path_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SDLC_MODELS_TOML", raising=False)
    monkeypatch.chdir(tmp_path)

    from sdlc_core.assign_model import _load_models_toml

    with pytest.raises(SystemExit):
        _load_models_toml()


# ---------------------------------------------------------------------------
# _validate_model
# ---------------------------------------------------------------------------


def test_validate_model_not_in_toml_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sdlc_core.assign_model import _validate_model

    with pytest.raises(SystemExit):
        _validate_model("ghost", {"models": {"other": {}}})


def test_validate_model_missing_env_var_exits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sdlc_core.assign_model import _validate_model

    monkeypatch.delenv("MISSING_KEY", raising=False)
    with pytest.raises(SystemExit):
        _validate_model(
            "m", {"models": {"m": {"api_key_env": "MISSING_KEY"}}}
        )


def test_validate_model_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    from sdlc_core.assign_model import _validate_model

    monkeypatch.setenv("MY_KEY", "tok")
    # Should not raise.
    _validate_model("m", {"models": {"m": {"api_key_env": "MY_KEY"}}})


def test_validate_model_no_key_env() -> None:
    from sdlc_core.assign_model import _validate_model

    # Local model with empty api_key_env: should not raise.
    _validate_model("local", {"models": {"local": {"api_key_env": ""}}})


def test_validate_model_manual_provider_disallowed_exits() -> None:
    from sdlc_core.assign_model import _validate_model

    with pytest.raises(SystemExit):
        _validate_model("x", {"models": {"x": {"provider": "manual"}}})


def test_validate_model_manual_name_disallowed_exits() -> None:
    from sdlc_core.assign_model import _validate_model

    with pytest.raises(SystemExit):
        _validate_model("manual", {"models": {"manual": {"provider": "ollama"}}})


def test_validate_model_no_entry_shows_available(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from sdlc_core.assign_model import _validate_model

    with pytest.raises(SystemExit):
        _validate_model("ghost", {"models": {"a": {}, "b": {}}})

    err = capsys.readouterr().err
    assert "a" in err or "b" in err


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def _setup_db_and_run(tmp_path: Path) -> tuple[Path, str]:
    """Create a DB with one run and return (db_path, run_id)."""
    db = setup_db(tmp_path / "logs" / "experiment.db")
    run_id = open_run(project="proj", approach=1, db_path=db)
    return db, run_id


def test_main_run_id_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text('[models.localmodel]\nprovider = "ollama"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    monkeypatch.chdir(tmp_path)
    _setup_db_and_run(tmp_path)

    test_args = [
        "sdlc-assign-model",
        "--run-id", "nonexistent-run",
        "--phase", "3",
        "--model", "localmodel",
    ]
    with patch("sys.argv", test_args):
        from sdlc_core.assign_model import main

        with pytest.raises(SystemExit):
            main()


def test_main_success_writes_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text('[models.localmodel]\nprovider = "ollama"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    # Point _connect at our tmp DB.
    monkeypatch.setenv("SDLC_DB_PATH", str(tmp_path / "logs" / "experiment.db"))
    monkeypatch.chdir(tmp_path)

    _, run_id = _setup_db_and_run(tmp_path)

    test_args = [
        "sdlc-assign-model",
        "--run-id", run_id,
        "--phase", "4",
        "--model", "localmodel",
    ]
    with patch("sys.argv", test_args):
        from sdlc_core.assign_model import main

        main()

    # Confirm a violation row was written.
    import sqlite3

    conn = sqlite3.connect(tmp_path / "logs" / "experiment.db")
    rows = conn.execute(
        "SELECT * FROM violations WHERE run_id = ? AND violation_type = 'other'",
        (run_id,),
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    assert "localmodel" in rows[0][4]  # detail column (index 4) contains model name


def test_main_invalid_phase_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text('[models.localmodel]\nprovider = "ollama"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    monkeypatch.chdir(tmp_path)

    test_args = [
        "sdlc-assign-model",
        "--run-id", "any",
        "--phase", "99",  # out of 2-8 range
        "--model", "localmodel",
    ]
    with patch("sys.argv", test_args):
        from sdlc_core.assign_model import main

        with pytest.raises(SystemExit):
            main()


def test_main_model_not_in_toml_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    toml = tmp_path / "models.toml"
    toml.write_text('[models.localmodel]\nprovider = "ollama"\n', encoding="utf-8")
    monkeypatch.setenv("SDLC_MODELS_TOML", str(toml))
    monkeypatch.chdir(tmp_path)
    _setup_db_and_run(tmp_path)

    test_args = [
        "sdlc-assign-model",
        "--run-id", "any",
        "--phase", "3",
        "--model", "ghost-model",
    ]
    with patch("sys.argv", test_args):
        from sdlc_core.assign_model import main

        with pytest.raises(SystemExit):
            main()
