#!/usr/bin/env python3
"""Stage 2: V' control, ordinary-curve control, H2 count agreement."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package
from soundness import (
    N,
    build_factor_base,
    build_koblitz_curve,
    census_metrics,
    find_generator,
    frobenius_point_F,
    h2_counts,
    leave_V_fraction,
    random_subspace,
    random_targets,
    select_V_f1,
    verify_group_order,
)

RUN_VPRIME = "RUN-BINSTD-46f8b5"
RUN_ORDINARY = "RUN-BINSTD-1041c0"
RUN_H2 = "RUN-BINSTD-a1c040"
SEED_VPRIME = 2026100121
SEED_ORDINARY = 2026100122
N_TARGETS_CONTROL = 40  # smaller control sample; labeled; Stage-1 remains primary


def ensure_stage1() -> None:
    if not (EXP_ROOT / "stage1").is_dir():
        raise SystemExit("REFUSE: stage1/ missing; Stage 2 gated on Stage 1")
    for req in ("tau-stability-check.yaml", "soundness-census.yaml"):
        if not (EXP_ROOT / "stage1" / req).exists():
            raise SystemExit(f"REFUSE: stage1/{req} missing")


def run_vprime() -> None:
    ensure_stage1()
    started = utc_now()
    t0 = time.time()
    F, E = build_koblitz_curve()
    _g, V, _vmeta = select_V_f1(F)
    Vprime = random_subspace(F, 8, SEED_VPRIME, forbid_stable=[set(V)])
    leave = leave_V_fraction(F, Vprime)
    # Also sample a few targets and report leave among squared solution coords if any
    gord = verify_group_order(E)
    G = find_generator(E, gord["l_order"], SEED_VPRIME)
    targets = random_targets(E, G, gord["l_order"], N_TARGETS_CONTROL, SEED_VPRIME)
    fb = build_factor_base(E, Vprime)
    # For V', equivariance undefined; report leave on V' elements and on squared pairs from S
    from soundness import solution_set_S, square_tuple

    leave_tuple = 0
    n_tuple = 0
    Vset = set(Vprime)
    for R in targets:
        S = solution_set_S(E, R, fb)
        for t in S:
            n_tuple += 1
            st = square_tuple(F, t)
            if st[0] not in Vset or st[1] not in Vset:
                leave_tuple += 1
    doc = {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "stage": 2,
        "arm": "Vprime_control",
        "seed": SEED_VPRIME,
        "run_id": RUN_VPRIME,
        "dim": 8,
        "card_Vprime": len(Vprime),
        "leave_Vprime_fraction": leave["leave_Vprime_fraction"],
        "leave_count": leave["leave_count"],
        "n_control_targets": N_TARGETS_CONTROL,
        "n_solution_tuples_seen": n_tuple,
        "leave_among_squared_tuples": leave_tuple,
        "leave_among_squared_tuples_fraction": (leave_tuple / n_tuple) if n_tuple else None,
        "note": (
            "Random non-tau-stable V' of matched dimension. "
            "equivariance_agreement undefined (squaring leaves V'). "
            "leave_Vprime_fraction is the artifact tell. MEASURED."
        ),
        "label": "MEASURED",
        "no_deployed_curve_break_claimed": True,
    }
    dump_yaml(EXP_ROOT / "stage2" / "vprime-control.yaml", doc)
    finished = utc_now()
    wall = time.time() - t0
    write_run_package(
        RUN_VPRIME,
        stage=2,
        arm="Vprime_control",
        seed=SEED_VPRIME,
        command="python3 experiments/EXP-BINSTD-38e4ad/implementation/stage2_run.py --arm vprime",
        parameters={"curve_id": "RC1-n17-a1b1", "window_kind": "random", "dim": 8, "seed": SEED_VPRIME},
        metrics={**leave, "wall_s": wall, "termination_reason": "completed", "peak_rss_bytes": peak_rss_bytes()},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps(doc, indent=2) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note="V' control measurement; certificate.kind=none",
    )
    print(json.dumps(leave, indent=2))


def run_ordinary() -> None:
    ensure_stage1()
    started = utc_now()
    t0 = time.time()
    F, _Ek = build_koblitz_curve()
    # ordinary: same field, b = t (not in F_2), a = 1
    B = 2  # t
    E = Curve(F, 1, B)
    order = E.count_by_trace()
    # Factor order for subgroup targets — may not match Koblitz order
    # Draw random on-curve points as targets (not necessarily prime-order)
    import random

    rng = random.Random(SEED_ORDINARY)
    targets = []
    for _ in range(10000):
        if len(targets) >= N_TARGETS_CONTROL:
            break
        x = rng.randrange(1, F.q)
        P = E.lift_x(x)
        if P is not None:
            targets.append(P)
    _g, V, _vmeta = select_V_f1(F)
    # Use same V for fair instrument check; sigma not endomorphism
    fb = build_factor_base(E, V)
    # Manual equivariance: squared tuples vs S(sigma(R)) where sigma may leave E
    from soundness import solution_set_S, square_tuple

    n_sq = 0
    n_on_e_sig = 0
    n_in_Ssig = 0
    n_sig_on_curve = 0
    for R in targets:
        Rsig = frobenius_point_F(F, R)
        on = E.on_curve(Rsig)
        if on:
            n_sig_on_curve += 1
        S = solution_set_S(E, R, fb)
        Ssig = solution_set_S(E, Rsig, fb) if on else set()
        for t in S:
            n_sq += 1
            st = square_tuple(F, t)
            if on:
                n_on_e_sig += 1
            if st in Ssig:
                n_in_Ssig += 1
    eq = (n_in_Ssig / n_sq) if n_sq else None
    # Prediction: equivariance fails (eq << 1 or 0)
    doc = {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "stage": 2,
        "arm": "ordinary_curve_control",
        "seed": SEED_ORDINARY,
        "run_id": RUN_ORDINARY,
        "curve": "y^2+xy=x^3+x^2+t",
        "A": 1,
        "B": "t",
        "B_int": B,
        "group_order_E_measured": order,
        "n_targets": len(targets),
        "n_sigma_R_on_curve": n_sig_on_curve,
        "n_squared_tuples": n_sq,
        "n_squared_in_S_sigma": n_in_Ssig,
        "equivariance_agreement": eq,
        "ordinary_curve_equivariance_fails": eq is None or eq < 1.0,
        "note": (
            "b=t not in F_2; Frobenius is not an endomorphism of E. "
            "Squared tuples must fail to lie in S(sigma(R)) for E. MEASURED."
        ),
        "label": "MEASURED",
        "no_deployed_curve_break_claimed": True,
    }
    dump_yaml(EXP_ROOT / "stage2" / "ordinary-curve-control.yaml", doc)
    finished = utc_now()
    wall = time.time() - t0
    write_run_package(
        RUN_ORDINARY,
        stage=2,
        arm="ordinary_curve_control",
        seed=SEED_ORDINARY,
        command="python3 experiments/EXP-BINSTD-38e4ad/implementation/stage2_run.py --arm ordinary",
        parameters={"curve_id": "n17-a1-b=t", "window_kind": "ordinary_curve", "seed": SEED_ORDINARY},
        metrics={
            "equivariance_agreement": eq,
            "ordinary_curve_equivariance_fails": doc["ordinary_curve_equivariance_fails"],
            "group_order_E": order,
            "wall_s": wall,
            "peak_rss_bytes": peak_rss_bytes(),
            "termination_reason": "completed",
            "label": "MEASURED",
        },
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps(doc, indent=2) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note="Ordinary-curve control; certificate.kind=none",
    )
    print(json.dumps({k: doc[k] for k in ("equivariance_agreement", "ordinary_curve_equivariance_fails", "n_squared_tuples")}, indent=2))


def run_h2() -> None:
    ensure_stage1()
    started = utc_now()
    t0 = time.time()
    F, E = build_koblitz_curve()
    _g, V, vmeta = select_V_f1(F)
    if not vmeta["tau_stability"]["pass"]:
        raise SystemExit("tau-stability failed; refuse H2")
    counts = h2_counts(E, V, N)
    if not counts["h2_count_agreement"]:
        termination = "instrument_halt"
        valid = False
        invalid_reason = "h2_count_agreement false"
    else:
        termination = "completed"
        valid = True
        invalid_reason = None
    agree_doc = {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "stage": 2,
        "arm": "H2_count",
        "run_id": RUN_H2,
        "V": "ker f1(tau)",
        "direct_count": counts["direct_count"],
        "per_orbit_sum": counts["per_orbit_sum"],
        "n_orbits": counts["n_orbits"],
        "fixed_points_in_xcap": counts["fixed_points_in_xcap"],
        "h2_count_agreement": counts["h2_count_agreement"],
        "label": "MEASURED",
        "note": (
            "Direct |x(E)∩V| vs sum of tau-orbit sizes over representatives. "
            "Exact equality expected on tau-stable V (HEUR-BINSTD-c3d68f-H2). "
            "Preprocessing-only; no exponent claim."
        ),
        "no_deployed_curve_break_claimed": True,
    }
    dump_yaml(EXP_ROOT / "stage2" / "h2-count-agreement.yaml", agree_doc)
    heur = {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "heuristic_id": "HEUR-BINSTD-c3d68f-H2",
        "stage": 2,
        "HEUR_H2_holds": bool(counts["h2_count_agreement"]),
        "comparison_to_frozen_prediction": {
            "h2_count_agreement": counts["h2_count_agreement"],
            "predicted": True,
        },
        "interpretation_boundary": (
            "Observations only. H2 is preprocessing-only / true-by-construction "
            "on tau-stable V; not an exponent lever. No deployed-curve break claimed."
        ),
        "run_id": RUN_H2,
        "label": "MEASURED",
    }
    dump_yaml(EXP_ROOT / "stage2" / "heur-h2-verdict.yaml", heur)
    finished = utc_now()
    wall = time.time() - t0
    write_run_package(
        RUN_H2,
        stage=2,
        arm="H2_count",
        seed=None,
        command="python3 experiments/EXP-BINSTD-38e4ad/implementation/stage2_run.py --arm h2",
        parameters={"curve_id": "RC1-n17-a1b1", "V": "ker f1(tau)"},
        metrics={
            **{k: counts[k] for k in ("direct_count", "per_orbit_sum", "n_orbits", "h2_count_agreement")},
            "HEUR_H2_holds": heur["HEUR_H2_holds"],
            "wall_s": wall,
            "peak_rss_bytes": peak_rss_bytes(),
            "termination_reason": termination,
            "label": "MEASURED",
        },
        valid=valid,
        invalid_reason=invalid_reason,
        termination_reason=termination,
        stdout_text=json.dumps(agree_doc, indent=2) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note="H2 count agreement; certificate.kind=none",
    )
    print(json.dumps(agree_doc, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["vprime", "ordinary", "h2", "all"], default="all")
    args = ap.parse_args()
    (EXP_ROOT / "stage2").mkdir(parents=True, exist_ok=True)
    if args.arm in ("vprime", "all"):
        run_vprime()
    if args.arm in ("ordinary", "all"):
        run_ordinary()
    if args.arm in ("h2", "all"):
        run_h2()


if __name__ == "__main__":
    main()
