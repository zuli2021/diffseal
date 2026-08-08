"""Derived Markdown reporter.

``evidence.md`` is derived from the canonical EvidenceBundle and prioritizes
reviewer usability: repository/change, final decision, decision reasons, each
check with PASS/FAIL/ERROR/SKIPPED and required/optional status, concise
findings, warnings, and tool versions.
"""

from __future__ import annotations

from pathlib import Path

from diffseal.models import EvidenceBundle


def render_markdown(bundle: EvidenceBundle) -> str:
    """Render an EvidenceBundle as reviewer-oriented Markdown."""
    lines: list[str] = []
    lines.append("# DiffSeal Evidence\n")

    decision = bundle.decision.value if bundle.decision is not None else "N/A"
    lines.append(f"## Decision: **{decision}**\n")

    if bundle.decision_reasons:
        lines.append("### Reasons")
        for reason in bundle.decision_reasons:
            lines.append(f"- {reason}")
        lines.append("")

    lines.append("### Run")
    lines.append(f"- Schema version: `{bundle.schema_version}`")
    lines.append(f"- Evidence ID: `{bundle.evidence_id}`")
    lines.append(f"- Run ID: `{bundle.run_id}`")
    lines.append(f"- Product version: `{bundle.product_version}`")
    lines.append(f"- Started: `{bundle.started_at}`")
    lines.append(f"- Finished: `{bundle.finished_at}`")
    lines.append(f"- Invocation mode: `{bundle.invocation_mode}`")
    lines.append(f"- Configuration hash: `{bundle.configuration_hash}`")
    lines.append(f"- Policy hash: `{bundle.policy_hash}`")
    lines.append("")

    lines.append("### Repository / Change")
    lines.append(f"- Repository: `{bundle.repository or 'n/a'}`")
    lines.append(f"- Base revision: `{bundle.base_revision or 'n/a'}`")
    lines.append(f"- Head revision: `{bundle.head_revision or 'n/a'}`")
    for key, value in sorted(bundle.change_summary.items()):
        lines.append(f"- {key}: `{value}`")
    lines.append("")

    if bundle.checks:
        lines.append("## Checks\n")
        for check in bundle.checks:
            lines.append(f"### {check.id} ({'required' if check.required else 'optional'})")
            lines.append(f"**{check.outcome.value}** — {check.summary}")
            lines.append(f"- collector: `{check.collector_id}`")
            lines.append(f"- duration: {check.duration:.3f}s")
            if check.findings:
                lines.append("")
                lines.append("Findings:")
                for finding in check.findings:
                    if finding.data:
                        lines.append(f"- `{finding.code}` {finding.message} {finding.data}")
                    else:
                        lines.append(f"- `{finding.code}` {finding.message}")
            lines.append("")

    if bundle.tool_versions:
        lines.append("## Tool Versions")
        for name, version in sorted(bundle.tool_versions.items()):
            lines.append(f"- {name}: `{version}`")
        lines.append("")

    if bundle.warnings:
        lines.append("## Warnings")
        for warning in bundle.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    return "\n".join(lines) + "\n"


def write_markdown(bundle: EvidenceBundle, path: Path) -> Path:
    """Write derived ``evidence.md`` and return the written path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(bundle), encoding="utf-8")
    return path
