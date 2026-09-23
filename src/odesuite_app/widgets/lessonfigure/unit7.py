"""Figures for Series solutions."""

from __future__ import annotations

import math

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from .base import LessonFigure

#: Digits as subscripts, for naming a coefficient in the readout. The rest of
#: this package sets mathematics typographically -- a₆ rather than a_6 -- and
#: an index that arrives as a number has to be converted rather than typed.
_SUBSCRIPTS = str.maketrans("0123456789", "\u2080\u2081\u2082\u2083"
                                          "\u2084\u2085\u2086\u2087"
                                          "\u2088\u2089")


def _subscript(value: int) -> str:
    return str(int(value)).translate(_SUBSCRIPTS)


# ---------------------------------------------------------------------------
# Power series: how many terms, and how far they are good for
# ---------------------------------------------------------------------------


class PartialSumsFigure(LessonFigure):
    """Partial sums of a series solution, against the answer and the radius.

    Two of the lesson's claims are hard to believe from prose and obvious
    here. Truncating is a *choice* -- add terms and the partial sum hugs the
    true curve further out, with the series itself never in error. And the
    radius of convergence is real: past the marked line no number of terms
    helps at all, because the coefficient of y′ vanishes there and the
    equation has nothing to say.

    The equation is (1 − t)·y′ = y with y(0) = 1, whose recurrence gives
    a_{n+1} = a_n and so the series 1 + t + t² + …, and whose closed form is
    1/(1 − t). Everything on the screen can therefore be checked by hand.
    """

    title = "Partial sums, and where they stop being any use"
    caption = ("(1 − t)·y′ = y with y(0) = 1. Every coefficient equals the "
               "one before it, so the series is 1 + t + t² + … and the answer "
               "is 1/(1 − t). Add terms and the partial sum follows the curve "
               "further — but never past the dashed line, which is where the "
               "leading coefficient vanishes.")

    _TLIM = (-1.25, 1.25)
    _RADIUS = 1.0

    def build_sliders(self) -> None:
        self.add_slider("n", "terms kept", 1, 24, 5,
                        hint="How far the sum is truncated. The series is "
                             "not an approximation; a truncation of it is.")

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        terms = int(round(self.value("n")))
        t = np.linspace(*self._TLIM, 1400)

        # The exact solution, drawn either side of its own singularity so the
        # two branches are not joined by a spurious vertical line.
        for piece in (t[t < self._RADIUS - 0.02], t[t > self._RADIUS + 0.02]):
            if piece.size:
                self.plot.plot(piece, 1.0 / (1.0 - piece),
                               pen=pg.mkPen(self.palette_obj.text_muted,
                                            width=2, style=Qt.DotLine))

        # Every coefficient is 1, which is the recurrence this equation gives.
        partial = np.zeros_like(t)
        for power in range(terms):
            partial = partial + t ** power
        self.plot.plot(t, partial, pen=pg.mkPen(self.colour(0), width=3))

        for edge in (-self._RADIUS, self._RADIUS):
            self.plot.addLine(x=edge,
                              pen=pg.mkPen(self.palette_obj.warning, width=2,
                                           style=Qt.DashLine))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        # Tall enough that the agreement near the origin is as visible as the
        # departure past the radius, which is the comparison being made.
        self.plot.setYRange(-2.0, 14.0, padding=0.02)
        self._describe(terms)

    def _describe(self, terms: int) -> None:
        # Where the truncation is still within a percent of the truth, found
        # by walking out from the origin rather than asserted.
        grid = np.linspace(0.0, 0.995, 800)
        partial = np.zeros_like(grid)
        for power in range(terms):
            partial = partial + grid ** power
        exact = 1.0 / (1.0 - grid)
        close = np.abs(partial - exact) <= 0.01 * np.abs(exact)
        reach = float(grid[close][-1]) if close.any() else 0.0
        self.readout.setText(
            f"{terms} term{'' if terms == 1 else 's'}: within 1% of the "
            f"answer out to t = {reach:.3f}. The radius is 1 whatever the "
            "number of terms — past it the series diverges and the equation "
            "loses its leading coefficient."
        )


# ---------------------------------------------------------------------------
# The recurrence: the coefficients themselves, and where they stop
# ---------------------------------------------------------------------------


class RecurrenceFigure(LessonFigure):
    """``(1 - t^2)y" - 2t y' + L y = 0``, drawn as its coefficients.

    A recurrence is the actual output of the series method -- the truncation
    that gets printed is a consequence of it -- and it is the one part of the
    method a reader never sees a picture of. So the left pane is the
    coefficients themselves: a_(n+2) = [n(n+1) - L] / [(n+1)(n+2)] * a_n,
    drawn as a stem per term.

    What that buys is the termination condition, which is otherwise a piece of
    algebra to be taken on trust. Slide L and the stems mostly march on
    forever; land it on L = l(l+1) for a whole number l, and the numerator of
    the recurrence hits zero at n = l and every stem past it vanishes at once.
    That is the entire reason Legendre polynomials exist, and it happens on
    screen.

    l snaps to a whole number when it comes within half a slider step, for
    the reason `DampingFigure` snaps to critical damping: the interesting
    values are isolated points, and a quantised slider will otherwise never
    land on one.
    """

    title = "The recurrence, and the ℓ that makes it stop"
    caption = ("Left: the coefficients aₙ from the recurrence, one stem each. "
               "Right: the partial sum they build. Slide ℓ onto a whole "
               "number and watch the stems past n = ℓ vanish — the numerator "
               "n(n+1) − ℓ(ℓ+1) is zero there, and every coefficient after it "
               "inherits the zero.")
    plots = 2

    _TERMS = 16
    _TLIM = (-1.0, 1.0)
    #: Half a slider step, so a whole l is reachable. See the class docstring.
    _SNAP = 6.0 / 1000 / 2

    def build_sliders(self) -> None:
        self.add_slider("l", "ℓ   (so that λ = ℓ(ℓ+1))", 0.0, 6.0, 3.0,
                        hint="Whole numbers are the special ones, and the "
                             "slider snaps onto them: that is exactly when "
                             "the series terminates into a polynomial.")

    def degree(self) -> float:
        value = self.value("l")
        nearest = round(value)
        return float(nearest) if abs(value - nearest) < self._SNAP else value

    def coefficients(self, degree: float) -> np.ndarray:
        """``a_0 ... a_n`` from the recurrence, both parities at once.

        Both, because the equation supplies two independent solutions and the
        recurrence steps by two: the even coefficients descend from a_0 and
        the odd from a_1, and a picture showing only one of them would hide
        the fact that termination happens to exactly one parity at a time.
        """
        eigenvalue = degree * (degree + 1.0)
        terms = np.zeros(self._TERMS)
        terms[0], terms[1] = 1.0, 1.0
        for n in range(self._TERMS - 2):
            terms[n + 2] = (
                terms[n] * (n * (n + 1.0) - eigenvalue)
                / ((n + 1.0) * (n + 2.0))
            )
        return terms

    def draw(self) -> None:
        degree = self.degree()
        terms = self.coefficients(degree)
        self._draw_stems(terms, degree)
        self._draw_sum(terms)
        self._describe(terms, degree)

    def _draw_stems(self, terms: np.ndarray, degree: float) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "n")
        pane.setLabel("left", "aₙ")
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        for n, value in enumerate(terms):
            # A stem rather than a bar: what matters is the sign as well as
            # the size, and the coefficients alternate.
            alive = abs(value) > 1e-12
            colour = self.colour(0) if alive else self.palette_obj.text_muted
            pane.plot([n, n], [0.0, float(value)],
                      pen=pg.mkPen(colour, width=3 if alive else 1))
            pane.plot([n], [float(value)], pen=None, symbol="o",
                      symbolSize=7 if alive else 4, symbolBrush=colour)
        nearest = round(degree)
        if abs(degree - nearest) < 1e-9:
            pane.addLine(x=nearest,
                         pen=pg.mkPen(self.palette_obj.warning, width=2,
                                      style=Qt.DashLine))
        pane.setYRange(-2.5, 2.5, padding=0.02)

    def _draw_sum(self, terms: np.ndarray) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "partial sum")
        t = np.linspace(*self._TLIM, 800)
        even = np.zeros_like(t)
        odd = np.zeros_like(t)
        for n, value in enumerate(terms):
            piece = value * t ** n
            if n % 2:
                odd = odd + piece
            else:
                even = even + piece
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot(t, even, pen=pg.mkPen(self.colour(0), width=3))
        pane.plot(t, odd, pen=pg.mkPen(self.colour(1), width=2,
                                       style=Qt.DashLine))
        pane.setYRange(-4.0, 4.0, padding=0.02)

    def _describe(self, terms: np.ndarray, degree: float) -> None:
        alive = np.flatnonzero(np.abs(terms) > 1e-12)
        last = int(alive[-1]) if alive.size else 0
        nearest = round(degree)
        if abs(degree - nearest) < 1e-9:
            parity = "even" if nearest % 2 == 0 else "odd"
            self.readout.setText(
                f"ℓ = {nearest:.0f}, so λ = {nearest * (nearest + 1):.0f}. "
                f"The numerator n(n+1) − λ is zero at n = {nearest:.0f}, so "
                f"the {parity} series stops there and is a polynomial of "
                f"degree {nearest:.0f}. The other parity runs on: the last "
                f"non-zero coefficient drawn is a{_subscript(last)}."
            )
            return
        self.readout.setText(
            f"ℓ = {degree:.3f}, so λ = {degree * (degree + 1):.3f}. The "
            "numerator is never zero, so neither series terminates — every "
            f"coefficient out to a{_subscript(self._TERMS - 1)} is non-zero, "
            "and the answer is a genuine infinite series rather than a "
            "polynomial."
        )


# ---------------------------------------------------------------------------
# Frobenius: the power the indicial equation gives, and the series that fixes it
# ---------------------------------------------------------------------------


class IndicialFigure(LessonFigure):
    """Bessel's equation: the leading power t^v, against the whole solution.

    Frobenius is a power series *multiplied by a power of t*, and the power is
    where the whole difficulty is: it is not a free choice, it is forced by
    the indicial equation, and for Bessel that is r^2 - v^2 = 0, giving
    r = +-v.

    The figure separates the two halves of that answer. The dashed curve is
    t^v alone -- what the indicial root by itself predicts -- and the solid
    one is the full Frobenius series. Near the origin they are on top of each
    other, which is what "the indicial root fixes the behaviour at the
    singular point" means and is the only thing the indicial equation
    actually claims. Further out they part, and the series is the whole of
    the difference.

    The second root, -v, is drawn too. Where the two roots differ by
    something other than a whole number it is the second solution outright,
    and it is unbounded at the origin whatever v is -- which is why an initial
    condition at a regular singular point usually picks the first root alone.
    """

    title = "The indicial root, and what the series adds to it"
    caption = ("Bessel's equation. Dashed: tᵛ, the behaviour the indicial "
               "root r² = ν² forces at the origin. Solid: the Frobenius "
               "series in full. They agree where the indicial equation claims "
               "they do — near t = 0 — and the series is everything after "
               "that. Dotted: the other root, −ν.")

    _TLIM = (0.01, 12.0)

    def build_sliders(self) -> None:
        self.add_slider("v", "ν   (so the roots are ±ν)", 0.25, 3.0, 1.0)
        self.add_slider("n", "terms of the series", 1, 22, 14,
                        hint="The correction to the leading power. One term "
                             "is the leading power itself; the rest is how "
                             "far out it stays right.")

    def _series(self, t: np.ndarray, order: float, terms: int) -> np.ndarray:
        """The Frobenius series for ``J_v``, summed term by term.

        Written out rather than taken from a library: the subject is the
        series, and a figure that called a Bessel routine would be drawing the
        answer without drawing the method.
        """
        half = t / 2.0
        total = np.zeros_like(t)
        for m in range(max(1, terms)):
            coefficient = ((-1.0) ** m
                           / (math.factorial(m) * math.gamma(m + order + 1.0)))
            total = total + coefficient * half ** (2 * m + order)
        return total

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        order = self.value("v")
        terms = int(round(self.value("n")))
        t = np.linspace(*self._TLIM, 1400)

        # The leading power, normalised to match the series' own first term,
        # so the two genuinely coincide near the origin rather than merely
        # having the same shape there.
        leading = ((t / 2.0) ** order) / math.gamma(order + 1.0)
        second = ((t / 2.0) ** -order) / math.gamma(1.0 - order) \
            if abs(order - round(order)) > 1e-9 else None

        self.plot.addLine(x=0, pen=pg.mkPen(self.palette_obj.warning, width=2,
                                            style=Qt.DashLine))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, leading, pen=pg.mkPen(self.colour(1), width=2,
                                                style=Qt.DashLine))
        if second is not None:
            self.plot.plot(t, second, pen=pg.mkPen(self.colour(2), width=2,
                                                   style=Qt.DotLine))
        self.plot.plot(t, self._series(t, order, terms),
                       pen=pg.mkPen(self.colour(0), width=3))
        self.plot.setXRange(-0.8, self._TLIM[1], padding=0.02)
        self.plot.setYRange(-1.2, 1.6, padding=0.02)
        self._describe(t, order, terms, leading)

    def _describe(self, t, order, terms, leading) -> None:
        full = self._series(t, order, terms)
        # How far out the leading power alone stays within 5% of the whole
        # solution, walked off the drawn samples rather than asserted.
        close = np.abs(full - leading) <= 0.05 * np.abs(full)
        reach = float(t[close][-1]) if close.any() else float(t[0])
        whole = abs(order - round(order)) < 1e-9
        second = (
            "the two roots differ by a whole number here, so the second "
            "solution needs a logarithm and is not simply t⁻ᵛ"
            if whole else
            f"the second root −ν = {-order:.2f} gives a solution unbounded at "
            "the origin, which is why a condition there picks the first"
        )
        self.readout.setText(
            f"indicial equation r² − ν² = 0, roots r = ±{order:.2f}. With "
            f"{terms} term{'' if terms == 1 else 's'}, tᵛ alone is within 5% "
            f"of the full solution out to t = {reach:.2f}; past that the "
            f"series is doing all the work. {second}."
        )
