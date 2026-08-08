"""Minimal repository / change context discovery.

Enough Git integration to identify the repository root, HEAD, an optional
configured base revision, and a basic working-tree change summary. No Git
abstraction framework, no GitHub, no remote API calls.

If no valid base revision is available, that is reported truthfully in the
evidence instead of being invented.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryContext:
    """Facts about the exact repository state under evaluation."""

    root: Path | None
    is_git: bool
    branch: str | None
    head_revision: str | None
    base_revision: str | None
    files_changed: int | None
    staged_files: int | None
    warnings: list[str] = field(default_factory=list)

    @property
    def change_summary(self) -> dict[str, object]:
        data: dict[str, object] = {"is_git": self.is_git}
        if self.branch is not None:
            data["branch"] = self.branch
        if self.files_changed is not None:
            data["files_changed"] = self.files_changed
        if self.staged_files is not None:
            data["staged_files"] = self.staged_files
        return data


def _run_git(args: list[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def discover_context(cwd: Path, base_revision: str | None = None) -> RepositoryContext:
    """Discover repository context for ``cwd``.

    ``base_revision`` is taken from configuration when present; it is used as
    reported without being invented by this package.
    """
    warnings: list[str] = []
    root = _run_git(["rev-parse", "--show-toplevel"], cwd)
    if root is None:
        return RepositoryContext(
            root=None,
            is_git=False,
            branch=None,
            head_revision=None,
            base_revision=None,
            files_changed=None,
            staged_files=None,
            warnings=["cwd is not inside a git working tree"],
        )

    root_path = Path(root)
    head = _run_git(["rev-parse", "HEAD"], root_path)
    branch = _run_git(["branch", "--show-current"], root_path)

    effective_base: str | None = None
    if base_revision is not None:
        resolved = _run_git(["rev-parse", "--verify", base_revision], root_path)
        if resolved is None:
            warnings.append(f"configured base revision {base_revision!r} could not be resolved")
        else:
            effective_base = resolved
    elif head is not None:
        parent = _run_git(["rev-parse", f"{head}~1"], root_path)
        if parent is None:
            warnings.append("no base revision available (no configured base and no parent commit)")

    status_short = _run_git(["status", "--short"], root_path)
    files_changed: int | None = None
    staged_files: int | None = None
    if status_short is not None:
        files_changed, staged_files = _parse_porcelain(status_short)

    return RepositoryContext(
        root=root_path,
        is_git=True,
        branch=branch,
        head_revision=head,
        base_revision=effective_base,
        files_changed=files_changed,
        staged_files=staged_files,
        warnings=warnings,
    )


def _parse_porcelain(text: str) -> tuple[int, int]:
    """Parse ``git status --short`` (porcelain v1) output.

    Each line is ``XY path`` where column X is the index/staged status and
    column Y is the worktree/unstaged status. Columns are interpreted
    independently:

    - ``files_changed`` counts every reported entry (staged, unstaged,
      untracked);
    - ``staged_files`` counts only entries whose index column is a real status
      (not blank and not ``?`` for untracked).

    Examples:

    - ``M  staged.txt``      -> changed, staged
    - `` M unstaged.txt``    -> changed, not staged
    - ``MM both.txt``        -> changed, staged
    - ``A  added.txt``       -> changed, staged
    - ``?? untracked.txt``   -> changed, not staged
    """
    lines = [line for line in text.splitlines() if line.strip()]
    staged = 0
    for line in lines:
        if len(line) < 2:
            continue
        index_col = line[0]
        if index_col != " " and index_col != "?":
            staged += 1
    return len(lines), staged
