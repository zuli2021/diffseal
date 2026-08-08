"""Basic coverage collector (v0.1).

Goal: determine whether basic coverage evidence satisfies a configured
threshold. Uses ``coverage.py`` to run the test suite and report a total
coverage percentage.

Semantics:

- threshold configured and satisfied       -> PASS
- threshold configured and not satisfied   -> FAIL
- coverage tool unavailable / no report    -> ERROR
- threshold not configured                 -> SKIPPED

Deliberately out of scope (Pro): diff coverage, changed-line coverage,
branch-diff semantics, rename awareness, baseline-service comparison.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from diffseal.collectors.base import Collector, check_result
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome, CheckResult, Finding
from diffseal.process import resolve_tool, run_process


class CoverageCollector(Collector):
    collector_id = "coverage"
    distribution_name = "coverage"

    def collect(self, check: CheckConfig, cwd: Path, timeout: float) -> CheckResult:
        threshold = check.threshold
        if threshold is None:
            return check_result(
                check,
                CheckOutcome.SKIPPED,
                0.0,
                "coverage threshold is not configured; check skipped",
            )
        tool = resolve_tool("coverage")
        if tool is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                0.0,
                "coverage is not available in the current environment",
                [
                    Finding(
                        "COVERAGE_MISSING",
                        "coverage could not be resolved on PATH or as a module",
                    )
                ],
            )

        run_cmd = [
            *tool,
            "run",
            "--branch",
            "--source=.",
            "-m",
            "pytest",
            *check.args,
        ]
        run_result = run_process(run_cmd, cwd=cwd, timeout=timeout)

        if run_result.executable_missing:
            return check_result(
                check,
                CheckOutcome.ERROR,
                run_result.duration,
                "coverage is not available in the current environment",
                [
                    Finding(
                        "COVERAGE_MISSING",
                        "coverage could not be resolved on PATH or as a module",
                    )
                ],
            )
        if run_result.timed_out:
            return check_result(
                check,
                CheckOutcome.ERROR,
                run_result.duration,
                f"coverage run timed out after {timeout:g}s",
                [Finding("COVERAGE_TIMEOUT", f"coverage exceeded the {timeout:g}s timeout")],
            )
        if run_result.exit_code is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                run_result.duration,
                "coverage run crashed",
                [Finding("COVERAGE_CRASH", run_result.stderr[:500])],
            )

        report = run_process([*tool, "report"], cwd=cwd, timeout=timeout)
        percent = self._parse_percent(report.stdout)
        if report.exit_code is None or report.timed_out or percent is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                report.duration,
                "coverage evidence could not be established",
                [Finding("COVERAGE_UNAVAILABLE", "coverage report could not be produced")],
            )

        if percent >= threshold:
            return check_result(
                check,
                CheckOutcome.PASS,
                run_result.duration + report.duration,
                f"coverage {percent:.1f}% meets threshold {threshold:g}%",
            )
        return check_result(
            check,
            CheckOutcome.FAIL,
            run_result.duration + report.duration,
            f"coverage {percent:.1f}% is below threshold {threshold:g}%",
            [Finding("COVERAGE_BELOW_THRESHOLD", f"coverage {percent:.1f}% < {threshold:g}%")],
        )

    @staticmethod
    def _parse_percent(stdout: str) -> Any:
        """Parse the total coverage percentage from ``coverage report`` text."""
        for line in stdout.splitlines():
            stripped = line.strip()
            if not stripped.startswith("TOTAL"):
                continue
            tokens = stripped.split()
            if not tokens:
                continue
            last = tokens[-1].rstrip("%")
            if last in ("", "--", "N/A"):
                continue
            try:
                return float(last)
            except ValueError:
                continue
        return None
