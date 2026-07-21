#!/usr/bin/env python3
"""
Degree-of-regularity growth law for the boolean Semaev t=3 Weil-descent family.

Self-contained (pure Python, no Sage): reproduces the semi-regular d_reg(n) law
using the SAME recurrence the SIG-005 instrument uses
(experiments/EXP-SIG-005/src/h013_f5_signatures.sage: semireg_rank_pred), which
was independently validated to match the random support-matched null EXACTLY at
every degree D < d_reg (see the Sage validation script).

Instrument family (verified from run receipts EV-SIG-003/005, all recorded n):
    nb = 2n boolean variables ;  n degree-2 equations + n degree-3 equations.

Semi-regular Hilbert series (the instrument's model, ascending in-place =
divide-by-(1+z^d) per equation):
    A(z) = (1+z)^{2n} / [ (1+z^2)^n (1+z^3)^n ] = B(z)^n,
    B(z) = (1+z)^2 / [ (1+z^2)(1+z^3) ].
d_reg(n) := first degree D with [A(z)]_D <= 0.
"""
from math import comb


def dreg(n, slack=25):
    N = int(0.5 * n) + slack
    a = [comb(2 * n, j) if j <= 2 * n else 0 for j in range(N)]
    for d in ([2] * n + [3] * n):          # ascending in-place == divide by (1+z^d)
        for j in range(d, N):
            a[j] -= a[j - d]
    return next(D for D in range(N) if a[D] <= 0)


if __name__ == "__main__":
    print("n     d_reg   d_reg/n")
    for n in [6, 9, 12, 15, 18, 21, 24, 30, 48, 96, 161,
              500, 1000, 2000, 4000, 8000]:
        dr = dreg(n)
        print(f"{n:5d} {dr:6d}   {dr/n:.5f}")
    # Asymptotic density c* = lim d_reg/n  (marginal slope):
    a1, a2 = dreg(4000), dreg(8000)
    print(f"\nmarginal slope over [4000,8000] = {(a2 - a1)/4000:.5f}  (-> c* ~ 0.238)")
    # Grobner-cost consequence at density c*=0.24 on nb=2n vars:
    #   #monomials <= d_reg ~ C(2n, 0.24n) = 2^{2n H(0.12)} = 2^{1.06 n}
    #   dense linear-algebra cost ~ (2^{1.06n})^omega, omega in [2, 2.37]
    #   => 2^{2.1 n} .. 2^{2.5 n}  >>  rho = 2^{n/2} on a binary-field curve.
