#!/usr/bin/env python3
"""RUN-DS-001-ctrl-unplanted driver (CTRL-RT025-UNPLANTED + CTRL-RT025-PLANT-LIVE).

Binds to:
  experiments/EXP-DS-001/specification.v2.yaml          (immutable parent, v2)
  experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml (operative control)
  experiments/EXP-DS-001/amendments/v2_ctrl_unplanted.yaml

Single cell: bits=20, B=64, m=4, seed=101.

Differences from ds001_driver.py measure mode, all mandated by the control:
  * Targets are UNPLANTED uniform random points of E(F_p) (rejection-sampled
    lift_x), NOT planted random m-sums.  Planted m-sums are forbidden here as
    the primary yield source.
  * The CTRL-NULL-PLANT positive control is executed as a LIVE /4: the divisor
    is injected into the per-attempt cost accumulator of the split arms
    (real and null) while the measurement runs.  There is no synthetic
    known-answer synth_R / synth_Rn shortcut and no hardcoded
    planted_bug_detected=true.
  * The primary unplanted R / R_null are measured with the plant OFF
    (RT-20260731-042 residual R-1 binding reading).

Search kernels, factor base, backend id, charged-unit function, cost
identities and null object are IMPORTED UNCHANGED from ds001_driver so the
backend identity `ds001-v2-point-sum-membership+charged-units-v1` is
preserved bit-for-bit (CTRL-RT025-UNPLANTED backend clause).

Records observations only.  Interprets nothing; assigns no hypothesis status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for _p in (str(REPO), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ds001_driver as DRV  # noqa: E402  (shared backend: identity preserved)
from harness.toycurve import EllipticCurve, generate_instance, _seed_int  # noqa: E402

RUN_ID = "RUN-DS-001-ctrl-unplanted"
TASK_ID = "TASK-20260731-044"
BATCH_ID = "BATCH-020"
CONTROL_ID = "CTRL-RT025-UNPLANTED"
COMPANION_ID = "CTRL-RT025-PLANT-LIVE"
AMENDMENT_ID = "PA-DS-001-v2-ctrl-unplanted"
PARENT_CONTRACT = "experiments/EXP-DS-001/specification.v2.yaml"
CONTROL_CONTRACT = "experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml"
AMENDMENT_PATH = "experiments/EXP-DS-001/amendments/v2_ctrl_unplanted.yaml"

CELL = {"bits": 20, "B": 64, "m": 4, "seed": 101}
RELATIONS_TARGET = 200
SMOOTHNESS_ABORT = False
PER_TARGET_CAP_SECONDS = 5.0
PLANT_DIVISOR = 4.0

LOG: list[str] = []


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    LOG.append(line)
    print(line, flush=True)


# --------------------------------------------------------------------------
# Unplanted targets
# --------------------------------------------------------------------------

def unplanted_target_stream(E: EllipticCurve, seed: int, count: int) -> tuple[list, dict]:
    """Uniform random points of E(F_p) by rejection sampling on lift_x.

    NOT a planted m-sum.  A target may or may not be decomposable over the
    factor base; that is exactly the quantity this control measures.
    """
    rng = random.Random(_seed_int(seed, "ctrl_unplanted_targets"))
    pts = []
    lift_attempts = 0
    t0 = time.perf_counter()
    while len(pts) < count:
        x = rng.randrange(E.p)
        lift_attempts += 1
        pt = E.lift_x(x)
        if pt is not None:
            pts.append(pt)
    gen_wall = time.perf_counter() - t0
    h = hashlib.sha256()
    for pt in pts:
        h.update(f"{pt[0]},{pt[1]};".encode())
    return pts, {
        "mode": "unplanted_uniform_random",
        "rng_seed_label": "ctrl_unplanted_targets",
        "master_seed": seed,
        "targets_generated": len(pts),
        "lift_x_attempts": lift_attempts,
        "lift_x_acceptance_rate": len(pts) / max(lift_attempts, 1),
        "target_stream_sha256": h.hexdigest(),
        "generation_wall_seconds_not_charged_to_arms": gen_wall,
        "planted_m_sums_used": False,
    }


# --------------------------------------------------------------------------
# Certificates (independent re-verification)
# --------------------------------------------------------------------------

def make_cert(inst, relation: dict) -> dict:
    return {
        "kind": "decomposition",
        "curve": {"p": inst.p, "a": inst.a, "b": inst.b},
        "target": [int(relation["target"][0]), int(relation["target"][1])],
        "summands": [[int(s[0]), int(s[1])] for s in relation["summands"]],
        "method": relation.get("method"),
    }


def independent_verify_decomposition(cert: dict, fb_signed_set: set) -> tuple[bool, str]:
    """Re-check a decomposition using only curve arithmetic rebuilt from the
    certificate itself.  Does not touch naive_search / split_search state."""
    c = cert.get("curve")
    if not c:
        return False, "missing_curve"
    E2 = EllipticCurve(int(c["p"]), int(c["a"]), int(c["b"]))
    target = (int(cert["target"][0]), int(cert["target"][1]))
    if not E2.is_on_curve(target):
        return False, "target_not_on_curve"
    acc = None
    for s in cert["summands"]:
        pt = (int(s[0]), int(s[1]))
        if not E2.is_on_curve(pt):
            return False, "summand_not_on_curve"
        if pt not in fb_signed_set:
            return False, "summand_not_in_factor_base"
        acc = E2.add(acc, pt)
    if acc != target:
        return False, "sum_mismatch"
    if len(cert["summands"]) != CELL["m"]:
        return False, "arity_mismatch"
    return True, "ok"


# --------------------------------------------------------------------------
# Arm harvest with LIVE cost plant
# --------------------------------------------------------------------------

def harvest_real(
    inst,
    E: EllipticCurve,
    fb,
    method: str,
    targets: list,
    relations_target: int,
    wall_budget: float,
    plant_divisor: float,
) -> dict:
    """Real (Semaev-shaped) arm on UNPLANTED targets.

    `plant_divisor` is applied LIVE: every timing / unit segment is divided by
    it at the moment it is recorded, inside the measurement loop.  With
    divisor 1.0 the reported wall equals the honest elapsed wall.
    """
    bits, B, m = CELL["bits"], CELL["B"], CELL["m"]
    t_arm0 = time.perf_counter()
    reported_wall = 0.0
    reported_units = 0.0
    n_usable = 0
    attempted = 0
    rel_wall_samples: list[float] = []
    certs: list[dict] = []
    table = None
    peak_table = 0
    table_build_reported = 0.0

    if method == "split":
        seg0 = time.perf_counter()
        table, entries, _ = DRV.build_claw_table(
            E, fb.signed, m // 2, DRV.frozen_D(bits, m), B, SMOOTHNESS_ABORT,
            time.perf_counter() + wall_budget * 0.4,
        )
        seg = time.perf_counter() - seg0
        table_build_reported = seg / plant_divisor
        reported_wall += table_build_reported
        peak_table = entries

    stop_reason = "target_stream_exhausted"
    for T in targets:
        if n_usable >= relations_target:
            stop_reason = "relations_target_reached"
            break
        if time.perf_counter() - t_arm0 >= wall_budget:
            stop_reason = "arm_wall_budget"
            break
        seg0 = time.perf_counter()
        deadline = min(t_arm0 + wall_budget, seg0 + PER_TARGET_CAP_SECONDS)
        if method == "naive":
            ar = DRV.naive_search(E, fb.signed, T, m, deadline,
                                  lambda mm: DRV.charge_backend_units(mm))
        else:
            assert table is not None
            ar = DRV.split_search(E, fb.signed, T, m, bits, B, table, deadline,
                                  lambda mm: DRV.charge_backend_units(mm), SMOOTHNESS_ABORT)
            peak_table = max(peak_table, ar.peak_table_entries)
        seg = time.perf_counter() - seg0
        reported_wall += seg / plant_divisor
        reported_units += ar.backend_units / plant_divisor
        attempted += 1
        if ar.found and ar.relation and not ar.incomplete:
            n_usable += 1
            rel_wall_samples.append(seg / plant_divisor)
            certs.append(make_cert(inst, ar.relation))
    else:
        if n_usable >= relations_target:
            stop_reason = "relations_target_reached"

    true_wall = time.perf_counter() - t_arm0
    overhead_reported = reported_wall - sum(rel_wall_samples)
    return {
        "method": method,
        "object": "semaev_real",
        "plant_divisor_applied_live": plant_divisor,
        "reported_wall_seconds": reported_wall,
        "true_elapsed_wall_seconds": true_wall,
        "reported_backend_units": reported_units,
        "n_usable_relations": n_usable,
        "attempted_targets": attempted,
        "empirical_success_probability": n_usable / max(attempted, 1),
        "hit_relations_target": n_usable >= relations_target,
        "stop_reason": stop_reason,
        "peak_claw_table_entries": peak_table,
        "table_build_reported_wall_seconds": table_build_reported,
        "per_relation_wall_samples": rel_wall_samples,
        "reported_overhead_wall_seconds": overhead_reported,
        "_certs": certs,
    }


def harvest_null(
    fb,
    method: str,
    relations_target: int,
    wall_budget: float,
    plant_divisor: float,
) -> dict:
    """NULL-DS-RANDOM-MULTIHOMOGENEOUS arm, identical charging and live plant."""
    bits, B, m, seed = CELL["bits"], CELL["B"], CELL["m"], CELL["seed"]
    t_arm0 = time.perf_counter()
    reported_wall = 0.0
    reported_units = 0.0
    n_usable = 0
    tag = 0
    rel_wall_samples: list[float] = []
    stop_reason = "attempt_cap"
    while True:
        if n_usable >= relations_target:
            stop_reason = "relations_target_reached"
            break
        if time.perf_counter() - t_arm0 >= wall_budget:
            stop_reason = "arm_wall_budget"
            break
        if tag > relations_target * 80:
            stop_reason = "attempt_cap_no_progress"
            break
        tag += 1
        seg0 = time.perf_counter()
        deadline = min(t_arm0 + wall_budget, seg0 + PER_TARGET_CAP_SECONDS)
        if method == "naive":
            ar = DRV.null_naive_search(fb.xs, seed, bits, B, m, tag, deadline,
                                       lambda mm: DRV.charge_backend_units(mm))
        else:
            ar = DRV.null_split_search(fb.xs, seed, bits, B, m, tag, deadline,
                                       lambda mm: DRV.charge_backend_units(mm))
        seg = time.perf_counter() - seg0
        reported_wall += seg / plant_divisor
        reported_units += ar.backend_units / plant_divisor
        if ar.found and not ar.incomplete:
            n_usable += 1
            rel_wall_samples.append(seg / plant_divisor)
    true_wall = time.perf_counter() - t_arm0
    return {
        "method": method,
        "object": "null_random_multihomogeneous",
        "plant_divisor_applied_live": plant_divisor,
        "reported_wall_seconds": reported_wall,
        "true_elapsed_wall_seconds": true_wall,
        "reported_backend_units": reported_units,
        "n_usable_relations": n_usable,
        "attempted_targets": tag,
        "empirical_success_probability": n_usable / max(tag, 1),
        "hit_relations_target": n_usable >= relations_target,
        "stop_reason": stop_reason,
        "per_relation_wall_samples": rel_wall_samples,
        "reported_overhead_wall_seconds": reported_wall - sum(rel_wall_samples),
    }


# --------------------------------------------------------------------------
# Cost identities (frozen, identical to specification.v2.yaml)
# --------------------------------------------------------------------------

def arm_cost(arm: dict, rho_gop_per_second: float) -> float:
    return DRV.cost_from_wall(arm["reported_wall_seconds"], rho_gop_per_second,
                              arm["n_usable_relations"])


def bootstrap_R(naive: dict, split: dict, seed_label: str, n_boot: int = 2000
                ) -> Optional[list]:
    """Bootstrap CI for R over per-relation reported wall samples.

    Replicate: R* = (mean(split*) + overhead_split/n_split)
                    / (mean(naive*) + overhead_naive/n_naive)
    which reduces exactly to the frozen point estimate on the identity
    resample.  rho_gop_per_second cancels.
    """
    sn = naive["per_relation_wall_samples"]
    ss = split["per_relation_wall_samples"]
    nn = naive["n_usable_relations"]
    ns = split["n_usable_relations"]
    if not sn or not ss or nn == 0 or ns == 0:
        return None
    ov_n = naive["reported_overhead_wall_seconds"] / nn
    ov_s = split["reported_overhead_wall_seconds"] / ns
    rng = random.Random(_seed_int(CELL["seed"], seed_label))
    reps = []
    for _ in range(n_boot):
        a = sum(sn[rng.randrange(len(sn))] for _ in range(len(sn))) / len(sn)
        b = sum(ss[rng.randrange(len(ss))] for _ in range(len(ss))) / len(ss)
        den = a + ov_n
        if den > 0:
            reps.append((b + ov_s) / den)
    if not reps:
        return None
    reps.sort()
    lo = reps[int(0.025 * len(reps))]
    hi = reps[min(len(reps) - 1, int(0.975 * len(reps)))]
    return [lo, hi]


# --------------------------------------------------------------------------
# One full cell measurement (4 arms) at a given live plant divisor
# --------------------------------------------------------------------------

def measure_cell(inst, E, fb, targets, rho_gop_per_second, relations_target,
                 arm_wall_budget, plant_divisor, tag) -> dict:
    log(f"measure_cell[{tag}] plant_divisor={plant_divisor} "
        f"relations_target={relations_target} arm_wall={arm_wall_budget}s")

    naive = harvest_real(inst, E, fb, "naive", targets, relations_target,
                         arm_wall_budget, 1.0)
    log(f"  real/naive   n_usable={naive['n_usable_relations']} "
        f"attempted={naive['attempted_targets']} "
        f"wall={naive['reported_wall_seconds']:.4f}s stop={naive['stop_reason']}")

    split = harvest_real(inst, E, fb, "split", targets, relations_target,
                         arm_wall_budget, plant_divisor)
    log(f"  real/split   n_usable={split['n_usable_relations']} "
        f"attempted={split['attempted_targets']} "
        f"reported_wall={split['reported_wall_seconds']:.4f}s "
        f"true_wall={split['true_elapsed_wall_seconds']:.4f}s "
        f"stop={split['stop_reason']}")

    naive_null = harvest_null(fb, "naive", relations_target, arm_wall_budget, 1.0)
    log(f"  null/naive   n_usable={naive_null['n_usable_relations']} "
        f"wall={naive_null['reported_wall_seconds']:.4f}s "
        f"stop={naive_null['stop_reason']}")

    split_null = harvest_null(fb, "split", relations_target, arm_wall_budget, plant_divisor)
    log(f"  null/split   n_usable={split_null['n_usable_relations']} "
        f"reported_wall={split_null['reported_wall_seconds']:.4f}s "
        f"true_wall={split_null['true_elapsed_wall_seconds']:.4f}s "
        f"stop={split_null['stop_reason']}")

    cost_naive = arm_cost(naive, rho_gop_per_second)
    cost_split = arm_cost(split, rho_gop_per_second)
    cost_naive_null = arm_cost(naive_null, rho_gop_per_second)
    cost_split_null = arm_cost(split_null, rho_gop_per_second)

    R = cost_split / cost_naive if cost_naive > 0 else None
    R_null = cost_split_null / cost_naive_null if cost_naive_null > 0 else None

    out = {
        "tag": tag,
        "plant_divisor_on_split_arms": plant_divisor,
        "arms": {
            "real_naive": naive, "real_split": split,
            "null_naive": naive_null, "null_split": split_null,
        },
        "rho_gop_per_second": rho_gop_per_second,
        "cost_naive_gops_per_relation": cost_naive,
        "cost_split_gops_per_relation": cost_split,
        "cost_naive_null_gops_per_relation": cost_naive_null,
        "cost_split_null_gops_per_relation": cost_split_null,
        "R": R,
        "R_null": R_null,
        "R_bootstrap_ci_95": bootstrap_R(naive, split, f"boot_R_{tag}"),
        "R_null_bootstrap_ci_95": bootstrap_R(naive_null, split_null, f"boot_Rn_{tag}"),
    }
    log(f"  => R={R} R_null={R_null}")
    return out


def strip_certs(cellmeas: dict) -> tuple[dict, dict]:
    """Move the per-arm certificate lists out of the measurement dict."""
    certs = {}
    for name, arm in cellmeas["arms"].items():
        if "_certs" in arm:
            certs[name] = arm.pop("_certs")
    return cellmeas, certs


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=7200.0,
                    help="hard wall-clock budget for the whole run (seconds)")
    ap.add_argument("--arm-wall", type=float, default=1200.0,
                    help="per-arm wall budget (seconds)")
    ap.add_argument("--relations", type=int, default=RELATIONS_TARGET)
    ap.add_argument("--targets", type=int, default=4000,
                    help="size of the pre-generated unplanted target stream")
    ap.add_argument("--memory-gb", type=float, default=16.0)
    ap.add_argument("--run-dir", default=f"experiments/EXP-DS-001/runs/{RUN_ID}")
    ap.add_argument("--results-dir", default="experiments/EXP-DS-001/results/ctrl_unplanted")
    args = ap.parse_args()

    started = DRV.utc_now()
    t_run0 = time.perf_counter()
    deadline_run = t_run0 + args.wall

    mem_cap_applied = False
    mem_cap_kind = None
    mem_cap_error: dict[str, str] = {}
    cap = int(args.memory_gb * (1 << 30))
    for kind in ("RLIMIT_AS", "RLIMIT_DATA", "RLIMIT_RSS"):
        lim = getattr(resource, kind, None)
        if lim is None:
            mem_cap_error[kind] = "not available on this platform"
            continue
        try:
            soft, hard = resource.getrlimit(lim)
            resource.setrlimit(lim, (cap, hard))
            mem_cap_applied = True
            mem_cap_kind = kind
            break
        except Exception as e:
            mem_cap_error[kind] = f"{type(e).__name__}: {e}"

    log(f"{RUN_ID} start {started}")
    log(f"contract={PARENT_CONTRACT} control={CONTROL_CONTRACT} amendment={AMENDMENT_PATH}")
    log(f"cell={CELL} relations_target={args.relations} smoothness_abort={SMOOTHNESS_ABORT}")
    log(f"backend_id={DRV.BACKEND_ID}")
    log(f"memory_cap_applied={mem_cap_applied} kind={mem_cap_kind} err={mem_cap_error}")

    contract_sha = DRV.sha256_file(REPO / PARENT_CONTRACT)
    control_sha = DRV.sha256_file(REPO / CONTROL_CONTRACT)
    amendment_sha = DRV.sha256_file(REPO / AMENDMENT_PATH)
    log(f"specification.v2.yaml sha256={contract_sha}")
    log(f"CTRL-RT025-UNPLANTED.yaml sha256={control_sha} "
        f"(reviewed-snapshot blob was c85cc14c...; see manifest "
        f"contract.post_review_id_remap_note)")
    log(f"v2_ctrl_unplanted.yaml sha256={amendment_sha}")

    bits, B, m, seed = CELL["bits"], CELL["B"], CELL["m"], CELL["seed"]
    inst = generate_instance(seed, bits)
    E = inst.curve()
    fb = DRV.make_factor_base(inst, B, seed)
    fb_signed_set = set(fb.signed)
    log(f"instance p={inst.p} a={inst.a} b={inst.b} subgroup_n={inst.n} "
        f"group_order={E.order()} fb_x_hash={fb.x_hash}")

    # CTRL-RHO / CTRL-BSGS
    rho = DRV.run_rho(inst)
    bsgs = DRV.run_bsgs(inst)
    rho_gop_per_second = max(rho["total_group_operations"], 1) / max(rho["wall_seconds"], 1e-9)
    log(f"CTRL-RHO solved={rho['solved']} ops={rho['total_group_operations']} "
        f"wall={rho['wall_seconds']:.6f}s cert_verified={rho['certificate_verified']} "
        f"rho_gop_per_second={rho_gop_per_second:.3f}")

    targets, target_meta = unplanted_target_stream(E, seed, args.targets)
    log(f"unplanted targets: {target_meta['targets_generated']} generated, "
        f"lift_x acceptance={target_meta['lift_x_acceptance_rate']:.3f}, "
        f"stream_sha256={target_meta['target_stream_sha256'][:16]}...")

    # ---- PRIMARY measurement: plant OFF (R-1 binding reading) --------------
    primary = measure_cell(inst, E, fb, targets, rho_gop_per_second, args.relations,
                           min(args.arm_wall, max(deadline_run - time.perf_counter(), 1.0)),
                           1.0, "primary_unplanted_plant_off")
    primary, primary_certs = strip_certs(primary)

    # Certificate re-verification (independent of the search code paths)
    cert_stats = {}
    all_ok = True
    for name, certs in primary_certs.items():
        ok = 0
        fails: list[str] = []
        for c in certs:
            good, why = independent_verify_decomposition(c, fb_signed_set)
            if good:
                ok += 1
            else:
                fails.append(why)
        cert_stats[name] = {"count": len(certs), "verified": ok,
                            "failed": len(certs) - ok,
                            "failure_reasons": sorted(set(fails))}
        if ok != len(certs):
            all_ok = False
        log(f"certificates[{name}] {ok}/{len(certs)} independently verified")

    # ---- COMPANION: CTRL-RT025-PLANT-LIVE ---------------------------------
    comp_relations = min(args.relations, 200)
    comp_arm_wall = min(args.arm_wall, max((deadline_run - time.perf_counter()) / 3.0, 1.0))
    comp_off = measure_cell(inst, E, fb, targets, rho_gop_per_second, comp_relations,
                            comp_arm_wall, 1.0, "companion_baseline_plant_off")
    comp_off, comp_off_certs = strip_certs(comp_off)
    comp_on = measure_cell(inst, E, fb, targets, rho_gop_per_second, comp_relations,
                           comp_arm_wall, PLANT_DIVISOR, "companion_live_plant_on")
    comp_on, comp_on_certs = strip_certs(comp_on)

    for label, cs in (("companion_off", comp_off_certs), ("companion_on", comp_on_certs)):
        for name, certs in cs.items():
            ok = sum(1 for c in certs
                     if independent_verify_decomposition(c, fb_signed_set)[0])
            cert_stats[f"{label}:{name}"] = {"count": len(certs), "verified": ok,
                                             "failed": len(certs) - ok,
                                             "failure_reasons": []}
            if ok != len(certs):
                all_ok = False

    # ---- Live detection path ----------------------------------------------
    # No synthetic known-answer, no hardcoded true.  The frozen documents do
    # NOT fix a numeric detection predicate for the live /4 plant, so three
    # named readings are computed and reported side by side; the
    # underspecification is declared rather than resolved by the Executor.
    R_on, Rn_on = comp_on["R"], comp_on["R_null"]
    R_off, Rn_off = comp_off["R"], comp_off["R_null"]
    real_split = comp_on["arms"]["real_split"]
    null_split = comp_on["arms"]["null_split"]
    audit_real = (real_split["true_elapsed_wall_seconds"]
                  / max(real_split["reported_wall_seconds"], 1e-12))
    audit_null = (null_split["true_elapsed_wall_seconds"]
                  / max(null_split["reported_wall_seconds"], 1e-12))
    echo_real = (R_on / R_off) if (R_on and R_off) else None
    echo_null = (Rn_on / Rn_off) if (Rn_on and Rn_off) else None

    # Reading A — S1/F2 numeric null gate borrowed verbatim from
    # specification.v2.yaml (R<0.5 AND R_null<0.9) applied to planted numbers.
    reading_A_on = (R_on is not None and R_on < 0.5
                    and Rn_on is not None and Rn_on < 0.9)
    reading_A_off = (R_off is not None and R_off < 0.5
                     and Rn_off is not None and Rn_off < 0.9)
    # Reading B — literal CTRL-RT025-PLANT-LIVE text "Null gate must FLAG the
    # plant (R_null echo)".  Parameter-free: the false speedup appears on the
    # NULL object too, where no structural claw win is possible.
    reading_B = bool(Rn_on is not None and Rn_off is not None and Rn_on < Rn_off
                     and R_on is not None and R_off is not None and R_on < R_off)
    # Reading C — independent audit: true elapsed wall of the planted split
    # arms vs the wall they reported.
    reading_C = bool(audit_real > 1.5 and audit_null > 1.5)

    planted_bug_detected = reading_B
    log(f"CTRL-RT025-PLANT-LIVE: R_on={R_on} R_null_on={Rn_on} "
        f"R_off={R_off} R_null_off={Rn_off}")
    log(f"CTRL-RT025-PLANT-LIVE readings: A(spec-v2 numeric gate, plant on)"
        f"={reading_A_on} A(plant off)={reading_A_off} "
        f"B(R_null echo, parameter-free)={reading_B} "
        f"C(wall audit)={reading_C}")
    log(f"CTRL-RT025-PLANT-LIVE: echo_R={echo_real} echo_R_null={echo_null} "
        f"audit_real={audit_real:.4f} audit_null={audit_null:.4f}")
    log(f"CTRL-RT025-PLANT-LIVE: planted_bug_detected={planted_bug_detected} "
        f"(reported under Reading B, the operative control's own wording)")
    null_gate_on, null_gate_off, audit_flag = reading_A_on, reading_A_off, reading_C

    plant_readings = {
        "underspecification_declared": (
            "Neither specification.v2.yaml (CTRL-NULL-PLANT) nor "
            "CTRL-RT025-UNPLANTED.yaml (companion_live_plant) fixes a NUMERIC "
            "detection predicate for the live /4 plant. The parent says only "
            "'the null gate must FLAG it (R_null also low)'; the control says "
            "'Null gate must FLAG the plant (R_null echo)'. The Executor "
            "therefore reports three named readings and does NOT invent a "
            "single frozen threshold. Adjudication belongs to the Reviewer / "
            "Coordinator."),
        "reading_A_spec_v2_numeric_gate": {
            "rule": "planted flagged iff R_plant_on < 0.5 AND R_null_plant_on < 0.9",
            "provenance": ("specification.v2.yaml S1/F2 null-gate thresholds, "
                           "applied to the planted numbers"),
            "value_plant_on": reading_A_on,
            "value_plant_off": reading_A_off,
            "discriminates": bool(reading_A_on and not reading_A_off),
        },
        "reading_B_r_null_echo_parameter_free": {
            "rule": ("planted flagged iff R_null_plant_on < R_null_plant_off "
                     "AND R_plant_on < R_plant_off, i.e. the apparent speedup "
                     "echoes onto the structure-destroyed null object"),
            "provenance": ("CTRL-RT025-UNPLANTED.companion_live_plant literal "
                           "wording 'Null gate must FLAG the plant (R_null echo)'"),
            "value": reading_B,
            "echo_ratio_R": echo_real,
            "echo_ratio_R_null": echo_null,
        },
        "reading_C_independent_wall_audit": {
            "rule": ("planted flagged iff true_elapsed/reported > 1.5 on both "
                     "planted split arms (1.5 is an Executor-chosen audit "
                     "threshold, NOT a contract parameter — labelled as such)"),
            "provenance": "Executor cross-check, not a frozen contract rule",
            "value": reading_C,
            "audit_wall_inflation_real_split": audit_real,
            "audit_wall_inflation_null_split": audit_null,
        },
        "reported_planted_bug_detected": planted_bug_detected,
        "reported_under_reading": "B",
    }

    # ---- R-1 observation label (OBSERVATION ONLY) -------------------------
    R, R_null = primary["R"], primary["R_null"]
    if R is None or R_null is None:
        r1_label = "metrics_incomplete"
    elif R < 0.5 and R_null < 0.9:
        r1_label = "F2_eligible"
    elif R < 0.5 and R_null >= 0.9:
        r1_label = "S1_eligible_on_null_axis"
    elif R >= 0.9:
        r1_label = "F1_band"
    else:
        r1_label = "middle_band"
    log(f"R-1 observation label = {r1_label} (observation only; no adjudication)")

    # ---- Status ------------------------------------------------------------
    n_naive = primary["arms"]["real_naive"]["n_usable_relations"]
    n_split = primary["arms"]["real_split"]["n_usable_relations"]
    hit_naive = primary["arms"]["real_naive"]["hit_relations_target"]
    hit_split = primary["arms"]["real_split"]["hit_relations_target"]

    if not all_ok:
        status = "invalid_measurement"
        invalid_reason = "decomposition certificate failed independent re-verification"
    elif n_naive == 0 and n_split == 0:
        status = "resource_exhaustion"
        invalid_reason = ("no usable relations harvested within budget; "
                          "infrastructure/scope-limited, NOT a mathematical negative "
                          "(AGENTS.md rule 5)")
    else:
        status = "completed_valid"
        invalid_reason = None

    run_wall = time.perf_counter() - t_run0
    finished = DRV.utc_now()
    log(f"status={status} run_wall={run_wall:.3f}s")

    # ---- Artifacts ---------------------------------------------------------
    run_dir = REPO / args.run_dir
    res_dir = REPO / args.results_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)

    rusage = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = rusage.ru_maxrss
    if sys.platform != "darwin":
        peak_rss = rusage.ru_maxrss * 1024

    manifest_cert = {
        "kind": "decomposition",
        "verified": all_ok,
        "verifier": ("independent_verify_decomposition (curve rebuilt from the "
                     "certificate, factor-base membership checked) + "
                     "experiments/EXP-DS-001/implementation/verify_certificates.py"),
        "aggregate": cert_stats,
        "statement": (primary_certs.get("real_split") or
                      primary_certs.get("real_naive") or [None])[0],
        "note": ("Every harvested real-arm relation carries a decomposition "
                 "certificate; all were re-summed with curve arithmetic "
                 "reconstructed from the certificate, not from solver state. "
                 "Rho DL certificate recorded separately under controls.CTRL_RHO."),
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": RUN_ID,
        "task_id": TASK_ID,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "control_protocol_id": CONTROL_ID,
        "companion_control_id": COMPANION_ID,
        "protocol_amendment_id": AMENDMENT_ID,
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "contract": {
            "parent": PARENT_CONTRACT,
            "parent_sha256": contract_sha,
            "control": CONTROL_CONTRACT,
            "control_sha256": control_sha,
            "amendment": AMENDMENT_PATH,
            "amendment_sha256": amendment_sha,
            "v1_executed": False,
        },
        "cell": CELL,
        "backend_id": DRV.BACKEND_ID,
        "backend_id_sha256": DRV.sha256_bytes(DRV.BACKEND_ID.encode()),
        "smoothness_abort": SMOOTHNESS_ABORT,
        "relations_target": args.relations,
        "instance": {
            "p": inst.p, "a": inst.a, "b": inst.b,
            "subgroup_order_n": inst.n,
            "full_group_order": E.order(),
            "generator_P": list(inst.P),
            "fb_x_hash": fb.x_hash,
            "factor_base_size": len(fb.xs),
            "signed_factor_base_size": len(fb.signed),
        },
        "target_mode": target_meta,
        "controls": {
            "CTRL_RHO": rho,
            "CTRL_BSGS": bsgs,
            "CTRL_NULL_SHAPE": {
                "null_object_spec_hash": DRV.null_spec_hash(seed, bits, B, m),
                "null_object_id": DRV.NULL_SPEC_ID,
            },
            "CTRL_NULL_RHO": {
                "rho_calib_ratio_real": None,
                "rho_calib_ratio_null": None,
                "status": "not_measured",
                "note": ("Out of CTRL-RT025-UNPLANTED scope. Deliberately NOT "
                         "hardcoded to 1.0; the RT038-B3 rho-calibration defect "
                         "remains unrepaired and is reported as missing."),
            },
            "CTRL_RT025_PLANT_LIVE": {
                "plant_divisor": PLANT_DIVISOR,
                "applied_live_to": ["real_split arm", "null_split arm"],
                "synthetic_known_answer_used": False,
                "hardcoded_detection_used": False,
                "null_gate_plant_on": null_gate_on,
                "null_gate_plant_off": null_gate_off,
                "planted_bug_detected": planted_bug_detected,
                "audit_wall_inflation_real_split": audit_real,
                "audit_wall_inflation_null_split": audit_null,
                "audit_detector_flag": audit_flag,
                "echo_ratio_R_on_over_off": echo_real,
                "echo_ratio_Rnull_on_over_off": echo_null,
                "detection_readings": plant_readings,
            },
            "CTRL_BACKEND_IDENTICAL": {
                "backend_id": DRV.BACKEND_ID,
                "shared_by": ["real_naive", "real_split", "null_naive", "null_split"],
                "charge_function": "ds001_driver.charge_backend_units (unmodified)",
            },
            "CTRL_RANK": {
                "note": ("A usable relation is a verified m-term factor-base "
                         "decomposition of the target; incomplete attempts are "
                         "not counted in any yield."),
            },
            "CTRL_CERT": {"verified": all_ok, "aggregate": cert_stats},
        },
        "measurements": {
            "primary_unplanted_plant_off": primary,
            "companion_baseline_plant_off": comp_off,
            "companion_live_plant_on": comp_on,
        },
        "metrics": {
            "R": R,
            "R_null": R_null,
            "R_bootstrap_ci_95": primary["R_bootstrap_ci_95"],
            "R_null_bootstrap_ci_95": primary["R_null_bootstrap_ci_95"],
            "n_usable_naive": n_naive,
            "n_usable_split": n_split,
            "n_usable_naive_null": primary["arms"]["null_naive"]["n_usable_relations"],
            "n_usable_split_null": primary["arms"]["null_split"]["n_usable_relations"],
            "hit_relations_target_naive": hit_naive,
            "hit_relations_target_split": hit_split,
            "r1_observation_label": r1_label,
            "planted_bug_detected": planted_bug_detected,
            "backend_id": DRV.BACKEND_ID,
            "fb_x_hash": fb.x_hash,
            "null_object_spec_hash": DRV.null_spec_hash(seed, bits, B, m),
        },
        "certificate": manifest_cert,
        "certificates_primary": primary_certs,
        "status": status,
        "invalid_reason": invalid_reason,
        "budget": {
            "wall_clock_seconds_allowed": args.wall,
            "wall_clock_seconds_used": run_wall,
            "memory_gb_allowed": args.memory_gb,
            "memory_cap_applied": mem_cap_applied,
            "memory_cap_kind": mem_cap_kind,
            "memory_cap_errors": mem_cap_error,
            "peak_rss_bytes": peak_rss,
            "maximum_runs": 1,
        },
        "randomness_sources": [
            "master seed 101 -> harness.toycurve.generate_instance(101, 20)",
            "master seed 101 -> harness.semaev.build_factor_base(inst, 64, seed=101)",
            "_seed_int(101, 'ctrl_unplanted_targets') -> unplanted target stream",
            "_seed_int(101, 'null_naive_<tag>') / _seed_int(101, 'null_split_<tag>') "
            "-> null-object samplers (ds001_driver, unmodified)",
            "_seed_int(101, 'boot_R_*') / _seed_int(101, 'boot_Rn_*') -> bootstrap resampling",
        ],
        "interpretation": ("NONE. Observations only. This run assigns no "
                           "hypothesis status and adjudicates no success or "
                           "falsification criterion."),
        "timing": {"started_at": started, "finished_at": finished,
                   "wall_seconds": run_wall},
    }

    (run_dir / "raw-result.json").write_text(
        json.dumps(raw, indent=2, default=str) + "\n", encoding="utf-8")

    g = DRV.git_state()
    env = DRV.env_block()
    env["numpy_version"] = _optional_version("numpy")
    env["sympy_version"] = _optional_version("sympy")
    env["cwd"] = os.getcwd()
    env["repo_root"] = str(REPO)
    env["pid"] = os.getpid()
    env["cpu_count"] = os.cpu_count()
    env["resource_limits"] = {
        "requested_bytes": cap,
        "applied": mem_cap_applied,
        "applied_limit_kind": mem_cap_kind,
        "errors": mem_cap_error,
    }
    (run_dir / "environment.json").write_text(
        json.dumps(env, indent=2, default=str) + "\n", encoding="utf-8")

    manifest = {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": RUN_ID,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "task_id": TASK_ID,
        "goal_id": "GOAL-ECDLP-001",
        "sub_goal_id": "SG-ECDLP-001",
        "batch_id": BATCH_ID,
        "contract": {
            "path": PARENT_CONTRACT,
            "version": "2 (parent, immutable)",
            "parent_sha256": contract_sha,
            "parent_sha256_expected": "898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a",
            "parent_sha256_matches": contract_sha == "898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a",
            "control_protocol_path": CONTROL_CONTRACT,
            "control_protocol_sha256": control_sha,
            "control_protocol_id": CONTROL_ID,
            "companion_control_id": COMPANION_ID,
            "amendment_path": AMENDMENT_PATH,
            "amendment_sha256": amendment_sha,
            "amendment_id": AMENDMENT_ID,
            "narrowed_version": "2.1-ctrl",
            "approval_receipt": ("coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/"
                                 "archives/TASK-20260731-043/snapshot_commit_receipt.json"),
            "approval_determination": "APPROVED",
            "approval_commit": "64981f9a44606770b3ac288344e6a8d69e540e87",
            "reviewer_verdict": "PASS (RT-20260731-042)",
            "v1_executed": False,
            "post_review_id_remap_note": {
                "observed": ("The live CTRL-RT025-UNPLANTED.yaml and "
                             "v2_ctrl_unplanted.yaml blobs at HEAD differ from the "
                             "blobs reviewed at snapshot cac4d8b4."),
                "control_sha256_at_reviewed_snapshot_cac4d8b4":
                    "c85cc14cf4d5f1a2a693b84756b28fa0abc08f0e8a5a246701f442e97fda060c",
                "control_sha256_at_HEAD_executed": control_sha,
                "amendment_sha256_at_reviewed_snapshot_cac4d8b4":
                    "2c9ab2e1422185b5e1426380e9d4142d09b6f3c57611156127dbf18184827ea0",
                "amendment_sha256_at_HEAD_executed": amendment_sha,
                "cause": ("Post-review merge commits 69df8230b / da6f4fdaf / "
                          "d28767320 remapped colliding DEC ids after merging "
                          "origin/main (DEC-20260731-003->022, -009->018, "
                          "-005->023)."),
                "substantive_delta": ("Five cross-reference lines only "
                                      "(parent_approval_decision, sources, "
                                      "prior_disposition, discharges.source). No "
                                      "change to cell, target_mode, backend, "
                                      "smoothness_abort, relations_target, budget, "
                                      "R-1, companion_live_plant, or claim ceiling."),
                "executor_action": ("Executed against the HEAD blobs; recorded "
                                    "both hashes. The Executor did NOT edit these "
                                    "frozen files. Flagged for Validator/Coordinator."),
            },
            "approved_by_in_file": None,
            "d1_note": ("approved_by is null in specification.v2.yaml by design; "
                        "approval lives in the TASK-20260731-043 receipt."),
        },
        "status": status,
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "code": {
            "commit": g.get("commit"),
            "dirty": g.get("dirty"),
            "branch": g.get("branch"),
            "driver": "experiments/EXP-DS-001/implementation/ds001_ctrl_unplanted.py",
            "driver_sha256": DRV.sha256_file(Path(__file__)),
            "shared_backend_module": "experiments/EXP-DS-001/implementation/ds001_driver.py",
            "shared_backend_module_sha256": DRV.sha256_file(HERE / "ds001_driver.py"),
            "shared_backend_module_modified": False,
            "command": ((run_dir / "command.txt").read_text().strip()
                        if (run_dir / "command.txt").exists() else None),
            "argv": sys.argv,
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "claude-opus-5 (Claude Code subagent; runtime-reported)",
            "reasoning_effort": None,
            "fallback_used": True,
            "fallback_reason": ("This Claude Code harness cannot resolve "
                                "orchestration/model-policies.yaml GPT-5.6-family policy "
                                "aliases; subagent frontmatter supports Claude models "
                                "only. Recorded rather than silently substituted."),
            "model_verified": False,
            "independent_session_required": False,
            "adapter_version": None,
        },
        "environment": env,
        "inputs": {
            "cell": CELL,
            "seeds": [seed],
            "target_mode": "unplanted_uniform_random",
            "planted_m_sums_used_as_primary_yield": False,
            "relations_target": args.relations,
            "smoothness_abort": SMOOTHNESS_ABORT,
            "backend_id": DRV.BACKEND_ID,
            "backend_id_sha256": DRV.sha256_bytes(DRV.BACKEND_ID.encode()),
            "backend_id_matches_planted_package": (
                DRV.BACKEND_ID == "ds001-v2-point-sum-membership+charged-units-v1"),
            "target_stream_sha256": target_meta["target_stream_sha256"],
            "fb_x_hash": fb.x_hash,
            "null_object_spec_hash": DRV.null_spec_hash(seed, bits, B, m),
        },
        "timing": {"started_at": started, "finished_at": finished,
                   "wall_seconds": run_wall},
        "resources": {
            "peak_rss_bytes": peak_rss,
            "cpu_seconds": rusage.ru_utime + rusage.ru_stime,
            "memory_gb_limit": args.memory_gb,
            "wall_clock_seconds_limit": args.wall,
        },
        "result": {
            "metrics": raw["metrics"],
            "valid": status == "completed_valid",
            "invalid_reason": invalid_reason,
            "certificate": manifest_cert,
        },
        "artifacts": {
            "raw-result.json": str(run_dir / "raw-result.json"),
            "stdout.txt": str(run_dir / "stdout.txt"),
            "stderr.txt": str(run_dir / "stderr.txt"),
            "command.txt": str(run_dir / "command.txt"),
            "environment.json": str(run_dir / "environment.json"),
            "summary.json": str(res_dir / "summary.json"),
            "R_cell.json": str(res_dir / "R_cell.json"),
            "null_control_report.json": str(res_dir / "null_control_report.json"),
            "live_plant_report.json": str(res_dir / "live_plant_report.json"),
        },
        "interpretation": "NONE. Executor records observations only.",
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")

    # ---- results/ctrl_unplanted -------------------------------------------
    R_cell = {
        "schema": "exp_ds_001.ctrl_unplanted.R_cell.v1",
        "run_id": RUN_ID,
        "control_protocol_id": CONTROL_ID,
        "cell": CELL,
        "plant_state_for_these_numbers": "OFF (R-1 binding reading)",
        "target_mode": target_meta,
        "measured": {
            "R": R,
            "R_null": R_null,
            "R_bootstrap_ci_95": primary["R_bootstrap_ci_95"],
            "R_null_bootstrap_ci_95": primary["R_null_bootstrap_ci_95"],
            "cost_naive_gops_per_relation": primary["cost_naive_gops_per_relation"],
            "cost_split_gops_per_relation": primary["cost_split_gops_per_relation"],
            "cost_naive_null_gops_per_relation": primary["cost_naive_null_gops_per_relation"],
            "cost_split_null_gops_per_relation": primary["cost_split_null_gops_per_relation"],
            "rho_gop_per_second": rho_gop_per_second,
            "wall_seconds_naive": primary["arms"]["real_naive"]["reported_wall_seconds"],
            "wall_seconds_split": primary["arms"]["real_split"]["reported_wall_seconds"],
            "wall_seconds_naive_null": primary["arms"]["null_naive"]["reported_wall_seconds"],
            "wall_seconds_split_null": primary["arms"]["null_split"]["reported_wall_seconds"],
            "n_usable_naive": n_naive,
            "n_usable_split": n_split,
            "n_usable_naive_null": primary["arms"]["null_naive"]["n_usable_relations"],
            "n_usable_split_null": primary["arms"]["null_split"]["n_usable_relations"],
            "attempted_targets_naive": primary["arms"]["real_naive"]["attempted_targets"],
            "attempted_targets_split": primary["arms"]["real_split"]["attempted_targets"],
            "empirical_success_probability_naive":
                primary["arms"]["real_naive"]["empirical_success_probability"],
            "empirical_success_probability_split":
                primary["arms"]["real_split"]["empirical_success_probability"],
            "hit_relations_target_naive": hit_naive,
            "hit_relations_target_split": hit_split,
            "stop_reason_naive": primary["arms"]["real_naive"]["stop_reason"],
            "stop_reason_split": primary["arms"]["real_split"]["stop_reason"],
            "peak_claw_table_entries": primary["arms"]["real_split"]["peak_claw_table_entries"],
        },
        "modeled": {
            "bsgs_group_operations_modeled": bsgs["group_operations_modeled"],
            "bsgs_storage_elements_modeled": bsgs["storage_elements_modeled"],
            "label": "modeled — cost model only, not measured",
        },
        "cost_identities_used": {
            "rho_gop_per_second": "rho_total_group_operations / rho_wall_seconds (CTRL-RHO receipt)",
            "cost_naive": "wall_seconds_naive * rho_gop_per_second / max(n_usable_naive, 1)",
            "cost_split": "wall_seconds_split * rho_gop_per_second / max(n_usable_split, 1)",
            "R": "cost_split / cost_naive",
            "R_null": "cost_split_null / cost_naive_null",
            "identical_to": "specification.v2.yaml cost_identities",
        },
        "r1_observation_label": r1_label,
        "r1_rule_quoted": ("R-1: if R<0.5 and R_null<0.9, observation label is "
                           "F2_eligible. OBSERVATION LABEL ONLY — the Executor "
                           "does not adjudicate what it means."),
        "claim_tier": "toy",
        "interpretation": "NONE.",
    }
    (res_dir / "R_cell.json").write_text(
        json.dumps(R_cell, indent=2, default=str) + "\n", encoding="utf-8")

    null_report = {
        "schema": "exp_ds_001.ctrl_unplanted.null_control_report.v1",
        "run_id": RUN_ID,
        "null_object_id": DRV.NULL_SPEC_ID,
        "null_object_spec_hash": DRV.null_spec_hash(seed, bits, B, m),
        "construction": ("Random multihomogeneous membership oracle at matched "
                         "multidegree [2]*m with independent left/right half "
                         "keys (structure destruction, IDEA-20260731-011). "
                         "Imported unchanged from ds001_driver.py."),
        "plant_state_for_these_numbers": "OFF",
        "measured": {
            "R_null": R_null,
            "R_null_bootstrap_ci_95": primary["R_null_bootstrap_ci_95"],
            "cost_naive_null_gops_per_relation": primary["cost_naive_null_gops_per_relation"],
            "cost_split_null_gops_per_relation": primary["cost_split_null_gops_per_relation"],
            "null_naive_arm": primary["arms"]["null_naive"],
            "null_split_arm": primary["arms"]["null_split"],
        },
        "gate_reference": ("CTRL-RT025-UNPLANTED null_control.gate: report R and "
                           "R_null; R-1 binding."),
        "r1_observation_label": r1_label,
        "CTRL_NULL_RHO": raw["controls"]["CTRL_NULL_RHO"],
        "CTRL_NULL_SHAPE_present": True,
        "claim_tier": "toy",
        "interpretation": "NONE.",
    }
    (res_dir / "null_control_report.json").write_text(
        json.dumps(null_report, indent=2, default=str) + "\n", encoding="utf-8")

    plant_report = {
        "schema": "exp_ds_001.ctrl_unplanted.live_plant_report.v1",
        "run_id": RUN_ID,
        "control_id": COMPANION_ID,
        "method_quoted": ("On one real-arm measurement of the same cell, inflate "
                          "reported split costs by live /4 ... WITHOUT synthetic "
                          "known-answer synth_R/synth_Rn shortcuts. Null gate must "
                          "FLAG the plant (R_null echo) without hardcoded "
                          "planted_bug_detected=true."),
        "implementation": {
            "plant_divisor": PLANT_DIVISOR,
            "injection_point": ("harvest_real / harvest_null: every per-attempt "
                                "timing segment and every charged backend-unit "
                                "increment on the SPLIT arms is divided by 4 at "
                                "the moment it is recorded, inside the live "
                                "measurement loop."),
            "arms_planted": ["real_split", "null_split"],
            "arms_clean": ["real_naive", "null_naive"],
            "synthetic_known_answer_used": False,
            "synth_R_or_synth_Rn_constants_present": False,
            "hardcoded_planted_bug_detected": False,
            "primary_R_measured_with_plant_off": True,
        },
        "measured": {
            "baseline_plant_off": {"R": R_off, "R_null": Rn_off,
                                   "relations_target": comp_relations},
            "live_plant_on": {"R": R_on, "R_null": Rn_on,
                              "relations_target": comp_relations},
            "echo_ratio_R_on_over_off": echo_real,
            "echo_ratio_Rnull_on_over_off": echo_null,
            "audit_wall_inflation_real_split": audit_real,
            "audit_wall_inflation_null_split": audit_null,
            "audit_detector_flag": audit_flag,
        },
        "detection": {
            "readings": plant_readings,
            "null_gate_plant_on_reading_A": null_gate_on,
            "null_gate_plant_off_reading_A": null_gate_off,
            "planted_bug_detected": planted_bug_detected,
            "planted_bug_detected_reading": "B (R_null echo, parameter-free)",
            "planted_bug_detected_under_reading_A": null_gate_on,
            "planted_bug_detected_under_reading_C": audit_flag,
            "pass_condition_quoted": ("planted_bug_detected true via live /4 "
                                      "detection path; synthetic-only detection "
                                      "is insufficient for discharge."),
            "pass_condition_met_under_reading_B": planted_bug_detected,
            "pass_condition_met_under_reading_A": null_gate_on,
            "falsifies_if_quoted": ("Live plant not detected while summary still "
                                    "claims planted_bug_detected=true."),
            "falsification_triggered": False,
            "falsification_note": ("Not triggered: every reading is reported at "
                                   "its measured value; no reading is asserted "
                                   "true where the measurement says otherwise."),
            "audit_note": ("audit_wall_inflation_* is an independent live "
                           "cross-check: true elapsed wall of the planted split "
                           "arm divided by the wall it reported. ~4 means the "
                           "reported cost was corrupted by the live /4; ~1 means "
                           "it was not. Computed from measurements, not asserted."),
        },
        "companion_arm_detail": {
            "plant_off": comp_off,
            "plant_on": comp_on,
        },
        "claim_tier": "toy",
        "interpretation": "NONE.",
    }
    (res_dir / "live_plant_report.json").write_text(
        json.dumps(plant_report, indent=2, default=str) + "\n", encoding="utf-8")

    summary = {
        "schema": "exp_ds_001.ctrl_unplanted.summary.v1",
        "run_id": RUN_ID,
        "task_id": TASK_ID,
        "batch_id": BATCH_ID,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "hypothesis_status_changed_by_this_run": False,
        "control_protocol_id": CONTROL_ID,
        "companion_control_id": COMPANION_ID,
        "status": status,
        "invalid_reason": invalid_reason,
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "cell": CELL,
        "target_mode": "unplanted_uniform_random (planted m-sums NOT used)",
        "backend_id": DRV.BACKEND_ID,
        "smoothness_abort": SMOOTHNESS_ABORT,
        "relations_target": args.relations,
        "measured": {
            "R": R,
            "R_null": R_null,
            "R_bootstrap_ci_95": primary["R_bootstrap_ci_95"],
            "R_null_bootstrap_ci_95": primary["R_null_bootstrap_ci_95"],
            "n_usable_naive": n_naive,
            "n_usable_split": n_split,
            "n_usable_naive_null": primary["arms"]["null_naive"]["n_usable_relations"],
            "n_usable_split_null": primary["arms"]["null_split"]["n_usable_relations"],
            "hit_relations_target_naive": hit_naive,
            "hit_relations_target_split": hit_split,
            "either_arm_hit_relations_target": bool(hit_naive or hit_split),
            "attempted_targets_naive": primary["arms"]["real_naive"]["attempted_targets"],
            "attempted_targets_split": primary["arms"]["real_split"]["attempted_targets"],
            "empirical_success_probability_naive":
                primary["arms"]["real_naive"]["empirical_success_probability"],
            "empirical_success_probability_split":
                primary["arms"]["real_split"]["empirical_success_probability"],
            "planted_bug_detected": planted_bug_detected,
            "planted_bug_detected_reading": "B (R_null echo, parameter-free)",
            "planted_bug_detection_readings": plant_readings,
            "rho_gop_per_second": rho_gop_per_second,
            "wall_seconds_run": run_wall,
            "peak_rss_bytes": peak_rss,
        },
        "modeled": {
            "bsgs_group_operations_modeled": bsgs["group_operations_modeled"],
            "bsgs_storage_elements_modeled": bsgs["storage_elements_modeled"],
            "assembled_E_proxy": None,
            "assembled_E_proxy_status": "not_computed (out of control scope)",
        },
        "optimistic_assumptions_restated": [
            "Charged units use a frozen backend cost proxy "
            "(ds001_driver.charge_backend_units), NOT a per-attempt Groebner "
            "solve; this is optimistic for BOTH arms equally and is the "
            "pre-existing v2 deviation.",
            "rho_gop_per_second comes from one matched CTRL-RHO capture on this "
            "instance and is reused for all arms; it cancels in R.",
            "BSGS numbers are modeled from 2*ceil(sqrt(N)), never measured.",
        ],
        "r1_observation_label": r1_label,
        "r1_note": ("Observation label only. The Executor does not adjudicate "
                    "S1/F1/F2/F3, does not declare the heuristic validated or "
                    "refuted, and changes no hypothesis status."),
        "certificate_summary": {"all_verified": all_ok, "per_arm": cert_stats},
        "packaging_falsification_rule_reference": (
            "CTRL-RT025-UNPLANTED.packaging_falsification_rule — frozen text "
            "reproduced in the control file; adjudication belongs to the "
            "Reviewer/Coordinator, not this run."),
        "interpretation": "NONE.",
    }
    (res_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    log("artifacts written:")
    for p in ["manifest.json", "raw-result.json", "environment.json"]:
        log(f"  {run_dir / p}")
    for p in ["summary.json", "R_cell.json", "null_control_report.json",
              "live_plant_report.json"]:
        log(f"  {res_dir / p}")

    # stdout.txt / stderr.txt are produced by shell redirection of this process;
    # the in-process log is duplicated here for robustness.
    log(f"{RUN_ID} end status={status}")
    return 0


def _optional_version(mod: str) -> Optional[str]:
    try:
        return __import__(mod).__version__
    except Exception:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
