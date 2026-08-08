"""Collector boundary: normalize raw tool execution into ``CheckResult``."""

from diffseal.collectors.base import Collector
from diffseal.collectors.coverage import CoverageCollector
from diffseal.collectors.dependency import DependencyCollector
from diffseal.collectors.pytest import PytestCollector
from diffseal.collectors.ruff import RuffCollector

__all__ = [
    "Collector",
    "PytestCollector",
    "RuffCollector",
    "CoverageCollector",
    "DependencyCollector",
]
