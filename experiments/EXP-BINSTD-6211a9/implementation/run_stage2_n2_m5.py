#!/usr/bin/env python3
"""Resume Stage 2 N2 + M5 after n29-M2-M3.yaml already exists (RUN-BINSTD-da96de)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cells import (
    Fb_E_intersect_V,
    analyze_curve_order,
    build_cell,
    enumerate_V,
    exhaustive_lambda_x_m2,
    fixed_V_basis,
    m5_ckk_orbits,
    modeled_rho,
)
from common import EXP_DIR, utc_now, write_run_package, write_yaml
from gf2n import make_field
import random

RUN_N2 = "RUN-BINSTD-b02dde"
RUN_M5 = "RUN-BINSTD-7667d6"


def yaml_dump(obj) -> str:
    return yaml.safe_dump(obj, sort_keys=False)


def main():
    n29_path = EXP_DIR / "stage2" / "n29-M2-M3.yaml"
    if not n29_path.exists():
        raise SystemExit("n29-M2-M3.yaml missing; run full run_stage2.py first")
    n29 = yaml.safe_load(n29_path.read_text())
    m2_1 = n29["M2"]["C-KG"]
    cells_params = n29["cells_params"]

    F = make_field(29, prefer_tables=False)
    V_basis = fixed_V_basis(29, 11)
    V_elems = enumerate_V(V_basis)

    # Rebuild C-KK for M5 (same seed as stage2)
    rng = random.Random(20261003)
    from cells import build_cell as bc
    # Need to replay cell draws in order C-KK, C-GK, C-KG, C-GG
    cells = {}
    for name in ["C-KK", "C-GK", "C-KG", "C-GG"]:
        cells[name] = bc(F, name, rng)
        # attach order from frozen artifact where possible
        cells[name].update({
            "group_order_E": cells_params[name]["group_order_E"],
            "r": cells_params[name]["r"],
            "cofactor_h": cells_params[name]["cofactor_h"],
            "Tr_a": cells_params[name]["Tr_a"],
        })

    started = utc_now()
    t0 = time.time()
    print("N2: second C-KG...", flush=True)
    rng2 = random.Random(20261004)
    ckg2 = bc(F, "C-KG", rng2)
    order2 = analyze_curve_order(ckg2["curve"])
    print(f"  #E={order2['group_order_E']} h={order2['cofactor_h']} r={order2['r']}", flush=True)
    fb2 = Fb_E_intersect_V(ckg2["curve"], V_elems)
    print(f"  |Fb|={len(fb2)}; M2...", flush=True)
    m2_2 = exhaustive_lambda_x_m2(
        ckg2["curve"], fb2, order2["r"], order2["cofactor_h"], strict_G=False
    )
    print(f"  M2 done lx={m2_2['lambda_x_measured']}", flush=True)

    def ratio(a, b):
        if a is None or b is None or b == 0:
            return None
        return a / b

    fb_ratio = ratio(m2_1["Fb_E_intersect_V"], m2_2["Fb_E_intersect_V"])
    lx_ratio = ratio(m2_1["lambda_x_measured"], m2_2["lambda_x_measured"])

    def in_band(r):
        return r is not None and 0.85 <= r <= 1.18

    n2_pass = in_band(fb_ratio) and (
        lx_ratio is None
        or in_band(lx_ratio)
        or (m2_1["lambda_x_measured"] == 0 and m2_2["lambda_x_measured"] == 0)
    )
    n2_art = {
        "artifact": "N2-transported-curve",
        "experiment_id": "EXP-BINSTD-6211a9",
        "cell": "C-KG",
        "seed_1": 20261003,
        "seed_2": 20261004,
        "curve_1": {
            "a": cells_params["C-KG"]["a"],
            "b": cells_params["C-KG"]["b"],
            "r": cells_params["C-KG"]["r"],
            "h": cells_params["C-KG"]["cofactor_h"],
        },
        "curve_2": {
            "a": ckg2["a"],
            "b": ckg2["b"],
            "r": order2["r"],
            "h": order2["cofactor_h"],
            "group_order_E": order2["group_order_E"],
        },
        "M2_1": {"Fb": m2_1["Fb_E_intersect_V"], "lambda_x": m2_1["lambda_x_measured"]},
        "M2_2": {"Fb": m2_2["Fb_E_intersect_V"], "lambda_x": m2_2["lambda_x_measured"]},
        "fb_ratio": fb_ratio,
        "lambda_x_ratio": lx_ratio,
        "band": [0.85, 1.18],
        "N2_agreement": bool(n2_pass),
        "G_membership_mode": "class_bit_proxy",
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
    }
    write_yaml(EXP_DIR / "stage2" / "N2-transported-curve.yaml", n2_art)
    write_run_package(
        RUN_N2,
        stage=2,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage2_n2_m5.py",
        seed=20261004,
        parameters={"arm": "N2"},
        metrics={"N2_agreement": n2_pass, "fb_ratio": fb_ratio, "lambda_x_ratio": lx_ratio},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(n2_art),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
    )
    print(f"N2_agreement={n2_pass}", flush=True)

    # M5
    started = utc_now()
    t0 = time.time()
    print("M5 C-KK...", flush=True)
    ckk = cells["C-KK"]
    fb = Fb_E_intersect_V(ckk["curve"], V_elems)
    orbits = m5_ckk_orbits(ckk["curve"], fb, 29)
    rho = modeled_rho(ckk["r"], 29, "C-KK")
    U = orbits["U_modeled_from_Fb"]
    m5 = {
        "artifact": "M5-C-KK-orbit-rho",
        "experiment_id": "EXP-BINSTD-6211a9",
        "n": 29,
        "cell": "C-KK",
        "Fb_E_intersect_V_abscissae": len(fb),
        "orbits": orbits,
        "U": U,
        "relation_count_proxy": None if U is None else int(round(U)),
        "rho_modeled": rho,
        "labels": {
            "Fb_E": "measured",
            "orbit_sizes": "measured",
            "U": "derived_from_measured_Fb",
            "rho": "modeled",
        },
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "no_deployed_curve_break_claim": True,
    }
    write_yaml(EXP_DIR / "stage2" / "M5-C-KK-orbit-rho.yaml", m5)
    write_run_package(
        RUN_M5,
        stage=2,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage2_n2_m5.py",
        seed=20261003,
        parameters={"arm": "M5", "cell": "C-KK"},
        metrics={"U": U, "n_orbits": orbits["n_orbits"], "rho_modeled": rho["rho_modeled"]},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump(m5),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
    )
    print("Stage 2 N2+M5 complete", flush=True)


if __name__ == "__main__":
    main()
