"""Tests for the Ruff collector (clean, violations, missing)."""

from __future__ import annotations

from diffseal.collectors.ruff import RuffCollector
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome


def _check() -> CheckConfig:
    return CheckConfig(
        id="ruff",
        collector_id="ruff",
        enabled=True,
        required=True,
        args=["check", "."],
        threshold=None,
    )


def test_ruff_clean(tmp_path):
    (tmp_path / "code.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
    result = RuffCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.PASS
    assert result.summary == "no lint violations"


def test_ruff_violation(tmp_path):
    (tmp_path / "code.py").write_text("import os\n\ndef foo():\n    return 1\n", encoding="utf-8")
    result = RuffCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.FAIL
    assert result.findings
    assert any(f.code != "RUFF" for f in result.findings)


def test_ruff_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("diffseal.collectors.ruff.resolve_tool", lambda _name: None)
    result = RuffCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.ERROR
    assert result.findings[0].code == "RUFF_MISSING"
