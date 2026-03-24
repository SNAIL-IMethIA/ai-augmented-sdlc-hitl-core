"""session.py: Active run context for an experiment working session.

A Session carries the run identifier, approach number, and active SDLC phase
so that LoggedProvider and other callers do not have to repeat these values
on every call. Create one at the start of each work session and pass it
through the stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


@dataclass
class Session:
    """Active experiment context held for the duration of a working session.

    Args:
        run_id:       Identifier of the parent run (from the ``runs`` table).
        approach:     Approach number for this run (1 or 2).
        active_phase: SDLC phase currently being executed (2 to 8).
        db_path:      Path to ``experiment.db``. ``None`` resolves the path
                      from the ``SDLC_DB_PATH`` environment variable or
                      defaults to ``logs/experiment.db`` relative to cwd.

    """

    run_id: str
    approach: int
    active_phase: int
    db_path: Path | None = None
    active_artifact_id: str | None = None
    _iterations: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    def next_iteration(self, artifact_id: str) -> int:
        """Return the next 1-based iteration index for *artifact_id*.

        The counter starts at 1 and increments on every call for the same
        artifact. A fresh ``Session`` starts with no history; the first call
        for any artifact always returns 1.

        Args:
            artifact_id: Identifier of the artifact being iterated, e.g.
                         ``"ARCH-ADR-01"``.

        Returns:
            The iteration number to record in the next ``log_interaction`` call.

        """
        self._iterations[artifact_id] = self._iterations.get(artifact_id, 0) + 1
        return self._iterations[artifact_id]

    def set_artifact(self, artifact_id: str | None) -> None:
        """Set or clear the active artifact for this session.

        When set, both ``LoggedProvider`` and ``InterventionLogger`` use this
        value automatically so callers do not have to repeat it on every call.
        Pass ``None`` to clear it between artifacts.

        Args:
            artifact_id: Identifier of the artifact now being worked on, e.g.
                         ``"ARCH-ADR-01"``. Pass ``None`` to clear.

        """
        self.active_artifact_id = artifact_id

    def set_phase(self, phase: int) -> None:
        """Update the active SDLC phase.

        Args:
            phase: New SDLC phase number. Must be between 2 and 8 inclusive.

        Raises:
            ValueError: If *phase* is outside the range 2 to 8.

        """
        if phase not in range(2, 9):
            raise ValueError(f"phase must be between 2 and 8, got {phase}")
        self.active_phase = phase


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------


class SessionManager:
    """Context manager that opens and closes a session record in the DB.

    Wraps :func:`sdlc_core.db.open_session` and
    :func:`sdlc_core.db.close_session` so researchers can track the three
    mandatory 8-hour working sessions without manually calling those
    functions.

    Args:
        session:        Active :class:`Session` instance carrying the
                        run identifier and DB path.
        session_number: 1-based ordinal of this session within the run
                        (1, 2, or 3).

    Example::

        with SessionManager(session, session_number=1) as sess:
            # work on Phase 2 for ~8 hours
            ...
        # ended_at is written automatically on exit

    """

    def __init__(self, session: Session, session_number: int) -> None:
        """Initialise the manager."""
        if session_number not in (1, 2, 3):
            raise ValueError(f"session_number must be 1, 2, or 3; got {session_number}")
        self._session = session
        self._session_number = session_number

    def __enter__(self) -> Session:
        """Open the session record and return the :class:`Session`."""
        from sdlc_core import db

        db.open_session(
            run_id=self._session.run_id,
            session_number=self._session_number,
            db_path=self._session.db_path,
        )
        return self._session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the session record.  Never suppresses exceptions."""
        from sdlc_core import db

        db.close_session(
            run_id=self._session.run_id,
            session_number=self._session_number,
            db_path=self._session.db_path,
        )
