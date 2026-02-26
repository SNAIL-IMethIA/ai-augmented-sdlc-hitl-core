# Modify strategy/indicator parameters

**ID:** REQ-08

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to modify the parameters of any building block within a strategy at any time, including after the strategy has been saved.

**Rationale:**
Strategy tuning is an iterative process; locking parameters after save would force users to rebuild strategies rather than refining them.

**Fit Criterion:**

- Any block parameter can be updated via the block configuration panel.
- The strategy is re-validated automatically after a parameter change without requiring a full rebuild.
- Modified parameters are reflected immediately in the visual pipeline graph.

**Customer Satisfaction (0–5):**

- 5: Core to the iterative strategy development workflow.

**Customer Dissatisfaction (0–5):**

- 5: Without editable parameters, strategy optimisation is impossible.

**Dependencies / Conflicts:**
REQ-25, REQ-09

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
