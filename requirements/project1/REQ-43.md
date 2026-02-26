# Mode selection on startup (persisted)

**ID:** REQ-43

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall prompt the user to select an operating mode (Basic or Advanced) on application startup and shall persist the selection for future sessions.

**Rationale:**
Presenting mode selection at startup ensures users are in the appropriate context for their experience level from the start of each session, with minimal friction for returning users.

**Fit Criterion:**

- A mode selection prompt appears on the first launch of the application.
- The selected mode is applied immediately and takes effect for the full session.
- The selection is pre-populated with the previously chosen mode on subsequent launches.
- The user can change the mode at any time from within the application settings.

**Customer Satisfaction (0–5):**

- 3: Smooth onboarding experience that routes users to the right context.

**Customer Dissatisfaction (0–5):**

- 2: Without mode selection, users may be overwhelmed by Advanced features or constrained by Basic mode unnecessarily.

**Dependencies / Conflicts:**
REQ-44, REQ-45

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
