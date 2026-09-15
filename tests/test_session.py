"""Saving and restoring what the application was looking at.

"Van der Pol at mu = 800, radau, rtol = 1e-9, on the Stiffness Explorer" could
not be written down: closing the application lost it, and an instructor had no
way to hand a class a configured starting point.

The security case is the one worth watching, and it has its own test below.
Every expression the parser saw used to have just been typed by the person
sitting there. A session file can arrive from anywhere, so loading one
re-parses its text through `symbolic.parse_equation` -- the same door the
keyboard uses, and therefore the same `reject_unsafe_syntax` check. A file must
not be able to smuggle an expression past a guard a person cannot.
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip("sympy")
pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app import catalog, session, symbolic  # noqa: E402
from odesuite_app.state import SessionState  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


@pytest.fixture
def state(qapp):
    made = SessionState()
    yield made
    catalog.clear_user_equation()


# ---------------------------------------------------------------------------
# The round trip
# ---------------------------------------------------------------------------


def test_a_configured_session_comes_back_exactly(state, qapp, tmp_path):
    """The acceptance criterion: problem, method, tolerances, parameters and
    screen all reproduced."""
    state.set_problem("van_der_pol")
    state.set_method("radau")
    state.set_tolerances(1e-9, 1e-11)
    state.set_param("mu", 800.0)

    written = session.save(state, screen="stiffness", path=tmp_path / "s.json")
    assert written is not None and written.exists()

    fresh = SessionState()
    screen = session.apply(fresh, session.load(written))

    assert screen == "stiffness"
    assert fresh.problem_key == "van_der_pol"
    assert fresh.method == "radau"
    assert fresh.rtol == pytest.approx(1e-9)
    assert fresh.atol == pytest.approx(1e-11)
    assert fresh.params["mu"] == pytest.approx(800.0)


def test_a_fixed_step_session_keeps_its_step_count(state, qapp, tmp_path):
    state.set_problem("harmonic_2d")
    state.set_method("verlet")
    state.set_n_steps(4321)

    written = session.save(state, path=tmp_path / "s.json")
    fresh = SessionState()
    session.apply(fresh, session.load(written))

    assert fresh.method == "verlet"
    assert fresh.n_steps == 4321


def test_the_saved_file_is_small_plain_json(state, qapp, tmp_path):
    """A session is a request, not a result. Storing the solution would make a
    large file that goes stale the moment anything changes."""
    written = session.save(state, screen="lab", path=tmp_path / "s.json")
    payload = json.loads(written.read_text(encoding="utf-8"))

    assert payload["format"] == session.FORMAT
    assert set(payload) <= {
        "format", "problem", "method", "rtol", "atol", "n_steps", "params",
        "screen", "equation",
    }
    assert written.stat().st_size < 4096


# ---------------------------------------------------------------------------
# A bad file is never fatal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "contents",
    [
        "",                                  # empty
        "{",                                 # truncated
        "not json at all",
        "[1, 2, 3]",                         # json, but not an object
        '{"format": 999, "problem": "logistic"}',   # a future format
        '{"problem": "logistic"}',           # no format at all
    ],
    ids=["empty", "truncated", "not-json", "not-an-object", "future", "unversioned"],
)
def test_an_unusable_file_reads_as_no_session(tmp_path, contents):
    path = tmp_path / "broken.json"
    path.write_text(contents, encoding="utf-8")
    assert session.load(path) is None


def test_a_missing_file_reads_as_no_session(tmp_path):
    assert session.load(tmp_path / "was-never-written.json") is None


def test_a_session_naming_a_problem_that_no_longer_exists_is_declined(state, qapp):
    assert session.apply(state, {"format": session.FORMAT, "problem": "atlantis"}) == ""


def test_one_bad_field_costs_that_field_and_not_the_restore(state, qapp):
    """A file may have been hand-edited. Restoring what makes sense beats
    refusing the lot."""
    screen = session.apply(state, {
        "format": session.FORMAT,
        "problem": "logistic",
        "method": "not-a-method",          # ignored
        "rtol": -1.0,                      # ignored: must be positive
        "atol": 1e-9,
        "n_steps": "many",                 # ignored: not an int
        "params": {"nonexistent": 1.0, "r": 0.5},
        "screen": "lab",
    })
    assert screen == "lab"
    assert state.problem_key == "logistic"
    assert state.method != "not-a-method"
    assert state.rtol > 0
    assert state.params.get("r") == pytest.approx(0.5)


def test_a_parameter_from_outside_the_slider_range_is_clamped(state, qapp):
    """Restoring a value the interface cannot show would make the control jump
    on first touch."""
    spec = next(s for s in catalog.get("logistic").params if s.name == "r")
    session.apply(state, {
        "format": session.FORMAT,
        "problem": "logistic",
        "params": {"r": spec.high * 1000},
    })
    assert state.params["r"] <= spec.high


def test_saving_somewhere_unwritable_returns_none_rather_than_raising(state, qapp,
                                                                     tmp_path):
    """Failing to save a session is a small loss, and not a reason to interrupt
    anyone -- the rule `progress.py` sets for the only other file written."""
    blocked = tmp_path / "a-file-not-a-directory"
    blocked.write_text("in the way", encoding="utf-8")
    assert session.save(state, path=blocked / "s.json") is None


# ---------------------------------------------------------------------------
# A typed equation, and the security property
# ---------------------------------------------------------------------------


def _register_typed(equation: str, conditions: str = ""):
    """Register a typed equation the way the Solver Lab does."""
    from odesuite_app.equationmodel import build_entry

    spec = symbolic.spec_for(equation, conditions)
    catalog.register_user_equation(build_entry(symbolic.parse_equation(spec)))
    return spec


def test_a_typed_equation_survives_the_round_trip(state, qapp, tmp_path):
    spec = _register_typed("y' = -3*y + sin(t)", "y(0) = 2")
    state.set_problem(catalog.USER_KEY, force=True)

    written = session.save(state, screen="lab", path=tmp_path / "s.json",
                           equation=spec)
    catalog.clear_user_equation()

    fresh = SessionState()
    screen = session.apply(fresh, session.load(written))

    assert screen == "lab"
    assert fresh.problem_key == catalog.USER_KEY
    restored = catalog.user_entry()
    assert restored is not None


def test_an_equation_in_a_session_file_goes_through_the_same_guard(state, qapp,
                                                                  tmp_path):
    """The security property. A session file is a *less* trustworthy source
    than a keyboard, because it can arrive from somewhere else, so the text in
    one is checked by `reject_unsafe_syntax` exactly as typed text is.
    """
    canary = tmp_path / "canary.txt"
    payload = (
        'sin.__class__.__init__.__globals__["__builtins__"]["open"]'
        f"({str(canary)!r}, 'w').write('pwned')"
    )
    hostile = tmp_path / "hostile.json"
    hostile.write_text(json.dumps({
        "format": session.FORMAT,
        "problem": catalog.USER_KEY,
        "method": "dopri5",
        "rtol": 1e-6, "atol": 1e-9, "n_steps": 2000, "params": {},
        "equation": {
            "equations": [f"y' = {payload}"],
            "initial_conditions": "",
            "variables": ["y"],
            "parameters": {},
            "t_span": [0.0, 10.0],
            "name": "hostile",
        },
    }), encoding="utf-8")

    stored = session.load(hostile)
    assert stored is not None, "the file itself is well-formed JSON"

    screen = session.apply(state, stored)

    assert not canary.exists(), "a session file executed code"
    assert screen == "", "the hostile equation must not restore"


def test_a_session_whose_equation_no_longer_parses_is_declined(state, qapp):
    """The equation *was* the session; without it there is nothing to restore,
    and falling back to some other problem would be a silent substitution."""
    screen = session.apply(state, {
        "format": session.FORMAT,
        "problem": catalog.USER_KEY,
        "equation": {
            "equations": ["y' = "],           # incomplete
            "initial_conditions": "",
            "variables": ["y"],
            "parameters": {},
            "t_span": [0.0, 10.0],
            "name": "broken",
        },
    })
    assert screen == ""


# ---------------------------------------------------------------------------
# The command line
# ---------------------------------------------------------------------------


def test_the_session_flag_is_accepted_and_documented():
    from odesuite_app.cli import build_parser

    parsed = build_parser().parse_args(["--session", "somewhere.json"])
    assert parsed.session == "somewhere.json"

    help_text = build_parser().format_help()
    assert "--session" in help_text
    for word in ("problem", "method", "screen"):
        assert word in help_text
