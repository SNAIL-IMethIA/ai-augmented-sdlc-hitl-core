# Advanced position sizing: Kelly criterion variants

**ID:** REQ-14

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall support the following advanced Kelly criterion position sizing variants: Kelly on R-multiples, volatility-targeted Kelly, Kelly capped at maximum risk (≤ 2% per trade), and dynamic Kelly updated via rolling windows.

**Rationale:**
The Kelly criterion and its variants offer mathematically optimal sizing for strategies with well-defined win rates and R-multiples; supporting multiple Kelly variants ensures the tool serves advanced users requiring sophisticated sizing beyond the fixed-allocation models defined in REQ-35.

**Fit Criterion:**

- Each Kelly variant is selectable independently per strategy.
- Each variant produces a numerically distinct position size when given the same account balance, win rate, and R-multiple as input.
- Each variant respects its specific constraint: R-multiple basis, volatility target, 2% risk cap, or rolling window update frequency.

**Customer Satisfaction (0–5):**

- 4: Advanced sizing models differentiate the product for sophisticated users.

**Customer Dissatisfaction (0–5):**

- 3: Users can fall back to fixed sizing (REQ-35), but advanced Kelly-based risk management is unavailable.

**Dependencies / Conflicts:**
REQ-12, REQ-35

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
