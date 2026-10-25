#!/usr/bin/env python3
"""Aggregate rt_d3_output.json: probability (rows independent) that the producer-style shuffled
control spikes somewhere on the D=-3 y-digit rows of a seed, overall and per digit (the
aggregate-reading veto), at margins 12 / 10 / 9 / 8; and the real-vs-matched-null DC ranks.
Usage: rt_d3_aggregate.py RT_D3_OUT.json OUT.json"""
import json, math, statistics as st, sys
res = json.load(open(sys.argv[1]))
out = {"per_seed": {}, "matched_null_dc_rank_of_real": {}}
for run in sorted({r["run"] for r in res}):
    sel = [r for r in res if r["run"] == run]
    d = {"records": [(r["p"], r["n"]) for r in sel]}
    for m in ("12", "10", "9", "8"):
        q_all = 1.0
        per_digit = {}
        for i in (1, 2, 3, 4):
            q = 1.0
            for r in sel:
                q *= 1 - r["digits"][f"y{i}"]["shuffled_spike_rate"][m]
            per_digit[f"y{i}"] = round(1 - q, 3)
            q_all *= q
        d[f"margin_{m}"] = {"P_shuffled_spikes_total_gt_0_from_D3_y_rows": round(1 - q_all, 3),
                            "P_veto_per_digit_aggregate_reading": per_digit}
    out["per_seed"][run] = d
ranks = [r["digits"][f"y{i}"]["matched_dc_rank_of_real"] for r in res for i in (1, 2, 3, 4)]
out["matched_null_dc_rank_of_real"] = {"rows": len(ranks), "mean": st.mean(ranks), "min": min(ranks),
                                       "below_0.05": sum(x < 0.05 for x in ranks),
                                       "note": "fraction of 60 symmetry-matched null draws whose DC max >= the real DC max; uniform(0,1) if the mu_6 symmetry explains the elevation"}
nd = [(r["digits"][f"y{i}"]["real_nondc"], r["digits"][f"y{i}"]["matched_nondc_mean"]) for r in res for i in (1, 2, 3, 4)]
out["real_nondc_minus_matched_nondc_mean"] = {"mean": st.mean(a - b for a, b in nd), "max": max(a - b for a, b in nd)}
p_both = (1 - out["per_seed"]["RUN-CZLIFT-037e5f"]["margin_12"]["P_shuffled_spikes_total_gt_0_from_D3_y_rows"]) * \
         (1 - out["per_seed"]["RUN-CZLIFT-d37ca4"]["margin_12"]["P_shuffled_spikes_total_gt_0_from_D3_y_rows"])
out["P_shuffled_zero_on_both_seeds_margin_12_from_D3_y_rows_alone"] = round(p_both, 3)
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps(out, indent=1))
