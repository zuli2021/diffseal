"""Tests for repository / change context discovery and status parsing."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from diffseal.repository import _parse_porcelain, discover_context


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )


def _init_repo(root: Path) -> None:
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "init")


def test_parse_porcelain_columns():
    status = "M  staged.txt\n M unstaged.txt\nMM both.txt\nA  added.txt\n?? untracked.txt\n"
    changed, staged = _parse_porcelain(status)
    assert changed == 5
    assert staged == 3


def test_parse_porcelain_no_entries():
    assert _parse_porcelain("") == (0, 0)


def test_parse_porcelain_untracked_only():
    changed, staged = _parse_porcelain("?? foo.py\n")
    assert changed == 1
    assert staged == 0


def test_parse_porcelain_unstaged_only():
    changed, staged = _parse_porcelain(" M foo.py\n")
    assert changed == 1
    assert staged == 0


def test_discover_context_counts_are_truthful(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _init_repo(repo)

    (repo / "unstaged.txt").write_text("2\n", encoding="utf-8")
    _git(repo, "add", "unstaged.txt")
    _git(repo, "commit", "-q", "-m", "seed")
    (repo / "unstaged.txt").write_text("3\n", encoding="utf-8")

    (repo / "both.txt").write_text("4\n", encoding="utf-8")
    _git(repo, "add", "both.txt")
    _git(repo, "commit", "-q", "-m", "seed2")
    (repo / "both.txt").write_text("5\n", encoding="utf-8")
    _git(repo, "add", "both.txt")
    (repo / "both.txt").write_text("6\n", encoding="utf-8")

    (repo / "staged.txt").write_text("1\n", encoding="utf-8")
    _git(repo, "add", "staged.txt")
    (repo / "added.txt").write_text("7\n", encoding="utf-8")
    _git(repo, "add", "added.txt")

    (repo / "untracked.txt").write_text("8\n", encoding="utf-8")

    context = discover_context(repo)
    assert context.is_git is True
    assert context.files_changed == 5
    assert context.staged_files == 3


def test_discover_context_not_a_repo(tmp_path):
    context = discover_context(tmp_path)
    assert context.is_git is False
    assert context.files_changed is None
    assert context.staged_files is None
    assert context.warnings
