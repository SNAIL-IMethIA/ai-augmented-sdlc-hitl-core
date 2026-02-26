# Backtest time span selection

**ID:** REQ-56

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow the user to select the historical time span used for backtesting by specifying a start date, an end date, or a rolling lookback period relative to the current date.

**Rationale:**
The time span of backtesting data directly determines which market regimes are included in the analysis; users must be able to control this to test strategies across specific periods or to replicate prior results.

**Fit Criterion:**

- The user can set start and end dates for the backtest window using a date picker.
- The user can alternatively specify a rolling lookback period (e.g. last 2 years).
- The selected range is validated against the available historical data for the configured asset and exchange; if insufficient data is available, an informative error is shown before the backtest begins.

**Customer Satisfaction (0–5):**

- 4: Time span control is a baseline expectation for any backtesting tool.

**Customer Dissatisfaction (0–5):**

- 4: Without time span selection, all backtest methods use an undefined or fixed window, making results uncontrollable and unreproducible.

**Dependencies / Conflicts:**
REQ-29, REQ-53

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
