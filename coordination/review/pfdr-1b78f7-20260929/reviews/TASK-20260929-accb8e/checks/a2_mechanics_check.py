"""AFTER THE SEAL: re-run my own A2 bootstrap for the two tests that differ (small_x|TT|m5,
subgroup|TT|m5) with the replicate mechanics read from analyze_census.py slope_test():
(i) an undefined y at one rung does NOT stop the draws for the remaining rungs of that
replicate; (ii) p = (1 + #{slope* <= 0} + dropped) / 2001. Own code; my sealed cells."""
import json, math, os, random, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "rederivation")); sys.path.insert(0, os.path.join(W, "checks"))
import rl
from j3_quantities import y_of, ols, q_lo_hi
d = json.load(open(rl.opened(os.path.join(W, "rederivation/out/j3-results.json"), "A2 mechanics check: my sealed cells")))
cells = {(c["arm"], c["class"], c["m"], c["bits"]): c for c in d["A1_cells"]}
out = {}
for arm in ("small_x", "subgroup"):
    cb = {b: cells[(arm, "TT", 5, b)] for b in range(20, 33, 2)}
    rungs = [b for b in sorted(cb) if cb[b]["resolved"]]
    xs = [sum(cb[b]["log2N_by_curve"][str(j)] for j in cb[b]["curves_used"]) / len(cb[b]["curves_used"]) for b in rungs]
    rng = random.Random(0); boots = []; dropped = 0
    for _ in range(2000):
        ys = []; bad = False
        for b in rungs:
            cA, cR = cb[b]["counts_A"], cb[b]["counts_R"]
            n = len(cA); pick = [rng.randrange(n) for _ in range(n)]
            CA = sum(cA[i] for i in pick); CR = sum(sum(cR[i]) for i in pick) / 3
            s2 = sum(sum((x - sum(cR[i]) / 3) ** 2 for x in cR[i]) / 2 for i in pick)
            y = y_of(CA, CR, max(s2, CR)); ys.append(y); bad = bad or y is None
        if bad: dropped += 1; continue
        boots.append(ols(xs, ys))
    lo, hi = q_lo_hi(boots)
    p = (1 + sum(1 for s in boots if s <= 0) + dropped) / 2001
    out[f"{arm}|TT|m5"] = {"lo": lo, "hi": hi, "p": p, "dropped": dropped}
print(json.dumps(out, indent=1))
