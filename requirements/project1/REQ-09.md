# Save and reload named presets

**ID:** REQ-09

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to save a strategy as a named preset and reload it in a future session with its complete configuration intact.

**Rationale:**
Persistent named presets enable users to manage a personal library of strategies and resume work across sessions without data loss.

**Fit Criterion:**

- A strategy can be saved under a user-defined name at any time.
- Reloading a saved preset restores the exact strategy configuration, including all block parameters, connections, and input settings.
- The preset is available across application restarts.

**Customer Satisfaction (0–5):**

- 5: Without persistence, all work is lost between sessions.

**Customer Dissatisfaction (0–5):**

- 5: Loss of work between sessions is a critical blocker.

**Dependencies / Conflicts:**
REQ-05, REQ-08

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
