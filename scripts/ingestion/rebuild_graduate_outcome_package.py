"""Structured CLI wrapper for graduate outcome package rebuilding."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _compat import exit_with_module_main, expose_package_module

_impl = expose_package_module("major_intel.ingestion.graduate_outcome_package", globals())


if __name__ == "__main__":
    raise SystemExit(exit_with_module_main(_impl))
