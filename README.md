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

This research explores **four AI-assisted SDLC approaches** applied to two projects:

- Human-led development with AI as a copilot
- Human orchestrator managing multiple AI agents  
- Autonomous single AI agent  
- Master AI agent coordinating a team of agents  

Each approach is performed from scratch and goes through the [7 same SDLC phases](#2-sdlc-phases-v-model). The same frozen backlog associated with the corresponding project is used in each project.  

---

## 2. SDLC Phases (V-Model)

> **Note:** Initial requirements are always obtained by the human overseer to ensure full understanding. These validated requirements serve as the starting point for all approaches.

### 1. Requirements Analysis

- Elicit, analyze, and validate the needs and constraints of the system with stakeholders or clients.
- Produce a clear, structured set of functional and non-functional requirements.

### 2. User Story Extraction / Requirement Refinement

- Break down high-level requirements into actionable user stories, use cases, or functional units.
- Ensure traceability between requirements and user stories.

### 3. Technical Specification

- Define detailed technical specifications, including interfaces, data models, and quality attributes.
- Serve as the bridge between requirements and design.

### 4. Architecture Design

- Design the high-level structure of the system, including components, their responsibilities, and interactions.
- Document architectural decisions and rationale.

### 5. Implementation

- Develop source code and related artifacts according to the specifications and architecture.
- Perform unit-level verification to ensure each component meets its design.

### 6. Verification & Validation (Testing & QA)

- Verify that the system and its components meet specifications (verification).
- Validate that the final product fulfills the original requirements (validation).
- Includes unit, integration, system, and acceptance testing.

### 7. Deployment

- Prepare and transition the validated system into its target environment.
- Ensure readiness for release and operational use.

Each phase is executed in every approach (human-led, orchestrated, or autonomous) and emphasizes traceability, reproducibility, and systematic validation in line with the V-model SDLC workflow.

> For further information, see [`protocol/sdlc.md`](protocol/sdlc.md)

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
  Each project and approach must follow the same **7-step SDLC workflow**, from requirements analysis to deployment and post-execution evaluation.

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

- [Approach 1: Template](#)  
- [Approach 2: Template](#)  
- [Approach 3: Template](#)  
- [Approach 4: Template](#)  

### Project 1: No-code finance strategy builder

- [Human-led, AI as a copilot.](#)  
- [Human orchestrator with multiple role playing agents.](#)  
- [Single autonomous AI agent for all team roles.](#)  
- [Master agent or automated workflow/pipeline coordinating a team of role playing agents.](#)  

### Project 2: Hotel (resort) reservation website

- [Human-led, AI as a copilot.](#)  
- [Human orchestrator with multiple role playing agents.](#)  
- [Single autonomous AI agent for all team roles.](#)  
- [Master agent or automated workflow/pipeline coordinating a team of role playing agents.](#)  

---

## 6. Metrics & Analysis

All experiments handle their own metrics extraction in their corresponding repository according to the protocol defined here for later **aggregation and analysis**.  

Scripts for final aggregation and analysis reside in the [`analysis/`](analysis/) folder with their results.

---
