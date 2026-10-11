"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

__all__ = ["main", "opening_screen"]

#: Modules that only the `[app]` extra provides.
_APP_EXTRA_MODULES = ("PySide6", "shiboken6", "pyqtgraph")

_APP_EXTRA_MESSAGE = (
    "this needs the interface, which is an optional extra:\n"
    "    pip install odesuite[app]\n"
    "The library itself, and `--list-problems` and `--selftest`, work without it."
)


def _is_missing_app_extra(exc: ImportError) -> bool:
    """True when `exc` is Qt (or pyqtgraph) being absent, not some other failure.

    Checked by module name rather than by catching ImportError broadly: a typo
    inside the interface code raises ImportError too, and reporting that as
    "install the app extra" would send someone off to reinstall a package they
    already have.
    """
    name = exc.name or ""
    return name.split(".")[0] in _APP_EXTRA_MODULES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odesuite-gui", description="odesuite ODE solver studio"
    )
    parser.add_argument(
        "--theme", choices=("dark", "light"), default="dark",
        help="colour theme (default: dark)",
    )
    parser.add_argument(
        "--problem", default=None,
        help="open a problem by key and jump straight to the Solver Lab",
    )
    parser.add_argument(
        "--screen", default=None,
        help="open on a specific screen. Learning Hub: course, lessons, quiz, "
             "glossary, steps, laplace, byhand, worked, print. Solver Studio: "
             "lab, portrait, stiffness, race, accuracy. Or home.",
    )
    parser.add_argument(
        "--rebuild-thumbnails", action="store_true",
        help="regenerate the home-screen previews and exit",
    )
    parser.add_argument(
        "--session", default=None, metavar="FILE",
        help="open a saved session: the problem, method, tolerances, parameter "
             "values and screen it was written with. An explicit --problem or "
             "--screen still wins. Unreadable files are reported and skipped.",
    )
    parser.add_argument(
        "--list-problems", action="store_true", help="print the catalogue and exit"
    )
    parser.add_argument(
        "--dsolve-worker", action="store_true",
        help=argparse.SUPPRESS,     # internal: the killable symbolic solver
    )
    parser.add_argument(
        "--selftest", metavar="REPORT", nargs="?", const="-",
        help="solve a few problems, write a report, and exit non-zero on "
             "failure. Intended for checking a packaged build, where a "
             "windowed executable has no console to print to.",
    )
    return parser


def opening_screen(window) -> str:
    """Where a launch with no --screen, --problem or --session opens.

    Where it was last closed, with what was open, if that is known. Otherwise
    this is a first launch, and a student's first screen is the Course Map:
    what the course is, how far through it they are, and a Continue button.
    Home, the old default, is a page of links to fourteen screens, and asks a
    newcomer to choose before they know what any of them is.
    """
    return window.restore_session() or window.remembered_screen() or "course"


def selftest(report_path: str | None = None) -> int:
    """Exercise the library and the catalogue end to end.

    The check that matters for a frozen build. A GUI executable on Windows has
    no stdout, so the exit code is the result and the optional report file is
    the detail.
    """
    import numpy as np

    from odesuite import solve

    from . import catalog
    from .custom import EXAMPLES, build

    lines: list[str] = []
    failures = 0

    checks = [
        ("lotka_volterra", "dopri5", {}),
        ("robertson", "radau", {"log_t_end": 8.0}),
        ("kepler_symplectic", "verlet", {"n_orbits": 5.0}),
        ("allen_cahn", "etdrk4", {"n_modes": 32.0, "t_end": 2.0}),
        ("pendulum", "taylor20", {"t_end": 10.0}),
    ]
    for key, method, overrides in checks:
        entry = catalog.get(key)
        params = {**entry.defaults(), **overrides}
        try:
            bench = entry.build(params)
            kwargs = (
                {"n_steps": 2000}
                if method in ("verlet", "yoshida4", "etdrk4")
                else {"rtol": 1e-8, "atol": 1e-10, "max_steps": 200_000}
            )
            solution = solve(bench.problem, method=method, **kwargs)
            ok = solution.success and np.all(np.isfinite(solution.y[:, -1]))
            lines.append(
                f"{'PASS' if ok else 'FAIL'}  {key:22s} {method:9s} "
                f"steps={solution.stats.naccepted}"
            )
            failures += not ok
        except Exception as exc:
            lines.append(f"FAIL  {key:22s} {method:9s} {type(exc).__name__}: {exc}")
            failures += 1

    for name, spec in EXAMPLES.items():
        try:
            system = build(spec)
            solution = solve(system.problem, method="radau", rtol=1e-7, atol=1e-10,
                             max_steps=200_000)
            ok = solution.success
            lines.append(f"{'PASS' if ok else 'FAIL'}  custom: {name}")
            failures += not ok
        except Exception as exc:
            lines.append(f"FAIL  custom: {name}: {type(exc).__name__}: {exc}")
            failures += 1

    # Typesetting depends on font files inside matplotlib's `mpl-data`, which
    # arrive in a frozen build only as bundled data -- nothing imports them, so
    # a packaging change could drop them and no test run from source would
    # notice. Checking here means the exit code covers it.
    try:
        import sympy as sp

        from . import mathrender

        symbol = sp.Symbol("t", real=True)
        expression = sp.exp(-symbol) * sp.cos(2 * symbol)
        data = mathrender.latex_to_png(sp.latex(expression), "#E6EDF3", 15.0, 110.0)
        ok = data.startswith(b"\x89PNG") and len(data) > 200
        lines.append(
            f"{'PASS' if ok else 'FAIL'}  typesetting: mathtext + Computer Modern"
            f" ({len(data)} bytes)"
        )
        failures += not ok
    except Exception as exc:
        lines.append(f"FAIL  typesetting: {type(exc).__name__}: {exc}")
        failures += 1

    lines.append(f"{len(lines) - failures}/{len(lines)} passed")
    text = "\n".join(lines)
    if report_path and report_path != "-":
        from pathlib import Path

        Path(report_path).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.dsolve_worker:
        from .dsolve_worker import run

        return run()

    if args.selftest:
        return selftest(args.selftest)

    if args.list_problems:
        from . import catalog

        width = max(len(k) for k in catalog.keys())
        for key in catalog.keys():
            entry = catalog.get(key)
            print(f"  {key:<{width}}  {entry.title:<26} [{', '.join(entry.tags)}]")
        return 0

    if args.rebuild_thumbnails:
        try:
            from . import thumbnails
            from .theme import PALETTES
        except ImportError as exc:
            if not _is_missing_app_extra(exc):
                raise
            print(_APP_EXTRA_MESSAGE, file=sys.stderr)
            return 1

        def report(done: int, total: int, key: str) -> None:
            print(f"  [{done:>2}/{total}] {key}")

        for name in ("dark", "light"):
            print(f"{name} theme:")
            thumbnails.ensure_all(PALETTES[name], force=True, progress=report)
        print(f"\nwritten to {thumbnails.cache_dir()}")
        return 0

    try:
        from .app import build_application
    except ImportError as exc:
        if not _is_missing_app_extra(exc):
            raise
        print(_APP_EXTRA_MESSAGE, file=sys.stderr)
        return 1

    app, window = build_application(args.theme)

    # A named session is applied first, so an explicit --problem or --screen on
    # the same command line still overrides it: the more specific instruction
    # wins, which is the rule the next two branches already follow.
    if args.session:
        from . import session as session_file

        stored = session_file.load(args.session)
        if stored is None:
            print(
                f"could not read a session from {args.session}; starting fresh",
                file=sys.stderr,
            )
        else:
            restored_screen = session_file.apply(window.state, stored)
            window.go(restored_screen or "lab")

    if args.problem:
        window.state.set_problem(args.problem)
        window.go("lab")
    if args.screen:
        window.go(args.screen)
    elif not args.problem and not args.session:
        # Reopen where it was last closed, and with what was open. An explicit
        # --screen, --problem or --session wins, because someone who named one
        # means it.
        window.go(opening_screen(window))
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
