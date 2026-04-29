"""Suggest fixes or improvements for crontab expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .validator import ValidationResult


@dataclass
class Suggestion:
    message: str
    replacement: str | None = None


@dataclass
class SuggestionResult:
    original: str
    suggestions: List[Suggestion] = field(default_factory=list)

    @property
    def has_suggestions(self) -> bool:
        return bool(self.suggestions)


_COMMON_REPLACEMENTS = {
    "* * * * *": ("@every-minute", "Use @every-minute alias for clarity"),
    "0 * * * *": ("@hourly", "Use @hourly alias instead"),
    "0 0 * * *": ("@daily", "Use @daily alias instead"),
    "0 0 * * 0": ("@weekly", "Use @weekly alias instead"),
    "0 0 1 * *": ("@monthly", "Use @monthly alias instead"),
    "0 0 1 1 *": ("@yearly", "Use @yearly alias instead"),
}


def _suggest_alias(expression: str) -> Suggestion | None:
    entry = _COMMON_REPLACEMENTS.get(expression.strip())
    if entry:
        replacement, message = entry
        return Suggestion(message=message, replacement=replacement)
    return None


def _suggest_slash_one(expression: str) -> list[Suggestion]:
    suggestions = []
    parts = expression.split()
    for part in parts:
        if "/1" in part:
            suggestions.append(
                Suggestion(
                    message=f"Field '{part}' uses '/1' which is redundant; consider removing the step.",
                    replacement=None,
                )
            )
    return suggestions


def _suggest_from_warnings(validation: ValidationResult) -> list[Suggestion]:
    suggestions = []
    for warning in validation.warnings:
        suggestions.append(Suggestion(message=f"Warning: {warning}"))
    return suggestions


def suggest(expression: str, validation: ValidationResult) -> SuggestionResult:
    """Generate suggestions for a crontab expression."""
    result = SuggestionResult(original=expression)

    alias_suggestion = _suggest_alias(expression)
    if alias_suggestion:
        result.suggestions.append(alias_suggestion)

    result.suggestions.extend(_suggest_slash_one(expression))
    result.suggestions.extend(_suggest_from_warnings(validation))

    return result
