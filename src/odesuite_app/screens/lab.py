"""Solver Lab: the main working screen.

    ┌──────────┬─────────────────────────────┬──────────┐
    │ source   │ [Trajectory] [Symbolic]     │  work    │
    │ problem  │                             │  counters│
    │  or your │        trajectory           │          │
    │  equation│         or closed form      │          │
    │ method   │                             │          │
    │ sliders  │                             │          │
    ├──────────┴─────────────────────────────┴──────────┤
    │  step size h(t)                                    │
    └────────────────────────────────────────────────────┘

Two sources, one screen. A problem from the catalogue, or an equation typed in.
The typed one is registered as a catalogue entry of its own
(`equationmodel.build_entry`), which is what lets everything downstream stay
exactly as it was: the method picker, the sliders, the plot, the statistics and
the step timeline never learn that this problem was written by hand, and neither
do the other screens, so a typed equation can be taken straight to the phase
portrait or the method race.

Everything reads from `SessionState`, so the problem and method chosen here are
still selected on every other screen.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import analysis, catalog, theme
from ..custom import ParseError
from ..equationmodel import build_entry
from ..state import SessionState, methods_for
from ..symbolic import with_parameters
from ..theme import Palette
from ..widgets.controls import (
    MethodPicker,
    ParameterPanel,
    TolerancePanel,
    add_heading,
    control_panel,
)
from ..widgets.equationeditor import EquationEditor
from ..widgets.plotpanel import PlotPanel
from ..widgets.stats import StatsPanel
from ..widgets.steptimeline import StepTimeline
from ..widgets.symbolicpanel import SymbolicPanel

__all__ = ["LabScreen"]

#: How long to wait after the last slider movement before asking for a closed
#: form. `dsolve` runs in a subprocess and may take seconds; the root table
#: updates immediately regardless, so the delay costs nothing visible.
_DSOLVE_DEBOUNCE_MS = 450


def _make_entry(spec, ranges, method: str):
    """Parse a typed equation into a catalogue entry, keeping the method if usable."""
    from ..symbolic import parse_equation

    parsed = parse_equation(spec)
    entry = build_entry(parsed, ranges, method=method)
    # The chosen method may not apply to the new equation -- a symplectic
    # integrator needs a separable Hamiltonian, which a typed equation is not
    # declared to be. `methods_for` decides; fall back to the entry's default.
    available = {name for names in methods_for(entry).values() for name in names}
    if method not in available:
        entry = build_entry(parsed, ranges)
    return entry, parsed


class LabScreen(QWidget):
    def __init__(self, state: SessionState, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._parsed = None                 # the typed equation, once parsed
        self._catalog_key = state.problem_key

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        body = QHBoxLayout()
        body.setSpacing(10)
        body.addWidget(self._build_controls())

        centre = QVBoxLayout()
        centre.setSpacing(10)

        self.tabs = QTabWidget()
        self.plot = PlotPanel(palette)
        self.tabs.addTab(self.plot, "Trajectory")
        self.symbolic = SymbolicPanel(palette)
        self.tabs.addTab(self.symbolic, "Symbolic")
        centre.addWidget(self.tabs, 1)

        self.timeline = StepTimeline(palette)
        centre.addWidget(self.timeline)
        body.addLayout(centre, 1)

        self.stats = StatsPanel(palette)
        body.addWidget(self.stats)
        outer.addLayout(body, 1)

        # A closed form costs a subprocess, so it waits until the slider stops.
        self._dsolve_timer = QTimer(self)
        self._dsolve_timer.setSingleShot(True)
        self._dsolve_timer.setInterval(_DSOLVE_DEBOUNCE_MS)
        self._dsolve_timer.timeout.connect(self._request_closed_form)

        # -- wiring ------------------------------------------------------
        state.result_changed.connect(self._on_result)
        state.busy_changed.connect(self._on_busy)
        state.problem_changed.connect(lambda _: self.sync())
        state.method_changed.connect(lambda _: self._sync_method_dependent())
        state.params_changed.connect(self._on_params_changed)
        self.plot.view_changed.connect(lambda _: self._replot())

        self.sync()
        self._sync_source_ui()
        if state.result is None:
            state.resolve()
        else:
            self._on_result(state.result)

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(258)

        add_heading(layout, "Problem")

        # -- source switch -----------------------------------------------
        source = QHBoxLayout()
        source.setSpacing(4)
        self.source_buttons = QButtonGroup(self)
        self.source_buttons.setExclusive(True)
        for index, (label, tip) in enumerate([
            ("Catalogue", "One of the problems this application ships with"),
            ("Your equation", "Type a differential equation and solve it"),
        ]):
            button = QPushButton(label)
            button.setProperty("role", "chip")
            button.setCheckable(True)
            button.setChecked(index == 0)
            button.setToolTip(tip)
            self.source_buttons.addButton(button, index)
            source.addWidget(button)
        source.addStretch(1)
        self.source_buttons.idClicked.connect(self._on_source_changed)
        layout.addLayout(source)

        # -- the two sources, one at a time -------------------------------
        self.source_stack = QStackedWidget()

        catalogue_page = QWidget()
        catalogue_layout = QVBoxLayout(catalogue_page)
        catalogue_layout.setContentsMargins(0, 0, 0, 0)
        catalogue_layout.setSpacing(6)

        self.problem_picker = QComboBox()
        for key in catalog.keys():
            self.problem_picker.addItem(catalog.get(key).title, key)
        self.problem_picker.currentIndexChanged.connect(self._on_problem_picked)
        catalogue_layout.addWidget(self.problem_picker)

        self.blurb = QLabel("")
        self.blurb.setWordWrap(True)
        self.blurb.setProperty("role", "muted")
        self.blurb.setStyleSheet(theme.scaled("font-size: 11px;"))
        catalogue_layout.addWidget(self.blurb)

        #: Shown only when the solve cannot be trusted to be the whole answer:
        #: uniqueness not guaranteed at the initial point, or event crossings
        #: known to have been missed. Hidden the rest of the time, which is
        #: almost always, so that its appearing means something.
        self.caution = QLabel("")
        self.caution.setWordWrap(True)
        self.caution.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        self.caution.hide()
        catalogue_layout.addWidget(self.caution)
        self.source_stack.addWidget(catalogue_page)

        self.editor = EquationEditor(self.palette_obj)
        self.editor.submitted.connect(self._on_equation_submitted)
        self.editor.failed.connect(self._on_equation_failed)
        self.source_stack.addWidget(self.editor)

        layout.addWidget(self.source_stack)

        add_heading(layout, "Method", space_above=6)

        self.method_picker = MethodPicker()
        self.method_picker.method_chosen.connect(self.state.set_method)
        layout.addWidget(self.method_picker)

        self.method_note = QLabel("")
        self.method_note.setWordWrap(True)
        self.method_note.setProperty("role", "muted")
        self.method_note.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        layout.addWidget(self.method_note)

        add_heading(layout, "Accuracy", space_above=6)

        self.tolerances = TolerancePanel()
        self.tolerances.tolerances_changed.connect(self.state.set_tolerances)
        self.tolerances.steps_changed.connect(self.state.set_n_steps)
        layout.addWidget(self.tolerances)

        add_heading(layout, "Parameters", space_above=6)

        self.parameters = ParameterPanel()
        self.parameters.changed.connect(self.state.set_param)
        layout.addWidget(self.parameters)

        layout.addSpacing(10)
        for label, slot, tip in [
            ("Reset parameters", self.state.reset_params,
             "Restore this problem's defaults"),
            ("Copy as code", self._copy_code,
             "Copy the odesuite snippet that reproduces exactly this solve"),
            ("Export solution…", self._export_csv,
             "Save t and y as CSV"),
            ("Save plot…", self._export_png, "Save the trajectory as a PNG"),
        ]:
            button = QPushButton(label)
            button.setToolTip(tip)
            button.clicked.connect(slot)
            layout.addWidget(button)

        self.toast = QLabel("")
        self.toast.setProperty("role", "muted")
        self.toast.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        self.toast.setWordWrap(True)
        layout.addWidget(self.toast)
        layout.addStretch(1)
        return panel

    # -- synchronisation with the session --------------------------------

    def sync(self) -> None:
        """Rebuild every control to match the current session state."""
        entry = self.state.entry

        # The typed equation has no row in the picker, and `findData` returning
        # -1 for it is correct rather than a problem -- the picker simply keeps
        # showing whichever catalogue problem is behind the switch.
        index = self.problem_picker.findData(entry.key)
        if index >= 0 and index != self.problem_picker.currentIndex():
            self.problem_picker.blockSignals(True)
            self.problem_picker.setCurrentIndex(index)
            self.problem_picker.blockSignals(False)

        # Another screen may have selected the user equation while the Lab was
        # not looking; follow it so the two never disagree.
        if entry.key == catalog.USER_KEY and not self.showing_equation:
            self.source_buttons.button(1).setChecked(True)
            self.source_stack.setCurrentIndex(1)
            self._sync_source_ui()

        self.blurb.setText(entry.blurb)
        self.method_picker.populate(methods_for(entry), self.state.method)
        self.parameters.rebuild(entry, self.state.params)
        self.tolerances.set_tolerances(self.state.rtol, self.state.atol)
        self.tolerances.set_steps(self.state.n_steps)
        self._sync_method_dependent()

    def _sync_method_dependent(self) -> None:
        fixed = self.state.uses_fixed_step
        self.tolerances.set_fixed_step(fixed)
        self.method_note.setText(
            "This method runs at a constant step size — accuracy is set by the "
            "step count, not a tolerance."
            if fixed else ""
        )
        if self.method_picker.current_method() != self.state.method:
            self.method_picker.populate(
                methods_for(self.state.entry), self.state.method
            )

    def _on_problem_picked(self, index: int) -> None:
        key = self.problem_picker.itemData(index)
        if key:
            self._catalog_key = key
            self.state.set_problem(key)

    # -- typed equations --------------------------------------------------

    @property
    def showing_equation(self) -> bool:
        return self.source_stack.currentIndex() == 1

    def _on_source_changed(self, index: int) -> None:
        self.source_stack.setCurrentIndex(index)
        self._sync_source_ui()
        if index == 0:
            self._parsed = None
            self.symbolic.clear(
                "Switch to “Your equation” to solve one symbolically."
            )
            self.state.set_problem(self._catalog_key)
        elif catalog.user_entry() is None:
            # Nothing typed yet: start from something that works rather than an
            # empty form and an error.
            self.editor.select_example("Damped oscillator")
        else:
            self.state.set_problem(catalog.USER_KEY, force=True)
            self._start_symbolic()

    def _sync_source_ui(self) -> None:
        """The symbolic tab is meaningless for a catalogue problem."""
        typed = self.showing_equation
        self.tabs.setTabEnabled(1, typed)
        if not typed and self.tabs.currentIndex() == 1:
            self.tabs.setCurrentIndex(0)

    def _on_equation_submitted(self, spec, ranges) -> None:
        """Parse what was typed, register it, and let the session take over."""
        try:
            entry, parsed = _make_entry(spec, ranges, self.state.method)
        except ParseError as exc:
            self._on_equation_failed(str(exc))
            return
        except Exception as exc:
            # `to_first_order` can also fail for reasons that are not parse
            # errors -- an equation singular at its own start point, say -- and
            # those messages are worth showing verbatim rather than as a crash.
            self._on_equation_failed(f"{type(exc).__name__}: {exc}")
            return

        self._parsed = parsed
        catalog.register_user_equation(entry)
        self.editor.show_message(
            f"{len(entry.labels)} state variable"
            f"{'s' if len(entry.labels) != 1 else ''}: "
            f"{', '.join(entry.labels)}",
            kind="ok",
        )
        # Always forced: the key is the same every time, so without this an
        # edited equation would be silently ignored.
        self.state.set_problem(catalog.USER_KEY, force=True)
        self._start_symbolic()

    def _on_equation_failed(self, message: str) -> None:
        self.editor.show_message(message, kind="error")
        self.symbolic.clear(message)

    def _start_symbolic(self) -> None:
        """Show the roots at once, and ask for the closed form shortly after."""
        if self._parsed is None:
            return
        parsed = with_parameters(self._parsed, self.state.params)
        self.symbolic.preview(parsed)
        self._dsolve_timer.start()

    def _request_closed_form(self) -> None:
        if self._parsed is None or not self.showing_equation:
            return
        self.symbolic.solve_for(with_parameters(self._parsed, self.state.params))

    def _on_params_changed(self, params: dict) -> None:
        if self._parsed is None or not self.showing_equation:
            return
        # The characteristic roots are a local calculation and follow the slider
        # immediately; `dsolve` is a subprocess and waits for the drag to end.
        self.symbolic.preview(with_parameters(self._parsed, params))
        self._dsolve_timer.start()

    # -- results ---------------------------------------------------------

    def _on_busy(self, busy: bool) -> None:
        if busy:
            self.stats.clear("solving…")

    def _on_result(self, result) -> None:
        self.stats.update_from(result)
        self.plot.update_from(result, self.plot.view.currentText())
        self.timeline.update_from(result, log_time=self.plot.log_time.isChecked())
        self._show_cautions(result)

    def _show_cautions(self, result) -> None:
        """Say when the answer on screen is not the whole answer.

        Two things the solver knows and the plot cannot show. Neither is a
        failure -- the curve is a genuine solution and the events found are
        genuine events -- which is exactly why they need saying: nothing else
        about the screen would suggest anything was missing.
        """
        notes: list[str] = []

        problem = getattr(getattr(result, "benchmark", None), "problem", None)
        if problem is not None:
            warning = analysis.uniqueness_warning(problem)
            if warning:
                notes.append(warning)

        solution = getattr(result, "solution", None)
        missed = getattr(solution, "incomplete_events", ()) if solution else ()
        if missed:
            notes.append(
                f"Crossings of {', '.join(missed)} were missed between steps. "
                f"The step size is chosen to resolve the solution, not the "
                f"event; raise the event's `subdivisions` to catch them."
            )

        if notes:
            self.caution.setStyleSheet(
                theme.scaled(f"font-size: 10.5px; color: {self.palette_obj.warning};")
            )
            self.caution.setText("  ".join(notes))
        self.caution.setVisible(bool(notes))

    def _replot(self) -> None:
        if self.state.result is not None:
            self._on_result(self.state.result)

    # -- export ----------------------------------------------------------

    def _flash(self, message: str, error: bool = False) -> None:
        colour = self.palette_obj.danger if error else self.palette_obj.success
        self.toast.setStyleSheet(theme.scaled(f"font-size: 10.5px; color: {colour};"))
        self.toast.setText(message)

    def _copy_code(self) -> None:
        code = self.state.request().as_code()
        QGuiApplication.clipboard().setText(code)
        self._flash(f"copied {len(code.splitlines())} lines to the clipboard")

    def _export_csv(self) -> None:
        result = self.state.result
        if result is None or not result.ok:
            self._flash("nothing to export", error=True)
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export solution", f"{self.state.problem_key}.csv",
            "CSV files (*.csv)",
        )
        if not path:
            return
        solution = result.solution
        entry = result.entry
        names = [
            entry.labels[i] if i < len(entry.labels) else f"y{i}"
            for i in range(solution.y.shape[0])
        ]
        data = np.column_stack([solution.t, solution.y.T])
        np.savetxt(
            path, data, delimiter=",", comments="",
            header="t," + ",".join(names),
        )
        self._flash(f"wrote {data.shape[0]} rows")

    def _export_png(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save plot", f"{self.state.problem_key}.png", "PNG files (*.png)"
        )
        if not path:
            return
        if self.plot.grab().save(path):
            self._flash("plot saved")
        else:
            self._flash("could not save the plot", error=True)
