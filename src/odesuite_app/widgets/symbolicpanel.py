"""The closed form, and the working behind it.

Shows what one would write out by hand: the equation, its classification, the
characteristic polynomial and its roots, the basis each root contributes, the
general solution, the particular solution once initial conditions are applied --
and whether substituting the answer back into the equation gives exactly zero.

That last part is why the panel can be confident. A closed form is either right
or it is not, and `symbolic` decides it by substitution rather than by trusting
`dsolve`, so nothing here has to present an unchecked answer as though it were
certain.

`dsolve` runs in a subprocess with a hard timeout because it can hang outright,
so the work happens on the thread pool and lands by signal. Retyping or dragging
a slider supersedes the previous request by token rather than queueing another
twelve-second subprocess behind it.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import symbolic as _symbolic
from ..symbolic import (
    ParsedEquation,
    SymbolicSolution,
    characteristic_analysis,
    describe_roots,
    solve_symbolically,
)
from ..theme import Palette
from .mathlabel import MathBlock, MathLabel

__all__ = ["SymbolicPanel"]


class _Signals(QObject):
    done = Signal(int, object)          # token, SymbolicSolution | Exception


class _SymbolicJob(QRunnable):
    """Runs `solve_symbolically` off the GUI thread."""

    def __init__(self, token: int, parsed: ParsedEquation, timeout: float,
                 signals: _Signals, steps: bool = False) -> None:
        super().__init__()
        self.token = token
        self.parsed = parsed
        self.timeout = timeout
        self.signals = signals
        self.steps = steps
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = solve_symbolically(self.parsed, timeout=self.timeout,
                                        steps=self.steps)
        except Exception as exc:                      # surfaced, never swallowed
            result = exc
        try:
            self.signals.done.emit(self.token, result)
        except RuntimeError:
            pass                                      # the panel went away


class SymbolicPanel(QWidget):
    """Everything the symbolic route found, or a plain account of why it did not."""

    solved = Signal(object)             # SymbolicSolution

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self._token = 0
        self._parsed: ParsedEquation | None = None
        self.solution: SymbolicSolution | None = None
        #: Ask the worker to narrate the derivation too. Off here because only
        #: the Learning Hub displays one, and the Studio should not pay for
        #: work it does not show.
        self.narrate = False

        self._signals = _Signals()
        self._signals.done.connect(self._on_done)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        self._layout = QVBoxLayout(page)
        self._layout.setContentsMargins(22, 18, 22, 22)
        self._layout.setSpacing(14)

        self._status = QLabel("Type an equation to see its closed form.")
        self._status.setProperty("role", "muted")
        self._status.setWordWrap(True)
        self._layout.addWidget(self._status)

        self._body = QVBoxLayout()
        self._body.setSpacing(16)
        self._layout.addLayout(self._body)
        self._layout.addStretch(1)

    # -- requesting ------------------------------------------------------

    def clear(self, message: str = "") -> None:
        self._token += 1                            # abandon anything in flight
        self.solution = None
        self._clear_body()
        self._status.setText(message)
        self._status.setStyleSheet(f"color: {self.palette_obj.text_muted};")

    def preview(self, parsed: ParsedEquation) -> SymbolicSolution:
        """Render what can be known immediately, without `dsolve`.

        The characteristic polynomial and its roots are a local calculation --
        collect the coefficients, factor, read off the basis -- and take well
        under a millisecond. Only the closed form needs the subprocess. Splitting
        them is what lets the root table follow a slider in real time while the
        expensive half is debounced behind it.
        """
        self._parsed = parsed
        analysis = characteristic_analysis(parsed)
        partial = SymbolicSolution(
            order=parsed.order,
            linear=analysis["linear"],
            homogeneous=analysis["homogeneous"],
            constant_coefficients=analysis["constant_coefficients"],
            roots=analysis["roots"],
            characteristic_poly=analysis["poly"],
            fundamental_set=analysis["fundamental_set"],
        )
        self.solution = partial
        self._render(partial)
        self._status.setVisible(True)
        self._status.setStyleSheet(f"color: {self.palette_obj.text_muted};")
        self._status.setText("finding the closed form…")
        return partial

    def solve_for(self, parsed: ParsedEquation,
                  timeout: float | None = None) -> int:
        """Start a symbolic solve. Returns its token."""
        timeout = _symbolic.DSOLVE_TIMEOUT if timeout is None else timeout
        self._parsed = parsed
        self._token += 1
        self._clear_body()
        self._status.setStyleSheet(f"color: {self.palette_obj.text_muted};")
        self._status.setText(
            f"solving symbolically… (up to {timeout:g} s — some equations have "
            f"no closed form, and sympy cannot always tell quickly)"
        )
        QThreadPool.globalInstance().start(
            _SymbolicJob(self._token, parsed, timeout, self._signals,
                         steps=self.narrate)
        )
        return self._token

    def _on_done(self, token: int, result) -> None:
        if token != self._token:
            return                                  # superseded
        if isinstance(result, Exception):
            self._status.setStyleSheet(f"color: {self.palette_obj.danger};")
            self._status.setText(f"{type(result).__name__}: {result}")
            return
        self.solution = result
        self._render(result)
        self.solved.emit(result)

    # -- rendering -------------------------------------------------------

    def _render(self, solution: SymbolicSolution) -> None:
        palette = self.palette_obj
        self._clear_body()

        if solution.timed_out:
            self._status.setStyleSheet(f"color: {palette.warning};")
            self._status.setText(
                "No closed form found within the time limit. That is not a "
                "failure of the equation — sympy hangs outright on some inputs "
                "(y′ = sin y, the pendulum), which is why this runs under a "
                "timeout. The numeric solution is exact enough to work with."
            )
        elif not solution.solved:
            reason = solution.message or "sympy has no method for this equation"
            self._status.setStyleSheet(f"color: {palette.text_muted};")
            self._status.setText(
                f"No closed form: {reason}. Most equations have none — that is "
                f"the reason numerical methods exist. The Trajectory tab still "
                f"has the answer."
            )
        else:
            self._status.setStyleSheet(f"color: {palette.text_muted};")
            self._status.setText(solution.message or "")
            self._status.setVisible(bool(solution.message))

        self._render_classification(solution)
        if solution.characteristic_poly is not None:
            self._render_characteristic(solution)
        if solution.general is not None:
            self._section("General solution", solution.general, lead="y(t) =")
        if solution.particular is not None:
            self._section(
                "Particular solution — with your initial conditions",
                solution.particular, lead="y(t) =",
            )
            self._render_interval(solution)
        if solution.solved:
            self._render_verification(solution)

    def _render_interval(self, solution: SymbolicSolution) -> None:
        """Where the particular solution is actually defined.

        Only for the particular solution, and only when it is bounded: the
        general solution carries an arbitrary constant, so where it breaks down
        depends on which constant, and the interval is a property of the
        solution through a *point*. Where nothing can be settled, or the answer
        is the whole line, nothing is shown -- an interval printed on every
        answer would stop being read.
        """
        from ..symbolic import format_interval, interval_of_validity

        t0 = solution.initial_point
        if t0 is None:
            return          # without the point the interval is not defined
        expression = solution.particular
        if isinstance(expression, list):
            return          # a system: each component has its own, not one line
        text = format_interval(interval_of_validity(expression, t0))
        if not text:
            return
        label = QLabel(
            f"valid on {text} — the solution runs into a singularity at the "
            f"edge of this interval, and means nothing beyond it"
        )
        label.setWordWrap(True)
        label.setStyleSheet(
            f"font-size: 10.5px; color: {self.palette_obj.warning};"
        )
        self._body.addWidget(label)

    def _render_classification(self, solution: SymbolicSolution) -> None:
        words = []
        if solution.order:
            words.append(f"order {solution.order}")
        words.append("linear" if solution.linear else "nonlinear")
        if solution.linear:
            words.append("homogeneous" if solution.homogeneous else "forced")
            words.append(
                "constant coefficients" if solution.constant_coefficients
                else "variable coefficients"
            )
        text = " · ".join(words)
        if solution.classification:
            text += f"   ({solution.classification.replace('_', ' ')})"

        label = QLabel(text)
        label.setProperty("role", "muted")
        label.setWordWrap(True)
        self._body.addWidget(label)

    def _render_characteristic(self, solution: SymbolicSolution) -> None:
        import sympy as sp

        palette = self.palette_obj
        frame, layout = self._card("Characteristic equation")

        equation = sp.Eq(solution.characteristic_poly, 0)
        layout.addWidget(MathLabel(palette, equation, point_size=16))

        summary = describe_roots(solution.roots, solution.order)
        if summary:
            note = QLabel(summary)
            note.setProperty("role", "muted")
            note.setWordWrap(True)
            self._style_muted(note)
            layout.addWidget(note)

        if solution.roots:
            grid = QGridLayout()
            grid.setHorizontalSpacing(18)
            grid.setVerticalSpacing(6)
            for column, title in enumerate(("root", "multiplicity", "contributes")):
                head = QLabel(title)
                head.setProperty("role", "muted")
                head.setStyleSheet("background: transparent; font-size: 10.5px;")
                grid.addWidget(head, 0, column)

            for row, (root, multiplicity, paired) in enumerate(
                _root_rows(solution.roots), start=1
            ):
                grid.addWidget(
                    MathLabel(palette, sp.nsimplify(root), point_size=14), row, 0
                )
                pieces = []
                if multiplicity > 1:
                    pieces.append(f"×{multiplicity}")
                if paired:
                    pieces.append("with its conjugate")
                count = QLabel(", ".join(pieces) or "—")
                count.setProperty("role", "muted")
                self._style_muted(count)
                grid.addWidget(count, row, 1)
                grid.addWidget(
                    MathBlock(palette, _contribution(root, multiplicity),
                              point_size=14),
                    row, 2,
                )
            grid.setColumnStretch(2, 1)
            layout.addLayout(grid)

        if solution.fundamental_set:
            caption = QLabel(
                "Together these span every solution of the homogeneous equation."
            )
            caption.setProperty("role", "muted")
            caption.setWordWrap(True)
            self._style_muted(caption)
            layout.addWidget(caption)
        self._body.addWidget(frame)

    def _render_verification(self, solution: SymbolicSolution) -> None:
        palette = self.palette_obj
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if solution.verified is True:
            colour, text = palette.success, (
                "verified — substituting this back into the equation simplifies "
                "to exactly 0"
            )
        elif solution.verified is False:
            colour, text = palette.danger, (
                "not verified — substituting it back did not simplify to zero"
            )
        else:
            colour, text = palette.text_muted, (
                "not checked — the substitution could not be simplified"
            )

        badge = QLabel("✓" if solution.verified else "•")
        badge.setStyleSheet(
            f"background: transparent; color: {colour}; font-size: 15px; "
            f"font-weight: 700;"
        )
        layout.addWidget(badge)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"background: transparent; color: {colour};")
        layout.addWidget(label, 1)
        self._body.addWidget(row)

    # -- helpers ---------------------------------------------------------

    def _section(self, title: str, expression, lead: str = "") -> None:
        frame, layout = self._card(title)
        layout.addWidget(MathBlock(self.palette_obj, expression, lead=lead,
                                   point_size=16))
        self._body.addWidget(frame)

    def _card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 13, 16, 15)
        layout.setSpacing(9)
        heading = QLabel(title)
        heading.setProperty("role", "heading")
        layout.addWidget(heading)
        return frame, layout

    def _style_muted(self, label: QLabel) -> None:
        label.setStyleSheet("background: transparent; font-size: 11.5px;")

    def _clear_body(self) -> None:
        self._status.setVisible(True)
        while self._body.count():
            item = self._body.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout() is not None:
                _drop(item.layout())

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
        if self.solution is not None:
            self._render(self.solution)


def _root_rows(roots: list) -> list[tuple]:
    """Merge conjugate pairs into one row.

    `characteristic_analysis` reports both members of a complex pair, which is
    correct -- they are both roots. Listing them separately in a table is not:
    each would claim the *same* pair of real basis functions, so the reader
    would count `e^{at}cos bt` twice and conclude the solution space is twice
    the size it is. Returns ``(root, multiplicity, is_conjugate_pair)``.
    """
    import sympy as sp

    rows: list[tuple] = []
    seen: set = set()
    for root, multiplicity in roots:
        imaginary = sp.im(root)
        if imaginary == 0:
            rows.append((root, multiplicity, False))
            continue
        key = (sp.simplify(sp.re(root)), sp.simplify(abs(imaginary)))
        if key in seen:
            continue
        seen.add(key)
        # Show the member with the positive imaginary part; "± b i" is how it
        # would be written by hand.
        principal = root if imaginary > 0 else sp.conjugate(root)
        rows.append((principal, multiplicity, True))
    return rows


def _contribution(root, multiplicity: int) -> list:
    """The basis functions one root contributes, as a course would write them.

    A real root gives ``e^{rt}`` with an extra factor of `t` per repetition; a
    complex pair gives ``e^{at}cos(bt)`` and ``e^{at}sin(bt)`` -- listed once for
    the pair, not once for each conjugate, since the two together span the same
    real two-dimensional space.
    """
    import sympy as sp

    t = sp.Symbol("t", real=True)
    real, imaginary = sp.nsimplify(sp.re(root)), sp.nsimplify(sp.im(root))
    out = []
    for k in range(multiplicity):
        prefix = t**k if k else sp.Integer(1)
        if imaginary == 0:
            out.append(prefix * sp.exp(real * t))
        else:
            magnitude = abs(imaginary)
            out.append(prefix * sp.exp(real * t) * sp.cos(magnitude * t))
            out.append(prefix * sp.exp(real * t) * sp.sin(magnitude * t))
    return out


def _drop(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _drop(item.layout())
