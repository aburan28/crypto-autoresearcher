#!/usr/bin/env python3
"""w6_parse_crosschecks.py -- joint W6: parse (not read) the cross-check logs of RUN-SEMBIN-5ed13e and compare them field by
field with the lane records. Writes outputs/w6_crosschecks.json and prints a summary. Read-only on the package.
Run: python3 w6_parse_crosschecks.py        (needs boolsys from the code dir for the system hash recomputation)"""
import os, re, json, hashlib, sys
REPO = "/home/user/crypto-autoresearcher"
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
WS = os.environ.get("WS", f"{REPO}/coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261004-7d2fb6")

def load_records(lane):
    return [json.loads(l) for l in open(f"{RUN}/{lane}/cells/results.jsonl") if l.strip()]

def parse_log(path):
    txt = open(path).read()
    out = {"path": os.path.relpath(path, REPO), "sha256_of_log": hashlib.sha256(txt.encode()).hexdigest()}
    m = re.search(r"instance N=(\d+) sha=([0-9a-f]+) solutions listed=(\d+); witness violates (\d+) generators", txt)
    out["N"], out["sha_prefix"], out["zeros_listed"], out["witness_violations"] = int(m[1]), m[2], int(m[3]), int(m[4])
    m = re.search(r"elimination (\S+) cap (\S+) m4ri (\S+)", txt)
    out["routine_header"], out["cap_gib"], out["m4ri_path"] = m[1], float(m[2]), m[3]
    ech = re.findall(r"\[ech (\d+) (\w+)\] (\d+) x (\d+) rank (\d+) \| rows not vanishing at the zero: in=(\d+) out=(\d+)(.*)", txt)
    out["eliminations"] = [{"call": int(a), "routine": b, "rows": int(c), "cols": int(d), "rank": int(e), "in": int(f), "out": int(g), "flag": h.strip()} for a, b, c, d, e, f, g, h in ech]
    out["all_in_out_zero"] = all(e["in"] == 0 and e["out"] == 0 for e in out["eliminations"])
    out["routines_in_ech_lines"] = sorted({e["routine"] for e in out["eliminations"]})
    batches = re.findall(r"\[closure D=(\d+) it=(\d+)\] batch rows=(\d+) \(basis (\d+) \+ (\d+) products\) -> rank (\d+) \(\+(\d+)\)", txt)
    out["batches"] = [{"D": int(a), "it": int(b), "rows": int(c), "basis": int(d), "products": int(e), "rank": int(f), "new": int(g)} for a, b, c, d, e, f, g in batches]
    m = re.search(r"DONE (\d+)s status=(\S+) rank=(\d+)/(\d+) contains_one=(\S+) std=(\S+) verdict=(\S+) lm_sha=(\S+) faults=(\d+) iters=(\[.*\])", txt)
    if m:
        out["done"] = {"wall_s": int(m[1]), "status": m[2], "rank": int(m[3]), "ncols": int(m[4]), "contains_one": m[5], "std": None if m[6] == "None" else int(m[6]),
                       "verdict": None if m[7] == "None" else m[7], "lm_sha": None if m[8] == "None" else m[8], "faults": int(m[9]),
                       "iters": eval(m[10])}
    return out

def per_D4(rec):
    for p in rec["per_D"]:
        if p.get("D") == 4:
            return p

res = {}
for tag, lane, inst, logs in (
    ("n44_d5", "closure_m2_n44", "ch_n44_m2_t2_k22_low_B_ran_s20260913101_d5", ["crosscheck_n44_d5/xcheck_default_cap7.log", "crosscheck_n44_d5/xcheck_default_cap10.5.log"]),
    ("n45_d0", "closure_m2_n45", "ch_n45_m2_t2_k23_low_B_ran_s20260913101_d0", ["crosscheck_n45_d0/xcheck_default_cap11.5.log"])):
    recs = [r for r in load_records(lane) if r["instance_id"] == inst]
    cl = next(r for r in recs if r["instrument"] == "closure_certificate")
    sc = next(r for r in recs if r["instrument"] == "exhaustive_solution_count")
    p4 = per_D4(cl)
    lane_env = json.load(open(f"{RUN}/{lane}/environment.json"))
    injson = json.load(open(f"{RUN}/{lane}/cells/instances/{inst}.json"))
    r = {"instance": inst, "record_system_sha256": cl["system_sha256"], "instance_json_system_sha256": injson["system_sha256"],
         "exact_count": sc["solutions"], "lane_m4ri_library": p4["m4ri_library"], "lane_elimination": p4["elimination"],
         "record_D4": {"status": p4["status"], "rank": p4["rank"], "ncols": p4["ncols"], "std": p4["standard_monomials"], "verdict": p4["verdict"],
                       "lm_sha": p4["basis_lm_sha256"], "faults": p4["elimination_faults"], "resumes": p4["checkpoint_resumes"], "dropped": p4["dropped_terms_above_D"],
                       "iters": [(x["rows"], x["rank_after"], x["new_pivots"]) for x in p4["iterations"]]},
         "xchecks": []}
    # recompute the system hash from the instance json's canonical payload
    sys.path.insert(0, f"{REPO}/experiments/EXP-SEMBIN-7e1371/code"); sys.path.insert(0, f"{REPO}/harness/macaulay_fp/fixtures")
    import boolsys
    r["recomputed_system_sha256"] = hashlib.sha256(json.dumps(injson["system"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    r["canonical_bytes_roundtrip_equal"] = (boolsys.canonical_bytes(injson["system"]) == json.dumps(injson["system"], sort_keys=True, separators=(",", ":")).encode())
    for lg in logs:
        x = parse_log(f"{RUN}/{lg}")
        x["system_hash_prefix_matches_record"] = cl["system_sha256"].startswith(x["sha_prefix"])
        x["m4ri_path_equals_lane_m4ri"] = (x["m4ri_path"] == p4["m4ri_library"])
        d = x.get("done")
        if d and d["status"] == "completed":
            x["rank_equal"] = d["rank"] == p4["rank"]; x["std_equal"] = d["std"] == p4["standard_monomials"]
            x["verdict_equal"] = d["verdict"] == p4["verdict"]; x["lm_sha_equal"] = d["lm_sha"] == p4["basis_lm_sha256"]
            x["iteration_profile_equal"] = d["iters"] == r["record_D4"]["iters"]
            # batching: per-iteration product counts from the batch lines vs the iteration's (rows - rank at start)
            prod = {}
            for b in x["batches"]:
                prod.setdefault(b["it"], []).append(b["products"])
            x["products_per_iteration_from_batch_lines"] = {k: sum(v) for k, v in prod.items()}
            x["n_batches_per_iteration"] = {k: len(v) for k, v in prod.items()}
        r["xchecks"].append(x)
    # the lane's own batching, from its stderr.log, is interleaved over several processes; report only that it exists
    res[tag] = r
json.dump(res, open(f"{WS}/outputs/w6_crosschecks.json", "w"), indent=1, default=str)
for tag, r in res.items():
    print("==", tag, r["instance"])
    print("  system sha256: record", r["record_system_sha256"][:16], "instance_json", r["instance_json_system_sha256"][:16], "recomputed", r["recomputed_system_sha256"][:16],
          "| equal:", r["record_system_sha256"] == r["instance_json_system_sha256"] == r["recomputed_system_sha256"])
    print("  exact |V| =", r["exact_count"], "| record D=4:", {k: v for k, v in r["record_D4"].items() if k != "iters"})
    print("  record iters:", r["record_D4"]["iters"])
    for x in r["xchecks"]:
        d = x.get("done", {})
        print(f"  xcheck {x['path']}: routine={x['routine_header']}/{x['routines_in_ech_lines']} cap={x['cap_gib']} zeros_listed={x['zeros_listed']} witness_violations={x['witness_violations']} "
              f"n_elim={len(x['eliminations'])} all_in_out_zero={x['all_in_out_zero']} sha_prefix_ok={x['system_hash_prefix_matches_record']} m4ri_ok={x['m4ri_path_equals_lane_m4ri']}")
        print(f"      done: status={d.get('status')} rank={d.get('rank')} std={d.get('std')} verdict={d.get('verdict')} lm_sha={str(d.get('lm_sha'))[:16]} faults={d.get('faults')}")
        for k in ("rank_equal", "std_equal", "verdict_equal", "lm_sha_equal", "iteration_profile_equal"):
            if k in x: print(f"      {k}: {x[k]}")
        if "products_per_iteration_from_batch_lines" in x:
            print("      products/iteration (batch lines):", x["products_per_iteration_from_batch_lines"], "batches/iteration:", x["n_batches_per_iteration"])
        print("      eliminations:", [(e["rows"], e["rank"]) for e in x["eliminations"]])
