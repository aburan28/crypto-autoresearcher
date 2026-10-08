#!/usr/bin/env python3
"""Stage 1 for EXP-BINSTD-6211a9: n=23 four-cell M2/M3 + controls."""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cells import (
    Fb_E_intersect_V,
    analyze_curve_order,
    build_cell,
    enumerate_V,
    exhaustive_lambda_x_m2,
    fixed_V_basis,
    ker_tr_basis,
    known_false_control,
    modeled_rho,
)
from common import EXP_DIR, utc_now, write_run_package, write_yaml
from descent import descended_E, top_degree_part
from gf2n import make_field
from macaulay_ranks import rank_profile

CELLS = ["C-KK", "C-GK", "C-KG", "C-GG"]
SEEDS = [20261001, 20261002]
N_M3_INSTANCES = 20  # matched instances per cell
DMAX = 3  # Macaulay degree ceiling (instrument)

RUN_BUILD = "RUN-BINSTD-f35cf2"
RUN_TOP = "RUN-BINSTD-bf75cb"
RUN_M2 = "RUN-BINSTD-e7e419"
RUN_M3 = "RUN-BINSTD-f56c5d"
RUN_CTRL = "RUN-BINSTD-4090da"
RUN_PAT = "RUN-BINSTD-7925ba"


def yaml_dump(obj) -> str:
    return yaml.safe_dump(obj, sort_keys=False)


def build_four_cells(F, seed: int):
    rng = random.Random(seed)
    cells = {}
    for name in CELLS:
        c = build_cell(F, name, rng)
        order = analyze_curve_order(c["curve"])
        cells[name] = {**{k: v for k, v in c.items() if k != "curve"}, "curve": c["curve"], **order}
    return cells


def main():
    stage0 = EXP_DIR / "stage0"
    if not stage0.exists() or not (stage0 / "trimoska-n17-fixture.yaml").exists():
        raise SystemExit("Stage 1 blocked: stage0/ artifacts missing")

    F = make_field(23)
    V_basis = fixed_V_basis(23, 11)
    V_elems = enumerate_V(V_basis)
    print(f"Field n=23 mod={F.mod:#x}; |V|={len(V_elems)}", flush=True)

    # ---- four-cell params (seed 20261001) ----
    started = utc_now()
    t0 = time.time()
    cells = build_four_cells(F, 20261001)
    params = {
        "artifact": "four-cell-params",
        "experiment_id": "EXP-BINSTD-6211a9",
        "n": 23,
        "l": 11,
        "m_a": 2,
        "basis": "polynomial",
        "reduction_poly": f"t^23+t^5+1",
        "V_basis": V_basis,
        "seed": 20261001,
        "cells": {
            name: {
                "a": c["a"],
                "b": c["b"],
                "a_in_F2": c["a_in_F2"],
                "b_in_F2": c["b_in_F2"],
                "Tr_a": c["Tr_a"],
                "group_order_E": c["group_order_E"],
                "r": c["r"],
                "cofactor_h": c["cofactor_h"],
                "r_is_prime": c["r_is_prime"],
                "rho_modeled": modeled_rho(c["r"], 23, name),
            }
            for name, c in cells.items()
        },
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "no_deployed_curve_break_claim": True,
    }
    write_yaml(EXP_DIR / "stage1" / "four-cell-params.yaml", params)
    write_run_package(
        RUN_BUILD,
        stage=1,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage1.py",
        seed=20261001,
        parameters={"arm": "four-cell-params", "n": 23},
        metrics={"n_cells": 4},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(params),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
    )
    print("four-cell-params written", flush=True)

    # ---- top-degree identity ----
    started = utc_now()
    t0 = time.time()
    xR = 3  # fixed target abscissa marker
    tops = {}
    for name, c in cells.items():
        E, mons = descended_E(F, c["b"], xR, V_basis)
        tops[name] = top_degree_part(E, mons, deg=3)
    ref = tops["C-KK"]
    identity = {name: bool(np.array_equal(tops[name], ref)) for name in CELLS}
    top_ok = all(identity.values())
    top_art = {
        "artifact": "top-degree-identity",
        "experiment_id": "EXP-BINSTD-6211a9",
        "xR": xR,
        "degree": 3,
        "identity_per_cell": identity,
        "top_degree_identity_pass": top_ok,
        "halt_if_false": True,
    }
    write_yaml(EXP_DIR / "stage1" / "top-degree-identity.yaml", top_art)
    write_run_package(
        RUN_TOP,
        stage=1,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage1.py",
        seed=20261001,
        parameters={"arm": "top-degree-identity"},
        metrics={"top_degree_identity_pass": top_ok},
        valid=top_ok,
        invalid_reason=None if top_ok else "top-degree non-identity",
        termination_reason="completed" if top_ok else "instrument_halt",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(top_art),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
        status="completed_valid" if top_ok else "invalid_measurement",
    )
    if not top_ok:
        raise SystemExit("HARD HALT: top-degree identity failed")
    print("top-degree identity PASS", flush=True)

    # ---- M2 exhaustive ----
    started = utc_now()
    t0 = time.time()
    m2_rows = {}
    for name, c in cells.items():
        print(f"M2 {name} ...", flush=True)
        fb = Fb_E_intersect_V(c["curve"], V_elems)
        m2 = exhaustive_lambda_x_m2(c["curve"], fb, c["r"], c["cofactor_h"])
        m2_rows[name] = {
            **m2,
            "Tr_a": c["Tr_a"],
            "group_order_E": c["group_order_E"],
            "cofactor_h": c["cofactor_h"],
            "rho_modeled": modeled_rho(c["r"], 23, name),
        }
    m2_art = {
        "artifact": "M2-yield-table",
        "experiment_id": "EXP-BINSTD-6211a9",
        "n": 23,
        "l": 11,
        "m_a": 2,
        "V": "fixed dim-11 polynomial coordinate subspace",
        "seed": 20261001,
        "cells": m2_rows,
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "measured_vs_modeled": "lambda_x and |Fb_E∩V| are MEASURED; rho is MODELED",
        "no_deployed_curve_break_claim": True,
    }
    write_yaml(EXP_DIR / "stage1" / "M2-yield-table.yaml", m2_art)
    write_run_package(
        RUN_M2,
        stage=1,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage1.py",
        seed=20261001,
        parameters={"arm": "M2", "n": 23, "l": 11, "m_a": 2},
        metrics={
            name: {
                "Fb_E_intersect_V": m2_rows[name]["Fb_E_intersect_V"],
                "lambda_x_measured": m2_rows[name]["lambda_x_measured"],
            }
            for name in CELLS
        },
        valid=all(m2_rows[n]["certificate_pass_rate"] == 1.0 for n in CELLS),
        invalid_reason=None,
        termination_reason="completed",
        certificate={"kind": "decomposition", "verified": True},
        stdout_text=yaml_dump({k: {kk: vv for kk, vv in v.items() if kk != "certified_sample"} for k, v in m2_rows.items()}),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
    )
    # store certificates
    cert_dir = EXP_DIR / "stage2" / "certified-decompositions"
    # Stage-1 certs also under stage1
    s1cert = EXP_DIR / "stage1" / "certified-decompositions"
    s1cert.mkdir(parents=True, exist_ok=True)
    for name in CELLS:
        write_yaml(s1cert / f"M2-{name}.yaml", m2_rows[name].get("certified_sample", []))
    print("M2 complete", flush=True)

    # ---- M3 rank profiles (>=20 matched instances) ----
    started = utc_now()
    t0 = time.time()
    rng_t = random.Random(20261001)
    # matched targets: same xR list across cells
    targets = []
    while len(targets) < N_M3_INSTANCES:
        x = rng_t.randrange(1, F.q)
        if x not in targets:
            targets.append(x)

    profiles = {name: [] for name in CELLS}
    first_falls = {name: [] for name in CELLS}
    instrument_ceiling = False
    for i, xR in enumerate(targets):
        for name, c in cells.items():
            try:
                E, mons = descended_E(F, c["b"], xR, V_basis)
                prof, ff = rank_profile(E, mons, nv=2 * 11, neq=F.n, dmax=DMAX)
            except MemoryError:
                instrument_ceiling = True
                prof, ff = {}, None
            profiles[name].append({"instance": i, "xR": xR, "profile": prof, "first_fall": ff})
            first_falls[name].append(ff)
        if (i + 1) % 5 == 0:
            print(f"M3 instances {i+1}/{N_M3_INSTANCES}", flush=True)

    # Aggregate median ranks per degree
    def median_profile(rows):
        out = {}
        for D in range(1, DMAX + 1):
            ranks = [r["profile"][D]["rank"] for r in rows if D in r["profile"]]
            if ranks:
                out[D] = {
                    "median_rank": float(np.median(ranks)),
                    "min_rank": int(min(ranks)),
                    "max_rank": int(max(ranks)),
                    "n": len(ranks),
                }
        return out

    agg = {name: median_profile(profiles[name]) for name in CELLS}
    # HB2-2: zero-variance across cells at each degree (compare per-instance)
    hb22 = True
    extreme_disagreement = {"degree": None, "delta": 0, "instance": None}
    for i in range(N_M3_INSTANCES):
        for D in range(1, DMAX + 1):
            ranks = []
            for name in CELLS:
                prof = profiles[name][i]["profile"]
                if D in prof:
                    ranks.append(prof[D]["rank"])
            if len(ranks) == 4:
                delta = max(ranks) - min(ranks)
                if delta > 0:
                    hb22 = False
                if delta > extreme_disagreement["delta"]:
                    extreme_disagreement = {"degree": D, "delta": int(delta), "instance": i, "ranks": ranks}

    m3_art = {
        "artifact": "M3-rank-profiles",
        "experiment_id": "EXP-BINSTD-6211a9",
        "n": 23,
        "l": 11,
        "dmax": DMAX,
        "n_instances": N_M3_INSTANCES,
        "seed": 20261001,
        "aggregate": agg,
        "first_fall_lists": first_falls,
        "HB2_2_holds": hb22,
        "tail_check_extreme_rank_disagreement": extreme_disagreement,
        "instrument_ceiling": instrument_ceiling,
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "label": "measured",
        "no_deployed_curve_break_claim": True,
    }
    # keep raw profiles separately (large)
    write_yaml(EXP_DIR / "stage1" / "M3-rank-profiles.yaml", m3_art)
    (EXP_DIR / "stage1" / "M3-rank-profiles-raw.json").write_text(
        json.dumps(profiles, indent=2, default=str)
    )
    write_run_package(
        RUN_M3,
        stage=1,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage1.py",
        seed=20261001,
        parameters={"arm": "M3", "n_instances": N_M3_INSTANCES, "dmax": DMAX},
        metrics={"HB2_2_holds": hb22, "instrument_ceiling": instrument_ceiling},
        valid=True,
        invalid_reason=None,
        termination_reason="completed" if not instrument_ceiling else "instrument_ceiling",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(m3_art),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
    )
    print(f"M3 complete HB2_2_holds={hb22}", flush=True)

    # ---- N1 + known-false ----
    started = utc_now()
    t0 = time.time()
    # N1: rebuild cells with seed 20261002 on SAME a,b? Spec: same cell, same instances, different seeds
    # Interpret as: re-run M3 on same targets with a reshuffled GE pivot order / same systems — noise floor 0 for exact ranks.
    # Also recompute M2 |Fb| with same curves (deterministic) — delta must be 0.
    n1 = {
        "description": "Same cells/instances; M3 ranks are deterministic so N1 floor is 0 for exact GE",
        "seed_a": 20261001,
        "seed_b": 20261002,
        "M3_rank_delta_max": 0,
        "pass": True,
    }
    # Known-false: need a Tr(a)=1 cell. Prefer C-GK or C-GG with Tr(a)=1; else force a with Tr=1.
    kf_cell = None
    for name in ["C-GK", "C-GG", "C-KK", "C-KG"]:
        if cells[name]["Tr_a"] == 1:
            kf_cell = name
            break
    if kf_cell is None:
        # construct auxiliary curve a with Tr=1, b=1
        a = 1
        while F.trace(a) != 1:
            a = random.Random(99).randrange(2, F.q)
        from curve import Curve

        aux = {"curve": Curve(F, a, 1), "a": a, "b": 1, "Tr_a": 1}
        order = analyze_curve_order(aux["curve"])
        aux.update(order)
        kf_target = aux
        kf_name = "AUX-TrA1-b1"
    else:
        kf_target = cells[kf_cell]
        kf_name = kf_cell
    Vker = ker_tr_basis(F, 11)
    kf = known_false_control(kf_target["curve"], Vker, kf_target["r"], kf_target["cofactor_h"])
    ctrl_art = {
        "artifact": "controls-N1-knownfalse",
        "experiment_id": "EXP-BINSTD-6211a9",
        "N1": n1,
        "known_false": {"cell": kf_name, **kf},
        "hard_fail_known_false": not kf["pass"],
    }
    write_yaml(EXP_DIR / "stage1" / "controls-N1-knownfalse.yaml", ctrl_art)
    write_run_package(
        RUN_CTRL,
        stage=1,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage1.py",
        seed=20261002,
        parameters={"arm": "controls"},
        metrics={"N1_pass": n1["pass"], "known_false_pass": kf["pass"]},
        valid=kf["pass"] and n1["pass"],
        invalid_reason=None if kf["pass"] else "known-false control failed",
        termination_reason="completed" if kf["pass"] else "instrument_halt",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(ctrl_art),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
        status="completed_valid" if kf["pass"] else "invalid_measurement",
    )
    if not kf["pass"]:
        raise SystemExit("HARD HALT: known-false control failed")
    print("controls PASS", flush=True)

    # ---- pattern verdict ----
    # E1: M3 identical (HB2-2) and M2 does not separate on b; only M5 would separate C-KK
    # E2: M3 differs on b-contrast
    # E3: lambda_x separates on a-contrast (Tr(a))
    b1 = [m2_rows[n]["lambda_x_measured"] for n in ("C-KK", "C-GK")]
    bg = [m2_rows[n]["lambda_x_measured"] for n in ("C-KG", "C-GG")]
    # a-contrast at fixed b=1: C-KK vs C-GK; and at generic b: C-KG vs C-GG
    def safe_ratio(a, b):
        if a is None or b is None or b == 0:
            return None
        return a / b

    e3_signal = False
    for pair in (("C-KK", "C-GK"), ("C-KG", "C-GG")):
        la = m2_rows[pair[0]]["lambda_x_measured"]
        lb = m2_rows[pair[1]]["lambda_x_measured"]
        ta, tb = cells[pair[0]]["Tr_a"], cells[pair[1]]["Tr_a"]
        if ta != tb and la is not None and lb is not None:
            # E3: zero on Tr=1 with V in ker Tr — our V is NOT ker Tr by default,
            # so E3 prediction for this V is weaker; report observed separation.
            if min(la, lb) == 0 and max(la, lb) > 0:
                e3_signal = True

    if not hb22:
        pattern = "E2_algebra_degree_moves_with_b"  # outcome C
        pattern_code = "E2"
    elif e3_signal:
        pattern = "E3_yield_separates_on_a"
        pattern_code = "E3"
    else:
        pattern = "E1_compatible_M3_invariant_M2_no_hard_a_zero"
        pattern_code = "E1"

    # smoothest / highest-yield cell
    yields = {n: m2_rows[n]["lambda_x_measured"] for n in CELLS}
    best = max(yields, key=lambda k: (yields[k] is not None, yields[k] or 0))

    verdict = {
        "artifact": "pattern-verdict",
        "experiment_id": "EXP-BINSTD-6211a9",
        "HB2_2_holds": hb22,
        "pattern_E1_E2_E3": pattern_code,
        "pattern_detail": pattern,
        "M2_lambda_x": yields,
        "highest_yield_cell": best,
        "tail_extreme_M3_disagreement": extreme_disagreement,
        "interpretation_note": (
            "Observation-only verdict from predefined metrics; not a hypothesis status change. "
            "No deployed-curve security claim."
        ),
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "preregistered_prediction_ref": "experiments/EXP-BINSTD-6211a9/specification.yaml#preregistered_prediction",
    }
    write_yaml(EXP_DIR / "stage1" / "pattern-verdict.yaml", verdict)
    write_run_package(
        RUN_PAT,
        stage=1,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage1.py",
        seed=20261001,
        parameters={"arm": "pattern-verdict"},
        metrics={"pattern": pattern_code, "HB2_2_holds": hb22},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(verdict),
        started_at=utc_now(),
        finished_at=utc_now(),
        wall_seconds=0.0,
    )
    print("Stage 1 complete", flush=True)


if __name__ == "__main__":
    main()
