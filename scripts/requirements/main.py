"""main.py: Requirements processing pipeline orchestrator.

Runs the full requirements processing pipeline in the correct order:

    Step 0: renumber (on by default, skip with --skip-renumber)
        Detects gaps or inconsistent padding in the REQ-NN sequence and
        reassigns compact sequential IDs.  Rewrites the **ID:** and
        **Dependencies / Conflicts:** fields in every affected file, then
        renames the files atomically in two phases to avoid collisions.
        Padding width is computed from the total requirement count so the
        scheme scales to any collection size.  When the sequence is already
        gap-free this step is a no-op and completes instantly.

    Step 1: validate (optional, on by default)
        Checks every REQ-*.md file for structural compliance with the
        Volere template: title heading present, all mandatory fields present,
        correct ID/filename match, valid vocabulary for Type/Status/Priority,
        CS/CD in [0, 5].

    Step 2: assign_priority
        Reads every REQ-*.md file, derives the MoSCoW priority label from
        its CS and CD scores using the rule defined in moscow.py, and writes
        the Priority (and Status if absent) field back into each file.

    Step 3: update_register
        Rebuilds the complete requirements table and metrics block in the
        project README.md from the REQ files.  Metrics cover total count,
        MoSCoW breakdown, type breakdown, status breakdown, and avg CS/CD.
        If no README.md exists in the target directory it is created
        automatically from a standard template.

Running this script is the single command needed to fully synchronise the
requirements register after any change to REQ-*.md files.

Usage (run from the repository root):
    python -m scripts.requirements.main [OPTIONS]

    By default, every sub-directory under ``requirements/`` that contains
    at least one REQ-*.md file is discovered and processed automatically.
    Supply --req-dir to target a single project instead.

    --req-dir PATH       Target a single project directory.
                         Default: auto-discover all projects under --req-root.
    --readme PATH        README.md to update (only with --req-dir).
                         Default: <req-dir>/README.md.
    --req-root PATH      Root directory for auto-discovery.
                         Default: requirements
    --dry-run            Print results without writing any files.
    --skip-renumber      Skip Step 0 (gap-filling renumber).
    --skip-validate      Skip Step 1 (template validation).
    --strict-validate    Abort the pipeline if any REQ file fails validation.
    --skip-priority      Skip Step 2 (priority assignment).
    --skip-register      Skip Step 3 (register rebuild).

Examples:
    # Process all projects (default)
    python -m scripts.requirements.main

    # Process a single project
    python -m scripts.requirements.main --req-dir requirements/project1

See Also:
    scripts/requirements/renumber.py        : Step 0 logic.
    scripts/requirements/validate.py        : Step 1 logic.
    scripts/requirements/assign_priority.py : Step 2 logic.
    scripts/requirements/update_register.py : Step 3 logic.
    scripts/requirements/README.md          : full usage guide.

"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import assign_priority, renumber, update_register, validate

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="main",
        description=(
            "Requirements processing pipeline: optional renumber → validate "
            "→ MoSCoW priority assignment → README register rebuild."
        ),
    )
    p.add_argument(
        "--req-dir",
        default=None,
        metavar="PATH",
        help=(
            "Directory containing REQ-*.md files for a single project. "
            "When omitted, every sub-directory under --req-root that "
            "contains at least one REQ-*.md file is processed automatically."
        ),
    )
    p.add_argument(
        "--readme",
        default=None,
        metavar="PATH",
        help=(
            "README.md register to update. Only relevant when --req-dir is "
            "also supplied; defaults to <req-dir>/README.md."
        ),
    )
    p.add_argument(
        "--req-root",
        default="requirements",
        metavar="PATH",
        help=(
            "Root directory searched for project sub-folders when --req-dir "
            "is not given (default: requirements)."
        ),
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print results without writing any files.",
    )
    p.add_argument(
        "--skip-renumber",
        action="store_true",
        help="Skip Step 0 (gap-filling renumber); useful when IDs are already sequential.",
    )
    p.add_argument(
        "--skip-priority",
        action="store_true",
        help="Skip Step 2 (priority assignment).",
    )
    p.add_argument(
        "--skip-register",
        action="store_true",
        help="Skip Step 3 (register rebuild).",
    )
    p.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip Step 1 (template validation).",
    )
    p.add_argument(
        "--strict-validate",
        action="store_true",
        help="Abort the pipeline if any REQ file fails template validation.",
    )
    return p.parse_args()



def run(
    req_dir: Path,
    readme_path: Path,
    *,
    dry_run: bool = False,
    skip_renumber: bool = False,
    skip_priority: bool = False,
    skip_register: bool = False,
    skip_validate: bool = False,
    strict_validate: bool = False,
) -> None:
    """Execute the full requirements processing pipeline.

    Args:
        req_dir:          Directory containing REQ-*.md files.
        readme_path:      Path to the README.md register to update.
        dry_run:          When True, print results without modifying files.
        skip_renumber:    When True, skip Step 0 (gap-filling renumber).
        skip_priority:    When True, skip Step 2 (priority assignment).
        skip_register:    When True, skip Step 3 (register rebuild).
        skip_validate:    When True, skip Step 1 (template validation).
        strict_validate:  When True, abort if any file fails validation.

    Raises:
        SystemExit: If req_dir is missing, or on validation failure in
                    strict mode.

    """
    if not req_dir.exists():
        print(f"[ERROR] Requirements directory not found: {req_dir}", file=sys.stderr)
        sys.exit(1)

    active_steps = (
        [("Step 0", "Renumbering REQ files")] * int(not skip_renumber)
        + [("Step 1", "Validating REQ files")] * int(not skip_validate)
        + [("Step 2", "Assigning MoSCoW priorities")] * int(not skip_priority)
        + [("Step 3", "Rebuilding README requirements register")] * int(not skip_register)
    )
    total_steps = len(active_steps)
    current_step = 0

    # ------------------------------------------------------------------
    # Step 0: Renumber REQ files to fill sequence gaps
    # ------------------------------------------------------------------
    if not skip_renumber:
        current_step += 1
        _print_step_banner(current_step, total_steps, "Renumbering REQ files")

        renumber.run(
            req_dir=req_dir,
            readme_path=readme_path,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # Step 1: Validate REQ files against the Volere template
    # ------------------------------------------------------------------
    if not skip_validate:
        current_step += 1
        _print_step_banner(current_step, total_steps, "Validating REQ files")

        _, errors = validate.validate_dir(req_dir, strict=strict_validate)
        if errors and not strict_validate:
            print(
                f"  [WARN] {errors} file(s) have template violations; "
                "run with --strict-validate to abort on errors.",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # Step 2: Assign MoSCoW priorities to individual REQ files
    # ------------------------------------------------------------------
    if not skip_priority:
        current_step += 1
        _print_step_banner(current_step, total_steps, "Assigning MoSCoW priorities")

        assign_priority.run(
            req_dir=req_dir,
            readme_path=readme_path,
            dry_run=dry_run,
            # The register rebuild in Step 3 will handle the README table;
            # skip the partial Priority-column-only update here to avoid
            # writing a half-formed table that Step 3 immediately overwrites.
            update_readme=skip_register,
        )

    # ------------------------------------------------------------------
    # Step 3: Rebuild the full README requirements register
    # ------------------------------------------------------------------
    if not skip_register:
        current_step += 1
        _print_step_banner(current_step, total_steps, "Rebuilding README requirements register")

        total = update_register.update(
            readme_path=readme_path,
            req_dir=req_dir,
            dry_run=dry_run,
        )
        print(f"\nRegister contains {total} requirements.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    if dry_run:
        print("[DRY RUN] No files were modified.")
    else:
        print("Pipeline complete.")


# ---------------------------------------------------------------------------
# Title-seeding helper
# ---------------------------------------------------------------------------

def _print_step_banner(step: int, total: int, description: str) -> None:
    """Print a formatted step banner to stdout."""
    border = "=" * 60
    print(f"\n{border}")
    print(f"  Step {step} of {total}: {description}")
    print(f"{border}")


def main() -> None:
    """Parse command-line arguments and run the pipeline."""
    args = _parse_args()

    if args.req_dir is not None:
        # Single-project mode: user explicitly specified a directory.
        readme = Path(args.readme) if args.readme else Path(args.req_dir) / "README.md"
        run(
            req_dir=Path(args.req_dir),
            readme_path=readme,
            dry_run=args.dry_run,
            skip_renumber=args.skip_renumber,
            skip_priority=args.skip_priority,
            skip_register=args.skip_register,
            skip_validate=args.skip_validate,
            strict_validate=args.strict_validate,
        )
    else:
        # Default: auto-discover every project folder under req_root.
        req_root = Path(args.req_root)
        if not req_root.exists():
            print(f"[ERROR] Requirements root not found: {req_root}", file=sys.stderr)
            sys.exit(1)

        project_dirs = sorted(
            d for d in req_root.iterdir()
            if d.is_dir() and any(d.glob("REQ-*.md"))
        )

        if not project_dirs:
            print(f"[WARN] No project directories with REQ-*.md files found under {req_root}.")
            return

        print(f"Discovered {len(project_dirs)} project(s): {', '.join(d.name for d in project_dirs)}\n")

        for project_dir in project_dirs:
            readme = project_dir / "README.md"
            print(f"{'=' * 60}")
            print(f"  Project: {project_dir.name}")
            print(f"{'=' * 60}")
            run(
                req_dir=project_dir,
                readme_path=readme,
                dry_run=args.dry_run,
                skip_renumber=args.skip_renumber,
                skip_priority=args.skip_priority,
                skip_register=args.skip_register,
                skip_validate=args.skip_validate,
                strict_validate=args.strict_validate,
            )
            print()


if __name__ == "__main__":
    main()

