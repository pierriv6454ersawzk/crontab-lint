"""Diff two crontab expressions and summarize what changed."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_lint.parser import _parse_field, CronField
from crontab_lint.explainer import _explain_field
from crontab_lint.validator import validate


FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


@dataclass
class FieldDiff:
    field: str
    old_value: str
    new_value: str
    old_explanation: str
    new_explanation: str


@dataclass
class DiffResult:
    old_expression: str
    new_expression: str
    changed_fields: List[FieldDiff] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_fields)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _split_fields(expression: str) -> Optional[List[str]]:
    """Split a cron expression into its five fields."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return None
    return parts


def diff(old_expression: str, new_expression: str) -> DiffResult:
    """Compare two crontab expressions and return a structured diff."""
    result = DiffResult(old_expression=old_expression, new_expression=new_expression)

    old_validation = validate(old_expression)
    if not old_validation.valid:
        result.errors.append(f"Old expression invalid: {'; '.join(old_validation.errors)}")

    new_validation = validate(new_expression)
    if not new_validation.valid:
        result.errors.append(f"New expression invalid: {'; '.join(new_validation.errors)}")

    if result.errors:
        return result

    old_fields = _split_fields(old_expression)
    new_fields = _split_fields(new_expression)

    if old_fields is None or new_fields is None:
        result.errors.append("Expressions must have exactly 5 fields.")
        return result

    cron_fields = list(CronField)
    for i, name in enumerate(FIELD_NAMES):
        old_val = old_fields[i]
        new_val = new_fields[i]
        if old_val != new_val:
            cf = cron_fields[i]
            old_exp = _explain_field(cf, old_val)
            new_exp = _explain_field(cf, new_val)
            result.changed_fields.append(
                FieldDiff(
                    field=name,
                    old_value=old_val,
                    new_value=new_val,
                    old_explanation=old_exp,
                    new_explanation=new_exp,
                )
            )

    return result
