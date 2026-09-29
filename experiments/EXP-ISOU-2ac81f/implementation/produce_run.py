#!/usr/bin/env python3
"""
CLI entry point: executes one census run and writes the full immutable run
record (manifest.yaml, command.txt, environment.json, stdout.log,
stderr.log, raw-result.json) under experiments/EXP-ISOU-2ac81f/runs/<run-id>/.

Usage: python3 produce_run.py <bit_length> <A|B> <RUN-ID> <output_root>
"""
import json
import os
import platform
import subprocess
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(__file__))

import run_census as rc

REPO_ROOT = "/home/user/crypto-autoresearcher"


def git_info():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO_ROOT).decode()
    dirty = len(status.strip()) > 0
    return commit, dirty, status


def main():
    bit_length = int(sys.argv[1])
    instance_label = sys.argv[2]
    run_id = sys.argv[3]
    output_root = sys.argv[4]

    run_dir = os.path.join(output_root, run_id)
    os.makedirs(run_dir, exist_ok=True)

    commit, dirty, status_text = git_info()

    command_str = f"python3 experiments/EXP-ISOU-2ac81f/implementation/produce_run.py {bit_length} {instance_label} {run_id} {output_root}"
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(command_str + "\n")

    environment = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "dependencies": {"stdlib_only": True, "no_sympy": True, "no_numpy": True, "no_gmpy2": True},
    }
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(environment, f, indent=2)

    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.time()
    stderr_lines = []
    try:
        raw_result, log = rc.run_census(bit_length, instance_label, run_id, run_dir)
        stdout_lines = log["stdout"]
        error = None
    except Exception as e:
        stdout_lines = []
        stderr_lines.append(traceback.format_exc())
        raw_result = {"terminal_status": "implementation_error", "error": str(e)}
        error = e
    wall = time.time() - t0
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        f.write("\n".join(stdout_lines) + "\n")
    with open(os.path.join(run_dir, "stderr.log"), "w") as f:
        f.write("\n".join(stderr_lines) + "\n")
    with open(os.path.join(run_dir, "raw-result.json"), "w") as f:
        json.dump(raw_result, f, indent=2, default=str)

    terminal_status = raw_result.get("terminal_status", "implementation_error")
    manifest_status_map = {
        "completed_valid": "completed_valid",
        "completed_incomplete_subgraph": "invalid_measurement",
        "invalid_measurement": "invalid_measurement",
        "budget_exhausted": "budget_exhausted",
        "implementation_error": "implementation_error",
    }
    manifest_status = manifest_status_map.get(terminal_status, "invalid_measurement")

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-ISOU-2ac81f",
            "status": manifest_status,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "dirty_detail": status_text.strip().splitlines() if dirty else [],
                "command": command_str,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "backend": None,
                "provider": None,
                "resolved_model_id": (
                    "the resolved session model under this Claude Code harness "
                    "(model: inherit); not independently probe-verified from "
                    "this session."
                ),
                "model_provenance": "unbound",
                "model_verified": False,
                "requested_reasoning_effort": "medium",
                "reasoning_effort": "medium",
                "fallback_used": True,
                "fallback_reason": (
                    "Policy aliases do not resolve to distinct models under "
                    "this Claude Code harness (CLAUDE.md 'Model policy note'); "
                    "no model was in this run's compute loop at all -- this is "
                    "a deterministic arithmetic run, not an LLM-mediated "
                    "measurement. Recorded rather than silently substituted."
                ),
                "degraded_requirements": [],
                "independent_session": False,
                "adapter_version": None,
                "config_digest": None,
            },
            "environment": environment,
            "inputs": {
                "curve_id": f"EXP-ISOU-2ac81f/{bit_length}bit/instance-{instance_label}",
                "seed": rc.BASE_CURVE_SEED.get(bit_length),
                "parameters": {
                    "bit_length": bit_length,
                    "instance_label": instance_label,
                    "isogeny_degrees": [2, 3, 5, 7, 11, 13],
                    "replication_seeds": rc.SEEDS,
                    "primary_seed": rc.PRIMARY_SEED,
                    "k_seed": rc.K_SEED.get(instance_label),
                    "base_curve_selection_seed": rc.BASE_CURVE_SEED.get(bit_length),
                    "null_object_seed": rc.NULL_OBJECT_SEED.get(bit_length),
                    "multiplier_schedule_seed": rc.MULTIPLIER_SCHEDULE_SEED,
                    "r_partitions": rc.R_PARTITIONS,
                    "per_solve_time_budget_seconds": rc.PER_SOLVE_TIME_BUDGET_S,
                },
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": wall,
            },
            "resources": {
                "peak_rss_bytes": None,
                "cpu_seconds": wall,
            },
            "result": {
                "metrics": {
                    "terminal_status": terminal_status,
                    "terminal_status_reasons": raw_result.get("terminal_status_reasons", []),
                    "class_number_h": raw_result.get("class_number_h"),
                    "walk_vertex_count": raw_result.get("walk_vertex_count"),
                    "completeness_ok": raw_result.get("completeness_ok"),
                    "null_object_separated": (raw_result.get("null_object_separation") or {}).get("separated"),
                },
                "valid": manifest_status == "completed_valid",
                "invalid_reason": None if manifest_status == "completed_valid" else terminal_status,
                "certificate": {
                    "kind": "discrete_log",
                    "verified": None,
                    "verifier": "certificate.py:verify_dlp_solution (independent re-implementation, no shared code path with rho_solver.py)",
                },
            },
            "artifacts": {
                "manifest": "manifest.yaml",
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "raw_result": "raw-result.json",
            },
        }
    }

    def yaml_dump_simple(obj, indent=0):
        # Minimal, dependency-free YAML emitter (no pyyaml available).
        lines = []
        pad = "  " * indent
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)) and v not in ({}, []):
                    lines.append(f"{pad}{k}:")
                    lines.extend(yaml_dump_simple(v, indent + 1))
                elif isinstance(v, (dict, list)):
                    lines.append(f"{pad}{k}: {'{}' if isinstance(v, dict) else '[]'}")
                else:
                    lines.append(f"{pad}{k}: {yaml_scalar(v)}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(yaml_dump_simple(item, indent + 1))
                else:
                    lines.append(f"{pad}- {yaml_scalar(item)}")
        return lines

    def yaml_scalar(v):
        if v is None:
            return "null"
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            if any(c in v for c in [":", "#", "\n"]) or v == "":
                return json.dumps(v)
            return v
        return str(v)

    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        f.write("\n".join(yaml_dump_simple(manifest)) + "\n")

    print(f"RUN {run_id} terminal_status={terminal_status} wall={wall:.2f}s")
    if error:
        raise error


if __name__ == "__main__":
    main()
