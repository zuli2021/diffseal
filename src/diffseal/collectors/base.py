"""Collector base class and shared helpers.

Collectors focus on tool invocation and normalization only. They do NOT define
gate policy semantics; that is the responsibility of the shared evaluation
path in :mod:`diffseal.evaluate`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version
from pathlib import Path

from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome, CheckResult, Finding


def distribution_version(name: str) -> str | None:
    """Return the installed distribution version for ``name``, if any."""
    try:
        return _distribution_version(name)
    except PackageNotFoundError:
        return None


def check_result(
    check: CheckConfig,
    outcome: CheckOutcome,
    duration: float,
    summary: str,
    findings: list[Finding] | None = None,
) -> CheckResult:
    return CheckResult(
        id=check.id,
        collector_id=check.collector_id,
        required=check.required,
        outcome=outcome,
        duration=duration,
        summary=summary,
        findings=list(findings or []),
    )


def truncate_findings(findings: list[Finding], limit: int = 100) -> list[Finding]:
    """Cap findings so evidence stays concise and reviewer-friendly."""
    return list(findings[:limit])


class Collector(ABC):
    """Base class for tool collectors."""

    collector_id: str

    @abstractmethod
    def collect(self, check: CheckConfig, cwd: Path, timeout: float) -> CheckResult:
        """Run the tool for one configured check and normalize the result."""

    def version(self) -> str | None:
        """Best-effort tool version for evidence ``tool_versions``."""
        if not self.distribution_name:
            return None
        return distribution_version(self.distribution_name)

    distribution_name: str = ""
