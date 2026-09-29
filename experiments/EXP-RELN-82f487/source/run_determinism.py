"""Shuffled-seed determinism re-run (specification.yaml's
shuffled_seed_determinism_rerun control): the cell (2^14, curve 1, base seed
201, ALL ARMS, BOTH CLASSES, F0) re-run twice -- once with every seed
unchanged (501), once with only the node-shuffle seed changed (501 -> 502)
-- REUSING the main run's selected hyperparameters (not re-selecting on the
validation split a second/third time; still "the identical model" per the
spec's own wording, and much cheaper).
"""
import json
import os
import sys
import time

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_SRC_DIR, "..", "..", ".."))
sys.path.insert(0, _SRC_DIR)
sys.path.insert(0, _REPO_ROOT)

import numpy as np
from harness.toycurve import EllipticCurve
import curve_gen
import enumerate_counts as ec
import run_cell as rc
from run_full_cell import to_jsonable, RUNG_K, CURVE_INDEX_J, CURVE_SEED, BASE_SEED, TRAINING_SEED, SIGMA


def main(all_arms_path, out_path):
    with open(all_arms_path) as f:
        all_arms = json.load(f)

    curve_rec = curve_gen.generate_curve(RUNG_K, CURVE_INDEX_J, CURVE_SEED)
    curve = EllipticCurve(curve_rec["p"], curve_rec["a"], curve_rec["b"])
    N = curve_rec["N"]
    B_eff = ec.b_eff_for_N(N)
    pts = ec.all_curve_points(curve)
    points_by_x = {}
    for (x, y) in pts:
        points_by_x.setdefault(x, []).append((x, y))

    out = {}
    t0 = time.time()
    for arm in rc.ARMS:
        f0 = all_arms[arm]["regimes"]["F0"]
        gnn_params = f0["model_metrics"]["gnn"]["model_card"]["params"]
        tree_params = f0["model_metrics"]["trees"]["model_card"]["params"]
        variants = {}
        for label, nshuf in [("unchanged_501", 501), ("variant_502", 502)]:
            r = rc.run_arm_cell(
                arm, curve, curve_rec, points_by_x, pts, B_eff, BASE_SEED, TRAINING_SEED, SIGMA,
                regimes=("F0",), classes=("gnn", "trees"),
                epochs=100, n_boot=200, n_null_draws=1000,
                fixed_gnn_lr=gnn_params.get("learning_rate", 1e-3),
                fixed_tree_params=tree_params,
                node_shuffle_seed=nshuf, do_permutation_null=False,
            )
            variants[label] = to_jsonable(r)
            print(f"[{time.time()-t0:.1f}s] arm={arm} variant={label} done")
        out[arm] = variants
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
