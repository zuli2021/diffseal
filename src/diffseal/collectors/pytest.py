"""pytest collector.

Semantics:

- ``pytest`` succeeds (exit 0)          -> PASS
- test assertions fail (exit 1)         -> FAIL
- no tests collected (exit 5)           -> SKIPPED
- missing/unexecutable/crash            -> ERROR

pytest is never reimplemented; it is invoked with argument arrays.
"""

from __future__ import annotations

import re
from pathlib import Path

from diffseal.collectors.base import Collector, check_result, truncate_findings
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome, CheckResult, Finding
from diffseal.process import resolve_tool, run_process

_SUMMARY_RE = re.compile(r"(?P<body>\d+ (?:failed|passed|error)[^\n]*?) in \d+(?:\.\d+)?s")


class PytestCollector(Collector):
    collector_id = "pytest"
    distribution_name = "pytest"

    def collect(self, check: CheckConfig, cwd: Path, timeout: float) -> CheckResult:
        tool = resolve_tool("pytest")
        if tool is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                0.0,
                "pytest is not available in the current environment",
                [Finding("PYTEST_MISSING", "pytest could not be resolved on PATH or as a module")],
            )

        result = run_process([*tool, *check.args], cwd=cwd, timeout=timeout)

        if result.executable_missing:
            return check_result(
                check,
                CheckOutcome.ERROR,
                result.duration,
                "pytest is not available in the current environment",
                [Finding("PYTEST_MISSING", "pytest could not be resolved on PATH or as a module")],
            )
        if result.timed_out:
            return check_result(
                check,
                CheckOutcome.ERROR,
                result.duration,
                f"pytest timed out after {timeout:g}s",
                [Finding("PYTEST_TIMEOUT", f"pytest exceeded the {timeout:g}s timeout")],
            )
        if result.exit_code is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                result.duration,
                "pytest invocation crashed",
                [Finding("PYTEST_CRASH", result.stderr[:500])],
            )

        combined = f"{result.stdout}\n{result.stderr}"

        if result.exit_code == 0:
            return check_result(
                check,
                CheckOutcome.PASS,
                result.duration,
                self._summary_line(combined) or "pytest passed",
            )

        if result.exit_code == 1:
            findings = self._failure_findings(combined)
            summary = self._summary_line(combined) or (
                "pytest reported test failures (exit code 1)"
            )
            return check_result(check, CheckOutcome.FAIL, result.duration, summary, findings)

        if result.exit_code == 5:
            return check_result(
                check,
                CheckOutcome.SKIPPED,
                result.duration,
                "pytest collected no tests; nothing to verify",
            )

        return check_result(
            check,
            CheckOutcome.ERROR,
            result.duration,
            f"pytest exited abnormally with code {result.exit_code}",
            [Finding("PYTEST_UNUSABLE", f"pytest exit code {result.exit_code} is not usable")],
        )

    @staticmethod
    def _summary_line(combined: str) -> str:
        for match in _SUMMARY_RE.findall(combined):
            return match.strip()
        return ""

    @staticmethod
    def _failure_findings(combined: str) -> list[Finding]:
        findings: list[Finding] = []
        for line in combined.splitlines():
            stripped = line.strip()
            if stripped.startswith("FAILED "):
                findings.append(Finding("TEST_FAILED", stripped[len("FAILED ") :].strip()))
        return truncate_findings(findings)
