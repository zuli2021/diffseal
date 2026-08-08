"""Ruff collector.

Semantics:

- no lint violations (exit 0)       -> PASS
- lint violations (exit non-zero)   -> FAIL
- Ruff unavailable/unexecutable     -> ERROR

Ruff is invoked with ``--output-format=json`` for concise, parseable findings.
"""

from __future__ import annotations

import json
from pathlib import Path

from diffseal.collectors.base import Collector, check_result, truncate_findings
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome, CheckResult, Finding
from diffseal.process import resolve_tool, run_process


class RuffCollector(Collector):
    collector_id = "ruff"
    distribution_name = "ruff"

    def collect(self, check: CheckConfig, cwd: Path, timeout: float) -> CheckResult:
        tool = resolve_tool("ruff")
        if tool is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                0.0,
                "ruff is not available in the current environment",
                [Finding("RUFF_MISSING", "ruff could not be resolved on PATH or as a module")],
            )

        command = [*tool, *check.args, "--output-format=json"]
        result = run_process(command, cwd=cwd, timeout=timeout)

        if result.executable_missing:
            return check_result(
                check,
                CheckOutcome.ERROR,
                result.duration,
                "ruff is not available in the current environment",
                [Finding("RUFF_MISSING", "ruff could not be resolved on PATH or as a module")],
            )
        if result.timed_out:
            return check_result(
                check,
                CheckOutcome.ERROR,
                result.duration,
                f"ruff timed out after {timeout:g}s",
                [Finding("RUFF_TIMEOUT", f"ruff exceeded the {timeout:g}s timeout")],
            )
        if result.exit_code is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                result.duration,
                "ruff invocation crashed",
                [Finding("RUFF_CRASH", result.stderr[:500])],
            )

        if result.exit_code == 0:
            return check_result(check, CheckOutcome.PASS, result.duration, "no lint violations")

        findings = self._violation_findings(result.stdout)
        return check_result(
            check,
            CheckOutcome.FAIL,
            result.duration,
            f"ruff reported {len(findings)} lint violation(s)",
            findings,
        )

    @staticmethod
    def _violation_findings(stdout: str) -> list[Finding]:
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            data = []
        if isinstance(data, list) and data:
            findings: list[Finding] = []
            for item in data[:100]:
                if not isinstance(item, dict):
                    continue
                code = str(item.get("code", "RUFF"))
                message = str(item.get("message", ""))
                filename = str(item.get("filename", ""))
                location = item.get("location") or {}
                row = location.get("row", "")
                col = location.get("column", "")
                location_text = f"{filename}:{row}:{col}" if filename else ""
                text = f"{code} {message}"
                if location_text:
                    text = f"{location_text} {text}"
                findings.append(Finding(code or "RUFF", text))
            return truncate_findings(findings)
        return [Finding("RUFF", "ruff reported lint violations")]
