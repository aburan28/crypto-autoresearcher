#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 Stage 1 (blocking instrument gate).

  stage1.py engine  RUN-ID   EXP-DREG-001 anchors (n=15, n=18; t=3, D=5) + calibration matrices
  stage1.py builder RUN-ID   builder vs point arithmetic at (12,2,2,6), (12,3,3,4) + known-false objects
  stage1.py smoke   RUN-ID   (40,2,2,20) SOLV4 smoke, 8 SAT + 8 UNSAT, dual arm

Environment: SEMBIN_BIN (binaries from build.sh), SEMBIN_WORK (scratch).
"""
import json
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import pipeline  # noqa: E402
import runlib  # noqa: E402

BIN = os.environ["SEMBIN_BIN"]
WORK = os.environ["SEMBIN_WORK"]
EXP = runlib.EXP
STAGE1 = os.path.join(EXP, "stage1")

DREG_EXPECTED = {
    15: {"rank": 69073, "nrows": 74880, "ncols": 143421,
         "system_hash": "23c234edb06c27dff137ac0c2f950706257fa8de87435953bdeeb0d140788403",
         "source": "experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N15-A"},
    18: {"rank": 143882, "nrows": 152532, "ncols": 358678,
         "system_hash": "b8bec47d65de694f1f78a0038c91d27a84856d1c1f2cc7a4b0f64ac17041515a",
         "source": "experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N18-A"},
}


def run_pair(cmds, logs):
    res = {}

    def go(k):
        res[k] = pipeline.run_capped(cmds[k], logs[k])

    th = [threading.Thread(target=go, args=(k,)) for k in cmds]
    for t in th:
        t.start()
    for t in th:
        t.join()
    return res


def engine(run_id):
    rd = os.path.join(EXP, "runs", run_id)
    os.makedirs(os.path.join(rd, "inputs"), exist_ok=True)
    os.makedirs(os.path.join(rd, "arms"), exist_ok=True)
    cmd = "SEMBIN_BIN=%s SEMBIN_WORK=%s python3 implementation/stage1.py engine %s" % (BIN, WORK, run_id)
    runlib.write_run_files(rd, cmd, BIN)
    started, t0 = runlib.now_utc(), time.time()
    out = {"anchors": {}, "calibration": {}}
    cpu = 0.0
    peak = 0
    for n in (15, 18):
        s = builder.dreg_anchor_system(n)
        sysp = os.path.join(rd, "inputs", "dreg_anchor_n%d_t3_seed2026_ti0.sys" % n)
        builder.write_system(sysp, s["N"], s["equations"],
                             {"source": "EXP-DREG-001 build_system(n=%d,t=3,ti=0,seed=2026) rebuilt without Sage" % n,
                              "modulus_conway": "%x" % s["f"], "RX": "%x" % s["RX"],
                              "system_hash_dreg_convention": s["system_hash"]})
        exp = DREG_EXPECTED[n]
        cmds, logs = {}, {}
        for arm in ("A", "B"):
            o = os.path.join(rd, "arms", "anchor_n%d_%s.json" % (n, arm))
            cmds[arm] = [BIN + "/solv4_" + arm, "macrank", sysp, "5", "1", o, "8192",
                         str(pipeline.SUB[arm])]
            logs[arm] = os.path.join(rd, "arms", "anchor_n%d_%s" % (n, arm))
        res = run_pair(cmds, logs)
        rec = {"expected": exp, "system_hash": s["system_hash"],
               "system_hash_match": s["system_hash"] == exp["system_hash"],
               "RX": s["RX"], "modulus": "%x" % s["f"], "arms": {}}
        ok = rec["system_hash_match"]
        for arm in ("A", "B"):
            o = cmds[arm][5]
            js = json.load(open(o)) if res[arm]["rc"] == 0 and os.path.exists(o) else None
            rec["arms"][arm] = {"cap": res[arm], "result": js}
            if js:
                cpu += js["cpu_seconds"]
                peak = max(peak, js["peak_rss_bytes"])
                okarm = (js["rank"] == exp["rank"] and js["nrows"] == exp["nrows"]
                         and js["ncols_support"] == exp["ncols"])
            else:
                okarm = False
            rec["arms"][arm]["reproduces_anchor"] = okarm
            ok = ok and okarm
        rec["pass"] = ok
        out["anchors"]["n%d" % n] = rec
    seed = "20261005"
    for inj in (0, 1):
        cmds, logs = {}, {}
        for arm in ("A", "B"):
            o = os.path.join(rd, "arms", "calib_inject%d_%s.json" % (inj, arm))
            cmds[arm] = [BIN + "/solv4_" + arm, "calib", "20000", "30000", "17000", str(inj), seed, o,
                         "8192", str(pipeline.SUB[arm])]
            logs[arm] = os.path.join(rd, "arms", "calib_inject%d_%s" % (inj, arm))
        res = run_pair(cmds, logs)
        rec = {"m": 20000, "n": 30000, "planted_rank": 17000 - inj, "inject": inj, "seed": seed, "arms": {}}
        ranks = []
        for arm in ("A", "B"):
            o = cmds[arm][7]
            js = json.load(open(o)) if res[arm]["rc"] == 0 and os.path.exists(o) else None
            rec["arms"][arm] = {"cap": res[arm], "result": js}
            ranks.append(js["rank"] if js else None)
            if js:
                cpu += js["cpu_seconds"]
                peak = max(peak, js["peak_rss_bytes"])
        rec["arms_agree"] = ranks[0] == ranks[1] and ranks[0] is not None
        trajA = rec["arms"]["A"]["result"]["chunk_rank_trajectory"] if rec["arms"]["A"]["result"] else None
        trajB = rec["arms"]["B"]["result"]["chunk_rank_trajectory"] if rec["arms"]["B"]["result"] else None
        rec["trajectories_agree"] = trajA == trajB and trajA is not None
        rec["matches_planted"] = ranks[0] == 17000 - inj
        rec["pass"] = rec["arms_agree"] and rec["trajectories_agree"] and rec["matches_planted"]
        out["calibration"]["inject%d" % inj] = rec
    gate = all(v["pass"] for v in out["anchors"].values()) and all(v["pass"] for v in out["calibration"].values())
    out["SR2_engine_gate_pass"] = gate
    out["injected_deficiency_seen_by_both_arms"] = (
        out["calibration"]["inject1"]["arms"]["A"]["result"] is not None
        and out["calibration"]["inject0"]["arms"]["A"]["result"]["rank"] - out["calibration"]["inject1"]["arms"]["A"]["result"]["rank"] == 1
        and out["calibration"]["inject0"]["arms"]["B"]["result"]["rank"] - out["calibration"]["inject1"]["arms"]["B"]["result"]["rank"] == 1)
    finished = runlib.now_utc()
    out["run_id"] = run_id
    out["finished_at_utc"] = finished
    with open(os.path.join(rd, "raw-result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    summary = {
        "document": "EXP-SEMBIN-35bf67 Stage-1 engine gate (SR-2). Observations only.",
        "run_id": run_id,
        "anchors": {k: {"expected_rank": v["expected"]["rank"], "system_hash_match": v["system_hash_match"],
                        "rank_A": (v["arms"]["A"]["result"] or {}).get("rank"),
                        "rank_B": (v["arms"]["B"]["result"] or {}).get("rank"),
                        "nrows_A": (v["arms"]["A"]["result"] or {}).get("nrows"),
                        "ncols_support_A": (v["arms"]["A"]["result"] or {}).get("ncols_support"),
                        "wall_A": (v["arms"]["A"]["result"] or {}).get("wall_seconds"),
                        "wall_B": (v["arms"]["B"]["result"] or {}).get("wall_seconds"),
                        "pass": v["pass"]} for k, v in out["anchors"].items()},
        "calibration": {k: {"planted_rank": v["planted_rank"],
                            "rank_A": (v["arms"]["A"]["result"] or {}).get("rank"),
                            "rank_B": (v["arms"]["B"]["result"] or {}).get("rank"),
                            "pass": v["pass"]} for k, v in out["calibration"].items()},
        "injected_deficiency_seen_by_both_arms": out["injected_deficiency_seen_by_both_arms"],
        "dual_arm_independence": "Arm A kernels = M4RI release-20240729 (git d0a1ee18, source build, not apt "
                                 "0.0.20200125); arm B kernels = executor C (kernel_b.c), no M4RI code. Shared: "
                                 "system construction, monomial indexing, compact-RREF bookkeeping (solv4.c).",
        "SR2_engine_gate_pass": gate,
        "outcome_if_fail": "O-ENGINE-FAIL; stop before Stage 2",
    }
    with open(os.path.join(STAGE1, "engine-gate.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    runlib.write_manifest(
        rd, run_id, "stage1_engine_gate (SR-2): EXP-DREG-001 anchors + calibration", "completed_valid",
        started, finished, round(time.time() - t0, 3), round(cpu, 3), peak,
        {"anchors": {"n15": DREG_EXPECTED[15], "n18": DREG_EXPECTED[18]},
         "calibration": {"m": 20000, "n": 30000, "rank": 17000, "inject": [0, 1], "seed": seed},
         "chunk": 8192, "sub_chunk": pipeline.SUB},
        {"SR2_engine_gate_pass": gate,
         "anchor_ranks": {k: [summary["anchors"][k]["rank_A"], summary["anchors"][k]["rank_B"]] for k in summary["anchors"]},
         "calibration_ranks": {k: [summary["calibration"][k]["rank_A"], summary["calibration"][k]["rank_B"]] for k in summary["calibration"]}},
        True, None,
        {"raw_result": "raw-result.json", "arm_outputs": "arms/", "anchor_systems": "inputs/",
         "stage_summary": "../../stage1/engine-gate.json"},
        ["Anchor systems rebuilt without Sage: Conway modulus, A=1, B=alpha, lift_x y-values ascending, "
         "random.Random(2026+n).sample, and PolyBoRi reversed variable indexing; identity established by "
         "the recorded EXP-DREG-001 system_hash (monosets_hash convention)."],
        BIN, cmd)
    print(json.dumps(summary, indent=1))


def builder_check(run_id):
    rd = os.path.join(EXP, "runs", run_id)
    os.makedirs(rd, exist_ok=True)
    cmd = "SEMBIN_BIN=%s SEMBIN_WORK=%s python3 implementation/stage1.py builder %s" % (BIN, WORK, run_id)
    runlib.write_run_files(rd, cmd, BIN)
    started, t0 = runlib.now_utc(), time.time()
    wd = os.path.join(WORK, run_id)
    os.makedirs(wd, exist_ok=True)
    recs = []
    allok = True
    for cell in [(12, 2, 2, 6), (12, 3, 3, 4)]:
        for i in range(20):
            p = builder.primary_instance(cell, "stage1-builder", i)
            sysp = os.path.join(wd, "sys.txt")
            builder.write_system(sysp, p["N"], p["equations"])
            n, m, t, k = cell
            sets = {}
            for meth in ("A", "B"):
                pf = os.path.join(wd, "pts_" + meth)
                subprocess.run([BIN + "/sols", meth, str(n), "%x" % p["f"], str(k), str(t), "%x" % p["B"],
                                "%x" % p["z"], "%x" % p["A"], pf], check=True, capture_output=True)
                sets["S-A" if meth == "A" else "S-B"] = pipeline.read_points(pf)
            pf = os.path.join(wd, "pts_naive")
            subprocess.run([BIN + "/exhaust", "check", sysp, pf], check=True, capture_output=True)
            sets["naive_exhaustive"] = pipeline.read_points(pf)
            pf = os.path.join(wd, "pts_gray")
            subprocess.run([BIN + "/exhaust", sysp, "0", "0", pf], check=True, capture_output=True)
            sets["S-C_gray"] = pipeline.read_points(pf)
            vals = list(sets.values())
            ok = all(v == vals[0] for v in vals)
            allok = allok and ok
            recs.append({"cell": list(cell), "index": i, "B": "%x" % p["B"], "z": "%x" % p["z"],
                         "f": "%x" % p["f"], "system_sha256": pipeline.sha256_file(sysp),
                         "counts": {kk: len(v) for kk, v in sets.items()}, "solutions": vals[0], "sets_agree": ok})
    # known-false objects (instrument sanity; DEC-20261005-c83e5a B3 proposals)
    kf = []
    # (i) counting-false: (12,2,2,6) instance truncated to its first 2 equations -> s > M_le4 = 794
    p = builder.primary_instance((12, 2, 2, 6), "stage1-builder", 100)
    eqs = [e for e in p["equations"] if e][:2]
    sysp = os.path.join(wd, "kf1.txt")
    builder.write_system(sysp, p["N"], eqs)
    pf = os.path.join(wd, "kf1_pts")
    subprocess.run([BIN + "/exhaust", "check", sysp, pf], check=True, capture_output=True)
    s1 = len(pipeline.read_points(pf))
    arms = {}
    for arm in ("A", "B"):
        o = os.path.join(wd, "kf1_%s.json" % arm)
        subprocess.run([BIN + "/solv4_" + arm, "closure", sysp, pf, o, "8192", str(pipeline.SUB[arm])], check=True)
        arms[arm] = json.load(open(o))
    kf.append({"object": "truncated (12,2,2,6) idx100, first 2 equations", "s_naive": s1, "M_le4": arms["A"]["M_le4"],
               "solv4_A": arms["A"]["solv4"], "solv4_B": arms["B"]["solv4"], "dim_A": arms["A"]["dim_R4"],
               "dim_B": arms["B"]["dim_R4"], "expected": "SOLV4 false (s > M_le4 makes dim = M - s impossible)",
               "pass": s1 > arms["A"]["M_le4"] and arms["A"]["solv4"] == 0 and arms["B"]["solv4"] == 0
               and arms["A"]["dim_R4"] == arms["B"]["dim_R4"]})
    # (ii) planted-inconsistent: a SAT (12,3,3,4) instance with one monomial toggled -> UNSAT
    sat = [r for r in recs if r["cell"] == [12, 3, 3, 4] and r["counts"]["S-A"] > 0]
    found = None
    if sat:
        r0 = sat[0]
        p = builder.primary_instance((12, 3, 3, 4), "stage1-builder", r0["index"])
        eqs = [list(e) for e in p["equations"] if e]
        for ei in range(len(eqs)):
            for mono in [0, 1, 2, 4] + list(eqs[ei][:4]):
                e2 = [list(e) for e in eqs]
                if mono in e2[ei]:
                    e2[ei].remove(mono)
                else:
                    e2[ei].append(mono)
                sysp = os.path.join(wd, "kf2.txt")
                builder.write_system(sysp, p["N"], [sorted(e) for e in e2])
                pf = os.path.join(wd, "kf2_pts")
                subprocess.run([BIN + "/exhaust", "check", sysp, pf], check=True, capture_output=True)
                if len(pipeline.read_points(pf)) == 0:
                    found = (ei, mono)
                    break
            if found:
                break
        if found:
            arms = {}
            for arm in ("A", "B"):
                o = os.path.join(wd, "kf2_%s.json" % arm)
                subprocess.run([BIN + "/solv4_" + arm, "closure", sysp, pf, o, "8192", str(pipeline.SUB[arm])], check=True)
                arms[arm] = json.load(open(o))
            kf.append({"object": "planted-inconsistent: (12,3,3,4) SAT idx %d (s=%d), equation %d monomial %x toggled"
                       % (r0["index"], r0["counts"]["S-A"], found[0], found[1]),
                       "s_naive_after_toggle": 0, "verdict_A": arms["A"]["verdict"], "verdict_B": arms["B"]["verdict"],
                       "dim_A": arms["A"]["dim_R4"], "dim_B": arms["B"]["dim_R4"], "M_le4": arms["A"]["M_le4"],
                       "expected": "never reports the planted count; SOLV4 iff 1 in R_4 (dim = M_le4)",
                       "pass": arms["A"]["dim_R4"] == arms["B"]["dim_R4"]
                       and ((arms["A"]["solv4"] == 1 and arms["A"]["dim_R4"] == arms["A"]["M_le4"]) or arms["A"]["solv4"] == 0)})
    if not found:
        kf.append({"object": "planted-inconsistent", "pass": None, "note": "no single-monomial toggle made the instance UNSAT among tried candidates"})
    finished = runlib.now_utc()
    out = {"run_id": run_id, "instances": recs, "known_false_objects": kf,
           "builder_vs_point_arithmetic_all_agree": allok}
    with open(os.path.join(rd, "raw-result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    summary = {"document": "EXP-SEMBIN-35bf67 Stage-1 builder solution set vs point arithmetic (tiny cells) and known-false objects",
               "run_id": run_id, "cells": [[12, 2, 2, 6], [12, 3, 3, 4]], "instances_per_cell": 20,
               "methods": ["S-A (S_3 quadratic over V)", "S-B (group law on E over F_q / F_q^2)",
                           "S-C (Gray-code exhaustive over 2^N)", "naive exhaustive over 2^N"],
               "all_solution_sets_agree": allok,
               "per_cell_counts": {str(c): [r["counts"]["S-A"] for r in recs if r["cell"] == list(c)] for c in [(12, 2, 2, 6), (12, 3, 3, 4)]},
               "known_false_objects": kf}
    with open(os.path.join(STAGE1, "builder-check.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    runlib.write_manifest(rd, run_id, "stage1_builder_check: solution set vs point arithmetic at tiny cells; known-false objects",
                          "completed_valid", started, finished, round(time.time() - t0, 3), None, None,
                          {"cells": [[12, 2, 2, 6], [12, 3, 3, 4]], "stage_tag": "stage1-builder", "indices": "0..19"},
                          {"all_solution_sets_agree": allok, "known_false_pass": [x.get("pass") for x in kf]},
                          True, None, {"raw_result": "raw-result.json", "stage_summary": "../../stage1/builder-check.json"},
                          [], BIN, cmd)
    print(json.dumps(summary, indent=1)[:3000])


def smoke(run_id):
    rd = os.path.join(EXP, "runs", run_id)
    os.makedirs(rd, exist_ok=True)
    cmd = "SEMBIN_BIN=%s SEMBIN_WORK=%s python3 implementation/stage1.py smoke %s" % (BIN, WORK, run_id)
    if not os.path.exists(os.path.join(rd, "command.txt")):
        runlib.write_run_files(rd, cmd, BIN)
    started, t0 = runlib.now_utc(), time.time()
    cell = [40, 2, 2, 20]
    pipeline.run_primary_cell(rd, cell, "stage1-smoke", {"SAT": 8, "UNSAT": 8}, time.time() + 6 * 3600,
                              workers=2, batch=16)
    done = pipeline.load_done(rd)
    recs = [r for r in done.values() if r["arm"] == "primary"]
    strata = {}
    for st in ("SAT", "UNSAT"):
        rs = [r for r in recs if r.get("stratum") == st and r["status"] == "VALID"]
        fails = sum(1 for r in rs if not r["solv4"])
        strata[st] = {"n": len(rs), "failures": fails, "rate": (fails / len(rs)) if rs else None,
                      "indices": sorted(r["index"] for r in rs)}
    nonvalid = [{"index": r["index"], "status": r["status"]} for r in recs if r["status"] != "VALID"]
    sr3_fail = any(v["rate"] is not None and v["rate"] > 0.10 for v in strata.values())
    complete = all(v["n"] >= 8 for v in strata.values())
    artifact = any(r["status"].startswith("ARTIFACT") for r in recs)
    finished = runlib.now_utc()
    cpu = sum((r.get("arm_A", {}).get("cpu_seconds") or 0) + (r.get("arm_B", {}).get("cpu_seconds") or 0) for r in recs)
    peak = max([max(r.get("arm_A", {}).get("peak_rss_bytes") or 0, r.get("arm_B", {}).get("peak_rss_bytes") or 0) for r in recs] or [0])
    summary = {"document": "EXP-SEMBIN-35bf67 Stage-1 Semaev (40,2,2,20) SOLV4 smoke (SR-3). Observations only.",
               "run_id": run_id, "cell": cell, "strata": strata, "non_valid_instances": nonvalid,
               "dual_rank_artifact_present": artifact, "smoke_complete_8_per_stratum": complete,
               "SR3_failure_rate_gt_0.10_in_any_stratum": sr3_fail,
               "per_instance": sorted([{"index": r["index"], "stratum": r.get("stratum"), "s": r.get("s"),
                                        "solv4": r.get("solv4"), "dim_R4": r.get("dim_R4"),
                                        "closure_round_count": r.get("closure_round_count"),
                                        "dual_rank_agree": r.get("dual_rank_agree"),
                                        "wall_A": r.get("arm_A", {}).get("wall_seconds"),
                                        "wall_B": r.get("arm_B", {}).get("wall_seconds"),
                                        "peak_rss_A": r.get("arm_A", {}).get("peak_rss_bytes"),
                                        "peak_rss_B": r.get("arm_B", {}).get("peak_rss_bytes"),
                                        "status": r["status"]} for r in recs], key=lambda x: x["index"]),
               "outcome_if_fail": "O-BASELINE-FAIL; stop before claiming Stage 2"}
    with open(os.path.join(rd, "raw-result.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(STAGE1, "baseline-smoke.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    runlib.write_manifest(rd, run_id, "stage1_smoke (SR-3): SOLV4 at (40,2,2,20), 8 SAT + 8 UNSAT, dual arm",
                          "completed_valid" if complete and not artifact else "completed_invalid",
                          started, finished, round(time.time() - t0, 3), round(cpu, 3), peak,
                          {"cell": cell, "stage_tag": "stage1-smoke", "targets": {"SAT": 8, "UNSAT": 8}},
                          {"strata": strata, "SR3_fail": sr3_fail},
                          complete and not artifact, None if complete and not artifact else "incomplete or artifact",
                          {"raw_result": "raw-result.json", "instances": "instances.jsonl",
                           "classification": "classify.jsonl", "arm_outputs": "arms/", "solutions": "solutions/",
                           "stage_summary": "../../stage1/baseline-smoke.json"}, [], BIN, cmd)
    print(json.dumps({k: summary[k] for k in summary if k != "per_instance"}, indent=1))


if __name__ == "__main__":
    {"engine": engine, "builder": builder_check, "smoke": smoke}[sys.argv[1]](sys.argv[2])
