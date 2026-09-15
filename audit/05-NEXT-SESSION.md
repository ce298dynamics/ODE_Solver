# Next session: the highest-ratio items

> **This brief has been run. Read `06-OUTCOME.md` first.** Four of the five
> items below were already built when it was written — they landed in
> `bb0b8eb`, the commit before this file — and two of the three things it calls
> broken are not broken in the way it says. The body below is otherwise left as
> the input that was actually given, amended only where a later session struck
> something out in place; `06-OUTCOME.md` is what came back.

A brief for a scheduled cloud session. Self-contained: it assumes no memory of
the sessions that produced `01-FINDINGS.md` through `04-ROADMAP.md`.

Five items, chosen for value per unit of effort rather than for size. They are
drawn from a longer list (A1–F3) that spans question design, feedback quality,
study workflow, figures, content gaps and accessibility; the rest of that list
is deliberately out of scope for this run.

---

## Read first

- `audit/03-BACKLOG.md` and `audit/01-FINDINGS.md` — the audit these item
  numbers come from (PED-xx, SYM-xx, A11Y-xx).
- `CONTRIBUTING.md`, and `git log -5` — the commit style here is distinctive
  essay prose that explains *why*, names what was measured, and admits what was
  got wrong along the way. Match it.
- `src/odesuite_app/lessons/model.py` and `lessons/generate.py` — the
  template / slot / draw machinery every generated question is built on.
  `ChoiceTemplate` and `NumericTemplate` already exist; `draw(template, seed)`
  is the API.
- `src/odesuite_app/symbolic.py` — `classify_ode`, `TECHNIQUES`, and
  `check_answer`, which grades by symbolic equivalence rather than string
  match. Several items below are that same trick pointed somewhere new.

## House rules — not optional

1. **Verify, don't guess.** Never cite a file, function or line you have not
   opened. Never quote a measurement you have not run.
2. **Measure before you build, and write the failing test first.** Earlier
   sessions killed a proposed design this way, when the sympy call underneath
   it did not return in ten minutes; and caught three of their own wrong test
   assumptions before the code was blamed.
3. **Say what you did not verify.** If PySide6 will not install in the cloud
   environment, the Qt tests `importorskip` and silently pass. That is not
   verification. State plainly which changes are unverified and why.
4. **Put the reasoning in a comment where the next reader will find it**, not
   only in the commit message.
5. If an item turns out to be a bad idea once measured, **say so and skip it**
   rather than building it anyway. A retraction with evidence is worth more
   than a feature.

## Step 0 — establish a baseline

**First, `git pull`** -- this brief is committed to the repository and may
be older than `main`. Then install (`pip install -e ".[app,dev]"`; see
`pyproject.toml`) and run
`pytest -q -m "not slow"`. Record pass / fail / skip counts *before* touching
anything.

Two known outstanding problems, both to fix before new work:

- ~~Roughly four failures somewhere in the app-side modules.~~ **Gone.** They
  were the portrait hang below: with `density=33` the analysis never returned,
  `_settle` timed out, and the assertions ran against `None`. `hopf_window` was
  the suspect named here and it was the wrong one — `all_benchmarks()` iterates
  the explicit `NONSTIFF`/`STIFF`/`DAE`/`TEXTBOOK` lists, not `__all__`, and
  nothing in the suite policices `__all__` at all. Recorded because a wrong
  suspect left standing costs the next reader an hour.

- **Two failures remain, and they are real:**
  `tests/test_text_scale.py::test_raising_the_scale_re_renders_rather_than_keeping_a_stale_bitmap`
  and `::test_the_maths_tracks_the_body_text`, from the in-flight A11Y-04 work.

  They reproduce **only** in a whole-suite `pytest -n 4` run — reliably there,
  three runs out of three — and never alone (12 passed, 2.9s), under xdist
  alone (`-n 1`, `-n 2`, `-n 4` all green), with their real predecessors from
  that worker (119 passed), or under deliberate parallel load against four
  CPU-heavy files (195 passed).

  The failure message now carries the deciding state, and it says:

      bitmap 44px, typeset=True, application font 18pt against a 9pt baseline

  So the scale **is** applied (18pt against a 9pt baseline is exactly 2.0), the
  label **is** typeset, the thread pool is **idle** — and the bitmap is still
  44px, the height it had at scale 1.0. This is not a timeout and not load: the
  equation simply never re-renders, which is precisely what the first of those
  two tests is named to catch. The test is right and the feature is not
  finished.

  Where to look: `MathLabel.changeEvent` in
  `src/odesuite_app/widgets/mathlabel.py` refreshes only when
  `abs(theme.text_scale() - self._scale) > 0.005`. A stale 44px bitmap with no
  null-pixmap flash in between means `_refresh` never ran, so the font event
  never arrived at the label — the `_FONT_EVENTS` comment right above it
  records that Qt's delivery here was already surprising once. Reproduce with
  the full `-n 4` suite; nothing smaller has worked.
- ~~`tests/test_app_portrait.py` does not complete in ten minutes.~~
  **Fixed in `aec8245`, after this brief was first written. Do not spend time
  on it; `git pull` before you start.** The cause was `analyse` passing the
  grid resolution positionally into `streamlines`' fourth parameter, which is
  matplotlib's `density` -- so every portrait was drawn at `density=33` against
  an intended 1.1. Measured on the pendulum: 0.76s at 1.1, 45s at 10, no answer
  at all at 33. The file now runs in 3m21s with all 21 unskipped tests passing.

  If you find yourself waiting many minutes on anything that builds a phase
  portrait, you are on an old checkout. Pull.

---

## A1 · Technique-selection drill

**Size:** S–M. **The best ratio on the whole list.**

Almost every question in the app is "apply the technique this lesson just
named". No exam works that way — choosing the technique *is* the skill, and it
is currently taught only in prose, at `lessons/unit1_first_order.py:780`.

Build a `ChoiceTemplate` over a pool of equations: which method applies, and
why not the other three. `classify_ode` and `TECHNIQUES` already exist and
should be used to keep the answer key honest — the key must be *derived*, never
hand-written, so it cannot drift from what the app actually does.

Per-option `becauses` is exactly the right shape for the distractors: "this is
separable-looking but the y does not factor". Ship one per unit plus a
cumulative pool.

## B1 · Diagnose the residual, don't print it

**Size:** S–M.

`_check_solve` currently prints the leftover expression raw: `what is left
over: <residual>`. The residual usually *names* the mistake. A short ladder of
tests turns a dump into a diagnosis:

- residual equals the forcing term → they solved the homogeneous equation and
  stopped. Say "you have the complementary function but no particular
  solution."
- answer is a constant multiple of a correct one → a lost coefficient.
- `matches_conditions` False while `correct` is True → the method was right and
  the constants were not.

Fall back to the current raw output when no rule fires. Do not guess at a
diagnosis you cannot justify from the expression.

## C3 · Formula-sheet generator

**Size:** S.

65 notes with `kind="formula"` already exist across the lessons. Collect them
per unit, and for the whole course, into one printable sheet. The real exam
allows a hand-written crib sheet, so this matches something the student
actually needs.

Note: printable infrastructure landed recently in `src/odesuite_app/printable.py`
and `screens/learn_print.py` — read them first and reuse rather than duplicate.

## D2 · Carry the equation into the tool

**Size:** S, and the highest *perceived* payoff on the list.

`_open_tool` emits a screen name and nothing else, so "open this in the Solver
Lab" lands the reader on an empty lab. Pass the lesson's example equation and
its initial conditions through, so it lands on the thing they were just
reading.

## F3 · Fully keyboard-driven drill loop

**Size:** S. (A11Y adjacent.)

`returnPressed` is already wired for *checking* an answer in four places;
*advancing* to the next question still needs the mouse. Make Enter check, then
Enter advance, so a drill can be run without leaving the keyboard.

---

## Deliverable

A branch and a pull request. In the PR description, state:

- the baseline test counts and the counts at the end;
- for each of the five items: done, partly done, or skipped — and if skipped,
  the evidence that killed it;
- **everything you could not verify**, and why.

Commit in coherent pieces rather than one lump, and give each commit the kind
of message the recent history has. Do not force-push, and do not rewrite
existing history.
