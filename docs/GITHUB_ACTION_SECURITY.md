# GitHub Action Security

This document explains the security model of the DiffSeal GitHub Action and the example workflow. It applies to the Action shipped in this repository (`action.yml`) and the usage example in `examples/workflow/diffseal.yml`.

## Threat model

DiffSeal executes verification tools against the checked-out repository state. In a GitHub Actions context, a pull request may contain untrusted code, including code that runs during `diffseal run` (for example, `pytest` executes the repository's test code and imports its modules).

Because the repository under evaluation is untrusted, the Action and its workflow must not be given elevated access:

- No elevated secrets or write tokens.
- No `pull_request_target`. Normal DiffSeal execution always runs in the merge-commit/`pull_request` context where fork code runs without access to repository secrets.
- Fork pull requests must remain usable without any repository secret.

## Default permissions

The example workflow uses:

```yaml
permissions:
  contents: read
```

The Action requires no repository secrets. `contents: read` is sufficient for checking out the repository and uploading evidence artifacts.

## Rules enforced by the example

- Trigger: `pull_request` (never `pull_request_target`).
- No PR comment posting.
- No write token.
- Evidence upload uses `actions/upload-artifact` with `name`/`path` only; artifact upload does not require repository write permission.
- No repository secret is referenced.

## Shell safety

The Action never executes user-controlled command strings. Action inputs are passed to the DiffSeal CLI as positional arguments via environment variables, never interpolated into a shell command. No `sh -c`, `bash -c`, `eval`, or equivalent is used with user input.

## Evidence content

Evidence artifacts may contain tool findings, filenames, and normalized check results. They must not contain environment-secret dumps. DiffSeal's process boundary runs tools with a sanitized allow-listed environment and never writes the full environment into evidence.

## Third-party action pinning

All external GitHub Actions referenced by DiffSeal workflows and the Action itself are pinned to full immutable commit SHAs, verified as originating from the official upstream repository. Every reference keeps a short version comment for maintainability, for example:

```yaml
uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

Current pinned set (verified against each official repository and current stable release):

| Action | Pinned version | Commit SHA |
|---|---|---|
| actions/checkout | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-python | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| actions/upload-artifact | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| actions/download-artifact | v8.0.1 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| pypa/gh-action-pypi-publish | v1.14.2 | `dc37677b2e1c63e2034f94d8a5b11f265b73ba33` |

Automated tests scan every committed workflow/example YAML and require every third-party GitHub Action reference to use a full 40-character commit SHA. Local `uses: ./...` references are exempt.

DiffSeal's own governed self-reference is `zuli2021/diffseal@v0.1.0`. It is the exact release-specific self-reference and is validated separately from third-party Action SHA pins; its release identity is governed as the `v0.1.0` release-specific tag. No other version-tag or moving-branch Action reference is accepted by the pinning tests.

## Verification

See `tests/test_action.py` and `tests/test_workflows.py` for automated validation of these guarantees, including structured YAML parsing of the Action metadata and workflow files.
