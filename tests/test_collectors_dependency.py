"""Tests for the basic dependency collector."""

from __future__ import annotations

from diffseal.collectors.dependency import DependencyCollector
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome


def _check() -> CheckConfig:
    return CheckConfig(
        id="dependency",
        collector_id="dependency",
        enabled=True,
        required=False,
        args=[],
        threshold=None,
    )


def _pyproject(dependencies: list[str]) -> str:
    lines = ["[project]", "name = 'demo'", "version = '0.1.0'"]
    if dependencies:
        rendered = "\n".join(f"    '{dep}'," for dep in dependencies)
        lines.append(f"dependencies = [\n{rendered}\n]")
    return "\n".join(lines) + "\n"


def test_no_declared_dependencies_skipped(tmp_path):
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.SKIPPED


def test_dependencies_satisfied_pass(tmp_path):
    (tmp_path / "pyproject.toml").write_text(_pyproject(["pytest>=7"]), encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.PASS


def test_missing_dependency_fail(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        _pyproject(["this-package-does-not-exist-xyz>=1"]), encoding="utf-8"
    )
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "DEPENDENCY_MISSING" for f in result.findings)


def test_unsatisfied_version_fail(tmp_path):
    (tmp_path / "pyproject.toml").write_text(_pyproject(["pytest<1"]), encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "DEPENDENCY_UNSATISFIED" for f in result.findings)


def test_unparseable_requirement_fail(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        _pyproject(["!!!not-a-valid-requirement!!!"]), encoding="utf-8"
    )
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "DEPENDENCY_UNPARSEABLE" for f in result.findings)


def test_invalid_pyproject_error(tmp_path):
    (tmp_path / "pyproject.toml").write_text("not valid toml [", encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.ERROR
    assert result.findings[0].code == "DEPENDENCY_UNREADABLE"


def test_requirements_txt_satisfied(tmp_path):
    (tmp_path / "requirements.txt").write_text("pytest>=7\n", encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.PASS


def test_environment_marker_excluded(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        _pyproject(['this-package-does-not-exist-xyz>=1; python_version < "1.0"']),
        encoding="utf-8",
    )
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.PASS


def test_both_sources_are_combined(tmp_path):
    (tmp_path / "pyproject.toml").write_text(_pyproject(["pytest>=7"]), encoding="utf-8")
    (tmp_path / "requirements.txt").write_text(
        "this-package-does-not-exist-xyz>=1\n", encoding="utf-8"
    )
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "DEPENDENCY_MISSING" for f in result.findings)


def test_empty_pyproject_does_not_mask_requirements_txt(tmp_path):
    (tmp_path / "pyproject.toml").write_text(_pyproject([]), encoding="utf-8")
    (tmp_path / "requirements.txt").write_text(
        "this-package-does-not-exist-xyz>=1\n", encoding="utf-8"
    )
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "DEPENDENCY_MISSING" for f in result.findings)


def test_duplicate_across_both_sources_is_deduplicated(tmp_path):
    (tmp_path / "pyproject.toml").write_text(_pyproject(["pytest>=7"]), encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest>=7\n", encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.PASS
    assert "1 applicable" in result.summary


def test_duplicate_within_requirements_txt_is_deduplicated(tmp_path):
    (tmp_path / "requirements.txt").write_text("pytest>=7\npytest>=7\n", encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.PASS
    assert "1 applicable" in result.summary


def test_conflicting_specifiers_are_both_evaluated(tmp_path):
    (tmp_path / "pyproject.toml").write_text(_pyproject(["pytest>=7"]), encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest<1\n", encoding="utf-8")
    result = DependencyCollector().collect(_check(), cwd=tmp_path, timeout=30.0)
    assert result.outcome == CheckOutcome.FAIL
    assert any(f.code == "DEPENDENCY_UNSATISFIED" for f in result.findings)
