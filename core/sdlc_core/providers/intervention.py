"""intervention.py: InterventionLogger, guided terminal UI for human intervention records.

Usage::

    from sdlc_core.session import Session
    from sdlc_core.providers.intervention import InterventionLogger

    logger = InterventionLogger(session)
    logger.log(artifact_id="IMPL-03")   # omit artifact_id to be prompted at runtime

"""

from __future__ import annotations

from typing import Any

from sdlc_core import db
from sdlc_core.enums import InterventionCategory, Severity
from sdlc_core.session import Session

# ---------------------------------------------------------------------------
# Menu definitions
# ---------------------------------------------------------------------------

_SEPARATOR = "-" * 72

_CATEGORIES: list[tuple[str, InterventionCategory]] = [
    ("clarification",      InterventionCategory.CLARIFICATION),
    ("correction",         InterventionCategory.CORRECTION),
    ("rejection",          InterventionCategory.REJECTION),
    ("strategic_decision", InterventionCategory.STRATEGIC_DECISION),
    ("safety_override",    InterventionCategory.SAFETY_OVERRIDE),
    ("manual_edit",        InterventionCategory.MANUAL_EDIT),
    ("environment_fix",    InterventionCategory.ENVIRONMENT_FIX),
    ("other",              InterventionCategory.OTHER),
]

_SEVERITIES: list[tuple[str, Severity]] = [
    ("minor",    Severity.MINOR),
    ("moderate", Severity.MODERATE),
    ("critical", Severity.CRITICAL),
]


# ---------------------------------------------------------------------------
# InterventionLogger
# ---------------------------------------------------------------------------


class InterventionLogger:
    """Guided terminal interface for logging human interventions.

    Actions such as a manual edit, a strategic decision, a correction, or an
    environment fix must be recorded in the ``interventions`` table whenever
    they occur outside an AI call. This class walks the researcher through
    the required fields with a numbered-menu UI and then writes the row.

    Args:
        session: Active experiment session holding ``run_id``,
                 ``active_phase``, and ``db_path``.

    Example::

        logger = InterventionLogger(session)
        row_id = logger.log(artifact_id="IMPL-03")

    """

    def __init__(self, session: Session) -> None:
        """Initialise with the active experiment session."""
        self._session = session

    def log(self, artifact_id: str | None = None) -> int:
        """Prompt the researcher for intervention details and write a DB row.

        Displays numbered menus for category and severity, then collects
        an optional artifact ID (unless pre-supplied), a required rationale,
        and the time spent on the intervention.  Writes one row to the
        ``interventions`` table via :func:`sdlc_core.db.log_intervention`.

        The ``time_spent_minutes`` field is self-reported because the
        intervention work happens before the logger is invoked. The
        researcher enters the actual duration of the work that prompted
        this record, not the time spent filling in this form.

        Args:
            artifact_id: Identifier of the affected artifact. When
                         ``None``, the researcher is prompted and may
                         press Enter to leave it unset for run-level
                         interventions not tied to a specific artifact.

        Returns:
            The primary key of the inserted ``interventions`` row.

        """
        print()
        print(_SEPARATOR)
        print("INTERVENTION LOGGER")
        print(_SEPARATOR)

        category = self._read_choice("Category", _CATEGORIES)
        severity = self._read_choice("Severity", _SEVERITIES)
        resolved_id = self._read_artifact(artifact_id)
        rationale = self._read_rationale()
        minutes = self._read_minutes()

        row_id = db.log_intervention(
            run_id=self._session.run_id,
            sdlc_phase=self._session.active_phase,
            category=category,
            severity=severity,
            rationale=rationale,
            time_spent_minutes=minutes,
            artifact_id=resolved_id,
            db_path=self._session.db_path,
        )

        print(f"\nLogged intervention #{row_id}.")
        print(_SEPARATOR)
        return row_id

    # ---------------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------------

    @staticmethod
    def _read_choice(label: str, options: list[tuple[str, Any]]) -> Any:  # noqa: ANN401
        """Display a numbered menu and return the value of the selected option.

        Args:
            label:   Section heading printed above the numbered list.
            options: Ordered pairs of (display_name, value) to present.

        Returns:
            The value from the selected option pair.

        """
        print(f"\n{label}:")
        for i, (name, _) in enumerate(options, start=1):
            print(f"  {i:>2}. {name}")
        n = len(options)
        while True:
            raw = input(f"Choice [1-{n}]: ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < n:
                    return options[idx][1]
            print(f"  Enter a number between 1 and {n}.")

    @staticmethod
    def _read_artifact(preset: str | None) -> str | None:
        """Return the preset artifact ID or prompt the researcher for one.

        Args:
            preset: A pre-supplied artifact ID. The prompt is skipped
                    when this value is not ``None``.

        Returns:
            A non-empty artifact ID string, or ``None`` when the
            researcher presses Enter without input.

        """
        if preset is not None:
            return preset
        raw = input("\nArtifact ID (press Enter to skip): ").strip()
        return raw if raw else None

    @staticmethod
    def _read_rationale() -> str:
        """Prompt for a non-empty rationale string, re-prompting on blank input.

        Returns:
            A non-empty string describing why the intervention was necessary.

        """
        while True:
            raw = input("\nRationale: ").strip()
            if raw:
                return raw
            print("  Rationale is required.")

    @staticmethod
    def _read_minutes() -> int:
        """Prompt for a positive integer number of minutes, re-prompting on invalid input.

        Returns:
            A positive integer representing the time spent on the intervention.

        """
        while True:
            raw = input("\nTime spent (minutes): ").strip()
            if raw.isdigit() and int(raw) > 0:
                return int(raw)
            print("  Enter a whole number greater than 0.")
