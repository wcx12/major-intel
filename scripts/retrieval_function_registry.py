"""Compatibility wrapper for ``major_intel.function_calls.registry``."""

from __future__ import annotations

from importlib import import_module
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _compat import ensure_src_on_path

ensure_src_on_path()
_impl = import_module("major_intel.function_calls.registry")
globals().update({name: getattr(_impl, name) for name in dir(_impl) if not (name.startswith("__") and name.endswith("__"))})


if __name__ == "__main__":
    raise SystemExit(_impl.main())
