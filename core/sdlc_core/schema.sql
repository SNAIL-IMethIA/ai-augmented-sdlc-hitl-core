-- Canonical schema for the AI-Augmented SDLC experiment database.
-- One database file per approach × project run.
-- Applied by sdlc_core.db.setup_db().
--
-- Foreign key enforcement must be enabled at connection time:
--   PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- runs
-- One row per approach × project execution.
-- Opened before Phase 2 begins; closed when the run terminates.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS runs (
    id              TEXT    PRIMARY KEY,   -- e.g. "run-proj1-approach2-20260310"
    project         TEXT    NOT NULL,      -- e.g. "project1"
    approach        INTEGER NOT NULL CHECK (approach IN (1, 2)),
    started_at      TEXT    NOT NULL,      -- ISO 8601
    ended_at        TEXT,                  -- ISO 8601; NULL while in progress
    terminal_phase  INTEGER CHECK (terminal_phase BETWEEN 2 AND 8)
);

-- ---------------------------------------------------------------------------
-- sessions
-- One row per working session (day) within a run.
-- A completed run has exactly 3 session rows.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT    NOT NULL REFERENCES runs (id),
    session_number  INTEGER NOT NULL CHECK (session_number IN (1, 2, 3)),
    started_at      TEXT    NOT NULL,      -- ISO 8601
    ended_at        TEXT,                  -- ISO 8601; NULL while session is open
    UNIQUE (run_id, session_number)
);

-- ---------------------------------------------------------------------------
-- phase_progress
-- One row per SDLC phase per run. Updated as work proceeds.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS phase_progress (
    run_id          TEXT    NOT NULL REFERENCES runs (id),
    phase_number    INTEGER NOT NULL CHECK (phase_number BETWEEN 2 AND 8),
    status          TEXT    NOT NULL CHECK (status IN (
                        'not_started', 'in_progress', 'completed', 'partially_reached'
                    )),
    entered_at      TEXT,                  -- ISO 8601; NULL if not yet started
    completed_at    TEXT,                  -- ISO 8601; NULL if not yet complete
    PRIMARY KEY (run_id, phase_number)
);

-- ---------------------------------------------------------------------------
-- artifacts
-- One row per accepted SDLC artifact.
-- Artifacts that are never accepted do not appear here; rejection is
-- captured in interactions via outcome = 'rejected'.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS artifacts (
    id              TEXT    NOT NULL,      -- e.g. "ARCH-VIEW-01"
    run_id          TEXT    NOT NULL REFERENCES runs (id),
    artifact_type   TEXT    NOT NULL,      -- e.g. "architecture_note"
    phase           INTEGER NOT NULL CHECK (phase BETWEEN 1 AND 8),
    git_commit_sha  TEXT,                  -- NULL until committed
    content_hash    TEXT,                  -- SHA-256 of artifact content
    status          TEXT    NOT NULL CHECK (status IN ('draft', 'accepted', 'superseded')),
    created_at      TEXT    NOT NULL,      -- ISO 8601
    PRIMARY KEY (id, run_id)
);

-- ---------------------------------------------------------------------------
-- interactions
-- One row per prompt–response exchange (human-initiated or agent-to-agent).
-- Primary log table; main source for effort, iteration, and modification
-- metrics.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interactions (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                      TEXT    NOT NULL REFERENCES runs (id),
    artifact_id                 TEXT,      -- NULL for exploratory prompts
    timestamp                   TEXT    NOT NULL,  -- ISO 8601
    sdlc_phase                  INTEGER NOT NULL CHECK (sdlc_phase BETWEEN 2 AND 8),
    approach                    INTEGER NOT NULL CHECK (approach IN (1, 2)),
    agent_role                  TEXT    NOT NULL,
    model                       TEXT    NOT NULL,
    prompt                      TEXT    NOT NULL,
    response                    TEXT    NOT NULL,
    iteration                   INTEGER NOT NULL CHECK (iteration >= 1),
    outcome                     TEXT    NOT NULL CHECK (outcome IN (
                                    'accepted', 'accepted_with_modifications', 'rejected'
                                )),
    human_modified              INTEGER NOT NULL CHECK (human_modified IN (0, 1)),
    human_modification_notes    TEXT,      -- required when human_modified = 1
    duration_seconds            INTEGER,   -- AI response latency only
    human_review_seconds        INTEGER,   -- time from response display to outcome entry
    prompt_tokens               INTEGER,   -- token count of the submitted prompt
    completion_tokens           INTEGER,   -- token count of the model response
    FOREIGN KEY (artifact_id, run_id) REFERENCES artifacts (id, run_id),
    CHECK (
        (human_modified = 0 AND human_modification_notes IS NULL) OR
        (human_modified = 1 AND human_modification_notes IS NOT NULL)
    )
);

-- ---------------------------------------------------------------------------
-- interventions
-- One row per human action taken outside an AI interaction.
-- Covers manual edits, acceptance decisions, environment fixes, etc.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interventions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT    NOT NULL REFERENCES runs (id),
    artifact_id         TEXT,              -- NULL for run-level interventions
    timestamp           TEXT    NOT NULL,  -- ISO 8601
    sdlc_phase          INTEGER NOT NULL CHECK (sdlc_phase BETWEEN 2 AND 8),
    category            TEXT    NOT NULL CHECK (category IN (
                            'clarification', 'correction', 'rejection',
                            'strategic_decision', 'safety_override',
                            'manual_edit', 'environment_fix', 'other'
                        )),
    severity            TEXT    NOT NULL CHECK (severity IN ('minor', 'moderate', 'critical')),
    rationale           TEXT    NOT NULL,
    time_spent_minutes  INTEGER NOT NULL CHECK (time_spent_minutes >= 0),
    FOREIGN KEY (artifact_id, run_id) REFERENCES artifacts (id, run_id)
);

-- ---------------------------------------------------------------------------
-- traceability_links
-- One row per directed link between two artifacts.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS traceability_links (
    from_artifact_id    TEXT    NOT NULL,
    to_artifact_id      TEXT    NOT NULL,
    run_id              TEXT    NOT NULL REFERENCES runs (id),
    link_type           TEXT    NOT NULL DEFAULT 'traces_to',
    created_at          TEXT    NOT NULL,  -- ISO 8601
    PRIMARY KEY (from_artifact_id, to_artifact_id, run_id),
    FOREIGN KEY (from_artifact_id, run_id) REFERENCES artifacts (id, run_id),
    FOREIGN KEY (to_artifact_id,   run_id) REFERENCES artifacts (id, run_id)
);

-- ---------------------------------------------------------------------------
-- validation_results
-- One row per formal validation or verification session.
-- Individual defects are in the defects table.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS validation_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id     TEXT,                  -- NULL for system-wide sessions
    run_id          TEXT    NOT NULL REFERENCES runs (id),
    sdlc_phase      INTEGER NOT NULL CHECK (sdlc_phase BETWEEN 2 AND 8),
    validation_type TEXT    NOT NULL CHECK (validation_type IN (
                        'testing', 'demonstration', 'review', 'acceptance_test'
                    )),
    result          TEXT    NOT NULL CHECK (result IN ('accepted', 'rejected', 'conditional')),
    defects_found   INTEGER NOT NULL CHECK (defects_found >= 0),
    notes           TEXT,
    timestamp       TEXT    NOT NULL,      -- ISO 8601
    FOREIGN KEY (artifact_id, run_id) REFERENCES artifacts (id, run_id)
);

-- ---------------------------------------------------------------------------
-- defects
-- One row per individual defect detected during a validation session.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS defects (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                  TEXT    NOT NULL REFERENCES runs (id),
    validation_result_id    INTEGER NOT NULL REFERENCES validation_results (id),
    artifact_id             TEXT,          -- NULL if not attributable to one artifact
    sdlc_phase_detected     INTEGER NOT NULL CHECK (sdlc_phase_detected BETWEEN 2 AND 8),
    origin_phase            INTEGER CHECK (origin_phase BETWEEN 2 AND 8),
    severity                TEXT    NOT NULL CHECK (severity IN ('minor', 'moderate', 'critical')),
    description             TEXT    NOT NULL,
    detected_at             TEXT    NOT NULL,  -- ISO 8601
    resolved_at             TEXT               -- ISO 8601; NULL if still open
);

-- ---------------------------------------------------------------------------
-- pipeline_events
-- Approach 2 only.
-- One row per control-flow event during an autonomous pipeline execution.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pipeline_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      TEXT    NOT NULL REFERENCES runs (id),
    pipeline_id TEXT    NOT NULL,          -- e.g. "PIPE-run-proj1-approach2-20260310-01"
    timestamp   TEXT    NOT NULL,          -- ISO 8601
    step        TEXT    NOT NULL,
    agent_role  TEXT    NOT NULL,
    event_type  TEXT    NOT NULL CHECK (event_type IN (
                    'gate_pass', 'gate_fail', 'retry', 'circuit_break',
                    'reentry_approval', 'halt', 'resume'
                )),
    artifact_id TEXT,
    detail      TEXT    NOT NULL
);

-- ---------------------------------------------------------------------------
-- violations
-- One row per integrity or semantic failure detected during a run.
-- Written automatically by write helpers on constraint failure, and by
-- check.py for semantic violations.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS violations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT,                  -- NULL if run could not be resolved
    artifact_id     TEXT,                  -- NULL for run-level or pre-artifact violations
    violation_type  TEXT    NOT NULL CHECK (violation_type IN (
                        'missing_required_field', 'foreign_key_failure',
                        'schema_constraint_failure', 'traceability_gap',
                        'requirement_coverage_gap', 'prompt_structure_violation',
                        'fit_criterion_failure', 'other'
                    )),
    detail          TEXT    NOT NULL,
    timestamp       TEXT    NOT NULL       -- ISO 8601
);
