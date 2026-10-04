#!/usr/bin/env python3
"""Stage 1 for EXP-BINSTD-375338: equivariance vs unsound constraint tests (a)-(e)."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arithmetic import (
    A17,
    A19,
    B17,
    B19,
    H19,
    L19_EXPECTED,
    MOD17,
    MOD19,
    N17,
    N19,
    V19_DEG,
    build_curve,
    build_factor_base,
    certify_decomposition,
    exhaustive_decomp_index,
    find_generator,
    frobenius_point_F,
    frobenius_scalar,
    ker_g_tau,
    lifts_of_x,
    ord_n_of_2,
    phi_n_factors_over_f2,
    poly_basis_window,
    run_tests_abc_e,
    select_targets_from_index,
    tau_stable_check,
    verify_toy_k19,
    zl_replica,
)
from runpack import (
    EXP_ROOT,
    dump_json,
    dump_yaml,
    peak_rss_bytes,
    utc_now,
    write_run_package,
)

# Minted via allocate_id --next/--check
# First K19 attempt (per-coordinate orbit-min for test e): RUN-BINSTD-8c9916
# Corrected K19 (tuple-orbit lex-min for test e):
RUN_K19 = "RUN-BINSTD-822306"
RUN_ZL = "RUN-BINSTD-8d5245"
RUN_K17 = "RUN-BINSTD-d89f6a"
# First RC1 attempt (over-strict tuple_probe including x=0): RUN-BINSTD-5e64fc
# Corrected RC1:
RUN_RC1 = "RUN-BINSTD-4150f4"

ZL_SEEDS = [20261001, 20261002, 20261003, 20261004, 20261005]
TARGET_SEED = 20261001
MAX_TARGETS = 50


def ensure_stage0() -> None:
    required = [
        "ord-n-2-census.yaml",
        "stable-dimension-sets.yaml",
        "reachability-table-cells.yaml",
        "koblitz-ab-regression-fixture.yaml",
        "hexblob-regex-fixture.yaml",
        "orbit-system-restatement.md",
    ]
    stage0 = EXP_ROOT / "stage0"
    missing = [n for n in required if not (stage0 / n).exists()]
    if missing:
        raise SystemExit(f"REFUSE: Stage 0 incomplete; missing {missing}")


def run_k19() -> dict:
    ensure_stage0()
    started = utc_now()
    t0 = time.time()
    lines = []
    F, E = build_curve(N19, MOD19, A19, B19)
    vinfo = verify_toy_k19(E)
    lines.append(f"K19 order check: {vinfo}")
    if not vinfo["ok"]:
        finished = utc_now()
        wall = time.time() - t0
        write_run_package(
            RUN_K19,
            stage=1,
            arm="BIN-TOY-K19",
            seed=TARGET_SEED,
            command="python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm k19",
            parameters={"curve_id": "BIN-TOY-K19", "n": N19, "A": A19, "B": B19},
            metrics={"setup_halt": True, "verify": vinfo, "termination_reason": "completed"},
            valid=False,
            invalid_reason="#E or l disagrees with frozen cell description",
            termination_reason="completed",
            stdout_text="\n".join(lines) + "\n",
            started_at=started,
            finished_at=finished,
            wall_seconds=wall,
            certificate={"kind": "none", "verified": False, "note": "setup halt"},
        )
        return {"valid": False, "reason": "setup_halt"}

    l_order = vinfo["l_order"]
    G = find_generator(E, H19, l_order, TARGET_SEED)
    mu = frobenius_scalar(E, G, l_order)
    lines.append(f"generator G={G} mu={mu} ord_mu check mu^{N19}%l={(pow(mu, N19, l_order))}")

    V = poly_basis_window(V19_DEG)
    fb = build_factor_base(E, V)
    lines.append(f"V card={len(V)} n_x_on_E={fb['n_x']} n_points={fb['n_points']}")

    index = exhaustive_decomp_index(E, fb, l_order)
    targets = select_targets_from_index(index, E, MAX_TARGETS)
    lines.append(f"targets_with_decomp={len(index)} selected={len(targets)}")

    # Persist certified decompositions (sample + full summary)
    cert_dir = EXP_ROOT / "stage1" / "certified-decompositions"
    cert_dir.mkdir(parents=True, exist_ok=True)
    cert_records = []
    cert_fail = 0
    for ti, item in enumerate(targets):
        R = item["R"]
        for di, d in enumerate(item["decomps"]):
            ok = certify_decomposition(E, R, d["P1"], d["P2"])
            if not ok:
                cert_fail += 1
            rec = {
                "target_index": ti,
                "decomp_index": di,
                "R": [R[0], R[1]],
                "P1": [d["P1"][0], d["P1"][1]],
                "P2": [d["P2"][0], d["P2"][1]],
                "x1": d["x1"],
                "x2": d["x2"],
                "verified_independent_sum": ok,
            }
            cert_records.append(rec)
    dump_json(
        cert_dir / f"BIN-TOY-K19-decompositions-{RUN_K19}.json",
        {
            "curve_id": "BIN-TOY-K19",
            "run_id": RUN_K19,
            "n": N19,
            "m": 2,
            "l_order": l_order,
            "mu": mu,
            "n_targets": len(targets),
            "n_certified_records": len(cert_records),
            "certificate_failures": cert_fail,
            "records": cert_records,
            "label": "MEASURED",
            "test_e_operationalization": (
                "tuple-orbit lex-min among n Frobenius images of ordered pair"
            ),
        },
    )

    metrics_abc_e = run_tests_abc_e(E, F, targets, fb["Vset"])
    lines.append(json.dumps({k: metrics_abc_e[k] for k in metrics_abc_e if k != "solutions_lost_fractions_per_target"}, sort_keys=True))

    # Expected unsoundness band
    expected_mid = 1.0 - 1.0 / N19
    band = [0.7 * expected_mid, 1.0 * expected_mid]
    med = metrics_abc_e["solutions_lost_median_fraction"]
    in_band = med is not None and band[0] <= med <= band[1]

    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        **metrics_abc_e,
        "mu": mu,
        "n_targets": len(targets),
        "n_factor_base_points": fb["n_points"],
        "ord_n_2": ord_n_of_2(N19),
        "unsoundness_expected_mid": expected_mid,
        "unsoundness_band": band,
        "unsoundness_median_in_band": in_band,
        "group_order_check": vinfo,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    # Validity: instrument controls + certificate; scientific predictions are observations
    valid = (
        metrics_abc_e["leg_swap_hit_rate"] == 1.0
        and metrics_abc_e["certificate_pass_rate"] == 1.0
        and metrics_abc_e["hard_stop_same_instance"] is None
        and cert_fail == 0
        and len(targets) >= 1
    )
    invalid_reason = None
    if not valid:
        invalid_reason = "instrument/control failure on BIN-TOY-K19"
    write_run_package(
        RUN_K19,
        stage=1,
        arm="BIN-TOY-K19_tests_a_b_c_e",
        seed=TARGET_SEED,
        command="python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm k19",
        parameters={
            "curve_id": "BIN-TOY-K19",
            "n": N19,
            "m": 2,
            "V_kind": "nonstable_window_deg_lt_10",
            "A": A19,
            "B": B19,
            "modulus_hex": hex(MOD19),
            "max_targets": MAX_TARGETS,
            "mu": mu,
        },
        metrics=metrics,
        valid=valid,
        invalid_reason=invalid_reason,
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": cert_fail == 0 and len(cert_records) > 0,
            "verifier": "independent-recompute-curve-sum",
            "n_statements": len(cert_records),
            "note": "Every listed decomposition re-verified by summing points on the curve",
        },
    )
    return {
        "valid": valid,
        "metrics": metrics,
        "mu": mu,
        "l_order": l_order,
        "fb_n_points": fb["n_points"],
        "n_targets": len(targets),
    }


def run_zl(mu: int, l_order: int, window_size: int) -> dict:
    ensure_stage0()
    started = utc_now()
    t0 = time.time()
    lines = []
    results = []
    for seed in ZL_SEEDS:
        r = zl_replica(l_order, mu, window_size, seed, N19)
        results.append(r)
        lines.append(
            f"seed={seed} same={r['same_instance_hits']} conj={r['conjugate_instance_hits']} "
            f"inW={r['shifted_legs_in_window_fraction']}"
        )
    finished = utc_now()
    wall = time.time() - t0
    conj_vals = [r["conjugate_instance_hits"] for r in results if r["conjugate_instance_hits"] is not None]
    same_vals = [r["same_instance_hits"] for r in results]
    metrics = {
        "n_seeds": len(ZL_SEEDS),
        "seeds": ZL_SEEDS,
        "mu": mu,
        "l_order": l_order,
        "window_size": window_size,
        "per_seed": results,
        "same_instance_hits_total": sum(same_vals),
        "conjugate_instance_hits_mean": statistics.mean(conj_vals) if conj_vals else None,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
        "label": "MEASURED",
    }
    valid = metrics["same_instance_hits_total"] == 0 and all(
        c is not None and c >= 0.99 for c in conj_vals
    )
    write_run_package(
        RUN_ZL,
        stage=1,
        arm="zl_scalar_replica",
        seed=ZL_SEEDS[0],
        command="python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm zl",
        parameters={
            "curve_id": "Z/l-replica",
            "V_kind": "size_matched_random_Zl",
            "seeds": ZL_SEEDS,
            "mu": mu,
            "l_order": l_order,
            "window_size": window_size,
        },
        metrics=metrics,
        valid=valid,
        invalid_reason=None if valid else "Z/l replica did not match equivariance pattern",
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": False,
            "note": "Z/l scalar replica measurement; no curve decomposition claim",
        },
    )
    return {"valid": valid, "metrics": metrics}


def run_k17() -> dict:
    ensure_stage0()
    started = utc_now()
    t0 = time.time()
    lines = []
    F, E = build_curve(N17, MOD17, A17, B17)
    order = E.count_by_trace()
    # Standard CERTBIN cell: #E=2*65587
    cofactor = 2
    l_order = order // cofactor
    lines.append(f"K17 #E={order} l={l_order} prime={__import__('curve').is_prime(l_order)}")
    factors = phi_n_factors_over_f2(N17)
    # pick first factor; ker has dim = deg(g) = ord_17(2) = 8
    g = factors[0]
    V = ker_g_tau(F, g)
    stab = tau_stable_check(F, V)
    lines.append(f"stable V dim={stab['dim_V']} card={stab['card_V']} pass={stab['pass']} g={bin(g)}")
    if not stab["pass"] or stab["dim_V"] not in (8, 9):
        finished = utc_now()
        wall = time.time() - t0
        write_run_package(
            RUN_K17,
            stage=1,
            arm="BIN-TOY-K17-STABLE",
            seed=TARGET_SEED,
            command="python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm k17",
            parameters={"curve_id": "BIN-TOY-K17-STABLE", "n": N17},
            metrics={"stab": stab, "termination_reason": "completed"},
            valid=False,
            invalid_reason="stable-V construction failed",
            termination_reason="completed",
            stdout_text="\n".join(lines) + "\n",
            started_at=started,
            finished_at=finished,
            wall_seconds=wall,
            certificate={"kind": "none", "verified": False, "note": "setup halt"},
        )
        return {"valid": False}

    fb = build_factor_base(E, V)
    G = find_generator(E, cofactor, l_order, TARGET_SEED ^ 0x17)
    index = exhaustive_decomp_index(E, fb, l_order)
    targets = select_targets_from_index(index, E, max_targets=max(20, min(50, len(index))))
    lines.append(f"K17 targets selected={len(targets)} index_size={len(index)}")

    # in-V shift test: for every certified decomp, both squared legs in V
    in_v = 0
    trials = 0
    conj = 0
    same = 0
    for item in targets:
        R = item["R"]
        Rsig = frobenius_point_F(F, R)
        for d in item["decomps"]:
            sx1, sx2 = F.sqr(d["x1"]), F.sqr(d["x2"])
            trials += 1
            if sx1 in fb["Vset"] and sx2 in fb["Vset"]:
                in_v += 1
            from arithmetic import any_sign_sums_to

            if any_sign_sums_to(E, sx1, sx2, [R, E.neg(R)]):
                if Rsig != R and Rsig != E.neg(R):
                    same += 1
            if any_sign_sums_to(E, sx1, sx2, [Rsig, E.neg(Rsig)]):
                conj += 1

    in_v_frac = in_v / trials if trials else None
    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "n": N17,
        "ord_n_2": ord_n_of_2(N17),
        "dim_V": stab["dim_V"],
        "tau_stable_pass": stab["pass"],
        "n_targets": len(targets),
        "shifted_legs_in_V_fraction": in_v_frac,
        "same_instance_hits": same,
        "conjugate_instance_hits": (conj / trials) if trials else None,
        "trials": trials,
        "irreducible": "t^17+t^3+1",
        "A": A17,
        "B": B17,
        "chosen_phi_factor_bits": bin(g),
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
        "label": "MEASURED",
    }
    valid = (
        in_v_frac == 1.0
        and len(targets) >= 20
        and same == 0
        and metrics["conjugate_instance_hits"] == 1.0
    )
    write_run_package(
        RUN_K17,
        stage=1,
        arm="BIN-TOY-K17-STABLE",
        seed=TARGET_SEED,
        command="python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm k17",
        parameters={
            "curve_id": "BIN-TOY-K17-STABLE",
            "n": N17,
            "m": 2,
            "V_kind": "frobenius_stable",
            "A": A17,
            "B": B17,
            "modulus_hex": hex(MOD17),
        },
        metrics=metrics,
        valid=valid,
        invalid_reason=None if valid else "stable-V in-V/equivariance control failed",
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": False,
            "note": "Stable-V in-V fraction measurement; decompositions certified inline during census",
        },
    )
    # also write cell setup note
    dump_yaml(
        EXP_ROOT / "stage1" / "BIN-TOY-K17-STABLE-setup.yaml",
        {
            "curve_id": "BIN-TOY-K17-STABLE",
            "n": N17,
            "irreducible": "t^17+t^3+1",
            "A": A17,
            "B": B17,
            "group_order_E": order,
            "l_order": l_order,
            "dim_V": stab["dim_V"],
            "card_V": stab["card_V"],
            "phi_factors_count": len(factors),
            "label": "RECOMPUTED",
        },
    )
    return {"valid": valid, "metrics": metrics}


def run_rc1() -> dict:
    ensure_stage0()
    started = utc_now()
    t0 = time.time()
    lines = []
    # NULL-RC1: non-Koblitz ordinary binary curve at n=19, A generic
    A = 97044  # review exemplar; < 2^19
    B = 1
    assert A not in (0, 1)
    F, E = build_curve(N19, MOD19, A, B)
    # Random points: sigma must not lie on E
    import random

    rng = random.Random(TARGET_SEED ^ 0x0C1)
    n_try = 200
    on_curve_shifted = 0
    not_on_curve = 0
    examples = []
    for _ in range(n_try):
        x = rng.randrange(1, F.q)
        P = E.lift_x(x)
        if P is None:
            continue
        Ps = frobenius_point_F(F, P)
        if E.on_curve(Ps):
            on_curve_shifted += 1
            if len(examples) < 5:
                examples.append({"P": list(P), "sigmaP": list(Ps), "on_curve": True})
        else:
            not_on_curve += 1
            if len(examples) < 5:
                examples.append({"P": list(P), "sigmaP": list(Ps), "on_curve": False})
    # Shifted-tuple probe: exclude x=0 (with B in F_2, (0,sqrt(B)) is fixed by
    # sigma and lies on every E: y^2+xy=x^3+A x^2+B). Control is for x!=0.
    V = poly_basis_window(8)
    fb = build_factor_base(E, V)
    tuple_on = 0
    tuple_off = 0
    for P in fb["points"]:
        if P[0] == 0:
            continue
        Ps = frobenius_point_F(F, P)
        if E.on_curve(Ps):
            tuple_on += 1
        else:
            tuple_off += 1
    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "curve_id": "NULL-RC1",
        "n": N19,
        "A": A,
        "B": B,
        "n_points_tested": not_on_curve + on_curve_shifted,
        "sigma_on_curve_count": on_curve_shifted,
        "sigma_not_on_curve_count": not_on_curve,
        "every_shifted_reports_not_on_curve": on_curve_shifted == 0 and not_on_curve > 0,
        "tuple_probe_on_x_nonzero": tuple_on,
        "tuple_probe_off_x_nonzero": tuple_off,
        "x0_exception_note": (
            "Points with x=0 and B in F_2 remain on E under coordinate squaring "
            "for any A; excluded from the null probe."
        ),
        "examples": examples,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
        "label": "MEASURED",
    }
    lines.append(json.dumps({k: metrics[k] for k in metrics if k != "examples"}))
    valid = (
        metrics["every_shifted_reports_not_on_curve"]
        and tuple_on == 0
        and tuple_off > 0
    )
    write_run_package(
        RUN_RC1,
        stage=1,
        arm="NULL-RC1",
        seed=TARGET_SEED,
        command="python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm rc1",
        parameters={"curve_id": "NULL-RC1", "n": N19, "A": A, "B": B, "modulus_hex": hex(MOD19)},
        metrics=metrics,
        valid=valid,
        invalid_reason=None if valid else "RC-1 null reported on-curve shifted images",
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": False,
            "note": "NULL-RC1 not-on-curve control measurement",
        },
    )
    return {"valid": valid, "metrics": metrics}


def write_summaries(k19, zl, k17, rc1) -> None:
    stage1 = EXP_ROOT / "stage1"
    stage1.mkdir(parents=True, exist_ok=True)
    summary = {
        "experiment_id": "EXP-BINSTD-375338",
        "task_id": "TASK-20261001-ff051b",
        "stage": 1,
        "preregistered_prediction_ref": {
            "quantity": (
                "(A) same_instance_hits=0; (B) conjugate_instance_hits=1.0; "
                "(C) solutions_lost median in [0.7,1.0]*(1-1/19); "
                "(D) in-V=1.0 on stable-V; ~0 on n=19 window; "
                "(E) Stage0 ord match"
            ),
            "source": "experiments/EXP-BINSTD-375338/specification.yaml preregistered_prediction",
            "claim_tier": "observational",
            "note": "Executor reports comparison statistics only; no support/refute conclusion",
        },
        "BIN-TOY-K19": {
            "run_id": RUN_K19,
            "tests": "(a)(b)(c)(e)",
            "metrics": k19.get("metrics"),
            "valid_instrument": k19.get("valid"),
        },
        "zl_replica": {
            "run_id": RUN_ZL,
            "test": "(d)",
            "metrics": zl.get("metrics"),
            "valid_instrument": zl.get("valid"),
        },
        "BIN-TOY-K17-STABLE": {
            "run_id": RUN_K17,
            "metrics": k17.get("metrics"),
            "valid_instrument": k17.get("valid"),
        },
        "NULL-RC1": {
            "run_id": RUN_RC1,
            "metrics": rc1.get("metrics"),
            "valid_instrument": rc1.get("valid"),
        },
        "primary_success_axes": [
            "equivariance",
            "unsoundness",
            "census",
        ],
        "unauthorized": [
            "per-instance CNF-XOR leaf-count arms claiming division by mu",
            "Stage >1",
        ],
    }
    dump_json(stage1 / "metrics-summary.json", summary)

    controls = {
        "experiment_id": "EXP-BINSTD-375338",
        "task_id": "TASK-20261001-ff051b",
        "stage": 1,
        "controls": [
            {
                "name": "leg_swap_same_instance",
                "run_id": RUN_K19,
                "leg_swap_hit_rate": (k19.get("metrics") or {}).get("leg_swap_hit_rate"),
                "required": 1.0,
                "pass": (k19.get("metrics") or {}).get("leg_swap_hit_rate") == 1.0,
            },
            {
                "name": "zl_scalar_replica",
                "run_id": RUN_ZL,
                "n_seeds": len(ZL_SEEDS),
                "seeds": ZL_SEEDS,
                "same_instance_hits_total": (zl.get("metrics") or {}).get(
                    "same_instance_hits_total"
                ),
                "conjugate_instance_hits_mean": (zl.get("metrics") or {}).get(
                    "conjugate_instance_hits_mean"
                ),
                "pass": zl.get("valid"),
            },
            {
                "name": "null_non_koblitz_RC1",
                "run_id": RUN_RC1,
                "every_shifted_reports_not_on_curve": (rc1.get("metrics") or {}).get(
                    "every_shifted_reports_not_on_curve"
                ),
                "pass": rc1.get("valid"),
            },
            {
                "name": "stable_V_positive",
                "run_id": RUN_K17,
                "shifted_legs_in_V_fraction": (k17.get("metrics") or {}).get(
                    "shifted_legs_in_V_fraction"
                ),
                "required": 1.0,
                "n_targets": (k17.get("metrics") or {}).get("n_targets"),
                "min_targets": 20,
                "pass": k17.get("valid"),
            },
        ],
        "same_instance_hits": {
            "K19": (k19.get("metrics") or {}).get("same_instance_hits"),
            "K17": (k17.get("metrics") or {}).get("same_instance_hits"),
            "ZL_total": (zl.get("metrics") or {}).get("same_instance_hits_total"),
        },
        "conjugate_instance_hits": {
            "K19": (k19.get("metrics") or {}).get("conjugate_instance_hits"),
            "K17": (k17.get("metrics") or {}).get("conjugate_instance_hits"),
            "ZL_mean": (zl.get("metrics") or {}).get("conjugate_instance_hits_mean"),
        },
        "solutions_lost": {
            "count": (k19.get("metrics") or {}).get(
                "solutions_lost_under_canonical_constraint"
            ),
            "median_fraction": (k19.get("metrics") or {}).get(
                "solutions_lost_median_fraction"
            ),
            "worst_fraction": (k19.get("metrics") or {}).get(
                "solutions_lost_worst_fraction"
            ),
        },
    }
    dump_yaml(stage1 / "controls-report.yaml", controls)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--arm",
        choices=["all", "k19", "zl", "k17", "rc1"],
        default="all",
    )
    ap.add_argument("--mu", type=int, default=None, help="Frobenius scalar (for zl arm)")
    ap.add_argument("--l-order", type=int, default=None)
    ap.add_argument("--window-size", type=int, default=512)
    args = ap.parse_args()

    if args.arm == "k19":
        print(run_k19())
        return
    if args.arm == "zl":
        if args.mu is None or args.l_order is None:
            raise SystemExit("--mu and --l-order required for zl arm")
        print(run_zl(args.mu, args.l_order, args.window_size))
        return
    if args.arm == "k17":
        print(run_k17())
        return
    if args.arm == "rc1":
        print(run_rc1())
        return

    # all
    k19 = run_k19()
    if not k19.get("mu"):
        # still attempt controls with frozen l if setup somehow partial
        mu = k19.get("mu") or 0
        l_order = k19.get("l_order") or L19_EXPECTED
    else:
        mu = k19["mu"]
        l_order = k19["l_order"]
    window = 512
    zl = run_zl(mu, l_order, window)
    k17 = run_k17()
    rc1 = run_rc1()
    write_summaries(k19, zl, k17, rc1)
    print(
        json.dumps(
            {
                "k19_valid": k19.get("valid"),
                "zl_valid": zl.get("valid"),
                "k17_valid": k17.get("valid"),
                "rc1_valid": rc1.get("valid"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
