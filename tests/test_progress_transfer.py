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


def _mastered(**kwargs):
    """A record in the last Leitner box: three in a row, all of them right."""
    base = dict(right=3, tries=3, streak=progress.MASTERED_STREAK)
    base.update(kwargs)
    return _answer(**base)


@pytest.mark.parametrize("days,expected", [
    (0, False),
    (progress.STALE_AFTER_DAYS - 1, False),
    (progress.STALE_AFTER_DAYS, True),
    (progress.STALE_AFTER_DAYS * 4, True),
])
def test_staleness_starts_at_the_threshold(days, expected):
    """For something mastered, which is what the longest interval is for."""
    assert _mastered(seen=_days_ago(days)).is_stale is expected


def test_something_got_wrong_is_never_stale():
    """It is not stale, it is unfinished -- and `weakest` already surfaces
    those. Calling it stale as well would report one gap twice."""
    wrong = _answer(state=progress.State.ATTEMPTED, right=0, streak=0,
                    seen=_days_ago(progress.STALE_AFTER_DAYS * 3))
    assert not wrong.is_stale


# ---------------------------------------------------------------------------
# The Leitner boxes
# ---------------------------------------------------------------------------


def test_the_three_boxes_are_named_and_ordered():
    names = [name for name, _ in progress.LEITNER]
    intervals = [days for _, days in progress.LEITNER]
    assert names == ["learning", "familiar", "known"]
    assert intervals == sorted(intervals), "a later box must wait longer"
    assert intervals[-1] == progress.STALE_AFTER_DAYS


@pytest.mark.parametrize("streak,bucket", [
    (0, "learning"),
    (1, "familiar"),
    (2, "familiar"),
    (progress.MASTERED_STREAK, "known"),
    (progress.MASTERED_STREAK + 5, "known"),
])
def test_the_streak_decides_the_box(streak, bucket):
    """Leitner exactly: a right answer moves the card on, a wrong one sends it
    back to the front. `streak` is already that counter."""
    answer = _answer(right=max(streak, 1), tries=max(streak, 1), streak=streak)
    assert answer.bucket == bucket


def test_a_missed_question_falls_back_to_the_first_box():
    """However long its tick has stood. This is the property a flat rule could
    not express: three weeks after a miss is not three weeks after mastery."""
    lapsed = _answer(right=9, tries=12, streak=0, seen=_days_ago(2))
    assert lapsed.bucket == "learning"
    assert lapsed.interval == 1
    assert lapsed.is_stale, "due the day after it was missed"


def test_a_recovery_is_not_promoted_to_the_last_box():
    """Three in a row on a question missed more often than not is a recovery.
    Believing the streak over the record would hide it for three weeks."""
    struggled = _answer(right=3, tries=9, streak=progress.MASTERED_STREAK)
    assert struggled.accuracy < progress.LEITNER_ACCURACY
    assert struggled.bucket == "familiar"
    assert struggled.interval == 7


def test_the_interval_is_per_question_not_per_file():
    """The whole of the change. Two questions answered on the same day are
    not equally due."""
    day = _days_ago(8)
    fresh = _answer(right=1, tries=1, streak=1, seen=day)
    known = _mastered(seen=day)
    assert fresh.is_stale and not known.is_stale
    assert fresh.days_until_due == -1
    assert known.days_until_due == 13
    assert fresh.overdue == 1 and known.overdue == 0


def test_a_record_with_no_date_is_never_due():
    """Unknown is not the same as overdue; a version 2 file honestly has no
    date, and inventing one would invent a schedule."""
    assert _mastered(seen="").days_until_due is None
    assert _mastered(seen="").overdue == 0


def test_boxes_counts_every_recorded_question(store):
    from odesuite_app.lessons import UNITS

    lesson = UNITS[0].lessons[0]
    everything = {
        lesson.key: {
            lesson.questions[0].key: _answer(right=1, tries=1, streak=1),
            lesson.questions[1].key: _mastered(),
        },
        progress.drill_key(lesson.key): {
            lesson.templates[0].key: _answer(
                state=progress.State.ATTEMPTED, right=0, tries=2, streak=0),
        },
    }
    assert progress.boxes(UNITS, everything) == {
        "learning": 1, "familiar": 1, "known": 1,
    }


def test_boxes_ignores_records_the_course_no_longer_has(store):
    """A key left behind by a lesson that has since changed is not a fact
    about anybody's memory."""
    from odesuite_app.lessons import UNITS

    everything = {"a-lesson-that-went-away": {"q1": _mastered()}}
    assert progress.boxes(UNITS, everything) == {
        "learning": 0, "familiar": 0, "known": 0,
    }


def test_stale_ranks_by_the_debt_not_the_age(store):
    """A question a fortnight past a one-day interval is more overdue than one
    a day past a three-week interval, even though it is younger."""
    from odesuite_app.lessons import UNITS

    first, second = UNITS[0].lessons[0], UNITS[0].lessons[1]
    everything = {
        # Younger, but in the first box and so fifteen days overdue.
        first.key: {q.key: _answer(right=1, tries=3, streak=0,
                                   state=progress.State.CORRECT,
                                   seen=_days_ago(16))
                    for q in first.questions},
        # Older, but mastered, so only a day past due.
        second.key: {q.key: _mastered(seen=_days_ago(22))
                     for q in second.questions},
    }
    order = [item[0].key for item in progress.stale(UNITS, everything)]
    assert order == [first.key, second.key]


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
# Which option, not just which question
# ---------------------------------------------------------------------------
#
# A state can say a question was missed. It cannot say *how*, and how is the
# interesting half: every distractor in the course is written as one
# misconception, with its own reason attached, and until the pick was stored
# none of that could be read back. Four misses of four questions and four
# misses of the same option are different facts about somebody.


def test_a_pick_is_recorded_beside_the_state(store):
    store.record("separable", "q1", store.State.ATTEMPTED, picked=2)
    assert store.load()["separable"]["q1"].picks == (2,)


def test_picks_accumulate_in_the_order_they_happened(store):
    for option in (2, 2, 0):
        store.record("separable", "q1", store.State.ATTEMPTED, picked=option)
    assert store.load()["separable"]["q1"].picks == (2, 2, 0)


def test_only_the_last_few_picks_are_kept(store):
    """A window, not a history. A drill answered fifty times would otherwise
    let a misconception long since fixed outvote the one still held."""
    for option in range(store.PICKS_KEPT + 5):
        store.record("separable", "q1", store.State.ATTEMPTED,
                     picked=option % 4)
    kept = store.load()["separable"]["q1"].picks
    assert len(kept) == store.PICKS_KEPT
    assert kept[-1] == (store.PICKS_KEPT + 4) % 4, "the most recent survives"


def test_a_typed_answer_records_no_pick(store):
    """There were no options, so there is nothing to say about which was
    chosen -- and the file should not carry an empty list per question."""
    store.record("separable", "q1", store.State.CORRECT)
    assert store.load()["separable"]["q1"].picks == ()

    saved = json.loads((store.path()).read_text(encoding="utf-8"))
    assert "picks" not in saved["answers"]["separable"]["q1"]


def test_a_file_from_before_picks_existed_reads_as_none(store, tmp_path):
    folder = tmp_path / "odesuite"
    folder.mkdir(parents=True)
    (folder / "progress.json").write_text(json.dumps({
        "version": 3,
        "answers": {"separable": {"q1": {"state": "attempted", "right": 0,
                                         "tries": 1, "streak": 0,
                                         "seen": date.today().isoformat()}}},
    }), encoding="utf-8")

    answer = store.load()["separable"]["q1"]
    assert answer.picks == ()
    assert answer.tries == 1, "the rest of the record is untouched"


def test_nonsense_in_the_picks_is_discarded_and_the_record_kept(store,
                                                                tmp_path):
    """The file is user-editable by design. Losing a tick somebody earned over
    a field that only decides the wording of a hint would be the worse bug."""
    folder = tmp_path / "odesuite"
    folder.mkdir(parents=True)
    (folder / "progress.json").write_text(json.dumps({
        "version": 4,
        "answers": {"separable": {
            "q1": {"state": "correct", "right": 1, "tries": 1, "streak": 1,
                   "picks": [1, "two", -3, None, 0]},
            "q2": {"state": "correct", "right": 1, "tries": 1, "streak": 1,
                   "picks": "not a list"},
        }},
    }), encoding="utf-8")

    kept = store.load()["separable"]
    assert kept["q1"].picks == (1, 0)
    assert kept["q2"].picks == ()
    assert kept["q2"].correct, "the record survives its broken field"


def test_picks_survive_an_export_and_an_import(store, tmp_path):
    store.record("separable", "q1", store.State.ATTEMPTED, picked=3)
    store.export_to(tmp_path / "copy.json")
    store.reset()
    store.import_from(tmp_path / "copy.json")

    assert store.load()["separable"]["q1"].picks == (3,)


# ---------------------------------------------------------------------------
# What the picks are for
# ---------------------------------------------------------------------------


def _choice_lesson():
    """The first lesson holding a hand-written multiple-choice question."""
    from odesuite_app.lessons import UNITS

    for unit in UNITS:
        for lesson in unit.lessons:
            for question in lesson.questions:
                if getattr(question, "kind", "") == "choice":
                    return UNITS, unit, lesson, question
    pytest.skip("no multiple-choice question in the course")


def test_the_same_wrong_option_three_times_is_surfaced(store):
    units, _unit, lesson, question = _choice_lesson()
    wrong = next(index for index in range(len(question.options))
                 if index != question.answer)
    everything = {lesson.key: {question.key: _answer(
        state=progress.State.ATTEMPTED, right=0, streak=0,
        picks=(wrong, wrong, wrong),
    )}}

    found = progress.misconceptions(units, everything)
    assert [item.option for item in found] == [wrong]
    assert found[0].times == 3
    assert found[0].picks == 3
    assert found[0].lesson.key == lesson.key
    assert found[0].question is question


def test_choosing_the_right_option_repeatedly_is_not_a_misconception(store):
    """It is the point. Only the distractors are counted."""
    units, _unit, lesson, question = _choice_lesson()
    everything = {lesson.key: {question.key: _answer(
        picks=(question.answer,) * 5
    )}}

    assert progress.misconceptions(units, everything) == []


def test_one_wrong_pick_is_a_slip_rather_than_a_habit(store):
    units, _unit, lesson, question = _choice_lesson()
    wrong = next(index for index in range(len(question.options))
                 if index != question.answer)
    everything = {lesson.key: {question.key: _answer(
        state=progress.State.ATTEMPTED, right=0, streak=0,
        picks=(question.answer, wrong),
    )}}

    assert progress.misconceptions(units, everything) == []


def test_a_pick_is_recorded_in_the_option_the_author_wrote(store):
    """The whole reason `Choice.origins` exists. A generated question shuffles
    its options per draw, so a tally of shown positions would count a different
    option each time -- the position is drilled, the index is remembered."""
    from odesuite_app.lessons import generate

    units, _unit, lesson, template = _drill_template()
    first, second = generate.draw_choice(template, 1), generate.draw_choice(
        template, 2)
    wrong = next(index for index in range(len(template.options))
                 if index != template.answer)
    # The same option, at whatever position each draw happens to show it.
    picks = (first.canonical(first.origins.index(wrong)),
             second.canonical(second.origins.index(wrong)))
    assert picks == (wrong, wrong)

    everything = {progress.drill_key(lesson.key): {template.key: _answer(
        state=progress.State.ATTEMPTED, right=0, streak=0, picks=picks,
    )}}
    found = progress.misconceptions(units, everything)
    assert [item.option for item in found] == [wrong]

    shown, reason = generate.option_written(template, wrong)
    assert shown and reason, "the index turns back into what was clicked"


def _drill_template():
    from odesuite_app.lessons import UNITS

    for unit in UNITS:
        for lesson in unit.lessons:
            for template in lesson.templates:
                if getattr(template, "kind", "") == "choice-template":
                    return UNITS, unit, lesson, template
    pytest.skip("no generated multiple-choice drill in the course")


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
