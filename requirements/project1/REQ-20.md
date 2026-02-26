# Copy, cut, and paste elements

**ID:** REQ-20

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to copy, cut, and paste selected pipeline elements, preserving their internal connections where applicable.

**Rationale:**
Copy/cut/paste accelerates building of repetitive sub-patterns and enables reuse of validated block configurations within or across pipelines.

**Fit Criterion:**

- Copying a block or group and pasting produces a duplicate with identical parameters.
- Pasting a group preserves intra-group connections.
- Cutting removes the element(s) from the graph and places them in a clipboard buffer available for paste.

**Customer Satisfaction (0–5):**

- 3: Standard editing affordance that users expect from any graphical editor.

**Customer Dissatisfaction (0–5):**

- 2: Users can manually recreate elements, but this is significantly slower.

**Dependencies / Conflicts:**
REQ-19, REQ-22

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
