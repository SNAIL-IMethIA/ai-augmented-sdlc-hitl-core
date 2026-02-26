# Run result history per session and preset

**ID:** REQ-61

**Type:** Functional

**Originator:** Kevin Schweitzer

**Description:**
The system shall maintain a persistent history of all completed backtest and optimisation results, associated with their corresponding named preset and work session, accessible for review and comparison at any time.

**Rationale:**
Users iterating on strategies need to track how results evolve across runs within a session and across sessions for the same preset. Without result history, intermediate improvements are lost and users cannot determine whether a new configuration is genuinely better than a previous one.

**Fit Criterion:**

- All completed backtest and optimisation results are automatically stored and linked to their corresponding preset ID and session identifier.
- A user can view the full result history for any named preset from within the application, ordered by date and time.
- The history persists across application restarts without data loss.
- At least 50 historical result entries per preset are retained.
- Individual historical results can be selected and compared side by side with the current result.

**Customer Satisfaction (0–5):**

- 4: Directly supports iterative strategy refinement; users find value in seeing improvement over time.

**Customer Dissatisfaction (0–5):**

- 4: Without result history, comparing runs requires manual note-taking and intermediate results are irrecoverably lost.

**Dependencies / Conflicts:**
REQ-09, REQ-31, REQ-41

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-26 | Kevin Schweitzer | Created | New requirement identified during requirements audit
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
