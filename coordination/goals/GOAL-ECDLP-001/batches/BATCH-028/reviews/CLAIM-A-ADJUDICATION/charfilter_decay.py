#!/usr/bin/env python3
"""
The composition's empirical input.

Theorem A (O2_fourier_obstruction.md) : eps_+ <= 1/M + Lambda(h),  no factor M.
Theorem 3 (O2_derivation_attempt.md)  : max_psi |T_psi| <= c1*D*p^{-1/2} + c2*D/N
                                        for the CHARACTER-FILTER class.

Composing them predicts, for a character filter with bounded complexity D,

    Lambda(h)  =  O( p^{-1/2} )      -- NOT merely o(1)

which is what lets a Wagner level with M ~ p^{1/3} be closed.  Theorem 3's own
route, using the M-lossy (star), only reaches M <= p^{1/4} and leaves j=2 open.

This script measures Lambda for genuine character filters (F1 family C) across
three orders of magnitude in p and fits the decay exponent.  If Weil governs
Lambda, the fitted exponent is ~0.5.
"""
import numpy as np
import sys

sys.path.insert(0, ".")
from fourier_obstruction import is_prime, curve_order, dlog_table, padd


def legendre(v, p):
    if v % p == 0:
        return 0
    return 1 if pow(v, (p - 1) // 2, p) == 1 else -1


def prime_order_curve_near(p_target, max_curves=400):
    p = p_target
    while not is_prime(p):
        p += 1
    tried = 0
    for a in range(0, 20):
        for b in range(1, 20):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            tried += 1
            if tried > max_curves:
                return None
            n = curve_order(p, a, b)
            if is_prime(n):
                return p, a, b, n
    return None


def char_filter(pts, p, offsets):
    """F1 family C: h(P) = ( chi(x-e) )_{e in offsets},  M = 2^r.

    Bit is 0/1 from the quadratic character; x=0 for the identity point.
    Complexity D is bounded (each x-e has 2 zeros/poles on E), independent of p.
    """
    r = len(offsets)
    out = np.zeros(len(pts), dtype=np.int64)
    for i, P in enumerate(pts):
        x = 0 if P is None else P[0]
        v = 0
        for j, e in enumerate(offsets):
            v |= (1 if legendre(x - e, p) >= 0 else 0) << j
        out[i] = v
    return out, 2 ** r


def Lambda(hv, M):
    """max_{t != 0} max_xi |ghat_t(xi)| -- the quantity Theorem A consumes."""
    N = len(hv)
    best = 0.0
    for t in range(1, M):
        g = np.exp(2j * np.pi * t * hv / M)
        ghat = np.fft.fft(g) / N
        best = max(best, float(np.abs(ghat).max()))
    return best


def main():
    targets = (523, 1033, 2063, 4111, 8219, 16417, 32779, 65539)
    for r, offsets in ((1, (0,)), (2, (0, 1)), (3, (0, 1, 2))):
        rows = []
        print(f"\n=== character filter, r={r} bits, offsets={offsets}, M={2**r} ===")
        print(f"{'p':>8} {'N':>8} {'M':>4} {'Lambda':>10} {'p^-1/2':>10} {'L*sqrt(p)':>10}")
        for t in targets:
            found = prime_order_curve_near(t)
            if not found:
                continue
            p, a, b, N = found
            G0, pts = dlog_table(p, a, b, N)
            hv, M = char_filter(pts, p, offsets)
            L = Lambda(hv, M)
            rows.append((p, L))
            print(f"{p:>8} {N:>8} {M:>4} {L:>10.6f} {1/np.sqrt(p):>10.6f} "
                  f"{L*np.sqrt(p):>10.4f}")
        A = np.array(rows)
        slope = np.polyfit(np.log(A[:, 0]), np.log(A[:, 1]), 1)[0]
        print(f"  fitted decay exponent: Lambda ~ p^({slope:+.4f})   "
              f"[Weil predicts -0.5000]")

    print()
    print("=" * 78)
    print("CONSEQUENCE (Theorem A + measured/Weil Lambda ~ p^-1/2):")
    print("  Wagner level gain = eps*M <= 1 + M*Lambda ~ 1 + M*p^-1/2")
    print("  p^{o(1)} gain  <=>  M <= p^{1/2-o(1)}")
    print()
    print(f"{'j':>3} {'M ~ p^(1/(j+1))':>17} {'exponent(m=16)':>15} "
          f"{'Thm3 via (star)':>17} {'ThmA + Weil':>13}")
    for j in (2, 3, 4):
        e = 1.0 / (j + 1)
        expo = (2 ** j + 16) / (16 * (j + 1))
        print(f"{j:>3} {'p^'+format(e,'.4f'):>17} {expo:>15.4f} "
              f"{('CLOSED' if e <= 0.25 else 'open'):>17} "
              f"{('CLOSED' if e < 0.5 else 'open'):>13}")


if __name__ == "__main__":
    main()
