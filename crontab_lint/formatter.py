"""Formatters for cron lint results (text and JSON)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from crontab_lint.validator import ValidationResult
from crontab_lint.schedule import ScheduleResult


def _result_to_dict(result: ValidationResult) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "expression": result.expression,
        "valid": result.valid,
    }
    if result.error:
        d["error"] = result.error
    if result.warnings:
        d["warnings"] = result.warnings
    if result.explanation:
        d["explanation"] = result.explanation
    return d


def _schedule_to_dict(schedule: ScheduleResult) -> Dict[str, Any]:
    return {
        "next_runs": [dt.isoformat() for dt in schedule.next_runs],
        "error": schedule.error,
    }


class TextFormatter:
    def format(
        self,
        result: ValidationResult,
        schedule: Optional[ScheduleResult] = None,
    ) -> str:
        lines: List[str] = []
        status = "OK" if result.valid else "INVALID"
        lines.append(f"[{status}] {result.expression}")
        if result.error:
            lines.append(f"  Error   : {result.error}")
        for w in result.warnings or []:
            lines.append(f"  Warning : {w}")
        if result.explanation:
            lines.append(f"  Meaning : {result.explanation}")
        if schedule and schedule.ok and schedule.next_runs:
            lines.append("  Next runs:")
            for dt in schedule.next_runs:
                lines.append(f"    - {dt.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)


class JsonFormatter:
    def format(
        self,
        result: ValidationResult,
        schedule: Optional[ScheduleResult] = None,
    ) -> str:
        d = _result_to_dict(result)
        if schedule:
            d["schedule"] = _schedule_to_dict(schedule)
        return json.dumps(d, indent=2)
