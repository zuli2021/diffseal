"""Validation of GitHub workflow files for CI, release, and publishing."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
EXAMPLE_WORKFLOW = REPO_ROOT / "examples" / "workflow" / "diffseal.yml"

WORKFLOWS = {
    "ci.yml": WORKFLOW_DIR / "ci.yml",
    "publish-pypi.yml": WORKFLOW_DIR / "publish-pypi.yml",
    "release.yml": WORKFLOW_DIR / "release.yml",
}


class _GithubLoader(yaml.SafeLoader):
    """SafeLoader with YAML 1.2-style booleans so `on:` stays a string key."""


_GithubLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:bool"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _load(path: Path) -> dict:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_GithubLoader)


def test_workflow_files_exist_and_are_valid_yaml():
    for name, path in WORKFLOWS.items():
        assert path.is_file(), name
        assert isinstance(_load(path), dict), name
    assert EXAMPLE_WORKFLOW.is_file()
    assert isinstance(_load(EXAMPLE_WORKFLOW), dict)


def test_no_pull_request_target_anywhere():
    for path in list(WORKFLOWS.values()) + [EXAMPLE_WORKFLOW]:
        text = path.read_text(encoding="utf-8")
        assert "pull_request_target" not in text, path


def test_ci_has_no_publication_path():
    text = (WORKFLOW_DIR / "ci.yml").read_text(encoding="utf-8")
    assert "pypa/gh-action-pypi-publish" not in text
    assert "publish" not in text.lower()


def test_ci_permissions_and_no_secrets():
    data = _load(WORKFLOW_DIR / "ci.yml")
    assert data["permissions"] == {"contents": "read"}
    assert "publish" not in yaml.dump(data).lower()


def test_ci_matrix_covers_310_and_312():
    data = _load(WORKFLOW_DIR / "ci.yml")
    versions = data["jobs"]["test"]["strategy"]["matrix"]["python-version"]
    assert "3.10" in versions
    assert "3.12" in versions


def test_pypi_workflow_uses_release_only_trigger():
    data = _load(WORKFLOW_DIR / "publish-pypi.yml")
    triggers = data["on"]
    assert "push" not in triggers, "must not publish on ordinary pushes"
    assert "release" in triggers
    assert triggers["release"]["types"] == ["published"]


def test_pypi_workflow_uses_oidc_not_api_token():
    data = _load(WORKFLOW_DIR / "publish-pypi.yml")
    assert data["permissions"]["id-token"] == "write"
    assert data["permissions"]["contents"] == "read"
    text = (WORKFLOW_DIR / "publish-pypi.yml").read_text(encoding="utf-8")
    assert "PYPI_API_TOKEN" not in text
    assert "secrets." not in text
    assert "pypa/gh-action-pypi-publish" in text
    assert "environment: pypi" in text


def test_release_workflow_is_validation_only():
    data = _load(WORKFLOW_DIR / "release.yml")
    assert data["on"] == {"push": {"tags": ["v*"]}}
    assert data["permissions"] == {"contents": "read"}
    assert set(data["jobs"]) == {"verify"}
    dump = yaml.dump(data).lower()
    assert "pypa/gh-action-pypi-publish" not in dump
    assert "publish" not in dump


def test_example_workflow_minimal_permissions_and_safe():
    data = _load(EXAMPLE_WORKFLOW)
    assert data["permissions"] == {"contents": "read"}
    text = EXAMPLE_WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request_target" not in text
    assert "write" not in yaml.dump(data).lower()
    assert "secrets:" not in text
    assert "${{ secrets" not in text
    steps = data["jobs"]["diffseal"]["steps"]
    uploads = [s for s in steps if "upload-artifact" in str(s.get("uses", ""))]
    assert len(uploads) == 1
    upload = uploads[0]
    assert "github_token" not in str(upload.get("with", {}))
    assert upload["with"]["path"] == "evidence/"
