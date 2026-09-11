# RELEASE_DISTRIBUTION_POLICY

Status: Closed Decision

Supersedes `docs/COMMERCIAL_RELEASE_POLICY.md` (removed by rename) under
decision `DIFFSEAL-SINGLE-FREE-OSS-001` (`docs/DECISIONS.md`): DiffSeal is one
free, open-source Apache-2.0 product. There is no paid edition, no checkout,
no payment provider, and no purchase funnel.

## Release And Launch

Release is not launch.

Public publication (tag, GitHub Release, PyPI upload, Marketplace
publication) requires explicit owner authorization at execution time.

No public namespace change is authorized without explicit governance.

## Frozen Identities

- Product identity: `DiffSeal`
- CLI identity: `diffseal`
- Python package identity: `diffseal`
- Repository identity: `diffseal`
- GitHub Action identity: `DiffSeal`

Repository or Action renaming after adoption MUST be treated as a
compatibility-breaking distribution concern.

## Licensing And Delivery

- The product is licensed Apache-2.0, free of charge.
- Distribution artifacts are the standard open-source Python artifacts:
  sdist and wheel, plus the composite GitHub Action.
- No runtime DRM or license server. No mandatory telemetry.
- No checkout, payment provider, or purchase metrics exist for DiffSeal.

## Distribution Surfaces

Distribution surfaces: GitHub repository, GitHub Releases, PyPI, GitHub
Actions Marketplace, product documentation.

GitHub availability alone MUST NOT be interpreted as launch.

Intentional launch SHOULD use qualified external channels such as targeted
developer outreach, a technical demonstration or article, an appropriate
technical community, and Product Hunt only if launch assets justify it.

Required launch assets: usable product documentation, a demo, and install
guidance.

## Adoption Understanding

Meaningful, truthful adoption signals (no analytics infrastructure):

- qualified exposure
- product-page visit
- install
- successful first run
- repeated use / Action use
- feedback

Important distinctions (do not conflate):

- GitHub view is not a qualified visitor.
- download is not install.
- install is not successful first run.
- star is not adoption.
- feedback is not usage growth.

Activation means a successful first run of DiffSeal with usable evidence
output.

Continue/improve decisions SHOULD be based on qualified traffic, activated
users, and real feedback rather than raw GitHub traffic.

## Constraints

- No compliance claims.
- No public namespace changes without explicit governance.
- Public publication remains owner-gated.
