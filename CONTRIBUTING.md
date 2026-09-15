# Contributing

## Getting set up

```
python -m venv .venv
.venv/bin/pip install -e ".[dev]"          # Windows: .venv\Scripts\pip
```

`[dev]` brings the interface, sympy, pytest and the checkers. The library alone
needs only numpy and scipy — `pip install -e .` — and that is worth knowing,
because keeping it true is one of the project's promises (see Architecture).

## The three checks CI runs

```
pytest tests/ -q -n auto        # ~8 minutes in parallel
ruff check .
mypy
```

All three must be clean. `pytest` forces Qt's offscreen platform from
`tests/conftest.py`, so the interface tests run without opening a window.

Coverage is gated: 95% for `odesuite`, 88% overall.

```
pytest tests/ -q -n auto --cov=odesuite --cov=odesuite_app
```

## What "done" means here

This project holds itself to a standard that is stricter than most, and the
reason is the subject: a plausible-looking wrong answer from an ODE solver is
worse than an obvious failure, and a student cannot tell the difference. So:

1. **A change is covered by a test that fails without it.** For anything
   numerical, that test asserts a *number* — an observed convergence order, an
   achieved-versus-requested error ratio, a step count — not merely that the
   code runs. `tests/test_convergence.py` and `tests/test_regressions.py` are
   the models.

2. **A claim in a docstring is backed by a test, or it is not made.** If a
   docstring says a method is fifth order, something measures that it is.

3. **The reason is recorded where the next reader will find it** — in a comment
   at the code, not only in a commit message. This is the practice most worth
   protecting. `steppers/rosenbrock.py` explains why ROS3P was deleted rather
   than shipped with an error estimate that could not be verified; that comment
   is why nobody will put it back by accident.

4. **A behavioural change goes in `CHANGELOG.md`**, under the right heading,
   with removals under Removed.

5. **No new magic number** without a named constant and a comment saying what it
   trades against what.

6. **If a change alters what the application tells a learner**, the lesson or
   blurb is updated in the same commit. The standing example of getting this
   wrong: a lesson taught that `y' = y^(1/3)`, `y(0) = 0` has two solutions
   while the solver returned one of them and reported success, with nothing to
   connect the two.

## Architecture, in one paragraph

`odesuite` is the numerics: problems, steppers, controllers, dense output,
events, and a driver that owns time and contains no method-specific
mathematics. It depends on numpy and scipy and **never imports Qt** — there is a
CI job whose only purpose is to fail if it starts to. `odesuite_app` is the
interface on top: a `SessionState` view-model, thirteen screens, and a
non-Qt logic layer (`symbolic`, `steps`, `analysis`, `catalog`, `lessons`) that
is testable without a display. Adding a Runge–Kutta method means adding
coefficients to `tableaux.py` and no code at all.

## Adding a method

Coefficients go in `tableaux.py` (explicit) or the relevant stepper module.
`tests/test_tableaux.py` will check them against the rooted-tree order
conditions automatically, and `tests/test_convergence.py` will measure the order
you claimed. Both run without being asked. If either disagrees with the
docstring, the docstring is wrong until proven otherwise.

Prefer deriving coefficients to transcribing them where that is possible: Radau's
eigendecomposition comes from `numpy.linalg.eig` at import time and the Yoshida
composition weights from a closed-form recursion, precisely so that neither can
be mistyped.

## Parsing user input

Anything a user can type reaches sympy, and sympy's parser evaluates what it is
given. Any new call to `parse_expr` must be preceded by
`odesuite_app.custom.reject_unsafe_syntax`. See `SECURITY.md` for why both the
name whitelist and the syntax check are needed and why neither is sufficient
alone.

## Reporting a security issue

Do not open a public issue. See `SECURITY.md`.
