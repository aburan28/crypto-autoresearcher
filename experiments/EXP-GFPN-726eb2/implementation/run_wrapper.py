#!/usr/bin/env python3
"""Run-package wrapper for EXP-GFPN-726eb2.

Usage: run_wrapper.py RUN-ID CURVE_ID -- <command ...>

Creates experiments/EXP-GFPN-726eb2/runs/<RUN-ID>/ (refuses to overwrite an
existing run directory: run records are immutable), records command.txt,
environment.json (tool versions, git commit, dirty state), runs the command
capturing stdout.log / stderr.log, wall time and peak RSS of the child, copies
the command's JSON result (the command must write raw-result.json into the run
directory via $GFPN_RUN_DIR) and writes manifest.yaml.

The manifest `status` is taken from raw-result.json's top-level
"run_status" (completed_valid | failed | invalid) and "failure_class"; the
wrapper never invents a status: a crashed command is recorded as failed /
infrastructure_error with the exit code.
"""
import json, os, platform, resource, subprocess, sys, time, datetime, shutil
import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EXP = "EXP-GFPN-726eb2"
RUNS = os.path.join(REPO, "experiments", EXP, "runs")

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:  # recorded, never hidden
        return f"ERROR: {e}"

def environment():
    return {
        "operating_system": platform.platform(),
        "kernel": sh("uname -r"),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "sage_note": "Sage is not installed on this host; PARI/GP is used directly (gp + cypari2).",
        "dependencies": {
            "pari_gp": sh("gp --version-short 2>&1 | head -1"),
            "cypari2": sh("pip show cypari2 2>/dev/null | grep -i '^version' | cut -d' ' -f2"),
            "pari_seadata": sh("ls /usr/share/pari/seadata 2>/dev/null | wc -l") + " files (apt pari-seadata, installed 2026-09-21 by this task)",
            "gmp_ecm": sh("dpkg -s gmp-ecm 2>/dev/null | grep '^Version' | cut -d' ' -f2") + " (apt gmp-ecm, installed 2026-09-21 by this task)",
            "sympy": sh("python3 -c 'import sympy;print(sympy.__version__)'"),
            "pyyaml": sh("python3 -c 'import yaml;print(yaml.__version__)'"),
            "msolve": sh("msolve -h 2>&1 | head -1"),
        },
        "cpu": sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(),
        "nproc": os.cpu_count(),
        "mem_total_kb": sh("grep MemTotal /proc/meminfo | awk '{print $2}'"),
        "git": {
            "commit": sh(f"git -C {REPO} rev-parse HEAD"),
            "branch": sh(f"git -C {REPO} branch --show-current"),
            "dirty_paths": [l for l in sh(f"git -C {REPO} status --porcelain").splitlines() if l.strip()],
        },
    }

def main():
    argv = sys.argv[1:]
    run_id, curve_id = argv[0], argv[1]
    assert argv[2] == "--"
    cmd = argv[3:]
    run_dir = os.path.join(RUNS, run_id)
    if os.path.exists(run_dir):
        print(f"REFUSING: run directory exists (immutable): {run_dir}", file=sys.stderr)
        return 2
    os.makedirs(os.path.join(run_dir, "certificates"))
    env = environment()
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=2)
    cmd_str = " ".join(cmd)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(f"# cwd: {REPO}\n# GFPN_RUN_DIR={run_dir}\n{cmd_str}\n")
    child_env = dict(os.environ, GFPN_RUN_DIR=run_dir, PYTHONHASHSEED="0")
    started = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.time()
    with open(os.path.join(run_dir, "stdout.log"), "w") as so, open(os.path.join(run_dir, "stderr.log"), "w") as se:
        proc = subprocess.run(cmd, cwd=REPO, env=child_env, stdout=so, stderr=se)
    wall = time.time() - t0
    finished = datetime.datetime.now(datetime.timezone.utc)
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    raw_path = os.path.join(run_dir, "raw-result.json")
    raw = None
    if os.path.exists(raw_path):
        try:
            raw = json.load(open(raw_path))
        except Exception as e:
            raw = {"run_status": "failed", "failure_class": "implementation_error",
                   "note": f"raw-result.json unparseable: {e}"}
    if raw is None:
        raw = {"run_status": "failed", "failure_class": "infrastructure_error",
               "note": f"command exited {proc.returncode} without writing raw-result.json"}
        json.dump(raw, open(raw_path, "w"), indent=2)
    status = raw.get("run_status", "failed")
    if proc.returncode != 0 and status == "completed_valid":
        status = "failed"; raw.setdefault("failure_class", "infrastructure_error")
    manifest = {"run": {
        "id": run_id,
        "experiment_id": EXP,
        "status": status,
        "failure_class": raw.get("failure_class"),
        "hypothesis_id": "H-GFPN-ee4d45",
        "task_id": "TASK-20260920-d78326",
        "claim_tier": "observational",
        "code": {
            "commit": env["git"]["commit"],
            "dirty": bool(env["git"]["dirty_paths"]),
            "dirty_note": ("Untracked/modified paths at run time are the experiment's own "
                           "implementation and run artifacts written by this task (listed in "
                           "environment.json git.dirty_paths); no other path was modified."
                           if env["git"]["dirty_paths"] else None),
            "command": cmd_str,
            "wrapper": "experiments/EXP-GFPN-726eb2/implementation/run_wrapper.py",
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "canonical_policy": "executor-implementation",
            "backend": "anthropic",
            "provider": "anthropic",
            "resolved_model_id": "claude-sonnet-5",
            "resolved_by": "python3 -m orchestration.adapter resolve --role executor (2026-09-21): executor-implementation -> anthropic:claude-sonnet-5 (effort=medium)",
            "session_model_self_reported": "claude-fable-5-1",
            "model_provenance": "operator-supplied",
            "model_verified": False,
            "requested_reasoning_effort": "medium",
            "reasoning_effort": "medium",
            "fallback_used": False,
            "fallback_reason": None,
            "degraded_requirements": [],
            "independent_session": False,
            "adapter_version": None,
            "config_digest": None,
            "note": ("The run's numbers come from deterministic code (PARI/GP, GMP-ECM, pure Python); "
                     "no model is in the arithmetic loop. The model recorded here is the Executor "
                     "session that wrote and launched the scripts. The runtime self-reports a "
                     "different model id than the adapter resolves; both are recorded, neither is "
                     "substituted. Not Amazon Bedrock."),
        },
        "environment": {k: env[k] for k in ("operating_system", "architecture", "python_version", "sage_version", "dependencies")},
        "inputs": {
            "curve_id": curve_id,
            "seed": raw.get("seed"),
            "parameters": raw.get("parameters", {}),
            "sources": raw.get("sources", []),
        },
        "timing": {
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "wall_seconds": round(wall, 3),
        },
        "resources": {
            "peak_rss_bytes": ru.ru_maxrss * 1024,
            "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 3),
            "memory_cap_gb": 8,
        },
        "result": {
            "metrics": raw.get("metrics", {}),
            "valid": status == "completed_valid",
            "invalid_reason": raw.get("invalid_reason"),
            "exit_code": proc.returncode,
            "certificate": {
                "kind": "none",
                "verified": None,
                "verifier": None,
                "note": ("Pure parameter audit (docs/claims-and-verification.md): no discrete-log, "
                         "decomposition or key-recovery certificate is claimed. Regenerated "
                         "order / factorization / primality artifacts are audit certificates "
                         "stored under certificates/ and re-verified by independent code."),
            },
        },
        "artifacts": {
            "raw_result": "raw-result.json",
            "audit_table": "audit-table.yaml",
            "figure_provenance": "figure-provenance.yaml",
            "certificates_dir": "certificates/",
            "stdout": "stdout.log", "stderr": "stderr.log",
        },
    }}
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False, width=100)
    print(f"{run_id}: status={status} wall={wall:.1f}s exit={proc.returncode} dir={run_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
