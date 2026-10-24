#!/usr/bin/env python3
"""Red team TASK-20261023-792040, joints R1/R2/PTM-1: scope, power and threshold audit.

Reads the two admissible raw-result.json files by key (no driver code) and the
validator's replay rows (argmax indices) and reports:
  * per curve record: h = (n-1)/2, T = ln((p-1)n) + 12, blind (h <= T: the
    trivial bound X <= h makes 'max < T' a tautology), and the single-pair
    detection floor rho_min = sqrt(T/h) (normalised correlation a noiseless
    leak must have with one (psi, chi) pair to reach T);
  * the number of tests and the family-wise level the margin 12 buys, against
    the margin a 5 % family-wise level per seed would need, calibrated on the
    uniform control's own maxima;
  * the D = -3 y-digit elevation real vs shuffled vs uniform, and where the
    maxima sit (chi index t = 0, the permutation-invariant DC term).
Usage: rt_scope.py OUT.json
"""
from __future__ import annotations

import json
import math
import statistics as st
import sys

BASE = "experiments/EXP-CZLIFT-1a3453"
RUNS = ["RUN-CZLIFT-037e5f", "RUN-CZLIFT-d37ca4"]
REPLAY = f"{BASE}/reports/validation-20261022/j2_replay_output.json"
GAMMA = 0.5772156649
MARGIN = 12.0


def main(out_path: str) -> None:
    replay = json.load(open(REPLAY))
    rep = {(e["run"], e["index"]): e for e in replay}
    records = []
    for run in RUNS:
        raw = json.load(open(f"{BASE}/runs/{run}/raw-result.json"))
        for idx, c in enumerate(raw["raw"]["curves"]):
            p, n = c["p"], c["n"]
            h = (n - 1) // 2
            T = math.log((p - 1) * n) + MARGIN
            r = rep[(run, idx)]
            assert r["p"] == p and r["n"] == n
            rows = []
            for row, rrow in zip(c["rows"], r["replay"]["rows"]):
                assert row["coord"] == rrow["coord"] and row["digit"] == rrow["digit"]
                assert abs(row["threshold"] - T) < 1e-9
                rows.append({**row, "argmax_t": rrow["argmax_t"], "shuffled_argmax_t": rrow["shuffled_argmax_t"],
                             "half_max_multiplicity": rrow.get("half_max_multiplicity"),
                             "half_distinct_values": rrow.get("half_distinct_values")})
            records.append({"run": run, "index": idx, "arm": c["arm"], "label": c["label"], "p": p, "n": n,
                            "N": c["N"], "cofactor": c["N"] // n, "h": h, "T": T, "blind": h <= T,
                            "rho_min": math.sqrt(T / h) if h > 0 else None, "rows": rows})

    out = {"records": [{k: v for k, v in r.items() if k != "rows"} for r in records]}

    # ---- power / blind zone
    def cnt(pred):
        return sum(1 for r in records if pred(r))
    summary = {}
    for run in RUNS:
        for arm in ("cm_canonical", "random_naive"):
            sel = [r for r in records if r["run"] == run and r["arm"] == arm]
            summary[f"{run}:{arm}"] = {"records": len(sel), "blind": sum(r["blind"] for r in sel),
                                       "power_bearing": sum(not r["blind"] for r in sel)}
    pb = [r for r in records if not r["blind"]]
    bl = [r for r in records if r["blind"]]
    out["blind_zone"] = {
        "total": len(records), "blind": len(bl), "power_bearing": len(pb), "by_run_arm": summary,
        "max_n_blind": max(r["n"] for r in bl), "min_n_power": min(r["n"] for r in pb),
        "rho_min_power_bearing": {"min": min(r["rho_min"] for r in pb), "median": st.median(r["rho_min"] for r in pb),
                                  "max": max(r["rho_min"] for r in pb)},
        "power_bearing_with_rho_min_below_0.5": cnt(lambda r: not r["blind"] and r["rho_min"] < 0.5),
        "D_labels_power_bearing": sorted({r["label"] for r in pb}),
        "unique_curves_power_bearing": len({(r["arm"], r["p"], r["n"]) for r in pb}),
        "random_arm_power_bearing_unique": len({(r["p"], r["n"]) for r in pb if r["arm"] == "random_naive"}),
    }

    # ---- tests and family-wise level
    per_seed_rows = {"signal_higher": 36 * 8, "signal_digit0": 36 * 2, "shuffled": 36 * 10, "uniform": 36 * 10}
    tail_row = math.exp(-MARGIN)  # Bonferroni over N pairs (conservative: X(a,t) = X(p-a,n-t) halves it)
    out["fwer"] = {
        "pairs_per_row": "N = (p-1) n, including the trivial chi (t = 0); distinct values N/2 by X(a,t)=X(p-a,n-t)",
        "per_row_bonferroni_tail": tail_row,
        "per_row_tail_distinct_values": tail_row / 2,
        "rows_per_seed": per_seed_rows,
        "per_seed_fwer_signal_higher_digits": 288 * tail_row,
        "per_seed_fwer_all_1080_rows": 1080 * tail_row,
        "margin_for_5pct_fwer_per_seed_over_288_higher_rows_bonferroni": math.log(288 / 0.05),
        "margin_for_5pct_fwer_per_seed_over_1080_rows_bonferroni": math.log(1080 / 0.05),
    }
    # empirical calibration from the uniform control: excess of the row maximum over ln N
    ex_u = [row["uniform_max_power"] - (r["T"] - MARGIN) for r in pb for row in r["rows"]]
    ex_u_all = [row["uniform_max_power"] - (r["T"] - MARGIN) for r in records for row in r["rows"]]
    # Gumbel fit by moments: max = ln N + mu + G * beta;  mean = mu + gamma*beta, sd = pi beta / sqrt 6
    m, s = st.mean(ex_u), st.pstdev(ex_u)
    beta = s * math.sqrt(6) / math.pi
    mu = m - GAMMA * beta
    out["uniform_calibration_power_bearing"] = {
        "rows": len(ex_u), "mean_excess_over_lnN": m, "sd": s, "max": max(ex_u),
        "gumbel_mu": mu, "gumbel_beta": beta,
        "implied_margin_5pct_fwer_288_rows": mu + beta * (-math.log(-math.log(1 - 0.05 / 288))),
        "implied_margin_5pct_fwer_1080_rows": mu + beta * (-math.log(-math.log(1 - 0.05 / 1080))),
        "note": "row max = ln N + mu + beta*Gumbel; mu < gamma because pairs are conjugate-paired and zero-padded FFT bins correlate",
    }
    out["uniform_calibration_all_rows"] = {"rows": len(ex_u_all), "mean_excess_over_lnN": st.mean(ex_u_all),
                                           "max": max(ex_u_all)}

    # detection floor under the frozen margin and under the 5 % FWER margin
    m5 = out["fwer"]["margin_for_5pct_fwer_per_seed_over_1080_rows_bonferroni"]
    alt = []
    for r in records:
        T5 = r["T"] - MARGIN + m5
        alt.append({"p": r["p"], "n": r["n"], "blind_at_margin_12": r["blind"], "blind_at_5pct_margin": r["h"] <= T5,
                    "rho_min_12": r["rho_min"], "rho_min_5pct": math.sqrt(T5 / r["h"])})
    out["margin_sensitivity"] = {
        "margin_5pct_fwer": m5,
        "blind_at_margin_12": sum(a["blind_at_margin_12"] for a in alt),
        "blind_at_5pct_margin": sum(a["blind_at_5pct_margin"] for a in alt),
        "rho_min_ratio_median": st.median(a["rho_min_5pct"] / a["rho_min_12"] for a in alt if not a["blind_at_margin_12"]),
    }

    # ---- excess over the Exp(1) expectation by class, non-blind only
    def cls(r, row):
        if r["label"] == "D=-3" and row["coord"] == "y" and row["digit"] >= 1:
            return "D-3_y_higher"
        if r["label"] == "D=-3":
            return "D-3_other"
        return "other_higher" if row["digit"] >= 1 else "other_digit0"
    classes = {}
    for r in pb:
        e0 = math.log((r["p"] - 1) * r["n"] / 2) + GAMMA
        for row in r["rows"]:
            c = classes.setdefault(cls(r, row), {"real": [], "shuffled": [], "uniform": [], "real_t0": 0, "shuf_t0": 0,
                                                 "rows": 0, "max_mult": []})
            c["rows"] += 1
            c["real"].append(row["max_power"] - e0)
            c["shuffled"].append(row["shuffled_max_power"] - e0)
            c["uniform"].append(row["uniform_max_power"] - e0)
            c["real_t0"] += int(row["argmax_t"] == 0)
            c["shuf_t0"] += int(row["shuffled_argmax_t"] == 0)
            c["max_mult"].append(row["half_max_multiplicity"])
    out["excess_over_exp1_expectation_power_bearing"] = {
        k: {"rows": v["rows"], "real_mean": st.mean(v["real"]), "shuffled_mean": st.mean(v["shuffled"]),
            "uniform_mean": st.mean(v["uniform"]), "real_argmax_at_dc": v["real_t0"],
            "shuffled_argmax_at_dc": v["shuf_t0"], "half_max_multiplicity_max": max(v["max_mult"])}
        for k, v in classes.items()}

    # ---- closest approaches and the margin at which a first spike would have appeared
    tops = []
    for r in records:
        for row in r["rows"]:
            for kind, key, tkey in (("real", "max_power", "argmax_t"), ("shuffled", "shuffled_max_power", "shuffled_argmax_t"),
                                    ("uniform", "uniform_max_power", None)):
                tops.append({"run": r["run"], "label": r["label"], "p": r["p"], "n": r["n"], "row": f"{row['coord']}{row['digit']}",
                             "kind": kind, "excess_over_T": row[key] - r["T"],
                             "margin_of_first_spike": row[key] - (r["T"] - MARGIN),
                             "argmax_t": row[tkey] if tkey else None})
    out["closest_approaches"] = {kind: sorted([t for t in tops if t["kind"] == kind], key=lambda t: -t["excess_over_T"])[:6]
                                 for kind in ("real", "shuffled", "uniform")}
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("blind_zone", "fwer", "uniform_calibration_power_bearing", "margin_sensitivity",
                                           "excess_over_exp1_expectation_power_bearing")}, indent=1))
    for kind, lst in out["closest_approaches"].items():
        for t in lst[:4]:
            print(kind, t)


if __name__ == "__main__":
    main(sys.argv[1])
