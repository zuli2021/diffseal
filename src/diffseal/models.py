"""Canonical DiffSeal evidence models.

These types are the normalized contract between collectors, evaluation, and
reporters. They follow ``docs/EVIDENCE_CONTRACT.md`` exactly.
"""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


class CheckOutcome(str, enum.Enum):
    """Normalized outcome of a single check.

    Meaning (canonical, from ``docs/EVIDENCE_CONTRACT.md``):

    - ``PASS``: the check established that its requirement passed.
    - ``FAIL``: the check established that its requirement failed.
    - ``ERROR``: required evidence could not be established successfully.
    - ``SKIPPED``: the check did not run by design or policy.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class GateDecision(str, enum.Enum):
    """Explicit review-readiness decision for the whole evidence bundle.

    Meaning (canonical, from ``docs/EVIDENCE_CONTRACT.md``):

    - ``PASS``: the normalized evidence satisfies the current gate policy.
    - ``FAIL``: evidence established that a verification requirement failed.
    - ``REVIEW_REQUIRED``: evidence exists but policy requires human review.
    - ``INSUFFICIENT_EVIDENCE``: required evidence could not be established with
      enough confidence to pass the gate.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class Finding:
    """A single concise, normalized finding attached to a check.

    ``code`` is a short stable machine-readable identifier. ``message`` is a
    concise human-readable line. Additional ``data`` carries a minimal amount
    of structured context; it must never contain secrets.
    """

    code: str
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


@dataclass(frozen=True)
class CheckResult:
    """A normalized, tool-independent verification result for one check."""

    id: str
    collector_id: str
    required: bool
    outcome: CheckOutcome
    duration: float
    summary: str
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "collector_id": self.collector_id,
            "required": self.required,
            "outcome": self.outcome.value,
            "duration": round(self.duration, 4),
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class EvidenceBundle:
    """The canonical v0.1 evidence bundle.

    Matches the conceptual ``EvidenceBundle`` from ``docs/EVIDENCE_CONTRACT.md``.
    Serialization is performed by :func:`EvidenceBundle.to_dict` with stable,
    insertion-independent field ordering.
    """

    schema_version: str = "0.1"
    evidence_id: str = ""
    product_version: str = ""

    run_id: str = ""
    started_at: str = ""
    finished_at: str = ""

    repository: str = ""
    base_revision: str = ""
    head_revision: str = ""

    invocation_mode: str = ""

    configuration_hash: str = ""
    policy_hash: str = ""

    tool_versions: dict[str, str] = field(default_factory=dict)

    checks: list[CheckResult] = field(default_factory=list)

    change_summary: dict[str, Any] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    decision: GateDecision | None = None
    decision_reasons: list[str] = field(default_factory=list)

    environment_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict with canonical ordering.

        Enum values are emitted exactly (``PASS``, ``FAIL``, ``ERROR``,
        ``SKIPPED`` and gate decision names). ``None`` decision is omitted
        so partial bundles remain valid.
        """
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "product_version": self.product_version,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "repository": self.repository,
            "base_revision": self.base_revision,
            "head_revision": self.head_revision,
            "invocation_mode": self.invocation_mode,
            "configuration_hash": self.configuration_hash,
            "policy_hash": self.policy_hash,
            "tool_versions": self.tool_versions,
            "checks": [c.to_dict() for c in self.checks],
            "change_summary": self.change_summary,
            "warnings": self.warnings,
            "environment_metadata": self.environment_metadata,
        }
        if self.decision is not None:
            data["decision"] = self.decision.value
            data["decision_reasons"] = self.decision_reasons
        return data


def _canonical_json(data: dict[str, Any]) -> str:
    """Serialize dict to JSON with recursively sorted keys and stable separators."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: dict[str, Any]) -> str:
    """Return a stable hex digest for a normalized, order-independent dict.

    The digest does not depend on dictionary insertion order. Callers must
    pass only normalized, secret-free data.
    """
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()
