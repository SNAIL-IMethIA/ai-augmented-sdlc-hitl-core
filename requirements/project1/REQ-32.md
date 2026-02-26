# Grid search optimisation with CV

**ID:** REQ-32

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall perform parameter optimisation using grid search combined with cross-validation to identify the best-performing parameter set for a strategy.

**Rationale:**
Systematic grid search with cross-validation provides a reproducible, exhaustive approach to optimisation that reduces manual trial-and-error and the risk of overfitting.

**Fit Criterion:**

- Given a user-defined parameter grid, the system evaluates all specified combinations.
- The best-performing parameter set is identified by the highest cross-validated out-of-sample metric score.
- The full grid search result, including all evaluated combinations, is available for inspection.

**Customer Satisfaction (0–5):**

- 4: Automates a time-consuming optimisation process that is error-prone manually.

**Customer Dissatisfaction (0–5):**

- 3: Users can manually adjust parameters, but systematic search is unavailable.

**Dependencies / Conflicts:**
REQ-29, REQ-33, REQ-34

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
