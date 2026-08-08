"""Tests for the pytest collector (pass, fail, missing, no-tests)."""

from __future__ import annotations

from diffseal.collectors.pytest import PytestCollector
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome


def _check(required: bool = True) -> CheckConfig:
    return CheckConfig(
        id="pytest",
        collector_id="pytest",
        enabled=True,
        required=required,
        args=["-q"],
        threshold=None,
    )


def test_pytest_pass(tmp_path):
    hello = "def greet(name):\n    return f'Hi, {name}'\n"
    (tmp_path / "hello.py").write_text(hello, encoding="utf-8")
    (tmp_path / "test_hello.py").write_text(
        "from hello import greet\n\ndef test_greet():\n    assert greet('x') == 'Hi, x'\n",
        encoding="utf-8",
    )
    result = PytestCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.PASS
    assert "passed" in result.summary


def test_pytest_fail(tmp_path):
    (tmp_path / "test_bad.py").write_text("def test_bad():\n    assert False\n", encoding="utf-8")
    result = PytestCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "TEST_FAILED" for f in result.findings)
    assert "failed" in result.summary


def test_pytest_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("diffseal.collectors.pytest.resolve_tool", lambda _name: None)
    result = PytestCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.ERROR
    assert result.findings[0].code == "PYTEST_MISSING"


def test_pytest_no_tests_collected(tmp_path):
    result = PytestCollector().collect(_check(), cwd=tmp_path, timeout=60.0)
    assert result.outcome == CheckOutcome.SKIPPED
