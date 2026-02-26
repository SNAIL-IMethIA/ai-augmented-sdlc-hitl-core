# Double-click to open block config

**ID:** REQ-25

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to open a block's configuration panel by double-clicking on it in the pipeline graph.

**Rationale:**
Double-click to configure is a well-established convention in graphical editors; it provides the most direct path to editing a block without navigating menus.

**Fit Criterion:**

- Double-clicking any block in the pipeline graph opens its configuration panel within 500 ms.
- The configuration panel displays all editable parameters for the selected block.

**Customer Satisfaction (0–5):**

- 3: Expected interaction pattern; speeds up parameter editing.

**Customer Dissatisfaction (0–5):**

- 3: Users can access configuration via a context menu or toolbar, but double-click is significantly faster.

**Dependencies / Conflicts:**
REQ-08, REQ-17

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
