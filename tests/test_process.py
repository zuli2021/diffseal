"""Tests for the tool invocation (subprocess) boundary."""

from __future__ import annotations

import sys
from pathlib import Path

from diffseal.process import (
    run_process,
    sanitized_env,
)


def _py(code: str) -> list:
    return [sys.executable, "-c", code]


def test_success(tmp_path: Path):
    result = run_process(_py("print('hello')"), cwd=tmp_path)
    assert result.exit_code == 0
    assert result.stdout.strip() == "hello"
    assert not result.executable_missing
    assert not result.timed_out
    assert result.error is None
    assert result.duration >= 0.0


def test_nonzero_exit(tmp_path: Path):
    result = run_process(_py("import sys; sys.exit(3)"), cwd=tmp_path)
    assert result.exit_code == 3
    assert result.error is None


def test_stdout_and_stderr_captured(tmp_path: Path):
    code = "import sys; sys.stderr.write('boom'); sys.stdout.write('out')"
    result = run_process(_py(code), cwd=tmp_path)
    assert "boom" in result.stderr
    assert "out" in result.stdout


def test_executable_missing(tmp_path: Path):
    result = run_process(["definitely-not-a-real-tool-xyz"], cwd=tmp_path)
    assert result.executable_missing
    assert result.exit_code is None
    assert "not found" in result.error


def test_empty_command_raises(tmp_path: Path):
    import pytest

    from diffseal.process import ToolError

    with pytest.raises(ToolError):
        run_process([], cwd=tmp_path)


def test_timeout(tmp_path: Path):
    result = run_process(
        _py("import time; time.sleep(30)"),
        cwd=tmp_path,
        timeout=1.0,
    )
    assert result.timed_out
    assert result.exit_code is None
    assert "timed out" in result.error


def test_argument_array_no_shell(tmp_path: Path):
    result = run_process(["echo", "a; echo b > /tmp/diffseal-shell-injection"], cwd=tmp_path)
    assert result.stdout.strip() == "a; echo b > /tmp/diffseal-shell-injection"


def test_env_is_sanitized_and_minimal(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DIFFSEAL_SUPER_SECRET", "hunter2")
    result = run_process(
        _py("import os; print(os.environ.get('DIFFSEAL_SUPER_SECRET', '<absent>'))"),
        cwd=tmp_path,
    )
    assert result.stdout.strip() == "<absent>"
    assert "DIFFSEAL_SUPER_SECRET" not in sanitized_env()


def test_env_preserves_path(tmp_path: Path):
    result = run_process(
        _py("import os; print('PATH' in os.environ)"),
        cwd=tmp_path,
    )
    assert result.stdout.strip() == "True"
