"""__init__.py: Shared experiment runtime library for the AI-Augmented SDLC study.

Provides database setup, structured write helpers, semantic integrity
checking, and metrics reporting for both approach template repositories.
"""

from __future__ import annotations

from sdlc_core.session import Session

__all__ = ["Session"]
