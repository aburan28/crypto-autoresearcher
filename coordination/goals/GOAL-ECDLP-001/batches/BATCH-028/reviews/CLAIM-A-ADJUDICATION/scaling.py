#!/usr/bin/env python3
"""
Scaling of Delta(h) and delta(h) for the x-coordinate filter on prime-order
E(F_p).  These are the two quantities the obstruction theorem reduces the
whole (h, f, M) sweep to.

Model under test: for a "structureless" h the Fourier coefficients behave like
independent complex values of scale N^{-1/2}, so their MAXIMUM over ~M*N of
them should grow like sqrt(log(M*N)/N), not like N^{-1/2} exactly.  We fit both.
"""
import numpy as np
from fourier_obstruction import (is_prime, curve_order, dlog_table,
                                 fourier_quantities, h_x_mod, h_sha)


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


def main():
    M = 16
    rows = []
    for p_target in (503, 1103, 1901, 3847, 7873, 15013, 30011, 60013, 120017):
        found = prime_order_curve_near(p_target)
        if not found:
            print(f"  (no prime-order curve near {p_target})")
            continue
        p, a, b, N = found
        G0, pts = dlog_table(p, a, b, N)
        Dx, dx, _, _ = fourier_quantities(h_x_mod(pts, p, M), M)
        Ds, ds, _, _ = fourier_quantities(h_sha(pts, M), M)
        rows.append((N, Dx, dx, Ds, ds))
        print(f"  N={N:>7}  x-coord: Delta={Dx:.6f} delta={dx:.6f}   "
              f"sha: Delta={Ds:.6f} delta={ds:.6f}")

    A = np.array(rows)
    N = A[:, 0]
    print()
    print(f"{'N':>8} {'Delta_x':>10} {'D*sqrtN':>9} {'D/sqrt(logMN/N)':>16} "
          f"{'delta_x':>10} {'d*sqrtN':>9}")
    for N_, Dx, dx, Ds, ds in rows:
        pred = np.sqrt(np.log(M * N_) / N_)
        print(f"{int(N_):>8} {Dx:>10.6f} {Dx*np.sqrt(N_):>9.3f} "
              f"{Dx/pred:>16.3f} {dx:>10.6f} {dx*np.sqrt(N_):>9.3f}")

    # log-log slope of Delta vs N
    for name, col in (("Delta_x", 1), ("delta_x", 2), ("Delta_sha", 3), ("delta_sha", 4)):
        s = np.polyfit(np.log(N), np.log(A[:, col]), 1)[0]
        print(f"  log-log slope of {name:<10} vs N : {s:+.4f}   "
              f"(pure N^-1/2 would be -0.5000)")

    print()
    print("CONSEQUENCE for a Wagner 2^j-tree, which needs M ~ N^{1/(j+1)}:")
    print("  affine f    : need Delta >= 3/M   -> M >= 3/Delta ~ 0.9*sqrt(N)")
    print("  arbitrary f : need delta >= 3/M^2 -> M >= sqrt(3/delta) ~ N^{1/4}")
    print()
    print(f"{'j':>3} {'M ~ N^(1/(j+1))':>16} {'exponent':>9} {'affine f':>12} {'arbitrary f':>14}")
    for j in (2, 3, 4):
        e_M = 1.0 / (j + 1)
        # closed iff required correlation exceeds what a structureless h has (~N^-1/2)
        aff_closed = e_M < 0.5          # need M >~ sqrt(N)
        arb_closed = 2 * e_M < 0.5      # need M >~ N^{1/4}
        m_exp = (2 ** j + 16) / (16 * (j + 1))
        print(f"{j:>3} {'N^'+format(e_M,'.4f'):>16} {m_exp:>9.4f} "
              f"{'CLOSED' if aff_closed else 'open':>12} "
              f"{'CLOSED' if arb_closed else 'OPEN':>14}")


if __name__ == "__main__":
    main()
