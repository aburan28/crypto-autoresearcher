"""Run wrapper for EXP-ECDLP-612fb1: one immutable run directory per run.

Usage:
  python3 harness_run.py --run-id RUN-... --kind generic --n-bits 20 --a 1/4 --seed 1
  python3 harness_run.py --run-id RUN-... --kind analysis --stages G,1,2
  python3 harness_run.py --run-id RUN-... --kind curve-search
  python3 harness_run.py --run-id RUN-... --kind curve --seed 1

Writes manifest.yaml, command.txt, environment.json, stdout.log, stderr.log
and leaves raw-result.json / summary.json to the child.  Enforces the
per-run wall-clock ceiling (3600 s) with a hard kill; a timeout or crash is
recorded as failed_infrastructure, never as a result.  The run directory is
never overwritten: an existing directory refuses.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))
EXP_ID = "EXP-ECDLP-612fb1"
WALL_LIMIT = 3600
MEM_LIMIT_BYTES = 8 * (1 << 30)


def sh(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).stdout.strip()


def git_state():
    commit = sh(["git", "rev-parse", "HEAD"])
    status = sh(["git", "status", "--porcelain", "--untracked-files=all"])
    files = [l for l in status.splitlines() if l.strip()]
    tracked_dirty = [l for l in files if not l.startswith("??")]
    return {"commit": commit, "dirty": bool(tracked_dirty),
            "dirty_tracked_files": [l[3:] for l in tracked_dirty],
            "untracked_files_count": len([l for l in files if l.startswith("??")]),
            "untracked_under_this_experiment": [l[3:] for l in files if l.startswith("??") and EXP_ID in l],
            "branch": sh(["git", "branch", "--show-current"])}


def source_hashes():
    out = {}
    for name in sorted(os.listdir(HERE)):
        p = os.path.join(HERE, name)
        if os.path.isfile(p) and name.endswith(".py"):
            out[name] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def environment():
    import numpy
    env = {
        "operating_system": platform.platform(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "dependencies": {"numpy": numpy.__version__, "pyyaml": __import__("yaml").__version__},
        "cpu_model": None, "cpu_count": os.cpu_count(),
        "threads": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
        "workers": 1,
    }
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                env["cpu_model"] = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return env


def inference_block():
    return {
        "requested_policy": "executor-implementation",
        "canonical_policy": "executor-implementation",
        "backend": "anthropic",
        "provider": "anthropic",
        "runtime": "claude_code",
        "binding_model_for_policy": "claude-sonnet-5 (orchestration/model-bindings.yaml, anthropic backend; not probed)",
        "resolved_model_id": "claude-fable-5-1",
        "model_provenance": "operator-supplied",
        "model_verified": False,
        "model_note": ("self-reported by the executing subagent; the policy's capability requirements "
                       "(reasoning_effort medium, tool_use, structured_output, context >= 120k, output >= 24k) "
                       "are met; the binding's model name differs from the self-reported model and this is "
                       "disclosed rather than hidden"),
        "requested_reasoning_effort": "medium",
        "reasoning_effort": "medium",
        "fallback_used": False,
        "fallback_reason": None,
        "degraded_requirements": [],
        "independent_session": False,
        "adapter_version": "1.1.0",
        "config_digest": None,
        "harness_note": "the run itself is deterministic Python/NumPy; the model wrote and launched the code",
    }


def child_command(args):
    py = sys.executable
    if args.kind == "generic":
        return [py, os.path.join(HERE, "run_generic.py"), "--n-bits", str(args.n_bits), "--a", args.a,
                "--seed", str(args.seed), "--outdir", args.outdir]
    if args.kind == "analysis":
        return [py, os.path.join(HERE, "analysis.py"), "--runs-dir", os.path.join(EXP_DIR, "runs"),
                "--stages", args.stages, "--outdir", args.outdir, "--resamples", str(args.resamples)]
    if args.kind == "curve-search":
        return [py, os.path.join(HERE, "curve_search.py"), "--outdir", args.outdir]
    if args.kind == "curve":
        return [py, os.path.join(HERE, "run_curve.py"), "--seed", str(args.seed), "--curve-record",
                args.curve_record, "--outdir", args.outdir]
    raise SystemExit("unknown kind")


def validity(kind, outdir):
    """Apply the contract's validity rules to the child's summary.json."""
    sp = os.path.join(outdir, "summary.json")
    if not os.path.exists(sp):
        return False, "summary.json missing", {}
    s = json.load(open(sp))
    reasons = []
    if kind == "generic":
        ch = s.get("checks", {})
        bad0 = [k for k, v in ch.get("round0_identity", {}).items() if not v]
        if bad0:
            reasons.append(f"round-0 non-identity with STATIC twin: {bad0} (contract stopping rule 4)")
        badb = [k for k, v in ch.get("bit_identity_all_rounds", {}).items() if not v]
        if badb:
            reasons.append(f"NULL-B / PHI(0) not bit-identical to STATIC: {badb} (invalidation rule 4)")
        exc = [k for k, v in ch.get("exceedance", {}).items() if v.get("any_exact_exceedance")]
        if exc:
            reasons.append(f"exact coverage above exact top-T_sel share: {exc} (invalidation rule 6)")
        if s.get("walker_vs_exact_basins_agree") is False:
            reasons.append("vectorised walker disagrees with exact basin tables (implementation error)")
        badsel = [k for k, v in s.get("arms", {}).items() if not v.get("selector_verified_against_numpy", True)]
        if badsel:
            reasons.append(f"counted selector disagrees with numpy ordering: {badsel}")
        if ch.get("phi1_equals_resel_l_T/2") is False:
            reasons.append("PHI(1) differs from RESEL-L(T/2)")
    elif kind == "curve":
        c = s.get("certificates", {})
        if c.get("passed") != c.get("solved_total"):
            reasons.append("certificate pass count differs from solved count (invalidation rule 8)")
        if c.get("failed", 0):
            reasons.append("a certificate failed independent re-verification")
        if not c.get("seeded_log_all_match", False):
            reasons.append("a recovered logarithm differs from the seeded logarithm (checker read)")
        ch = s.get("checks", {})
        bad0 = [k for k, v in ch.get("round0_identity", {}).items() if not v]
        if bad0:
            reasons.append(f"round-0 non-identity: {bad0}")
        exc = [k for k, v in ch.get("exceedance", {}).items() if v.get("any_exact_exceedance")]
        if exc:
            reasons.append(f"exact coverage above exact top-T_sel share: {exc} (invalidation rule 6)")
        if s.get("walker_vs_exact_basins_agree") is False:
            reasons.append("vectorised curve walker disagrees with exact basin tables (implementation error)")
        badsel = [k for k, v in s.get("arms", {}).items() if not v.get("selector_verified_against_numpy", True)]
        if badsel:
            reasons.append(f"counted selector disagrees with numpy ordering: {badsel}")
    elif kind == "curve-search":
        if not s.get("verified"):
            reasons.append("curve record verification failed")
    metrics = s.get("headline_metrics", {})
    return (len(reasons) == 0), ("; ".join(reasons) if reasons else None), metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--kind", required=True, choices=["generic", "analysis", "curve-search", "curve"])
    ap.add_argument("--n-bits", type=int)
    ap.add_argument("--a", type=str)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--stages", type=str, default="G,1,2")
    ap.add_argument("--resamples", type=int, default=2000)
    ap.add_argument("--curve-record", type=str)
    ap.add_argument("--purpose", type=str, default="")
    ap.add_argument("--stage", type=str, default="")
    args = ap.parse_args()

    outdir = os.path.join(EXP_DIR, "runs", args.run_id)
    if os.path.exists(outdir):
        raise SystemExit(f"refusing to overwrite existing run directory {outdir}")
    os.makedirs(outdir)
    args.outdir = outdir
    cmd = child_command(args)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               PYTHONHASHSEED="0")
    rel_cmd = " ".join(c.replace(REPO + "/", "") for c in cmd)
    with open(os.path.join(outdir, "command.txt"), "w") as fh:
        fh.write(f"cd {REPO}\nOMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 "
                 f"timeout {WALL_LIMIT}s {rel_cmd}\n")
    gs = git_state()
    envd = environment()
    with open(os.path.join(outdir, "environment.json"), "w") as fh:
        json.dump({**envd, "git": gs, "source_sha256": source_hashes(),
                   "wall_limit_seconds": WALL_LIMIT, "memory_limit_bytes": MEM_LIMIT_BYTES}, fh, indent=1)

    started = dt.datetime.now(dt.timezone.utc)
    t0 = __import__("time").monotonic()
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT_BYTES, MEM_LIMIT_BYTES))

    status = "completed_valid"
    failure = None
    with open(os.path.join(outdir, "stdout.log"), "w") as so, open(os.path.join(outdir, "stderr.log"), "w") as se:
        try:
            proc = subprocess.run(cmd, cwd=REPO, env=env, stdout=so, stderr=se, timeout=WALL_LIMIT,
                                  preexec_fn=limits)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = None
            status = "failed_infrastructure"
            failure = f"wall clock exceeded {WALL_LIMIT} s; process killed (resource_exhaustion); NOT a result"
    wall = __import__("time").monotonic() - t0
    finished = dt.datetime.now(dt.timezone.utc)
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = r1.ru_maxrss * 1024
    cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
    if rc not in (0, None):
        status = "failed_infrastructure"
        failure = f"child exited with code {rc} (crash / dependency failure); NOT a result"
    valid, reason, metrics = (False, failure, {})
    if status == "completed_valid":
        valid, reason, metrics = validity(args.kind, outdir)
        if not valid:
            status = "completed_invalid"
    if not os.path.exists(os.path.join(outdir, "raw-result.json")):
        with open(os.path.join(outdir, "raw-result.json"), "w") as fh:
            json.dump({"status": status, "note": "child produced no raw result", "failure": failure}, fh)
    seeds = None
    params = {"kind": args.kind, "stage": args.stage}
    sp = os.path.join(outdir, "summary.json")
    if os.path.exists(sp):
        s = json.load(open(sp))
        if "params" in s:
            params.update({k: v for k, v in s["params"].items() if k != "seeds"})
            seeds = s["params"].get("seeds")
        if args.kind == "curve":
            params["field_bits"] = s.get("curve", {}).get("field_bits")
    cert = {"kind": "none", "verified": None, "verifier": None,
            "note": "pure measurement run; nothing is solved or certified"}
    if args.kind == "curve" and os.path.exists(sp):
        c = json.load(open(sp)).get("certificates", {})
        cert = {"kind": "discrete_log" if c.get("solved_total", 0) else "none",
                "verified": bool(c.get("passed", 0) == c.get("solved_total", -1) and not c.get("failed", 0)),
                "verifier": "verify_certificate.py (independent double-and-add, shares no code with the walk)",
                "verifier_commit": gs["commit"], "passed": c.get("passed"), "failed": c.get("failed"),
                "solved_total": c.get("solved_total"), "seeded_log_check_passed": c.get("seeded_log_passed")}
    manifest = {"run": {
        "id": args.run_id, "experiment_id": EXP_ID, "purpose": args.purpose, "stage": args.stage,
        "status": status,
        "code": {"commit": gs["commit"], "dirty": gs["dirty"], "dirty_tracked_files": gs["dirty_tracked_files"],
                 "untracked_under_this_experiment": gs["untracked_under_this_experiment"],
                 "branch": gs["branch"], "command": open(os.path.join(outdir, "command.txt")).read().strip(),
                 "source_sha256": source_hashes(),
                 "note": "source/ and runs/ are untracked new files at this commit (snapshot archive pending); "
                         "source files are hash-pinned above"},
        "inference": inference_block(),
        "environment": envd,
        "inputs": {"curve_id": None, "seed": args.seed, "seeds": seeds, "parameters": params},
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(),
                   "wall_seconds": round(wall, 3), "timing_source": "wrapper monotonic clock",
                   "wall_limit_seconds": WALL_LIMIT, "wall_within_limit": wall <= WALL_LIMIT},
        "resources": {"peak_rss_bytes": int(peak_rss), "cpu_seconds": round(cpu, 3),
                      "memory_limit_bytes": MEM_LIMIT_BYTES, "peak_rss_within_limit": peak_rss <= MEM_LIMIT_BYTES,
                      "workers": 1},
        "result": {"metrics": metrics, "valid": valid, "invalid_reason": reason,
                   "failure_class": (None if valid else ("resource_exhaustion" if rc is None else
                                     "infrastructure_error" if rc not in (0, None) else "invalid_measurement")),
                   "certificate": cert},
        "artifacts": {"command": "command.txt", "environment": "environment.json", "stdout": "stdout.log",
                      "stderr": "stderr.log", "raw_result": "raw-result.json", "summary": "summary.json"},
    }}
    for extra in ("cost_table.json", "basin_histogram.json.gz", "ci_tables.json", "analysis.md",
                  "curve_record.json", "certificates.json"):
        if os.path.exists(os.path.join(outdir, extra)):
            manifest["run"]["artifacts"][extra.split(".")[0]] = extra
    import yaml
    with open(os.path.join(outdir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, default_flow_style=False, width=100)
    print(f"{args.run_id}: {status} wall={wall:.1f}s cpu={cpu:.1f}s peak_rss={peak_rss/1e9:.2f}GB"
          + (f" reason={reason}" if reason else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
