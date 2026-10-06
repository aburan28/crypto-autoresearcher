"""09b -- the same per-rung aggregate T on the PTM-5 synthetic generic engine (on mode,
primary stop), r_frozen and r_rank, with the PTM-5 share of r_frozen in X^2/N
(kappa_frozen = sum r_frozen / sum X^2/N, X = 2S). Descriptive; no slope fitted (F7's)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump
recs = [json.loads(l) for l in open(os.path.join(OUT, "ptm5_results.jsonl"))]
res = {}
for m in (3, 4, 5):
    for b in range(12, 25, 2):
        rs = [r for r in recs if r["m"] == m and r["bits"] == b and r["mode"] == "on" and r["primary"]]
        num = sum(r["primary"]["S"] ** 2 / (r["N"] * r["B"]) for r in rs)
        out = {"n": len(rs)}
        for conv, key in (("frozen", "r_frozen"), ("rank", "rank")):
            den = sum(r["primary"][key] * r["N"] / 4 / (r["N"] * r["B"]) for r in rs)
            out[conv] = num / den
        out["kappa_frozen"] = sum(r["primary"]["r_frozen"] for r in rs) / sum(4 * r["primary"]["S"] ** 2 / r["N"] for r in rs)
        res[f"m{m}|b{b}"] = out
dump("09b_ptm5_agg_by_rung.json", res)
for m in (3, 4, 5):
    print(m, " ".join("b%d:%.2f/%.1f(k=%.2f)" % (b, res[f"m{m}|b{b}"]["frozen"], res[f"m{m}|b{b}"]["rank"], res[f"m{m}|b{b}"]["kappa_frozen"]) for b in range(12, 25, 2)))
