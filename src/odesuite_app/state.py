"""Session state: the single source of truth the screens read from.

A deliberate view-model layer. Screens never talk to `odesuite` directly and
never hold their own copy of "which problem, which method, which tolerance" --
they mutate this object and react to its signals. Two consequences worth the
indirection:

* Switching screens preserves context. Choose Van der Pol at mu=800 in the Lab,
  jump to the Stiffness Explorer, and it is already looking at the same system.
* Nothing here imports a Qt widget, so the whole application state is testable
  headlessly and a different front end could be built over it unchanged.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from odesuite.steppers import EXPLICIT_METHODS, IMPLICIT_METHODS, SPECIAL_METHODS

from . import catalog
from .catalog import CatalogEntry
from .solver import SolveRequest, SolveRunner

__all__ = ["SessionState", "METHOD_GROUPS", "methods_for"]


#: Methods grouped for the picker, in the order they should appear.
METHOD_GROUPS: dict[str, list[str]] = {
    "Explicit Runge–Kutta": ["rk23", "rkf45", "cashkarp", "dopri5", "tsit5"],
    "Stiff": ["rodas4", "radau"],
    "Taylor series": ["taylor8", "taylor20", "taylor30"],
    "Symplectic": ["verlet", "yoshida4", "yoshida6"],
    "Exponential": ["etdrk4"],
}

#: Methods that need a constant step size rather than a tolerance.
FIXED_STEP = {"verlet", "yoshida4", "yoshida6", "yoshida8", "etdrk4"}

#: Methods each problem class can actually run. Offering a method that will
#: raise on selection is worse than not offering it.
_REQUIRES = {
    "verlet": "separable",
    "yoshida4": "separable",
    "yoshida6": "separable",
    "yoshida8": "separable",
    "etdrk4": "semilinear",
}


def methods_for(entry: CatalogEntry) -> dict[str, list[str]]:
    """The method groups applicable to `entry`, with impossible ones removed."""
    tags = set(entry.tags)
    groups: dict[str, list[str]] = {}
    for group, names in METHOD_GROUPS.items():
        usable = []
        for name in names:
            requirement = _REQUIRES.get(name)
            if requirement and requirement not in tags:
                continue
            # A mass matrix or a DAE rules out every explicit method.
            if ("dae" in tags or "mass" in tags) and name in EXPLICIT_METHODS:
                continue
            # Taylor needs a jet-expressible right-hand side and a non-stiff
            # problem; `supports_taylor` records which entries have both.
            if name.startswith("taylor") and not entry.supports_taylor:
                continue
            usable.append(name)
        if usable:
            groups[group] = usable
    return groups


class SessionState(QObject):
    """Current problem, method, tolerances and last result."""

    problem_changed = Signal(str)          # key
    method_changed = Signal(str)
    tolerance_changed = Signal(float, float)
    params_changed = Signal(dict)
    result_changed = Signal(object)        # SolveResult
    busy_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.runner = SolveRunner(self)
        self.runner.latest.connect(self._on_result)
        self.runner.started.connect(lambda _: self.busy_changed.emit(True))

        self._key = "van_der_pol"
        entry = catalog.get(self._key)
        self._method = entry.default_method
        self._rtol = entry.default_rtol
        self._atol = entry.default_rtol * 1e-3
        self._params = entry.defaults()
        self._n_steps = 2000
        self.result = None

    # -- accessors -------------------------------------------------------

    @property
    def entry(self) -> CatalogEntry:
        return catalog.get(self._key)

    @property
    def problem_key(self) -> str:
        return self._key

    @property
    def method(self) -> str:
        return self._method

    @property
    def rtol(self) -> float:
        return self._rtol

    @property
    def atol(self) -> float:
        return self._atol

    @property
    def params(self) -> dict:
        return dict(self._params)

    @property
    def n_steps(self) -> int:
        return self._n_steps

    @property
    def uses_fixed_step(self) -> bool:
        return self._method in FIXED_STEP

    # -- mutators --------------------------------------------------------

    def set_problem(self, key: str, *, resolve: bool = True,
                    force: bool = False) -> None:
        """Select a problem by key.

        `force` re-reads the entry even when the key has not changed. The user's
        typed equation always lives under the same reserved key, so editing it
        would otherwise be a no-op: the key matches, the early return fires, and
        the screen goes on showing the previous equation's solution.
        """
        if key == self._key and not force:
            return
        self._key = key
        entry = self.entry
        self._params = entry.defaults()
        self._rtol = entry.default_rtol
        self._atol = entry.default_rtol * 1e-3
        # Keep the current method if the new problem supports it; otherwise
        # fall back to the problem's own default rather than erroring later.
        available = {m for names in methods_for(entry).values() for m in names}
        if self._method not in available:
            self._method = entry.default_method
            self.method_changed.emit(self._method)
        self.problem_changed.emit(key)
        self.params_changed.emit(self.params)
        if resolve:
            self.resolve()

    def set_method(self, method: str, *, resolve: bool = True) -> None:
        if method == self._method:
            return
        self._method = method
        self.method_changed.emit(method)
        if resolve:
            self.resolve()

    def set_tolerances(self, rtol: float, atol: float, *, resolve: bool = True) -> None:
        self._rtol, self._atol = float(rtol), float(atol)
        self.tolerance_changed.emit(self._rtol, self._atol)
        if resolve:
            self.resolve()

    def set_param(self, name: str, value: float, *, resolve: bool = True) -> None:
        if self._params.get(name) == value:
            return
        self._params[name] = float(value)
        self.params_changed.emit(self.params)
        if resolve:
            self.resolve()

    def set_n_steps(self, n: int, *, resolve: bool = True) -> None:
        self._n_steps = max(1, int(n))
        if resolve:
            self.resolve()

    def reset_params(self) -> None:
        self._params = self.entry.defaults()
        self.params_changed.emit(self.params)
        self.resolve()

    # -- solving ---------------------------------------------------------

    def request(self, **overrides) -> SolveRequest:
        """The `SolveRequest` describing the current state."""
        base = dict(
            problem_key=self._key,
            method=self._method,
            rtol=self._rtol,
            atol=self._atol,
            params=self.params,
            n_steps=self._n_steps if self.uses_fixed_step else None,
        )
        base.update(overrides)
        return SolveRequest(**base)

    def resolve(self) -> int:
        """Kick off a solve for the current state. Returns its token."""
        return self.runner.submit(self.request())

    def _on_result(self, result) -> None:
        self.result = result
        self.busy_changed.emit(False)
        self.result_changed.emit(result)
