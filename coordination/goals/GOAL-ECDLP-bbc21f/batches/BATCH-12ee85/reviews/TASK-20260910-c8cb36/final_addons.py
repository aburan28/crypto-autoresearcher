#!/usr/bin/env python3
"""J2 final add-ons:
 - manifest zero-RESEL declaration (correct string check)
 - Stage A run.log ordering vs seal.json order_used claim
 - Stage A k_25 / k_5 / mean margins / margin>=0 counts / null-mean fields
   recomputed from cells.jsonl vs Stage A summary.json
"""
import json
import re
import numpy as np
from collections import defaultdict

res = {}

# 1. manifests: zero online re-selection declaration
ok, bad = 0, []
for nbits in (20, 24):
    for s in range(1, 26):
        rid = f"RUN-ECDLP-6ac801-v3-n{nbits}-s{s:02d}"
        man = open(f"experiments/EXP-ECDLP-6ac801/runs/{rid}/manifest.yaml").read()
        cert = json.load(open(f"experiments/EXP-ECDLP-6ac801/runs/{rid}/summary.json"))["certificate"]
        has_decl = ("re-selection arm is run" in man or "RESEL" in man
                    or "re-selected arms" in man)
        cert_none = cert["kind"] == "none" and "re-selected" in cert.get("note", "")
        if has_decl and cert_none:
            ok += 1
        else:
            bad.append({"run": rid, "has_decl": has_decl, "cert": cert})
res["zero_resel_declaration"] = {"runs_ok": ok, "of": 50, "failures": bad}

# 2. Stage A run.log cell ordering vs seal claim
log = open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/"
           "TASK-20260907-7afa98/run.log").read()
order = re.findall(r"=== N=(\d+) a=(\d+)/(\d+) ===", log)
res["runlog_cell_order"] = [f"N={n} a={an}/{ad}" for n, an, ad in order]
expected_first_of_scale = {"1048576": "1/4", "16777216": "1/4"}
scales = []
for n, an, ad in order:
    if not scales or scales[-1] != n:
        scales.append(n)
res["runlog_order_matches_seal_claim"] = (
    scales == ["1048576", "16777216"]
    and all(expected_first_of_scale[n] == f"{an}/{ad}"
            for (n, an, ad) in [o for o in order if o[0] in expected_first_of_scale
                                and o is order[0] or True][:1]
            ) )
# simpler explicit check
first_per_scale = {}
for n, an, ad in order:
    if n not in first_per_scale:
        first_per_scale[n] = f"{an}/{ad}"
res["runlog_first_cell_per_scale"] = first_per_scale
res["runlog_scale_order"] = scales
res["runlog_order_matches_seal_claim"] = (
    scales == ["1048576", "16777216"]
    and first_per_scale == {"1048576": "1/4", "16777216": "1/4"})

# 3. Stage A aggregates recomputed from cells.jsonl
A = defaultdict(list)
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/"
          "TASK-20260907-7afa98/cells.jsonl") as f:
    for line in f:
        d = json.loads(line)
        A[(d["N"], d["a_num"], d["a_den"])].append(d)
S = json.load(open("coordination/goals/GOAL-ECDLP-bbc21f/batches/"
                   "BATCH-4433c1/reviews/TASK-20260907-7afa98/summary.json"))
Sby = {(s["N"], s["a_num"], s["a_den"]): s for s in S["summaries"]}
aggA, mism = {}, []
for key, rows in sorted(A.items()):
    s = Sby[key]
    ms = [r["margin"] for r in rows]
    k25 = sum(1 for m in ms if m >= 0)
    k5 = sum(1 for m in ms[:5] if m >= 0)
    mean = float(np.mean(ms))
    nulls = {}
    for fld, lbl in [("margin_null_oracle_rand_uniform", "uniform"),
                     ("margin_null_oracle_rand_sizebiased", "sizebiased"),
                     ("margin_null_randsel", "randsel"),
                     ("margin_null_shuf", "shuf")]:
        vals = [r[fld] for r in rows]
        nulls[lbl] = {"mean": float(np.mean(vals)),
                      "n_nonneg": sum(1 for v in vals if v >= 0)}
    aggA[f"N={key[0]} a={key[1]}/{key[2]}"] = {
        "k25_recomputed": k25, "k25_recorded": s["k_25"],
        "k5_recomputed": k5, "k5_recorded": s["k_5"],
        "mean_margin_recomputed": mean, "mean_margin_recorded": s["mean_margin"],
        "n_margin_geq_0_recomputed": k25,
        "max_residual_fraction_recomputed": max(r["residual_fraction"] for r in rows),
        "max_residual_fraction_recorded": s["max_residual_fraction"],
        "nulls_recomputed": nulls,
        "nulls_recorded": {
            "uniform": {"mean": s["mean_margin_null_oracle_rand_uniform"],
                        "n_nonneg": s["n_seeds_margin_null_nonneg_oracle_rand_uniform"]},
            "sizebiased": {"mean": s["mean_margin_null_oracle_rand_sizebiased"],
                           "n_nonneg": s["n_seeds_margin_null_nonneg_oracle_rand_sizebiased"]},
            "randsel": {"mean": s["mean_margin_null_randsel"],
                        "n_nonneg": s["n_seeds_margin_null_nonneg_randsel"]},
            "shuf": {"mean": s["mean_margin_null_shuf"],
                     "n_nonneg": s["n_seeds_margin_null_nonneg_shuf"]},
        },
    }
    if k25 != s["k_25"] or k5 != s["k_5"] or abs(mean - s["mean_margin"]) > 1e-15:
        mism.append(key)
    for lbl in nulls:
        if (abs(nulls[lbl]["mean"] - aggA[f"N={key[0]} a={key[1]}/{key[2]}"]["nulls_recorded"][lbl]["mean"]) > 1e-15
                or nulls[lbl]["n_nonneg"] != aggA[f"N={key[0]} a={key[1]}/{key[2]}"]["nulls_recorded"][lbl]["n_nonneg"]):
            mism.append((key, "null_" + lbl))
res["stageA_aggregates"] = aggA
res["stageA_aggregate_mismatches"] = [str(m) for m in mism]
res["stageA_cells_count"] = sum(len(v) for v in A.values())

print(json.dumps(res, indent=1))
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/"
          "TASK-20260910-c8cb36/final_addons.json", "w") as f:
    json.dump(res, f, indent=1)
