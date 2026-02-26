# Strategy execution isolation

**ID:** REQ-11

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall execute each strategy in isolation such that the runtime state of one strategy does not affect the execution or results of any other strategy.

**Rationale:**
Cross-contamination between strategies would produce incorrect signals or results, undermining the reliability of all backtest and live trading outputs.

**Fit Criterion:**

- Running Strategy A and Strategy B concurrently produces results that are numerically identical to running each strategy in isolation under the same conditions.
- No shared mutable state exists between strategy execution contexts.

**Customer Satisfaction (0–5):**

- 5: Correctness guarantee; required for results to be trustworthy.

**Customer Dissatisfaction (0–5):**

- 5: Contaminated results could cause incorrect trading decisions and financial loss.

**Dependencies / Conflicts:**
REQ-01

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
