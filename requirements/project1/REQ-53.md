# Input configuration panel

**ID:** REQ-53

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall provide an input configuration panel that allows the user to select the exchange (from a dropdown of pre-saved API setups), asset, and time frame at any point during strategy construction, with the ability to save changes to a preset or discard them.

**Rationale:**
The input data source is the foundation of every strategy; users must be able to update it freely without restarting or recreating the strategy, and must be able to preview changes without committing them.

**Fit Criterion:**

- The input configuration panel is accessible from the builder interface at any stage of strategy construction.
- Selecting a different exchange, asset, or time frame updates all dependent pipeline blocks and visualisations within 2 seconds.
- Changes can be saved to the current preset or discarded, restoring the previous configuration exactly.
- All available time frames are dynamically populated based on the selected exchange API capabilities.

**Customer Satisfaction (0–5):**

- 5: Input selection is the entry point of every strategy; it must be frictionless and reversible.

**Customer Dissatisfaction (0–5):**

- 5: Without a configurable and reversible input panel, users cannot safely experiment with different data sources.

**Dependencies / Conflicts:**
REQ-04, REQ-09, REQ-37, REQ-38, REQ-39

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
