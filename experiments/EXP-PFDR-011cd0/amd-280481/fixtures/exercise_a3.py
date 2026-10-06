"""EXP-PFDR-011cd0 pre-pin fixture exercise: runs run_jobs.py (dummy commands only),
merge_relcensus.py, analyze_relcensus.py, verify_rows.py and verify_solves.py on the
fixtures of make_fixtures.py (task scratch FX) and checks every planted case.  Writes a JSON log
(--log) with each command, its exit code, the expectation and whether it was met."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

REPO = "/home/user/crypto-autoresearcher"
PY = sys.executable
E = "experiments/EXP-PFDR-011cd0"
LOG = []


def run(label, cmd, expect_rc=None, check=None):
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    ok_rc = expect_rc is None or r.returncode in (expect_rc if isinstance(expect_rc, tuple) else (expect_rc,))
    res = {"step": label, "cmd": " ".join(cmd), "exit_code": r.returncode, "expected_exit": expect_rc,
           "stdout_tail": r.stdout[-1500:], "stderr_tail": r.stderr[-1500:]}
    met = ok_rc
    if check is not None:
        try:
            c = check()
            res["check"] = c[1]
            met = met and c[0]
        except Exception as exc:  # recorded
            res["check"] = f"check raised {type(exc).__name__}: {exc}"
            met = False
    res["expectation_met"] = bool(met)
    LOG.append(res)
    print(f"[{'OK ' if met else 'BAD'}] {label} (exit {r.returncode})", flush=True)
    return r


def j(path):
    return json.load(open(path))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fx", required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    FX = a.fx
    D = os.path.join(FX, "dummy")
    os.makedirs(D)
    # 1. run_jobs.py with dummy commands only
    run("jobs R10 list", [PY, f"{E}/run_jobs.py", "jobs", "--run", "R10", "--out", f"{D}/jobs-r10.json"], 0,
        lambda: (len(j(f"{D}/jobs-r10.json")["jobs"]) == 45, "45 R10 jobs"))
    run("jobs R14 list", [PY, f"{E}/run_jobs.py", "jobs", "--run", "R14", "--out", f"{D}/jobs-r14.json"], 0,
        lambda: (sum(len(x["expected_keys"]) for x in j(f"{D}/jobs-r14.json")["jobs"]) == 264, "264 R14 instances"))
    first4 = ",".join(x["name"] for x in j(f"{D}/jobs-r10.json")["jobs"][:4])
    att = f"{D}/RUN-dummy-ok/attempt-1"
    run("dummy run ok", [PY, f"{E}/run_jobs.py", "run", "--run-id", "RUN-dummy-ok", "--attempt-dir", att,
                         "--jobs-file", f"{D}/jobs-r10.json", "--only", first4, "--trigger", "fixture",
                         "--dummy", "--poll", "0.5"], 0)
    run("dummy finalize ok -> completed_valid, discrete_log verified true",
        [PY, f"{E}/run_jobs.py", "finalize-attempt", "--attempt-dir", att, "--run-id", "RUN-dummy-ok"], 0,
        lambda: (lambda m: (m["run"]["status"] == "completed_valid"
                            and m["run"]["result"]["certificate"]["kind"] == "discrete_log"
                            and m["run"]["result"]["certificate"]["verified"] is True,
                            m["run"]["result"]["certificate"]))(__import__("yaml").safe_load(open(f"{att}/manifest.yaml"))))
    names = [x["name"] for x in j(f"{D}/jobs-r10.json")["jobs"][:4]]
    beh = {names[0]: "invalid", names[1]: "missing", names[2]: "crash", names[3]: "badcert"}
    att2 = f"{D}/RUN-dummy-bad/attempt-1"
    run("dummy run planted failures (max-procs 1: invalid stops the run)",
        [PY, f"{E}/run_jobs.py", "run", "--run-id", "RUN-dummy-bad", "--attempt-dir", att2, "--jobs-file",
         f"{D}/jobs-r10.json", "--only", ",".join(names), "--trigger", "fixture", "--dummy", "--max-procs", "1",
         "--dummy-behaviour-json", json.dumps(beh), "--poll", "0.5"], 0,
        lambda: (lambda ix: (ix["run_stop_at_job"] is not None and len(ix["not_started"]) >= 1,
                             {"run_stop_at_job": ix["run_stop_at_job"], "not_started": ix["not_started"]}))(j(f"{att2}/jobs-index.json")))
    run("dummy finalize planted failures -> invalid, certificate kind none",
        [PY, f"{E}/run_jobs.py", "finalize-attempt", "--attempt-dir", att2, "--run-id", "RUN-dummy-bad"], 0,
        lambda: (lambda m: (m["run"]["status"] == "invalid" and m["run"]["result"]["certificate"]["kind"] == "none",
                            m["run"]["validity"]))(__import__("yaml").safe_load(open(f"{att2}/manifest.yaml"))))
    beh3 = {names[0]: "missing", names[1]: "crash", names[2]: "badcert", names[3]: "ok"}
    att3 = f"{D}/RUN-dummy-bad2/attempt-1"
    run("dummy run missing/crash/badcert (no invalid row)",
        [PY, f"{E}/run_jobs.py", "run", "--run-id", "RUN-dummy-bad2", "--attempt-dir", att3, "--jobs-file",
         f"{D}/jobs-r10.json", "--only", ",".join(names), "--trigger", "fixture", "--dummy",
         "--dummy-behaviour-json", json.dumps(beh3), "--poll", "0.5"], 0)
    run("dummy finalize: bad certificate -> invalid (verify_solves rejects k+1)",
        [PY, f"{E}/run_jobs.py", "finalize-attempt", "--attempt-dir", att3, "--run-id", "RUN-dummy-bad2"], 0,
        lambda: (lambda raw: (raw["certificate"]["verify_pass"] is False and raw["completeness"]["keys_missing"] >= 1,
                              {"cert": raw["certificate"], "completeness": raw["completeness"],
                               "abnormal": raw["abnormal_job_ends"]}))(j(f"{att3}/raw-result.json")))
    beh4 = {names[0]: "fi", names[1]: "missing"}
    rd5 = f"{D}/RUN-dummy-resume"
    run("dummy attempt-1 with a failed_infrastructure row and a missing key",
        [PY, f"{E}/run_jobs.py", "run", "--run-id", "RUN-dummy-resume", "--attempt-dir", f"{rd5}/attempt-1",
         "--jobs-file", f"{D}/jobs-r10.json", "--only", ",".join(names[:2]), "--trigger", "fixture", "--dummy",
         "--dummy-behaviour-json", json.dumps(beh4), "--poll", "0.5"], 0)
    run("dummy finalize -> failed_infrastructure",
        [PY, f"{E}/run_jobs.py", "finalize-attempt", "--attempt-dir", f"{rd5}/attempt-1", "--run-id", "RUN-dummy-resume"], 0,
        lambda: (__import__("yaml").safe_load(open(f"{rd5}/attempt-1/manifest.yaml"))["run"]["status"] == "failed_infrastructure", "status"))
    run("dummy attempt-2 resumes both jobs",
        [PY, f"{E}/run_jobs.py", "run", "--run-id", "RUN-dummy-resume", "--attempt-dir", f"{rd5}/attempt-2",
         "--jobs-file", f"{D}/jobs-r10.json", "--only", ",".join(names[:2]), "--trigger", "fixture", "--dummy",
         "--poll", "0.5"], 0)
    run("merge dummy attempts: failed row superseded, missing key filled",
        [PY, f"{E}/merge_relcensus.py", "merge", "--run-dir", rd5, "--run-id", "RUN-dummy-resume",
         "--attempts", "attempt-1", "attempt-2"], 0,
        lambda: (lambda mr: (len(mr["superseded_rows"]) >= 1 and not mr["missing_keys"]
                             and mr["keys_with_exactly_one_canonical_row"],
                             {"superseded": len(mr["superseded_rows"]), "missing": mr["missing_keys"]}))(j(f"{rd5}/merge-report.json")))
    rd6 = f"{D}/RUN-dummy-missing"
    run("dummy attempt with a missing key only",
        [PY, f"{E}/run_jobs.py", "run", "--run-id", "RUN-dummy-missing", "--attempt-dir", f"{rd6}/attempt-1",
         "--jobs-file", f"{D}/jobs-r10.json", "--only", names[0], "--trigger", "fixture", "--dummy",
         "--dummy-behaviour-json", json.dumps({names[0]: "missing"}), "--poll", "0.5"], 0)
    run("merge reports the missing key (exit 1)",
        [PY, f"{E}/merge_relcensus.py", "merge", "--run-dir", rd6, "--run-id", "RUN-dummy-missing",
         "--attempts", "attempt-1"], 1,
        lambda: (len(j(f"{rd6}/merge-report.json")["missing_keys"]) == 1, "one missing key"))
    # 2. merge / view / gates on the toy engine fixtures (A1)
    A1 = os.path.join(FX, "A1", "runs")
    run("merge A1 table: planted duplicate row reported (exit 1)",
        [PY, f"{E}/merge_relcensus.py", "merge", "--run-dir", f"{A1}/RUN-PFDR-011cd0-table",
         "--run-id", "RUN-PFDR-011cd0-table", "--attempts", "attempt-1"], 1,
        lambda: (len(j(f"{A1}/RUN-PFDR-011cd0-table/merge-report.json")["duplicate_rows_within_attempt"]) == 1, "dup"))
    for run_name in ("RUN-PFDR-011cd0-search", "RUN-PFDR-011cd0-srch-check"):
        run(f"merge A1 {run_name}", [PY, f"{E}/merge_relcensus.py", "merge", "--run-dir", f"{A1}/{run_name}",
                                     "--run-id", run_name, "--attempts", "attempt-1"], 0)
    run("view A1", [PY, f"{E}/merge_relcensus.py", "view", "--runs", f"{A1}/RUN-PFDR-011cd0-table",
                    f"{A1}/RUN-PFDR-011cd0-search", "--out", f"{FX}/A1/view"], 0,
        lambda: (os.path.exists(f"{FX}/A1/view/view-map.json"), "view-map"))
    run("tabcompare A1 (G-TAB) passes", [PY, f"{E}/merge_relcensus.py", "tabcompare", "--table",
                                        f"{A1}/RUN-PFDR-011cd0-table", "--search", f"{A1}/RUN-PFDR-011cd0-search",
                                        "--out", f"{FX}/A1/tab-report.json"], 0)
    run("srchcompare A1 (G-SRCH) passes", [PY, f"{E}/merge_relcensus.py", "srchcompare", "--search",
                                          f"{A1}/RUN-PFDR-011cd0-search", "--check", f"{A1}/RUN-PFDR-011cd0-srch-check",
                                          "--out", f"{FX}/A1/srch-report.json"], 0,
        lambda: (lambda r: (r["pass"], {"matched": r["matched"], "censored": len(r["census_stopped_before_X_fix"])}))(j(f"{FX}/A1/srch-report.json")))
    run("curvecheck A1 good design passes", [PY, f"{E}/merge_relcensus.py", "curvecheck", "--design",
                                            f"{FX}/A1/design-good.json", "--runs", f"{A1}/RUN-PFDR-011cd0-table",
                                            f"{A1}/RUN-PFDR-011cd0-search", "--out", f"{FX}/A1/curve-good.json"], 0)
    run("curvecheck A1 planted mismatch fails", [PY, f"{E}/merge_relcensus.py", "curvecheck", "--design",
                                                f"{FX}/A1/design-planted-mismatch.json", "--runs",
                                                f"{A1}/RUN-PFDR-011cd0-table", "--out", f"{FX}/A1/curve-bad.json"], 1)
    run("grel A1 (G-REL) passes", [PY, f"{E}/amd-280481/analyze_relcensus.py", "grel", "--runs", f"{A1}/RUN-PFDR-011cd0-table",
                                  f"{A1}/RUN-PFDR-011cd0-search", f"{A1}/RUN-PFDR-011cd0-srch-check",
                                  "--out", f"{FX}/A1/grel.json"], 0)
    bad = f"{FX}/A1/RUN-grel-planted"
    shutil.copytree(f"{A1}/RUN-PFDR-011cd0-table", bad, symlinks=True)
    rows = [json.loads(l) for l in gzip.open(f"{bad}/rows.jsonl.gz", "rt")]
    for r in rows:
        if r["arm"] == "random_sub_r0" and r["harvest"]["TT"]["at_stop"]["rows_emitted"] > 0:
            r["harvest"]["TT"]["at_stop"]["relations_distinct"] += 1
            break
    os.remove(f"{bad}/rows.jsonl.gz")
    with gzip.open(f"{bad}/rows.jsonl.gz", "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    run("grel planted mismatch fails", [PY, f"{E}/amd-280481/analyze_relcensus.py", "grel", "--runs", bad,
                                       "--out", f"{FX}/A1/grel-bad.json"], 1)
    run("verify_rows A1 table (G4-R) passes", [PY, f"{E}/verify_rows.py", "--run-dir", f"{A1}/RUN-PFDR-011cd0-table",
                                              "--out", f"{FX}/A1/row-verify-table.json", "--sample-mod", "1"], 0)
    run("verify_rows A1 search passes", [PY, f"{E}/verify_rows.py", "--run-dir", f"{A1}/RUN-PFDR-011cd0-search",
                                        "--out", f"{FX}/A1/row-verify-search.json", "--sample-mod", "1"], 0)
    badr = f"{FX}/A1/RUN-rows-planted"
    shutil.copytree(f"{A1}/RUN-PFDR-011cd0-table", badr)
    mr = j(f"{badr}/merge-report.json")
    hfile = next(v["harvest_rows_file"] for v in mr["harvest_rows_map"].values() if v["harvest_rows_file"])
    hrs = [json.loads(l) for l in gzip.open(os.path.join(REPO, hfile), "rt")]
    hrs[0]["rhs"] = (hrs[0]["rhs"] + 1)
    newh = f"{badr}/planted-harvest-rows.jsonl.gz"
    with gzip.open(newh, "wt") as fh:
        for h in hrs:
            fh.write(json.dumps(h) + "\n")
    for k, v in mr["harvest_rows_map"].items():
        if v["harvest_rows_file"] == hfile:
            v["harvest_rows_file"] = newh
    json.dump(mr, open(f"{badr}/merge-report.json", "w"))
    run("verify_rows planted corrupted row fails", [PY, f"{E}/verify_rows.py", "--run-dir", badr, "--out",
                                                   f"{FX}/A1/row-verify-bad.json", "--sample-mod", "1"], 1)
    run("verify_solves A1 srch-check certificates pass",
        [PY, f"{E}/verify_solves.py", f"{A1}/RUN-PFDR-011cd0-srch-check/solve-certs.jsonl.gz", "--out",
         f"{FX}/A1/solve-verify.json"], 0)
    # 3. fixcompare (G-FIX) on A2 (archive) vs A3 (new): the straddle pair edit is attributed,
    #    the s3_solves edit is not
    A3 = f"{FX}/A3/RUN-PFDR-011cd0-fix-check"
    run("merge A3", [PY, f"{E}/merge_relcensus.py", "merge", "--run-dir", A3, "--run-id", "RUN-PFDR-011cd0-fix-check",
                     "--attempts", "attempt-1"], 0)
    planted = j(f"{FX}/A2/planted.json")
    run("fixcompare: exactly the planted s3_solves edit is unattributed (exit 1)",
        [PY, f"{E}/merge_relcensus.py", "fixcompare", "--old-runs", f"{FX}/A2/runs", "--new", A3,
         "--out", f"{A3}/fix-report.json"], 1,
        lambda: (lambda r: ([u["key"] for u in r["unattributed"]] == [planted["s3_solves_changed_key"]]
                            and r["instances_with_pair_change"] >= 1,
                            {"unattributed": r["unattributed"], "pair_changes": r["instances_with_pair_change"]}))(j(f"{A3}/fix-report.json")))
    # 4. P0 on the synthetic archive (C): P0X must find the planted wrong count
    C = f"{FX}/C"
    os.makedirs(f"{C}/out")
    run("p0 on synthetic inputs: P0X detects the planted count (exit 1), design written",
        [PY, f"{E}/amd-280481/analyze_relcensus.py", "p0", "--archived-runs", f"{C}/runs", "--bundles", f"{C}/bundles.jsonl",
         "--curves", f"{C}/curves.jsonl.gz", "--spec", f"{C}/fake-spec.yaml", "--out", f"{C}/out", "--reps", "1000"], 1,
        lambda: (lambda r, d: (r["difference_count"] == 1 and r["compared"] > 10 and "final_n" in d,
                               {"p0x_compared": r["compared"], "differences": r["differences"],
                                "final_n": d["final_n"], "t_star_plan": d["t_star_plan"]["t"],
                                "rule": [{k: v for k, v in x.items() if k != "evaluations"} for x in d["rule"]],
                                "design_stop": d["design_stop"]}))(j(f"{C}/out/p0x-report.json"), j(f"{C}/out/design.json")))
    # 5. calibrate / unmask on the synthetic count panel (B)
    B = f"{FX}/B"
    run("view B", [PY, f"{E}/merge_relcensus.py", "view", "--runs", f"{B}/runs/RUN-PFDR-011cd0-table",
                   f"{B}/runs/RUN-PFDR-011cd0-search", "--out", f"{B}/view"], 0)
    os.makedirs(f"{B}/cal")
    run("calibrate B: no structured or planted arm parsed",
        [PY, f"{E}/amd-280481/analyze_relcensus.py", "calibrate", "--runs-dir", f"{B}/view", "--design", f"{B}/design.json",
         "--out", f"{B}/cal", "--reps", "2000"], 0,
        lambda: (lambda al, cal: (not al["structured_or_planted_arm_parsed"]
                                  and set(al["parsed_arms"]) <= {"random_sub_r0", "random_sub_r1", "random_sub_r2",
                                                                 "random_dick_r0", "random_dick_r1", "random_dick_r2",
                                                                 "known_null_sub", "known_null_dick", "known_log"}
                                  and cal["PC_1"]["pass"],
                                  {"parsed_arms": al["parsed_arms"], "t_star": cal["t_star"]["t"],
                                   "t_carry": cal["t_carry"]["t"], "PC_NULL": {k: cal["PC_NULL"][k] for k in ("K_obs", "P_K_null_ge_K_obs", "pass")},
                                   "PC_NULL_ks_p": cal["PC_NULL"]["ks"]["p"], "PC_1": cal["PC_1"]["pass"]}))(
            j(f"{B}/cal/arm-read-log.json"), j(f"{B}/cal/calibration.json")))
    cal_sha = sha(f"{B}/cal/calibration.json")
    os.makedirs(f"{B}/an")
    run("unmask refuses a wrong calibration sha256",
        [PY, f"{E}/amd-280481/analyze_relcensus.py", "unmask", "--runs-dir", f"{B}/view", "--design", f"{B}/design.json",
         "--calibration", f"{B}/cal/calibration.json", "--calibration-sha256", "0" * 64, "--out", f"{B}/an",
         "--gates-ok", "1"], 3)
    run("unmask B: the planted excess (subgroup TT3, kappa 1.5) exceeds t*; planted arm detected; known-null not",
        [PY, f"{E}/amd-280481/analyze_relcensus.py", "unmask", "--runs-dir", f"{B}/view", "--design", f"{B}/design.json",
         "--calibration", f"{B}/cal/calibration.json", "--calibration-sha256", cal_sha, "--out", f"{B}/an",
         "--gates-ok", "1"], 0,
        lambda: (lambda an: ("subgroup|TT3|band" in an["fam1_cells_z_gt_tstar"]
                             and all(not x.startswith("known_null") for x in an["fam1_cells_z_gt_tstar"])
                             and an["PC_R"]["i_pass"] and an["PC_R"]["ii_pass"] and an["PC_R"]["iii"]["pass"]
                             and an["outcome_ids"][0] == "O-CANDIDATE",
                             {"exceed": an["fam1_cells_z_gt_tstar"], "outcomes": an["outcome_ids"],
                              "PC_R": {k: v for k, v in an["PC_R"].items() if k != "iii"} | {"iii_pass": an["PC_R"]["iii"]["pass"]},
                              "kappa_subgroup_TT3": an["A_INT"]["subgroup|TT3|band"]["kappa_rel"],
                              "ci95": an["A_INT"]["subgroup|TT3|band"]["ci95"],
                              "coverage_example": an["A_INT"]["dickson|TT3|band"]["coverage"]}))(j(f"{B}/an/analysis.json")))
    # 6. stage-r on a synthetic stage run built from B (subgroup TT3 curves relabelled to c >= 20000)
    st = f"{B}/runs/RUN-PFDR-011cd0-stage-r"
    os.makedirs(st)
    rows = [json.loads(l) for l in gzip.open(f"{B}/runs/RUN-PFDR-011cd0-table/rows.jsonl.gz", "rt")]
    keep = [dict(r, curve=r["curve"] - 10 + 20000) for r in rows
            if r["m"] == 3 and r["bits"] in (30, 32) and r["arm"] in ("subgroup", "random_sub_r0", "random_sub_r1",
                                                                       "random_sub_r2", "known_null_sub")]
    with gzip.open(f"{st}/rows.jsonl.gz", "wt") as fh:
        for r in keep:
            fh.write(json.dumps(r) + "\n")
    run("view B with stage", [PY, f"{E}/merge_relcensus.py", "view", "--runs", f"{B}/runs/RUN-PFDR-011cd0-table",
                              f"{B}/runs/RUN-PFDR-011cd0-search", st, "--out", f"{B}/view2"], 0)
    run("stage-r calibrate (A not read)", [PY, f"{E}/amd-280481/analyze_relcensus.py", "stage-r", "--runs-dir", f"{B}/view2",
                                          "--analysis", f"{B}/an/analysis.json", "--out", st, "--step", "calibrate",
                                          "--reps", "2000"], 0,
        lambda: (lambda c: (set(c["parsed_arms"]) <= {"random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub"},
                            {k: v["t_R"] for k, v in c["cells"].items()} | {"parsed": c["parsed_arms"]}))(j(f"{st}/stage-calibration.json")))
    run("stage-r unmask: O-ALIVE-CANDIDATE on the planted cell (TW-ALIVE path)",
        [PY, f"{E}/amd-280481/analyze_relcensus.py", "stage-r", "--runs-dir", f"{B}/view2", "--analysis", f"{B}/an/analysis.json",
         "--out", st, "--step", "unmask", "--calibration-sha256", sha(f"{st}/stage-calibration.json")], 0,
        lambda: (lambda r: (any(o.startswith("O-ALIVE-CANDIDATE:subgroup|TT3") for o in r["outcome_ids"]),
                            r["outcome_ids"]))(j(f"{st}/analysis.json")))
    met = sum(1 for x in LOG if x["expectation_met"])
    json.dump({"what": "EXP-PFDR-011cd0 pre-pin fixture exercise", "fx": FX, "steps": LOG,
               "steps_total": len(LOG), "steps_expectation_met": met}, open(a.log, "w"), indent=1)
    print(f"{met}/{len(LOG)} expectations met")
    return 0 if met == len(LOG) else 1


if __name__ == "__main__":
    raise SystemExit(main())
