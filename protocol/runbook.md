# Operator runbook

## Purpose

This runbook defines the standard operator flow for experiment execution. It is the canonical guide for approach repositories after scaffolding.

## Preconditions

- You are in an approach repository created by `sdlc-scaffold`.
- `core_version.txt` is pinned and committed.
- `models.toml`, `run_config.toml`, and `.env` are populated.
- The repository uses the frozen dependency and runtime configuration.

## Pre-run checks

Run the setup gate before any experiment work.

```bash
poetry sync --no-root
poetry run sdlc-setup
poetry run sdlc-status --db logs/experiment.db
```

If setup fails, do not start the run. Fix configuration or connectivity first.

## Daily execution loop

1. Start with the active phase and planned artifact.
2. Execute approach commands for that artifact.
3. Record outcome and human intervention notes as required.
4. Update phase status transitions as they occur.
5. Accept artifacts and commit immediately after acceptance.
6. Check current run state before moving to the next artifact.

```bash
poetry run sdlc-phase-status --phase <2-8> --status in_progress
poetry run sdlc-phase-status --phase <2-8> --status completed
```

```bash
poetry run sdlc-status --db logs/experiment.db
```

## Phase close checks

Run integrity checks at phase close.

```bash
poetry run python -m sdlc_core.check --db logs/experiment.db
```

If check fails, resolve issues before proceeding.

When ending a work block/day boundary, pause with session close:

```bash
poetry run sdlc-pause --close-session
```

## Change attribution since last commit

Use the diff summary command to inspect what changed and whether changes were AI-originated or human-modified.

```bash
poetry run sdlc-diff-summary --since <commit_sha> --repo . --db logs/experiment.db
```

For machine-readable output, add `--json`.

## Run close

At run end, generate final metrics and verify integrity.

```bash
poetry run python -m sdlc_core.check --db logs/experiment.db
poetry run python -m sdlc_core.metrics --db logs/experiment.db --out logs/metrics_report.json
poetry run sdlc-status --db logs/experiment.db
```

Commit all run artifacts and reports in the run-end commit.
