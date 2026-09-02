"""What the learner has already answered, remembered between sessions.

This is the only thing the application stores on disk. Everything else it does
is recomputed from the equation in front of it, which is why there was no config
file for a long time -- but a study tool that forgets what you have done each
time you open it is a study tool nobody finishes.

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
record, in the ordinary per-user config directory, with a button in the
interface that deletes it.

Format
------

Version 2 records how many times a question was attempted as well as how it
ended, because a course map that can only say "answered" cannot tell steady work
from a lucky guess::

    {"version": 2,
     "answers": {"separable": {"q1": {"state": "correct",
                                      "right": 1, "tries": 2}}}}

Version 1 stored the bare state string. Such a file still loads -- an existing
`progress.json` written by an earlier build keeps its ticks, and is rewritten in
the new shape the next time anything is recorded. Refusing to read it, or
quietly dropping it, would take away work already done, which is the one thing
this module exists to avoid.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "VERSION",
    "MASTERED_STREAK",
    "State",
    "Answer",
    "directory",
    "path",
    "drill_key",
    "load",
    "record",
    "reset",
    "counts",
    "mastery",
    "drills",
    "unit_progress",
    "weakest",
    "UnitProgress",
]

#: The format written. Older files are read; nothing writes an older one.
VERSION = 2

#: Correct answers in a row before a drill counts as mastered. Three is Khan
#: Academy's rule and a defensible one: one is luck, two is a coincidence, and
#: a drill draws fresh numbers each time so three is three different questions.
MASTERED_STREAK = 3


class State:
    """The states a question can be in. Strings, so the file stays readable."""

    CORRECT = "correct"
    ATTEMPTED = "attempted"


@dataclass(frozen=True)
class Answer:
    """What is known about one question."""

    state: str
    #: How many times it has been answered correctly.
    right: int = 0
    #: How many times it has been answered at all.
    tries: int = 0
    #: Correct answers in a row, right now. Reset by a wrong one -- which is
    #: the point: a drill is mastered by getting it right repeatedly, not by
    #: getting it right eventually.
    streak: int = 0

    @property
    def correct(self) -> bool:
        return self.state == State.CORRECT

    @property
    def mastered(self) -> bool:
        return self.streak >= MASTERED_STREAK


#: Everything valid that may appear as a state. Anything else is discarded on
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


def drill_key(lesson: str) -> str:
    """Where a lesson's drill answers live.

    A separate bucket, because a drill never runs out and a lesson's practice
    questions do. Counting both in one place would make "3 of 5" mean nothing:
    the denominator is fixed and the numerator would not be.
    """
    return f"{lesson}/drill"


def _count(value: object) -> int:
    """A non-negative integer, or 0 for anything else.

    `bool` is excluded explicitly: it is a subclass of `int`, so ``True`` would
    otherwise be stored and later printed as a tally of one.
    """
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _answer(value: object) -> Answer | None:
    """One stored record, in either format, or None if it is not usable."""
    if isinstance(value, str):                      # version 1
        if value not in _STATES:
            return None
        right = 1 if value == State.CORRECT else 0
        return Answer(state=value, right=right, tries=1, streak=right)
    if isinstance(value, dict):                     # version 2
        state = value.get("state")
        if state not in _STATES:
            return None
        # `streak` arrived after the rest of version 2, so a file written
        # between the two reads as "no streak yet" rather than as broken.
        return Answer(state=state, right=_count(value.get("right")),
                      tries=_count(value.get("tries")),
                      streak=_count(value.get("streak")))
    return None


def load() -> dict[str, dict[str, Answer]]:
    """Everything recorded, or an empty mapping if there is nothing usable.

    Never raises. The shape is validated rather than trusted at every level:
    the file is plain JSON in a directory the user owns, so it can contain
    anything at all, and the interface must not be handed a string where it
    expects a mapping.
    """
    try:
        raw = json.loads(path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}

    # A version 2 file wraps the answers; a version 1 file *is* them.
    if isinstance(raw.get("answers"), dict) and "version" in raw:
        raw = raw["answers"]

    clean: dict[str, dict[str, Answer]] = {}
    for lesson, answers in raw.items():
        if not isinstance(lesson, str) or not isinstance(answers, dict):
            continue
        kept = {}
        for question, value in answers.items():
            if not isinstance(question, str):
                continue
            answer = _answer(value)
            if answer is not None:
                kept[question] = answer
        if kept:
            clean[lesson] = kept
    return clean


def record(lesson: str, question: str,
           state: str) -> dict[str, dict[str, Answer]]:
    """Note an answer and save. Returns the whole updated mapping.

    A question already answered correctly stays correct: getting it right and
    then mistyping it should not take the tick away. The attempt is still
    counted, because it happened.
    """
    if state not in _STATES:
        raise ValueError(f"unknown state {state!r}")

    everything = load()
    answers = everything.setdefault(lesson, {})
    before = answers.get(question)
    was_right = state == State.CORRECT
    right = (before.right if before else 0) + was_right
    tries = (before.tries if before else 0) + 1
    kept = State.CORRECT if (before and before.correct) else state
    streak = ((before.streak if before else 0) + 1) if was_right else 0
    answers[question] = Answer(state=kept, right=right, tries=tries,
                               streak=streak)
    _save(everything)
    return everything


def reset() -> None:
    """Forget everything. The file is removed rather than emptied."""
    try:
        path().unlink()
    except OSError:
        pass


def counts(lesson: str, questions: int,
           everything: dict[str, dict[str, Answer]] | None = None
           ) -> tuple[int, int]:
    """``(answered correctly, total)`` for one lesson.

    Clamped, so a lesson that lost a question does not report 6 of 5 from a
    file written before it did.
    """
    answers = (load() if everything is None else everything).get(lesson, {})
    correct = sum(1 for answer in answers.values() if answer.correct)
    return min(correct, questions), questions


def mastery(lesson: str, questions: int,
            everything: dict[str, dict[str, Answer]] | None = None) -> float:
    """How much of a lesson is done, in 0…1. Zero questions reads as zero."""
    if questions <= 0:
        return 0.0
    done, total = counts(lesson, questions, everything)
    return done / total


def drills(lesson: str, templates, everything=None) -> tuple[int, int]:
    """``(mastered, total)`` for one lesson's drills.

    `templates` is the lesson's templates, or just their keys. Mastery is a
    streak rather than an ever-answered-correctly, so this number can go down;
    that is deliberate, and it is what makes it worth showing.
    """
    keys = [getattr(item, "key", item) for item in templates]
    if not keys:
        return 0, 0
    answers = (load() if everything is None
               else everything).get(drill_key(lesson), {})
    done = sum(1 for key in keys
               if key in answers and answers[key].mastered)
    return done, len(keys)


@dataclass(frozen=True)
class UnitProgress:
    """What is done in one unit, for the Course Map and the quiz picker."""

    answered: int
    questions: int
    mastered: int
    drills: int
    #: Lessons with every question answered correctly.
    finished: int
    lessons: int

    @property
    def fraction(self) -> float:
        """Questions and drills together, in 0…1.

        Both, rather than questions alone: a unit whose questions are all
        ticked but whose drills are untouched is not finished in any sense the
        word is usually meant, and a ring that said it was would be lying by
        omission.
        """
        total = self.questions + self.drills
        if total <= 0:
            return 0.0
        return (self.answered + self.mastered) / total


def unit_progress(unit, everything: dict[str, dict[str, Answer]] | None = None
                  ) -> UnitProgress:
    """Aggregate one unit's lessons. Built from `counts` and `drills`.

    No new storage: the file already records everything this needs, and a
    second place recording the same facts would be a second place for them to
    disagree.
    """
    everything = load() if everything is None else everything
    answered = questions = mastered = total_drills = finished = 0
    for lesson in unit.lessons:
        done, asked = counts(lesson.key, len(lesson.questions), everything)
        answered += done
        questions += asked
        finished += bool(asked and done == asked)
        got, has = drills(lesson.key, lesson.templates, everything)
        mastered += got
        total_drills += has
    return UnitProgress(answered=answered, questions=questions,
                        mastered=mastered, drills=total_drills,
                        finished=finished, lessons=len(unit.lessons))


def weakest(units, everything: dict[str, dict[str, Answer]] | None = None,
            limit: int = 3) -> list:
    """The lessons worth going back to, weakest first.

    Only lessons that have been *started*: a lesson never opened is not weak,
    it is simply next, and putting it here would turn "what to review" into a
    second table of contents. What counts as weak is the fraction of questions
    answered correctly, so a lesson answered wrongly and left ranks above one
    barely begun.
    """
    everything = load() if everything is None else everything
    scored = []
    for unit in units:
        for lesson in unit.lessons:
            asked = len(lesson.questions)
            done, _ = counts(lesson.key, asked, everything)
            attempted = len(everything.get(lesson.key, {}))
            if not attempted or (asked and done == asked):
                continue
            scored.append(((done / asked) if asked else 0.0, lesson, unit))
    scored.sort(key=lambda item: (item[0], item[1].key))
    return [(lesson, unit) for _, lesson, unit in scored[:limit]]


def _save(everything: dict[str, dict[str, Answer]]) -> None:
    """Write atomically, and treat failure as not worth interrupting anyone for.

    Written to a temporary file in the same directory and renamed over the
    destination, because rename within a directory is atomic on every platform
    this runs on. A crash halfway through leaves the previous file, not half of
    this one.
    """
    payload = {
        "version": VERSION,
        "answers": {
            lesson: {
                question: {"state": answer.state, "right": answer.right,
                           "tries": answer.tries, "streak": answer.streak}
                for question, answer in answers.items()
            }
            for lesson, answers in everything.items()
        },
    }
    try:
        folder = directory()
        folder.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=folder, suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=1, sort_keys=True)
            os.replace(temporary, path())
        except BaseException:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise
    except OSError:
        pass                # a read-only home should not break the interface
