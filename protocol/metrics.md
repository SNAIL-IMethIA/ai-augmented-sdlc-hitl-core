# Evaluation metrics

## Table of Contents

1. [Introduction](#introduction)
2. [Phase reach rate](#phase-reach-rate)
3. [Traceability](#traceability)
4. [Governance rules](#governance-rules)
5. [Human effort](#human-effort)
6. [Time effort](#time-effort)
7. [Defects](#defects)
8. [Prompt refinements](#prompt-refinements)
9. [Requirements coverage](#requirements-coverage)
10. [Code coverage](#code-coverage)
11. [Complexity](#complexity)
12. [Architectural completeness and dependencies](#architectural-completeness-and-dependencies)
13. [Defect-origin mappings](#defect-origin-mappings)
14. [Deployment rate and client acceptance ratio](#deployment-rate-and-client-acceptance-ratio)
15. [Static analysis](#static-analysis)

## Introduction

This document defines the evaluation metrics collected across both approaches of this research. Metrics are pre-defined and locked before any experiment begins. They may not be added, removed, or redefined during or after execution. This ensures that findings can be compared across approaches and projects in a fair, reproducible, and auditable manner.

Metrics are designed to capture four primary dimensions of interest, namely development quality, human effort, automation dynamics, and traceability. Where applicable, raw counts are normalized to enable meaningful cross-domain comparison despite differences in project scope and complexity.

Normalization bases used throughout this document include:

- per requirement
- per artifact
- per SDLC phase
- per 1,000 lines of code (kLOC)

Not every approach will complete all eight SDLC phases within the 24-hour time budget. **All metrics in this document are computed exclusively over the phases actually reached by a given approach.** A metric for a phase that was not reached returns `N/A` for that approach and is excluded from cross-approach averages for that metric. The set of phases reached is itself reported first, as the Phase reach rate metric.

> Interaction logs and human intervention records, which serve as the primary data source for several of the metrics defined here, are governed by the [interaction guidelines](interactions.md). The database schema that stores these records is defined in [logging.md](logging.md).

---

## Phase reach rate

Phase reach rate is the primary headline metric of the study. It measures how far each approach progresses through the SDLC within the 24-hour time budget and is reported before all other metrics.

- **Terminal phase**: the last SDLC phase (Phases 2–8) for which at least one artifact was completed and accepted within the time budget.
- **Phase reach count**: the number of phases fully completed within the time budget. A phase is fully completed when all required artifacts for that phase have been accepted.
- **Phase reach profile**: a per-approach record showing, for each of Phases 2–8, one of three states: `Completed`, `Partially reached` (entered but not all artifacts accepted), or `Not reached`.

$$\text{Phase Reach Rate} = \frac{\text{phases fully completed}}{7} \times 100$$

This metric is the primary basis for comparing the productivity ceiling of each approach. For example, Approach 1 reaching Phase 5 while Approach 2 reaches Phase 8 is a concrete, standalone finding independent of artifact quality metrics.

> This metric informs **RQ1**.

---

## Traceability

Traceability metrics measure the degree to which artifacts are explicitly linked to their upstream sources across SDLC phases.

**Traceability coverage rate** is the percentage of artifacts for which all required upstream dependencies have been declared:

$$\text{Traceability Coverage} = \frac{\text{artifacts with complete upstream links}}{\text{total artifacts produced}} \times 100$$

This metric is computed at each phase transition and recorded in the traceability matrix maintained throughout the lifecycle. A traceability gap is defined as any artifact missing at least one declared upstream dependency.

Derived from the same matrix, two linkage rates expose coverage gaps before they reach deployment.

- **Requirement-to-design linkage rate**: the percentage of system requirements linked to at least one architectural or design artifact.
- **Requirement-to-test linkage rate**: the percentage of system requirements linked to at least one test case.

Both must reach 100% before the deployment phase is authorized to begin.

> This metric informs **RQ4**.

---

## Governance rules

Governance compliance measures adherence to the structural and procedural rules defined in the interaction guidelines, artifact naming conventions, coding conventions, and prompt standards.

**Governance compliance rate** is computed per artifact:

$$\text{Compliance Rate} = \frac{\text{compliant artifacts}}{\text{total artifacts}} \times 100$$

A violation is recorded when an artifact does not conform to at least one mandatory rule. Each violation type corresponds to a distinct layer of the governance rules. The `violation_type` values used in the `violations` table for each category are indicated in parentheses.

- **Prompt structure violations** (`prompt_structure_violation`): a prompt was missing one or more required sections of the structured template (persona, task, input artifacts, context scope, output template, acceptance criteria).
- **Artifact format violations** (`fit_criterion_failure`): an artifact does not conform to its required template or fails a declared acceptance criterion.
- **Logging violations** (`missing_required_field`): an interaction, intervention, or validation result was not recorded at the time it occurred, or was recorded with a required field missing.
- **Naming violations** (`schema_constraint_failure`): an artifact does not follow the declared identifier scheme.

Violation counts are reported as a raw total per approach and normalized per artifact.

> This metric informs **RQ4**.

---

## Human effort

Human effort metrics capture the volume and nature of human involvement across all SDLC phases. Alongside the raw totals, per-phase, per-artifact, and per-category breakdowns reveal where within the lifecycle and within which intervention types the effort concentrates.

- **Total intervention count**: the total number of logged human interventions across the full experiment.
- **Intervention count per SDLC phase**: the distribution of interventions across phases, revealing where human involvement concentrates.
- **Intervention count per requirement**: total interventions normalized by the number of requirements in scope.
- **Intervention count per artifact**: total interventions normalized by the total number of produced artifacts.
- **Intervention count by category**: breakdown across clarification, correction, rejection, strategic decision, safety override, manual edit, environment fix, and other. The `manual_edit` category is particularly significant when comparing Approach 1 against Approach 2, as it records effort that generates no prompt log entry.
- **Intervention count by severity**: breakdown across minor, moderate, and critical.

> Intervention logging procedures and category definitions are defined in the [interventions table](logging.md#interventions).
> This metric informs **RQ2**.

---

## Time effort

Time effort metrics capture how human working time is distributed across approaches and phases. Rather than a single cumulative total, time expenditure is granularized so that phase-level and artifact-level comparisons remain valid even when overall project scope differs between approaches.

- **Total human time per approach**: sum of all logged human time across all phases and interventions.
- **Time per SDLC phase**: human time logged within each phase, enabling phase-level comparison.
- **Time per requirement**: total human time normalized by requirement count.
- **Time per artifact**: total human time normalized by the number of artifacts produced.
- **Time per kLOC**: total human time normalized per 1,000 lines of code, applicable during implementation and verification phases.
- **Time to first accepted artifact per phase**: a measure of AI responsiveness and prompt effectiveness within a given phase.

Time is recorded in minutes. All measurements are derived from interaction logs and human intervention records, both of which include a timestamp on every entry.

> Timestamp logging procedures are defined in the [interactions table](logging.md#interactions).
> This metric informs **RQ2**.

---

## Defects

Defect metrics capture the density, severity, and distribution of errors detected during verification and validation activities. Individual defects are recorded in the `defects` table in the experiment database; the `validation_results` table holds the session-level summary. All sub-metrics below derive from queries over those two tables.

- **Defect density per requirement**: total defects normalized by requirement count.
- **Defect density per kLOC**: total defects normalized per 1,000 lines of code.
- **Defect density per artifact**: total defects normalized by artifact count.
- **Defect severity distribution**: breakdown of defects by severity (minor, moderate, critical).
- **Defect detection phase**: the SDLC phase in which each defect was formally identified.
- **Defect resolution time**: the elapsed time between defect detection and resolution, recorded in minutes.

A defect is defined as any deviation from the acceptance criteria defined for an artifact, detected during a validation or verification activity and recorded in a validation log.

> Defect records are collected through the [validation_results table](logging.md#validation_results).
> This metric informs **RQ3** and **RQ5**.

---

## Prompt refinements

Prompt refinement metrics capture how many iterations were required to produce an accepted artifact, reflecting the effectiveness of prompts and the degree of AI alignment with task expectations. Speed of convergence and residual correction burden are jointly tracked across four indicators.

- **Iteration count per artifact**: the number of prompt-response cycles required before an artifact was accepted.
- **Average iteration count per phase**: the mean number of iterations across all artifacts produced in a given SDLC phase.
- **Rejection rate**: the percentage of prompts that resulted in a fully rejected output requiring a complete re-prompt.
- **Modification rate**: the percentage of accepted outputs that required human modification before acceptance.

All three indicators are derived from the prompt logs, where each refinement iteration is recorded as a separate entry linked to the same artifact identifier.

> Prompt logging procedures are defined in the [interactions table](logging.md#interactions).
> This metric informs **RQ3**.

---

## Requirements coverage

Requirements coverage measures the extent to which stakeholder and system requirements are addressed by downstream artifacts. Starting from stakeholder goals and ending at executed test results, completeness is verified at each level of the requirements hierarchy.

- **Stakeholder-to-system requirements coverage**: the percentage of stakeholder requirements explicitly addressed by at least one system-level requirement.
- **System requirements test coverage**: the percentage of system requirements linked to at least one executed test case.
- **Untested requirement count**: the absolute number of system requirements with no associated passing test at the time of validation.

Both indicators are sourced from the traceability matrix and test execution records.

> This metric informs **RQ4**.

---

## Code coverage

How thoroughly the test suite exercises the source code is evaluated at three stacked levels of granularity, ascending from raw line execution through conditional branching up to per-requirement test passage.

- **Line coverage**: the percentage of executable source lines executed by at least one test.
- **Branch coverage**: the percentage of conditional branches exercised by at least one test.
- **Requirement-level coverage**: the percentage of system requirements for which at least one associated test has passed.

Coverage data is produced by the test execution toolchain and stored alongside test suite artifacts.

> This metric informs **RQ3**.

---

## Complexity

Well-functioning AI-generated code is not only correct but maintainable. Control-flow complexity and cognitive readability are therefore both quantified, at the granularity of individual functions, aggregated at module level, and normalized against the requirement set.

- **Cyclomatic complexity**: computed per function or method. Both the average and maximum values are reported per module and per release.
- **Cognitive complexity**: where supported by static analysis tooling, cognitive complexity is reported as a supplementary indicator of code readability.
- **Complexity per requirement**: the average cyclomatic complexity of code modules that directly implement a given requirement, normalized across the requirement set.

High complexity values are flagged for manual review and any resulting refactoring intervention is logged accordingly.

> This metric informs **RQ3**.

---

## Architectural completeness and dependencies

Architecture phase completion is gated on three verifiable structural properties. Every requirement must be allocated to at least one component, every declared interface must have a corresponding specification, and the component dependency graph must be acyclic.

- **Requirement allocation rate**: the percentage of system requirements allocated to at least one architectural component.
- **Interface definition completeness**: the percentage of declared component interfaces that have a corresponding specification.
- **Cyclic dependency count**: the number of cyclic dependencies detected between components at architecture review time.

A requirement allocation rate below 100% at the end of the architecture phase is treated as a phase-level defect and prevents progression to design definition.

> This metric informs **RQ4**.

---

## Defect-origin mappings

Defect-origin mapping tracks which SDLC phase introduced each detected defect, enabling analysis of error propagation across the lifecycle. Beyond confirming that a defect exists, these measurements establish where it originated and how many phases it crossed before being detected.

- **Defect origin distribution**: the percentage of defects attributed to each SDLC phase.
- **Error propagation depth**: for each defect, the number of SDLC phases traversed between the phase of introduction and the phase of detection.
- **Mean propagation depth**: the average error propagation depth across all detected defects.
- **Late-detection rate**: the percentage of defects detected two or more phases after their phase of origin.

Origin is established by cross-referencing each defect record with the phase in which the flawed artifact was produced, using the traceability matrix.

> This metric informs **RQ3** and **RQ4**.

---

## Deployment rate and client acceptance ratio

Delivery success is appraised across five indicators that together capture whether deployment happened, how autonomously it happened, how much effort it required, and whether the client accepted the result. These indicators are particularly important for comparing Approach 2 (fully automated pipeline) against Approach 1 (human orchestrator).

- **Deployment automation level**: the declared automation level of the transition, as recorded in the TRANS artifact: `Fully automated`, `Human-assisted`, or `Manual`. Reported per approach, not as a rate.
- **Deployment attempt count**: the total number of deployment attempts required before the release was accepted, including failed attempts. A count above 1 indicates a deployment failure occurred and contributes to failure analysis.
- **Successful deployment rate**: the percentage of deployment attempts (across all retry attempts per release) that completed without critical errors. A release requiring two attempts has a 50% attempt-level success rate.
- **Client acceptance ratio**: the percentage of stakeholder requirements confirmed as satisfied by the client during acceptance validation.
- **Time to accepted deployment**: the elapsed time in minutes from the first deployment attempt to the accepted deployment, as recorded in the TRANS artifact.

> This metric informs **RQ5**.

---

## Static analysis

Static analysis metrics are collected over the source code produced during implementation, using automated analysis tooling applied at each significant code checkpoint. Tooling output is grouped into four categories.

- **Warning count by severity**: the total number of static analysis findings, broken down by severity level (error, warning, informational).
- **Warning count by category**: findings grouped by type (e.g., null dereference, unused variable, security vulnerability, style violation).
- **Violations per kLOC**: total static analysis warnings normalized per 1,000 lines of code.
- **Evolution across iterations**: the change in violation count between successive code iterations, measuring whether AI-generated code improves or degrades in quality over refinement cycles.

Static analysis is run on the final artifact of each implementation iteration and results are stored as part of the artifact metadata.

> This metric informs **RQ3**.
