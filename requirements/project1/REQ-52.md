# Demo / sample strategy

**ID:** REQ-52

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall ship with at least one pre-loaded demo strategy that users can open, inspect, and modify without affecting the original.

**Rationale:**
A demo strategy gives new users an immediately runnable example, accelerating onboarding and reducing the barrier to understanding how the pipeline and builder work.

**Fit Criterion:**

- The demo strategy is accessible from the startup screen and the strategy library without any prior setup.
- Opening the demo strategy does not require selecting an exchange or asset; sensible defaults are pre-configured.
- Any modifications made to the demo strategy are isolated to a user copy and do not alter the original demo.

**Customer Satisfaction (0–5):**

- 4: A working demo significantly reduces onboarding friction and time-to-first-success.

**Customer Dissatisfaction (0–5):**

- 2: Absence slows onboarding but users can still start from scratch.

**Dependencies / Conflicts:**
REQ-05, REQ-44, REQ-46

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
