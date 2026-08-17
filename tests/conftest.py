"""Shared pytest configuration.

Qt is forced into its offscreen platform before PySide6 is imported anywhere, so
the interface tests run headlessly -- in CI, over SSH, and without stealing
focus by flashing windows onto the developer's screen.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Qt no longer bundles fonts; under the offscreen platform it needs pointing at
# the system directory or every text metric collapses to zero.
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
