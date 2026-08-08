"""End-to-end tests over controlled fixture repositories.

Demonstrates the three mandatory scenarios:

1. healthy repository                 -> PASS
2. failing tests or lint              -> FAIL
3. required tool unavailable          -> INSUFFICIENT_EVIDENCE

Uses subprocess invocation of the installed CLI for full fidelity.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from diffseal.cli import EXIT_FAIL, EXIT_INSUFFICIENT, EXIT_OK

EVIDENCE_JSON = "evidence.json"
EVIDENCE_MD = "evidence.md"


def _cli(
    repo: Path,
    *args: str,
    env: dict | None = None,
    python: str | None = None,
) -> subprocess.CompletedProcess:
    command = [(python or sys.executable), "-m", "diffseal", *args]
    merged_env = dict(os.environ)
    merged_env.update(env or {})
    return subprocess.run(
        command,
        cwd=str(repo),
        capture_output=True,
        text=True,
        env=merged_env,
        timeout=300,
    )


def _read_evidence(repo: Path) -> dict:
    return json.loads((repo / EVIDENCE_JSON).read_text(encoding="utf-8"))


def test_end_to_end_healthy_passes(monkeypatch, make_fixture_repo, healthy_files, tmp_path):
    repo = make_fixture_repo(healthy_files, git=True)
    result = _cli(repo, "run")
    assert result.returncode == EXIT_OK, result.stdout + result.stderr
    data = _read_evidence(repo)
    assert data["decision"] == "PASS"
    assert (repo / EVIDENCE_MD).exists()
    assert data["repository"]
    assert data["head_revision"]
    assert data["schema_version"] == "0.1"
    outcomes = {c["id"]: c["outcome"] for c in data["checks"]}
    assert outcomes["pytest"] == "PASS"
    assert outcomes["ruff"] == "PASS"
    assert outcomes["coverage"] == "PASS"
    assert outcomes["dependency"] in ("PASS", "SKIPPED")


def test_end_to_end_failing_tests(monkeypatch, make_fixture_repo, fail_test_files):
    repo = make_fixture_repo(fail_test_files, git=True)
    result = _cli(repo, "run")
    assert result.returncode == EXIT_FAIL
    data = _read_evidence(repo)
    assert data["decision"] == "FAIL"
    pytest_check = next(c for c in data["checks"] if c["id"] == "pytest")
    assert pytest_check["outcome"] == "FAIL"
    assert pytest_check["findings"][0]["code"] == "TEST_FAILED"


def test_end_to_end_failing_lint(monkeypatch, make_fixture_repo, fail_lint_files):
    repo = make_fixture_repo(fail_lint_files, git=True)
    result = _cli(repo, "run")
    assert result.returncode == EXIT_FAIL
    data = _read_evidence(repo)
    assert data["decision"] == "FAIL"
    ruff_check = next(c for c in data["checks"] if c["id"] == "ruff")
    assert ruff_check["outcome"] == "FAIL"
    assert ruff_check["findings"]


def test_end_to_end_missing_required_tool(monkeypatch, make_fixture_repo, healthy_files, tmp_path):
    """A required tool genuinely unavailable in the environment -> INSUFFICIENT_EVIDENCE.

    Uses the system Python interpreter (which has no pytest/coverage/ruff
    installed) so tool resolution genuinely fails, with a slim PATH that only
    provides git for repository context.
    """
    system_python = shutil.which("python3")
    assert system_python, "system python3 required for this test"
    # Verify the system python really lacks the tools so the scenario is authentic.
    probe = subprocess.run(
        [system_python, "-c", "import importlib.util; print(importlib.util.find_spec('ruff'))"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "None" in probe.stdout, "expected system python to lack ruff for this test"

    repo = make_fixture_repo(healthy_files, git=True)
    bin_dir = tmp_path / "slimbin"
    bin_dir.mkdir()
    real_git = shutil.which("git")
    assert real_git
    (bin_dir / "git").symlink_to(real_git)

    src_dir = str(Path(__file__).resolve().parent.parent / "src")
    env = {
        "PATH": str(bin_dir),
        "PYTHONPATH": src_dir,
    }
    result = _cli(repo, "run", env=env, python=system_python)
    assert result.returncode == EXIT_INSUFFICIENT, result.stdout + result.stderr
    data = _read_evidence(repo)
    assert data["decision"] == "INSUFFICIENT_EVIDENCE"
    ruff_check = next(c for c in data["checks"] if c["id"] == "ruff")
    assert ruff_check["outcome"] == "ERROR"
    assert any("'ruff'" in r and "ERROR" in r for r in data["decision_reasons"])


def test_end_to_end_python_m_module_entrypoint(monkeypatch, make_fixture_repo, healthy_files):
    repo = make_fixture_repo(healthy_files, git=True)
    result = _cli(repo, "--version")
    assert result.returncode == 0
    assert "diffseal" in result.stdout


def test_evidence_contains_no_environment_secrets(monkeypatch, make_fixture_repo, healthy_files):
    repo = make_fixture_repo(healthy_files, git=True)
    env = {"DIFFSEAL_TOPSECRET": "super-secret-value"}
    result = _cli(repo, "run", env=env)
    assert result.returncode == EXIT_OK
    for path in (repo / EVIDENCE_JSON, repo / EVIDENCE_MD):
        content = path.read_text(encoding="utf-8")
        assert "super-secret-value" not in content
        assert "DIFFSEAL_TOPSECRET" not in content


def test_end_to_end_required_skipped(monkeypatch, make_fixture_repo):
    """A required pytest that collects no tests -> SKIPPED -> INSUFFICIENT_EVIDENCE."""
    repo = make_fixture_repo(
        {
            "pyproject.toml": "[project]\nname = 'notests'\nversion = '0.1.0'\n",
            "hello.py": "def greet(name):\n    return f'Hi, {name}'\n",
        },
        git=True,
    )
    result = _cli(repo, "run")
    assert result.returncode == EXIT_INSUFFICIENT, result.stdout + result.stderr
    data = _read_evidence(repo)
    assert data["decision"] == "INSUFFICIENT_EVIDENCE"
    pytest_check = next(c for c in data["checks"] if c["id"] == "pytest")
    assert pytest_check["outcome"] == "SKIPPED"
    assert any("'pytest'" in r and "SKIPPED" in r for r in data["decision_reasons"])
