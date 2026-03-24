# Experiment logging

## Table of Contents

1. [Purpose](#purpose)
2. [Storage model](#storage-model)
3. [Integrity model](#integrity-model)
4. [Tables](#tables)
   - [runs](#runs)
   - [sessions](#sessions)
   - [phase\_progress](#phase_progress)
   - [artifacts](#artifacts)
   - [interactions](#interactions)
   - [interventions](#interventions)
   - [traceability\_links](#traceability_links)
   - [validation\_results](#validation_results)
   - [defects](#defects)
   - [pipeline\_events](#pipeline_events)
   - [violations](#violations)
5. [Metrics queries](#metrics-queries)

---

## Purpose

All experiment data is captured in a single structured relational database. This includes prompt interactions, human interventions, traceability links, validation results, and pipeline events. Using a relational database rather than flat log files is a deliberate design decision, as it enforces referential integrity between records at write time, making structural omissions immediately detectable rather than silently absent. A log entry that references a non-existent artifact is itself a recorded violation, not a gap in the data.

The database is the ground truth for all metrics defined in [metrics.md](metrics.md). Metrics are computed at analysis time as queries over the raw tables. No metric is stored as a pre-computed value.

---

## Storage model

Each template repository (one per approach × project run) holds its own `logs/experiment.db` file. The database is created before the run begins by running `python setup.py` in the template repo, which calls `sdlc_core.db.setup_db()` from the shared core library. The empty schema file is committed to version control at that point and constitutes the verifiable start state of the run.

The database grows exclusively during the run. At run end, `python -m sdlc_core.metrics` is run to produce `logs/metrics_report.json`, which is also committed. Cross-run aggregation is performed separately in the core repository's `analysis/` folder after all runs are complete, by reading each repo's `metrics_report.json`.

Every table includes a `run_id` column that links records back to the single run this database covers. The `runs` table will therefore contain exactly one row at the conclusion of a normal run.

---

## Integrity model

The database enforces the following integrity rules:

- **Foreign keys.** Every `run_id` must reference an existing row in `runs`. Every non-null `artifact_id` in `interactions`, `interventions`, `traceability_links`, `validation_results`, and `defects` must reference an existing row in `artifacts` for the same run.
- **Enumerated fields.** All fields that accept a controlled vocabulary (`outcome`, `category`, `violation_type`, `status`, event types, etc.) are constrained to their declared value sets. A value outside the set is rejected at write time.
- **Conditional requirements.** `human_modification_notes` is required when `human_modified` is `true`; the constraint is enforced by the database and cannot be bypassed.
- **Traceability link integrity.** Every non-null `from_artifact_id` and `to_artifact_id` in `traceability_links` must each reference an existing row in `artifacts` for the same run.
- **Defect count consistency.** The `defects_found` integer in every `validation_results` row must equal the number of rows in `defects` whose `validation_result_id` references that row. A mismatch is detected by checker scripts and recorded as a violation.

When a write is rejected due to any of the above, the rejection is itself recorded as a row in the `violations` table with the timestamp and a description of what failed. Integrity failures are data, not lost information.

---

## Tables

### runs

One row per approach × project execution. A run spans Phases 2–8 or until the 24-hour budget is exhausted. The run record is opened before Phase 2 begins and closed when the run terminates.

| Field | Type | Description |
| --- | --- | --- |
| `id` | text, primary key | Unique run identifier, e.g. `run-proj1-approach2-20250610` |
| `project` | text | Project identifier, e.g. `project1` |
| `approach` | integer | Approach number: 1, 2, 3, or 4 |
| `started_at` | text | ISO 8601 timestamp when the run began |
| `ended_at` | text | ISO 8601 timestamp when the run ended; null while in progress |
| `terminal_phase` | integer | The last SDLC phase reached (2–8); null while in progress |

---

### sessions

One row per working session within a run. A run is structured as three working days of eight hours each; each session represents one of those days. Session records are the verifiable evidence that no active work occurred outside the declared session windows. They are opened at the start of each day of work and closed at the end.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `run_id` | text | Foreign key to `runs.id` |
| `session_number` | integer | Ordinal index of the session within the run: 1, 2, or 3 |
| `started_at` | text | ISO 8601 timestamp when this session began |
| `ended_at` | text | ISO 8601 timestamp when this session ended; null while in progress |

A run has exactly three session rows at conclusion. The absence of a third row or an `ended_at` that is null at the time of analysis is itself a protocol deviation, recorded in the `violations` table.

---

### phase_progress

One row per phase per run. Updated as work proceeds through the V-model.

| Field | Type | Description |
| --- | --- | --- |
| `run_id` | text | Foreign key to `runs.id` |
| `phase_number` | integer | SDLC phase number (2–8) |
| `status` | text | One of: `not_started`, `in_progress`, `completed`, `partially_reached` |
| `entered_at` | text | ISO 8601 timestamp when the phase began; null if not yet started |
| `completed_at` | text | ISO 8601 timestamp when the phase ended; null if not yet complete |

---

### artifacts

One row per accepted SDLC artifact produced during a run. An artifact that is never accepted (all iterations rejected) does not appear here; rejection is captured in `interactions` via `outcome = rejected`.

| Field | Type | Description |
| --- | --- | --- |
| `id` | text | Artifact identifier, e.g. `ARCH-01`, `IMPL-03` |
| `run_id` | text | Foreign key to `runs.id` |
| `artifact_type` | text | Artifact type, e.g. `architecture_note`, `test_case`, `implementation_unit` |
| `phase` | integer | SDLC phase in which the artifact was produced (2–8) |
| `git_commit_sha` | text | SHA of the git commit in which the artifact was accepted; null until committed |
| `content_hash` | text | SHA-256 of the artifact content (see note below) |
| `status` | text | One of: `draft`, `accepted`, `superseded` |
| `created_at` | text | ISO 8601 timestamp |

**`content_hash` computation.** For single-file artifacts, `content_hash` is the SHA-256 of the committed file content as stored in the repository. For artifacts that span multiple files (for example, an implementation unit with a separate source file and test file), `content_hash` is computed as the SHA-256 of the canonical directory tree: the hash input is the sorted concatenation of strings of the form `[relative_path]:[file_sha256]`, one per file under the artifact's directory, sorted lexicographically by relative path. This rule ensures that the hash is deterministic regardless of file system order and that any change to any constituent file invalidates the stored hash.

---

### interactions

One row per prompt–response exchange, whether human-initiated or agent-to-agent. This is the primary log table and the main source for effort, iteration, governance, and modification metrics.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `run_id` | text | Foreign key to `runs.id` |
| `artifact_id` | text | Artifact produced or updated; null for exploratory prompts before artifact creation |
| `timestamp` | text | ISO 8601 |
| `sdlc_phase` | integer | SDLC phase (2–8) |
| `approach` | integer | Approach number (1–4) |
| `agent_role` | text | Declared role of the AI, e.g. `architect`, `reviewer` |
| `model` | text | Model name and version |
| `prompt` | text | Full prompt content, unredacted |
| `response` | text | Full raw AI response, unredacted |
| `iteration` | integer | Refinement iteration index, starting at 1 for each artifact |
| `outcome` | text | One of: `accepted`, `accepted_with_modifications`, `rejected` |
| `human_modified` | boolean | `true` if the accepted output differs from the raw AI response in any way |
| `human_modification_notes` | text | Required when `human_modified` is `true`; the authoritative account of what was changed manually and why. `null` otherwise. |
| `duration_seconds` | integer | Elapsed time from prompt submission to response receipt |

---

### interventions

One row per human action taken outside an AI interaction. This includes manual edits made without prompting an AI, acceptance decisions, fit-criterion checks, environment fixes, and any other deviation from the automated path.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `run_id` | text | Foreign key to `runs.id` |
| `artifact_id` | text | Artifact involved, if applicable; null for run-level interventions |
| `timestamp` | text | ISO 8601 |
| `sdlc_phase` | integer | SDLC phase in which the intervention occurred (2–8) |
| `category` | text | One of: `clarification`, `correction`, `rejection`, `strategic_decision`, `safety_override`, `manual_edit`, `environment_fix`, `other` |
| `severity` | text | One of: `minor`, `moderate`, `critical` |
| `rationale` | text | Free-text description of why the intervention was necessary |
| `time_spent_minutes` | integer | Time spent on the intervention |

---

### traceability_links

One row per directed traceability link between two artifacts. Links are asserted by the participant when an artifact is produced; gaps detected at analysis time are recorded as violations.

| Field | Type | Description |
| --- | --- | --- |
| `from_artifact_id` | text | Source artifact, e.g. `REQ-03` |
| `to_artifact_id` | text | Target artifact, e.g. `ARCH-01` |
| `run_id` | text | Foreign key to `runs.id` |
| `link_type` | text | Default: `traces_to` |
| `created_at` | text | ISO 8601 |

---

### validation_results

One row per formal validation or verification session (Phases 6–8). This covers verification test sessions, client demonstration or review sessions, and deployment acceptance tests. Records the session outcome and a total defect count; individual defect detail (severity, origin phase, resolution timestamp) is stored in the `defects` table, which references this row.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `artifact_id` | text | Artifact under validation; null when the session covers the system as a whole rather than a single artifact (e.g. a system-wide acceptance test) |
| `run_id` | text | Foreign key to `runs.id` |
| `sdlc_phase` | integer | SDLC phase in which the validation occurred (2–8) |
| `validation_type` | text | One of: `testing`, `demonstration`, `review`, `acceptance_test` |
| `result` | text | One of: `accepted`, `rejected`, `conditional` |
| `defects_found` | integer | Count of defects identified during the session; must equal the number of rows in `defects` that reference this `validation_results.id` |
| `notes` | text | Free-text session-level observations. Individual defect records (description, severity, origin phase, resolution timestamp) are logged as separate rows in the `defects` table referencing this `validation_results.id`. Do not record defect detail in this field. |
| `timestamp` | text | ISO 8601 |

---

### defects

One row per individual defect detected during a validation or verification session. The `defects_found` count in `validation_results` is a summary; this table holds the per-defect records that enable defect resolution time and defect-origin mapping to be computed as database queries.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `run_id` | text | Foreign key to `runs.id` |
| `validation_result_id` | integer | Foreign key to `validation_results.id` in which this defect was detected |
| `artifact_id` | text | Artifact in which the defect was found; null if the defect cannot be attributed to a single artifact |
| `sdlc_phase_detected` | integer | SDLC phase in which the defect was detected |
| `origin_phase` | integer | SDLC phase in which the defect is believed to have been introduced; null until assessed by the researcher |
| `severity` | text | One of: `minor`, `moderate`, `critical` |
| `description` | text | Free-text description of the defect |
| `detected_at` | text | ISO 8601 timestamp of detection (must equal the `timestamp` of the referenced `validation_results` row) |
| `resolved_at` | text | ISO 8601 timestamp when the defect was resolved; null if still open |

Defect resolution time is computed as the interval between `detected_at` and `resolved_at`. Error propagation depth is computed as `sdlc_phase_detected` minus `origin_phase`. Both computations are database queries over this table; neither requires external tooling.

---

### pipeline_events

Applies to Approach 2 only. One row per control-flow event generated during an autonomous pipeline execution. These records complement the interaction log and are the primary data source for pipeline autonomy metrics and error propagation analysis.

**`pipeline_id` format and scope.** A `pipeline_id` identifies the specific version of the pipeline contract governing an execution. Format: `PIPE-[RUN_ID]-[NN]`, where `NN` is a two-digit sequential index starting at `01` for the first pipeline execution within a run. A single run may produce multiple pipeline executions (for example, one per SDLC phase in Approach 2), each assigned a distinct `pipeline_id` while sharing the same `run_id`. The pipeline contract itself is a versioned document that specifies the step graph, gate criteria, retry limits, and circuit-breaker conditions for the execution. If the contract is revised mid-run, the revised version receives a new `NN` value.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `run_id` | text | Foreign key to `runs.id` |
| `pipeline_id` | text | Identifier of the pipeline contract governing this execution |
| `timestamp` | text | ISO 8601 |
| `step` | text | The pipeline step identifier at which the event occurred |
| `agent_role` | text | The agent role active at the time of the event |
| `event_type` | text | One of: `gate_pass`, `gate_fail`, `retry`, `circuit_break`, `reentry_approval`, `halt`, `resume` |
| `artifact_id` | text | Artifact involved, if applicable; null otherwise |
| `detail` | text | Structured description: the gate criterion that failed, the retry count, the circuit breaker trigger condition, or the approver identity for a re-entry approval |

---

### violations

One row per integrity or semantic failure detected during a run. Violations are the mechanism by which failures become data rather than invisible gaps.

Two kinds of violations are recorded:

- **Structural violations** are written automatically when a database write is rejected due to a constraint failure (foreign key, missing required field, value outside enumerated set).
- **Semantic violations** are written by checker scripts when a structural write succeeds but the content is analytically incomplete. Examples include an AI response that does not reference all requirements it was asked to address, or an accepted artifact that is missing a required traceability link.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer, autoincrement | Primary key |
| `run_id` | text | Null if the run itself could not be resolved |
| `artifact_id` | text | Null for run-level or pre-artifact violations |
| `violation_type` | text | One of: `missing_required_field`, `foreign_key_failure`, `schema_constraint_failure`, `traceability_gap`, `requirement_coverage_gap`, `prompt_structure_violation`, `fit_criterion_failure`, `other` |
| `detail` | text | Free-text description of the failure |
| `timestamp` | text | ISO 8601 |

---

## Metrics queries

All metrics defined in [metrics.md](metrics.md) are computed at analysis time as queries over the raw tables above. The table below maps each metric section to its primary data source.

Metrics sourced entirely from external tooling output are not derived from this database. These cover code coverage, complexity, architectural completeness, and static analysis. Their data is produced by analysis toolchains and stored as structured fields in the relevant artifact files.

| Metric (as named in metrics.md) | Primary source table(s) |
| --- | --- |
| Phase reach rate | `phase_progress`, `runs` |
| Traceability | `traceability_links`, `artifacts` |
| Governance rules | `violations` |
| Human effort | `interventions` |
| Time effort | `interactions`, `interventions` |
| Defects | `validation_results`, `defects` |
| Prompt refinements | `interactions` |
| Requirements coverage | `traceability_links`, `artifacts`, `violations` |
| Defect-origin mappings | `defects`, `artifacts`, `phase_progress` |
| Deployment rate and client acceptance ratio | `validation_results` (client acceptance ratio); TRANS artifact files in version control (attempt count, automation level, time to accepted deployment; these are structured fields in TRANS artifacts, not pre-computed metrics); `pipeline_events` (Approach 2 pipeline-level telemetry) |

No metric is stored as a pre-computed value. The raw tables are the ground truth.
