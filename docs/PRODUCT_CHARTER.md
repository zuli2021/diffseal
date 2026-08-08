# PRODUCT_CHARTER

Status: Architecture Closed

## Product

DiffSeal is a local-first, Python-first PR evidence/proof gate that turns verification signals for one exact repository change into one normalized evidence bundle and one explicit review-readiness decision.

## Target Buyer

- solo Python developer
- freelancer or consultant
- very small engineering team or technical owner
- developers reviewing AI-assisted changes

## Core Pain

Verification is scattered across pytest, Ruff, coverage, dependency, and CI outputs, forcing the reviewer to manually determine whether an exact change is ready for review.

## Value Proposition

One exact change -> real verification signals -> normalized evidence -> one readable proof packet -> one explicit decision.

## Positioning

DiffSeal MUST be positioned as a local developer tool for review readiness.
DiffSeal MUST NOT be positioned as a compliance platform, governance infrastructure, AI code reviewer, SaaS quality platform, security scanner, or replacement for pytest, Ruff, or coverage.

## Scope Principles

- Local-first operation is REQUIRED.
- Python-first scope is REQUIRED.
- Public release remains owner-gated.

## Identity

- Product name: `DiffSeal`
- CLI identity: `diffseal`
- Python package identity: `diffseal`
- Repository identity: `diffseal`
- Name status: `APPROVED_AND_FROZEN`

## Community And Pro

- Community license: Apache-2.0
- Pro license: proprietary commercial license
- Community MUST remain independently useful.
- Community MUST NOT depend on Pro.

## Explicit Non-Goals

DiffSeal MUST NOT introduce microservices, a database, a SaaS backend, hosted evidence storage, dashboards, accounts, SSO, RBAC, organizations, a GitHub App, GitLab support, a generic multi-language framework, Python entry-point plugin discovery, OPA/Rego, an LLM requirement, an AI reviewer, a custom scanner, a custom test runner, SARIF, SBOM, Sigstore, in-toto, compliance mapping, GRC integrations, a license server, DRM, or mandatory telemetry.
