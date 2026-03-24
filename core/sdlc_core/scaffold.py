"""scaffold.py: ``sdlc-scaffold`` entry point.

Generates a ready-to-use template repository for a given approach.

Usage
-----
    poetry run sdlc-scaffold --approach A1 --output ./path/to/new-repo

What it creates
---------------
    <output>/
        .github/
            copilot-instructions.md
            workflows/ci.yml
        artifacts/
            phase2/.gitkeep  ...  phase8/.gitkeep
        logs/
            .gitkeep
        prompts/
            phase2.md  ...  phase8.md   (approach-specific stubs)
        scripts/
            bootstrap.py
            hitl_runner.py      (Approach 1)
            pipeline_runner.py  (Approach 2)
        .env.example
        .gitignore
        core_version.txt
        models.example.toml
        tooling.example.toml
        pyproject.toml
        README.md
        run_config.example.toml

The output directory must not already exist (to avoid clobbering).

Pinning and dependency source
-----------------------------
By default, generated templates depend on ``sdlc-core`` via a pinned Git
revision (portable across machines). You can also generate a template that
uses a local path dependency for rapid iteration on the same machine.

Run ``sdlc-scaffold`` only when the core repo is in the state you want to
freeze for the experiment.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _die(message: str) -> None:
    print(f"[sdlc-scaffold] ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def _get_core_sha() -> str:
    """Return the current HEAD SHA of this repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "REPLACE_WITH_CORE_SHA"


def _get_core_repo_url() -> str:
    """Return the remote origin URL of this repository."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        # Normalise SSH URL to HTTPS for pip-style git deps
        if url.startswith("git@github.com:"):
            url = "https://github.com/" + url[len("git@github.com:"):]
        if url.endswith(".git"):
            url = url[:-4]
        return url
    except Exception:
        return "https://github.com/OWNER/ai-augmented-sdlc-hitl-core"


def _license_text() -> str:
    """Return the repository LICENSE content when available."""
    license_path = Path(__file__).resolve().parents[2] / "LICENSE"
    if license_path.exists():
        return license_path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Per-approach content
# ---------------------------------------------------------------------------

_APPROACH_DESCRIPTIONS = {
    1: "Human orchestrator: structured prompts with role-specialized agents and HITL acceptance.",
    2: "Autonomous pipeline: machine-readable I/O contract drives agent handoffs and gates.",
}

_PHASE_NAMES = {
    2: "Stakeholder Requirements Definition",
    3: "System Requirements Analysis",
    4: "Architecture Design",
    5: "Detailed Design",
    6: "Implementation",
    7: "Verification",
    8: "Validation",
}


def _prompt_stub(approach: int, phase: int) -> str:
    """Return the prompt stub content for a given approach and phase."""
    phase_name = _PHASE_NAMES[phase]

    if approach == 1:
        return f"""\
# Phase {phase} - {phase_name}

## Persona

You are a **[role name]** working on the {phase_name} phase.

## Inputs

The following accepted artifacts are available:

- [artifact ID(s) from previous phase(s)]
- [requirements/design constraints]

## Task

[Describe one atomic obligation for this prompt.]

## Output template

Use the canonical template from the protocol for this artifact type.

## Acceptance criteria

1. [Criterion 1]
2. [Criterion 2]

## Chain-of-thought instruction

Before final output, reason step by step through constraints, alternatives,
and tradeoffs, then produce the artifact.
"""

    if approach == 2:
        return f"""\
# Phase {phase} - {phase_name}

This phase is driven by ``pipeline_contract.json`` and your template repo's
orchestration runtime. Keep prompts, handoffs, and escalation behavior aligned
with ``tooling.toml`` and your runtime policy.

Expected runtime behavior for this phase:

- Agent-to-agent handoffs are explicit and structured.
- Ambiguity triggers clarification loops or escalation.
- Context transfer between agents is structured and lossless.
- HITL checkpoints remain available for approval and override.

Template repositories should provide concrete execution commands. Example:

    poetry run python -m scripts.pipeline_runner --phase {phase}
"""

    raise ValueError(f"Unsupported approach {approach}; expected 1 or 2")


# ---------------------------------------------------------------------------
# File generators
# ---------------------------------------------------------------------------

def _gitignore() -> str:
    return """\
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
dist/
build/

# Environment and secrets
# Never commit these
.env
models.toml

# Editor
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db
"""


def _env_example() -> str:
    return """\
# Copy this file to .env and fill in your API keys
# .env is gitignored and must never contain committed real keys
#
# Only set variables for providers you actually use
# Leave others blank or remove them

# Anthropic Claude
ANTHROPIC_API_KEY=

# OpenAI
OPENAI_API_KEY=

# Google Gemini
GOOGLE_API_KEY=

# LangSmith (optional: tracing and observability for LangChain / LangGraph runs)
# Create a free account at https://smith.langchain.com to get a key
# Set LANGCHAIN_TRACING_V2=false to disable entirely
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=sdlc-hitl-experiment

# Custom / other
# MY_CUSTOM_KEY=
"""


def _models_example_toml() -> str:
    return """\
# models.example.toml
# -------------------------------------------------------------------------------
# Copy this file to models.toml and fill in models you can access
# models.toml is gitignored and local to your machine
#
# Each [[models.<name>]] entry defines one model you can assign to a phase
# Use the name in run_config.toml, for example phase2 = "llama3-local"
#
# provider    -> built-in key ("ollama" or "manual") or a registered custom key
# model_id    -> the model identifier string the API expects
# api_key_env -> name of the environment variable holding the API key
#               Leave empty for local models that need no key
# api_base    -> override the API endpoint (for non-default Ollama ports, vLLM, etc)
#               Leave empty to use the provider default
# -------------------------------------------------------------------------------

# -- Ollama via LangChain (recommended: integrates with LangGraph natively) ---

[models.llama3-local]
provider    = "ollama-lc"
model_id    = "llama3"
api_key_env = ""
# defaults to http://localhost:11434
api_base    = ""

[models.codellama-local]
provider    = "ollama-lc"
model_id    = "codellama:13b"
api_key_env = ""
api_base    = ""

[models.mistral-local]
provider    = "ollama-lc"
model_id    = "mistral"
api_key_env = ""
api_base    = ""

# -- Ollama direct (raw Python client, no LangChain: simpler but no LangGraph) --
# Uncomment if you want to bypass LangChain for a phase:
# [models.llama3-raw]
# provider    = "ollama"
# model_id    = "llama3"
# api_key_env = ""
# api_base    = ""

# -- Manual / HITL (for any phase done by hand) ---------------------------------

[models.manual]
provider    = "manual"
model_id    = ""
api_key_env = ""
api_base    = ""

# -- Commercial providers (require registering the example extension first) -----
# See sdlc_core/providers/examples/ for the provider class and registration
# instructions

# [models.claude-sonnet]
# provider    = "anthropic"
# model_id    = "claude-sonnet-4-5"
# api_key_env = "ANTHROPIC_API_KEY"
# api_base    = ""

# [models.gpt-4o]
# provider    = "openai"
# model_id    = "gpt-4o"
# api_key_env = "OPENAI_API_KEY"
# api_base    = ""

# [models.gemini-flash]
# provider    = "gemini"
# model_id    = "gemini-2.0-flash"
# api_key_env = "GOOGLE_API_KEY"
# api_base    = ""
"""


def _run_config_example_toml(approach: int) -> str:
    example_model = "llama3-local"
    return f"""\
# run_config.toml
# -------------------------------------------------------------------------------
# Fill in this file before running poetry run sdlc-setup
# This file IS committed and is part of the experiment record
# -------------------------------------------------------------------------------

[run]
project    = ""          # e.g. "project1"
approach   = "A{approach}"

[phases]
# Assign a model name from models.toml to each phase
# Use "manual" for any phase you run by hand (Approach 1 uses this for all)

phase2 = "{example_model}"   # {_PHASE_NAMES[2]}
phase3 = "{example_model}"   # {_PHASE_NAMES[3]}
phase4 = "{example_model}"   # {_PHASE_NAMES[4]}
phase5 = "{example_model}"   # {_PHASE_NAMES[5]}
phase6 = "{example_model}"   # {_PHASE_NAMES[6]}
phase7 = "{example_model}"   # {_PHASE_NAMES[7]}
phase8 = "{example_model}"   # {_PHASE_NAMES[8]}
"""


def _tooling_example_toml() -> str:
    return """\
# tooling.example.toml
# -------------------------------------------------------------------------------
# Copy this file to tooling.toml
# This repository uses a fixed orchestration stack for reproducibility
# -------------------------------------------------------------------------------

[stack]
framework = "langchain"
runtime = "langgraph"
local_model_interface = "langchain-ollama"
harness = "autogen"
tracing = "langsmith"

[capabilities]
agent_handoffs = true
clarification_loops = true
ambiguity_escalation = true
structured_context_transfer = true
hitl_checkpoints = true
durable_state = true
streaming = true

# Disable LangSmith tracing by setting this to false in .env if you do not
# have an account.  LangSmith can also run fully locally.
# LANGCHAIN_TRACING_V2=false
"""


def _pyproject_toml(
    approach: int,
    sha: str,
    core_url: str,
    *,
    core_source: str = "git",
    local_core_path: Path | None = None,
) -> str:
    stack_deps = (
        '\nlangchain = "==0.3.20"'
        '\nlangchain-core = "==0.3.45"'
        '\nlangchain-community = "==0.3.19"'
        '\nlangchain-ollama = "==0.2.3"'
        '\nlanggraph = "==0.2.74"'
        '\nlangsmith = "==0.2.19"'
    )
    if approach == 2:
        stack_deps += (
            '\nautogen-agentchat = "==0.4.9"'
            '\nautogen-ext = "==0.4.9"'
        )

    script_block = (
        "\n[tool.poetry.scripts]\n"
        "sdlc-bootstrap = \"scripts.bootstrap:main\"\n"
        "sdlc-hitl-run = \"scripts.hitl_runner:main\"\n"
        if approach == 1
        else "\n[tool.poetry.scripts]\n"
             "sdlc-bootstrap = \"scripts.bootstrap:main\"\n"
             "sdlc-pipeline = \"scripts.pipeline_runner:main\"\n"
    )

    if core_source == "git":
        core_dep = f'sdlc-core = {{git = "{core_url}.git", rev = "{sha}", subdirectory = "core"}}'
    elif core_source == "local":
        if local_core_path is None:
            local_core_path = Path(__file__).resolve().parents[2] / "core"
        core_dep = f'sdlc-core = {{path = "{local_core_path.resolve().as_posix()}", develop = true}}'
    else:
        raise ValueError(f"Unsupported core_source {core_source!r}; expected 'git' or 'local'.")

    return f"""\
[tool.poetry]
name = "sdlc-hitl-a{approach}"
version = "0.1.0"
description = "AI-Augmented SDLC, Approach {approach}: {_APPROACH_DESCRIPTIONS[approach]}"
authors = []
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
{core_dep}{stack_deps}
{script_block}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""


def _readme(
    approach: int,
    sha: str,
    repo_name: str,
    *,
    core_source: str = "git",
    local_core_path: Path | None = None,
) -> str:
    approach_desc = _APPROACH_DESCRIPTIONS[approach]
    repo_slug = repo_name.strip() or f"template-approach{approach}"
    approach_title = (
        "Human Orchestrator" if approach == 1 else "Autonomous Pipeline"
    )
    run_phase_snippet = (
        "poetry run sdlc-hitl-run --phase 2 --agent-role requirements_analyst --artifact-id REQ-01"
        if approach == 1
        else "poetry run sdlc-pipeline --phase 2"
    )
    if core_source == "git":
        core_mode_text = (
            "**Git (portable, recommended)**. This template installs `sdlc-core` "
            "from a pinned commit and works on any machine without sibling repo layout assumptions."
        )
    else:
        if local_core_path is None:
            local_core_path = Path(__file__).resolve().parents[2] / "core"
        core_mode_text = (
            "**Local path (machine-specific)**. This template points `sdlc-core` to "
            f"`{local_core_path.resolve().as_posix()}` for rapid local iteration."
        )

    return f"""\
# {repo_slug}

Approach {approach} ({approach_title}) for the AI-Augmented SDLC Human-in-the-Loop experiment.

{approach_desc}

This repository is a template for running one approach of the
AI-Augmented SDLC Human-in-the-Loop experiment.

---

## Quick start

```bash
git clone <this-repo>
cd <this-repo>
poetry install
poetry run sdlc-bootstrap --project <project_id>
```

## Core Dependency Mode

{core_mode_text}

`sdlc-bootstrap` prepares local config files (`models.toml`, `tooling.toml`,
`run_config.toml`) and initializes the run database.

After bootstrap completes, begin Phase 2 using the prompt stubs in
`prompts/`.

The orchestration stack is fixed for reproducibility:

- Framework: LangChain
- Runtime: LangGraph
- Harness: AutoGen (Approach 2)
- Local model interface: langchain-ollama (ChatOllama)
- Tracing: LangSmith (optional, disable via ``LANGCHAIN_TRACING_V2=false``)

Model and provider choice remains flexible via `models.toml`.  The default
is Ollama (no API key, any open-source model).  Register any other provider
using the ``@register_provider`` decorator. See
``sdlc_core/providers/examples/`` for ready-to-use extensions.

Run your first phase command:

```bash
{run_phase_snippet}
```

---

## Switching a model mid-run

```bash
poetry run sdlc-assign-model --run-id <run_id> --phase 6 --model codellama-local
```

---

## Core library version

Pinned to commit `{sha[:12]}` of
[ai-augmented-sdlc-hitl-core](https://github.com/SNAIL-IMethIA/ai-augmented-sdlc-hitl-core).

See `core_version.txt` for the full SHA.  This must not change once a run
has started.

---

## Repository structure

```
artifacts/phase2..8/   <- accepted SDLC artifacts, one folder per phase
logs/                  <- experiment.db lives here (generated by sdlc-setup)
prompts/               <- prompt stubs for each phase
run_config.toml        <- committed run declaration (fill before sdlc-setup)
models.toml            <- local model registry (gitignored)
.env                   <- API keys (gitignored)
core_version.txt       <- SHA of sdlc-core dependency (written by sdlc-setup)
```
"""


def _copilot_instructions(approach: int) -> str:
    return f"""\
# GitHub Copilot Instructions: Approach {approach}

This workspace is a single approach repository for the
**AI-Augmented SDLC Human-in-the-Loop** research experiment.

## What this repo is

An execution environment for Approach {approach} ({_APPROACH_DESCRIPTIONS[approach]}).

Each phase (2 through 8) follows the IEEE 12207-aligned protocol defined in
the core repository.  Prompt stubs live in `prompts/`.  Accepted artifacts go
in `artifacts/phase<N>/`.  All interactions are logged to `logs/experiment.db`.

## Key commands

| Command | Purpose |
|---|---|
| `poetry run sdlc-setup` | Initialise DB and open run record (run once) |
| `poetry run sdlc-assign-model` | Reassign a model for a phase mid-run |

## Files not to modify during a run

- `core_version.txt`: SHA-locked, never hand-edit
- `pyproject.toml`: dependency versions are frozen for the run

## Protocol reference

See the core repository:
https://github.com/SNAIL-IMethIA/ai-augmented-sdlc-hitl-core
"""


def _ci_workflow() -> str:
    return """\
name: CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run integrity check
        run: |
          if [ -f logs/experiment.db ]; then
            poetry run python -m sdlc_core.check logs/experiment.db
          else
            echo "No experiment.db found. Skipping check."
          fi
"""


def _scripts_init() -> str:
    return """\
\"\"\"Template approach runners.\"\"\"
"""


def _bootstrap_py(approach: int) -> str:
    default_model = "manual" if approach == 1 else "llama3-local"
    return f"""\
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _copy_if_missing(src: Path, dst: Path) -> None:
    if not dst.exists() and src.exists():
        shutil.copyfile(src, dst)


def _write_run_config(project: str, model: str) -> None:
    content = (
        "# run_config.toml\n"
        "[run]\n"
        'project    = "' + project + '"\n'
        f'approach   = "A{approach}"\n'
        "\n"
        "[phases]\n"
        'phase2 = "' + model + '"\n'
        'phase3 = "' + model + '"\n'
        'phase4 = "' + model + '"\n'
        'phase5 = "' + model + '"\n'
        'phase6 = "' + model + '"\n'
        'phase7 = "' + model + '"\n'
        'phase8 = "' + model + '"\n'
    )
    Path("run_config.toml").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap this template for immediate run start")
    parser.add_argument("--project", required=True, help="Project identifier (e.g. project1)")
    parser.add_argument(
        "--model",
        default="{default_model}",
        help="Model key from models.toml assigned to phases 2..8",
    )
    parser.add_argument(
        "--overwrite-run-config",
        action="store_true",
        help="Overwrite existing run_config.toml",
    )
    args = parser.parse_args()

    _copy_if_missing(Path("models.example.toml"), Path("models.toml"))
    _copy_if_missing(Path("tooling.example.toml"), Path("tooling.toml"))
    _copy_if_missing(Path(".env.example"), Path(".env"))

    run_cfg = Path("run_config.toml")
    if (not run_cfg.exists()) or args.overwrite_run_config:
        _write_run_config(args.project, args.model)

    from sdlc_core.setup_run import main as setup_main

    setup_main()


if __name__ == "__main__":
    main()
"""


def _hitl_runner_py() -> str:
    return """\
from __future__ import annotations

import argparse
import sqlite3
import tomllib
from pathlib import Path

from sdlc_core.providers import LoggedProvider
from sdlc_core.providers.registry import get_provider
from sdlc_core.session import Session


def _resolve_run_id(db_path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT id FROM runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise ValueError("No run found in logs/experiment.db. Run sdlc-setup first.")
    return str(row[0])


def _model_for_phase(phase: int) -> str:
    data = tomllib.loads(Path("run_config.toml").read_text(encoding="utf-8"))
    model = str(data.get("phases", {}).get(f"phase{phase}", "")).strip()
    if not model:
        raise ValueError(f"No model assigned for phase {phase} in run_config.toml")
    return model


def _load_prompt(phase: int, prompt_file: str | None) -> str:
    path = Path(prompt_file) if prompt_file else Path("prompts") / f"phase{phase}.md"
    if not path.exists():
        raise ValueError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one HITL phase interaction.")
    parser.add_argument("--phase", type=int, required=True, choices=range(2, 9))
    parser.add_argument("--agent-role", required=True)
    parser.add_argument("--artifact-id", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--prompt-file", default=None)
    args = parser.parse_args()

    db_path = Path("logs") / "experiment.db"
    run_id = _resolve_run_id(db_path, args.run_id)
    model_name = args.model or _model_for_phase(args.phase)
    prompt = _load_prompt(args.phase, args.prompt_file)

    session = Session(run_id=run_id, approach=1, active_phase=args.phase, db_path=db_path)
    provider = LoggedProvider(get_provider(model_name), session=session)
    provider.complete(prompt, agent_role=args.agent_role, artifact_id=args.artifact_id)


if __name__ == "__main__":
    main()
"""


def _pipeline_runner_py() -> str:
    return """\
from __future__ import annotations

import argparse
import json
import sqlite3
import tomllib
from pathlib import Path

from sdlc_core.db import log_pipeline_event
from sdlc_core.enums import PipelineEventType
from sdlc_core.providers import LoggedProvider
from sdlc_core.providers.registry import get_provider
from sdlc_core.session import Session


def _resolve_run_id(db_path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT id FROM runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise ValueError("No run found in logs/experiment.db. Run sdlc-setup first.")
    return str(row[0])


def _model_for_phase(phase: int) -> str:
    data = tomllib.loads(Path("run_config.toml").read_text(encoding="utf-8"))
    model = str(data.get("phases", {}).get(f"phase{phase}", "")).strip()
    if not model:
        raise ValueError(f"No model assigned for phase {phase} in run_config.toml")
    return model


def _load_phase_prompt(phase: int) -> str:
    contract_path = Path("pipeline_contract.json")
    if contract_path.exists():
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        phase_cfg = contract.get("phases", {}).get(str(phase), {})
        prompt = str(phase_cfg.get("prompt", "")).strip()
        if prompt:
            return prompt
    prompt_path = Path("prompts") / f"phase{phase}.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    raise ValueError(f"No prompt available for phase {phase}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one autonomous pipeline phase.")
    parser.add_argument("--phase", type=int, required=True, choices=range(2, 9))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--artifact-id", default=None)
    parser.add_argument("--agent-role", default="pipeline_orchestrator")
    args = parser.parse_args()

    db_path = Path("logs") / "experiment.db"
    run_id = _resolve_run_id(db_path, args.run_id)
    model_name = _model_for_phase(args.phase)
    prompt = _load_phase_prompt(args.phase)
    pipeline_id = f"PIPE-{run_id}"

    log_pipeline_event(
        run_id=run_id,
        pipeline_id=pipeline_id,
        step=f"phase{args.phase}",
        agent_role=args.agent_role,
        event_type=PipelineEventType.RESUME,
        detail="Phase execution started",
        artifact_id=args.artifact_id,
        db_path=db_path,
    )

    session = Session(run_id=run_id, approach=2, active_phase=args.phase, db_path=db_path)
    provider = LoggedProvider(get_provider(model_name), session=session)
    provider.complete(prompt, agent_role=args.agent_role, artifact_id=args.artifact_id)

    log_pipeline_event(
        run_id=run_id,
        pipeline_id=pipeline_id,
        step=f"phase{args.phase}",
        agent_role=args.agent_role,
        event_type=PipelineEventType.GATE_PASS,
        detail="Phase execution completed",
        artifact_id=args.artifact_id,
        db_path=db_path,
    )


if __name__ == "__main__":
    main()
"""


# ---------------------------------------------------------------------------
# Main scaffold logic
# ---------------------------------------------------------------------------

def _scaffold(
    approach: int,
    output: Path,
    *,
    core_source: str = "git",
    local_core_path: Path | None = None,
) -> None:
    if output.exists():
        _die(f"Output directory {output} already exists.  Choose a different path.")

    # Fail fast with a clear message when users pass placeholder paths like
    # "/path/..." or any location they cannot create.
    parent = output.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        _die(
            f"Cannot create output directory under {parent.resolve()}.\n"
            "Choose a writable path (for example: ./project2-approach1-human-orchestrator)."
        )
    except FileNotFoundError:
        _die(
            f"Parent path does not exist: {parent}.\n"
            "Use a real path on your machine instead of a placeholder like '/path/...'."
        )

    sha = _get_core_sha()
    core_url = _get_core_repo_url()

    # Static files shared across all approaches
    _write(output / ".gitignore", _gitignore())
    _write(output / ".env.example", _env_example())
    _write(output / "models.example.toml", _models_example_toml())
    _write(output / "tooling.example.toml", _tooling_example_toml())
    _write(output / "run_config.example.toml", _run_config_example_toml(approach))
    _write(
        output / "pyproject.toml",
        _pyproject_toml(
            approach,
            sha,
            core_url,
            core_source=core_source,
            local_core_path=local_core_path,
        ),
    )
    _write(
        output / "README.md",
        _readme(
            approach,
            sha,
            output.name,
            core_source=core_source,
            local_core_path=local_core_path,
        ),
    )
    _write(output / "core_version.txt", sha + "\n")
    license_text = _license_text()
    if license_text:
        _write(output / "LICENSE", license_text)
    _write(output / ".github" / "copilot-instructions.md", _copilot_instructions(approach))
    _write(output / ".github" / "workflows" / "ci.yml", _ci_workflow())
    _write(output / "scripts" / "__init__.py", _scripts_init())
    _write(output / "scripts" / "bootstrap.py", _bootstrap_py(approach))

    # Artifact phase directories
    for phase in range(2, 9):
        _touch(output / "artifacts" / f"phase{phase}" / ".gitkeep")

    # Logs directory
    _touch(output / "logs" / ".gitkeep")

    # Prompt stubs
    for phase in range(2, 9):
        _write(output / "prompts" / f"phase{phase}.md", _prompt_stub(approach, phase))

    if approach == 1:
        _write(output / "scripts" / "hitl_runner.py", _hitl_runner_py())

    # Approach 2 also gets a pipeline contract stub
    if approach == 2:
        _write(output / "scripts" / "pipeline_runner.py", _pipeline_runner_py())
        import json
        contract: dict[str, Any] = {
            "_comment": "Machine-readable phase I/O contract for Approach 2.",
            "runtime_policy": {
                "agent_handoffs": "explicit",
                "clarification_loops": "enabled",
                "ambiguity_escalation": "enabled",
                "structured_context_transfer": "required",
                "hitl_checkpoints": "enabled",
            },
            "phases": {
                str(phase): {
                    "name": _PHASE_NAMES[phase],
                    "inputs": [],
                    "outputs": [],
                    "acceptance_criteria": [],
                }
                for phase in range(2, 9)
            },
        }
        _write(
            output / "pipeline_contract.json",
            json.dumps(contract, indent=2) + "\n",
        )

    print(f"\n[sdlc-scaffold] Approach A{approach} template created at {output.resolve()}")
    print("\nNext steps:")
    print(f"  cd {output}")
    print("  git init && git add . && git commit -m 'Initial scaffold'")
    print("  cp models.example.toml models.toml   # then edit")
    print("  cp run_config.example.toml run_config.toml   # then edit")
    print("  cp .env.example .env   # then add API keys")
    print("  poetry install")
    print("  poetry run sdlc-setup")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the ``sdlc-scaffold`` command."""
    parser = argparse.ArgumentParser(
        prog="sdlc-scaffold",
        description="Scaffold a new approach template repository.",
    )
    parser.add_argument(
        "--approach",
        required=True,
        choices=["A1", "A2", "1", "2"],
        help="Approach identifier (A1 or A2).",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path where the new repository directory will be created.",
    )
    parser.add_argument(
        "--core-source",
        default="git",
        choices=["git", "local"],
        help=(
            "How templates depend on sdlc-core. "
            "'git' (default) is portable and pinned. "
            "'local' writes a local path dependency for fast same-machine iteration."
        ),
    )
    parser.add_argument(
        "--core-path",
        type=Path,
        default=None,
        help=(
            "Optional path to local core package used when --core-source local. "
            "Defaults to this repository's ./core path."
        ),
    )
    args = parser.parse_args()

    approach = int(str(args.approach).lstrip("A"))
    _scaffold(
        approach,
        args.output,
        core_source=args.core_source,
        local_core_path=args.core_path,
    )


if __name__ == "__main__":
    main()
