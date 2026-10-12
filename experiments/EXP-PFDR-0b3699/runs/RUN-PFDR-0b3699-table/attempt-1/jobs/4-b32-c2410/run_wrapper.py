"""Run wrapper for TASK-20260929-f90fed (EXP-PFDR-1b78f7 under protocol version 2 =
specification.yaml v1 + AMD-20260929-1de84f).  Derived from the archived wrapper of
TASK-20260928-51b8c8 (runs/RUN-PFDR-1b78f7-tests/run_wrapper.py): same three phases;
changes: task id, protocol block, inference block, pinned files, porcelain scope,
finalize also records the protocol, the certificate block and the extra-file inputs.

Three phases, each invoked explicitly so every step is recorded:

  exec      create the run directory (refuses an existing one), copy this
            wrapper into it, record command.txt, environment.json, the git
            commit / dirty state and the sha256 of every pinned source file,
            then run the command with a per-process address-space cap
            (RLIMIT_AS, inherited by every worker process) and a per-run
            watchdog; stdout/stderr go to stdout.log / stderr.log; timing,
            exit status and resource use go to execution.json.
  post      run one post-processing command (comparison, gzip -n) in the run
            directory's context and append it, with its exit code and output,
            to post-processing.json / post.log.
  finalize  write manifest.yaml from execution.json + post-processing.json +
            raw-result.json and a caller-supplied status/reason, then
            checksums.sha256 over every other file in the directory.

Nothing here interprets a result.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import time

REPO = "/home/user/crypto-autoresearcher"
PINNED_GLOBS = [
    "src/crypto_autoresearcher/index_calculus",
]
EXTRA_PINNED = [
    "tests/test_index_calculus_fp.py",
    "tests/test_index_calculus_harvest.py",
    "experiments/EXP-PFDR-7c8bf2/analyze_floor.py",
    "experiments/EXP-PFDR-1b78f7/compare_regression.py",
    "experiments/EXP-PFDR-1b78f7/analyze_census.py",
    "experiments/EXP-PFDR-1b78f7/amd-1de84f/function_diff.py",
    "experiments/EXP-PFDR-1b78f7/amd-1de84f/run_wrapper.py",
    "experiments/EXP-PFDR-1b78f7/amd-1de84f/summarize_run.py",
]

PROTOCOL = {
    "version": 2,
    "specification": "experiments/EXP-PFDR-1b78f7/specification.yaml (v1, frozen)",
    "amendment": "AMD-20260929-1de84f (experiments/EXP-PFDR-1b78f7/amendments/AMD-20260929-1de84f.yaml)",
    "approval_decisions": ["DEC-20260928-ab2d31", "DEC-20260929-523aab"],
    "handoff": "TASK-20260929-f90fed",
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
    "note": "the run itself is deterministic code; no model is in the measurement loop",
}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def head_sha(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        return None
    return hashlib.sha256(r.stdout).hexdigest()


def pinned_sources() -> dict:
    files = []
    for d in PINNED_GLOBS:
        for name in sorted(os.listdir(os.path.join(REPO, d))):
            if name.endswith(".py"):
                files.append(f"{d}/{name}")
    files += [f for f in EXTRA_PINNED if os.path.exists(os.path.join(REPO, f))]
    out = {}
    for rel in files:
        dg = sha256(os.path.join(REPO, rel))
        hd = head_sha(rel)
        out[rel] = {"sha256": dg,
                    "status": "untracked" if hd is None else ("clean" if hd == dg else "modified")}
    return out


def pip_freeze() -> list[str]:
    r = subprocess.run(["uv", "pip", "freeze", "--python", sys.executable],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().splitlines()
    import importlib.metadata as md
    return sorted(f"{d.metadata['Name']}=={d.version}" for d in md.distributions())


def environment() -> dict:
    cpu = ""
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    try:
        import numpy
        npv = numpy.__version__
    except Exception:  # pragma: no cover
        npv = None
    return {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "numpy_version": npv,
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "cpu_model": cpu,
        "cpu_count": os.cpu_count(),
        "mem_total_bytes": os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"),
        "pip_freeze": pip_freeze(),
        "pip_freeze_note": "venv has no pip module; list from `uv pip freeze --python <venv python>`",
        "env": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                                "MKL_NUM_THREADS", "PYTHONHASHSEED",
                                                "PYTHONDONTWRITEBYTECODE")},
    }


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def cmd_exec(a) -> int:
    rd = a.run_dir
    if os.path.exists(rd) and os.listdir(rd):
        print(f"refusing: {rd} exists and is not empty (run records are immutable)", file=sys.stderr)
        return 3
    os.makedirs(rd, exist_ok=True)
    shutil.copy2(__file__, os.path.join(rd, "run_wrapper.py"))
    command = a.command
    if command and command[0] == "--":
        command = command[1:]
    with open(os.path.join(rd, "command.txt"), "w") as fh:
        fh.write(" ".join(command) + "\n")
        if a.spec_command:
            fh.write("# frozen specification command: " + a.spec_command + "\n")
        fh.write(f"# cwd: {REPO}\n")
    env_block = environment()
    with open(os.path.join(rd, "environment.json"), "w") as fh:
        json.dump(env_block, fh, indent=2, sort_keys=True)
    commit = _git("rev-parse", "HEAD").strip()
    status_porcelain = _git("status", "--porcelain", "--untracked-files=all",
                            "--", "src", "tests", ":(glob)experiments/EXP-PFDR-*/*.py",
                            ":(glob)experiments/EXP-PFDR-*/*.yaml",
                            "experiments/EXP-PFDR-1b78f7/amd-1de84f").splitlines()
    tracked_dirty = bool(_git("status", "--porcelain", "--untracked-files=no").strip())
    sources = pinned_sources()
    started = now()
    t0 = time.monotonic()
    cap = int(a.rss_cap_bytes)

    def preexec():
        os.setsid()
        if cap > 0:
            resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "PYTHONDONTWRITEBYTECODE": "1"})
    timed_out = False
    with open(os.path.join(rd, "stdout.log"), "wb") as so, \
            open(os.path.join(rd, "stderr.log"), "wb") as se:
        proc = subprocess.Popen(command, cwd=REPO, stdout=so, stderr=se,
                                preexec_fn=preexec, env=env)
        try:
            rc = proc.wait(timeout=a.watchdog if a.watchdog > 0 else None)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                time.sleep(10)
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            rc = proc.wait()
    wall = time.monotonic() - t0
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    ex = {
        "run_id": a.run_id, "experiment_id": a.exp,
        "command": command, "spec_command": a.spec_command, "cwd": REPO,
        "started_at": started, "finished_at": now(), "wall_seconds": round(wall, 3),
        "exit_code": rc, "watchdog_seconds": a.watchdog, "watchdog_expired": timed_out,
        "rlimit_as_bytes_per_process": cap,
        "rss_cap_note": ("per-process cap enforced as RLIMIT_AS (address space >= RSS), "
                         "inherited by every worker; 3.5e9 bytes"),
        "peak_rss_bytes_max_descendant": ru.ru_maxrss * 1024,
        "cpu_seconds_descendants": round(ru.ru_utime + ru.ru_stime, 3),
        "git": {"commit": commit, "tracked_tree_dirty": tracked_dirty,
                "status_porcelain_scoped": status_porcelain},
        "source_sha256": sources,
        "thread_env_forced": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                              "MKL_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    }
    with open(os.path.join(rd, "execution.json"), "w") as fh:
        json.dump(ex, fh, indent=2)
    print(json.dumps({k: ex[k] for k in ("exit_code", "wall_seconds", "watchdog_expired",
                                         "peak_rss_bytes_max_descendant",
                                         "cpu_seconds_descendants")}))
    return 0


def cmd_post(a) -> int:
    rd = a.run_dir
    command = a.command[1:] if a.command and a.command[0] == "--" else a.command
    t0 = time.monotonic()
    r = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
    rec = {"command": command, "exit_code": r.returncode, "started_at": now(),
           "wall_seconds": round(time.monotonic() - t0, 3)}
    path = os.path.join(rd, "post-processing.json")
    recs = json.load(open(path)) if os.path.exists(path) else []
    recs.append(rec)
    with open(path, "w") as fh:
        json.dump(recs, fh, indent=2)
    with open(os.path.join(rd, "post.log"), "a") as fh:
        fh.write(f"$ {' '.join(command)}\n{r.stdout}{r.stderr}[exit {r.returncode}]\n")
    print(r.stdout + r.stderr)
    return r.returncode


def cmd_finalize(a) -> int:
    import yaml

    rd = a.run_dir
    if os.path.exists(os.path.join(rd, "manifest.yaml")):
        print("refusing: manifest.yaml exists", file=sys.stderr)
        return 3
    ex = json.load(open(os.path.join(rd, "execution.json")))
    post = (json.load(open(os.path.join(rd, "post-processing.json")))
            if os.path.exists(os.path.join(rd, "post-processing.json")) else [])
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    extra = yaml.safe_load(open(a.extra)) if a.extra else {}
    cert = raw.get("certificate", {"kind": "none"})
    manifest = {"run": {
        "id": ex["run_id"],
        "experiment_id": ex["experiment_id"],
        "task_id": "TASK-20260929-f90fed",
        "protocol": PROTOCOL,
        "status": a.status,
        "validity": {"valid": a.status == "completed_valid", "reason": a.reason},
        "code": {"commit": ex["git"]["commit"],
                 "dirty": ex["git"]["tracked_tree_dirty"],
                 "status_porcelain_scoped": ex["git"]["status_porcelain_scoped"],
                 "command": " ".join(ex["command"]),
                 "spec_command": ex["spec_command"],
                 "source_sha256": ex["source_sha256"],
                 "wrapper": {"path": "run_wrapper.py",
                             "sha256": sha256(os.path.join(rd, "run_wrapper.py"))}},
        "inference": INFERENCE,
        "environment": {k: v for k, v in json.load(open(os.path.join(rd, "environment.json"))).items()
                        if k != "pip_freeze"} | {"dependencies": "environment.json pip_freeze"},
        "inputs": extra.get("inputs", {}),
        "timing": {"started_at": ex["started_at"], "finished_at": ex["finished_at"],
                   "wall_seconds": ex["wall_seconds"], "timing_source": "wrapper"},
        "resources": {"peak_rss_bytes_max_descendant": ex["peak_rss_bytes_max_descendant"],
                      "cpu_seconds_descendants": ex["cpu_seconds_descendants"],
                      "rlimit_as_bytes_per_process": ex["rlimit_as_bytes_per_process"],
                      "watchdog_seconds": ex["watchdog_seconds"],
                      "watchdog_expired": ex["watchdog_expired"],
                      "exit_code": ex["exit_code"]},
        "post_processing": post,
        "result": {"summary": extra.get("summary", {}),
                   "certificate": {k: v for k, v in cert.items() if k != "instances"}},
        "deviations": extra.get("deviations", []),
        "observations_unexpected": extra.get("unexpected", []),
        "artifacts": sorted(f for f in os.listdir(rd) if f != "checksums.sha256") + ["checksums.sha256"],
    }}
    with open(os.path.join(rd, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100)
    lines = []
    for root, _, files in os.walk(rd):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, rd)
            if rel == "checksums.sha256":
                continue
            lines.append(f"{sha256(p)}  {rel}")
    with open(os.path.join(rd, "checksums.sha256"), "w") as fh:
        fh.write("\n".join(sorted(lines, key=lambda s: s.split("  ", 1)[1])) + "\n")
    print(f"finalized {rd}: {a.status}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("exec")
    e.add_argument("--run-dir", required=True)
    e.add_argument("--run-id", required=True)
    e.add_argument("--exp", required=True)
    e.add_argument("--spec-command", default="")
    e.add_argument("--watchdog", type=float, default=86400)
    e.add_argument("--rss-cap-bytes", type=float, default=3.5e9)
    e.add_argument("command", nargs=argparse.REMAINDER)
    p = sub.add_parser("post")
    p.add_argument("--run-dir", required=True)
    p.add_argument("command", nargs=argparse.REMAINDER)
    f = sub.add_parser("finalize")
    f.add_argument("--run-dir", required=True)
    f.add_argument("--status", required=True)
    f.add_argument("--reason", required=True)
    f.add_argument("--extra", default=None)
    a = ap.parse_args()
    return {"exec": cmd_exec, "post": cmd_post, "finalize": cmd_finalize}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
