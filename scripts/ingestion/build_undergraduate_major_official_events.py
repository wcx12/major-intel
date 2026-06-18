"""Structured CLI wrapper for undergraduate official major-event outputs."""

from __future__ import annotations

from importlib import import_module
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _compat import ensure_src_on_path

ensure_src_on_path()
_impl = import_module("major_intel.ingestion.undergraduate_major_official_events")
globals().update({name: getattr(_impl, name) for name in dir(_impl) if not (name.startswith("__") and name.endswith("__"))})


if __name__ == "__main__":
    raise SystemExit(_impl.main())
