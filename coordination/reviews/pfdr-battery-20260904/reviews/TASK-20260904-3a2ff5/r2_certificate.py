"""R2: independent check of the completeness certificate (C1 / C2) and of Lemma 3
(C2 is automatic once D >= e(Z) + 2), plus the dense-engine exactness bound.
TASK-20260904-3a2ff5."""
import json, os, sys, random, itertools
sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-cbdefb")
import numpy as np
from harness.macaulay_fp import ColumnSpace, Ring
from harness.macaulay_fp.linalg import Echelon
from harness.macaulay_fp.nulls import random_form
import closure as CL
OUT = "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5"

def s3_poly(ring, x1, x2, x3c, a, b):
    R = ring; mul, add = R.mul, R.add
    sc = lambda f, c: {m: (v * c) % R.p for m, v in f.items() if (v * c) % R.p}
    x1x2 = mul(x1, x2); d12 = add(x1, sc(x2, -1))
    return R.reduce(add(add(sc(mul(d12, d12), pow(x3c, 2, R.p)),
                            sc(add(mul(add(x1, x2), add(x1x2, R.constant(a))),
                                   R.constant((2 * b) % R.p)), (-2 * x3c) % R.p)),
                        add(mul(add(x1x2, R.constant((-a) % R.p)), add(x1x2, R.constant((-a) % R.p))),
                            sc(add(x1, x2), (-4 * b) % R.p))))

def digit_semaev(p, s, a, b, xR):
    ring = Ring(p, 2 * s, 0)
    ells = []
    for k in range(2):
        e = {}
        for i in range(s):
            e = ring.add(e, {ring.sq_var(k * s + i): pow(2, i, p)})
        ells.append(e)
    return ring, s3_poly(ring, ells[0], ells[1], xR, a, b)

# --- INDEPENDENT (second-implementation) computation of dim(J + sum_i a_i J) ------------
def dim_J_plus_vars_J(ring, gens, D):
    """dim( (I cap B_{<=D-1}) + sum_i a_i (I cap B_{<=D-1}) ) inside B_{<=D}, by explicit
    basis construction (no annihilator/dual argument): kernel basis of the evaluation map,
    multiplied out and echelonised."""
    p = ring.p; n = ring.n_sq
    full = ColumnSpace.build(ring, n)
    Ev = CL.evaluation_matrix(ring, full)
    Z = CL.zero_set(ring, gens, full, Ev)
    Nprev = full.ncols_upto(D - 1); ND = full.ncols_upto(D)
    # basis of J = I cap B_{<=D-1} = kernel of the |Z| x Nprev evaluation matrix
    M = Ev[Z, :Nprev] % p if Z else np.zeros((0, Nprev))
    E = Echelon(p)
    for row in M:
        E.add({int(j): int(v) % p for j, v in enumerate(row) if int(v) % p})
    piv = sorted(E.pivots); pivset = set(piv)
    basisJ = []
    for c in range(Nprev):
        if c in pivset:
            continue
        vec = {c: 1}
        for q in piv:
            v = E.pivots[q].get(c, 0)
            if v:
                vec[q] = (-v) % p
        basisJ.append(vec)
    T = CL.multiplication_table(ring, full)
    Etot = Echelon(p)
    for vec in basisJ:
        Etot.add(dict(vec))
        for i in range(n):
            prod = {}
            for c, v in vec.items():
                t = int(T[i, c])
                prod[t] = (prod.get(t, 0) + v) % p
            Etot.add({k: v for k, v in prod.items() if v})
    dim_I_D = CL.ideal_dimension(Ev, Z, ND, p)[0]
    return {"D": D, "Z_size": len(Z), "dim_J": len(basisJ), "dim_J_plus_aJ": Etot.rank,
            "dim_I_cap_B_leq_D": dim_I_D, "C2_holds_independent": Etot.rank == dim_I_D}

out = {}
# 1. Semaev at s = 4 (n = 8): C2 at D = 8 (the certificate's own range) and at D = 5, 6, 7
ring, sem = digit_semaev(4099, 4, 3245, 455, 1960)
out["semaev_s4_C2_independent"] = [dim_J_plus_vars_J(ring, [sem], D) for D in (4, 5, 6, 7, 8)]
# cross-check against the producer's c2_check
full = ColumnSpace.build(ring, ring.n_sq)
Ev = CL.evaluation_matrix(ring, full); T = CL.multiplication_table(ring, full)
Z = CL.zero_set(ring, [sem], full, Ev)
out["semaev_s4_c2_check_producer"] = [CL.c2_check(ring, full, Ev, Z, D, T) for D in (4, 5, 6, 7, 8)]

# 2. a system with a LARGE zero set: is C2 informative at all?
rng = random.Random(4242)
ring2 = Ring(4099, 8, 0)
g = random_form(ring2, list(range(8)), 1, rng)          # one linear form: |Z| = 2^7
out["linear_form_n8"] = [dim_J_plus_vars_J(ring2, [g], D) for D in (2, 3, 4, 5)]

# 3. the PTM-2 planted late-fall system (Z_size 386): C2 above D_max
def planted_late(seed=20260904, p=4099, n=10):
    r = Ring(p, n, 0); rr = random.Random(seed); V = list(range(n))
    f1 = random_form(r, V, 5, rr); f2 = random_form(r, V, 5, rr)
    u = random_form(r, V, 3, rr); v = random_form(r, V, 3, rr); h = random_form(r, V, 7, rr)
    return r, [f1, f2, r.reduce(r.add(r.add(r.mul(u, f1), r.mul(v, f2)), h))]
r3, g3 = planted_late()
out["planted_late_C2"] = [dim_J_plus_vars_J(r3, g3, D) for D in (8, 9, 10)]

# 4. e(Z): the interpolation degree of the observed Semaev zero sets
def interp_degree(ring, Z):
    full = ColumnSpace.build(ring, ring.n_sq)
    Ev = CL.evaluation_matrix(ring, full)
    for D in range(0, ring.n_sq + 1):
        if CL.ideal_dimension(Ev, Z, full.ncols_upto(D), ring.p)[1] == len(Z):
            return D
    return None
out["e_of_Z_semaev_s4"] = {"Z": Z, "e": interp_degree(ring, Z)}

# 5. dense-engine exactness: the actual worst-case partial sum at the largest cell
worst = {}
for p, N in ((65537, 968), (65537, 1024), (4099, 968)):
    worst[f"p={p},N={N}"] = {"bound_asserted_p2_N1": p * p * (N + 1),
                             "log2_bound": float(np.log2(p * p * (N + 1))),
                             "under_2_53": p * p * (N + 1) < 2 ** 53}
out["dense_exactness"] = worst
json.dump(out, open(os.path.join(OUT, "r2_certificate.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
