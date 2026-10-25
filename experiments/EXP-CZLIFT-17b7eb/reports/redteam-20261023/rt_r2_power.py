"""R2 power: what the pooled |z| <= 4 statistic can and cannot exclude, from the actual sample composition."""
import json, math
from statistics import NormalDist
RUNS = {"RUN-CZLIFT-041d05": "../../runs/RUN-CZLIFT-041d05/raw-result.json",
        "RUN-CZLIFT-6709c9": "../../runs/RUN-CZLIFT-6709c9/raw-result.json"}
Phi = NormalDist().cdf
out = {}
allrows = []
for rid, path in RUNS.items():
    raw = json.load(open(path))
    rows = [dict(r, p=c["p"], D=c["D"]) for c in raw["raw"]["curves"] for r in c["rows"] if r["vP"] >= 2]
    allrows += rows
    ps = [r["p"] for r in rows]
    n = len(ps)
    null = [1 / (p + 1) for p in ps]
    mu0 = sum(null)
    sd0 = math.sqrt(sum(x * (1 - x) for x in null))

    def power(alt):  # P(z > 4) under alternative rates alt (normal approx)
        mu1 = sum(alt)
        sd1 = math.sqrt(sum(a * (1 - a) for a in alt))
        return (mu1 - mu0) / sd0, 1 - Phi((4 * sd0 + mu0 - mu1) / sd1)

    # minimal uniform multiplicative leak lambda/(p+1) detected with 50% / 80% power at z > 4
    def lam_for(target):
        lo, hi = 1.0, 20.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if power([min(1, mid / (p + 1)) for p in ps])[1] < target:
                lo = mid
            else:
                hi = mid
        return round(hi, 3)

    share_small = sum(1 / (p + 1) for p in ps if p <= 19) / mu0
    res = {"n": n, "null_mean": mu0 / n, "null_sd_of_count": sd0, "abs_excess_rate_at_4sd": 4 * sd0 / n,
           "fraction_of_null_mass_from_p<=19": round(share_small, 3),
           "fraction_of_rows_with_p<=19": round(sum(p <= 19 for p in ps) / n, 3),
           "lambda_uniform_50pct": lam_for(0.5), "lambda_uniform_80pct": lam_for(0.8)}
    alts = {
        "rho_parity_1/sqrt(p)_all_p": [1 / math.sqrt(p) for p in ps],
        "rho_parity_1/sqrt(p)_only_p>500": [1 / math.sqrt(p) if p > 500 else 1 / (p + 1) for p in ps],
        "rho_parity_1/sqrt(p)_only_p>500_one_section": [1 / math.sqrt(p) if (p > 500 and r["section"] == "teichmuller") else 1 / (p + 1) for p, r in zip(ps, rows)],
        "10/p_only_p>500": [10 / p if p > 500 else 1 / (p + 1) for p in ps],
        "2/p_all_p": [2 / p for p in ps],
        "leak_only_at_p=1373_rate_0.05": [0.05 if p == 1373 else 1 / (p + 1) for p in ps],
    }
    res["pooled_test_against_alternatives"] = {k: {"expected_z": round(power(v)[0], 2), "power_z>4": round(power(v)[1], 4)} for k, v in alts.items()}
    out[rid] = res

# per-curve, both seeds pooled, all sections: observed successes, null expectation, one-sided 95% Poisson upper bound on the rate
def pois_upper(k, conf=0.95):
    lo, hi = 0.0, 50.0 + 5 * k
    for _ in range(100):
        mid = (lo + hi) / 2
        # P(X <= k | mid)
        s, term = 0.0, math.exp(-mid)
        for i in range(k + 1):
            s += term
            term *= mid / (i + 1)
        if s > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi
percurve = []
for p in sorted({r["p"] for r in allrows}):
    rr = [r for r in allrows if r["p"] == p]
    k = sum(r["success"] for r in rr)
    ub = pois_upper(k) / len(rr)
    percurve.append({"p": p, "D": rr[0]["D"], "rows_both_seeds": len(rr), "successes": k,
                     "expected_null_1/(p+1)": round(len(rr) / (p + 1), 2),
                     "rate_upper95": round(ub, 4), "upper95_times_p": round(ub * p, 2),
                     "1/sqrt(p)": round(1 / math.sqrt(p), 4), "excludes_1/sqrt(p)": ub < 1 / math.sqrt(p)})
out["per_curve_both_seeds"] = percurve
big = [r for r in allrows if r["p"] > 500]
kbig = sum(r["success"] for r in big)
out["p>500_pooled"] = {"rows": len(big), "successes": kbig, "expected_null": round(sum(1 / (r['p'] + 1) for r in big), 2),
                       "expected_if_1/sqrt(p)": round(sum(1 / math.sqrt(r['p']) for r in big), 1)}
print(json.dumps(out, indent=1))
json.dump(out, open("rt_r2_power_output.json", "w"), indent=1)
