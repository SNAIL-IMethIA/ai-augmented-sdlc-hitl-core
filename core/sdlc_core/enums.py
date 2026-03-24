"""enums.py: Controlled vocabularies for all enumerated database fields.

Every field in the schema that accepts a fixed set of values has a corresponding
enum here.  Write helpers in db.py accept either the enum member or its string
value, so callers may use whichever is more convenient.
"""

from __future__ import annotations

from enum import Enum


class Outcome(str, Enum):
    """Possible outcomes of a single prompt-response interaction."""

    ACCEPTED = "accepted"
    ACCEPTED_WITH_MODIFICATIONS = "accepted_with_modifications"
    REJECTED = "rejected"


class InterventionCategory(str, Enum):
    """Category labels for human interventions recorded in the run log."""

    CLARIFICATION = "clarification"
    CORRECTION = "correction"
    REJECTION = "rejection"
    STRATEGIC_DECISION = "strategic_decision"
    SAFETY_OVERRIDE = "safety_override"
    MANUAL_EDIT = "manual_edit"
    ENVIRONMENT_FIX = "environment_fix"
    OTHER = "other"


class Severity(str, Enum):
    """Severity level for defects and interventions."""

    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class ViolationType(str, Enum):
    """Categories of governance or schema violations written to the violations table."""

    MISSING_REQUIRED_FIELD = "missing_required_field"
    FOREIGN_KEY_FAILURE = "foreign_key_failure"
    SCHEMA_CONSTRAINT_FAILURE = "schema_constraint_failure"
    TRACEABILITY_GAP = "traceability_gap"
    REQUIREMENT_COVERAGE_GAP = "requirement_coverage_gap"
    PROMPT_STRUCTURE_VIOLATION = "prompt_structure_violation"
    FIT_CRITERION_FAILURE = "fit_criterion_failure"
    OTHER = "other"


class ValidationResult(str, Enum):
    """Outcome of a validation activity (review, test, acceptance test)."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"


class ValidationType(str, Enum):
    """Type of validation activity performed."""

    TESTING = "testing"
    DEMONSTRATION = "demonstration"
    REVIEW = "review"
    ACCEPTANCE_TEST = "acceptance_test"


class PipelineEventType(str, Enum):
    """Control-flow event types emitted by automated pipelines (Approach 2)."""

    GATE_PASS = "gate_pass"
    GATE_FAIL = "gate_fail"
    RETRY = "retry"
    CIRCUIT_BREAK = "circuit_break"
    REENTRY_APPROVAL = "reentry_approval"
    HALT = "halt"
    RESUME = "resume"


class ArtifactStatus(str, Enum):
    """Lifecycle status of an artifact stored in the artifacts table."""

    DRAFT = "draft"
    ACCEPTED = "accepted"
    SUPERSEDED = "superseded"


class PhaseStatus(str, Enum):
    """Progress status of an SDLC phase within a run."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_REACHED = "partially_reached"


class AutomationLevel(str, Enum):
    """Degree of automation for a task or phase step."""

    FULLY_AUTOMATED = "Fully automated"
    HUMAN_ASSISTED = "Human-assisted"
    MANUAL = "Manual"


# ---------------------------------------------------------------------------
# Lookup table
# ---------------------------------------------------------------------------

# All concrete enum classes in this module, used to build ENUM_VALUES below
_ENUM_CLASSES: list[type[Enum]] = [
    Outcome,
    InterventionCategory,
    Severity,
    ViolationType,
    ValidationResult,
    ValidationType,
    PipelineEventType,
    ArtifactStatus,
    PhaseStatus,
    AutomationLevel,
]

# Mapping from enum class name to its set of valid string values
# Used by db.py to validate field values before writing
ENUM_VALUES: dict[str, set[str]] = {
    cls.__name__: {str(m.value) for m in cls}
    for cls in _ENUM_CLASSES
}
