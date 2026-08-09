# Community v0.1.0 Release Protocol

This document defines the governed release gates and execution sequence for
the first DiffSeal Community release. Live external state must be re-verified
immediately before each irreversible release operation. This document is a
protocol, not a live snapshot of current external configuration.

## Fixed release identities

- Product: `DiffSeal`
- Repository: `zuli2021/diffseal`
- Package: `diffseal`
- Version: `0.1.0`
- Release-specific tag: `v0.1.0`
- GitHub Release: `v0.1.0`
- PyPI workflow: `publish-pypi.yml`
- GitHub environment: `pypi`

## Release artifacts

Intended first-release artifacts:

- source repository
- Git tag `v0.1.0`
- GitHub Release `v0.1.0`
- Python sdist
- Python wheel
- PyPI project `diffseal`
- GitHub Marketplace Action `DiffSeal`

Not in scope for v0.1: Docker, GHCR, SBOM, provenance bundle, custom binaries,
installers, Homebrew, Scoop, Winget, crates.io.

## Release boundaries

- The first canonical release authorizes only the release-specific tag
  `v0.1.0`.
- A moving compatibility alias `v0` is NOT part of the v0.1.0 execution
  sequence. Any moving major alias remains a separately governed future
  decision and operation.
- PyPI publication is not a manually started step. The GitHub Release
  `published` event triggers `publish-pypi.yml` automatically.
- Marketplace Action publication is associated with publishing a tagged GitHub
  Release through the Release Action UI. It is not a guaranteed, fully
  independent post-release API step, and it requires eligibility verification
  before release publication.

## GitHub `pypi` environment invariant

Immediately before release, verify the protected publishing environment:

- environment name = `pypi`
- required reviewer = owner
- `prevent_self_review` = false for sole-owner operation
- `can_admins_bypass` = false
- deployment policy allows the intended governed release/tag context
- unnecessary environment secrets = none
- long-lived PyPI API token = none

Do not mutate the environment during release execution.

## PyPI namespace / pending publisher rule

A Pending Trusted Publisher does NOT reserve the project name until first
successful publication. A fresh PyPI namespace check is required immediately
before the irreversible tag/release sequence.

Immediately before release, verify the Pending Trusted Publisher matches:

- project: `diffseal`
- owner: `zuli2021`
- repository: `diffseal`
- workflow: `publish-pypi.yml`
- environment: `pypi`

If the `diffseal` PyPI namespace becomes occupied unexpectedly:

- STOP
- do not create the tag
- do not create the GitHub Release
- do not upload manually
- report the naming/distribution collision for governed recovery

No API-token fallback is permitted.

## Owner authorization

Every irreversible external mutation requires explicit owner authorization at
execution time. This document does not store a permanent authorization state.

## First-release sequence

1. Verify final public `main` SHA and green CI.
2. Verify clean local state.
3. Verify GitHub presentation metadata.
4. Verify tags = 0 and GitHub Releases = 0.
5. Recheck PyPI `diffseal` namespace.
6. Verify exact Pending Trusted Publisher configuration.
7. Verify exact GitHub `pypi` environment/protection/policy.
8. Verify release and publish workflow contents.
9. Verify GitHub Marketplace eligibility immediately before release
   publication (Action metadata valid; `DiffSeal` Marketplace name available;
   Marketplace Developer Agreement accepted / publish checkbox usable), if
   Marketplace publication is included in the release operation.
10. Create the exact release-specific tag `v0.1.0` at the final governed
    public-main SHA.
11. Push only `v0.1.0`.
12. Wait for the tag-triggered Release validation workflow to succeed.
13. Prepare the GitHub Release using the EXISTING `v0.1.0` tag.
14. Review release title/notes and Marketplace selection before publishing.
15. Publish GitHub Release `v0.1.0`.
16. Publishing the GitHub Release naturally triggers `publish-pypi.yml`.
17. Approve the protected `pypi` environment when GitHub requests owner
    approval.
18. Let Trusted Publishing/OIDC publish to PyPI.
19. Verify PyPI metadata and clean install.
20. Verify GitHub Release/tag identity.
21. Verify Action use from `zuli2021/diffseal@v0.1.0`.
22. Verify Marketplace listing if it was included.
23. Produce the final release closure report.

## Verification

See `tests/test_release_hardening.py` for automated validation of release
hardening, including the durable release protocol assertions.
