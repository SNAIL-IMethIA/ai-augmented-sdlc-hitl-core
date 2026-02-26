# Decision tree / state machine inspection

**ID:** REQ-24

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall provide an inspection view that renders the strategy logic as a decision tree or state machine diagram.

**Rationale:**
A formal structural view (distinct from the pipeline graph) helps users and reviewers verify that the strategy's decision logic is correct and complete.

**Fit Criterion:**

- For any valid strategy, the inspection view renders a syntactically correct decision tree or state machine diagram.
- The diagram correctly reflects the current strategy logic, including all conditional branches and state transitions.

**Customer Satisfaction (0–5):**

- 3: Valuable for understanding and auditing complex strategies.

**Customer Dissatisfaction (0–5):**

- 2: Users can manually trace logic in the pipeline graph, but this is significantly more effort.

**Dependencies / Conflicts:**
REQ-02, REQ-17

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
