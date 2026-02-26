"""register.py: README.md requirements register updates.

Provides a single public function:

    update(readme_path, priorities)

        Reads the requirements register table in ``README.md`` and adds or
        updates a ``Priority`` column using the supplied mapping.

Table format expected in README.md:

    | ID | Title | Type | CS | CD | Status | Priority | File |
    |----|-------|------|----|----|---------|----|------|
    | REQ-01 | ... | Functional | 4 | 3 | Draft | Should | ... |

If the ``Priority`` column is absent from the header row it is appended
before the final ``|``.  If it is already present, the value in each data
row is replaced in place.

The function is intentionally narrow in scope: it does not parse requirement
files, compute priorities, or modify anything other than the register table.
All business logic lives in :mod:`moscow`; all file parsing lives in
:mod:`parser`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Matches a Priority cell that already exists in a data row.
_PRIORITY_CELL_RE = re.compile(
    r"\|\s*(Must|Should|Could|Won't)\s*\|\s*$"
)

# Matches a table separator row (e.g. ``|---|---|``).
_SEPARATOR_ROW_RE = re.compile(r"\|[-| ]+\|")

# Captures the REQ-NN ID from the first cell of a data row.
_DATA_ROW_ID_RE = re.compile(r"\|\s*(REQ-\d+)\s*\|")


def update(readme_path: Path, priorities: dict[str, str]) -> None:
    """Add or update the Priority column in the README register table.

    The function detects the requirements table by looking for a header row
    that contains both ``| ID |`` and ``| Title |``.  It then processes
    subsequent rows until it encounters a blank line or end of file.

    Args:
        readme_path: Path to the ``README.md`` file containing the register.
        priorities:  Mapping of requirement ID (e.g. ``"REQ-01"``) to its
                     MoSCoW label (e.g. ``"Must"``).

    Note:
        If ``readme_path`` does not exist the function emits a warning to
        ``stderr`` and returns without raising, so the caller's pipeline
        continues uninterrupted.

    """
    if not readme_path.exists():
        print(f"[WARN] README not found: {readme_path}", file=sys.stderr)
        return

    text = readme_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    has_priority_col = "| Priority |" in text or "| Priority|" in text
    in_table = False
    new_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        if "| ID |" in line and "| Title |" in line:
            in_table = True
            new_lines.append(_maybe_append_col(line, "Priority", has_priority_col))
            continue

        if in_table and _SEPARATOR_ROW_RE.match(stripped):
            new_lines.append(_maybe_append_col(line, "----------", has_priority_col))
            continue

        if in_table and stripped.startswith("| REQ-"):
            id_match = _DATA_ROW_ID_RE.match(stripped)
            req_id = id_match.group(1) if id_match else None
            label = priorities.get(req_id, "") if req_id else ""
            new_lines.append(_set_priority_cell(line, label, has_priority_col))
            continue

        if in_table and not stripped:
            in_table = False

        new_lines.append(line)

    readme_path.write_text("".join(new_lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _maybe_append_col(line: str, value: str, already_present: bool) -> str:
    """Append a column cell to a table row if the column does not yet exist.

    Args:
        line:            Raw line from the markdown file, including newline.
        value:           Cell content to append (without pipe characters).
        already_present: Whether the column already exists in the table.

    Returns:
        Updated line string.

    """
    if already_present:
        return line
    line = line.rstrip("\n").rstrip()
    suffix = f" {value} |" if line.endswith("|") else f"| {value} |"
    return line + suffix + "\n"


def _set_priority_cell(line: str, label: str, already_present: bool) -> str:
    """Replace or append the Priority cell value in a data row.

    Args:
        line:            Raw data row line, including newline.
        label:           MoSCoW label to write (e.g. ``"Must"``).
        already_present: Whether the Priority column already exists.

    Returns:
        Updated line string with trailing newline.

    """
    line = line.rstrip("\n").rstrip()
    if already_present:
        line = _PRIORITY_CELL_RE.sub(f"| {label} |", line)
    else:
        suffix = f" {label} |" if line.endswith("|") else f"| {label} |"
        line = line + suffix
    return line + "\n"
