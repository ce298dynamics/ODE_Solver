# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-08-17

The first release that can be installed, and the first with a measured
performance claim behind it.

### Added

- **`PredictiveController`** — Gustafsson's predictive step-size controller, and
  the default for the implicit methods. It adds a term reading how the error
  responded to the last step-size change rather than the current error alone,
  and declines any proposed growth under 1.2× outright, keeping `h`
  bit-for-bit identical so the iteration matrix stays valid.
- **`Stepper.default_controller`** — a method now states which controller suits
  it. A step-size change is free for an explicit method and costs an `O(n³)`
  refactorisation for an implicit one; that is a property of the method, not a
  caller preference.
- `examples/` — eight runnable scripts, every one executed by the test suite.
- A documentation site (`mkdocs.yml`, `docs/`) with an API reference generated
  from the docstrings.
- `py.typed` — the library has been fully annotated and `mypy`-clean for a while,
  and without this marker none of that was visible to a downstream type checker.
- `ruff` and `mypy` configuration, and GitHub Actions CI across Linux and
  Windows on Python 3.10 and 3.12, including a job asserting that the library
  never imports Qt.
- `tests/test_controllers.py` and `tests/test_newton.py` — the two modules that
  had no direct tests at all.
- `figures/work_precision.json`, written beside the figure so a change in
  performance is a reviewable diff rather than something spotted by eye.

### Changed

- **Stiff solvers are 1.18–1.32× faster**, using 19% fewer RHS evaluations and
  10% fewer LU factorisations. Against SciPy's Radau the gap closed from
  1.3–1.5× evaluations to 1.08–1.22×, and from ~1.7× wall time to 1.2–1.5×.
  Explicit methods are unaffected, and a test asserts their output is bitwise
  identical.
- `irk.py` now uses `simplified_newton` and `JacobianPolicy` instead of
  reimplementing both inline. Verified bit-identical on the stiff benchmarks.
- `ODEProblem.f` fast-paths a right-hand side that already returns a 1-D array;
  `is_dae` is cached instead of running an SVD on every access.
- `solve(controller=...)` now defaults to `None`, meaning "let the method
  choose". Passing a name or instance still overrides it.
- The work-precision figure wraps into a grid; it was previously a 3 806 px-wide
  strip in which no legend was legible.
- The version is declared once, in `odesuite.__version__`. It had drifted across
  three files.

### Fixed

- **A reused `Controller` instance carried its error history between solves**, so
  the same problem solved twice gave 82 steps and then 83. Nothing raised and
  both answers were within tolerance; the only symptom was that an identical
  computation was not reproducible.
- **`thumbnails.render_thumbnail` drove pyplot from a worker thread** while its
  own docstring promised thread-safety. pyplot's figure registry is global and
  `matplotlib.use` swaps the global backend.
- A non-finite state is now reported as such instead of surfacing as step-size
  underflow, which named nothing the caller had written.
- `_solve_event` returned the end of the step as a root when the bracket did not
  survive interpolation — a fabricated detection, which could also consume a
  terminal event's allowance. It now reports none.
- `DSOLVE_TIMEOUT` was bound as a default argument at import and could not be
  changed at runtime; `symbolicpanel` had imported the value rather than the
  module, freezing it twice over.
- `odesuite-gui` printed a bare PySide6 traceback when the `app` extra was not
  installed. It now says which extra to install. `--list-problems` and
  `--selftest` work without Qt.
- A docstring in `steppers/exponential.py` had a prose paragraph inside its
  `Parameters` block, so every numpydoc tool read the first word of each line as
  a parameter name.
- `test_split_solve_is_cheaper_on_a_large_system` compared two ~4 ms wall-clock
  samples and inverted under `pytest -n auto`. It now times the factorisation
  the claim is actually about (a ~9x margin rather than 1.5x), and skips where
  the platform BLAS has a pathologically slow complex `getrf` — measured at
  1300x slower than the real path for n >= 100 with numpy 2.2.6 on Windows,
  which makes the split path lose for reasons that have nothing to do with this
  library. The deterministic half of the old test, that the two linear-solve
  paths agree, is now its own test.

## [0.1.0] — 2026-08-16

The state of the project when it came under version control: the library, the
studio, and 943 tests. Its development is narrated in the README — the adaptive
Runge–Kutta core, stiff solvers and DAEs, events and dense output, the Taylor
and exponential integrators, the symbolic equation solver, and the typeset
closed forms.

[0.2.0]: https://keepachangelog.com/
[0.1.0]: https://keepachangelog.com/
