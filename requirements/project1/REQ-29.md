# Multiple backtest methods (3)

**ID:** REQ-29

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall support the following backtest methods, each independently selectable: historical, out-of-sample, regime-based.

**Rationale:**
A comprehensive suite of backtest methods reduces the risk of overfitting and provides statistically robust evidence of strategy performance across varied market conditions.

**Fit Criterion:**

- Each of the eight backtest methods can be selected and executed independently.
- Each method produces a distinct result set for the same strategy configuration.
- All methods are available for the configured historical data range and asset.

**Customer Satisfaction (0–5):**

- 5: Robust backtesting is a primary differentiator and directly impacts user confidence in results.

**Customer Dissatisfaction (0–5):**

- 4: Fewer methods increases the risk of deploying overfit strategies with real capital.

**Dependencies / Conflicts:**
REQ-31, REQ-32

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
