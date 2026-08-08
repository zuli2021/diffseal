"""Tests for the CLI (init, plan, run, exit codes)."""

from __future__ import annotations

import json

import pytest

from diffseal.cli import main

PASS_EXIT = 0
FAIL_EXIT = 1
REVIEW_EXIT = 2
INSUFFICIENT_EXIT = 3
USAGE_EXIT = 4


def test_version_flag():
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_init_creates_config(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == PASS_EXIT
    assert (tmp_path / ".diffseal.toml").exists()


def test_init_refuses_overwrite(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == PASS_EXIT
    original = (tmp_path / ".diffseal.toml").read_text(encoding="utf-8")
    assert main(["init"]) == USAGE_EXIT
    assert (tmp_path / ".diffseal.toml").read_text(encoding="utf-8") == original


def test_init_force_overwrites(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".diffseal.toml").write_text("[evaluation]\nreview_on = []\n", encoding="utf-8")
    assert main(["init", "--force"]) == PASS_EXIT
    assert "checks.pytest" in (tmp_path / ".diffseal.toml").read_text(encoding="utf-8")


def test_plan_does_not_execute_tools(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["plan"]) == PASS_EXIT
    out = capsys.readouterr().out
    assert "pytest" in out
    assert "ruff" in out
    assert "required" in out
    assert "optional" in out
    assert "does not execute any verification tool" in out


def test_run_healthy_repo(monkeypatch, make_fixture_repo, healthy_files):
    repo = make_fixture_repo(healthy_files, git=True)
    monkeypatch.chdir(repo)
    assert main(["run"]) == PASS_EXIT
    assert (repo / "evidence.json").exists()
    assert (repo / "evidence.md").exists()
    data = json.loads((repo / "evidence.json").read_text(encoding="utf-8"))
    assert data["decision"] == "PASS"


def test_run_failing_repo(monkeypatch, make_fixture_repo, fail_test_files):
    repo = make_fixture_repo(fail_test_files, git=True)
    monkeypatch.chdir(repo)
    assert main(["run"]) == FAIL_EXIT
    data = json.loads((repo / "evidence.json").read_text(encoding="utf-8"))
    assert data["decision"] == "FAIL"


def test_run_missing_required_tool(monkeypatch, make_fixture_repo, healthy_files):
    repo = make_fixture_repo(healthy_files, git=True)
    monkeypatch.chdir(repo)
    monkeypatch.setattr("diffseal.collectors.ruff.resolve_tool", lambda _name: None)
    assert main(["run"]) == INSUFFICIENT_EXIT
    data = json.loads((repo / "evidence.json").read_text(encoding="utf-8"))
    assert data["decision"] == "INSUFFICIENT_EVIDENCE"


def test_run_review_required(monkeypatch, make_fixture_repo, tmp_path):
    repo = make_fixture_repo(
        {
            "hello.py": (
                "def greet(name):\n    return f'Hi, {name}'\n\ndef untested():\n    return 42\n"
            ),
            "test_hello.py": (
                "from hello import greet\n\n\ndef test_greet():\n    assert greet('x') == 'Hi, x'\n"
            ),
        },
        git=True,
    )
    (repo / ".diffseal.toml").write_text(
        "[checks.coverage]\nthreshold = 100.0\n\n[evaluation]\nreview_on = ['coverage']\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(repo)
    assert main(["run"]) == REVIEW_EXIT
    data = json.loads((repo / "evidence.json").read_text(encoding="utf-8"))
    assert data["decision"] == "REVIEW_REQUIRED"


def test_run_output_dir_option(monkeypatch, make_fixture_repo, healthy_files, tmp_path):
    repo = make_fixture_repo(healthy_files, git=True)
    out = tmp_path / "out"
    monkeypatch.chdir(repo)
    assert main(["run", "--output-dir", str(out)]) == PASS_EXIT
    assert (out / "evidence.json").exists()
    assert (out / "evidence.md").exists()


def test_usage_error_exits_4():
    with pytest.raises(SystemExit) as exc:
        main(["not-a-command"])
    assert exc.value.code == USAGE_EXIT


def test_config_error_exits_usage(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".diffseal.toml").write_text("bogus = 1\n", encoding="utf-8")
    assert main(["plan"]) == USAGE_EXIT
