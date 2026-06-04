"""Compatibility wrapper for ``major_intel.ingestion.graduate_outcome_package``."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _compat import exit_with_module_main, expose_package_module

_impl = expose_package_module("major_intel.ingestion.graduate_outcome_package", globals())


if __name__ == "__main__":
    raise SystemExit(exit_with_module_main(_impl))
