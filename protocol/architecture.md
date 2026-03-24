# Architecture Artifact Templates

Architecture artifacts capture the structural organisation of the system and the decisions behind it. Two artifact types are defined, inspired by the C4 model (Brown, 2018) for lightweight component decomposition and the ADR format (Nygard, 2011) for traceable decision recording. Both types are produced during Phase 3 (Architecture Definition) and serve as the upstream traceability anchors for all design and implementation artifacts.

---

## Table of Contents

1. [Artifact Types](#artifact-types)
2. [Architecture Note](#architecture-note)
3. [Architectural Decision Record](#architectural-decision-record)
4. [References](#references)

---

## Artifact Types

| Type | Identifier | Purpose |
| --- | --- | --- |
| Architecture Note | `ARCH-VIEW-NN` | Describes the structural organisation of the system or a subsystem: components, responsibilities, and interfaces. |
| Architectural Decision Record (ADR) | `ARCH-ADR-NN` | Records a single architecture decision: options evaluated, choice made, rationale, and accepted tradeoffs. |

---

## Architecture Note

### Identifier Scheme

`ARCH-VIEW-NN`, where NN is a zero-padded sequential number. Example: `ARCH-VIEW-01`.

### Fields

| Field | Description |
| --- | --- |
| **Title** | Short name for this view, as a `# Heading`. |
| **ID** | Unique identifier following the `ARCH-VIEW-NN` scheme. |
| **Viewpoint** | The concern this view addresses: `Structural`, `Deployment`, `Interface`, or `Data`. |
| **Allocated Requirements** | IDs of the requirements this view addresses. At least one. |
| **Components** | Table of components in this view: name, single responsibility, provided interfaces, required interfaces. |
| **Rationale** | Why this structure was chosen. Sufficient detail to understand the decision context, without full justification. |
| **Status** | `Draft` / `Approved` / `Deprecated`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

### Copy-Paste Block

```markdown
# [Short title]

**ID:** ARCH-VIEW-NN

**Viewpoint:** [Structural / Deployment / Interface / Data]

**Allocated Requirements:**
- REQ-NN: [brief description]

**Components:**

| Component | Responsibility | Provides | Requires |
| --- | --- | --- | --- |
| [Name] | [Single responsibility] | [Interface(s)] | [Interface(s)] |

**Rationale:**
[Why this structure was chosen.]

**Status:** Draft

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Architectural Decision Record

### Identifier Scheme

`ARCH-ADR-NN`, sequential and never reused even when superseded. Example: `ARCH-ADR-01`.

### Fields

| Field | Description |
| --- | --- |
| **Title** | Short noun phrase naming the decision, as a `# Heading`. |
| **ID** | Unique identifier following the `ARCH-ADR-NN` scheme. |
| **Context** | Why a decision was needed. What forces or constraints made it non-trivial. |
| **Options Considered** | At least two named options with a brief description each. |
| **Decision** | The chosen option, stated in one sentence. |
| **Rationale** | Why this option was chosen over the others. |
| **Consequences** | What becomes easier or harder as a result. Both sides of the tradeoff. |
| **Status** | `Proposed` / `Accepted` / `Deprecated` / `Superseded by ARCH-ADR-NN`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

### Copy-Paste Block

```markdown
# [Decision title]

**ID:** ARCH-ADR-NN

**Context:**
[Why this decision was needed. What constraints or forces made it non-trivial.]

**Options Considered:**
- [Option A]: [brief description]
- [Option B]: [brief description]

**Decision:**
[Option X], because [brief justification].

**Rationale:**
[Why this option is preferred over the others.]

**Consequences:**
- Positive: [what this makes easier or better]
- Negative: [tradeoff or cost accepted]

**Status:** Proposed

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Example

### Architecture Note

```markdown
# System Component Overview

**ID:** ARCH-VIEW-01

**Viewpoint:** Structural

**Allocated Requirements:**
- REQ-01: The system shall allow users to create trading strategies without writing code.
- REQ-05: The system shall persist strategy configurations across sessions.

**Components:**

| Component | Responsibility | Provides | Requires |
| --- | --- | --- | --- |
| Strategy Builder UI | Renders the no-code editor and captures user input | Web interface | REST API |
| Strategy Service | Validates and persists strategy configurations | REST API (`/strategies`) | Database |
| Database | Stores user accounts and strategy data | Query interface | none |

**Rationale:**
Three-tier separation allows each layer to be implemented and tested independently, which is important given that different approaches may generate them in different orders. No shared state between UI and service keeps the integration surface minimal.

**Status:** Draft

**History:**
- 2026-03-03 | Architect Agent | Created
```

### Architectural Decision Record

```markdown
# REST API for frontend-backend communication

**ID:** ARCH-ADR-01

**Context:**
The UI and the Strategy Service must communicate. The mechanism chosen affects deployment independence and testing complexity.

**Options Considered:**
- REST over HTTP: stateless, easy to test in isolation, widely supported.
- WebSocket: lower latency but adds connection state management with no benefit for discrete CRUD operations.

**Decision:**
REST over HTTP, because strategy operations are discrete and stateless, and each tier can be tested independently without managing persistent connections.

**Rationale:**
Stateless HTTP fits the CRUD nature of strategy management. WebSocket complexity is not justified by the requirements and would add implementation burden for both approaches.

**Consequences:**
- Positive: each tier starts, stops, and is tested independently.
- Negative: real-time push notifications would require an additional mechanism if ever needed.

**Status:** Accepted

**History:**
- 2026-03-03 | Architect Agent | Created
- 2026-03-03 | Human Overseer | Accepted
```

---

## References

- **[Brown, 2018]** Simon Brown. *The C4 Model for Visualising Software Architecture.* [https://c4model.com/](https://c4model.com/)
- **[Nygard, 2011]** Michael Nygard. *Documenting Architecture Decisions.* [https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
