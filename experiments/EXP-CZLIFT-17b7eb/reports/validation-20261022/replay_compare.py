#!/usr/bin/env python3
"""J2/J3/PTM-1 replay for TASK-20261022-282b02 (run with python3 -B).

Regenerates the producer's sample stream (lift coefficients, P, d, x-digit) by
following the documented rng draw order of run.py and calling ONLY
harness.czlift.random_point / toycurve for the choice of P in E(F_p). Every
measured quantity -- v_p(j(E^) - j_cm) (exact rationals, uncapped), the Hensel
and Teichmuller point lifts, v_p(z([p]P^)) and the leading digit of
z([p]Q^)/z([p]P^) -- is recomputed with the validator's sealed blind code
(blind/blind_rederive.py: z_of_pP_closed, hensel_y, teichmuller, jinv, vp_frac),
then compared row by row with raw-result.json.

Usage: python3 -B replay_compare.py <repo_root> <run_dir> [<run_dir> ...]
"""
import importlib.util
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("blind", os.path.join(HERE, "blind", "blind_rederive.py"))
blind = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blind)

PREC = 8
SECTIONS = ("hensel_random", "naive", "teichmuller")


def producer_lift_draws(p, A, B, j_cm, rng, per_class):
    """Re-implementation of the rng draw order of run.lift_classes (coefficients only)."""
    out = [("canonical", A, B, None)]
    for _ in range(per_class):
        t = rng.randrange(1, p)
        s = 1 + p * t
        out.append(("isomorphic", A * s * s, B * s ** 3, ("t", t)))
    for _ in range(per_class):
        if j_cm == 0:
            r1, r2 = rng.randrange(1, p), rng.randrange(0, p)
            out.append(("pert_p", p * r1, B + p * r2, ("a4=p*r1,b+=p*r2", r1, r2)))
            r1, r2 = rng.randrange(1, p), rng.randrange(0, p)
            out.append(("pert_p2", p * p * r1, B + p * r2, ("a4=p^2*r1,b+=p*r2", r1, r2)))
        else:
            r1, r2 = rng.randrange(1, p), rng.randrange(1, p)
            out.append(("pert_p", A + p * r1, B + p * r2, ("a4+=p*r1,a6+=p*r2", r1, r2)))
            r1, r2 = rng.randrange(1, p), rng.randrange(1, p)
            out.append(("pert_p2", A + p * p * r1, B + p * p * r2, ("a4+=p^2*r1,a6+=p^2*r2", r1, r2)))
    return out


def my_lift(P, section, a, b, p, n, eps):
    x0, y0 = P
    if section == "hensel_random":
        x = x0 + p * eps
    elif section == "naive":
        x = x0
    else:
        x = blind.teichmuller(x0, p, n)
    x %= p ** n
    return x, blind.hensel_y(x, y0, a, b, p, n)


def replay(run_dir, czlift):
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    seed = raw["metrics"]["seed"]
    per_class, samples = 2, 12
    mism = Counter()
    mism_rows = []
    d_range_viol = 0
    total = 0
    true_v_beyond_cap = Counter()
    lift_table = []
    alt = defaultdict(lambda: {"n": 0, "succ": 0, "inv": 0.0, "inv1": 0.0, "var": 0.0, "var1": 0.0})
    for c in raw["raw"]["curves"]:
        D, p, A, B, j_cm = c["D"], c["p"], c["A"], c["B"], c["j_cm"]
        e = 3 if j_cm == 0 else 1
        rng = random.Random(seed * 1_000_003 + p)
        Efp = czlift.EllipticCurve(p, A % p, B % p)
        assert blind.count_points(A, B, p) == p
        assert blind.jinv(A, B) == Fraction(j_cm)
        rows = iter(c["rows"])
        for idx, (cls, A2, B2, meta) in enumerate(producer_lift_draws(p, A, B, j_cm, rng, per_class)):
            dj = blind.jinv(A2, B2) - Fraction(j_cm)
            vdj_true = blind.vp_frac(dj, p)
            vdj_cap = PREC if vdj_true is None or vdj_true >= PREC else vdj_true
            lift_rec = {"D": D, "p": p, "class": cls, "lift_index": idx, "draw": meta,
                        "v_dj_exact": vdj_true, "two_e": 2 * e, "vP_hist": Counter(), "success": 0, "n": 0}
            for section in SECTIONS:
                for _ in range(samples):
                    P = czlift.random_point(Efp, rng)
                    d = rng.randrange(2, p - 1)
                    if not (2 <= d <= p - 2):
                        d_range_viol += 1
                    Q = blind.mul_modp(d, P, A % p, p)
                    epsP = rng.randrange(p) if section == "hensel_random" else 0
                    epsQ = rng.randrange(p) if section == "hensel_random" else 0
                    Ph = my_lift(P, section, A2, B2, p, PREC, epsP)
                    Qh = my_lift(Q, section, A2, B2, p, PREC, epsQ)
                    kP, uP = blind.z_of_pP_closed(Ph, A2, p, PREC)
                    kQ, uQ = blind.z_of_pP_closed(Qh, A2, p, PREC)
                    if kP >= PREC or kQ >= PREC:
                        Ph12 = my_lift(P, section, A2, B2, p, 14, epsP)
                        true_v_beyond_cap[(cls, blind.z_of_pP_closed(Ph12, A2, p, 14)[0])] += 1
                    ratio = None
                    if kP == kQ and kP < PREC:
                        ratio = uQ * pow(uP, -1, p) % p
                    succ = ratio == d
                    mine = {"vP": kP, "vQ": kQ, "v_dj": vdj_cap,
                            "degenerate": kP >= 2, "predicted_degenerate": vdj_cap >= 2 * e,
                            "success": succ}
                    r = next(rows)
                    total += 1
                    for k, v in mine.items():
                        if r[k] != v:
                            mism[k] += 1
                            if len(mism_rows) < 10:
                                mism_rows.append({"D": D, "p": p, "class": cls, "section": section,
                                                  "key": k, "mine": v, "recorded": r[k]})
                    if r["class"] != cls or r["section"] != section:
                        mism["class/section order"] += 1
                    lift_rec["vP_hist"][kP] += 1
                    lift_rec["success"] += int(succ)
                    lift_rec["n"] += 1
                    # alternative degenerate-rate definitions
                    if kP >= 2:
                        defs = {"spec_literal_all_vP_ge_2": True,
                                "producer_vQ_ge_vP": kQ >= kP and kP < PREC,
                                "symmetric_vQ_eq_vP": kQ == kP and kP < PREC}
                        for name, inc in defs.items():
                            if inc:
                                a_ = alt[name]
                                a_["n"] += 1
                                a_["succ"] += int(succ)
                                a_["inv"] += 1 / p
                                a_["inv1"] += 1 / (p - 1)
                                a_["var"] += (1 / p) * (1 - 1 / p)
                                a_["var1"] += (1 / (p - 1)) * (1 - 1 / (p - 1))
            lift_rec["vP_hist"] = dict(lift_rec["vP_hist"])
            lift_table.append(lift_rec)
        assert next(rows, None) is None, "extra recorded rows"
    alt_out = {}
    for name, a_ in alt.items():
        n = a_["n"]
        ref = a_["inv"] / n
        alt_out[name] = {
            "n": n, "successes": a_["succ"], "rate": a_["succ"] / n, "ref_inv_p": ref,
            "z_pooled_inv_p": (a_["succ"] / n - ref) / math.sqrt(ref * (1 - ref) / n),
            "z_hetero_inv_p": (a_["succ"] - a_["inv"]) / math.sqrt(a_["var"]),
            "z_hetero_inv_p_minus_1": (a_["succ"] - a_["inv1"]) / math.sqrt(a_["var1"]),
        }
    pert_lifts = [l for l in lift_table if l["class"] == "pert_p"]
    ptm = {
        "pert_p_lifts": len(pert_lifts),
        "pert_p_lifts_with_v_dj_ge_2e": [l for l in pert_lifts
                                         if l["v_dj_exact"] is None or l["v_dj_exact"] >= l["two_e"]],
        "pert_p_samples_in_PTM_object_(v_dj<2e)": sum(l["n"] for l in pert_lifts
                                                      if l["v_dj_exact"] is not None and l["v_dj_exact"] < l["two_e"]),
        "of_which_vP_eq_1": sum(l["vP_hist"].get(1, 0) for l in pert_lifts
                                if l["v_dj_exact"] is not None and l["v_dj_exact"] < l["two_e"]),
        "of_which_smart_success": sum(l["success"] for l in pert_lifts
                                      if l["v_dj_exact"] is not None and l["v_dj_exact"] < l["two_e"]),
        "pert_p_v_dj_exact_hist": dict(Counter(l["v_dj_exact"] for l in pert_lifts)),
        "pert_p2_v_dj_exact_hist": dict(Counter(l["v_dj_exact"] for l in lift_table if l["class"] == "pert_p2")),
    }
    return {
        "run_dir": run_dir, "seed": seed, "rows_replayed": total,
        "row_mismatches": dict(mism), "first_mismatch_rows": mism_rows,
        "d_outside_2_to_p_minus_2": d_range_viol,
        "true_valuation_of_capped_rows": {str(k): v for k, v in true_v_beyond_cap.items()},
        "degenerate_rate_definitions": alt_out,
        "ptm1": ptm,
    }


def main():
    repo = sys.argv[1]
    sys.path.insert(0, repo)
    from harness import czlift  # producer module: used ONLY for random_point / EllipticCurve
    out = {}
    for rd in sys.argv[2:]:
        out[os.path.basename(rd.rstrip("/"))] = replay(rd, czlift)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
