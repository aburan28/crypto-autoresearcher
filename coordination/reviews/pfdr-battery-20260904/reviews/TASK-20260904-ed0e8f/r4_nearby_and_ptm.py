#!/usr/bin/env python3
"""R4 + proves_too_much (TASK-20260904-ed0e8f, red team).

Objects, all measured with the independent meter rt_meter.py:

 A. NEARBY-MIXED-BLOCK as executed: x_k = sum_{i<ms} c_{k,i} a_i with ALL ms
    digit variables shared (m = 2, s = 3).  Independent recomputation.
 B. NEARBY-MIXED-BLOCK, the LITERAL reading the executor recorded but did not
    run: x_k = sum_{i<s} c_{k,i} a_i on s = 3 SHARED variables (n = 3).
 C. NON-TENSOR TOP FORM at (2,2,3) that does NOT collapse:
       g_top = ell_1^3 ell_2 + ell_1 ell_2^3   (rank-2 in A_1 tensor A_2)
    plus random sub-top terms.  The tensor-kernel step of (D4) does not apply.
    Also a second non-tensor object: ell_1^2 ell_2^2 + ell_1^3 ell_2.
 D. PROVES-TOO-MUCH object 3: the DIRECT presentation at m = 2 with membership
    degree B = 4, generators (f_1(x_1), f_2(x_2), S_3(x_1, x_2, x_R)) of
    degrees (4, 4, 4) in the ORDINARY polynomial ring F_p[x_1, x_2].  The
    argument's algebra (squarefree block algebra) is absent; the first fall
    must not be the digit value 5.
 E. PROVES-TOO-MUCH object 4: the regime s < 2^{m-1}, i.e. (m, s) = (3, 3).
    ell_k^4 = 0 in 3 squarefree variables, so the argument's delta = 12 is
    wrong.  Measure the actual generator degree and first fall.
"""
import json
import random
import sys
from itertools import combinations

import sympy as sp

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f")
from rt_meter import (pmul, padd, pscal, ppow, deg, top_part, homog_part,
                      layer_profile, first_fall, monomials_of_degree,
                      rank_mod_p, digit_forms, S3)

SEED = 561428
P = 4099
A_, B_, XR = 527, 72, 2374


def add_subtop(g, n, delta, p, rng, density=1.0):
    out = dict(g)
    for d in range(0, delta):
        for mu in monomials_of_degree(n, d):
            if rng.random() < density:
                c = rng.randrange(1, p)
                v = (out.get(mu, 0) + c) % p
                if v:
                    out[mu] = v
                elif mu in out:
                    del out[mu]
    return out


# ------------------------------------------------------------------ A, B
def mixed_block(nvars, p, rng):
    forms = []
    for _ in range(2):
        forms.append({1 << i: rng.randrange(1, p) for i in range(nvars)})
    return forms


def run_mixed(nvars, p, rng, reps, Dmax):
    out = []
    for _ in range(reps):
        x1, x2 = mixed_block(nvars, p, rng)
        g = S3(x1, x2, {0: XR}, A_, B_, p)
        prof = layer_profile(g, nvars, p, Dmax)
        dff, fd = first_fall(prof)
        out.append({"n": nvars, "gen_degree": deg(g), "top_terms": len(top_part(g)),
                    "profile": prof, "d_ff": dff, "fall_dim": fd})
    return out


# ------------------------------------------------------------------ C
def nontensor_objects(s, p, rng, reps, Dmax):
    n = 2 * s
    ells = digit_forms(2, s, p)
    l1, l2 = ells
    out = []
    variants = {
        "ell1^3*ell2 + ell1*ell2^3": padd(pmul(ppow(l1, 3, p), l2, p),
                                          pmul(l1, ppow(l2, 3, p), p), p),
        "ell1^2*ell2^2 + ell1^3*ell2": padd(pmul(ppow(l1, 2, p), ppow(l2, 2, p), p),
                                            pmul(ppow(l1, 3, p), l2, p), p),
        "ell1^2*ell2^2 (tensor, control)": pmul(ppow(l1, 2, p), ppow(l2, 2, p), p),
    }
    for name, gh in variants.items():
        # keep only the degree-4 homogeneous part as the intended top form
        gtop = homog_part(gh, 4)
        for rep in range(reps):
            g = add_subtop(gtop, n, 4, p, rng, 1.0)
            prof = layer_profile(g, n, p, Dmax)
            dff, fd = first_fall(prof)
            out.append({"top_form": name, "rep": rep, "gen_degree": deg(g),
                        "top_terms": len(top_part(g)),
                        "top_form_is_rank1_tensor": tensor_rank_one(gtop, s),
                        "profile": prof, "d_ff": dff, "fall_dim": fd})
    return out


def tensor_rank_one(gtop, s):
    """Is the degree-4 form a single tensor q_1(block1) * q_2(block2)?
    Write the coefficient array as a matrix rows = block-1 monomials,
    cols = block-2 monomials, and test rank <= 1 over the rationals."""
    rows = {}
    for mask, c in gtop.items():
        m1 = mask & ((1 << s) - 1)
        m2 = mask >> s
        rows.setdefault(m1, {})[m2] = c
    mats = [dict(v) for v in rows.values()]
    return rank_mod_p(mats, P) <= 1


# ------------------------------------------------------------------ D
def direct_presentation(p, B, xR, a, b, Dmax):
    """Ordinary graded polynomial ring F_p[x1, x2]; generators
    f_1 = prod_{v in FB}(x1 - v), f_2 likewise, and S_3(x1, x2, xR).
    Monomial = (i, j).  Per-layer rows {mu * f : deg mu = D - deg f}."""
    FB = list(range(B))

    def pm(f, g):
        out = {}
        for (i1, j1), c1 in f.items():
            for (i2, j2), c2 in g.items():
                k = (i1 + i2, j1 + j2)
                v = (out.get(k, 0) + c1 * c2) % p
                if v:
                    out[k] = v
                elif k in out:
                    del out[k]
        return out

    def pa(f, g):
        out = dict(f)
        for k, c in g.items():
            v = (out.get(k, 0) + c) % p
            if v:
                out[k] = v
            elif k in out:
                del out[k]
        return out

    f1 = {(0, 0): 1}
    for v in FB:
        f1 = pm(f1, {(1, 0): 1, (0, 0): (-v) % p})
    f2 = {(0, 0): 1}
    for v in FB:
        f2 = pm(f2, {(0, 1): 1, (0, 0): (-v) % p})
    x1 = {(1, 0): 1}
    x2 = {(0, 1): 1}
    one = {(0, 0): 1}

    def sc(f, c):
        return {k: (v * c) % p for k, v in f.items() if (v * c) % p}
    diff = pa(x1, sc(x2, -1))
    S = pa(pa(sc(pm(diff, diff), xR * xR % p),
              sc(pm(pa(x1, x2), pa(pm(x1, x2), sc(one, a))), (-2 * xR) % p)),
           pa(sc(one, (-4 * xR * b) % p),
              pa(pm(pa(pm(x1, x2), sc(one, -a)), pa(pm(x1, x2), sc(one, -a))),
                 sc(pa(x1, x2), (-4 * b) % p))))
    gens = {"f1": f1, "f2": f2, "S3": S}
    degs = {k: max(i + j for (i, j) in v) for k, v in gens.items()}
    prof = []
    for D in range(min(degs.values()), Dmax + 1):
        rows_full, rows_top = [], []
        for name, g in gens.items():
            k = D - degs[name]
            if k < 0:
                continue
            for i in range(k + 1):
                mu = (i, k - i)
                r = pm({mu: 1}, g)
                rows_full.append(r)
                rows_top.append({m: c for m, c in r.items() if sum(m) == D})
        fr = rank_mod_p([{str(k): v for k, v in r.items()} for r in rows_full], p)
        tr = rank_mod_p([{str(k): v for k, v in r.items()} for r in rows_top], p)
        prof.append((D, len(rows_full), fr, tr, fr - tr))
    return {"generator_degrees": degs, "profile": prof,
            "d_ff": first_fall(prof)[0], "fall_dim": first_fall(prof)[1]}


# ------------------------------------------------------------------ E
def s4_poly(p, a, b, xR):
    x1, x2, x3, U = sp.symbols("x1 x2 x3 U")

    def S3s(u, v, w):
        return sp.expand((u - v) ** 2 * w ** 2
                         - 2 * ((u + v) * (u * v + a) + 2 * b) * w
                         + (u * v - a) ** 2 - 4 * b * (u + v))
    R = sp.expand(sp.resultant(sp.Poly(S3s(x1, x2, U), U),
                               sp.Poly(S3s(x3, xR, U), U)))
    poly = sp.Poly(R, x1, x2, x3)
    return {tuple(mon): int(c) % p for mon, c in
            zip(poly.monoms(), poly.coeffs()) if int(c) % p}


def digit_m3(s, p, a, b, xR):
    coeffs = s4_poly(p, a, b, xR)
    ells = digit_forms(3, s, p)
    pw = [[{0: 1}] for _ in range(3)]
    for k in range(3):
        for j in range(1, 5):
            pw[k].append(pmul(pw[k][-1], ells[k], p))
    g = {}
    for (i, j, k), c in coeffs.items():
        term = pmul(pmul(pw[0][i], pw[1][j], p), pw[2][k], p)
        g = padd(g, pscal(term, c, p), p)
    return g


def main():
    rng = random.Random(SEED)
    out = {}
    out["A_mixed_block_all_shared_n6"] = run_mixed(6, P, rng, 3, 7)
    out["B_mixed_block_literal_shared_n3"] = run_mixed(3, P, rng, 3, 6)
    out["C_non_tensor_top_forms_s3"] = nontensor_objects(3, P, rng, 3, 8)
    out["D_direct_presentation_B4"] = direct_presentation(P, 4, XR, A_, B_, 9)
    g = digit_m3(3, P, A_, B_, XR)
    prof = layer_profile(g, 9, P, 12)
    dff, fd = first_fall(prof)
    out["E_m3_s3_out_of_regime"] = {
        "n": 9, "gen_degree": deg(g), "gen_terms": len(g),
        "top_terms": len(top_part(g)),
        "closed_form_delta_would_be": 12,
        "closed_form_d_ff_would_be": 3 * 4 + (3 - 4) // 2 + 1,
        "profile": prof, "d_ff": dff, "fall_dim": fd}
    json.dump(out, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
