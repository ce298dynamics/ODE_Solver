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
