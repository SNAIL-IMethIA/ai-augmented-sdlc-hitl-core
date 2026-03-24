# AI-Augmented SDLC HITL Core

An IEEE 12207–Aligned Workflow for AI-Augmented Software Development: From Human-Orchestrated to Agent-Based Automation.

![Status](https://img.shields.io/badge/status-experimental-yellow) ![License](https://img.shields.io/badge/license-MIT-blue)

## Overview

AI-Augmented SDLC HITL Core is the central repository of this research which aims to evaluate and compare two AI-assisted SDLC approaches centered on human-in-the-loop orchestration versus autonomous pipeline execution.  

The repository centralizes experiment rules and documentation, while templates and project-specific code reside in separate repositories.

---

## Table of Contents

1. [Research Overview](#1-research-overview)
2. [Research Questions](#2-research-questions)
3. [SDLC Phases (V-Model)](#3-sdlc-phases-v-model)
4. [SDLC Approaches](#4-sdlc-approaches)
5. [Experimental Protocol](#5-experimental-protocol)
6. [Core Library](#6-core-library)
7. [Repositories Overview](#7-repositories-overview)
8. [Metrics & Analysis](#8-metrics--analysis)

---

## 1. Research Overview

This research explores **two AI-assisted SDLC approaches** applied to two distinct [projects](#project-1-no-code-finance-strategy-builder) on a span of **24 work hours per project (3 standard work days of 8 hours each)**:

- Human orchestrator managing multiple role-playing AI agents  
- Master AI agent or automated pipeline coordinating role-specialized agents  

Each approach is performed from scratch and goes through the [8 same SDLC phases](#3-sdlc-phases-v-model). Both approaches start from the same frozen Stakeholder Requirements Specification for the corresponding project.

---

## 2. Research Questions

These are the main questions driving the experiment. The metrics in [`protocol/metrics.md`](protocol/metrics.md) are designed with these questions in mind, but any interesting pattern or unexpected finding the data reveals is equally worth examining and reporting.

**RQ1.** How far through the SDLC can each approach realistically get within a 24-hour working budget?

**RQ2.** How does increasing AI autonomy change the human workload and how often does a person need to step in, at what moments, for what reason?

**RQ3.** Does higher AI autonomy produce better or worse artifacts in terms of prompt iterations needed, how often outputs require human editing, defect rates, and overall code quality?

**RQ4.** Does higher AI autonomy help or hurt traceability and protocol compliance across the lifecycle?

**RQ5.** Can a fully autonomous pipeline actually deliver a working, client-accepted product created from scratch while keeping human involvement limited to pre-defined checkpoints?

**RQ6.** Do the differences observed between approaches hold across different projects, or are they specific to a particular domain or problem size?

---

## 3. SDLC Phases (V-Model)

> **Note:** Phase 1 (Stakeholder Requirements Definition) is performed once per project by the human overseer, prior to and independently of all timed experiments, and is **excluded from the 24-hour worktime measurement**. Requirements are extracted and formalised from client interviews and notes. The resulting approved Stakeholder Requirements Specification serves as the common, frozen starting point for both approaches.

The SDLC is organized into eight sequential and traceable phases, aligned with ISO/IEC/IEEE 12207 and structured through a V-Model:

1. **Stakeholder Requirements Definition** *(pre-experiment, excluded from worktime)*

   - Conducted once per project by the human overseer before timed evaluation begins.
   - Formalizes stakeholder intent from client interviews and notes into structured, approved requirements.
   - Ensures requirements are atomic, unambiguous, testable, consistent, and feasible.
   - Requirements follow a formal template ([`protocol/requirements.md`](protocol/requirements.md)).

2. **System Requirements Definition**

   - Refines stakeholder requirements into technically precise system-level requirements.
   - Includes functional, non-functional, interface, and environmental constraints.

3. **Architecture Definition**

   - Establishes high-level structural organization, allocates requirements to components, and defines interfaces.

4. **Design Definition**

   - Refines architecture into detailed technical specifications for implementation.
   - Includes behavioral definitions, data models, algorithms, and API contracts.

5. **Implementation**

   - Transforms design specifications into executable system elements (source code, configuration, documentation).

6. **Verification**

   - Evaluates development artifacts against their specifications (unit, design, integration verification).
   - Ensures correctness and traceability.

7. **Validation**

   - Assesses whether the system fulfills requirements and stakeholder intent in its operational context.
   - Includes system and acceptance validation, scenario execution, and stakeholder evaluation.

8. **Transition**

   - Moves the validated system into operational use (deployment, release, handover, acceptance confirmation).

Each phase is executed in both approaches (human-orchestrated and autonomous pipeline) and emphasizes traceability, reproducibility, and systematic validation in line with the V-model SDLC workflow.

> For full details, see [`protocol/sdlc.md`](protocol/sdlc.md).

## 4. SDLC Approaches

| **Approach** | **Description** |
| :------------- | :--------------------------------------------------------------- |
| **Approach 1** | Human orchestrator with multiple role-playing agents. |
| **Approach 2** | Master agent or automated workflow/pipeline coordinating a team of role-playing agents. |

> For further information, see [`protocol/approaches.md`](protocol/approaches.md)

---

## 5. Experimental Protocol

All experiments follow the **same SDLC steps and standardized rules** to ensure fair and reproducible comparison across approaches and projects.

### Key Guidelines

- **Consistent SDLC Execution** ([details](protocol/sdlc.md))  
  Each project and approach must follow the same **8-phase SDLC workflow**, from system requirements definition to transition. Phase 1 is pre-experiment and excluded from worktime.

- **Frozen Requirements Specification** ([details](protocol/requirements.md))  
  A Stakeholder Requirements Specification is produced once per project by the human overseer, prior to all timed experiments, following the Volere-grounded template in [`protocol/requirements.md`](protocol/requirements.md). It is **finalized and immutable** before any approach begins. Both approaches start from this exact specification.

- **Standardized Interactions** ([details](protocol/interactions.md))  
  Human-AI, and AI-AI interactions are **standardized** and follow an interaction protocol that is established before development on each project starts.

- **Comparable Metrics** ([details](protocol/metrics.md))  
  Metrics are **pre-defined** and collected uniformly across both approaches. Examples include:  
  - Number of prompts or AI interactions  
  - Human override frequency  
  - Time spent per requirement or SDLC phase  
  - Quality and coverage of generated code and tests

- **Detailed Logging** ([details](protocol/logging.md))  
  All AI interactions are logged in a **structured format**, including:  
  - Prompts and AI responses  
  - Models used  
  - Date and time of each interaction  
  - Any human edits or decisions

- **Isolation of Approaches**  
  Each approach is executed in its **own repository** to prevent cross-contamination of code, prompts, or experimental artifacts.

- **Reproducibility**  
  Templates and project repositories are structured to allow **full replication** of each approach. Experiments can be rerun or audited without modification.

- **Standardized Evaluation**  
  Final analysis scripts and procedures are centralized in the main repository to **aggregate metrics consistently** across all projects and approaches.

> The goal of these rules is to provide a **rigorous framework** for evaluating AI-assisted SDLC workflows while maintaining experimental integrity, reproducibility and traceable results.

---

## 6. Core Library

The `sdlc_core` Python package (located in [`core/`](core/)) is the shared tooling library used by both approach template repositories. It provides:

- **Database setup**: `sdlc_core.db.setup_db()` creates `logs/experiment.db` with the canonical 11-table schema on first run.
- **Write helpers**: one function per event type (interaction, intervention, artifact, validation result, defect, pipeline event, violation).
- **Integrity checker**: `python -m sdlc_core.check` verifies semantic constraints that go beyond what the schema can enforce (traceability completeness, defect count consistency, phase exit criteria).
- **Metrics runner**: `python -m sdlc_core.metrics` queries the database and writes `logs/metrics_report.json` with all metric values as defined in [`protocol/metrics.md`](protocol/metrics.md).

### Pinning in template repositories

Each template repository installs `sdlc_core` at a pinned commit SHA before the run starts:

```git
sdlc-core @ git+https://github.com/SNAIL-IMethIA/ai-augmented-sdlc-hitl-core.git@{COMMIT_SHA}#subdirectory=core
```

The SHA is also written to `core_version.txt` in the template repository and committed as the first entry in the run's git log. It is never changed once a run begins.

> For full developer documentation see [`core/README.md`](core/README.md). For the database schema and logging conventions see [`protocol/logging.md`](protocol/logging.md).

---

## 7. Repositories Overview

### Templates (Scaffolding)

- [Approach 1: Human orchestrator with multiple role-playing agents](https://github.com/SNAIL-IMethIA/template-approach2-human-orchestrator)  
- [Approach 2: Master agent / AI workflow coordinating multiple agents](https://github.com/SNAIL-IMethIA/template-approach4-ai-workflow)  

### Project 1: No-code finance strategy builder

- [Approach 1: Human orchestrator with multiple role-playing agents](https://github.com/SNAIL-IMethIA/project1-approach2-human-orchestrator)  
- [Approach 2: Master agent / AI workflow coordinating multiple agents](https://github.com/SNAIL-IMethIA/project1-approach4-ai-workflow)  

### Project 2: Hotel (resort) reservation website

- [Approach 1: Human orchestrator with multiple role-playing agents](https://github.com/SNAIL-IMethIA/project2-approach2-human-orchestrator)  
- [Approach 2: Master agent / AI workflow coordinating multiple agents](https://github.com/SNAIL-IMethIA/project2-approach4-ai-workflow)  

---

## 8. Metrics & Analysis

All experiments handle their own metrics extraction in their corresponding repository according to the protocol defined in [`protocol/metrics.md`](protocol/metrics.md). Aggregation and cross-approach analysis are performed after all runs are complete.

---
