"""moscow.py: MoSCoW priority derivation from CS/CD scores.

This module contains the sole authoritative definition of the rule that maps
Customer Satisfaction (CS) and Customer Dissatisfaction (CD) scores to a
MoSCoW priority label.  All other modules delegate to this module; the rule
must never be duplicated elsewhere.

Rule (in priority order):
    1. CD == 5               → Must   (critical-failure override)
    2. CS + CD >= 8          → Must
    3. CS + CD >= 6          → Should
    4. CS + CD >= 4          → Could
    5. CS + CD  < 4          → Won't

Rationale:
    The CD override on rule 1 ensures that any requirement whose absence
    causes a critical failure is always treated as Must, regardless of how
    useful its presence is perceived to be.  This prevents a high-CS /
    low-CD requirement from ever outranking a stakeholder blocker.

    The combined-score thresholds on rules 2–5 reflect a symmetric view of
    value: both the benefit of implementation and the cost of omission are
    weighted equally when neither score is at its extreme.
"""

from __future__ import annotations

MOSCOW_LABELS: tuple[str, ...] = ("Must", "Should", "Could", "Won't")


def compute(cs: int, cd: int) -> str:
    """Derive a MoSCoW priority label from CS and CD scores.

    Args:
        cs: Customer Satisfaction score, integer in [0, 5].
        cd: Customer Dissatisfaction score, integer in [0, 5].

    Returns:
        One of ``"Must"``, ``"Should"``, ``"Could"``, or ``"Won't"``.

    Raises:
        ValueError: If either score is outside the range [0, 5].

    Examples:
        >>> compute(5, 5)
        'Must'
        >>> compute(3, 2)
        'Could'
        >>> compute(1, 5)
        'Must'
        >>> compute(1, 1)
        "Won't"

    """
    if not (0 <= cs <= 5 and 0 <= cd <= 5):
        raise ValueError(
            f"CS and CD must each be in [0, 5]; received CS={cs}, CD={cd}."
        )

    if cd == 5:
        return "Must"

    combined = cs + cd
    if combined >= 8:
        return "Must"
    if combined >= 6:
        return "Should"
    if combined >= 4:
        return "Could"
    return "Won't"
