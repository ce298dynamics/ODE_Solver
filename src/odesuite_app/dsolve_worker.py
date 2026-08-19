"""The subprocess that runs `sympy.dsolve`.

Separate process rather than a thread, for one reason: `dsolve` can hang. Not
take a long time -- hang. ``y' = sin(y)`` and ``y'' + sin(y) = 0`` never return,
and a Python thread cannot be killed from outside, so the only way to impose a
time limit is to own a process and terminate it.

Communication is JSON over stdin/stdout carrying `sympy.srepr` strings, which
round-trip exactly and, unlike pickle, cannot execute anything on the way back.

Invoked through the ordinary CLI (``--dsolve-worker``) so it works identically
from source and inside a frozen build, where ``sys.executable`` is the
application rather than an interpreter.
"""

from __future__ import annotations

import json
import sys

__all__ = ["run", "solve_payload"]


def derivation_reply(equation, function, ics: dict) -> dict | None:
    """`steps.derive` reduced to plain JSON-able data, or None if nothing applies."""
    import sympy as sp

    from .steps import derive

    hints = sp.classify_ode(equation, function)
    derivation = derive(equation, function.func, hints=hints, ics=ics)
    if derivation is None:
        return None
    return {
        "technique": derivation.technique,
        "title": derivation.title,
        "message": derivation.message,
        "verified": derivation.verified,
        "result": None if derivation.result is None else sp.srepr(derivation.result),
        "steps": [
            {"title": s.title, "latex": s.latex, "note": s.note,
             "verified": s.verified}
            for s in derivation.steps
        ],
    }


def solve_payload(payload: dict, emit=None) -> dict:
    """Do the symbolic work described by `payload` and return a plain-dict reply.

    `emit`, when given, is called with the reply as soon as the classification
    and any derivation are ready and **before** `dsolve` is attempted. That
    ordering is deliberate: `dsolve` is the part that hangs, and a derivation
    already computed should not die with it. ``y' = sin(y)`` is the case that
    motivates it -- `dsolve` never returns, while separation of variables
    solves it in a few seconds.
    """
    import sympy as sp

    equations = [sp.sympify(text) for text in payload["equations"]]
    functions = [sp.sympify(text) for text in payload["functions"]]
    ics = {
        sp.sympify(key): sp.sympify(value)
        for key, value in payload.get("ics", {}).items()
    }

    reply: dict = {"ok": False}

    # Classification first: it is fast, it is useful even when no closed form
    # comes out, and it is what tells the user *why* their equation is easy or
    # hard.
    #
    # The whole tuple is returned, not just its head. `classify_ode` orders
    # hints by what sympy would rather solve with, which is not the order a
    # course teaches: `y'' + 3y' + 2y = 0` leads with `factorable` and
    # `y' + 2y = t` with `1st_exact`. Choosing among them is the caller's job
    # (`symbolic.preferred_hint`), and it cannot choose from one string.
    if len(equations) == 1:
        try:
            hints = sp.classify_ode(equations[0], functions[0])
            reply["hints"] = [h for h in hints if not h.endswith("_Integral")]
            reply["classification"] = hints[0] if hints else ""
        except Exception:
            reply["hints"] = []
            reply["classification"] = ""

    # Published in two stages, cheapest first. Classification takes
    # milliseconds and narration can take seconds, so emitting only once -- at
    # the end of both -- meant that asking for steps could lose the
    # classification a caller would otherwise have kept when the timeout fired.
    if emit is not None:
        emit(dict(reply, partial=True))

    if payload.get("steps") and len(equations) == 1:
        try:
            reply["derivation"] = derivation_reply(equations[0], functions[0], ics)
        except Exception as exc:                  # narration is never fatal
            reply["derivation"] = None
            reply["derivation_error"] = f"{type(exc).__name__}: {exc}"
        if emit is not None:
            emit(dict(reply, partial=True))

    try:
        if len(equations) == 1:
            general = sp.dsolve(equations[0], functions[0])
            reply["general"] = sp.srepr(general.rhs)
            if ics:
                particular = sp.dsolve(equations[0], functions[0], ics=ics)
                reply["particular"] = sp.srepr(particular.rhs)
        else:
            general = sp.dsolve(equations)
            reply["general"] = [sp.srepr(item.rhs) for item in general]
            if ics:
                particular = sp.dsolve(equations, ics=ics)
                reply["particular"] = [sp.srepr(item.rhs) for item in particular]
        reply["ok"] = True
    except NotImplementedError:
        reply["error"] = "sympy has no method for this equation"
    except Exception as exc:
        # An initial-value problem can fail where the general solution
        # succeeded -- inconsistent or insufficient conditions. Keep whatever
        # was obtained rather than discarding it.
        if "general" in reply:
            reply["ok"] = True
            reply["message"] = (
                f"general solution found, but the initial conditions could not "
                f"be applied ({type(exc).__name__})"
            )
        else:
            reply["error"] = f"{type(exc).__name__}: {exc}"
    return reply


def run() -> int:
    """Read one request from stdin, write one reply to stdout."""
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"bad request: {exc}"}))
        return 1

    def emit(partial: dict) -> None:
        """Publish what is already known, in case `dsolve` never returns.

        Flushed immediately: the parent reads this back out of the killed
        process's captured output when the timeout fires.
        """
        print(json.dumps(partial), flush=True)

    try:
        reply = solve_payload(payload, emit=emit)
    except Exception as exc:                              # never crash silently
        reply = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    print(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(run())
