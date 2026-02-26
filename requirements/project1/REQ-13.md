# Maximum drawdown limit enforcement

**ID:** REQ-13

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall enforce a user-defined maximum drawdown limit per strategy and flag any simulation that breaches this limit.

**Rationale:**
Drawdown limits are a primary risk control mechanism; surfacing breaches during simulation prevents users from deploying dangerously risky strategies live.

**Fit Criterion:**

- A maximum drawdown value (expressed as a percentage) can be configured per strategy.
- Any backtest or simulation run that exceeds the configured limit generates a visible warning or halts execution with a clear explanation.

**Customer Satisfaction (0–5):**

- 0: Provides an essential safety guardrail for risk-aware users.

**Customer Dissatisfaction (0–5):**

- 0: Without drawdown limits, users may unknowingly deploy strategies with catastrophic risk profiles.

**Dependencies / Conflicts:**
REQ-12, REQ-31

**Status:**
Approved

**Priority:**
Won't

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
