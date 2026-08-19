"""Butcher tableaux as data.

Every explicit Runge-Kutta method in this library is an instance of
`ButcherTableau` consumed by the single generic stepper in `steppers/erk.py`.
Adding a method means adding coefficients here, not code.

A tableau is

    c | A
    --+----
      | b        propagated solution, order `order`
      | b_hat    embedded solution, order `error_order`

and the error estimate uses ``e = b - b_hat`` directly, so the embedded solution
is never formed.

Correctness of every array below is machine-checked by
``tests/test_tableaux.py``, which evaluates the rooted-tree order conditions
up to order 5 plus the row-sum consistency condition ``c_i = sum_j a_ij``. A
single mistyped digit fails that test immediately, which is why it exists in
Phase 1 rather than at the end.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

__all__ = ["ButcherTableau", "TABLEAUX", "get_tableau"]


@dataclass(frozen=True)
class ButcherTableau:
    """Coefficients of an embedded explicit Runge-Kutta pair."""

    name: str
    A: np.ndarray          # (s, s) strictly lower triangular
    b: np.ndarray          # (s,)   weights of the propagated solution
    c: np.ndarray          # (s,)   stage abscissae
    #: ``b - b_hat``, the error weights. None for a method with no embedded
    #: pair -- Euler and classical RK4 have none, and inventing one for them
    #: would be worse than admitting they are fixed-step.
    e: np.ndarray | None
    order: int             # order of the propagated solution
    error_order: int       # order of the embedded solution
    P: np.ndarray | None = None   # (s, k) dense-output matrix, if any
    interpolant_order: int = 3    # order of the interpolant actually used
    description: str = ""
    fsal: bool = field(init=False)

    def __post_init__(self) -> None:
        s = self.b.size
        if self.A.shape != (s, s):
            raise ValueError(f"{self.name}: A must be ({s}, {s})")
        if self.c.size != s:
            raise ValueError(f"{self.name}: c must have length {s}")
        if self.e is not None and self.e.size != s:
            raise ValueError(f"{self.name}: e must have length {s}")
        if np.any(np.triu(self.A) != 0):
            raise ValueError(f"{self.name}: A must be strictly lower triangular")
        # First Same As Last: the final stage already equals f(t+h, y_new), so the
        # driver can carry it into the next step instead of re-evaluating.
        fsal = bool(
            np.isclose(self.c[-1], 1.0)
            and np.allclose(self.A[-1], self.b)
        )
        object.__setattr__(self, "fsal", fsal)

    @property
    def n_stages(self) -> int:
        return self.b.size

    @property
    def embedded(self) -> bool:
        """Whether the pair carries an error estimate, i.e. can adapt its step."""
        return self.e is not None

    def __repr__(self) -> str:
        return (
            f"ButcherTableau({self.name}, order={self.order}"
            f"({self.error_order}), stages={self.n_stages}"
            f"{', FSAL' if self.fsal else ''})"
        )


def _tab(name, A_rows, b, c, b_hat, order, error_order, **kw) -> ButcherTableau:
    """Build a tableau from ragged lower-triangular rows.

    `b_hat` may be None, for a method that carries no embedded estimate.
    """
    s = len(b)
    A = np.zeros((s, s))
    for i, row in enumerate(A_rows):
        A[i, : len(row)] = row
    b = np.asarray(b, dtype=float)
    return ButcherTableau(
        name=name,
        A=A,
        b=b,
        c=np.asarray(c, dtype=float),
        e=None if b_hat is None else b - np.asarray(b_hat, dtype=float),
        order=order,
        error_order=error_order,
        **kw,
    )


# ---------------------------------------------------------------------------
# Bogacki-Shampine 3(2)  --  Bogacki & Shampine, Appl. Math. Lett. 2 (1989) 321
# ---------------------------------------------------------------------------

RK23 = _tab(
    "RK23",
    A_rows=[
        [],
        [1 / 2],
        [0, 3 / 4],
        [2 / 9, 1 / 3, 4 / 9],
    ],
    b=[2 / 9, 1 / 3, 4 / 9, 0],
    c=[0, 1 / 2, 3 / 4, 1],
    b_hat=[7 / 24, 1 / 4, 1 / 3, 1 / 8],
    order=3,
    error_order=2,
    interpolant_order=3,
    description="Bogacki-Shampine 3(2), FSAL, 3 evaluations per step.",
)


# ---------------------------------------------------------------------------
# Runge-Kutta-Fehlberg 4(5)  --  Fehlberg, NASA TR R-315 (1969)
#
# Propagated with the fifth-order weights (local extrapolation), which is the
# modern convention and strictly more accurate than Fehlberg's original choice.
# ---------------------------------------------------------------------------

RKF45 = _tab(
    "RKF45",
    A_rows=[
        [],
        [1 / 4],
        [3 / 32, 9 / 32],
        [1932 / 2197, -7200 / 2197, 7296 / 2197],
        [439 / 216, -8, 3680 / 513, -845 / 4104],
        [-8 / 27, 2, -3544 / 2565, 1859 / 4104, -11 / 40],
    ],
    b=[16 / 135, 0, 6656 / 12825, 28561 / 56430, -9 / 50, 2 / 55],
    c=[0, 1 / 4, 3 / 8, 12 / 13, 1, 1 / 2],
    b_hat=[25 / 216, 0, 1408 / 2565, 2197 / 4104, -1 / 5, 0],
    order=5,
    error_order=4,
    interpolant_order=3,
    description="Fehlberg 4(5) with local extrapolation, 6 evaluations per step.",
)


# ---------------------------------------------------------------------------
# Cash-Karp 5(4)  --  Cash & Karp, ACM TOMS 16 (1990) 201
# ---------------------------------------------------------------------------

CASHKARP = _tab(
    "CashKarp",
    A_rows=[
        [],
        [1 / 5],
        [3 / 40, 9 / 40],
        [3 / 10, -9 / 10, 6 / 5],
        [-11 / 54, 5 / 2, -70 / 27, 35 / 27],
        [1631 / 55296, 175 / 512, 575 / 13824, 44275 / 110592, 253 / 4096],
    ],
    b=[37 / 378, 0, 250 / 621, 125 / 594, 0, 512 / 1771],
    c=[0, 1 / 5, 3 / 10, 3 / 5, 1, 7 / 8],
    b_hat=[2825 / 27648, 0, 18575 / 48384, 13525 / 55296, 277 / 14336, 1 / 4],
    order=5,
    error_order=4,
    interpolant_order=3,
    description="Cash-Karp 5(4), 6 evaluations per step.",
)


# ---------------------------------------------------------------------------
# Dormand-Prince 5(4)  --  Dormand & Prince, J. Comput. Appl. Math. 6 (1980) 19
#
# The default. Carries Shampine's free fourth-order dense-output interpolant
# (Shampine, Math. Comp. 46 (1986) 135), which needs no extra RHS evaluations.
# ---------------------------------------------------------------------------

_DOPRI5_P = np.array(
    [
        [
            1,
            -8048581381 / 2820520608,
            8663915743 / 2820520608,
            -12715105075 / 11282082432,
        ],
        [0, 0, 0, 0],
        [
            0,
            131558114200 / 32700410799,
            -68118460800 / 10900136933,
            87487479700 / 32700410799,
        ],
        [
            0,
            -1754552775 / 470086768,
            14199869525 / 1410260304,
            -10690763975 / 1880347072,
        ],
        [
            0,
            127303824393 / 49829197408,
            -318862633887 / 49829197408,
            701980252875 / 199316789632,
        ],
        [
            0,
            -282668133 / 205662961,
            2019193451 / 616988883,
            -1453857185 / 822651844,
        ],
        [
            0,
            40617522 / 29380423,
            -110615467 / 29380423,
            69997945 / 29380423,
        ],
    ]
)

DOPRI5 = _tab(
    "DOPRI5",
    A_rows=[
        [],
        [1 / 5],
        [3 / 40, 9 / 40],
        [44 / 45, -56 / 15, 32 / 9],
        [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
        [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
        [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84],
    ],
    b=[35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0],
    c=[0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1],
    b_hat=[
        5179 / 57600,
        0,
        7571 / 16695,
        393 / 640,
        -92097 / 339200,
        187 / 2100,
        1 / 40,
    ],
    order=5,
    error_order=4,
    P=_DOPRI5_P,
    interpolant_order=4,
    description="Dormand-Prince 5(4), FSAL, 6 evaluations per step, "
    "free 4th-order dense output.",
)


# ---------------------------------------------------------------------------
# Tsitouras 5(4)  --  Tsitouras, Comput. Math. Appl. 62 (2011) 770
#
# Coefficients minimise the leading truncation-error norm subject to the
# amplification factor staying small; in practice slightly more efficient than
# DOPRI5 at loose-to-moderate tolerances. `btilde` is b - b_hat as published,
# so it is used directly as the error weight vector.
# ---------------------------------------------------------------------------

_TSIT5_b = np.array(
    [
        0.09646076681806523,
        0.01,
        0.4798896504144996,
        1.379008574103742,
        -3.290069515436081,
        2.324710524099774,
        0.0,
    ]
)

_TSIT5_btilde = np.array(
    [
        -0.00178001105222577714,
        -0.0008164344596567469,
        0.007880878010261995,
        -0.1447110071732629,
        0.5823571654525552,
        -0.45808210592918697,
        0.015151515151515152,
    ]
)

TSIT5 = _tab(
    "Tsit5",
    A_rows=[
        [],
        [0.161],
        [-0.008480655492356989, 0.335480655492357],
        [2.8971530571054935, -6.359448489975075, 4.3622954328695815],
        [
            5.325864828439257,
            -11.748883564062828,
            7.4955393428898365,
            -0.09249506636175525,
        ],
        [
            5.86145544294642,
            -12.92096931784711,
            8.159367898576159,
            -0.071584973281401,
            -0.028269050394068383,
        ],
        list(_TSIT5_b[:6]),
    ],
    b=_TSIT5_b,
    c=[0, 0.161, 0.327, 0.9, 0.9800255409045097, 1.0, 1.0],
    b_hat=_TSIT5_b - _TSIT5_btilde,
    order=5,
    error_order=4,
    interpolant_order=3,
    description="Tsitouras 5(4), FSAL, 6 evaluations per step.",
)


# ---------------------------------------------------------------------------
# The two methods every first course teaches by hand.
#
# Neither has an embedded pair, so neither can choose its own step: both run
# fixed-step and the driver asks for `n_steps` or `first_step`, exactly as the
# symplectic methods do. That is the honest arrangement -- a made-up error
# estimate would let them pretend to adapt while the controller flew blind,
# which is the failure this project already has a recorded bug for.
# ---------------------------------------------------------------------------

EULER = _tab(
    "Euler",
    A_rows=[[]],
    b=[1.0],
    c=[0.0],
    b_hat=None,
    order=1,
    error_order=0,
    description="Forward Euler. One evaluation per step, first order; the "
    "method every course starts with and no method should end with.",
)

RK4 = _tab(
    "RK4",
    A_rows=[
        [],
        [1 / 2],
        [0, 1 / 2],
        [0, 0, 1],
    ],
    b=[1 / 6, 1 / 3, 1 / 3, 1 / 6],
    c=[0, 1 / 2, 1 / 2, 1],
    b_hat=None,
    order=4,
    error_order=3,
    description="The classical Runge-Kutta method. Four evaluations per step, "
    "fourth order, no embedded estimate.",
)


TABLEAUX: dict[str, ButcherTableau] = {
    "euler": EULER,
    "rk4": RK4,
    "rk23": RK23,
    "rkf45": RKF45,
    "cashkarp": CASHKARP,
    "dopri5": DOPRI5,
    "rk45": DOPRI5,   # familiar alias
    "tsit5": TSIT5,
}


def get_tableau(name: str) -> ButcherTableau:
    """Look up a tableau by (case-insensitive) name."""
    key = name.lower().replace("-", "").replace("_", "")
    if key not in TABLEAUX:
        raise KeyError(
            f"unknown explicit method {name!r}; available: "
            f"{', '.join(sorted(TABLEAUX))}"
        )
    return TABLEAUX[key]
