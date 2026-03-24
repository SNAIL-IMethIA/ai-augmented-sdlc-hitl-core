# Design Specification Template

A Design Specification translates an Architecture Note into a concrete description of a single component: what it does, what interfaces it exposes, and why it is designed the way it is. The essential fields (type, purpose, interface, rationale) are drawn from the core design entity attributes of IEEE 1016-2009. Produce one artifact per architectural component that requires independent specification.

---

## Table of Contents

1. [Identifier Scheme](#identifier-scheme)
2. [Fields](#fields)
3. [Copy-Paste Block](#copy-paste-block)
4. [Example](#example)
5. [References](#references)

---

## Identifier Scheme

`DSGN-NN`, where NN is a zero-padded sequential number. Example: `DSGN-01`.

---

## Fields

| Field | Description |
| --- | --- |
| **Title** | Short name for this component, as a `# Heading`. |
| **ID** | Unique identifier following the `DSGN-NN` scheme. |
| **Type** | `Module`, `Class`, `Service`, `Interface`, or `Data Store`. |
| **Implements** | ID of the Architecture Note this design refines (e.g. `ARCH-VIEW-01`). |
| **Purpose** | One to three sentences: what this component does and why it exists. |
| **Interfaces** | Table of all exposed operations: method/endpoint, inputs, outputs, and any key pre/post conditions. |
| **Data Structures** | Key data types this component owns or exchanges. Omit if none. |
| **Dependencies** | Other components or external services this component calls. Reference by DSGN-NN or name. |
| **Rationale** | Why this design was chosen. Enough to reconstruct the decision intent, not exhaustive. |
| **Status** | `Draft` / `Approved` / `Deprecated`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

---

## Copy-Paste Block

```markdown
# [Component name]

**ID:** DSGN-NN

**Type:** [Module / Class / Service / Interface / Data Store]

**Implements:** ARCH-VIEW-NN

**Purpose:**
[What this component does and why it exists.]

**Interfaces:**

| Method / Endpoint | Inputs | Outputs | Notes |
| --- | --- | --- | --- |
| [name] | [params] | [return type] | [preconditions or error cases] |

**Data Structures:**

| Structure | Field | Type | Notes |
| --- | --- | --- | --- |
| [Name] | [field] | [type] | [constraint or N/A] |

**Dependencies:**
- [Component or service name (DSGN-NN or external)]: [nature of dependency]

**Rationale:**
[Why this design was chosen.]

**Status:** Draft

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Example

```markdown
# User Authentication Service

**ID:** DSGN-01

**Type:** Service

**Implements:** ARCH-VIEW-01

**Purpose:**
Validates user credentials against stored password hashes and issues signed JWT session tokens. Also provides a session invalidation endpoint.

**Interfaces:**

| Method / Endpoint | Inputs | Outputs | Notes |
| --- | --- | --- | --- |
| POST /auth/authenticate | `{username, password}` | `{token, expires_at}` | Returns 401 if credentials do not match |
| POST /auth/invalidate | `{token}` (bearer) | `204 No Content` | Token remains valid until expiry (30 min) |

**Data Structures:**

| Structure | Field | Type | Notes |
| --- | --- | --- | --- |
| Credentials | username | string | Max 128 chars, non-empty |
| Credentials | password | string | Never logged or stored in plaintext |
| SessionToken | token | string | Signed JWT, HS256 |
| SessionToken | expires_at | ISO 8601 datetime | 30 minutes from issuance |

**Dependencies:**
- User Repository (DSGN-02): reads stored credential records via `findByUsername`.

**Rationale:**
JWT issuance is kept within this service to limit the secret key surface. Stateless token validation means downstream services do not need to call back to this service on every request.

**Status:** Draft

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## References

- **[IEEE 1016-2009]** IEEE 1016-2009. *IEEE Standard for Information Technology — Systems Design — Software Design Descriptions.* IEEE, 2009.
