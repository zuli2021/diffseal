# ROADMAP

Status: Execution Milestones Only

Milestones follow decision `DIFFSEAL-SINGLE-FREE-OSS-001`
(`docs/DECISIONS.md`): DiffSeal is one free open-source Apache-2.0 product.
There is no paid tier and no proprietary edition.

## Milestone 1 - Canonical closure (DONE)

Product, architecture, evidence, and governance decisions recorded in
canonical repository documents (`docs/DECISIONS.md` and companion docs).

## Milestone 2 - Core (DONE, v0.1)

- package skeleton, models, EvidenceBundle schema 0.1
- config, check and gate semantics
- subprocess and tool invocation boundary
- pytest, Ruff, basic coverage, dependency collectors
- JSON and Markdown reporters
- CLI `diffseal init` / `diffseal plan` / `diffseal run`
- tests, lint, typecheck, build

## Milestone 3 - Distribution (DONE, v0.1.1)

- composite GitHub Action
- secure permissions, fork threat tests
- example repository, README and quickstart, sample evidence
- PyPI packaging, Trusted Publishing preparation
- release automation, Marketplace metadata

## Milestone 4 - Professional features (v0.2, in progress)

- deterministic base-to-head change intelligence
- dependency delta between base and head
- structured, stable decision reason codes
- advanced reviewer-facing report derived from canonical evidence
- GitHub Action UX (step summary, revision outputs)
- cross-platform CI and release hardening

Deferred beyond v0.2 (not implemented in this milestone):

- changed-line / diff coverage

## Later stabilization (toward v1.0)

- hardening and polish based on real usage feedback
- performance and large-repository behavior
- documentation expansion

No dates are invented for future milestones. No speculative phases are
authorized beyond this sequence.
