# Community Release Preflight

Operational release gates for the first governed public DiffSeal Community
release. This document records local preflight results and the exact external
steps that require owner authorization. It is not new architecture.

## Status

- Local preflight: COMPLETE (see PKG-004).
- External public release: NOT AUTHORIZED. `EXTERNAL_PUBLIC_RELEASE_AUTHORIZED`
  remains FALSE until owner authorization is granted.

## Version / release identity

- Package version: `0.1.0`
- Release-specific Git tag: `v0.1.0`
- GitHub Release: `v0.1.0`
- Optional moving Action compatibility tag: `v0` -> `v0.1.0`
  - `v0.1.0` is the governed release-specific tag identity.
  - `v0` is a movable compatibility alias for consumers; moving it later is an
    intentional, governed release operation.
  - `v0` does not imply `v1` semantics for a 0.x package.

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

## Namespace preflight (read-only, at PKG-004 time)

- PyPI project `diffseal`: AVAILABLE (registry lookup 404).
- GitHub user/org `diffseal`: not found (no exact collision observed).
- Exact `owner/diffseal` repository: not queryable until the owner is resolved.
- GitHub Marketplace `DiffSeal`: no collision observed in read-only search;
  reconfirm after the public repository exists.

Important: a PyPI pending Trusted Publisher does NOT reserve the project name
until first successful publication. Namespace availability must be rechecked
immediately before the actual release operation.

## Future PyPI pending Trusted Publisher fields (do not submit)

- PyPI project: `diffseal`
- GitHub owner: `<UNRESOLVED UNTIL OWNER/REMOTE AUTHORIZATION>`
- Repository: `diffseal`
- Workflow filename: `publish-pypi.yml`
- Environment: `pypi`

## GitHub `pypi` environment requirements (future configuration)

Required for the protected publishing environment:

- required reviewer/owner approval;
- prevent self-review where practical;
- restrict deployment to the intended release/tag context where available;
- no unnecessary environment secrets;
- no long-lived PyPI token.

This environment is NOT configured in PKG-004 and MUST NOT be claimed as
configured. It is an external gate.

## External configuration still required

1. GitHub repository creation and visibility (owner-gated).
2. GitHub `pypi` protected environment configuration.
3. PyPI pending Trusted Publisher creation (after repository exists).
4. GitHub Marketplace agreement and publication (separately governed).
5. Immutable-SHA pinning of any newly added third-party Actions.

## Proposed first-release sequence

1. Final clean local baseline.
2. External namespace recheck (PyPI, GitHub, Marketplace).
3. Create the owner-approved GitHub repository.
4. Configure the protected `pypi` environment.
5. Configure the PyPI pending Trusted Publisher.
6. Push `main`.
7. Verify GitHub CI on `main`.
8. Create and push tag `v0.1.0`.
9. Verify the tag-triggered release validation workflow.
10. Create/publish the GitHub Release `v0.1.0`.
11. Publish the Action to the GitHub Marketplace via the governed release UI.
12. The protected OIDC workflow publishes to PyPI.
13. Verify the PyPI package.
14. Verify the Marketplace listing.
15. Verify installation from PyPI (`pip install diffseal`).
16. Verify the Action from the public tag.
17. Final canonical release verdict.

None of these steps may be executed without separate owner authorization.
