# Optimisation comparison window

**ID:** REQ-28

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall display a side-by-side comparison window showing the pre-optimisation and current best-optimised strategy configurations per indicator during an active optimisation run.

**Rationale:**
Seeing the delta between the original and optimised strategy helps users understand which parameters changed and whether the improvement justifies adoption.

**Fit Criterion:**

- The comparison window is accessible at any time during an active optimisation run.
- The window displays configuration diffs (changed parameters) and metric deltas between the pre-optimisation and current best-optimised versions.

**Customer Satisfaction (0–5):**

- 3: Provides useful context during the optimisation step.

**Customer Dissatisfaction (0–5):**

- 2: Users can compare manually by noting parameters before optimisation, but this adds friction.

**Dependencies / Conflicts:**
REQ-10, REQ-32

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
