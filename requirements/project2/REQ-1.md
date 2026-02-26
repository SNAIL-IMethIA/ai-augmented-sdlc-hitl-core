# User authentication and session management

**ID:** REQ-1

**Type:** Functional

**Originator:** Product Owner

**Description:**
The system shall authenticate users via email and password and maintain a secure, time-limited session for each successful login.

**Rationale:**
Without authentication, all user data and tasks would be accessible to any visitor; enforcing login ensures data isolation between users and protects sensitive project information.

**Fit Criterion:**

- A user can register with a unique email address and a password of at least 8 characters.
- A successful login returns a session token valid for at least 24 hours.
- An invalid email or password combination returns an error within 2 seconds without disclosing which field was incorrect.
- An expired or invalid token results in a redirect to the login screen.

**Customer Satisfaction (0–5):**

- 5: Authentication is a prerequisite for any personalised user experience.

**Customer Dissatisfaction (0–5):**

- 5: Without it, any visitor can access any user's tasks and data.

**Dependencies / Conflicts:**
None

**Status:**
Draft

**Priority:**
Must

**History:**

- 2026-02-26 | Product Owner | Created | Initial draft for project2 demo
