# DiffSeal Distribution Compliance Matrix

Status: Noncanonical distribution/evidence artifact. This document records
distribution-channel compliance evidence and prerequisite analysis. It does
not modify product architecture. It does not authorize publication.

Generated at baseline commit `00874ff6696bc038ae3abcb42fd09f85e1dec800`.

---

## 1. Current Distribution Baseline

Evidence recorded from the repository and public state at baseline.

| Item | Value | Evidence |
|---|---|---|
| Current main SHA | `00874ff6696bc038ae3abcb42fd09f85e1dec800` | `git rev-parse HEAD` |
| Package version | `0.1.1` | `pyproject.toml` `version = "0.1.1"` |
| Python requirement | `>=3.10` | `pyproject.toml` `requires-python` |
| Package license | Apache-2.0 (SPDX expression) | `pyproject.toml` `license = "Apache-2.0"`, `license-files = ["LICENSE"]` |
| License file | `LICENSE` (Apache-2.0 text) | repository root |
| CLI entry point | `diffseal` | `pyproject.toml` `[project.scripts]` |
| Package formats produced | sdist + wheel (`diffseal-0.1.1.tar.gz`, `diffseal-0.1.1-py3-none-any.whl`) | local build and PyPI |
| GitHub Action | published; root `action.yml`, name `DiffSeal`, composite | `action.yml`; Marketplace listing live |
| GitHub Marketplace | LIVE | https://github.com/marketplace/actions/diffseal |
| PyPI | LIVE (`diffseal` 0.1.1 published) | https://pypi.org/project/diffseal/ |
| Upstream maturity wording | Alpha (`Development Status :: 3 - Alpha`; README "early/Alpha release line") | `pyproject.toml` classifiers, `README.md` |
| Windows-native portable executable | NONE | no DiffSeal `.exe`/`.msi`/`.msix`/portable zip; v0.1.1 release has no binary assets |
| Root legal/distribution files | `LICENSE`, `README.md`, `pyproject.toml`, `action.yml` | repository root |
| Author/publisher evidence | `Zuli2021 <zulisaberi@gmail.com>` | git commits; `pyproject.toml` authors |
| Adoption evidence | 0 stars, 0 forks | GitHub API |

Public releases: `v0.1.0` (`764ebdc3072199ed9a68daee2a8b515b8c8ff8f4`) and
`v0.1.1` (`e66aff6bb4c26c8c915d1c0439c73913e8a9369d`), both non-draft,
non-prerelease. No `v0` alias.

---

## 2. Channel Matrix

For each channel: status classification `READY` / `CONDITIONAL` / `BLOCKED` /
`LIVE` / `LIVE_WITH_OPEN_ERR` is evidence-backed, not assumed from "can
technically create a package".

### 3. GitHub Marketplace

- A. Channel: GitHub Marketplace
- B. Intended package type: GitHub composite Action
- C. Eligibility today: published (LIVE)
- D. Required fields (official listing): name, short description, category (primary/secondary), repository, release tag
- E. Optional but recommended: long description, screenshots, links
- F. Field-length / validator constraints: action `name` and `description` are required metadata; Marketplace validates action metadata during publication. Exact Marketplace UI/validator limits must be rechecked before a future Marketplace publication; no permanent numeric limit is asserted without current official evidence. Current DiffSeal description length is 103 characters.
- G. Accepted license representation: repository license metadata (Apache-2.0 shown)
- H. Source/artifact requirements: repository with root `action.yml`; immutable release tag
- I. Checksum/signature requirements: none for Action metadata
- J. Install/uninstall requirements: composite Action consumed by workflows
- K. Validation commands: GitHub web-UI "Publish this Action to the GitHub Marketplace" validator
- L. Automated validation: GitHub Release flow parse of `action.yml`
- M. Human/manual review gate: publication through owner release UI; Marketplace eligibility
- N. Owner-only interaction: release publication UI; category selection
- O. Namespace/name collision check: listing name `DiffSeal` live and unique
- P. Resubmission semantics: new release tag for new version
- Q. Current DiffSeal blocker: none for Community listing; legal item below
- R. Next prerequisite: none
- S. Status: **LIVE_WITH_OPEN_ERR**

**Legal open item:**

`MARKETPLACE_EULA_INTERPRETATION = OPEN / ERR-DIFFSEAL-LEGAL-001`

GitHub Marketplace Developer Agreement section 2.4 requires a separate EULA
for Developer Products. Whether `LICENSE` (Apache-2.0) alone satisfies that
language is not decided here. This document does not modify Marketplace or
legal files and does not assert an interpretation.

### 4. PyPI

- A. Channel: PyPI
- B. Intended package type: Python sdist + wheel
- C. Eligibility today: published (LIVE)
- D. Required fields: Core Metadata mandatory fields are `Metadata-Version`, `Name`, and `Version`. DiffSeal intentionally also publishes `description`, `author`, the Apache-2.0 license expression/license file, `Requires-Python`, project URLs, classifiers, and other project metadata.
- E. Optional but recommended: project URLs, keywords, classifiers, license metadata, Requires-Python (all intentionally published by DiffSeal)
- F. Field-length / validator constraints: PEP 621 / PEP 639 metadata model; field-length limits are validator-governed (e.g., PyPI's metadata validator) and are not asserted here as invented numeric limits
- G. Accepted license representation: SPDX license expression (`Apache-2.0`) plus `license-files`
- H. Source/artifact requirements: building/publishing both sdist and wheel is DiffSeal's selected release policy and PyPA-recommended practice; PyPI acceptance does not inherently require both formats
- I. Checksum/signature requirements: SHA-256 digests published per file
- J. Install/uninstall requirements: standard pip install/uninstall
- K. Validation commands: `pip install`, `importlib.metadata.version`
- L. Automated validation: Trusted Publishing / OIDC publish workflow (`publish-pypi.yml`)
- M. Human/manual review gate: protected `pypi` environment owner approval
- N. Owner-only interaction: `pypi` environment `Approve and deploy`
- O. Namespace/name collision check: `diffseal` published and owned
- P. Resubmission semantics: new version upload; immutability by version; yanking is available but should be used only deliberately
- Q. Current DiffSeal blocker: none
- R. Next prerequisite: none
- S. Status: **LIVE**

Current live metadata: `License-Expression: Apache-2.0`, `License-File: LICENSE`,
project URLs Repository + Issues, `requires-python >=3.10`, version `0.1.1`
published with wheel and sdist, neither yanked.

### 5. Chocolatey

**A. NuSpec / package metadata:**

- `.nupkg` package with `chocolateyinstall.ps1` (and optional embedded or downloaded binary)
- non-empty `projectUrl` is a Community Repository requirement
- `authors` must describe the software author/vendor accurately
- `copyright` must reflect actual evidence
- `licenseUrl` is required when a license exists
- `description` is moderation/validator governed (Package Validator checks description character count above 4000 — description limited to 4000 characters)
- `tags` are validator/moderation governed
- `packageSourceUrl` / `iconUrl` remain recommended / as-applicable

**B. Community Repository moderation requirements:**

- normal Community packages/new versions are subject to moderation/human approval (docs.chocolatey.org moderation lifecycle)
- submission account and moderation communication are owner-only
- package id uniqueness is enforced

**C. Eligibility today:** BLOCKED_BY_GOVERNED_ARTIFACT_STRATEGY (see
platform-capability vs recommended-architecture distinction below; unresolved
legal owner/copyright identity also remains relevant for metadata).

**VERIFICATION.txt rule:**

- if binaries are EMBEDDED in the nupkg, `VERIFICATION.txt` is REQUIRED
- if the package downloads a remote artifact, checksum validation is REQUIRED
- the document does NOT claim `VERIFICATION.txt` is universally required for
  every downloaded-artifact package, and does NOT call it universally optional

**Installer/artifact model (fields):**

- source/artifact: installer or downloaded artifact with checksum
- checksum/signature: SHA-256 (and SHA-1/SHA-512 accepted) checksums for downloaded artifacts
- install/uninstall: silent install/uninstall via script or embedded binary; `chocolateyinstall.ps1` / `chocolateyuninstall.ps1` if scripts are used
- validation commands: `choco pack`, `choco install`, Package Validator run
- automated validation: Package Validator (description length, metadata, checksum, VERIFICATION where applicable)

**Key rule:**

`CHOCOLATEY_HUMAN_GATE = REQUIRED`

Future execution rule: ONE submission → STOP → wait for validator/verifier/
moderator result. No blind retry loop, no repeated push loop, no automatic
resubmission after a human/pending state.

**CHOCOLATEY PLATFORM CAPABILITY vs DIFFSEAL RECOMMENDED ARCHITECTURE:**

The document does NOT assert that Chocolatey requires DiffSeal to ship a
native Windows EXE. Chocolatey supports package-script and zip-oriented
models. This distinction is recorded explicitly:

- **TECHNICALLY POSSIBLE:** a Python/pip-oriented Chocolatey package may be
  technically possible (e.g., a package that installs/uses the Python wheel
  via pip or references a Python runtime).

- **BUT WHY THAT MAY BE A POOR DIFFSEAL PRODUCT MODEL** (analysis, not
  platform policy):
  - external Python runtime dependency (the `>=3.10` requirement must be
    satisfied on the target machine)
  - pip environment ownership and who owns/updates the installed package
  - shim/CLI discovery for the `diffseal` entry point
  - uninstall semantics (removing the pip package cleanly)
  - upgrade semantics across versions
  - dependency installation and its side effects
  - interaction with local virtualenvs on the target machine
  - Chocolatey verifier behavior on a pip-installed package
  - subprocess/tool-discovery semantics inside a pip-installed Python package
  - reproducibility of the resulting environment
  - end-user experience (Python toolchain required before install)

- **RECOMMENDED DIFFSEAL DIRECTION:** a shared Windows portable artifact may
  be materially cleaner for both WinGet and Chocolatey, subject to closure of
  `ERR-DIFFSEAL-WINDOWS-DIST-001`. The shared artifact decision is a product
  architecture decision, not a Chocolatey platform requirement.

- **Unresolved legal metadata:** legal owner/copyright identity for Chocolatey
  metadata is unresolved and is not guessed here (`ERR-DIFFSEAL-LEGAL-001` is
  the legal-boundary record).

### 6. WinGet

- A. Channel: Microsoft WinGet Community Repository (`microsoft/winget-pkgs`)
- B. Intended package type: manifest for supported installer types
- C. Eligibility today: BLOCKED (no supported installer/portable executable)
- D. Required fields (generic installer metadata): `PackageIdentifier`, `PackageVersion`, `PackageLocale`, `Publisher`, `PackageName`, `License`, `ShortDescription`, `InstallerType`, `Architecture`, `InstallerUrl`, `InstallerSha256`, `ManifestType`, `ManifestVersion`
- E. Optional but recommended: `LicenseUrl`, `PrivacyUrl`, `Description`, `Tags`
- F. Field-length / validator constraints: official schema conventions in the repo; string-length conventions documented in `microsoft/winget-pkgs` docs
- G. Accepted license representation: `License` (SPDX-ish) + optional `LicenseUrl`
- H. Source/artifact requirements: installer hosted at immutable URL; SHA-256 (`InstallerSha256`) required
- I. Checksum/signature requirements: `InstallerSha256` required
- J. Install/uninstall requirements: silent / silent-with-progress support required for the installer
- K. Validation commands: `winget validate --manifest <path>`; Windows Sandbox test (`SandboxTest.ps1`)
- L. Automated validation: winget-pkgs automated PR validation pipeline
- M. Human/manual review gate: possible manual review; Microsoft retains refusal discretion
- N. Owner-only interaction: PR submission; Microsoft review
- O. Namespace/name collision check: `PackageIdentifier` uniqueness (`Publisher.PackageName`)
- P. Resubmission semantics: PR updated on review findings; no version churn to bypass review
- Q. Current DiffSeal blocker: current artifact is a Python wheel/sdist — NOT a supported Windows installer or portable executable
- R. Next prerequisite: versioned Windows portable artifact (see Section 11)
- S. Status: **BLOCKED**

**Key rule:**

`SCRIPT_BASED_INSTALLER = NOT SUPPORTED` by the WinGet community repository
(official winget-pkgs README). This does NOT mean ZIP archives are
unsupported: current WinGet supports ZIP archive packages, portable packages
are supported, and a ZIP can contain a nested portable executable.

`CURRENT_SCHEMA_MUST_BE_RECHECKED_BEFORE_SUBMISSION`

WinGet manifest schema/version guidance evolves. Before ANY future WinGet
submission:

1. re-read the current `microsoft/winget-pkgs` PR template;
2. re-read the current manifest documentation/schema;
3. identify the then-current recommended `ManifestVersion`;
4. run the then-current validation tooling (`winget validate` and Windows
   Sandbox test).

Do NOT freeze today's schema version permanently into governance. Schema
evidence recorded in this document reflects the baseline only.

**Preferred candidate artifact shape (analysis only, not implemented):**

```
diffseal-<version>-windows-x64.zip
    containing:
        diffseal.exe
```

Conditional manifest requirements for the proposed ZIP/archive model:

- `InstallerType: zip`
- `NestedInstallerType: portable`
- `NestedInstallerFiles` with `RelativeFilePath` identifying `diffseal.exe`
- `PortableCommandAlias: diffseal` is useful for the proposed CLI but is NOT
  misclassified as universally required

with a WinGet manifest using an archive installer with a nested portable
executable (`InstallerType: zip`, `NestedInstallerType: portable`,
`PortableCommandAlias: diffseal`), IF repository/product behavior can support
this safely. No compiler/bundler is selected in this document (see Section 11).

### 7. Homebrew

- A. Channel: Homebrew core (`Homebrew/homebrew-core`)
- B. Intended package type: Formula (source build via `python` resources)
- C. Eligibility today: BLOCKED_BY_UPSTREAM_ALPHA_STATUS
- D. Candidate formula planning fields: `desc`, `homepage`, `url`, `sha256`, `license`. `version` must resolve correctly; Homebrew normally derives version from the URL/tag, and an explicit `version` is used only when derivation is insufficient or requires an override — it is not listed as universally required.
- E. Optional but recommended: resources for Python dependencies with pinned `sha256`
- F. Field-length / validator constraints: `brew audit` conventions
- G. Accepted license representation: `license` field (SPDX)
- H. Source/artifact requirements: stable upstream release with immutable, versioned, verifiable source tarball; SHA-256
- I. Checksum/signature requirements: `sha256` required for formula/resource
- J. Install/uninstall requirements: `brew install`/`uninstall`; supported CI matrix (`brew test-bot`)
- K. Validation commands: `brew audit --new --formula <formula>`, `brew test-bot`
- L. Automated validation: Homebrew CI on PR
- M. Human/manual review gate: maintainer review via PR
- N. Owner-only interaction: PR submission; maintainer review
- O. Namespace/name collision check: formula name uniqueness
- P. Resubmission semantics: PR updated per maintainer feedback
- Q. Current DiffSeal blocker: upstream maturity is Alpha (`Development Status :: 3 - Alpha`; README "early/Alpha"); open-source/DFSG-compatible license requirement is satisfied by Apache-2.0, but Alpha maturity is not changed here to satisfy Homebrew
- R. Next prerequisite: a genuine stable upstream status (a real product/release decision, not an edit)
- S. Status: **BLOCKED_BY_UPSTREAM_ALPHA_STATUS**

A third-party tap is technically possible but is lower-value acquisition and
not the preferred immediate channel unless later evidence justifies it.

### 8. Scoop

- A. Channel: Scoop Main bucket (`ScoopInstaller/Main`)
- B. Intended package type: Manifest (`.json`) for a CLI tool
- C. Eligibility today: BLOCKED_BY_ADOPTION_CRITERIA
- D. Required-properties classification (Scoop schema): `version`, `homepage`, `license` are required properties; `description` is expected for new/updated manifests but the official docs state it is not technically required. Optional schema properties include `url`, `hash`, `bin`, `architecture`, `checkver`, `autoupdate`, and `installer`/`uninstaller`.
- E. DiffSeal candidate needs: for a portable downloadable DiffSeal CLI manifest, `url`/`hash`/`bin` would be expected/needed by OUR selected manifest shape even though they are not all generic Scoop-schema mandatory properties.
- F. Field-length / validator constraints: Scoop manifest schema
- G. Accepted license representation: `license` field (SPDX) / URL
- H. Source/artifact requirements: version-specific download URL + `hash`; CLI behavior via `bin`
- I. Checksum/signature requirements: `hash` (SHA-256 preferred) required
- J. Install/uninstall requirements: standard install; no elaborate pre/post scripts preferred; verifier command/comment flow
- K. Validation commands: `scoop install`, `scoop update`, manifest `checkver`
- L. Automated validation: Scoop CI checks on PR
- M. Human/manual review gate: Main bucket maintainer review
- N. Owner-only interaction: PR submission; maintainer review
- O. Namespace/name collision check: app name uniqueness
- P. Resubmission semantics: PR updated per feedback; no version churn
- Q. Current DiffSeal blocker: Main criteria require a reasonably well-known, widely used developer tool; the official criteria give an INDICATIVE example ("at least 500 stars and 150 forks" for a GitHub project) rather than a hard numerical threshold. Current DiffSeal evidence is 0 stars / 0 forks, which still fails the broader "reasonably well-known and widely used" criterion on current evidence; the example is not treated as an absolute contractual threshold. Latest stable version is also required (current upstream is Alpha).
- R. Next prerequisite: genuine adoption/maturity evidence (no fabricated signal; no personal bucket created to claim coverage)
- S. Status: **BLOCKED_BY_ADOPTION_CRITERIA**

A custom bucket is technically possible but low-discovery; it is not created
here and is not counted as market coverage.

---

## 9. Cost / Effort / Maintenance Model

Qualitative per-channel assessment. No dollar values are invented. Direct
platform fees are recorded only where an official source identifies them;
otherwise `NOT_IDENTIFIED_IN_OFFICIAL_SOURCE` or `NOT_PUBLISHED` is used.
Engineering/maintenance burden is qualitative (LOW / MEDIUM / HIGH /
UNRESOLVED) with rationale based on artifact complexity, platform-specific
files, version/update work, dependency maintenance, validation burden, human
moderation, Windows artifact maintenance, and future release synchronization.

### GitHub Marketplace

- DIRECT PLATFORM COST = NOT_IDENTIFIED_IN_OFFICIAL_SOURCE (no public listing fee identified in official sources reviewed)
- ENGINEERING COST / EFFORT = LOW — existing composite Action already published; no per-release engineering beyond Action metadata
- ONGOING MAINTENANCE BURDEN = MEDIUM — each release must keep `action.yml` valid, description within limits, and listing current
- OPTIONAL COSTS = NOT_PUBLISHED (code signing not applicable to Action metadata)
- UNKNOWN / NOT_PUBLISHED COSTS = NOT_PUBLISHED

### PyPI

- DIRECT PLATFORM COST = NOT_IDENTIFIED_IN_OFFICIAL_SOURCE (no fee identified in official PyPI/PyPA sources)
- ENGINEERING COST / EFFORT = LOW — Trusted Publishing workflow already exists (`publish-pypi.yml`)
- ONGOING MAINTENANCE BURDEN = LOW — release-triggered build + publish; metadata from `pyproject.toml`
- OPTIONAL COSTS = NOT_PUBLISHED
- UNKNOWN / NOT_PUBLISHED COSTS = NOT_PUBLISHED

### Chocolatey

- DIRECT PLATFORM COST = NOT_IDENTIFIED_IN_OFFICIAL_SOURCE (Community repository; no official fee identified)
- ENGINEERING COST / EFFORT = HIGH — Windows package/installer artifact work, checksum + `VERIFICATION.txt`, moderation iterations
- ONGOING MAINTENANCE BURDEN = HIGH — per-version package rebuild, moderator findings, silent install/uninstall regression, Windows artifact maintenance
- OPTIONAL COSTS = NOT_PUBLISHED
- UNKNOWN / NOT_PUBLISHED COSTS = NOT_PUBLISHED (legal/copyright identity unresolved — `ERR-DIFFSEAL-LEGAL-001`)

### WinGet

- DIRECT PLATFORM COST = NOT_IDENTIFIED_IN_OFFICIAL_SOURCE (Community repository; no official fee identified)
- ENGINEERING COST / EFFORT = MEDIUM/HIGH — manifest authoring + schema recheck, Windows portable artifact, `winget validate` + Sandbox testing
- ONGOING MAINTENANCE BURDEN = HIGH — schema drift revalidation before each submission, portable artifact maintenance, PR review iterations
- OPTIONAL COSTS = NOT_PUBLISHED
- UNKNOWN / NOT_PUBLISHED COSTS = NOT_PUBLISHED

### Homebrew / core

- DIRECT PLATFORM COST = NOT_IDENTIFIED_IN_OFFICIAL_SOURCE (no official fee identified)
- ENGINEERING COST / EFFORT = HIGH — formula + Python resources with pinned SHAs, `brew audit` + `test-bot`, CI matrix
- ONGOING MAINTENANCE BURDEN = HIGH — resource/SHA updates on dependency changes, release synchronization
- OPTIONAL COSTS = NOT_PUBLISHED
- UNKNOWN / NOT_PUBLISHED COSTS = NOT_PUBLISHED (upstream Alpha status blocks eligibility)

### Scoop Main

- DIRECT PLATFORM COST = NOT_IDENTIFIED_IN_OFFICIAL_SOURCE (no official fee identified)
- ENGINEERING COST / EFFORT = MEDIUM — manifest authoring, `hash`, `checkver`/`autoupdate`
- ONGOING MAINTENANCE BURDEN = MEDIUM — manifest updates per version, autoupdate maintenance
- OPTIONAL COSTS = NOT_PUBLISHED
- UNKNOWN / NOT_PUBLISHED COSTS = NOT_PUBLISHED (adoption criteria not met)

---

## 10. Post-Publication Feedback Lifecycle

Reusable lifecycle governing the distribution matrix:

```
product / architecture decision
    ->
build artifact
    ->
license / IP validation
    ->
package
    ->
platform validation
    ->
publication
    ->
discovery / acquisition
    ->
install / adoption evidence
    ->
user / moderator feedback
    ->
defects / requests / friction
    ->
distribution + product backlog
    ->
governed improvement
    ->
next iteration
```

Publication is NOT project completion. After publication, the following
observable evidence categories are tracked WITHOUT inventing analytics
infrastructure:

- package downloads where officially exposed (e.g., PyPI download counts)
- repository traffic/adoption indicators (GitHub traffic where available)
- installs where available
- stars/forks as WEAK adoption signals only
- Marketplace visibility
- issue reports
- package-manager moderation feedback
- user support requests
- failed installation reports
- upgrade/uninstall problems
- Pro interest / commercial conversion evidence where applicable (see
  `docs/COMMERCIAL_RELEASE_POLICY.md` funnel distinctions)

The COMMERCIAL_RELEASE_POLICY distinctions are preserved and NOT equated:
view ≠ acquisition; download ≠ successful install; install ≠ successful
activation; star ≠ paying customer.

Feedback (moderator findings, issue reports, failed-install reports, upgrade
friction) feeds the distribution + product backlog, and every change is a
governed improvement subject to the Human Gate Protocol (Section 13).

---

## 11. Shared Windows Portable Artifact Prerequisite

Analysis only. No artifact is implemented. No bundler is selected.

**Shared target shape (analyzed, not built):**

```
diffseal-<version>-windows-x64.zip
    containing:
        diffseal.exe
```

This one versioned artifact could serve both WinGet (archive + nested
portable) and Chocolatey (downloaded zip with checksum).

**Future artifact requirements (recorded, not satisfied yet):**

- exact version identity matching package version
- deterministic/reproducible-enough build evidence
- immutable GitHub Release asset
- SHA-256
- no hidden network behavior, no telemetry
- preserves the current DiffSeal CLI contract and exit codes
- can invoke repository-local verification tools (pytest, Ruff, coverage, dependency) as intended — requires that `resolve_tool` module/PATH resolution works in a bundled runtime
- clean install and uninstall on supported Windows environments
- must not include Pro code (Community artifact only)
- ships required Community license material
- dependency license review
- malware/AV false-positive consideration
- Windows architecture support decision (x64; x86/ARM64 undecided)
- code-signing decision explicitly **DEFERRED** unless later evidence requires it

**Candidate bundlers — recorded, UNDECIDED:**

Each candidate is unverified for this product (mark `UNRESOLVED` where repo
evidence is insufficient). Do not select one in this package. License labels
below are recorded from each project's primary official documentation.

| Candidate | Project license (official) | Windows support | Native standalone `.exe` | Target Python | One-file / one-dir | Runtime extraction | Subprocess/tool-discovery implication for DiffSeal | Size / maintenance | Reproducibility |
|---|---|---|---|---|---|---|---|---|---|
| PyInstaller | GPLv2-with-runtime-exception (GPL-compatible license with a bootloader exception); a commercial-use option exists for exception cases | Yes | Yes (one-file or one-dir) | Same as host CPython | One-file or one-dir | One-file extracts to a temp dir at runtime | `sys.executable` inside a bundled app differs; pytest/Ruff/coverage discovery via `resolve_tool` is `UNRESOLVED` for a bundled DiffSeal | One-file size large; one-dir smaller | Known reproducibility challenge |
| Nuitka | GNU AGPL-3.0 with a runtime exception granted in `LICENSE-RUNTIME.txt` (NOT Apache-2.0) | Yes | Yes (compiled) | Same as host CPython | Standalone mode: directory-based distribution; onefile mode: single file | Standalone mode: no generic runtime extraction; onefile mode: unpacks its payload at runtime, default extraction location is a unique temporary directory (configurable to a cached path) | Compiled app's `sys.executable`/module discovery differs; tool discovery `UNRESOLVED` | Builds larger; compile time significant | UNRESOLVED_FOR_DIFFSEAL (no measured DiffSeal-specific reproducibility evidence) |
| Briefcase | BSD-3-Clause | Yes | Packaged app (installer-oriented) | Python project | Installer/app bundle | n/a | Not evaluated for DiffSeal | Higher (app-bundle oriented) | Not evaluated |
| cx_Freeze | PSF-derived license ("This license is derived from the Python Software Foundation License"; copyright holders Marcelo Duarte, Anthony Tuininga, Computronix (Canada) Ltd.) — NOT MIT | Yes | Native executable: YES, as an executable in a frozen application/build directory; native single-file on Windows: NO (cx_Freeze itself does not provide a Linux AppImage-style single-file mode on Windows) | Same as host CPython | Windows distribution options: frozen build directory; `bdist_msi` where appropriate | N/A for a native cx_Freeze Windows one-file mode (that mode is not supported on Windows); an external SFX wrapper would be a separate architecture, UNRESOLVED | `sys.executable` in a frozen app differs; tool discovery `UNRESOLVED` | Moderate | Not proven for DiffSeal |
| shiv / zipapp | shiv: BSD-2-Clause | Yes but requires a compatible Python runtime | **NO** — a `python`-based zipapp, NOT a standalone native `diffseal.exe` | Requires an available compatible Python | Single zipapp | shiv dependencies are extracted/cached at runtime | Relies on an external Python; not equivalent to a standalone executable unless extra wrapping/architecture is introduced | Small | Reproducible artifact mode is available via `--reproducible` / `SOURCE_DATE_EPOCH`; reproducibility is not inherent to every default build |

**Important classification:** shiv/zipapp are Python archive tools, not native
Windows executable bundlers. They generally rely on a compatible Python
runtime and therefore are NOT equivalent to a standalone `diffseal.exe`
unless additional wrapping/architecture is introduced. They are recorded only
for completeness.

Subprocess behavior is a material open question for ANY bundler: DiffSeal
invokes `resolve_tool` which prefers `[sys.executable, "-m", <tool>]`, then a
PATH executable. A bundled single-file `diffseal.exe` must either (a) still
locate and invoke the repository's installed pytest/Ruff/coverage on PATH, or
(b) document that bundled mode changes tool discovery. This is an
architecture-level decision deferred outside this document.

`ERR-DIFFSEAL-WINDOWS-DIST-001` — Windows portable artifact architecture is
unresolved. This package is analysis only; the ERR is NOT closed.

---

## 12. Distribution Sequence Recommendation

Evidence-consistent recommendation (change if official evidence proves
otherwise):

1. Maintain existing GitHub / PyPI / Marketplace distribution.
2. Resolve/contain distribution legal metadata gaps where required
   (Marketplace EULA item; Chocolatey owner/copyright identity).
3. Close the Windows portable artifact architecture (Section 11 decision).
4. Build and test a Windows portable Community artifact.
5. Use that artifact for governed WinGet + Chocolatey packaging.
6. STOP at each platform human approval gate.
7. Homebrew/core only after a genuine stable upstream status (real product
   decision, not an edit).
8. Scoop Main only after adoption criteria become credible (real evidence,
   no fabricated signal).

---

## 13. Human Gate Protocol

Reusable protocol for platform submission gates:

- **Automated check failure:** executor may diagnose and fix within approved
  scope, revalidate, then STOP before public resubmission if authorization is
  required.
- **Human review / moderation / pending:** STOP immediately. No repeated push,
  no automated retry, no duplicate submission, no version churn to bypass
  review. Report the exact platform state and wait for the human response.
- **Human rejection with a specific finding:** record the exact finding;
  assess architecture/legal impact; fix only after governed review; resubmit
  only with explicit authorization.
- **Unknown platform state:** STOP / ERR. Do not guess.

---

## 14. Open ERRs / Blockers

| ERR | Description | Status |
|---|---|---|
| ERR-DIFFSEAL-LEGAL-001 | GitHub Marketplace EULA / legal-owner / distribution legal boundary (Developer Agreement section 2.4 separate-EULA language; Chocolatey owner/copyright identity) | OPEN — do not guess legal ownership or EULA interpretation |
| ERR-DIFFSEAL-WINDOWS-DIST-001 | Windows portable artifact architecture unresolved (bundler choice, subprocess/tool discovery, code signing, AV) | OPEN — analysis only; prerequisite for WinGet + Chocolatey |

---

## 15. Project Matrix — Cross-Cutting Coverage

References current governed repository evidence; no new decisions are
invented here.

**PRODUCT / ARCHITECTURE**
- `PRODUCT_CHARTER` = Architecture Closed
- local-first / Python-first
- Community independently useful
- Community Apache-2.0
- Pro proprietary

**DEPENDENCIES**
- current runtime dependencies come from `pyproject.toml`
- distribution-specific bundler/runtime dependencies remain UNRESOLVED until
  the Windows architecture closes (`ERR-DIFFSEAL-WINDOWS-DIST-001`)
- no hidden dependency assumption

**BUILD / PACKAGE**
- current Community distribution = sdist + wheel
- Windows portable artifact = not built; ERR remains open

**VERSIONING / MATURITY**
- version 0.1.1
- Alpha
- maturity is NOT changed to gain package-manager eligibility

**SECURITY**
- reference `docs/GITHUB_ACTION_SECURITY.md`
- least-privilege Action
- no repository secrets required
- no `pull_request_target`
- third-party Actions SHA-pinned
- subprocess environment sanitized

**TEST / CI**
- reference current CI (`.github/workflows/ci.yml`)
- Python 3.10 + 3.12
- pytest
- Ruff lint
- Ruff formatting
- mypy
- package build

**CI/CD / PUBLICATION GATES**
- normal main push = CI only
- `v*` tag = release validation only (`.github/workflows/release.yml`)
- PyPI publication = `release: published` + protected `pypi` environment
- public publication remains owner-gated

**PRICING**
- founding Pro experiment price = $19 one-time
- price remains fixed during the initial 14-day experiment
  (`docs/COMMERCIAL_RELEASE_POLICY.md`)

**LAUNCH / ACQUISITION**
Reference `COMMERCIAL_RELEASE_POLICY`:
- targeted developer outreach
- technical demonstration/article
- appropriate technical community
- Product Hunt only if launch assets justify it
- GitHub availability != launch

**TARGET BUYER**
Reference `PRODUCT_CHARTER`:
- solo Python developer
- freelancer/consultant
- very small engineering team/technical owner
- developers reviewing AI-assisted changes

**SUPPORT**
- Community public issue/feedback channel = GitHub Issues
- no support SLA is claimed
- Pro support model = NOT_PUBLISHED unless another closed repository decision
  defines it
- no invented support promise

**MEASUREMENT**
Reference the closed 14-day manual worksheet:
- date, source, qualified, installed, first_run, repeated_use, pro_interest,
  checkout, purchase, feedback
- funnel distinctions preserved: view != acquisition; download != successful
  install; install != activation; star != paying customer

**FEEDBACK**
Reference Section 10: feedback -> backlog -> governed improvement -> next
iteration.

---

## Validation notes

All external factual requirements above cite official primary sources:

- GitHub Marketplace / Developer Agreement: docs.github.com / github.com
  Marketplace Developer Agreement (section 2.4 EULA requirement referenced)
- PyPI / packaging: PyPA docs (PEP 621 / PEP 639 SPDX license expression and
  license-files; pypi.org JSON metadata)
- Chocolatey: docs.chocolatey.org community-repository package validator and
  moderation lifecycle (description 4000-character validator limit; human
  moderation)
- WinGet: microsoft/winget-pkgs official README and doc/README (supported
  installer types; script-based not supported; `winget validate`; Windows
  Sandbox / SandboxTest.ps1)
- Homebrew: docs.brew.sh/Formula-Cookbook (homepage, license, sha256, audit,
  CI)
- Scoop: ScoopInstaller/Main README and Scoop wiki
  "Criteria-for-including-apps-in-the-main-bucket" (500 stars / 150 forks
  example; latest stable version; standard install; non-GUI)

Current-product assertions are grounded in repository evidence (see Section
1). No unsupported license/legal interpretation is asserted; the Marketplace
EULA item is explicitly marked OPEN.
