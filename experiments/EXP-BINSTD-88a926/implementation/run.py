#!/usr/bin/env python3
"""EXP-BINSTD-88a926 Stages 0-1 launcher (frozen contract v1).

Stage 0: freeze (c_nb,c_pb,N) with binomial density match, dual #E, empty-pool
         null, twin add, inline M2 instrument note. No walk.
Stage 1: n=17 three-arm mitt (normal-HW / poly-HW / uniform), ≥200 attempts;
         RESULTS.md with exactly one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. Dual-route Python arithmetic.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from gf2 import MODULI, is_irreducible  # noqa: E402
from mitt import (  # noqa: E402
    ATTEMPTS,
    CUTOFF_C,
    DENSITY_MATCH_MAX,
    NB_SEED,
    PB_SEED,
    POOL_N,
    POOL_SEED,
    R_SEED,
    STAGE1_N,
    UNI_SEED,
    YIELD_BAND,
    binomial_hw_density,
    build_hw_pool,
    build_uniform_pool,
    density_rel_err,
    dual_add_ok,
    empty_pool_null,
    find_normal_element,
    hw_normal,
    hw_poly,
    in_yield_band,
    make_fields,
    make_koblitz,
    mitt_search,
    models,
    random_curve_point,
    ratio,
    relerr,
)

EXPERIMENT_ID = "EXP-BINSTD-88a926"
HYPOTHESIS_ID = "H-BINSTD-2cea8d"
APPROVED_BY = "DEC-20261003-a9a886"
EXP_ROOT = Path(__file__).resolve().parents[1]
RUN0 = "RUN-BINSTD-e61a1c"
RUN1 = "RUN-BINSTD-20e8f7"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = []
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ")
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    n = STAGE1_N
    ok, irr = is_irreducible(MODULI[n])
    if not ok:
        raise RuntimeError("irreducibility failed")
    table, school = make_fields(n)
    ct = make_koblitz(table)
    cs = make_koblitz(school)
    order_table = ct.count_by_trace()
    order_school = cs.count_by_trace()
    twin_order = order_table == order_school
    rng = __import__("random").Random(POOL_SEED)
    P = random_curve_point(ct, rng)
    Q = random_curve_point(ct, rng)
    twin_add = dual_add_ok(ct, cs, P, Q)
    null = empty_pool_null(ct, cs, attempts=20)
    beta = find_normal_element(table)
    c_nb = CUTOFF_C
    c_pb = CUTOFF_C
    dens_nb = binomial_hw_density(n, c_nb)
    dens_pb = binomial_hw_density(n, c_pb)
    dens_err = density_rel_err(dens_nb, dens_pb)
    density_ok = dens_err <= DENSITY_MATCH_MAX
    m = models(POOL_N, order_table)
    cells = [
        {
            "n": n,
            "c_nb": c_nb,
            "c_pb": c_pb,
            "N": POOL_N,
            "attempts": ATTEMPTS,
            "density_nb": dens_nb,
            "density_pb": dens_pb,
            "density_rel_err": dens_err,
            "density_match_max": DENSITY_MATCH_MAX,
            "group_order": order_table,
            "p_m1": m["p_m1"],
            "p_m2": m["p_m2"],
            "expected_count_m1": ATTEMPTS * m["p_m1"],
            "expected_count_m2": ATTEMPTS * m["p_m2"],
            "normal_element": int(beta),
            "walk": False,
        }
    ]
    freeze = {
        "amazon_bedrock": "NOT SELECTED",
        "experiment_id": EXPERIMENT_ID,
        "yield_ratio_band": YIELD_BAND,
        "density_match_max": DENSITY_MATCH_MAX,
        "attempts": ATTEMPTS,
        "cells": cells,
        "arms": ["normal_hw", "poly_hw", "uniform"],
        "sampling": "rejection_only_no_walk",
        "inline_m2_note": "uniform-arm p_hat compared to M1 and M2 after Stage 1; out-of-band pairwise ratios are not read as H_alt unless min(relerr_M1, relerr_M2) <= 0.5 on the uniform arm",
        "group_order_is": "cardinality of E(F_2^n), not a prime-order subgroup",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", freeze)
    note = {
        "amazon_bedrock": "NOT SELECTED",
        "empty_pool_hits": null["hits"],
        "empty_pool_ok": null["hits"] == 0,
        "experiment_id": EXPERIMENT_ID,
        "irreducible": True,
        "irreducibility_n": irr["n"],
        "modulus": MODULI[n],
        "n": n,
        "order_school": order_school,
        "order_table": order_table,
        "twin_add_ok": twin_add,
        "twin_order_ok": twin_order,
        "density_ok": density_ok,
        "walk": False,
    }
    write_json(EXP_ROOT / "stage0" / "methodological-note.json", note)
    if not twin_order or not twin_add or null["hits"] != 0 or not density_ok:
        outcome = "O-ARTIFACT"
    else:
        outcome = "O-STAGE0-OK"
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "cells": cells,
        "certificate": {"kind": "none"},
        "claims": {"break": False, "exponent_move": False},
        "density_ok": density_ok,
        "empty_pool_hits": null["hits"],
        "experiment_id": EXPERIMENT_ID,
        "group_order": order_table,
        "hypothesis_id": HYPOTHESIS_ID,
        "outcome": outcome,
        "stage": 0,
        "twin_add_ok": twin_add,
        "twin_order_ok": twin_order,
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "id": RUN0,
            "experiment_id": EXPERIMENT_ID,
            "status": "completed",
            "stage": 0,
            "outcome": outcome,
            "validity": "valid" if outcome == "O-STAGE0-OK" else "invalid",
            "amazon_bedrock": "NOT SELECTED",
            "certificate_kind": "none",
        },
    )
    return raw


def decide(row: dict, twin_ok: bool, cert_ok: bool, null_ok: bool, density_ok: bool) -> str:
    if not twin_ok or not cert_ok or not null_ok or not density_ok:
        return "O-ARTIFACT"
    uni_ok = min(row["uniform_relerr_M1"], row["uniform_relerr_M2"]) <= 0.5
    pairwise = [
        row["ratio_nb_over_pb"],
        row["ratio_nb_over_uni"],
        row["ratio_pb_over_uni"],
    ]
    all_in = all(in_yield_band(r) for r in pairwise)
    if not uni_ok:
        return "O-INCONCLUSIVE"
    if all_in:
        return "O-SUPPORT"
    return "O-FAIL-BAND"


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    freeze_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    note_path = EXP_ROOT / "stage0" / "methodological-note.json"
    if not freeze_path.is_file() or not note_path.is_file():
        raise RuntimeError("Stage 0 freeze missing")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    note = json.loads(note_path.read_text(encoding="utf-8"))
    cells = freeze.get("cells")
    if not isinstance(cells, list) or not cells:
        raise RuntimeError("freeze cells must be a list")
    cell = cells[0]
    n = int(cell["n"])
    if n != STAGE1_N:
        raise RuntimeError("frozen cell n drifted")
    table, school = make_fields(n)
    ct = make_koblitz(table)
    cs = make_koblitz(school)
    beta = int(cell["normal_element"])
    c_nb = int(cell["c_nb"])
    c_pb = int(cell["c_pb"])
    N = int(cell["N"])
    attempts = int(cell["attempts"])
    dens_err = float(cell["density_rel_err"])
    density_ok = dens_err <= DENSITY_MATCH_MAX

    nb_pool, nb_draws = build_hw_pool(
        ct, N, NB_SEED, lambda P: hw_normal(table, beta, P[0]) <= c_nb
    )
    pb_pool, pb_draws = build_hw_pool(
        ct, N, PB_SEED, lambda P: hw_poly(P[0]) <= c_pb
    )
    uni_pool, uni_draws = build_uniform_pool(ct, N, UNI_SEED)

    y_nb = mitt_search(ct, cs, nb_pool, attempts, R_SEED + 11)
    y_pb = mitt_search(ct, cs, pb_pool, attempts, R_SEED + 13)
    y_uni = mitt_search(ct, cs, uni_pool, attempts, R_SEED + 17)
    twin_ok = not (y_nb["twin_fail"] or y_pb["twin_fail"] or y_uni["twin_fail"])
    cert_ok = not (y_nb["certificate_fail"] or y_pb["certificate_fail"] or y_uni["certificate_fail"])
    m = models(N, int(cell["group_order"]))
    row = {
        "n": n,
        "N": N,
        "attempts": attempts,
        "c_nb": c_nb,
        "c_pb": c_pb,
        "density_rel_err": dens_err,
        "nb_hits": y_nb["hits"],
        "pb_hits": y_pb["hits"],
        "uni_hits": y_uni["hits"],
        "nb_p_hat": y_nb["p_hat"],
        "pb_p_hat": y_pb["p_hat"],
        "uni_p_hat": y_uni["p_hat"],
        "ratio_nb_over_pb": ratio(y_nb["p_hat"], y_pb["p_hat"]),
        "ratio_nb_over_uni": ratio(y_nb["p_hat"], y_uni["p_hat"]),
        "ratio_pb_over_uni": ratio(y_pb["p_hat"], y_uni["p_hat"]),
        "in_band_nb_pb": in_yield_band(ratio(y_nb["p_hat"], y_pb["p_hat"])),
        "in_band_nb_uni": in_yield_band(ratio(y_nb["p_hat"], y_uni["p_hat"])),
        "in_band_pb_uni": in_yield_band(ratio(y_pb["p_hat"], y_uni["p_hat"])),
        "uniform_relerr_M1": relerr(y_uni["p_hat"], m["p_m1"]),
        "uniform_relerr_M2": relerr(y_uni["p_hat"], m["p_m2"]),
        "p_m1": m["p_m1"],
        "p_m2": m["p_m2"],
        "nb_draws": nb_draws,
        "pb_draws": pb_draws,
        "uni_draws": uni_draws,
        "certificate_pass_nb": y_nb["certificate_pass"],
        "certificate_fail_nb": y_nb["certificate_fail"],
        "certificate_pass_pb": y_pb["certificate_pass"],
        "certificate_fail_pb": y_pb["certificate_fail"],
        "certificate_pass_uni": y_uni["certificate_pass"],
        "certificate_fail_uni": y_uni["certificate_fail"],
        "twin_fail_nb": y_nb["twin_fail"],
        "twin_fail_pb": y_pb["twin_fail"],
        "twin_fail_uni": y_uni["twin_fail"],
        "hit_examples_nb": y_nb["hit_examples"],
        "hit_examples_pb": y_pb["hit_examples"],
        "hit_examples_uni": y_uni["hit_examples"],
        "walk": False,
    }
    null = empty_pool_null(ct, cs, attempts=20)
    null_ok = null["hits"] == 0
    outcome = decide(row, twin_ok, cert_ok, null_ok, density_ok)
    table_out = {
        "amazon_bedrock": "NOT SELECTED",
        "cells": [row],
        "empty_pool_hits": null["hits"],
        "outcome": outcome,
        "group_order": cell["group_order"],
        "yield_ratio_band": YIELD_BAND,
        "stage0_twin_order_ok": note.get("twin_order_ok"),
        "walk": False,
    }
    write_json(EXP_ROOT / "stage1" / "three-arm-yield.json", table_out)
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {
            "empty_pool_hits": null["hits"],
            "empty_pool_ok": null_ok,
            "twin_ok": twin_ok,
            "cert_ok": cert_ok,
            "density_ok": density_ok,
            "walk": False,
            "cells": [
                {
                    "n": row["n"],
                    "N": row["N"],
                    "twin_fail_nb": row["twin_fail_nb"],
                    "twin_fail_pb": row["twin_fail_pb"],
                    "twin_fail_uni": row["twin_fail_uni"],
                    "certificate_fail_nb": row["certificate_fail_nb"],
                    "certificate_fail_pb": row["certificate_fail_pb"],
                    "certificate_fail_uni": row["certificate_fail_uni"],
                }
            ],
        },
    )
    md = [
        f"# RESULTS EXP-BINSTD-88a926 / {HYPOTHESIS_ID}",
        "",
        f"outcome: {outcome}",
        f"ratio_nb_over_pb: {row['ratio_nb_over_pb']}",
        f"ratio_nb_over_uni: {row['ratio_nb_over_uni']}",
        f"ratio_pb_over_uni: {row['ratio_pb_over_uni']}",
        f"uniform_relerr_M1: {row['uniform_relerr_M1']}",
        f"uniform_relerr_M2: {row['uniform_relerr_M2']}",
        f"empty_pool_hits: {null['hits']}",
        f"twin_ok: {twin_ok}",
        f"cert_ok: {cert_ok}",
        f"density_ok: {density_ok}",
        "walk: false",
        "",
        "CLAIM TIER: observational / composition measurement. No break. No exponent.",
        "Amazon Bedrock was not selected.",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(md))
    any_hits = bool(row["nb_hits"] or row["pb_hits"] or row["uni_hits"])
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "cells": [row],
        "certificate": {"kind": "decomposition" if any_hits else "none"},
        "cert_ok": cert_ok,
        "claims": {"break": False, "exponent_move": False},
        "empty_pool_hits": null["hits"],
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "outcome": outcome,
        "stage": 1,
        "twin_ok": twin_ok,
        "wall_clock_seconds": time.time() - t0,
        "walk": False,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "id": RUN1,
            "experiment_id": EXPERIMENT_ID,
            "status": "completed",
            "stage": 1,
            "outcome": outcome,
            "validity": "valid" if outcome not in ("O-ARTIFACT", "O-IMPEDIMENT") else "invalid",
            "amazon_bedrock": "NOT SELECTED",
            "certificate_kind": "decomposition" if any_hits else "none",
        },
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True)
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        if args.stage == 0:
            stage0(run_dir)
        elif args.stage == 1:
            stage1(run_dir)
        else:
            print(f"unauthorized stage {args.stage}", file=sys.stderr)
            return 2
    except FileExistsError as exc:
        print(f"O-ARTIFACT refuse overwrite: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"O-IMPEDIMENT: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
