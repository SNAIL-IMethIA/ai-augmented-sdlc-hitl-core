# Ghost blocks with typed suggestions

**ID:** REQ-26

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall display placeholder (ghost) blocks for required but unassigned block dependencies, and restrict block suggestions to only compatible types when a user attempts to fill a ghost block.

**Rationale:**
Ghost blocks make missing dependencies visually explicit and guide users towards valid completions, reducing trial-and-error during strategy construction.

**Fit Criterion:**

- A ghost block is displayed for every unfilled required input connection of any block in the pipeline.
- When a user interacts with a ghost block to assign a real block, the suggestion list contains only block types that satisfy the dependency's type contract.
- Assigning an incompatible block type to a ghost block is not permitted.

**Customer Satisfaction (0–5):**

- 3: Significantly reduces errors and guides novice users towards valid configurations.

**Customer Dissatisfaction (0–5):**

- 2: Without ghost blocks, unmet dependencies may be overlooked until runtime.

**Dependencies / Conflicts:**
REQ-17, REQ-18

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
