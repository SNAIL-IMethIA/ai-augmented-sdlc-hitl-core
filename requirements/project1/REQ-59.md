# Web interface

**ID:** REQ-59

**Type:** Non-functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall provide a web-based interface accessible from a standard browser, offering the same core functionality as the local desktop application.

**Rationale:**
A web interface broadens accessibility beyond users who can install a local desktop application, enabling use on restricted or shared machines and complementing cloud-hosted deployments under REQ-58.

**Fit Criterion:**

- The web interface exposes all core workflows available in the local desktop application: strategy creation, backtesting, and result viewing.
- The web interface is accessible via a standard modern browser without any additional plugin or extension installation.
- The web interface functions correctly when the application is running on cloud infrastructure (see REQ-58).

**Customer Satisfaction (0–5):**

- 2: Useful for users who cannot install locally; not required for core functionality.

**Customer Dissatisfaction (0–5):**

- 1: Users can use the local desktop application or a cloud-hosted desktop; a browser-based interface is an optional channel.

**Dependencies / Conflicts:**
REQ-50, REQ-58

**Status:**
Approved

**Priority:**
Won't

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes; split from original non-atomic REQ-50
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
