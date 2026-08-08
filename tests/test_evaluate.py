"""Tests for deterministic gate evaluation and precedence."""

from __future__ import annotations

from diffseal.evaluate import evaluate
from diffseal.models import CheckOutcome, CheckResult, GateDecision


def _check(
    check_id: str,
    outcome: CheckOutcome,
    required: bool = False,
) -> CheckResult:
    return CheckResult(
        id=check_id,
        collector_id=check_id,
        required=required,
        outcome=outcome,
        duration=0.0,
        summary="",
    )


def _decide(checks: list[CheckResult], review_on: list[str] = None) -> GateDecision:
    return evaluate(checks, review_on or []).decision


def test_pass_when_all_required_satisfied():
    checks = [
        _check("pytest", CheckOutcome.PASS, required=True),
        _check("ruff", CheckOutcome.PASS, required=True),
        _check("coverage", CheckOutcome.SKIPPED),
    ]
    assert _decide(checks) == GateDecision.PASS


def test_pass_with_no_checks():
    assert _decide([]) == GateDecision.PASS


def test_fail_on_required_fail():
    checks = [
        _check("pytest", CheckOutcome.PASS, required=True),
        _check("ruff", CheckOutcome.FAIL, required=True),
    ]
    assert _decide(checks) == GateDecision.FAIL


def test_insufficient_evidence_on_required_error():
    checks = [_check("pytest", CheckOutcome.ERROR, required=True)]
    assert _decide(checks) == GateDecision.INSUFFICIENT_EVIDENCE


def test_required_error_precedence_over_required_fail():
    checks = [
        _check("pytest", CheckOutcome.FAIL, required=True),
        _check("ruff", CheckOutcome.ERROR, required=True),
    ]
    assert _decide(checks) == GateDecision.INSUFFICIENT_EVIDENCE


def test_required_skipped_is_insufficient_evidence():
    checks = [_check("pytest", CheckOutcome.SKIPPED, required=True)]
    assert _decide(checks) == GateDecision.INSUFFICIENT_EVIDENCE


def test_required_skipped_precedence_over_required_fail():
    checks = [
        _check("pytest", CheckOutcome.FAIL, required=True),
        _check("ruff", CheckOutcome.SKIPPED, required=True),
    ]
    assert _decide(checks) == GateDecision.INSUFFICIENT_EVIDENCE


def test_optional_skipped_does_not_fail_gate():
    checks = [
        _check("pytest", CheckOutcome.PASS, required=True),
        _check("coverage", CheckOutcome.SKIPPED),
    ]
    assert _decide(checks) == GateDecision.PASS


def test_error_is_distinct_from_skipped():
    assert CheckOutcome.ERROR is not CheckOutcome.SKIPPED
    assert CheckOutcome.ERROR.value != CheckOutcome.SKIPPED.value
    error_result = evaluate([_check("pytest", CheckOutcome.ERROR, required=True)], [])
    skipped_result = evaluate([_check("pytest", CheckOutcome.SKIPPED, required=True)], [])
    assert error_result.decision == skipped_result.decision == GateDecision.INSUFFICIENT_EVIDENCE
    assert error_result.reasons[0].startswith("required check 'pytest' produced ERROR")
    assert skipped_result.reasons[0].startswith("required check 'pytest' produced SKIPPED")


def test_error_never_becomes_fail():
    result = evaluate([_check("pytest", CheckOutcome.ERROR, required=True)], [])
    assert result.decision == GateDecision.INSUFFICIENT_EVIDENCE


def test_review_required_for_optional_fail_in_review_on():
    checks = [
        _check("pytest", CheckOutcome.PASS, required=True),
        _check("coverage", CheckOutcome.FAIL),
    ]
    assert _decide(checks, review_on=["coverage"]) == GateDecision.REVIEW_REQUIRED


def test_optional_fail_ignored_by_default():
    checks = [
        _check("pytest", CheckOutcome.PASS, required=True),
        _check("coverage", CheckOutcome.FAIL),
    ]
    assert _decide(checks) == GateDecision.PASS


def test_required_fail_in_review_on_still_fails():
    checks = [
        _check("pytest", CheckOutcome.FAIL, required=True),
    ]
    assert _decide(checks, review_on=["pytest"]) == GateDecision.FAIL


def test_review_reasons_are_returned():
    result = evaluate([_check("coverage", CheckOutcome.FAIL)], review_on=["coverage"])
    assert result.decision == GateDecision.REVIEW_REQUIRED
    assert any("coverage" in reason for reason in result.reasons)


def test_evaluation_is_deterministic():
    checks = [_check("ruff", CheckOutcome.FAIL, required=True)]
    assert evaluate(checks, []) == evaluate(checks, [])
