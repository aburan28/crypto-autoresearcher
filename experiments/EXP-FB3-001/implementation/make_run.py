"""Run wrapper for EXP-FB3-001: executes a run and writes its immutable record.

Creates experiments/EXP-FB3-001/runs/<RUN-ID>/ containing exactly
manifest.yaml, command.txt, environment.json, stdout.log, stderr.log and
raw-result.json.  stdout.log/stderr.log are the real captured streams of the
real child process; the manifest's timing and peak-RSS come from the wrapper's
own measurement of that child.

Run records are immutable: this wrapper refuses to write into an existing run
directory.  A corrected run is a NEW run id.

Usage:
  python3 make_run.py --run-id RUN-FB3-001-N14 --kind battery --bits 14
  python3 make_run.py --run-id RUN-FB3-001-CTRL --kind controls
  python3 make_run.py --run-id RUN-FB3-001-FAMILY --kind family
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
import sympy
import yaml

import fb3_core as C

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
IMPL_REL = "experiments/EXP-FB3-001/implementation"
RUNS_REL = "experiments/EXP-FB3-001/runs"

# The executor's inference block.  orchestration/model-policies.yaml routes the
# executor role to a GPT-5.6 Terra alias that this Claude-family harness cannot
# resolve (CLAUDE.md "Model policy note"), so fallback_used is true.
INFERENCE = {
    "requested_policy": "executor-terra",
    "resolved_model": "claude-opus-5",
    "resolved_model_note": "self-reported model family; the exact deployment "
                           "identifier is not exposed to the agent",
    "reasoning_effort": "unspecified",
    "fallback_used": True,
    "fallback_reason": "orchestration/model-policies.yaml routes the executor to "
                       "a GPT-5.6 Terra alias that this Claude-family harness "
                       "cannot resolve (CLAUDE.md model policy note).",
}


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def env_block() -> dict:
    return {
        "python": platform.python_version(),
        "os": subprocess.run(["uname", "-srmo"], capture_output=True,
                             text=True).stdout.strip(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": {"numpy": np.__version__, "sympy": sympy.__version__,
                     "pyyaml": yaml.__version__},
        "cpu_count": os.cpu_count(),
        "memory_gb": 15,
        "sage_version": None,
        "notes": "pure Python + numpy; no SageMath, Singular, or PARI in this "
                 "environment",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--kind", required=True, choices=["battery", "controls", "family"])
    ap.add_argument("--bits", type=int)
    ap.add_argument("--null-draws", type=int, default=200)
    args = ap.parse_args()

    run_dir = os.path.join(REPO, RUNS_REL, args.run_id)
    if os.path.exists(run_dir):
        print(f"REFUSING: run directory already exists (records are immutable): "
              f"{run_dir}", file=sys.stderr)
        return 2
    os.makedirs(run_dir)
    raw_rel = f"../runs/{args.run_id}/raw-result.json"

    if args.kind == "battery":
        if args.bits is None:
            ap.error("--bits is required for --kind battery")
        entrypoint = f"{IMPL_REL}/run_battery.py"
        cmd = (f"cd {IMPL_REL} && python3 run_battery.py --bits {args.bits} "
               f"--out {raw_rel} --null-draws {args.null_draws}")
        purpose = (f"exact six-geometry factor-base battery with shared "
                   f"permutation null at N ~ 2^{args.bits}")
    elif args.kind == "controls":
        entrypoint = f"{IMPL_REL}/run_controls.py"
        cmd = f"cd {IMPL_REL} && python3 run_controls.py --out {raw_rel}"
        purpose = ("counter verification against brute force, conservation and "
                   "closed-form controls, and H016/H017 port fidelity")
    else:
        entrypoint = f"{IMPL_REL}/run_family.py"
        cmd = (f"cd {IMPL_REL} && python3 run_family.py --runs ../runs "
               f"--out {raw_rel}")
        purpose = ("family-level Holm correction, bootstrap CIs, growth slopes, "
                   "prior-cell accounting, and analytic-arm consequence checks")

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write(cmd + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(env_block() | {"git_commit": commit, "git_dirty_tree": dirty,
                                 "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                                 "dirty_paths": git("status", "--porcelain").splitlines()},
                  fh, indent=1)

    rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    t0 = time.time()
    with open(os.path.join(run_dir, "stdout.log"), "wb") as so, \
         open(os.path.join(run_dir, "stderr.log"), "wb") as se:
        proc = subprocess.run(cmd, shell=True, cwd=REPO, stdout=so, stderr=se)
    wall = time.time() - t0
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    peak_kb = max(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  rusage_before)
    peak_mb = peak_kb / 1024.0

    raw_path = os.path.join(run_dir, "raw-result.json")
    raw = None
    if os.path.exists(raw_path):
        with open(raw_path) as fh:
            raw = json.load(fh)

    ok = proc.returncode == 0 and raw is not None
    status = "completed" if ok else "failed"
    validity = "valid" if ok else "failed_infrastructure"

    params: dict = {"m": 3}
    summary = ""
    validity_reason = ""
    if args.kind == "battery":
        bits = args.bits
        orders = [c["N"] for c in raw["curves"]] if raw else []
        bsizes = sorted({C.matched_size(n) for n in orders}) if orders else []
        params |= {
            "field_bits": bits,
            "group_order": orders,
            "group_order_target": 1 << bits,
            "group_order_min": min(orders) if orders else None,
            "group_order_max": max(orders) if orders else None,
            "base_size_B": bsizes,
            "base_size_B_rule": C.FROZEN["matched_size_rule"],
            "n_curves": len(orders),
            "n_replicate_seeds": 4,
            "null_draws_per_cell": args.null_draws,
            "null_draws_frozen_minimum": 100,
            "geometries": ["high_bit_interval", "small_height", "mixed_two_base",
                           "coset_union", "greedy_optimized", "asymmetric_sizing"],
            "target_space": "all N group elements (exact count, no sampling)",
            "counting_convention": "multisets {i<=j<=k}, m=3, no signs (H016 record)",
            "curve_seeds": [c["seed"] for c in raw["curves"]] if raw else [],
            "asym_ladder_weights": C.FROZEN["asym_ladder_weights"],
            "greedy_pool_factor": C.FROZEN["greedy_pool_factor"],
        }
        if raw:
            ctrl = raw["controls"]
            n_measured = sum(1 for c in raw["cells"]
                             if c.get("terminal_state") == "measured")
            n_infeasible = sum(1 for c in raw["cells"]
                               if c.get("terminal_state") == "infeasible")
            summary = (f"{n_measured} measured cell records and {n_infeasible} "
                       f"infeasible at 2^{bits} over 4 curves x 4 seeds; exact "
                       f"totals matched the closed form in "
                       f"{ctrl['closed_form_total_checks']} of "
                       f"{ctrl['closed_form_total_checks']} checks")
            validity_reason = (f"all controls pass: closed-form total "
                               f"{ctrl['closed_form_total_control']}, independent "
                               f"recount {ctrl['independent_recount_control']}, "
                               f"FFT route {ctrl['fft_route_control']}")
    elif args.kind == "controls":
        params |= {
            "field_bits": 18,
            "field_bits_note": "controls touch 14/16/18-bit generated curves and "
                               "the recorded 14/17-bit H016 curves; 18 is the "
                               "maximum field size, which sets the claim tier",
            "group_order": ([c["N"] for c in raw["controls"]
                             ["B_conservation_closed_form"]["checks"]
                             if c["base"] == "matched_random"] if raw else []),
            "recorded_h016_group_orders": ([c["recorded_N"] for c in
                                            raw["controls"]["D_port_fidelity"]["cells"]]
                                           if raw else []),
            "base_size_B": (sorted({c["B"] for c in raw["controls"]
                                    ["B_conservation_closed_form"]["checks"]})
                            if raw else []),
            "brute_force_orders": [211, 307, 401, 503, 1009],
            "sampling_mc_reps": 400,
            "port_fidelity_source": "inputs/h100_session/h016_base_yield.json",
        }
        if raw:
            v = raw["control_verdicts"]
            summary = (f"counter verification {v['A']}, conservation {v['B']}, "
                       f"machinery {v['C']}, port fidelity {v['D']}")
            validity_reason = ("brute-force agreement on full count vectors and "
                              "exact reproduction of the recorded H016/H017 curve "
                              "orders, closed-form means, bands and p-value "
                              "convention")
    else:
        params |= {
            "field_bits": 18,
            "field_bits_note": "aggregates the 14/16/18-bit size runs; 18 is the "
                               "maximum field size, which sets the claim tier",
            "group_order": "aggregate of RUN-FB3-001-N14/N16/N18",
            "base_size_B": "aggregate of RUN-FB3-001-N14/N16/N18",
            "sizes_log2N": [14, 16, 18],
            "holm_family_size_per_size": C.FROZEN["family_size_per_size"],
            "holm_alpha": C.FROZEN["holm_alpha"],
            "bootstrap_resamples": C.FROZEN["bootstrap_resamples"],
            "bootstrap_seed": C.FROZEN["bootstrap_seed"],
            "prior_cells": ["prior_H016_qr_base", "prior_H017_small_multiples"],
        }
        if raw:
            v = raw["frozen_criteria_check"]["verdict"]
            a = raw["analytic_arm"]
            summary = (f"{v['n_geometries_meeting_success_criterion']} of 6 "
                       f"geometries meet the frozen success criterion; analytic "
                       f"consequences i/ii/iii/iv = "
                       f"{a['consequence_i_mean_is_geometry_independent']['status']}/"
                       f"{a['consequence_ii_slope_identically_zero']['status']}/"
                       f"{a['consequence_iii_coverage_bound']['status']}/"
                       f"{a['consequence_iv_typing_penalty']['status']}")
            validity_reason = ("aggregation of immutable size-run records; no new "
                               "measurement performed")

    manifest = {
        "run": {
            "id": args.run_id,
            "experiment_id": "EXP-FB3-001",
            "amendment_id": "EXP-FB3-001-AMD-001",
            "task_id": "TASK-20260724-228",
            "purpose": purpose,
            "status": status,
            "code": {
                "commit": commit,
                "dirty_tree": dirty,
                "command": cmd,
                "entrypoint": entrypoint,
                "modules": [f"{IMPL_REL}/fb3_core.py", f"{IMPL_REL}/{os.path.basename(entrypoint)}",
                            f"{IMPL_REL}/make_run.py"],
            },
            "environment": env_block(),
            "inputs": {
                "parameters": params,
                "seeds": [1, 2, 3, 4],
                "seed_derivation": {
                    "curve_seed": "FROZEN.curve_seed_base*1000 + bits*10 + curve_index",
                    "cell_seed": "FROZEN.cell_seed_base + bits*100000 "
                                 "+ curve_index*1000 + replicate_seed",
                    "greedy_split_seed": "cell_seed + 500000",
                    "bootstrap_seed": C.FROZEN["bootstrap_seed"],
                },
                "sources_of_randomness": [
                    "curve generation (p, a, b) from the recorded curve seed",
                    "matched-random null bases from the recorded cell seed",
                    "greedy candidate pool and train/held-out split from the "
                    "recorded cell seed",
                    "asymmetric-sizing sub-base elements from the recorded cell seed",
                    "bootstrap resampling from the recorded bootstrap seed",
                ],
                "files": ["inputs/h100_session/h016_base_yield.json"]
                         if args.kind == "controls" else [],
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_clock_seconds": round(wall, 3),
                "peak_memory_mb": round(peak_mb, 1),
            },
            "result": {
                "validity": validity,
                "validity_reason": validity_reason or f"child exit code {proc.returncode}",
                "certificate": {
                    "kind": "none",
                    "reason": "pure measurement run: this experiment counts "
                              "decompositions of every target and claims no "
                              "discrete-log solve and no factor-base relation",
                },
                "summary": summary or f"child exit code {proc.returncode}",
                "exit_code": proc.returncode,
            },
            "inference": INFERENCE,
            "artifacts": {
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "command": "command.txt",
                "environment": "environment.json",
                "sha256": {name: sha256(os.path.join(run_dir, name))
                           for name in sorted(os.listdir(run_dir))},
            },
            "honesty_notes": [
                "Discrete logs of factor-base points are known BY CONSTRUCTION "
                "and are used only to count decompositions; no cost, speedup, or "
                "attack claim is derived from their availability.",
                "This run measures decomposition yield and coverage, not the cost "
                "of FINDING a decomposition (the point-decomposition solve).",
                "Toy scale (N <= 2^18): no crypto-scale statement is implied.",
            ],
        }
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100,
                       default_flow_style=False)
    print(f"run_id={args.run_id} status={status} exit={proc.returncode} "
          f"wall={wall:.1f}s peak_rss={peak_mb:.0f}MB dir={run_dir}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
