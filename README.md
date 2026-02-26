# AI-Augmented SDLC HITL Core

An IEEE 12207–Aligned Workflow for AI-Augmented Software Development: From Human-Orchestrated to Agent-Based Automation.

![Status](https://img.shields.io/badge/status-experimental-yellow) ![License](https://img.shields.io/badge/license-MIT-blue)

## Overview

AI-Augmented SDLC HITL Core is the central repository of this research which aims to evaluate and compare four different approaches to AI-assisted software development with varying degrees of human implication.  

The repository centralizes experiment rules and documentation, while templates and project-specific code reside in separate repositories.

---

## Table of Contents

1. [Research Overview](#1-research-overview)
2. [SDLC Phases (V-Model)](#2-sdlc-phases-v-model)
3. [SDLC Approaches](#3-sdlc-approaches)
4. [Experimental Protocol](#4-experimental-protocol)
5. [Repositories Overview](#5-repositories-overview)
6. [Metrics & Analysis](#6-metrics--analysis)

---

## 1. Research Overview

This research explores **four AI-assisted SDLC approaches** applied to two distinct [projects](#project-1-no-code-finance-strategy-builder) on a span of **24 work hours per project (3 standard work days of 8 hours each)**:

- Human-led development with AI as a copilot
- Human orchestrator managing multiple AI agents  
- Autonomous single AI agent  
- Master AI agent coordinating a team of agents  

Each approach is performed from scratch and goes through the [8 same SDLC phases](#2-sdlc-phases-v-model). The same frozen backlog associated with the corresponding project is used in each project.

> **Note on Phase 1:** Stakeholder Requirements Definition (Phase 1) is conducted once per project by the human overseer, prior to and independently of all timed experiments. It is excluded from the 24-hour worktime measurement. All four approaches start from the same approved stakeholder requirements, extracted and formalised from client interviews and notes.  

---

## 2. SDLC Phases (V-Model)

> **Note:** Phase 1 (Stakeholder Requirements Definition) is performed once per project by the human overseer, prior to and independently of all timed experiments, and is **excluded from the 24-hour worktime measurement**. Requirements are extracted and formalised from client interviews and notes. The resulting approved Stakeholder Requirements Specification serves as the common, frozen starting point for all four approaches.

The SDLC is organized into eight sequential and traceable phases, aligned with ISO/IEC/IEEE 12207 and structured through a V-Model:

1. **Stakeholder Requirements Definition** *(pre-experiment, excluded from worktime)*

- Conducted once per project by the human overseer before timed evaluation begins.
- Formalizes stakeholder intent from client interviews and notes into structured, approved requirements.
- Ensures requirements are atomic, unambiguous, testable, consistent, and feasible.
- Requirements follow a formal template ([`protocol/requirements.md`](protocol/requirements.md)).

1. **System Requirements Definition**

- Refines stakeholder requirements into technically precise system-level requirements.
- Includes functional, non-functional, interface, and environmental constraints.

1. **Architecture Definition**

- Establishes high-level structural organization, allocates requirements to components, and defines interfaces.

1. **Design Definition**

- Refines architecture into detailed technical specifications for implementation.
- Includes behavioral definitions, data models, algorithms, and API contracts.

1. **Implementation**

- Transforms design specifications into executable system elements (source code, configuration, documentation).

1. **Verification**

- Evaluates development artifacts against their specifications (unit, design, integration verification).
- Ensures correctness and traceability.

1. **Validation**

- Assesses whether the system fulfills requirements and stakeholder intent in its operational context.
- Includes system and acceptance validation, scenario execution, and stakeholder evaluation.

1. **Transition**

- Moves the validated system into operational use (deployment, release, handover, acceptance confirmation).

Each phase is executed in every approach (human-led, orchestrated, or autonomous) and emphasizes traceability, reproducibility, and systematic validation in line with the V-model SDLC workflow.

> For full details, see [`protocol/sdlc.md`](protocol/sdlc.md).

## 3. SDLC Approaches

| **Approach** | **Description** |
| :------------- | :--------------------------------------------------------------- |
| **Approach 1** | Human-led, AI as a copilot. |
| **Approach 2** | Human orchestrator with multiple role playing agents. |
| **Approach 3** | Single autonomous AI agent for all team roles. |
| **Approach 4** | Master agent or automated workflow/pipeline coordinating a team of role playing agents. |

> For further information, see [`protocol/approaches.md`](protocol/approaches.md)

---

## 4. Experimental Protocol

All experiments follow the **same SDLC steps and standardized rules** to ensure fair and reproducible comparison across approaches and projects.

### Key Guidelines

- **Consistent SDLC Execution** ([details](protocol/sdlc.md))  
  Each project and approach must follow the same **8-phase SDLC workflow**, from system requirements definition to transition. Phase 1 is pre-experiment and excluded from worktime.

- **Frozen Backlogs** ([details](protocol/backlog.md))  
  Project backlogs are **finalized and immutable** before development on each project starts.  
  All approaches must start from these exact requirements.

- **Standardized Interactions** ([details](protocol/interactions.md))  
  Human-AI, and AI-AI interactions are **standardized** and follow an interaction protocol that is established before development on each project starts.

- **Comparable Metrics** ([details](protocol/metrics.md))  
  Metrics are **pre-defined** and collected uniformly across all approaches. Examples include:  
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

## 5. Repositories Overview

### Templates (Scaffolding)

- [Approach 1: Human-led, AI as a copilot](https://github.com/SNAIL-IMethIA/template-approach1-human-copilot)  
- [Approach 2: Human orchestrator with multiple role playing agents](https://github.com/SNAIL-IMethIA/template-approach2-human-orchestrator)  
- [Approach 3: Single autonomous AI agent for all team roles](https://github.com/SNAIL-IMethIA/template-approach3-single-agent)  
- [Approach 4: Master agent / AI workflow coordinating multiple agents](https://github.com/SNAIL-IMethIA/template-approach4-ai-workflow)  

### Project 1: No-code finance strategy builder

- [Human-led, AI as a copilot](https://github.com/SNAIL-IMethIA/project1-approach1-human-copilot)  
- [Human orchestrator with multiple role playing agents](https://github.com/SNAIL-IMethIA/project1-approach2-human-orchestrator)  
- [Single autonomous AI agent for all team roles](https://github.com/SNAIL-IMethIA/project1-approach3-single-agent)  
- [Master agent / AI workflow coordinating multiple agents](https://github.com/SNAIL-IMethIA/project1-approach4-ai-workflow)  

### Project 2: Hotel (resort) reservation website

- [Human-led, AI as a copilot](https://github.com/SNAIL-IMethIA/project2-approach1-human-copilot)  
- [Human orchestrator with multiple role playing agents](https://github.com/SNAIL-IMethIA/project2-approach2-human-orchestrator)  
- [Single autonomous AI agent for all team roles](https://github.com/SNAIL-IMethIA/project2-approach3-single-agent)  
- [Master agent / AI workflow coordinating multiple agents](https://github.com/SNAIL-IMethIA/project2-approach4-ai-workflow)  

---

## 6. Metrics & Analysis

All experiments handle their own metrics extraction in their corresponding repository according to the protocol defined here for later **aggregation and analysis**.  

Scripts for final aggregation and analysis reside in the [`analysis/`](analysis/) folder with their results.

---
