"""db.py: Write helpers for experiment.db.

All writes to the database go through the functions in this module.
No caller should write SQL directly.

Design decisions:
- Every function opens its own connection and commits immediately.
  No long-lived connection state to manage across a run.
- Enum fields accept either the enum member or its string value.
  An unknown string value is accepted (so the researcher is not blocked
  during a run) but a row is written to `violations` and a warning is
  printed to stderr.
- Foreign key enforcement is enabled on every connection via PRAGMA.
- The path to experiment.db is resolved from the DB_PATH environment
  variable if set, falling back to "logs/experiment.db" relative to the
  working directory.
"""

from __future__ import annotations

import os
import sqlite3
import warnings
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from sdlc_core.enums import (
    InterventionCategory,
    Outcome,
    PhaseStatus,
    PipelineEventType,
    Severity,
    ValidationResult,
    ValidationType,
    ViolationType,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_db_path() -> Path:
    env = os.environ.get("SDLC_DB_PATH")
    return Path(env) if env else Path("logs") / "experiment.db"


@contextmanager
def _connect(db_path: Path | None = None) -> Generator[sqlite3.Connection]:
    path = db_path or _default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _coerce_enum(
    value: Enum | str,
    expected_values: set[str],
    field_name: str,
    *,
    fallback: str | None = None,
) -> str:
    """Return the string value; emit a warning and coerce to *fallback* if unrecognised.

    When *fallback* is provided and the value is not in *expected_values*, the
    warning is emitted and *fallback* is returned instead of the raw invalid
    string.  This keeps the database write from failing a CHECK constraint
    while still recording that an unexpected value was supplied.

    When *fallback* is ``None`` (default), the raw string is returned; the
    caller is responsible for handling any resulting constraint violation.
    """
    str_value: str = str(value.value) if isinstance(value, Enum) else str(value)
    if str_value not in expected_values:
        effective = fallback if fallback is not None else str_value
        warnings.warn(
            f"Field '{field_name}' received unexpected value '{str_value}'. "
            f"Expected one of: {sorted(expected_values)}. "
            f"The value will be stored as '{effective}' and a violation record "
            "will be written.",
            stacklevel=3,
        )
        return effective
    return str_value


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------

def setup_db(db_path: Path | str | None = None) -> Path:
    """Create the experiment database with the canonical schema.

    Idempotent: safe to call multiple times (uses ``CREATE TABLE IF NOT EXISTS``).

    Args:
        db_path: Path to the SQLite file to create.  Defaults to the value of
                 the ``SDLC_DB_PATH`` environment variable, or
                 ``logs/experiment.db`` relative to the working directory.

    Returns:
        Resolved :class:`~pathlib.Path` to the created database file.

    """
    path = Path(db_path) if db_path else _default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    with sqlite3.connect(path) as conn:
        conn.executescript(schema_sql)

    print(f"[sdlc_core] Database ready at {path}")
    return path


# ---------------------------------------------------------------------------
# runs
# ---------------------------------------------------------------------------

def open_run(
    *,
    project: str,
    approach: int,
    run_id: str | None = None,
    db_path: Path | None = None,
) -> str:
    """Insert a new row in ``runs`` and return the run identifier.

    Args:
        project:  Short project identifier string (e.g. ``"project1"``).
        approach: Approach number, must be one of 1 or 2.
        run_id:   Optional explicit run identifier.  When omitted a
                  deterministic identifier is derived from *project*,
                  *approach*, and the current UTC date.
        db_path:  Path to ``experiment.db``.  Defaults to
                  :func:`_default_db_path`.

    Returns:
        The run identifier string that was inserted.

    Raises:
        ValueError: If *approach* is not in the set {1, 2}.

    """
    if approach not in (1, 2):
        raise ValueError(f"approach must be 1 or 2, got {approach}")

    now = _now()
    rid = run_id or f"run-{project}-approach{approach}-{now[:10].replace('-', '')}"

    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO runs (id, project, approach, started_at) VALUES (?, ?, ?, ?)",
            (rid, project, approach, now),
        )
    return rid


def close_run(
    *,
    run_id: str,
    terminal_phase: int,
    db_path: Path | None = None,
) -> None:
    """Set ``ended_at`` and ``terminal_phase`` on an existing runs row.

    Args:
        run_id:         Identifier of the run to close.
        terminal_phase: Last SDLC phase number reached within the time budget.
        db_path:        Path to ``experiment.db``.  Defaults to
                        :func:`_default_db_path`.

    """
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE runs SET ended_at = ?, terminal_phase = ? WHERE id = ?",
            (_now(), terminal_phase, run_id),
        )


# ---------------------------------------------------------------------------
# sessions
# ---------------------------------------------------------------------------

def open_session(
    *,
    run_id: str,
    session_number: int,
    db_path: Path | None = None,
) -> None:
    """Insert a new row in ``sessions`` marking the start of a work session.

    Args:
        run_id:         Identifier of the parent run.
        session_number: 1-based ordinal of this session within the run.
        db_path:        Path to ``experiment.db``.  Defaults to
                        :func:`_default_db_path`.

    """
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO sessions (run_id, session_number, started_at) VALUES (?, ?, ?)",
            (run_id, session_number, _now()),
        )


def close_session(
    *,
    run_id: str,
    session_number: int,
    db_path: Path | None = None,
) -> None:
    """Set ``ended_at`` on an open sessions row.

    Args:
        run_id:         Identifier of the parent run.
        session_number: 1-based ordinal of the session to close.
        db_path:        Path to ``experiment.db``.  Defaults to
                        :func:`_default_db_path`.

    """
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE run_id = ? AND session_number = ?",
            (_now(), run_id, session_number),
        )


# ---------------------------------------------------------------------------
# phase_progress
# ---------------------------------------------------------------------------

def set_phase_status(
    *,
    run_id: str,
    phase_number: int,
    status: PhaseStatus | str,
    db_path: Path | None = None,
) -> None:
    """Insert or update the ``phase_progress`` row for a given phase.

    Uses ``INSERT ... ON CONFLICT ... DO UPDATE`` so it is safe to call
    multiple times as a phase transitions through states.

    Args:
        run_id:       Identifier of the parent run.
        phase_number: SDLC phase number (2 to 8).
        status:       New status value; a :class:`~sdlc_core.enums.PhaseStatus`
                      member or its string value.
        db_path:      Path to ``experiment.db``.  Defaults to
                      :func:`_default_db_path`.

    """
    status_str = _coerce_enum(
        status,
        {m.value for m in PhaseStatus},
        "status",
    )
    now = _now()
    entered_at = now if status_str == PhaseStatus.IN_PROGRESS.value else None
    completed_at = now if status_str == PhaseStatus.COMPLETED.value else None

    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO phase_progress (run_id, phase_number, status, entered_at, completed_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (run_id, phase_number) DO UPDATE SET
                status       = excluded.status,
                entered_at   = COALESCE(phase_progress.entered_at,   excluded.entered_at),
                completed_at = COALESCE(phase_progress.completed_at, excluded.completed_at)
            """,
            (run_id, phase_number, status_str, entered_at, completed_at),
        )


# ---------------------------------------------------------------------------
# artifacts
# ---------------------------------------------------------------------------

def accept_artifact(
    *,
    run_id: str,
    artifact_id: str,
    artifact_type: str,
    phase: int,
    git_commit_sha: str | None = None,
    content_hash: str | None = None,
    upstream_ids: list[str] | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert an accepted artifact and write its upstream traceability links.

    If the artifact already exists in the database (same ``id`` and ``run_id``)
    only the ``status``, ``git_commit_sha``, and ``content_hash`` are updated.
    Traceability link rows are inserted with ``INSERT OR IGNORE`` so
    duplicate edges are silently skipped.

    Args:
        run_id:         Identifier of the parent run.
        artifact_id:    Unique identifier for the artifact (e.g. ``ARCH-01``).
        artifact_type:  Human-readable type label (e.g. ``"Architecture Document"``).
        phase:          SDLC phase number in which the artifact was produced.
        git_commit_sha: SHA of the git commit that contains the artifact file.
        content_hash:   Optional SHA-256 of the artifact's contents.
        upstream_ids:   List of artifact identifiers that this artifact traces
                        to.  A ``traceability_links`` row is inserted for each.
        db_path:        Path to ``experiment.db``.  Defaults to
                        :func:`_default_db_path`.

    """
    now = _now()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO artifacts
                (id, run_id, artifact_type, phase, git_commit_sha, content_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'accepted', ?)
            ON CONFLICT (id, run_id) DO UPDATE SET
                status         = 'accepted',
                git_commit_sha = COALESCE(excluded.git_commit_sha, artifacts.git_commit_sha),
                content_hash   = COALESCE(excluded.content_hash,   artifacts.content_hash)
            """,
            (artifact_id, run_id, artifact_type, phase, git_commit_sha, content_hash, now),
        )
        for upstream_id in (upstream_ids or []):
            conn.execute(
                """
                INSERT OR IGNORE INTO traceability_links
                    (from_artifact_id, to_artifact_id, run_id, link_type, created_at)
                VALUES (?, ?, ?, 'traces_to', ?)
                """,
                (artifact_id, upstream_id, run_id, now),
            )


# ---------------------------------------------------------------------------
# interactions
# ---------------------------------------------------------------------------

def log_interaction(
    *,
    run_id: str,
    sdlc_phase: int,
    approach: int,
    agent_role: str,
    model: str,
    prompt: str,
    response: str,
    iteration: int,
    outcome: Outcome | str,
    human_modified: bool,
    artifact_id: str | None = None,
    human_modification_notes: str | None = None,
    duration_seconds: int | None = None,
    human_review_seconds: int | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    db_path: Path | None = None,
) -> int:
    """Insert one prompt-response exchange into ``interactions``.

    Args:
        run_id:                    Identifier of the parent run.
        sdlc_phase:                SDLC phase number (2 to 8).
        approach:                  Approach number (1 or 2).
        agent_role:                Role label for the AI agent (e.g.
                                   ``"requirements_analyst"``).
        model:                     Model identifier string.
        prompt:                    Full prompt text submitted to the model.
        response:                  Full model response text.
        iteration:                 1-based iteration count for this artifact.
        outcome:                   Interaction outcome; an
                                   :class:`~sdlc_core.enums.Outcome` member
                                   or its string value.
        human_modified:            Whether the response was edited before
                                   acceptance.
        artifact_id:               Optional identifier of the artifact being
                                   produced by this interaction.
        human_modification_notes:  Required when *human_modified* is ``True``.
                                   Describes what was changed and why.
        duration_seconds:          AI response latency measured from prompt
                                   submission to response receipt.
        human_review_seconds:      Time in seconds from response display to
                                   outcome entry by the researcher.
        prompt_tokens:             Token count of the submitted prompt as
                                   reported by the model.  ``None`` when
                                   the provider does not report usage.
        completion_tokens:         Token count of the model response.  ``None``
                                   when the provider does not report usage.
        db_path:                   Optional path to the SQLite database file.

    Returns:
        The ``rowid`` (integer primary key) of the inserted row.

    Raises:
        ValueError: If *human_modified* is ``True`` and
                    *human_modification_notes* is ``None`` or empty.

    """
    outcome_str = _coerce_enum(
        outcome, {m.value for m in Outcome}, "outcome", fallback="accepted"
    )

    if human_modified and not human_modification_notes:
        raise ValueError(
            "human_modification_notes is required when human_modified is True."
        )

    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO interactions
                (run_id, artifact_id, timestamp, sdlc_phase, approach, agent_role, model,
                 prompt, response, iteration, outcome, human_modified,
                 human_modification_notes, duration_seconds, human_review_seconds,
                 prompt_tokens, completion_tokens)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id, artifact_id, _now(), sdlc_phase, approach, agent_role, model,
                prompt, response, iteration, outcome_str, int(human_modified),
                human_modification_notes, duration_seconds, human_review_seconds,
                prompt_tokens, completion_tokens,
            ),
        )
        # INSERT always produces a rowid
        assert cur.lastrowid is not None
        return cur.lastrowid


# ---------------------------------------------------------------------------
# interventions
# ---------------------------------------------------------------------------

def log_intervention(
    *,
    run_id: str,
    sdlc_phase: int,
    category: InterventionCategory | str,
    severity: Severity | str,
    rationale: str,
    time_spent_minutes: int,
    artifact_id: str | None = None,
    db_path: Path | None = None,
) -> int:
    """Insert a human intervention record into ``interventions``.

    Args:
        run_id:              Identifier of the parent run.
        sdlc_phase:          SDLC phase number (2 to 8).
        category:            Intervention category; an
                             :class:`~sdlc_core.enums.InterventionCategory`
                             member or its string value.
        severity:            Severity level; a
                             :class:`~sdlc_core.enums.Severity` member or
                             its string value.
        rationale:           Free-text explanation of why the intervention
                             was needed.
        time_spent_minutes:  Duration of the intervention in minutes.
        artifact_id:         Optional identifier of the affected artifact.
        db_path:             Path to ``experiment.db``.  Defaults to
                             :func:`_default_db_path`.

    Returns:
        The ``rowid`` (integer primary key) of the inserted row.

    """
    cat_str = _coerce_enum(
        category, {m.value for m in InterventionCategory}, "category", fallback="other"
    )
    sev_str = _coerce_enum(severity, {m.value for m in Severity}, "severity")

    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO interventions
                (run_id, artifact_id, timestamp, sdlc_phase, category, severity,
                 rationale, time_spent_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, artifact_id, _now(), sdlc_phase, cat_str, sev_str,
             rationale, time_spent_minutes),
        )
        # INSERT always produces a rowid
        assert cur.lastrowid is not None
        return cur.lastrowid


# ---------------------------------------------------------------------------
# validation_results + defects
# ---------------------------------------------------------------------------

def log_validation_result(
    *,
    run_id: str,
    sdlc_phase: int,
    validation_type: ValidationType | str,
    result: ValidationResult | str,
    defects_found: int,
    artifact_id: str | None = None,
    notes: str | None = None,
    db_path: Path | None = None,
) -> int:
    """Insert a validation result record into ``validation_results``.

    Args:
        run_id:           Identifier of the parent run.
        sdlc_phase:       SDLC phase number (2 to 8).
        validation_type:  Validation activity type; a
                          :class:`~sdlc_core.enums.ValidationType` member
                          or its string value.
        result:           Outcome of the validation; a
                          :class:`~sdlc_core.enums.ValidationResult` member
                          or its string value.
        defects_found:    Count of defects identified during this validation
                          session.  Must equal the number of associated
                          ``defects`` rows (enforced by check G3).
        artifact_id:      Optional identifier of the artifact under review.
        notes:            Free-text notes from the reviewer.
        db_path:          Path to ``experiment.db``.  Defaults to
                          :func:`_default_db_path`.

    Returns:
        The ``rowid`` (integer primary key) of the inserted row.

    """
    vtype_str = _coerce_enum(validation_type, {m.value for m in ValidationType}, "validation_type")
    result_str = _coerce_enum(result, {m.value for m in ValidationResult}, "result")

    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO validation_results
                (artifact_id, run_id, sdlc_phase, validation_type, result,
                 defects_found, notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (artifact_id, run_id, sdlc_phase, vtype_str, result_str,
             defects_found, notes, _now()),
        )
        # INSERT always produces a rowid
        assert cur.lastrowid is not None
        return cur.lastrowid


def log_defect(
    *,
    run_id: str,
    validation_result_id: int,
    sdlc_phase_detected: int,
    severity: Severity | str,
    description: str,
    artifact_id: str | None = None,
    origin_phase: int | None = None,
    db_path: Path | None = None,
) -> int:
    """Insert a defect record into ``defects``.

    Args:
        run_id:               Identifier of the parent run.
        validation_result_id: Primary key of the parent
                              ``validation_results`` row.
        sdlc_phase_detected:  SDLC phase in which the defect was found.
        severity:             Defect severity; a
                              :class:`~sdlc_core.enums.Severity` member
                              or its string value.
        description:          Free-text description of the defect.
        artifact_id:          Optional identifier of the defective artifact.
        origin_phase:         SDLC phase in which the defect was introduced,
                              if known.  Used for defect-origin mapping.
        db_path:              Path to ``experiment.db``.  Defaults to
                              :func:`_default_db_path`.

    Returns:
        The ``rowid`` (integer primary key) of the inserted row.

    """
    sev_str = _coerce_enum(severity, {m.value for m in Severity}, "severity")
    now = _now()

    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO defects
                (run_id, validation_result_id, artifact_id, sdlc_phase_detected,
                 origin_phase, severity, description, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, validation_result_id, artifact_id, sdlc_phase_detected,
             origin_phase, sev_str, description, now),
        )
        # INSERT always produces a rowid
        assert cur.lastrowid is not None
        return cur.lastrowid


def resolve_defect(
    *,
    defect_id: int,
    db_path: Path | None = None,
) -> None:
    """Mark a defect as resolved by setting its ``resolved_at`` timestamp.

    Args:
        defect_id: Primary key of the ``defects`` row to resolve.
        db_path:   Path to ``experiment.db``.  Defaults to
                   :func:`_default_db_path`.

    """
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE defects SET resolved_at = ? WHERE id = ?",
            (_now(), defect_id),
        )


# ---------------------------------------------------------------------------
# pipeline_events (Approach 2 only)
# ---------------------------------------------------------------------------

def log_pipeline_event(
    *,
    run_id: str,
    pipeline_id: str,
    step: str,
    agent_role: str,
    event_type: PipelineEventType | str,
    detail: str,
    artifact_id: str | None = None,
    db_path: Path | None = None,
) -> int:
    """Insert a pipeline control-flow event into ``pipeline_events``.

    Intended for Approach 2 only. Callers using Approach 1 should not call
    this function.

    Args:
        run_id:       Identifier of the parent run.
        pipeline_id:  Identifier of the pipeline or workflow that emitted
                      the event.
        step:         Name of the pipeline step (e.g. ``"arch_review"``).
        agent_role:   Role of the agent that triggered the event.
        event_type:   Event type; a
                      :class:`~sdlc_core.enums.PipelineEventType` member
                      or its string value.
        detail:       Free-text description of the event payload.
        artifact_id:  Optional identifier of the artifact involved.
        db_path:      Path to ``experiment.db``.  Defaults to
                      :func:`_default_db_path`.

    Returns:
        The ``rowid`` (integer primary key) of the inserted row.

    """
    etype_str = _coerce_enum(event_type, {m.value for m in PipelineEventType}, "event_type")

    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO pipeline_events
                (run_id, pipeline_id, timestamp, step, agent_role, event_type,
                 artifact_id, detail)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, pipeline_id, _now(), step, agent_role, etype_str,
             artifact_id, detail),
        )
        # INSERT always produces a rowid
        assert cur.lastrowid is not None
        return cur.lastrowid


# ---------------------------------------------------------------------------
# violations
# ---------------------------------------------------------------------------

def log_violation(
    *,
    violation_type: ViolationType | str,
    detail: str,
    run_id: str | None = None,
    artifact_id: str | None = None,
    db_path: Path | None = None,
) -> int:
    """Insert a violation record into ``violations``.

    This function is the internal fallback called automatically by
    :func:`_coerce_enum` whenever an unrecognised enum value is encountered.
    It may also be called directly by any caller that detects a governance
    rule breach.

    Args:
        violation_type: Violation category; a
                        :class:`~sdlc_core.enums.ViolationType` member or
                        its string value.
        detail:         Free-text description of the specific breach.
        run_id:         Optional identifier of the affected run.
        artifact_id:    Optional identifier of the affected artifact.
        db_path:        Path to ``experiment.db``.  Defaults to
                        :func:`_default_db_path`.

    Returns:
        The ``rowid`` (integer primary key) of the inserted row.

    """
    vtype_str = _coerce_enum(
        violation_type, {m.value for m in ViolationType}, "violation_type"
    )

    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO violations (run_id, artifact_id, violation_type, detail, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, artifact_id, vtype_str, detail, _now()),
        )
        # INSERT always produces a rowid
        assert cur.lastrowid is not None
        return cur.lastrowid
