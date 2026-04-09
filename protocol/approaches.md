# Two Approaches to AI-Assisted Development

## Table of Contents

1. [Introduction](#introduction)
2. [Approach 1: Human orchestrator with multiple role-playing agents](#approach-1-human-orchestrator-with-multiple-role-playing-agents)
3. [Approach 2: Master agent or automated pipeline](#approach-2-master-agent-or-automated-pipeline)

---

## Introduction

The experiment compares two deliberately different execution modes for the same SDLC protocol.

- **Approach 1** keeps the human in active control of each interaction while using role-specialized AI agents.
- **Approach 2** moves execution to an autonomous pipeline where human involvement is constrained to explicit supervision and re-entry points.

This framing isolates the core research axis of interest: **human-in-the-loop orchestration versus autonomous pipeline operation** under identical SDLC artifacts, checks, and metrics.

> Interaction standards (prompt template, per-phase contract, AI-AI rules) are defined in [interactions.md](interactions.md). Metrics are defined in [metrics.md](metrics.md). Data schemas are in [logging.md](logging.md).
> Daily execution flow and checkpoint operations are defined in [runbook.md](runbook.md).

---

## Approach 1: Human orchestrator with multiple role-playing agents

This approach uses structured, role-based prompting. Agents are specialized and each role-plays a specific development team role exclusively. For example, during implementation, one agent may role-play as developer while another role-plays as tester.

**Prompt format.** Every prompt must conform to the structured template defined in [interactions.md](interactions.md). All five locked variables (persona, inputs, pattern, CoT, output schema) are resolved per the per-phase interaction contract before each prompt is composed.

**Human role.** The human operates as orchestrator. They construct every prompt, submit it to the appropriate agent, review outputs, accept or reject them, and pass accepted artifacts to the next role.

**AI involvement.** Every agent interaction is human-initiated. There is no autonomous chaining. This guarantees a human-in-the-loop at every interaction boundary.

**Interaction capture.** Every agent call in Approach 1 must be submitted through `LoggedProvider`. The orchestrator enters the outcome judgment interactively so no exchange is omitted from the experiment log.

---

## Approach 2: Master agent or automated pipeline

This approach introduces full autonomy by chaining role-specialized agents in an automated workflow. The pipeline starts from system requirements and advances across SDLC phases with minimal human interruption.

**Prompt format.** Prompts conform to the structured template in [interactions.md](interactions.md) and are composed by the master agent or pipeline orchestrator, not by the human.

**Human role.** The human overseer monitors pipeline execution and is required only at declared re-entry points or when circuit-breaker conditions trigger a halt.

**AI involvement.** The pipeline is the active operator. Human involvement is supervisory, boundary-crossing, and failure-recovery only.

### Pipeline contract

Before autonomous execution begins, a pipeline contract must be authored and frozen. The contract defines ordered agent roles, artifact schemas at each handoff, validation rules, retry limits, and escalation actions. The contract is versioned and may not be modified by agents at runtime.

### Validation gates

At every handoff, a validation gate must pass before the consuming agent is invoked. The gate evaluates structural conformance, completeness, traceability, and format compliance. A gate failure halts the pipeline, records the failure, and triggers the contract-defined escalation action.

### Observation interfaces

The pipeline must expose observation interfaces so the human can inspect current execution position, most recent handoff artifact, latest gate result, and running retry and escalation counts without interrupting execution. Observation data is captured in the interaction and pipeline logs defined in [logging.md](logging.md).

### Circuit breaker conditions

The pipeline must halt automatically and transfer control to the human when any of the following occur:

- a single agent exceeds maximum retry count,
- the same artifact is gate-rejected three or more times consecutively,
- an agent output contains an explicit uncertainty declaration or refusal,
- a required upstream artifact reference cannot be resolved,
- total pipeline execution time exceeds declared timeout.

No data produced after a circuit-breaker trigger is committed until the human explicitly resumes or redirects execution.

### Human re-entry points

The pipeline contract must declare explicit human re-entry points at SDLC phase boundaries at minimum. These are hard barriers. The pipeline cannot traverse them without logged human approval. Additional re-entry points may be declared at high-risk handoffs.
