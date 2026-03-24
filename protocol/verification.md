# Verification Record Template

Verification checks that a unit behaves according to its design specification. Two artifact types are used: a **Test Case** (VER-NN) records a single executable test; a **Verification Completion Report** (VCR-NN) summarises the overall verification outcome for one implementation record. Structure follows the test case and test summary report concepts of ISO/IEC 29119-3:2021.

---

## Table of Contents

1. [Identifier Scheme](#identifier-scheme)
2. [Test Case Fields (VER-NN)](#test-case-fields-ver-nn)
3. [Completion Report Fields (VCR-NN)](#completion-report-fields-vcr-nn)
4. [Copy-Paste Blocks](#copy-paste-blocks)
5. [Example](#example)
6. [References](#references)

---

## Identifier Scheme

- `VER-NN`, identifying an individual test case (e.g. `VER-01`).
- `VCR-NN`, identifying a verification completion report (e.g. `VCR-01`).

---

## Test Case Fields (VER-NN)

| Field | Description |
| --- | --- |
| **Title** | Short name for the test, as a `# Heading`. |
| **ID** | Unique identifier following the `VER-NN` scheme. |
| **Tests** | IMPL-NN of the implementation under test. |
| **Traces To** | DSGN-NN of the design element being verified. |
| **Level** | `Unit` / `Integration`. |
| **Feature Under Test** | Which interface, method, or behaviour is being tested. |
| **Inputs** | Concrete input values or preconditions. |
| **Expected Result** | The exact outcome that constitutes a pass. |
| **Actual Result** | Outcome observed when the test was last executed. `Not run` if not yet executed. |
| **Status** | `Pass` / `Fail` / `Not run`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

---

## Completion Report Fields (VCR-NN)

| Field | Description |
| --- | --- |
| **Title** | Short name for the report, as a `# Heading`. |
| **ID** | Unique identifier following the `VCR-NN` scheme. |
| **Covers** | IMPL-NN whose test cases are summarised here. |
| **Results Summary** | Count of test cases: N passed / N failed / N not run. |
| **Coverage** | Design elements covered vs total (e.g. "5 / 6 interfaces tested"). |
| **Open Anomalies** | List of VER-NN identifiers with a `Fail` status, or `None`. |
| **Outcome** | `Passed` / `Failed` / `Incomplete`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

---

## Copy-Paste Blocks

### Test Case

```markdown
# [Test name]

**ID:** VER-NN

**Tests:** IMPL-NN

**Traces To:** DSGN-NN

**Level:** [Unit / Integration]

**Feature Under Test:** [Method, endpoint, or behaviour being tested]

**Inputs:**
- [Input name]: [value or description]

**Expected Result:**
[Precise outcome that constitutes a pass.]

**Actual Result:**
Not run

**Status:** Not run

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

### Completion Report

```markdown
# [Report name]

**ID:** VCR-NN

**Covers:** IMPL-NN

**Results Summary:** [N passed / N failed / N not run]

**Coverage:** [N / N design elements tested]

**Open Anomalies:** [VER-NN list, or None]

**Outcome:** [Passed / Failed / Incomplete]

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Example

```markdown
# Authenticate (Valid Credentials)

**ID:** VER-01

**Tests:** IMPL-01

**Traces To:** DSGN-01

**Level:** Unit

**Feature Under Test:** `AuthService.authenticate` (successful login path)

**Inputs:**
- credentials: `{username: "alice", password: "correct_password"}`
- stored record: username `alice`, bcrypt hash matching `correct_password`

**Expected Result:**
Returns a `SessionToken` with a non-empty `token` field and `expires_at` set to approximately 30 minutes from call time.

**Actual Result:**
Not run

**Status:** Not run

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## References

- **[ISO/IEC 29119-3:2021]** ISO/IEC 29119-3:2021. *Software and systems engineering — Software testing — Part 3: Test documentation.* ISO, 2021.
