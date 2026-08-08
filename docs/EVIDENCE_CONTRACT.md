# EVIDENCE_CONTRACT

Status: Closed Decision

## Canonical Rules

- JSON is the canonical evidence format.
- Markdown is derived from canonical JSON.
- The schema MUST be versioned.
- Canonical JSON MUST NOT contain raw secrets.
- Raw logs are not required inside canonical JSON.
- Environment metadata MUST remain minimal.

## CheckOutcome

- `PASS`
- `FAIL`
- `ERROR`
- `SKIPPED`

Meaning:

- `PASS` means the check established that its requirement passed.
- `FAIL` means the check established that its requirement failed.
- `ERROR` means required evidence could not be established successfully.
- `SKIPPED` means the check did not run by design or policy.

## GateDecision

- `PASS`
- `FAIL`
- `REVIEW_REQUIRED`
- `INSUFFICIENT_EVIDENCE`

Default meaning:

- `PASS` means the normalized evidence satisfies the current gate policy.
- `FAIL` means evidence established that a verification requirement failed.
- `REVIEW_REQUIRED` means evidence exists but configured policy requires human review.
- `INSUFFICIENT_EVIDENCE` means required evidence could not be established with enough confidence to pass the gate.

## Default Precedence

A required check that cannot execute successfully MUST produce `ERROR` at the check level and SHOULD default to `INSUFFICIENT_EVIDENCE` at the gate level.

`ERROR` MUST NOT automatically become `FAIL`.

A later policy MAY explicitly map `ERROR` differently, but the default semantics are closed by this document.

## Conceptual EvidenceBundle

```text
schema_version
evidence_id
product_version

run_id
started_at
finished_at

repository
base_revision
head_revision

invocation_mode

configuration_hash
policy_hash

tool_versions

checks[]
    id
    collector_id
    required
    outcome
    duration
    summary
    findings

change_summary

warnings[]

decision
decision_reasons[]

environment_metadata
```

## Determinism And Reproducibility

Deterministic evaluation means the same normalized evidence plus the same policy produces the same `GateDecision`.

Reproducibility is a semantic evidence reproducibility claim under equivalent inputs and tooling. It is NOT a guarantee of byte-for-byte identical artifacts, because timestamps and run IDs may naturally differ.

## Exclusions

This contract does NOT define SARIF, SBOM, or in-toto implementations.
