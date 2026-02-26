# Backtest time estimation

**ID:** REQ-30

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall display an estimated completion time to the user before or at the start of any backtest run.

**Rationale:**
Time estimates help users decide whether to proceed immediately or schedule long-running backtests, and prevent the system from appearing frozen during execution.

**Fit Criterion:**

- A time estimate is displayed within 5 seconds of initiating a backtest run.
- The actual backtest duration does not exceed 3× the displayed estimate under normal operating conditions.

**Customer Satisfaction (0–5):**

- 3: Provides useful feedback during operation and improves perceived responsiveness.

**Customer Dissatisfaction (0–5):**

- 2: Without an estimate, users uncertain of wait time may abandon runs unnecessarily.

**Dependencies / Conflicts:**
REQ-29

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
