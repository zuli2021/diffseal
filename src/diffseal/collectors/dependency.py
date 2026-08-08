"""Basic dependency collector.

Deterministic, local, network-free: reads declared runtime dependencies from
``pyproject.toml`` (``[project].dependencies``) and ``requirements.txt`` when
present, combines both sources deterministically, and verifies each applicable
requirement is installed in the local environment and satisfies its declared
version specifier.

This check verifies LOCAL DECLARED REQUIREMENT SATISFACTION only. It is
deliberately NOT a vulnerability/audit scanner; a vulnerability database,
custom advisory logic, and network-heavy architecture are out of scope for
Community Core.

Semantics:

- all declared deps satisfied          -> PASS
- a declared dep missing/unsatisfied   -> FAIL
- declared requirements unreadable     -> ERROR
- no declared dependencies             -> SKIPPED
"""

from __future__ import annotations

from pathlib import Path

from diffseal.collectors.base import Collector, check_result, distribution_version
from diffseal.config import CheckConfig
from diffseal.models import CheckOutcome, CheckResult, Finding

try:  # Python 3.11+
    import tomllib  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised on Python < 3.11
    import tomli as tomllib  # type: ignore[import-not-found, no-redef]

try:
    from packaging.requirements import Requirement
except ImportError:  # pragma: no cover - packaging unavailable in the running env
    Requirement = None  # type: ignore[assignment, misc]


class DependencyCollector(Collector):
    collector_id = "dependency"
    distribution_name = ""

    def collect(self, check: CheckConfig, cwd: Path, timeout: float) -> CheckResult:
        requirement_cls = Requirement
        if requirement_cls is None:
            return check_result(
                check,
                CheckOutcome.ERROR,
                0.0,
                "dependency evidence could not be established",
                [Finding("DEPENDENCY_UNAVAILABLE", "packaging library is not available")],
            )

        try:
            declared = self._declared_requirements(cwd)
        except ValueError as exc:
            return check_result(
                check,
                CheckOutcome.ERROR,
                0.0,
                "dependency evidence could not be established",
                [Finding("DEPENDENCY_UNREADABLE", str(exc))],
            )

        if not declared:
            return check_result(
                check,
                CheckOutcome.SKIPPED,
                0.0,
                "no declared dependencies found; check skipped",
            )

        failures: list[Finding] = []
        applicable = 0
        for raw in declared:
            try:
                requirement = requirement_cls(raw)
            except Exception as exc:  # packaging raises various specifier errors
                failures.append(
                    Finding("DEPENDENCY_UNPARSEABLE", f"cannot parse requirement {raw!r}: {exc}")
                )
                continue
            if requirement.marker is not None and not requirement.marker.evaluate():
                continue
            applicable += 1
            name = requirement.name
            installed = distribution_version(name)
            if installed is None:
                installed = distribution_version(name.replace("-", "_"))
            if installed is None:
                failures.append(
                    Finding("DEPENDENCY_MISSING", f"required package {name!r} is not installed")
                )
            elif not requirement.specifier.contains(installed, prereleases=True):
                failures.append(
                    Finding(
                        "DEPENDENCY_UNSATISFIED",
                        f"installed {name} {installed} does not satisfy {requirement.specifier}",
                    )
                )

        if failures:
            return check_result(
                check,
                CheckOutcome.FAIL,
                0.0,
                f"{len(failures)} declared dependency problem(s) in local environment",
                failures,
            )
        return check_result(
            check,
            CheckOutcome.PASS,
            0.0,
            f"{applicable} applicable declared dependency(ies) satisfied",
        )

    @staticmethod
    def _declared_requirements(cwd: Path) -> list[str]:
        """Return merged, deduplicated declared requirement strings.

        Supported sources, both inspected whenever present:

        - ``pyproject.toml`` ``[project].dependencies``
        - ``requirements.txt``

        Declarations are combined in that order and deduplicated by canonical
        package name (first declaration wins), so the same package declared in
        both sources is not double-reported. Returns ``[]`` when no source
        declares anything.
        """
        pyproject = cwd / "pyproject.toml"
        requirements_txt = cwd / "requirements.txt"
        requirements: list[str] = []

        if pyproject.is_file():
            try:
                with open(pyproject, "rb") as handle:
                    data = tomllib.load(handle)
            except tomllib.TOMLDecodeError as exc:  # type: ignore[attr-defined]
                raise ValueError(f"invalid TOML in pyproject.toml: {exc}") from exc
            project = data.get("project") if isinstance(data, dict) else None
            if isinstance(project, dict):
                deps = project.get("dependencies")
                if isinstance(deps, list):
                    requirements.extend(str(item) for item in deps)

        if requirements_txt.is_file():
            for raw_line in requirements_txt.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith(("-r", "-c", "-e", "-f", "--", "git+")):
                    continue
                requirements.append(line)

        return DependencyCollector._dedupe(requirements)

    @staticmethod
    def _dedupe(requirements: list[str]) -> list[str]:
        """Deduplicate identical declarations, preserving first order.

        A declaration identity is its canonical requirement (normalized name,
        extras, specifier, and marker). Identical declarations repeated across
        supported sources collapse to one; the same package declared with a
        different version specifier is kept so each declaration is evaluated.
        """
        seen: set[object] = set()
        result: list[str] = []
        for raw in requirements:
            key: object = raw
            if Requirement is not None:
                try:
                    req = Requirement(raw)
                    key = (
                        req.name.lower(),
                        tuple(sorted(req.extras)),
                        str(req.specifier),
                        str(req.marker),
                    )
                except Exception:
                    key = raw
            if key in seen:
                continue
            seen.add(key)
            result.append(raw)
        return result
