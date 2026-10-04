#!/usr/bin/env python3
"""Complete the run package of a run whose wrapper was killed with its child.

Run records are immutable and are never deleted or re-keyed. When the Executor
stops a run deliberately (or the host kills it), the wrapper cannot write its
manifest, which would leave an orphan directory that no checker can read. This
utility closes such a directory out as an explicitly FAILED run, carrying the
reason, whatever partial progress the run's own stdout.log shows, and the same
required artifact set as any other run package. Nothing is claimed from it.

Usage: close_terminated_run.py RUN-DIR --reason TEXT --class CLASS [--kind KIND]
"""
import argparse, datetime, json, os, re, sys
import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

INFERENCE = {
    "requested_policy": "executor-implementation", "canonical_policy": "executor-implementation",
    "backend": "anthropic", "provider": "anthropic", "resolved_model_id": "claude-sonnet-5",
    "resolved_by": ("python3 -m orchestration.adapter resolve --role executor (2026-09-21): "
                    "executor-implementation -> anthropic:claude-sonnet-5 (effort=medium)"),
    "session_model_self_reported": "claude-opus-5", "model_provenance": "operator-supplied",
    "model_verified": False, "requested_reasoning_effort": "medium", "reasoning_effort": "medium",
    "fallback_used": False, "fallback_reason": None, "degraded_requirements": [],
    "independent_session": False, "adapter_version": None, "config_digest": None,
    "note": ("Deterministic code produced any numbers here (msolve, python-flint, PARI/GP, pure Python); "
             "no model is in the arithmetic loop. The model recorded is the Executor session that launched "
             "the run. Not Amazon Bedrock."),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--class", dest="fclass", required=True,
                    choices=["infrastructure_error", "resource_exhaustion", "implementation_error"])
    ap.add_argument("--kind", default="cell")
    ap.add_argument("--cell", default=None)
    a = ap.parse_args()
    rd = os.path.abspath(a.run_dir)
    rid = os.path.basename(rd.rstrip("/"))
    if os.path.exists(os.path.join(rd, "manifest.yaml")):
        print(f"REFUSING: {rid} already has a manifest (run records are immutable)", file=sys.stderr)
        return 2
    env = json.load(open(os.path.join(rd, "environment.json")))
    stdout_path = os.path.join(rd, "stdout.log")
    lines = open(stdout_path).read().splitlines() if os.path.exists(stdout_path) else []
    progress = [l for l in lines if " target " in l or "NOT MEASURED" in l or "built" in l or "EARLY STOP" in l]
    not_measured = []
    for l in lines:
        mm = re.search(r"target (\d+) NOT MEASURED (\w+) (\w+) ([\d.]+)", l)
        if mm:
            not_measured.append({"target": int(mm.group(1)), "class": mm.group(2), "outcome": mm.group(3),
                                 "wall_seconds": float(mm.group(4)),
                                 "rule": ("specification stopping rule: an m=5 timeout or OOM is NOT MEASURED "
                                          "and is never evidence that D is large")})
    raw = {
        "run_status": "failed", "failure_class": a.fclass, "kind": a.kind,
        "cell": a.cell, "invalid_reason": a.reason, "note": a.reason,
        "parameters": {"closed_out_by": "implementation/close_terminated_run.py",
                       "closed_out_note": ("the wrapper was killed together with its child, so this package was "
                                           "completed from the run's own stdout.log and environment.json")},
        "seeds": None, "sources": [], "targets": [], "certificates": [],
        "not_measured": not_measured, "partial_progress": progress,
        "metrics": {"targets_attempted": 0, "targets_not_measured": len(not_measured),
                    "terminated_before_completion": True,
                    "not_measured_outcomes": sorted({x["outcome"] for x in not_measured})},
        "certificate": {"kind": "none", "verified": None, "verifier": None,
                        "note": "terminated run; no decomposition accepted or claimed"},
    }
    json.dump(raw, open(os.path.join(rd, "raw-result.json"), "w"), indent=1)
    cmd = open(os.path.join(rd, "command.txt")).read().strip().splitlines()[-1]
    manifest = {"run": {
        "id": rid, "experiment_id": "EXP-GFPN-05ff43", "status": "failed", "failure_class": a.fclass,
        "hypothesis_id": "H-GFPN-9a29be", "task_id": "TASK-20260920-dd8205", "claim_tier": "toy",
        "cell": a.cell or a.kind,
        "code": {"commit": env["git"]["commit"], "dirty": bool(env["git"]["dirty_paths"]),
                 "dirty_note": ("Untracked/modified paths at run time are the experiment's own implementation and "
                                "run artifacts written by this task; no other path was modified."),
                 "command": cmd, "wrapper": "experiments/EXP-GFPN-05ff43/implementation/run_wrapper.py",
                 "manifest_written_by": "experiments/EXP-GFPN-05ff43/implementation/close_terminated_run.py"},
        "inference": dict(INFERENCE),
        "environment": {k: env[k] for k in ("operating_system", "architecture", "python_version", "sage_version", "dependencies")},
        "inputs": {"cell": a.cell or a.kind, "seeds": None, "parameters": raw["parameters"], "sources": []},
        "timing": {"started_at": (lines[0].split()[0] if lines else None), "finished_at": None,
                   "wall_seconds": None,
                   "timing_note": "wrapper killed with its child; times are those in the run's own stdout.log"},
        "resources": {"peak_rss_bytes": None, "cpu_seconds": None, "memory_cap_gb": 11, "watchdog": None},
        "result": {"metrics": raw["metrics"], "valid": False, "invalid_reason": a.reason, "exit_code": -9,
                   "certificate": raw["certificate"], "not_measured": not_measured},
        "artifacts": {"raw_result": "raw-result.json", "ladder_table": "ladder-table.yaml",
                      "heur_dflat": "heur-dflat.yaml", "cost_band_p64": "cost-band-p64.yaml",
                      "certificates_dir": "certificates/", "stdout": "stdout.log", "stderr": "stderr.log"},
    }}
    yaml.safe_dump(manifest, open(os.path.join(rd, "manifest.yaml"), "w"), sort_keys=False, width=100)
    note = f"terminated run ({a.fclass}); no ladder cell completed"
    yaml.safe_dump({"ladder_table": {"note": note, "rows": []}}, open(os.path.join(rd, "ladder-table.yaml"), "w"), sort_keys=False)
    yaml.safe_dump({"heur_dflat": {"heuristic": "HEUR-GFPN-DFLAT", "heur_dflat_pass": "not_applicable", "note": note}},
                   open(os.path.join(rd, "heur-dflat.yaml"), "w"), sort_keys=False)
    yaml.safe_dump({"cost_band_p64": {"status": "not_applicable_in_this_run", "note": note}},
                   open(os.path.join(rd, "cost-band-p64.yaml"), "w"), sort_keys=False)
    os.makedirs(os.path.join(rd, "certificates"), exist_ok=True)
    print(f"closed out {rid}: failed / {a.fclass}; {len(not_measured)} not_measured targets recorded")
    return 0

if __name__ == "__main__":
    sys.exit(main())
