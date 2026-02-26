# SDLC Phases Aligned with IEEE 12207 and Structured Through a V-Model

## Table of Contents

1. [SDLC Phases Aligned with IEEE 12207 and Structured Through a V-Model](#sdlc-phases-aligned-with-ieee-12207-and-structured-through-a-v-model)
2. [V-Model Structure](#v-model-structure)
3. [Development Side (System Definition)](#development-side-system-definition)

    - [1. Stakeholder Requirements Definition](#1-stakeholder-requirements-definition)
    - [2. System Requirements Definition](#2-system-requirements-definition)
    - [3. Architecture Definition](#3-architecture-definition)
    - [4. Design Definition](#4-design-definition)
    - [5. Implementation](#5-implementation)

4. [Evaluation Side (Verification and Validation)](#evaluation-side-verification-and-validation)

    - [6. Verification](#6-verification)
    - [7. Validation](#7-validation)
    - [8. Transition](#8-transition)

5. [V-Model Guarantees](#v-model-guarantees)

This document defines the Software Development Lifecycle (SDLC) structure applied in this research.  
The lifecycle is derived from ISO/IEC/IEEE 12207 (Systems and Software Engineering: Software Life Cycle Processes) and is operationalized using a V-Model structure to ensure systematic refinement, bidirectional traceability, and structured evaluation of artifacts.

The SDLC is organized into eight sequential and traceable phases:

1. Stakeholder Requirements Definition  
2. System Requirements Definition  
3. Architecture Definition  
4. Design Definition  
5. Implementation  
6. Verification  
7. Validation  
8. Transition  

Each phase transforms its input into a more concrete and operational representation. The output of one phase forms the controlled baseline for the next phase. This ensures continuity, traceability, and controlled refinement across the lifecycle.

---

## V-Model Structure

The SDLC is structured according to a V-Model consisting of two logically related sides:

- The development side (system definition)
- The evaluation side (verification and validation)

The development side refines intent into progressively more technical and concrete artifacts.  
The evaluation side examines those artifacts against their originating specifications at equivalent abstraction levels.

![V-Model SDLC Diagram](../figures/v-model.svg)

The alignment between development and evaluation activities is structured as follows:

| Development Phase                    | Evaluation Activity                  |
| ------------------------------------ | ------------------------------------ |
| Stakeholder Requirements Definition  | Acceptance Validation                |
| System Requirements Definition       | System Validation                    |
| Architecture Definition              | Integration Verification             |
| Design Definition                    | Design and Component Verification    |
| Implementation                       | Unit Verification                    |

This alignment ensures that evaluation activities are derived directly from defined development artifacts. No evaluation activity is defined independently of its originating specification.

---

## Development Side (System Definition)

### 1. Stakeholder Requirements Definition

> **Experimental scope note:** This phase is conducted once per project by the human overseer, prior to and independently of all timed experiment runs. It is excluded from the 24-hour worktime measurement (3 standard work days of 8 hours each) applied to Phases 2–8. The approved Stakeholder Requirements Specification produced here serves as the common, frozen baseline for all four approaches.

Stakeholder Requirements Definition formalizes stakeholder intent into a structured set of stakeholder requirements. This phase defines why the system exists, what objectives it must fulfill, and under which business, regulatory, operational, and environmental constraints it must operate.

Stakeholder inputs may include client interviews and notes, workshops, contractual documents, regulatory texts, domain analyses, and exploratory discussions. These inputs are analyzed to identify explicit and implicit expectations. The system boundary is defined to clearly distinguish in-scope from out-of-scope elements.

Stakeholder requirements are expressed in a solution-independent manner. They describe expected capabilities and constraints without prescribing technical realization.

#### Requirement Quality Criteria

Each stakeholder requirement must satisfy the following quality attributes:

**Atomic**  
A requirement expresses a single obligation or capability. It must not combine multiple independent conditions.  
Example of non-atomic statement:  
"The system shall store user data and encrypt communications."  
This contains two distinct obligations and must be decomposed.

**Unambiguous**  
The requirement must admit only one interpretation. Terms such as "fast", "efficient", or "user-friendly" must be replaced by measurable criteria.  
Example of ambiguous statement:  
"The system shall respond quickly."  
Rewritten as:  
"The system shall respond to user queries within 2 seconds under normal operating conditions."

**Testable**  
The requirement must be verifiable through inspection, analysis, demonstration, or testing. A requirement that cannot be objectively evaluated cannot be accepted.

**Consistent**  
The requirement must not conflict with other stakeholder requirements. Cross-review and traceability analysis are applied to detect contradictions.

**Feasible**  
The requirement must be technically and operationally achievable within defined constraints.

#### Requirement Template

To ensure uniformity and traceability, stakeholder requirements follow a structured format. A formal Requirement Specification template is maintained in the [`requirements.md`](requirements.md) file to ensure consistent documentation across case studies.

#### Outputs

- Stakeholder Requirements Specification (StRS)  
- Defined acceptance criteria  
- Unique identification scheme  
- Traceability matrix initialization  

---

### 2. System Requirements Definition

System Requirements Definition translates stakeholder requirements into a complete and technically precise set of system-level requirements.

This phase refines external expectations into observable system behavior, performance characteristics, interface definitions, and operational constraints.

System requirements are structured into:

- Functional requirements  
- Non-functional requirements  
- Interface requirements  
- Environmental and operational constraints  

Each system requirement is explicitly traceable to one or more stakeholder requirements. Traceability relationships are maintained in a formal matrix.

System requirements must satisfy the same quality attributes defined previously: atomicity, unambiguity, measurability, consistency, and feasibility.

#### Outputs

- System Requirements Specification (SyRS)  
- Stakeholder-to-system traceability mappings  
- System validation criteria  

---

### 3. Architecture Definition

Architecture Definition establishes the high-level structural organization of the system. System requirements are allocated to architectural components.

Architectural definition includes:

- Identification of subsystems and components  
- Allocation of system requirements  
- Definition of interfaces  
- Selection of architectural patterns  
- Documentation of assumptions and constraints  

Architecture Definition produces a structural baseline against which integration verification will later be conducted.

#### Outputs

- Architecture description document  
- Interface specifications  
- Requirement allocation matrix  
- Architectural decision records  

---

### 4. Design Definition

Design Definition refines architectural components into detailed technical specifications sufficient for implementation.

This includes:

- Component-level behavioral definitions  
- Data structures and schemas  
- Algorithm specifications  
- API contracts  
- Error handling mechanisms  

Design Definition establishes the baseline for design and component verification.

#### Outputs

- Detailed design documentation  
- Interface contracts  
- Data models  
- Component specifications  

---

### 5. Implementation

Implementation transforms design specifications into executable system elements.

Activities include:

- Source code development  
- Interface realization  
- Build configuration  
- Internal documentation  
- Preparation of unit verification artifacts  

Implementation produces the executable baseline that enters structured evaluation on the evaluation side of the V-Model.

#### Outputs

- Source code  
- Executable artifacts  
- Configuration files  
- Unit verification artifacts  

---

## Evaluation Side (Verification and Validation)

### 6. Verification

Verification evaluates whether development artifacts conform to their defined specifications. It assesses correctness relative to defined baselines.

Verification activities include:

- Unit Verification against Design Definition  
- Design and Component Verification against Architecture Definition  
- Integration Verification against Architecture Definition and interface specifications  

Verification may involve testing, inspection, formal review, or analytical techniques. All verification artifacts maintain traceability to development artifacts.

#### Outputs

- Verification reports  
- Test suites  
- Coverage analysis  
- Defect records  

---

### 7. Validation

Validation evaluates whether the system fulfills defined requirements and stakeholder intent within its operational context.

Validation activities include:

- System Validation against the System Requirements Specification  
- Acceptance Validation against the Stakeholder Requirements Specification  
- Operational scenario execution  
- Stakeholder evaluation sessions  

Validation establishes fitness for purpose and readiness for transition.

#### Outputs

- Validation reports  
- Acceptance records  
- Requirement satisfaction evidence  

---

### 8. Transition

Transition moves the validated system into operational use.

Activities include:

- Deployment preparation  
- Environment configuration  
- Release packaging  
- Installation procedures  
- Operational handover  
- Final acceptance confirmation  

Transition marks the formal conclusion of the development lifecycle and the beginning of operational exploitation.

#### Outputs

- Deployment artifacts  
- Release documentation  
- Operational configuration records  
- Acceptance confirmation  

---

## V-Model Guarantees

The structured V-Model ensures:

- Every development artifact is evaluated against its originating specification.  
- Evaluation activities are derived from development artifacts.  
- Detected defects can be traced to their originating phase.  
- Full bidirectional traceability is maintained from stakeholder intent to deployed system.  

This structure provides methodological rigor, controlled refinement, and evaluative coherence across the entire lifecycle.
