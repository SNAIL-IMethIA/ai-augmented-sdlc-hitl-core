"""assign_model.py: ``sdlc-assign-model`` entry point.

Updates the model assignment for a single SDLC phase within an active run.

Usage
-----
    poetry run sdlc-assign-model --run-id <run_id> --phase <2-8> --model <model_name>

The new model must exist in ``models.toml`` and its API key env var (if any)
must be set.  Both the original and new assignment are preserved in the DB
``interactions`` metadata. This command writes a note to ``violations`` with
category ``other`` so the change is fully traceable.

Switching a model mid-run does not restart the run. It simply records what
was actually used from that point forward.
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from sdlc_core.db import _connect

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _die(message: str) -> None:
    print(f"[sdlc-assign-model] ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def _load_models_toml() -> dict[str, Any]:
    env_path = os.environ.get("SDLC_MODELS_TOML")
    path = Path(env_path) if env_path else Path("models.toml")
    if not path.exists():
        _die(
            f"models.toml not found at {path.resolve()}.\n"
            "Copy models.example.toml to models.toml and fill in your models."
        )
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _validate_model(model_name: str, models_data: dict[str, Any]) -> None:
    models_section: dict[str, Any] = models_data.get("models", {})
    if model_name not in models_section:
        available = ", ".join(models_section.keys()) or "(none)"
        _die(
            f"Model {model_name!r} not found in models.toml.\n"
            f"Available models: {available}"
        )
    entry: dict[str, Any] = models_section[model_name]
    provider_name = str(entry.get("provider", "")).strip().lower()
    if model_name.lower() == "manual" or provider_name == "manual":
        _die(
            f"Model {model_name!r} uses provider 'manual', which is disallowed "
            "by protocol. Use a valid AI model provider."
        )
    api_key_env: str = entry.get("api_key_env", "")
    if api_key_env and not os.environ.get(api_key_env):
        _die(
            f"Env var {api_key_env!r} (required by model {model_name!r}) is not set.\n"
            "Set it in your .env file and re-run."
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the ``sdlc-assign-model`` command."""
    parser = argparse.ArgumentParser(
        prog="sdlc-assign-model",
        description="Update the model assignment for a phase within an active run.",
    )
    parser.add_argument("--run-id", required=True, help="Run ID (from sdlc-setup output).")
    parser.add_argument("--phase", required=True, type=int, choices=range(2, 9),
                        help="SDLC phase number (2-8).")
    parser.add_argument("--model", required=True, help="Model name as defined in models.toml.")
    args = parser.parse_args()

    models_data = _load_models_toml()
    _validate_model(args.model, models_data)

    # Record the reassignment as a violation row (type "other") for full traceability
    # The original model is visible in earlier interactions rows
    from datetime import UTC, datetime
    now = datetime.now(UTC).isoformat()
    detail = (
        f"Model reassignment: phase {args.phase} now uses {args.model!r}. "
        f"Reassigned at {now}."
    )

    with _connect() as conn:
        # Verify the run ID exists
        row = conn.execute("SELECT id FROM runs WHERE id = ?", (args.run_id,)).fetchone()
        if row is None:
            _die(f"Run ID {args.run_id!r} not found in experiment.db.")

        conn.execute(
            """
            INSERT INTO violations (run_id, violation_type, detail, timestamp)
            VALUES (?, 'other', ?, ?)
            """,
            (args.run_id, detail, now),
        )

    print(
        f"[sdlc-assign-model] Phase {args.phase} -> {args.model!r} "
        f"recorded for run {args.run_id!r}."
    )


if __name__ == "__main__":
    main()
