"""10 -- minimum r_rank and r_rank1 ratios over every evaluable instance, by (class, mode), for
the narrowest statements. No randomness."""
import json, math, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump
xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
mins = defaultdict(lambda: [9e9, None, 9e9])
for x in xs:
    if not x["evaluable"]:
        continue
    k = f"{x['src'] if x['src'] == 'stage-r' else 'R10-R14'}|{x['cls']}|{x['mode']}"
    v = x["S"] / (0.5 * math.sqrt(x["rank"] * x["N"])) if x["rank"] > 0 else None
    v1 = x["S"] / (0.5 * math.sqrt((x["rank"] + 1) * x["N"]))
    if v is not None and v < mins[k][0]:
        mins[k][0], mins[k][1] = v, [x["bits"], x["curve"], x["m"], x["arm"]]
    mins[k][2] = min(mins[k][2], v1)
out = {k: {"min_rank_ratio": v[0], "at": v[1], "min_rank1_ratio": v[2]} for k, v in sorted(mins.items())}
dump("10_rank_min.json", out)
for k, v in out.items():
    print(k, round(v["min_rank_ratio"], 3), v["at"], round(v["min_rank1_ratio"], 3))
