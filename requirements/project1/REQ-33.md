# Statistical significance testing

**ID:** REQ-33

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall apply a statistical significance test to optimisation results to distinguish genuine performance improvements from chance, and shall report the result of this test alongside each optimised output.

**Rationale:**
Optimising over in-sample data can produce spurious improvements attributable to luck; a significance test (e.g., t-test or permutation test) provides evidence that improvements are systematic.

**Fit Criterion:**

- A p-value or equivalent significance indicator is reported alongside every optimisation result.
- Improvements with p > 0.05 are visually flagged as not statistically significant.
- The test method used is disclosed to the user in the results view.

**Customer Satisfaction (0–5):**

- 4: Protects users from deploying overfit strategies; adds scientific rigour.

**Customer Dissatisfaction (0–5):**

- 4: Absence increases the risk of deploying strategies that only appeared profitable in-sample.

**Dependencies / Conflicts:**
REQ-32

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
