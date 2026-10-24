#!/usr/bin/env python3
"""J2 borderline-definition probes and the J3 blind-versus-recorded comparison
(TASK-20261022-3aca4b). Run after the blind seal (blind/SEAL.sha256) and after the J2
recomputation seal (J2_PRE_CHECKPY.sha256).

Usage: python3 -I j2_probes_j3_compare.py <repo-root>
"""
import json
import statistics
import sys

ROOT = sys.argv[1]
EXP = ROOT + "/experiments/EXP-CZLIFT-a255fc"
HERE = EXP + "/reports/validation-20261022"
sys.path.insert(0, EXP + "/implementation")
sys.path.insert(0, ROOT)
import run as producer  # noqa: E402  (used only to evaluate the producer's functions at J3 points)


def model(N, Np):
    return Np * (1.0 - (1.0 - 1.0 / Np) ** N)


def main():
    out = {}
    raws = {r: json.load(open(f"{EXP}/runs/{r}/raw-result.json"))
            for r in ("RUN-CZLIFT-74f172", "RUN-CZLIFT-490b33")}
    # ---------------- J2 probes ----------------
    for run, raw in raws.items():
        curves = raw["raw"]["curves"]
        P = {}
        # heuristic-domain reading of the cell filter: N >= 30 and N <= 0.9 N_p
        cells = [c for cv in curves for c in cv["coverage"] if c["n_points"] >= 30 and c["n_points"] <= 0.9 * c["N_p"]]
        rs = [c["distinct"] / model(c["n_points"], c["N_p"]) for c in cells]
        P["variant_HEUR_domain_N_le_0p9_Np"] = {
            "cells": len(rs), "median": statistics.median(rs),
            "frac_above_1p5": sum(r > 1.5 for r in rs) / len(rs),
            "frac_below_0p5": sum(r < 0.5 for r in rs) / len(rs)}
        # 37a1: is every row maximally spread (distinct == min(N, N_p))?
        c37 = [cv for cv in curves if cv["label"] == "37a1"][0]
        P["37a1_rows_distinct_eq_min_N_Np"] = [sum(1 for c in c37["coverage"]
                                                   if c["distinct"] == min(c["n_points"], c["N_p"])),
                                               len(c37["coverage"])]
        # twist rows: O counted once, filter on the corrected N
        tw = [(cv["label"], t) for cv in curves for t in (cv.get("twists") or [])]
        if tw:
            def tmet(rows, sub_one):
                keep = []
                for lab, t in rows:
                    N = t["n_base_points"] + t["n_twist_points"] - (1 if sub_one else 0)
                    m = model(N, t["N_p"])
                    if N >= 30 and m <= 0.9 * t["N_p"]:
                        keep.append((lab, t["distinct_union"] / m))
                r = [x for _, x in keep]
                return {"cells": len(r), "median": statistics.median(r) if r else None,
                        "upper_median_producer_style": sorted(r)[len(r) // 2] if r else None,
                        "frac_above_1p5": (sum(x > 1.5 for x in r) / len(r)) if r else None,
                        "per_curve": {l: sum(1 for k, _ in keep if k == l) for l in sorted({k for k, _ in tw})}}
            P["twist_as_recorded_N_base_plus_N_twist"] = tmet(tw, False)
            P["twist_O_counted_once"] = tmet(tw, True)
            P["twist_rows_with_only_O_from_twist"] = sum(1 for _, t in tw if t["n_twist_points"] == 1)
            P["twist_rows_total"] = len(tw)
            P["twist_curve_D_pairs_with_nontrivial_twist_points"] = sorted({
                (lab, t["D"], t["n_twist_points"] - 1) for lab, t in tw if t["n_twist_points"] > 1})
        out[run] = P

    # ---------------- J3 comparison ----------------
    blind = json.load(open(HERE + "/blind/blind_output.json"))
    J3 = {"blind_seal": open(HERE + "/blind/SEAL.sha256").read().strip().splitlines()}
    rows = []
    for run, raw in raws.items():
        for cv in raw["raw"]["curves"]:
            lab = cv["label"]
            if lab not in ("11a1", "37a1"):
                continue
            for H, n in cv["counts"].items():
                b_slow = blind["slow_search"][lab]["N_E"].get(H)
                b_gl = blind["grouplaw_crosscheck"][lab]["N_E"].get(H)
                rows.append({"run": run, "curve": lab, "H": int(H), "recorded": n,
                             "blind_slow_search": b_slow, "blind_group_law": b_gl,
                             "agree": all(v is None or v == n for v in (b_slow, b_gl))})
    J3["N_E_rows"] = rows
    J3["N_E_all_agree"] = all(r["agree"] for r in rows)
    J3["headline"] = {
        "11a1_H300": {"blind": blind["headline"]["N_E_11a1_H300"],
                      "recorded": [raws[r]["raw"]["curves"][0]["counts"]["300"] for r in raws]},
        "11a1_H1000": {"blind": blind["headline"]["N_E_11a1_H1000"],
                       "recorded": [raws[r]["raw"]["curves"][0]["counts"]["1000"] for r in raws]},
        "37a1_H300": {"blind": blind["headline"]["N_E_37a1_H300"],
                      "recorded": [raws[r]["raw"]["curves"][1]["counts"]["300"] for r in raws]},
        "37a1_H1000": {"blind": blind["headline"]["N_E_37a1_H1000"],
                       "recorded": [raws[r]["raw"]["curves"][1]["counts"]["1000"] for r in raws]},
    }
    # uniform model for 37a1 at 101 and 1009: the producer never used these primes
    # (its prime list starts at 103), so evaluate the producer's own functions there.
    ai = [0, 0, 1, -1, 0]
    um = {}
    for p in ("101", "1009"):
        bp = blind["uniform_model_37a1"][p]
        Np_prod = producer.curve_order_mod_p(ai, int(p))
        rws = []
        for r in bp["rows"]:
            mp = producer.model_distinct(Np_prod, r["N"])
            rws.append({"H": r["H"], "N": r["N"], "blind_model": r["model"], "producer_function_model": mp,
                        "abs_diff": abs(mp - r["model"])})
        um[p] = {"blind_N_p": bp["N_p"], "producer_curve_order_mod_p": Np_prod,
                 "N_p_agree": Np_prod == bp["N_p"], "rows": rws,
                 "max_abs_model_diff": max(x["abs_diff"] for x in rws)}
    J3["uniform_model_37a1"] = um
    J3["producer_primes_include_101_or_1009"] = any(
        int(p) in raws["RUN-CZLIFT-74f172"]["raw"]["curves"][1]["primes"] for p in ("101", "1009"))
    # blind formula versus the recorded model on every recorded 37a1 cell (same N, N_p)
    worst = 0.0
    for raw in raws.values():
        for c in raw["raw"]["curves"][1]["coverage"]:
            worst = max(worst, abs(model(c["n_points"], c["N_p"]) - c["model_distinct"]))
    J3["blind_formula_vs_recorded_model_all_37a1_cells_max_abs_diff"] = worst
    out["J3"] = J3
    json.dump(out, sys.stdout, indent=1, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
