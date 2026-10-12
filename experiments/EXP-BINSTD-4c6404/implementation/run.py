#!/usr/bin/env python3
"""EXP-BINSTD-4c6404 Stages 0-2: block/scalar Wiedemann vs dense GE over GF(2).

Pure Python. No Magma/Sage/AUXIN/Bedrock. Real arithmetic on frozen toy
sparse matrices — not a missing-launcher detector.
Observations only. No ECDLP solve. No exponent. No n>=131 transfer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from gf2la import (  # noqa: E402
    dense_ge_solve,
    matrix_sha256,
    matvec,
    median_insert,
    median_sort,
    wiedemann_solve,
)
from matrices import R_N, ROW_WEIGHT, SURPLUS, full_rank_square  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-4c6404"
HYPOTHESIS_ID = "H-BINSTD-dcc004"
APPROVED_BY = "DEC-20261003-3ff445"
SOURCE_IDEA = "IDEA-20261002-79a077"
EXP_ROOT = Path(__file__).resolve().parents[1]

TAU = 1.0
N_REP = 7
CATALOG_SEED = 2026100307
PIN_SEED = 2026100308
NULL_SEED = 2026100309
AUTHORIZED_STAGES = [0, 1, 2]
STAGE1_NS = [17]
STAGE2_NS = [23, 31]
NULL_RATIO_LO, NULL_RATIO_HI = 0.25, 4.0

OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
    "O-NULL-FAIL",
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def combinadic_a(sorted_ids: list[int]) -> int:
    def binom(n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        k = min(k, n - k)
        num = den = 1
        for i in range(k):
            num *= n - i
            den *= i + 1
        return num // den

    return sum(binom(c, i + 1) for i, c in enumerate(sorted_ids))


def combinadic_b(sorted_ids: list[int]) -> int:
    def binom(n: int, k: int) -> int:
        if k < 0 or n < k:
            return 0
        if k == 0 or k == n:
            return 1
        acc = 1
        for t in range(k):
            acc = acc * (n - t) // (t + 1)
        return acc

    return sum(binom(c, i + 1) for i, c in enumerate(sorted_ids))


def dual_clocks(fn):
    t0a = time.perf_counter()
    t0b = time.monotonic()
    result = fn()
    wall_a = time.perf_counter() - t0a
    wall_b = time.monotonic() - t0b
    return result, float(wall_a), float(wall_b)


def race_one(kind: str, n_label: int, surplus: float, rep: int, seed_base: int) -> dict[str, Any] | None:
    seed = seed_base + n_label * 10007 + int(surplus * 10) * 1009 + rep * 17
    built = full_rank_square(kind, n_label, surplus, seed)
    if built is None:
        return None
    rows, r, nnz, tries = built
    digest = matrix_sha256(rows, r)
    rng = random.Random(PIN_SEED + seed)
    v_true = rng.getrandbits(r) or 1
    b = matvec(rows, v_true)
    u = rng.getrandbits(r) or 1

    def run_w():
        return wiedemann_solve(list(rows), b, r, u)

    def run_d():
        return dense_ge_solve(list(rows), b, r)

    (xw, _), wa_w, wb_w = dual_clocks(run_w)
    (xd, rank), wa_d, wb_d = dual_clocks(run_d)
    if xw is None or xd is None or rank != r:
        return None
    if matvec(rows, xw) != b or matvec(rows, xd) != b:
        return None
    if matrix_sha256(rows, r) != digest:
        return None
    return {
        "kind": kind,
        "n": n_label,
        "surplus": surplus,
        "rep": rep,
        "r": r,
        "nnz": nnz,
        "rank_tries": tries,
        "matrix_sha256": digest,
        "wall_wiedemann_perf": wa_w,
        "wall_wiedemann_mono": wb_w,
        "wall_dense_perf": wa_d,
        "wall_dense_mono": wb_d,
        "x_w": xw,
        "x_d": xd,
        "same_solution": xw == xd,
        "b": b,
        "v_true": v_true,
    }


def cell_races(kind: str, ns: list[int], seed_base: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for n_label in ns:
        for s in SURPLUS:
            for rep in range(N_REP):
                rec = race_one(kind, n_label, s, rep, seed_base)
                if rec is not None:
                    out.append(rec)
    return out


def ratio_from_races(races: list[dict[str, Any]], n_label: int, surplus: float) -> dict[str, Any]:
    xs_w = [x["wall_wiedemann_perf"] for x in races if x["n"] == n_label and x["surplus"] == surplus]
    xs_d = [x["wall_dense_perf"] for x in races if x["n"] == n_label and x["surplus"] == surplus]
    mw_a, mw_b = median_sort(xs_w), median_insert(xs_w)
    md_a, md_b = median_sort(xs_d), median_insert(xs_d)
    dual_ok = mw_a == mw_b and md_a == md_b and mw_a is not None and md_a is not None
    ratio = None
    if dual_ok and md_a not in (None, 0):
        ratio = mw_a / md_a
    return {
        "n": n_label,
        "surplus": surplus,
        "n_success": len(xs_w),
        "median_w_sort": mw_a,
        "median_w_insert": mw_b,
        "median_d_sort": md_a,
        "median_d_insert": md_b,
        "dual_ok": dual_ok,
        "ratio": ratio,
        "beats_tau": (ratio is not None and ratio <= TAU),
    }


def decide(cells: list[dict[str, Any]], null_cells: list[dict[str, Any]] | None, stage: int) -> str:
    if not cells:
        return "O-INCONCLUSIVE"
    if any(not c["dual_ok"] for c in cells):
        return "O-ARTIFACT"
    if any(c["n_success"] < 5 for c in cells):
        return "O-INCONCLUSIVE"
    if any(c["ratio"] is None for c in cells):
        return "O-INCONCLUSIVE"
    if null_cells:
        if any(not c["dual_ok"] or c["ratio"] is None for c in null_cells):
            return "O-ARTIFACT"
        if any(not (NULL_RATIO_LO <= c["ratio"] <= NULL_RATIO_HI) for c in null_cells if c["ratio"] is not None):
            return "O-NULL-FAIL"
    if all(c["beats_tau"] for c in cells):
        return "O-SUPPORT" if stage >= 1 else "O-STAGE0-OK"
    return "O-FAIL-BAND"


def stage0() -> dict[str, Any]:
    cells = []
    ids = []
    for n_label, r in R_N.items():
        cells.append({"n": n_label, "r": r, "row_weight": ROW_WEIGHT, "surplus": list(SURPLUS)})
        ids.append(n_label)
    ids_sorted = sorted(ids)
    ca, cb = combinadic_a(ids_sorted), combinadic_b(ids_sorted)
    pred = {
        "heuristic": "HEUR-BINSTD-79a077-H1",
        "quantity": "median(wall_Wiedemann) / median(wall_dense)",
        "formula": "R <= tau",
        "tau": TAU,
        "written_before_any_scientific_timing": True,
        "n_rep": N_REP,
        "row_weight": ROW_WEIGHT,
        "surplus": list(SURPLUS),
        "r_n": R_N,
        "null_ratio_interval": [NULL_RATIO_LO, NULL_RATIO_HI],
        "solvers": ["python_krylov_wiedemann", "python_dense_ge_bitpacked"],
        "amazon_bedrock": "NOT SELECTED",
        "magma_sage_auxin": "NOT USED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    vcat = {
        "note": "Toy FB column counts r(n); no curve library. Surplus folds extra rows into the square operator.",
        "cells": {f"n{n}": c for n, c in zip((x["n"] for x in cells), cells)},
        "combinadic": {"a": ca, "b": cb, "agree": ca == cb},
        "catalog_seed": CATALOG_SEED,
        "pin_seed": PIN_SEED,
        "null_seed": NULL_SEED,
    }
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", vcat)
    tcat = {
        "targets": [{"target_id": n, "r": R_N[n]} for n in ids_sorted],
        "combinadic": {"a": ca, "b": cb, "agree": ca == cb},
        "n_rep": N_REP,
    }
    write_json(EXP_ROOT / "stage0" / "target-catalog.json", tcat)
    probe = {
        "python_dense_ge": True,
        "python_wiedemann": True,
        "magma": False,
        "sage": False,
        "auxin": False,
        "note": "Both solver arms are in gf2la.py. Missing-launcher detector is not this contract.",
    }
    write_json(EXP_ROOT / "stage0" / "launcher-probe.json", probe)
    write_text(
        EXP_ROOT / "stage0" / "derivations-note.md",
        "Square race matrix = XOR-fold of a surplus-s rectangular sparse GF(2) "
        "matrix onto r(n) rows. IC-like rows have exact weight 6; null rows are "
        "Bernoulli with mean weight 6. Both solvers receive identical packed rows. "
        "tau=1.0 frozen before any scientific timing.\n",
    )
    outcome = "O-STAGE0-OK" if ca == cb else "O-ARTIFACT"
    return {
        "stage": 0,
        "outcome": outcome,
        "twin_ok": ca == cb,
        "tau": TAU,
        "r_n": R_N,
    }


def write_results(path: Path, outcome: str, body: str) -> None:
    text = (
        f"# RESULTS {EXPERIMENT_ID}\n\n"
        f"outcome: {outcome}\n\n"
        f"hypothesis: {HYPOTHESIS_ID}\n"
        f"idea: {SOURCE_IDEA}\n"
        f"approved_by: {APPROVED_BY}\n\n"
        f"{body}\n\n"
        "No ECDLP solve. No exponent. No n>=131 transfer. "
        "Amazon Bedrock NOT USED. Magma/Sage/AUXIN NOT USED.\n"
    )
    write_text(path, text)


def stage1() -> dict[str, Any]:
    pred = json.loads((EXP_ROOT / "stage0" / "preregistered-predictions.json").read_text())
    if pred.get("tau") != TAU or not pred.get("written_before_any_scientific_timing"):
        raise RuntimeError("stage0 freeze missing or tau mutated")
    races = cell_races("ic", STAGE1_NS, CATALOG_SEED)
    cells = [ratio_from_races(races, n, s) for n in STAGE1_NS for s in SURPLUS]
    outcome = decide(cells, None, stage=1)
    timings = {
        "admitted": True,
        "kind": "ic",
        "races": [
            {k: v for k, v in rec.items() if k not in {"x_w", "x_d", "b", "v_true"}}
            | {"x_w": rec["x_w"], "x_d": rec["x_d"], "b": rec["b"]}
            for rec in races
        ],
        "cells": cells,
        "outcome": outcome,
    }
    write_json(EXP_ROOT / "stage1" / "timings.json", timings)
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {
            "same_matrix_bytes": True,
            "tau": TAU,
            "dual_median": all(c["dual_ok"] for c in cells) if cells else False,
            "n_success_by_cell": [{"n": c["n"], "s": c["surplus"], "k": c["n_success"]} for c in cells],
        },
    )
    write_results(
        EXP_ROOT / "RESULTS.md",
        outcome,
        "Stage 1 n=17 IC-like square races (s in {1.5, 2.0}). "
        f"cells={json.dumps(cells, sort_keys=True)}",
    )
    return {"stage": 1, "outcome": outcome, "cells": cells, "n_races": len(races)}


def stage2() -> dict[str, Any]:
    if (EXP_ROOT / "RESULTS.md").exists():
        # Stage 2 must not overwrite Stage-1 RESULTS.md
        pass
    races_ic = cell_races("ic", STAGE2_NS, CATALOG_SEED)
    races_null = cell_races("null", STAGE2_NS, NULL_SEED)
    cells = [ratio_from_races(races_ic, n, s) for n in STAGE2_NS for s in SURPLUS]
    null_cells = [ratio_from_races(races_null, n, s) for n in STAGE2_NS for s in SURPLUS]
    outcome = decide(cells, null_cells, stage=2)
    write_json(
        EXP_ROOT / "stage2" / "timings.json",
        {
            "admitted": True,
            "kind": "ic",
            "races": [
                {k: v for k, v in rec.items() if k not in {"v_true"}}
                for rec in races_ic
            ],
            "cells": cells,
            "outcome": outcome,
        },
    )
    write_json(
        EXP_ROOT / "stage2" / "null-control.json",
        {
            "kind": "null",
            "races": [
                {k: v for k, v in rec.items() if k not in {"v_true"}}
                for rec in races_null
            ],
            "cells": null_cells,
            "interval": [NULL_RATIO_LO, NULL_RATIO_HI],
        },
    )
    write_results(
        EXP_ROOT / "stage2" / "RESULTS.md",
        outcome,
        "Stage 2 n in {23,31} IC-like plus Bernoulli-null. "
        f"ic_cells={json.dumps(cells, sort_keys=True)} "
        f"null_cells={json.dumps(null_cells, sort_keys=True)}",
    )
    return {"stage": 2, "outcome": outcome, "cells": cells, "null_cells": null_cells}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=AUTHORIZED_STAGES)
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        payload = stage0()
    elif args.stage == 1:
        payload = stage1()
    else:
        payload = stage2()
    raw = {
        "amazon_bedrock": "NOT_USED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "ecdlp_solve": False, "exponent_move": False},
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "magma_sage_auxin": "NOT_USED",
        "outcome": payload["outcome"],
        "source_idea": SOURCE_IDEA,
        "stage": args.stage,
        "trial_plan": args.trial_plan,
        "payload": payload,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": args.stage,
            "outcome": payload["outcome"],
            "approved_by": APPROVED_BY,
            "valid": True,
            "amazon_bedrock": "NOT_USED",
        },
    )
    print(json.dumps({"ok": True, "stage": args.stage, "outcome": payload["outcome"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
