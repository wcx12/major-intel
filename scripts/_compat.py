"""Compatibility helpers for legacy script entrypoints.

The project is moving stable implementation code into ``src/major_intel``.
Many manual test commands still execute files under ``scripts/`` directly, and
direct execution puts ``scripts/`` rather than the repository root on
``sys.path``.  This helper keeps those old commands working while the real
modules live in the importable package.
"""

from __future__ import annotations

from importlib import import_module
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def ensure_src_on_path() -> None:
    """Make ``src/`` importable for legacy wrappers.

    The function is intentionally idempotent because several wrappers can be
    imported in the same Python process during unit tests.
    """

    src_root = Path(__file__).resolve().parents[1] / "src"
    src_root_text = str(src_root)
    if src_root_text not in sys.path:
        sys.path.insert(0, src_root_text)


def expose_package_module(module_name: str, namespace: dict[str, Any]) -> ModuleType:
    """Expose a package module through a legacy script namespace.

    Most files under ``scripts/`` are now compatibility entrypoints.  Tests and
    manual commands may still import names from those legacy files, so wrappers
    need to re-export public functions, constants, and classes from the real
    implementation module.  Keeping that logic here prevents every wrapper from
    hand-rolling a slightly different import/export pattern.
    """

    ensure_src_on_path()
    module = import_module(module_name)
    namespace.update(
        {
            name: getattr(module, name)
            for name in dir(module)
            if not (name.startswith("__") and name.endswith("__"))
        }
    )
    return module


def exit_with_module_main(module: ModuleType) -> int:
    """Run ``module.main`` for wrapper CLI execution when it exists.

    Some legacy files such as oracle helpers were import-only modules and never
    had a command-line ``main``.  Returning ``0`` for those keeps direct
    execution harmless while preserving imports for older tests.
    """

    main = getattr(module, "main", None)
    if main is None:
        return 0
    result = main()
    return int(result) if isinstance(result, int) else 0
