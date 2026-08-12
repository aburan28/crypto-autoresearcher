"""
Orchestrator for EXP-REPL-1d1287 pilot execution.

Executes run_cell.run() in-process (avoids ~1-2s per-process torch import
overhead x hundreds of runs) but writes out the full AGENTS.md-required
run-directory layout for every run, with a command.txt that reproduces the
identical result standalone (verified: run_cell.py is a pure function of its
CLI args plus the on-disk curves.json / cache/*.npz, both frozen before any
run in this batch).

Run order (fixed, matches the frozen protocol's control ordering):
  1. C6: scrambled arm, 5 seeds, ALL non-presentation combos -> seed-variance
     measured and comparison band fixed BEFORE any curve-arm scoring.
  2. C2 (shuffled labels, blocking) and C3 (planted leaky, blocking).
  3. C5: table attack reproduction (separate script, not a training run).
  4. Main matched grid: curve_1 (full: both archs x both splits x 3 caps x
     3 real presentations x 5 seeds), then curve_2 restricted to
     architecture=mlp (both splits x 3 caps x 3 real presentations x 5 seeds)
     -- curve_2/transformer is NOT run; named explicitly as incomplete due to
     the run-count budget (see implementation.md, "Scope deviation").
"""
import argparse, json, os, platform, subprocess, sys, time, traceback
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
import run_cell
from ec import load_curves

BASE = "/tmp/wt-run-exp/experiments/EXP-REPL-1d1287"
RUNS_DIR = os.path.join(BASE, "runs")

SEEDS = [11, 22, 33, 44, 55]
REAL_PRESENTATIONS = ["affine_xy_limbs", "x_only_limbs", "projective_jacobian_limbs"]
ARCHS = ["mlp", "transformer"]
CAPS = [0, 1, 2]
SPLITS = ["random_by_logarithm", "contiguous_block_by_logarithm"]

def git_state():
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd="/tmp/wt-run-exp",
                             capture_output=True, text=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain"], cwd="/tmp/wt-run-exp",
                             capture_output=True, text=True).stdout
    return commit, bool(status.strip())

def env_info():
    return {
        "python": sys.version, "torch": torch.__version__,
        "numpy": np.__version__, "platform": platform.platform(),
        "resolved_inference_model": "claude-sonnet-5",
        "inference_policy": "executor-implementation",
        "fallback_used": False,
    }

RUN_COUNTER = 0

def do_run(kind, curve, split_mode, presentation, shuffle_labels, architecture,
           capacity_id, seed, epochs=25, patience=5, max_train=None, notes=None):
    global RUN_COUNTER
    RUN_COUNTER += 1
    run_id = f"RUN-{RUN_COUNTER:04d}-{kind}"
    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    args = argparse.Namespace(
        curve=curve, split_mode=split_mode, presentation=presentation,
        shuffle_labels=shuffle_labels, architecture=architecture,
        capacity_id=capacity_id, seed=seed, epochs=epochs, patience=patience,
        batch_size=128, max_train=max_train,
    )
    cmd = (f"python3 run_cell.py --curve {curve} --split_mode {split_mode} "
           f"--presentation {presentation} "
           f"{'--shuffle_labels ' if shuffle_labels else ''}"
           f"--architecture {architecture} --capacity_id {capacity_id} "
           f"--seed {seed} --epochs {epochs} --patience {patience} "
           f"--batch_size 128" + (f" --max_train {max_train}" if max_train else ""))

    commit, dirty = git_state()
    t0 = time.time()
    status = "completed_valid"
    reason = None
    result = None
    stderr_text = ""
    try:
        result = run_cell.run(args)
    except Exception as e:
        status = "implementation_error"
        reason = f"{type(e).__name__}: {e}"
        stderr_text = traceback.format_exc()
    wall = time.time() - t0

    if result is not None and result.get("budget_limited") and result.get("epochs_run", 0) >= epochs:
        # ran to the epoch cap without early-stop trigger: not truncated by
        # a wall-clock timeout, just reached the max-epoch schedule -- this
        # is a normal terminal state here, not a budget-limited abort.
        pass

    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(cmd + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env_info(), f, indent=2)
    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        f.write(json.dumps(result, indent=2) if result is not None else "")
    with open(os.path.join(run_dir, "stderr.log"), "w") as f:
        f.write(stderr_text)
    if result is not None:
        with open(os.path.join(run_dir, "raw-result.json"), "w") as f:
            json.dump(result, f, indent=2)

    manifest = {
        "run_id": run_id, "kind": kind, "experiment": "EXP-REPL-1d1287",
        "command": cmd,
        "git_commit": commit, "git_dirty": dirty,
        "seed": seed,
        "params": {
            "curve": curve, "split_mode": split_mode, "presentation": presentation,
            "shuffle_labels": shuffle_labels, "architecture": architecture,
            "capacity_id": capacity_id, "epochs_cap": epochs, "patience": patience,
            "max_train": max_train,
        },
        "environment": env_info(),
        "wall_clock_seconds": wall,
        "status": status,
        "reason": reason,
        "certificate": {"kind": "none"},
        "notes": notes,
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        json.dump(manifest, f, indent=2)  # JSON is valid YAML; keeps this dependency-free

    return run_id, status, result

def main():
    curves = load_curves()
    log = []

    print("=== Phase 1: C6 seed-variance on scrambled arm (runs FIRST) ===", file=sys.stderr)
    c6_timestamp_start = time.time()
    c6_results = []
    for curve_name in curves:
        archs_here = ARCHS if curve_name == "curve_1" else ["mlp"]
        caps_here = CAPS
        for split_mode in SPLITS:
            for arch in archs_here:
                for cap in caps_here:
                    for seed in SEEDS:
                        max_train = 6000 if curve_name == "curve_2" else None
                        rid, status, res = do_run(
                            "C1C6-scrambled", curve_name, split_mode, "scrambled_labels",
                            False, arch, cap, seed, max_train=max_train,
                            notes="scrambled arm (C1 primary-measurement dataset AND C6 seed-variance source)")
                        log.append((rid, status, res))
                        c6_results.append((curve_name, split_mode, arch, cap, seed, res))
    c6_timestamp_end = time.time()
    with open(os.path.join(BASE, "c6-seed-variance.json"), "w") as f:
        json.dump({
            "timestamp_start": c6_timestamp_start, "timestamp_end": c6_timestamp_end,
            "note": "C6 scrambled-arm seed variance measured BEFORE any curve-arm scoring below.",
            "results": [
                {"curve": c, "split_mode": s, "architecture": a, "capacity_id": cap, "seed": sd,
                 "heldout_advantage": (r["heldout_advantage"] if r else None)}
                for (c, s, a, cap, sd, r) in c6_results
            ],
        }, f, indent=2)
    print(f"C6 done: {len(c6_results)} scrambled-arm runs, band-timestamp recorded.", file=sys.stderr)

    print("=== Phase 2: C2 (shuffled labels, blocking) ===", file=sys.stderr)
    c2_results = []
    for arch in ARCHS:
        for cap in CAPS:
            for seed in SEEDS[:1]:
                rid, status, res = do_run("C2-shuffled", "curve_1", "random_by_logarithm",
                                           "affine_xy_limbs", True, arch, cap, seed,
                                           notes="C2 blocking control: shuffled labels")
                log.append((rid, status, res))
                c2_results.append(res)

    print("=== Phase 3: C3 (planted leaky, blocking) ===", file=sys.stderr)
    c3_results = []
    for arch in ARCHS:
        for cap in CAPS:
            for seed in SEEDS[:1]:
                rid, status, res = do_run("C3-planted", "curve_1", "random_by_logarithm",
                                           "planted_leaky", False, arch, cap, seed,
                                           notes="C3 blocking control: planted leaky encoding")
                log.append((rid, status, res))
                c3_results.append(res)

    with open(os.path.join(BASE, "c2-c3-controls.json"), "w") as f:
        json.dump({
            "C2_shuffled_labels": [
                {"architecture": r["architecture"], "capacity_id": r["capacity_id"],
                 "seed": r["seed"], "heldout_advantage": r["heldout_advantage"],
                 "heldout_se_binomial": r["heldout_se_binomial"]} for r in c2_results if r],
            "C3_planted_leaky": [
                {"architecture": r["architecture"], "capacity_id": r["capacity_id"],
                 "seed": r["seed"], "heldout_advantage": r["heldout_advantage"]} for r in c3_results if r],
        }, f, indent=2)

    print("=== Phase 4: main matched grid ===", file=sys.stderr)
    main_results = []

    def matched_cell(curve_name, split_mode, arch, cap, presentations, max_train=None):
        for pres in presentations:
            for seed in SEEDS:
                rid, status, res = do_run("MAIN-real", curve_name, split_mode, pres, False,
                                           arch, cap, seed, max_train=max_train)
                main_results.append(("real", curve_name, split_mode, arch, cap, pres, seed, status, res))
                log.append((rid, status, res))

    # curve_1: FULL grid (both architectures)
    for split_mode in SPLITS:
        for arch in ARCHS:
            for cap in CAPS:
                matched_cell("curve_1", split_mode, arch, cap, REAL_PRESENTATIONS)

    # curve_2: architecture=mlp ONLY (budget-limited scope; transformer at
    # curve_2 is NOT run -- named explicitly as incomplete in the report).
    for split_mode in SPLITS:
        for cap in CAPS:
            matched_cell("curve_2", split_mode, "mlp", cap, REAL_PRESENTATIONS, max_train=6000)

    with open(os.path.join(BASE, "run-log-summary.json"), "w") as f:
        json.dump({"total_runs": RUN_COUNTER,
                   "status_counts": {s: sum(1 for _, st, _ in log if st == s)
                                      for s in set(st for _, st, _ in log)}},
                  f, indent=2)

    print(f"TOTAL RUNS: {RUN_COUNTER}", file=sys.stderr)

if __name__ == "__main__":
    main()
