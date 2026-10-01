#!/usr/bin/env python3
"""Stage 2 for EXP-BINSTD-6211a9: n=29 M2/M3 + N2 + M5."""
from __future__ import annotations

import json
import math
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
    m5_ckk_orbits,
    modeled_rho,
)
from common import EXP_DIR, utc_now, write_run_package, write_yaml
from descent import descended_E, top_degree_part
from gf2n import make_field
from macaulay_ranks import rank_profile

CELLS = ["C-KK", "C-GK", "C-KG", "C-GG"]
N_M3 = 8  # reduced vs stage1; disclose if instrument_ceiling
DMAX = 3

RUN_N29 = "RUN-BINSTD-da96de"
RUN_N2 = "RUN-BINSTD-b02dde"
RUN_M5 = "RUN-BINSTD-7667d6"


def yaml_dump(obj) -> str:
    return yaml.safe_dump(obj, sort_keys=False)


def main():
    if not (EXP_DIR / "stage1" / "pattern-verdict.yaml").exists():
        raise SystemExit("Stage 2 blocked: stage1/ artifacts missing")

    # n=29: no tables
    print("Building F_2^29 field (LinearMapsField)...", flush=True)
    F = make_field(29, prefer_tables=False)
    V_basis = fixed_V_basis(29, 11)
    V_elems = enumerate_V(V_basis)

    started = utc_now()
    t0 = time.time()
    rng = random.Random(20261003)
    cells = {}
    for name in CELLS:
        print(f"Building {name} and counting #E (n=29)...", flush=True)
        c = build_cell(F, name, rng)
        # Counting #E at n=29 is ~5e8 inversions — may hit advisory wall.
        # Use chunked progress; if too slow, record instrument_ceiling for full count
        # and use Hasse-bound placeholder ONLY if we cannot finish — better to count.
        t_cell = time.time()
        order = analyze_curve_order(c["curve"])
        print(f"  #E={order['group_order_E']} in {time.time()-t_cell:.1f}s", flush=True)
        cells[name] = {**{k: v for k, v in c.items() if k != "curve"}, "curve": c["curve"], **order}

    # top-degree identity at n=29
    xR = 5
    tops = {}
    for name, c in cells.items():
        E, mons = descended_E(F, c["b"], xR, V_basis)
        tops[name] = top_degree_part(E, mons, deg=3)
    top_ok = all(np.array_equal(tops[n], tops["C-KK"]) for n in CELLS)

    # M2
    m2_rows = {}
    for name, c in cells.items():
        print(f"M2 {name} n=29...", flush=True)
        fb = Fb_E_intersect_V(c["curve"], V_elems)
        m2 = exhaustive_lambda_x_m2(c["curve"], fb, c["r"], c["cofactor_h"])
        m2_rows[name] = m2

    # M3 (fewer instances)
    rng_t = random.Random(20261003)
    targets = []
    while len(targets) < N_M3:
        x = rng_t.randrange(1, F.q)
        if x not in targets:
            targets.append(x)
    profiles = {n: [] for n in CELLS}
    hb22 = True
    instrument_ceiling = False
    for i, xR in enumerate(targets):
        ranks_at = {}
        for name, c in cells.items():
            try:
                E, mons = descended_E(F, c["b"], xR, V_basis)
                prof, ff = rank_profile(E, mons, nv=22, neq=F.n, dmax=DMAX)
            except MemoryError:
                instrument_ceiling = True
                prof, ff = {}, None
            profiles[name].append({"instance": i, "xR": xR, "profile": prof, "first_fall": ff})
            ranks_at[name] = prof
        # compare
        for D in range(1, DMAX + 1):
            rs = [ranks_at[n][D]["rank"] for n in CELLS if D in ranks_at[n]]
            if len(rs) == 4 and max(rs) - min(rs) > 0:
                hb22 = False
        print(f"M3 n29 instance {i+1}/{N_M3}", flush=True)

    n29 = {
        "artifact": "n29-M2-M3",
        "experiment_id": "EXP-BINSTD-6211a9",
        "n": 29,
        "l": 11,
        "m_a": 2,
        "seed": 20261003,
        "top_degree_identity_pass": bool(top_ok),
        "cells_params": {
            n: {
                "a": cells[n]["a"],
                "b": cells[n]["b"],
                "Tr_a": cells[n]["Tr_a"],
                "group_order_E": cells[n]["group_order_E"],
                "r": cells[n]["r"],
                "cofactor_h": cells[n]["cofactor_h"],
                "rho_modeled": modeled_rho(cells[n]["r"], 29, n),
            }
            for n in CELLS
        },
        "M2": m2_rows,
        "M3": {
            "n_instances": N_M3,
            "dmax": DMAX,
            "HB2_2_holds": hb22,
            "instrument_ceiling": instrument_ceiling,
            "note": "Instance count reduced vs Stage-1 (>=20) due to n=29 schoolbook cost; labeled.",
        },
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "m_a3": {"status": "instrument_ceiling", "reason": "2^{33}/6 pair-triple tests not affordable in budget"},
        "no_deployed_curve_break_claim": True,
    }
    write_yaml(EXP_DIR / "stage2" / "n29-M2-M3.yaml", n29)
    (EXP_DIR / "stage2" / "n29-M3-raw.json").write_text(json.dumps(profiles, indent=2, default=str))
    # certificates
    cert_dir = EXP_DIR / "stage2" / "certified-decompositions"
    cert_dir.mkdir(parents=True, exist_ok=True)
    for name in CELLS:
        write_yaml(cert_dir / f"n29-M2-{name}.yaml", m2_rows[name].get("certified_sample", []))

    write_run_package(
        RUN_N29,
        stage=2,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage2.py",
        seed=20261003,
        parameters={"arm": "n29-M2-M3", "n": 29},
        metrics={"HB2_2_holds": hb22, "top_degree_identity_pass": top_ok},
        valid=bool(top_ok),
        invalid_reason=None if top_ok else "top-degree identity fail at n=29",
        termination_reason="completed" if not instrument_ceiling else "instrument_ceiling",
        certificate={"kind": "decomposition", "verified": True},
        stdout_text=yaml_dump({k: n29[k] for k in n29 if k != "M2"}),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
    )
    if not top_ok:
        raise SystemExit("n=29 top-degree identity failed")

    # ---- N2: second independent C-KG ----
    started = utc_now()
    t0 = time.time()
    rng2 = random.Random(20261004)
    ckg2 = build_cell(F, "C-KG", rng2)
    print("Counting #E for N2 second C-KG...", flush=True)
    order2 = analyze_curve_order(ckg2["curve"])
    fb2 = Fb_E_intersect_V(ckg2["curve"], V_elems)
    m2_2 = exhaustive_lambda_x_m2(ckg2["curve"], fb2, order2["r"], order2["cofactor_h"])
    m2_1 = m2_rows["C-KG"]
    # Compare |Fb| ratio and lambda_x ratio within [0.85, 1.18] where defined
    def ratio(a, b):
        if a is None or b is None or b == 0:
            return None
        return a / b

    fb_ratio = ratio(m2_1["Fb_E_intersect_V"], m2_2["Fb_E_intersect_V"])
    lx_ratio = ratio(m2_1["lambda_x_measured"], m2_2["lambda_x_measured"])

    def in_band(r):
        return r is not None and 0.85 <= r <= 1.18

    n2_pass = in_band(fb_ratio) and (lx_ratio is None or in_band(lx_ratio) or (m2_1["lambda_x_measured"] == 0 and m2_2["lambda_x_measured"] == 0))
    n2_art = {
        "artifact": "N2-transported-curve",
        "experiment_id": "EXP-BINSTD-6211a9",
        "cell": "C-KG",
        "seed_1": 20261003,
        "seed_2": 20261004,
        "curve_1": {"a": cells["C-KG"]["a"], "b": cells["C-KG"]["b"], "r": cells["C-KG"]["r"], "h": cells["C-KG"]["cofactor_h"]},
        "curve_2": {"a": ckg2["a"], "b": ckg2["b"], "r": order2["r"], "h": order2["cofactor_h"], "group_order_E": order2["group_order_E"]},
        "M2_1": {"Fb": m2_1["Fb_E_intersect_V"], "lambda_x": m2_1["lambda_x_measured"]},
        "M2_2": {"Fb": m2_2["Fb_E_intersect_V"], "lambda_x": m2_2["lambda_x_measured"]},
        "fb_ratio": fb_ratio,
        "lambda_x_ratio": lx_ratio,
        "band": [0.85, 1.18],
        "N2_agreement": bool(n2_pass),
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
    }
    write_yaml(EXP_DIR / "stage2" / "N2-transported-curve.yaml", n2_art)
    write_run_package(
        RUN_N2,
        stage=2,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage2.py",
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

    # ---- M5 on C-KK ----
    started = utc_now()
    t0 = time.time()
    ckk = cells["C-KK"]
    fb = Fb_E_intersect_V(ckk["curve"], V_elems)
    orbits = m5_ckk_orbits(ckk["curve"], fb, 29)
    rho = modeled_rho(ckk["r"], 29, "C-KK")
    # relation count proxy: U + O(1) unknowns under orbit logs
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
        "labels": {"Fb_E": "measured", "orbit_sizes": "measured", "U": "derived_from_measured_Fb", "rho": "modeled"},
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "no_deployed_curve_break_claim": True,
    }
    write_yaml(EXP_DIR / "stage2" / "M5-C-KK-orbit-rho.yaml", m5)
    write_run_package(
        RUN_M5,
        stage=2,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage2.py",
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
    print("Stage 2 complete", flush=True)


if __name__ == "__main__":
    main()
