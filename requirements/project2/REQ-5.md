# Email notifications for task due dates

**ID:** REQ-5

**Type:** Functional

**Originator:** Product Owner

**Description:**
The system shall send an email notification to the assigned user 24 hours before a task's due date, provided the task has not already been marked as Done.

**Rationale:**
Proactive reminders reduce missed deadlines without requiring users to actively monitor the application, improving overall task completion rates.

**Fit Criterion:**

- Notification emails are delivered within 30 minutes of the scheduled trigger time.
- No notification is sent if the task status is "Done" at the time of trigger.
- Users can opt out of email notifications per task or globally via account settings.
- Notification includes the task title, due date, and a direct link to the task.

**Customer Satisfaction (0–5):**

- 3: Useful convenience feature that increases engagement and reduces missed deadlines.

**Customer Dissatisfaction (0–5):**

- 2: Users can check the dashboard manually; notifications are a convenience, not a blocker.

**Dependencies / Conflicts:**
REQ-1, REQ-2

**Status:**
Draft

**Priority:**
Could

**History:**

- 2026-02-26 | Product Owner | Created | Initial draft for project2 demo
