"""Sliders, pickers and the parameter panel.

Two decisions shape everything here.

**Sliders debounce.** Qt emits a value on every pixel of a drag; solving on each
one would queue hundreds of jobs to display the last. A short timer coalesces a
drag into one solve, while the numeric readout updates immediately so the
control still feels live.

**Ranges that span decades are logarithmic.** A linear slider for Van der Pol's
mu over [0.1, 1000] spends 99% of its travel in the non-stiff regime and makes
the interesting part unreachable.
"""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .. import catalog
from ..catalog import CatalogEntry, ParamSpec


def fill_problem_picker(combo: QComboBox, accept=None, *,
                        include_user: bool = True) -> None:
    """(Re)populate a problem combo box, keeping the current selection.

    Every screen offers a subset of the catalogue -- the phase portrait wants
    autonomous planar systems, the race excludes the PDEs -- so each passes its
    own `accept` predicate and this handles the rest.

    Re-populating rather than filling once is what lets a typed equation appear.
    It is registered while the user is on the Solver Lab, long after the other
    screens were built, so their pickers have to be refreshed when they are next
    shown or the equation is simply absent from them.
    """
    previous = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    for key in catalog.keys(include_user=include_user):
        entry = catalog.get(key)
        if accept is None or accept(entry):
            combo.addItem(entry.title, key)
    index = combo.findData(previous)
    if index >= 0:
        combo.setCurrentIndex(index)
    combo.blockSignals(False)

__all__ = [
    "ValueSlider",
    "ParameterPanel",
    "MethodPicker",
    "TolerancePanel",
    "fill_problem_picker",
    "format_value",
]

#: Slider resolution. Integers internally, mapped to the real range on the way
#: out; 1000 steps is finer than the eye can drag.
_TICKS = 1000

#: Coalescing window for a drag, in milliseconds.
_DEBOUNCE_MS = 140


def format_value(value: float) -> str:
    """Compact human-readable number for a slider readout."""
    if value == 0:
        return "0"
    magnitude = abs(value)
    if magnitude >= 1e5 or magnitude < 1e-3:
        return f"{value:.3g}"
    if magnitude >= 100:
        return f"{value:.1f}"
    if magnitude >= 1:
        return f"{value:.3g}"
    return f"{value:.4g}"


class ValueSlider(QWidget):
    """A labelled slider over a real range, optionally logarithmic.

    Emits `preview` continuously while dragging (cheap, for the readout) and
    `committed` once the drag settles (expensive, triggers a solve).
    """

    preview = Signal(float)
    committed = Signal(float)

    def __init__(self, label: str, low: float, high: float, value: float,
                 log: bool = False, hint: str = "", parent=None) -> None:
        super().__init__(parent)
        self.low, self.high, self.log = float(low), float(high), bool(log)
        if self.log and self.low <= 0:
            raise ValueError("a logarithmic slider needs a positive lower bound")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(2)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self.name = QLabel(label)
        self.name.setStyleSheet("font-size: 12px;")
        header.addWidget(self.name)
        header.addStretch(1)
        self.readout = QLabel(format_value(value))
        self.readout.setProperty("role", "mono")
        header.addWidget(self.readout)
        layout.addLayout(header)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, _TICKS)
        self.slider.setValue(self._to_tick(value))
        if hint:
            self.setToolTip(hint)
        layout.addWidget(self.slider)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(_DEBOUNCE_MS)
        self._timer.timeout.connect(
            lambda: self.committed.emit(self.value())
        )
        self.slider.valueChanged.connect(self._on_moved)

    # -- mapping ---------------------------------------------------------

    def _to_tick(self, value: float) -> int:
        value = min(max(value, self.low), self.high)
        if self.log:
            span = math.log(self.high / self.low)
            fraction = math.log(value / self.low) / span if span else 0.0
        else:
            span = self.high - self.low
            fraction = (value - self.low) / span if span else 0.0
        return int(round(fraction * _TICKS))

    def _from_tick(self, tick: int) -> float:
        fraction = tick / _TICKS
        if self.log:
            return self.low * (self.high / self.low) ** fraction
        return self.low + fraction * (self.high - self.low)

    # -- behaviour -------------------------------------------------------

    def value(self) -> float:
        return self._from_tick(self.slider.value())

    def set_value(self, value: float, *, notify: bool = False) -> None:
        blocked = self.slider.blockSignals(not notify)
        self.slider.setValue(self._to_tick(value))
        self.slider.blockSignals(blocked)
        self.readout.setText(format_value(self.value()))

    def _on_moved(self, _tick: int) -> None:
        current = self.value()
        self.readout.setText(format_value(current))
        self.preview.emit(current)
        self._timer.start()


class ParameterPanel(QWidget):
    """The sliders for one problem's parameters, rebuilt when it changes."""

    changed = Signal(str, float)     # name, value

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._sliders: dict[str, ValueSlider] = {}

    def rebuild(self, entry: CatalogEntry, values: dict) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # Unparent *now*, not on the next event-loop turn. `deleteLater`
                # alone leaves the old sliders visible and still painting until
                # the loop spins, so the outgoing problem's labels appear
                # overlaid on the incoming one's.
                widget.setParent(None)
                widget.deleteLater()
        self._sliders.clear()

        for spec in entry.params:
            slider = ValueSlider(
                spec.label, spec.low, spec.high,
                values.get(spec.name, spec.default), spec.log, spec.hint,
            )
            slider.committed.connect(
                lambda v, n=spec.name: self.changed.emit(n, v)
            )
            self._layout.addWidget(slider)
            self._sliders[spec.name] = slider

    def set_values(self, values: dict) -> None:
        for name, slider in self._sliders.items():
            if name in values:
                slider.set_value(values[name])


class MethodPicker(QComboBox):
    """A grouped method list, with non-selectable group headings.

    Grouping matters here: "radau" and "verlet" are not interchangeable
    alternatives, they belong to different families with different
    requirements, and a flat alphabetical list would hide that entirely.
    """

    method_chosen = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.currentIndexChanged.connect(self._on_index)
        self._suppress = False

    def populate(self, groups: dict[str, list[str]], current: str) -> None:
        self._suppress = True
        self._model.clear()
        target = 0
        for group, methods in groups.items():
            header = QStandardItem(f"  {group}")
            header.setFlags(Qt.NoItemFlags)          # a label, not a choice
            header.setData("", Qt.UserRole)
            self._model.appendRow(header)
            for name in methods:
                item = QStandardItem(f"      {name}")
                item.setData(name, Qt.UserRole)
                self._model.appendRow(item)
                if name == current:
                    target = self._model.rowCount() - 1
        self.setCurrentIndex(target)
        self._suppress = False

    def current_method(self) -> str:
        return self._model.item(self.currentIndex()).data(Qt.UserRole) or ""

    def _on_index(self, index: int) -> None:
        if self._suppress or index < 0:
            return
        item = self._model.item(index)
        name = item.data(Qt.UserRole) if item else ""
        if name:
            self.method_chosen.emit(name)


class TolerancePanel(QWidget):
    """Tolerance controls, or a step count for the fixed-step methods.

    Symplectic and exponential integrators run at a constant step by
    construction, so presenting them with a tolerance slider would be a lie.
    The panel swaps to a step-count control instead.
    """

    tolerances_changed = Signal(float, float)
    steps_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.rtol = ValueSlider("relative tolerance", 1e-13, 1e-2, 1e-8, log=True,
                                hint="Tighter tolerance costs more steps")
        self.atol = ValueSlider("absolute tolerance", 1e-16, 1e-4, 1e-11, log=True)
        self.steps = ValueSlider("fixed steps", 50, 200_000, 2000, log=True,
                                 hint="This method runs at a constant step size")

        for widget in (self.rtol, self.atol, self.steps):
            layout.addWidget(widget)

        # Absolute tolerance tracks relative by default: three decades below is
        # the usual convention and one fewer thing to get wrong.
        self.rtol.committed.connect(self._on_rtol)
        self.rtol.preview.connect(
            lambda v: self.atol.set_value(v * 1e-3)
        )
        self.atol.committed.connect(
            lambda _: self.tolerances_changed.emit(
                self.rtol.value(), self.atol.value()
            )
        )
        self.steps.committed.connect(lambda v: self.steps_changed.emit(int(v)))
        self.set_fixed_step(False)

    def _on_rtol(self, value: float) -> None:
        self.atol.set_value(value * 1e-3)
        self.tolerances_changed.emit(value, self.atol.value())

    def set_fixed_step(self, fixed: bool) -> None:
        self.rtol.setVisible(not fixed)
        self.atol.setVisible(not fixed)
        self.steps.setVisible(fixed)

    def set_tolerances(self, rtol: float, atol: float) -> None:
        self.rtol.set_value(rtol)
        self.atol.set_value(atol)

    def set_steps(self, n: int) -> None:
        self.steps.set_value(n)
