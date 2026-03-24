# Contributing

All contributions must pass `ruff` and `mypy` with zero errors before commit.

---

## Tools

| Tool | Version | Purpose |
| ------ | --------- | --------- |
| [Python](https://docs.python.org/3.11/) | 3.11+ | Runtime |
| [Poetry](https://python-poetry.org/) | latest | Dependency and package management |
| [ruff](https://docs.astral.sh/ruff/) | ^0.9 | Linting, import sorting, docstring checks |
| [mypy](https://mypy.readthedocs.io/) | ^1.15 | Static type checking (strict mode) |
| [pytest](https://docs.pytest.org/) | ^8.0 | Test runner |
| [SQLite](https://www.sqlite.org/docs.html) | 3.x | Experiment database (`experiment.db`) |

---

## Development setup

Requires Python 3.11+ and [Poetry](https://python-poetry.org/).

```bash
# Clone and install everything. One venv at repo root covers all packages.
# sdlc-core (core/) is installed as an editable path dependency automatically.
poetry install
```

```bash
# Lint and type-check (run from repo root)
poetry run ruff check .
poetry run ruff check . --fix          # apply safe auto-fixes
poetry run mypy core/sdlc_core/ core/tests/ scripts/requirements/
```

```bash
# Run the test suite (from repo root)
# If your shell sources ROS 2, strip PYTHONPATH first to prevent
# ROS pytest plugins from crashing collection:
env -u PYTHONPATH poetry run pytest

# Without ROS 2 in your environment:
poetry run pytest
```

---

## Testing

### Running with coverage

```bash
# Show per-module coverage with missing line numbers (from repo root):
env -u PYTHONPATH poetry run pytest --cov --cov-report=term-missing

# Fail the run if coverage drops below the configured threshold (90%):
env -u PYTHONPATH poetry run pytest --cov --cov-fail-under=90
```

Coverage source and reporting are configured in `[tool.coverage.run]` and
`[tool.coverage.report]` in `pyproject.toml`.  The `fail_under = 90` threshold
is enforced automatically when `--cov` is supplied.

### Test conventions

| Convention | Detail |
| --- | --- |
| Return type | Every test function must be annotated `-> None` |
| Typed parametrize | `pytest.mark.parametrize` arguments must be fully typed |
| DB connections | Use `@contextmanager` helpers with `finally: conn.close()`. Raw `sqlite3.Connection` as a context manager does **not** close. |
| Environment / argv | Use `monkeypatch.setenv` and `monkeypatch.setattr("sys.argv", [...])` |
| Private internals | Suppress Pylance's `reportPrivateUsage` with `# pyright: ignore[reportPrivateUsage]` on the import line |
| Unreachable branches | Architecturally unreachable branches (e.g. SQLite PK violation via normal API) are documented as accepted gaps, not tested via raw SQL bypass |

### Fixtures (`core/tests/conftest.py`)

| Fixture | Scope | Description |
| --- | --- | --- |
| `db_path` | `function` | Fresh `setup_db()` database in `tmp_path` |
| `run_id` | `function` | Pre-seeded run via `open_run()` on `db_path` |
| `q_count` | n/a | Helper: `SELECT COUNT(*) FROM <table> WHERE <clause>` |
| `q_one` | n/a | Helper: `SELECT * FROM <table> WHERE <clause>` (single row) |

---

## Standards and specifications

| Standard | Enforced by | Notes |
| ---------- | ------------- | ------- |
| [PEP 8](https://peps.python.org/pep-0008/) -- Style Guide | ruff `E`/`W` | Line length: 100 characters |
| [PEP 257](https://peps.python.org/pep-0257/) -- Docstring Conventions | ruff `D` | Refined by D212, D400, D413, D415 |
| [PEP 484](https://peps.python.org/pep-0484/) -- Type Hints | mypy strict | All public functions fully annotated |
| [PEP 526](https://peps.python.org/pep-0526/) -- Variable Annotations | mypy strict | No bare generics |
| [PEP 563](https://peps.python.org/pep-0563/) -- Postponed Annotations | `from __future__ import annotations` | Required in every module |
| [PEP 572](https://peps.python.org/pep-0572/) -- Assignment Expressions | allowed | Use sparingly and only when clarity improves |
| [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | ruff `D` | Docstring section format (Args/Returns/Raises) |
| [IEEE 12207:2017](https://www.iso.org/standard/63712.html) | protocol/ docs | SDLC process model the experiment targets |

---

## Python conventions (quick reference)

### File header

The **module docstring** is the first thing in every `.py` file. It gives
tools (IDEs, `pydoc`, documentation generators) a machine-readable description
of the module's purpose without executing any code.

[`from __future__ import annotations`](https://peps.python.org/pep-0563/)
must appear immediately after. It switches Python's annotation evaluation from
eager (evaluated at import time) to lazy (stored as strings and resolved only
when needed). This removes all forward-reference problems -- you can annotate
`def fn() -> MyClass` before `MyClass` is defined -- and it makes the type
annotations zero-cost at runtime.

```python
"""module.py: One-line summary ending with a period."""

from __future__ import annotations
```

### Docstrings -- [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

```python
def fn(path: Path, *, dry_run: bool = False) -> list[str]:
    """One-line summary ending with a period.

    Args:
        path:    Path to the file to process.
        dry_run: When True, no files are modified.

    Returns:
        List of human-readable result strings.

    Raises:
        FileNotFoundError: If ``path`` does not exist.

    """
```

- D212: summary on the same line as the opening `"""`.
- D400/D415: summary ends with a period.
- D413: blank line required before the closing `"""` when sections are present.
- All public classes (including `Enum` subclasses) need a class-level docstring.

### Type annotations

All public functions must be fully annotated (mypy strict mode):

- No bare generics: `list[str]`, `dict[str, Any]`, never bare `list` or `dict`.
- No `Any` in public signatures without justification.
- Use `datetime.UTC` (not `timezone.utc`) for timezone-aware datetimes.
- After `cursor.execute(INSERT ...)`, assert `cursor.lastrowid is not None`
  before returning it as `int`.

### Imports

Groups separated by a blank line, sorted alphabetically within each group:

1. `from __future__ import annotations`
2. Standard library
3. Third party
4. First party / internal

### Punctuation in source text

Use plain ASCII in all code, comments, and docstrings:

- Hyphen `-` for compound words and ranges (not en-dash or em-dash).
- `...` for literal ellipsis (not the Unicode character).
- Semicolon `;` or a new sentence to join independent clauses (not em-dash).

Exception: field-name strings that must match REQ template content verbatim
(e.g. `"Customer Satisfaction (0-5)"` in `validate.py`) are left unchanged.

### Section banners

```python
# ---------------------------------------------------------------------------
# Section name
# ---------------------------------------------------------------------------
```

### Entry points

```python
def main() -> None:
    """Parse arguments and run the pipeline."""
    ...

if __name__ == "__main__":
    main()
```

---

## Commit conventions

```text
type(scope): short imperative summary

Body if needed. Wrap at 72 characters.
```

Common types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.  
Scope examples: `db`, `check`, `metrics`, `enums`, `parser`, `protocol`.

Each commit must leave ruff and mypy clean.
