#!/usr/bin/env python3
"""Phase 2 (J2 curve-level checks + J3 comparison) using ONLY the sealed blind code.

Verifies the sealed blind_rederive.py against its SEAL hash before importing it, then
applies its point counter and its v_p(z([p]P^)) routine to every curve the producer
sampled (both seeds). Nothing from harness/ or the producer's implementation is imported.
"""
import hashlib
import importlib.util
import json
import os
import random
import sys
from fractions import Fraction

ROOT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
EXP = "experiments/EXP-CZLIFT-f5e06c"
RUNS = {"RUN-CZLIFT-032a92": 20261009, "RUN-CZLIFT-6447f0": 20261010}

seal = {l.split()[1]: l.split()[0] for l in open(os.path.join(HERE, "blind", "SEAL.sha256")) if len(l.split()) == 2}
src = os.path.join(HERE, "blind", "blind_rederive.py")
assert hashlib.sha256(open(src, "rb").read()).hexdigest() == seal["blind_rederive.py"], "sealed code changed"
spec = importlib.util.spec_from_file_location("blind", src)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

CM_J = {-3: 0, -7: -3375, -8: 8000, -11: -32768, -19: -884736, -43: -884736000,
        -67: -147197952000, -163: -262537412640768000}


def jq(a, b):
    return Fraction(1728 * 4 * a ** 3, 4 * a ** 3 + 27 * b ** 2)


def largest_prime_factor(n):
    f, q, best = n, 2, 1
    while q * q <= f:
        while f % q == 0:
            best, f = q, f // q
        q += 1
    return max(best, f) if f > 1 else best


out = {"sealed_code_sha256": seal["blind_rederive.py"], "runs": {}}
rng = random.Random(65)  # validator's own seed, for point choice only
for run, seed in RUNS.items():
    raw = json.load(open(os.path.join(ROOT, EXP, "runs", run, "raw-result.json")))["raw"]
    an, tor = [], []
    for c in raw["curves_anomalous"]:
        p, A, Bc, D = c["p"], c["A"], c["B"], c["D"]
        cnt = B.count_points(p, A, Bc)
        j_exact = jq(A, Bc)
        x0, y0 = B.random_point(p, A % p, Bc % p, rng)
        r_can = B.vz_mult_p(p, A, Bc, x0, y0, 8)
        r_pa = B.vz_mult_p(p, A + p, Bc, x0, y0, 8)
        r_pa2 = B.vz_mult_p(p, A + p * p, Bc, x0, y0, 8)
        r_red = B.vz_mult_p(p, A % p, Bc % p, x0, y0, 8)
        prod = {cls: sorted({r["vP"] for r in c["rows"] if r["class"] == cls}) for cls in
                ("canonical", "isomorphic", "pert_p", "pert_p2")}
        an.append({
            "D": D, "p": p, "is_prime": B.is_prime(p), "in_range": 10_000 <= p <= 100_000,
            "count": cnt, "anomalous": cnt == p,
            "j_exact_equals_cm": j_exact == CM_J[D], "coeffs_integral_model_not_reduced": not (0 <= A < p and 0 <= Bc < p) or D == -3,
            "v_canonical": r_can[0]["v"], "v_canonical_chain2": r_can[1]["v"],
            "v_pertA_p": r_pa[0]["v"], "v_pertA_p2": r_pa2[0]["v"], "v_coeffs_reduced_mod_p": r_red[0]["v"],
            "producer_vP_by_class": prod,
        })
    for c in raw["curves_torsion"]:
        p, A, Bc, N, n = c["p"], c["A"], c["B"], c["N"], c["n"]
        cnt = B.count_points(p, A, Bc)
        rec = {"arm": c["arm"], "label": c["label"], "p": p, "is_prime": B.is_prime(p),
               "in_range": 10_000 <= p <= 100_000, "N_recorded": N, "N_count": cnt, "N_ok": cnt == N,
               "n": n, "n_prime": B.is_prime(n), "n_divides_N": N % n == 0, "n_is_largest_prime_factor": largest_prime_factor(N) == n,
               "n_ge_101": n >= 101, "n_ne_p": n != p, "N_odd": N % 2 == 1, "not_anomalous": cnt != p}
        if c["arm"] == "cm_canonical":
            D = int(c["label"].split("=")[1])
            rec["j_exact_equals_cm"] = jq(A, Bc) == CM_J[D]
        else:
            rec["coeffs_in_0_p"] = 0 <= A < p and 0 <= Bc < p
        tor.append(rec)
    # cost bound recomputation (torsion_cost_within_bound is a recorded secondary flag)
    cost_sum = sum(r["tor_cost_additions"] for c in raw["curves_torsion"] for r in c["rows"])
    bound_sum = sum((2 * (c["n"].bit_length() + (c["p"] ** c["precision"]).bit_length()) + 1) * len(c["rows"])
                    for c in raw["curves_torsion"])
    out["runs"][run] = {
        "anomalous": an, "torsion": tor,
        "summary": {
            "anomalous_curves": len(an),
            "all_anomalous_by_own_count": all(x["anomalous"] for x in an),
            "all_prime_in_range": all(x["is_prime"] and x["in_range"] for x in an + tor),
            "all_canonical_j_exact": all(x["j_exact_equals_cm"] for x in an),
            "own_v_canonical": sorted({x["v_canonical"] for x in an} | {x["v_canonical_chain2"] for x in an}),
            "own_v_pertA_p": sorted({x["v_pertA_p"] for x in an}),
            "own_v_pertA_p2": sorted({x["v_pertA_p2"] for x in an}),
            "own_v_coeffs_reduced_mod_p_by_D": sorted({(x["D"], x["v_coeffs_reduced_mod_p"]) for x in an}),
            "producer_vP_canonical": sorted({v for x in an for v in x["producer_vP_by_class"]["canonical"]}),
            "producer_vP_pert_p": sorted({v for x in an for v in x["producer_vP_by_class"]["pert_p"]}),
            "producer_vP_pert_p2": sorted({v for x in an for v in x["producer_vP_by_class"]["pert_p2"]}),
            "torsion_curves": len(tor),
            "torsion_all_N_ok": all(x["N_ok"] for x in tor),
            "torsion_all_subgroup_ok": all(x["n_prime"] and x["n_divides_N"] and x["n_is_largest_prime_factor"]
                                           and x["n_ge_101"] and x["n_ne_p"] and x["N_odd"] for x in tor),
            "torsion_all_non_anomalous": all(x["not_anomalous"] for x in tor),
            "cm_arm_j_exact": all(x.get("j_exact_equals_cm", True) for x in tor),
            "random_arm_coeffs_in_0_p": all(x.get("coeffs_in_0_p", True) for x in tor),
            "cm_arm_D_labels": sorted({x["label"] for x in tor if x["arm"] == "cm_canonical"}),
            "torsion_cost_sum": cost_sum, "torsion_cost_bound_sum": bound_sum,
            "torsion_cost_within_bound": cost_sum <= bound_sum,
        },
    }
json.dump(out, sys.stdout, indent=1, default=str)
print()
