"""A local record of failed solves, and a report to paste into a bug (REL-04).

The application sends nothing anywhere, and that stays true: see the README's
Privacy section, which names this file. What was missing is the other half of
that position. With no telemetry, the only way the author learns that a solver
failed for somebody is that somebody reports it -- and until now there was
nothing useful to report, because `SolveResult` captured the traceback and the
screen showed one line of it and then it was gone.

So: failed solves are appended to ``diagnostics.log`` beside `progress.json`,
one JSON object per line, and `report` turns the last few into text for the
clipboard. Three rules, the same three `progress` keeps:

* **Never fatal.** Logging runs inside the path that is already handling a
  failure; it must not become a second one. Every write and read swallows its
  own errors.
* **Bounded.** Past `MAX_BYTES` the older half is dropped, so the file cannot
  grow without limit on a machine that fails the same solve all afternoon.
* **Nothing about you.** What is recorded is the problem, the method, the
  tolerances, the parameters and the error -- the same things `session.json`
  already holds -- and tracebacks are scrubbed of every filesystem path above
  the package that raised, so a username in a home directory does not end up
  pasted into an issue tracker.
"""

from __future__ import annotations

import json
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any

from . import progress

__all__ = ["MAX_BYTES", "path", "record", "record_result", "recent", "report",
           "scrub"]

_FILENAME = "diagnostics.log"

#: Size at which the older half of the log is dropped. At a few hundred bytes
#: an entry -- more with a traceback -- this keeps the last hundred or so
#: failures, which is far more than a bug report needs.
MAX_BYTES = 64 * 1024

#: Entries a report includes by default.
REPORT_ENTRIES = 10


def path() -> Path:
    return progress.directory() / _FILENAME


# A traceback line reads ``File "C:\Users\someone\...\odesuite_app\x.py"``.
# Everything up to the last directory that is a package the reader can look up
# -- this project's, or a third-party one under site-packages -- is dropped.
_PATH = re.compile(r'File "([^"]+)"')
_ANCHORS = ("odesuite_app", "odesuite", "site-packages")


def scrub(text: str) -> str:
    """`text` with filesystem paths cut down to the package they are inside.

    Only paths in ``File "..."`` lines are touched, and only their prefix: the
    part that says which module and line raised is the part a report is for.
    A path under none of the anchors -- the user's own script, say -- is
    replaced by its file name alone.
    """
    def shorten(match: re.Match) -> str:
        parts = re.split(r"[\\/]", match.group(1))
        for index in range(len(parts) - 1, -1, -1):
            if parts[index] in _ANCHORS:
                keep = parts[index + 1:] if parts[index] == "site-packages" \
                    else parts[index:]
                return 'File "' + "/".join(keep) + '"'
        return 'File "' + parts[-1] + '"'

    home = str(Path.home())
    return _PATH.sub(shorten, text).replace(home, "~")


def record(entry: dict[str, Any], *, where: Path | None = None) -> None:
    """Append one entry. Never raises."""
    target = where or path()
    try:
        entry = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), **entry}
        if "traceback" in entry:
            entry["traceback"] = scrub(str(entry["traceback"]))
        line = json.dumps(entry, default=str, ensure_ascii=False) + "\n"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size + len(line) > MAX_BYTES:
            lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
            target.write_text("".join(lines[len(lines) // 2:]), encoding="utf-8")
        with target.open("a", encoding="utf-8") as handle:
            handle.write(line)
    except Exception:           # noqa: BLE001 - a log must never be the failure
        pass


def record_result(result, *, where: Path | None = None) -> bool:
    """Record a `SolveResult` if it failed. Returns whether it was recorded.

    A cancelled solve is not a failure -- the user moved a slider -- and a
    clean finish is not one either. Anything else is: an exception while
    building or solving, or a solver that stopped and said why.
    """
    try:
        if getattr(result, "cancelled", False):
            return False
        solution = getattr(result, "solution", None)
        diagnosis = getattr(solution, "diagnosis", None)
        error = getattr(result, "error", None)
        if error is None and (diagnosis is None or not diagnosis.failed):
            return False
        request = result.request
        entry: dict[str, Any] = {
            "problem": request.problem_key,
            "method": request.method,
            "rtol": request.rtol,
            "atol": request.atol,
            "n_steps": request.n_steps,
            "params": dict(request.params or {}),
        }
        if error is not None:
            entry["error"] = error
        if diagnosis is not None:
            entry["diagnosis"] = str(diagnosis)
        trace = getattr(result, "traceback", None)
        if trace:
            entry["traceback"] = trace
        record(entry, where=where)
        return True
    except Exception:           # noqa: BLE001
        return False


def recent(count: int = REPORT_ENTRIES, *, where: Path | None = None) -> list[dict]:
    """The last `count` entries, oldest first. Unreadable lines are skipped."""
    target = where or path()
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except Exception:           # noqa: BLE001
        return []
    entries = []
    for line in lines[-count:]:
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    return entries


def _versions() -> list[str]:
    from . import __version__

    found = [f"odesuite {__version__}",
             f"Python {platform.python_version()} ({sys.implementation.name})"]
    for name in ("numpy", "scipy", "sympy", "PySide6", "pyqtgraph", "matplotlib"):
        module = sys.modules.get(name)
        version = getattr(module, "__version__", None) if module else None
        if version:
            found.append(f"{name} {version}")
    return found


def report(count: int = REPORT_ENTRIES, *, where: Path | None = None) -> str:
    """Plain text for a bug report: versions, platform, and recent failures."""
    lines = ["odesuite diagnostics", "",
             *_versions(),
             f"{platform.system()} {platform.release()} ({platform.machine()})",
             ""]
    entries = recent(count, where=where)
    if not entries:
        lines.append("No failed solves recorded.")
    for entry in entries:
        lines.append(
            f"[{entry.get('time', '?')}] {entry.get('problem', '?')} with "
            f"{entry.get('method', '?')}, rtol={entry.get('rtol')}, "
            f"atol={entry.get('atol')}, n_steps={entry.get('n_steps')}"
        )
        if entry.get("params"):
            lines.append(f"  params: {entry['params']}")
        for field in ("error", "diagnosis"):
            if entry.get(field):
                lines.append(f"  {field}: {entry[field]}")
        if entry.get("traceback"):
            lines += ["  " + row for row in str(entry["traceback"]).splitlines()]
        lines.append("")
    return scrub("\n".join(lines).rstrip() + "\n")
