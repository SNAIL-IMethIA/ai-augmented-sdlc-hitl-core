"""test_enums.py: Tests for sdlc_core.enums and _coerce_enum."""

from __future__ import annotations

import warnings

import pytest

from sdlc_core.db import _coerce_enum  # pyright: ignore[reportPrivateUsage]
from sdlc_core.enums import (
    _ENUM_CLASSES,  # pyright: ignore[reportPrivateUsage]
    ENUM_VALUES,
    InterventionCategory,
    Outcome,
    PhaseStatus,
    PipelineEventType,
    Severity,
    ValidationResult,
    ValidationType,
    ViolationType,
)

_EXPECTED_CLASS_NAMES = {
    "Outcome",
    "InterventionCategory",
    "Severity",
    "ViolationType",
    "ValidationResult",
    "ValidationType",
    "PipelineEventType",
    "ArtifactStatus",
    "PhaseStatus",
    "AutomationLevel",
}


# ---------------------------------------------------------------------------
# ENUM_VALUES structure
# ---------------------------------------------------------------------------


def test_enum_values_has_all_expected_classes() -> None:
    assert set(ENUM_VALUES.keys()) == _EXPECTED_CLASS_NAMES


def test_enum_values_match_actual_members() -> None:
    for cls in _ENUM_CLASSES:
        expected = {str(m.value) for m in cls}
        assert ENUM_VALUES[cls.__name__] == expected, (
            f"ENUM_VALUES['{cls.__name__}'] does not match its enum members"
        )


def test_enum_values_are_non_empty() -> None:
    for name, values in ENUM_VALUES.items():
        assert len(values) > 0, f"ENUM_VALUES['{name}'] is empty"


# ---------------------------------------------------------------------------
# Spot-checks on specific enum members
# ---------------------------------------------------------------------------


def test_outcome_accepted_value() -> None:
    assert Outcome.ACCEPTED.value == "accepted"


def test_severity_critical_value() -> None:
    assert Severity.CRITICAL.value == "critical"


def test_phase_status_completed_value() -> None:
    assert PhaseStatus.COMPLETED.value == "completed"


def test_automation_level_values_non_ascii() -> None:
    # AutomationLevel uses sentence-case values; they must round-trip via ENUM_VALUES.
    assert "Fully automated" in ENUM_VALUES["AutomationLevel"]
    assert "Human-assisted" in ENUM_VALUES["AutomationLevel"]
    assert "Manual" in ENUM_VALUES["AutomationLevel"]


# ---------------------------------------------------------------------------
# _coerce_enum behaviour
# ---------------------------------------------------------------------------


def test_coerce_valid_enum_member_returns_string() -> None:
    result = _coerce_enum(Outcome.ACCEPTED, ENUM_VALUES["Outcome"], "outcome")
    assert result == "accepted"


def test_coerce_valid_string_returns_unchanged() -> None:
    result = _coerce_enum("accepted", ENUM_VALUES["Outcome"], "outcome")
    assert result == "accepted"


def test_coerce_enum_member_with_modifications() -> None:
    result = _coerce_enum(
        Outcome.ACCEPTED_WITH_MODIFICATIONS,
        ENUM_VALUES["Outcome"],
        "outcome",
    )
    assert result == "accepted_with_modifications"


def test_coerce_unknown_string_emits_warning() -> None:
    with pytest.warns(UserWarning, match="unexpected value"):
        _coerce_enum("invalid_value", ENUM_VALUES["Outcome"], "outcome")


def test_coerce_unknown_string_still_returns_value() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = _coerce_enum("anything_goes", ENUM_VALUES["Outcome"], "outcome")
    assert result == "anything_goes"


def test_coerce_intervention_category_valid() -> None:
    result = _coerce_enum(
        InterventionCategory.CORRECTION,
        ENUM_VALUES["InterventionCategory"],
        "category",
    )
    assert result == "correction"


def test_coerce_pipeline_event_type_valid() -> None:
    result = _coerce_enum(
        PipelineEventType.GATE_PASS,
        ENUM_VALUES["PipelineEventType"],
        "event_type",
    )
    assert result == "gate_pass"


def test_coerce_validation_result_valid() -> None:
    result = _coerce_enum(
        ValidationResult.CONDITIONAL,
        ENUM_VALUES["ValidationResult"],
        "result",
    )
    assert result == "conditional"


def test_coerce_validation_type_valid() -> None:
    result = _coerce_enum(
        ValidationType.ACCEPTANCE_TEST,
        ENUM_VALUES["ValidationType"],
        "validation_type",
    )
    assert result == "acceptance_test"


def test_coerce_violation_type_valid() -> None:
    result = _coerce_enum(
        ViolationType.TRACEABILITY_GAP,
        ENUM_VALUES["ViolationType"],
        "violation_type",
    )
    assert result == "traceability_gap"
