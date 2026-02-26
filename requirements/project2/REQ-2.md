# Task creation and management

**ID:** REQ-2

**Type:** Functional

**Originator:** Product Owner

**Description:**
The system shall allow an authenticated user to create, edit, and delete tasks, each containing a title, optional description, due date, priority level, and assignee.

**Rationale:**
Task creation is the primary value-delivery action of the application; without it the system has no functional content for users to manage or collaborate on.

**Fit Criterion:**

- A user can create a task with at minimum a title; all other fields are optional.
- A task can be edited at any time by the creator or any assigned collaborator.
- Deleting a task requires a confirmation prompt and removes it permanently from all views.
- A task title cannot exceed 200 characters; an error is shown immediately upon violation.

**Customer Satisfaction (0–5):**

- 5: Core feature; the product delivers no value without task management.

**Customer Dissatisfaction (0–5):**

- 5: Without task creation the application is unusable.

**Dependencies / Conflicts:**
REQ-1

**Status:**
Draft

**Priority:**
Must

**History:**

- 2026-02-26 | Product Owner | Created | Initial draft for project2 demo
