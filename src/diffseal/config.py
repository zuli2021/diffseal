"""Project-local configuration for DiffSeal Community Core.

Configuration lives in ``.diffseal.toml`` and is intentionally small. Only
settings genuinely required by Community v0.1 are supported. Unknown keys
produce a useful error instead of being silently ignored.

Normalized effective configuration is used for deterministic hashing; secrets
can never enter the hash because only validated, whitelisted fields are kept.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from diffseal.models import stable_hash

try:  # Python 3.11+
    import tomllib  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised on Python < 3.11
    import tomli as tomllib  # type: ignore[import-not-found, no-redef]


CONFIG_FILENAME = ".diffseal.toml"

KNOWN_CHECKS = ("pytest", "ruff", "coverage", "dependency")

_CHECK_ALLOWED_KEYS = {"enabled", "required", "args", "threshold", "description"}
_TOP_LEVEL_ALLOWED_KEYS = {"checks", "evaluation", "repository"}
_EVALUATION_ALLOWED_KEYS = {"review_on"}


class ConfigError(Exception):
    """Raised when a configuration file is malformed or unsupported."""


@dataclass(frozen=True)
class CheckConfig:
    """Effective settings for one check."""

    id: str
    collector_id: str
    enabled: bool
    required: bool
    args: list[str]
    threshold: float | None
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "collector_id": self.collector_id,
            "enabled": self.enabled,
            "required": self.required,
            "args": list(self.args),
        }
        if self.threshold is not None:
            data["threshold"] = self.threshold
        if self.description:
            data["description"] = self.description
        return data


@dataclass(frozen=True)
class EvaluationConfig:
    """Evaluation policy settings.

    ``review_on`` lists check ids (normally optional checks) whose failure
    should force a ``REVIEW_REQUIRED`` decision instead of being ignored.
    Required failures always produce ``FAIL`` regardless of this list.
    """

    review_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"review_on": sorted(self.review_on)}


@dataclass(frozen=True)
class RepositoryConfig:
    """Repository / change context settings."""

    base_revision: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.base_revision is not None:
            data["base_revision"] = self.base_revision
        return data


@dataclass(frozen=True)
class Config:
    """Normalized, merged, effective configuration."""

    checks: dict[str, CheckConfig]
    evaluation: EvaluationConfig
    repository: RepositoryConfig
    path: Path | None = None

    @property
    def configuration_hash(self) -> str:
        """Stable hash of the normalized effective configuration.

        Independent of dictionary insertion order and secret-free by
        construction (only validated whitelisted fields are hashed).
        """
        checks = {cid: cfg.to_dict() for cid, cfg in sorted(self.checks.items())}
        normalized: dict[str, Any] = {
            "checks": checks,
            "evaluation": self.evaluation.to_dict(),
            "repository": self.repository.to_dict(),
        }
        return stable_hash(normalized)

    @property
    def policy_hash(self) -> str:
        """Stable hash of the normalized effective evaluation policy."""
        return stable_hash(self.evaluation.to_dict())

    def enabled_checks(self) -> list[CheckConfig]:
        """Enabled checks in deterministic (config) order."""
        return [c for c in self.checks.values() if c.enabled]


def _default_check(id: str) -> CheckConfig:
    defaults = {
        "pytest": ("pytest", True, True, ["-q"], None, "Python test suite via pytest"),
        "ruff": ("ruff", True, True, ["check", "."], None, "Python lint via Ruff"),
        "coverage": (
            "coverage",
            True,
            False,
            ["-q"],
            80.0,
            "Basic coverage threshold via coverage.py",
        ),
        "dependency": (
            "dependency",
            True,
            False,
            [],
            None,
            "Declared dependency availability in the local environment",
        ),
    }
    collector_id, enabled, required, args, threshold, description = defaults[id]
    return CheckConfig(
        id=id,
        collector_id=collector_id,
        enabled=enabled,
        required=required,
        args=list(args),
        threshold=threshold,
        description=description,
    )


def default_config(path: Path | None = None) -> Config:
    """Return the effective configuration when no file exists."""
    return Config(
        checks={cid: _default_check(cid) for cid in KNOWN_CHECKS},
        evaluation=EvaluationConfig(),
        repository=RepositoryConfig(),
        path=path,
    )


def _bool_value(key: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"check.{key} must be a boolean, got {value!r}")
    return value


def _string_list(key: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError(f"check.{key} must be a list of strings, got {value!r}")
    return list(value)


def _optional_float(key: str, value: Any) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigError(f"check.{key} must be a number, got {value!r}")
    return float(value)


def _parse_check(check_id: str, table: Any) -> CheckConfig:
    if not isinstance(table, dict):
        raise ConfigError(f"[checks.{check_id}] must be a table")
    for key in table:
        if key not in _CHECK_ALLOWED_KEYS:
            raise ConfigError(
                f"unknown key {key!r} in [checks.{check_id}]; "
                f"allowed keys: {', '.join(sorted(_CHECK_ALLOWED_KEYS))}"
            )

    base = _default_check(check_id)
    enabled = _bool_value("enabled", table["enabled"]) if "enabled" in table else base.enabled
    required = _bool_value("required", table["required"]) if "required" in table else base.required
    args = _string_list("args", table["args"]) if "args" in table else base.args
    threshold = (
        _optional_float("threshold", table["threshold"]) if "threshold" in table else base.threshold
    )
    description = table.get("description", base.description)
    if not isinstance(description, str):
        raise ConfigError(f"check.{check_id}.description must be a string")
    return CheckConfig(
        id=check_id,
        collector_id=base.collector_id,
        enabled=enabled,
        required=required,
        args=list(args),
        threshold=threshold,
        description=description,
    )


def _parse_evaluation(table: Any) -> EvaluationConfig:
    if not isinstance(table, dict):
        raise ConfigError("[evaluation] must be a table")
    for key in table:
        if key not in _EVALUATION_ALLOWED_KEYS:
            raise ConfigError(
                f"unknown key {key!r} in [evaluation]; "
                f"allowed keys: {', '.join(sorted(_EVALUATION_ALLOWED_KEYS))}"
            )
    review_on: list[str] = []
    if "review_on" in table:
        review_on = _string_list("review_on", table["review_on"])
        for check_id in review_on:
            if check_id not in KNOWN_CHECKS:
                raise ConfigError(f"evaluation.review_on contains unknown check {check_id!r}")
    return EvaluationConfig(review_on=review_on)


def _parse_repository(table: Any) -> RepositoryConfig:
    if not isinstance(table, dict):
        raise ConfigError("[repository] must be a table")
    for key in table:
        if key != "base_revision":
            raise ConfigError(f"unknown key {key!r} in [repository]; allowed keys: base_revision")
    base_revision = table.get("base_revision")
    if base_revision is not None and not isinstance(base_revision, str):
        raise ConfigError("repository.base_revision must be a string")
    return RepositoryConfig(base_revision=base_revision)


def load_config_file(path: Path) -> Config:
    """Load and normalize ``.diffseal.toml`` from ``path``."""
    if not path.is_file():
        raise ConfigError(f"configuration file not found: {path}")
    try:
        with open(path, "rb") as handle:
            raw = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:  # type: ignore[attr-defined]
        raise ConfigError(f"invalid TOML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"configuration root must be a TOML table in {path}")
    for key in raw:
        if key not in _TOP_LEVEL_ALLOWED_KEYS:
            raise ConfigError(
                f"unknown top-level key {key!r} in {path}; "
                f"allowed tables: {', '.join(sorted(_TOP_LEVEL_ALLOWED_KEYS))}"
            )

    checks: dict[str, CheckConfig] = {cid: _default_check(cid) for cid in KNOWN_CHECKS}
    checks_table = raw.get("checks", {})
    if not isinstance(checks_table, dict):
        raise ConfigError("[checks] must be a table")
    for check_id, table in checks_table.items():
        if check_id not in KNOWN_CHECKS:
            raise ConfigError(
                f"unknown check {check_id!r} in [checks]; known checks: {', '.join(KNOWN_CHECKS)}"
            )
        checks[check_id] = _parse_check(check_id, table)

    evaluation = _parse_evaluation(raw.get("evaluation", {}))
    repository = _parse_repository(raw.get("repository", {}))
    return Config(
        checks=checks,
        evaluation=evaluation,
        repository=repository,
        path=path,
    )


def find_config(start: Path) -> Path | None:
    """Locate ``.diffseal.toml`` at ``start`` or any parent directory."""
    current = start.resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def load_config(start: Path, explicit: Path | None = None) -> Config:
    """Load effective configuration.

    Precedence: explicit ``--config`` path, then ``.diffseal.toml`` found from
    ``start`` upward, then built-in defaults.
    """
    if explicit is not None:
        return load_config_file(explicit)
    found = find_config(start)
    if found is None:
        return default_config()
    return load_config_file(found)


DEFAULT_TOML = """\
# DiffSeal Community Core configuration.
# This file is optional; absent it, built-in defaults apply.

[checks.pytest]
enabled = true
required = true
args = ["-q"]

[checks.ruff]
enabled = true
required = true
args = ["check", "."]

[checks.coverage]
enabled = true
required = false
threshold = 80.0
args = ["-q"]

[checks.dependency]
enabled = true
required = false

[evaluation]
# Optional checks listed here force REVIEW_REQUIRED when they fail.
review_on = []

[repository]
# Optional explicit base revision for change context, e.g. "main".
# base_revision = "main"
"""


def config_file_exists(start: Path) -> bool:
    return (start / CONFIG_FILENAME).is_file() or find_config(start) is not None


def write_default_config(target: Path, force: bool = False) -> Path:
    """Write a minimal default config, refusing to overwrite an existing file."""
    if target.exists() and not force:
        raise ConfigError(f"refusing to overwrite existing file: {target}")
    target.write_text(DEFAULT_TOML, encoding="utf-8")
    return target
