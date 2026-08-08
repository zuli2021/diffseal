"""Release-hardening validation: immutable pinning of external Actions and
Marketplace/version invariants."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

YAML_PATHS = [
    *sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml")),
    REPO_ROOT / "action.yml",
    *sorted((REPO_ROOT / "examples").glob("**/*.yml")),
]

# The DiffSeal self-reference placeholder in the example workflow is resolved
# to the public owner + immutable tag at the governed release, so it is exempt.
SELF_REFERENCE_PLACEHOLDER = "<owner>/diffseal@<ref>"

USES_RE = re.compile(r"\buses:\s*([^\s#]+)")


def _uses_refs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    refs = []
    for match in USES_RE.finditer(text):
        ref = match.group(1)
        if ref == SELF_REFERENCE_PLACEHOLDER or ref.startswith("./"):
            continue
        refs.append(ref)
    return refs


def _all_external_refs() -> list[tuple[Path, str]]:
    collected: list[tuple[Path, str]] = []
    for path in YAML_PATHS:
        for ref in _uses_refs(path):
            collected.append((path, ref))
    return collected


def test_all_yaml_files_exist():
    for path in YAML_PATHS:
        assert path.is_file(), path


def test_every_external_action_is_pinned_to_full_sha():
    refs = _all_external_refs()
    assert refs, "expected at least one external Action reference to validate"
    for path, ref in refs:
        owner_repo, separator, pinned = ref.rpartition("@")
        assert separator == "@", f"{path}: malformed reference {ref!r}"
        assert len(pinned) == 40, f"{path}: {ref!r} is not pinned to a full SHA"
        assert re.fullmatch(r"[0-9a-f]{40}", pinned), f"{path}: {ref!r} SHA must be lowercase hex"
        assert owner_repo, f"{path}: {ref!r} missing owner/repo"


def test_pinned_shas_match_documented_policy():
    text = (REPO_ROOT / "docs" / "GITHUB_ACTION_SECURITY.md").read_text(encoding="utf-8")
    for path, ref in _all_external_refs():
        pinned = ref.rpartition("@")[2]
        assert len(pinned) == 40
        assert pinned in text, f"{path}: pinned SHA not documented in security policy"


def test_marketplace_root_action_metadata_is_unique():
    root_yamls = [
        REPO_ROOT / "action.yml",
        REPO_ROOT / "action.yaml",
    ]
    present = [p for p in root_yamls if p.is_file()]
    assert len(present) == 1, f"expected exactly one root action metadata file, got {present}"
    data = yaml.safe_load(present[0].read_text(encoding="utf-8"))
    assert data["name"] == "DiffSeal"
    assert data["description"]
    assert data["runs"]["using"] == "composite"
    assert isinstance(data.get("inputs"), dict)
    assert isinstance(data.get("outputs"), dict)


def test_release_identity_is_consistent():
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.1.0"' in pyproject
    preflight = (REPO_ROOT / "docs" / "COMMUNITY_RELEASE_PREFLIGHT.md").read_text(encoding="utf-8")
    assert "v0.1.0" in preflight
    assert "v0" in preflight
