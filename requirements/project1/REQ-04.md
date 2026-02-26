# Strategy scope (one asset, one venue)

**ID:** REQ-04

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall enforce that each strategy operates on exactly one asset and one exchange venue.

**Rationale:**
Restricting a strategy to a single asset and venue ensures deterministic data flow, simplifies risk attribution, and prevents accidental cross-contamination of trading signals.

**Fit Criterion:**

- A strategy configuration accepts only one asset and one exchange as input.
- Attempting to assign more than one asset or exchange to a single strategy is rejected with a clear error message.

**Customer Satisfaction (0–5):**

- 4: Enforces clean strategy boundaries and simplifies reasoning about performance.

**Customer Dissatisfaction (0–5):**

- 4: Without this constraint, strategies may produce ambiguous or incorrect results.

**Dependencies / Conflicts:**
REQ-02, REQ-03

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
