# Undo / redo (≥ 20 steps)

**ID:** REQ-22

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall support undo and redo operations covering all builder actions.

**Rationale:**
Undo/redo allows users to safely experiment with changes, knowing they can instantly revert any mistake without losing prior work.

**Fit Criterion:**

- At least 20 consecutive undo steps are supported without losing history.
- Each undo restores the pipeline to the exact state prior to the undone action.
- Redo re-applies the undone action.
- Undo and redo are accessible via keyboard shortcut and a visible UI control.

**Customer Satisfaction (0–5):**

- 4: Industry-standard expectation for any editing tool; absence would be jarring.

**Customer Dissatisfaction (0–5):**

- 4: Without undo, every mistake requires manual correction, significantly impeding workflow.

**Dependencies / Conflicts:**
REQ-20, REQ-21, REQ-27

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
