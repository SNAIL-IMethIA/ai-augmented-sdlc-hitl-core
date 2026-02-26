# Export results (CSV, PDF)

**ID:** REQ-41

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow a user to export backtest and optimisation results in at least two standard file formats.

**Rationale:**
Exportable results enable users to archive, share, and perform further analysis outside the tool using familiar applications.

**Fit Criterion:**

- Results can be exported to at least CSV and PDF formats.
- Exported files contain all metrics displayed in the in-application results view.
- Export completes within 10 seconds for any results dataset produced by the system.

**Customer Satisfaction (0–5):**

- 3: Convenient for record-keeping, reporting, and external analysis.

**Customer Dissatisfaction (0–5):**

- 5: Users can manually transcribe results, but this is time-consuming and error-prone.

**Dependencies / Conflicts:**
REQ-31, REQ-34, REQ-61

**Status:**
Approved

**Priority:**
Must

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call
- 2026-02-26 | Kevin Schweitzer | Updated | Added REQ-61 dependency; result history entries should also be exportable
