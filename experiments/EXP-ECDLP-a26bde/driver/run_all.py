"""Top-level orchestration for EXP-ECDLP-a26bde: freezes the curve/prime
list (curves.py), runs Stage 2+3 on all 20 (curve, prime) instances
(stage23.py), and runs the dedicated anomalous-break instance on the frozen
anomalous curve. Writes one raw-result JSON per instance to the given
output directory; the calling shell wraps each in its own run directory
(manifest.yaml, command.txt, environment.json, stdout.log, stderr.log,
raw-result.json) per docs/task-lifecycle.md.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

from harness.toycurve import EllipticCurve  # noqa: E402
from formalgroup import FormalGroup  # noqa: E402
from instrument import split_point, hensel_lift_point, AnomalousBreak, PrecisionInsufficient  # noqa: E402
import curves as curves_mod  # noqa: E402
import stage23  # noqa: E402


def run_instance(curve, prime_entry, out_dir, seed):
    t0 = time.time()
    result = stage23.run_instance(curve["idx"], prime_entry["p"], curve["A"],
                                   curve["B"], curve["x0"], curve["y0"],
                                   prime_entry["n"], seed=seed)
    result["order"] = prime_entry["order"]
    result["trace"] = prime_entry["trace"]
    fname = os.path.join(out_dir, f"instance_c{curve['idx']}_p{prime_entry['p']}.json")
    with open(fname, "w") as f:
        json.dump(result, f, indent=2, default=str)
    return fname, time.time() - t0


def run_anomalous_break(anomalous, out_dir):
    """Stage 3's anomalous arm: call split_point (which internally calls
    the torsion-section construction) forcing n = p on the anomalous
    curve's own prime, and record exactly which operation refuses."""
    p, A, B, x0, y0 = anomalous["p"], anomalous["A"], anomalous["B"], anomalous["x0"], anomalous["y0"]
    fg = FormalGroup(A, B, D=stage23.WORKING_DEGREE)
    lift_fn = lambda N: hensel_lift_point(fg, p, N, x0, y0)
    record = {"p": p, "A": A, "B": B, "x0": x0, "y0": y0, "order": anomalous["order"]}
    try:
        split_point(p, 2, lift_fn, n=p, fg=fg)  # force n = p
        record["outcome"] = "NO EXCEPTION -- DEFECT (expected AnomalousBreak)"
        record["refused_correctly"] = False
    except AnomalousBreak as e:
        record["outcome"] = str(e)
        record["refused_correctly"] = True
        record["refused_at"] = "division by n inside E_1 (pow(n, -1, p^K) with p | n)"
    except Exception as e:
        record["outcome"] = f"WRONG EXCEPTION TYPE {type(e).__name__}: {e}"
        record["refused_correctly"] = False
    fname = os.path.join(out_dir, "anomalous_break.json")
    with open(fname, "w") as f:
        json.dump(record, f, indent=2, default=str)
    return fname, record


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    seed = 20260905
    os.makedirs(out_dir, exist_ok=True)

    curves, anomalous = curves_mod.frozen_instances(seed=seed)
    with open(os.path.join(out_dir, "frozen_curves_and_primes.json"), "w") as f:
        json.dump({"curves": curves, "anomalous": anomalous}, f, indent=2)

    manifest = {"instances": [], "anomalous": None}
    for curve in curves:
        for prime_entry in curve["primes"]:
            fname, dt = run_instance(curve, prime_entry, out_dir, seed)
            manifest["instances"].append({"file": os.path.basename(fname),
                                           "curve_idx": curve["idx"],
                                           "p": prime_entry["p"], "wall_seconds": dt})
            print(f"instance curve={curve['idx']} p={prime_entry['p']} done in {dt:.2f}s", flush=True)

    fname, record = run_anomalous_break(anomalous, out_dir)
    manifest["anomalous"] = {"file": os.path.basename(fname),
                              "refused_correctly": record["refused_correctly"]}
    print("anomalous break:", record["outcome"], flush=True)

    with open(os.path.join(out_dir, "manifest_summary.json"), "w") as f:
        json.dump(manifest, f, indent=2)
