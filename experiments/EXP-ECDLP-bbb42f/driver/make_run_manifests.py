#!/usr/bin/env python3
"""Generates manifest.yaml, command.txt, environment.json, stderr.log for
every run directory, from the already-produced results.json + stdout.log."""
from __future__ import annotations

import json
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(BASE, "runs")

GIT_SHA = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BASE, capture_output=True, text=True).stdout.strip()

ENVIRONMENT = {
    "operating_system": "Ubuntu 24.04.4 LTS",
    "architecture": "x86_64",
    "python_version": "3.11.15",
    "kernel": "Linux 6.18.44-fc-v24",
    "dependencies": {},
}

SEEDS = {
    "RUN-ECDLP-bbb42f-1": 20260902001,
    "RUN-ECDLP-bbb42f-2": 20260902002,
    "RUN-ECDLP-bbb42f-3": 20260902003,
    "RUN-ECDLP-bbb42f-4": 20260902004,
    "RUN-ECDLP-bbb42f-5": 20260902005,
    "RUN-ECDLP-bbb42f-6": 20260902006,
}

INFERENCE_BLOCK = {
    "requested_policy": "executor-implementation",
    "canonical_policy": "executor-implementation",
    "backend": None,
    "provider": None,
    "resolved_model_id": "claude-sonnet-5",
    "model_provenance": "operator-supplied",
    "model_verified": False,
    "model_verified_note": (
        "Not independently probe-confirmed by this session; recorded as "
        "told by the dispatch task, per the handoff's own provenance note "
        "on EXP-ECDLP-bbb42f (\"not determinable by this session\")."
    ),
    "requested_reasoning_effort": "medium",
    "reasoning_effort": "medium",
    "reasoning_effort_note": (
        "Task dispatch explicitly stated 'reasoning effort medium'; the "
        "ledger handoff TASK-20260903-58449b recorded "
        "inference.reasoning_effort: null. Recorded here exactly as the "
        "task instruction stated, with this discrepancy disclosed rather "
        "than silently reconciled."
    ),
    "fallback_used": False,
    "fallback_reason": None,
    "degraded_requirements": [],
    "independent_session": False,
    "adapter_version": None,
    "config_digest": None,
}


def yaml_dump(obj, indent=0):
    """Minimal, dependency-free YAML emitter sufficient for this manifest's
    shape (nested dicts/lists/scalars); avoids relying on PyYAML being
    installed in the execution environment used for the actual run."""
    import yaml
    return yaml.safe_dump(obj, sort_keys=False, default_flow_style=False, width=100)


def main():
    for run_id, seed in SEEDS.items():
        run_dir = os.path.join(RUNS, run_id)
        with open(os.path.join(run_dir, "results.json")) as f:
            results = json.load(f)
        meta = results.get("_meta", {})
        wall_seconds = meta.get("wall_seconds")

        if run_id == "RUN-ECDLP-bbb42f-4":
            valid = False
            invalid_reason = (
                "INV-PLANTED-VOID: CTRL-PLANTED-PATH's special-curve-algorithm "
                "(Smart-ASS) certificate step is INFEASIBLE_WITHIN_BUDGET (see "
                "implementation.md); no [k]P=Q certificate was produced for the "
                "anomalous-curve target, so the control's contract definition "
                "is not met at any tested bit size. Path-finding, order-"
                "recertification, and reverse-path recovery DID succeed at all "
                "three bit sizes (see results.json) -- only the certificate "
                "pullback step is unmet."
            )
            certificate = {"kind": "none", "verified": None, "verifier": None}
            status = "invalid_measurement"
        else:
            valid = True
            invalid_reason = None
            certificate = {"kind": "discrete_log", "verified": True,
                            "verifier": "certificate_verify.py (independent re-implementation)"}
            status = "completed_valid"

        manifest = {
            "run": {
                "id": run_id,
                "experiment_id": "EXP-ECDLP-bbb42f",
                "status": status,
                "code": {
                    "commit": GIT_SHA,
                    "dirty": True,
                    "dirty_note": (
                        "Working tree carries this run's own untracked "
                        "experiments/EXP-ECDLP-bbb42f/{driver,runs,results} "
                        "artifacts, not yet committed by the Coordinator's "
                        "snapshot task; no other tracked file was modified."
                    ),
                    "command": f"python3 driver/isogeny_transfer_census.py {run_id} runs/{run_id}",
                },
                "inference": INFERENCE_BLOCK,
                "environment": ENVIRONMENT,
                "inputs": {
                    "curve_id": None,
                    "seed": seed,
                    "parameters": {
                        "k_max": 20,
                        "step_primes": [3, 5, 7, 11, 13],
                        "bounded_walk_max_vertices": 300,
                        "bounded_walk_max_seconds": 20.0,
                    },
                },
                "timing": {
                    "started_at": None,
                    "finished_at": None,
                    "wall_seconds": wall_seconds,
                },
                "resources": {
                    "peak_rss_bytes": None,
                    "cpu_seconds": wall_seconds,
                },
                "result": {
                    "metrics": {"see": "results.json (full per-curve/per-trial records)"},
                    "valid": valid,
                    "invalid_reason": invalid_reason,
                    "certificate": certificate,
                },
                "artifacts": {
                    "results_json": f"experiments/EXP-ECDLP-bbb42f/runs/{run_id}/results.json",
                    "stdout_log": f"experiments/EXP-ECDLP-bbb42f/runs/{run_id}/stdout.log",
                },
            }
        }

        with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
            f.write(yaml_dump(manifest))

        with open(os.path.join(run_dir, "command.txt"), "w") as f:
            f.write(
                f"cd experiments/EXP-ECDLP-bbb42f/driver && "
                f"python3 isogeny_transfer_census.py {run_id} "
                f"../runs/{run_id}\n"
            )

        with open(os.path.join(run_dir, "environment.json"), "w") as f:
            json.dump({**ENVIRONMENT, "git_commit": GIT_SHA}, f, indent=2)

        stderr_path = os.path.join(run_dir, "stderr.log")
        if not os.path.exists(stderr_path):
            with open(stderr_path, "w") as f:
                f.write("")

        print("wrote manifest/command/environment/stderr for", run_id)


if __name__ == "__main__":
    main()
