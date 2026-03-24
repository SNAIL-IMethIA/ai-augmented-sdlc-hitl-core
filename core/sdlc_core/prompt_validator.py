"""prompt_validator.py: Validate that a prompt conforms to the structured template.

The interaction protocol (protocol/interactions.md) mandates all prompts in
both approaches follow a five-section template with locked variables resolved
before execution.  This module checks structural compliance before a prompt
is submitted to any provider.

A validation failure writes a ``PROMPT_STRUCTURE_VIOLATION`` row to the
``violations`` table and prints a warning.  The prompt is not blocked; the
researcher decides whether to proceed.

Sections required (case-insensitive matching, ``##`` heading level)
-------------------------------------------------------------------
- ``PERSONA``
- ``TASK``
- ``INPUT ARTIFACTS``
- ``OUTPUT TEMPLATE``  (or ``OUTPUT``)
- ``ACCEPTANCE CRITERIA``  (or ``ACCEPTANCE``)
- ``CHAIN-OF-THOUGHT``  (or ``CHAIN OF THOUGHT`` or ``CHAIN``)

Usage
-----
    from sdlc_core.prompt_validator import validate_prompt, PromptValidationResult
    from sdlc_core.session import Session

    session = Session(run_id="run-001", approach=1, active_phase=3)
    result = validate_prompt(prompt_text, session=session, artifact_id="REQ-01")
    if not result.passed:
        print(result.missing_sections)  # decide whether to proceed

"""

from __future__ import annotations

import re
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Required sections
# ---------------------------------------------------------------------------

# Each entry: (canonical_name, list_of_regex_fragments)
# A section is found when at least one fragment matches a ## heading in the prompt
_REQUIRED_SECTIONS: list[tuple[str, list[str]]] = [
    ("PERSONA",            ["persona"]),
    ("TASK",               ["task"]),
    ("INPUT ARTIFACTS",    ["input artifacts", "input artifact", "inputs"]),
    ("OUTPUT TEMPLATE",    ["output template", "output"]),
    ("ACCEPTANCE CRITERIA",["acceptance criteria", "acceptance"]),
    ("CHAIN-OF-THOUGHT",   ["chain.of.thought", "chain of thought", "chain"]),
]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class PromptValidationResult:
    """Result of a structural prompt validation.

    Attributes:
        passed:           ``True`` when all required sections are present.
        missing_sections: List of canonical section names that were not found.
        found_sections:   List of canonical section names that were found.

    """

    passed: bool
    missing_sections: list[str] = field(default_factory=list)
    found_sections: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a concise human-readable validation summary."""
        if self.passed:
            return "PromptValidationResult: passed"
        return (
            f"PromptValidationResult: FAILED - missing sections: "
            f"{', '.join(self.missing_sections)}"
        )


# ---------------------------------------------------------------------------
# Core validation logic
# ---------------------------------------------------------------------------

def _extract_headings(prompt: str) -> list[str]:
    """Return the text of all ``##`` headings in *prompt*, lowercased."""
    return [
        m.group(1).strip().lower()
        for m in re.finditer(r"^#{1,3}\s+(.+)$", prompt, re.MULTILINE)
    ]


def check_prompt_structure(prompt: str) -> PromptValidationResult:
    """Check *prompt* for the required structural sections.

    This is a pure function with no side effects.

    Args:
        prompt: The full prompt text to validate.

    Returns:
        A :class:`PromptValidationResult` describing which sections were
        found and which are missing.

    """
    headings = _extract_headings(prompt)

    found: list[str] = []
    missing: list[str] = []

    for canonical, fragments in _REQUIRED_SECTIONS:
        found_this = any(
            any(re.search(frag, h) for h in headings)
            for frag in fragments
        )
        if found_this:
            found.append(canonical)
        else:
            missing.append(canonical)

    return PromptValidationResult(
        passed=len(missing) == 0,
        missing_sections=missing,
        found_sections=found,
    )


def validate_prompt(
    prompt: str,
    *,
    session: object | None = None,
    artifact_id: str | None = None,
    db_path: Path | None = None,
    strict: bool = False,
) -> PromptValidationResult:
    """Validate *prompt* structure and optionally write a violation on failure.

    Args:
        prompt:      Full prompt text to validate.
        session:     Active :class:`~sdlc_core.session.Session`.  When
                     provided and validation fails, a
                     ``PROMPT_STRUCTURE_VIOLATION`` row is written to the
                     ``violations`` table.
        artifact_id: Optional artifact identifier linked to the prompt.
        db_path:     Path to ``experiment.db``.  Ignored when *session* is
                     ``None``.
        strict:      When ``True``, raise :class:`ValueError` if validation
                     fails instead of returning a result object.

    Returns:
        A :class:`PromptValidationResult` with pass/fail details.

    Raises:
        ValueError: When *strict* is ``True`` and validation fails.

    """
    result = check_prompt_structure(prompt)

    if not result.passed:
        msg = (
            f"Prompt is missing required sections: "
            f"{', '.join(result.missing_sections)}. "
            "All prompts must conform to the five-section template "
            "(protocol/interactions.md)."
        )
        warnings.warn(msg, stacklevel=2)
        print(f"\n[prompt-validator] WARNING: {msg}", file=sys.stderr)

        if session is not None:
            try:
                from sdlc_core import db
                from sdlc_core.enums import ViolationType

                run_id: str = getattr(session, "run_id", "")
                _db_path: Path | None = db_path or getattr(session, "db_path", None)

                db.log_violation(
                    run_id=run_id,
                    violation_type=ViolationType.PROMPT_STRUCTURE_VIOLATION,
                    detail=msg,
                    artifact_id=artifact_id,
                    db_path=_db_path,
                )
            except Exception:
                pass  # never block a run due to validator failure

        if strict:
            raise ValueError(msg)

    return result
