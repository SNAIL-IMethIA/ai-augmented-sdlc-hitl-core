# Strategy pipeline structure

**ID:** REQ-02

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall structure each strategy as an ordered pipeline composed of the following stage types in sequence: input data, indicators, rules, patterns, and output/decision.

**Rationale:**
A standardised pipeline structure ensures consistency, traceability, and predictable execution across all strategies.

**Fit Criterion:**

- A complete strategy can be constructed by connecting at least one block from each required stage type.
- The pipeline executes stages in the defined order without skipping a stage type.

**Customer Satisfaction (0–5):**

- 5: The pipeline model is the core architectural building block of the product.

**Customer Dissatisfaction (0–5):**

- 5: Without a structured pipeline, strategy construction and execution are undefined.

**Dependencies / Conflicts:**
REQ-05, REQ-16, REQ-17

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
