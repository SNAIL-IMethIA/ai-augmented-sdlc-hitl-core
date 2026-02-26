# Requirement Scripts

This package automates the maintenance of the requirements register for the AI-Augmented SDLC project. Run the full pipeline from the repository root with:

```bash
python -m scripts.requirements.main
```

By default this discovers and processes **every project folder** under `requirements/` that contains at least one `REQ-*.md` file. To target a single project, supply `--req-dir`:

```bash
python -m scripts.requirements.main --req-dir requirements/project1
```

---

## Pipeline

The pipeline runs up to four steps in order. Each step can be skipped or enabled individually via flags on `main.py`.

### Step 0 - renumber.py (on by default, `--skip-renumber`)

Detects gaps or inconsistent padding in the `REQ-NN` numeric sequence and reassigns compact sequential IDs starting from `REQ-01`.  Padding width is computed dynamically from the total requirement count (e.g. 59 requirements → two-digit padding; 100+ → three-digit), so the scheme scales naturally without manual adjustment.

For every file that needs a new ID the script rewrites both the `**ID:**` field and the `**Dependencies / Conflicts:**` field (which lists other requirement IDs this requirement is linked to). Renaming is performed in two atomic phases: all affected files are first renamed to collision-safe temporary names, then renamed to their final targets, so that sequences like REQ-59 → REQ-58 never accidentally overwrite an existing file.

Renumber runs automatically on every pipeline invocation.  Pass `--skip-renumber` to disable it.

Use the standalone entry point for a dry-run preview:

```bash
python -m scripts.requirements.renumber --dry-run
```

### Step 1 - validate.py

Checks every `REQ-*.md` file against the Volere-inspired template. It verifies that:

1. A `# Title` heading is present as the first non-blank line.
2. All mandatory bold fields are present and non-empty.
3. The `ID` field matches the filename.
4. `Type`, `Status`, and `Priority` use accepted vocabulary.
5. CS and CD scores are integers between 0 and 5.

### Step 2 - assign_priority.py

Reads each `REQ-*.md` file and derives the MoSCoW priority from the CS and CD scores using the rule below. It then writes the computed `Priority` field (and `Status: Draft` if absent) back into the file.

Priority is determined by the combined score `CS + CD`:

| Combined score (CS + CD) | CD override | Priority |
| :---: | :---: | :---: |
| >= 8 | - | Must |
| 6-7 | - | Should |
| 4-5 | - | Could |
| < 4 | - | Won't |
| any | CD == 5 | Must (forced) |

The CD == 5 override promotes any requirement whose absence causes a critical failure to Must, regardless of CS.

### Step 3 - update_register.py

Rebuilds the full requirements table and the `Total requirements:` count in the project `README.md`. All columns (ID, Title, Type, CS, CD, Status, Priority) are sourced from the `REQ-*.md` files. Title is read from each file's leading `# Heading`; the README table is fully derived from the REQ files. For files that do not yet have a title heading, the old README title cell is used as a fallback during migration.

---

## REQ file template

Every `REQ-*.md` file must follow this structure. The `# Title` heading on the first line is mandatory and is the source of truth for the register.

```markdown
# Short descriptive title

**ID:** REQ-01

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
…

**Rationale:**
…

**Fit Criterion:**

- …

**Customer Satisfaction (0–5):**

- 4: …

**Customer Dissatisfaction (0–5):**

- 3: …

**Dependencies / Conflicts:**
REQ-XX, REQ-YY

**Status:**
Draft

**Priority:**
Should

**History:**

- YYYY-MM-DD | Source | Event | Notes
```

---

## main.py options

| Flag | Description | Default |
| ---- | ----------- | ------- |
| `--req-dir PATH` | Directory containing `REQ-*.md` files | `requirements/project1` |
| `--readme PATH` | README register to update | `requirements/project1/README.md` |
| `--dry-run` | Print results without writing any files | Off |
| `--skip-renumber` | Skip Step 0 (gap-filling renumber) | Off |
| `--skip-validate` | Skip Step 1 | Off |
| `--strict-validate` | Abort if any file fails validation | Off |
| `--skip-priority` | Skip Step 2 | Off |
| `--skip-register` | Skip Step 3 | Off |

---

## Supporting modules

`models.py` defines the `Requirement` dataclass used across all modules. `parser.py` handles reading and writing individual `REQ-*.md` files, including the `# Title` heading and all bold fields. `moscow.py` is the pure function implementing the CS + CD scoring rule. `register.py` is a helper used by `assign_priority.py` for partial Priority column updates when the full register rebuild is skipped.
