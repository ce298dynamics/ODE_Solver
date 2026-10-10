"""Run something on the next pass of the event loop, unless its owner goes first.

`QTimer.singleShot(0, owner, callback)` is the obvious way, and with a Python
callable it crashed: test workers died with an access violation inside
`processEvents`, at the moment pending zero-delay timers fire, once three
widgets had begun deferring work that way, and never on `main`, which used
none. A timer that is the owner's *child* cannot outlive it: Qt deletes it with
the owner, so it never fires for a widget that is already gone.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QTimer

__all__ = ["run_soon"]


def run_soon(owner: QObject, callback: Callable[[], None]) -> None:
    """Call `callback` once the event loop next runs, if `owner` still exists.

    One callback per owner: the first one given is the one the timer keeps,
    and asking again before it fires runs it once, not twice -- which is what
    every caller here wants, since each defers one decision about itself.
    """
    timer = getattr(owner, "_run_soon_timer", None)
    if timer is None:
        timer = QTimer(owner)
        timer.setSingleShot(True)
        timer.setInterval(0)
        timer.timeout.connect(callback)
        owner._run_soon_timer = timer  # type: ignore[attr-defined]
    timer.start()
