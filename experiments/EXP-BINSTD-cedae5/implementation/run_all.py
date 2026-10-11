#!/usr/bin/env python3
"""Driver for EXP-BINSTD-cedae5 Stages 0–5 (Stage 5 gated).

Observations only. No GTTD. No rho-beating claim.
"""
from __future__ import annotations

import json
import math
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeleg import (  # noqa: E402
    RC1_ORDER,
    build_rc1,
    enumerate_window,
    generic_zn_census,
    result_to_metrics,
    run_census,
    subsample_pair_indices,
)
from runpack import dump_json, dump_text, dump_yaml, utc_now, write_run_package  # noqa: E402

# Pre-minted and --check'd RUN ids for this task
RUN_STAGE0 = "RUN-BINSTD-1b0b64"
RUN_S1_V = "RUN-BINSTD-ad20e8"
RUN_S1_V0 = "RUN-BINSTD-e0b78d"
RUN_S1_RECOMB_OFF = "RUN-BINSTD-c85825"
RUN_S2 = "RUN-BINSTD-6696d3"
RUN_S3 = "RUN-BINSTD-041330"
RUN_S3_RATIO = "RUN-BINSTD-3e3cae"
RUN_S4 = "RUN-BINSTD-7bcd67"
RUN_S5 = "RUN-BINSTD-fdff79"

SEEDS = [20261001, 20261002, 20261003]


def stage0_run() -> None:
    started = utc_now()
    t0 = __import__("time").perf_counter()
    N = 2**131
    rho = 60.809
    rows = []
    for B, floor in [(1, 66.0), (1024, 71.0), (1048576, 76.0), (1073741824, 81.0)]:
        log2t = math.log2(math.sqrt(2 * N * B))
        rows.append(
            {
                "B": B,
                "log2_sqrt_2NB": log2t,
                "hold_q_floor": floor,
                "match": abs(log2t - floor) < 1e-12,
                "gap_above_rho": log2t - rho,
            }
        )
    ok = all(r["match"] for r in rows)
    # verify RC-1 constructible
    _, _, order = build_rc1()
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    metrics = {
        "floors_match_hold_q": ok,
        "rows": rows,
        "rc1_order": order,
        "rc1_order_expected": RC1_ORDER,
        "rc1_order_ok": order == RC1_ORDER,
    }
    stdout = json.dumps(metrics, indent=2)
    write_run_package(
        RUN_STAGE0,
        stage=0,
        arm="stage0_pricing_verify",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 0",
        parameters={"curve_id": "ECC2K-130-pricing", "N": "2^131", "B_grid": [1, 1024, 1048576, 1073741824]},
        metrics=metrics,
        valid=ok and order == RC1_ORDER,
        invalid_reason=None if (ok and order == RC1_ORDER) else "pricing or RC-1 order mismatch",
        termination_reason="completed",
        stdout_text=stdout + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
    )
    print("Stage 0 run written", RUN_STAGE0)


def _census_yaml(r, run_id: str, arm: str) -> dict:
    return {
        "experiment_id": "EXP-BINSTD-cedae5",
        "task_id": "TASK-20261001-e57118",
        "run_id": run_id,
        "arm": arm,
        "window_kind": r.window_kind,
        "window_size": r.window_size,
        "T": r.T,
        "N": r.N,
        "identity_sum_pairs": r.identity_sum_pairs,
        "full_relation_count": r.full_relation_count,
        "combined_relation_count": r.combined_relation_count,
        "certificate_pass_rate_combined": r.certificate_pass_rate_combined,
        "combined_verified": r.combined_verified,
        "combined_failed": r.combined_failed,
        "residual_support_S_fitted": r.residual_support_S_fitted,
        "residual_collision_rate_ratio": r.residual_collision_rate_ratio,
        "max_residual_multiplicity": r.max_residual_multiplicity,
        "attempts_to_B_relations": r.attempts_to_B_relations,
        "attempts_to_B_relations_log2": r.attempts_to_B_relations_log2,
        "modeled_T2_over_2N": r.modeled_T2_over_2N,
        "modeled_T2_over_2S": r.modeled_T2_over_2S,
        "collection_wall_clock_s": r.collection_wall_clock_s,
        "merge_wall_clock_s": r.merge_wall_clock_s,
        "peak_rss_bytes": r.peak_rss_bytes,
        "extra": r.extra,
        "preregistered_prediction_ref": "experiments/EXP-BINSTD-cedae5/stage0/preregistered-predictions.yaml",
        "claim_boundary": {
            "deployed_curve_break_claimed": False,
            "rho_competitiveness_claimed": False,
            "gttd_claimed": False,
        },
    }


def stage1() -> dict:
    results = {}
    # --- V exhaustive ---
    started = utc_now()
    t0 = __import__("time").perf_counter()
    print("Stage 1: census V ...", flush=True)
    rV = run_census("V", recombination=True, verify_all_combined=True)
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    metrics = result_to_metrics(rV)
    cert_ok = rV.combined_failed == 0 and (
        rV.certificate_pass_rate_combined == 1.0 or rV.combined_relation_count == 0
    )
    write_run_package(
        RUN_S1_V,
        stage=1,
        arm="curve_V",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 1",
        parameters={"curve_id": "BIN-TOY-RC1", "window_kind": "poly_deg_lt_9", "n": 17, "m": 3},
        metrics=metrics,
        valid=cert_ok and rV.extra.get("full_failed", 0) == 0,
        invalid_reason=None if cert_ok else "certificate failure under correct c",
        termination_reason="completed",
        stdout_text=json.dumps(metrics, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": cert_ok,
            "verifier": "freeleg.verify_combined independent re-sum on fresh Curve",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S1_V}/raw-result.json",
            "combined_verified": rV.combined_verified,
            "combined_failed": rV.combined_failed,
        },
    )
    dump_yaml(ROOT / "stage1" / "census-V.yaml", _census_yaml(rV, RUN_S1_V, "curve_V"))
    dump_json(
        ROOT / "stage1" / "residual-histogram-V.json",
        {
            "run_id": RUN_S1_V,
            "residual_key_multiplicity_histogram": rV.residual_value_histogram,
            "max_residual_multiplicity": rV.max_residual_multiplicity,
            "S_fitted": rV.residual_support_S_fitted,
            "T": rV.T,
            "N": rV.N,
            "collision_pair_count": rV.extra.get("collision_pair_count"),
            "modeled_T2_over_2N": rV.modeled_T2_over_2N,
        },
    )
    results["V"] = rV
    print(
        f"  V: T={rV.T} full={rV.full_relation_count} combined={rV.combined_relation_count} "
        f"pass={rV.certificate_pass_rate_combined} ratio={rV.residual_collision_rate_ratio}",
        flush=True,
    )

    # --- V'_0 ---
    started = utc_now()
    t0 = __import__("time").perf_counter()
    print("Stage 1: census V'_0 ...", flush=True)
    rV0 = run_census("V0", recombination=True, verify_all_combined=True)
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    metrics = result_to_metrics(rV0)
    cert_ok = rV0.combined_failed == 0 and (
        rV0.certificate_pass_rate_combined == 1.0 or rV0.combined_relation_count == 0
    )
    write_run_package(
        RUN_S1_V0,
        stage=1,
        arm="curve_V0",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 1",
        parameters={"curve_id": "BIN-TOY-RC1", "window_kind": "aligned_half_c0_eq_0", "n": 17, "m": 3},
        metrics=metrics,
        valid=cert_ok and rV0.extra.get("full_failed", 0) == 0,
        invalid_reason=None if cert_ok else "certificate failure under correct c",
        termination_reason="completed",
        stdout_text=json.dumps(metrics, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": cert_ok,
            "verifier": "freeleg.verify_combined independent re-sum on fresh Curve",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S1_V0}/raw-result.json",
            "combined_verified": rV0.combined_verified,
            "combined_failed": rV0.combined_failed,
        },
    )
    dump_yaml(ROOT / "stage1" / "census-V0.yaml", _census_yaml(rV0, RUN_S1_V0, "curve_V0"))
    results["V0"] = rV0
    print(
        f"  V0: T={rV0.T} full={rV0.full_relation_count} combined={rV0.combined_relation_count} "
        f"pass={rV0.certificate_pass_rate_combined} ratio={rV0.residual_collision_rate_ratio}",
        flush=True,
    )

    # --- recombination-off baseline on V ---
    started = utc_now()
    t0 = __import__("time").perf_counter()
    print("Stage 1: recombination-off baseline ...", flush=True)
    rOff = run_census("V", recombination=False, verify_all_combined=False)
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    metrics = result_to_metrics(rOff)
    B = rOff.window_size
    # modeled free-leg full yield ≈ T * B / N ; also B^3/(6N)
    modeled_freeleg = rOff.T * B / RC1_ORDER
    modeled_balance = (B**3) / (math.factorial(3) * RC1_ORDER)
    dump_yaml(
        ROOT / "stage1" / "recombination-off-baseline.yaml",
        {
            "experiment_id": "EXP-BINSTD-cedae5",
            "run_id": RUN_S1_RECOMB_OFF,
            "arm": "recombination_off",
            "window_kind": "V",
            "window_size": B,
            "T": rOff.T,
            "full_relation_count": rOff.full_relation_count,
            "combined_relation_count": rOff.combined_relation_count,
            "combined_must_be_zero": rOff.combined_relation_count == 0,
            "modeled_freeleg_T_B_over_N": modeled_freeleg,
            "modeled_balance_B3_over_6N": modeled_balance,
            "full_over_modeled_freeleg": (rOff.full_relation_count / modeled_freeleg)
            if modeled_freeleg
            else None,
            "certificate": "decomposition full-relation re-sums only; no combined claimed",
            "full_verified": rOff.extra.get("full_verified"),
            "full_failed": rOff.extra.get("full_failed"),
        },
    )
    write_run_package(
        RUN_S1_RECOMB_OFF,
        stage=1,
        arm="recombination_off",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 1",
        parameters={"curve_id": "BIN-TOY-RC1", "recombination": False, "window_kind": "poly_deg_lt_9"},
        metrics=metrics,
        valid=rOff.combined_relation_count == 0 and rOff.extra.get("full_failed", 0) == 0,
        invalid_reason=None
        if rOff.combined_relation_count == 0
        else "phantom combined relations with recombination off",
        termination_reason="completed",
        stdout_text=json.dumps(metrics, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": rOff.extra.get("full_failed", 0) == 0,
            "verifier": "freeleg.verify_full on fresh Curve; recombination disabled",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S1_RECOMB_OFF}/raw-result.json",
        },
    )
    results["recomb_off"] = rOff
    print(
        f"  recomb-off: full={rOff.full_relation_count} combined={rOff.combined_relation_count} "
        f"modeled≈{modeled_freeleg:.1f}",
        flush=True,
    )
    return results


def stage2(rV) -> None:
    started = utc_now()
    t0 = __import__("time").perf_counter()
    print("Stage 2: T-subsample growth curve ...", flush=True)
    from freeleg import run_census as _rc  # already imported
    from freeleg import build_rc1, enumerate_window

    _, E, _ = build_rc1()
    window = enumerate_window(E, "V")
    B = len(window)
    # T grid: B, 2B, 4B, ... up to C(B,2)
    total = B * (B - 1) // 2
    grid = []
    t = B
    while t <= total:
        grid.append(t)
        t *= 2
    if total not in grid:
        grid.append(total)

    S_ref = rV.residual_support_S_fitted or RC1_ORDER
    curves = []
    for seed in SEEDS:
        series = []
        for T in grid:
            pairs = subsample_pair_indices(B, T, seed)
            r = run_census("V", recombination=True, pair_indices=pairs, verify_all_combined=True)
            modeled = (r.T * r.T) / (2.0 * S_ref)
            series.append(
                {
                    "T": r.T,
                    "combined_relation_count": r.combined_relation_count,
                    "full_relation_count": r.full_relation_count,
                    "modeled_T2_over_2S": modeled,
                    "modeled_T2_over_2N": r.modeled_T2_over_2N,
                    "certificate_pass_rate_combined": r.certificate_pass_rate_combined,
                    "combined_failed": r.combined_failed,
                    "residual_collision_rate_ratio": r.residual_collision_rate_ratio,
                }
            )
            print(f"  seed={seed} T={r.T} combined={r.combined_relation_count} modeled={modeled:.1f}", flush=True)
        curves.append({"seed": seed, "series": series})

    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    payload = {
        "experiment_id": "EXP-BINSTD-cedae5",
        "run_id": RUN_S2,
        "window_kind": "V",
        "window_size": B,
        "S_fitted_from_stage1_V": rV.residual_support_S_fitted,
        "S_used_for_model": S_ref,
        "T_grid": grid,
        "seeds": SEEDS,
        "curves": curves,
        "preregistered_prediction_ref": "experiments/EXP-BINSTD-cedae5/stage0/preregistered-predictions.yaml",
        "formula_modeled": "T^2/(2S)",
        "claim_boundary": {"rho_competitiveness_claimed": False, "gttd_claimed": False},
    }
    dump_yaml(ROOT / "stage2" / "growth-curve.yaml", payload)
    # certificate: all points must pass
    any_fail = any(pt["combined_failed"] for c in curves for pt in c["series"])
    metrics = {
        "n_seeds": len(SEEDS),
        "T_grid": grid,
        "S_used": S_ref,
        "any_certificate_failure": any_fail,
        "wall_s": wall,
    }
    write_run_package(
        RUN_S2,
        stage=2,
        arm="T_subsample_growth",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 2",
        parameters={"seeds": SEEDS, "T_grid": grid, "window_kind": "V"},
        metrics=metrics,
        valid=not any_fail,
        invalid_reason="certificate failure in growth subsample" if any_fail else None,
        termination_reason="completed",
        stdout_text=json.dumps(payload, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": not any_fail,
            "verifier": "freeleg.verify_combined on each subsample combined pair",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S2}/raw-result.json",
        },
    )


def stage3(rV) -> dict:
    started = utc_now()
    t0 = __import__("time").perf_counter()
    print("Stage 3: Z/(4l) generic replica ...", flush=True)
    B = rV.window_size
    replicas = []
    for seed in SEEDS:
        g = generic_zn_census(B, seed)
        replicas.append(g)
        print(
            f"  seed={seed} T={g['T']} combined={g['combined_relation_count']} "
            f"ratio={g['residual_collision_rate_ratio']} pass={g['certificate_pass_rate_combined']}",
            flush=True,
        )
    primary = replicas[0]
    # curve_over_generic: compare Stage-1 V collision rate / combined to primary
    curve_combined = rV.combined_relation_count
    gen_combined = primary["combined_relation_count"]
    # match T roughly — both exhaustive over same window size
    ratio_combined = (curve_combined / gen_combined) if gen_combined else None
    ratio_collision = None
    if rV.residual_collision_rate_ratio and primary["residual_collision_rate_ratio"]:
        ratio_collision = rV.residual_collision_rate_ratio / primary["residual_collision_rate_ratio"]
    # use combined-count ratio as primary curve_over_generic_ratio
    curve_over_generic = ratio_combined
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()

    dump_yaml(
        ROOT / "stage3" / "generic-replica.yaml",
        {
            "experiment_id": "EXP-BINSTD-cedae5",
            "run_id": RUN_S3,
            "group": f"Z/{RC1_ORDER}",
            "window": "random_matched_size",
            "window_size": B,
            "seeds": SEEDS,
            "replicas": replicas,
            "primary_seed": SEEDS[0],
            "claim_boundary": {"rho_competitiveness_claimed": False, "gttd_claimed": False},
        },
    )
    ratio_doc = {
        "experiment_id": "EXP-BINSTD-cedae5",
        "run_id": RUN_S3_RATIO,
        "curve_run_id": RUN_S1_V,
        "generic_run_id": RUN_S3,
        "curve_combined_relation_count": curve_combined,
        "generic_combined_relation_count_primary": gen_combined,
        "curve_over_generic_ratio": curve_over_generic,
        "curve_collision_rate_ratio": rV.residual_collision_rate_ratio,
        "generic_collision_rate_ratio_primary": primary["residual_collision_rate_ratio"],
        "collision_rate_curve_over_generic": ratio_collision,
        "band": [0.5, 2.0],
        "inside_band": (
            curve_over_generic is not None and 0.5 <= curve_over_generic <= 2.0
        ),
        "concentration_trigger": (
            curve_over_generic is not None
            and (curve_over_generic < 0.5 or curve_over_generic > 2.0 or curve_over_generic > 4.0)
        ),
        "preregistered_prediction_ref": "experiments/EXP-BINSTD-cedae5/stage0/preregistered-predictions.yaml",
    }
    dump_yaml(ROOT / "stage3" / "curve-over-generic.yaml", ratio_doc)

    any_fail = any(g["combined_failed"] for g in replicas)
    write_run_package(
        RUN_S3,
        stage=3,
        arm="generic_replica",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 3",
        parameters={"group": f"Z/{RC1_ORDER}", "window_size": B, "seeds": SEEDS},
        metrics={"replicas": replicas, "any_certificate_failure": any_fail},
        valid=not any_fail,
        invalid_reason="generic replica certificate failure" if any_fail else None,
        termination_reason="completed",
        stdout_text=json.dumps(replicas, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": not any_fail,
            "verifier": "Z/n sum a+b+c+d ≡ 0 (mod 4*32603)",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S3}/raw-result.json",
        },
    )
    write_run_package(
        RUN_S3_RATIO,
        stage=3,
        arm="curve_over_generic",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 3",
        parameters={"curve_run": RUN_S1_V, "generic_run": RUN_S3},
        metrics=ratio_doc,
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps(ratio_doc, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
    )
    return ratio_doc


def stage4() -> dict:
    started = utc_now()
    t0 = __import__("time").perf_counter()
    print("Stage 4: adversarial 8-bit truncated key ...", flush=True)
    r = run_census("V", hash_key_bits=8, recombination=True, verify_all_combined=True)
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    total = r.combined_verified + r.combined_failed
    failure_rate = (r.combined_failed / total) if total else 0.0
    ok_control = failure_rate > 0
    payload = {
        "experiment_id": "EXP-BINSTD-cedae5",
        "run_id": RUN_S4,
        "hash_key_bits": 8,
        "T": r.T,
        "combined_relation_count": r.combined_relation_count,
        "combined_verified": r.combined_verified,
        "combined_failed": r.combined_failed,
        "adversarial_certificate_failure_rate": failure_rate,
        "failure_rate_gt_0": ok_control,
        "certificate_pass_rate_combined": r.certificate_pass_rate_combined,
        "note": (
            "Truncated keys deliberately collide distinct residuals; independent "
            "re-sum must fail at measurable rate (control has power)."
        ),
    }
    dump_yaml(ROOT / "stage4" / "adversarial-truncated-key.yaml", payload)
    metrics = result_to_metrics(r)
    metrics["adversarial_certificate_failure_rate"] = failure_rate
    write_run_package(
        RUN_S4,
        stage=4,
        arm="adversarial",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 4",
        parameters={"hash_key_bits": 8, "window_kind": "V"},
        metrics=metrics,
        valid=ok_control,
        invalid_reason=None if ok_control else "adversarial failure rate == 0 (instrument has no power)",
        termination_reason="completed",
        stdout_text=json.dumps(payload, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": False,  # adversarial: expected failures
            "verifier": "freeleg.verify_combined; truncated key control",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S4}/raw-result.json",
            "adversarial_certificate_failure_rate": failure_rate,
        },
        status_override="completed_valid" if ok_control else "invalid_measurement",
    )
    print(f"  failure_rate={failure_rate}", flush=True)
    return payload


def stage5(ratio_doc: dict) -> None:
    trigger = bool(ratio_doc.get("concentration_trigger"))
    started = utc_now()
    if not trigger:
        payload = {
            "experiment_id": "EXP-BINSTD-cedae5",
            "run_id": RUN_S5,
            "skipped": True,
            "reason": "concentration trigger did not fire",
            "curve_over_generic_ratio": ratio_doc.get("curve_over_generic_ratio"),
            "band": [0.5, 2.0],
            "trigger_rule": "ratio outside [0.5,2] or excess >4x",
        }
        dump_yaml(ROOT / "stage5" / "skip-not-triggered.yaml", payload)
        write_run_package(
            RUN_S5,
            stage=5,
            arm="skip_not_triggered",
            seed=None,
            command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 5",
            parameters={"optional": True},
            metrics=payload,
            valid=True,
            invalid_reason=None,
            termination_reason="completed",
            stdout_text=json.dumps(payload, indent=2) + "\n",
            started_at=started,
            finished_at=utc_now(),
            wall_seconds=0.0,
            certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
        )
        print("Stage 5 skipped (trigger not fired)", flush=True)
        return

    print("Stage 5: concentration trigger fired — n=19 Koblitz sibling census ...", flush=True)
    from freeleg import N19_ORDER, generic_zn_census, run_census_n19

    t0 = __import__("time").perf_counter()
    r = run_census_n19("V", recombination=True, verify_all_combined=True)
    print(
        f"  n19 V: T={r.T} full={r.full_relation_count} combined={r.combined_relation_count} "
        f"pass={r.certificate_pass_rate_combined} ratio={r.residual_collision_rate_ratio} S={r.residual_support_S_fitted}",
        flush=True,
    )
    # matched-size generic replica in Z/(4*130873)
    g = generic_zn_census(r.window_size, SEEDS[0], modulus=N19_ORDER)
    print(
        f"  n19 generic: T={g['T']} combined={g['combined_relation_count']} "
        f"ratio={g['residual_collision_rate_ratio']} pass={g['certificate_pass_rate_combined']}",
        flush=True,
    )
    cog = (
        r.combined_relation_count / g["combined_relation_count"]
        if g["combined_relation_count"]
        else None
    )
    wall = __import__("time").perf_counter() - t0
    finished = utc_now()
    cert_ok = r.combined_failed == 0 and r.certificate_pass_rate_combined == 1.0
    payload = {
        "experiment_id": "EXP-BINSTD-cedae5",
        "run_id": RUN_S5,
        "skipped": False,
        "trigger_source": ratio_doc,
        "curve": "y^2 + xy = x^3 + 1",
        "n": 19,
        "group_order": N19_ORDER,
        "window_deg_lt": 10,
        "census": result_to_metrics(r),
        "generic_replica": g,
        "curve_over_generic_ratio_n19": cog,
        "band": [0.5, 2.0],
        "inside_band_n19": cog is not None and 0.5 <= cog <= 2.0,
        "claim_boundary": {
            "deployed_curve_break_claimed": False,
            "rho_competitiveness_claimed": False,
            "gttd_claimed": False,
        },
    }
    dump_yaml(ROOT / "stage5" / "n19-census.yaml", payload)
    dump_yaml(
        ROOT / "stage5" / "n19-curve-over-generic.yaml",
        {
            "curve_over_generic_ratio_n19": cog,
            "curve_combined": r.combined_relation_count,
            "generic_combined": g["combined_relation_count"],
            "curve_collision_rate_ratio": r.residual_collision_rate_ratio,
            "generic_collision_rate_ratio": g["residual_collision_rate_ratio"],
            "inside_band": payload["inside_band_n19"],
        },
    )
    write_run_package(
        RUN_S5,
        stage=5,
        arm="n19_koblitz_sibling",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 5",
        parameters={"n": 19, "curve": "y^2+xy=x^3+1", "window_deg_lt": 10},
        metrics=payload,
        valid=cert_ok and g["combined_failed"] == 0,
        invalid_reason=None if cert_ok else "n19 certificate failure",
        termination_reason="completed",
        stdout_text=json.dumps(payload, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": cert_ok,
            "verifier": "freeleg.verify_combined on n=19 Curve + Z/n signed cancel",
            "artifact": f"experiments/EXP-BINSTD-cedae5/runs/{RUN_S5}/raw-result.json",
            "combined_verified": r.combined_verified,
            "combined_failed": r.combined_failed,
        },
    )
    # secondary package for generic arm
    write_run_package(
        "RUN-BINSTD-981b8a",
        stage=5,
        arm="n19_generic_replica",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-cedae5/implementation/run_all.py --stage 5",
        parameters={"group": f"Z/{N19_ORDER}", "window_size": r.window_size},
        metrics=g,
        valid=g["combined_failed"] == 0,
        invalid_reason=None if g["combined_failed"] == 0 else "n19 generic cert fail",
        termination_reason="completed",
        stdout_text=json.dumps(g, indent=2, default=str) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": g["combined_failed"] == 0,
            "verifier": "Z/n signed residual cancel",
            "artifact": "experiments/EXP-BINSTD-cedae5/runs/RUN-BINSTD-981b8a/raw-result.json",
        },
    )
    print(f"Stage 5 done; curve_over_generic_n19={cog}", flush=True)


def main(argv: list[str]) -> int:
    stages = set()
    if "--stage" in argv:
        i = argv.index("--stage")
        stages.add(int(argv[i + 1]))
    else:
        stages = {0, 1, 2, 3, 4, 5}
    try:
        if 0 in stages:
            stage0_run()
        s1 = None
        if 1 in stages:
            s1 = stage1()
        if 2 in stages:
            if s1 is None:
                # reload from yaml if running stage2 alone — not supported; require 1
                raise RuntimeError("Stage 2 requires Stage 1 results in-process; run without --stage or with 1 then 2")
            stage2(s1["V"])
        ratio = None
        if 3 in stages:
            if s1 is None:
                raise RuntimeError("Stage 3 requires Stage 1 in-process")
            ratio = stage3(s1["V"])
        if 4 in stages:
            stage4()
        if 5 in stages:
            if ratio is None:
                # read from artifact
                import yaml

                ratio = yaml.safe_load((ROOT / "stage3" / "curve-over-generic.yaml").read_text())
            stage5(ratio)
    except Exception as e:
        traceback.print_exc()
        print(f"FATAL: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
