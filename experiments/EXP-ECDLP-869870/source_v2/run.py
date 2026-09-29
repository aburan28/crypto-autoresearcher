"""Run wrapper for EXP-ECDLP-869870 v2: one immutable run directory,
3600 s wall and 8 GB RLIMIT_AS, stdout/stderr, peak RSS, manifest.yaml.
Refuses to overwrite an existing run directory.

Usage: python3 run.py --run-id RUN-... --script run_generic_exact.py --kind fixture -- -- <args>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = "EXP-ECDLP-869870"
RUNS = os.environ.get("EXP869870_RUNS_DIR") or os.path.join(REPO, "experiments", EXP, "runs")
WALL_LIMIT = 3600
MEM_LIMIT = 8 * 1024 ** 3
TASK = "TASK-20260907-fe3512"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


def git_state():
    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain", "--untracked-files=all")
    lines = [l for l in status.splitlines() if l.strip()]
    return commit, bool(lines), lines


def inference_block():
    """Requested policy and the model that actually answered this session.

    Not a copied v1 claude-sonnet / claude-fable block. Adapter resolve and
    session self-report are recorded separately; no probe was run.
    """
    adapter_line = None
    adapter_model = None
    adapter_backend = None
    try:
        r = subprocess.run(
            [sys.executable, "-m", "orchestration.adapter", "resolve", "--role", "executor"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        adapter_line = (r.stdout or r.stderr or "").strip().splitlines()[-1] if (r.stdout or r.stderr) else None
        if adapter_line and "->" in adapter_line:
            rhs = adapter_line.split("->", 1)[1].strip()
            # e.g. anthropic:claude-sonnet-5 (effort=medium)
            left = rhs.split()[0]
            if ":" in left:
                adapter_backend, adapter_model = left.split(":", 1)
            else:
                adapter_model = left
    except Exception as e:
        adapter_line = f"adapter resolve failed: {e}"

    session_model = "Cursor Grok 4.6"
    return {
        "requested_policy": "executor-implementation",
        "canonical_policy": "executor-implementation",
        "requested_reasoning_effort": "medium",
        "reasoning_effort": "medium",
        "runtime": "cursor",
        "backend": "cursor",
        "adapter_resolve_stdout": adapter_line,
        "adapter_resolved_backend": adapter_backend,
        "adapter_resolved_model_id": adapter_model,
        "binding_model_id": adapter_model,
        "resolved_model_id": session_model,
        "model_provenance": (
            "self-reported by the executing session (system prompt: "
            "'You are Cursor Grok 4.6'); adapter resolve recorded separately; "
            "not probe-verified"
        ),
        "model_verified": False,
        "probe_run": False,
        "fallback_used": False,
        "fallback_reason": (
            "handoff fallback_allowed is false; this session did not select a "
            "different policy or backend. requested_policy remains "
            "executor-implementation. adapter resolve names "
            f"{adapter_backend}:{adapter_model}; the session that answered is "
            f"{session_model}. both are recorded; neither is substituted."
        ),
        "degraded_requirements": [],
        "independent_session": True,
        "compute_note": (
            "the numbers in this run come from deterministic code "
            "(source_v2/ at the pinned hashes); no model is in the compute loop"
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--kind", required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("--extra-input", action="append", default=[])
    ap.add_argument("args", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    script_args = [x for x in a.args if x != "--"]
    run_dir = os.path.join(RUNS, a.run_id)
    if os.path.exists(run_dir):
        print(f"REFUSED: run directory exists (immutable): {run_dir}", file=sys.stderr)
        sys.exit(3)
    os.makedirs(run_dir)
    cmd = [sys.executable, os.path.join(HERE, a.script), *script_args, "--out", run_dir]
    cmd_str = " ".join(cmd)
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write(cmd_str + "\n")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1", PYTHONHASHSEED="0")
    commit, dirty, dirty_files = git_state()
    src_files = sorted(f for f in os.listdir(HERE) if f.endswith(".py") or f.endswith(".md"))
    src_hashes = {f: sha256(os.path.join(HERE, f)) for f in src_files if os.path.isfile(os.path.join(HERE, f))}
    environment = {
        "operating_system": platform.platform(), "architecture": platform.machine(),
        "python_version": platform.python_version(), "numpy_version": np.__version__,
        "pyyaml_version": yaml.__version__, "sage_version": None,
        "cpu_count": os.cpu_count(), "threads": "single (OMP/OPENBLAS/MKL=1)",
        "host_memory_note": "4 cores / 15 GiB host; per-run cap 8 GB RLIMIT_AS, 3600 s wall",
        "env_limits": {"wall_clock_seconds": WALL_LIMIT, "memory_bytes_rlimit_as": MEM_LIMIT},
    }
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(environment, fh, indent=1)

    def preexec():
        resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))

    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    out = open(os.path.join(run_dir, "stdout.log"), "wb")
    err = open(os.path.join(run_dir, "stderr.log"), "wb")
    proc = subprocess.Popen(cmd, stdout=out, stderr=err, env=env, cwd=HERE, preexec_fn=preexec)
    timed_out = False
    while True:
        try:
            pid, status, ru = os.wait4(proc.pid, os.WNOHANG)
        except ChildProcessError:
            pid, status, ru = proc.pid, 0, None
        if pid != 0:
            break
        if time.time() - t0 > WALL_LIMIT:
            proc.kill()
            timed_out = True
            pid, status, ru = os.wait4(proc.pid, 0)
            break
        time.sleep(0.5)
    wall = time.time() - t0
    finished = datetime.now(timezone.utc).isoformat()
    out.close()
    err.close()
    exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else -os.WTERMSIG(status)
    peak_rss = ru.ru_maxrss * 1024 if ru else None
    cpu = (ru.ru_utime + ru.ru_stime) if ru else None

    summary_path = os.path.join(run_dir, "summary.json")
    raw_path = os.path.join(run_dir, "raw-result.json")
    status_s, invalid_reason, failure_class = "completed_valid", None, None
    if timed_out:
        status_s, failure_class = "failed_infrastructure", "resource_exhaustion"
        invalid_reason = f"wall clock exceeded {WALL_LIMIT} s; killed (never a result)"
    elif exit_code != 0:
        # OOM typically SIGKILL (-9) under RLIMIT_AS
        if exit_code in (-9, 137) or (peak_rss and peak_rss > MEM_LIMIT):
            status_s, failure_class = "failed_infrastructure", "resource_exhaustion"
            invalid_reason = f"compute process exited with {exit_code} (OOM/signal); never a result"
        else:
            status_s, failure_class = "failed_infrastructure", "infrastructure_error"
            invalid_reason = f"compute process exited with {exit_code} (see stderr.log); never a result"
    elif not (os.path.exists(summary_path) and os.path.exists(raw_path)):
        status_s, failure_class = "failed_infrastructure", "infrastructure_error"
        invalid_reason = "compute process produced no summary/raw output"
    header = {}
    if status_s == "completed_valid":
        with open(summary_path) as fh:
            header = json.load(fh).get("header", {})
        inv = header.get("invalidity", {})
        if inv.get("completed_invalid"):
            status_s, failure_class = "completed_invalid", "implementation_error"
            invalid_reason = "invalidation rule fired: " + "; ".join(
                k for k, v in inv.items() if v and k != "completed_invalid"
            )
        if peak_rss and peak_rss > MEM_LIMIT:
            status_s, failure_class = "failed_infrastructure", "resource_exhaustion"
            invalid_reason = "peak RSS above the 8 GB ceiling"
    artifacts = {f: sha256(os.path.join(run_dir, f)) for f in sorted(os.listdir(run_dir))}
    manifest = {"run": {
        "id": a.run_id, "experiment_id": EXP, "task_id": TASK, "kind": a.kind, "status": status_s,
        "failure_class": failure_class, "note": a.note,
        "protocol": "PA-ECDLP-869870-v1-to-v2",
        "code": {"commit": commit, "dirty": dirty,
                 "dirty_tree_files_this_experiment": [l for l in dirty_files if f"experiments/{EXP}" in l],
                 "dirty_tree_other_entries_count": len([l for l in dirty_files if f"experiments/{EXP}" not in l]),
                 "dirty_tree_other_entries_sample": [l for l in dirty_files if f"experiments/{EXP}" not in l][:10],
                 "command": cmd_str, "source_dir": f"experiments/{EXP}/source_v2",
                 "source_sha256": src_hashes,
                 "source_note": "source_v2 files are written by TASK-20260907-fe3512; v1 source/ is untouched"},
        "inference": inference_block(),
        "environment": environment,
        "inputs": {"curve_id": None, "seed": header.get("seed"), "seeds": header.get("seeds"),
                   "mixer": header.get("mixer"),
                   "walk_projection": header.get("walk_projection"),
                   "walk_key_K": header.get("walk_key_K"),
                   "dp_key_K2": header.get("dp_key_K2"),
                   "walk_key_string": header.get("walk_key_string"),
                   "dp_key_string": header.get("dp_key_string"),
                   "parameters": {k: header.get(k) for k in (
                       "stage", "log2N", "N", "T", "a", "a_grid", "r_grid", "M_online", "bits_per_entry"
                   ) if k in header},
                   "script_args": script_args, "extra_inputs": a.extra_input,
                   "contract": f"experiments/{EXP}/amendments/v2_rekeyed_fixture.yaml (PA-ECDLP-869870-v1-to-v2, approved)",
                   "v1_specification_read_only": f"experiments/{EXP}/specification.yaml (version 1, never edited)"},
        "timing": {"started_at": started, "finished_at": finished, "wall_seconds": wall,
                   "wall_clock_limit_seconds": WALL_LIMIT, "timed_out": timed_out},
        "resources": {"peak_rss_bytes": peak_rss, "cpu_seconds": cpu, "memory_limit_bytes": MEM_LIMIT,
                      "exit_code": exit_code},
        "result": {"valid": status_s == "completed_valid", "invalid_reason": invalid_reason,
                   "certificate": header.get("certificate", {"kind": "none", "verified": None, "verifier": None}),
                   "invalidity_checks": header.get("invalidity"),
                   "metrics_location": "summary.json (per cell); raw-result.json (raw)"},
        "artifacts": artifacts,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }}
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100)

    # Thin receipt.yaml (handoff deliverable name) pointing at the same numbers.
    receipt = {
        "run_id": a.run_id,
        "status": status_s,
        "failure_class": failure_class,
        "invalid_reason": invalid_reason,
        "mixer": header.get("mixer"),
        "seed": header.get("seed"),
        "walk_projection": header.get("walk_projection"),
        "walk_key_K": header.get("walk_key_K"),
        "dp_key_K2": header.get("dp_key_K2"),
        "walk_key_string": header.get("walk_key_string"),
        "dp_key_string": header.get("dp_key_string"),
        "wall_seconds": wall,
        "peak_rss_bytes": peak_rss,
        "metrics_from": "summary.json",
        "manifest": "manifest.yaml",
    }
    if status_s == "completed_valid" and os.path.exists(summary_path):
        with open(summary_path) as fh:
            cell = json.load(fh)["cells"]["a=0.25"]
        fx = cell["fixture"]
        receipt.update({
            "scaled_cost_sampled": fx["scaled_cost_sampled_this_seed"],
            "scaled_cost_exact_expectation": fx["scaled_cost_exact_expectation"],
            "scaled_P": fx["scaled_precomp_measured"],
            "top_T_share_8W": cell["global_oracle"]["top_T_share_8W"],
            "top_T_share_20W": cell["global_oracle"]["top_T_share_20W"],
            "cycle_mass": cell["cycle_mass"],
            "capped_mass_8W": cell["capped_mass_8W"],
            "capped_mass_20W": cell["capped_mass_20W"],
            "residual_cost_raw": fx["residual_sampled_minus_published_raw"],
            "o_theta_correction_status": fx["o_theta_correction"]["status"],
        })
        with open(os.path.join(run_dir, "results.json"), "w") as fh:
            json.dump({"header": header, "fixture": fx,
                       "global_oracle": cell["global_oracle"],
                       "cycle_mass": cell["cycle_mass"],
                       "capped_mass_8W": cell["capped_mass_8W"],
                       "capped_mass_20W": cell["capped_mass_20W"]}, fh, indent=1)
    with open(os.path.join(run_dir, "receipt.yaml"), "w") as fh:
        yaml.safe_dump(receipt, fh, sort_keys=False, width=100)
    # Re-hash after receipt.yaml is written so artifacts stay complete.
    artifacts = {f: sha256(os.path.join(run_dir, f)) for f in sorted(os.listdir(run_dir))}
    manifest["run"]["artifacts"] = artifacts
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100)

    print(f"{a.run_id}: {status_s} wall={wall:.1f}s rss={peak_rss} cpu={cpu}")
    sys.exit(0 if status_s.startswith("completed") else 1)


if __name__ == "__main__":
    main()
