"""Tests for canonical evidence models and deterministic hashing."""

from __future__ import annotations

import json

from diffseal.models import (
    CheckOutcome,
    CheckResult,
    EvidenceBundle,
    Finding,
    GateDecision,
    stable_hash,
)


def test_check_outcome_values_are_exact():
    assert [o.value for o in CheckOutcome] == ["PASS", "FAIL", "ERROR", "SKIPPED"]


def test_gate_decision_values_are_exact():
    assert [d.value for d in GateDecision] == [
        "PASS",
        "FAIL",
        "REVIEW_REQUIRED",
        "INSUFFICIENT_EVIDENCE",
    ]


def test_check_result_to_dict():
    result = CheckResult(
        id="pytest",
        collector_id="pytest",
        required=True,
        outcome=CheckOutcome.FAIL,
        duration=1.23456,
        summary="tests failed",
        findings=[Finding("TEST_FAILED", "some test failed")],
    )
    data = result.to_dict()
    assert data["id"] == "pytest"
    assert data["outcome"] == "FAIL"
    assert data["duration"] == 1.2346
    assert data["findings"][0]["code"] == "TEST_FAILED"


def test_check_result_default_findings_empty():
    result = CheckResult(
        id="x",
        collector_id="x",
        required=False,
        outcome=CheckOutcome.PASS,
        duration=0.0,
        summary="ok",
    )
    assert result.to_dict()["findings"] == []


def test_evidence_bundle_to_dict_canonical_order():
    bundle = EvidenceBundle(
        schema_version="0.1",
        evidence_id="ev",
        product_version="0.1.0",
        decision=GateDecision.PASS,
        decision_reasons=["all required evidence satisfactory"],
    )
    data = bundle.to_dict()
    keys = list(data.keys())
    assert keys == [
        "schema_version",
        "evidence_id",
        "product_version",
        "run_id",
        "started_at",
        "finished_at",
        "repository",
        "base_revision",
        "head_revision",
        "invocation_mode",
        "configuration_hash",
        "policy_hash",
        "tool_versions",
        "checks",
        "change_summary",
        "warnings",
        "environment_metadata",
        "decision",
        "decision_reasons",
    ]
    assert data["decision"] == "PASS"


def test_evidence_bundle_omits_none_decision():
    data = EvidenceBundle().to_dict()
    assert "decision" not in data
    assert "decision_reasons" not in data


def test_evidence_bundle_json_roundtrip():
    bundle = EvidenceBundle(
        schema_version="0.1",
        evidence_id="ev",
        product_version="0.1.0",
        checks=[
            CheckResult(
                id="ruff",
                collector_id="ruff",
                required=True,
                outcome=CheckOutcome.PASS,
                duration=0.5,
                summary="clean",
            )
        ],
        decision=GateDecision.PASS,
        decision_reasons=["all required evidence satisfactory"],
    )
    text = json.dumps(bundle.to_dict())
    parsed = json.loads(text)
    assert parsed["checks"][0]["outcome"] == "PASS"
    assert parsed["decision"] == "PASS"
    assert parsed["schema_version"] == "0.1"


def test_stable_hash_order_independent():
    a = stable_hash({"a": 1, "b": {"c": [1, 2], "d": "x"}})
    b = stable_hash({"b": {"d": "x", "c": [1, 2]}, "a": 1})
    assert a == b


def test_stable_hash_is_deterministic():
    data = {"checks": {"pytest": {"enabled": True, "required": True}}}
    assert stable_hash(data) == stable_hash(data)


def test_stable_hash_detects_changes():
    assert stable_hash({"a": 1}) != stable_hash({"a": 2})
