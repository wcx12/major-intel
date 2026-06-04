"""Compatibility helpers for legacy script entrypoints.

The project is moving stable implementation code into ``src/major_intel``.
Many manual test commands still execute files under ``scripts/`` directly, and
direct execution puts ``scripts/`` rather than the repository root on
``sys.path``.  This helper keeps those old commands working while the real
modules live in the importable package.
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_on_path() -> None:
    """Make ``src/`` importable for legacy wrappers.

    The function is intentionally idempotent because several wrappers can be
    imported in the same Python process during unit tests.
    """

    src_root = Path(__file__).resolve().parents[1] / "src"
    src_root_text = str(src_root)
    if src_root_text not in sys.path:
        sys.path.insert(0, src_root_text)
