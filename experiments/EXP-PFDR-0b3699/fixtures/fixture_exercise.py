"""EXP-PFDR-0b3699 synthetic fixtures and fixture exercise (TASK-20261002-8a6b8a).

    <PY> experiments/EXP-PFDR-0b3699/fixtures/fixture_exercise.py

Fixture tooling, not an experiment script: it reads NO real data of this experiment and no
EXP-PFDR-011cd0 file.  It builds, under experiments/EXP-PFDR-0b3699/fixtures/:

  archived/   a synthetic stand-in for the EXP-PFDR-011cd0 P0 inputs at 20 and 22 bits
              (census jobs of the SUB family run with the engine, and calibration.json /
              analysis.json / design.json / localise / sizing / red-team files whose integer
              targets are computed here from the HARVESTER's in-process counts, so P0X-A checks
              analyze_a.py's independent recount against them);
  out/        the four scripts run end to end on a small fresh design (20 and 22 bits):
              design_a.py -> analyze_a.py p0 -> census jobs -> run_jobs.py merge ->
              analyze_a.py checks -> calibrate -> unmask; plus reproduce_check.py;
  defects     duplicated keys (merge must flag them), a planted vector absent on one curve
              (PC-R-iii must FAIL for exactly that instance), a mutated census row
              (reproduce_check.py must FAIL naming the key);
  known sizes a known-null arm (its CC-8 cell must equal the harvester's total) and a planted
              excess of known size (C_planted_sub - C_planted_target must equal the number of
              used curves outside S, exactly).

Writes exercise-log.json (every command, exit code, expectation and verdict).  Exit 0 iff
every expectation holds.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

REPO = "/home/user/crypto-autoresearcher"
EXPDIR = "experiments/EXP-PFDR-0b3699"
FX = os.environ.get("FIXTURE_DIR", f"{EXPDIR}/fixtures")  # development runs use a scratch copy
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
BITS = [20, 22]
ARCH_CURVES = list(range(10, 16))
SUB_FAMILY = ["subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub"]
NULL = ["random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub"]
LOG: list = []
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def A(p):
    return os.path.join(REPO, p)


def sha256(p):
    return hashlib.sha256(open(A(p), "rb").read()).hexdigest()


def run(name, cmd, expect_exit, check=None):
    t = time.time()
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, env=ENV)
    rec = {"step": name, "command": " ".join(cmd), "exit_code": r.returncode,
           "expected_exit": expect_exit, "seconds": round(time.time() - t, 2),
           "stdout_tail": r.stdout[-1500:], "stderr_tail": r.stderr[-1500:]}
    ok = r.returncode == expect_exit if expect_exit is not None else True
    if check is not None:
        try:
            res = check()
            rec["check"] = res
            ok = ok and bool(res.get("ok"))
        except Exception as exc:  # recorded, the exercise fails
            rec["check"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            ok = False
    rec["verdict"] = "PASS" if ok else "FAIL"
    LOG.append(rec)
    print(f"[{rec['verdict']}] {name} (exit {r.returncode}, expected {expect_exit})", flush=True)
    return r


def read_jsonl(p):
    with gzip.open(A(p), "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def write_gz(p, recs):
    with open(A(p)[:-3], "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    subprocess.run(["gzip", "-n", "-f", A(p)[:-3]], check=True)


def census(jd, bits, c0, k, arms):
    os.makedirs(A(jd), exist_ok=True)
    cmd = [PY, "-m", "crypto_autoresearcher.index_calculus", "census", "--panel", "main", "--m", "4",
           "--bits", str(bits), "--curve-offset", str(c0), "--curves", str(k), "--modes", "table",
           "--arms", *arms, "--known-log-max-bits", "0", "--retain", "all", "--relcount",
           "--instance-watchdog", "1800", "--bases-out", f"{jd}/bases.jsonl", "--bases-sample-mod", "10",
           "--workers", "1", "--out", f"{jd}/rows.jsonl", "--rows-out", f"{jd}/harvest-rows.jsonl",
           "--staircase-out", f"{jd}/staircase.jsonl", "--quiet"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, env=ENV)
    for f in ("rows.jsonl", "harvest-rows.jsonl", "staircase.jsonl", "bases.jsonl"):
        if os.path.exists(A(f"{jd}/{f}")):
            subprocess.run(["gzip", "-n", A(f"{jd}/{f}")], check=True)
    return r.returncode


def build_archived():
    base = f"{FX}/archived"
    rows_all = []
    for b in BITS:
        jd = f"{base}/jobs/4-b{b}-c{ARCH_CURVES[0]}"
        census(jd, b, ARCH_CURVES[0], len(ARCH_CURVES), SUB_FAMILY)
        rows_all += read_jsonl(f"{jd}/rows.jsonl.gz")
    n = {}
    for r in rows_all:
        n[(r["bits"], r["curve"], r["arm"])] = r["harvest"]["TT"]["at_stop"]["relations_nonformal"]
    three_CR = six_s2 = CA = 0
    groups = []
    for b in BITS:
        mj = []
        for c in ARCH_CURVES:
            v = [n[(b, c, a)] for a in NULL[:3]]
            three_CR += sum(v)
            six_s2 += 3 * sum(x * x for x in v) - sum(v) ** 2
            CA += n[(b, c, "known_null_sub")]
            mj.append(sum(v) / 3 + 0.05)
        groups.append({"key": ["SUB", "TT", 4, b], "curves": ARCH_CURVES, "mj": mj,
                       "D": 1.05 if b == BITS[0] else 1.1, "log2N": [0.0] * len(ARCH_CURVES), "masks": {}})
    cal = {"generators": {"G-NB-R": {"groups": groups}},
           "PC_NULL": {"known_null_band_cells": {"known_null_sub|TT4|band": {
               "C_A": float(CA), "C_R": three_CR / 3 + 1e-12, "sum_s2": six_s2 / 6 + 1e-12,
               "V": max(six_s2 / 6, three_CR / 3), "curves_used": len(BITS) * len(ARCH_CURVES)}}}}
    json.dump(cal, open(A(f"{base}/calibration.json"), "w"), indent=1)
    curves = []
    for r in rows_all:
        if r["arm"] == "random_sub_r0":
            curves.append({"bits": r["bits"], "curve": r["curve"], "p": r["p"], "a": r["a"], "b": r["b"],
                           "N": r["N"], "sizes": {"4": {"s_sub": r["fb_size"]}}})
    json.dump({"curves": curves}, open(A(f"{base}/design.json"), "w"), indent=1)
    json.dump({"A_INT": {"small_x|TT4|band": {"SE": 0.05, "q": {"q_one_sided_095": 2.0},
                                              "upper95_one_sided": 1.2, "kappa_rel": 1.1}}},
              open(A(f"{base}/analysis.json"), "w"), indent=1)
    loc = {f"small_x|{b}": {"C_R": sum(n[(b, c, a)] for c in ARCH_CURVES for a in NULL[:3]) / 3,
                            "curves": len(ARCH_CURVES)} for b in BITS}
    json.dump(loc, open(A(f"{base}/localise.json"), "w"), indent=1)
    json.dump({"cells": {"small_x|TT4|band": {"curves_power0.8_at_1.100_alpha_0.01_single_test": 1,
                                              "curves_power0.9_at_1.100_alpha_0.01_single_test": 2}}},
              open(A(f"{base}/sizing.json"), "w"), indent=1)
    open(A(f"{base}/red-team.yaml"), "w").write(
        "red_team_report:\n  joints:\n    J4:\n      computation:\n        d_dispersion: fixture text\n")
    return {"3xC_R": three_CR, "6xsum_s2": six_s2, "C_A": CA}


def main() -> int:
    for d in ("archived", "out"):
        if os.path.exists(A(f"{FX}/{d}")):
            print(f"refusing: {FX}/{d} exists (fixtures are built once)", file=sys.stderr)
            return 3
    t0 = time.time()
    arch_ints = build_archived()
    LOG.append({"step": "build synthetic archived inputs", "harvester_integer_targets": arch_ints,
                "verdict": "PASS"})
    out = f"{FX}/out"
    os.makedirs(A(out))
    # design_a
    run("design_a.py on fixture rungs 20, 22 (c0 2010, 16 per rung)",
        [PY, f"{EXPDIR}/design_a.py", "--bits", "20", "22", "--c0", "2010", "--n-per-rung", "16",
         "--workers", "2", "--out", f"{out}/curves.jsonl.gz"], 0,
        lambda: {"ok": len(read_jsonl(f"{out}/curves.jsonl.gz")) == 32})
    # p0 (design stops are possible at toy bits; the exit code is recorded, the files must exist)
    p0 = f"{out}/p0"
    arch = f"{FX}/archived"
    run("analyze_a.py p0 --fixture (P0X-A vs harvester integers, G-FRESH, sizing, S, jobs)",
        [PY, f"{EXPDIR}/analyze_a.py", "p0", "--curves", f"{out}/curves.jsonl.gz", "--out-dir", p0,
         "--rungs", "20", "22", "--c0", "2010", "--declared-n", "8", "--arch-jobs", f"{arch}/jobs",
         "--arch-calibration", f"{arch}/calibration.json", "--arch-analysis", f"{arch}/analysis.json",
         "--arch-design", f"{arch}/design.json", "--localise", f"{arch}/localise.json",
         "--sizing", f"{arch}/sizing.json", "--redteam", f"{arch}/red-team.yaml",
         "--reps", "2000", "--designs", "50", "--fixture"], None,
        lambda: (lambda r, d: {"ok": r["pass"] and all(v["equal"] for v in r["integer_pairs"].values())
                               and d["G-FRESH"]["pass"] and len(d["jobs"]) == 2,
                               "p0x_a_pairs": r["integer_pairs"], "design_stop": d["design_stop"],
                               "final_n_b": d["final_n_b"], "S": d["S"]})(
            json.load(open(A(f"{p0}/p0x-a-report.json"))), json.load(open(A(f"{p0}/design.json")))))
    design = json.load(open(A(f"{p0}/design.json")))
    # census jobs of the fixture design (the RA-04 command template of run_jobs.py)
    spec = importlib.util.spec_from_file_location("rj", A(f"{EXPDIR}/run_jobs.py"))
    rj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rj)
    tab = f"{out}/table"
    for j in design["jobs"]:
        jd = f"{tab}/attempt-1/jobs/{j['job']}"
        os.makedirs(A(jd))
        cmd = rj.table_command(j, jd)
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, env=ENV)
        open(A(f"{jd}/stdout.log"), "w").write(r.stdout)
        for f in ("rows.jsonl", "harvest-rows.jsonl", "staircase.jsonl", "bases.jsonl"):
            subprocess.run(["gzip", "-n", A(f"{jd}/{f}")], check=True)
        LOG.append({"step": f"census job {j['job']} (run_jobs.table_command)", "exit_code": r.returncode,
                    "summary_ar1_keys": rj.parse_job_summary(A(jd)),
                    "verdict": "PASS" if r.returncode == 0 else "FAIL"})
    run("run_jobs.py merge (clean)",
        [PY, f"{EXPDIR}/run_jobs.py", "merge", "--run-dir", tab, "--run-id", "FIXTURE-table",
         "--design", f"{p0}/design.json"], 0,
        lambda: (lambda m: {"ok": m["keys_with_exactly_one_canonical_row"] and not m["missing_keys"]
                            and "canonical_staircase_records" not in m})(
            json.load(open(A(f"{tab}/merge-report.json")))))
    run("analyze_a.py checks (clean table: every check passes)",
        [PY, f"{EXPDIR}/analyze_a.py", "checks", "--run-dir", tab, "--design", f"{p0}/design.json"], 0,
        lambda: (lambda c, v: {"ok": c["pass"] and v["pass"] and "rows_checked" not in v
                               and "failure_count" not in v,
                               "checks": {k: x["pass"] for k, x in c["checks"].items()}})(
            json.load(open(A(f"{tab}/checks-report.json"))), json.load(open(A(f"{tab}/row-verify.json")))))
    # defect: duplicated keys
    dup = f"{out}/table-dup"
    j0 = design["jobs"][0]["job"]
    shutil.copytree(A(f"{tab}/attempt-1/jobs/{j0}"), A(f"{dup}/attempt-1/jobs/{j0}"))
    rr = read_jsonl(f"{dup}/attempt-1/jobs/{j0}/rows.jsonl.gz")
    os.remove(A(f"{dup}/attempt-1/jobs/{j0}/rows.jsonl.gz"))
    write_gz(f"{dup}/attempt-1/jobs/{j0}/rows.jsonl.gz", rr + rr[:1])
    run("run_jobs.py merge (duplicated key must be flagged; other rung missing)",
        [PY, f"{EXPDIR}/run_jobs.py", "merge", "--run-dir", dup, "--run-id", "FIXTURE-dup",
         "--design", f"{p0}/design.json"], 1,
        lambda: (lambda m: {"ok": len(m["duplicate_rows_within_attempt"]) == 1
                            and not m["keys_with_exactly_one_canonical_row"],
                            "duplicates": m["duplicate_rows_within_attempt"]})(
            json.load(open(A(f"{dup}/merge-report.json")))))
    # defect: planted vector absent on one curve
    nop = f"{out}/table-noplant"
    shutil.copytree(A(f"{tab}/attempt-1"), A(f"{nop}/attempt-1"))
    jd = f"{nop}/attempt-1/jobs/{j0}"
    rows = read_jsonl(f"{jd}/rows.jsonl.gz")
    target = next(r for r in rows if r["arm"] == "planted_sub")
    N = target["N"]
    tt = [x for x in target["fb_params"]["planted_relations"] if x["class"] == "TT"][0]
    pv = sorted((i, s % N) for i, s in zip(tt["indices"], tt["signs"]))
    hr = read_jsonl(f"{jd}/harvest-rows.jsonl.gz")

    def is_planted_row(h):
        if not (h["arm"] == "planted_sub" and h["curve"] == target["curve"] and h["class"] == "TT"):
            return False
        v = sorted((i, c % N) for i, c in h["coeffs"] if c % N)
        if not v:
            return False
        inv = pow(v[0][1], -1, N)
        return [(i, c * inv % N) for i, c in v] == pv
    kept = [h for h in hr if not is_planted_row(h)]
    os.remove(A(f"{jd}/harvest-rows.jsonl.gz"))
    write_gz(f"{jd}/harvest-rows.jsonl.gz", kept)
    run("run_jobs.py merge (planted-vector-absent copy)",
        [PY, f"{EXPDIR}/run_jobs.py", "merge", "--run-dir", nop, "--run-id", "FIXTURE-noplant",
         "--design", f"{p0}/design.json"], 0)
    key = json.dumps([target["bits"], target["curve"], 4, "planted_sub", "table"])
    run("analyze_a.py checks (planted vector absent on one curve: PC-R-iii FAIL there only)",
        [PY, f"{EXPDIR}/analyze_a.py", "checks", "--run-dir", nop, "--design", f"{p0}/design.json"], 1,
        lambda: (lambda c: {"ok": (not c["checks"]["PC-R-iii"]["pass"])
                            and c["per_instance"][key]["PC-R-iii"] == "FAIL"
                            and sum(1 for v in c["per_instance"].values() if v.get("PC-R-iii") == "FAIL") == 1,
                            "removed_rows": len(hr) - len(kept),
                            "mismatch_keys": c["checks"]["PC-R-iii"]["mismatch_keys"]})(
            json.load(open(A(f"{nop}/checks-report.json")))))
    # calibrate and unmask on the clean fixture table
    cal_dir = f"{out}/calibrate"
    run("analyze_a.py calibrate --fixture (null arms only; arm-read-log)",
        [PY, f"{EXPDIR}/analyze_a.py", "calibrate", "--table-dir", tab, "--design", f"{p0}/design.json",
         "--out-dir", cal_dir, "--reps", "2000", "--designs", "50", "--fixture"], 0,
        lambda: (lambda lg: {"ok": all(set(f["parsed_lines_by_arm"]) <= set(NULL) for f in lg["files"])
                             and any(f["structured_lines_skipped_unparsed"] for f in lg["files"])})(
            json.load(open(A(f"{cal_dir}/arm-read-log.json")))))
    csha = sha256(f"{cal_dir}/calibration.json")
    ana_dir = f"{out}/analysis"
    run("analyze_a.py unmask refuses a wrong calibration sha256",
        [PY, f"{EXPDIR}/analyze_a.py", "unmask", "--table-dir", tab, "--design", f"{p0}/design.json",
         "--calibration", f"{cal_dir}/calibration.json", "--calibration-sha256", "0" * 64,
         "--out-dir", f"{out}/analysis-refused", "--reps", "2000", "--fixture"], 1,
        lambda: {"ok": not os.path.exists(A(f"{out}/analysis-refused"))})

    def check_unmask():
        an = json.load(open(A(f"{ana_dir}/analysis.json")))
        rows_t = read_jsonl(f"{tab}/rows.jsonl.gz")
        used = {(r["bits"], r["curve"]) for r in json.load(open(A(f"{cal_dir}/calibration.json")))["null_table"]}
        harv = {}
        for r in rows_t:
            if (r["bits"], r["curve"]) in used:
                harv[r["arm"]] = harv.get(r["arm"], 0) + r["harvest"]["TT"]["at_stop"]["relations_nonformal"]
        S = {(int(b), c) for b, cs in design["S"].items() for c in cs}
        outside = sum(1 for k in used if k not in S)
        cps = an["cells"]["planted_sub"]["C_X"]
        cpt = an["cells"]["planted_target"]["C_X"]
        vm5 = {f["path"]: f["sha256"] for f in json.load(open(A(f"{cal_dir}/view-map.json")))["files"]}
        vm6 = {f["path"]: f["sha256"] for f in json.load(open(A(f"{ana_dir}/view-map.json")))["files"]}
        agree = all(vm6[p] == h for p, h in vm5.items() if p in vm6)
        return {"ok": cps == harv["planted_sub"] and an["cells"]["known_null_sub"]["C_X"] == harv["known_null_sub"]
                and cps - cpt == outside and agree and an["outcome_id"].split()[0] in
                ("O-A-INVALID", "O-A-UNCAL", "O-A1", "O-A1b", "O-A2", "O-A3", "O-A4"),
                "known_null_C_X": an["cells"]["known_null_sub"]["C_X"], "harvester_known_null": harv["known_null_sub"],
                "planted_excess_known_size": {"C_planted_sub_minus_C_planted_target": cps - cpt,
                                              "used_curves_outside_S": outside},
                "view_maps_agree": agree, "outcome_id_fixture": an["outcome_id"]}
    run("analyze_a.py unmask --fixture (known-null arm, planted excess of known size, view-maps)",
        [PY, f"{EXPDIR}/analyze_a.py", "unmask", "--table-dir", tab, "--design", f"{p0}/design.json",
         "--calibration", f"{cal_dir}/calibration.json", "--calibration-sha256", csha,
         "--gate-report", f"{tab}/checks-report.json", "--gate-report", f"{tab}/row-verify.json",
         "--gate-report", f"{p0}/p0x-a-report.json",
         "--out-dir", ana_dir, "--reps", "2000", "--fixture"], 0, check_unmask)
    # reproduce_check: identical copy passes; a mutated census row fails naming its key
    rc = f"{out}/repro"
    src = f"{arch}/jobs/4-b20-c10"
    shutil.copytree(A(src), A(f"{rc}/same"))
    shutil.copytree(A(src), A(f"{rc}/mutated"))
    rr = read_jsonl(f"{rc}/mutated/rows.jsonl.gz")
    rr[3] = dict(rr[3], table_entries=rr[3]["table_entries"] + 1, seconds=rr[3]["seconds"] + 5)
    os.remove(A(f"{rc}/mutated/rows.jsonl.gz"))
    write_gz(f"{rc}/mutated/rows.jsonl.gz", rr)
    run("reproduce_check.py identical job passes",
        [PY, f"{EXPDIR}/reproduce_check.py", "--pair", src, f"{rc}/same", "base",
         "--out", f"{rc}/same-report.json"], 0)
    run("reproduce_check.py mutated row fails (timing key ignored, table_entries named)",
        [PY, f"{EXPDIR}/reproduce_check.py", "--pair", src, f"{rc}/mutated", "base",
         "--out", f"{rc}/mutated-report.json"], 1,
        lambda: (lambda m: {"ok": [x["field"] for x in m["pairs"][0]["mismatches"]] == ["table_entries"],
                            "mismatches": m["pairs"][0]["mismatches"]})(
            json.load(open(A(f"{rc}/mutated-report.json")))))
    # run_jobs.py launcher paths (census-jobs under the wrapper, step, finalize) on the fixture design
    runs = f"{out}/runs"
    ENV["EXP0B3699_RUNS_ROOT"] = runs
    rid = "FIXTURE-RUN"
    rroot = f"{runs}/{rid}"
    run("run_jobs.py census-jobs --kind table (wrapper exec, RLIMIT_AS, gzip -n, AR-1 (2) parse)",
        [PY, f"{EXPDIR}/run_jobs.py", "census-jobs", "--run-id", rid, "--kind", "table",
         "--design", f"{p0}/design.json", "--design-sha256", sha256(f"{p0}/design.json")], 0,
        lambda: {"ok": all(os.path.exists(A(f"{rroot}/attempt-1/jobs/{j['job']}/{f}"))
                           for j in design["jobs"] for f in ("rows.jsonl.gz", "harvest-rows.jsonl.gz",
                                                              "staircase.jsonl.gz", "bases.jsonl.gz",
                                                              "execution.json", "run_wrapper.py"))
                 and "cert_pass" not in open(A(f"{rroot}/stdout.log")).read()})
    run("run_jobs.py step merge",
        [PY, f"{EXPDIR}/run_jobs.py", "step", "--run-id", rid, "--step", "merge", "--",
         PY, f"{EXPDIR}/run_jobs.py", "merge", "--run-dir", rroot, "--run-id", rid,
         "--design", f"{p0}/design.json"], 0,
        lambda: {"ok": os.path.exists(A(f"{rroot}/merge-report.json"))})
    run("run_jobs.py step checks",
        [PY, f"{EXPDIR}/run_jobs.py", "step", "--run-id", rid, "--step", "checks", "--",
         PY, f"{EXPDIR}/analyze_a.py", "checks", "--run-dir", rroot, "--design", f"{p0}/design.json"], 0,
        lambda: {"ok": json.load(open(A(f"{rroot}/checks-report.json")))["pass"]})
    run("run_jobs.py step refuses an existing step directory",
        [PY, f"{EXPDIR}/run_jobs.py", "step", "--run-id", rid, "--step", "checks", "--", PY, "-c", "pass"], 3)

    def check_finalize():
        import yaml
        out_ = {}
        for loc in (rroot, f"{rroot}/attempt-1"):
            man = yaml.safe_load(open(A(f"{loc}/manifest.yaml")))["run"]
            cert = man["result"]["certificate"]
            lines = open(A(f"{loc}/checksums.sha256")).read().split("\n")
            listed = {l.split("  ", 1)[1] for l in lines if l.strip()}
            files = set()
            for r_, _, fs in os.walk(A(loc)):
                for f in fs:
                    files.add(os.path.relpath(os.path.join(r_, f), A(loc)))
            ok_sums = all(hashlib.sha256(open(os.path.join(A(loc), f), "rb").read()).hexdigest() == h
                          for h, f in (l.split("  ", 1) for l in lines if l.strip()))
            out_[loc] = (cert["kind"] == "none" and cert["instances_claimed"] == 0 and cert["instances_verified"] == 0
                         and man["timing"]["started_at"] and man["timing"]["finished_at"]
                         and listed == files - {"checksums.sha256"} and ok_sums
                         and man["inference"]["resolved_model_id"] is None
                         and "Bedrock" not in json.dumps(man["inference"]).replace("Bedrock never selected", ""))
        return {"ok": all(out_.values()), "locations": out_}
    run("run_jobs.py finalize (manifest certificate none/0/0, timing, checksums cover every file)",
        [PY, f"{EXPDIR}/run_jobs.py", "finalize", "--run-id", rid, "--status", "completed_valid",
         "--reason", "fixture", "--gate-report", f"{rroot}/checks-report.json",
         "--completeness", json.dumps({"fixture": True})], 0, check_finalize)
    run("run_jobs.py finalize refuses a second finalize",
        [PY, f"{EXPDIR}/run_jobs.py", "finalize", "--run-id", rid, "--status", "completed_valid",
         "--reason", "fixture"], 3)
    ok = all(r.get("verdict") == "PASS" for r in LOG)
    log = {"what": "EXP-PFDR-0b3699 fixture exercise", "task": "TASK-20261002-8a6b8a",
           "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "seconds": round(time.time() - t0, 1), "pass": ok,
           "scripts_sha256": {f: sha256(f"{EXPDIR}/{f}") for f in
                              ("run_jobs.py", "design_a.py", "analyze_a.py", "reproduce_check.py")}
           | {"fixtures/fixture_exercise.py": sha256(f"{EXPDIR}/fixtures/fixture_exercise.py")},
           "fixture_dir": FX,
           "steps": LOG}
    json.dump(log, open(A(f"{FX}/exercise-log.json"), "w"), indent=1)
    print(json.dumps({"fixture_exercise_pass": ok, "steps": len(LOG)}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
