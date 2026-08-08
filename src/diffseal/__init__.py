"""DiffSeal is a local-first, Python-first PR evidence gate.

It turns verification signals for one exact repository change into one
normalized evidence bundle and one explicit review-readiness decision.
"""

from diffseal.models import CheckOutcome, CheckResult, EvidenceBundle, GateDecision

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "CheckOutcome",
    "CheckResult",
    "EvidenceBundle",
    "GateDecision",
]
