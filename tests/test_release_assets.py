"""Validation of README, demo project, and committed sample evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from diffseal.config import load_config_file
from diffseal.models import CheckOutcome, GateDecision

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
DEMO = REPO_ROOT / "examples" / "python-basic"
SAMPLE = REPO_ROOT / "examples" / "evidence"


def test_readme_references_real_commands():
    text = README.read_text(encoding="utf-8")
    for command in ("diffseal init", "diffseal plan", "diffseal run"):
        assert command in text


def test_readme_example_config_parses():
    text = README.read_text(encoding="utf-8")
    block = text.split("## Example configuration")[1].split("## GitHub Actions")[0]
    toml = block.split("```toml")[1].split("```")[0]
    target = REPO_ROOT / "README-config-check.toml"
    try:
        target.write_text(toml, encoding="utf-8")
        config = load_config_file(target)
        assert config.checks["pytest"].required is True
        assert config.checks["coverage"].threshold == 80.0
    finally:
        target.unlink(missing_ok=True)


def test_demo_config_parses():
    config = load_config_file(DEMO / ".diffseal.toml")
    assert config.checks["pytest"].required is True
    assert config.checks["ruff"].required is True
    assert config.checks["coverage"].threshold == 80.0


def test_demo_tests_pass():
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=str(DEMO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_demo_produces_pass_evidence(tmp_path):
    out_dir = tmp_path / "evidence"
    result = subprocess.run(
        [sys.executable, "-m", "diffseal", "run", "--output-dir", str(out_dir)],
        cwd=str(DEMO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
    assert data["decision"] == "PASS"
    assert (out_dir / "evidence.md").exists()


def test_sample_evidence_validates():
    data = json.loads((SAMPLE / "evidence.json").read_text(encoding="utf-8"))
    assert data["schema_version"] == "0.1"
    assert data["product_version"] == "0.1.0"
    assert data["decision"] in {d.value for d in GateDecision}
    for check in data["checks"]:
        assert check["outcome"] in {o.value for o in CheckOutcome}
        assert "id" in check
        assert "collector_id" in check
        assert "required" in check
    assert (SAMPLE / "evidence.md").exists()


def test_sample_evidence_head_revision_is_genuine():
    data = json.loads((SAMPLE / "evidence.json").read_text(encoding="utf-8"))
    revision = data["head_revision"]
    assert len(revision) == 40
    assert all(c in "0123456789abcdef" for c in revision)
    assert revision != "0" * 40, "head_revision must not be a fabricated zero placeholder"


def test_sample_markdown_corresponds_to_same_bundle():
    data = json.loads((SAMPLE / "evidence.json").read_text(encoding="utf-8"))
    md = (SAMPLE / "evidence.md").read_text(encoding="utf-8")
    assert data["decision"] in md
    for check in data["checks"]:
        assert f"### {check['id']}" in md
        assert check["outcome"] in md
    for reason in data["decision_reasons"]:
        assert reason in md


def test_sample_evidence_has_no_machine_paths_or_secrets():
    for path in (SAMPLE / "evidence.json", SAMPLE / "evidence.md"):
        text = path.read_text(encoding="utf-8")
        assert "/home/" not in text
        assert "/Users/" not in text
        assert "TOPSECRET" not in text
    data = json.loads((SAMPLE / "evidence.json").read_text(encoding="utf-8"))
    assert "examples/python-basic" in data["environment_metadata"]["cwd"]


def test_readme_documents_sample_normalization():
    text = README.read_text(encoding="utf-8")
    assert "head_revision" in text
    assert "normalized" in text
    assert "run_id" in text
    assert "examples/python-basic" in text
    for phrase in (
        "evidence_id",
        "started_at",
        "finished_at",
        "actual commit SHA",
    ):
        assert phrase in text


def test_demo_leave_no_unexpected_tracked_artifacts():
    # demo runs generate cache/coverage artifacts that must be gitignored
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (".coverage", "__pycache__/", ".pytest_cache/", ".venv/"):
        assert pattern in gitignore
    assert "/evidence.json" in gitignore
    assert "/evidence.md" in gitignore
