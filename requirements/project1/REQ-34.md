# Out-of-sample validation

**ID:** REQ-34

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall validate the optimised strategy on a held-out, previously unseen dataset that was not used during the optimisation process, and shall display the same set of metrics as produced during backtesting.

**Rationale:**
Out-of-sample validation on fresh data is the definitive test of whether an optimised strategy generalises beyond the training data.

**Fit Criterion:**

- The validation dataset consists exclusively of data not used in any stage of the optimisation.
- The validation report contains all nine metrics defined in REQ-31.
- A clear label distinguishes out-of-sample validation results from backtest results.

**Customer Satisfaction (0–5):**

- 5: Out-of-sample validation is the gold standard for assessing strategy robustness.

**Customer Dissatisfaction (0–5):**

- 5: Without it, users cannot distinguish genuinely robust strategies from overfit ones.

**Dependencies / Conflicts:**
REQ-31, REQ-32

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
