"""diff_summary.py: Summarize file changes and artifact ownership since a commit."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

_ARTIFACT_PATH_RE = re.compile(r"^artifacts/phase\d+/([^/]+)")


def _run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _latest_run_id(db_path: Path) -> str | None:
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT id FROM runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return str(row[0])
    finally:
        conn.close()


def _changed_files(repo: Path, since: str) -> list[str]:
    output = _run_git(repo, ["diff", "--name-only", f"{since}..HEAD"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _author_counts(repo: Path, since: str) -> dict[str, int]:
    output = _run_git(repo, ["log", "--pretty=%an", f"{since}..HEAD"])
    if not output:
        return {}
    counter = Counter(line.strip() for line in output.splitlines() if line.strip())
    return dict(counter)


def _artifact_ids_from_paths(paths: list[str]) -> set[str]:
    artifact_ids: set[str] = set()
    for path in paths:
        match = _ARTIFACT_PATH_RE.match(path)
        if not match:
            continue
        base = match.group(1)
        artifact_ids.add(base.split(".")[0])
    return artifact_ids


def _artifact_classification(
    db_path: Path,
    run_id: str,
    artifact_ids: set[str],
) -> dict[str, str]:
    if not artifact_ids:
        return {}

    conn = sqlite3.connect(db_path)
    try:
        placeholders = ",".join("?" for _ in artifact_ids)
        params = [run_id, *sorted(artifact_ids)]

        ai_rows = conn.execute(
            f"""
            SELECT artifact_id, MAX(CASE WHEN human_modified = 1 THEN 1 ELSE 0 END)
            FROM interactions
            WHERE run_id = ?
              AND artifact_id IN ({placeholders})
            GROUP BY artifact_id
            """,
            params,
        ).fetchall()

        manual_rows = conn.execute(
            f"""
            SELECT artifact_id, COUNT(*)
            FROM interventions
            WHERE run_id = ?
              AND category = 'manual_edit'
              AND artifact_id IN ({placeholders})
            GROUP BY artifact_id
            """,
            params,
        ).fetchall()

        has_interaction = {str(row[0]): int(row[1]) for row in ai_rows}
        has_manual_edit = {str(row[0]): int(row[1]) for row in manual_rows}

        result: dict[str, str] = {}
        for artifact_id in sorted(artifact_ids):
            human_modified = has_interaction.get(artifact_id, 0) == 1
            manual_edit_count = has_manual_edit.get(artifact_id, 0)
            if human_modified or manual_edit_count > 0:
                result[artifact_id] = "human-modified"
            elif artifact_id in has_interaction:
                result[artifact_id] = "ai-originated"
            else:
                result[artifact_id] = "unknown"
        return result
    finally:
        conn.close()


def _summary(repo: Path, db_path: Path, since: str) -> dict[str, Any]:
    files = _changed_files(repo, since)
    run_id = _latest_run_id(db_path)
    artifact_ids = _artifact_ids_from_paths(files)

    classifications: dict[str, str] = {}
    if run_id is not None:
        classifications = _artifact_classification(db_path, run_id, artifact_ids)

    classified_files = [
        path
        for path in files
        if _ARTIFACT_PATH_RE.match(path)
    ]
    unlinked_files = [path for path in files if path not in classified_files]

    return {
        "since": since,
        "repo": repo.as_posix(),
        "db": db_path.as_posix(),
        "latest_run_id": run_id,
        "changed_files": files,
        "changed_file_count": len(files),
        "artifact_classification": classifications,
        "authors": _author_counts(repo, since),
        "unlinked_files": unlinked_files,
    }


def _print_human(summary: dict[str, Any]) -> None:
    print(f"since: {summary['since']}")
    print(f"changed_file_count: {summary['changed_file_count']}")
    print(f"latest_run_id: {summary['latest_run_id']}")
    print(f"authors: {summary['authors']}")
    print("artifact_classification:")
    for artifact_id, status in summary["artifact_classification"].items():
        print(f"  {artifact_id}: {status}")
    if summary["unlinked_files"]:
        print("unlinked_files:")
        for path in summary["unlinked_files"]:
            print(f"  {path}")


def main() -> None:
    """Parse CLI arguments and print a change attribution summary."""
    parser = argparse.ArgumentParser(
        description="Summarize git changes since a commit and map artifact ownership."
    )
    parser.add_argument("--since", required=True, help="Commit SHA to diff from.")
    parser.add_argument("--repo", default=".", help="Repository path.")
    parser.add_argument("--db", default="logs/experiment.db", help="Path to experiment DB.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    summary = _summary(Path(args.repo), Path(args.db), args.since)
    if args.json:
        print(json.dumps(summary, indent=2))
        return
    _print_human(summary)


if __name__ == "__main__":
    main()
