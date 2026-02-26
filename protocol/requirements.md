# Requirements Specification Template

This template provides a structured format for documenting stakeholder and system requirements inspired by the **Volere Requirements Specification Method**, ensuring traceability, clarity, and verifiability within the project protocol.

---

## Table of Contents

1. [Instructions](#instructions)
2. [Requirement Types](#requirement-types)
3. [Customer Satisfaction / Dissatisfaction Scales](#customer-satisfaction--dissatisfaction-scales)
4. [Requirement Template](#requirement-template)
5. [Copy-Paste Block Format](#copy-paste-block-format)
6. [Examples](#examples)

---

## Instructions

1. Document each requirement individually using the template below.  
2. Requirements must satisfy the following quality attributes:  
   - **Atomic**: Only one obligation, capability, or constraint per requirement.  
   - **Unambiguous**: Only one interpretation possible.  
   - **Testable / Verifiable**: Can be objectively evaluated.  
   - **Consistent**: Does not conflict with other requirements.  
   - **Feasible**: Achievable within project constraints.  
3. Use mandatory language: **“The system shall …”**.  
4. Maintain **traceability** to the requirement originator, stakeholder, or regulation.  
5. Maintain a **history log** for all creation, modifications, reviews, and approvals.  
6. Dates must follow **ISO 8601** format (`YYYY-MM-DD`).  
7. Use sequential requirement IDs in the format `REQ-01`, `REQ-02`, etc. Padding width is computed automatically from the total requirement count by the renumber script (e.g. up to 99 requirements → two digits; 100–999 → three digits). Each ID must be unique; gaps introduced by deletion are closed automatically by running `python -m scripts.requirements.main --renumber`.

---

## Requirement Types

| Type | Description |
| --- | --- |
| Functional | System behavior or capability. |
| Non-functional | Performance, security, usability, or other quality attributes. |
| Interface | Interaction with other systems, APIs, or hardware. |
| Constraint | Regulatory, technical, or operational limitations. |
| Environmental | Operational, physical, or deployment conditions. |

---

## Customer Satisfaction / Dissatisfaction Scales

**Customer Satisfaction (CS):** impact if requirement is implemented:  

- 0 = No positive impact  
- 1 = Minimal benefit  
- 2 = Moderate benefit  
- 3 = Significant benefit  
- 4 = Major benefit  
- 5 = Critical / essential  

**Customer Dissatisfaction (CD):** impact if requirement is missing:  

- 0 = No impact  
- 1 = Minor inconvenience  
- 2 = Moderate inconvenience  
- 3 = Significant negative impact  
- 4 = Major disruption  
- 5 = Critical failure / blocking  

---

## Requirement Template

| Field | Description |
| --- | --- |
| **Title** | Short, plain-language label placed as a `# Heading` on the first line of the file. Used as the display title in the requirements register. |
| **ID** | Unique identifier in the format `REQ-NN` with zero-padding computed from the total requirement count (e.g. 1–99 → two digits, 100–999 → three digits). Assigned sequentially; managed automatically by the renumber script. |
| **Type** | Functional / Non-functional / Interface / Constraint / Environmental |
| **Originator** | Person or role requesting or defining the requirement. |
| **Description** | Atomic, mandatory requirement statement using **“The system shall …”**. |
| **Rationale** | Reason why this requirement exists. |
| **Fit Criterion** | Objective, measurable condition demonstrating requirement fulfillment. |
| **Customer Satisfaction** | 0–5 scale; see CS definitions above. |
| **Customer Dissatisfaction** | 0–5 scale; see CD definitions above. |
| **Dependencies / Conflicts** | Other requirement IDs or `None`. Updated automatically by the renumber script when IDs change. |
| **Status** | Current lifecycle state: `Draft` / `Reviewed` / `Approved` / `Deprecated`. |
| **Priority** | MoSCoW classification: `Must` / `Should` / `Could` / `Won't`. Derived from CS/CD scores. See [`scripts/requirements/README.md`](../scripts/requirements/README.md). |
| **History** | `YYYY-MM-DD \| Author \| Action \| Notes` |

---

## Copy-Paste Block Format

```markdown
# [Short descriptive title]

**ID:** REQ-[number]

**Type:** [Functional / Non-functional / Interface / Constraint / Environmental]

**Originator:** [Person or role]

**Description:**
The system shall …

**Rationale:**
[Reason for requirement]

**Fit Criterion:**
- [Quantifiable, measurable criteria]

**Customer Satisfaction (0–5):**
- [Impact if implemented]

**Customer Dissatisfaction (0–5):**
- [Impact if missing]

**Dependencies / Conflicts:**
[Other requirement IDs or None]

**Status:**
Draft

**Priority:**
[Must / Should / Could / Won't]

**History:**
- YYYY-MM-DD | Author | Action | Notes
```

## Examples

### Functional Requirement

```markdown
# No-code strategy creation

**ID:** REQ-01

**Type:** Functional

**Originator:** John Doe

**Description:**
The system shall allow a user to create a trading strategy without writing code.

**Rationale:**
To enable non-programmer users to design algorithmic trading strategies independently.

**Fit Criterion:**
- A user can configure a complete strategy using graphical elements.  
- No source code modification is required.  
- The strategy can be saved after configuration.

**Customer Satisfaction (0–5):**
- 5: Non-programmers can independently create strategies, increasing adoption.

**Customer Dissatisfaction (0–5):**
- 5: Non-programmers would be unable to use the system without this feature.

**Dependencies / Conflicts:**
None

**Status:**
Approved

**Priority:**
Must

**History:**
- 2026-02-05 | John Doe | Created | Initial draft
```

### Non-functional Requirement

```markdown
# UI action response time ≤ 200 ms

**ID:** REQ-02

**Type:** Non-functional

**Originator:** Jane Doe

**Description:**
The system shall process any user-initiated action and render the updated interface within 200 milliseconds under nominal load conditions.

**Rationale:**
Response times above 200 ms are perceptible to users and degrade the perceived quality of interactive tools; maintaining this threshold ensures a fluid, professional experience.

**Fit Criterion:**
- 95% of all user-initiated actions complete and re-render within 200 ms under a simulated load of 10 concurrent users.
- No individual action exceeds 500 ms at the 99th percentile under the same conditions.
- Performance is measured via automated load test on the staging environment.

**Customer Satisfaction (0–5):**
- 4: A fast, responsive interface directly improves user confidence and productivity.

**Customer Dissatisfaction (0–5):**
- 4: Sluggish interactions would be immediately noticeable and erode trust in the tool.

**Dependencies / Conflicts:**
None

**Status:**
Approved

**Priority:**
Should

**History:**
- 2026-02-21 | Jane Doe | Created | Initial draft
- 2026-02-25 | John Doe | Approved | Requirement meets quality and traceability standards
```
