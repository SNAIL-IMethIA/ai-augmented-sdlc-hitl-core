# Live trading API connection with confirmation

**ID:** REQ-37

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to connect an optimised strategy to a real-time trading platform via a pre-configured exchange API, and shall require explicit user confirmation before enabling live trading.

**Rationale:**
Live trading involves real financial risk; an explicit confirmation gate prevents accidental activation and ensures the user has consciously accepted the transition from simulation to live.

**Fit Criterion:**

- The live connection flow presents a clear confirmation prompt before enabling any live order submission.
- The strategy begins receiving real-time data and submitting orders only after the user confirms.
- The connection status is permanently visible in the UI while live trading is active.

**Customer Satisfaction (0–5):**

- 3: Live trading connectivity is the ultimate output of the strategy development workflow.

**Customer Dissatisfaction (0–5):**

- 1: Without live connectivity, the tool is limited to simulation only.

**Dependencies / Conflicts:**
REQ-38, REQ-09

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
