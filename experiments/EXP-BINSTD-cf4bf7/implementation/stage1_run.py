#!/usr/bin/env python3
"""Stage 1: construct primary composite (d,k)=(2,17)/F_2^34 and null n=37 curves."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import (
    Curve,
    factor_group_order,
    order_via_hasse_bsgs,
    verify_subgroup_order,
)
from gf2n import Field, elements_of_f4, find_irreducible, poly_to_string
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-847e2c"
SEED = 20261001


def build_arm(n: int, *, require_f4_coeffs: bool, seed: int, label: str) -> dict:
    t0 = time.time()
    mod = find_irreducible(n, prefer_trinomial=True)
    F = Field(n, mod)
    f4 = elements_of_f4(F) if (n % 2 == 0) else None

    # Deterministic coefficient search: prefer A,B in F_4 (composite) or F_2 (null).
    candidates = []
    if require_f4_coeffs:
        assert f4 is not None
        for A in f4:
            for B in f4:
                if B == 0:
                    continue
                candidates.append((A, B))
    else:
        # Null arm: ordinary binary curve over F_2 coeffs first, then small ints.
        for A in range(0, 8):
            for B in range(1, 8):
                candidates.append((A, B))

    attempts = []
    chosen = None
    for idx, (A, B) in enumerate(candidates):
        E = Curve(F, A, B)
        import random as pyrandom

        rng = pyrandom.Random(seed + idx)
        try:
            E.random_point(rng)
        except RuntimeError as exc:
            attempts.append({"A": A, "B": B, "error": str(exc)})
            continue
        order_info = order_via_hasse_bsgs(E, seed=seed + idx, max_trials=48)
        # Drop per-trial details from the persisted attempt log (keep summary).
        order_summary = {
            k: v for k, v in order_info.items() if k != "details"
        }
        attempts.append(
            {
                "A": A,
                "B": B,
                "A_hex": hex(A),
                "B_hex": hex(B),
                "order_ok": order_info["ok"],
                "group_order": order_info.get("group_order"),
                "trace_t": order_info.get("trace_t"),
                "trials_used": order_info.get("trials_used"),
                "lcm_point_orders": order_info.get("lcm_point_orders"),
            }
        )
        print(
            f"  candidate[{idx}] A={hex(A)} B={hex(B)} "
            f"ok={order_info['ok']} N={order_info.get('group_order')} "
            f"trials={order_info.get('trials_used')}",
            flush=True,
        )
        if not order_info["ok"]:
            continue
        N = order_info["group_order"]
        fac = factor_group_order(N)
        vsub = None
        if fac["l_order"] and fac["l_order_probable_prime"]:
            vsub = verify_subgroup_order(E, N, fac["l_order"], seed=seed + idx)
            if not vsub["verified"]:
                attempts[-1]["subgroup_verify"] = vsub
                # Still accept the curve with verified #E even if subgroup probe fails
                vsub_ok = False
            else:
                vsub_ok = True
        else:
            vsub_ok = False
        chosen = {
            "label": label,
            "n": n,
            "field_bits": n,
            "modulus_hex": hex(mod),
            "irreducible": poly_to_string(mod),
            "A": A,
            "B": B,
            "A_hex": hex(A),
            "B_hex": hex(B),
            "A_in_F4": (f4 is not None and A in f4),
            "B_in_F4": (f4 is not None and B in f4),
            "f4_structure_required": require_f4_coeffs,
            "f4_structure_satisfied": (
                (not require_f4_coeffs)
                or (f4 is not None and A in f4 and B in f4)
            ),
            "group_order_E": N,
            "trace_t": order_info["trace_t"],
            "hasse_bound": order_info["hasse_bound"],
            "order_summary": order_summary,
            "l_order": fac["l_order"],
            "cofactor_h": fac["cofactor_h"],
            "l_order_probable_prime": fac["l_order_probable_prime"],
            "factorization_N": fac["factors"],
            "subgroup_verification": vsub,
            "subgroup_order_verified": vsub_ok,
            "curve_order_verified": True,
            "order_method": "hasse_bsgs_lcm_weil_filter",
            "wall_s_arm": time.time() - t0,
            "candidate_index": idx,
        }
        break

    if chosen is None:
        return {
            "label": label,
            "n": n,
            "ok": False,
            "error": "no suitable curve found in candidate list within trial budget",
            "attempts": attempts,
            "modulus_hex": hex(mod),
            "irreducible": poly_to_string(mod),
            "wall_s_arm": time.time() - t0,
            "curve_order_verified": False,
        }
    chosen["ok"] = True
    chosen["attempts_count"] = len(attempts)
    return chosen


def main() -> None:
    started = utc_now()
    t0 = time.time()
    lines: list[str] = []

    lines.append("Stage 1: composite arm F_2^34 with F_4 coefficients")
    composite = build_arm(34, require_f4_coeffs=True, seed=SEED, label="BIN-TOY-primary-composite")
    lines.append(
        f"  composite ok={composite.get('ok')} N={composite.get('group_order_E')} "
        f"l={composite.get('l_order')} A={composite.get('A_hex')} B={composite.get('B_hex')}"
    )

    lines.append("Stage 1: null arm F_2^37 (primitive-prime null; NOT n=31)")
    null = build_arm(37, require_f4_coeffs=False, seed=SEED + 1000, label="BIN-TOY-primary-null")
    lines.append(
        f"  null ok={null.get('ok')} N={null.get('group_order_E')} "
        f"l={null.get('l_order')} A={null.get('A_hex')} B={null.get('B_hex')}"
    )

    both_ok = bool(composite.get("ok") and null.get("ok"))
    payload = {
        "experiment_id": "EXP-BINSTD-cf4bf7",
        "task_id": "TASK-20261001-18804b",
        "stage": 1,
        "seed": SEED,
        "primary_pair": {"d": 2, "k": 17, "n_null": 37},
        "worst_ladder_ratio_error_pp_disclosed": -17.0,
        "composite_arm": composite,
        "null_arm": null,
        "n31_used_as_null": False,
        "curve_order_verified": both_ok,
        "no_break_claim": True,
        "infrastructure_failure": not both_ok,
    }
    dump_yaml(EXP_ROOT / "stage1" / "curve-construction.yaml", payload)

    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "composite_ok": bool(composite.get("ok")),
        "null_ok": bool(null.get("ok")),
        "curve_order_verified": both_ok,
        "composite_group_order": composite.get("group_order_E"),
        "null_group_order": null.get("group_order_E"),
        "composite_l_order": composite.get("l_order"),
        "null_l_order": null.get("l_order"),
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
    }
    # Infrastructure failure if construction/order verification fails (per spec).
    if both_ok:
        valid = True
        termination = "completed"
        status_override = None
        invalid_reason = None
    else:
        valid = False
        termination = "crash"  # maps to failed_infrastructure; construction tool failure
        status_override = "failed_infrastructure"
        invalid_reason = "curve construction or order verification failed (infrastructure)"

    write_run_package(
        RUN_ID,
        stage=1,
        arm="primary_toy_pair",
        seed=SEED,
        command="python3 experiments/EXP-BINSTD-cf4bf7/implementation/stage1_run.py",
        parameters={
            "composite": {"d": 2, "k": 17, "n": 34},
            "null": {"n": 37},
            "curve_id": "BIN-TOY-primary",
        },
        metrics=metrics,
        valid=valid,
        invalid_reason=invalid_reason,
        termination_reason=termination,
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
        status_override=status_override,
    )
    print("\n".join(lines))
    if not both_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
