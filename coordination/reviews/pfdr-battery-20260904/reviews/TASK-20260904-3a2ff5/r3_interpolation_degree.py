"""R3: per-draw check that Theorem A's degree condition d_ff >= e(Z) + 2 is met, using
e(Z) <= max(0, |Z| - 1) (Lemma 2) and the record-derived bound r_D = N_D - dim_I_at_D.
TASK-20260904-3a2ff5.  Reads runs/*/raw-result.json only."""
import json, os, collections
from math import comb
ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-cbdefb/runs")
OUT = os.path.join(ROOT, "coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5")

def systems(raw):
    yield from (("semaev", d["semaev"]) for d in raw["raw"]["draws"])
    yield from (("noncurve", d["result"]) for d in raw["raw"]["noncurve"])
    yield from (("null1", o["result"]) for d in raw["raw"]["draws"] for o in d.get("null1", []))
    yield from (("null2", o["result"]) for o in raw["raw"].get("null2_objects", []))
    yield from (("null3", o["result"]) for o in raw["raw"].get("null3_objects", []))

rows = collections.Counter()
for s in (1, 2, 3, 4, 5):
    for p in (4099, 16411, 65537):
        raw = json.load(open(os.path.join(RUNS, f"RUN-PFDR-cbdefb-m2-s{s}-p{p}", "raw-result.json")))
        n = 2 * s
        for arm, r in systems(raw):
            if r.get("degenerate"):
                continue
            Z = r["certificate"].get("Z_size")
            falls = [h for h in r["history"] if h["fall"]]
            if not falls:
                continue
            dff = falls[0]["D"]
            e_lemma2 = 1 if (Z is not None and Z <= 3) else (max(0, Z - 1) if Z is not None else None)
            e_record = None                       # least D in the history with r_D = |Z|
            for h in r["history"]:
                N = sum(comb(n, j) for j in range(0, min(h["D"], n) + 1))
                if h.get("dim_I_at_D") is not None and N - h["dim_I_at_D"] == Z:
                    e_record = h["D"]
                    break
            e_best = min(x for x in (e_lemma2, e_record) if x is not None)
            rows[(s, arm, Z, dff, e_lemma2, e_record, e_best, e_best <= dff - 2)] += 1
out = [{"s": k[0], "arm": k[1], "Z_size": k[2], "d_ff": k[3], "e_bound_lemma2": k[4],
        "e_bound_from_record": k[5], "e_bound_used": k[6],
        "TheoremA_degree_condition_d_ff >= e+2": k[7], "count": v}
       for k, v in sorted(rows.items(), key=str)]
summary = collections.Counter((r["arm"], r["TheoremA_degree_condition_d_ff >= e+2"]) for r in out
                              for _ in range(r["count"]))
json.dump({"rows": out, "summary_by_arm": {f"{a}:{b}": c for (a, b), c in summary.items()}},
          open(os.path.join(OUT, "r3_interpolation_degree.json"), "w"), indent=1)
print({f"{a}:{b}": c for (a, b), c in summary.items()})
