"""07b -- MC-4 pooled: the census's generic on-mode evaluable instances at 12..24 bits against
the PTM-5 per-(m, rung) on-mode r_frozen firing rate; expected count, P(>= observed) by exact
Poisson-binomial, family-wise P(>= 1). No randomness."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump
from numlib import poisson_binomial_tail
o = json.load(open(os.path.join(OUT, "07_ptm5_analysis.json")))
rate = {}
for k, v in o["cells"].items():
    m, b, mode = k.split("|")
    rate[(int(m[1:]), int(b[1:]), mode)] = v["primary_frozen"]["rate"]
xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r" and x["bits"] <= 24 and x["mode"] == "on"
      and x["cls"] in ("random", "structured", "j0_random")]
ps = [rate[(x["m"], x["bits"], "on")] for x in ev]
obs = sum(1 for x in ev if x["ratio"] < 0.9)
out = {"family": "census generic on-mode evaluable instances, 12..24 bits (random, structured, j0_random)",
       "n": len(ev), "observed": obs, "expected_ptm5": sum(ps), "P_ge_observed": poisson_binomial_tail(ps, obs),
       "familywise_P_ge_1": 1 - math.prod(1 - p for p in ps)}
dump("07b_ptm5_pooled.json", out)
print(out)
