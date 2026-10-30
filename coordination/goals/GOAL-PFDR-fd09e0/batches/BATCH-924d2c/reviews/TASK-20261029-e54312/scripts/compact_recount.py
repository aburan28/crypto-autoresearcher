"""Write outputs/recount-sample.json (< 64 KiB) from the selection file, the full CPython 3.13 recount and the
CPython 3.11 set-regeneration digests (full outputs kept in scratch, not staged; their sha256 is recorded).

usage: python3 -I -B compact_recount.py <recount-selection.json> <recount-py313.json> <recount-sets-py311.json> <out.json>
"""
import hashlib
import json
import sys

sel_p, full_p, sets_p, out_p = sys.argv[1:5]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


sel = json.load(open(sel_p))
full = json.load(open(full_p))
s311 = json.load(open(sets_p))
d311 = {(j["cell"], j["c"]): j["digests"] for j in s311["jobs"]}
jobs = []
for j in full["jobs"]:
    key = (j["cell"], j["c"])
    dg = j["digests"]
    same = d311[key] == dg
    comb = hashlib.sha256(json.dumps(dg, sort_keys=True).encode()).hexdigest()
    F = j["fields"]
    jobs.append({
        "cell": j["cell"], "c": j["c"], "selection_hash": j["selection_hash"],
        "fields_equal": {k: v["equal"] for k, v in F.items()},
        "values": {k: F[k]["recount"] for k in ("p", "N", "gap_C", "gap_D", "plant_m", "plant_internal", "plant_C",
                                                "plant_D", "plant_feasible")},
        "gap_meta": F["gap_meta"]["recount"],
        "null_C_null_D": "20 + 20 values equal to the record" if F["null_C"].get("equal") and F["null_D"].get("equal") else F["null_C"],
        "checks_true": sum(v is True for v in j["checks"].values()),
        "checks_failed": sorted(k for k, v in j["checks"].items() if v is False),
        "checks_other": {k: v for k, v in j["checks"].items() if not isinstance(v, bool)},
        "sets_sha256_combined": comb,
        "sets_identical_under_py311_regeneration": same,
        "seconds": j["seconds"],
    })
out = {
    "joint": "J2b (1)",
    "rule": sel["rule"],
    "selection_file": {"path": "outputs/recount-selection.json", "sha256": sha(sel_p),
                       "written": "2026-10-29T05:09:43Z, before any count field was read"},
    "selection_hash_order": [{"cell": s["cell"], "c": s["c"], "hash": s["selection_hash"],
                              "next_in_order": [x["c"] for x in s["next_in_order"]], "ok_records": s["ok_records_in_cell"]}
                             for s in sel["jobs"]],
    "method": {
        "regeneration": "scripts/ownec.py: curve from seed 8,100,000 + c with own primality, Jacobi symbol, Cipolla roots, "
                        "affine/Jacobian group law and BSGS order search; base points, log-GAP half-box enumeration, null and "
                        "planted builders written from the frozen definitions, RNG consumption order read from run.py and "
                        "vendor/curve.py only",
        "counting": "A: numpy pair-sum array + sort + run lengths (all sets); B: numpy bincount histogram over [0, p) (all 22 "
                    "sets of every job with p < 2^25); P: pure-Python dict prefix counter for the plant m search "
                    "(linear scan for the least m in [4, n/2]; the driver bisects). labelsum.c is never called.",
        "interpreters": {"count": full["python"], "count_executable": full["executable"],
                         "sets_only": s311["python"], "sets_only_executable": s311["executable"]},
        "plant_threshold": "0.30 x (sum(null_C)/20) as a float, as the frozen rule; also decided in exact rationals "
                           "(200 internal >= 3 sum null_C) -- checks.plant_threshold_float_vs_exact_agree",
    },
    "check_names": sorted({k for j in full["jobs"] for k in j["checks"]}),
    "jobs": jobs,
    "summary": dict(full["summary"], sets_identical_py311_vs_py313=sum(j["sets_identical_under_py311_regeneration"] for j in jobs),
                    n_ge_1024_jobs=sum(1 for j in jobs if int(j["cell"].split("-n")[1]) >= 1024),
                    planted_arm_regenerated_jobs=len(jobs), wall_seconds_py313=full["wall_seconds"]),
    "full_outputs_not_staged": {"recount-py313.json": sha(full_p), "recount-sets-py311.json": sha(sets_p)},
}
with open(out_p, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(json.dumps(out["summary"]))
