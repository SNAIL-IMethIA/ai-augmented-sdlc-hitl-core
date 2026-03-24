"""test_setup_run.py: Tests for sdlc_core.setup_run."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# _die and _warn
# ---------------------------------------------------------------------------


def test_die_exits_with_message(capsys: pytest.CaptureFixture[str]) -> None:
    from sdlc_core.setup_run import _die

    with pytest.raises(SystemExit):
        _die("something went wrong")

    err = capsys.readouterr().err
    assert "something went wrong" in err


def test_warn_prints_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    from sdlc_core.setup_run import _warn

    _warn("heads up")
    assert "heads up" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _load_toml
# ---------------------------------------------------------------------------


def test_load_toml_missing_file_exits(tmp_path: Path) -> None:
    from sdlc_core.setup_run import _load_toml

    with pytest.raises(SystemExit):
        _load_toml(tmp_path / "missing.toml", "run_config.toml")


def test_load_toml_parses_valid_file(tmp_path: Path) -> None:
    f = tmp_path / "cfg.toml"
    f.write_text('[run]\nproject = "myproject"\n', encoding="utf-8")
    from sdlc_core.setup_run import _load_toml

    data = _load_toml(f, "cfg.toml")
    assert data["run"]["project"] == "myproject"


# ---------------------------------------------------------------------------
# _validate_run_config
# ---------------------------------------------------------------------------


def test_validate_run_config_missing_project_exits() -> None:
    from sdlc_core.setup_run import _validate_run_config

    with pytest.raises(SystemExit):
        _validate_run_config({"run": {"approach": "A1"}})


def test_validate_run_config_missing_approach_exits() -> None:
    from sdlc_core.setup_run import _validate_run_config

    with pytest.raises(SystemExit):
        _validate_run_config({"run": {"project": "p"}})


def test_validate_run_config_invalid_approach_exits() -> None:
    from sdlc_core.setup_run import _validate_run_config

    with pytest.raises(SystemExit):
        _validate_run_config({"run": {"project": "p", "approach": "A9"}})


def test_validate_run_config_string_approach() -> None:
    from sdlc_core.setup_run import _validate_run_config

    section = _validate_run_config({"run": {"project": "p", "approach": "A2"}})
    assert section["approach"] == "A2"


def test_validate_run_config_int_approach() -> None:
    from sdlc_core.setup_run import _validate_run_config

    section = _validate_run_config({"run": {"project": "p", "approach": 2}})
    assert section["approach"] == 2


def test_validate_run_config_all_string_approaches_valid() -> None:
    from sdlc_core.setup_run import _validate_run_config

    for approach in ("A1", "A2"):
        _validate_run_config({"run": {"project": "p", "approach": approach}})


def test_validate_run_config_all_int_approaches_valid() -> None:
    from sdlc_core.setup_run import _validate_run_config

    for approach in (1, 2):
        _validate_run_config({"run": {"project": "p", "approach": approach}})


# ---------------------------------------------------------------------------
# _validate_models
# ---------------------------------------------------------------------------


def test_validate_models_model_not_in_toml_exits() -> None:
    from sdlc_core.setup_run import _validate_models

    run_cfg = {
        "project": "p",
        "approach": "A1",
        "phases": {"phase2": "ghost-model"},
    }
    with pytest.raises(SystemExit):
        _validate_models(run_cfg, {"models": {}})


def test_validate_models_missing_env_var_exits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sdlc_core.setup_run import _validate_models

    monkeypatch.delenv("MY_SECRET_KEY", raising=False)
    run_cfg = {
        "project": "p",
        "approach": "A1",
        "phases": {"phase2": "themodel"},
    }
    with pytest.raises(SystemExit):
        _validate_models(
            run_cfg, {"models": {"themodel": {"api_key_env": "MY_SECRET_KEY"}}}
        )


def test_validate_models_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    from sdlc_core.setup_run import _validate_models

    monkeypatch.setenv("MY_KEY", "secret")
    run_cfg = {
        "project": "p",
        "approach": "A1",
        "phases": {"phase2": "m", "phase3": "m"},
    }
    phase_map = _validate_models(
        run_cfg, {"models": {"m": {"api_key_env": "MY_KEY"}}}
    )
    assert phase_map[2] == "m"
    assert phase_map[3] == "m"


def test_validate_models_no_api_key_env() -> None:
    from sdlc_core.setup_run import _validate_models

    run_cfg = {
        "project": "p",
        "approach": "A1",
        "phases": {"phase2": "localmodel"},
    }
    phase_map = _validate_models(
        run_cfg, {"models": {"localmodel": {"api_key_env": ""}}}
    )
    assert phase_map[2] == "localmodel"


def test_validate_models_unassigned_phase_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from sdlc_core.setup_run import _validate_models

    run_cfg = {
        "project": "p",
        "approach": "A1",
        "phases": {},
    }
    _validate_models(run_cfg, {"models": {}})
    err = capsys.readouterr().err
    assert "WARNING" in err


# ---------------------------------------------------------------------------
# _resolve_sha
# ---------------------------------------------------------------------------


def test_resolve_sha_from_pyproject_rev(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry.dependencies]\n'
        '"sdlc-core" = {git = "https://github.com/OWNER/repo.git", rev = "abc123def"}\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    from sdlc_core.setup_run import _resolve_sha

    assert _resolve_sha() == "abc123def"


def test_resolve_sha_falls_back_to_git_when_no_rev(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    # sdlc-core dep is a plain version string, not a git dep.
    pyproject.write_text(
        '[tool.poetry.dependencies]\n"sdlc-core" = ">=0.1"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="deadbeef1234\n", returncode=0)
        from sdlc_core.setup_run import _resolve_sha

        sha = _resolve_sha()
    assert sha == "deadbeef1234"


def test_resolve_sha_falls_back_to_git_when_no_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="cafebabe\n", returncode=0)
        from sdlc_core.setup_run import _resolve_sha

        sha = _resolve_sha()
    assert sha == "cafebabe"


def test_resolve_sha_returns_unknown_on_all_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with patch("subprocess.run", side_effect=OSError("no git")):
        from sdlc_core.setup_run import _resolve_sha

        sha = _resolve_sha()
    assert sha == "unknown"


# ---------------------------------------------------------------------------
# _write_core_version
# ---------------------------------------------------------------------------


def test_write_core_version_creates_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with patch("sdlc_core.setup_run._resolve_sha", return_value="sha999"):
        from sdlc_core.setup_run import _write_core_version

        returned = _write_core_version()

    assert returned == "sha999"
    assert (tmp_path / "core_version.txt").read_text(encoding="utf-8") == "sha999\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_missing_run_config_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    from sdlc_core.setup_run import main

    with pytest.raises(SystemExit):
        main()


def test_main_missing_models_toml_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_cfg = tmp_path / "run_config.toml"
    run_cfg.write_text(
        '[run]\nproject = "p"\napproach = "A1"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    # models.toml does not exist. SDLC_MODELS_TOML is not set.
    monkeypatch.delenv("SDLC_MODELS_TOML", raising=False)
    from sdlc_core.setup_run import main

    with pytest.raises(SystemExit):
        main()


def test_main_success_prints_run_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_cfg = tmp_path / "run_config.toml"
    run_cfg.write_text(
        '[run]\nproject = "proj1"\napproach = "A2"\n'
        '[phases]\nphase2 = "localmodel"\n',
        encoding="utf-8",
    )
    models = tmp_path / "models.toml"
    models.write_text(
        '[models.localmodel]\nprovider = "ollama"\nmodel_id = "llama3"\n',
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDLC_MODELS_TOML", str(models))

    fake_db = tmp_path / "experiment.db"
    with (
        patch("sdlc_core.setup_run.setup_db", return_value=fake_db),
        patch("sdlc_core.setup_run.open_run", return_value="run-XYZ"),
        patch("sdlc_core.setup_run._resolve_sha", return_value="abc123"),
    ):
        from sdlc_core.setup_run import main

        main()

    out = capsys.readouterr().out
    assert "run-XYZ" in out
    assert "proj1" in out
    assert "A2" in out


def test_main_approach_int_resolves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_cfg = tmp_path / "run_config.toml"
    # approach as integer 1, not string
    run_cfg.write_text(
        '[run]\nproject = "p"\napproach = 1\n',
        encoding="utf-8",
    )
    models = tmp_path / "models.toml"
    models.write_text("[models]\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDLC_MODELS_TOML", str(models))

    fake_db = tmp_path / "experiment.db"
    with (
        patch("sdlc_core.setup_run.setup_db", return_value=fake_db),
        patch("sdlc_core.setup_run.open_run", return_value="run-001"),
        patch("sdlc_core.setup_run._resolve_sha", return_value="sha"),
    ):
        from sdlc_core.setup_run import main

        main()
