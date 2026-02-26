"""parser.py: Reading and writing REQ-*.md files.

Provides two public functions:

    load(path)          Read a single REQ-*.md file and return a Requirement.
    save(req, updates)  Apply field updates to a Requirement and write it back.

File structure:
    Every REQ file starts with an optional markdown heading that acts as the
    human-readable title::

        # Short descriptive title

        **ID:** REQ-01
        …

    When the heading is present, ``load`` extracts it as ``Requirement.title``.
    When it is absent, ``title`` is ``None``.  ``save`` can insert or replace
    the heading via the ``title`` keyword argument.

Parsing strategy for bold fields:
    Each field in a REQ file is formatted as::

        **Field Name:**
        value

    Fields that contain a bulleted score (CS / CD) use the format::

        **Customer Satisfaction (0–5):**
        - 4: Description text…

    The leading digit on the first bullet is extracted as the score.

    Fields may be absent in older files that predate the template revision
    that added ``Status`` and ``Priority``.  Absent fields are represented
    as ``None`` on the returned Requirement and can be added via ``save``.

Insertion order when adding absent bold fields:
    Priority  → inserted after Status (preferred) or after
                Dependencies / Conflicts.
    Status    → inserted after Dependencies / Conflicts.
    Fallback  → inserted immediately before **History:** if neither
                anchor is found.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import Requirement

# ---------------------------------------------------------------------------
# Internal regex constants
# ---------------------------------------------------------------------------

_TITLE_HEADING_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)
_ID_RE = re.compile(r"\*\*ID:\*\*\s*(REQ-\d+)")
_TYPE_RE = re.compile(r"\*\*Type:\*\*\s*(\S[^\n]*)", re.MULTILINE)
_CS_RE = re.compile(
    r"\*\*Customer Satisfaction \(0.5\):\*\*\s*(.*?)(?=\n\*\*|\Z)", re.DOTALL
)
_CD_RE = re.compile(
    r"\*\*Customer Dissatisfaction \(0.5\):\*\*\s*(.*?)(?=\n\*\*|\Z)", re.DOTALL
)
_STATUS_RE = re.compile(r"\*\*Status:\*\*\s*\n(\S[^\n]*)", re.MULTILINE)
_PRIORITY_RE = re.compile(r"\*\*Priority:\*\*\s*\n(\S[^\n]*)", re.MULTILINE)
_SCORE_BULLET_RE = re.compile(r"^\s*-\s*(\d)", re.MULTILINE)
_SCORE_PLAIN_RE = re.compile(r"^\s*(\d)\s*$", re.MULTILINE)

# Anchors used when inserting absent bold fields
_DEPS_BLOCK_RE = re.compile(
    r"(\*\*Dependencies / Conflicts:\*\*\s*\n\S[^\n]*)", re.MULTILINE
)
_STATUS_BLOCK_RE = re.compile(
    r"(\*\*Status:\*\*\s*\n\S[^\n]*)", re.MULTILINE
)
_HISTORY_RE = re.compile(r"(\*\*History:\*\*)", re.MULTILINE)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load(path: Path) -> Requirement:
    """Read a REQ-*.md file and return a populated Requirement.

    Args:
        path: Absolute path to a ``REQ-*.md`` file.

    Returns:
        A :class:`~models.Requirement` instance.  The ``status``,
        ``priority``, and ``title`` attributes are ``None`` when those
        fields are absent in the source file.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If CS or CD scores cannot be parsed from the file.

    """
    text = path.read_text(encoding="utf-8")

    id_match = _ID_RE.search(text)
    req_id = id_match.group(1) if id_match else path.stem

    cs_match = _CS_RE.search(text)
    cd_match = _CD_RE.search(text)

    cs = _extract_score(cs_match.group(1)) if cs_match else None
    cd = _extract_score(cd_match.group(1)) if cd_match else None

    if cs is None or cd is None:
        raise ValueError(
            f"Could not parse CS or CD scores from '{path.name}'. "
            "Ensure the file follows the standard REQ template."
        )

    status_match = _STATUS_RE.search(text)
    priority_match = _PRIORITY_RE.search(text)
    type_match = _TYPE_RE.search(text)

    # Title is the text of the first ``# Heading`` in the file.
    title_match = _TITLE_HEADING_RE.search(text)
    title = title_match.group(1).strip() if title_match else None

    return Requirement(
        req_id=req_id,
        cs=cs,
        cd=cd,
        status=status_match.group(1).strip() if status_match else None,
        priority=priority_match.group(1).strip() if priority_match else None,
        source_path=path,
        raw_text=text,
        req_type=type_match.group(1).strip() if type_match else None,
        title=title,
    )


def save(
    req: Requirement,
    *,
    status: str | None = None,
    priority: str | None = None,
    title: str | None = None,
) -> None:
    """Write updated field values back to the requirement's source file.

    Only fields explicitly passed as keyword arguments are written.  Fields
    that are already present in the file are updated in place; absent fields
    are inserted at the appropriate position (see module docstring).

    Args:
        req:      The requirement to update.  ``req.source_path`` must be
                  writable.
        status:   New value for the ``Status`` field, or ``None`` to skip.
        priority: New value for the ``Priority`` field, or ``None`` to skip.
        title:    New value for the leading ``# Title`` heading, or ``None``
                  to skip.  When provided and the heading is already present
                  it is replaced in place; when absent it is prepended to the
                  file.

    """
    text = req.raw_text

    if title is not None:
        text = _upsert_title(text, title)

    if status is not None:
        text = _upsert_field(text, "Status", status)

    if priority is not None:
        text = _upsert_field(text, "Priority", priority)

    req.source_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _upsert_title(text: str, title: str) -> str:
    """Replace an existing ``# Title`` heading or prepend a new one.

    Args:
        text:  Full content of a REQ file.
        title: New title string (must not start with ``#``).

    Returns:
        Updated file content with the heading at the top.

    """
    if _TITLE_HEADING_RE.search(text):
        # Replace the first heading line in place.
        return _TITLE_HEADING_RE.sub(f"# {title}", text, count=1)
    # No heading present: prepend it followed by a blank line.
    return f"# {title}\n\n{text.lstrip()}"


def _extract_score(block: str) -> int | None:
    """Extract a single integer score from a CS/CD field value block.

    Handles both bulleted format (``- 4: description``) and plain integer
    format (``4`` on its own line).

    Args:
        block: Raw text of the field value as captured by the regex.

    Returns:
        Integer score, or ``None`` if no digit could be found.

    """
    match = _SCORE_BULLET_RE.search(block)
    if match:
        return int(match.group(1))
    match = _SCORE_PLAIN_RE.search(block)
    if match:
        return int(match.group(1))
    return None


def _upsert_field(text: str, field: str, value: str) -> str:
    """Update an existing field or insert a new one at the correct position.

    Args:
        text:  Full content of a REQ file.
        field: Field name exactly as it appears between ``**`` markers,
               e.g. ``"Status"`` or ``"Priority"``.
        value: New field value (single line).

    Returns:
        Updated file content as a string.

    """
    existing = re.compile(
        rf"(\*\*{re.escape(field)}:\*\*\s*\n)(\S[^\n]*)", re.MULTILINE
    )
    if existing.search(text):
        return existing.sub(rf"\g<1>{value}", text)

    # Field is absent: insert at the appropriate anchor.
    if field == "Priority":
        if _STATUS_BLOCK_RE.search(text):
            return _STATUS_BLOCK_RE.sub(
                r"\1" + f"\n\n**Priority:**\n{value}", text, count=1
            )
        if _DEPS_BLOCK_RE.search(text):
            return _DEPS_BLOCK_RE.sub(
                r"\1" + f"\n\n**Priority:**\n{value}", text, count=1
            )

    if field == "Status":
        if _DEPS_BLOCK_RE.search(text):
            return _DEPS_BLOCK_RE.sub(
                r"\1" + f"\n\n**Status:**\n{value}", text, count=1
            )

    # Fallback: insert immediately before **History:**.
    if _HISTORY_RE.search(text):
        return _HISTORY_RE.sub(
            f"**{field}:**\n{value}\n\n" + r"\1", text, count=1
        )

    # Last resort: append to end of file.
    return text + f"\n\n**{field}:**\n{value}\n"
