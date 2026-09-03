"""Progress worth keeping: exporting it, importing it, and letting it go stale.

Three small things that share a subject -- what happens to what you have done.
Before them, progress lived in one file on one machine with no way to ask for a
copy, mastery was a streak that never decayed so a lesson finished in July
could never be surfaced again, and the window reopened on Home at a default
size every single time.

The riskiest of the three is `import_from`, and the test that matters most is
that it cannot lose work: importing a file from a machine where less had been
done must not delete anything, which is the exact failure the feature exists
to prevent.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest

pytest.importorskip("sympy")

from odesuite_app import progress  # noqa: E402


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    return progress


def _answer(**kwargs):
    base = dict(state=progress.State.CORRECT, right=1, tries=1, streak=1,
                seen=date.today().isoformat())
    base.update(kwargs)
    return progress.Answer(**base)


def _days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


# ---------------------------------------------------------------------------
# The date on an answer
# ---------------------------------------------------------------------------


def test_recording_stamps_the_day(store):
    store.record("separable", "q1", store.State.CORRECT)
    answer = store.load()["separable"]["q1"]

    assert answer.seen == date.today().isoformat()
    assert answer.days_since_seen == 0
    assert not answer.is_stale


def test_a_file_from_before_the_date_existed_reads_as_never_seen(store,
                                                                 tmp_path):
    """A version 2 file has no `seen`, and that is what it honestly is -- so it
    reads as unknown rather than as today, which would invent a fact."""
    folder = tmp_path / "odesuite"
    folder.mkdir(parents=True)
    (folder / "progress.json").write_text(json.dumps({
        "version": 2,
        "answers": {"separable": {"q1": {"state": "correct", "right": 1,
                                         "tries": 1, "streak": 1}}},
    }), encoding="utf-8")

    answer = store.load()["separable"]["q1"]
    assert answer.seen == ""
    assert answer.days_since_seen is None
    assert not answer.is_stale, "unknown is not the same as long ago"


def test_a_nonsense_date_is_not_trusted(store, tmp_path):
    """The file is user-editable by design, so every field is validated."""
    folder = tmp_path / "odesuite"
    folder.mkdir(parents=True)
    (folder / "progress.json").write_text(json.dumps({
        "version": 3,
        "answers": {"separable": {
            "q1": {"state": "correct", "right": 1, "tries": 1, "streak": 1,
                   "seen": "the day before yesterday"},
            "q2": {"state": "correct", "right": 1, "tries": 1, "streak": 1,
                   "seen": 20260101},
        }},
    }), encoding="utf-8")

    kept = store.load()["separable"]
    assert kept["q1"].days_since_seen is None
    assert kept["q2"].seen == "", "a non-string date is discarded"


@pytest.mark.parametrize("days,expected", [
    (0, False),
    (progress.STALE_AFTER_DAYS - 1, False),
    (progress.STALE_AFTER_DAYS, True),
    (progress.STALE_AFTER_DAYS * 4, True),
])
def test_staleness_starts_at_the_threshold(days, expected):
    assert _answer(seen=_days_ago(days)).is_stale is expected


def test_something_got_wrong_is_never_stale():
    """It is not stale, it is unfinished -- and `weakest` already surfaces
    those. Calling it stale as well would report one gap twice."""
    wrong = _answer(state=progress.State.ATTEMPTED, right=0, streak=0,
                    seen=_days_ago(progress.STALE_AFTER_DAYS * 3))
    assert not wrong.is_stale


# ---------------------------------------------------------------------------
# What to bring back
# ---------------------------------------------------------------------------


def test_stale_surfaces_a_lesson_that_weakest_cannot(store):
    """The whole reason for the second list. A lesson answered perfectly long
    ago scores perfectly, so ranking by score can never bring it back."""
    from odesuite_app.lessons import UNITS

    lesson = UNITS[0].lessons[0]
    everything = {
        lesson.key: {
            question.key: _answer(seen=_days_ago(60))
            for question in lesson.questions
        }
    }

    assert progress.weakest(UNITS, everything) == [], "it scores perfectly"
    brought_back = progress.stale(UNITS, everything)
    assert [item[0].key for item in brought_back] == [lesson.key]
    assert brought_back[0][2] >= 60


def test_stale_puts_the_longest_ago_first(store):
    from odesuite_app.lessons import UNITS

    first, second = UNITS[0].lessons[0], UNITS[0].lessons[1]
    everything = {
        first.key: {q.key: _answer(seen=_days_ago(90))
                    for q in first.questions},
        second.key: {q.key: _answer(seen=_days_ago(30))
                     for q in second.questions},
    }
    order = [item[0].key for item in progress.stale(UNITS, everything)]
    assert order == [first.key, second.key]


def test_nothing_recent_is_stale(store):
    from odesuite_app.lessons import UNITS

    lesson = UNITS[0].lessons[0]
    everything = {lesson.key: {q.key: _answer() for q in lesson.questions}}
    assert progress.stale(UNITS, everything) == []


# ---------------------------------------------------------------------------
# Export and import
# ---------------------------------------------------------------------------


def test_export_writes_a_file_the_application_can_read(store, tmp_path):
    """The exported file *is* a progress file -- one format, so there is no
    second schema to keep in step and it can be copied into place by hand."""
    store.record("separable", "q1", store.State.CORRECT)
    written = store.export_to(tmp_path / "backup.json")

    assert written.exists()
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["version"] == progress.VERSION
    assert payload["answers"]["separable"]["q1"]["state"] == "correct"


def test_a_round_trip_loses_nothing(store, tmp_path):
    store.record("separable", "q1", store.State.CORRECT)
    store.record("linear", "q2", store.State.ATTEMPTED)
    before = store.load()

    written = store.export_to(tmp_path / "backup.json")
    store.reset()
    assert store.load() == {}

    assert store.import_from(written) == before


def test_import_merges_rather_than_replacing(store, tmp_path):
    """Replacing outright would let an import from a machine where less had
    been done delete work -- the failure this feature exists to prevent,
    committed by the feature itself."""
    store.record("separable", "q1", store.State.CORRECT)
    written = store.export_to(tmp_path / "one.json")

    store.reset()
    store.record("linear", "q1", store.State.CORRECT)
    store.import_from(written)

    everything = store.load()
    assert "separable" in everything, "the imported lesson is missing"
    assert "linear" in everything, "the existing lesson was deleted"


def test_the_merge_keeps_the_stronger_record(store, tmp_path):
    """Where both files know a question, the better record wins: more correct
    answers, then the longer streak, then the later date."""
    for _ in range(3):
        store.record("separable", "q1", store.State.CORRECT)
    strong = store.load()["separable"]["q1"]
    assert strong.streak == 3
    written = store.export_to(tmp_path / "strong.json")

    store.reset()
    store.record("separable", "q1", store.State.ATTEMPTED)
    merged = store.import_from(written)["separable"]["q1"]

    assert merged.streak == 3
    assert merged.right == 3


def test_the_merge_does_not_weaken_what_is_already_there(store, tmp_path):
    """The other direction, which matters just as much: importing an older,
    thinner file must not undo a streak built since."""
    store.record("separable", "q1", store.State.ATTEMPTED)
    thin = store.export_to(tmp_path / "thin.json")

    store.reset()
    for _ in range(3):
        store.record("separable", "q1", store.State.CORRECT)
    merged = store.import_from(thin)["separable"]["q1"]

    assert merged.streak == 3, "an older file overwrote a better record"


def test_importing_rubbish_is_not_fatal(store, tmp_path):
    """An imported file is exactly as untrustworthy as the one on disk: plain
    JSON somebody may have edited."""
    store.record("separable", "q1", store.State.CORRECT)
    broken = tmp_path / "broken.json"
    broken.write_text("{not json at all", encoding="utf-8")

    assert store.import_from(broken)["separable"]["q1"].correct
    missing = store.import_from(tmp_path / "nothing-here.json")
    assert missing["separable"]["q1"].correct


def test_import_can_replace_when_asked(store, tmp_path):
    store.record("separable", "q1", store.State.CORRECT)
    written = store.export_to(tmp_path / "one.json")

    store.reset()
    store.record("linear", "q1", store.State.CORRECT)
    store.import_from(written, merge=False)

    everything = store.load()
    assert "separable" in everything
    assert "linear" not in everything, "replace should mean replace"
