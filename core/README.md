# sdlc_core: Shared Experiment Runtime Library

This package is the shared runtime library for the AI-Augmented SDLC research experiment.
It is installed as a dependency in every approach template repository.

---

## Modules

| Module | Purpose |
| --- | --- |
| `sdlc_core.db` | Schema creation and all write helpers for `experiment.db` |
| `sdlc_core.enums` | Controlled vocabularies as Python enums |
| `sdlc_core.check` | Semantic integrity checker (run at phase close and run end) |
| `sdlc_core.metrics` | Metric query runner; produces `logs/metrics_report.json` |
| `sdlc_core.session` | `Session` dataclass: active run context and per-artifact iteration counter |
| `sdlc_core.providers.logged` | `LoggedProvider`: timing, outcome capture, and DB logging around any provider |

---

## Session and LoggedProvider

`Session` carries the active run context so that callers do not repeat `run_id`,
`approach`, `active_phase`, and `db_path` on every call:

```python
from sdlc_core import Session

session = Session(
    run_id="run-001",
    approach=1,
    active_phase=2,
    db_path=Path("logs/experiment.db"),
)
session.set_phase(3)
iteration = session.next_iteration("REQ-DOC-01")  # returns 1 on first call
```

`LoggedProvider` wraps any `ModelProvider`. On every `complete()` call it times
the underlying request, prints the response, prompts the researcher for an
outcome (`[A]ccept / [R]eject / [M]odified`) and optional modification notes,
then writes a complete row to `interactions` via `sdlc_core.db.log_interaction()`.
Every exchange is captured automatically; the only manual input is the
three-value outcome judgment:

```python
from sdlc_core.providers import LoggedProvider
from sdlc_core.providers.ollama import OllamaProvider

base = OllamaProvider(model_id="llama3.2")
provider = LoggedProvider(provider=base, session=session)

response = provider.complete(prompt="Draft the requirements document.")
```

---

## Installation in a template repo

Add to `requirements.txt` (replace `{COMMIT_SHA}` with the pinned commit):

```git
sdlc-core @ git+https://github.com/SNAIL-IMethIA/ai-augmented-sdlc-hitl-core.git@{COMMIT_SHA}#subdirectory=core
```

Also write the same SHA to `core_version.txt` in the template root and commit it before
the run begins. This file must not be modified during or after the run.

---

## Setup (run once per clone, before the run begins)

```bash
pip install -r requirements.txt
python setup.py
```

`setup.py` calls `sdlc_core.db.setup_db("logs/experiment.db")`, which creates the database
with the full schema. The resulting empty `logs/experiment.db` must be committed before any
experiment work begins.

---

## Usage during a run

```python
from sdlc_core.db import open_run, open_session, log_interaction, accept_artifact, close_session, close_run

run_id = open_run(project="project1", approach=2)
open_session(run_id=run_id, session_number=1)

log_interaction(
    run_id=run_id,
    artifact_id="ARCH-VIEW-01",
    sdlc_phase=3,
    approach=2,
    agent_role="architect",
    model="gpt-4o-2024-11-20",
    prompt="...",
    response="...",
    iteration=1,
    outcome="accepted",
    human_modified=False,
    duration_seconds=14,
)

accept_artifact(
    run_id=run_id,
    artifact_id="ARCH-VIEW-01",
    artifact_type="architecture_note",
    phase=3,
    git_commit_sha="abc123",
    upstream_ids=["REQ-01", "REQ-02"],
)

close_session(run_id=run_id, session_number=1)
close_run(run_id=run_id, terminal_phase=3)
```

---

## Integrity check (run at phase close and run end)

```bash
python -m sdlc_core.check --db logs/experiment.db
```

Exits with code 0 if all checks pass, code 1 if any fail. Output is printed to stdout and
also written to `logs/check_report.json`.

---

## Metrics report (run at run end)

```bash
python -m sdlc_core.metrics --db logs/experiment.db --out logs/metrics_report.json
```

Produces a JSON report with all metrics defined in `protocol/metrics.md`. Commit this file
as part of the run-end commit.
