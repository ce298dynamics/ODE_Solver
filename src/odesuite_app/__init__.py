"""odesuite studio — a desktop front end for the odesuite ODE solver.

Kept in a separate package from `odesuite` on purpose: the library must remain
importable, testable and installable with no GUI dependency. Install this with

    pip install odesuite[app]

and launch it with ``odesuite-gui`` or ``python -m odesuite_app``.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["main", "__version__"]


def main(argv: list[str] | None = None) -> int:
    """Entry point. Imported lazily so `import odesuite_app` stays cheap."""
    from .cli import main as _main

    return _main(argv)
