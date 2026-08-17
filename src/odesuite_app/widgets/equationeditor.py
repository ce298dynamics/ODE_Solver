"""Typing an equation.

Accepts either form a course uses: one equation of any order,

    y'' - mu*(1 - y**2)*y' + y = 0

or a system of first-order ones,

    x' = 10*(y - x)
    y' = x*(28 - z) - y
    z' = x*y - 8*z/3

Two things are worked out from the text rather than asked for. **Which names are
unknowns** is decided by which ones carry a prime: only a dependent variable is
ever differentiated, so `y` in the first example is the unknown and `mu` is not.
**What is left over** is therefore a parameter, and appears in the parameter
table ready to be given a value and a slider range -- so typing a `c` into an
equation is all it takes to get a control for it.

Ranges are shown and editable rather than inferred silently. A slider span
guessed from a single typed number is wrong about as often as it is right, and a
wrong span is worse than an obvious one: it quietly limits what the user can
explore.
"""

from __future__ import annotations

import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..custom import ALLOWED_FUNCTIONS, ParseError
from ..symbolic import EquationSpec
from ..theme import Palette

__all__ = ["EquationEditor", "infer_variables", "infer_parameters", "examples"]

_MAX_EQUATIONS = 4
_MAX_PARAMETERS = 4

#: Names that are never a parameter: the independent variable and the functions
#: the parser already provides.
_RESERVED = {"t", "e", "E", "I", "pi", "oo", *ALLOWED_FUNCTIONS}

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
#: A name carrying a prime or an explicit derivative order.
_DIFFERENTIATED = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:'|′|\^\s*\(\s*\d+\s*\))")


def infer_variables(equations: list[str]) -> list[str]:
    """The dependent variables: the names that appear differentiated.

    Unambiguous in a way that guessing from position is not -- a parameter is
    never differentiated, so carrying a prime is exactly the property that
    distinguishes an unknown.
    """
    found: list[str] = []
    for line in equations:
        for name in _DIFFERENTIATED.findall(line or ""):
            # Deliberately *not* filtered against the reserved names. Carrying a
            # prime settles the question on its own: the SIR model's infected
            # compartment is called `I`, and treating that as sympy's imaginary
            # unit silently dropped a whole equation from the system.
            if name not in found and name != "t":
                found.append(name)
    return found


def infer_parameters(equations: list[str], variables: list[str]) -> list[str]:
    """Names that are neither unknowns, `t`, nor known functions.

    Done on the raw text rather than after parsing, because parsing is what
    fails when a parameter has not been declared yet -- the editor has to offer
    the field *before* the equation can be read.
    """
    known = set(variables) | _RESERVED
    found: list[str] = []
    for line in equations:
        for name in _IDENTIFIER.findall(line or ""):
            if name not in known and name not in found:
                found.append(name)
    return found


def examples() -> dict[str, EquationSpec]:
    """Worked examples: the equations, plus the multi-variable systems.

    The systems come from `custom.EXAMPLES` rewritten as first-order equations,
    so Lorenz and the rest survive the removal of the old builder screen.
    """
    from ..custom import EXAMPLES as SYSTEMS
    from ..symbolic import EXAMPLES as EQUATIONS

    out: dict[str, EquationSpec] = dict(EQUATIONS)
    for name, spec in SYSTEMS.items():
        if name in out:
            continue
        out[name] = EquationSpec(
            equations=[
                f"{variable}' = {expression}"
                for variable, expression in zip(spec.variables, spec.expressions)
            ],
            initial_conditions=", ".join(
                f"{variable}(0) = {value:g}"
                for variable, value in zip(spec.variables, spec.initial)
            ),
            variables=list(spec.variables),
            parameters=dict(spec.parameters),
            t_span=tuple(spec.t_span),
            name=name,
        )
    return out


class EquationEditor(QWidget):
    """The form: equations, initial conditions, parameters, span and method."""

    #: Emitted with ``(EquationSpec, ranges)`` when the user asks to solve.
    submitted = Signal(object, object)
    #: Emitted with a human-readable reason when the form cannot be read.
    failed = Signal(str)

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self._examples = examples()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.example_picker = QComboBox()
        self.example_picker.addItems(list(self._examples))
        self.example_picker.currentTextChanged.connect(self.load_example)
        layout.addWidget(self.example_picker)

        note = QLabel(
            "One equation of any order, or several first-order ones. Write "
            "derivatives as <i>y'</i>, <i>y''</i> or <i>y^(3)</i>."
        )
        note.setWordWrap(True)
        note.setProperty("role", "muted")
        note.setStyleSheet("font-size: 11px;")
        layout.addWidget(note)

        self.equation_fields: list[QLineEdit] = []
        for index in range(_MAX_EQUATIONS):
            field = QLineEdit()
            field.setPlaceholderText(
                "y'' + 2*y' + 5*y = 0" if index == 0 else "another equation…"
            )
            field.textChanged.connect(self._refresh_parameter_names)
            field.returnPressed.connect(self.submit)
            layout.addWidget(field)
            self.equation_fields.append(field)

        layout.addSpacing(4)
        layout.addWidget(self._heading("Initial conditions"))
        self.ics = QLineEdit()
        self.ics.setPlaceholderText("y(0) = 1, y'(0) = 0     (optional)")
        self.ics.returnPressed.connect(self.submit)
        layout.addWidget(self.ics)

        hint = QLabel(
            "Leave empty for the general solution, with arbitrary constants."
        )
        hint.setWordWrap(True)
        hint.setProperty("role", "muted")
        hint.setStyleSheet("font-size: 10.5px;")
        layout.addWidget(hint)

        # Kept in its own container so it can vanish entirely. Most equations
        # have no parameters, and an empty table headed "Parameters" sitting
        # directly above the Lab's slider panel -- also headed "Parameters" --
        # reads as a duplicate of it.
        self.parameter_box = QWidget()
        box = QVBoxLayout(self.parameter_box)
        box.setContentsMargins(0, 4, 0, 0)
        box.setSpacing(4)
        box.addWidget(self._heading("Parameters in the equation"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)
        for column, title in enumerate(("name", "value", "min", "max")):
            head = QLabel(title)
            head.setProperty("role", "muted")
            head.setStyleSheet("font-size: 10.5px;")
            grid.addWidget(head, 0, column)

        self.parameter_rows: list[tuple[QLabel, QLineEdit, QLineEdit, QLineEdit]] = []
        for row in range(_MAX_PARAMETERS):
            name = QLabel("")
            name.setProperty("role", "mono")
            value, low, high = QLineEdit(), QLineEdit(), QLineEdit()
            for field in (value, low, high):
                field.setFixedWidth(58)
                field.returnPressed.connect(self.submit)
            grid.addWidget(name, row + 1, 0)
            grid.addWidget(value, row + 1, 1)
            grid.addWidget(low, row + 1, 2)
            grid.addWidget(high, row + 1, 3)
            grid.setColumnStretch(0, 1)
            self.parameter_rows.append((name, value, low, high))
        box.addLayout(grid)
        layout.addWidget(self.parameter_box)

        layout.addSpacing(4)
        span = QHBoxLayout()
        span.setSpacing(6)
        label = QLabel("t from")
        label.setProperty("role", "muted")
        span.addWidget(label)
        self.t_start = QLineEdit("0")
        self.t_start.setFixedWidth(58)
        span.addWidget(self.t_start)
        to = QLabel("to")
        to.setProperty("role", "muted")
        span.addWidget(to)
        self.t_end = QLineEdit("10")
        self.t_end.setFixedWidth(58)
        span.addWidget(self.t_end)
        span.addStretch(1)
        layout.addLayout(span)

        self.solve_button = QPushButton("Solve")
        self.solve_button.setProperty("role", "primary")
        self.solve_button.clicked.connect(self.submit)
        layout.addWidget(self.solve_button)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        self.message.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.message)

        self._refresh_parameter_names()

    # -- construction helpers --------------------------------------------

    def _heading(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("role", "heading")
        return label

    # -- reading the form ------------------------------------------------

    def equation_texts(self) -> list[str]:
        return [f.text().strip() for f in self.equation_fields if f.text().strip()]

    def _refresh_parameter_names(self) -> None:
        """Show a row for each undeclared name, keeping any values already typed."""
        equations = self.equation_texts()
        variables = infer_variables(equations)
        names = infer_parameters(equations, variables)

        self.parameter_box.setVisible(bool(names))
        previous = {
            label.text(): (value.text(), low.text(), high.text())
            for label, value, low, high in self.parameter_rows
            if label.text()
        }
        for index, (label, value, low, high) in enumerate(self.parameter_rows):
            if index < len(names):
                name = names[index]
                label.setText(name)
                kept = previous.get(name)
                if kept:
                    value.setText(kept[0])
                    low.setText(kept[1])
                    high.setText(kept[2])
                elif not value.text():
                    value.setText("1")
                for field in (value, low, high):
                    field.setEnabled(True)
                    field.setVisible(True)
                label.setVisible(True)
            else:
                label.setText("")
                label.setVisible(False)
                for field in (value, low, high):
                    field.clear()
                    field.setVisible(False)

    def read(self) -> tuple[EquationSpec, dict[str, tuple[float, float]]]:
        """Collect the form. Raises `ParseError` with something readable."""
        equations = self.equation_texts()
        if not equations:
            raise ParseError("type an equation")

        variables = infer_variables(equations)
        if not variables:
            raise ParseError(
                "no derivative found — write y' or y'' (or y^(3)) somewhere"
            )

        parameters: dict[str, float] = {}
        ranges: dict[str, tuple[float, float]] = {}
        for label, value, low, high in self.parameter_rows:
            name = label.text().strip()
            if not name:
                continue
            parameters[name] = _number(value.text(), f"{name} =", default=1.0)
            bounds = [
                _number(low.text(), f"{name} min", default=None),
                _number(high.text(), f"{name} max", default=None),
            ]
            if bounds[0] is not None and bounds[1] is not None:
                ranges[name] = (min(bounds), max(bounds))

        start = _number(self.t_start.text(), "t from", default=0.0)
        end = _number(self.t_end.text(), "t to", default=10.0)
        if start == end:
            raise ParseError("the time span must cover an interval")

        spec = EquationSpec(
            equations=equations,
            initial_conditions=self.ics.text().strip(),
            variables=variables,
            parameters=parameters,
            t_span=(start, end),
            name=self._title(equations),
        )
        return spec, ranges

    def _title(self, equations: list[str]) -> str:
        chosen = self.example_picker.currentText()
        if chosen in self._examples:
            spec = self._examples[chosen]
            if [e.strip() for e in spec.equations] == equations:
                return chosen
        return equations[0] if len(equations) == 1 else "your system"

    def submit(self) -> None:
        try:
            spec, ranges = self.read()
        except ParseError as exc:
            self.show_message(str(exc), kind="error")
            self.failed.emit(str(exc))
            return
        self.show_message("")
        self.submitted.emit(spec, ranges)

    # -- populating ------------------------------------------------------

    def load_example(self, name: str) -> None:
        spec = self._examples.get(name)
        if spec is None:
            return
        for index, field in enumerate(self.equation_fields):
            field.blockSignals(True)
            field.setText(spec.equations[index] if index < len(spec.equations) else "")
            field.blockSignals(False)

        self.ics.setText(spec.initial_conditions)
        self.t_start.setText(f"{spec.t_span[0]:g}")
        self.t_end.setText(f"{spec.t_span[1]:g}")

        self._refresh_parameter_names()
        for label, value, low, high in self.parameter_rows:
            name_text = label.text()
            if name_text in spec.parameters:
                amount = float(spec.parameters[name_text])
                value.setText(f"{amount:g}")
                span = _default_range(amount)
                low.setText(f"{span[0]:g}")
                high.setText(f"{span[1]:g}")
        self.submit()

    def select_example(self, name: str) -> None:
        index = self.example_picker.findText(name)
        if index >= 0:
            self.example_picker.setCurrentIndex(index)
            self.load_example(name)

    def show_message(self, text: str, kind: str = "info") -> None:
        colour = {
            "error": self.palette_obj.danger,
            "warn": self.palette_obj.warning,
            "ok": self.palette_obj.success,
        }.get(kind, self.palette_obj.text_muted)
        self.message.setStyleSheet(f"font-size: 11px; color: {colour};")
        self.message.setText(text)


def _default_range(value: float) -> tuple[float, float]:
    from ..equationmodel import default_range

    return default_range(value)


def _number(text: str, what: str, default=0.0):
    text = (text or "").strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError as exc:
        raise ParseError(f"{what} {text!r} is not a number") from exc
