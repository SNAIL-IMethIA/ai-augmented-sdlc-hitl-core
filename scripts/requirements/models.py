"""models.py: Requirement dataclass.

Defines the canonical in-memory representation of a single REQ-*.md file.
All other modules in this package operate on Requirement instances rather
than on raw strings, keeping parsing logic isolated from business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Requirement:
    """Parsed representation of a single REQ-*.md file.

    Attributes:
        req_id:           Requirement identifier, e.g. ``REQ-01``.
        cs:               Customer Satisfaction score (0–5).
        cd:               Customer Dissatisfaction score (0–5).
        status:           Lifecycle status (``Draft``, ``Reviewed``,
                          ``Approved``, or ``Deprecated``).
                          ``None`` if the field is absent in the source file.
        priority:         MoSCoW label (``Must``, ``Should``, ``Could``,
                          or ``Won't``).
                          ``None`` if the field is absent in the source file.
        source_path:      Absolute path to the originating ``.md`` file.
        raw_text:         Full unmodified content of the source file.
        title:            Short descriptive title extracted from the leading
                          ``# Title`` heading.  ``None`` if the heading is
                          absent in the source file.
        req_type:         Requirement category, e.g. ``Functional``,
                          ``Non-Functional``, ``Constraint``.

    """

    req_id: str
    cs: int
    cd: int
    status: str | None
    priority: str | None
    source_path: Path
    raw_text: str
    req_type: str | None = None  #: e.g. ``Functional``, ``Non-Functional``, ``Constraint``.
    title: str | None = None     #: Short title from the leading ``# Title`` heading.
