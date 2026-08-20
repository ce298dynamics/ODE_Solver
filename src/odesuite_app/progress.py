"""What the learner has already answered, remembered between sessions.

This is the first thing the application stores on disk. Everything else it does
is recomputed from the equation in front of it, which is why there has never
been a config file -- but a study tool that forgets what you have done each time
you open it is a study tool nobody finishes.

Three rules, all of them about not being the reason someone loses work or
cannot start the app.

**A broken file is never fatal.** Anything unreadable -- truncated, edited by
hand, written by a different version -- is treated as "no progress recorded"
rather than raised. Losing a tick is a small harm; refusing to open the Learning
Hub is a large one.

**Writes are atomic.** The file is written beside its destination and renamed
over it, so a crash midway leaves the previous version intact rather than half
a file.

**It is plain, small, and yours.** One JSON object of lesson -> question ->
state, in the ordinary per-user config directory, with a button in the
interface that deletes it.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

__all__ = [
    "State",
    "directory",
    "path",
    "load",
    "record",
    "reset",
    "counts",
]


class State:
    """The states a question can be in. Strings, so the file stays readable."""

    CORRECT = "correct"
    ATTEMPTED = "attempted"


#: Everything valid that may appear as a value. Anything else is discarded on
#: load rather than trusted -- the file is user-editable by design.
_STATES = frozenset({State.CORRECT, State.ATTEMPTED})

_FILENAME = "progress.json"


def directory() -> Path:
    """The per-user config directory, following each platform's convention."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / "odesuite"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "odesuite"
    base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / "odesuite"


def path() -> Path:
    return directory() / _FILENAME


def load() -> dict[str, dict[str, str]]:
    """Everything recorded, or an empty mapping if there is nothing usable.

    Never raises. The shape is validated rather than trusted: the file is plain
    JSON in a directory the user owns, so it can contain anything at all, and
    the interface must not be handed a string where it expects a mapping.
    """
    try:
        raw = json.loads(path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}

    clean: dict[str, dict[str, str]] = {}
    for lesson, answers in raw.items():
        if not isinstance(lesson, str) or not isinstance(answers, dict):
            continue
        kept = {
            question: state
            for question, state in answers.items()
            if isinstance(question, str) and state in _STATES
        }
        if kept:
            clean[lesson] = kept
    return clean


def record(lesson: str, question: str, state: str) -> dict[str, dict[str, str]]:
    """Note an answer and save. Returns the whole updated mapping.

    A question already answered correctly stays correct: getting it right and
    then mistyping it should not take the tick away.
    """
    if state not in _STATES:
        raise ValueError(f"unknown state {state!r}")

    everything = load()
    answers = everything.setdefault(lesson, {})
    if answers.get(question) == State.CORRECT and state != State.CORRECT:
        return everything
    answers[question] = state
    _save(everything)
    return everything


def reset() -> None:
    """Forget everything. The file is removed rather than emptied."""
    try:
        path().unlink()
    except OSError:
        pass


def counts(lesson: str, questions: int,
           everything: dict[str, dict[str, str]] | None = None) -> tuple[int, int]:
    """``(answered correctly, total)`` for one lesson."""
    answers = (load() if everything is None else everything).get(lesson, {})
    correct = sum(1 for state in answers.values() if state == State.CORRECT)
    return min(correct, questions), questions


def _save(everything: dict[str, dict[str, str]]) -> None:
    """Write atomically, and treat failure as not worth interrupting anyone for.

    Written to a temporary file in the same directory and renamed over the
    destination, because rename within a directory is atomic on every platform
    this runs on. A crash halfway through leaves the previous file, not half of
    this one.
    """
    try:
        folder = directory()
        folder.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=folder, suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(everything, stream, indent=1, sort_keys=True)
            os.replace(temporary, path())
        except BaseException:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise
    except OSError:
        pass                # a read-only home should not break the interface
