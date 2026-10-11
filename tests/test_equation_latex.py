"""Questions show their equations typeset, in the notation a course writes.

Practice, the drills and the quiz showed a Solve question's equation as the
code it is stored as, ``y' = 2*t*y`` in a monospace font, on the same page as
choice questions whose equations were typeset. `mathrender.equation_latex`
reads the stored text instead, so these tests pin what it makes of it: prime
notation, terms in the order written, and every equation the course can show
actually rendering, which is checked by rendering it. Mathtext accepts some
LaTeX and draws nothing.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy", reason="the app extra is not installed")

from odesuite_app import lessons as content  # noqa: E402
from odesuite_app import mathrender
from odesuite_app.lessons import generate
from odesuite_app.mathrender import equation_latex


@pytest.mark.parametrize("text, expected", [
    ("y' = 2*t*y", "y' = 2 t y"),
    ("y'' + 2*y' + 5*y = 0", "y'' + 2 y' + 5 y = 0"),
    ("t^2*y'' - 3*t*y' + 4*y = 0", "t^{2} y'' - 3 t y' + 4 y = 0"),
    ("y^(4) - y = 0", "y^{(4)} - y = 0"),
    ("y' = -0.2*(y - 20)", r"y' = -0.2 \left(y - 20\right)"),
    ("y' = -y/t + t", r"y' = -\frac{y}{t} + t"),
    ("y'' + y = 1/(1 + exp(t))", r"y'' + y = \frac{1}{1 + e^{t}}"),
])
def test_an_equation_reads_as_written(text, expected):
    """In prime notation, the terms in the order written, and none of the
    artifacts sympy prints for an unevaluated tree: no "1 \\frac{1}{...}",
    no "\\left(-1\\right) y"."""
    assert equation_latex(text) == expected


def test_conditions_follow_the_equation():
    assert (equation_latex("y'' + y = 0", "y(0) = 1, y'(0) = 0")
            == r"y'' + y = 0,\qquad y(0) = 1,\quad y'(0) = 0")


def test_a_system_is_one_line_per_equation():
    assert (equation_latex("x' = x + 2*y; y' = 3*x + 2*y")
            == r"x' = x + 2 y,\quad y' = 3 x + 2 y")


def test_a_switch_is_written_u_as_the_course_writes_it():
    assert "u" in equation_latex("y'' + y = Heaviside(t - 2)")
    assert "theta" not in equation_latex("y'' + y = Heaviside(t - 2)")


def test_the_point_an_equilibrium_question_asks_about_is_kept():
    latex = equation_latex("x' = y; y' = -sin(x)     at (x, y) = (pi, 0)")
    assert latex.endswith(r"\mathrm{at}\ (x, y) = (\pi, 0)")


def test_unsafe_text_is_refused_not_parsed():
    assert equation_latex("y' = sin.__class__") is None


def _every_equation_the_course_shows() -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for lesson in content.LESSONS:
        for question in lesson.questions:
            if getattr(question, "equation", "") and hasattr(question, "conditions"):
                found.add((question.equation, question.conditions))
        for template in lesson.templates:
            for seed in range(12):
                question = generate.draw(template, seed)
                if type(question).__name__ == "Solve":
                    found.add((question.equation, question.conditions))
                for line in (getattr(question, "shown", "") or "").splitlines():
                    if ":" in line:
                        line = line.split(":", 1)[1].strip()
                    equation, _, conditions = line.partition(",   ")
                    if equation.strip():
                        found.add((equation.strip(), conditions.strip()))
    return found


def test_every_equation_the_course_shows_is_typeset():
    unread, undrawn = [], []
    for equation, conditions in sorted(_every_equation_the_course_shows()):
        latex = equation_latex(equation, conditions)
        if latex is None:
            unread.append(equation)
        elif not mathrender.latex_to_png(latex, "#000000", 13, 96):
            undrawn.append(latex)
    assert not unread, f"left as code: {unread[:5]}"
    assert not undrawn, f"accepted but drawn as nothing: {undrawn[:5]}"
