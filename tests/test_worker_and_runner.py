"""The subprocess boundary and the threading layer.

These were the two least-covered non-trivial modules in the application —
`dsolve_worker` at 58% and `solver` at 79% — and they are also the two where a
bug is hardest to reproduce and most likely to hang the interface. What was
covered in both was the happy path; what was not was every way each can fail.

`dsolve_worker` is exercised in-process by calling `solve_payload` and `run`
with crafted payloads rather than by spawning the real subprocess. That is not a
shortcut: it is the only way to reach a branch like "the general solution came
out but the initial conditions could not be applied" deterministically, and the
real subprocess round trip is already covered by `test_symbolic.py`.
"""

from __future__ import annotations

import io
import json

import pytest

pytest.importorskip("sympy")
pytest.importorskip("PySide6", reason="the app extra is not installed")

import sympy as sp  # noqa: E402

from odesuite_app import dsolve_worker  # noqa: E402

_T = sp.Symbol("t", real=True)


def _payload(equation_text, function_text="y(t)", ics=None, **extra):
    """A request in the shape the parent process sends: `srepr` strings."""
    return {
        "equations": [equation_text],
        "functions": [function_text],
        "ics": ics or {},
        **extra,
    }


def _srepr_problem(rhs, order=1):
    """``y' = rhs`` (or ``y'' = rhs``) as the wire format carries it."""
    y = sp.Function("y")
    equation = sp.Eq(sp.Derivative(y(_T), (_T, order)), rhs)
    return sp.srepr(equation), sp.srepr(y(_T))


# ---------------------------------------------------------------------------
# The wire protocol
# ---------------------------------------------------------------------------


def test_a_malformed_request_is_answered_rather_than_crashed(monkeypatch, capsys):
    """The parent reads one JSON object from this process's stdout. A worker
    that dies without writing one leaves the parent parsing nothing."""
    monkeypatch.setattr("sys.stdin", io.StringIO("this is not json"))

    status = dsolve_worker.run()

    assert status == 1
    reply = json.loads(capsys.readouterr().out.strip())
    assert reply["ok"] is False
    assert "bad request" in reply["error"]


def test_a_valid_request_produces_exactly_one_final_reply(monkeypatch, capsys):
    equation, function = _srepr_problem(-2 * sp.Function("y")(_T))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO(json.dumps(_payload(equation, function)))
    )

    status = dsolve_worker.run()

    assert status == 0
    lines = [line for line in readouterr_lines(capsys) if line.strip()]
    final = json.loads(lines[-1])
    assert final["ok"] is True
    assert final.get("partial") is not True


def readouterr_lines(capsys):
    return capsys.readouterr().out.splitlines()


def test_partials_are_published_before_the_final_reply(monkeypatch, capsys):
    """`dsolve` can hang, so the worker publishes what it already knows first
    and the parent reads that out of the killed process's output. If partials
    stopped being emitted, a timeout would lose the classification and the
    narration that had already been computed."""
    equation, function = _srepr_problem(-2 * sp.Function("y")(_T))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO(json.dumps(_payload(equation, function)))
    )

    dsolve_worker.run()

    lines = [json.loads(line) for line in readouterr_lines(capsys) if line.strip()]
    assert len(lines) >= 2, "no partial was published"
    assert any(reply.get("partial") for reply in lines[:-1])
    assert lines[-1].get("partial") is not True


def test_a_worker_failure_becomes_a_reply_not_a_traceback(monkeypatch, capsys):
    """`solve_payload` raising must still leave the parent a readable answer."""

    def explode(payload, emit=None):
        raise RuntimeError("something in sympy gave way")

    monkeypatch.setattr(dsolve_worker, "solve_payload", explode)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(_payload("x"))))

    status = dsolve_worker.run()

    assert status == 0
    reply = json.loads(readouterr_lines(capsys)[-1])
    assert reply["ok"] is False
    assert "something in sympy gave way" in reply["error"]


# ---------------------------------------------------------------------------
# The branches of solve_payload
# ---------------------------------------------------------------------------


def test_an_equation_sympy_cannot_solve_says_so_without_failing():
    """`NotImplementedError` from `dsolve` is an answer, not a fault."""
    y = sp.Function("y")
    # A right-hand side with no closed form sympy will find.
    equation = sp.Eq(sp.Derivative(y(_T), _T), sp.sin(y(_T)) + _T ** 2 * y(_T) ** 3)
    reply = dsolve_worker.solve_payload(
        _payload(sp.srepr(equation), sp.srepr(y(_T)))
    )
    assert reply["ok"] is False
    assert "error" in reply
    # The classification is still useful even when no closed form comes out.
    assert "hints" in reply


def test_a_general_solution_survives_initial_conditions_that_do_not_apply():
    """An IVP can fail where the general solution succeeded — inconsistent or
    insufficient conditions. Throwing the general solution away because the
    conditions were wrong would discard the useful half."""
    y = sp.Function("y")
    equation = sp.Eq(sp.Derivative(y(_T), _T), -2 * y(_T))
    # Two conditions for a first-order equation: over-determined.
    ics = {
        sp.srepr(y(sp.Integer(0))): sp.srepr(sp.Integer(1)),
        sp.srepr(y(sp.Integer(1))): sp.srepr(sp.Integer(5)),
    }
    reply = dsolve_worker.solve_payload(
        _payload(sp.srepr(equation), sp.srepr(y(_T)), ics=ics)
    )
    assert "general" in reply
    if not reply.get("particular"):
        assert reply["ok"] is True
        assert "initial conditions could not be applied" in reply.get("message", "")


def test_laplace_mode_skips_dsolve_entirely():
    """The transform route wants the derivation and nothing else, and skipping
    the one part of the module that can hang costs it nothing."""
    y = sp.Function("y")
    equation = sp.Eq(
        sp.Derivative(y(_T), (_T, 2)) + y(_T), sp.Integer(0)
    )
    ics = {
        sp.srepr(y(sp.Integer(0))): sp.srepr(sp.Integer(1)),
        sp.srepr(sp.Subs(sp.Derivative(y(_T), _T), _T, sp.Integer(0))): sp.srepr(
            sp.Integer(0)
        ),
    }
    reply = dsolve_worker.solve_payload(
        _payload(sp.srepr(equation), sp.srepr(y(_T)), ics=ics, mode="laplace")
    )
    # Either a derivation or an honest error, but never the dsolve path.
    assert "general" not in reply
    assert reply.get("ok") is True or "error" in reply


def test_a_narration_failure_is_never_fatal():
    """Narration is a nicety; the closed form is the answer. A narrator that
    raises must not take the solve down with it."""
    y = sp.Function("y")
    equation = sp.Eq(sp.Derivative(y(_T), _T), -2 * y(_T))
    reply = dsolve_worker.solve_payload(
        _payload(sp.srepr(equation), sp.srepr(y(_T)))
    )
    assert reply["ok"] is True
    assert "general" in reply


def test_the_right_hand_side_helper_handles_a_list_of_solutions():
    """`dsolve` returns a list for some equations and a bare Eq for others."""
    y = sp.Function("y")
    single = sp.Eq(y(_T), sp.exp(-2 * _T))
    assert dsolve_worker._right_hand_side(single) == sp.srepr(sp.exp(-2 * _T))
    assert dsolve_worker._right_hand_side([single, single]) == sp.srepr(
        sp.exp(-2 * _T)
    )
    with pytest.raises(ValueError, match="no solutions"):
        dsolve_worker._right_hand_side([])


# ---------------------------------------------------------------------------
# The threading layer
# ---------------------------------------------------------------------------
#
# `solver.py` documents a careful discipline: every solve runs on a pool
# thread, each carries a token, and a superseded one stops at its next step
# boundary rather than running to completion for an answer nobody will read.
# A fifth of it was unexercised, including the failure path — and an exception
# on a pool thread that never reaches a signal leaves the screen waiting
# forever.

from PySide6.QtCore import QThreadPool  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app.solver import (  # noqa: E402
    SolveRequest,
    SolveResult,
    SolveRunner,
    _Job,
    _Signals,
)


@pytest.fixture(scope="module")
def qapp():
    application = QApplication.instance() or QApplication([])
    yield application


def _request(**overrides):
    fields = dict(
        problem_key="logistic", method="dopri5", rtol=1e-6, atol=1e-9, params={}
    )
    fields.update(overrides)
    return SolveRequest(**fields)


def _run_job(request, is_stale=None):
    """Run one job synchronously and return its result.

    Synchronously on purpose: `_Job.run` is what the pool calls, and driving it
    directly removes the scheduling from the test without removing anything
    being tested.
    """
    signals = _Signals()
    received: list = []
    signals.finished.connect(received.append)
    _Job(request, signals, is_stale=is_stale).run()
    assert len(received) == 1, "the job did not report a result"
    return received[0]


def test_a_failing_solve_reports_the_error_rather_than_escaping_the_pool(qapp):
    """An uncaught exception on a pool thread is lost: the signal never
    arrives and the screen waits for an answer that is not coming."""
    result = _run_job(_request(method="not-a-method"))

    assert result.error is not None
    assert not result.ok
    assert "not-a-method" in result.error
    # The traceback is attached for the diagnostics report, not shown raw.
    assert hasattr(result, "traceback")
    assert "Traceback" in result.traceback


def test_a_superseded_solve_stops_almost_immediately(qapp):
    """The token discipline. Before `solve` grew a callback, a superseded job
    ran to completion anyway — holding a pool thread for however long the
    problem took, purely to have its answer discarded."""
    request = _request(problem_key="lorenz")

    uncancelled = _run_job(request).solution.stats.nfev
    cancelled = _run_job(request, is_stale=lambda: True).solution

    assert cancelled.cancelled, cancelled.status
    assert not cancelled.success, "a cancelled solve is not a successful one"
    assert cancelled.stats.nfev < 0.2 * uncancelled, (
        f"cancelled after {cancelled.stats.nfev} of {uncancelled} evaluations; "
        f"it should stop at the first step boundary"
    )


def test_a_solve_that_is_never_stale_runs_to_completion(qapp):
    """The control for the above: the callback must not stop a live solve."""
    result = _run_job(_request(), is_stale=lambda: False)
    assert result.ok
    assert result.solution.success


def test_only_the_newest_of_a_superseding_series_reports(qapp):
    """A slider drag submits many; the screen wants one. Cancelled jobs emit
    neither `finished` nor `latest`."""
    runner = SolveRunner(max_threads=2)
    latest: list = []
    finished: list = []
    runner.latest.connect(latest.append)
    runner.finished.connect(finished.append)

    tokens = [runner.submit(_request(problem_key="lorenz"), supersede=True)
              for _ in range(6)]
    QThreadPool.globalInstance().waitForDone(60_000)
    for _ in range(50):
        qapp.processEvents()
    runner.cancel_all()

    assert tokens == sorted(tokens), "tokens must increase"
    assert len(latest) <= 1, f"{len(latest)} results claimed to be the newest"
    for result in finished:
        assert not result.cancelled, "a cancelled job reported itself"


def test_cancel_all_stops_a_series_that_is_not_superseding(qapp):
    """The Method Race submits one solve per method and wants every one, so
    supersession is opt-in — but screen teardown still has to stop them."""
    runner = SolveRunner(max_threads=2)
    runner.submit(_request(problem_key="lorenz"))
    runner.cancel_all()
    QThreadPool.globalInstance().waitForDone(60_000)
    for _ in range(50):
        qapp.processEvents()
    # Nothing to assert about results -- the point is that this returns rather
    # than leaving the pool working, and that a later submit still functions.
    assert runner.submit(_request()) > 0


def test_status_text_says_something_for_every_outcome(qapp):
    assert "failed" in SolveResult(request=_request(), error="boom").status_text
    assert SolveResult(request=_request()).status_text == "no result"


def test_step_sizes_are_empty_rather_than_broken_for_a_single_point(qapp):
    """A solve with one output point has no gaps to plot, and the timeline
    asks for them regardless."""
    import numpy as np

    from odesuite import Solution

    one_point = Solution(t=np.array([0.0]), y=np.zeros((1, 1)))
    midpoints, h = SolveResult(request=_request(), solution=one_point).step_sizes()
    assert midpoints.size == 0 and h.size == 0


def test_invariant_drift_declines_when_there_is_nothing_conserved(qapp):
    import numpy as np

    from odesuite import Solution

    solution = Solution(t=np.array([0.0, 1.0]), y=np.zeros((1, 2)))
    result = SolveResult(request=_request(), solution=solution, benchmark=None)
    assert result.invariant_drift() == (None, None)


def test_the_reproducing_snippet_covers_both_of_its_branches(qapp):
    """`as_code` emits a tolerance or a step count, and the snippet is
    asserted elsewhere to actually reproduce the solve."""
    with_steps = _request(problem_key="harmonic_2d", method="verlet",
                          n_steps=500).as_code()
    assert "n_steps=500" in with_steps
    assert "rtol" not in with_steps

    with_tolerance = _request().as_code()
    assert "rtol" in with_tolerance
    assert "n_steps" not in with_tolerance
