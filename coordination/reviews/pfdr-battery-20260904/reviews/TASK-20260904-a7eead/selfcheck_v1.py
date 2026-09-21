#!/usr/bin/env python3
"""Anti-artifact self-checks for the V1 re-derivation instrument (own code).

(a) which columns of degree <= 8 are NOT reached by any product row
(b) POSITIVE CONTROL on my own meter: two quartics sharing a quadratic factor
    (h q1, h q2) have the non-Koszul syzygy q2 (h q1) - q1 (h q2) = 0 at
    multiplier degree 2, so deficit must be NONZERO from D = 6 on.
(c) NEGATIVE CONTROL: two independent random quartics of the same supports
    -> deficit must be 0 (Koszul only).
"""
import random
import numpy as np
import rederive_v1 as R

P = R.P
cols = R.monomials_upto(8)
cidx = {m: i for i, m in enumerate(cols)}


def build_and_rank(E1, E2, Dlist=(5, 6, 7, 8)):
    mults = R.monomials_upto(4)
    rows, meta, zero = [], [], 0
    for m in mults:
        for gi, E in ((1, E1), (2, E2)):
            pr = R.pmul({m: 1}, E)
            if not pr:
                zero += 1
                continue
            v = np.zeros(len(cols), dtype=np.int64)
            for mo, c in pr.items():
                v[cidx[mo]] = c
            rows.append(v)
            meta.append(R.deg(m))
    marks = {sum(1 for d in meta if d <= D - 4): D for D in Dlist}
    ranks, _ = R.prefix_ranks(rows, marks)
    out = {}
    for D in Dlist:
        n = sum(1 for d in meta if d <= D - 4)
        k = 1 if D >= 8 else 0
        out[D] = (n, ranks[D], k, n - ranks[D] - k)
    sup = set()
    for v in rows:
        sup.update(int(c) for c in np.nonzero(v)[0])
    return out, zero, sup


# ---- (a) unreached columns on a real instance ------------------------------
x1, x2, x3 = R.leaf(1), R.leaf(2), R.leaf(3)
E1 = R.S3(x1, x2, {R.U: 1}, 2975, 3349)
E2 = R.S3({R.U: 1}, x3, R.const(2292), 2975, 3349)
res, zero, sup = build_and_rank(E1, E2)
missing = [cols[i] for i in range(len(cols)) if i not in sup]
print("(a) columns of deg<=8 unreached by any row:", len(missing))
from collections import Counter
print("    by (digit-degree, u-exponent):",
      sorted(Counter((bin(m[0]).count('1'), m[1]) for m in missing).items()))
print("    by total degree:",
      sorted(Counter(R.deg(m) for m in missing).items()))

# ---- (b) positive control: planted non-Koszul syzygy ------------------------
rng = random.Random(20260904)


def rand_form(vars_masks, use_u, degree):
    """random element supported on monomials of total degree <= `degree`"""
    f = {}
    for m in R.monomials_upto(degree):
        if not use_u and m[1] > 0:
            continue
        f[m] = rng.randrange(1, P)
    return f


h = rand_form(None, True, 2)          # random quadratic in digits and u
q1 = rand_form(None, True, 2)
q2 = rand_form(None, True, 2)
F1, F2 = R.pmul(h, q1), R.pmul(h, q2)
print("(b) planted-syzygy system: deg F1 =", max(R.deg(m) for m in F1),
      " deg F2 =", max(R.deg(m) for m in F2))
resb, zb, _ = build_and_rank(F1, F2)
for D in (5, 6, 7, 8):
    print(f"    D={D}: rows={resb[D][0]} rank={resb[D][1]} "
          f"koszul={resb[D][2]} deficit={resb[D][3]}")

# ---- (c) negative control: two independent random quartics -----------------
G1 = rand_form(None, True, 4)
G2 = rand_form(None, True, 4)
resc, zc, _ = build_and_rank(G1, G2)
print("(c) two independent random <=quartics (dense support):")
for D in (5, 6, 7, 8):
    print(f"    D={D}: rows={resc[D][0]} rank={resc[D][1]} "
          f"koszul={resc[D][2]} deficit={resc[D][3]}")
