# DECISIONS

Status: Living Decision Record

This file records governed product decisions for DiffSeal. Decisions listed
here are authoritative for the repository. Superseded decisions remain visible
in git history and in superseded documents referenced below.

## DIFFSEAL-SINGLE-FREE-OSS-001 — One free open-source Apache-2.0 product

- Status: APPROVED
- Owner approval: recorded in this repository's governance package
  (mission DIFFSEAL-FREE-PROFESSIONAL-V020-001, executed by OpenCode on
  2026-09-11 against repository baseline `7bc5e7dc574815d75682f947812db207decb0e79`).

### Decision

1. The previous Community/Pro commercial split is **superseded**. DiffSeal is
   one free, open-source product.
2. License: **Apache-2.0** for the entire product. There is no proprietary
   tier, no paid edition, and no checkout.
3. Product/repository/package/CLI/Action identities are unchanged:
   - Product name: `DiffSeal`
   - Repository identity: `diffseal` (`zuli2021/diffseal`)
   - Python distribution identity: `diffseal`
   - Python import identity: `diffseal`
   - CLI identity: `diffseal`
   - GitHub Action identity: `DiffSeal`
4. Architecture style and evidence semantics remain intact: small modular
   monolith, local-first, Python-first, collectors normalize tool output
   without defining gate semantics, one shared evaluation path, canonical
   JSON evidence with derived Markdown, thin GitHub Action adapter. The only
   authorized evolution is the explicitly versioned **additive** evidence
   schema change to `0.2` (structured change summary, dependency delta,
   decision reason codes).
5. No proprietary Pro repository or package is required. The previously open
   `ERR-DIFFSEAL-PRO-SOURCE-BOUNDARY-001` question is closed by this
   decision: there is no proprietary source boundary to define.
6. Distribution remains free of charge: GitHub, PyPI, GitHub Marketplace
   Action, and documentation. No payment provider, price, funnel, or
   purchase metrics apply to DiffSeal.

### Consequences

- `docs/PRODUCT_CHARTER.md`, `docs/ROADMAP.md`, and `README.md` describe one
  product line.
- `docs/COMMERCIAL_RELEASE_POLICY.md` is superseded by
  `docs/RELEASE_DISTRIBUTION_POLICY.md`.
- `docs/DISTRIBUTION_COMPLIANCE_MATRIX.md` Pro/proprietary/commercial entries
  are reconciled with the one-product Apache-2.0 model.
- Release vs. launch distinction and owner gates for tag/release/publication
  remain in force.
- The v0.2 professional feature milestone (change intelligence, dependency
  delta, decision reason codes, advanced reviewer report, GitHub Action UX,
  cross-platform release hardening) is in scope for the open-source product;
  changed-line/diff coverage remains deferred.
