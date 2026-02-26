"""renumber.py: Gap-free sequential renumbering of REQ-*.md files.

Scans a directory of REQ-*.md files, detects gaps or inconsistent padding
in the numeric sequence, and reassigns compact sequential IDs starting from
REQ-01.  Padding width is computed dynamically from the total requirement
count so that the scheme scales naturally as requirements are added or
removed.

After renaming the files the script rewrites the **ID:** field and the
**Dependencies / Conflicts:** field inside every file so that cross-
references remain consistent.

Safety:
    Renaming is performed in two atomic phases to prevent collisions:

        Phase 1: every file is renamed to a temporary name
                  (``REQ-TEMP-<index>.md``) that cannot clash with any
                  current or target name.
        Phase 2: every temporary file is renamed to its final target name.

    If ``--dry-run`` is given, no files are modified and the planned changes
    are printed instead.

Usage (run from the repository root):
    python -m scripts.requirements.renumber [OPTIONS]

    --req-dir PATH   Directory containing REQ-*.md files.
                     Default: requirements/project1
    --readme PATH    Path to the README.md register to update.
                     Default: requirements/project1/README.md
    --dry-run        Print planned renames without writing any files.

See Also:
    scripts/requirements/README.md    : overview and usage guide.
    scripts/requirements/main.py      : pipeline orchestrator (--renumber).
    scripts/requirements/parser.py    : REQ file reading / writing.

"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Matches an isolated REQ-NN token (word boundary on both sides).
_REQ_ID_RE = re.compile(r"\bREQ-(\d+)\b")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_id_map(req_files: list[Path]) -> dict[str, str]:
    """Return a mapping of old REQ IDs to new sequential IDs.

    The new IDs are assigned in ascending order of the existing numeric
    component.  Padding width equals ``len(str(total))`` so the scheme
    scales to any collection size without manual adjustment.

    Args:
        req_files: All ``REQ-*.md`` paths in the directory, in any order.

    Returns:
        Dict mapping e.g. ``"REQ-59"`` → ``"REQ-58"``.  Only entries where
        the ID actually changes are included; IDs that stay the same are
        omitted to keep the result concise.

    """
    # Parse each file name → (numeric_value, stem_string).
    numbered: list[tuple[int, str]] = []
    for path in req_files:
        m = re.match(r"REQ-(\d+)$", path.stem, re.IGNORECASE)
        if m:
            numbered.append((int(m.group(1)), path.stem))

    numbered.sort(key=lambda t: t[0])
    total = len(numbered)
    if total == 0:
        return {}

    pad = len(str(total))

    id_map: dict[str, str] = {}
    for new_num, (_, old_id) in enumerate(numbered, start=1):
        new_id = f"REQ-{new_num:0{pad}d}"
        if old_id != new_id:
            id_map[old_id] = new_id

    return id_map


def _rewrite_ids_in_text(text: str, id_map: dict[str, str]) -> str:
    """Replace every old REQ-NN token in *text* with its new ID.

    Uses whole-word matching so that ``REQ-1`` is not accidentally
    substituted inside ``REQ-10``.

    Args:
        text:   Raw file content.
        id_map: Mapping of old ID → new ID.

    Returns:
        Updated file content.

    """
    if not id_map:
        return text

    def replacer(match: re.Match[str]) -> str:
        full: str = match.group(0)      # e.g. "REQ-59"
        return id_map.get(full, full)   # swap or pass through unchanged

    return _REQ_ID_RE.sub(replacer, text)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run(
    req_dir: Path,
    readme_path: Path,
    *,
    dry_run: bool = False,
) -> dict[str, str]:
    """Renumber all REQ-*.md files in *req_dir* to fill sequence gaps.

    Steps performed:
        1. Scan *req_dir* for ``REQ-*.md`` files and build an old→new ID map.
        2. Rewrite the text of every file that needs updating (``**ID:**``
           and ``**Dependencies / Conflicts:**`` fields).
        3. Rename files in two phases to avoid name collisions.

    Args:
        req_dir:     Directory containing ``REQ-*.md`` files.
        readme_path: Path to the ``README.md`` register (currently unused
                     during renumber; the caller's pipeline runs
                     ``update_register`` afterwards to rebuild the table).
        dry_run:     When True, print planned changes without modifying any
                     files.

    Returns:
        The old→new ID mapping that was applied (empty when no gaps exist).

    Raises:
        SystemExit: If *req_dir* does not exist or contains no REQ files.

    """
    if not req_dir.exists():
        print(f"[ERROR] Directory not found: {req_dir}", file=sys.stderr)
        sys.exit(1)

    req_files = sorted(req_dir.glob("REQ-*.md"))
    if not req_files:
        print(f"[ERROR] No REQ-*.md files found in {req_dir}.", file=sys.stderr)
        sys.exit(1)

    id_map = _build_id_map(req_files)

    if not id_map:
        print(
            f"\nNo gaps or padding inconsistencies found in {len(req_files)} "
            "requirement(s). Nothing to renumber."
        )
        return {}

    # Determine padding from total count.
    pad = len(str(len(req_files)))

    print(f"\nFound {len(id_map)} ID(s) to renumber (pad={pad}):")
    for old, new in sorted(id_map.items(), key=lambda t: int(t[0].split("-")[1])):
        print(f"  {old}  →  {new}")

    if dry_run:
        print("\n[DRY RUN] No files were modified.")
        return id_map

    # -----------------------------------------------------------------------
    # Phase 1: rewrite file content for ALL files (even those whose own ID
    # does not change, since their Dependencies / Conflicts may reference IDs
    # that do change).
    # -----------------------------------------------------------------------
    print("\nRewriting file content…")
    for path in req_files:
        text = path.read_text(encoding="utf-8")
        new_text = _rewrite_ids_in_text(text, id_map)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")

    # -----------------------------------------------------------------------
    # Phase 2a: rename files that need a new name → temporary names, so that
    # a direct rename (e.g. REQ-59→REQ-58) never overwrites an existing file.
    # -----------------------------------------------------------------------
    temp_map: dict[Path, Path] = {}   # temp_path → final_path
    files_to_rename = {
        path: req_dir / f"{id_map[path.stem]}.md"
        for path in req_files
        if path.stem in id_map
    }

    print("Renaming files… (phase 1: to temp names)")
    for old_path, new_path in files_to_rename.items():
        temp_path = req_dir / f"REQ-TEMP-{old_path.stem}.md"
        old_path.rename(temp_path)
        temp_map[temp_path] = new_path

    # -----------------------------------------------------------------------
    # Phase 2b: rename temporary files to their final names.
    # -----------------------------------------------------------------------
    print("Renaming files… (phase 2: to final names)")
    for temp_path, final_path in temp_map.items():
        temp_path.rename(final_path)

    print(
        f"\nRenumber complete: {len(id_map)} file(s) renamed, "
        f"{len(req_files) - len(id_map)} unchanged."
    )
    return id_map


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="renumber",
        description=(
            "Renumber REQ-*.md files to fill sequence gaps, "
            "updating IDs and dependency references."
        ),
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
        help="README.md register path (default: requirements/project1/README.md).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned renames without writing any files.",
    )
    return p.parse_args()


def main() -> None:
    """Parse command-line arguments and run the renumber pipeline."""
    args = _parse_args()
    run(
        req_dir=Path(args.req_dir),
        readme_path=Path(args.readme),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
