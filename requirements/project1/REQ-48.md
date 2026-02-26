# Built-in component descriptions

**ID:** REQ-48

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall provide detailed built-in textual descriptions for each pipeline component, describing its function, parameters, and role within a strategy, accessible when inspecting any strategy.

**Rationale:**
Built-in explanations reduce the need for users to leave the application to understand what a block does, improving both onboarding speed and expert review quality.

**Fit Criterion:**

- Inspecting any valid strategy displays a textual description for every component present in its pipeline.
- Each description covers the component's function, configurable parameters, and expected output.
- Descriptions are displayed within the application without requiring an internet connection.

**Customer Satisfaction (0–5):**

- 4: Directly supports non-expert users and improves confidence in strategy construction.

**Customer Dissatisfaction (0–5):**

- 1: Users must consult external references to understand component behaviour.

**Dependencies / Conflicts:**
REQ-15, REQ-47

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
