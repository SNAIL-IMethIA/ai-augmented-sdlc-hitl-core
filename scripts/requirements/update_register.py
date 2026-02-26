"""update_register.py: Full README requirements register rebuild.

Scans all REQ-*.md files in a requirements directory, parses their
metadata, and regenerates the complete requirements table and the
"Total requirements:" count in the project README.md.

The REQ files are the authoritative source for all columns: ID, Type, CS,
CD, Status, Priority, and Title.  Title is read from the leading ``# Title``
heading in each REQ file.  When a file does not yet have a title heading,
the value is read from the existing README table as a migration fallback;
once the heading is present in the file, the README is no longer consulted.

Usage (run from the repository root):
    python -m scripts.requirements.update_register [OPTIONS]

    --req-dir PATH   Directory containing REQ-*.md files.
                     Default: requirements/project1
    --readme PATH    Path to the README.md register to update.
                     Default: requirements/project1/README.md
    --dry-run        Print the generated table without writing any files.

See Also:
    scripts/requirements/README.md     : overview and usage guide.
    scripts/requirements/parser.py     : REQ file parsing.
    scripts/requirements/assign_priority.py : priority computation.

"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import parser as req_parser
from .models import Requirement

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Matches the "Total requirements:" metadata line (legacy, kept for backward compat).
_TOTAL_RE = re.compile(r"(\*\*Total requirements:\*\*\s*)\d+")

# Matches the full metrics block delimited by HTML comments.
_METRICS_BLOCK_RE = re.compile(
    r"<!-- metrics:start -->.*?<!-- metrics:end -->",
    re.DOTALL,
)

# Matches a markdown table header or data row (starts with a pipe).
_TABLE_ROW_RE = re.compile(r"^\|")

# Matches a table separator row (e.g. |----|---|).
_SEPARATOR_ROW_RE = re.compile(r"^\|[-| ]+\|$")

# Matches a data row whose first cell is a REQ-NN identifier.
_DATA_ROW_RE = re.compile(r"^\|\s*REQ-\d+")


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def _compute_metrics(reqs: list) -> dict:
    """Compute summary metrics from a list of Requirement instances.

    Returns a dict with keys:
        total, must, should, could, wont,
        functional, non_functional, constraint, interface, environmental,
        other_type,
        draft, reviewed, approved, deprecated, other_status,
        avg_cs, avg_cd.
    """
    counts: dict = dict(
        total=len(reqs),
        must=0, should=0, could=0, wont=0,
        functional=0, non_functional=0, constraint=0,
        interface=0, environmental=0, other_type=0,
        draft=0, reviewed=0, approved=0, deprecated=0, other_status=0,
    )

    for r in reqs:
        # Priority
        p = (r.priority or "").strip().lower()
        if p == "must":
            counts["must"] += 1
        elif p == "should":
            counts["should"] += 1
        elif p == "could":
            counts["could"] += 1
        elif p in ("won't", "wont", "won\u2019t"):
            counts["wont"] += 1

        # Type
        t = (r.req_type or "").strip().lower()
        if t == "functional":
            counts["functional"] += 1
        elif t in ("non-functional", "non_functional"):
            counts["non_functional"] += 1
        elif t == "constraint":
            counts["constraint"] += 1
        elif t == "interface":
            counts["interface"] += 1
        elif t == "environmental":
            counts["environmental"] += 1
        else:
            counts["other_type"] += 1

        # Status
        s = (r.status or "").strip().lower()
        if s == "draft":
            counts["draft"] += 1
        elif s == "reviewed":
            counts["reviewed"] += 1
        elif s == "approved":
            counts["approved"] += 1
        elif s == "deprecated":
            counts["deprecated"] += 1
        else:
            counts["other_status"] += 1


    return counts


def _build_metrics_block(m: dict) -> str:
    """Return the full metrics block string including HTML comment delimiters.

    Three pure-Markdown tables are stacked vertically, each preceded by a
    level-3 section header. No inline HTML is used (markdownlint-compliant).
    """
    total = m["total"]
    lines = [
        "<!-- metrics:start -->",
        "",
        "## Metrics",
        "",
        "### Priority",
        "",
        "| Priority | Count |",
        "| -------- | ----: |",
        f"| Must | {m['must']} |",
        f"| Should | {m['should']} |",
        f"| Could | {m['could']} |",
        f"| Won't | {m['wont']} |",
        f"| **Total** | **{total}** |",
        "",
        "### Type",
        "",
        "| Type | Count |",
        "| ---- | ----: |",
        f"| Functional | {m['functional']} |",
        f"| Non-functional | {m['non_functional']} |",
        f"| Constraint | {m['constraint']} |",
        f"| Interface | {m['interface']} |",
        f"| Environmental | {m['environmental']} |",
        f"| **Total** | **{total}** |",
        "",
        "### Status",
        "",
        "| Status | Count |",
        "| ------ | ----: |",
        f"| Draft | {m['draft']} |",
        f"| Reviewed | {m['reviewed']} |",
        f"| Approved | {m['approved']} |",
        f"| Deprecated | {m['deprecated']} |",
        f"| **Total** | **{total}** |",
        "",
        "<!-- metrics:end -->",
    ]
    return "\n".join(lines)

def _replace_metrics_in_text(text: str, new_block: str) -> str:
    """Replace the <!-- metrics:start/end --> block with *new_block*.

    Falls back to replacing the legacy ``**Total requirements:** N`` line
    if no delimited block is found.
    """
    if _METRICS_BLOCK_RE.search(text):
        return _METRICS_BLOCK_RE.sub(new_block, text)

    # Legacy fallback: replace the bare **Total requirements:** line
    if _TOTAL_RE.search(text):
        return _TOTAL_RE.sub(new_block, text)

    return text


def _create_readme(readme_path: Path, req_dir: Path) -> None:
    """Create a minimal README.md from a template when none exists.

    The project name is derived from the requirement directory's folder name.

    Args:
        readme_path: Destination path for the new README.
        req_dir:     Directory containing the REQ files (used to derive name).
    """
    project_name = req_dir.name
    nl = "\n"
    lines = [
        f"# Requirements Register: {project_name}",
        "",
        f"This folder contains the requirements for **{project_name}**.",
        "",
        "Each requirement is documented in its own file following the Volere-inspired "
        "template defined in [`protocol/requirements.md`](../../protocol/requirements.md). "
        "This README serves as the central register and entry point for all requirements "
        "in this project.",
        "",
        "<!-- metrics:start -->",
        "",
        "## Metrics",
        "",
        "### Priority",
        "",
        "| Priority | Count |",
        "| -------- | ----: |",
        "| Must | 0 |",
        "| Should | 0 |",
        "| Could | 0 |",
        "| Won\u2019t | 0 |",
        "| **Total** | **0** |",
        "",
        "### Type",
        "",
        "| Type | Count |",
        "| ---- | ----: |",
        "| Functional | 0 |",
        "| Non-functional | 0 |",
        "| Constraint | 0 |",
        "| Interface | 0 |",
        "| Environmental | 0 |",
        "| **Total** | **0** |",
        "",
        "### Status",
        "",
        "| Status | Count |",
        "| ------ | ----: |",
        "| Draft | 0 |",
        "| Reviewed | 0 |",
        "| Approved | 0 |",
        "| Deprecated | 0 |",
        "| **Total** | **0** |",
        "",
        "<!-- metrics:end -->",
        "",
        "## Requirements",
        "",
        "| ID | Title | Type | CS | CD | Status | Priority | File |",
        "| -- | ----- | ---- | -- | -- | ------ | -------- | ---- |",
        "",
    ]
    readme_path.write_text(nl.join(lines), encoding="utf-8")
    print(f"[INFO] Created README: {readme_path}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_titles_from_readme(readme_path: Path) -> dict[str, str]:
    """Return a mapping of REQ-ID → title from the existing README table.

    Used only as a migration fallback for REQ files that do not yet carry a
    ``# Title`` heading.  Once a file has the heading, ``parser.load`` will
    populate ``Requirement.title`` directly and this lookup is not consulted.

    Args:
        readme_path: Path to the README.md file to read.

    Returns:
        Dict mapping e.g. ``"REQ-01"`` → ``"Parallel strategy creation"``.
        Empty dict when the file does not exist or has no matching rows.

    """
    if not readme_path.exists():
        return {}

    titles: dict[str, str] = {}
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not _DATA_ROW_RE.match(stripped):
            continue
        # Split on "|" and grab the first two non-empty cells (ID, Title).
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 2 and cells[0]:
            titles[cells[0]] = cells[1]

    return titles


def _build_table(reqs: list[Requirement], fallback_titles: dict[str, str]) -> str:
    """Return the full markdown requirements table as a string.

    Titles are sourced from ``req.title`` (the ``# Heading`` in each REQ
    file).  When that is absent, ``fallback_titles`` (read from the existing
    README) is consulted for backward compatibility during migration.

    The Priority column is included whenever any requirement carries a
    non-None priority value.

    Args:
        reqs:            List of :class:`~models.Requirement` instances, in
                         display order.
        fallback_titles: Mapping of REQ-ID → title string used when
                         ``req.title`` is ``None``.

    Returns:
        Markdown table string without a trailing newline.

    """
    has_priority = any(r.priority is not None for r in reqs)

    if has_priority:
        header = "| ID | Title | Type | CS | CD | Status | Priority | File |"
        sep    = "| -- | ----- | ---- | -- | -- | ------ | -------- | ---- |"
    else:
        header = "| ID | Title | Type | CS | CD | Status | File |"
        sep    = "| -- | ----- | ---- | -- | -- | ------ | ---- |"

    rows = [header, sep]

    for req in reqs:
        rid      = req.req_id
        # Title: read from the file's # heading; fall back to the README
        # register for files that have not yet been given a heading.
        title    = req.title or fallback_titles.get(rid, "")
        rtype    = req.req_type if req.req_type else "Functional"
        cs       = req.cs
        cd       = req.cd
        status   = req.status if req.status else "Draft"
        priority = req.priority if req.priority else ""
        link     = f"[{rid}.md]({rid}.md)"

        if has_priority:
            rows.append(
                f"| {rid} | {title} | {rtype} | {cs} | {cd} "
                f"| {status} | {priority} | {link} |"
            )
        else:
            rows.append(
                f"| {rid} | {title} | {rtype} | {cs} | {cd} "
                f"| {status} | {link} |"
            )

    return "\n".join(rows)


def _replace_table_in_text(text: str, new_table: str) -> str:
    """Locate the requirements table in *text* and replace it with *new_table*.

    The table is identified as a contiguous block of pipe-delimited rows that
    includes a header row containing both ``ID`` and ``Title``.  The
    replacement preserves the surrounding markdown structure (headings, blank
    lines, horizontal rules, etc.).

    Args:
        text:      Full content of the README file.
        new_table: Replacement table string (no trailing newline).

    Returns:
        Updated file content.  If no table is found, the original text is
        returned unchanged.

    """
    lines = text.splitlines(keepends=True)
    new_lines: list[str] = []
    i = 0

    while i < len(lines):
        raw    = lines[i]
        stripped = raw.rstrip("\n").strip()

        # Detect the requirements table header row.
        if (
            _TABLE_ROW_RE.match(stripped)
            and "| ID |" in stripped
            and "| Title |" in stripped
        ):
            # Consume the entire table block (header + separator + data rows).
            while i < len(lines):
                cur = lines[i].rstrip("\n").strip()
                if _TABLE_ROW_RE.match(cur) or _SEPARATOR_ROW_RE.match(cur):
                    i += 1
                else:
                    break

            # Emit the replacement table followed by a single newline.
            new_lines.append(new_table + "\n")
            continue  # do not advance i again; the outer loop will

        new_lines.append(raw)
        i += 1

    return "".join(new_lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def update(readme_path: Path, req_dir: Path, *, dry_run: bool = False) -> int:
    """Rebuild the register table and update the total count in README.md.

    Steps performed:
        1. Scan *req_dir* for ``REQ-*.md`` files and parse each one.
        2. Read titles from the existing README table (titles are not stored
           in individual REQ files).
        3. Regenerate the complete table, including a Priority column when
           any requirement carries a priority value.
        4. Update the ``**Total requirements:** N`` metadata line.
        5. Write the result back to *readme_path* (unless ``dry_run``).

    Args:
        readme_path: Path to the ``README.md`` file to update.
        req_dir:     Directory containing ``REQ-*.md`` files.
        dry_run:     When True, print the generated table to stdout without
                     modifying any files.

    Returns:
        Number of requirements successfully processed (i.e. table row count).

    """
    req_files = sorted(req_dir.glob("REQ-*.md"))
    reqs: list[Requirement] = []
    skipped: list[str] = []

    for path in req_files:
        try:
            reqs.append(req_parser.load(path))
        except ValueError as exc:
            print(f"  [SKIP] {path.name}: {exc}", file=sys.stderr)
            skipped.append(path.name)

    if not reqs:
        print(
            f"[WARN] No parseable REQ-*.md files found in {req_dir}.",
            file=sys.stderr,
        )
        return 0

    titles    = _parse_titles_from_readme(readme_path)
    new_table = _build_table(reqs, titles)
    metrics   = _compute_metrics(reqs)
    new_block = _build_metrics_block(metrics)
    total     = metrics["total"]

    if skipped:
        print(
            f"[WARN] {len(skipped)} file(s) skipped due to parse errors: "
            + ", ".join(skipped),
            file=sys.stderr,
        )

    if dry_run:
        print(f"\n--- Generated metrics block ({total} requirements) ---\n")
        print(new_block)
        print(f"\n--- Generated table ({total} requirements) ---\n")
        print(new_table)
        print("\n[DRY RUN] README not modified.")
        return total

    # Auto-create README if it does not exist.
    if not readme_path.exists():
        _create_readme(readme_path, req_dir)

    text = readme_path.read_text(encoding="utf-8")

    # Replace the metrics block (handles both new delimited block and legacy line).
    text = _replace_metrics_in_text(text, new_block)

    # Replace the requirements table block.
    text = _replace_table_in_text(text, new_table)

    readme_path.write_text(text, encoding="utf-8")
    print(f"Register updated: {total} requirements written to {readme_path}")

    return total


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="update_register",
        description="Rebuild the README requirements register table from REQ-*.md files.",
    )
    p.add_argument(
        "--req-dir",
        default="requirements/project1",
        metavar="PATH",
        help="Directory containing REQ-*.md files (default: requirements/project1).",
    )
    p.add_argument(
        "--readme",
        default="requirements/project1/README.md",
        metavar="PATH",
        help="README.md register to update (default: requirements/project1/README.md).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated table without writing any files.",
    )
    return p.parse_args()


def main() -> None:
    """Parse CLI arguments and run the register update."""
    args = _parse_args()
    update(
        readme_path=Path(args.readme),
        req_dir=Path(args.req_dir),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
