# Transition Record Template

A Transition Record captures the research-observable properties of deploying a validated release into its target environment. The goal is not to document *how* a specific technology is operated, as that is project-specific and irrelevant to the research, but to record the outcomes that differ between approaches: whether deployment was automated or manual, how many attempts it took, what failed and why, and whether the client accepted the result. Structure is aligned with ISO/IEC 12207:2017 §6.4.10.

---

## Table of Contents

1. [Identifier Scheme](#identifier-scheme)
2. [Fields](#fields)
3. [Copy-Paste Block](#copy-paste-block)
4. [Example](#example)
5. [References](#references)

---

## Identifier Scheme

`TRANS-NN`, where NN is a zero-padded sequential number. Example: `TRANS-01`.

---

## Fields

| Field | Description |
| --- | --- |
| **Title** | Short name for the release, as a `# Heading`. |
| **ID** | Unique identifier following the `TRANS-NN` scheme. |
| **Release Tag** | Version identifier or VCS tag for the released artefact (e.g. `v1.0.0`). Technology-agnostic; use whatever versioning scheme the project employs. |
| **Validation Evidence** | VAL-NN identifiers whose `Pass` outcomes authorise this release. |
| **Automation Level** | One of: `Fully automated` (deployment was triggered and completed without human intervention, typical of Approach 2); `Human-assisted` (automated scripts ran but required human decisions or corrections at one or more steps); `Manual` (all deployment steps were performed directly by the human overseer). |
| **Attempt Count** | Total number of deployment attempts made, including failed ones, before the release was accepted. |
| **Failure Summary** | For each failed attempt: a brief description of what failed and the identified cause. `None` if the first attempt succeeded. |
| **Time to Accepted Deployment** | Elapsed time in minutes from the first deployment attempt to the accepted deployment. |
| **Acceptance Confirmation** | Name or role of the person who accepted the release, and ISO 8601 date. `pending` if not yet accepted. |
| **Status** | `Planned` / `Deployed` / `Accepted` / `Rolled back`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

---

## Copy-Paste Block

```markdown
# [Release name]

**ID:** TRANS-NN

**Release Tag:** [vX.Y.Z or equivalent]

**Validation Evidence:** [VAL-NN, …]

**Automation Level:** [Fully automated / Human-assisted / Manual]

**Attempt Count:** [N]

**Failure Summary:**
[Description of each failed attempt and its cause, or None.]

**Time to Accepted Deployment:** [N minutes]

**Acceptance Confirmation:** pending

**Status:** Planned

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Example

```markdown
# Release v1.0.0

**ID:** TRANS-01

**Release Tag:** v1.0.0

**Validation Evidence:** VAL-01, VAL-02, VAL-03

**Automation Level:** Human-assisted

**Attempt Count:** 2

**Failure Summary:**
- Attempt 1: deployment script failed during the database migration step due to a missing environment variable (`DB_HOST`) in the production configuration. Cause: configuration file not updated before deployment.
- Attempt 2: succeeded.

**Time to Accepted Deployment:** 34 minutes

**Acceptance Confirmation:** Jane Doe (client representative) / 2026-03-03

**Status:** Accepted

**History:**
- 2026-03-03 | [Author/Agent] | Created
- 2026-03-03 | [Author/Agent] | Updated after second deployment attempt
- 2026-03-03 | Jane Doe | Accepted
```

---

## References

- **[ISO/IEC 12207:2017]** ISO/IEC 12207:2017. *Systems and software engineering — Software life cycle processes.* ISO, 2017. §6.4.10 Software transition process.
