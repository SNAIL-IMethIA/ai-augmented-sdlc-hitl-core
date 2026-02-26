# Monte Carlo stress testing and EV visualisation

**ID:** REQ-36

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall perform a Monte Carlo stress test automatically after each completed backtest run, generating a variance-adjusted expected value (EV) visualisation that displays a deterministic EV curve, multiple stochastic equity paths, and percentile envelope bands (confidence intervals).

**Rationale:**
A Monte Carlo simulation applied after backtesting produces a forward-looking outcome distribution, showing users the range of realistic equity paths under random trade sequencing and market variability. This helps users assess robustness and calibrate risk expectations before committing capital.

**Fit Criterion:**

- Monte Carlo stress testing is triggered automatically upon completion of any backtest run.
- The visualisation renders a single deterministic EV line, at least 100 simulated stochastic equity paths, and 10th, 50th, and 90th percentile bands.
- All components are rendered simultaneously on the same chart for a user-specified number of forward trades.
- The chart updates within 10 seconds of backtest completion.

**Customer Satisfaction (0–5):**

- 5: Unique and insightful feature that aids user decision-making and communicates strategy robustness clearly.

**Customer Dissatisfaction (0–5):**

- 2: Users can reason about EV from metrics alone, but the stochastic visualisation is significantly more intuitive.

**Dependencies / Conflicts:**
REQ-29, REQ-31, REQ-34

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
- 2026-02-26 | Kevin Schweitzer | Updated | Renamed to Monte Carlo stress testing; expanded description and fit criterion to explicitly cover post-backtest Monte Carlo simulation; added REQ-29 dependency
