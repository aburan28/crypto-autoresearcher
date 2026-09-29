#!/usr/bin/env python3
"""COUNTEREXAMPLE CERTIFICATE (TASK-20260904-ed0e8f, red team).

Claim refuted: H-PFDR-4148b8 (D4)/(D6) and prediction P2/P3, in the clause
'fall_dim(d_ff) = m [C(s,a_0) - C(s,a_0+e)]', asserted (quantifier_order) for
ALL p > 3, ALL s with 2^{m-1} <= s and 2^s <= p, ALL non-singular E/F_p and
ALL affine targets x_R.

Instance:  m = 2, d = 2, s = 2, p = 13, E: y^2 = x^3 + 12 x + 3, x_R = 11.
Predicted: (d_ff, fall_dim) = (5, 4).      Actual: (5, 3).

Self-contained: standard library only, ~60 lines, no import from this review's
other scripts, from harness/, or from the experiment package.  Prints PASS if
the counterexample re-checks.  A second instance (p = 19, a = 2, b = 15,
x_R = 9) is checked the same way.
"""
from itertools import combinations


def check(p, a, b, xR, s=2, verbose=True):
    m, e, n = 2, 2, 2 * s
    a0 = (s - e) // 2 + 1
    delta = 4
    d_ff_pred = m * e + a0                      # 5
    from math import comb
    fall_pred = m * (comb(s, a0) - comb(s, a0 + e))   # 4

    assert (4 * a ** 3 + 27 * b ** 2) % p != 0, "curve is singular"
    assert a % p and b % p, "j in {0, 1728}"
    assert 2 ** s <= p, "2^s <= p violated"

    # value of the digit-presented generator at the 0/1 point omega:
    # ell_k = sum_i 2^i a_{k,i}; variable index of a_{k,i} is k*s + i.
    def S3(x1, x2, x3):
        return ((x1 - x2) ** 2 * x3 ** 2
                - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
                + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p

    def val(omega):
        u1 = sum(((omega >> i) & 1) << i for i in range(s))
        u2 = sum(((omega >> (s + i)) & 1) << i for i in range(s))
        return S3(u1, u2, xR)

    pts = [val(w) for w in range(1 << n)]
    N_sol = sum(1 for v in pts if v == 0)

    # The generator as an element of B = F_p[a]/(a^2-a) is the unique
    # multilinear interpolation of `pts`; the layer-D rows are the functions
    # omega -> mu(omega) * g(omega).  Ranks are taken on the 2^n point values,
    # which is the same rank as on the monomial basis (Moebius transform is
    # invertible).  top_rank(D) uses the degree-D part, obtained by Moebius.
    def moebius(vals):
        c = list(vals)
        for i in range(n):
            for w in range(1 << n):
                if (w >> i) & 1:
                    c[w] = (c[w] - c[w ^ (1 << i)]) % p
        return c

    def rank(rows):
        piv, r = {}, 0
        for row in rows:
            row = {k: v % p for k, v in enumerate(row) if v % p}
            while row:
                col = min(row)
                if col in piv:
                    f = row[col]
                    for k, v in piv[col].items():
                        nv = (row.get(k, 0) - f * v) % p
                        if nv:
                            row[k] = nv
                        else:
                            row.pop(k, None)
                else:
                    inv = pow(row[col], p - 2, p)
                    piv[col] = {k: (v * inv) % p for k, v in row.items()}
                    r += 1
                    break
        return r

    profile = []
    for D in range(delta, n + 2):
        k = D - delta
        if k > n:
            break
        rows_full, rows_top = [], []
        for combo in combinations(range(n), k):
            mask = 0
            for i in combo:
                mask |= 1 << i
            prod = [(pts[w] if (mask & ~w) == 0 else 0) for w in range(1 << n)]
            rows_full.append(prod)
            coeffs = moebius(prod)
            rows_top.append([coeffs[w] if bin(w).count("1") == D else 0
                             for w in range(1 << n)])
        fr, tr = rank(rows_full), rank(rows_top)
        profile.append((D, len(rows_full), fr, tr, fr - tr))
    d_ff = next((D for (D, _, fr, tr, fd) in profile if fd > 0), None)
    fall = next((fd for (D, _, fr, tr, fd) in profile if fd > 0), None)
    if verbose:
        print(f"p={p} a={a} b={b} x_R={xR} s={s}: N_sol={N_sol} "
              f"profile(D,rows,full,top,fall)={profile}")
        print(f"   predicted (d_ff, fall_dim) = ({d_ff_pred}, {fall_pred});"
              f"  actual = ({d_ff}, {fall})")
    return d_ff == d_ff_pred and fall != fall_pred


if __name__ == "__main__":
    ok1 = check(13, 12, 3, 11)
    ok2 = check(19, 2, 15, 9)
    print("PASS: both instances have the predicted d_ff and a fall_dim "
          "different from the frozen value" if (ok1 and ok2) else "FAIL")
