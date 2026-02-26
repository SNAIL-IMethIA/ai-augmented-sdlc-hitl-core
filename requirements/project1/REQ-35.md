# Capital per trade configuration

**ID:** REQ-35

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to configure the capital allocated per trade as either a fixed monetary amount or a fixed percentage of available capital.

**Rationale:**
Capital allocation per trade is a fundamental risk control; supporting both fixed and percentage modes accommodates users at different experience levels and with different account management styles.

**Fit Criterion:**

- Both fixed-amount and fixed-percentage modes are selectable per strategy.
- Each mode produces the correct position size for at least three distinct account balances and entry price scenarios.
- The selected mode and value are persisted with the strategy preset.

**Customer Satisfaction (0–5):**

- 5: Capital allocation is mandatory before any live or simulated trading.

**Customer Dissatisfaction (0–5):**

- 5: Without configurable capital allocation, the system cannot compute position sizes.

**Dependencies / Conflicts:**
REQ-14, REQ-54

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
