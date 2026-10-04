#!/usr/bin/env python3
"""EXP-BINSTD-0f2222 Stages 0-1 launcher (frozen contract v1).

Stage 0: freeze M1/M2/M3 formulas, relerr band 0.25, measured #E via dual
         trace-count, N grid so E_M2 ∈ {5,15,40}, empty-pool null, twin add.
Stage 1: n=17 mitt bake-off on the frozen N grid (≥200 attempts/cell);
         RESULTS.md with exactly one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
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

from curve import Curve  # noqa: E402
from gf2 import Field, TableField, MODULI, is_irreducible  # noqa: E402
from mitt import (  # noqa: E402
    ATTEMPTS,
    E_M2_TARGETS,
    POOL_SEED,
    RELERR_BAND,
    R_SEED,
    STAGE1_N,
    TIE_BAND,
    build_uniform_pool,
    choose_N,
    dual_add_ok,
    empty_pool_null,
    make_fields,
    make_koblitz,
    mitt_search,
    models,
    random_curve_point,
    relerr,
)

EXPERIMENT_ID = "EXP-BINSTD-0f2222"
HYPOTHESIS_ID = "H-BINSTD-f4b5bb"
APPROVED_BY = "DEC-20261003-c943ba"
EXP_ROOT = Path(__file__).resolve().parents[1]
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
    cells = []
    for e_target in E_M2_TARGETS:
        N = choose_N(order_table, e_target, ATTEMPTS)
        m = models(N, order_table)
        cells.append(
            {
                "n": n,
                "e_m2_target": e_target,
                "attempts": ATTEMPTS,
                "N": N,
                "group_order": order_table,
                "expected_count_m2": ATTEMPTS * m["p_m2"],
                "p_m1": m["p_m1"],
                "p_m2": m["p_m2"],
                "p_m3": m["p_m3"],
            }
        )
    freeze = {
        "amazon_bedrock": "NOT SELECTED",
        "experiment_id": EXPERIMENT_ID,
        "formulas": {
            "M1": "p = N*(N-1)/(2*|G|)  unordered distinct pairs",
            "M2": "p = N^2/|G|  ordered pairs",
            "M3": "p = 1-exp(-N^2/|G|)  occupancy",
        },
        "group_order_is": "cardinality of E(F_2^n), not a prime-order subgroup",
        "relerr_band": RELERR_BAND,
        "tie_band": TIE_BAND,
        "attempts": ATTEMPTS,
        "cells": cells,
        "sampling_universe": "uniform random affine points on E: Y^2+XY=X^3+1",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", freeze)
    note = {
        "experiment_id": EXPERIMENT_ID,
        "irreducible": True,
        "irreducibility_n": irr["n"],
        "order_table": order_table,
        "order_school": order_school,
        "twin_order_ok": twin_order,
        "twin_add_ok": twin_add,
        "empty_pool_hits": null["hits"],
        "empty_pool_ok": null["hits"] == 0,
        "modulus": MODULI[n],
        "n": n,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "methodological-note.json", note)
    if not twin_order or not twin_add or null["hits"] != 0:
        outcome = "O-ARTIFACT"
    else:
        outcome = "O-STAGE0-OK"
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "exponent_move": False},
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "outcome": outcome,
        "stage": 0,
        "twin_order_ok": twin_order,
        "twin_add_ok": twin_add,
        "empty_pool_hits": null["hits"],
        "group_order": order_table,
        "cells": cells,
        "certificate": {"kind": "none"},
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "id": "RUN-BINSTD-15c441",
            "experiment_id": EXPERIMENT_ID,
            "status": "completed",
            "stage": 0,
            "outcome": outcome,
            "validity": "valid" if outcome == "O-STAGE0-OK" else "invalid",
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def decide(rows: list[dict], twin_ok: bool, cert_ok: bool, null_ok: bool) -> str:
    if not twin_ok or not cert_ok or not null_ok:
        return "O-ARTIFACT"
    holds = {"M1": 0, "M2": 0, "M3": 0}
    for row in rows:
        for name in ("M1", "M2", "M3"):
            if row[f"in_band_{name}"]:
                holds[name] += 1
    winners = [k for k, v in holds.items() if v >= 3]
    if len(winners) == 1:
        return "O-SUPPORT"
    if len(winners) == 0:
        return "O-FAIL-BAND"
    close = True
    for row in rows:
        ps = [row["p_m1"], row["p_m2"], row["p_m3"]]
        if max(ps) == 0:
            continue
        if (max(ps) - min(ps)) / max(ps) > TIE_BAND:
            close = False
    return "O-INCONCLUSIVE" if close else "O-INCONCLUSIVE"


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    freeze_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    note_path = EXP_ROOT / "stage0" / "methodological-note.json"
    if not freeze_path.is_file() or not note_path.is_file():
        raise RuntimeError("Stage 0 freeze missing")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    note = json.loads(note_path.read_text(encoding="utf-8"))
    n = STAGE1_N
    table, school = make_fields(n)
    ct = make_koblitz(table)
    cs = make_koblitz(school)
    rows = []
    twin_ok = True
    cert_ok = True
    for i, cell in enumerate(freeze["cells"]):
        if cell["n"] != n:
            raise RuntimeError("frozen cell n drifted")
        N = int(cell["N"])
        attempts = int(cell["attempts"])
        pool = build_uniform_pool(ct, N, POOL_SEED + 17 * i)
        y = mitt_search(ct, cs, pool, attempts, R_SEED + 31 * i)
        if y["twin_fail"]:
            twin_ok = False
        if y["certificate_fail"]:
            cert_ok = False
        m = models(N, int(cell["group_order"]))
        phat = y["p_hat"]
        row = {
            "n": n,
            "e_m2_target": cell["e_m2_target"],
            "N": N,
            "attempts": attempts,
            "hits": y["hits"],
            "p_hat": phat,
            "p_m1": m["p_m1"],
            "p_m2": m["p_m2"],
            "p_m3": m["p_m3"],
            "relerr_M1": relerr(phat, m["p_m1"]),
            "relerr_M2": relerr(phat, m["p_m2"]),
            "relerr_M3": relerr(phat, m["p_m3"]),
            "in_band_M1": relerr(phat, m["p_m1"]) <= RELERR_BAND,
            "in_band_M2": relerr(phat, m["p_m2"]) <= RELERR_BAND,
            "in_band_M3": relerr(phat, m["p_m3"]) <= RELERR_BAND,
            "certificate_pass": y["certificate_pass"],
            "certificate_fail": y["certificate_fail"],
            "twin_fail": y["twin_fail"],
            "certificate_kind": y["certificate_kind"],
            "hit_examples": y["hit_examples"],
        }
        rows.append(row)
    null = empty_pool_null(ct, cs, attempts=20)
    null_ok = null["hits"] == 0
    outcome = decide(rows, twin_ok, cert_ok, null_ok)
    holds = {"M1": sum(1 for r in rows if r["in_band_M1"]),
             "M2": sum(1 for r in rows if r["in_band_M2"]),
             "M3": sum(1 for r in rows if r["in_band_M3"])}
    winners = [k for k, v in holds.items() if v >= 3]
    winning_model = winners[0] if len(winners) == 1 else None
    table_out = {
        "amazon_bedrock": "NOT SELECTED",
        "cells": rows,
        "empty_pool_hits": null["hits"],
        "holds": holds,
        "relerr_band": RELERR_BAND,
        "winning_model": winning_model,
        "outcome": outcome,
        "group_order": freeze["cells"][0]["group_order"] if freeze["cells"] else None,
        "group_order_is": freeze.get("group_order_is"),
        "stage0_twin_order_ok": note.get("twin_order_ok"),
    }
    write_json(EXP_ROOT / "stage1" / "bakeoff-table.json", table_out)
    write_json(EXP_ROOT / "stage1" / "control-table.json", {
        "empty_pool_hits": null["hits"],
        "empty_pool_ok": null_ok,
        "twin_ok": twin_ok,
        "cert_ok": cert_ok,
        "cells": [{"n": r["n"], "N": r["N"], "twin_fail": r["twin_fail"],
                   "certificate_fail": r["certificate_fail"]} for r in rows],
    })
    md = [
        f"# RESULTS EXP-BINSTD-0f2222 / {HYPOTHESIS_ID}",
        "",
        f"outcome: {outcome}",
        f"winning_model: {winning_model}",
        f"holds: {holds}",
        f"empty_pool_hits: {null['hits']}",
        f"twin_ok: {twin_ok}",
        f"cert_ok: {cert_ok}",
        "",
        "CLAIM TIER: observational / instrument. No break. No exponent.",
        "Amazon Bedrock was not selected.",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(md))
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "exponent_move": False},
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "outcome": outcome,
        "stage": 1,
        "winning_model": winning_model,
        "holds": holds,
        "cells": rows,
        "empty_pool_hits": null["hits"],
        "twin_ok": twin_ok,
        "cert_ok": cert_ok,
        "certificate": {"kind": "decomposition" if any(r["hits"] for r in rows) else "none"},
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "id": "RUN-BINSTD-df8235",
            "experiment_id": EXPERIMENT_ID,
            "status": "completed",
            "stage": 1,
            "outcome": outcome,
            "validity": "valid" if outcome not in ("O-ARTIFACT", "O-IMPEDIMENT") else "invalid",
            "amazon_bedrock": "NOT SELECTED",
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
    except Exception as exc:  # noqa: BLE001 — surface as impediment, never as math
        print(f"O-IMPEDIMENT: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
