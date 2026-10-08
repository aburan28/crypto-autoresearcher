"""EXP-PFDR-0b3699 launcher, merge and per-location artifact writer (TASK-20261002-8a6b8a).

Written for this experiment; the job-launch, checksum and merge logic follows
experiments/EXP-PFDR-011cd0/run_jobs.py and the merge subcommand of
experiments/EXP-PFDR-011cd0/merge_relcensus.py (read-only copy sources, never invoked;
AR-2 (2)).  Imports NO crypto_autoresearcher module and no engine module.  The merge
subcommand uses the standard library only (PyYAML is imported lazily by `finalize` alone).

Every process of a run is launched through the archived wrapper
experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py `exec` (RLIMIT_AS 3.5e9 bytes,
per-process watchdog), which writes the wrapped process's own command.txt,
environment.json, stdout.log, stderr.log, execution.json and a copy of itself into the
process directory (AR-2 (5)).  Layout of a run:

    runs/<RUN-ID>/                      run root (canonical location): data files of the run,
                                        command.txt, environment.json, stdout.log, stderr.log,
                                        raw-result.json, manifest.yaml, checksums.sha256
    runs/<RUN-ID>/attempt-1/            the attempt: raw-result.json, manifest.yaml,
                                        checksums.sha256
    runs/<RUN-ID>/attempt-1/<step>/     one wrapped process (analysis / test / check step)
    runs/<RUN-ID>/attempt-1/jobs/<job>/ one wrapped census job

Subcommands
  step         run one wrapped process into attempt-1/<step>/ (resource gates first).
  census-jobs  launch the census jobs of RA-02 (the archived R12 commands and their
               extended-arm variants) or RA-04 (design.json's jobs), at most 4 at once; gzip -n
               every JSONL of a job when it ends, then hash; parse ONLY the summary keys
               instances, by_status, stopped_at_job and certificates.cert_fail of a job's
               stdout.log (AR-1 (2)); nothing else of a job's output is read or echoed.
  merge        (standard library only) canonical rows.jsonl.gz, staircase.jsonl.gz and
               merge-report.json at the run root under AR-1 (3).
  finalize     raw-result.json, manifest.yaml and checksums.sha256 at attempt-1 and at the
               run root.

Nothing here computes or prints a relation count, kappa or z, and nothing is interpreted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

REPO = "/home/user/crypto-autoresearcher"
EXP = "EXP-PFDR-0b3699"
EXPDIR = f"experiments/{EXP}"
RUNS = os.environ.get("EXP0B3699_RUNS_ROOT", f"{EXPDIR}/runs")  # override used by the fixture exercise only
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
WRAPPER = "experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py"
TASK = "TASK-20261002-8a6b8a"
RSS_CAP = 3_500_000_000
PER_JOB_WATCHDOG = 21600
ATTEMPT_WATCHDOG = 86400
MIN_MEM_AVAIL_BYTES = 4 * 1024 ** 3
DISK_FLOOR_BYTES = int(2.5 * 1024 ** 3)
PACKAGE_GUARD_BYTES = 1.0 * 1024 ** 3
MAX_FILE_BYTES = 95 * 1024 * 1024
MAX_PROCS = 4

ARCHIVED_JOBS = "experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-table/attempt-1/jobs"
REPRO_JOBS = ("4-b30-c10", "4-b32-c10")
EXTENDED_ARMS = ("planted_sub", "small_x_offset")
RA04_ARMS = ["subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
             "known_null_sub", "planted_sub", "small_x_offset"]

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
    "tests/test_index_calculus_smallx_offset.py",
    f"{EXPDIR}/run_jobs.py",
    f"{EXPDIR}/design_a.py",
    f"{EXPDIR}/analyze_a.py",
    f"{EXPDIR}/reproduce_check.py",
    "experiments/EXP-PFDR-011cd0/verify_rows.py",
    WRAPPER,
    f"{EXPDIR}/specification.yaml",
]

PROTOCOL = {
    "specification": f"{EXPDIR}/specification.yaml (v1, frozen; approval_rulings AR-1 .. AR-7)",
    "approval_decision": "DEC-20261002-e7f8c9",
    "handoff": TASK,
    "output_archive": "TASK-20261002-33afa9",
    "amendments": [],
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
    "RUN-PFDR-0b3699-tests": "no seeds (deterministic tests)",
    "RUN-PFDR-0b3699-repro": {
        "curves": "bits 30 and 32, c = 10 .. 109 (the archived R12 jobs 4-b30-c10, 4-b32-c10)",
        "curve_generator": "generate_prime_order_curve(bits, c, p_filter=subgroup_prime_filter([3, 4, 5], 0.15))",
        "instance": "__main__._instance(bits, c, 0, pf); target label census, target seed 0; solver seed c",
        "bases": "subgroup c; dickson c; random_sub_r0/r1/r2 c, c+1000, c+2000; known_null_sub c+6000; "
                 "random_dick_r0/r1/r2 c+3000, c+4000, c+5000; known_null_dick c+7000; "
                 "planted_sub c+8000; small_x_offset c+9000 (label fb-smallx-offset|p|a|b|size|seed)",
    },
    "RUN-PFDR-0b3699-p0-design": {
        "curves": "candidate c = 2010 .. 8809 at bits 30 and 32 (PDI-8); design n_b from P0",
        "curve_generator": "generate_prime_order_curve(bits, c, p_filter=subgroup_prime_filter([3, 4, 5], 0.15))",
        "offset_x0": "random.Random(f'fb-smallx-offset|{p}|{a}|{b}|{s_sub}|{c + 9000}').randrange(p // 2) + p // 4",
        "planted": "FactorBase.planted(E, s_sub, seed = c + 8000)",
        "planted_target_subset": "random.Random(f'plant-target|EXP-PFDR-0b3699|{bits}').sample(curves_b, n_b)[:K_plant_b]",
        "simulation": "numpy SeedSequence([0x0b3699, family]) for family 0..4 (children spawned per purpose, recorded in power.json)",
    },
    "RUN-PFDR-0b3699-table": {
        "curves": "design.json final curves (bits 30 and 32, c = 2010 .. 2010 + n_b - 1)",
        "instance": "__main__._instance(bits, c, 0, pf); target label census, target seed 0; solver seed c",
        "bases": "subgroup c; small_x none; random_sub_r0/r1/r2 c, c+1000, c+2000; known_null_sub c+6000; "
                 "planted_sub c+8000; small_x_offset c+9000",
    },
    "RUN-PFDR-0b3699-calibrate": {
        "simulation": "numpy SeedSequence([0x0b3699, family]) family 0..4; permutation null "
                      "SeedSequence([0x0b3699, 100 + family]); bootstrap SeedSequence([0x0b3699, 200]) "
                      "(children recorded in calibration.json)",
    },
    "RUN-PFDR-0b3699-analysis": {
        "simulation": "numpy SeedSequence([0x0b3699, family]) family 0..4 (the RA-05 bank regenerated); "
                      "bootstrap SeedSequence([0x0b3699, 200]) (children recorded in analysis.json)",
    },
    "RUN-PFDR-0b3699-repro-attribution": "as RUN-PFDR-0b3699-repro, restricted to the mismatching instances",
}


# ------------------------------------------------------------------------------------------
# helpers

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def absp(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def rel(p: str) -> str:
    return os.path.relpath(absp(p), REPO)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: str):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def head_sha(relpath: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{relpath}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        return None
    return hashlib.sha256(r.stdout).hexdigest()


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
    for root, _, files in os.walk(absp(EXPDIR)):
        for f in files:
            try:
                tot += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return tot


def run_root(run_id: str) -> str:
    return absp(f"{RUNS}/{run_id}")


def log(run_id: str, msg: str, err: bool = False) -> None:
    """Orchestration log line -> console and the run root's stdout.log / stderr.log."""
    line = f"[{now()}] {msg}"
    print(line, file=sys.stderr if err else sys.stdout, flush=True)
    root = run_root(run_id)
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "stderr.log" if err else "stdout.log"), "a") as fh:
        fh.write(line + "\n")


def init_root(run_id: str, command_line: str) -> None:
    """command.txt (appended per invocation) and environment.json (once) at the run root."""
    root = run_root(run_id)
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "command.txt"), "a") as fh:
        fh.write(command_line + "\n")
    envp = os.path.join(root, "environment.json")
    if not os.path.exists(envp):
        with open(envp, "w") as fh:
            json.dump(wrapper_module().environment(), fh, indent=2, sort_keys=True)
    for f in ("stdout.log", "stderr.log"):
        open(os.path.join(root, f), "a").close()


def load_module(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, absp(relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wrapper_module():
    """The archived wrapper, loaded for environment() only."""
    return load_module("run_wrapper_amd1de84f", WRAPPER)


def resource_gate() -> str | None:
    """None when a process may start; otherwise the reason it may not (machine protection)."""
    if mem_available_bytes() < MIN_MEM_AVAIL_BYTES:
        return "MemAvailable < 4 GB"
    if free_disk_bytes() < DISK_FLOOR_BYTES:
        return "free disk < 2.5 GB (TW-DISK)"
    if package_bytes() > PACKAGE_GUARD_BYTES:
        return "experiments/EXP-PFDR-0b3699/ exceeds 1.0 GB (TW-DISK checkpoint)"
    return None


def attempt_started_at(ad: str) -> float | None:
    """Earliest started_at of any execution.json under the attempt (no extra file kept)."""
    first = None
    for root, _, files in os.walk(ad):
        if "execution.json" in files:
            ex = json.load(open(os.path.join(root, "execution.json")))
            t = dt.datetime.fromisoformat(ex["started_at"]).timestamp()
            first = t if first is None else min(first, t)
    return first


def remaining_attempt_seconds(ad: str) -> float:
    t0 = attempt_started_at(ad)
    if t0 is None:
        return ATTEMPT_WATCHDOG
    return ATTEMPT_WATCHDOG - (time.time() - t0)


def wrapped(run_id: str, proc_dir: str, command: list[str], watchdog: float,
            spec_command: str) -> dict:
    """Run one process under run_wrapper.py exec; return the wrapper's summary line."""
    wcmd = [PY, absp(WRAPPER), "exec", "--run-dir", proc_dir, "--run-id", run_id, "--exp", EXP,
            "--spec-command", spec_command, "--watchdog", str(int(watchdog)),
            "--rss-cap-bytes", str(RSS_CAP), "--", *command]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run(wcmd, cwd=REPO, capture_output=True, text=True, env=env)
    out = {"wrapper_exit": r.returncode}
    try:
        out.update(json.loads(r.stdout.strip().splitlines()[-1]))
    except (IndexError, json.JSONDecodeError):
        out["wrapper_stdout_unparsed"] = True
    if r.stderr.strip():
        out["wrapper_stderr"] = r.stderr.strip()[-2000:]
    return out


def gzip_jsonl(d: str) -> list[dict]:
    """gzip -n every *.jsonl of a directory, then hash; flag any file above 95 MB."""
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".jsonl"):
            subprocess.run(["gzip", "-n", os.path.join(d, f)], check=True)
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if os.path.isfile(p):
            out.append({"file": f, "bytes": os.path.getsize(p), "sha256": sha256(p),
                        "above_95MB": os.path.getsize(p) > MAX_FILE_BYTES})
    return out


def parse_job_summary(jd: str) -> dict:
    """AR-1 (2): extract ONLY instances, by_status, stopped_at_job, certificates.cert_fail."""
    try:
        s = json.loads(open(os.path.join(jd, "stdout.log")).read())
    except (OSError, json.JSONDecodeError):
        return {"parsed": False}
    out = {"parsed": True, "instances": s.get("instances"), "by_status": s.get("by_status"),
           "stopped_at_job": s.get("stopped_at_job"),
           "cert_fail": (s.get("certificates") or {}).get("cert_fail")}
    del s
    return out


# ------------------------------------------------------------------------------------------
# step

def cmd_step(a) -> int:
    run_id = a.run_id
    command = a.command[1:] if a.command and a.command[0] == "--" else a.command
    root = run_root(run_id)
    init_root(run_id, f"run_jobs.py step --run-id {run_id} --step {a.step} -- "
                      + " ".join(shlex.quote(c) for c in command))
    pd = os.path.join(root, "attempt-1", a.step)
    if os.path.exists(pd):
        log(run_id, f"refusing: {rel(pd)} exists (records are immutable)", err=True)
        return 3
    why = resource_gate()
    if why:
        log(run_id, f"step {a.step} NOT started: {why}", err=True)
        return 4
    wd = min(a.watchdog, remaining_attempt_seconds(os.path.join(root, "attempt-1")))
    if wd <= 0:
        log(run_id, f"step {a.step} NOT started: attempt watchdog expired", err=True)
        return 5
    os.makedirs(os.path.dirname(pd), exist_ok=True)
    log(run_id, f"step {a.step} start: {' '.join(command)}")
    res = wrapped(run_id, pd, command, wd, a.spec_command)
    big = [f for f in os.listdir(pd) if os.path.getsize(os.path.join(pd, f)) > MAX_FILE_BYTES]
    log(run_id, f"step {a.step} end: {json.dumps(res)}" + (f" FILES ABOVE 95 MB: {big}" if big else ""))
    return 0 if res.get("exit_code") == 0 else 1


# ------------------------------------------------------------------------------------------
# census jobs

def repro_jobs(attempt_dir: str) -> list[dict]:
    jobs = []
    for name in REPRO_JOBS:
        old = f"{ARCHIVED_JOBS}/{name}"
        first = open(absp(f"{old}/command.txt")).read().splitlines()[0]
        argv = shlex.split(first)
        for kind in ("base", "extended"):
            jname = name if kind == "base" else f"{name}-ext"
            jd = rel(os.path.join(attempt_dir, "jobs", jname))
            cmd = [c.replace(old, jd) for c in argv]
            if kind == "extended":
                i = cmd.index("--arms")
                j = i + 1
                while j < len(cmd) and not cmd[j].startswith("--"):
                    j += 1
                cmd = cmd[:j] + list(EXTENDED_ARMS) + cmd[j:]
            jobs.append({"job": jname, "kind": kind, "archived_job": old, "job_dir": jd,
                         "command": cmd})
    return jobs


def table_command(job: dict, jd: str) -> list[str]:
    return [PY, "-m", "crypto_autoresearcher.index_calculus", "census", "--panel", "main",
            "--m", "4", "--bits", str(job["bits"]), "--curve-offset", str(job["c0"]),
            "--curves", str(job["curves"]), "--modes", "table", "--arms", *job["arms"],
            "--known-log-max-bits", "0", "--retain", "all", "--relcount",
            "--instance-watchdog", "1800", "--bases-out", f"{jd}/bases.jsonl",
            "--bases-sample-mod", "10", "--workers", "1", "--out", f"{jd}/rows.jsonl",
            "--rows-out", f"{jd}/harvest-rows.jsonl", "--staircase-out", f"{jd}/staircase.jsonl"]


TABLE_SPEC_COMMAND = ("run_jobs.py over design.json's jobs, each: <PY> -m crypto_autoresearcher.index_calculus "
                      "census --panel main --m 4 --bits <30|32> --curve-offset <c0> --curves <K <= 100> "
                      "--modes table --arms subgroup small_x random_sub_r0 random_sub_r1 random_sub_r2 "
                      "known_null_sub planted_sub small_x_offset --known-log-max-bits 0 --retain all "
                      "--relcount --instance-watchdog 1800 --bases-out JOB/bases.jsonl --bases-sample-mod 10 "
                      "--workers 1 --out JOB/rows.jsonl --rows-out JOB/harvest-rows.jsonl "
                      "--staircase-out JOB/staircase.jsonl")
REPRO_SPEC_COMMAND = ("the two archived R12 job commands (G-REPRO), output paths moved under this "
                      "experiment's run directory, then the same with --arms extended by planted_sub and "
                      "small_x_offset")


def table_jobs(design: dict, attempt_dir: str) -> list[dict]:
    jobs = []
    for j in design["jobs"]:
        if j["arms"] != RA04_ARMS:
            raise SystemExit(f"design.json job {j['job']} arms differ from the frozen RA-04 arm list")
        jd = rel(os.path.join(attempt_dir, "jobs", j["job"]))
        jobs.append({"job": j["job"], "kind": "table", "job_dir": jd, "bits": j["bits"],
                     "c0": j["c0"], "curves": j["curves"], "command": table_command(j, jd)})
    return jobs


def cmd_census_jobs(a) -> int:
    run_id = a.run_id
    root = run_root(run_id)
    ad = os.path.join(root, "attempt-1")
    init_root(run_id, " ".join(shlex.quote(x) for x in ["run_jobs.py", *sys.argv[1:]]))
    if a.kind == "repro":
        jobs, spec_cmd = repro_jobs(ad), REPRO_SPEC_COMMAND
    else:
        dp = absp(a.design)
        if a.design_sha256 and sha256(dp) != a.design_sha256:
            log(run_id, "refusing: design.json sha256 differs from the pinned value", err=True)
            return 6
        jobs, spec_cmd = table_jobs(json.load(open(dp)), ad), TABLE_SPEC_COMMAND
    todo = [j for j in jobs if not os.path.exists(absp(j["job_dir"]))]
    log(run_id, f"census-jobs {a.kind}: {len(jobs)} jobs, {len(todo)} not yet started")
    stop = {"flag": False, "reason": None}
    results: dict = {}

    def run_one(job: dict) -> None:
        while True:
            if stop["flag"]:
                results[job["job"]] = {"not_started": stop["reason"]}
                return
            why = resource_gate()
            if why is None:
                break
            if "TW-DISK" in why:
                stop["flag"], stop["reason"] = True, why
                log(run_id, f"CHECKPOINT: {why}", err=True)
                continue
            time.sleep(15)
        wd = min(PER_JOB_WATCHDOG, remaining_attempt_seconds(ad))
        if wd <= 0:
            stop["flag"], stop["reason"] = True, "attempt watchdog 86400 s expired (checkpoint)"
            results[job["job"]] = {"not_started": stop["reason"]}
            return
        jd = absp(job["job_dir"])
        os.makedirs(os.path.dirname(jd), exist_ok=True)
        log(run_id, f"job {job['job']} start")
        res = wrapped(run_id, jd, job["command"], wd, spec_cmd)
        files = gzip_jsonl(jd)
        summ = parse_job_summary(jd)
        big = [f["file"] for f in files if f["above_95MB"]]
        rec = {"exit_code": res.get("exit_code"), "watchdog_expired": res.get("watchdog_expired"),
               "wall_seconds": res.get("wall_seconds"),
               "peak_rss_bytes_max_descendant": res.get("peak_rss_bytes_max_descendant"),
               "cpu_seconds_descendants": res.get("cpu_seconds_descendants"),
               "summary": summ, "files_above_95MB": big}
        results[job["job"]] = rec
        log(run_id, f"job {job['job']} end: exit {rec['exit_code']} watchdog {rec['watchdog_expired']} "
                    f"instances {summ.get('instances')} by_status {json.dumps(summ.get('by_status'))} "
                    f"stopped_at_job {summ.get('stopped_at_job') is not None} cert_fail {summ.get('cert_fail')}")
        if summ.get("cert_fail") not in (0, None) or summ.get("stopped_at_job") is not None:
            stop["flag"], stop["reason"] = True, f"job {job['job']}: certificate / gate stop (G4)"
            log(run_id, f"STOP: {stop['reason']}", err=True)
        if big:
            stop["flag"], stop["reason"] = True, f"job {job['job']}: a file above 95 MB"
            log(run_id, f"STOP: {stop['reason']}", err=True)

    with ThreadPoolExecutor(max_workers=MAX_PROCS) as pool:
        list(pool.map(run_one, todo))
    ok = all(r.get("exit_code") == 0 for r in results.values()) and not stop["flag"]
    log(run_id, f"census-jobs {a.kind} done: {sum(1 for r in results.values() if 'exit_code' in r)} ran, "
                f"{sum(1 for r in results.values() if 'not_started' in r)} not started, "
                f"stop {stop['reason']}")
    return 0 if ok else 1


# ------------------------------------------------------------------------------------------
# merge (standard library only; AR-1 (3), AR-2 (2))

def row_m(r: dict):
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


def key_of(r: dict) -> tuple:
    return (r.get("bits"), r.get("curve"), row_m(r), r.get("arm"), r.get("mode"))


def ks(k) -> str:
    return json.dumps(list(k))


def write_gz_jsonl(path: str, recs) -> str:
    if os.path.exists(path):
        raise SystemExit(f"refusing: {path} exists (records are immutable)")
    tmp = path[:-3]
    with open(tmp, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    subprocess.run(["gzip", "-n", tmp], check=True)
    return sha256(path)


def cmd_merge(a) -> int:
    rd = absp(a.run_dir)
    for f in ("rows.jsonl.gz", "staircase.jsonl.gz", "merge-report.json"):
        if os.path.exists(os.path.join(rd, f)):
            print(f"refusing: {rd}/{f} exists (records are immutable)", file=sys.stderr)
            return 3
    design = json.load(open(absp(a.design)))
    expected: dict[str, None] = {}
    for j in design["jobs"]:
        for c in range(j["c0"], j["c0"] + j["curves"]):
            for arm in j["arms"]:
                expected.setdefault(ks((j["bits"], c, 4, arm, "table")), None)
    sources: dict[str, dict] = {}
    superseded, dup_same_attempt, non_cell = [], [], []
    attempts_info = []
    for att in a.attempts:
        jroot = os.path.join(rd, att, "jobs")
        names = sorted(os.listdir(jroot)) if os.path.isdir(jroot) else []
        attempts_info.append({"attempt": att, "jobs_ran": names})
        for name in names:
            jd = os.path.join(jroot, name)
            rp = os.path.join(jd, "rows.jsonl.gz")
            if not os.path.exists(rp):
                continue
            seen_here = Counter()
            for r in read_jsonl(rp):
                k = ks(key_of(r))
                seen_here[k] += 1
                if seen_here[k] > 1:
                    dup_same_attempt.append({"key": json.loads(k), "attempt": att, "job": name})
                    continue
                if k not in expected:
                    non_cell.append({"key": json.loads(k), "attempt": att, "job": name,
                                     "status": r.get("status")})
                    continue
                prev = sources.get(k)
                cand = {"attempt": att, "job": name, "job_dir": rel(jd), "row": r}
                if prev is None:
                    sources[k] = cand
                elif prev["row"].get("status") == "failed_infrastructure":
                    superseded.append({"key": json.loads(k), "attempt": prev["attempt"],
                                       "status": "failed_infrastructure", "superseded_by": att})
                    sources[k] = cand
                else:
                    superseded.append({"key": json.loads(k), "attempt": att, "status": r.get("status"),
                                       "note": "later row not used: an earlier attempt holds a "
                                               "non-infrastructure row for this key"})
    missing = sorted(k for k in expected if k not in sources)
    keys_sorted = sorted(sources, key=lambda k: tuple(json.loads(k)))
    rows_sha = write_gz_jsonl(os.path.join(rd, "rows.jsonl.gz"),
                              (sources[k]["row"] for k in keys_sorted))
    by_job: dict = defaultdict(set)
    for k in keys_sorted:
        by_job[sources[k]["job_dir"]].add(k)
    stairs = []
    harvest_map, bases_map = {}, {}
    for jd_rel, keyset in sorted(by_job.items()):
        jd = absp(jd_rel)
        sp = os.path.join(jd, "staircase.jsonl.gz")
        if os.path.exists(sp):
            stairs.extend(s for s in read_jsonl(sp) if ks(key_of(s)) in keyset)
        hp = os.path.join(jd, "harvest-rows.jsonl.gz")
        hsha = sha256(hp) if os.path.exists(hp) else None
        for k in keyset:
            harvest_map[k] = {"harvest_rows_file": rel(hp) if hsha else None, "sha256": hsha}
        bp = os.path.join(jd, "bases.jsonl.gz")
        if os.path.exists(bp):
            bsha = sha256(bp)
            for b in read_jsonl(bp):
                bk = ks((b["bits"], b["curve"], b["m"], b["arm"]))
                if ks((b["bits"], b["curve"], b["m"], b["arm"], "table")) in keyset:
                    bases_map[bk] = {"bases_file": rel(bp), "sha256": bsha}
    stairs.sort(key=lambda s: (key_of(s), s.get("class", "")))
    st_sha = write_gz_jsonl(os.path.join(rd, "staircase.jsonl.gz"), stairs)
    del stairs
    statuses = {k: sources[k]["row"].get("status") for k in keys_sorted}
    counts = Counter(statuses.values())
    non_valid: dict = defaultdict(list)
    for k in keys_sorted:
        if statuses[k] != "completed_valid":
            non_valid[str(statuses[k])].append(json.loads(k))
    rep = {"what": "EXP-PFDR-0b3699 canonical row set (run_jobs.py merge)",
           "run_id": a.run_id, "canonical_location": rel(rd), "created_at": now(),
           "blinding_note": ("AR-1 (3): keys, per-key sources, instance counts, the maps verify_rows.py "
                             "reads and file hashes only; no total of relations, harvest rows, "
                             "certificates or staircase records"),
           "attempts": attempts_info, "expected_keys": len(expected), "canonical_rows": len(keys_sorted),
           "missing_keys": [json.loads(k) for k in missing],
           "keys_with_exactly_one_canonical_row": not missing and not dup_same_attempt,
           "per_key_source": {k: {"attempt": sources[k]["attempt"], "job": sources[k]["job"],
                                  "rows_file": rel(os.path.join(absp(sources[k]["job_dir"]), "rows.jsonl.gz"))}
                              for k in keys_sorted},
           "superseded_rows": superseded, "duplicate_rows_within_attempt": dup_same_attempt,
           "non_cell_rows_excluded": non_cell,
           "harvest_rows_map": harvest_map,
           "harvest_rows_note": "harvest rows stay in their job directories and are mapped here",
           "bases_map": bases_map,
           "canonical_files": {"rows.jsonl.gz": rows_sha, "staircase.jsonl.gz": st_sha},
           "counts_by_status": dict(counts),
           "non_valid_keys": dict(non_valid),
           "sort_rule": "(bits, curve, m, arm, mode), stable"}
    with open(os.path.join(rd, "merge-report.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({k: rep[k] for k in ("run_id", "expected_keys", "canonical_rows",
                                          "keys_with_exactly_one_canonical_row", "counts_by_status")}))
    return 0 if rep["keys_with_exactly_one_canonical_row"] else 1


# ------------------------------------------------------------------------------------------
# finalize

def code_block() -> dict:
    sources = {}
    for rp in PINNED_FILES:
        p = absp(rp)
        if not os.path.exists(p):
            sources[rp] = {"sha256": None, "status": "absent"}
            continue
        dg, hd = sha256(p), head_sha(rp)
        sources[rp] = {"sha256": dg,
                       "status": "untracked" if hd is None else ("clean" if hd == dg else "modified")}
    porcelain = git("status", "--porcelain", "--untracked-files=all", "--", "src", "tests",
                    EXPDIR).splitlines()
    return {"commit": git("rev-parse", "HEAD").strip(),
            "dirty": bool(git("status", "--porcelain", "--untracked-files=no").strip()),
            "dirty_note": ("tracked-tree dirty flag over the whole repository; the EC-A1 edits are "
                           "uncommitted by design (card NO COMMITS) and pinned by sha256 in "
                           "implementation-notes.yaml pins.scripts"),
            "status_porcelain_scoped": [l for l in porcelain if "__pycache__" not in l
                                        and "/runs/" not in l],
            "source_sha256": sources}


def write_checksums(d: str) -> None:
    lines = []
    for root, dirs, files in os.walk(d):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            r = os.path.relpath(p, d)
            if r == "checksums.sha256":
                continue
            lines.append(f"{sha256(p)}  {r}")
    with open(os.path.join(d, "checksums.sha256"), "w") as fh:
        fh.write("\n".join(sorted(lines, key=lambda s: s.split("  ", 1)[1])) + "\n")


def executions(ad: str) -> list[dict]:
    out = []
    for root, dirs, files in os.walk(ad):
        dirs.sort()
        if "execution.json" in files:
            ex = json.load(open(os.path.join(root, "execution.json")))
            ex["_dir"] = rel(root)
            out.append(ex)
    return out


def certificate_block() -> dict:
    return {"kind": "none", "instances_claimed": 0, "instances_verified": 0,
            "note": "no run of this experiment determines a discrete log (card GATES AND CERTIFICATES)"}


def all_files(d: str) -> dict:
    out = {}
    for root, dirs, files in os.walk(d):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            r = os.path.relpath(p, d)
            if r in ("manifest.yaml", "checksums.sha256", "raw-result.json"):
                continue
            out[r] = sha256(p)
    return out


def cmd_finalize(a) -> int:
    import yaml

    run_id = a.run_id
    root = run_root(run_id)
    ad = os.path.join(root, "attempt-1")
    for d in (ad, root):
        for f in ("manifest.yaml", "raw-result.json", "checksums.sha256"):
            if os.path.exists(os.path.join(d, f)):
                print(f"refusing: {rel(d)}/{f} exists (records are immutable)", file=sys.stderr)
                return 3
    if a.status not in ("completed_valid", "failed_infrastructure", "invalid"):
        raise SystemExit(f"status {a.status!r} is not a status value of this contract")
    exs = executions(ad)
    if not exs:
        raise SystemExit("no execution.json under the attempt; nothing ran")
    started = min(e["started_at"] for e in exs)
    finished = max(e["finished_at"] for e in exs)
    summaries = {}
    for e in exs:
        d = absp(e["_dir"])
        if "/jobs/" in e["_dir"] + "/":
            summaries[e["_dir"]] = parse_job_summary(d)
    by_status: Counter = Counter()
    for s in summaries.values():
        for k, v in (s.get("by_status") or {}).items():
            by_status[k] += v
    gates = {}
    for g in a.gate_report or []:
        gp = absp(g)
        rep = json.load(open(gp))
        gates[rel(gp)] = {"gate": rep.get("gate"), "pass": rep.get("pass"),
                          "checks": {k: v.get("pass") for k, v in (rep.get("checks") or {}).items()
                                     if isinstance(v, dict) and "pass" in v} or None,
                          "sha256": sha256(gp)}
    metrics = None
    if a.metrics_from:
        mp = absp(a.metrics_from)
        m = json.load(open(mp))
        metrics = {"source": rel(mp), "sha256": sha256(mp),
                   "declared_metrics": m.get("declared_metrics", m.get("raw_result_metrics"))}
    extra = json.loads(a.extra_json) if a.extra_json else {}
    completeness = json.loads(a.completeness) if a.completeness else {}
    code = code_block()
    commands = [{"dir": e["_dir"], "command": e["command"], "spec_command": e.get("spec_command"),
                 "exit_code": e["exit_code"], "watchdog_expired": e["watchdog_expired"],
                 "started_at": e["started_at"], "finished_at": e["finished_at"],
                 "wall_seconds": e["wall_seconds"],
                 "peak_rss_bytes_max_descendant": e["peak_rss_bytes_max_descendant"],
                 "cpu_seconds_descendants": e["cpu_seconds_descendants"],
                 "git": e.get("git")} for e in exs]
    resources = {"peak_rss_bytes_max_process": max(e["peak_rss_bytes_max_descendant"] for e in exs),
                 "cpu_seconds_sum": round(sum(e["cpu_seconds_descendants"] for e in exs), 3),
                 "wall_seconds_sum_processes": round(sum(e["wall_seconds"] for e in exs), 3),
                 "wall_seconds_span": round(dt.datetime.fromisoformat(finished).timestamp()
                                            - dt.datetime.fromisoformat(started).timestamp(), 3),
                 "rlimit_as_bytes_per_process": RSS_CAP,
                 "package_bytes_at_finalize": package_bytes()}
    for loc, d in (("attempt", ad), ("run_root", root)):
        raw = {"run_id": run_id, "experiment_id": EXP, "location": rel(d), "status": a.status,
               "status_reason": a.reason, "completeness": completeness,
               "instance_counts_by_status": dict(by_status) or None,
               "job_summaries_ar1_keys_only": summaries or None,
               "gates": gates, "metrics": metrics,
               "certificate": certificate_block(),
               "file_sha256": all_files(d), "extra": extra or None}
        with open(os.path.join(d, "raw-result.json"), "w") as fh:
            json.dump(raw, fh, indent=1)
        env = json.load(open(os.path.join(root, "environment.json")))
        body = {
            "id": run_id, "experiment_id": EXP, "task_id": TASK, "location_kind": loc,
            "location": rel(d), "protocol": PROTOCOL, "status": a.status,
            "status_vocabulary": "completed_valid | failed_infrastructure | invalid, with completeness",
            "completeness": completeness,
            "validity": {"valid": a.status == "completed_valid", "reason": a.reason},
            "code": code | {"interpreter": PY, "env": {"PYTHONDONTWRITEBYTECODE": "1"},
                            "commands": commands,
                            "root_command_log": "command.txt (run root): every run_jobs.py invocation"},
            "inference": INFERENCE,
            "environment": {k: v for k, v in env.items() if k != "pip_freeze"}
                           | {"dependencies": "environment.json pip_freeze"},
            "inputs": json.loads(a.inputs_json) if a.inputs_json else {},
            "seeds": SEEDS.get(run_id),
            "timing": {"started_at": started, "finished_at": finished},
            "resources": resources,
            "result": {"raw_result": "raw-result.json", "certificate": certificate_block()},
            "deviations": json.loads(a.deviations_json) if a.deviations_json else [],
            "observations_unexpected": json.loads(a.unexpected_json) if a.unexpected_json else [],
        }
        files = []
        for r_, ds, fs in os.walk(d):
            for f in fs:
                files.append(os.path.relpath(os.path.join(r_, f), d))
        body["artifacts"] = sorted(set(files) | {"manifest.yaml", "checksums.sha256"})
        with open(os.path.join(d, "manifest.yaml"), "w") as fh:
            yaml.safe_dump({"run": body}, fh, sort_keys=False, width=100)
        write_checksums(d)
        print(f"finalized {rel(d)}: {a.status}")
    return 0


# ------------------------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("step")
    s.add_argument("--run-id", required=True)
    s.add_argument("--step", required=True)
    s.add_argument("--spec-command", default="")
    s.add_argument("--watchdog", type=float, default=ATTEMPT_WATCHDOG)
    s.add_argument("command", nargs=argparse.REMAINDER)
    c = sub.add_parser("census-jobs")
    c.add_argument("--run-id", required=True)
    c.add_argument("--kind", choices=("repro", "table"), required=True)
    c.add_argument("--design", default=None)
    c.add_argument("--design-sha256", default=None)
    m = sub.add_parser("merge")
    m.add_argument("--run-dir", required=True)
    m.add_argument("--run-id", required=True)
    m.add_argument("--design", required=True)
    m.add_argument("--attempts", nargs="+", default=["attempt-1"])
    f = sub.add_parser("finalize")
    f.add_argument("--run-id", required=True)
    f.add_argument("--status", required=True)
    f.add_argument("--reason", required=True)
    f.add_argument("--completeness", default=None, help="JSON")
    f.add_argument("--gate-report", action="append", default=None)
    f.add_argument("--metrics-from", default=None)
    f.add_argument("--inputs-json", default=None)
    f.add_argument("--deviations-json", default=None)
    f.add_argument("--unexpected-json", default=None)
    f.add_argument("--extra-json", default=None)
    a = ap.parse_args()
    return {"step": cmd_step, "census-jobs": cmd_census_jobs, "merge": cmd_merge,
            "finalize": cmd_finalize}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
