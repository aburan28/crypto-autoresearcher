#!/usr/bin/env python3
"""V1 BLIND RE-DERIVATION -- TASK-20260904-a7eead.

Implements review_plan.blind_rederivation.quantity of
ledger/handoffs/TASK-20260904-a7eead.yaml from its statement alone.

Ring   R = F_p[a_{k,i} : k in 1..3, i in 0..2][u] / (a_{k,i}^2 - a_{k,i})
       nine squarefree digit variables + one FREE variable u.
       deg(monomial) = #digit variables + u-exponent.
Leaves x_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}.
S_3(X1,X2,X3) = (X1-X2)^2 X3^2
                - 2((X1+X2)(X1 X2 + A) + 2B) X3
                + (X1 X2 - A)^2 - 4B(X1+X2)
E1 = S_3(x1, x2, u),  E2 = S_3(u, x3, x_R), both reduced in R.
rows(D)    = { m E_i : i in {1,2}, m a monomial of R with deg m <= D-4 }
             (CUMULATIVE), zero products dropped and counted
columns(D) = all monomials of R of total degree <= D
rank(D)    = rank over F_p of the row set on those columns
koszul(D)  = 1 if D >= 8 else 0
deficit(D) = rows(D) - rank(D) - koszul(D)

NO import of harness/macaulay_fp; no producer artifact was read.
Rank engine: own prefix-incremental echelon elimination over F_p (numpy int64
carrier, exact modular arithmetic -- no floating point anywhere).
"""

import json
import sys
from itertools import combinations
from math import comb

import numpy as np

P = 4099
NDIG = 9  # index 3*(k-1)+i  for a_{k,i}
DIGITS_OF = {1: (0, 1, 2), 2: (3, 4, 5), 3: (6, 7, 8)}
DMAX = 8

# ---------------------------------------------------------------- ring ------
# monomial = (mask, e) : mask 9-bit squarefree digit set, e = exponent of u
ONE = (0, 0)
U = (0, 1)


def deg(m):
    return bin(m[0]).count("1") + m[1]


def pmul(f, g, p=P):
    out = {}
    for (m1, e1), c1 in f.items():
        for (m2, e2), c2 in g.items():
            k = (m1 | m2, e1 + e2)          # a^2 -> a  is exactly mask OR
            v = out.get(k, 0) + c1 * c2
            out[k] = v % p
    return {k: v for k, v in out.items() if v}


def padd(*fs, p=P):
    out = {}
    for f in fs:
        for k, c in f.items():
            v = (out.get(k, 0) + c) % p
            if v:
                out[k] = v
            else:
                out.pop(k, None)
    return out


def pscal(c, f, p=P):
    c %= p
    if c == 0:
        return {}
    return {k: (c * v) % p for k, v in f.items()}


def const(c, p=P):
    c %= p
    return {ONE: c} if c else {}


def leaf(k):
    """x_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}"""
    idx = DIGITS_OF[k]
    return {(1 << idx[i], 0): (1 << i) % P for i in range(3)}


def S3(X1, X2, X3, A, B):
    d = padd(X1, pscal(-1, X2))
    s = padd(X1, X2)
    pr = pmul(X1, X2)
    t1 = pmul(pmul(d, d), pmul(X3, X3))
    t2 = pscal(-2, pmul(padd(pmul(s, padd(pr, const(A))), const(2 * B)), X3))
    t3 = pmul(padd(pr, const(-A)), padd(pr, const(-A)))
    t4 = pscal(-4 * B, s)
    return padd(t1, t2, t3, t4)


# ------------------------------------------------------- monomial bases -----
def monomials_upto(D):
    """all monomials of R with total degree <= D, deterministic order
    (degree, mask, e)."""
    out = []
    for j in range(0, NDIG + 1):
        if j > D:
            break
        for cmb in combinations(range(NDIG), j):
            mask = 0
            for b in cmb:
                mask |= 1 << b
            for e in range(0, D - j + 1):
                out.append((mask, e))
    out.sort(key=lambda m: (deg(m), m[0], m[1]))
    return out


def count_monomials_upto(D):
    return sum(comb(NDIG, j) * (D - j + 1) for j in range(0, min(NDIG, D) + 1))


# ------------------------------------------------------------- rank ---------
def prefix_ranks(rows_dense, marks):
    """Process rows in order; return rank of each prefix in `marks`.
    Echelon elimination over F_P, exact."""
    basis = {}          # pivot column -> normalized row (np.int64)
    piv_sorted = []
    rank = 0
    out = {}
    marks = dict(marks)  # prefix_length -> label
    for i, v in enumerate(rows_dense, start=1):
        v = v.copy()
        for c in piv_sorted:
            f = int(v[c])
            if f:
                v -= f * basis[c]
                v %= P
        nz = np.nonzero(v)[0]
        if nz.size:
            c = int(nz[0])
            inv = pow(int(v[c]), P - 2, P)
            v = (v * inv) % P
            basis[c] = v
            piv_sorted.append(c)
            piv_sorted.sort()
            rank += 1
        if i in marks:
            out[marks[i]] = rank
    return out, rank


# ------------------------------------------------------------ driver --------
INSTANCES = [
    # curve_seed, A, B, target, u_planted, x_R
    (4101, 2975, 3349, 1, 3091, 2292),
    (4101, 2975, 3349, 2, 1163, 3046),
    (4102, 1174, 2571, 1, 1343, 2173),
    (4102, 1174, 2571, 2, 3446, 264),
    (4103, 743, 2019, 1, 1903, 197),
    (4103, 743, 2019, 2, 3423, 3278),
    (4104, 1581, 2498, 1, 3746, 3001),
    (4104, 1581, 2498, 2, 3376, 3105),
    (4105, 181, 2138, 1, 2028, 1263),
    (4105, 181, 2138, 2, 344, 3919),
    (4106, 3669, 1241, 1, 940, 1845),
    (4106, 3669, 1241, 2, 276, 1845),
]


def run_instance(A, B, xR, verbose=True):
    x1, x2, x3 = leaf(1), leaf(2), leaf(3)
    E1 = S3(x1, x2, {U: 1}, A, B)
    E2 = S3({U: 1}, x3, const(xR), A, B)
    dE1 = max(deg(m) for m in E1)
    dE2 = max(deg(m) for m in E2)

    cols = monomials_upto(DMAX)
    cidx = {m: i for i, m in enumerate(cols)}
    ncols = len(cols)

    mults = monomials_upto(DMAX - 4)          # deg m <= 4, sorted by degree
    rows_meta = []                            # (deg m, generator index)
    rows_dense = []
    zero_rows = 0
    for m in mults:
        for gi, E in ((1, E1), (2, E2)):
            prod = pmul({m: 1}, E)
            if not prod:
                zero_rows += 1
                continue
            v = np.zeros(ncols, dtype=np.int64)
            for mono, c in prod.items():
                v[cidx[mono]] = c
            rows_dense.append(v)
            rows_meta.append((deg(m), gi))

    # prefix marks: rows with deg m <= D-4
    marks = {}
    for D in (5, 6, 7, 8):
        n = sum(1 for (dm, _) in rows_meta if dm <= D - 4)
        marks[n] = D
    ranks, _ = prefix_ranks(rows_dense, marks)

    res = {}
    for D in (5, 6, 7, 8):
        nrows = sum(1 for (dm, _) in rows_meta if dm <= D - 4)
        ncols_D = count_monomials_upto(D)
        # support: columns actually hit by those rows
        sup = set()
        for v, (dm, _) in zip(rows_dense, rows_meta):
            if dm <= D - 4:
                for c in np.nonzero(v)[0]:
                    sup.add(int(c))
        kos = 1 if D >= 8 else 0
        res[D] = dict(rows=nrows, columns=ncols_D, support_columns=len(sup),
                      rank=ranks[D], koszul=kos,
                      deficit=nrows - ranks[D] - kos)
        # every row of a D-prefix must be supported inside columns of degree<=D
        maxdeg = max((deg(cols[c]) for c in sup), default=0)
        assert maxdeg <= D, (D, maxdeg)

    # --- independent check of the Koszul baseline: exhibit the relation ------
    # sum_m c_{E2}(m) (m E1)  -  sum_m c_{E1}(m) (m E2)  == 0
    acc = np.zeros(ncols, dtype=np.int64)
    rowmap = {}
    k = 0
    for m in mults:
        for gi, E in ((1, E1), (2, E2)):
            prod = pmul({m: 1}, E)
            if not prod:
                continue
            rowmap[(m, gi)] = k
            k += 1
    kvec = np.zeros(len(rows_dense), dtype=np.int64)
    for m, c in E2.items():
        kvec[rowmap[(m, 1)]] = (kvec[rowmap[(m, 1)]] + c) % P
    for m, c in E1.items():
        kvec[rowmap[(m, 2)]] = (kvec[rowmap[(m, 2)]] - c) % P
    for j, cf in enumerate(kvec):
        if cf:
            acc += int(cf) * rows_dense[j]
            acc %= P
    koszul_relation_verified = bool(not acc.any()) and bool(kvec.any())
    koszul_support_maxdeg_mult = max(deg(m) for m in list(E1) + list(E2))

    return dict(A=A, B=B, x_R=xR, degE1=dE1, degE2=dE2,
                terms_E1=len(E1), terms_E2=len(E2),
                zero_product_rows=zero_rows,
                koszul_relation_verified=koszul_relation_verified,
                koszul_needs_multiplier_degree=koszul_support_maxdeg_mult,
                per_degree=res)


def main():
    import sympy
    assert sympy.isprime(P), "p must be prime"
    print(f"p = {P} prime: True")
    print("closed-form counts (independent of any matrix build):")
    for D in (5, 6, 7, 8):
        print(f"  D={D}: columns(<=D) = {count_monomials_upto(D)}, "
              f"multipliers(<=D-4) = {count_monomials_upto(D - 4)}, "
              f"rows = {2 * count_monomials_upto(D - 4)}")
    out = []
    seen = {}
    # NO caching: every instance is computed from scratch, so that a duplicate
    # generator system agrees by computation rather than by construction.
    for (seed, A, B, tgt, u_pl, xR) in INSTANCES:
        r = run_instance(A, B, xR)
        key = (A, B, xR)
        r["generator_triple_(A,B,x_R)"] = list(key)
        if key in seen:
            r["identical_generator_system_as"] = seen[key]
        else:
            seen[key] = f"{seed}/t{tgt}"
        r.update(curve_seed=seed, target=tgt, u_planted=u_pl)
        out.append(r)
        pd = r["per_degree"]
        print(f"seed {seed} t{tgt} A={A} B={B} x_R={xR}: "
              f"deficit(5..8) = ("
              f"{pd[5]['deficit']}, {pd[6]['deficit']}, "
              f"{pd[7]['deficit']}, {pd[8]['deficit']})  "
              f"rows8={pd[8]['rows']} cols8={pd[8]['columns']} "
              f"rank8={pd[8]['rank']} sup8={pd[8]['support_columns']} "
              f"zero_rows={r['zero_product_rows']} "
              f"koszul_ok={r['koszul_relation_verified']}")
        sys.stdout.flush()
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
