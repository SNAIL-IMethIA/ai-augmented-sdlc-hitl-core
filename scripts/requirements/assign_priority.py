"""assign_priority.py: CLI entry point for MoSCoW priority assignment.

Scans a directory of REQ-*.md files, computes the MoSCoW priority for each
requirement from its CS and CD scores, writes the result back into the
individual files, and updates the Priority column in the README register.

Usage:
    python -m scripts.requirements.assign_priority [OPTIONS]

    --req-dir PATH   Directory containing REQ-*.md files.
                     Default: requirements/project1
    --readme PATH    Path to the README.md register to update.
                     Default: requirements/project1/README.md
    --dry-run        Print computed priorities without writing any files.

See Also:
    scripts/requirements/README.md    : rule definition and full usage guide.
    scripts/requirements/moscow.py    : MoSCoW derivation logic.
    scripts/requirements/parser.py    : REQ file parsing and writing.
    scripts/requirements/register.py  : README register updates.

"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import moscow, parser, register


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="assign_priority",
        description="Assign MoSCoW priority labels to REQ-*.md files from CS/CD scores.",
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
        help="Print computed priorities without writing any files.",
    )
    return p.parse_args()


def run(
    req_dir: Path,
    readme_path: Path,
    *,
    dry_run: bool = False,
    update_readme: bool = True,
) -> dict[str, str]:
    """Run the priority assignment pipeline programmatically.

    Scans ``req_dir`` for REQ-*.md files, computes MoSCoW priorities, writes
    them back into each file (unless ``dry_run`` is True), and optionally
    updates the Priority column in the README register.

    Args:
        req_dir:       Directory containing REQ-*.md files.
        readme_path:   Path to the README.md register.
        dry_run:       When True, print results without modifying any files.
        update_readme: When True (default), update the README Priority column
                       after writing the individual files.  Pass False when an
                       orchestrator will rebuild the whole register separately.

    Returns:
        Mapping of requirement ID → assigned MoSCoW label for every
        successfully processed file.

    Raises:
        SystemExit: If ``req_dir`` does not exist or contains no REQ files.

    """
    if not req_dir.exists():
        print(f"[ERROR] Directory not found: {req_dir}", file=sys.stderr)
        sys.exit(1)

    req_files = sorted(req_dir.glob("REQ-*.md"))
    if not req_files:
        print(f"[ERROR] No REQ-*.md files found in {req_dir}.", file=sys.stderr)
        sys.exit(1)

    priorities: dict[str, str] = {}
    skipped: list[str] = []

    header = f"{'ID':<10}  {'CS':>3}  {'CD':>3}  {'Sum':>5}  {'Priority':<8}  Note"
    print(f"\n{header}")
    print("-" * len(header))

    for path in req_files:
        try:
            req = parser.load(path)
        except ValueError as exc:
            print(f"  [SKIP] {path.name}: {exc}", file=sys.stderr)
            skipped.append(path.name)
            continue

        label = moscow.compute(req.cs, req.cd)
        priorities[req.req_id] = label

        note = "(CD=5 override)" if req.cd == 5 and (req.cs + req.cd) < 8 else ""
        print(
            f"{req.req_id:<10}  {req.cs:>3}  {req.cd:>3}  "
            f"{req.cs + req.cd:>5}  {label:<8}  {note}"
        )

        if not dry_run:
            parser.save(
                req,
                status=req.status if req.status is not None else "Draft",
                priority=label,
            )

    print("-" * len(header))
    print(f"\n{len(priorities)} requirements processed, {len(skipped)} skipped.")

    if dry_run:
        print("\n[DRY RUN] No files were modified.")
        return priorities

    if update_readme:
        print(f"\nUpdating register: {readme_path}")
        register.update(readme_path, priorities)
        print("Done.")

    return priorities


def main() -> None:
    """Parse command-line arguments and run the priority assignment pipeline."""
    args = _parse_args()
    run(
        req_dir=Path(args.req_dir),
        readme_path=Path(args.readme),
        dry_run=args.dry_run,
        update_readme=True,
    )


if __name__ == "__main__":
    main()

