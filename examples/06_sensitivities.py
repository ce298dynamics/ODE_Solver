"""dy/dp: how the trajectory responds to its parameters, and fitting with it.

    py -3.10 examples/06_sensitivities.py

Forward sensitivities integrate the variational equations alongside the state,
so `dy/dp` comes out to the same tolerance as `y` itself. The alternative --
differencing two separate solves -- is dominated by integration noise, because
each trajectory is only accurate to the tolerance and you are then dividing
their difference by a small number.

There is a sharp practical lesson in here about the Jacobian, measured below:
**at tight tolerances you must supply one.** Without it the augmented system is
differenced, and a finite-difference Jacobian is accurate to about `sqrt(eps)`,
roughly 1e-8. Ask for 1e-12 and Newton is being asked to converge to an
accuracy the iteration matrix does not have, so it thrashes: 29 000 steps and
3 800 rejections on a problem that takes 1 156 steps and one rejection with the
derivative written down. That is not a small constant factor.
"""

from __future__ import annotations

import time

import numpy as np

from odesuite import forward_sensitivities

TRUE = np.array([1.5, 1.0])          # (a, b)
Y0 = np.array([2.0])
SPAN = (0.0, 3.0)


def decay(t, y, p):
    """y' = -a*y + b, a two-parameter linear problem with a closed form."""
    a, b = p
    return np.array([-a * y[0] + b])


def jac(t, y, p):
    a, _ = p
    return np.array([[-a]])


def dfdp(t, y, p):
    return np.array([[-y[0], 1.0]])


def exact(t, a, b, y0=2.0):
    return (y0 - b / a) * np.exp(-a * t) + b / a


def main() -> None:
    # -- correctness ----------------------------------------------------
    result = forward_sensitivities(decay, SPAN, Y0, TRUE, jac=jac, dfdp=dfdp,
                                   rtol=1e-12, atol=1e-14)
    computed = result.S_at_end()[0]

    a, b, t_end = TRUE[0], TRUE[1], SPAN[1]
    eps = 1e-6
    da = (exact(t_end, a + eps, b) - exact(t_end, a - eps, b)) / (2 * eps)
    db = (exact(t_end, a, b + eps) - exact(t_end, a, b - eps)) / (2 * eps)

    print(f"sensitivities at t = {t_end:g}   ({result.stats})")
    print(f"  dy/da  computed {computed[0]:+.10f}   reference {da:+.10f}")
    print(f"  dy/db  computed {computed[1]:+.10f}   reference {db:+.10f}")
    assert abs(computed[0] - da) < 1e-6
    assert abs(computed[1] - db) < 1e-6

    # -- why the Jacobian matters ---------------------------------------
    print("\nthe cost of not supplying a Jacobian:")
    print(f"  {'rtol':>8s}   {'differenced':>22s}   {'analytic':>22s}")
    for rtol in (1e-8, 1e-10, 1e-11):
        started = time.perf_counter()
        fd = forward_sensitivities(decay, SPAN, Y0, TRUE, rtol=rtol, atol=rtol * 1e-2)
        fd_ms = (time.perf_counter() - started) * 1e3

        started = time.perf_counter()
        an = forward_sensitivities(decay, SPAN, Y0, TRUE, jac=jac, dfdp=dfdp,
                                   rtol=rtol, atol=rtol * 1e-2)
        an_ms = (time.perf_counter() - started) * 1e3

        print(f"  {rtol:8.0e}   {fd.stats.naccepted:6d} steps {fd.stats.nrejected:5d} rej"
              f" {fd_ms:6.0f}ms   {an.stats.naccepted:6d} steps {an.stats.nrejected:5d} rej"
              f" {an_ms:6.0f}ms")

    print("  the differenced Jacobian is accurate to ~sqrt(eps); asking for more")
    print("  than that makes the Newton iteration, and then the controller, thrash.")

    # -- what it is all for: parameter fitting --------------------------
    times = np.linspace(0.2, 3.0, 12)
    observations = np.array([exact(t, *TRUE) for t in times])

    guess = np.array([0.8, 0.4])
    print(f"\nGauss-Newton fit from a={guess[0]:g}, b={guess[1]:g}")
    for iteration in range(20):
        run = forward_sensitivities(decay, SPAN, Y0, guess, jac=jac, dfdp=dfdp,
                                    t_eval=times, rtol=1e-11, atol=1e-13)
        residual = run.y[0] - observations
        jacobian = run.S[0].T                       # (len(times), n_params)
        step, *_ = np.linalg.lstsq(jacobian, -residual, rcond=None)
        guess = guess + step
        if np.linalg.norm(step) < 1e-12:
            break

    print(f"  recovered a={guess[0]:.10f}, b={guess[1]:.10f} in {iteration + 1} iterations")
    print(f"  true      a={TRUE[0]:.10f}, b={TRUE[1]:.10f}")
    assert np.allclose(guess, TRUE, atol=1e-7), guess


if __name__ == "__main__":
    main()
