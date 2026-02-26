# Block selection panel (+ button / node propositions)

**ID:** REQ-55

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall provide a block selection panel, triggered by both a dedicated add button (ghost blocks) and a configurable keyboard shortcut, that presents a categorised and filtered list of compatible block types (indicators, patterns, rules, actions) for insertion into the pipeline at the current position.

**Rationale:**
A contextually filtered selection panel reduces cognitive load by surfacing only valid choices, speeds up pipeline construction, and allows discovery of available blocks without requiring prior knowledge of the full library.

**Fit Criterion:**

- The panel opens within 200 ms of the add trigger (button press or keyboard shortcut).
- Both the add button and the keyboard shortcut independently open the panel.
- Only block types that are compatible with the current insertion point are shown.
- Blocks are organised by category (indicator, pattern, rule, action) and searchable by name.
- Selecting a block from the panel inserts it into the pipeline at the triggered position.

**Customer Satisfaction (0–5):**

- 5: The add-block interaction is the most frequent action in strategy construction; its quality directly defines the UX.

**Customer Dissatisfaction (0–5):**

- 4: Without a filtered selection panel, users must discover compatible blocks by trial and error.

**Dependencies / Conflicts:**
REQ-16, REQ-17, REQ-18, REQ-26, REQ-27

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
