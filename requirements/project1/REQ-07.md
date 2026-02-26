# Clone existing strategy

**ID:** REQ-07

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to clone an existing strategy into a new, fully independent copy.

**Rationale:**
Cloning enables iterative experimentation (e.g., changing a single parameter in a copy) without risking the integrity of the original, validated strategy.

**Fit Criterion:**

- Cloning a strategy produces a new, separately named strategy with identical configuration.
- Modifications to the cloned copy do not alter the original strategy in any way.

**Customer Satisfaction (0–5):**

- 4: Essential for A/B-style iteration and version-controlled experimentation.

**Customer Dissatisfaction (0–5):**

- 3: Users can manually recreate a strategy, but this is time-consuming and error-prone.

**Dependencies / Conflicts:**
REQ-05, REQ-09

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
