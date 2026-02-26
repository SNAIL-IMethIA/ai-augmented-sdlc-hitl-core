# API response time ≤ 300 ms (p95)

**ID:** REQ-4

**Type:** Non-functional

**Originator:** Technical Lead

**Description:**
The system shall respond to all authenticated API requests within 300 milliseconds at the 95th percentile under a load of up to 50 concurrent users.

**Rationale:**
Response times above 300 ms are perceptible to users and degrade perceived quality; meeting this threshold ensures the interface remains fluid under expected load.

**Fit Criterion:**

- Automated load tests with 50 concurrent users show p95 API response time ≤ 300 ms.
- No single request exceeds 1 000 ms at the 99th percentile under the same conditions.
- Tests are run against the staging environment before each production release.

**Customer Satisfaction (0–5):**

- 4: A fast interface directly improves productivity and user satisfaction.

**Customer Dissatisfaction (0–5):**

- 4: Sluggish responses would erode trust and drive users away.

**Dependencies / Conflicts:**
None

**Status:**
Draft

**Priority:**
Must

**History:**

- 2026-02-26 | Technical Lead | Created | Initial draft for project2 demo
