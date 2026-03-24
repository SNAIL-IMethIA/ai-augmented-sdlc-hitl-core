# Implementation Record Template

An Implementation Record links a design specification to the source code that realises it. The key outcomes of an implementation process (ISO/IEC 12207:2017 §6.4.7) are traceability from design to code, a buildable and testable unit, and a clear record of what was implemented and verified.

---

## Table of Contents

1. [Identifier Scheme](#identifier-scheme)
2. [Fields](#fields)
3. [Copy-Paste Block](#copy-paste-block)
4. [Example](#example)
5. [References](#references)

---

## Identifier Scheme

`IMPL-NN`, where NN is a zero-padded sequential number. Example: `IMPL-01`.

---

## Fields

| Field | Description |
| --- | --- |
| **Title** | Short name for the implemented unit, as a `# Heading`. |
| **ID** | Unique identifier following the `IMPL-NN` scheme. |
| **Realises** | ID of the Design Specification this implementation fulfils (e.g. `DSGN-01`). |
| **Source File** | Relative path(s) to the primary source file(s). |
| **Language / Framework** | Programming language and any relevant framework or runtime version. |
| **Description** | Two to four sentences summarising what was implemented and any notable deviation from the design. Note "Implemented as designed" if no deviations. |
| **Traceability** | Table mapping each design element (interface, data structure, algorithm) to the concrete code location. |
| **Verification Artifacts** | IDs of VER records that exercise this implementation (e.g. `VER-01, VER-02`). Populate after verification artifacts are created. |
| **Status** | `Draft` / `Approved` / `Deprecated`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

---

## Copy-Paste Block

```markdown
# [Component name]

**ID:** IMPL-NN

**Realises:** DSGN-NN

**Source File:** `[path/to/file.ext]`

**Language / Framework:** [Language, version / Framework, version]

**Description:**
[What was implemented. Note any deviation from the design, or state "Implemented as designed."]

**Traceability:**

| Design Element | Code Location |
| --- | --- |
| [Interface / method / structure name] | `[file.ext:ClassName.methodName]` |

**Verification Artifacts:** [VER-NN, …]

**Status:** Draft

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Example

```markdown
# User Authentication Service

**ID:** IMPL-01

**Realises:** DSGN-01

**Source File:** `src/auth/authentication_service.py`

**Language / Framework:** Python 3.12 / FastAPI 0.110

**Description:**
Implements the `authenticate` and `invalidate` endpoints defined in DSGN-01. Bcrypt hashing is performed via the `bcrypt` library; token signing uses PyJWT HS256. Implemented as designed; no deviations.

**Traceability:**

| Design Element | Code Location |
| --- | --- |
| `authenticate` interface | `authentication_service.py:AuthService.authenticate` |
| `invalidate` interface | `authentication_service.py:AuthService.invalidate` |
| `Credentials` structure | `models.py:Credentials` |
| `SessionToken` structure | `models.py:SessionToken` |
| Bcrypt hash comparison algorithm | `authentication_service.py:AuthService._verify_password` |

**Verification Artifacts:** VER-01, VER-02

**Status:** Draft

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## References

- **[ISO/IEC 12207:2017]** ISO/IEC 12207:2017. *Systems and software engineering — Software life cycle processes.* ISO, 2017. §6.4.7 Software implementation process.
