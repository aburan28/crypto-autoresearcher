#!/usr/bin/env python3
"""EXP-DREG-002 run harness (executor infrastructure, not an instrument).

Copied from EXP-DREG-001/DREG_harness.py and retargeted at EXP-DREG-002.
Runs ONE cell command under a hard watchdog timeout, captures stdout/stderr,
and writes the run receipt: command.txt, environment.json, manifest.yaml.

Convention follows docs/evidence-and-reproducibility.md and the existing
RUN-DREG-001-* receipts. Never mutates anything outside the run directory.
"""
import argparse, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent  # workspace root
EXP = "EXP-DREG-002"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def git_state():
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=WS,
                                capture_output=True, text=True).stdout.strip()
        status = subprocess.run(["git", "status", "--porcelain"], cwd=WS,
                                capture_output=True, text=True).stdout
        dirty = bool(status.strip())
        dirty_sha = hashlib.sha256(status.encode()).hexdigest()
        (WS / "experiments" / EXP / "runs" / "_git_status_latest.txt").write_text(status)
    except Exception as e:
        commit, dirty, dirty_sha = f"error:{e}", None, None
    return commit, dirty, dirty_sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--inputs", default="{}")       # JSON, recorded verbatim
    ap.add_argument("--expected", default="{}")     # JSON, recorded verbatim
    ap.add_argument("--timeout", type=float, default=590.0)
    ap.add_argument("--valid-if", default="")       # path (rel. to run dir) whose existence => completed
    ap.add_argument("--metrics-from", default="")   # path (rel.) to JSON with metrics
    ap.add_argument("cmd", nargs=argparse.REMAINDER)  # after '--'
    args = ap.parse_args()
    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        sys.exit("no command given")

    rd = WS / "experiments" / EXP / "runs" / args.run_id
    rd.mkdir(parents=True, exist_ok=True)
    commit, dirty, dirty_sha = git_state()

    (rd / "command.txt").write_text(" ".join(cmd) + "\n")
    env = {
        "operating_system": "Darwin 24.6.0 arm64",
        "architecture": "arm64",
        "host": "Adams-MacBook-Pro.local",
        "sage_version": "10.9",
        "python_runtime": "Sage Python",
        "field_backend": "Sage Matrix_mod2_dense/M4RI",
        "sage_cache": str(WS / "experiments" / EXP / "runtime" / "sage"),
        "resource_wrapper": "/usr/bin/time -l, approved outside sandbox for sysctl receipt",
        "timezone": "America/Los_Angeles",
    }
    (rd / "environment.json").write_text(json.dumps(env, indent=1) + "\n")

    started = time.time()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started))
    out_f = open(rd / "stdout.log", "wb")
    err_f = open(rd / "stderr.log", "wb")
    proc = subprocess.Popen(cmd, cwd=WS, stdout=out_f, stderr=err_f,
                            start_new_session=True)
    timed_out = False
    try:
        proc.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
    out_f.close(); err_f.close()
    finished_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    wall = time.time() - started

    # peak RSS from /usr/bin/time -l output on stderr
    peak_rss = None
    try:
        for line in open(rd / "stderr.log", errors="replace"):
            if "maximum resident set size" in line:
                peak_rss = int(line.split()[0])
    except Exception:
        pass

    metrics = {}
    mf = args.metrics_from
    if mf and (rd / mf).exists():
        try:
            metrics = json.load(open(rd / mf))
        except Exception:
            metrics = {}

    valid_path_ok = bool(args.valid_if) and (rd / args.valid_if).exists()
    if timed_out:
        status, valid, reason = "censored_timeout", None, (
            f"watchdog {args.timeout:.0f}s fired; checkpoint preserved; "
            "infrastructure censoring, not evidence (AGENTS rule 5)")
    elif proc.returncode != 0:
        status, valid, reason = "failed_infrastructure", False, (
            f"exit code {proc.returncode}; see stderr.log")
    elif valid_path_ok:
        status, valid, reason = "completed_valid", True, None
    else:
        status, valid, reason = "completed_unverified", None, (
            "process exited 0 but expected result artifact missing")

    artifacts = {"stdout": "stdout.log", "stderr": "stderr.log"}
    hashes = {}
    for name in ("stdout.log", "stderr.log"):
        hashes[name.split(".")[0]] = sha256_file(rd / name)
    if mf and (rd / mf).exists():
        artifacts["raw_result"] = mf
        hashes["raw_result"] = sha256_file(rd / mf)
    artifacts["sha256"] = hashes

    man = {
        "run": {
            "id": args.run_id,
            "experiment_id": EXP,
            "status": status,
            "purpose": args.purpose,
            "protocol_version": 1,
            "code": {
                "commit": commit, "dirty": dirty,
                "dirty_status_sha256": dirty_sha,
                "command_file": "command.txt",
            },
            "environment": {"file": "environment.json"},
            "inputs": json.loads(args.inputs),
            "expected": json.loads(args.expected),
            "timing": {
                "started_at": started_utc, "finished_at": finished_utc,
                "wall_seconds": round(wall, 2),
            },
            "resources": {"peak_rss_bytes": peak_rss},
            "result": {
                "metrics": metrics, "valid": valid, "invalid_reason": reason,
            },
            "artifacts": artifacts,
        }
    }

    def emit(d, ind=0):
        lines = []
        for k, v in d.items():
            pad = "  " * ind
            if isinstance(v, dict):
                lines.append(f"{pad}{k}:")
                lines.extend(emit(v, ind + 1))
            else:
                s = json.dumps(v) if not isinstance(v, (int, float)) else str(v)
                lines.append(f"{pad}{k}: {s}")
        return lines

    (rd / "manifest.yaml").write_text("\n".join(emit(man)) + "\n")
    print(json.dumps({"run_id": args.run_id, "status": status,
                      "wall_seconds": round(wall, 1),
                      "peak_rss_bytes": peak_rss, "metrics": metrics}))


if __name__ == "__main__":
    main()
