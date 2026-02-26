# Human-readable strategy explanations

**ID:** REQ-15

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall generate a human-readable textual explanation of a strategy's indicators, pipeline structure, signals, and backtest results upon user request.

**Rationale:**
Non-expert users need plain-language descriptions to understand what a strategy does and why it performed as it did, enabling informed refinement decisions.

**Fit Criterion:**

- For any valid strategy with a completed backtest, the system produces a plain-language summary covering all four areas: indicators, pipeline structure, signals, and backtest results.
- The explanation is generated without requiring any additional user input beyond the initial request.

**Customer Satisfaction (0–5):**

- 4: Directly addresses the needs of non-programmer users and improves trust in the system.

**Customer Dissatisfaction (0–5):**

- 1: Advanced users can interpret results independently, but novice users are left without guidance.

**Dependencies / Conflicts:**
REQ-02, REQ-31

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
