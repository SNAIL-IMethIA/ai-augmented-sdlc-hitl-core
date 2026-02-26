# Custom asset selection (Advanced mode)

**ID:** REQ-39

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow users in Advanced mode to define custom asset selections beyond the default asset list by entering a custom ticker symbol.

**Rationale:**
Limiting users to a pre-defined asset list prevents strategies on less common or newly listed assets; custom asset entry removes this constraint for advanced users.

**Fit Criterion:**

- A custom asset ticker can be entered via the asset selection interface in Advanced mode.
- The system successfully fetches historical and real-time data for the custom asset from the configured exchange.
- The custom asset is usable as the primary asset in a strategy pipeline.

**Customer Satisfaction (0–5):**

- 3: High value for users trading niche or emerging assets.

**Customer Dissatisfaction (0–5):**

- 2: Users can approximate by selecting the nearest available asset, but data may be inaccurate.

**Dependencies / Conflicts:**
REQ-45, REQ-38

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
