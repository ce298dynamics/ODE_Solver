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


def solve_payload(payload: dict) -> dict:
    """Do the symbolic work described by `payload` and return a plain-dict reply."""
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
    if len(equations) == 1:
        try:
            hints = sp.classify_ode(equations[0], functions[0])
            reply["classification"] = hints[0] if hints else ""
        except Exception:
            reply["classification"] = ""

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

    try:
        reply = solve_payload(payload)
    except Exception as exc:                              # never crash silently
        reply = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    print(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(run())
