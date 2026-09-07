"""Driver for RUN-RELN-82f487-N14-sigma8-seed2 (TASK-20260907-8b29e0):
identical logic to source/run_full_cell.py, with ONLY the
(curve_index_j, curve_seed, base_seed, training_seed) substituted per
specification.yaml's replication.seeds second triple (102/202/302), per the
handoff's instruction to reuse source/ as-is and not rewrite it. This file
lives in the run directory (not source/) precisely because it is a
parameter substitution, not a protocol or implementation change; every
function it calls is imported unchanged from experiments/EXP-RELN-82f487/source/.

Rung=2^14 (curve_index_j=2, matching curve_seeds[1]=102 by the same
index-to-seed convention curve_gen.py and run_full_cell.py already use for
the first triple: index j=1 <-> seed 101), sigma=1/8, all five arms, both
model classes, both feature regimes (F0, F1), label-permutation null with
training_seed 302 (this cell's own training seed, per spec's
label_permutation_null construction: "training seed 301 only" documents
that the FIRST cell's permutation null uses seed 301; this cell is a
distinct replicate and uses its own training_seed 302 throughout,
consistent with run_cell.run_arm_cell's do_permutation_null argument,
which is unconditional on which training_seed is passed in -- the same
code path the first cell used).
"""
import json
import os
import sys
import time

_RUN_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.abspath(os.path.join(_RUN_DIR, "..", "..", "source"))
_REPO_ROOT = os.path.abspath(os.path.join(_RUN_DIR, "..", "..", "..", ".."))
sys.path.insert(0, _SRC_DIR)
sys.path.insert(0, _REPO_ROOT)
import numpy as np
from harness.toycurve import EllipticCurve
import curve_gen
import enumerate_counts as ec
import run_cell as rc

RUNG_K = 14
CURVE_INDEX_J = 2
CURVE_SEED = 102
BASE_SEED = 202
TRAINING_SEED = 302
SIGMA = 0.125


def to_jsonable(o):
    if isinstance(o, dict):
        return {k: to_jsonable(v) for k, v in o.items() if k != "model"}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    t_start = time.time()
    log_lines = []

    def log(msg):
        line = f"[{time.time()-t_start:8.1f}s] {msg}"
        print(line, flush=True)
        log_lines.append(line)

    curve_rec = curve_gen.generate_curve(RUNG_K, CURVE_INDEX_J, CURVE_SEED)
    log(f"curve generated: {curve_rec}")
    curve = EllipticCurve(curve_rec["p"], curve_rec["a"], curve_rec["b"])
    N = curve_rec["N"]
    B_eff = ec.b_eff_for_N(N)
    log(f"B_eff={B_eff} B={2*B_eff} N={N} p={curve_rec['p']}")

    t0 = time.time()
    pts = ec.all_curve_points(curve)
    log(f"enumerated {len(pts)} curve points in {time.time()-t0:.1f}s")
    points_by_x = {}
    for (x, y) in pts:
        points_by_x.setdefault(x, []).append((x, y))

    with open(os.path.join(out_dir, "curve.json"), "w") as f:
        json.dump(curve_rec, f, indent=2)

    all_results = {}
    for arm in rc.ARMS:
        arm_path = os.path.join(out_dir, f"arm_{arm}.json")
        if os.path.exists(arm_path):
            log(f"arm {arm}: already computed, skipping")
            with open(arm_path) as f:
                all_results[arm] = json.load(f)
            continue
        log(f"=== arm {arm}: starting ===")
        t_arm = time.time()
        result = rc.run_arm_cell(
            arm, curve, curve_rec, points_by_x, pts, B_eff, BASE_SEED, TRAINING_SEED, SIGMA,
            regimes=("F0", "F1"), classes=("gnn", "trees"),
            epochs=100, n_boot=1000, n_null_draws=1000,
            run_gnn_lr_grid=(1e-3, 3e-3), node_shuffle_seed=501,
            do_permutation_null=True, log=log,
        )
        jr = to_jsonable(result)
        with open(arm_path, "w") as f:
            json.dump(jr, f, indent=2)
        all_results[arm] = jr
        log(f"=== arm {arm}: done in {time.time()-t_arm:.1f}s ===")

    with open(os.path.join(out_dir, "all_arms.json"), "w") as f:
        json.dump(all_results, f, indent=2)

    try:
        er = all_results["E_random_matched"]["regimes"]["F0"]["model_metrics"]
        zr = all_results["ZN_random"]["regimes"]["F0"]["model_metrics"]
        log(f"E/random vs Z/N-random (F0): E_random={er}, ZN_random={zr}")
    except Exception as e:
        log(f"comparison failed: {e}")

    with open(os.path.join(out_dir, "run_log.txt"), "w") as f:
        f.write("\n".join(log_lines))

    log("MAIN CELL COMPLETE")


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/run_full_cell_seed2_out"
    main(out_dir)
