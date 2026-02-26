# Import strategy from file

**ID:** REQ-51

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow the user to import a previously exported strategy from a file into the strategy library.

**Rationale:**
Import enables users to share strategies across installations, restore from backups, and collaborate by exchanging strategy files outside the platform.

**Fit Criterion:**

- A strategy file saved by the system (see REQ-09) can be re-imported and appears in the strategy library without loss of parameters, blocks, or configuration.
- An import from an unrecognised or malformed file surfaces a clear error message and does not corrupt the library.

**Customer Satisfaction (0–5):**

- 3: Useful for sharing and portability but not blocking for core usage.

**Customer Dissatisfaction (0–5):**

- 2: Users can recreate strategies manually; inconvenient but not critical.

**Dependencies / Conflicts:**
REQ-05, REQ-09

**Status:**
Approved

**Priority:**
Could

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
