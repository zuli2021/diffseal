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

## First-party action pinning

Example workflows reference first-party actions by major-version release tag (for example `actions/setup-python@v5`, `actions/upload-artifact@v4`). At the governed Community release, these references are replaced with immutable commit SHAs. DiffSeal is always referenced as `owner/diffseal@<ref>` where `<ref>` is the pinned release.

## Verification

See `tests/test_action.py` and `tests/test_workflows.py` for automated validation of these guarantees, including structured YAML parsing of the Action metadata and workflow files.
