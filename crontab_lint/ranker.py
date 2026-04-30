"""Rank crontab expressions by complexity and risk."""
from dataclasses import dataclass, field
from typing import List

from crontab_lint.validator import ValidationResult
from crontab_lint.suggester import SuggestionResult


@dataclass
class RankResult:
    expression: str
    score: int
    level: str
    reasons: List[str] = field(default_factory=list)


_LEVELS = [
    (0, "simple"),
    (3, "moderate"),
    (6, "complex"),
    (9, "risky"),
]


def _level_for_score(score: int) -> str:
    level = "simple"
    for threshold, name in _LEVELS:
        if score >= threshold:
            level = name
    return level


def rank(expression: str, validation: ValidationResult, suggestions: SuggestionResult) -> RankResult:
    """Compute a complexity/risk score for a crontab expression."""
    score = 0
    reasons: List[str] = []

    if not validation.valid:
        return RankResult(
            expression=expression,
            score=10,
            level="risky",
            reasons=["Expression is invalid"],
        )

    fields = expression.strip().split()
    if len(fields) == 5:
        minute, hour, dom, month, dow = fields
    else:
        return RankResult(expression=expression, score=0, level="simple", reasons=[])

    if minute == "*" and hour == "*":
        score += 4
        reasons.append("Runs every minute")
    elif minute == "*":
        score += 2
        reasons.append("Runs every minute of the specified hour(s)")

    for f in (minute, hour, dom, month, dow):
        if "," in f:
            score += 1
            reasons.append(f"Field '{f}' uses a list")
            break

    if dom != "*" and dow != "*":
        score += 2
        reasons.append("Both day-of-month and day-of-week are restricted (OR semantics)")

    for w in validation.warnings:
        score += 1
        reasons.append(f"Warning: {w}")

    if suggestions.has_suggestions:
        score += 1
        reasons.append("Expression can be simplified with an alias")

    score = min(score, 10)
    return RankResult(
        expression=expression,
        score=score,
        level=_level_for_score(score),
        reasons=reasons,
    )
