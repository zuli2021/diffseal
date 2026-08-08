"""End-to-end orchestration for a DiffSeal run.

Loads configuration, discovers repository context, executes configured
collectors, normalizes results into an ``EvidenceBundle``, evaluates the gate
decision, and writes canonical JSON plus derived Markdown.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from pathlib import Path

from diffseal import __version__
from diffseal.collectors import (
    Collector,
    CoverageCollector,
    DependencyCollector,
    PytestCollector,
    RuffCollector,
)
from diffseal.config import CheckConfig, Config, load_config
from diffseal.evaluate import evaluate
from diffseal.models import CheckResult, EvidenceBundle, GateDecision
from diffseal.reporters import write_json, write_markdown
from diffseal.repository import discover_context

EVIDENCE_JSON = "evidence.json"
EVIDENCE_MD = "evidence.md"


class RunError(Exception):
    """Raised when a run cannot be completed."""


@dataclass
class RunResult:
    """Outcome of a run plus paths of written artifacts."""

    bundle: EvidenceBundle
    json_path: Path
    markdown_path: Path

    @property
    def decision(self) -> GateDecision:
        if self.bundle.decision is None:  # pragma: no cover - always set after a run
            raise RunError("run completed without a decision")
        return self.bundle.decision


def _collector_for(check: CheckConfig) -> Collector:
    collectors = {
        "pytest": PytestCollector(),
        "ruff": RuffCollector(),
        "coverage": CoverageCollector(),
        "dependency": DependencyCollector(),
    }
    try:
        return collectors[check.collector_id]
    except KeyError as exc:  # pragma: no cover - config validation prevents this
        raise RunError(f"no collector registered for {check.collector_id!r}") from exc


def build_bundle(
    config: Config,
    checks: list[CheckResult],
    cwd: Path,
    started_at: str,
    finished_at: str,
    run_id: str,
    evidence_id: str,
    tool_versions: dict[str, str],
) -> EvidenceBundle:
    """Assemble a canonical EvidenceBundle from a completed run."""
    context = discover_context(cwd, base_revision=config.repository.base_revision)
    evaluation = evaluate(checks, config.evaluation.review_on)

    bundle = EvidenceBundle(
        schema_version="0.1",
        evidence_id=evidence_id,
        product_version=__version__,
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        repository=str(context.root) if context.root is not None else str(cwd),
        base_revision=context.base_revision or "",
        head_revision=context.head_revision or "",
        invocation_mode="local-cli",
        configuration_hash=config.configuration_hash,
        policy_hash=config.policy_hash,
        tool_versions=tool_versions,
        checks=checks,
        change_summary=context.change_summary,
        warnings=list(context.warnings),
        decision=evaluation.decision,
        decision_reasons=list(evaluation.reasons),
        environment_metadata={
            "python_version": _python_version(),
            "platform": _platform(),
            "cwd": str(cwd),
        },
    )
    return bundle


def _python_version() -> str:
    import sys

    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _platform() -> str:
    import platform

    return platform.system().lower()


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run(
    cwd: Path,
    config_path: Path | None = None,
    output_dir: Path | None = None,
    timeout: float = 180.0,
) -> RunResult:
    """Run configured collectors, evaluate, and write evidence artifacts."""
    config = load_config(cwd, explicit=config_path)
    started_at = _now_iso()

    enabled = config.enabled_checks()
    tool_versions: dict[str, str] = {}
    results: list[CheckResult] = []
    for check in enabled:
        collector = _collector_for(check)
        version = collector.version()
        if version:
            tool_versions.setdefault(check.collector_id, version)
        results.append(collector.collect(check, cwd=cwd, timeout=timeout))

    finished_at = _now_iso()
    run_id = uuid.uuid4().hex
    evidence_id = uuid.uuid4().hex

    bundle = build_bundle(
        config,
        results,
        cwd,
        started_at,
        finished_at,
        run_id,
        evidence_id,
        tool_versions,
    )

    target_dir = (output_dir or cwd).resolve()
    json_path = write_json(bundle, target_dir / EVIDENCE_JSON)
    markdown_path = write_markdown(bundle, target_dir / EVIDENCE_MD)
    return RunResult(bundle=bundle, json_path=json_path, markdown_path=markdown_path)


def plan(cwd: Path, config_path: Path | None = None) -> dict[str, object]:
    """Produce a deterministic, human-readable execution plan.

    Never executes verification tools.
    """
    config = load_config(cwd, explicit=config_path)
    context = discover_context(cwd, base_revision=config.repository.base_revision)
    checks = [
        {
            "id": check.id,
            "collector_id": check.collector_id,
            "required": check.required,
            "enabled": check.enabled,
            "description": check.description,
            "args": list(check.args),
            "threshold": check.threshold,
        }
        for check in config.checks.values()
    ]
    return {
        "config_path": str(config.path) if config.path else "<defaults>",
        "repository_root": str(context.root) if context.root else "<not a git repository>",
        "checks": checks,
        "review_on": list(config.evaluation.review_on),
        "base_revision": context.base_revision,
    }


def render_plan(plan_data: dict[str, object]) -> str:
    """Render a plan dict as deterministic, readable text."""
    lines: list[str] = []
    lines.append("DiffSeal execution plan")
    lines.append(f"Configuration : {plan_data['config_path']}")
    lines.append(f"Repository     : {plan_data['repository_root']}")
    lines.append(f"Base revision  : {plan_data['base_revision'] or '<none>'}")
    lines.append("")
    lines.append("Checks:")
    checks = plan_data["checks"]
    if not isinstance(checks, list):
        raise RunError("invalid plan data")
    for entry in checks:
        if not isinstance(entry, dict):
            raise RunError("invalid plan data")
        marker = "x" if entry.get("enabled") else "-"
        status = "required" if entry.get("required") else "optional"
        threshold = entry.get("threshold")
        threshold_text = f", threshold={threshold:g}" if isinstance(threshold, (int, float)) else ""
        lines.append(
            f"  [{marker}] {entry['id']:<10} {status:<8} "
            f"{entry.get('description', '')}{threshold_text}"
        )
    raw_review_on = plan_data.get("review_on")
    review_on = raw_review_on if isinstance(raw_review_on, list) else []
    lines.append("")
    joined_review = ", ".join(review_on) if review_on else "<none>"
    lines.append(f"Review-on failing optional checks: {joined_review}")
    lines.append("This plan does not execute any verification tool.")
    return "\n".join(lines) + "\n"
