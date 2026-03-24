# Interaction guidelines

## Table of Contents

1. [Introduction](#introduction)
2. [Standards for human-AI interactions](#standards-for-human-ai-interactions)
3. [Standards for AI-AI interactions](#standards-for-ai-ai-interactions)
4. [Data and governance references](#data-and-governance-references)
5. [References](#references)

## Introduction

This document defines the interaction guidelines that govern all human-AI and AI-AI exchanges throughout the research. These guidelines apply uniformly across both approaches and ensure that interactions are structured, traceable, and reproducible.

Interactions are treated as first-class empirical data. Every prompt, response, refinement, and human intervention is logged, categorized, and associated with a specific SDLC phase and artifact, making human involvement a measurable and comparable variable across approaches.

The guidelines are locked before any experiment run begins and may not be modified during execution. Any deviation must be recorded as a protocol deviation.

**Design principle.** The per-phase interaction contract pre-resolves every prompt dimension before execution begins. The five locked dimensions are persona, input artifacts, pattern, CoT requirement, and output schema. No prompt engineering decision is left to runtime judgment. This makes runs comparable within and across approaches. Observed differences in artifact quality are attributable to the approach, not to choices made at the time of prompting.

> For metrics derived from interactions, see [metrics.md](metrics.md). For approach-specific interaction ownership and pipeline governance rules, see [approaches.md](approaches.md).

---

## Standards for human-AI interactions

Three rules apply universally across both approaches:

1. All AI-produced outputs must be reviewed and explicitly accepted, modified, or rejected by the human overseer before use as input to a subsequent phase. Accepted outputs with modifications must have those modifications recorded in the interaction log.
2. Every interaction, regardless of form, must be logged in full using the schema defined in [logging.md](logging.md).
3. Every accepted artifact must be committed to version control immediately upon acceptance as a single isolated commit before work on the next artifact begins. Commit messages must follow the convention `[ARTIFACT-ID]: [short description], phase [N]`.

The prompt format is structured in both approaches to preserve cross-run comparability. The difference between approaches is not prompt schema; it is execution ownership (human-orchestrated versus autonomous pipeline).

### Model declaration and control

The AI model must be declared and locked before the first experiment run begins. The same model name and version must be used across both approaches for a given project. Any finding attributing a difference in output quality, iteration count, or defect density to an approach is valid only if the model is held constant. The declared model is recorded in the `model` field of every interaction log entry. A run in which more than one model version is used within the same phase must be flagged as a protocol deviation in the `violations` table.

### Structured prompt template (both approaches)

Every prompt in Approach 1 and Approach 2 must conform to the following template [[White et al., 2023](https://arxiv.org/abs/2303.07839); [Amatriain, 2024](https://arxiv.org/abs/2401.14423)]. No section may be omitted; if a section does not apply, it must be stated explicitly rather than left blank.

```markdown
## PERSONA
You are a [role, e.g. requirements analyst / software architect / developer / tester].
Act solely in this capacity for the duration of this interaction.

## TASK
[Single, atomic statement of what the AI must produce or evaluate.
Express one obligation only. Do not compound multiple tasks in this section.]

## INPUT ARTIFACTS
The following artifacts are provided as input to this task:

- [ARTIFACT-ID-1]: [brief description; full content or reference below]
- [ARTIFACT-ID-2]: [brief description; full content or reference below]

[Paste or attach full artifact content here, labelled by identifier.]

## CONTEXT SCOPE
In scope: [Explicit list of phases, artifacts, constraints, or domains the AI may draw on.]
Out of scope: [Explicit list of what must be ignored or excluded from this response.]

## OUTPUT TEMPLATE
Produce your response using the following structure exactly:

[Copy the artifact schema from the protocol document for the current SDLC phase here.
Do not modify field names, headings, or structure. See the phase-to-schema table
in the interactions protocol for the correct source document.]

## ACCEPTANCE CRITERIA
Your output will be accepted only if it satisfies all of the following:

1. [Criterion 1, stated as a measurable and testable condition]
2. [Criterion 2, stated as a measurable and testable condition]
3. [Add criteria as required]

[Include the following section only when the artifact type requires it -- see contract table.]
## CHAIN-OF-THOUGHT INSTRUCTION
Before producing your final output, reason step by step through [specific reasoning
required, e.g. the requirements, constraints, tradeoffs]. Present your reasoning
explicitly under a "Reasoning" heading, then present your final output under the
field headings copied into the Output Template above.
```

### Artifact schema sources

The `OUTPUT TEMPLATE` section must be populated with the canonical artifact schema for the active phase, copied verbatim. The table below maps each artifact type to its schema source. This mapping is fixed and may not be overridden at the prompt level.

| SDLC phase | Artifact type | Schema source |
| --- | --- | --- |
| Stakeholder Requirements Definition | Requirement | Copy-Paste Block Format in [requirements.md](requirements.md) (pre-experiment, governed by [requirements.md](requirements.md) exclusively) |
| System Requirements Definition | System Requirement (`REQ-NN`) | Copy-Paste Block Format in [requirements.md](requirements.md) |
| Architecture Definition | Architecture Note (`ARCH-VIEW-NN`) | Copy-Paste Block in the Architecture Note section of [architecture.md](architecture.md) |
| Architecture Definition | Architectural Decision Record (`ARCH-ADR-NN`) | Copy-Paste Block in the Architectural Decision Record section of [architecture.md](architecture.md) |
| Design Definition | Design Specification (`DSGN-NN`) | Copy-Paste Block in [design.md](design.md) |
| Implementation | Implementation Record (`IMPL-NN`) | Copy-Paste Block in [implementation.md](implementation.md) |
| Verification | Test Case (`VER-NN`) | Test Case Copy-Paste Block in [verification.md](verification.md) |
| Verification | Verification Completion Report (`VCR-NN`) | Completion Report Copy-Paste Block in [verification.md](verification.md) |
| Validation | Validation Record (`VAL-NN`) | Copy-Paste Block in [validation.md](validation.md) |
| Transition | Transition Record (`TRANS-NN`) | Copy-Paste Block in [transition.md](transition.md) |

In both approaches, the canonical schema defines the required output form and is copied verbatim into the structured prompt template.

### Per-phase interaction contract

The table below is the concrete content of SOPs used by both approaches. Each row locks five variables per artifact type: the declared persona, the mandatory input artifacts, the mandatory prompt pattern, the Chain-of-Thought requirement, and the output schema source. All five variables are fixed before any experiment run begins and may not be overridden at runtime [[Hong et al., 2024](https://openreview.net/forum?id=VtmBAGCN7o); [Qian et al., 2024](https://arxiv.org/abs/2307.07924)].

| Artifact type | Declared persona | Mandatory inputs (INPUT ARTIFACTS) | Mandatory pattern | CoT | Output schema source |
| --- | --- | --- | --- | --- | --- |
| System Requirement (`REQ-NN`) | Requirements analyst | Relevant accepted stakeholder requirements (`REQ-NN` from StRS) | (none beyond base template) | absent | [requirements.md](requirements.md) |
| Architecture Note (`ARCH-VIEW-NN`) | Software architect | All accepted system requirements (`REQ-NN` from SyRS) | (none beyond base template) | absent | [architecture.md](architecture.md) |
| Architectural Decision Record (`ARCH-ADR-NN`) | Software architect | Relevant `REQ-NN` from SyRS + relevant `ARCH-VIEW-NN` | **Three-turn structured sequence** | mandatory | [architecture.md](architecture.md) |
| Design Specification (`DSGN-NN`) | Software designer | Relevant `ARCH-VIEW-NN` + relevant `ARCH-ADR-NN` | **Recipe** | mandatory | [design.md](design.md) |
| Implementation Record (`IMPL-NN`) | Software developer | Corresponding `DSGN-NN` | **Recipe** | absent | [implementation.md](implementation.md) |
| Test Case (`VER-NN`) | Software tester | Corresponding `IMPL-NN` + originating `DSGN-NN` | (none beyond base template) | absent | [verification.md](verification.md) |
| Verification Completion Report (`VCR-NN`) | Quality assurance engineer | All `VER-NN` for the corresponding `IMPL-NN` | (none beyond base template) | absent | [verification.md](verification.md) |
| Validation Record (`VAL-NN`) | Validation engineer | Relevant `REQ-NN` from SyRS + all accepted `VCR-NN` | (none beyond base template) | absent | [validation.md](validation.md) |
| Transition Record (`TRANS-NN`) | Deployment engineer | All accepted `VAL-NN` + accepted artifacts from all prior phases | (none beyond base template) | absent | [transition.md](transition.md) |

The declared persona must appear verbatim in `## PERSONA`. The mandatory inputs define the minimum set for `## INPUT ARTIFACTS`. Additional upstream artifacts may be included when relevant. The mandatory pattern name and CoT status must be recorded in the `prompt` field of every interaction log entry.

**Recipe** replaces the single-sentence TASK with an ordered numbered list of sub-tasks, each expressing one obligation [[DiCuffa et al., 2025](https://arxiv.org/abs/2506.01604)]. No other section of the template changes.

**Three-turn structured sequence** produces three log entries under the same `artifact_id` [[Maranhão & Guerra, 2024](https://dl.acm.org/doi/10.1145/3698322.3698324)]. Turn 1 enumerates candidate options and evaluation criteria. Turn 2 compares options against each criterion. Turn 3 synthesizes the decision. PERSONA, INPUT ARTIFACTS, CONTEXT SCOPE, and ACCEPTANCE CRITERIA remain constant across all three turns. TASK and OUTPUT TEMPLATE are updated each turn to reflect the current sub-goal. CoT is mandatory and the `## CHAIN-OF-THOUGHT INSTRUCTION` section must appear in each turn. The ADR is not considered complete until the third turn is accepted.

---

## Standards for AI-AI interactions

> **Scope:** Role declaration and SOPs apply to both approaches. Structured communication, communicative dehallucination, and conversation programming apply whenever distinct agents hand off output to one another. Autonomous pipeline governance applies to Approach 2 and is defined in [approaches.md](approaches.md).

### Role declaration and Standardized Operating Procedures

Before any agent produces output, it must declare the role it is currently performing. Each role is governed by a pre-defined SOP [[Hong et al., 2024](https://openreview.net/forum?id=VtmBAGCN7o)] that specifies the responsibilities, permitted upstream artifacts, required output schema, and acceptance criteria for that role. SOPs are locked before experiments begin and may not be modified at runtime.

In both approaches, each role transition must be explicitly declared in the prompt. The transition is logged as a role-change event and treated as a boundary between two distinct interaction units.

### Structured communication and message schemas

All inter-agent communication is mediated through structured, typed artifact handoffs [[Hong et al., 2024](https://openreview.net/forum?id=VtmBAGCN7o)]. Each role's SOP defines the output schema and the set of fields the consuming agent receives. This subscription-based filtering prevents information overload from irrelevant upstream context. An agent may only consume artifacts produced and validated at a prior step. It may not infer or hallucinate upstream context that was not explicitly passed to it.

### Communicative dehallucination

Within each binary agent interaction, the communicative dehallucination mechanism [[Qian et al., 2024](https://arxiv.org/abs/2307.07924)] must be applied to all artifacts that serve as inputs to a subsequent phase:

1. The assistant produces a candidate output per its SOP.
2. The instructor reviews the candidate against the SOP acceptance criteria and either approves it or raises a specific, structured objection.
3. The assistant revises the output or provides a justified defense.
4. This continues until consensus is reached or a maximum turn count is exceeded, at which point the conflict is escalated as a validation failure.

All turns are logged as part of the artifact's prompt chain.

### Conversation programming and workflow declaration

The complete inter-agent workflow must be specified as a declarative conversation program [[Wu et al., 2024](https://openreview.net/forum?id=BAakY1hNKS)] before execution begins, defining the ordered sequence of agent interactions, the conversation pattern for each, the termination conditions, and the artifact handoff schema. No agent may modify the workflow at runtime. Workflow modifications are human-level decisions and constitute logged interventions. In Approach 2, the conversation program is the machine-readable pipeline protocol and must be stored in version control [[Dibia et al., 2024](https://arxiv.org/abs/2408.15247)].

---

## Data and governance references

The following documents govern data collection, artifact identity, and traceability. None of these rules are repeated here.

| Concern | Document |
| --- | --- |
| Interaction log schema, intervention schema, validation result schema, pipeline event log, artifact table | [logging.md](logging.md) |
| Artifact identifiers, traceability requirements, V-Model phase exit criteria | [sdlc.md](sdlc.md) |
| Autonomous pipeline governance for Approach 2 (pipeline contract, validation gates, circuit breakers, human re-entry points) | [approaches.md](approaches.md) |

---

## References

- **[Qian et al., 2024]** Chen Qian, Wei Liu, Hongzhang Liu, et al. [*ChatDev: Communicative Agents for Software Development.*](https://arxiv.org/abs/2307.07924) ACL 2024.
- **[Wu et al., 2024]** Qingyun Wu, Gagan Bansal, Jieyu Zhang, et al. [*AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversations.*](https://openreview.net/forum?id=BAakY1hNKS) COLM 2024.
- **[Hong et al., 2024]** Sirui Hong, Mingchen Zhuge, Jonathan Chen, et al. [*MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework.*](https://openreview.net/forum?id=VtmBAGCN7o) ICLR 2024 (Oral).
- **[Amatriain, 2024]** Xavier Amatriain. [*Prompt Design and Engineering: Introduction and Advanced Methods.*](https://arxiv.org/abs/2401.14423) arXiv:2401.14423.
- **[White et al., 2023]** Jules White, Sam Hays, Quchen Fu, Jesse Spencer-Smith, Douglas C. Schmidt. [*ChatGPT Prompt Patterns for Improving Code Quality, Refactoring, Requirements Elicitation, and Software Design.*](https://arxiv.org/abs/2303.07839) arXiv:2303.07839.
- **[Maranhão & Guerra, 2024]** João José Maranhão and Eduardo Martins Guerra. [*A Prompt Pattern Sequence Approach to Apply Generative AI in Assisting Software Architecture Decision-making.*](https://dl.acm.org/doi/10.1145/3698322.3698324) EuroPLoP 2024.
- **[DiCuffa et al., 2025]** Sophia DiCuffa, Amanda Zambrana, Priyanshi Yadav, et al. [*Exploring Prompt Patterns in AI-Assisted Code Generation: Towards Faster and More Effective Developer-AI Collaboration.*](https://arxiv.org/abs/2506.01604) arXiv:2506.01604.
- **[Dibia et al., 2024]** Victor Dibia, Jingya Chen, Gagan Bansal, et al. [*AutoGen Studio: A No-Code Developer Tool for Building and Debugging Multi-Agent Systems.*](https://arxiv.org/abs/2408.15247) arXiv:2408.15247.
