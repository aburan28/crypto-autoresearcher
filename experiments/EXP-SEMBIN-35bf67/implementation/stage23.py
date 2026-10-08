#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 Stage 2 / Stage 3 cell runner.

  stage23.py cell RUN-ID STAGE n m t k SAT UNSAT NULL HOURS NULL_T
      STAGE in {stage2, stage3}; targets per stratum; NULL null instances (0 = none);
      HOURS = session-level wall allocation for this cell (executor scheduling, OP-CAPS);
      NULL_T = prefix split (2^T processes) for the null arm's exhaustive s.
  stage23.py summarize RUN-ID       (re-write raw-result.json / manifest from records)

Order (OP-ORDER): primary arm first (alternating SAT/UNSAT), then the null arm.
Allocation: up to 85% of HOURS for the primary arm when NULL > 0, remainder for null.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pipeline  # noqa: E402
import runlib  # noqa: E402
import stats  # noqa: E402

BIN = os.environ["SEMBIN_BIN"]
WORK = os.environ["SEMBIN_WORK"]
EXP = runlib.EXP


def summarize(rd, run_id, params=None, started=None, t0=None, cmd=None):
    pfile = os.path.join(rd, "params.json")
    if params is None:
        params = json.load(open(pfile))
    done = pipeline.load_done(rd)
    recs = sorted(done.values(), key=lambda r: (r["arm"], r["index"]))
    out = {"run_id": run_id, "cell": params["cell"], "stage": params["stage"], "params": params}
    arms = {}
    for arm in ("primary", "null"):
        rs = [r for r in recs if r["arm"] == arm]
        if not rs:
            continue
        blk = {}
        for st in ("SAT", "UNSAT"):
            v = [r for r in rs if r.get("stratum") == st and r["status"] == "VALID"]
            blk[st] = stats.rate_block([0 if r["solv4"] else 1 for r in v])
            blk[st]["indices"] = [r["index"] for r in v]
            blk[st]["s_values"] = sorted(r["s"] for r in v)
            blk[st]["closure_round_counts"] = sorted(r["closure_round_count"] for r in v)
            blk[st]["not_solv4_indices"] = [r["index"] for r in v if not r["solv4"]]
            blk[st]["eval_rank_lt_s_indices"] = [r["index"] for r in v if r["eval_rank_rE"] != r["s"]]
        blk["status_counts"] = {}
        for r in rs:
            blk["status_counts"][r["status"]] = blk["status_counts"].get(r["status"], 0) + 1
        blk["artifact_instances"] = [{"index": r["index"], "status": r["status"], "diffs": r.get("dual_rank_diffs")}
                                     for r in rs if r["status"].startswith("ARTIFACT")]
        blk["censored_instances"] = [{"index": r["index"], "A": r.get("arm_A", {}).get("cap"), "B": r.get("arm_B", {}).get("cap")}
                                     for r in rs if r["status"] == "CENSORED"]
        blk["failed_infrastructure_instances"] = [r["index"] for r in rs if r["status"] == "FAILED_INFRASTRUCTURE"]
        cpu = [((r.get("arm_A") or {}).get("cpu_seconds") or 0) + ((r.get("arm_B") or {}).get("cpu_seconds") or 0) for r in rs]
        wallA = [(r.get("arm_A") or {}).get("wall_seconds") for r in rs if (r.get("arm_A") or {}).get("wall_seconds")]
        rssA = [(r.get("arm_A") or {}).get("peak_rss_bytes") for r in rs if (r.get("arm_A") or {}).get("peak_rss_bytes")]
        rssB = [(r.get("arm_B") or {}).get("peak_rss_bytes") for r in rs if (r.get("arm_B") or {}).get("peak_rss_bytes")]
        wallB = [(r.get("arm_B") or {}).get("wall_seconds") for r in rs if (r.get("arm_B") or {}).get("wall_seconds")]
        blk["resources_measured"] = {
            "solv4_cpu_seconds_total_both_arms": round(sum(cpu), 1),
            "arm_A_wall_seconds": {"min": min(wallA) if wallA else None, "max": max(wallA) if wallA else None,
                                   "mean": round(sum(wallA) / len(wallA), 1) if wallA else None},
            "arm_B_wall_seconds": {"min": min(wallB) if wallB else None, "max": max(wallB) if wallB else None,
                                   "mean": round(sum(wallB) / len(wallB), 1) if wallB else None},
            "peak_rss_bytes_max": {"A": max(rssA) if rssA else None, "B": max(rssB) if rssB else None},
            "s_seconds_note": "per-instance S-A/S-B/S-C seconds are in instances.jsonl"}
        blk["dual_rank_agree_all_valid"] = all(r.get("dual_rank_agree") for r in rs if r["status"] == "VALID")
        arms[arm] = blk
    out["arms"] = arms
    cls = []
    cp = os.path.join(rd, "classify.jsonl")
    if os.path.exists(cp):
        cls = [json.loads(l) for l in open(cp)]
    run_idx = {r["index"] for r in recs if r["arm"] == "primary"}
    out["classification"] = {
        "classified": len(cls),
        "sat": sum(1 for c in cls if c["agree"] and c["s"] > 0),
        "unsat": sum(1 for c in cls if c["agree"] and c["s"] == 0),
        "s_disagreement": [c["index"] for c in cls if not c["agree"]],
        "classified_not_run": sorted(c["index"] for c in cls if c["index"] not in run_idx)}
    tg = params["targets"]
    out["shortfall"] = {}
    for st in ("SAT", "UNSAT"):
        got = arms.get("primary", {}).get(st, {}).get("n", 0)
        out["shortfall"]["primary_" + st] = max(0, tg[st] - got)
    out["shortfall"]["null"] = max(0, tg["null"] - sum(arms.get("null", {}).get(st, {}).get("n", 0) for st in ("SAT", "UNSAT")))
    out["shortfall_reason"] = ("session-level wall allocation (OP-CAPS); counts not reached are not invented. "
                               "See params.allocation_hours and the per-instance wall times.")
    out["cell_artifact"] = any(arms[a]["artifact_instances"] for a in arms)
    with open(os.path.join(rd, "raw-result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    finished = runlib.now_utc()
    cpu_total = sum(arms[a]["resources_measured"]["solv4_cpu_seconds_total_both_arms"] for a in arms)
    peak = max([v for a in arms for v in arms[a]["resources_measured"]["peak_rss_bytes_max"].values() if v] or [0])
    valid = not out["cell_artifact"]
    runlib.write_manifest(
        rd, run_id, "%s cell %s: SOLV4 census, dual arm, SAT/UNSAT strata%s" % (
            params["stage"], params["cell"], ", null arm" if tg["null"] else ""),
        "completed_valid" if valid else "completed_invalid",
        params.get("started_at"), finished, round(time.time() - params.get("t0", time.time()), 1),
        round(cpu_total, 1), peak,
        {"cell": params["cell"], "stage_tag": params["stage"], "targets": tg,
         "allocation_hours": params["allocation_hours"], "null_split_T": params["null_T"],
         "chunk": pipeline.CH, "sub_chunk": pipeline.SUB},
        {a: {st: {k: arms[a][st][k] for k in ("n", "failures", "rate", "clopper_pearson_95")}
             for st in ("SAT", "UNSAT")} for a in arms},
        valid, None if valid else "dual-rank disagreement or s mismatch (SR-4 -> O-ARTIFACT for this cell)",
        {"raw_result": "raw-result.json", "instances": "instances.jsonl", "classification": "classify.jsonl",
         "arm_outputs": "arms/", "solutions": "solutions/", "params": "params.json"},
        ["Session-level allocation and shortfall per raw-result.json. Instance systems are not retained; "
         "each record carries system_sha256 and the regeneration seed namespace."],
        BIN, params["command"])
    return out


def cell(argv):
    run_id, stage = argv[0], argv[1]
    n, m, t, k = map(int, argv[2:6])
    sat, uns, nul = map(int, argv[6:9])
    hours = float(argv[9])
    T = int(argv[10])
    frac = float(argv[11]) if len(argv) > 11 else 0.85
    rd = os.path.join(EXP, "runs", run_id)
    os.makedirs(rd, exist_ok=True)
    cmd = "SEMBIN_BIN=%s SEMBIN_WORK=%s python3 implementation/stage23.py cell %s" % (BIN, WORK, " ".join(argv))
    pfile = os.path.join(rd, "params.json")
    if os.path.exists(pfile):
        params = json.load(open(pfile))
        params.setdefault("resumed_at", []).append(runlib.now_utc())
    else:
        runlib.write_run_files(rd, cmd, BIN)
        params = {"cell": [n, m, t, k], "stage": stage, "targets": {"SAT": sat, "UNSAT": uns, "null": nul},
                  "allocation_hours": hours, "primary_fraction": frac if nul else 1.0,
                  "null_T": T, "command": cmd,
                  "started_at": runlib.now_utc(), "t0": time.time()}
    with open(pfile, "w") as fh:
        json.dump(params, fh, indent=1)
    t_start = time.time()
    prim_deadline = t_start + hours * 3600 * (params["primary_fraction"] if nul else 1.0)
    pipeline.run_primary_cell(rd, [n, m, t, k], stage, {"SAT": sat, "UNSAT": uns}, prim_deadline,
                              workers=2, batch=24)
    Nvars = n * (t - 2) + k * t
    if nul and Nvars > 42:
        params["null_arm_note"] = ("null arm not executed: N = %d > 42, null s not computable in budget "
                                   "-> null arm O-CENSORED by OP-NULL" % Nvars)
    elif nul and params.get("primary_fraction", 1.0) >= 1.0:
        params["null_arm_note"] = ("null arm not executed: zero null allocation in "
                                   "implementation/schedule-allocation.md (cost per null instance)")
    elif nul:
        pipeline.run_null_cell(rd, [n, m, t, k], stage, nul, t_start + hours * 3600, T)
    with open(pfile, "w") as fh:
        json.dump(params, fh, indent=1)
    out = summarize(rd, run_id, params)
    print(json.dumps({"run_id": run_id, "cell": out["cell"],
                      "arms": {a: {st: {kk: out["arms"][a][st][kk] for kk in ("n", "failures", "rate")}
                                   for st in ("SAT", "UNSAT")} for a in out["arms"]},
                      "shortfall": out["shortfall"], "cell_artifact": out["cell_artifact"]}, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "cell":
        cell(sys.argv[2:])
    elif sys.argv[1] == "summarize":
        rd = os.path.join(EXP, "runs", sys.argv[2])
        print(json.dumps(summarize(rd, sys.argv[2])["shortfall"]))
