# Dashboard with task summary

**ID:** REQ-3

**Type:** Functional

**Originator:** Product Owner

**Description:**
The system shall display a dashboard that summarises the authenticated user's tasks grouped by status (To Do, In Progress, Done) with counts and a list of tasks due within the next 7 days.

**Rationale:**
A summary dashboard gives users an immediate, actionable view of their workload without navigating into individual task lists, reducing time-to-first-insight.

**Fit Criterion:**

- The dashboard loads within 2 seconds for up to 500 tasks.
- Task counts per status are always accurate relative to the current database state.
- The "due this week" list shows all tasks whose due date falls within 7 calendar days of the current date, in ascending due-date order.

**Customer Satisfaction (0–5):**

- 4: Significantly improves daily usability and prioritisation.

**Customer Dissatisfaction (0–5):**

- 3: Users can navigate task lists manually, but at considerably more effort.

**Dependencies / Conflicts:**
REQ-1, REQ-2

**Status:**
Draft

**Priority:**
Should

**History:**

- 2026-02-26 | Product Owner | Created | Initial draft for project2 demo
