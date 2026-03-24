"""logged.py: LoggedProvider, automatic interaction logging around any ModelProvider.

Every call to ``complete()`` measures wall-clock time, submits the prompt to
the wrapped provider, captures the researcher's outcome decision from the
terminal, and writes a full row to the ``interactions`` table. The three
unavoidably human data points (outcome, whether the response was modified, and
modification notes) are collected via a compact terminal prompt immediately
after the response is displayed.

Usage::

    from sdlc_core.session import Session
    from sdlc_core.providers import OllamaProvider
    from sdlc_core.providers.logged import LoggedProvider

    session = Session(run_id="run-001", approach=2, active_phase=3)
    provider = LoggedProvider(OllamaProvider("llama3"), session=session)
    response = provider.complete(
        prompt="...",
        agent_role="software_architect",
        artifact_id="ARCH-VIEW-01",
    )

"""

from __future__ import annotations

import time
from typing import Any

from sdlc_core import db
from sdlc_core.enums import Outcome
from sdlc_core.providers.base import ModelProvider
from sdlc_core.session import Session

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SEPARATOR = "-" * 72

_OUTCOME_MAP: dict[str, Outcome] = {
    "a": Outcome.ACCEPTED,
    "r": Outcome.REJECTED,
    "m": Outcome.ACCEPTED_WITH_MODIFICATIONS,
}


# ---------------------------------------------------------------------------
# LoggedProvider
# ---------------------------------------------------------------------------


class LoggedProvider:
    """Wraps any ModelProvider with automatic timing and DB interaction logging.

    Args:
        provider: The underlying model provider to call.
        session:  Active experiment session holding ``run_id``, ``approach``,
                  ``active_phase``, and ``db_path``.

    """

    def __init__(self, provider: ModelProvider, session: Session) -> None:
        """Initialise the wrapper with a provider and active session."""
        self._provider = provider
        self._session = session

    @property
    def model_id(self) -> str:
        """Return the model identifier from the wrapped provider.

        Reads the ``_model_id`` attribute when present. Falls back to the
        provider's class name when the attribute is absent.

        Returns:
            A string identifying the model, e.g. ``"llama3:70b"``.

        """
        return str(getattr(self._provider, "_model_id", type(self._provider).__name__))

    def complete(
        self,
        prompt: str,
        *,
        agent_role: str,
        artifact_id: str | None = None,
        system: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> str:
        """Submit *prompt*, display the response, capture outcome, and write the DB row.

        Args:
            prompt:      Full prompt text to submit to the model.
            agent_role:  Declared role of the AI for this interaction,
                         e.g. ``"software_architect"``.
            artifact_id: Identifier of the artifact being produced. Pass
                         ``None`` for exploratory prompts not tied to an artifact.
            system:      Optional system prompt forwarded to the provider.
            **kwargs:    Forwarded to the underlying provider's ``complete`` method.

        Returns:
            The model response text exactly as returned by the provider.

        """
        t0 = time.perf_counter()
        response = self._provider.complete(prompt, system=system, **kwargs)
        ai_duration = int(time.perf_counter() - t0)

        print()
        print(_SEPARATOR)
        print("RESPONSE")
        print(_SEPARATOR)
        print(response)
        print(_SEPARATOR)

        t_review = time.perf_counter()
        outcome, notes = self._capture_outcome()
        human_review = int(time.perf_counter() - t_review)

        iteration = (
            self._session.next_iteration(artifact_id) if artifact_id is not None else 1
        )

        # Read token usage only when the provider exposes a real dict
        _raw_usage = getattr(self._provider, "last_token_usage", None)
        token_usage: dict[str, int] = _raw_usage if isinstance(_raw_usage, dict) else {}

        db.log_interaction(
            run_id=self._session.run_id,
            sdlc_phase=self._session.active_phase,
            approach=self._session.approach,
            agent_role=agent_role,
            model=self.model_id,
            prompt=prompt,
            response=response,
            iteration=iteration,
            outcome=outcome,
            human_modified=(outcome == Outcome.ACCEPTED_WITH_MODIFICATIONS),
            artifact_id=artifact_id,
            human_modification_notes=notes,
            duration_seconds=ai_duration,
            human_review_seconds=human_review,
            prompt_tokens=token_usage.get("prompt_tokens") or None,
            completion_tokens=token_usage.get("completion_tokens") or None,
            db_path=self._session.db_path,
        )

        return response

    def _capture_outcome(self) -> tuple[Outcome, str | None]:
        """Prompt the researcher at the terminal to declare the interaction outcome.

        Returns:
            A tuple of (outcome, modification_notes). Notes are ``None`` unless
            the outcome is ``accepted_with_modifications``.

        """
        outcome = self._read_outcome()
        notes = self._read_notes() if outcome == Outcome.ACCEPTED_WITH_MODIFICATIONS else None
        return outcome, notes

    def _read_outcome(self) -> Outcome:
        """Read a valid outcome choice from stdin, re-prompting on invalid input.

        Returns:
            The resolved ``Outcome`` enum member.

        """
        while True:
            raw = input("\nOutcome? [A]ccept / [R]eject / [M]odified: ").strip().lower()
            result = _OUTCOME_MAP.get(raw[:1] if raw else "")
            if result is not None:
                return result
            print("  Enter A, R, or M.")

    def _read_notes(self) -> str:
        """Read a non-empty modification notes string from stdin.

        Returns:
            A non-empty string describing what was changed and why.

        """
        while True:
            notes = input("Modification notes (required): ").strip()
            if notes:
                return notes
            print("  Notes are required for modified outcomes.")
