# Backtest metrics report (9 metrics)

**ID:** REQ-31

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall compute and display the following performance metrics upon completion of any backtest run: number of trades, win rate, maximum drawdown, total strategy return over the backtest period, strategy return vs. market return delta, exposure time, Sharpe ratio, Sortino ratio, and profit factor.

**Rationale:**
These nine metrics collectively give a complete and standardised picture of strategy performance, risk, and efficiency, enabling informed comparison and decision-making.

**Fit Criterion:**

- All nine metrics are present in the results report for every completed backtest.
- Each metric value is numerically correct within a 0.1% tolerance.
- The report is available within 5 seconds of backtest completion.

**Customer Satisfaction (0–5):**

- 5: Metric reporting is the primary output of the backtest feature.

**Customer Dissatisfaction (0–5):**

- 5: Without metrics, backtest results are meaningless to the user.

**Dependencies / Conflicts:**
REQ-29, REQ-34

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
