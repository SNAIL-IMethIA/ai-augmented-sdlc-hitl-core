# Cloud / remote execution

**ID:** REQ-58

**Type:** Non-functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall support execution on remote cloud infrastructure, enabling users to access the full application remotely without a local installation.

**Rationale:**
Cloud execution allows the system to serve users who lack the hardware or operating system prerequisites for a local installation, and enables centralised management of compute-intensive tasks such as backtesting and optimisation.

**Fit Criterion:**

- The application can be deployed and run on a standard cloud virtual machine.
- A user can access the full application remotely via the web interface (REQ-59) when the system is running on cloud infrastructure.
- Strategy files and configurations are preserved across cloud session restarts without data loss.

**Customer Satisfaction (0–5):**

- 2: Useful for users who prefer managed infrastructure or require high compute for backtesting.

**Customer Dissatisfaction (0–5):**

- 1: Users can run the application locally or use the web interface on their own hardware; cloud is an optional enhancement.

**Dependencies / Conflicts:**
REQ-50, REQ-59

**Status:**
Approved

**Priority:**
Won't

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes; split from original non-atomic REQ-50
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
