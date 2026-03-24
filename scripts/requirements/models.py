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
        cs:               Customer Satisfaction score (0 to 5).
        cd:               Customer Dissatisfaction score (0 to 5).
        status:           Lifecycle status (``Draft``, ``Reviewed``,
                          ``Approved``, or ``Deprecated``).
        priority:         MoSCoW label (``Must``, ``Should``, ``Could``,
                          or ``Won't``).
        source_path:      Absolute path to the originating ``.md`` file.
        raw_text:         Full unmodified content of the source file.
        title:            Short descriptive title extracted from the leading
                          ``# Title`` heading.
        req_type:         Requirement category, e.g. ``Functional``,
                          ``Non-Functional``, ``Constraint``.

    """

    req_id: str
    cs: int
    cd: int
    status: str
    priority: str
    source_path: Path
    raw_text: str
    req_type: str
    title: str
