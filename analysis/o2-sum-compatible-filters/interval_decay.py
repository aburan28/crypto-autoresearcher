#!/usr/bin/env python3
"""
Falsification check for the additive-character completion.

O2_derivation_attempt.md section 7.6 item 2 lists interval / bit-window /
congruence filters -- F1 families A, B, I, J -- as NOT covered, sketches
additive-character completion, and does not carry it out.  It calls this the
largest missing piece.

The claimed argument, fibred exactly as the multiplicative case:

    sum_{P,Q} e_p(a x(P) + b x(Q) + c x(P+Q))
        = sum_R e_p(c x(R)) * sum_P e_p(a x(P) + b x(R-P))

The inner sum is a ONE-VARIABLE additive character sum of the rational function
F_R(P) = a x(P) + b x(R-P) on E, so Weil applies unless F_R is Artin-Schreier
degenerate, i.e. constant in P.  x(P) has a double pole at O and x(R-P) a double
pole at P=R, so for a,b nonzero and R != O the combination has poles at two
distinct places and cannot be constant.  Degeneracy therefore survives only on a
BOUNDED exceptional set, as in the multiplicative case, and completion costs
sum|c_alpha| = O(log p).

PREDICTION, if that is right:   Lambda = O(p^{-1/2 + o(1)})  for families A/B/I/J.

DISCRIMINATING CONTROL.  The dlog-interval filter of Proposition 2 is the SAME
shape -- an interval pullback -- but of the discrete log rather than of x.  It
has Lambda ~ 1/2 with NO decay.  If the apparatus is sound it must separate
these two cleanly: x-intervals decay at p^{-1/2}, the dlog-interval stays flat.
That separation is the cost clause made visible: x(P) is computable from P, the
dlog is not.

A null is included: SHA-256 of x, which is F1's in-arm null (family H).
"""
import hashlib
import sys

import numpy as np

sys.path.insert(0, ".")
from fourier_obstruction import is_prime, curve_order, dlog_table


def Lambda(hv, M):
    """max_{t != 0} max_xi |ghat_t(xi)| -- the quantity Theorem A consumes."""
    N = len(hv)
    return max(float(np.abs(np.fft.fft(np.exp(2j * np.pi * t * hv / M)) / N).max())
               for t in range(1, M))


def find_curve(p_target):
    p = p_target
    while not is_prime(p):
        p += 1
    for a in range(0, 30):
        for b in range(1, 30):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            n = curve_order(p, a, b)
            if is_prime(n):
                return p, a, b, n
    return None


def build(kind, xs, p, N, M):
    """Filter families. xs[i] = x-coordinate of [i]G0 (0 at the identity)."""
    if kind == "A: floor(Mx/p)":          # interval pullback of x
        return (xs.astype(np.int64) * M) // p
    if kind == "I: x mod M":              # congruence filter
        return xs % M
    if kind == "B: low bits":             # bit window, low end
        return xs & (M - 1)
    if kind == "B: high bits":            # bit window, top end
        return (xs >> max(0, int(p).bit_length() - int(M).bit_length())) % M
    if kind == "B: mid bits":
        sh = max(0, (int(p).bit_length() - int(M).bit_length()) // 2)
        return (xs >> sh) % M
    if kind == "H: sha(x) [null]":
        return np.array([int(hashlib.sha256(str(int(v)).encode()).hexdigest(), 16) % M
                         for v in xs], dtype=np.int64)
    if kind == "P2: dlog-int [ctrl]":     # Proposition 2 -- must NOT decay
        return (np.arange(N, dtype=np.int64) * M) // N
    raise ValueError(kind)


KINDS = ("A: floor(Mx/p)", "I: x mod M", "B: low bits", "B: high bits",
         "B: mid bits", "H: sha(x) [null]", "P2: dlog-int [ctrl]")


def main():
    targets = (523, 1033, 2063, 4111, 8219, 16417, 32779, 65539)
    curves = []
    for t in targets:
        f = find_curve(t)
        if f:
            p, a, b, N = f
            _, pts = dlog_table(p, a, b, N)
            xs = np.array([0 if P is None else P[0] for P in pts], dtype=np.int64)
            curves.append((p, N, xs))

    for M in (4, 16):
        print(f"\n{'='*82}\nM = {M}\n{'='*82}")
        print(f"{'filter':>22} " + " ".join(f"{p:>8}" for p, _, _ in curves)
              + f"  {'alpha':>7}")
        for kind in KINDS:
            row, ps = [], []
            for p, N, xs in curves:
                hv = build(kind, xs, p, N, M)
                if len(np.unique(hv)) < M:
                    row.append(float("nan")); ps.append(p); continue
                row.append(Lambda(hv, M)); ps.append(p)
            arr = np.array(row)
            ok = ~np.isnan(arr)
            alpha = (np.polyfit(np.log(np.array(ps)[ok]), np.log(arr[ok]), 1)[0]
                     if ok.sum() >= 3 else float("nan"))
            print(f"{kind:>22} " + " ".join(f"{v:>8.5f}" for v in arr)
                  + f"  {alpha:>+7.3f}")

    print(f"\n{'='*82}")
    print("alpha is the fitted exponent in Lambda ~ p^alpha.")
    print("  Weil / additive completion predicts alpha ~ -0.5 for A, B, I.")
    print("  Proposition 2 requires alpha ~ 0.0 for the dlog-interval control.")
    print("  A flat control beside decaying filters is the cost clause made visible.")


if __name__ == "__main__":
    main()
