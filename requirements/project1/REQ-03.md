# Cross-asset comparison in rules

**ID:** REQ-03

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow rule blocks within a strategy to compare values from different assets, provided the compared assets are normalised to a compatible unit or ratio.

**Rationale:**
Cross-asset comparisons (e.g., BTC vs. ETH relative strength) provide more expressive strategy logic and support longer-term correlation-based strategies.

**Fit Criterion:**

- A rule block can reference data from a secondary asset distinct from the strategy's primary asset.
- The secondary asset data is scaled or normalised before comparison, and the rule produces a valid boolean or signal output.

**Customer Satisfaction (0–5):**

- 3: Useful for advanced users building multi-asset signal rules.

**Customer Dissatisfaction (0–5):**

- 2: Users can approximate cross-asset logic with workarounds, but expressiveness is limited.

**Dependencies / Conflicts:**
REQ-02, REQ-04

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
