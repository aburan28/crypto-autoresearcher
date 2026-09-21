#!/usr/bin/env python3
"""N1, step (3) continued: recompute ARM C's z-scores from the JSON's OWN counts
and identify which variance each uses.  No producer code read."""
import json
import math
import statistics as st

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/c0-lower-bound.json"
d = json.load(open(RUN))
cells = d["exact_enumeration_measured"]
rows = []
for c in cells:
    curve = [c["empty_cosets_curve_structured_V"]] + list(c["empty_cosets_curve_random_V"])
    nulls = list(c["empty_cosets_null_structured_V"]) + list(c["empty_cosets_null_random_V"])
    cm = sum(curve) / len(curve)
    nm = sum(nulls) / len(nulls)
    sd_pop = st.pstdev(nulls)
    sd_samp = st.stdev(nulls)
    # which one does the JSON's null_sd equal?
    which_sd = ("population" if abs(sd_pop - c["null_sd"]) < 1e-9
                else "sample(ddof=1)" if abs(sd_samp - c["null_sd"]) < 1e-9 else "neither")
    if c["null_sd"] == 0:
        print("  SKIP n=%d k=%d: null_sd = 0 (nulls all %d); curve structured %d, "
              % (c["n"], c["k"], nulls[0], c["empty_cosets_curve_structured_V"])
              + f"curve structured {c['empty_cosets_curve_structured_V']}, "
              f"curve random {c['empty_cosets_curve_random_V']}, json z = {c['curve_minus_null_in_null_sd']}")
        continue
    z_producer = (cm - nm) / c["null_sd"]
    # proper standard error of the difference of two means (independent draws)
    se_diff = c["null_sd"] * math.sqrt(1 / len(curve) + 1 / len(nulls))
    z_diff = (cm - nm) / se_diff
    # binomial theoretical sd of one draw of #empty cosets
    ncos, k = c["n_cosets"], c["k"]
    q = (1 - c["measured_delta"]) ** (2 ** k)
    sd_binom = math.sqrt(ncos * q * (1 - q))
    z_struct_producer = (c["empty_cosets_curve_structured_V"] - nm) / c["null_sd"]
    rows.append(dict(n=c["n"], k=k,
                     curve_mean=cm, json_curve_mean=c["curve_mean"],
                     curve_mean_match=abs(cm - c["curve_mean"]) < 1e-9,
                     null_mean=nm, json_null_mean=c["null_mean"],
                     null_mean_match=abs(nm - c["null_mean"]) < 1e-9,
                     json_null_sd=c["null_sd"], null_sd_is=which_sd,
                     sd_binomial_theory=sd_binom,
                     z_producer=z_producer, json_z=c["curve_minus_null_in_null_sd"],
                     z_match=abs(z_producer - c["curve_minus_null_in_null_sd"]) < 1e-9,
                     z_diff_of_means=z_diff,
                     z_struct_producer=z_struct_producer,
                     z_struct_vs_binomial_sd=(c["empty_cosets_curve_structured_V"]
                                              - c["predicted_empty_cosets_binomial"]) / sd_binom))

print(f"{'n':>4}{'k':>3} | {'null_sd is':>15} | {'z_prod':>8} {'json_z':>8} ok | "
      f"{'z_diffmeans':>11} | {'z_struct':>9} | {'z_str/binom':>11} | {'sd_json':>9} {'sd_theory':>9}")
for r in rows:
    print(f"{r['n']:>4}{r['k']:>3} | {r['null_sd_is']:>15} | {r['z_producer']:>8.3f} "
          f"{r['json_z']:>8.3f} {'Y' if r['z_match'] else 'N'} | {r['z_diff_of_means']:>11.3f} | "
          f"{r['z_struct_producer']:>9.3f} | {r['z_struct_vs_binomial_sd']:>11.3f} | "
          f"{r['json_null_sd']:>9.2f} {r['sd_binomial_theory']:>9.2f}")

zp = [r["z_producer"] for r in rows]
zd = [r["z_diff_of_means"] for r in rows]
zs = [r["z_struct_producer"] for r in rows]
zb = [r["z_struct_vs_binomial_sd"] for r in rows]
comp = d["comparison"]
print(f"\nproducer pooled z: mean {st.mean(zp):.5f} (json {comp['curve_minus_null_in_null_sd']['mean']:.5f}), "
      f"max|z| {max(abs(x) for x in zp):.6f} (json {comp['curve_minus_null_in_null_sd']['max_abs']:.6f}), "
      f"n>2sd {sum(1 for x in zp if abs(x) > 2)} (json {comp['curve_minus_null_in_null_sd']['cells_beyond_2_sd']})")
print(f"  NB the JSON's mean/max_abs are over {len(comp['curve_minus_null_in_null_sd']['values'])} values, "
      f"I have {len(zp)} cells")
print(f"difference-of-means z: mean {st.mean(zd):.4f}, max|z| {max(abs(x) for x in zd):.4f}, "
      f"n>2sd {sum(1 for x in zd if abs(x) > 2)}, n>3sd {sum(1 for x in zd if abs(x) > 3)}")
print(f"structured-only z (producer): max|z| {max(abs(x) for x in zs):.6f} "
      f"(json {comp['structured_V_only_max_abs_sd']:.6f}), n>2sd {sum(1 for x in zs if abs(x) > 2)}")
print(f"structured-only z vs BINOMIAL theory sd: max|z| {max(abs(x) for x in zb):.4f}, "
      f"n>2sd {sum(1 for x in zb if abs(x) > 2)}")
print("\nJSON structured_V_only_cells_beyond_2_sd:", json.dumps(comp["structured_V_only_cells_beyond_2_sd"]))
print("cells with |z_diffmeans| > 2:", [(r["n"], r["k"], round(r["z_diff_of_means"], 3))
                                        for r in rows if abs(r["z_diff_of_means"]) > 2])
print("cells with |z_struct_binom| > 2:", [(r["n"], r["k"], round(r["z_struct_vs_binomial_sd"], 3))
                                           for r in rows if abs(r["z_struct_vs_binomial_sd"]) > 2])
json.dump(rows, open("own_zscores.json", "w"), indent=1)
