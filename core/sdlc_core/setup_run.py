"""setup_run.py: ``sdlc-setup`` entry point.

Initialises a new experiment run in a template repository:

1. Validates ``run_config.toml``: all required fields must be present.
2. Validates ``models.toml``: every model named in ``run_config.toml``
   has an entry, and its API key env var is set (if declared).
3. Writes ``core_version.txt`` with the pinned SHA of sdlc-core.
4. Calls ``setup_db()`` to create ``experiment.db``.
5. Calls ``open_run()`` to insert the run record.
6. Prints a confirmation table.

This command is run once per approach × project run, before Phase 2 starts.
It is idempotent: calling it a second time with the same run_config.toml
will reuse the existing run record if the run ID is already present.
"""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from sdlc_core.db import open_run, setup_db

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REQUIRED_RUN_FIELDS: tuple[str, ...] = ("project", "approach")
_PHASES: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8)


def _load_toml(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        _die(
            f"{label} not found at {path.resolve()}.\n"
            f"Copy {label.replace('.toml', '.example.toml')} and fill it in."
        )
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _die(message: str) -> None:
    print(f"[sdlc-setup] ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def _warn(message: str) -> None:
    print(f"[sdlc-setup] WARNING: {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_run_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """Return the ``[run]`` section after checking all required fields."""
    run_section: dict[str, Any] = cfg.get("run", {})
    missing = [f for f in _REQUIRED_RUN_FIELDS if not run_section.get(f, "")]
    if missing:
        _die(
            f"run_config.toml is missing required fields: {', '.join(missing)}\n"
            "Fill them in before running sdlc-setup."
        )
    approach = run_section["approach"]
    if approach not in ("A1", "A2", 1, 2):
        _die(f"run_config.toml: approach must be A1/A2, got {approach!r}.")
    return run_section


def _validate_models(run_cfg: dict[str, Any], models_data: dict[str, Any]) -> dict[int, str]:
    """Check every phase model is declared in models.toml and its key is set.

    Returns a mapping of phase_number -> model_name.
    """
    phases_section: dict[str, Any] = run_cfg.get("phases", {})
    models_section: dict[str, Any] = models_data.get("models", {})
    phase_map: dict[int, str] = {}
    errors: list[str] = []

    for phase in _PHASES:
        key = f"phase{phase}"
        model_name: str = phases_section.get(key, "").strip()
        if not model_name:
            _warn(f"No model assigned for phase {phase} (key '{key}' is empty).")
            continue

        if model_name not in models_section:
            errors.append(
                f"  - Phase {phase}: model {model_name!r} not found in models.toml."
            )
            continue

        entry: dict[str, Any] = models_section[model_name]
        api_key_env: str = entry.get("api_key_env", "")
        if api_key_env and not os.environ.get(api_key_env):
            errors.append(
                f"  - Phase {phase}: env var {api_key_env!r} "
                f"(required by model {model_name!r}) is not set."
            )
        phase_map[phase] = model_name

    if errors:
        _die(
            "Validation failed. Fix the following before running sdlc-setup:\n"
            + "\n".join(errors)
        )

    return phase_map


# ---------------------------------------------------------------------------
# core_version.txt
# ---------------------------------------------------------------------------

def _write_core_version() -> str:
    """Write core_version.txt and return the SHA string."""
    sha = _resolve_sha()
    Path("core_version.txt").write_text(sha + "\n", encoding="utf-8")
    return sha


def _resolve_sha() -> str:
    """Try to read the pinned SHA from pyproject.toml, fall back to git HEAD."""
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        with pyproject.open("rb") as fh:
            data = tomllib.load(fh)
        deps: dict[str, Any] = (
            data.get("tool", {})
            .get("poetry", {})
            .get("dependencies", {})
        )
        sdlc_dep = deps.get("sdlc-core", "")
        # Extract SHA from strings like:
        # {git = "https://github.com/.../ai-augmented-sdlc-hitl-core.git", rev = "abc123"}
        if isinstance(sdlc_dep, dict):
            rev = sdlc_dep.get("rev", "")
            if rev:
                return str(rev)

    # Fall back to git HEAD of the current repo
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the ``sdlc-setup`` command."""
    run_cfg_path = Path("run_config.toml")
    models_path_env = os.environ.get("SDLC_MODELS_TOML")
    models_path = Path(models_path_env) if models_path_env else Path("models.toml")

    run_data = _load_toml(run_cfg_path, "run_config.toml")
    models_data = _load_toml(models_path, "models.toml")

    run_section = _validate_run_config(run_data)
    phase_map = _validate_models(run_data, models_data)

    sha = _write_core_version()

    project: str = run_section["project"]
    approach_raw = run_section["approach"]
    # Accept "A1" or 1
    approach: int = (
        int(str(approach_raw).lstrip("A"))
        if isinstance(approach_raw, str)
        else int(approach_raw)
    )

    db_path = setup_db()
    run_id = open_run(project=project, approach=approach)

    # Print confirmation
    width = 60
    print()
    print("=" * width)
    print("  sdlc-setup complete")
    print("=" * width)
    print(f"  Run ID    : {run_id}")
    print(f"  Project   : {project}")
    print(f"  Approach  : A{approach}")
    print(f"  Core SHA  : {sha[:12]}...")
    print(f"  DB        : {db_path}")
    print()
    print("  Phase assignments:")
    for phase in _PHASES:
        model = phase_map.get(phase, "(unassigned)")
        print(f"    Phase {phase}: {model}")
    print("=" * width)
    print("  Ready to start Phase 2.")
    print("=" * width)
    print()


if __name__ == "__main__":
    main()
