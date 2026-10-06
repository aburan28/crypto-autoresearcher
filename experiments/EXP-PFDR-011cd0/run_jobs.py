"""EXP-PFDR-011cd0 launcher and manifest writer (EC-9).  TASK-20261001-7f7a33.

Started from a copy of experiments/EXP-PFDR-1b78f7/amd-430f44/run_jobs.py (read-only);
imports NO crypto_autoresearcher module and no other engine module.

Every census JOB is its own process run through the archived wrapper
experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py `exec` (RLIMIT_AS 3.5e9 bytes on the
job process; per-job watchdog = min(21600 s, remaining attempt watchdog)), at most
--max-procs (4) processes at once.  No job starts while MemAvailable < 4 GB, while free
disk < 2.5 GB, or once experiments/EXP-PFDR-011cd0/ exceeds 1.5 GB (TW-DISK: the attempt
checkpoints).  When a job ends, every JSONL of its directory is gzip -n compressed and then
hashed; a file above 95 MB stops further starts.

Subcommands
  jobs              write the job list of R10, R12, R13, R14 or R17 (frozen cells; R12/R13
                    curves from the pinned design.json) as JSON.
  run               launch the jobs of one attempt (RUN_DIR/attempt-N/jobs/<job>/).
  finalize-attempt  raw-result.json, solve-certs + verify_solves (when solves exist),
                    manifest.yaml and checksums.sha256 of an attempt.
  finalize          manifest.yaml + checksums.sha256 for a run root or a frozen-command run
                    directory (needs raw-result.json; reads execution.json when present).

Rows are read for KEYS, STATUS, STATUS_REASON, the k_found/k_verified flags and the G4/G5
certificate counters only.  Nothing here computes or prints a kappa, z, ratio, dispersion or
relation count, and nothing is interpreted.
"""
from __future__ import annotations

import argparse
import datetime as dt
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
EXP = "EXP-PFDR-011cd0"
EXPDIR = f"experiments/{EXP}"
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
SCRATCH = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/7f7a33"
WRAPPER = "experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py"
HERE = os.path.dirname(os.path.abspath(__file__))
TASK = "TASK-20261001-7f7a33"
RSS_CAP = 3_500_000_000
PER_JOB_WATCHDOG = 21600
ATTEMPT_WATCHDOG = 86400
MIN_MEM_AVAIL_GB = 4.0
DISK_FLOOR_GB = 2.5
PACKAGE_GUARD_BYTES = 1.5e9
MAX_FILE_BYTES = 95 * 1024 * 1024

LEGACY_MAIN_ARMS = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
                    "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2"]
ARMS_11 = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
           "known_null_sub", "random_dick_r0", "random_dick_r1", "random_dick_r2",
           "known_null_dick"]
ARMS_12 = ARMS_11 + ["planted_sub"]

PROTOCOL = {
    "version": 1,
    "specification": f"{EXPDIR}/specification.yaml (v1, frozen)",
    "amendments": [],
    "amendments_note": ("none in force: experiments/EXP-PFDR-011cd0/amendments/ holds only .gitkeep; "
                        "contract-touch ruling DEC-20261001-e9e7e6: does not touch, no amendment"),
    "approval_decisions": ["DEC-20261001-56f873"],
    "handoff": TASK,
    "output_archive": "TASK-20261001-b64be7",
}

INFERENCE = {
    "requested_policy": "executor-implementation",
    "runtime": "claude_code",
    "subagent": "executor",
    "backend": "the session's default Anthropic backend (Bedrock never selected, not used)",
    "resolved_model_id": None,
    "model_provenance": "withheld by the session's artifact policy; not probe-verified",
    "model_verified": False,
    "reasoning_effort": "medium (from .claude/agents/executor.md frontmatter; card inference.reasoning_effort null)",
    "fallback_used": False,
    "degraded_requirements": [],
    "note": "the runs are deterministic code; no model is in the measurement loop",
}

PINNED_FILES = [
    "src/crypto_autoresearcher/index_calculus/__init__.py",
    "src/crypto_autoresearcher/index_calculus/__main__.py",
    "src/crypto_autoresearcher/index_calculus/_accel.py",
    "src/crypto_autoresearcher/index_calculus/curve.py",
    "src/crypto_autoresearcher/index_calculus/decompose.py",
    "src/crypto_autoresearcher/index_calculus/factor_base.py",
    "src/crypto_autoresearcher/index_calculus/harvest.py",
    "src/crypto_autoresearcher/index_calculus/linalg.py",
    "src/crypto_autoresearcher/index_calculus/msolve.py",
    "src/crypto_autoresearcher/index_calculus/polyfp.py",
    "src/crypto_autoresearcher/index_calculus/rho.py",
    "src/crypto_autoresearcher/index_calculus/semaev.py",
    "src/crypto_autoresearcher/index_calculus/solver.py",
    "src/crypto_autoresearcher/index_calculus/stats.py",
    "src/crypto_autoresearcher/index_calculus/tails.py",
    "tests/test_index_calculus_fp.py",
    "tests/test_index_calculus_harvest.py",
    "tests/test_index_calculus_relcensus.py",
    "tests/fixtures/harvest_pre_obj5.py",
    f"{EXPDIR}/run_jobs.py",
    f"{EXPDIR}/merge_relcensus.py",
    f"{EXPDIR}/design_curves.py",
    f"{EXPDIR}/analyze_relcensus.py",
    f"{EXPDIR}/verify_solves.py",
    f"{EXPDIR}/verify_rows.py",
    "experiments/EXP-PFDR-1b78f7/compare_regression.py",
    WRAPPER,
]

SEEDS_CENSUS = {
    "curve_seeds": "c (each job's curves; census c >= 10 per design.json; R10: the archived 1b78f7 jobs' c in {0, 1})",
    "target_seed": 0,
    "target_log_rule": "k = random.Random(f'target|{bits}|{c}|0').randrange(1, N) (__main__._instance)",
    "target_label": "census",
    "solver_seed": "c",
    "subgroup_and_dickson_seed": "c",
    "random_seeds": ("random_sub_rK c + 1000K (K = 0, 1, 2); random_dick_rK c + 3000 + 1000K; "
                     "known_null_sub c + 6000; known_null_dick c + 7000; planted_sub c + 8000"),
    "curve_generator": "generate_prime_order_curve(bits, c, p_filter=subgroup_prime_filter([3, 4, 5], 0.15))",
    "other_randomness": "none; every rng in the engine is seeded from the above",
}


# ------------------------------------------------------------------------------------------
# utilities

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wrapper_module():
    """The archived wrapper, loaded for environment() only."""
    return load_module("run_wrapper_amd1de84f", WRAPPER)


def mem_available_bytes() -> int:
    with open("/proc/meminfo") as fh:
        for line in fh:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable not found")


def free_disk_bytes() -> int:
    st = os.statvfs(REPO)
    return st.f_bavail * st.f_frsize


def package_bytes() -> int:
    tot = 0
    for root, _, files in os.walk(os.path.join(REPO, EXPDIR)):
        for f in files:
            try:
                tot += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return tot


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def head_sha(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        return None
    return hashlib.sha256(r.stdout).hexdigest()


def code_block() -> dict:
    sources = {}
    for rel in PINNED_FILES:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            sources[rel] = {"sha256": None, "status": "absent"}
            continue
        dg, hd = sha256(p), head_sha(rel)
        sources[rel] = {"sha256": dg,
                        "status": "untracked" if hd is None else ("clean" if hd == dg else "modified")}
    porcelain = git("status", "--porcelain", "--untracked-files=all", "--", "src", "tests",
                    EXPDIR).splitlines()
    return {"commit": git("rev-parse", "HEAD").strip(),
            "dirty": bool(git("status", "--porcelain", "--untracked-files=no").strip()),
            "dirty_note": ("tracked-tree dirty flag over the whole repository; the engine and test "
                           "edits are uncommitted by design (card NO COMMITS) and pinned by sha256"),
            "status_porcelain_scoped": [l for l in porcelain if "__pycache__" not in l],
            "source_sha256": sources}


def environment_json() -> dict:
    return wrapper_module().environment()


def write_checksums(d: str) -> None:
    lines = []
    for root, dirs, files in os.walk(d):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, d)
            if rel == "checksums.sha256":
                continue
            lines.append(f"{sha256(p)}  {rel}")
    with open(os.path.join(d, "checksums.sha256"), "w") as fh:
        fh.write("\n".join(sorted(lines, key=lambda s: s.split("  ", 1)[1])) + "\n")


def certificate_block(raw: dict) -> dict:
    """Card CERTIFICATE FORMAT.  raw["certificate"] = {"instances_claimed", "instances_verified",
    "verify_report", ...}.  kind discrete_log with verified the boolean true only when every
    claimed solve was re-verified by verify_solves.py; otherwise this raises (no manifest)."""
    rc = raw.get("certificate") or {}
    claimed = int(rc.get("instances_claimed", 0) or 0)
    if claimed == 0:
        out = {"kind": "none", "note": rc.get("note", "no solve is claimed at this location")}
        for k in ("harvested_row_check", "row_verification"):
            if k in rc:
                out[k] = rc[k]
        return out
    ver = int(rc.get("instances_verified", 0) or 0)
    if ver != claimed or not rc.get("verify_pass"):
        raise SystemExit(f"CERTIFICATE FAILURE: {claimed} claimed solves, {ver} verified by "
                         "verify_solves.py; the run is invalid (I-3); no manifest written with verified true")
    out = {"kind": "discrete_log", "verified": True,
           "instances_claimed": claimed, "instances_verified": ver,
           "verifier": "experiments/EXP-PFDR-011cd0/verify_solves.py (G4-D; standard library only)",
           "verifier_sha256": rc.get("verifier_sha256"),
           "certificates_file": rc.get("certificates_file"),
           "certificates_sha256": rc.get("certificates_sha256"),
           "verify_report": rc.get("verify_report")}
    for k in ("harvested_row_check", "row_verification"):
        if k in rc:
            out[k] = rc[k]
    return out


def write_manifest(d: str, *, run_id: str, location_kind: str, status: str, reason: str,
                   completeness: dict, command: str, command_template: str | None = None,
                   job_list: list | None = None, spec_command: str | None = None,
                   timing: dict, resources: dict, inputs: dict, summary: dict, raw: dict,
                   deviations: list | None = None, unexpected: list | None = None,
                   extra: dict | None = None, code: dict | None = None) -> None:
    import yaml

    if os.path.exists(os.path.join(d, "manifest.yaml")):
        raise SystemExit(f"refusing: {d}/manifest.yaml exists (records are immutable)")
    if status not in ("completed_valid", "failed_infrastructure", "invalid"):
        raise SystemExit(f"status {status!r} is not a status value of this contract")
    if not timing.get("started_at") or not timing.get("finished_at"):
        raise SystemExit("started_at and finished_at must be non-null (NA-16)")
    if status != "invalid":
        cert = certificate_block(raw)
    else:  # an invalid run claims nothing; never verified true, never false-and-continue
        rc = raw.get("certificate") or {}
        cert = {"kind": "none",
                "note": "run invalid: no solve or relation is claimed as evidence",
                "solver_determined_k_instances": int(rc.get("instances_claimed", 0) or 0),
                "verify_solves_accepted": int(rc.get("instances_verified", 0) or 0)}
    env = (json.load(open(os.path.join(d, "environment.json")))
           if os.path.exists(os.path.join(d, "environment.json")) else environment_json())
    body = {
        "id": run_id,
        "experiment_id": EXP,
        "task_id": TASK,
        "location_kind": location_kind,
        "location": os.path.relpath(os.path.abspath(d), REPO),
        "protocol": PROTOCOL,
        "status": status,
        "status_vocabulary": "completed_valid | failed_infrastructure | invalid, with completeness",
        "completeness": completeness,
        "validity": {"valid": status == "completed_valid", "reason": reason},
        "code": (code or code_block()) | {"command": command,
                                          "command_template": command_template,
                                          "job_list": job_list,
                                          "spec_command": spec_command,
                                          "interpreter": PY},
        "inference": INFERENCE,
        "environment": {k: v for k, v in env.items() if k != "pip_freeze"}
                       | {"dependencies": "environment.json pip_freeze"},
        "inputs": inputs,
        "timing": timing,
        "resources": resources,
        "result": {"summary": summary, "certificate": cert, "raw_result": "raw-result.json"},
        "deviations": deviations or [],
        "observations_unexpected": unexpected or [],
    }
    if extra:
        body.update(extra)
    files = []
    for root, dirs, fs in os.walk(d):
        for f in fs:
            files.append(os.path.relpath(os.path.join(root, f), d))
    body["artifacts"] = sorted(set(files) | {"manifest.yaml", "checksums.sha256"})
    with open(os.path.join(d, "manifest.yaml"), "w") as fh:
        yaml.safe_dump({"run": body}, fh, sort_keys=False, width=100)
    write_checksums(d)


# ------------------------------------------------------------------------------------------
# job lists (frozen cells)

def _census_base(m: int, bits: int, c0: int, k: int) -> list[str]:
    return [PY, "-m", "crypto_autoresearcher.index_calculus", "census", "--panel", "main",
            "--m", str(m), "--bits", str(bits), "--curve-offset", str(c0), "--curves", str(k)]


def _io(jd: str, rows_out: str | None = None, bases: bool = False, certs: bool = False,
        staircase: bool = True) -> list[str]:
    out = ["--workers", "1", "--out", f"{jd}/rows.jsonl",
           "--rows-out", rows_out or f"{jd}/harvest-rows.jsonl"]
    if staircase:
        out += ["--staircase-out", f"{jd}/staircase.jsonl"]
    if bases:
        out = ["--bases-out", f"{jd}/bases.jsonl", "--bases-sample-mod", "10"] + out
    if certs:
        out = ["--solve-certs", f"{jd}/solve-certs.jsonl"] + out
    return out


def _keys(bits, curves, m, arms, modes):
    return [[bits, c, m, a, md] for c in curves for a in arms for md in modes]


def jobs_r10() -> list[dict]:
    spec = [(m, b, c) for m in (3, 4, 5) for b in range(12, 25, 2) for c in (0, 1)]
    spec += [(3, 32, 0), (4, 26, 0), (5, 32, 0)]
    out = []
    for m, b, c in spec:
        name = f"{m}-b{b:02d}-c{c}"
        klm = 24 if m == 3 else 0
        arms = LEGACY_MAIN_ARMS + (["known_log"] if (m == 3 and b <= klm) else [])
        out.append({"name": name, "m": m, "bits": b, "curve_offset": c, "curves": 1,
                    "args_tail": ["--known-log-max-bits", str(klm), "--relcount"],
                    "certs": True, "bases": False, "rows_to_scratch": True,
                    "expected_keys": _keys(b, [c], m, arms, ["census", "on"])})
    return out


def jobs_from_design(design: dict, panel: str) -> list[dict]:
    """R12 (panel 'table') or R13 (panel 'search') jobs from design.json."""
    out = []
    for j in design["jobs"][panel]:
        m, b, c0, k = j["m"], j["bits"], j["curve_offset"], j["curves"]
        curves = list(range(c0, c0 + k))
        if panel == "table":
            if j.get("pc1"):
                arms, tail = ["known_log"], ["--known-log-max-bits", "24"]
                name = f"{m}-b{b:02d}-c{c0}-known_log"
            else:
                arms = ARMS_12 if m == 3 else ARMS_11
                tail = ["--known-log-max-bits", "0"]
                name = f"{m}-b{b:02d}-c{c0}"
            args = ["--modes", "table", "--arms", *arms] + tail + [
                "--retain", "all", "--relcount", "--instance-watchdog", "1800"]
            out.append({"name": name, "m": m, "bits": b, "curve_offset": c0, "curves": k,
                        "args_tail": args, "certs": False, "bases": True, "rows_to_scratch": False,
                        "expected_keys": _keys(b, curves, m, arms, ["table"])})
        else:
            arms = ARMS_11
            args = ["--modes", "search", "--encoding-budget-lambda", "20", "--arms", *arms,
                    "--known-log-max-bits", "0", "--retain", "all", "--digest-classes", "TT", "TB",
                    "--relcount", "--instance-watchdog", "1800"]
            out.append({"name": f"{m}-b{b:02d}-c{c0}", "m": m, "bits": b, "curve_offset": c0,
                        "curves": k, "args_tail": args, "certs": False, "bases": True,
                        "rows_to_scratch": False,
                        "expected_keys": _keys(b, curves, m, arms, ["search"])})
    return out


def jobs_r14() -> list[dict]:
    out = []
    for m in (3, 4, 5):
        for b in (20, 26):
            for c in range(10, 14):
                args = ["--modes", "census", "--budget-snapshot-only", "--encoding-budget-lambda", "20",
                        "--arms", *ARMS_11, "--known-log-max-bits", "0", "--retain", "xfix",
                        "--digest-classes", "TT", "TB", "--relcount"]
                out.append({"name": f"{m}-b{b:02d}-c{c}", "m": m, "bits": b, "curve_offset": c,
                            "curves": 1, "args_tail": args, "certs": True, "bases": False,
                            "rows_to_scratch": False,
                            "expected_keys": _keys(b, [c], m, ARMS_11, ["census"])})
    return out


def jobs_r17(analysis: dict, design: dict) -> list[dict]:
    """Stage R' (R17): per triggered cell, fresh curves c = 20000 .. 20000 + n - 1 at the cell's
    rungs (30 and 32; 28 for CARRY-1), n = the cell's final n in its panel, arms A, its three
    randoms and its known-null arm, the panel's mode and flags (R12 / R13)."""
    fam_r = {"SUB": ["random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub"],
             "DICK": ["random_dick_r0", "random_dick_r1", "random_dick_r2", "known_null_dick"]}
    fam_of = {"subgroup": "SUB", "small_x": "SUB", "dickson": "DICK"}
    want: dict = {}
    trig = []
    for cid in analysis["fam1_cells_z_gt_tstar"]:
        arm, cm, _ = cid.split("|")
        trig.append((arm, cm[:2], int(cm[2:]), [30, 32]))
    if analysis["CARRY_1"]["z_gt_t_carry"]:
        trig.append(("subgroup", "TT", 3, [28]))
    for arm, cls, m, rungs in trig:
        panel = "search" if cls == "SS" else "table"
        for b in rungs:
            k = (panel, m, b)
            want.setdefault(k, set()).update([arm] + fam_r[fam_of[arm]])
    order = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
             "known_null_sub", "random_dick_r0", "random_dick_r1", "random_dick_r2", "known_null_dick"]
    out = []
    for (panel, m, b), arms in sorted(want.items()):
        arms = [x for x in order if x in arms]
        n = design["final_n"][panel][str(m)][str(b)]
        blk = 100 if panel == "table" else 10
        for c0 in range(20000, 20000 + n, blk):
            k = min(blk, 20000 + n - c0)
            curves = list(range(c0, c0 + k))
            if panel == "table":
                args = ["--modes", "table", "--arms", *arms, "--known-log-max-bits", "0", "--retain", "all",
                        "--relcount", "--instance-watchdog", "1800"]
                modes = ["table"]
            else:
                args = ["--modes", "search", "--encoding-budget-lambda", "20", "--arms", *arms,
                        "--known-log-max-bits", "0", "--retain", "all", "--digest-classes", "TT", "TB",
                        "--relcount", "--instance-watchdog", "1800"]
                modes = ["search"]
            out.append({"name": f"{panel[0]}{m}-b{b:02d}-c{c0}", "m": m, "bits": b, "curve_offset": c0,
                        "curves": k, "args_tail": args, "certs": False, "bases": True,
                        "rows_to_scratch": False, "expected_keys": _keys(b, curves, m, arms, modes)})
    return out


def job_command(job: dict, jd: str) -> list[str]:
    if job.get("dummy"):
        return [PY, os.path.join(HERE, "fixtures", "dummy_job.py"), "--job-dir", jd,
                "--behaviour", job.get("behaviour", "ok"), "--keys", json.dumps(job["expected_keys"])]
    rows_out = None
    if job.get("rows_to_scratch"):
        rows_out = os.path.join(SCRATCH, "r10-harvest-rows", job["name"], "harvest-rows.jsonl")
    return (_census_base(job["m"], job["bits"], job["curve_offset"], job["curves"])
            + job["args_tail"] + _io(jd, rows_out, bases=job["bases"], certs=job["certs"]))


def cmd_jobs(a) -> int:
    if a.run == "R10":
        jobs = jobs_r10()
    elif a.run in ("R12", "R13"):
        design = json.load(open(a.design))
        if a.design_sha256 and sha256(a.design) != a.design_sha256:
            print("refusing: design.json does not match the pinned sha256", file=sys.stderr)
            return 3
        jobs = jobs_from_design(design, "table" if a.run == "R12" else "search")
    elif a.run == "R14":
        jobs = jobs_r14()
    elif a.run == "R17":
        jobs = jobs_r17(json.load(open(a.analysis)), json.load(open(a.design)))
    else:
        print(f"no job list for {a.run}", file=sys.stderr)
        return 2
    with open(a.out, "w") as fh:
        json.dump({"run": a.run, "created_at": now(), "launcher_sha256": sha256(__file__),
                   "design": a.design, "design_sha256": sha256(a.design) if a.design else None,
                   "jobs": jobs}, fh, indent=1)
    print(f"{len(jobs)} jobs, {sum(len(j['expected_keys']) for j in jobs)} expected instance keys")
    return 0


# ------------------------------------------------------------------------------------------
# run

def read_status_fields(path: str) -> list[dict]:
    keep = ("panel", "method", "m", "bits", "curve", "arm", "mode", "status", "status_reason",
            "k_found", "k_verified")
    out = []
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                d = {k: r.get(k) for k in keep if k in r}
                h = r.get("harvest")
                if h:  # G4 / G5 counters only
                    d["g4"] = all(h[c]["at_stop"]["cert_fail"] == 0 and
                                  h[c]["at_stop"]["cert_pass"] == h[c]["at_stop"]["rows_emitted"]
                                  for c in ("TT", "TB", "SS"))
                    d["g5"] = bool(h["ss_store"]["identity_ok"])
                    d["rows_emitted"] = sum(h[c]["at_stop"]["rows_emitted"] for c in ("TT", "TB", "SS"))
                checks = r.get("checks") or {}
                d["checks_failed"] = sorted(k for k, v in checks.items() if v is False)
                out.append(d)
    return out


def key_of(r: dict) -> list:
    m = r.get("m")
    if m is None and str(r.get("method", "")).startswith("ic_m"):
        m = int(r["method"][4:])
    return [r.get("bits"), r.get("curve"), m, r.get("arm"), r.get("mode")]


class Log:
    def __init__(self, d: str):
        self.out = open(os.path.join(d, "stdout.log"), "a")
        self.err = open(os.path.join(d, "stderr.log"), "a")

    def __call__(self, msg: str, err: bool = False) -> None:
        line = f"[{now()}] {msg}"
        print(line, file=sys.stderr if err else sys.stdout, flush=True)
        fh = self.err if err else self.out
        fh.write(line + "\n")
        fh.flush()


def postprocess_job(jobdir: str, scratch_rows: str | None) -> tuple[dict, list]:
    """gzip -n each JSONL after the job ends, then hash every file of the job directory."""
    for name in sorted(os.listdir(jobdir)):
        if name.endswith(".jsonl"):
            subprocess.run(["gzip", "-n", os.path.join(jobdir, name)], check=True)
    if scratch_rows and os.path.exists(scratch_rows):
        subprocess.run(["gzip", "-n", scratch_rows], check=True)
    files = {os.path.relpath(os.path.join(r, f), jobdir): sha256(os.path.join(r, f))
             for r, _, fs in os.walk(jobdir) for f in sorted(fs)}
    big = [f for f in files if os.path.getsize(os.path.join(jobdir, f)) > MAX_FILE_BYTES]
    return files, big


def cmd_run(a) -> int:
    ad = a.attempt_dir if os.path.isabs(a.attempt_dir) else os.path.join(REPO, a.attempt_dir)
    jobs_parent = os.path.join(ad, "jobs")
    if os.path.exists(os.path.join(ad, "jobs-index.json")) or os.path.exists(jobs_parent):
        print(f"refusing: {ad} already holds jobs-index.json or jobs/", file=sys.stderr)
        return 3
    spec = json.load(open(a.jobs_file))
    jobs = spec["jobs"]
    if a.only:
        keep = set(a.only.split(","))
        jobs = [j for j in jobs if j["name"] in keep]
    if a.dummy:
        beh = json.loads(a.dummy_behaviour_json) if a.dummy_behaviour_json else {}
        jobs = [dict(j, dummy=True, behaviour=beh.get(j["name"], "ok")) for j in jobs]
    names = [j["name"] for j in jobs]
    if len(set(names)) != len(names):
        print("duplicate job names", file=sys.stderr)
        return 2
    os.makedirs(jobs_parent)
    with open(os.path.join(ad, "jobs-spec.json"), "w") as fh:  # this attempt's jobs only
        json.dump(dict(spec, jobs=jobs, source_jobs_file=os.path.abspath(a.jobs_file),
                       source_jobs_file_sha256=sha256(a.jobs_file), only=a.only), fh, indent=1)
    log = Log(ad)
    order = sorted(jobs, key=lambda j: (-j["bits"], j["m"], j["curve_offset"], j["name"]))
    with open(os.path.join(ad, "command.txt"), "w") as fh:
        fh.write(" ".join([PY, os.path.relpath(os.path.abspath(__file__), REPO)] + sys.argv[1:]) + "\n")
        fh.write(f"# each job runs through: {PY} {WRAPPER} exec --run-dir <jobdir> --run-id {a.run_id} "
                 f"--exp {EXP} --spec-command <frozen> --watchdog <min({PER_JOB_WATCHDOG}, remaining "
                 f"attempt watchdog)> --rss-cap-bytes {RSS_CAP} -- <job command>\n")
        if a.spec_command:
            fh.write(f"# frozen specification command of the run: {a.spec_command}\n")
        fh.write(f"# job commands: jobs-index.json (command per job); job list: jobs-spec.json\n")
        fh.write(f"# cwd: {REPO}\n")
    with open(os.path.join(ad, "environment.json"), "w") as fh:
        json.dump(environment_json(), fh, indent=2, sort_keys=True)
    pins = code_block()
    log(f"attempt {os.path.relpath(ad, REPO)}: {len(order)} jobs, max {a.max_procs} processes, "
        f"attempt watchdog {a.watchdog} s, per-job {PER_JOB_WATCHDOG} s, MemAvailable gate "
        f"{MIN_MEM_AVAIL_GB} GB, disk floor {DISK_FLOOR_GB} GB, package guard {PACKAGE_GUARD_BYTES} B; "
        f"trigger: {a.trigger}")
    t_start = time.time()
    started_at = now()
    deadline = t_start + a.watchdog
    pending = list(order)
    running: dict = {}
    index: list[dict] = []
    run_stop = None
    checkpoint = None
    mem_waits = 0
    while pending or running:
        for name in list(running):
            job = running[name]
            if job["proc"].poll() is None:
                continue
            del running[name]
            rec = job["rec"]
            rec["ended_at"] = now()
            rec["wrapper_exit_code"] = job["proc"].returncode
            exf = os.path.join(job["dir"], "execution.json")
            if os.path.exists(exf):
                ex = json.load(open(exf))
                rec.update({"exit_code": ex["exit_code"],
                            "signal": -ex["exit_code"] if ex["exit_code"] < 0 else None,
                            "watchdog_expired": ex["watchdog_expired"],
                            "wall_seconds": ex["wall_seconds"],
                            "peak_rss_bytes": ex["peak_rss_bytes_max_descendant"],
                            "cpu_seconds": ex["cpu_seconds_descendants"]})
            else:
                rec.update({"exit_code": None, "signal": None, "watchdog_expired": None,
                            "note": "wrapper wrote no execution.json"})
            scratch_rows = job["scratch_rows"]
            rec["files_sha256"], big = postprocess_job(job["dir"], scratch_rows)
            if scratch_rows:
                sp = scratch_rows + ".gz"
                rec["scratch_harvest_rows"] = {"path": sp, "sha256": sha256(sp) if os.path.exists(sp) else None}
            rp = os.path.join(job["dir"], "rows.jsonl.gz")
            rows = read_status_fields(rp) if os.path.exists(rp) else []
            got = [key_of(r) for r in rows]
            exp = {json.dumps(k) for k in job["expected"]}
            gotj = [json.dumps(k) for k in got]
            st: dict = {}
            for r in rows:
                st[r.get("status")] = st.get(r.get("status"), 0) + 1
            rec["rows_written"] = len(rows)
            rec["status_counts"] = st
            rec["expected_keys"] = len(exp)
            rec["missing_keys"] = sorted(exp - set(gotj))
            rec["duplicate_keys"] = sorted({k for k in gotj if gotj.count(k) > 1})
            rec["non_job_keys"] = sorted(set(gotj) - exp)
            rec["invalid_instances"] = [[*key_of(r), r.get("status_reason")] for r in rows
                                        if r.get("status") == "invalid"]
            rec["failed_infrastructure_instances"] = [[*key_of(r), r.get("status_reason")] for r in rows
                                                      if r.get("status") == "failed_infrastructure"]
            rec["g4_fail_instances"] = [key_of(r) for r in rows if r.get("g4") is False]
            rec["g5_fail_instances"] = [key_of(r) for r in rows if r.get("g5") is False]
            rec["checks_failed_instances"] = [[*key_of(r), r["checks_failed"]] for r in rows if r.get("checks_failed")]
            rec["solved_instances"] = sum(1 for r in rows if r.get("k_found") and r.get("k_verified"))
            rec["files_above_95MB"] = big
            rec["abnormal_end"] = (not rows) or (rec.get("exit_code") not in (0, 1)) or bool(rec.get("watchdog_expired"))
            index.append(rec)
            log(f"job {name} ended: exit {rec.get('exit_code')} rows {len(rows)} statuses {st} "
                f"missing {len(rec['missing_keys'])} wall {rec.get('wall_seconds')} s "
                f"peak_rss {rec.get('peak_rss_bytes')} abnormal {rec['abnormal_end']}")
            if (rec["invalid_instances"] or rec["g4_fail_instances"] or rec["g5_fail_instances"]
                    or rec["checks_failed_instances"]) and run_stop is None:
                run_stop = name
                log(f"RUN STOP: job {name} has an invalid instance or a gate failure; no further job "
                    f"starts (certificate/gate failure stops the run; rows retained)", err=True)
            if big and checkpoint is None:
                checkpoint = f"file above 95 MB in job {name}: {big}"
                log(f"CHECKPOINT: {checkpoint}; no further job starts", err=True)
        while pending and len(running) < a.max_procs and run_stop is None and checkpoint is None:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            pb = package_bytes()
            if pb > PACKAGE_GUARD_BYTES:
                checkpoint = f"TW-DISK: {EXPDIR} holds {pb} bytes > {PACKAGE_GUARD_BYTES}"
                log(f"CHECKPOINT: {checkpoint}; no further job starts", err=True)
                break
            fd = free_disk_bytes()
            ma = mem_available_bytes()
            if ma < MIN_MEM_AVAIL_GB * 1e9 or fd < DISK_FLOOR_GB * 1e9:
                mem_waits += 1
                if mem_waits % 20 == 1:
                    log(f"MemAvailable {ma} B / free disk {fd} B below the gate; waiting before "
                        f"starting {pending[0]['name']}")
                if fd < DISK_FLOOR_GB * 1e9 and not running:
                    checkpoint = f"TW-DISK: free disk {fd} B below {DISK_FLOOR_GB} GB with nothing running"
                    log(f"CHECKPOINT: {checkpoint}", err=True)
                break
            job = pending.pop(0)
            name = job["name"]
            jd = os.path.join(jobs_parent, name)
            jd_rel = os.path.relpath(jd, REPO)
            scratch_rows = None
            if job.get("rows_to_scratch") and not job.get("dummy"):
                scratch_rows = os.path.join(SCRATCH, "r10-harvest-rows", name, "harvest-rows.jsonl")
                if os.path.exists(os.path.dirname(scratch_rows)):
                    log(f"refusing to reuse scratch dir {os.path.dirname(scratch_rows)}", err=True)
                    return 3
                os.makedirs(os.path.dirname(scratch_rows))
            cmd = job_command(job, jd_rel)
            wd = max(1.0, min(PER_JOB_WATCHDOG, remaining))
            wcmd = [PY, os.path.join(REPO, WRAPPER), "exec", "--run-dir", jd, "--run-id", a.run_id,
                    "--exp", EXP, "--spec-command", a.spec_command or "", "--watchdog", f"{wd:.1f}",
                    "--rss-cap-bytes", str(RSS_CAP), "--"] + cmd
            rec = {"job": name, "m": job["m"], "bits": job["bits"], "curve_offset": job["curve_offset"],
                   "curves": job["curves"], "command": cmd, "wrapper_command": wcmd, "job_dir": jd_rel,
                   "started_at": now(), "watchdog_seconds": round(wd, 1),
                   "mem_available_at_start_bytes": ma, "free_disk_at_start_bytes": fd,
                   "package_bytes_at_start": pb}
            proc = subprocess.Popen(wcmd, cwd=REPO, stdout=subprocess.DEVNULL,
                                    stderr=open(os.path.join(ad, "wrapper-stderr.log"), "a"))
            running[name] = {"proc": proc, "rec": rec, "dir": jd, "expected": job["expected_keys"],
                             "scratch_rows": scratch_rows}
            log(f"job {name} started (pid {proc.pid}; watchdog {rec['watchdog_seconds']} s)")
        if not running and pending and (run_stop is not None or checkpoint is not None
                                         or deadline - time.time() <= 0):
            break
        time.sleep(a.poll)
    not_started = [j["name"] for j in pending]
    why = ("not_started_after_run_stop" if run_stop is not None else
           "not_started_checkpoint" if checkpoint is not None else
           "not_started_attempt_watchdog" if not_started else None)
    wall = time.time() - t_start
    idx = {"run_id": a.run_id, "attempt_dir": os.path.relpath(ad, REPO), "trigger": a.trigger,
           "started_at": started_at, "finished_at": now(), "wall_seconds": round(wall, 3),
           "attempt_watchdog_seconds": a.watchdog, "per_job_watchdog_seconds": PER_JOB_WATCHDOG,
           "max_procs": a.max_procs, "min_mem_avail_gb": MIN_MEM_AVAIL_GB,
           "disk_floor_gb": DISK_FLOOR_GB, "package_guard_bytes": PACKAGE_GUARD_BYTES,
           "mem_gate_wait_polls": mem_waits, "rlimit_as_bytes_per_job_process": RSS_CAP,
           "dummy": bool(a.dummy), "run_stop_at_job": run_stop, "checkpoint": checkpoint,
           "not_started": not_started, "not_started_reason": why,
           "launcher_sha256": sha256(os.path.abspath(__file__)),
           "jobs_spec_sha256": sha256(os.path.join(ad, "jobs-spec.json")),
           "code_at_launch": pins,
           "jobs": sorted(index, key=lambda r: (-r["bits"], r["m"], r["curve_offset"], r["job"]))}
    with open(os.path.join(ad, "jobs-index.json"), "w") as fh:
        json.dump(idx, fh, indent=1)
    log(f"attempt done: {len(index)} jobs ended, not started {len(not_started)} ({why}); wall {wall:.1f} s")
    return 0


# ------------------------------------------------------------------------------------------
# finalize

def concat_certs(paths: list[str], out: str) -> int:
    """Concatenate solve-certs files (gzip -n), records sorted by key; returns the count."""
    recs = []
    for p in paths:
        with gzip.open(p, "rt") as fh:
            recs.extend(l for l in fh if l.strip())
    recs.sort(key=lambda l: json.dumps(json.loads(l)["key"], sort_keys=True))
    tmp = out[:-3] if out.endswith(".gz") else out
    with open(tmp, "w") as fh:
        fh.writelines(recs)
    subprocess.run(["gzip", "-n", tmp], check=True)
    return len(recs)


def run_verify_solves(d: str, certs_gz: str, allow_empty: bool) -> dict:
    out = os.path.join(d, "solve-verify.json")
    cmd = [PY, os.path.join(HERE, "verify_solves.py"), certs_gz, "--out", out]
    if allow_empty:
        cmd.append("--allow-empty")
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    with open(os.path.join(d, "stdout.log"), "a") as fh:
        fh.write(f"[{now()}] $ {' '.join(cmd)}\n{r.stdout}{r.stderr}[exit {r.returncode}]\n")
    rep = json.load(open(out))
    return {"instances_claimed": rep["records"], "instances_verified": rep["verified"],
            "verify_pass": bool(rep["pass"]), "verify_report": os.path.relpath(out, REPO),
            "verifier_sha256": rep["verifier_sha256"],
            "certificates_file": os.path.relpath(certs_gz, REPO),
            "certificates_sha256": rep["certificates_sha256"], "exit_code": r.returncode}


def finalize_attempt(ad: str, run_id: str, location_kind: str, spec_command: str | None,
                     inputs_extra: dict | None = None) -> int:
    idx = json.load(open(os.path.join(ad, "jobs-index.json")))
    jobs = idx["jobs"]
    exp_total = sum(j["expected_keys"] for j in jobs)
    missing = sum(len(j["missing_keys"]) for j in jobs)
    status_totals: dict = {}
    for j in jobs:
        for k, v in j["status_counts"].items():
            status_totals[str(k)] = status_totals.get(str(k), 0) + v
    cert_files = sorted(os.path.join(REPO, j["job_dir"], "solve-certs.jsonl.gz") for j in jobs
                        if os.path.exists(os.path.join(REPO, j["job_dir"], "solve-certs.jsonl.gz")))
    solved_rows = sum(j.get("solved_instances", 0) for j in jobs)
    certificate = {"instances_claimed": 0, "note": "no solve is claimed at this location"}
    if cert_files:
        cg = os.path.join(ad, "solve-certs.jsonl.gz")
        n = concat_certs(cert_files, cg)
        vs = run_verify_solves(ad, cg, allow_empty=(n == 0))
        certificate = vs | {"solved_rows": solved_rows,
                            "certificates_equal_solved_rows": vs["instances_claimed"] == solved_rows}
        if n == 0:
            certificate["instances_claimed"] = 0
            certificate["note"] = "certificate files present but empty: no instance determined k"
    raw = {"run_id": run_id, "location": os.path.relpath(ad, REPO), "dummy": idx["dummy"],
           "jobs_ended": len(jobs), "not_started": idx["not_started"],
           "not_started_reason": idx["not_started_reason"], "run_stop_at_job": idx["run_stop_at_job"],
           "checkpoint": idx["checkpoint"],
           "completeness": {"expected_keys": exp_total, "keys_missing": missing,
                            "keys_with_row": exp_total - missing,
                            "duplicate_keys": sum(len(j["duplicate_keys"]) for j in jobs),
                            "non_job_keys": sum(len(j["non_job_keys"]) for j in jobs)},
           "status_totals": status_totals,
           "gates": {"G4_fail_instances": [k for j in jobs for k in j["g4_fail_instances"]],
                     "G5_fail_instances": [k for j in jobs for k in j["g5_fail_instances"]],
                     "checks_failed_instances": [k for j in jobs for k in j["checks_failed_instances"]]},
           "invalid_instances": [k for j in jobs for k in j["invalid_instances"]],
           "failed_infrastructure_instances": [k for j in jobs for k in j["failed_infrastructure_instances"]],
           "abnormal_job_ends": [j["job"] for j in jobs if j.get("abnormal_end")],
           "files_above_95MB": {j["job"]: j["files_above_95MB"] for j in jobs if j["files_above_95MB"]},
           "certificate": certificate,
           "jobs_index_sha256": sha256(os.path.join(ad, "jobs-index.json"))}
    with open(os.path.join(ad, "raw-result.json"), "w") as fh:
        json.dump(raw, fh, indent=1)
    gates_bad = any(raw["gates"].values())
    cert_bad = bool(cert_files) and bool(certificate["instances_claimed"]) and not certificate.get("verify_pass")
    if raw["invalid_instances"] or idx["run_stop_at_job"] or gates_bad or cert_bad or \
            (cert_files and not certificate.get("certificates_equal_solved_rows", True)):
        status, reason = "invalid", ("an instance is invalid, a gate failed or a solve certificate "
                                     "failed (I-3/I-4); rows retained")
    elif missing or idx["not_started"] or raw["abnormal_job_ends"] or idx["checkpoint"]:
        status = "failed_infrastructure"
        reason = (f"attempt incomplete: {missing} expected keys without a row; not started "
                  f"{len(idx['not_started'])} ({idx['not_started_reason']}); abnormal job ends "
                  f"{raw['abnormal_job_ends']}; checkpoint {idx['checkpoint']}")
    else:
        status = "completed_valid"
        reason = ("every expected key of the attempt's jobs has exactly one row, no row is invalid and "
                  "no gate failed; instance-level failed_infrastructure rows are allowed and listed")
    started = min((j["started_at"] for j in jobs), default=idx["started_at"])
    ended = max((j.get("ended_at") or "" for j in jobs), default=idx["finished_at"])
    write_manifest(
        ad, run_id=run_id, location_kind=location_kind, status=status, reason=reason,
        completeness=raw["completeness"] | {"jobs_ended": len(jobs), "jobs_not_started": len(idx["not_started"])},
        command=open(os.path.join(ad, "command.txt")).read().splitlines()[0],
        command_template="per-job commands in jobs-index.json (field 'command'), from jobs-spec.json",
        job_list=[j["job"] for j in jobs] + [f"{n} (not started)" for n in idx["not_started"]],
        spec_command=spec_command,
        timing={"started_at": idx["started_at"], "finished_at": idx["finished_at"],
                "first_job_started_at": started, "last_job_ended_at": ended,
                "wall_seconds": idx["wall_seconds"], "timing_source": "run_jobs.py (jobs-index.json)"},
        resources={"peak_rss_bytes_max_job_process": max((j.get("peak_rss_bytes") or 0 for j in jobs), default=0),
                   "cpu_seconds_sum_job_processes": round(sum(j.get("cpu_seconds") or 0 for j in jobs), 3),
                   "wall_seconds": idx["wall_seconds"],
                   "rlimit_as_bytes_per_job_process": RSS_CAP,
                   "attempt_watchdog_seconds": idx["attempt_watchdog_seconds"],
                   "per_job_watchdog_seconds": PER_JOB_WATCHDOG,
                   "max_concurrent_job_processes": idx["max_procs"],
                   "min_mem_available_gate_gb": MIN_MEM_AVAIL_GB, "disk_floor_gb": DISK_FLOOR_GB,
                   "package_guard_bytes": PACKAGE_GUARD_BYTES,
                   "watchdog_expired_jobs": [j["job"] for j in jobs if j.get("watchdog_expired")]},
        inputs={"cells": "jobs-spec.json (expected keys per job)", "seeds": SEEDS_CENSUS} | (inputs_extra or {}),
        summary={"status_totals": status_totals, "jobs_ended": len(jobs),
                 "not_started": idx["not_started"], "run_stop_at_job": idx["run_stop_at_job"],
                 "checkpoint": idx["checkpoint"], "dummy": idx["dummy"]},
        raw=raw)
    print(f"finalized {os.path.relpath(ad, REPO)}: {status}")
    return 0


def cmd_finalize_attempt(a) -> int:
    ad = a.attempt_dir if os.path.isabs(a.attempt_dir) else os.path.join(REPO, a.attempt_dir)
    extra = json.load(open(a.inputs_json)) if a.inputs_json else None
    return finalize_attempt(ad, a.run_id, a.location_kind, a.spec_command, extra)


def cmd_finalize(a) -> int:
    """Manifest for a run root (after merge) or a frozen-command directory (run_wrapper exec)."""
    import yaml

    d = a.dir if os.path.isabs(a.dir) else os.path.join(REPO, a.dir)
    raw = json.load(open(os.path.join(d, "raw-result.json")))
    extra = yaml.safe_load(open(a.extra)) if a.extra else {}
    code = code_block()
    exf = os.path.join(d, "execution.json")
    if os.path.exists(exf):
        ex = json.load(open(exf))
        code["source_sha256_at_exec"] = ex["source_sha256"]
        code["git_at_exec"] = ex["git"]
        command = " ".join(ex["command"])
        timing = {"started_at": ex["started_at"], "finished_at": extra.get("finished_at") or now(),
                  "exec_finished_at": ex["finished_at"], "wall_seconds": ex["wall_seconds"],
                  "timing_source": "run_wrapper.py execution.json (finished_at: after post-processing)"}
        resources = {"peak_rss_bytes_max_descendant": ex["peak_rss_bytes_max_descendant"],
                     "cpu_seconds_descendants": ex["cpu_seconds_descendants"],
                     "rlimit_as_bytes_per_process": ex["rlimit_as_bytes_per_process"],
                     "watchdog_seconds": ex["watchdog_seconds"], "watchdog_expired": ex["watchdog_expired"],
                     "exit_code": ex["exit_code"]}
        spec_command = ex.get("spec_command")
    else:
        command = extra.get("command", "")
        timing = extra["timing"]
        resources = extra.get("resources", {})
        spec_command = extra.get("spec_command")
    post = (json.load(open(os.path.join(d, "post-processing.json")))
            if os.path.exists(os.path.join(d, "post-processing.json")) else [])
    write_manifest(
        d, run_id=a.run_id, location_kind=a.location_kind, status=a.status, reason=a.reason,
        completeness=extra.get("completeness", {}), command=command,
        command_template=extra.get("command_template"), job_list=extra.get("job_list"),
        spec_command=spec_command, timing=timing, resources=resources,
        inputs=extra.get("inputs", {}), summary=extra.get("summary", {}) | {"post_processing": post},
        raw=raw, deviations=extra.get("deviations"), unexpected=extra.get("unexpected"),
        extra=extra.get("extra"), code=code)
    print(f"finalized {os.path.relpath(d, REPO)}: {a.status}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs")
    j.add_argument("--run", required=True, choices=("R10", "R12", "R13", "R14", "R17"))
    j.add_argument("--analysis", default=None, help="R16 analysis.json (R17 only)")
    j.add_argument("--design", default=None)
    j.add_argument("--design-sha256", default=None)
    j.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run-id", required=True)
    r.add_argument("--attempt-dir", required=True)
    r.add_argument("--jobs-file", required=True)
    r.add_argument("--only", default=None, help="comma-separated job names (resume attempts)")
    r.add_argument("--spec-command", default="")
    r.add_argument("--trigger", required=True)
    r.add_argument("--watchdog", type=float, default=ATTEMPT_WATCHDOG)
    r.add_argument("--max-procs", type=int, default=4)
    r.add_argument("--poll", type=float, default=2.0)
    r.add_argument("--dummy", action="store_true", help="pre-pin exercise: dummy commands, no solver")
    r.add_argument("--dummy-behaviour-json", default=None)
    f2 = sub.add_parser("finalize-attempt")
    f2.add_argument("--attempt-dir", required=True)
    f2.add_argument("--run-id", required=True)
    f2.add_argument("--location-kind", default="attempt")
    f2.add_argument("--spec-command", default="")
    f2.add_argument("--inputs-json", default=None)
    f = sub.add_parser("finalize")
    f.add_argument("--dir", required=True)
    f.add_argument("--run-id", required=True)
    f.add_argument("--location-kind", default="run_root")
    f.add_argument("--status", required=True)
    f.add_argument("--reason", required=True)
    f.add_argument("--extra", default=None)
    a = ap.parse_args()
    if a.cmd == "run" and a.max_procs > 4:
        print("refusing: at most 4 job processes (machine protection)", file=sys.stderr)
        return 2
    return {"jobs": cmd_jobs, "run": cmd_run, "finalize-attempt": cmd_finalize_attempt,
            "finalize": cmd_finalize}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
