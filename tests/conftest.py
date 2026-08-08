"""Shared test fixtures for DiffSeal Community Core."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

FIXTURE_ROOT = Path(__file__).parent / "fixtures"


def write_files(root: Path, files: dict[str, str]) -> Path:
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


def git_commit_all(root: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(root), check=True)
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )
    subprocess.run(["git", "add", "-A"], cwd=str(root), check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(root), check=True, env=env)


@pytest.fixture
def make_fixture_repo(tmp_path: Path) -> Callable[[dict[str, str], bool], Path]:
    """Build a fixture repository directory (optionally a git repo)."""

    def _make(files: dict[str, str], git: bool = True) -> Path:
        root = tmp_path / f"repo-{abs(hash(frozenset(files.items())))}"
        root.mkdir(parents=True)
        write_files(root, files)
        if git:
            git_commit_all(root)
        return root

    return _make


@pytest.fixture
def healthy_files() -> dict[str, str]:
    """A minimal repository whose tests pass, lint is clean, coverage is 100%."""
    return {
        "pyproject.toml": "[project]\nname = 'healthy'\nversion = '0.1.0'\n",
        "hello.py": "def greet(name):\n    return f'Hello, {name}!'\n",
        "test_hello.py": (
            "from hello import greet\n\n\n"
            "def test_greet():\n"
            "    assert greet('World') == 'Hello, World!'\n"
        ),
    }


@pytest.fixture
def fail_test_files() -> dict[str, str]:
    """A repository whose tests fail but lint is clean."""
    return {
        "hello.py": "def greet(name):\n    return f'Hello, {name}!'\n",
        "test_hello.py": (
            "from hello import greet\n\n\ndef test_greet():\n    assert greet('World') == 'Wrong'\n"
        ),
    }


@pytest.fixture
def fail_lint_files() -> dict[str, str]:
    """A repository with a Ruff violation but passing tests."""
    return {
        "hello.py": ("import os\n\n\ndef greet(name):\n    return f'Hello, {name}!'\n"),
        "test_hello.py": (
            "from hello import greet\n\n\n"
            "def test_greet():\n"
            "    assert greet('World') == 'Hello, World!'\n"
        ),
    }


@pytest.fixture
def real_stdout() -> None:
    """Marker fixture: tests using it intentionally exercise real tools."""
