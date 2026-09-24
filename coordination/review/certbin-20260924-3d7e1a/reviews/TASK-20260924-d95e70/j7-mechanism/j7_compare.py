#!/usr/bin/env python3
"""J7 (b) comparison -- run only AFTER predictions.json (ORDER.log step 3).
Compares PR-1/PR-2/PR-3/PR-4 with the archived closures.jsonl.gz per instance,
cross-checks my set selection against instance-sets.json, and checks the
J7 (a) degree consistency against certificate-verification.json."""
import collections
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"

pred = json.load(open(os.path.join(HERE, "predictions.json")))
recs = [json.loads(l) for l in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt")]
W4 = {(r["set"], r["idx"]): r for r in recs if r["closure"] == "W_4"}
M4 = {(r["set"], r["idx"]): r for r in recs if r["closure"] == "M_4"}
iset = json.load(open(os.path.join(RUN, "instance-sets.json")))

rows, disagree = [], []
for p in pred["instances"]:
    s = "S62" if p["set"] == "S10" else p["set"]
    w = W4[(s, p["idx"])]
    eng_one_W1 = bool(w["one"]) and w["one_first_iteration"] is not None and w["one_first_iteration"] <= 1
    dimW1 = w["dims"][1] if len(w["dims"]) > 1 else w["dims"][0]
    row = {"set": p["set"], "idx": p["idx"], "x_R": p["x_R"],
           "pred_one_in_W1": p["PR1_predict_one_in_W1"], "engine_one_in_W1": eng_one_W1,
           "engine_one_first_iteration": w["one_first_iteration"], "engine_dims": w["dims"],
           "engine_final_dim": w["final_dim"], "engine_dims_by_deg": w["dims_by_deg"],
           "engine_new_fallen_per_iteration": w.get("new_fallen_per_iteration"),
           "engine_M4_rank": M4[(s, p["idx"])]["rank"],
           "rank_R4p": p["rank_R4p"], "PR2_lower_bound_dim_W1": p["PR2_lower_bound_dim_W1"],
           "engine_dim_W1": dimW1,
           "PR1_agrees": p["PR1_predict_one_in_W1"] == eng_one_W1,
           "PR2_bound_respected": dimW1 >= p["PR2_lower_bound_dim_W1"],
           "fill_exceeds_ell_route_by": dimW1 - p["PR2_lower_bound_dim_W1"]}
    if not row["PR1_agrees"]:
        row["disagreement_type"] = "A" if p["PR1_predict_one_in_W1"] else "B"
        disagree.append(row)
    rows.append(row)

# set membership cross-check (my selection vs the run's instance-sets.json)
def run_idxs(name):
    return sorted(x["idx"] for x in iset["sets"][name])

mine = collections.defaultdict(list)
for p in pred["instances"]:
    mine[p["set"]].append(p["idx"])
membership = {"U62": sorted(mine["U62"]) == run_idxs("U62"),
              "C20": sorted(mine["C20"]) == run_idxs("C20"),
              "S10_is_first10_of_S62": sorted(mine["S10"]) == run_idxs("S62")[:10]}

# J7 (a): certificate degrees
cv = json.load(open(os.path.join(RUN, "certificate-verification.json")))
cl = cv.get("certificates", cv.get("results", cv))
degs = collections.Counter()
if isinstance(cl, list):
    for c in cl:
        degs[(c["key"].split(":")[0], c.get("closure"), c.get("max_deg_mu"), c.get("verified"))] += 1

summary = {
    "n": len(rows),
    "PR1_agreement": {f"{k[0]}|agrees={k[1]}": v for k, v in collections.Counter((r["set"], r["PR1_agrees"]) for r in rows).items()},
    "disagreements": disagree,
    "PR2_bound_respected_all": all(r["PR2_bound_respected"] for r in rows),
    "U62_engine_first_iteration": collections.Counter(r["engine_one_first_iteration"] for r in rows if r["set"] == "U62"),
    "U62_engine_dim_W1": collections.Counter(r["engine_dim_W1"] for r in rows if r["set"] == "U62"),
    "U62_ell_route_dim": collections.Counter(r["PR2_lower_bound_dim_W1"] for r in rows if r["set"] == "U62"),
    "U62_engine_new_fallen_it0": collections.Counter(r["engine_new_fallen_per_iteration"][0] for r in rows if r["set"] == "U62"),
    "set_membership_matches_run": membership,
    "certificate_degree_table": {f"{k[0]}|{k[1]}|maxdeg={k[2]}|verified={k[3]}": v for k, v in sorted(degs.items(), key=str)},
}
summary = json.loads(json.dumps(summary, default=lambda o: {str(k): v for k, v in o.items()}))
json.dump({"summary": summary, "rows": rows}, open(os.path.join(HERE, "comparison.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
