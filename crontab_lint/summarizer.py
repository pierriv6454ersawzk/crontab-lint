"""Summarize multiple crontab expressions into a statistical report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_lint.validator import validate
from crontab_lint.suggester import has_suggestions, suggest


@dataclass
class SummaryResult:
    total: int
    valid: int
    invalid: int
    with_suggestions: int
    invalid_expressions: List[str] = field(default_factory=list)
    suggestion_expressions: List[str] = field(default_factory=list)

    @property
    def valid_pct(self) -> float:
        return round(self.valid / self.total * 100, 1) if self.total else 0.0

    @property
    def invalid_pct(self) -> float:
        return round(self.invalid / self.total * 100, 1) if self.total else 0.0

    @property
    def suggestion_pct(self) -> float:
        return round(self.with_suggestions / self.total * 100, 1) if self.total else 0.0


def summarize(expressions: List[str]) -> SummaryResult:
    """Analyse a list of crontab expression strings and return a summary."""
    total = len(expressions)
    valid_count = 0
    invalid_count = 0
    suggestion_count = 0
    invalid_exprs: List[str] = []
    suggestion_exprs: List[str] = []

    for expr in expressions:
        expr = expr.strip()
        if not expr:
            continue
        vr = validate(expr)
        if vr.valid:
            valid_count += 1
            sr = suggest(vr)
            if has_suggestions(sr):
                suggestion_count += 1
                suggestion_exprs.append(expr)
        else:
            invalid_count += 1
            invalid_exprs.append(expr)

    return SummaryResult(
        total=total,
        valid=valid_count,
        invalid=invalid_count,
        with_suggestions=suggestion_count,
        invalid_expressions=invalid_exprs,
        suggestion_expressions=suggestion_exprs,
    )
