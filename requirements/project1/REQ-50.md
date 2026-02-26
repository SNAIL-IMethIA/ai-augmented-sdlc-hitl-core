# Local desktop deployment

**ID:** REQ-50

**Type:** Non-functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall be installable and fully operable as a standalone local desktop application on the host operating system.

**Rationale:**
Local execution provides low-latency interaction during strategy construction and live trading, and ensures that strategy configuration and API credentials never leave the user's machine without explicit consent.

**Fit Criterion:**

- All features are accessible and functional in the local desktop installation if the data is available.
- The application starts and a complete strategy workflow can be executed with no active network connection except for pulling the data.
- Installation completes successfully using the published installer on a clean operating system environment.

**Customer Satisfaction (0–5):**

- 3: Local execution is a baseline deployment expectation, not a differentiator.

**Customer Dissatisfaction (0–5):**

- 3: Without a local desktop option, users requiring offline or privacy-sensitive setups are excluded.

**Dependencies / Conflicts:**
REQ-43, REQ-44, REQ-45

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-16 | Kevin Schweitzer | Revised | Split from original non-atomic entry; see also REQ-58 (cloud/remote execution) and REQ-59 (web interface)
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
