"""Cross-check of this study against research/nist_seed_lvalue_20261030 (independent code,
same question). Reads committed outputs only; recomputes nothing.

For each curve in both studies (matched by p and Delta): compare this study's log P_DK
(Euler product over all primes <= 10^6, conductor stripped prime by prime) with lvalue's
log L-hat at x = 10^6 (chi of coredisc(Delta)); compare null percentiles (different null
implementations: 10^6 Monte Carlo draws to l <= 1000 plus a Gaussian tail here, 200,000
draws to l <= 10^5 there); and report lvalue's x = 10^8 value and the 10^6 -> 10^8 change."""
import json, math, sys
mine = json.load(open("runs/results.json"))["rows"]
lv = json.load(open("../nist_seed_lvalue_20261030/runs/lvalues.json"))["rows"]
key = lambda p, D: (int(p), int(D))
M = {key(x["p"], x["D"]): x for x in mine}
rows = []
for y in lv:
    x = M.get(key(y["p"], y["D"]))
    if x is None: continue
    a, b = x["logP_DK"], y["logL"]["1000000"]
    rows.append(dict(name=y["name"], label=y["label"], bits=y["bits"], f_pi=y["f_pi"],
                     logP_DK_1e6_here=a, logL_1e6_lvalue=b, diff_1e6=a - b,
                     logL_1e8_lvalue=y["logL"]["100000000"], change_1e6_to_1e8=y["logL"]["100000000"] - b,
                     pct_delta_here=x["pct_delta"], pct_logL_lvalue=y["pct_logL"]))
n = len(rows)
mx = max(abs(r["diff_1e6"]) for r in rows)
pd = [r["pct_delta_here"] - r["pct_logL_lvalue"] for r in rows]
t = next(r for r in rows if r["name"] == "prime239v1")
rk_here = sorted(rows, key=lambda r: r["logP_DK_1e6_here"]).index(t) + 1
rk_lv = sorted(rows, key=lambda r: r["logL_1e8_lvalue"]).index(t) + 1
xs = [r["pct_delta_here"] for r in rows]; ys = [r["pct_logL_lvalue"] for r in rows]
mxs, mys = sum(xs) / n, sum(ys) / n
corr = sum((a - mxs) * (b - mys) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mxs) ** 2 for a in xs) * sum((b - mys) ** 2 for b in ys))
out = dict(shared_curves=n, only_here=len(mine) - n, only_lvalue=len(lv) - n,
           max_abs_diff_logL_1e6=mx, max_abs_change_1e6_to_1e8=max(abs(r["change_1e6_to_1e8"]) for r in rows),
           pct_diff_mean=sum(pd) / n, pct_diff_max_abs=max(abs(v) for v in pd), pct_corr=corr,
           prime239v1=dict(logP_DK_1e6_here=t["logP_DK_1e6_here"], logL_1e6_lvalue=t["logL_1e6_lvalue"],
                           logL_1e8_lvalue=t["logL_1e8_lvalue"], pct_here=t["pct_delta_here"], pct_lvalue=t["pct_logL_lvalue"],
                           rank_here_of_shared=rk_here, rank_lvalue_of_shared=rk_lv),
           rows=rows)
json.dump(out, open("runs/crosscheck.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
