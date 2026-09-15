# What the next session actually found

The outcome of running `05-NEXT-SESSION.md`. Read it beside that brief: four of
the five items it asks for were already built when it was written, and two of
the three things it says are broken are not broken in the way it says.

None of that is a criticism of the brief, which was written to be read cold and
succeeds at that. It is the ordinary hazard of a plan written a commit before
it is executed.

---

## The five items, against the code as it stood

| Item | State at HEAD before this session |
|---|---|
| **A1** technique-selection drill | Partly built. `ClassifyTemplate`, `Case`, `vocabulary.VOCABULARIES` and `generate.draw_classify` all existed, with drills in four units of seven. No cumulative pool. |
| **B1** diagnose the residual | **Already done.** `symbolic.diagnose`, with the ladder the brief describes — forcing term left over, constant multiple, conditions failing while `correct` is True — and the raw-residual fallback. Wired into `learn_lessons._check_solve` and `learn_quiz._check_solve`. |
| **C3** formula-sheet generator | **Already done.** `lessons.formulas()` collects the 65 `kind="formula"` notes, `printable.formula_sheet()` sets them, and `screens/learn_print.py` offers per-unit and whole-course. |
| **D2** carry the equation into the tool | **Already done.** `open_tool` carries `(key, equation, conditions)`, `app._open_tool` calls `screen.load_equation`, and `CARRIES_EQUATION` names the two tools that can take one. |
| **F3** keyboard-only drill loop | **Already done.** `learn_lessons._keyboard_loop`: Enter checks, Enter again advances, the key taken once at the card so a single press cannot do both. |

All four landed in `bb0b8eb`, the commit immediately before the brief itself.

So the work left for A1 was the cumulative pool and the units without a drill,
and that is what this session built — plus the finding that two of those units
should not have one at all, recorded in `lessons/vocabulary.py`.

## The two known-broken things

**"Roughly four failures, prime suspect `hopf_window`."** Seven failures, and
`hopf_window` is innocent. Nothing iterates `problems.__all__`;
`all_benchmarks` walks the explicit `NONSTIFF`, `STIFF`, `DAE` and `TEXTBOOK`
tuples plus `bouncing_ball`, and `hopf_window` is in none of the eight groups.
`all_benchmarks()` returns 26 benchmarks without error and the catalogue has
its 30 entries. Every one of the seven was a test that had gone stale — a
signal that grew an argument, two tests that predate difficulty tiers, a
question-kind tuple never extended, a `getattr` the test did not use, one
false positive in a "reads as generated" guard, and one test that could only
ever have passed on Windows. See `f1f4a99`.

**"`test_app_portrait.py` does not complete in ten minutes."** True, and the
cause is not in that file. `analyse` passed its `resolution` — 33 —
positionally into `streamlines`' `density` parameter. Measured on the pendulum
over the window the screen opens on: 0.781 s and 90 paths at the intended
density, 372.045 s and 4609 paths at 33. The fixture builds a screen per test,
so 24 tests each waited out a six-minute analysis. With the density passed
correctly the file runs all 24 tests in 122 s. It was also a defect in what the
screen *drew*: 4609 overlapping curves is a scribble. See `e69c7f1`.

## A third thing the brief did not know about

`ruff check .` was red at HEAD — twelve findings, all introduced by the
bifurcation work, none of them a defect. `CONTRIBUTING.md` says all three
checks must be clean. `mypy` was clean. See `52a8eef`.

## Measuring the suite at all

Worth knowing before the next run. Serially, `pytest -q -m "not slow"` with
`test_app_portrait.py` excluded does not finish inside 50 minutes on a
four-core cloud container. The project's own CI invocation — `-n auto`, per
`CONTRIBUTING.md` — does it in about 15 minutes.

But `-n 4` is not a reliable way to *count* failures here: it reported fifteen,
and the extra eight were all in `test_mathrender.py`, every one of which passes
serially and in isolation. They are contention between parallel workers over
the Qt text machinery. Count serially; run in parallel.

Two tests in `tests/test_quiz.py` seed their paper from `int(time.time())`, so
they draw different questions depending on the second the run starts. Both are
now pinned with `seed_override`; if a quiz test starts failing intermittently,
that is the first thing to check.
