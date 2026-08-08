"""Tests for JSON and Markdown reporters."""

from __future__ import annotations

import json

from diffseal.models import (
    CheckOutcome,
    CheckResult,
    EvidenceBundle,
    Finding,
    GateDecision,
)
from diffseal.reporters.json import bundle_to_json, write_json
from diffseal.reporters.markdown import render_markdown, write_markdown


def _bundle() -> EvidenceBundle:
    return EvidenceBundle(
        schema_version="0.1",
        evidence_id="evid",
        product_version="0.1.0",
        run_id="runid",
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:01+00:00",
        repository="/repo",
        base_revision="abc",
        head_revision="def",
        invocation_mode="local-cli",
        configuration_hash="cfg",
        policy_hash="pol",
        tool_versions={"pytest": "9.0.0", "ruff": "0.6.0"},
        checks=[
            CheckResult(
                id="pytest",
                collector_id="pytest",
                required=True,
                outcome=CheckOutcome.PASS,
                duration=1.25,
                summary="tests passed",
            ),
            CheckResult(
                id="ruff",
                collector_id="ruff",
                required=True,
                outcome=CheckOutcome.FAIL,
                duration=0.5,
                summary="violations",
                findings=[Finding("E501", "line too long")],
            ),
        ],
        change_summary={"is_git": True},
        warnings=["something"],
        decision=GateDecision.FAIL,
        decision_reasons=["required check 'ruff' produced FAIL"],
        environment_metadata={"python_version": "3.12.3"},
    )


def test_bundle_to_json_is_valid_and_canonical():
    text = bundle_to_json(_bundle())
    parsed = json.loads(text)
    assert parsed["decision"] == "FAIL"
    assert parsed["checks"][0]["outcome"] == "PASS"
    assert parsed["checks"][1]["outcome"] == "FAIL"
    assert parsed["checks"][1]["findings"][0]["code"] == "E501"
    assert parsed["schema_version"] == "0.1"


def test_write_json_creates_file(tmp_path):
    target = tmp_path / "evidence.json"
    write_json(_bundle(), target)
    assert target.exists()
    json.loads(target.read_text(encoding="utf-8"))


def test_markdown_contains_decision_and_checks():
    text = render_markdown(_bundle())
    assert "## Decision: **FAIL**" in text
    assert "### pytest (required)" in text
    assert "**PASS**" in text
    assert "### ruff (required)" in text
    assert "**FAIL**" in text
    assert "`E501`" in text
    assert "required check 'ruff' produced FAIL" in text
    assert "tool_versions" not in text  # no internal field names leak
    assert "- pytest: `9.0.0`" in text
    assert "something" in text


def test_write_markdown_derived_from_same_bundle(tmp_path):
    bundle = _bundle()
    md_path = tmp_path / "evidence.md"
    write_markdown(bundle, md_path)
    assert md_path.exists()
    assert "FAIL" in md_path.read_text(encoding="utf-8")


def test_no_secret_leak_in_reports(tmp_path):
    bundle = _bundle()
    bundle.environment_metadata = {"python_version": "3.12.3"}
    json_text = bundle_to_json(bundle)
    md_text = render_markdown(bundle)
    for text in (json_text, md_text):
        assert "DIFFSEAL_SECRET" not in text
        assert "os.environ" not in text
