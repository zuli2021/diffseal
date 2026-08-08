"""Deterministic gate evaluation.

Same normalized evidence plus the same policy MUST produce the same
``GateDecision``. This module implements the canonical default precedence
(``docs/EVIDENCE_CONTRACT.md``):

1. any required check with outcome ``ERROR`` or ``SKIPPED``
   -> ``INSUFFICIENT_EVIDENCE``
2. otherwise, a required check with outcome ``FAIL`` -> ``FAIL``
3. otherwise, a configured optional review condition (an optional check
   listed in the policy's ``review_on`` that failed) -> ``REVIEW_REQUIRED``
4. otherwise -> ``PASS``

``ERROR`` (execution/evidence acquisition failed unexpectedly) and
``SKIPPED`` (did not run by design, policy, or applicable collector
condition) remain distinct outcomes, and neither may be silently treated as
``PASS`` when the check is required. ``ERROR`` never automatically becomes
``FAIL``.
"""

from __future__ import annotations

from dataclasses import dataclass

from diffseal.models import CheckOutcome, CheckResult, GateDecision


@dataclass(frozen=True)
class Evaluation:
    decision: GateDecision
    reasons: list[str]


def evaluate(checks: list[CheckResult], review_on: list[str]) -> Evaluation:
    """Evaluate a normalized set of checks against the policy ``review_on``.

    ``review_on`` lists check ids whose failure should force human review. It
    applies to optional checks: a required ``FAIL`` always yields ``FAIL`` per
    the canonical default precedence, regardless of this list.
    """
    review_set = set(review_on or [])

    required_error = [
        c for c in checks if c.required and c.outcome in (CheckOutcome.ERROR, CheckOutcome.SKIPPED)
    ]
    if required_error:
        reasons = [
            f"required check {c.id!r} produced {c.outcome.value}; "
            "required evidence could not be established"
            for c in required_error
        ]
        return Evaluation(GateDecision.INSUFFICIENT_EVIDENCE, reasons)

    required_fail = [c for c in checks if c.required and c.outcome == CheckOutcome.FAIL]
    if required_fail:
        reasons = [
            f"required check {c.id!r} produced FAIL; a verification requirement failed"
            for c in required_fail
        ]
        return Evaluation(GateDecision.FAIL, reasons)

    review_triggered = [
        c
        for c in checks
        if not c.required and c.id in review_set and c.outcome == CheckOutcome.FAIL
    ]
    if review_triggered:
        reasons = [
            f"optional check {c.id!r} failed and is listed for human review"
            for c in review_triggered
        ]
        return Evaluation(GateDecision.REVIEW_REQUIRED, reasons)

    return Evaluation(GateDecision.PASS, ["all required evidence satisfactory"])
