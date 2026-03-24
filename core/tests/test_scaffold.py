"""test_scaffold.py: Tests for sdlc_core.scaffold."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# _get_core_sha
# ---------------------------------------------------------------------------


def test_get_core_sha_success() -> None:
    from sdlc_core.scaffold import _get_core_sha

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="abc123\n", returncode=0)
        sha = _get_core_sha()

    assert sha == "abc123"


def test_get_core_sha_fallback_on_failure() -> None:
    from sdlc_core.scaffold import _get_core_sha

    with patch("subprocess.run", side_effect=OSError("no git")):
        sha = _get_core_sha()

    assert sha == "REPLACE_WITH_CORE_SHA"


# ---------------------------------------------------------------------------
# _get_core_repo_url
# ---------------------------------------------------------------------------


def test_get_core_repo_url_https_passthrough() -> None:
    from sdlc_core.scaffold import _get_core_repo_url

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="https://github.com/OWNER/repo.git\n", returncode=0
        )
        url = _get_core_repo_url()

    assert url == "https://github.com/OWNER/repo"


def test_get_core_repo_url_ssh_converted_to_https() -> None:
    from sdlc_core.scaffold import _get_core_repo_url

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="git@github.com:OWNER/repo.git\n", returncode=0
        )
        url = _get_core_repo_url()

    assert url == "https://github.com/OWNER/repo"


def test_get_core_repo_url_fallback_on_failure() -> None:
    from sdlc_core.scaffold import _get_core_repo_url

    with patch("subprocess.run", side_effect=OSError("no git")):
        url = _get_core_repo_url()

    assert "github.com" in url


# ---------------------------------------------------------------------------
# _prompt_stub
# ---------------------------------------------------------------------------


def test_prompt_stub_approach1_contains_phase_name() -> None:
    from sdlc_core.scaffold import _prompt_stub

    stub = _prompt_stub(1, 2)
    assert "Stakeholder Requirements Definition" in stub
    assert "Phase 2" in stub
    assert "Persona" in stub


def test_prompt_stub_approach2_references_pipeline_contract() -> None:
    from sdlc_core.scaffold import _prompt_stub

    stub = _prompt_stub(2, 3)
    assert "pipeline_contract.json" in stub


def test_prompt_stub_all_phases_for_all_approaches() -> None:
    from sdlc_core.scaffold import _prompt_stub

    for approach in (1, 2):
        for phase in range(2, 9):
            stub = _prompt_stub(approach, phase)
            assert isinstance(stub, str)
            assert len(stub) > 0


# ---------------------------------------------------------------------------
# Content generators
# ---------------------------------------------------------------------------


def test_gitignore_contains_dotenv() -> None:
    from sdlc_core.scaffold import _gitignore

    content = _gitignore()
    assert ".env" in content
    assert "models.toml" in content


def test_env_example_contains_api_key_placeholders() -> None:
    from sdlc_core.scaffold import _env_example

    content = _env_example()
    assert "ANTHROPIC_API_KEY" in content
    assert "OPENAI_API_KEY" in content
    assert "GOOGLE_API_KEY" in content


def test_models_example_toml_contains_ollama_section() -> None:
    from sdlc_core.scaffold import _models_example_toml

    content = _models_example_toml()
    assert "ollama" in content
    assert "manual" in content


def test_run_config_example_approach1_uses_llama3() -> None:
    from sdlc_core.scaffold import _run_config_example_toml

    content = _run_config_example_toml(1)
    assert "llama3-local" in content
    assert 'approach   = "A1"' in content


def test_run_config_example_approach2_uses_llama3() -> None:
    from sdlc_core.scaffold import _run_config_example_toml

    content = _run_config_example_toml(2)
    assert "llama3-local" in content
    assert 'approach   = "A2"' in content


def test_pyproject_toml_contains_sdlc_core_dep() -> None:
    from sdlc_core.scaffold import _pyproject_toml

    content = _pyproject_toml(1, "abc123", "https://github.com/OWNER/repo")
    assert "sdlc-core" in content
    assert "abc123" in content


def test_pyproject_toml_approach2_has_fixed_stack() -> None:
    from sdlc_core.scaffold import _pyproject_toml

    content = _pyproject_toml(2, "sha", "https://github.com/OWNER/repo")
    assert 'sdlc-core = {git = "https://github.com/OWNER/repo.git"' in content
    assert 'rev = "sha", subdirectory = "core"}' in content
    assert 'sdlc-bootstrap = "scripts.bootstrap:main"' in content
    assert 'sdlc-pipeline = "scripts.pipeline_runner:main"' in content
    assert 'langchain = "==0.3.20"' in content
    assert 'langchain-ollama = "==0.2.3"' in content
    assert 'langgraph = "==0.2.74"' in content
    assert 'langsmith = "==0.2.19"' in content
    assert 'autogen-agentchat = "==0.4.9"' in content


def test_pyproject_toml_approach1_has_fixed_base_stack() -> None:
    from sdlc_core.scaffold import _pyproject_toml

    content = _pyproject_toml(1, "sha", "https://github.com/OWNER/repo")
    assert 'sdlc-bootstrap = "scripts.bootstrap:main"' in content
    assert 'sdlc-hitl-run = "scripts.hitl_runner:main"' in content
    assert 'langchain = "==0.3.20"' in content
    assert 'langchain-ollama = "==0.2.3"' in content
    assert 'langgraph = "==0.2.74"' in content
    assert 'langsmith = "==0.2.19"' in content
    assert 'autogen-agentchat = "==0.4.9"' not in content


def test_tooling_example_toml_contains_stack_and_capabilities() -> None:
    from sdlc_core.scaffold import _tooling_example_toml

    content = _tooling_example_toml()
    assert "[stack]" in content
    assert "[capabilities]" in content
    assert 'framework = "langchain"' in content
    assert 'runtime = "langgraph"' in content
    assert 'local_model_interface = "langchain-ollama"' in content
    assert 'tracing = "langsmith"' in content
    assert 'harness = "autogen"' in content
    assert "agent_handoffs = true" in content


def test_readme_contains_approach_description() -> None:
    from sdlc_core.scaffold import _readme

    content = _readme(1, "abc123def456")
    assert "Approach 1" in content
    assert "abc123def456"[:12] in content


def test_copilot_instructions_approach_specific() -> None:
    from sdlc_core.scaffold import _copilot_instructions

    content = _copilot_instructions(2)
    assert "Approach 2" in content
    assert "sdlc-setup" in content


def test_ci_workflow_contains_check_step() -> None:
    from sdlc_core.scaffold import _ci_workflow

    content = _ci_workflow()
    assert "experiment.db" in content
    assert "sdlc_core.check" in content


# ---------------------------------------------------------------------------
# _scaffold
# ---------------------------------------------------------------------------


@pytest.fixture()
def _mock_git() -> Generator[None, None, None]:
    """Patch git calls used by _scaffold."""
    with (
        patch("sdlc_core.scaffold._get_core_sha", return_value="deadbeef"),
        patch(
            "sdlc_core.scaffold._get_core_repo_url",
            return_value="https://github.com/OWNER/repo",
        ),
    ):
        yield


def test_scaffold_approach1_creates_required_files(
    tmp_path: Path, _mock_git: None
) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a1"
    _scaffold(1, output)

    assert (output / ".gitignore").exists()
    assert (output / ".env.example").exists()
    assert (output / "models.example.toml").exists()
    assert (output / "tooling.example.toml").exists()
    assert (output / "run_config.example.toml").exists()
    assert (output / "pyproject.toml").exists()
    assert (output / "README.md").exists()
    assert (output / "core_version.txt").exists()
    assert (output / ".github" / "copilot-instructions.md").exists()
    assert (output / ".github" / "workflows" / "ci.yml").exists()
    assert (output / "scripts" / "__init__.py").exists()
    assert (output / "scripts" / "bootstrap.py").exists()
    assert (output / "scripts" / "hitl_runner.py").exists()


def test_scaffold_approach1_creates_artifact_dirs(
    tmp_path: Path, _mock_git: None
) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a1"
    _scaffold(1, output)

    for phase in range(2, 9):
        assert (output / "artifacts" / f"phase{phase}" / ".gitkeep").exists()


def test_scaffold_approach1_creates_prompt_stubs(
    tmp_path: Path, _mock_git: None
) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a1"
    _scaffold(1, output)

    for phase in range(2, 9):
        stub = output / "prompts" / f"phase{phase}.md"
        assert stub.exists()
        assert stub.stat().st_size > 0


def test_scaffold_approach2_creates_pipeline_contract(
    tmp_path: Path, _mock_git: None
) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a2"
    _scaffold(2, output)

    contract_path = output / "pipeline_contract.json"
    runner_path = output / "scripts" / "pipeline_runner.py"
    bootstrap_path = output / "scripts" / "bootstrap.py"
    assert contract_path.exists()
    assert runner_path.exists()
    assert bootstrap_path.exists()
    data = json.loads(contract_path.read_text(encoding="utf-8"))
    assert "phases" in data
    assert "runtime_policy" in data
    assert "2" in data["phases"]
    assert "8" in data["phases"]


def test_scaffold_approach1_no_pipeline_contract(
    tmp_path: Path, _mock_git: None
) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a1"
    _scaffold(1, output)

    assert not (output / "pipeline_contract.json").exists()


def test_scaffold_all_approaches(tmp_path: Path, _mock_git: None) -> None:
    from sdlc_core.scaffold import _scaffold

    for approach in (1, 2):
        out = tmp_path / f"approach{approach}"
        _scaffold(approach, out)
        assert out.is_dir()


def test_scaffold_core_version_written(tmp_path: Path, _mock_git: None) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a2"
    _scaffold(2, output)

    content = (output / "core_version.txt").read_text(encoding="utf-8")
    assert "deadbeef" in content


def test_scaffold_existing_output_exits(
    tmp_path: Path, _mock_git: None, capsys: pytest.CaptureFixture[str]
) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a1"
    output.mkdir()  # already exists

    with pytest.raises(SystemExit):
        _scaffold(1, output)


def test_scaffold_logs_dir_created(tmp_path: Path, _mock_git: None) -> None:
    from sdlc_core.scaffold import _scaffold

    output = tmp_path / "a2"
    _scaffold(2, output)

    assert (output / "logs" / ".gitkeep").exists()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_creates_scaffold(tmp_path: Path, _mock_git: None) -> None:
    from unittest.mock import patch

    output = tmp_path / "new_repo"
    test_args = ["sdlc-scaffold", "--approach", "A2", "--output", str(output)]

    with patch("sys.argv", test_args):
        from sdlc_core.scaffold import main

        main()

    assert output.is_dir()
    assert (output / "README.md").exists()


def test_main_accepts_numeric_approach(tmp_path: Path, _mock_git: None) -> None:
    output = tmp_path / "repo"
    test_args = ["sdlc-scaffold", "--approach", "2", "--output", str(output)]

    with patch("sys.argv", test_args):
        from sdlc_core.scaffold import main

        main()

    assert output.is_dir()


def test_main_rejects_invalid_approach(tmp_path: Path) -> None:
    test_args = [
        "sdlc-scaffold",
        "--approach", "A9",
        "--output", str(tmp_path / "X"),
    ]
    with patch("sys.argv", test_args):
        from sdlc_core.scaffold import main

        with pytest.raises(SystemExit):
            main()
