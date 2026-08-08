"""Single, small, testable boundary for tool (subprocess) invocation.

Collectors MUST NOT embed ad hoc subprocess behavior. They delegate command
execution, environment handling, timeouts, and error classification here.

Invocation always uses argument arrays, never shell composition, to avoid
shell injection. The subprocess environment is a sanitized allow-list so the
entire parent environment is never captured or leaked.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT = 180.0

_ALLOWED_ENV_KEYS = (
    "PATH",
    "HOME",
    "VIRTUAL_ENV",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "PYTHONIOENCODING",
    "NO_COLOR",
    "TERM",
    "XDG_CACHE_HOME",
)


class ToolError(Exception):
    """Raised for an unusable tool invocation (missing binary, timeout, crash)."""


@dataclass(frozen=True)
class ProcessResult:
    """Outcome of a single tool invocation."""

    command: list[str]
    cwd: Path
    exit_code: int | None
    stdout: str
    stderr: str
    duration: float
    timed_out: bool
    executable_missing: bool
    error: str | None = None


def sanitized_env() -> dict[str, str]:
    """Build a minimal allow-listed environment for subprocesses."""
    env: dict[str, str] = {}
    for key in _ALLOWED_ENV_KEYS:
        value = os.environ.get(key)
        if value is not None:
            env[key] = value
    return env


def resolve_executable(name: str) -> str | None:
    """Resolve a tool executable on the sanitized PATH; None if missing."""
    path = os.environ.get("PATH", "")
    return shutil.which(name, path=path)


def resolve_tool(name: str) -> list[str] | None:
    """Resolve the best command prefix to run ``name``.

    Preference order:

    1. ``[sys.executable, "-m", name]`` when the module is importable in the
       interpreter running DiffSeal, so the tool runs in the same environment
       as DiffSeal itself;
    2. a ``name`` executable on ``PATH`` (covers standalone tools such as a
       globally installed Ruff binary);
    3. ``None`` when neither is available.
    """
    import importlib.util

    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        spec = None
    if spec is not None:
        return [sys.executable, "-m", name]
    executable = resolve_executable(name)
    if executable is not None:
        return [executable]
    return None


def run_process(
    command: list[str],
    cwd: Path,
    timeout: float = DEFAULT_TIMEOUT,
    env: dict[str, str] | None = None,
) -> ProcessResult:
    """Execute ``command`` as an argument array and normalize the outcome.

    ``executable_missing`` is set when the binary cannot be found;
    ``timed_out`` is set when the command exceeds ``timeout`` seconds.
    Neither case raises; collectors translate these into ``ERROR``.
    """
    if not command:
        raise ToolError("cannot invoke an empty command")
    resolved = command[0]
    executable = resolve_executable(resolved)
    if executable is None:
        return ProcessResult(
            command=command,
            cwd=cwd,
            exit_code=None,
            stdout="",
            stderr=f"executable not found: {resolved}",
            duration=0.0,
            timed_out=False,
            executable_missing=True,
            error="executable not found",
        )

    started = time.monotonic()
    try:
        proc = subprocess.run(
            [executable, *command[1:]],
            cwd=str(cwd),
            env=env if env is not None else sanitized_env(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - started
        stdout = (
            exc.stdout.decode("utf-8", errors="replace")
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        stderr = (
            exc.stderr.decode("utf-8", errors="replace")
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "")
        )
        return ProcessResult(
            command=command,
            cwd=cwd,
            exit_code=None,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            timed_out=True,
            executable_missing=False,
            error=f"timed out after {timeout:g}s",
        )
    except OSError as exc:
        duration = time.monotonic() - started
        return ProcessResult(
            command=command,
            cwd=cwd,
            exit_code=None,
            stdout="",
            stderr=str(exc),
            duration=duration,
            timed_out=False,
            executable_missing=False,
            error=str(exc),
        )

    duration = time.monotonic() - started
    return ProcessResult(
        command=command,
        cwd=cwd,
        exit_code=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        duration=duration,
        timed_out=False,
        executable_missing=False,
    )
