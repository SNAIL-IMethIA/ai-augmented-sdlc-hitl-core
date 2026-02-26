# Block compatibility validation

**ID:** REQ-18

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall validate block connections in real time and prevent incompatible blocks from being linked.

**Rationale:**
Real-time validation prevents users from creating logically invalid pipelines that would fail silently or produce incorrect results.

**Fit Criterion:**

- Attempting to connect two incompatible blocks displays an inline error indicator on the connection or blocks within 200 ms.
- The invalid connection is not created.
- A plain-language explanation of the incompatibility is displayed.

**Customer Satisfaction (0–5):**

- 0: Prevents silent errors and guides users towards valid configurations.

**Customer Dissatisfaction (0–5):**

- 5: Without validation, invalid pipelines may appear correct until runtime failure.

**Dependencies / Conflicts:**
REQ-17, REQ-26

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
