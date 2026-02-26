# Delete multiple elements

**ID:** REQ-21

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to delete one or more selected pipeline elements simultaneously.

**Rationale:**
Bulk deletion reduces the effort required to restructure or clean up complex pipelines.

**Fit Criterion:**

- Selecting N elements and invoking the delete action removes all N elements and all connections attached to them from the pipeline graph.
- The deletion is undoable via the undo operation (see REQ-22).

**Customer Satisfaction (0–5):**

- 3: Standard editing affordance expected in any graphical editor.

**Customer Dissatisfaction (0–5):**

- 2: Single-element deletion is a viable fallback, but is slower for bulk operations.

**Dependencies / Conflicts:**
REQ-19, REQ-22

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
