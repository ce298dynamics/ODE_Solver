"""Fresh numbers for the drills that have run through their built-in versions.

One function per template, named after it, each ``(rng, tier) -> slots``. They
return the slots the template's format strings name, and only have to be
plausible: `generate.sample` applies the template's `reject` and `level`, and
`freshdraw` solves every draw before a student sees it.

The ranges are a little wider than the hand-picked pools, which is the point,
but kept to numbers a course would set: small integers, roots that come out
whole, and conditions that are not both zero.
"""

from __future__ import annotations

from random import Random

from .generate import REGIMES, integer_box, second_order_from_roots

#: For the root-case drills, which regime each tier is: the same reading as
#: their `level`. Distinct real roots are where the method is introduced, a
#: complex pair is the usual case, and a repeated root needs the extra t.
_REGIME_OF_TIER = {"easier": "distinct", "typical": "complex",
                   "harder": "repeated"}


def _regime(rng: Random, tier: str) -> str:
    return _REGIME_OF_TIER.get(tier) or rng.choice(REGIMES)


def _start(rng: Random) -> tuple[int, int]:
    """``y(0), y'(0)``, not both zero: that is the zero solution."""
    while True:
        p, v = integer_box(rng, -3, 3), integer_box(rng, -3, 3)
        if p or v:
            return p, v


def growth(rng: Random, tier: str) -> dict:
    k = {"easier": 0, "typical": 1, "harder": 2}.get(tier)
    return {"a": integer_box(rng, 1, 5),
            "k": rng.randint(0, 2) if k is None else k,
            "c": integer_box(rng, 1, 5)}


def cooling(rng: Random, tier: str) -> dict:
    b = 5 * integer_box(rng, 1, 8)
    return {"a": integer_box(rng, 1, 5), "b": b,
            "c": 5 * integer_box(rng, 0, 20, exclude=(b // 5,))}


def constant_p(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 1, 6), "b": integer_box(rng, 1, 6),
            "c": integer_box(rng, -3, 3)}


def exponential_forcing(rng: Random, tier: str) -> dict:
    a = integer_box(rng, 1, 6)
    return {"a": a, "b": integer_box(rng, 1, 5),
            "c": integer_box(rng, 1, 6, exclude=(a,))}


def three_cases(rng: Random, tier: str) -> dict:
    b, c = second_order_from_roots(_regime(rng, tier), rng)
    p, v = _start(rng)
    return {"b": b, "c": c, "p": p, "v": v}


def polynomial_forcing(rng: Random, tier: str) -> dict:
    b, c = second_order_from_roots(rng.choice(REGIMES), rng)
    return {"b": b, "c": c, "d": integer_box(rng, 1, 5)}


def independent_pair(rng: Random, tier: str) -> dict:
    p, v = _start(rng)
    return {"c": integer_box(rng, 1, 7) ** 2, "p": p, "v": v}


def which_regime(rng: Random, tier: str) -> dict:
    c, k = second_order_from_roots(rng.choice(REGIMES), rng)
    return {"c": c, "k": k, "p": integer_box(rng, 1, 4)}


def laplace_first_order(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 1, 6), "b": integer_box(rng, 1, 6),
            "c": integer_box(rng, -3, 3)}


# -- first order -------------------------------------------------------------


def variable_p(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 1, 4), "b": integer_box(rng, 1, 4),
            "k": integer_box(rng, 1, 3), "c": integer_box(rng, 0, 3)}


def linear_exact(rng: Random, tier: str) -> dict:
    # A multiple of 3, so the potential's t³/3 comes out whole.
    return {"a": 3 * integer_box(rng, 1, 4), "b": integer_box(rng, 1, 5),
            "c": integer_box(rng, 1, 3)}


def homogeneous(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 1, 5), "c": integer_box(rng, 1, 5)}


def bernoulli(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 1, 5), "b": integer_box(rng, 1, 4)}


def growth_decay(rng: Random, tier: str) -> dict:
    return {"k": integer_box(rng, -6, 6, exclude=(0,)),
            "p": rng.choice((5, 10, 20, 25, 50, 100))}


# No sampler for the logistic drill, deliberately. sympy's solve time for
# y' = y(1 - y/K) is erratic in K and y(0): measured 2-6 s for most pairs but
# 33 s for K = 20, y(0) = 4 and over 40 s for K = 40, y(0) = 8, with no rule
# that predicts which. A fresh draw has 8 s; most would fall back to the pool.


# -- second order and higher -------------------------------------------------


def cosine_forcing(rng: Random, tier: str) -> dict:
    # Resonance included, as in the pool: w² = w·w is a case to recognise.
    natural = integer_box(rng, 1, 4)
    return {"w2": natural * natural, "w": integer_box(rng, 1, 4),
            "b": integer_box(rng, 1, 4)}


def second_from_first(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 2, 5), "b": integer_box(rng, 1, 4)}


def indicial(rng: Random, tier: str) -> dict:
    # The indicial equation is r² + (b - 1) r + c = 0, so its roots are built
    # the way the constant-coefficient ones are, and b is one more.
    # Not b = 0, which the pool never sets: "+ 0*t*y'" does not tidy away.
    while True:
        shift, c = second_order_from_roots(rng.choice(REGIMES), rng,
                                           damped=rng.random() < 0.5)
        if shift != -1:
            return {"b": shift + 1, "c": c}


def third_order(rng: Random, tier: str) -> dict:
    """From three integer roots, so the cubic factors: r³ - a r² + b r - c."""
    while True:
        roots = [integer_box(rng, -2, 3) for _ in range(3)]
        if len(set(roots)) > 1:
            break
    first, second, third = roots
    p, v, w = (integer_box(rng, -2, 2) for _ in range(3))
    if not (p or v or w):
        p = 1
    return {"a": first + second + third,
            "b": first * second + first * third + second * third,
            "c": first * second * third, "p": p, "v": v, "w": w}


def driven_oscillator(rng: Random, tier: str) -> dict:
    natural = integer_box(rng, 1, 5)
    return {"k": natural * natural, "w": integer_box(rng, 1, 5)}


def rlc_regimes(rng: Random, tier: str) -> dict:
    r, s = second_order_from_roots(rng.choice(REGIMES), rng)
    return {"r": r, "s": s, "q0": integer_box(rng, 1, 3)}


# -- Laplace -----------------------------------------------------------------


def transform_constant(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, 1, 6), "b": integer_box(rng, 1, 6),
            "c": integer_box(rng, -2, 3)}


def laplace_second_order(rng: Random, tier: str) -> dict:
    p, v = _start(rng)
    natural = integer_box(rng, 1, 5)
    return {"w2": natural * natural, "p": p, "v": v}


def complete_the_square(rng: Random, tier: str) -> dict:
    b, c = second_order_from_roots("complex", rng)
    return {"b": b, "c": c, "p": integer_box(rng, 1, 3)}


# -- systems -----------------------------------------------------------------


def two_by_two(rng: Random, tier: str) -> dict:
    """A = P diag(l1, l2) P⁻¹ with P of determinant 1, so A is whole and its
    eigenvalues are l1 and l2: distinct, nonzero integers.

    Every entry nonzero and small, as in the pool: a zero off the diagonal
    makes the system triangular, which is the defective drill's business, and
    a zero on it prints as ``0*x``.
    """
    while True:
        p = integer_box(rng, -2, 2, exclude=(0,))
        q = integer_box(rng, -2, 2, exclude=(0,))
        first, second = rng.sample([n for n in range(-4, 5) if n], 2)
        # P = [[1, p], [q, 1 + pq]] and P⁻¹ = [[1 + pq, -p], [-q, 1]].
        lead = 1 + p * q
        entries = {"a": first * lead - second * p * q,
                   "b": -first * p + second * p,
                   "c": first * q * lead - second * q * lead,
                   "d": -first * p * q + second * lead}
        if all(entries.values()) and max(map(abs, entries.values())) <= 9:
            return entries


def spiral_system(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, -4, 4, exclude=(0,)),
            "b": integer_box(rng, 1, 5)}


def defective(rng: Random, tier: str) -> dict:
    return {"a": integer_box(rng, -4, 4, exclude=(0,)),
            "b": integer_box(rng, 1, 4)}


def constant_forcing(rng: Random, tier: str) -> dict:
    return {"f": integer_box(rng, 1, 6), "p": integer_box(rng, 0, 4)}


def convertible(rng: Random, tier: str) -> dict:
    b, c = second_order_from_roots(rng.choice(REGIMES), rng)
    p, v = _start(rng)
    return {"b": b, "c": c, "p": p, "v": v}
