#!/usr/bin/env python3
"""Stage 3: Koblitz Frobenius-arm null vs ordinary RC-1 null (P4)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from closure import Closure
from descent_s3 import descend_s3
from gf2n import TableField
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package
from targets import KOBLITZ17, RC1, SEED, build_koblitz_targets, build_rc1_targets, frobenius_conjugates_x

RUN_KOB = "RUN-BINSTD-b2950c"
RUN_ORD = "RUN-BINSTD-6b3f87"

# Frobenius-stable ker g(σ) of dimension 8 (factor of X^17+1 over F2)
G_SIGMA = 0b100111001  # deg 8, ker_dim 8


def ker_g_sigma(F, g: int) -> list[int]:
    def apply(poly, x):
        acc = 0
        y = x
        p = poly
        while p:
            if p & 1:
                acc ^= y
            y = F.sqr(y)
            p >>= 1
        return acc

    V = [x for x in range(F.q) if apply(g, x) == 0]
    # Extract F2 basis via Gaussian elim
    used = []
    basis = []
    for v in V:
        x = v
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
        basis.append(v)
    return basis


def w4_work(F, B, basis, xR, D=4):
    eqs, meta = descend_s3(F, B, basis, xR)
    assert meta["max_boolean_degree"] <= 2
    cl = Closure(meta["nv"], D, meta["neq"])
    t0 = time.time()
    rec, _cert = cl.w_closure(eqs, want_cert=False)
    wall = time.time() - t0
    # Work proxy: sum of dims over iterations + final_dim
    dims = rec.get("dims") or []
    work = int(sum(dims) + rec.get("final_dim", 0))
    return {
        "first_iteration_containing_1": rec.get("one_first_iteration"),
        "final_dim": rec.get("final_dim"),
        "iterations_to_fixpoint": rec.get("iterations_to_fixpoint"),
        "one": rec.get("one"),
        "W4_work_units": work,
        "wall_s": wall,
        "nv": meta["nv"],
        "neq": meta["neq"],
        "dims": dims,
    }


def arm_koblitz():
    F = TableField(KOBLITZ17["n"], KOBLITZ17["mod"])
    basis = ker_g_sigma(F, G_SIGMA)
    assert len(basis) == 8, len(basis)
    _, E, G, targets = build_koblitz_targets(n_targets=5, seed=SEED)
    started = utc_now()
    t0 = time.time()
    rows = []
    for t in targets:
        one = w4_work(F, KOBLITZ17["B"], basis, t["x_R"])
        conj = t["conjugates_x"]
        conj_recs = [w4_work(F, KOBLITZ17["B"], basis, x) for x in conj]
        sum_work = sum(r["W4_work_units"] for r in conj_recs)
        ratio = sum_work / (17 * one["W4_work_units"]) if one["W4_work_units"] else None
        rows.append(
            {
                "idx": t["idx"],
                "x_R": t["x_R"],
                "one_instance": one,
                "orbit_sum_W4_work_units": sum_work,
                "orbit_closure_ratio": ratio,
                "orbit_mean_first_iter_1": float(
                    np.mean([r["first_iteration_containing_1"] if r["first_iteration_containing_1"] is not None else -1 for r in conj_recs])
                ),
                "conjugates": conj,
            }
        )
    mean_ratio = float(np.mean([r["orbit_closure_ratio"] for r in rows if r["orbit_closure_ratio"] is not None]))
    metrics = {
        "arm": "koblitz_orbit",
        "dim_V": 8,
        "g_sigma": bin(G_SIGMA),
        "V_basis": [int(b) for b in basis],
        "n_targets": len(targets),
        "rows": rows,
        "orbit_closure_ratio_mean": mean_ratio,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_s": time.time() - t0,
        "termination_reason": "completed",
    }
    finished = utc_now()
    write_run_package(
        RUN_KOB,
        stage=3,
        arm="koblitz_orbit",
        seed=SEED,
        command="python3 experiments/EXP-BINSTD-ef7fa4/implementation/stage3_run.py --arm koblitz",
        parameters={"n_targets": 5, "conjugates": 17, "dim_V": 8, "D": 4},
        metrics={k: v for k, v in metrics.items() if k != "rows"},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=f"Koblitz mean orbit_closure_ratio={mean_ratio}\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={"kind": "none", "verified": None, "note": "P4 W4 shape metric-only"},
        curve_id="BIN-TOY-koblitz-frobenius",
    )
    return metrics


def arm_ordinary():
    """Ordinary RC-1 with 17 unrelated targets as null (same V dim 8 poly window)."""
    F = TableField(RC1["n"], RC1["mod"])
    # size-matched poly window dim 8 (not Frobenius-stable)
    basis = [1 << j for j in range(8)]
    _, E, G, targets = build_rc1_targets(n_targets=5, seed=SEED + 123)
    started = utc_now()
    t0 = time.time()
    rows = []
    rng = np.random.default_rng(SEED + 321)
    for t in targets:
        one = w4_work(F, RC1["B"], basis, t["x_R"])
        # 17 unrelated targets (not Frobenius conjugates)
        unrelated = []
        seen = {t["x_R"]}
        while len(unrelated) < 17:
            x = int(rng.integers(1, F.q))
            if x in seen:
                continue
            # require x is an abscissa on the curve
            from curve import Curve

            E2 = Curve(F, RC1["A"], RC1["B"])
            if E2.lift_x(x) is None:
                continue
            seen.add(x)
            unrelated.append(x)
        urecs = [w4_work(F, RC1["B"], basis, x) for x in unrelated]
        sum_work = sum(r["W4_work_units"] for r in urecs)
        ratio = sum_work / (17 * one["W4_work_units"]) if one["W4_work_units"] else None
        rows.append(
            {
                "idx": t["idx"],
                "x_R": t["x_R"],
                "one_instance": one,
                "unrelated_sum_W4_work_units": sum_work,
                "orbit_closure_ratio": ratio,  # same metric name for comparison
                "unrelated_x": unrelated,
            }
        )
    mean_ratio = float(np.mean([r["orbit_closure_ratio"] for r in rows if r["orbit_closure_ratio"] is not None]))
    metrics = {
        "arm": "ordinary_null",
        "dim_V": 8,
        "V_basis": [int(b) for b in basis],
        "n_targets": len(targets),
        "rows": rows,
        "orbit_closure_ratio_mean": mean_ratio,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_s": time.time() - t0,
        "termination_reason": "completed",
    }
    finished = utc_now()
    write_run_package(
        RUN_ORD,
        stage=3,
        arm="ordinary_null",
        seed=SEED,
        command="python3 experiments/EXP-BINSTD-ef7fa4/implementation/stage3_run.py --arm ordinary",
        parameters={"n_targets": 5, "unrelated": 17, "dim_V": 8, "D": 4},
        metrics={k: v for k, v in metrics.items() if k != "rows"},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=f"Ordinary mean orbit_closure_ratio={mean_ratio}\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={"kind": "none", "verified": None, "note": "P4 ordinary null metric-only"},
        curve_id="BIN-TOY-RC1",
    )
    return metrics


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--arm", default="all", choices=["all", "koblitz", "ordinary"])
    args = p.parse_args()
    (EXP_ROOT / "stage3").mkdir(parents=True, exist_ok=True)
    kob = ord_ = None
    if args.arm in ("all", "koblitz"):
        kob = arm_koblitz()
    if args.arm in ("all", "ordinary"):
        ord_ = arm_ordinary()
    # summary
    summary = {
        "experiment_id": "EXP-BINSTD-ef7fa4",
        "metric": "P4",
        "koblitz": None,
        "ordinary_null": None,
        "comparison": None,
        "no_break_guard": True,
        "claim": "observations_only_preregistered_null_shape",
        "prediction": "no drop on Koblitz vs ordinary attributable to Frobenius structure",
    }
    if kob:
        summary["koblitz"] = {
            "run_id": RUN_KOB,
            "orbit_closure_ratio_mean": kob["orbit_closure_ratio_mean"],
            "dim_V": 8,
            "g_sigma": kob["g_sigma"],
            "rows": kob["rows"],
        }
    if ord_:
        summary["ordinary_null"] = {
            "run_id": RUN_ORD,
            "orbit_closure_ratio_mean": ord_["orbit_closure_ratio_mean"],
            "dim_V": 8,
            "rows": ord_["rows"],
        }
    if kob and ord_:
        summary["comparison"] = {
            "koblitz_mean": kob["orbit_closure_ratio_mean"],
            "ordinary_mean": ord_["orbit_closure_ratio_mean"],
            "abs_diff": abs(kob["orbit_closure_ratio_mean"] - ord_["orbit_closure_ratio_mean"]),
            "note": "Null: ratios should be comparable (~1 when summing 17 single-instance works).",
        }
    out = EXP_ROOT / "stage3" / "frobenius-arm-summary.yaml"
    if out.exists():
        out.unlink()
    dump_yaml(out, summary)
    print("Stage 3 summary", out)


if __name__ == "__main__":
    main()
