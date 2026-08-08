"""Tests for configuration loading, validation, hashing, and init behavior."""

from __future__ import annotations

import pytest

from diffseal.config import (
    KNOWN_CHECKS,
    ConfigError,
    default_config,
    load_config,
    load_config_file,
    write_default_config,
)
from diffseal.models import stable_hash

VALID_TOML = """\
[checks.pytest]
enabled = true
required = true
args = ["-q"]

[checks.ruff]
required = false

[checks.coverage]
threshold = 70.0

[evaluation]
review_on = ["coverage"]

[repository]
base_revision = "main"
"""


def test_default_config_values():
    config = default_config()
    assert config.checks["pytest"].required is True
    assert config.checks["ruff"].required is True
    assert config.checks["coverage"].required is False
    assert config.checks["coverage"].threshold == 80.0
    assert config.checks["dependency"].threshold is None
    assert config.evaluation.review_on == []
    assert set(config.checks) == set(KNOWN_CHECKS)


def test_load_config_with_no_file_uses_defaults(tmp_path):
    config = load_config(tmp_path)
    assert config.path is None
    assert config.checks["pytest"].enabled is True


def test_load_valid_config_file(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text(VALID_TOML, encoding="utf-8")
    config = load_config_file(path)
    assert config.checks["ruff"].required is False
    assert config.checks["coverage"].threshold == 70.0
    assert config.evaluation.review_on == ["coverage"]
    assert config.repository.base_revision == "main"


def test_explicit_config_wins_over_discovered(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text(VALID_TOML, encoding="utf-8")
    config = load_config(tmp_path, explicit=path)
    assert config.path == path


def test_config_file_not_found_errors(tmp_path):
    with pytest.raises(ConfigError):
        load_config(tmp_path, explicit=tmp_path / "missing.toml")


def test_unknown_top_level_key_rejected(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text("bogus = 1\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown top-level key"):
        load_config_file(path)


def test_unknown_check_rejected(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text("[checks.nope]\nenabled = true\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown check"):
        load_config_file(path)


def test_unknown_check_key_rejected(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text("[checks.pytest]\nwibble = true\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown key"):
        load_config_file(path)


def test_invalid_toml_rejected(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text("checks = [", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid TOML"):
        load_config_file(path)


def test_wrong_types_rejected(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text('[checks.pytest]\nenabled = "yes"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="must be a boolean"):
        load_config_file(path)


def test_review_on_unknown_check_rejected(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text('[evaluation]\nreview_on = ["nope"]\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown check"):
        load_config_file(path)


def test_configuration_hash_is_stable_across_equivalent_configs():
    a = default_config()
    b = default_config()
    assert a.configuration_hash == b.configuration_hash
    assert a.configuration_hash != a.configuration_hash[:0]


def test_configuration_hash_changes_with_settings(tmp_path):
    base = default_config()
    path = tmp_path / "conf.toml"
    path.write_text("[checks.coverage]\nthreshold = 90.0\n", encoding="utf-8")
    changed = load_config_file(path)
    assert changed.configuration_hash != base.configuration_hash


def test_policy_hash_from_review_on():
    assert default_config().policy_hash == stable_hash({"review_on": []})


def test_write_default_config_and_refuse_overwrite(tmp_path):
    target = tmp_path / ".diffseal.toml"
    write_default_config(target)
    assert target.exists()
    assert "review_on" in target.read_text(encoding="utf-8")
    with pytest.raises(ConfigError, match="refusing to overwrite"):
        write_default_config(target)


def test_enabled_checks_are_ordered(tmp_path):
    config = default_config()
    assert [c.id for c in config.enabled_checks()] == [
        "pytest",
        "ruff",
        "coverage",
        "dependency",
    ]
