#!/usr/bin/env python3
"""TASK-20260923-b8f163 J3, I-4 alternative B residual: count pivots that are
CONSTANT over the 993 non-degenerate F-S3 targets yet have S_k >= 193 (they
could become r-dependent, with h <= 7/207, if 7 replacement targets were added).
Validator's own forms; zero trials."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import j3_recompute as R
recs, refs = R.load()
B = json.load(open(os.path.join(R.RUN, "curve.json")))["B"]
ol = {}
for line in gzip.open(os.path.join(R.RUN, "F-S3-reference-oplogs-D4.jsonl.gz"), "rt"):
    r = json.loads(line); ol.setdefault(r["ref"], []).append(r)
ol = {k: [(r["p"], r["c"], r["X"]) for r in sorted(v, key=lambda r: r["k"])] for k, v in ol.items()}
labs = ["U1", "U2", "U3", "S1", "S2"]
forms, _ = R.forms_for_refs(B, ol, labs)
tg = [r for r in recs["F-S3"] if r["D"] == 4 and not r["degenerate"]]
out = {}
for lab in labs:
    a0, a = forms[lab]; K = len(a)
    ev = [R.eval_e(a0, a, r["x_R"]) for r in tg]
    S, Z, _ = R.hazards(ev, K)
    const = [k for k in range(K) if len({e[k] for e in ev}) == 1 and S[k] >= 193]
    out[lab] = {"constant_pivots_with_S_k_ge_193": len(const), "their_a_k_nonzero": sum(1 for k in const if a[k]),
                "their_constant_value": sorted({ev[0][k] for k in const})}
tot = sum(v["constant_pivots_with_S_k_ge_193"] for v in out.values())
out["total"] = tot
out["reading"] = ("P2 has 26 pairs (11 at h = 0, 15 in band). Each added pair would sit at h <= 0.034. "
                  "The median falls below 0.2 only if at least 4 pairs are added (11 + m >= (26 + m)/2 + 1). "
                  "The in-band fraction can only fall. So DR-4 could move only to 'H1 FALSIFIED', and only "
                  "if 4 or more such pivots became dependent.")
json.dump(out, open(os.path.join(HERE, "j3_I4B_residual.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
