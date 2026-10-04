#!/usr/bin/env python3
"""Coordinator re-derivation behind CORR-20260913-53739b.

Two copies of IDEA-20260913-191ed2 and of IDEA-20260913-8138a0 disagree on
their headline figures. This script decides each disagreement from the frozen
source's own formulas rather than from either copy, and prints every number the
correction record quotes so a later reader can re-run it and compare.

Nothing here is measured. Every quantity is an exact evaluation of a published
formula at stated parameters:

  eq. (11)  P(q, m, t, |V|) = 1 - (1 - 1/q)^K,  K ~ |V|^t / t!
            linearised to P ~ |V|^t / (q t!) when that ratio is o(1)
            -> at |V| = 2^k, q = 2^n, t = m:  1/P = m! 2^{n - mk}

  eq. (15)  stage1 = 2^k * (1/P) * n^{4 omega}          (single-term, Semaev)
            stage1 = 2^k * ((1/P) C(d_u) + C(d_s))      (two-term, IDEA-191ed2)
            with C(d) = n^{d omega} under Section 4.5.2's block solver

  eq. (16)  stage2 = 2^{k omega'}

No degree is measured or asserted anywhere in this file.
"""

import math
from math import ceil, expm1, lgamma, log, log2, sqrt

OMEGA = 3.0          # matches Semaev's Table 3
OMEGA_PRIME = 2.0    # stage-2 linear algebra; every conclusion below is checked
                     # against omega' in {1, 2, 2.376, 3} and is invariant


def log2_factorial(m: float) -> float:
    return lgamma(m + 1) / log(2)


def log2_sum(*terms: float) -> float:
    """log2 of a sum given each addend's log2, without overflow."""
    top = max(terms)
    return top + log2(sum(2.0 ** (term - top) for term in terms))


def inv_yield_log2(n: int, m: int, k: float, convention: str) -> float:
    """log2(1/P) under each of the three conventions in play.

    m_only    1/P = m!                 -- what ledger/proposals/IDEA-191ed2 charges
    eq11      1/P = m! 2^{n-mk}        -- eq. (11) linearised, the draft's charge
    eq11exact 1/P from 1-(1-1/q)^K     -- eq. (11) unlinearised, as a control
    """
    if convention == "m_only":
        return log2_factorial(m)
    if convention == "eq11":
        return log2_factorial(m) + (n - m * k)
    if convention == "eq11exact":
        lam_log2 = (m * k - n) - log2_factorial(m)
        if lam_log2 < -30:      # P ~ lambda; the linearisation is exact here
            return -lam_log2
        if lam_log2 > 10:       # P ~ 1
            return 0.0
        return -log2(-expm1(-(2.0 ** lam_log2)))
    raise ValueError(convention)


def total_log2(n: int, m: int, d_s: int, convention: str,
               omega_prime: float = OMEGA_PRIME, ceiled: bool = True,
               d_u: int = 4) -> tuple[float, float]:
    k = ceil(n / m) if ceiled else n / m
    stage1 = log2_sum(
        k + inv_yield_log2(n, m, k, convention) + d_u * OMEGA * log2(n),
        k + d_s * OMEGA * log2(n),
    )
    return log2_sum(stage1, k * omega_prime), k


def optimum(n: int, d_s: int, convention: str, **kw) -> tuple[float, int, float]:
    best = None
    for m in range(2, n + 1):
        value, k = total_log2(n, m, d_s, convention, **kw)
        if best is None or value < best[0]:
            best = (value, m, k)
    return best


def crossover(d_s: int, convention: str, hi: int = 900, **kw) -> int | None:
    """Smallest n at which the re-optimised total drops below 2^{n/2}."""
    for n in range(50, hi):
        if optimum(n, d_s, convention, **kw)[0] < n / 2.0:
            return n
    return None


def degree_floor(n: int, m: int, omega: float) -> float:
    """IDEA-8138a0 (C5): d >= [c - 1/c'] sqrt(n ln n) / (omega log2(n(m-1)))."""
    c_prime = sqrt(2 * log(2))
    c = 2 / c_prime
    return (c - 1 / c_prime) * sqrt(n * log(n)) / (omega * log2(n * (m - 1)))


def main() -> None:
    c_prime = sqrt(2 * log(2))
    c = 2 / c_prime
    print(f"c' = sqrt(2 ln 2) = {c_prime:.6f}   c = 2/c' = {c:.6f}   "
          f"c - 1/c' = {c - 1 / c_prime:.6f} (= c/2)")

    print("\n### 1. Semaev's own single-term stage-1 at his Table 3 cell")
    print(f"  n=571 m=12 k=48, 2^k m! n^{{4 omega}}: log2 = "
          f"{48 + log2_factorial(12) + 12 * log2(571):.2f}   (record quotes 186.7)")

    print("\n### 2. IDEA-20260913-191ed2: the two copies, each under its own charge")
    for convention, whose in (("m_only", "ledger/proposals copy"),
                              ("eq11", "coordination/ideation draft")):
        s1 = [log2_sum(48 + inv_yield_log2(571, 12, 48, convention) + 12 * log2(571),
                       48 + d * OMEGA * log2(571)) for d in (4, 5, 6, 7)]
        print(f"  {convention:5s} ({whose})")
        print(f"    stage1 at m=12,k=48, d_s=4/5/6/7: "
              + " / ".join(f"{v:.1f}" for v in s1))
        for d_s in (4, 5, 6):
            value, m, k = optimum(571, d_s, convention)
            print(f"    d_s={d_s}: re-optimised total {value:.1f} at m={m}, k={k:.0f}")
        print("    crossover with 2^(n/2): "
              + " / ".join(f"d_s={d}: n*={crossover(d, convention)}" for d in (4, 5, 6, 7)))

    print("\n### 3. Is the linearisation of eq. (11) safe at the shifted optimum?")
    for d_s in (4,):
        for n in (163, 233, 283, 409, 571, 1000):
            lin = optimum(n, d_s, "eq11")
            exact = optimum(n, d_s, "eq11exact")
            m, k = lin[1], ceil(n / lin[1])
            lam_log2 = (m * k - n) - log2_factorial(m)
            print(f"  n={n:4d}: linearised {lin[0]:.4f} at m={lin[1]}, "
                  f"exact {exact[0]:.4f} at m={exact[1]}, "
                  f"log2(lambda)={lam_log2:.2f} (needs << 0)")

    print("\n### 4. Under UN-CEILED k the two charges must agree exactly (slack is 0)")
    for n in (283, 571):
        a = optimum(n, 4, "m_only", ceiled=False)[0]
        b = optimum(n, 4, "eq11", ceiled=False)[0]
        print(f"  n={n}: m_only={a:.6f}  eq11={b:.6f}  |difference|={abs(a - b):.2e}")

    print("\n### 5. How much does the m!-only charge overcharge at integer k?")
    import statistics
    gaps, argmin_differs, disagree_vs_rho = [], 0, []
    for n in range(100, 1001):
        a = optimum(n, 4, "m_only")
        b = optimum(n, 4, "eq11")
        gaps.append(a[0] - b[0])
        argmin_differs += a[1] != b[1]
        if (a[0] < n / 2.0) != (b[0] < n / 2.0):
            disagree_vs_rho.append(n)
    print(f"  n in [100,1000], d_s=4: mean {statistics.mean(gaps):.2f} bits, "
          f"median {statistics.median(gaps):.2f}, min {min(gaps):.2f}, "
          f"max {max(gaps):.2f}, sd {statistics.pstdev(gaps):.2f}")
    print(f"  optimal m differs at {argmin_differs}/901 values of n")
    print(f"  the two charges disagree on whether the method beats 2^(n/2) at "
          f"{len(disagree_vs_rho)} values of n: "
          f"{min(disagree_vs_rho)}-{max(disagree_vs_rho)}")

    print("\n### 6. omega'-invariance of the d_s=6 optimum (ledger charge)")
    for omega_prime in (1.0, 2.0, 2.376, 3.0):
        value, m, k = optimum(571, 6, "m_only", omega_prime=omega_prime)
        print(f"  omega'={omega_prime}: m={m}, k={k:.0f}, total={value:.2f}")
    print("  flatness around it (is m=21/k=28 a near-tie?):")
    for m in (17, 18, 19, 20, 21):
        value, k = total_log2(571, m, 6, "m_only")
        print(f"    m={m} k={k:.0f} total={value:.2f}")

    print("\n### 7. IDEA-20260913-8138a0: the required-degree floor is route-dependent")
    print("  n=571, omega=3, floor by m and the coefficient it implies:")
    for m in (2, 3, 12, 62, 571):
        value = degree_floor(571, m, 3.0)
        print(f"    m={m:4d}: d >= {value:.4f}  implied coefficient "
              f"{value / sqrt(571 / log(571)):.5f}  "
              f"log2(n(m-1))/log2(n) = {log2(571 * (m - 1)) / log2(571):.3f}")
    print("  the record's named route m = n/log2(n), as n grows:")
    for n in (571, 10 ** 4, 10 ** 6, 10 ** 10, 10 ** 20):
        m = max(2, round(n / log2(n)))
        value = degree_floor(n, m, 3.0)
        print(f"    n={n:<22d} m={m:<20d} implied coefficient "
              f"{value / sqrt(n / log(n)):.5f}")
    print("  and at omega = 2.376, the two bracketing routes:")
    for m, label in ((2, "m = 2      "), (571, "m = n = 571")):
        value = degree_floor(571, m, 2.376)
        print(f"    {label}: d >= {value:.4f}  implied coefficient "
              f"{value / sqrt(571 / log(571)):.5f}")


if __name__ == "__main__":
    main()
