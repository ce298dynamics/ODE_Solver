"""Entry point for the frozen application.

`odesuite_app/__main__.py` uses a relative import, which is correct for
``python -m odesuite_app`` but fails under PyInstaller: the bundle runs the
entry script as a top-level module, so it has no parent package. This launcher
uses an absolute import instead, and leaves `__main__.py` alone.
"""

from __future__ import annotations

import multiprocessing
import sys

if __name__ == "__main__":
    # Required on Windows: without it, any library that spawns a process would
    # re-execute the bundled application instead of a Python interpreter.
    multiprocessing.freeze_support()

    from odesuite_app.cli import main

    sys.exit(main())
