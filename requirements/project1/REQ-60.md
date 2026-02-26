# Pause and background execution for long-running computations

**ID:** REQ-60

**Type:** Functional

**Originator:** Kevin Schweitzer

**Description:**
The system shall allow a user to pause, resume, or move to background any active backtest or optimisation run without terminating it or losing computation progress.

**Rationale:**
Backtests and optimisation runs can take considerable time. Requiring users to remain on the results screen or to cancel and restart if they need to use other parts of the application creates unnecessary friction and wastes compute time. Background execution and pause/resume controls give users full control over when and how compute is consumed.

**Fit Criterion:**

- A running backtest or optimisation can be paused at any point, with all in-progress computation state preserved.
- A paused run can be resumed from the point of interruption without restarting.
- A running or paused computation can be set to background mode, freeing the UI for other tasks while computation continues.
- The user is notified when a background computation completes.
- No progress is lost across pause, resume, or background transitions.

**Customer Satisfaction (0–5):**

- 4: Significantly improves usability during lengthy compute jobs; users appreciate not being blocked.

**Customer Dissatisfaction (0–5):**

- 3: Without this, users must wait idle or cancel and restart long runs, which is frustrating and wasteful.

**Dependencies / Conflicts:**
REQ-29, REQ-30, REQ-32

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-26 | Kevin Schweitzer | Created | New requirement identified during requirements audit
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
