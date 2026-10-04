#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-9d67ed. Dual-meter recompute; int n fields."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_residue import encode_pair, poly_basis  # noqa: E402
from gf2n import Field  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-9d67ed"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-FAIL-NULL",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
ALPHA = 3
N_TARGETS = 20
TARGET_SEED = 2026100302


def modulus_row(moduli: list, n: int) -> dict:
    matches = [row for row in moduli if row.get("n") == n]
    if len(matches) != 1:
        raise ValueError(f"expected one moduli row for n={n!r} (int), got {matches!r}")
    return matches[0]


def target_xR(n: int, ell: int, i: int) -> int:
    x = (TARGET_SEED * (i + 1) * 0x9E3779B1) ^ (n << 16) ^ (ell << 8) ^ i
    mask = (1 << n) - 1
    x = x & mask
    return x if x else 1


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir / "raw-result.json", run_dir / "manifest.yaml"
    errs = []
    if not raw_path.is_file() or raw_path.stat().st_size == 0:
        errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0:
        errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move"):
        errs.append("forbidden break/exponent claim present")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/encoder-pin.json",
            "stage0/v-catalog.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        pred = json.loads((root / "stage0" / "preregistered-predictions.json").read_text())
        pin = json.loads((root / "stage0" / "encoder-pin.json").read_text())
        cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
        if pred.get("alpha") != ALPHA:
            errs.append(f"alpha {pred.get('alpha')!r} != frozen {ALPHA}")
        if pred.get("n_targets") != N_TARGETS:
            errs.append("n_targets mismatch")
        if pred.get("target_seed") != TARGET_SEED:
            errs.append("target_seed mismatch")
        # Key-type lock: moduli and cells are lists; n is an int field, not a dict key.
        if isinstance(pin.get("moduli"), dict):
            errs.append("encoder-pin moduli must be a list, not a dict keyed by n")
        moduli = pin.get("moduli") or []
        if not isinstance(moduli, list):
            errs.append("moduli not a list")
        else:
            for row in moduli:
                if type(row.get("n")) is not int:
                    errs.append(f"moduli n must be JSON int, got {type(row.get('n'))}")
        cells = cat.get("cells")
        if isinstance(cells, dict):
            errs.append("v-catalog cells must be a list, not a dict keyed by n")
        elif not isinstance(cells, list):
            errs.append("v-catalog cells missing")
        else:
            for row in cells:
                if type(row.get("n")) is not int or type(row.get("ell")) is not int:
                    errs.append(f"catalog n/ell must be JSON ints, got {row!r}")
        stage1_cells = pred.get("authorized_stage1_cells") or []
        if isinstance(stage1_cells, dict):
            errs.append("authorized_stage1_cells must be a list of {n,ell} objects")
        else:
            for row in stage1_cells:
                if type(row.get("n")) is not int or type(row.get("ell")) is not int:
                    errs.append(f"stage1 cell n/ell must be JSON ints, got {row!r}")
        probe = cat.get("probe") or {}
        if type(probe.get("n")) is not int:
            errs.append("probe.n must be JSON int")
        else:
            try:
                mrow = modulus_row(moduli, probe["n"])
            except ValueError as exc:
                errs.append(str(exc))
                mrow = None
            if mrow is not None and type(probe.get("ell")) is int:
                F = Field(probe["n"], mrow["modulus"])
                basis = poly_basis(probe["ell"])
                pair = encode_pair(F, mrow["B"], basis, probe["xR"])
                if not pair["twin_ok"]:
                    errs.append("stage0 probe twin recompute failed")
                if pair["treated"]["C_nl_a"] != probe.get("treated_C_nl"):
                    errs.append("stage0 probe treated C_nl mismatch")
                if pair["null"]["C_nl_a"] != probe.get("null_C_nl"):
                    errs.append("stage0 probe null C_nl mismatch")
        if raw.get("outcome") not in {"O-STAGE0-OK", "O-ARTIFACT", "O-IMPEDIMENT"}:
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        pin = json.loads((root / "stage0" / "encoder-pin.json").read_text())
        moduli = pin.get("moduli") or []
        if (root / "stage1" / "panels.json").is_file():
            panels = json.loads((root / "stage1" / "panels.json").read_text())
            cells = panels.get("cells") or []
            if isinstance(cells, dict):
                errs.append("panels.cells must be a list, not a dict keyed by n")
            elif cells:
                row0 = cells[0]
                if type(row0.get("n")) is not int or type(row0.get("ell")) is not int:
                    errs.append("panel n/ell must be JSON ints")
                else:
                    mrow = modulus_row(moduli, row0["n"])
                    F = Field(row0["n"], mrow["modulus"])
                    basis = poly_basis(row0["ell"])
                    xR = target_xR(row0["n"], row0["ell"], 0)
                    pair = encode_pair(F, mrow["B"], basis, xR)
                    if not pair["twin_ok"]:
                        errs.append("stage1 row0 twin recompute failed")
                    rows = row0.get("rows") or []
                    if rows and rows[0].get("treated_C_nl") != pair["treated"]["C_nl_a"]:
                        errs.append("stage1 row0 treated C_nl mismatch vs recompute")
            if outcome in {"O-SUPPORT", "O-FAIL-BAND", "O-FAIL-NULL"}:
                for p in cells if isinstance(cells, list) else []:
                    if p.get("completed_target_count", 0) < N_TARGETS:
                        errs.append(f"{p.get('cell_id')}: band outcome without ≥20 targets")
                    if not p.get("twin_ok"):
                        errs.append(f"{p.get('cell_id')}: band outcome without twin_ok")
    else:
        errs.append(f"unknown stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
