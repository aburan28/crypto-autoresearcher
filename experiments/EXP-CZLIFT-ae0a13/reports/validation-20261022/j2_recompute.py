"""J2: validator-owned recomputation of every frozen metric from raw-result.json.

Written BEFORE reading implementation/check.py or run.py (only the raw-result
key structure had been inspected).  Definitions are taken from the
specification; where the specification leaves a convention open (denominator,
standard-error form, arm-difference z), every candidate is computed and the
one matching the record is reported, so a mismatch cannot hide behind a
convention choice.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[2] / "runs"
SECTIONS = ["hensel_random", "naive", "teichmuller"]
ARMS = ["cm_canonical", "random_naive"]
TORSION = {
    "canonicity_rate": "canonical",
    "homomorphism_rate_torsion": "hom_tor",
    "degeneracy_rate_torsion": "degenerate_tor",
    "torsion_reduces_rate": "tor_reduces",
    "scalar_mult_equivariance_rate": "scalar_mult_tor",
}
K = 4


def rows_of(raw, arm=None):
    for c in raw["raw"]["curves"]:
        if arm is None or c["arm"] == arm:
            for r in c["rows"]:
                yield c, r


def section_metrics(raw, sec, arm):
    rs = list(rows_of(raw, None if arm == "all" else arm))
    n = len(rs)
    succ = sum(1 for _, r in rs if r["sections"][sec]["success"])
    defined = sum(1 for _, r in rs if r["sections"][sec]["ratio_defined"])
    v11 = sum(1 for _, r in rs if r["sections"][sec]["vP"] == 1 and r["sections"][sec]["vQ"] == 1)
    vP1 = sum(1 for _, r in rs if r["sections"][sec]["vP"] == 1)
    ident_all = sum(1 for _, r in rs if r["sections"][sec]["identity_holds"])
    ident_def = sum(1 for _, r in rs if r["sections"][sec]["ratio_defined"] and r["sections"][sec]["identity_holds"])
    hom2 = sum(1 for _, r in rs if r["sections"][sec]["hom_prec2"])
    inv = [1.0 / c["p"] for c, _ in rs]
    ref = sum(inv) / n
    rate = succ / n
    se_mean = math.sqrt(ref * (1 - ref) / n)
    se_exact = math.sqrt(sum(q * (1 - q) for q in inv)) / n
    # rows where a success was recorded on an undefined ratio (must be 0)
    succ_undefined = sum(1 for _, r in rs if r["sections"][sec]["success"] and not r["sections"][sec]["ratio_defined"])
    # rows where ratio_defined disagrees with vP == vQ == 1 / vP == 1
    def_vs_v11 = sum(1 for _, r in rs if r["sections"][sec]["ratio_defined"] != (r["sections"][sec]["vP"] == 1 and r["sections"][sec]["vQ"] == 1))
    def_vs_vP1 = sum(1 for _, r in rs if r["sections"][sec]["ratio_defined"] != (r["sections"][sec]["vP"] == 1))
    return {
        "n": n, "successes": succ, "success_rate": rate,
        "reference_inv_p": ref,
        "z_score_mean_ref_se": (rate - ref) / se_mean,
        "z_score_exact_bernoulli_se": (rate - ref) / se_exact,
        "ratio_defined_count": defined,
        "frac_ratio_defined": defined / n,
        "frac_vP1_and_vQ1": v11 / n,
        "frac_vP1": vP1 / n,
        "identity_rate_all_rows": ident_all / n,
        "identity_rate_defined_rows": (ident_def / defined) if defined else None,
        "identity_failures": n - ident_all,
        "homomorphism_rate_prec2": hom2 / n,
        "hom_prec2_count": hom2,
        "success_on_undefined_ratio": succ_undefined,
        "ratio_defined_vs_v11_disagreements": def_vs_v11,
        "ratio_defined_vs_vP1_disagreements": def_vs_vP1,
    }


def arm_difference(s_cm, s_rn):
    d = s_cm["success_rate"] - s_rn["success_rate"]
    n1, n2 = s_cm["n"], s_rn["n"]
    x1, x2 = s_cm["successes"], s_rn["successes"]
    pooled = (x1 + x2) / (n1 + n2)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    p1, p2 = x1 / n1, x2 / n2
    se_unpooled = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    r1, r2 = s_cm["reference_inv_p"], s_rn["reference_inv_p"]
    se_ref = math.sqrt(r1 * (1 - r1) / n1 + r2 * (1 - r2) / n2)
    # null-referenced difference: (rate_cm - ref_cm) - (rate_rn - ref_rn)
    return {
        "difference": d,
        "z_pooled": (d / se_pooled) if se_pooled > 0 else None,
        "z_unpooled": (d / se_unpooled) if se_unpooled > 0 else None,
        "z_reference_se": d / se_ref,
        "z_reference_se_null_centered": (d - (r1 - r2)) / se_ref,
        "pooled_rate": pooled,
    }


def recompute(run_id):
    raw = json.loads((RUNS / run_id / "raw-result.json").read_text())
    out = {"run_id": run_id, "seed": raw["metrics"]["seed"]}
    rs = list(rows_of(raw))
    out["pairs_total"] = len(rs)
    for m, key in TORSION.items():
        out[m] = sum(1 for _, r in rs if r[key]) / len(rs)
        out[m + "_failures"] = sum(1 for _, r in rs if not r[key])
    costs = [r["tor_cost_additions"] for _, r in rs]
    bounds = [2 * (c["n"].bit_length() + (c["p"] ** K).bit_length()) + 1 for c, _ in rs]
    out["torsion_cost_mean_additions"] = sum(costs) / len(costs)
    out["torsion_cost_max"] = max(costs)
    out["torsion_cost_rowwise_within_bound"] = all(c <= b for c, b in zip(costs, bounds))
    out["torsion_cost_rowwise_violations"] = sum(1 for c, b in zip(costs, bounds) if c > b)
    out["torsion_cost_mean_bound"] = sum(bounds) / len(bounds)
    out["torsion_cost_mean_within_mean_bound"] = out["torsion_cost_mean_additions"] <= out["torsion_cost_mean_bound"]
    out["min_slack_cost_vs_bound"] = min(b - c for c, b in zip(costs, bounds))
    out["sections"] = {s: {a: section_metrics(raw, s, a) for a in ARMS + ["all"]} for s in SECTIONS}
    out["arm_difference"] = {s: arm_difference(out["sections"][s]["cm_canonical"], out["sections"][s]["random_naive"]) for s in SECTIONS}
    out["curves_cm"] = sum(1 for c in raw["raw"]["curves"] if c["arm"] == "cm_canonical")
    out["curves_random"] = sum(1 for c in raw["raw"]["curves"] if c["arm"] == "random_naive")
    out["rows_per_curve"] = [[c["arm"], c["label"], c["p"], c["n"], len(c["rows"])] for c in raw["raw"]["curves"]]
    out["rows_missing_vs_16"] = sum(16 - len(c["rows"]) for c in raw["raw"]["curves"])
    out["precision_all_4"] = all(c["precision"] == K for c in raw["raw"]["curves"])
    out["n_prime_ge11_ne_p_N_odd_n_div_N"] = all(
        c["n"] >= 11 and c["n"] != c["p"] and c["N"] % 2 == 1 and c["N"] % c["n"] == 0
        and all(c["n"] % q for q in range(2, int(c["n"] ** 0.5) + 1))
        for c in raw["raw"]["curves"])
    out["cm_p_range_ok"] = all(50 <= c["p"] <= 600 for c in raw["raw"]["curves"] if c["arm"] == "cm_canonical")
    out["random_primes"] = sorted(c["p"] for c in raw["raw"]["curves"] if c["arm"] == "random_naive")
    # ---------------------------------------------- compare with record
    rec = raw["metrics"]
    cmp = []

    def chk(name, mine, theirs):
        same = (mine is None and theirs is None) or (
            mine is not None and theirs is not None and
            (mine == theirs if isinstance(theirs, (bool, int)) and not isinstance(theirs, float) else abs(mine - theirs) <= 1e-12))
        cmp.append({"metric": name, "validator": mine, "recorded": theirs, "match": bool(same)})

    chk("pairs_total", out["pairs_total"], rec["pairs_total"])
    for m in TORSION:
        chk(m, out[m], rec[m])
    chk("torsion_cost_mean_additions", out["torsion_cost_mean_additions"], rec["torsion_cost_mean_additions"])
    chk("torsion_cost_within_bound(rowwise)", out["torsion_cost_rowwise_within_bound"], rec["torsion_cost_within_bound"])
    chk("curves_cm", out["curves_cm"], rec["curves_cm"])
    chk("curves_random", out["curves_random"], rec["curves_random"])
    conv = {}
    for s in SECTIONS:
        for a in ARMS + ["all"]:
            mine, theirs = out["sections"][s][a], rec["sections"][s][a]
            chk(f"{s}.{a}.n", mine["n"], theirs["n"])
            chk(f"{s}.{a}.success_rate", mine["success_rate"], theirs["success_rate"])
            chk(f"{s}.{a}.reference_inv_p", mine["reference_inv_p"], theirs["reference_inv_p"])
            chk(f"{s}.{a}.homomorphism_rate_prec2", mine["homomorphism_rate_prec2"], theirs["homomorphism_rate_prec2"])
            for cand in ("z_score_mean_ref_se", "z_score_exact_bernoulli_se"):
                if abs(mine[cand] - theirs["z_score"]) <= 1e-9:
                    conv.setdefault("z_score", set()).add(cand)
            chk(f"{s}.{a}.z_score", mine["z_score_mean_ref_se"], theirs["z_score"])
            for cand in ("frac_ratio_defined", "frac_vP1_and_vQ1", "frac_vP1"):
                if abs(mine[cand] - theirs["frac_valuation_1"]) <= 1e-12:
                    conv.setdefault("frac_valuation_1", set()).add(cand)
            # First pass compared frac_vP1_and_vQ1 (7 + 5 cell mismatches, preserved in
            # j2_recompute_firstpass_*); every cell matches frac_vP1 == frac_ratio_defined.
            chk(f"{s}.{a}.frac_valuation_1", mine["frac_vP1"], theirs["frac_valuation_1"])
            for cand in ("identity_rate_all_rows", "identity_rate_defined_rows"):
                if mine[cand] is not None and abs(mine[cand] - theirs["identity_rate"]) <= 1e-12:
                    conv.setdefault("identity_rate", set()).add(cand)
            chk(f"{s}.{a}.identity_rate", mine["identity_rate_all_rows"], theirs["identity_rate"])
        md, td = out["arm_difference"][s], rec["arm_difference"][s]
        chk(f"arm_difference.{s}.difference", md["difference"], td["difference"])
        for cand in ("z_pooled", "z_unpooled", "z_reference_se", "z_reference_se_null_centered"):
            if (md[cand] is None and td["z_score"] is None) or (
                    md[cand] is not None and td["z_score"] is not None and abs(md[cand] - td["z_score"]) <= 1e-9):
                conv.setdefault("arm_difference_z", set()).add(cand)
        chk(f"arm_difference.{s}.z_score(pooled)", md["z_pooled"], td["z_score"])
    out["comparison"] = cmp
    out["comparison_mismatches"] = [c for c in cmp if not c["match"]]
    out["conventions_matching_record"] = {k: sorted(v) for k, v in conv.items()}
    # ---------------------------------------------- criteria (validator's evaluation)
    torsion_ok = all(out[m] == 1.0 for m in TORSION)
    ident_ok = all(out["sections"][s][a]["identity_rate_all_rows"] == 1.0 for s in SECTIONS for a in ARMS)
    z_ok = all(abs(out["sections"][s][a]["z_score_mean_ref_se"]) <= 4 for s in SECTIONS for a in ARMS)
    z_ok_exact = all(abs(out["sections"][s][a]["z_score_exact_bernoulli_se"]) <= 4 for s in SECTIONS for a in ARMS)
    armd = {s: out["arm_difference"][s]["z_pooled"] for s in SECTIONS}
    armd_ok_defined = all(abs(z) <= 3 for z in armd.values() if z is not None)
    armd_undefined = [s for s, z in armd.items() if z is None]
    armd_alt = {s: out["arm_difference"][s]["z_reference_se"] for s in SECTIONS}
    out["criteria"] = {
        "torsion_rates_all_1": torsion_ok,
        "identity_rates_all_1": ident_ok,
        "section_abs_z_le_4_each_arm(mean-ref SE)": z_ok,
        "section_abs_z_le_4_each_arm(exact Bernoulli SE)": z_ok_exact,
        "section_z_gt_4_any_arm": any(out["sections"][s][a]["z_score_mean_ref_se"] > 4 for s in SECTIONS for a in ARMS),
        "arm_difference_pooled_z": armd,
        "arm_difference_abs_z_le_3_where_defined": armd_ok_defined,
        "arm_difference_pooled_z_undefined_for": armd_undefined,
        "arm_difference_reference_se_z": armd_alt,
        "arm_difference_abs_z_le_3_reference_se": all(abs(z) <= 3 for z in armd_alt.values()),
        "torsion_cost_within_bound_rowwise": out["torsion_cost_rowwise_within_bound"],
        "max_abs_section_z": max(abs(out["sections"][s][a]["z_score_mean_ref_se"]) for s in SECTIONS for a in ARMS),
    }
    return out


def main():
    res = {r: recompute(r) for r in ["RUN-CZLIFT-dab752", "RUN-CZLIFT-5b2581"]}
    here = Path(__file__).resolve().parent
    (here / "j2_recompute_output.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=list) + "\n")
    for r, o in res.items():
        print("==", r, "seed", o["seed"], "pairs", o["pairs_total"], "missing_vs_16", o["rows_missing_vs_16"])
        print("  mismatches:", len(o["comparison_mismatches"]), "of", len(o["comparison"]))
        for m in o["comparison_mismatches"]:
            print("   ", m)
        print("  conventions:", o["conventions_matching_record"])
        print("  criteria:", json.dumps(o["criteria"]))
        print("  cost mean", o["torsion_cost_mean_additions"], "max", o["torsion_cost_max"],
              "rowwise ok", o["torsion_cost_rowwise_within_bound"], "min slack", o["min_slack_cost_vs_bound"])
        for s in SECTIONS:
            for a in ARMS:
                m = o["sections"][s][a]
                print(f"   {s:14s} {a:13s} n={m['n']:4d} succ={m['successes']} rate={m['success_rate']:.5f} ref={m['reference_inv_p']:.5f} "
                      f"z={m['z_score_mean_ref_se']:+.3f} zx={m['z_score_exact_bernoulli_se']:+.3f} defined={m['ratio_defined_count']} "
                      f"ident_fail={m['identity_failures']} succ_undef={m['success_on_undefined_ratio']} "
                      f"def!=v11={m['ratio_defined_vs_v11_disagreements']} hom2={m['hom_prec2_count']}")
        print("  structure: precision4", o["precision_all_4"], "n-criteria", o["n_prime_ge11_ne_p_N_odd_n_div_N"],
              "cm p range", o["cm_p_range_ok"], "random primes", o["random_primes"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
