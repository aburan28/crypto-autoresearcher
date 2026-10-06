#!/usr/bin/env python3
"""Stage 2: h=2 Koblitz control (Z/4 undefined; parity ratio ~2)."""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coset import (
    build_curve,
    build_windows,
    coset_fractions_x,
    count_decomps_m2,
    count_decomps_m3,
    sample_subgroup_targets,
    verify_order,
)
from runpack import EXP_ROOT, dump_yaml, utc_now, write_run_package


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, default=20261004)
    args = ap.parse_args()

    stage1 = EXP_ROOT / "stage1"
    if not stage1.exists():
        raise SystemExit("Stage 2 refused: stage1/ does not exist")

    started = utc_now()
    t0 = time.time()
    logs = []

    F, E, cell = build_curve("n19_koblitz_h2")
    order_info = verify_order(E, cell)
    logs.append(f"order_info={order_info}")
    if not order_info["pass"]:
        raise SystemExit(f"h=2 order verification failed: {order_info}")

    h = 2
    l = cell["expected_l"]
    windows = build_windows(E, cell, args.seed, deg_dim=10)
    fracs = coset_fractions_x(windows["V"], h)
    logs.append(f"fractions={fracs}")

    # Z/4 bookkeeping must refuse / report undefined — never coerce.
    z4_status = {
        "requested": "Z/4 class-sum bookkeeping",
        "status": "undefined",
        "reason": (
            "cofactor h=2 => E ≅ Z/(2l); the quotient E/4E ≅ Z/4 does not exist. "
            "Only Z/2 (parity) bookkeeping is defined."
        ),
        "coerced": False,
    }

    rng = random.Random(args.seed)
    targets = sample_subgroup_targets(E, h, 40, rng)
    yields = {}
    violations = 0
    for m in (2, 3):
        yields[m] = {}
        for name in ("V", "V0", "random"):
            if m == 2:
                res = count_decomps_m2(E, windows[name], targets, l, h)
            else:
                res = count_decomps_m3(E, windows[name], targets, l, h)
            violations += res["class_sum_violations"]
            yields[m][name] = res
        # V_C for h=2 is the order-l subgroup coset (class 0 under Z/2)
        if m == 2:
            yields[m]["V_C"] = count_decomps_m2(E, windows["V_C"], targets, l, h)
        else:
            yields[m]["V_C"] = count_decomps_m3(E, windows["V_C"], targets, l, h)
        violations += yields[m]["V_C"]["class_sum_violations"]

    parity = {}
    for m in (2, 3):
        a = yields[m]["V0"]["mean"]
        b = yields[m]["random"]["mean"]
        ratio = (a / b) if b else None
        parity[m] = {
            "V0_mean_measured": a,
            "random_mean_measured": b,
            "parity_ratio_measured": ratio,
            "modeled_comparator": 2.0,
            "within_half_to_double_of_modeled": (
                (0.5 * 2.0 <= ratio <= 2.0 * 2.0) if ratio is not None else False
            ),
        }
        logs.append(f"m={m} parity_ratio={ratio} modeled=2")

    if violations > 0:
        raise SystemExit("HARD HALT: class-sum violations on h=2 cell")

    report = {
        "experiment_id": "EXP-BINSTD-58758f",
        "task_id": "TASK-20261001-c04c94",
        "cell": cell,
        "seed": args.seed,
        "order_info": order_info,
        "coset_fractions_Z2": fracs,
        "z4_bookkeeping": z4_status,
        "parity_ratios": parity,
        "yield_means": {
            m: {w: yields[m][w]["mean"] for w in yields[m]} for m in yields
        },
        "class_sum_violations": violations,
        "h1_null_absent": True,
        "no_deployed_break_claim": True,
        "no_free_cofactor_framing": True,
        "note": (
            "h=2 sibling control: Z/4 undefined (not coerced); parity ratio still "
            "compared to modeled 2. Observations only."
        ),
    }
    dump_yaml(EXP_ROOT / "stage2" / "h2-control-report.yaml", report)
    logs.append("wrote stage2/h2-control-report.yaml")

    finished = utc_now()
    wall = time.time() - t0
    write_run_package(
        args.run_id,
        stage=2,
        arm="h2-control",
        seed=args.seed,
        command=(
            f"python3 experiments/EXP-BINSTD-58758f/implementation/stage2_run.py "
            f"--run-id {args.run_id} --seed {args.seed}"
        ),
        parameters={"curve_id": cell["curve_id"], "seed": args.seed, "a": 1, "b": 1},
        metrics={
            "z4_undefined": True,
            "parity": parity,
            "class_sum_violations": violations,
            "order_pass": order_info["pass"],
        },
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text="\n".join(logs) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note=(
            "Stage 2 h=2 control measurement; certificate.kind=none; "
            "Z/4 bookkeeping explicitly undefined"
        ),
    )
    print("\n".join(logs))


if __name__ == "__main__":
    main()
