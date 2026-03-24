"""test_prompt_validator.py: Tests for sdlc_core.prompt_validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from sdlc_core.prompt_validator import (
    PromptValidationResult,
    check_prompt_structure,
    validate_prompt,
)

# ---------------------------------------------------------------------------
# Sample prompts
# ---------------------------------------------------------------------------

_FULL_PROMPT = """\
## PERSONA
You are a requirements analyst.

## TASK
Extract functional requirements from the stakeholder interview notes.

## INPUT ARTIFACTS
- INT-01: Interview transcript with the product owner.

## OUTPUT TEMPLATE
Use the REQ-NN template from protocol/requirements.md.

## ACCEPTANCE CRITERIA
1. Each requirement is atomic.
2. Each requirement uses mandatory language.

## CHAIN-OF-THOUGHT
Reason through each stakeholder concern before writing the requirement.
"""

_MISSING_PERSONA_PROMPT = """\
## TASK
Do something.

## INPUT ARTIFACTS
None.

## OUTPUT TEMPLATE
Some template.

## ACCEPTANCE CRITERIA
1. Criterion.

## CHAIN-OF-THOUGHT
Think first.
"""

_MINIMAL_VALID_PROMPT = """\
## Persona
Analyst.

## Task
Do X.

## Inputs
None.

## Output
Template.

## Acceptance
Criteria here.

## Chain
Think first.
"""

# ---------------------------------------------------------------------------
# check_prompt_structure
# ---------------------------------------------------------------------------


def test_check_full_prompt_passes() -> None:
    result = check_prompt_structure(_FULL_PROMPT)
    assert result.passed
    assert result.missing_sections == []


def test_check_missing_persona_fails() -> None:
    result = check_prompt_structure(_MISSING_PERSONA_PROMPT)
    assert not result.passed
    assert "PERSONA" in result.missing_sections


def test_check_result_found_sections_populated() -> None:
    result = check_prompt_structure(_FULL_PROMPT)
    assert len(result.found_sections) == 6


def test_check_empty_prompt_fails_all() -> None:
    result = check_prompt_structure("")
    assert not result.passed
    assert len(result.missing_sections) == 6


def test_check_minimal_valid_prompt_passes() -> None:
    result = check_prompt_structure(_MINIMAL_VALID_PROMPT)
    assert result.passed


def test_check_case_insensitive_headings() -> None:
    prompt = """\
## persona
X.
## task
Y.
## input artifacts
None.
## output template
T.
## acceptance criteria
C.
## chain-of-thought
Think.
"""
    result = check_prompt_structure(prompt)
    assert result.passed


# ---------------------------------------------------------------------------
# PromptValidationResult.__str__
# ---------------------------------------------------------------------------


def test_result_str_passed() -> None:
    r = PromptValidationResult(passed=True)
    assert "passed" in str(r)


def test_result_str_failed_shows_missing() -> None:
    r = PromptValidationResult(passed=False, missing_sections=["PERSONA", "TASK"])
    s = str(r)
    assert "FAILED" in s
    assert "PERSONA" in s
    assert "TASK" in s


# ---------------------------------------------------------------------------
# validate_prompt
# ---------------------------------------------------------------------------


def test_validate_prompt_passed_no_warnings() -> None:
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = validate_prompt(_FULL_PROMPT)
    assert result.passed
    assert len(w) == 0


def test_validate_prompt_missing_emits_warning() -> None:
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = validate_prompt(_MISSING_PERSONA_PROMPT)
    assert not result.passed
    assert len(w) == 1
    assert "PERSONA" in str(w[0].message)


def test_validate_prompt_strict_raises_on_failure() -> None:
    with pytest.raises(ValueError, match="missing required sections"):
        validate_prompt(_MISSING_PERSONA_PROMPT, strict=True)


def test_validate_prompt_strict_does_not_raise_on_pass() -> None:
    result = validate_prompt(_FULL_PROMPT, strict=True)
    assert result.passed


def test_validate_prompt_with_session_no_crash(tmp_path: Path) -> None:
    from sdlc_core.db import open_run, setup_db
    from sdlc_core.session import Session

    db_path = setup_db(tmp_path / "experiment.db")
    run_id = open_run(project="proj", approach=1, run_id="run-pv-01", db_path=db_path)
    session = Session(run_id=run_id, approach=1, active_phase=3, db_path=db_path)

    result = validate_prompt(_MISSING_PERSONA_PROMPT, session=session, artifact_id="REQ-01")
    assert not result.passed
