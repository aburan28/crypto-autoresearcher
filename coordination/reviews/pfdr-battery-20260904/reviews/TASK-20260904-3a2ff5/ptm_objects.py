"""Proves-too-much control + R2 planted late-fall object, for TASK-20260904-3a2ff5.

Runs the PRODUCER'S UNCHANGED argument/instrument (experiments/EXP-PFDR-cbdefb/closure.py,
convention cbdefb-closure-v1, D_max = 7) against four objects whose answer is KNOWN, and
records the declared failure signature.  Nothing here is an experiment run.

Objects
  PTM-1  NULL-1 support-matched random generator at s = 2, 3, 4: KNOWN d_lf = s + 3 (rising).
  PTM-2  a planted LATE fall above D_max = 7 in n = 10 squarefree variables: 'certified
         complete at D_max = 7' is KNOWN FALSE; the certificate must refuse.
  PTM-3  the direct presentation at m = 2 with B = 8 (afe4ce floor d_lf >= 8 > D_max):
         the closure must report no fall / right-censored, never a flat certified d_lf.
  PTM-4  the s = 1 saturated digit systems (n = 2): the count-1 tell is KNOWN to fire on a
         non-artifact; report what the tell actually detects.
"""
import json, os, random, sys
sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-cbdefb")

from harness.macaulay_fp import ColumnSpace, Ring
from harness.macaulay_fp.nulls import support_matched_system, random_form
import closure as CL

OUT = "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5"

# ------------------------------------------------------------------ S_3 and the digit S~
def s3_poly(ring, x1, x2, x3c, a, b):
    """S_3(x1, x2, x_R) with x1, x2 polynomials in ``ring`` and x_R the constant x3c."""
    R = ring
    mul, add, sc = R.mul, R.add, lambda f, c: {m: (v * c) % R.p for m, v in f.items() if (v * c) % R.p}
    x1x2 = mul(x1, x2)
    d12 = add(x1, sc(x2, -1))
    t1 = sc(mul(d12, d12), pow(x3c, 2, R.p) % R.p)
    inner = add(mul(add(x1, x2), add(x1x2, R.constant(a))), R.constant((2 * b) % R.p))
    t2 = sc(inner, (-2 * x3c) % R.p)
    t3 = mul(add(x1x2, R.constant((-a) % R.p)), add(x1x2, R.constant((-a) % R.p)))
    t4 = sc(add(x1, x2), (-4 * b) % R.p)
    return R.reduce(add(add(t1, t2), add(t3, t4)))

def digit_semaev(p, s, a, b, xR):
    ring = Ring(p, 2 * s, 0)
    ells = []
    for k in range(2):
        e = {}
        for i in range(s):
            e = ring.add(e, {ring.sq_var(k * s + i): pow(2, i, p)})
        ells.append(e)
    return ring, s3_poly(ring, ells[0], ells[1], xR, a, b)

def measure(ring, gens, dmax, engine=None, certificate=True, graded=True):
    dmin = min(ring.degree(g) for g in gens)
    cols = ColumnSpace.build(ring, dmax)
    eng = engine or ("sparse" if cols.ncols <= CL.SPARSE_COLUMN_LIMIT else "dense")
    return CL.measure_system(ring, gens, cols, dmin, dmax, engine=eng, cross_check=False,
                             certificate=certificate, graded=graded)

def brief(r):
    return {"d_ff": r.get("d_ff"), "d_lf": r.get("d_lf"), "falls": r.get("falls"),
            "no_fall_in_window": r.get("no_fall_in_window"),
            "right_censored": r.get("right_censored"),
            "certificate": {k: v for k, v in (r.get("certificate") or {}).items()
                            if k in ("attempted", "certified", "route", "C1", "Z_size",
                                     "dim_I_at_Dmax", "dim_V_at_Dmax", "structural", "reason")},
            "C2": [(c["D"], c["holds"]) for c in (r.get("certificate") or {}).get("C2", []) or []],
            "history": [{k: h[k] for k in ("D", "dim_W0", "dim_V", "fall_dim", "fall",
                                           "iteration_count")} for h in r.get("history", [])],
            "min_iteration_count_at_falls": r.get("min_iteration_count_at_falls"),
            "engine": r.get("engine"), "convention": r.get("convention")}

out = {"closure_py_sha256": None, "objects": {}}
import hashlib
out["closure_py_sha256"] = hashlib.sha256(open(
    "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-cbdefb/closure.py", "rb").read()).hexdigest()

P, A, Bc, XR = 4099, 3245, 455, 1960

# ---------------------------------------------------------------- PTM-1  NULL-1 re-run
ptm1 = {}
for s in (2, 3, 4):
    ring, sem = digit_semaev(P, s, A, Bc, XR)
    for seed in (7, 11):
        null, meta = support_matched_system(ring, [sem], seed)
        r = measure(ring, null, 7)
        ptm1[f"s={s},seed={seed}"] = {"support_size": len(sem), "null_degree": ring.degree(null[0]),
                                      "expected_d_lf_s_plus_3": s + 3, **brief(r)}
    r = measure(ring, [sem], 7)
    ptm1[f"s={s},SEMAEV"] = brief(r)
out["objects"]["PTM-1_null1_support_matched"] = ptm1

# ---------------------------------------------------------------- PTM-2  planted LATE fall
# n = 10 squarefree variables, f1, f2 of degree 5, u, v of degree 3, h of degree 7,
# g = u f1 + v f2 + h of degree 8.  The combination u f1 + v f2 = g - h is in the degree-8
# Macaulay space of {f1, f2, g}, so h (degree 7) falls at D = 8, ABOVE D_max = 7.
def planted_late(seed=20260904, p=4099, n=10):
    ring = Ring(p, n, 0)
    rng = random.Random(seed)
    V = list(range(n))
    f1 = random_form(ring, V, 5, rng); f2 = random_form(ring, V, 5, rng)
    u = random_form(ring, V, 3, rng);  v = random_form(ring, V, 3, rng)
    h = random_form(ring, V, 7, rng)
    g = ring.reduce(ring.add(ring.add(ring.mul(u, f1), ring.mul(v, f2)), h))
    return ring, [f1, f2, g], h, [f1, f2]

ring2, gens2, h2, base2 = planted_late()
deg = {"f1": ring2.degree(gens2[0]), "f2": ring2.degree(gens2[1]), "g": ring2.degree(gens2[2]),
       "h": ring2.degree(h2)}
r_at_7 = measure(ring2, gens2, 7)            # the producer's instrument, D_max = 7
r_at_9 = measure(ring2, gens2, 9, certificate=True)   # the TRUE history through D = 9
out["objects"]["PTM-2_planted_late_fall"] = {
    "degrees": deg, "n": 10, "p": 4099, "seed": 20260904,
    "at_Dmax_7": brief(r_at_7), "true_history_to_D_9": brief(r_at_9)}

# ---------------------------------------------------------------- PTM-3  direct presentation, B = 8
ring3 = Ring(P, 0, 2)
x1 = {ring3.free_var(0): 1}; x2 = {ring3.free_var(1): 1}
S3d = s3_poly(ring3, x1, x2, XR, A, Bc)
def fV(ring, var, B):
    prod = {ring.one(): 1}
    for j in range(B):
        prod = ring.mul(prod, ring.add({var: 1}, ring.constant(-j)))
    return ring.reduce(prod)
gens3 = [S3d, fV(ring3, ring3.free_var(0), 8), fV(ring3, ring3.free_var(1), 8)]
r3 = measure(ring3, gens3, 7, certificate=True, graded=True)
out["objects"]["PTM-3_direct_presentation_B8"] = {
    "generator_degrees": [ring3.degree(g) for g in gens3], "afe4ce_floor_d_lf_ge_B": 8,
    "D_max": 7, **brief(r3)}

# ---------------------------------------------------------------- PTM-4  s = 1 saturated
ring4, sem4 = digit_semaev(P, 1, A, Bc, XR)
r4 = measure(ring4, [sem4], 7)
full = ColumnSpace.build(ring4, ring4.n_sq)
Ev = CL.evaluation_matrix(ring4, full)
Z4 = CL.zero_set(ring4, [sem4], full, Ev)
dims = {}
for D in range(1, ring4.n_sq + 1):
    dims[D] = CL.ideal_dimension(Ev, Z4, full.ncols_upto(D), P)[0]
out["objects"]["PTM-4_s1_saturated"] = {
    "n": ring4.n_sq, "generator_degree": ring4.degree(sem4), "Z": Z4,
    "dim_I_cap_B_leq_D": dims, "N_D": {D: full.ncols_upto(D) for D in range(0, ring4.n_sq + 1)},
    **brief(r4)}

json.dump(out, open(os.path.join(OUT, "ptm_objects.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:6000])
