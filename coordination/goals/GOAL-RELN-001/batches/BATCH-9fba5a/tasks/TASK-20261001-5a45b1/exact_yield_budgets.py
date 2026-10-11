"""NON-PROTOCOL design computation for EXP-RELN-dc761f (TASK-20261001-5a45b1).

Deterministic and label-free: no SHA256 seed label, no random draw, no
attempt. For each frozen EXP-RELN-c5a377 fixture (prime-order curves, so every
R = a G + b Q lies in the scanned group) it enumerates every unordered pair
of scan points and assigns each group element R != O the class of its FIRST
decomposition in scan order (the v4 generator's rule, contract rule G-4), then
computes the exact per-attempt LP-edge yield and the frozen budgets

    A_kappa = ceil(kappa * (n_lp + 1) / y_edge),   y_edge = n_edge / q,

for kappa in {1/4, 1/2, 1, 2}. Only class COUNTS are output; no graph, cycle
or degree statistic of the pair map is computed.

Usage: python3 exact_yield_budgets.py <ic_leads_fixtures_v2.json> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction

FIXTURE_SHA256 = "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"
KAPPAS = [Fraction(1, 4), Fraction(1, 2), Fraction(1), Fraction(2)]


def iroot_ceil(n: int, num: int, den: int) -> int:
    """Least B >= 0 with B^den >= n^num (exact ceil(n^{num/den}))."""
    target = n ** num
    lo, hi = 0, 1
    while hi ** den < target:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if mid ** den >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def sqrt_mod(r: int, p: int) -> int | None:
    if r == 0:
        return 0
    if pow(r, (p - 1) // 2, p) != 1:
        return None
    # Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, x = s, pow(z, q, p), pow(r, q, p), pow(r, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, x = i, b * b % p, t * b * b % p, x * b % p
    return x


def add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def fixture_counts(fx: dict) -> dict:
    p, a, b, q = fx["p"], fx["a"], fx["b"], fx["N"]
    B, B2 = iroot_ceil(p, 1, 5), iroot_ceil(p, 2, 5)
    S, fb, lp = [], 0, 0
    for x in range(B2):
        r = (x * x * x + a * x + b) % p
        y = sqrt_mod(r, p)
        if y is None:
            continue
        if y == 0:
            S.append((x, 0))
        else:
            S.extend(sorted([(x, y), (x, p - y)]))
        if x < B:
            fb += 1
        else:
            lp += 1
    first = {}  # R -> class of first decomposition in scan order
    for i in range(len(S)):
        Pi = S[i]
        for k in range(i, len(S)):
            R = add(Pi, S[k], a, p)
            if R is None or R in first:
                continue
            n_lp = (Pi[0] >= B) + (S[k][0] >= B)
            first[R] = ("full", "lp1", "lp2")[n_lp]
    cnt = {"full": 0, "lp1": 0, "lp2": 0}
    for c in first.values():
        cnt[c] += 1
    n_edge = cnt["lp1"] + cnt["lp2"]
    out = {
        "fixture_id": f"b{fx['bits']}-s{fx['seed']}", "p": p, "q": q,
        "B": B, "B2": B2, "L_fb_count": fb, "L_q": iroot_ceil(q, 1, 5),
        "n_lp": lp, "scan_size": len(S),
        "R_with_decomposition": len(first), "R_full": cnt["full"],
        "R_lp1": cnt["lp1"], "R_lp2": cnt["lp2"], "n_edge": n_edge,
        "y_edge": n_edge / q, "lp1_share": cnt["lp1"] / n_edge,
        "budgets": {},
    }
    for kap in KAPPAS:
        # ceil(kap * (n_lp+1) * q / n_edge) in exact rational arithmetic
        val = kap * (lp + 1) * q / n_edge
        A = -((-val.numerator) // val.denominator)
        out["budgets"][str(kap)] = {"attempts": A,
                                    "expected_edges": float(A * Fraction(n_edge, q))}
    return out


def main():
    path, out_path = sys.argv[1], sys.argv[2]
    raw = open(path, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != FIXTURE_SHA256:
        raise SystemExit(f"fixture sha256 mismatch: {digest}")
    fixtures = json.loads(raw)["EXP-RELN-c5a377"]
    rows = [fixture_counts(f) for f in fixtures]
    json.dump({"label": "NON-PROTOCOL design computation (label-free, deterministic)",
               "fixture_file_sha256": digest, "rows": rows}, open(out_path, "w"), indent=1)
    for r in rows:
        print(r["fixture_id"], r["B"], r["B2"], r["L_fb_count"], r["L_q"], r["n_lp"],
              r["scan_size"], f"{r['y_edge']:.5f}", f"{r['lp1_share']:.3f}",
              [v["attempts"] for v in r["budgets"].values()])


if __name__ == "__main__":
    main()
