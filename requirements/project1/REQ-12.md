# Stop-loss / take-profit simulation

**ID:** REQ-12

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall simulate stop-loss and take-profit levels for a strategy based on user-defined input parameters.

**Rationale:**
Calculating expected exit prices from entry, stop-loss, and take-profit inputs helps users quantify trade risk and reward before committing to a strategy.

**Fit Criterion:**

- Given entry price, stop-loss offset, and take-profit offset, the system computes and displays the resulting exit prices, risk amount, and expected return.
- Values update immediately when any input parameter is changed.

**Customer Satisfaction (0–5):**

- 5: Core risk management feature; directly linked to trade safety.

**Customer Dissatisfaction (0–5):**

- 4: Without simulated SL/TP, users cannot reliably reason about trade risk.

**Dependencies / Conflicts:**
REQ-13, REQ-14

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
