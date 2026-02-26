# Basic mode with guided workflow

**ID:** REQ-44

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall provide a Basic mode that guides users through strategy construction via a structured, step-by-step workflow covering input selection, indicator configuration, risk settings, and backtesting.

**Rationale:**
A guided workflow removes decision paralysis for new users and ensures that required steps are completed in the correct order, reducing the risk of misconfigured strategies.

**Fit Criterion:**

- A user with no prior experience can complete a full strategy setup, covering input selection through to backtest result, in Basic mode without accessing any unguided or Advanced interface elements.
- The workflow enforces step completion before advancing; incomplete steps are surfaced with guidance.
- All tools available in Basic mode are accessible via the guided workflow.

**Customer Satisfaction (0–5):**

- 3: Ideal for onboarding new and non-expert users.

**Customer Dissatisfaction (0–5):**

- 3: Without guided setup, novice users are likely to misconfigure strategies or abandon the product.

**Dependencies / Conflicts:**
REQ-43, REQ-47

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
