"""Per-job launcher (AMD-20260929-430f44 M-1, "PJ") for EXP-PFDR-1b78f7, protocol v3.

TASK-20260929-89c123.  New harness code; imports NO crypto_autoresearcher module.
It runs each census JOB -- one (panel, m, bits, curve) of `cells`, or under M-4 one
(job, arm) -- as its own process through the archived wrapper
experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py `exec` (RLIMIT_AS 3.5e9 bytes on the
job process; per-job watchdog = the remaining per-attempt watchdog), at most
--max-procs processes at once, never starting a job while host MemAvailable is below
--min-mem-avail-gb, in descending bits, then m, then curve (the frozen cmd_census sort).

Subcommands
  run       launch the jobs of one attempt; writes <attempt>/<jobs-subdir>/<job>/ (M-1 layout),
            jobs-index.json, command.txt, environment.json, stdout.log, stderr.log; with
            --finalize also raw-result.json (merge_census.py summarize), manifest.yaml and
            checksums.sha256.
  finalize-attempt   the same finalisation for an attempt run earlier with --no-finalize.
  finalize  manifest.yaml + checksums.sha256 for a directory produced by run_wrapper.py exec
            (a frozen-command run root: R13, R15).

Every job's rows are read for KEYS, STATUS and STATUS_REASON only (run-stop rule, M-4
trigger, completeness).  Nothing here computes or prints a kappa, rank, ratio, exponent,
Poisson or floor value, and nothing is interpreted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

REPO = "/home/user/crypto-autoresearcher"
EXP = "EXP-PFDR-1b78f7"
EXPDIR = f"experiments/{EXP}"
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
WRAPPER = f"{EXPDIR}/amd-1de84f/run_wrapper.py"
SUMMARIZE = f"{EXPDIR}/amd-1de84f/summarize_run.py"
HERE = os.path.dirname(os.path.abspath(__file__))
TASK = "TASK-20260929-89c123"
RSS_CAP = 3_500_000_000

MAIN_ARMS = ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
             "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2")
J0_ARMS = ("j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2")
MODES = ("census", "on")

PROTOCOL = {
    "version": 3,
    "specification": f"{EXPDIR}/specification.yaml (v1, frozen)",
    "amendments": [
        f"AMD-20260929-1de84f ({EXPDIR}/amendments/AMD-20260929-1de84f.yaml; v2)",
        f"AMD-20260929-430f44 ({EXPDIR}/amendments/AMD-20260929-430f44.yaml; v3)"],
    "approval_decisions": ["DEC-20260928-ab2d31", "DEC-20260929-523aab", "DEC-20260929-bb40ce"],
    "handoff": TASK,
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

SEEDS = {
    "curve_seeds": "c (the job's curve)",
    "target_seed": 0,
    "target_log_rule": "k = random.Random(f'target|{bits}|{c}|0').randrange(1, N) (main: __main__._instance; j0: _instance_j0, AMD-20260929-1de84f C-5)",
    "target_label": "census",
    "solver_seed": "c",
    "subgroup_and_dickson_seed": "c",
    "random_seeds_main": "random_sub_r0..2: c, c+1000, c+2000; random_dick_r0..2: c+3000, c+4000, c+5000",
    "random_seeds_j0": "j0_random_r0..2: c, c+1000, c+2000",
    "rho_seed": "c",
    "j0_curve_rule": "generate_prime_order_curve_j0 with the AMD-20260929-1de84f C-1 prime rule; exclusion set recomputed from c' = 0 in every job",
    "other_randomness": "none; every rng in the engine is seeded from the above (specification replication.seeds)",
}


# ------------------------------------------------------------------------------------------
# small utilities

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
    """The archived wrapper, loaded for its environment() and pinned_sources() only."""
    return load_module("run_wrapper_amd1de84f", WRAPPER)


def mem_available_bytes() -> int:
    with open("/proc/meminfo") as fh:
        for line in fh:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable not found")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def code_block() -> dict:
    wr = wrapper_module()
    sources = wr.pinned_sources()
    for rel in (f"{EXPDIR}/amd-430f44/run_jobs.py", f"{EXPDIR}/amd-430f44/merge_census.py"):
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            sources[rel] = {"sha256": sha256(p), "status": "untracked" if wr.head_sha(rel) is None
                            else ("clean" if wr.head_sha(rel) == sha256(p) else "modified")}
    porcelain = git("status", "--porcelain", "--untracked-files=all", "--", "src", "tests",
                    f":(glob){EXPDIR}/*.py", f":(glob){EXPDIR}/*.yaml",
                    f"{EXPDIR}/amd-1de84f", f"{EXPDIR}/amd-430f44").splitlines()
    return {"commit": git("rev-parse", "HEAD").strip(),
            "dirty": bool(git("status", "--porcelain", "--untracked-files=no").strip()),
            "dirty_note": ("tracked-tree dirty flag over the whole repository; "
                           "status_porcelain_scoped lists the code-relevant paths"),
            "status_porcelain_scoped": porcelain,
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
    """Manifest certificate from a raw-result certificate (summarize_run.py or merge_census.py
    summarize).  Card CERTIFICATE FORMAT: `verified` is the boolean true and only when every
    claimed solve has k_verified true; the counts go in instances_claimed/instances_verified.
    A failed verification raises: no manifest is written with verified true in that case."""
    rc = raw.get("certificate") or {}
    claimed = int(rc.get("solved_instances", rc.get("instances_claimed", 0)) or 0)
    ver = rc.get("instances_verified", rc.get("verified", 0))
    ver = int(ver or 0) if not isinstance(ver, bool) else (claimed if ver else 0)
    if claimed == 0:
        out = {"kind": "none",
               "note": rc.get("note", "no solve is claimed by the rows at this location")}
        if "harvested_row_check" in rc:
            out["harvested_row_check"] = rc["harvested_row_check"]
        return out
    if ver != claimed:
        raise SystemExit(f"CERTIFICATE FAILURE: {claimed} claimed solves, {ver} verified; "
                         "the run is invalid (I-3); no manifest written")
    out = {"kind": "discrete_log", "verified": True,
           "instances_claimed": claimed, "instances_verified": ver,
           "verifier": rc.get("verifier", "kP == Q by curve.py scalar multiplication")}
    if "harvested_row_check" in rc:
        out["harvested_row_check"] = rc["harvested_row_check"]
        out["harvested_row_check_note"] = rc.get("harvested_row_check_note")
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
        raise SystemExit(f"status {status!r} is not an M-7 status value")
    cert = certificate_block(raw)
    env = environment_json() if not os.path.exists(os.path.join(d, "environment.json")) \
        else json.load(open(os.path.join(d, "environment.json")))
    body = {
        "id": run_id,
        "experiment_id": EXP,
        "task_id": TASK,
        "location_kind": location_kind,
        "location": os.path.relpath(os.path.abspath(d), REPO),
        "protocol": PROTOCOL,
        "status": status,
        "status_vocabulary": "AMD-20260929-430f44 M-7 (completed_valid | failed_infrastructure | invalid) + completeness",
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
        "result": {"summary": summary, "certificate": cert,
                   "raw_result": "raw-result.json"},
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


def inputs_block(panel: str, m: int | None, bits: list, curves: list, arms: list,
                 known_log_max_bits: int | None, rho_curves: int | None) -> dict:
    cells = {"panel": panel, "m": m, "bits": bits, "curves": curves, "arms": arms,
             "modes": list(MODES) if panel != "rho" else None,
             "known_log_max_bits": known_log_max_bits, "rho_curves": rho_curves}
    if panel == "main":
        cells["A_fix"] = "s_sub = max(4, len(F_sub)) for every arm of the job"
        cells["known_log"] = "a cell only at m = 3 and bits <= 24 (not a cell here)" if m != 3 else "m = 3, bits <= K"
        cells["curve_generator"] = "generate_prime_order_curve(bits, c, p_filter=subgroup_prime_filter([3, 4, 5], 0.15))"
    elif panel == "j0":
        cells["A_fix"] = "s = len(F_coset)"
        cells["curve_generator"] = "generate_prime_order_curve_j0(bits, c, p_filter=j0_filter) with AMD-20260929-1de84f C-1"
        cells["rho"] = "pollard_rho(E, P, Q, seed=c) on the same curve (one per job)"
    else:
        cells["curve_generator"] = "main-panel curves; pollard_rho(E, P, Q, seed=c)"
    return {"cells": cells, "seeds": SEEDS,
            "instance_watchdog_seconds": "7200 (census default; no --instance-watchdog passed)"}


# ------------------------------------------------------------------------------------------
# jobs

def job_name(bits: int, c: int, arm: str | None = None, m: int | None = None) -> str:
    """b<BB>-c<C>[-<arm>]; with a per-job m (R16): m<M>-b<BB>-c<C>; a '+'-joined frozen
    --arms list (R16) adds no suffix."""
    return ((f"m{m}-" if m is not None else "") + f"b{bits:02d}-c{c}"
            + (f"-{arm}" if arm and "+" not in arm else ""))


def parse_jobs(spec: str) -> list[tuple]:
    """'b24-c1,b22-c0'; per-arm (M-4) 'b24-c1:subgroup'; R16 'm3-b28-c5:subgroup+random_sub_r0+...'
    (per-job m and the frozen --arms list).  Returns (bits, curve, arm_or_list, m) tuples."""
    out = []
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        arm = None
        if ":" in tok:
            tok, arm = tok.split(":", 1)
        parts = tok.split("-")
        m = None
        if parts[0].startswith("m"):
            m = int(parts[0][1:])
            parts = parts[1:]
        b, c = parts
        out.append((int(b[1:]), int(c[1:]), arm, m))
    return out


def job_arms(arm: str | None) -> list[str] | None:
    return arm.split("+") if arm else None


def job_command(a, bits: int, c: int, arm: str | None, jobdir_rel: str, m: int | None = None) -> list[str]:
    mm = m if m is not None else a.m
    if a.dummy:
        return [PY, os.path.join(HERE, "fixture-check", "dummy_job.py"), "--bits", str(bits),
                "--curve", str(c), "--m", str(mm if mm is not None else 3), "--panel", a.panel,
                "--behaviour", a.dummy_behaviour.get(job_name(bits, c, arm, m), "ok"),
                "--out", f"{jobdir_rel}/rows.jsonl", "--rows-out", f"{jobdir_rel}/harvest-rows.jsonl",
                "--staircase-out", f"{jobdir_rel}/staircase.jsonl"] + (["--arm", arm] if arm else [])
    base = [PY, "-m", "crypto_autoresearcher.index_calculus", "census"]
    if a.panel == "main":
        cmd = base + ["--panel", "main", "--m", str(mm), "--bits", str(bits), "--curve-offset", str(c),
                      "--curves", "1", "--known-log-max-bits", str(a.known_log_max_bits)]
        if arm:
            cmd += ["--arms", *job_arms(arm)]
        cmd += ["--workers", "1", "--out", f"{jobdir_rel}/rows.jsonl",
                "--rows-out", f"{jobdir_rel}/harvest-rows.jsonl",
                "--staircase-out", f"{jobdir_rel}/staircase.jsonl"]
    elif a.panel == "j0":
        cmd = base + ["--panel", "j0", "--m", "3", "--bits", str(bits), "--curve-offset", str(c),
                      "--curves", "1", "--rho-curves", str(a.rho_curves), "--workers", "1",
                      "--out", f"{jobdir_rel}/rows.jsonl", "--rows-out", f"{jobdir_rel}/harvest-rows.jsonl",
                      "--staircase-out", f"{jobdir_rel}/staircase.jsonl"]
    else:
        cmd = base + ["--panel", "rho", "--bits", str(bits), "--curve-offset", str(c),
                      "--rho-curves", "1", "--workers", "1", "--out", f"{jobdir_rel}/rows.jsonl"]
    return cmd


def command_template(a) -> str:
    if a.panel == "main":
        return (f"{PY} -m crypto_autoresearcher.index_calculus census --panel main --m "
                f"{a.m if a.m is not None else '<m>'} --bits <B> "
                f"--curve-offset <c> --curves 1 --known-log-max-bits {a.known_log_max_bits}"
                + (" --arms <arm list>" if a.per_arm else "")
                + " --workers 1 --out <jobdir>/rows.jsonl --rows-out <jobdir>/harvest-rows.jsonl "
                  "--staircase-out <jobdir>/staircase.jsonl")
    if a.panel == "j0":
        return (f"{PY} -m crypto_autoresearcher.index_calculus census --panel j0 --m 3 --bits <B> "
                f"--curve-offset <c> --curves 1 --rho-curves {a.rho_curves} --workers 1 --out "
                "<jobdir>/rows.jsonl --rows-out <jobdir>/harvest-rows.jsonl --staircase-out "
                "<jobdir>/staircase.jsonl")
    return (f"{PY} -m crypto_autoresearcher.index_calculus census --panel rho --bits <B> "
            "--curve-offset <c> --rho-curves 1 --workers 1 --out <jobdir>/rows.jsonl")


def read_status_fields(path: str) -> list[dict]:
    """Rows of a job file, reduced to key, status and status_reason fields."""
    keep = ("panel", "method", "m", "bits", "curve", "arm", "mode", "status", "status_reason")
    out = []
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out.append({k: r.get(k) for k in keep if k in r})
    return out


def row_m(r: dict):
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


def expected_job_keys(a, bits: int, c: int, arm: str | None, m: int | None = None) -> list[tuple]:
    if a.panel == "rho":
        return [("rho", "rho", bits, c)]
    arms = job_arms(arm) if arm else list(MAIN_ARMS if a.panel == "main" else J0_ARMS)
    m = (m if m is not None else a.m) if a.panel == "main" else 3
    keys = [(a.panel, m, bits, c, x, md) for x in arms for md in MODES]
    if a.panel == "j0" and not arm and c < (a.rho_curves or 0):
        keys.append(("j0", "rho", bits, c))
    return keys


def key_of(r: dict) -> tuple:
    if r.get("method") == "rho" or r.get("panel") == "rho":
        return (r.get("panel"), "rho", r.get("bits"), r.get("curve"))
    return (r.get("panel"), row_m(r), r.get("bits"), r.get("curve"), r.get("arm"), r.get("mode"))


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


def postprocess_job(jobdir: str) -> dict:
    """gzip -n each JSONL after the job ends, then hash every file of the job directory."""
    for name in ("rows.jsonl", "harvest-rows.jsonl", "staircase.jsonl"):
        p = os.path.join(jobdir, name)
        if os.path.exists(p):
            subprocess.run(["gzip", "-n", p], check=True)
    return {os.path.relpath(os.path.join(r, f), jobdir): sha256(os.path.join(r, f))
            for r, _, fs in os.walk(jobdir) for f in sorted(fs)}


def cmd_run(a) -> int:
    ad = os.path.join(REPO, a.attempt_dir) if not os.path.isabs(a.attempt_dir) else a.attempt_dir
    jobs_parent = os.path.join(ad, a.jobs_subdir) if a.jobs_subdir else ad
    if os.path.exists(os.path.join(ad, "jobs-index.json")) or os.path.exists(os.path.join(ad, "manifest.yaml")):
        print(f"refusing: {ad} already holds jobs-index.json or manifest.yaml", file=sys.stderr)
        return 3
    if a.jobs_subdir and os.path.exists(jobs_parent):
        print(f"refusing: {jobs_parent} exists", file=sys.stderr)
        return 3
    os.makedirs(jobs_parent, exist_ok=True)
    a.dummy_behaviour = json.loads(a.dummy_behaviour_json) if a.dummy_behaviour_json else {}
    a.per_arm = any(j[2] for j in parse_jobs(a.jobs))
    log = Log(ad)
    jobs = parse_jobs(a.jobs)
    order = sorted(jobs, key=lambda j: (-j[0], j[3] if j[3] is not None else 0, j[1],
                                        MAIN_ARMS.index(j[2]) if j[2] in MAIN_ARMS else -1))
    if len(set(order)) != len(order):
        log("duplicate job in --jobs", err=True)
        return 2
    tmpl = command_template(a)
    with open(os.path.join(ad, "command.txt"), "w") as fh:
        fh.write(" ".join([PY, os.path.relpath(os.path.abspath(__file__), REPO)] + sys.argv[1:]) + "\n")
        fh.write(f"# per-job command template (AMD-20260929-430f44 M-1): {tmpl}\n")
        fh.write(f"# each job runs through: {PY} {WRAPPER} exec --run-dir <jobdir> --run-id {a.run_id} "
                 f"--exp {EXP} --spec-command <frozen> --watchdog <remaining attempt watchdog> "
                 f"--rss-cap-bytes {RSS_CAP} -- <job command>\n")
        if a.spec_command:
            fh.write(f"# frozen specification command of the run: {a.spec_command}\n")
        fh.write(f"# jobs (execution order): {','.join(job_name(*j) for j in order)}\n")
        fh.write(f"# cwd: {REPO}\n")
    with open(os.path.join(ad, "environment.json"), "w") as fh:
        json.dump(environment_json(), fh, indent=2, sort_keys=True)
    pins = code_block()
    log(f"attempt {a.attempt_dir}: {len(order)} jobs, max {a.max_procs} processes, "
        f"watchdog {a.watchdog} s, MemAvailable gate {a.min_mem_avail_gb} GB, trigger: {a.trigger}")
    t_start = time.time()
    started_at = now()
    deadline = t_start + a.watchdog
    pending = list(order)
    running: dict = {}
    index: list[dict] = []
    run_stop = None
    mem_waits = 0
    while pending or running:
        # reap
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
            rec["files_sha256"] = postprocess_job(job["dir"])
            rp = os.path.join(job["dir"], "rows.jsonl.gz")
            rows = read_status_fields(rp) if os.path.exists(rp) else []
            got = [key_of(r) for r in rows]
            exp = set(job["expected"])
            st = {}
            for r in rows:
                st[r.get("status")] = st.get(r.get("status"), 0) + 1
            rec["rows_written"] = len(rows)
            rec["status_counts"] = st
            rec["expected_keys"] = len(exp)
            rec["missing_keys"] = [list(k) for k in sorted(exp - set(got), key=str)]
            rec["non_job_keys"] = [list(k) for k in got if k not in exp]
            rec["address_space_cap_instances"] = [list(key_of(r)) for r in rows
                                                  if str(r.get("status_reason") or "").startswith("address-space cap:")]
            rec["invalid_instances"] = [[*key_of(r), r.get("status_reason")] for r in rows
                                        if r.get("status") == "invalid"]
            rec["abnormal_end"] = (not rows) or (rec.get("exit_code") not in (0, 1)) or bool(rec.get("watchdog_expired"))
            rec["m4_trigger"] = bool(rec["address_space_cap_instances"]) or rec["abnormal_end"]
            index.append(rec)
            log(f"job {name} ended: exit {rec.get('exit_code')} rows {len(rows)} statuses {st} "
                f"wall {rec.get('wall_seconds')} s peak_rss {rec.get('peak_rss_bytes')} "
                f"abnormal {rec['abnormal_end']} m4_trigger {rec['m4_trigger']}")
            if rec["invalid_instances"] and run_stop is None:
                run_stop = name
                log(f"RUN STOP (M-1 run_stop_rule): job {name} has an invalid instance; "
                    f"no further job starts", err=True)
        # start
        while pending and len(running) < a.max_procs and run_stop is None:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            ma = mem_available_bytes()
            if ma < a.min_mem_avail_gb * 1e9:
                mem_waits += 1
                if mem_waits % 20 == 1:
                    log(f"MemAvailable {ma} B below {a.min_mem_avail_gb} GB; waiting before starting "
                        f"{job_name(*pending[0])}")
                break
            bits, c, arm, jm = pending.pop(0)
            name = job_name(bits, c, arm, jm)
            jd_rel = os.path.relpath(os.path.join(jobs_parent, name), REPO)
            cmd = job_command(a, bits, c, arm, jd_rel, jm)
            wcmd = [PY, os.path.join(REPO, WRAPPER), "exec", "--run-dir", os.path.join(REPO, jd_rel),
                    "--run-id", a.run_id, "--exp", EXP, "--spec-command", a.spec_command or "",
                    "--watchdog", f"{max(1.0, remaining):.1f}", "--rss-cap-bytes", str(RSS_CAP), "--"] + cmd
            rec = {"job": name, "bits": bits, "curve": c, "arm": arm, "arms": job_arms(arm), "panel": a.panel,
                   "m": (jm if jm is not None else a.m) if a.panel == "main" else (3 if a.panel == "j0" else None),
                   "command": cmd, "wrapper_command": wcmd, "job_dir": jd_rel,
                   "started_at": now(), "watchdog_seconds": round(max(1.0, remaining), 1),
                   "mem_available_at_start_bytes": ma}
            proc = subprocess.Popen(wcmd, cwd=REPO, stdout=subprocess.DEVNULL,
                                    stderr=open(os.path.join(ad, "wrapper-stderr.log"), "a"))
            running[name] = {"proc": proc, "rec": rec, "dir": os.path.join(REPO, jd_rel),
                             "expected": expected_job_keys(a, bits, c, arm, jm)}
            log(f"job {name} started (pid {proc.pid}; watchdog {rec['watchdog_seconds']} s; "
                f"MemAvailable {ma} B)")
        if not running and pending and (run_stop is not None or deadline - time.time() <= 0):
            break
        time.sleep(a.poll)
    not_started = [job_name(*j) for j in pending]
    why = ("not_started_after_run_stop" if run_stop is not None else
           "not_started_attempt_watchdog" if not_started else None)
    wall = time.time() - t_start
    idx = {"run_id": a.run_id, "attempt_dir": os.path.relpath(ad, REPO), "trigger": a.trigger,
           "started_at": started_at, "finished_at": now(), "wall_seconds": round(wall, 3),
           "attempt_watchdog_seconds": a.watchdog, "max_procs": a.max_procs,
           "min_mem_avail_gb": a.min_mem_avail_gb, "mem_gate_wait_polls": mem_waits,
           "rlimit_as_bytes_per_job_process": RSS_CAP, "command_template": tmpl,
           "panel": a.panel, "m": a.m, "known_log_max_bits": a.known_log_max_bits,
           "rho_curves": a.rho_curves, "dummy": bool(a.dummy),
           "run_stop_at_job": run_stop, "not_started": not_started, "not_started_reason": why,
           "not_started_specs": {job_name(*j): list(j) for j in pending},
           "launcher_sha256": sha256(os.path.abspath(__file__)),
           "code_at_launch": pins,
           "jobs": sorted(index, key=lambda r: (-r["bits"], r["curve"], r["arm"] or ""))}
    with open(os.path.join(ad, "jobs-index.json"), "w") as fh:
        json.dump(idx, fh, indent=2)
    log(f"attempt done: {len(index)} jobs ended, not started {not_started} ({why}); wall {wall:.1f} s")
    if a.finalize:
        return finalize_attempt(ad, a.run_id, a.location_kind, a.spec_command)
    return 0


def finalize_attempt(ad: str, run_id: str, location_kind: str, spec_command: str | None) -> int:
    idx = json.load(open(os.path.join(ad, "jobs-index.json")))
    r = subprocess.run([PY, os.path.join(HERE, "merge_census.py"), "summarize", "--attempt-dir", ad,
                        "--run-id", run_id], cwd=REPO, capture_output=True, text=True)
    with open(os.path.join(ad, "stdout.log"), "a") as fh:
        fh.write(f"$ merge_census.py summarize --attempt-dir {os.path.relpath(ad, REPO)} --run-id {run_id}\n"
                 f"{r.stdout}[exit {r.returncode}]\n")
    if r.returncode != 0:
        with open(os.path.join(ad, "stderr.log"), "a") as fh:
            fh.write(r.stderr)
        print(r.stderr, file=sys.stderr)
        return r.returncode
    raw = json.load(open(os.path.join(ad, "raw-result.json")))
    comp = raw["completeness"]
    abnormal = [j["job"] for j in idx["jobs"] if j.get("abnormal_end")]
    if raw["status_totals"].get("invalid") or idx["run_stop_at_job"]:
        status, reason = "invalid", "an instance is invalid (M-1 run_stop_rule / I-3)"
    elif comp["keys_missing"] or idx["not_started"] or abnormal:
        status = "failed_infrastructure"
        reason = (f"attempt incomplete: {comp['keys_missing']} expected keys without a row; "
                  f"not started {idx['not_started']}; abnormal job ends {abnormal}")
    else:
        status = "completed_valid"
        reason = ("every expected key of the attempt's jobs has exactly one row and no row is invalid; "
                  "instance-level failed_infrastructure rows are allowed and listed (M-7)")
    jobs = idx["jobs"]
    started = min((j["started_at"] for j in jobs), default=idx["started_at"])
    ended = max((j.get("ended_at") or "" for j in jobs), default=idx["finished_at"])
    bits = sorted({j["bits"] for j in jobs}, reverse=True)
    curves = sorted({j["curve"] for j in jobs})
    arms = sorted({x for j in jobs for x in (j.get("arms") or ([j["arm"]] if j["arm"] else []))}) or (
        list(MAIN_ARMS) if idx["panel"] == "main" else list(J0_ARMS) if idx["panel"] == "j0" else None)
    write_manifest(
        ad, run_id=run_id, location_kind=location_kind, status=status, reason=reason,
        completeness=comp,
        command=open(os.path.join(ad, "command.txt")).read().splitlines()[0],
        command_template=idx["command_template"],
        job_list=[j["job"] for j in jobs] + [f"{n} (not started)" for n in idx["not_started"]],
        spec_command=spec_command,
        timing={"started_at": idx["started_at"], "finished_at": idx["finished_at"],
                "first_job_started_at": started, "last_job_ended_at": ended,
                "wall_seconds": idx["wall_seconds"], "timing_source": "run_jobs.py (jobs-index.json)"},
        resources={"peak_rss_bytes_max_job_process": max((j.get("peak_rss_bytes") or 0 for j in jobs), default=0),
                   "cpu_seconds_sum_job_processes": round(sum(j.get("cpu_seconds") or 0 for j in jobs), 3),
                   "rlimit_as_bytes_per_job_process": RSS_CAP,
                   "attempt_watchdog_seconds": idx["attempt_watchdog_seconds"],
                   "instance_watchdog_seconds": 7200,
                   "max_concurrent_job_processes": idx["max_procs"],
                   "min_mem_available_gate_gb": idx["min_mem_avail_gb"],
                   "watchdog_expired_jobs": [j["job"] for j in jobs if j.get("watchdog_expired")]},
        inputs=inputs_block(idx["panel"], (idx["m"] if idx["m"] is not None else sorted({j["m"] for j in jobs}))
                            if idx["panel"] == "main" else (3 if idx["panel"] == "j0" else None),
                            bits, curves, arms, idx["known_log_max_bits"] if idx["panel"] == "main" else None,
                            idx["rho_curves"]),
        summary={"trigger": idx["trigger"], "jobs_ended": len(jobs), "not_started": idx["not_started"],
                 "not_started_reason": idx["not_started_reason"], "run_stop_at_job": idx["run_stop_at_job"],
                 "abnormal_job_ends": abnormal,
                 "m4_trigger_jobs": [j["job"] for j in jobs if j.get("m4_trigger")],
                 "status_totals": raw["status_totals"], "gates": raw["gates_summary"],
                 "raw_result_by": "merge_census.py summarize (attempt layout; summarize_run.py's interface "
                                  "needs one rows file per directory)"},
        raw=raw)
    print(f"finalized {os.path.relpath(ad, REPO)}: {status}")
    return 0


def cmd_finalize_attempt(a) -> int:
    ad = os.path.join(REPO, a.attempt_dir) if not os.path.isabs(a.attempt_dir) else a.attempt_dir
    return finalize_attempt(ad, a.run_id, a.location_kind, a.spec_command)


def cmd_finalize(a) -> int:
    """Manifest for a directory produced by run_wrapper.py exec (+ post): R13, R15."""
    import yaml

    d = os.path.join(REPO, a.dir) if not os.path.isabs(a.dir) else a.dir
    ex = json.load(open(os.path.join(d, "execution.json")))
    raw = json.load(open(os.path.join(d, "raw-result.json")))
    extra = yaml.safe_load(open(a.extra)) if a.extra else {}
    post = (json.load(open(os.path.join(d, "post-processing.json")))
            if os.path.exists(os.path.join(d, "post-processing.json")) else [])
    code = code_block()
    code["source_sha256_at_exec"] = ex["source_sha256"]
    code["git_at_exec"] = ex["git"]
    write_manifest(
        d, run_id=a.run_id, location_kind=a.location_kind, status=a.status, reason=a.reason,
        completeness=extra.get("completeness", {}), command=" ".join(ex["command"]),
        spec_command=ex.get("spec_command"),
        timing={"started_at": ex["started_at"], "finished_at": ex["finished_at"],
                "wall_seconds": ex["wall_seconds"], "timing_source": "run_wrapper.py execution.json"},
        resources={"peak_rss_bytes_max_descendant": ex["peak_rss_bytes_max_descendant"],
                   "cpu_seconds_descendants": ex["cpu_seconds_descendants"],
                   "rlimit_as_bytes_per_process": ex["rlimit_as_bytes_per_process"],
                   "watchdog_seconds": ex["watchdog_seconds"], "watchdog_expired": ex["watchdog_expired"],
                   "exit_code": ex["exit_code"]},
        inputs=extra.get("inputs", {}), summary=extra.get("summary", {}) | {"post_processing": post},
        raw=raw, deviations=extra.get("deviations"), unexpected=extra.get("unexpected"),
        extra=extra.get("extra"), code=code)
    print(f"finalized {os.path.relpath(d, REPO)}: {a.status}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run-id", required=True)
    r.add_argument("--attempt-dir", required=True)
    r.add_argument("--jobs-subdir", default="jobs", help="'' puts job directories directly in the attempt dir")
    r.add_argument("--panel", choices=("main", "j0", "rho"), required=True)
    r.add_argument("--m", type=int, default=None)
    r.add_argument("--known-log-max-bits", type=int, default=0)
    r.add_argument("--rho-curves", type=int, default=None)
    r.add_argument("--jobs", required=True, help="b<BB>-c<C>[:arm],...")
    r.add_argument("--spec-command", default="")
    r.add_argument("--trigger", required=True)
    r.add_argument("--location-kind", default="attempt")
    r.add_argument("--watchdog", type=float, default=86400)
    r.add_argument("--max-procs", type=int, default=4)
    r.add_argument("--min-mem-avail-gb", type=float, default=4.0)
    r.add_argument("--poll", type=float, default=5.0)
    r.add_argument("--finalize", action="store_true")
    r.add_argument("--dummy", action="store_true", help="pre-pin exercise: a dummy command, no solver")
    r.add_argument("--dummy-behaviour-json", default=None)
    f2 = sub.add_parser("finalize-attempt")
    f2.add_argument("--attempt-dir", required=True)
    f2.add_argument("--run-id", required=True)
    f2.add_argument("--location-kind", default="attempt")
    f2.add_argument("--spec-command", default="")
    f = sub.add_parser("finalize")
    f.add_argument("--dir", required=True)
    f.add_argument("--run-id", required=True)
    f.add_argument("--location-kind", default="run_root")
    f.add_argument("--status", required=True)
    f.add_argument("--reason", required=True)
    f.add_argument("--extra", default=None)
    a = ap.parse_args()
    return {"run": cmd_run, "finalize-attempt": cmd_finalize_attempt, "finalize": cmd_finalize}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
