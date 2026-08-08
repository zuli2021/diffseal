"""Canonical JSON reporter.

``evidence.json`` is the canonical evidence artifact: stable field names, valid
JSON, enum values serialized exactly, deterministic structural ordering, and
no secrets or environment dumps.
"""

from __future__ import annotations

import json
from pathlib import Path

from diffseal.models import EvidenceBundle


def bundle_to_json(bundle: EvidenceBundle) -> str:
    """Serialize an EvidenceBundle to canonical JSON text."""
    return json.dumps(bundle.to_dict(), indent=2, ensure_ascii=True) + "\n"


def write_json(bundle: EvidenceBundle, path: Path) -> Path:
    """Write canonical ``evidence.json`` and return the written path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(bundle_to_json(bundle), encoding="utf-8")
    return path
