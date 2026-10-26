#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51): blind hand re-derivation of ic-planner/1's
prime-field outputs for the six campaign curves, from the formulas as stated
(planner.rs doc table and constants, transcribed by hand -- no crypto code run):
  base N = round(#E^(1/3) / 2), capped at floor(sqrt(8 GiB / 24 B)) for p < 2^32;
  ic_over_rho = exp of the piecewise-linear interpolation of ln(ratio) in log2 r
  between (19.10, 6.6671) and (32.0, 32.955);
  support labels: size rule 'measured' if log2 r in [9.68-0.5, 32.0+0.5];
  rho outlook 'measured' within 0.25 of a point, else 'interpolated' strictly
  between the end points, else 'extrapolated'.
Also re-derives the two end points from their committed sources' numbers
(holdout: 6,980.417 / 1,047 GAE; 32-bit: ratio 32.955 at r = 2^32.0) and the
Koblitz kappa window. argv[1] = campaign dir (reads specs and one record per
c-curve for #E)."""
import json, math, sys, pathlib
root = pathlib.Path(sys.argv[1])
P = [(19.10, 6.6671), (32.0, 32.955)]
claimed = {"c24": (113, 11.46), "c28": (300, 19.33), "c30": (469, 24.55),
           "r24": (128, 12.23), "r26": (175, 14.45), "r28": (323, 20.08)}
summary_sh = {"r24": 12.233956652458087, "r26": 14.453197377819107, "r28": 20.078173411100984,
              "c24": 11.461210709103137, "c28": 19.325980413591978, "c30": 24.54954651510073}
cap = math.floor(math.sqrt(8 * 2 ** 30 / 24.0))
out = {"memory_cap_abscissae": cap, "curves": {}}
for c in ["r24", "r26", "r28", "c24", "c28", "c30"]:
    rec = json.loads(open(root / "sessions" / c / "records.jsonl").readline())
    E = rec["workload"]["curve"]["group_order"]; r = rec["workload"]["curve"]["r"]
    x = math.log2(r)
    ideal = round(E ** (1 / 3) / 2)
    N = min(ideal, cap)
    (x0, y0), (x1, y1) = P
    y = math.exp(math.log(y0) + (math.log(y1) - math.log(y0)) * (x - x0) / (x1 - x0))
    size_support = "measured" if 9.68 - 0.5 <= x <= 32.0 + 0.5 else "extrapolated"
    rho_support = "measured" if min(abs(x - x0), abs(x - x1)) < 0.25 else ("interpolated" if x0 < x < x1 else "extrapolated")
    spec = json.load(open(root / "specs" / f"{c}.json"))
    specN = int(next(a for a in spec["arms"] if a["name"] == "plan")["method"]["params"]["factor_base"].split("=")[1])
    out["curves"][c] = {"group_order": E, "r": r, "log2_r": x, "cbrt_E_over_2": E ** (1 / 3) / 2, "N": N,
                        "N_claimed": claimed[c][0], "N_in_spec": specN, "N_matches": N == claimed[c][0] == specN,
                        "ic_over_rho": y, "claimed_2dp": claimed[c][1], "summary_sh_value": summary_sh[c],
                        "rel_diff_vs_summary_sh": abs(y - summary_sh[c]) / summary_sh[c],
                        "rounds_to_claim": round(y, 2) == claimed[c][1],
                        "size_support": size_support, "rho_support": rho_support}
# end points from their sources' numbers
hold_ic, hold_rho, hold_r = 6980.417, 1047.0, 562427
out["endpoint_19_1"] = {"log2_r": math.log2(hold_r), "ratio_from_means": hold_ic / hold_rho,
                        "rho_S": hold_rho / math.sqrt(hold_r), "rho_S_over_theory": hold_rho / math.sqrt(hold_r) / math.sqrt(math.pi / 4),
                        "planner_rule_N_at_this_r": round(hold_r ** (1 / 3) / 2), "N_measured": 48}
out["endpoint_32"] = {"ratio": 32.95506794079421, "rho_S": 0.9664936675732191, "rho_S_over_theory": 0.9664936675732191 / math.sqrt(math.pi / 4),
                      "planner_rule_N_at_2^32": round((2 ** 32) ** (1 / 3) / 2), "N_measured": 1024, "N_grid": [1024, 2048, 4096, 8192, 16384]}
# interval band from the end points' own 95% intervals (crude, same-side pairing)
lo = [(19.10, 5.3684), (32.0, 27.67172868306268)]; hi = [(19.10, 8.3883), (32.0, 40.55964883000198)]
def interp(pts, x):
    (a0, b0), (a1, b1) = pts
    return math.exp(math.log(b0) + (math.log(b1) - math.log(b0)) * (x - a0) / (a1 - a0))
for c, d in out["curves"].items():
    d["prediction_band_from_endpoint_CIs"] = [interp(lo, d["log2_r"]), interp(hi, d["log2_r"])]
# Koblitz kappa window: values of kappa reproducing each chosen count with round(kappa*(r/n^3)^(1/3)), floor 1
panel = [(13, 2003, 1), (17, 65587, 1), (19, 130873, 2), (23, 2095853, 3), (29, 42457, 1), (31, 1439393, 2), (37, 230603167, 8), (41, 549756390943, 90)]
win = {}
for n, r, ch in panel:
    q = (r / n ** 3) ** (1 / 3)
    lo_k = 0.0 if ch == 1 else (ch - 0.5) / q
    hi_k = (ch + 0.5) / q
    win[f"n{n}"] = {"q": q, "kappa_window": [lo_k, hi_k], "kappa_0.6_gives": max(1, round(0.6 * q)), "chosen": ch,
                    "model_constant_2^(-1/3)_gives": max(1, round(2 ** (-1 / 3) * q))}
six = ["n13", "n17", "n19", "n23", "n29", "n31"]
out["koblitz_kappa"] = {"per_curve": win,
                        "window_reproducing_six_small": [max(win[k]["kappa_window"][0] for k in six), min(win[k]["kappa_window"][1] for k in six)],
                        "window_n37": win["n37"]["kappa_window"], "window_n41": win["n41"]["kappa_window"],
                        "model_optimum_constant": 2 ** (-1 / 3)}
json.dump(out, sys.stdout, indent=1)
