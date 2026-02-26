"""validate.py: Structural integrity checks for REQ-*.md files.

Verifies that every requirement file in a directory conforms to the
Volere-inspired template defined in ``protocol/requirements.md``.

Checks performed on each file:

    1. Title heading is present as the first line (``# Requirement title``).
    2. All mandatory bold fields are present and non-empty.
    3. ``**ID:**`` matches the filename (e.g. REQ-01.md → REQ-01).
    4. ``**Type:**`` is one of the accepted vocabulary.
    5. ``**Status:**`` is one of the accepted lifecycle states.
    6. ``**Priority:**`` is one of the accepted MoSCoW labels.
    7. CS and CD scores are integers in [0, 5].

Public API:

    validate_file(path)     Check a single file; return a list of violations.
    validate_dir(req_dir)   Check every REQ-*.md in a directory; print a
                            report and return (ok_count, error_count).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: tuple[str, ...] = (
    "ID",
    "Type",
    "Originator",
    "Description",
    "Rationale",
    "Fit Criterion",
    "Customer Satisfaction (0–5)",
    "Customer Dissatisfaction (0–5)",
    "Dependencies / Conflicts",
    "Status",
    "Priority",
    "History",
)

VALID_TYPES: frozenset[str] = frozenset(
    {"Functional", "Non-functional", "Non-Functional", "Interface", "Constraint", "Environmental"}
)

VALID_STATUSES: frozenset[str] = frozenset(
    {"Draft", "Reviewed", "Approved", "Deprecated"}
)

VALID_PRIORITIES: frozenset[str] = frozenset(
    {"Must", "Should", "Could", "Won't"}
)

# Matches **Field Name:** followed by a value on the same or next line.
_FIELD_RE = re.compile(r"\*\*([^*]+):\*\*\s*\n?(.*?)(?=\n\*\*|\Z)", re.DOTALL)
_ID_RE = re.compile(r"\*\*ID:\*\*\s*(REQ-\d+)")
_SCORE_RE = re.compile(r"^\s*-\s*(\d)|^\s*(\d)\s*$", re.MULTILINE)
# Matches the leading ``# Title`` heading (first non-blank line must be a h1).
_TITLE_HEADING_RE = re.compile(r"^#\s+\S", re.MULTILINE)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_file(path: Path) -> list[str]:
    """Check a single REQ-*.md file against the template.

    Args:
        path: Path to a ``REQ-*.md`` file.

    Returns:
        List of human-readable violation strings.  Empty list means the
        file is fully compliant.

    """
    text = path.read_text(encoding="utf-8")
    violations: list[str] = []

    # 1. Title heading present and non-empty.
    if not _TITLE_HEADING_RE.search(text):
        violations.append(
            "Missing title heading: file must start with '# Requirement title'"
        )

    # Build a dict of field name → raw value block from the file.
    fields: dict[str, str] = {}
    for m in _FIELD_RE.finditer(text):
        name = m.group(1).strip()
        value = m.group(2).strip()
        fields[name] = value

    # 2. All mandatory fields present and non-empty.
    for field in REQUIRED_FIELDS:
        if field not in fields:
            violations.append(f"Missing field: **{field}:**")
        elif not fields[field]:
            violations.append(f"Empty field: **{field}:**")

    # 3. ID matches filename.
    id_match = _ID_RE.search(text)
    if id_match:
        declared_id = id_match.group(1)
        expected_id = path.stem  # e.g. "REQ-01"
        if declared_id != expected_id:
            violations.append(
                f"ID mismatch: file is '{expected_id}' but **ID:** declares '{declared_id}'"
            )
    # (missing ID already caught by check 2)

    # 4. Type vocabulary.
    if "Type" in fields and fields["Type"] and fields["Type"] not in VALID_TYPES:
        violations.append(
            f"Invalid **Type:** '{fields['Type']}': "
            f"expected one of: {', '.join(sorted(VALID_TYPES))}"
        )

    # 5. Status vocabulary.
    if "Status" in fields and fields["Status"] and fields["Status"] not in VALID_STATUSES:
        violations.append(
            f"Invalid **Status:** '{fields['Status']}': "
            f"expected one of: {', '.join(sorted(VALID_STATUSES))}"
        )

    # 6. Priority vocabulary.
    if "Priority" in fields and fields["Priority"] and fields["Priority"] not in VALID_PRIORITIES:
        violations.append(
            f"Invalid **Priority:** '{fields['Priority']}': "
            f"expected one of: {', '.join(sorted(VALID_PRIORITIES))}"
        )

    # 7. CS and CD scores are integers in [0, 5].
    for score_field in ("Customer Satisfaction (0–5)", "Customer Dissatisfaction (0–5)"):
        if fields.get(score_field):
            score = _extract_score(fields[score_field])
            if score is None:
                violations.append(f"Could not parse integer score from **{score_field}:**")
            elif not 0 <= score <= 5:
                violations.append(
                    f"Score out of range in **{score_field}:** got {score}, expected 0–5"
                )

    return violations


def validate_dir(req_dir: Path, *, strict: bool = False) -> tuple[int, int]:
    """Validate every REQ-*.md file in *req_dir* and print a report.

    Args:
        req_dir: Directory containing ``REQ-*.md`` files.
        strict:  When True, treat any violation as a hard error (non-zero
                 exit via ``sys.exit``).  When False (default), violations
                 are reported as warnings and processing continues.

    Returns:
        ``(ok_count, error_count)``: number of files that passed and
        failed respectively.

    """
    req_files = sorted(req_dir.glob("REQ-*.md"))
    if not req_files:
        print(f"[WARN] No REQ-*.md files found in {req_dir}.", file=sys.stderr)
        return 0, 0

    ok_count = 0
    error_count = 0

    for path in req_files:
        violations = validate_file(path)
        if violations:
            error_count += 1
            print(f"  [FAIL] {path.name}", file=sys.stderr)
            for v in violations:
                print(f"         • {v}", file=sys.stderr)
        else:
            ok_count += 1

    _print_validation_summary(ok_count, error_count, len(req_files))

    if strict and error_count:
        sys.exit(1)

    return ok_count, error_count


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_score(block: str) -> int | None:
    """Extract the first integer score from a CS / CD field value block."""
    match = _SCORE_RE.search(block)
    if match:
        raw = match.group(1) or match.group(2)
        return int(raw)
    return None


def _print_validation_summary(ok: int, errors: int, total: int) -> None:
    label = "OK" if errors == 0 else "FAILED"
    print(f"\n  Validation: {ok}/{total} passed, {errors} failed: {label}")
