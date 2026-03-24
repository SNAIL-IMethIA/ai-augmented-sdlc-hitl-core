# Validation Record Template

A Validation Record confirms that the deployed system satisfies the user requirement it was built to meet. Where verification asks "was it built right?", validation asks "was the right thing built?" (ISO/IEC 12207:2017 §6.4.9). Each record traces a complete acceptance scenario from requirement to observed outcome.

---

## Table of Contents

1. [Identifier Scheme](#identifier-scheme)
2. [Fields](#fields)
3. [Copy-Paste Block](#copy-paste-block)
4. [Example](#example)
5. [References](#references)

---

## Identifier Scheme

`VAL-NN`, where NN is a zero-padded sequential number. Example: `VAL-01`.

---

## Fields

| Field | Description |
| --- | --- |
| **Title** | Short name for the scenario, as a `# Heading`. |
| **ID** | Unique identifier following the `VAL-NN` scheme. |
| **Level** | `System` (full system under test) or `Acceptance` (against user-agreed criteria). |
| **Validates** | REQ-NN of the requirement under validation. |
| **Scenario** | Brief narrative description of the situation being validated. |
| **Procedure** | Numbered steps to execute the scenario. |
| **Expected Outcome** | The observable result that constitutes acceptance. |
| **Result** | Observed outcome. `Not run` if not yet executed. |
| **Evidence** | Link, screenshot filename, or log reference supporting the result. `None` if not yet run. |
| **Executed By / On** | Name or role and ISO 8601 date of execution. `pending` if not yet run. |
| **Status** | `Pass` / `Fail` / `Not run`. |
| **History** | `YYYY-MM-DD \| Author/Agent \| Action` |

---

## Copy-Paste Block

```markdown
# [Scenario name]

**ID:** VAL-NN

**Level:** [System / Acceptance]

**Validates:** REQ-NN

**Scenario:**
[One to three sentences describing the situation being validated.]

**Procedure:**
1. [Step 1]
2. [Step 2]
3. [Continue as required]

**Expected Outcome:**
[Observable result that constitutes acceptance.]

**Result:**
Not run

**Evidence:** None

**Executed By / On:** pending

**Status:** Not run

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## Example

```markdown
# User Login (Valid Credentials)

**ID:** VAL-01

**Level:** System

**Validates:** REQ-05

**Scenario:**
A registered user submits correct credentials via the login form. The system should authenticate the user and redirect them to their dashboard within the defined response time.

**Procedure:**
1. Open the application and navigate to `/login`.
2. Enter username `alice` and the correct password.
3. Click the "Sign in" button.
4. Observe the response.

**Expected Outcome:**
The user is redirected to `/dashboard` and a valid session cookie is set. The response completes in under 2 seconds.

**Result:**
Not run

**Evidence:** None

**Executed By / On:** pending

**Status:** Not run

**History:**
- YYYY-MM-DD | [Author/Agent] | Created
```

---

## References

- **[ISO/IEC 12207:2017]** ISO/IEC 12207:2017. *Systems and software engineering — Software life cycle processes.* ISO, 2017. §6.4.9 Software validation process.
