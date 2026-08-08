"""Tests for the basic coverage collector (pass/fail/skip/unavailable)."""

from __future__ import annotations

from diffseal.collectors.coverage import CoverageCollector
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome

PARTIAL_MODULE = (
    "def greet(name):\n"
    "    return f'Hello, {name}!'\n\n"
    "def unused_a():\n"
    "    return 1\n\n"
    "def unused_b():\n"
    "    return 2\n"
)
TEST_FILE = (
    "from hello import greet\n\ndef test_greet():\n    assert greet('World') == 'Hello, World!'\n"
)


def _check(threshold: float | None = 80.0) -> CheckConfig:
    return CheckConfig(
        id="coverage",
        collector_id="coverage",
        enabled=True,
        required=False,
        args=["-q"],
        threshold=threshold,
    )


def _write_partial_repo(tmp_path):
    (tmp_path / "hello.py").write_text(PARTIAL_MODULE, encoding="utf-8")
    (tmp_path / "test_hello.py").write_text(TEST_FILE, encoding="utf-8")


def test_coverage_passes_threshold(tmp_path):
    _write_partial_repo(tmp_path)
    result = CoverageCollector().collect(_check(threshold=0.0), cwd=tmp_path, timeout=120.0)
    assert result.outcome == CheckOutcome.PASS
    assert "meets threshold" in result.summary


def test_coverage_fails_threshold(tmp_path):
    _write_partial_repo(tmp_path)
    result = CoverageCollector().collect(_check(threshold=80.0), cwd=tmp_path, timeout=120.0)
    assert result.outcome == CheckOutcome.FAIL
    assert result.findings[0].code == "COVERAGE_BELOW_THRESHOLD"


def test_coverage_skipped_when_threshold_not_configured(tmp_path):
    result = CoverageCollector().collect(_check(threshold=None), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.SKIPPED


def test_coverage_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr("diffseal.collectors.coverage.resolve_tool", lambda _name: None)
    result = CoverageCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.ERROR
    assert result.findings[0].code == "COVERAGE_MISSING"
