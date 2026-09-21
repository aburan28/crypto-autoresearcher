#!/usr/bin/env python3
"""
V1 BLIND RE-DERIVATION -- TASK-20260904-642cf5.

Written from review_plan.blind_rederivation.quantity in
ledger/handoffs/TASK-20260904-642cf5.yaml ALONE.  No producer implementation,
notes or report was read; harness/macaulay_fp is NOT imported and was not read
at the time this file was written.

DEFINITION IMPLEMENTED (verbatim reading of the handoff)
  B = F_p[a_{1,0},a_{1,1},a_{1,2},a_{2,0},a_{2,1},a_{2,2}] / (a_{k,i}^2 - a_{k,i}),
  spanned by the 64 squarefree monomials, graded by squarefree degree (the degree
  of the reduced representative).  Bit i of a mask <-> a_{1,0},a_{1,1},a_{1,2},
  a_{2,0},a_{2,1},a_{2,2} for i = 0..5.  Monomial product = union of supports
  (because a^2 = a), so B is the union-convolution algebra on 2^6 masks.

  ell_1 = a_{1,0} + 2 a_{1,1} + 4 a_{1,2},  ell_2 = a_{2,0} + 2 a_{2,1} + 4 a_{2,2}
  S_3(x1,x2,x3) = (x1-x2)^2 x3^2
                  - 2*((x1+x2)*(x1 x2 + a) + 2 b) * x3
                  + (x1 x2 - a)^2 - 4 b (x1 + x2)
  S~ = S_3(ell_1, ell_2, x_R) reduced in B.
  For D in {4,5,6,7}: rows { mu * S~ reduced in B : mu squarefree monomial,
  deg mu = D - 4 }.  full_rank(D) = rank over F_p on all 64 monomial columns;
  top_rank(D) = rank of the same rows restricted to the columns of degree
  exactly D; fall_dim(D) = full_rank(D) - top_rank(D);
  d_ff = least D with fall_dim(D) > 0.

All linear algebra is my own exact Gaussian elimination over F_p on Python ints.
"""
import json, sys, itertools, random, hashlib

NV = 6
NMASK = 1 << NV
POP = [bin(m).count("1") for m in range(NMASK)]
VARNAMES = ["a10", "a11", "a12", "a20", "a21", "a22"]


def mono_name(mask):
    if mask == 0:
        return "1"
    return "*".join(VARNAMES[i] for i in range(NV) if mask >> i & 1)


# ---------- arithmetic in B (dense vectors of length 64 over F_p) ----------
def zero():
    return [0] * NMASK


def const(c, p):
    v = zero()
    v[0] = c % p
    return v


def add(u, v, p):
    return [(x + y) % p for x, y in zip(u, v)]


def sub(u, v, p):
    return [(x - y) % p for x, y in zip(u, v)]


def smul(c, u, p):
    c %= p
    return [(c * x) % p for x in u]


def mul(u, v, p):
    w = zero()
    for i, ui in enumerate(u):
        if ui:
            for j, vj in enumerate(v):
                if vj:
                    w[i | j] = (w[i | j] + ui * vj) % p
    return w


def var(i, p):
    v = zero()
    v[1 << i] = 1 % p
    return v


def ell(block, p):
    """ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}"""
    v = zero()
    base = 3 * block
    for i, c in enumerate((1, 2, 4)):
        v[1 << (base + i)] = c % p
    return v


def S3_in_B(X1, X2, x3, a, b, p):
    """S_3(X1, X2, x3) with X1, X2 in B and x3, a, b scalars in F_p."""
    x3 = x3 % p
    a %= p
    b %= p
    d = sub(X1, X2, p)
    t1 = smul(pow(x3, 2, p), mul(d, d, p), p)                       # (x1-x2)^2 x3^2
    ssum = add(X1, X2, p)                                           # (x1 + x2)
    prod = mul(X1, X2, p)                                           # x1 x2
    inner = add(mul(ssum, add(prod, const(a, p), p), p), const(2 * b, p), p)
    t2 = smul((-2 * x3) % p, inner, p)                              # -2(...)x3
    pa = sub(prod, const(a, p), p)
    t3 = mul(pa, pa, p)                                             # (x1 x2 - a)^2
    t4 = smul((-4 * b) % p, ssum, p)                                # -4b(x1+x2)
    return add(add(t1, t2, p), add(t3, t4, p), p)


# ---------- exact rank over F_p ----------
def rank_mod_p(rows, p):
    M = [list(r) for r in rows]
    ncols = len(M[0]) if M else 0
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(M)):
            if M[i][c] % p:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], p - 2, p)
        M[r] = [(x * inv) % p for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(x - f * y) % p for x, y in zip(M[i], M[r])]
        r += 1
        if r == len(M):
            break
    return r


def deg_of(g):
    d = -1
    for m, c in enumerate(g):
        if c % 0x7FFFFFFFFFFFFFFF or c:
            if c:
                d = max(d, POP[m])
    return d


def profile(g, p, Dmax=7, delta=4):
    """Per-layer (full_rank, top_rank, fall_dim) at D = delta..Dmax and d_ff."""
    out = {}
    d_ff = None
    for D in range(delta, Dmax + 1):
        k = D - delta
        mus = [m for m in range(NMASK) if POP[m] == k]
        rows = [mul_by_mono(g, m, p) for m in mus]
        cols_top = [m for m in range(NMASK) if POP[m] == D]
        full = rank_mod_p(rows, p) if rows else 0
        top = rank_mod_p([[r[c] for c in cols_top] for r in rows], p) if (rows and cols_top) else 0
        fall = full - top
        out[D] = dict(n_rows=len(rows), full_rank=full, top_rank=top, fall_dim=fall)
        if d_ff is None and fall > 0:
            d_ff = D
    return out, d_ff


def mul_by_mono(g, mask, p):
    """multiply g by the squarefree monomial `mask` in B (union convolution)."""
    w = zero()
    for m, c in enumerate(g):
        if c:
            w[m | mask] = (w[m | mask] + c) % p
    return w


def support(g):
    return [m for m, c in enumerate(g) if c % 1 == 0 and c]


# ---------- instances declared in the handoff (review_plan.blind_rederivation.parameters) ----------
INSTANCES = [
    # (p, curve_seed, a, b, target_seed, x_R)
    (4099, 1101, 527, 72, 1, 2374),
    (4099, 1101, 527, 72, 2, 934),
    (4099, 1102, 1592, 55, 1, 1885),
    (4099, 1102, 1592, 55, 2, 3861),
    (4099, 1103, 3191, 1819, 1, 3717),
    (4099, 1103, 3191, 1819, 2, 2737),
    (65537, 1101, 5623, 46432, 1, 42063),
    (65537, 1101, 5623, 46432, 2, 3344),
    (65537, 1102, 703, 52025, 1, 47098),
    (65537, 1102, 703, 52025, 2, 35614),
    (65537, 1103, 61835, 65393, 1, 47685),
    (65537, 1103, 61835, 65393, 2, 47685),
]

RNG_SEED = 20260904642
BLOCK1_DEG2 = [(1 << 0) | (1 << 1), (1 << 0) | (1 << 2), (1 << 1) | (1 << 2)]
BLOCK2_DEG2 = [(1 << 3) | (1 << 4), (1 << 3) | (1 << 5), (1 << 4) | (1 << 5)]


def main():
    rng = random.Random(RNG_SEED)
    report = {
        "rng_seed": RNG_SEED,
        "ring": "F_p[a_{k,i}]/(a_{k,i}^2 - a_{k,i}), 6 vars, 64 squarefree monomials, "
                "graded by squarefree degree of the reduced representative",
        "ell": "ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}",
        "S3_formula": "(x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3 + (x1 x2 - a)^2 - 4b(x1+x2)",
        "rows": "per-layer: {mu*S~ : mu squarefree monomial, deg mu = D - 4}, D = 4..7",
        "instances": [],
        "block_factored_nulls": [],
        "support_matched_nulls": [],
    }

    # ---- Semaev arm: the 12 declared instances ----
    stilde_by_instance = {}
    for (p, cseed, a, b, tseed, xR) in INSTANCES:
        e1, e2 = ell(0, p), ell(1, p)
        St = S3_in_B(e1, e2, xR, a, b, p)
        key = (p, cseed, tseed)
        stilde_by_instance[key] = St
        prof, d_ff = profile(St, p)
        supp = [m for m in range(NMASK) if St[m]]
        deg4 = [m for m in supp if POP[m] == 4]
        rec = {
            "p": p, "curve_seed": cseed, "a": a, "b": b, "target_seed": tseed, "x_R": xR,
            "S_tilde_degree": max(POP[m] for m in supp),
            "S_tilde_support_size": len(supp),
            "S_tilde_support_by_degree": {str(dg): sum(1 for m in supp if POP[m] == dg)
                                          for dg in range(0, 5)},
            "S_tilde_top_deg4_monomials": {mono_name(m): St[m] for m in sorted(deg4)},
            "per_layer": {str(D): prof[D] for D in sorted(prof)},
            "d_ff": d_ff,
            "fall_dim_at_d_ff": prof[d_ff]["fall_dim"] if d_ff else None,
            "profile_full_top_D4_D5_D6": [[prof[D]["full_rank"], prof[D]["top_rank"]]
                                          for D in (4, 5, 6)],
        }
        report["instances"].append(rec)

    # ---- (i) block-factored nulls: two per prime ----
    for p in (4099, 65537):
        for k in range(2):
            c1 = [rng.randrange(p) for _ in range(3)]
            c2 = [rng.randrange(p) for _ in range(3)]
            q1 = zero()
            for m, c in zip(BLOCK1_DEG2, c1):
                q1[m] = c % p
            q2 = zero()
            for m, c in zip(BLOCK2_DEG2, c2):
                q2[m] = c % p
            g = mul(q1, q2, p)
            prof, d_ff = profile(g, p)
            report["block_factored_nulls"].append({
                "p": p, "draw": k + 1,
                "q1_coeffs": {mono_name(m): c % p for m, c in zip(BLOCK1_DEG2, c1)},
                "q2_coeffs": {mono_name(m): c % p for m, c in zip(BLOCK2_DEG2, c2)},
                "g_support_size": sum(1 for x in g if x),
                "g_degrees_present": sorted({POP[m] for m in range(NMASK) if g[m]}),
                "per_layer": {str(D): prof[D] for D in sorted(prof)},
                "d_ff": d_ff,
                "fall_dim_at_d_ff": prof[d_ff]["fall_dim"] if d_ff else None,
            })

    # ---- (ii) support-matched nulls: two per instance ----
    for (p, cseed, a, b, tseed, xR) in INSTANCES:
        St = stilde_by_instance[(p, cseed, tseed)]
        supp = [m for m in range(NMASK) if St[m]]
        for k in range(2):
            g = zero()
            for m in supp:
                g[m] = rng.randrange(1, p)      # uniformly random NONZERO coefficient
            prof, d_ff = profile(g, p)
            report["support_matched_nulls"].append({
                "p": p, "curve_seed": cseed, "target_seed": tseed, "draw": k + 1,
                "support_size": len(supp),
                "per_layer": {str(D): prof[D] for D in sorted(prof)},
                "d_ff": d_ff,
                "fall_dim_at_d_ff": prof[d_ff]["fall_dim"] if d_ff else None,
                "fall_dim_at_6": prof[6]["fall_dim"],
            })

    json.dump(report, sys.stdout, indent=1, sort_keys=False)
    print()


if __name__ == "__main__":
    main()
