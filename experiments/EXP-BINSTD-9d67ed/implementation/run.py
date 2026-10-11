#!/usr/bin/env python3
"""EXP-BINSTD-9d67ed Stages 0-1: Karabina residual nonlinear clause density.

Stage 0: freeze α, encoder pin, seeds, Karabina transform, V bases, target
         generator; twin-meter probe. Cell records are a LIST of objects with
         integer n/ell fields (never JSON-object keys equal to n).
Stage 1: n=17, ell in {3,4}, ≥20 independent xR targets; treated vs unsym
         null; median C_nl/N_var vs frozen α.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_residue import encode_pair, poly_basis  # noqa: E402
from gf2n import Field  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-9d67ed"
HYPOTHESIS_ID = "H-BINSTD-d460e5"
APPROVED_BY = "DEC-20261003-5c1347"
SOURCE_IDEA = "IDEA-20261002-92aa34"
EXP_ROOT = Path(__file__).resolve().parents[1]

# Moduli as a LIST of records so JSON freeze files never stringify n as a key.
MODULI_ROWS = [
    {"n": 17, "modulus": (1 << 17) | (1 << 3) | 1, "B": 1},
    {"n": 19, "modulus": (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1, "B": 1},
    {"n": 23, "modulus": (1 << 23) | (1 << 5) | 1, "B": 1},
]
ALPHA = 3
N_TARGETS = 20
TARGET_SEED = 2026100302
PIN_SEED = 2026100301
AUTHORIZED_STAGE1_CELLS = [{"n": 17, "ell": 3}, {"n": 17, "ell": 4}]
STAGE0_PROBE_CELL = {"n": 17, "ell": 3}
STAGE0_CATALOG_CELLS = [
    {"n": 17, "ell": 3},
    {"n": 17, "ell": 4},
    {"n": 19, "ell": 3},
    {"n": 19, "ell": 4},
    {"n": 23, "ell": 3},
    {"n": 23, "ell": 4},
]
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-FAIL-NULL",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


def cell_id(n: int, ell: int) -> str:
    return f"n{n}_l{ell}"


def modulus_for(n: int) -> dict:
    for row in MODULI_ROWS:
        if row["n"] == n:
            return row
    raise KeyError(n)


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
    lines = ["run:"]
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"  {k}: {'true' if v else 'false'}")
        elif v is None:
            lines.append(f"  {k}: null")
        elif isinstance(v, (int, float)):
            lines.append(f"  {k}: {v}")
        else:
            lines.append(f"  {k}: {json.dumps(v)}")
    write_text(path, "\n".join(lines) + "\n")


def target_xR(n: int, ell: int, i: int) -> int:
    """Deterministic nonzero xR from TARGET_SEED; n,ell,i are ints not strings."""
    x = (TARGET_SEED * (i + 1) * 0x9E3779B1) ^ (n << 16) ^ (ell << 8) ^ i
    mask = (1 << n) - 1
    x = (x & mask)
    if x == 0:
        x = 1
    return x


def targets_for(n: int, ell: int) -> list[int]:
    return [target_xR(n, ell, i) for i in range(N_TARGETS)]


def field_for(n: int) -> Field:
    row = modulus_for(n)
    return Field(n, row["modulus"])


def measure_cell(n: int, ell: int) -> dict:
    F = field_for(n)
    B = modulus_for(n)["B"]
    basis = poly_basis(ell)
    rows = []
    treated_d = []
    null_d = []
    twin_ok = True
    artifact = False
    for i, xR in enumerate(targets_for(n, ell)):
        pair = encode_pair(F, B, basis, xR)
        if not pair["twin_ok"]:
            twin_ok = False
            if pair["null"]["artifact"] or pair["treated"]["artifact"]:
                artifact = True
        td = pair["treated"]["density_a"]
        nd = pair["null"]["density_a"]
        if td is not None:
            treated_d.append(td)
        if nd is not None:
            null_d.append(nd)
        rows.append({
            "target_index": i,
            "xR": xR,
            "n": n,
            "ell": ell,
            "treated_C_nl": pair["treated"]["C_nl_a"],
            "treated_N_var": pair["treated"]["N_var_a"],
            "treated_density": td,
            "null_C_nl": pair["null"]["C_nl_a"],
            "null_N_var": pair["null"]["N_var_a"],
            "null_density": nd,
            "twin_ok": pair["twin_ok"],
        })
    completed = len(treated_d)
    median_t = statistics.median(treated_d) if treated_d else None
    median_n = statistics.median(null_d) if null_d else None
    return {
        "cell_id": cell_id(n, ell),
        "n": n,
        "ell": ell,
        "basis": basis,
        "completed_target_count": completed,
        "median_treated": median_t,
        "median_null": median_n,
        "twin_ok": twin_ok,
        "artifact": artifact,
        "alpha": ALPHA,
        "band_holds": (median_t is not None and completed >= N_TARGETS and median_t <= ALPHA),
        "null_ge_treated": (
            median_t is not None and median_n is not None and median_n >= median_t
        ),
        "rows": rows,
    }


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    F = field_for(STAGE0_PROBE_CELL["n"])
    B = modulus_for(STAGE0_PROBE_CELL["n"])["B"]
    basis = poly_basis(STAGE0_PROBE_CELL["ell"])
    xR = target_xR(STAGE0_PROBE_CELL["n"], STAGE0_PROBE_CELL["ell"], 0)
    probe = encode_pair(F, B, basis, xR)
    catalog = []
    for cell in STAGE0_CATALOG_CELLS:
        catalog.append({
            "cell_id": cell_id(cell["n"], cell["ell"]),
            "n": cell["n"],
            "ell": cell["ell"],
            "basis": poly_basis(cell["ell"]),
            "n_targets": N_TARGETS,
        })
    pred = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "source_idea": SOURCE_IDEA,
        "alpha": ALPHA,
        "n_targets": N_TARGETS,
        "target_seed": TARGET_SEED,
        "pin_seed": PIN_SEED,
        "transform": "karabina_aux_S_eq_x1plusx2_P_eq_x1x2_plus_symmetric_S3",
        "null_transform": "unsymmetrised_S3_x1x2_in_span_V",
        "C_nl_definition": (
            "count of Weil-bit equations retaining a deg>=2 monomial after "
            "deleting monomials supported only on pure-linear pivots"
        ),
        "N_var_definition": "len(nonlinear_support minus linear pivots)",
        "density_definition": "C_nl / N_var; N_var=0 and C_nl=0 => 0; else artifact",
        "authorized_stage1_cells": AUTHORIZED_STAGE1_CELLS,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
    }
    pin = {
        "experiment_id": EXPERIMENT_ID,
        "moduli": MODULI_ROWS,
        "encoder": "poly_basis span{1,t,...,t^{ell-1}}",
        "curve_B_note": "B stored per moduli row as integer field B, never keyed by n",
        "amazon_bedrock": "NOT SELECTED",
    }
    vcat = {
        "experiment_id": EXPERIMENT_ID,
        "cells": catalog,
        "probe": {
            "cell_id": cell_id(STAGE0_PROBE_CELL["n"], STAGE0_PROBE_CELL["ell"]),
            "n": STAGE0_PROBE_CELL["n"],
            "ell": STAGE0_PROBE_CELL["ell"],
            "xR": xR,
            "twin_ok": probe["twin_ok"],
            "treated_C_nl": probe["treated"]["C_nl_a"],
            "treated_N_var": probe["treated"]["N_var_a"],
            "null_C_nl": probe["null"]["C_nl_a"],
            "null_N_var": probe["null"]["N_var_a"],
        },
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "encoder-pin.json", pin)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", vcat)
    outcome = "O-STAGE0-OK" if probe["twin_ok"] else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": outcome,
        "twin_ok": probe["twin_ok"],
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False},
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(run_dir / "manifest.yaml", {
        "id": "RUN-BINSTD-c87287",
        "experiment_id": EXPERIMENT_ID,
        "status": "completed",
        "stage": 0,
        "valid": True,
    })
    return raw


def decide_outcome(panels: list[dict]) -> str:
    if any(p["artifact"] or not p["twin_ok"] for p in panels):
        return "O-ARTIFACT"
    if any(p["completed_target_count"] < N_TARGETS for p in panels):
        return "O-INCONCLUSIVE"
    if any(not p["band_holds"] for p in panels):
        return "O-FAIL-BAND"
    if any(not p["null_ge_treated"] for p in panels):
        return "O-FAIL-NULL"
    return "O-SUPPORT"


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    pin_path = EXP_ROOT / "stage0" / "encoder-pin.json"
    if not pred_path.is_file() or not pin_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze",
            "amazon_bedrock": "NOT SELECTED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(run_dir / "manifest.yaml", {
            "id": "RUN-BINSTD-4c79f8",
            "experiment_id": EXPERIMENT_ID,
            "status": "completed",
            "stage": 1,
            "valid": True,
        })
        return raw
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    if pred.get("alpha") != ALPHA:
        raise RuntimeError("alpha mutated after freeze")
    panels = []
    for cell in AUTHORIZED_STAGE1_CELLS:
        panels.append(measure_cell(cell["n"], cell["ell"]))
    outcome = decide_outcome(panels)
    panel_obj = {
        "experiment_id": EXPERIMENT_ID,
        "cells": panels,
        "outcome": outcome,
        "amazon_bedrock": "NOT SELECTED",
    }
    control = {
        "experiment_id": EXPERIMENT_ID,
        "null_unsymmetrised_encode": True,
        "shared_encoder_pin": True,
        "frozen_alpha": ALPHA,
        "n_targets": N_TARGETS,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage1" / "panels.json", panel_obj)
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)
    lines = [
        f"# RESULTS EXP-BINSTD-9d67ed",
        "",
        f"outcome: {outcome}",
        f"alpha: {ALPHA}",
        f"n_targets: {N_TARGETS}",
        "claim_tier: toy encoding-residue instrument. NO break. NO exponent. NO n>=131.",
        "",
        "| cell_id | n | ell | completed | median_treated | median_null | band_holds | null_ge_treated | twin_ok |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for p in panels:
        lines.append(
            f"| {p['cell_id']} | {p['n']} | {p['ell']} | {p['completed_target_count']} | "
            f"{p['median_treated']} | {p['median_null']} | {p['band_holds']} | "
            f"{p['null_ge_treated']} | {p['twin_ok']} |"
        )
    lines.extend([
        "",
        "O-* vocabulary: O-SUPPORT / O-FAIL-BAND / O-FAIL-NULL / O-INCONCLUSIVE / O-ARTIFACT / O-IMPEDIMENT.",
        "Exactly one outcome label above. Amazon Bedrock was not used.",
        "",
    ])
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines))
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "cells": [
            {
                "cell_id": p["cell_id"],
                "n": p["n"],
                "ell": p["ell"],
                "completed_target_count": p["completed_target_count"],
                "median_treated": p["median_treated"],
                "median_null": p["median_null"],
                "band_holds": p["band_holds"],
                "null_ge_treated": p["null_ge_treated"],
                "twin_ok": p["twin_ok"],
            }
            for p in panels
        ],
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False},
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(run_dir / "manifest.yaml", {
        "id": "RUN-BINSTD-4c79f8",
        "experiment_id": EXPERIMENT_ID,
        "status": "completed",
        "stage": 1,
        "valid": True,
    })
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=(0, 1))
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    print(json.dumps({"ok": True, "outcome": raw.get("outcome"), "stage": args.stage}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
