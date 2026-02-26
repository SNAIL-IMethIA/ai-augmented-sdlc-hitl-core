"""
Package: scripts.requirements

Tools for managing Volere-inspired requirement files (REQ-*.md).

Modules:
    models          : Requirement dataclass representing a parsed REQ file.
    parser          : Functions for reading and writing REQ-*.md files.
    moscow          : MoSCoW priority derivation from CS/CD scores.
    validate        : Structural integrity checks against the Volere template.
    register        : Functions for updating the README Priority column only.
    update_register : Rebuild the full README register table + total count.

Scripts (CLI entry points):
    renumber        : Gap-filling sequential renumber of REQ-*.md files after
                      a deletion, with dependency-reference rewriting.
    assign_priority : Compute MoSCoW priorities, write to REQ files, and
                      update the README Priority column.
    update_register : Rebuild the complete README register table from REQ
                      files and update the "Total requirements:" count.
    main            : Orchestrator: renumber (opt) → validate → assign_priority
                      → update_register.
"""
