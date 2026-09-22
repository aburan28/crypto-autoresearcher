#!/usr/bin/env python3
"""Shared helpers for the EXP-GFPN-05ff43 drivers: ladder loading, curve
construction, seeded target streams, solution lifting, certificates, artifact
writers.  Seeds (specification.replication.seeds):
  2026092001 -> known-scalar target stream, keyed per (p', curve)  [same targets across arms]
  2026092002 -> curve / base point / sample-point streams, keyed per (p', curve, arm)
"""
import hashlib, json, os, random, time
import numpy as np
import flint
import yaml
from gfpn5_core import Fq, Curve, poly_eval
from symmetrize import (elem_sym, build_pool_x, build_pool_t, ArmPolynomial, monomials_total,
                        monomials_box, eval_monomials_rows, descend_and_write, run_msolve,
                        parse_msolve_param, rational_solutions, OpCount)
import verify_independent

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP_DIR = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43")
SEED_TARGETS = 2026092001
SEED_CURVES = 2026092002
CACHE_DIR = os.environ.get("GFPN_CACHE_DIR", "/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/gfpn05_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def load_ladder():
    return json.load(open(os.path.join(HERE, "ladder.json")))

def ladder_entry(p):
    for r in load_ladder():
        if r["p"] == p:
            return r
    raise KeyError(p)

def make_curve(F, rung, shape):
    cv = rung["curves"][shape]
    E = Curve(F, F.from_coeffs(cv["a2"]), F.from_coeffs(cv["a4"]), F.from_coeffs(cv["a6"]), shape)
    return E, cv

def base_point(E, cv, p, shape):
    """Deterministic generator of the prime-order subgroup: cofactor * first random point."""
    rng = random.Random(f"{SEED_CURVES}:basepoint:{p}:{shape}")
    n = int(cv["subgroup_prime"]); cof = int(cv["cofactor"])
    while True:
        P = E.random_point(rng)
        G = E.mul(cof, P)
        if G is not None and E.mul(n, G) is None:
            return G, n

def targets(E, G, n, p, shape, count=20):
    rng = random.Random(f"{SEED_TARGETS}:targets:{p}:{shape}")
    out = []
    for i in range(count):
        k = rng.randrange(1, n)
        R = E.mul(k, G)
        out.append((i, k, R))
    return out

def fq_json(F, a):
    return F.coeffs(a)

def pt_json(F, P):
    return [F.coeffs(P[0]), F.coeffs(P[1])]

# ------------------------------------------------------------------ lifting
def lift_solution_S(E, sol_e, R, p, counter):
    """Arm S5/S4: e in F_p^m -> x_i roots of T^m - e1 T^{m-1} + ... ; lift to points and signs.
    Returns list of accepted relations [(points, signs)] (each sums to R) and diagnostics."""
    F = E.F; m = len(sol_e)
    coeffs = [((-1) ** (m - k)) * sol_e[m - k - 1] % p for k in range(m)] + [1]   # low -> high
    # T^m - e1 T^{m-1} + e2 T^{m-2} - ...: coefficient of T^{m-j} is (-1)^j e_j
    coeffs = [0] * (m + 1)
    coeffs[m] = 1
    for j in range(1, m + 1):
        coeffs[m - j] = ((-1) ** j) * sol_e[j - 1] % p
    poly = flint.nmod_poly(coeffs, p)
    rts = poly.roots()
    xs = []
    for r, mult in rts:
        xs += [int(r)] * int(mult)
    diag = {"n_roots_in_Fp": len(xs)}
    if len(xs) != m:
        diag["reject"] = "x-polynomial does not split over F_p"
        return [], diag
    pts = []
    for x in xs:
        P = E.lift_x(F(x))
        counter.fq_mul += 3; counter.fq_inv += 0
        if P is None:
            diag["reject"] = "x does not lift to a point over F_q"
            return [], diag
        pts.append(P)
    rels = sign_search(E, pts, R, counter, torsion=None)
    diag["n_relations"] = len(rels)
    return rels, diag

def lift_solution_T(E, sol_e, R, T, p, counter):
    """Arm torsion: e(t) -> t_i -> x_i root of X^2 - t X + b -> points; signs and torsion fix-up."""
    F = E.F; m = len(sol_e); b = E.a4
    coeffs = [0] * (m + 1); coeffs[m] = 1
    for j in range(1, m + 1):
        coeffs[m - j] = ((-1) ** j) * sol_e[j - 1] % p
    rts = flint.nmod_poly(coeffs, p).roots()
    ts = []
    for r, mult in rts:
        ts += [int(r)] * int(mult)
    diag = {"n_roots_in_Fp": len(ts)}
    if len(ts) != m:
        diag["reject"] = "t-polynomial does not split over F_p"
        return [], diag
    pts = []
    for t in ts:
        tt = F(t); disc = tt * tt - 4 * b
        counter.fq_mul += 2
        if not disc.is_square():
            diag["reject"] = "t^2 - 4b not a square in F_q"
            return [], diag
        x = (tt + disc.sqrt()) / 2
        counter.fq_inv += 1
        if x == 0:
            diag["reject"] = "x = 0"
            return [], diag
        P = E.lift_x(x)
        counter.fq_mul += 3
        if P is None:
            diag["reject"] = "x does not lift to a point over F_q"
            return [], diag
        pts.append(P)
    rels = sign_search(E, pts, R, counter, torsion=T)
    diag["n_relations"] = len(rels)
    return rels, diag

def sign_search(E, pts, R, counter, torsion=None):
    """All sign vectors with sum eps_i P_i == R (or == R + T, fixed by P_1 -> P_1 + T)."""
    m = len(pts)
    rels = []
    targets_ = {("R", 1): R}
    if torsion is not None:
        targets_[("RT", 1)] = E.add(R, torsion)
    negR = E.neg(R)
    for mask in range(1 << m):
        signs = [1 if (mask >> i) & 1 == 0 else -1 for i in range(m)]
        S = None
        for P, s in zip(pts, signs):
            S = E.add(S, P if s == 1 else E.neg(P))
            counter.fq_inv += 1; counter.fq_mul += 3
        if S is None:
            continue
        if S == R:
            rels.append((list(pts), signs))
        elif torsion is not None and S == E.add(R, torsion):
            P1T = E.add(pts[0], torsion)
            newpts = [P1T] + list(pts[1:])
            # eps_1 (P_1 + T) = eps_1 P_1 + T, so the signed sum becomes S + T = R
            rels.append((newpts, signs))
    # de-duplicate global sign flips are distinct relations only if they hit R; keep as found
    return rels

def pad5(cs):
    cs = [int(c) for c in cs]
    return cs + [0] * (5 - len(cs))

def make_certificate(F, E, cv, p, cmod, arm, m, shape, G, n, k, R, rel, target_index, rel_index, run_id):
    pts, signs = rel
    return {
        "schema": "crypto.autoresearch.decomposition_certificate.v1",
        "experiment_id": "EXP-GFPN-05ff43", "run_id": run_id,
        "arm": arm, "m": m, "curve_shape": shape, "p": p, "cmod": cmod,
        "field": f"F_{p}[z]/(z^5 - {cmod}); elements listed as [c0..c4] = c0 + c1 z + ... + c4 z^4",
        "curve": {"model": cv["model"], "a2": pad5(cv["a2"]), "a4": pad5(cv["a4"]), "a6": pad5(cv["a6"]), "order": cv["order"], "cofactor": cv["cofactor"]},
        "subgroup_order": n, "G": pt_json(F, G), "k": k, "R": pt_json(F, R),
        "known_scalar": True, "target_index": target_index, "relation_index": rel_index,
        "factor_base_condition": ("x(P) in F_p" if not arm.startswith("torsion") else "x(P) + b/x(P) in F_p (phi-factor base, FHJRV)"),
        "points": [pt_json(F, P) for P in pts], "signs": signs,
        "statement": "sum_i signs[i] * points[i] == R == [k]G on the curve; re-verified by verify_independent.py (pure Python, no shared code)",
    }

# ------------------------------------------------------------------ cache of arm polynomials
def cache_path(p, shape, arm, m):
    return os.path.join(CACHE_DIR, f"pol_{p}_{shape}_{arm}_m{m}.npz")

def save_polynomial(pol, path):
    np.savez_compressed(path, C=pol.C, monos=np.array(pol.monos, dtype=np.int64), meta=json.dumps(pol.meta))
    return sha256_file(path)

def load_polynomial(path):
    d = np.load(path, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    monos = [tuple(int(x) for x in row) for row in d["monos"]]
    return ArmPolynomial(meta["arm"], meta["m"], monos, meta["p"], d["C"], meta), sha256_file(path)

# ------------------------------------------------------------------ artifact writers
def write_yaml(path, obj):
    with open(path, "w") as f:
        yaml.safe_dump(obj, f, sort_keys=False, width=110)

def run_dir():
    d = os.environ.get("GFPN_RUN_DIR")
    assert d, "GFPN_RUN_DIR not set (launch through run_wrapper.py)"
    return d

def run_id_from_dir():
    return os.path.basename(run_dir().rstrip("/"))

def placeholder_ladder_artifacts(rd, note, rows=None, dflat=None, band=None):
    write_yaml(os.path.join(rd, "ladder-table.yaml"), {"ladder_table": {"note": note, "rows": rows or []}})
    write_yaml(os.path.join(rd, "heur-dflat.yaml"), {"heur_dflat": dflat or {"heuristic": "HEUR-GFPN-DFLAT", "decision_scope": "ladder-wide decision is made in the aggregation run", "note": note}})
    write_yaml(os.path.join(rd, "cost-band-p64.yaml"), {"cost_band_p64": band or {"note": note, "status": "not_applicable_in_this_run"}})

def prediction_reference():
    return {
        "source": "experiments/EXP-GFPN-05ff43/specification.yaml preregistered_prediction (frozen)",
        "D_raw_free_orbit": 2 ** 20, "D_S5_free_orbit": 2 ** 20 / 120, "D_torsion_S5_free_orbit": 2 ** 20 / 1920,
        "group_orders": {"raw": 1, "S5": 120, "torsion_S5": 1920},
        "min_ratio_S5": 2 ** 6, "min_ratio_torsion_S5": 2 ** 9, "dflat_threshold_relative": 0.10,
        "design_note_floor_bits": 142, "p_crypto": "18446744069414584321",
    }
