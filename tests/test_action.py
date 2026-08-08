"""Validation of the DiffSeal composite GitHub Action metadata and logic."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTION_PATH = REPO_ROOT / "action.yml"

FAKE_DIFFSEAL = """\
#!/usr/bin/env bash
set -u
out_dir="evidence"
prev=""
for arg in "$@"; do
  if [[ "$prev" == "--output-dir" ]]; then
    out_dir="$arg"
  fi
  prev="$arg"
done
mkdir -p "$out_dir"
decision="${FAKE_DIFFSEAL_DECISION:-PASS}"
cat > "$out_dir/evidence.json" <<EOF
{
  "schema_version": "0.1",
  "decision": "$decision",
  "checks": []
}
EOF
printf '# DiffSeal Evidence\\n\\n## Decision: **%s**\\n' "$decision" > "$out_dir/evidence.md"
exit "${FAKE_DIFFSEAL_EXIT:-0}"
"""


def _load_action() -> dict:
    return yaml.safe_load(ACTION_PATH.read_text(encoding="utf-8"))


def test_action_yaml_is_valid():
    data = _load_action()
    assert isinstance(data, dict)
    assert "runs" in data


def test_action_identity_is_diffseal():
    assert _load_action()["name"] == "DiffSeal"
    assert _load_action()["description"]


def test_action_is_composite():
    assert _load_action()["runs"]["using"] == "composite"


def test_action_expected_inputs_with_defaults():
    inputs = _load_action()["inputs"]
    assert set(inputs) == {"config", "output-dir", "timeout"}
    assert inputs["config"]["default"] == ""
    assert inputs["output-dir"]["default"] == "evidence"
    assert inputs["timeout"]["default"] == "180"


def test_action_expected_outputs():
    assert set(_load_action()["outputs"]) == {
        "decision",
        "evidence-json",
        "evidence-markdown",
    }


def test_action_invokes_diffseal_cli_not_duplicate_evaluator():
    steps = _load_action()["runs"]["steps"]
    run_blocks = [s["run"] for s in steps if "run" in s]
    combined = "\n".join(run_blocks)
    assert "diffseal run" in combined
    # Thin action: it must not contain gate-evaluation logic itself.
    assert "INSUFFICIENT_EVIDENCE" not in combined
    assert "GateDecision" not in combined


def test_action_install_from_checkout():
    steps = _load_action()["runs"]["steps"]
    run_blocks = [s["run"] for s in steps if "run" in s]
    assert any("pip install" in block and "github.action_path" in block for block in run_blocks)


def test_action_no_shell_injection_from_inputs():
    steps = _load_action()["runs"]["steps"]
    for step in steps:
        run = step.get("run", "")
        # User-controlled input values must not be interpolated into the run
        # script; they are passed through env vars and read as shell variables.
        assert "${{ inputs." not in run
        assert "sh -c" not in run
        assert "bash -c" not in run
        assert "eval " not in run
        assert "eval(" not in run


def test_action_inputs_reach_cli_via_env():
    steps = _load_action()["runs"]["steps"]
    env_step = next(s for s in steps if "DIFFSEAL_CONFIG" in str(s.get("env", {})))
    assert env_step["env"]["DIFFSEAL_CONFIG"] == "${{ inputs.config }}"
    assert env_step["env"]["DIFFSEAL_OUTPUT_DIR"] == "${{ inputs.output-dir }}"
    assert env_step["env"]["DIFFSEAL_TIMEOUT"] == "${{ inputs.timeout }}"
    run = env_step["run"]
    assert "--config" in run
    assert "--output-dir" in run
    assert "--timeout" in run


def test_action_outputs_written_to_github_output():
    steps = _load_action()["runs"]["steps"]
    run = next(s for s in steps if "GITHUB_OUTPUT" in s.get("run", ""))["run"]
    for marker in ("decision=", "evidence-json=", "evidence-markdown="):
        assert marker in run
    assert "evidence.json" in run
    assert "evidence.md" in run


def test_action_exit_code_preserves_gate_decision():
    steps = _load_action()["runs"]["steps"]
    run = next(s for s in steps if "GITHUB_OUTPUT" in s.get("run", ""))["run"]
    assert 'exit "$exit_code"' in run


def test_action_run_step_executes_locally(tmp_path):
    """Simulate the composite Action run step against a demo fixture.

    Verifies the script produces stable outputs and preserves the CLI exit
    code, using a controlled repository in a temporary directory.
    """
    repo = tmp_path / "demo"
    repo.mkdir()
    (repo / "hello.py").write_text("def greet(name):\n    return f'Hi, {name}'\n", encoding="utf-8")
    (repo / "test_hello.py").write_text(
        "from hello import greet\n\n\ndef test_greet():\n    assert greet('x') == 'Hi, x'\n",
        encoding="utf-8",
    )

    steps = _load_action()["runs"]["steps"]
    run_script = next(s for s in steps if "GITHUB_OUTPUT" in s.get("run", ""))["run"]

    github_output = tmp_path / "GITHUB_OUTPUT"
    github_output.write_text("", encoding="utf-8")
    env = dict(os.environ)
    env["PATH"] = f"{REPO_ROOT / '.venv' / 'bin'}:{env.get('PATH', '')}"
    env.update(
        {
            "DIFFSEAL_CONFIG": "",
            "DIFFSEAL_OUTPUT_DIR": "evidence",
            "DIFFSEAL_TIMEOUT": "180",
            "GITHUB_OUTPUT": str(github_output),
        }
    )
    proc = subprocess.run(
        ["bash", "-c", run_script],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    outputs = {}
    for line in github_output.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        outputs[key] = value
    assert outputs["decision"] == "PASS"
    assert (repo / "evidence" / "evidence.json").exists()
    assert (repo / "evidence" / "evidence.md").exists()


@pytest.mark.parametrize(
    ("decision", "exit_code"),
    [
        ("PASS", 0),
        ("FAIL", 1),
        ("REVIEW_REQUIRED", 2),
        ("INSUFFICIENT_EVIDENCE", 3),
    ],
)
def test_action_run_step_preserves_exit_and_outputs(tmp_path, decision, exit_code):
    """Nonzero gate results must still emit outputs and preserve the CLI exit code.

    Uses a controlled fake ``diffseal`` executable that writes a valid
    evidence.json and returns the requested gate exit code, exercising the real
    Action run-step shell body.
    """
    repo = tmp_path / "demo"
    repo.mkdir()
    (repo / "hello.py").write_text("pass\n", encoding="utf-8")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "diffseal"
    fake.write_text(FAKE_DIFFSEAL, encoding="utf-8")
    fake.chmod(0o755)

    steps = _load_action()["runs"]["steps"]
    run_script = next(s for s in steps if "GITHUB_OUTPUT" in s.get("run", ""))["run"]

    github_output = tmp_path / "GITHUB_OUTPUT"
    github_output.write_text("", encoding="utf-8")
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:{REPO_ROOT / '.venv' / 'bin'}:{env.get('PATH', '')}"
    env.update(
        {
            "DIFFSEAL_CONFIG": "",
            "DIFFSEAL_OUTPUT_DIR": "evidence",
            "DIFFSEAL_TIMEOUT": "180",
            "GITHUB_OUTPUT": str(github_output),
            "FAKE_DIFFSEAL_DECISION": decision,
            "FAKE_DIFFSEAL_EXIT": str(exit_code),
        }
    )
    proc = subprocess.run(
        ["bash", "-c", run_script],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    # Original gate exit code must be preserved by the Action run step.
    assert proc.returncode == exit_code, proc.stdout + proc.stderr

    # Outputs must survive the nonzero result.
    outputs = {}
    for line in github_output.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        outputs[key] = value
    assert outputs["decision"] == decision
    assert outputs["evidence-json"] == "evidence/evidence.json"
    assert outputs["evidence-markdown"] == "evidence/evidence.md"
    assert (repo / "evidence" / "evidence.json").exists()
    assert (repo / "evidence" / "evidence.md").exists()
