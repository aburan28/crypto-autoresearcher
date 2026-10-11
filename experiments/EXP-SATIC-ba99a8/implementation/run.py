#!/usr/bin/env python3
"""EXP-SATIC-ba99a8 Stages 0-1: restricted S4 product identity, dual routes.

Stage 0: freeze cell rows (integer n) and counting table; 20 dual-route
identity tuples on n=5.
Stage 1: 100 dual-route identity tuples on n=17; known-false sum control;
school vs expand S3 agreement.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No W_D.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from math import comb
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-SATIC-ba99a8"
HYPOTHESIS_ID = "H-SATIC-1b0c4e"
APPROVED_BY = "DEC-20261003-82cf2b"
IMPL = Path(__file__).resolve().parent
EXP_ROOT = IMPL.parent
if str(IMPL) not in sys.path:
    sys.path.insert(0, str(IMPL))
from gf2n import Field  # noqa: E402
from s3_eval import (  # noqa: E402
    identity_pair,
    s3_expand,
    s3_school,
)

# List rows with integer n (CI freeze shape).
CELLS = [
    {"n": 5, "ell": 2, "neq": 5, "nvars": 4, "modulus": 37, "B": 1, "tuples": 20, "seed": 2026100305},
    {"n": 17, "ell": 6, "neq": 17, "nvars": 12, "modulus": (1 << 17) | (1 << 3) | 1, "B": 1, "tuples": 100, "seed": 2026100317},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def binom_le(n: int, d: int) -> int:
    return sum(comb(n, k) for k in range(d + 1))


def counting_row(n: int, ell: int, D: int) -> dict[str, int]:
    nv = 2 * ell
    # Product descent: n quartics; Macaulay at D uses multipliers of degree <= D-4.
    rows = n * binom_le(nv, max(D - 4, 0)) if D >= 4 else n
    cols = binom_le(nv, D)
    return {"n": n, "ell": ell, "nvars": nv, "neq": n, "D": D, "rows": rows, "cols": cols}


def load_plan(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sample_identity(F: Field, B: int, rng: random.Random, count: int) -> dict[str, Any]:
    q = F.q
    tried = 0
    skipped_deg = 0
    agree = 0
    school_ok = 0
    false_sum_hits = 0
    rows: list[dict[str, Any]] = []
    while len(rows) < count:
        tried += 1
        a = rng.randrange(q)
        x2 = rng.randrange(q)
        x3 = rng.randrange(q)
        xr = rng.randrange(q)
        if a == xr:
            skipped_deg += 1
            continue
        rec = identity_pair(F, a, x2, x3, xr, B)
        if rec["product"] is None:
            continue
        # Known-false: (a+xr)^4 * (g+ + g-) must not be required to equal sylvester.
        from s3_eval import product_side, quad_roots, quad_coeffs_s3, resultant_sylvester

        g = quad_coeffs_s3(F, a, xr, B)
        roots = quad_roots(F, *g)
        assert roots is not None
        gp = s3_expand(F, x2, x3, roots[0], B)
        gm = s3_expand(F, x2, x3, roots[1], B)
        pre = F.sqr(F.sqr(a ^ xr))
        false_sum = F.mul(pre, gp ^ gm)
        f = quad_coeffs_s3(F, x2, x3, B)
        syl = resultant_sylvester(F, f, g)
        if false_sum == syl and (gp == 0 or gm == 0 or gp == gm):
            # Coincidence possible; count only when both factors nonzero and unequal.
            pass
        elif false_sum == syl:
            false_sum_hits += 1
        if rec["agree"]:
            agree += 1
        if rec["school_expand_agree"]:
            school_ok += 1
        rows.append({
            "a": a,
            "x2": x2,
            "x3": x3,
            "x_r": xr,
            "agree": bool(rec["agree"]),
            "school_expand_agree": bool(rec["school_expand_agree"]),
        })
        if tried > count * 50:
            break
    return {
        "tried": tried,
        "skipped_a_eq_xr": skipped_deg,
        "kept": len(rows),
        "identity_agree": agree,
        "school_expand_agree": school_ok,
        "false_sum_equals_resultant": false_sum_hits,
        "rows": rows,
    }


def stage0(plan: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    cell5 = CELLS[0]
    F = Field(int(cell5["n"]), int(cell5["modulus"]))
    rng = random.Random(int(cell5["seed"]))
    sample = sample_identity(F, int(cell5["B"]), rng, int(cell5["tuples"]))
    counting = [counting_row(int(c["n"]), int(c["ell"]), D) for c in CELLS for D in (4, 5, 6, 7)]
    freeze_cells = {
        "schema": "crypto.autoresearch.satic_prodpen_cells.v1",
        "experiment_id": EXPERIMENT_ID,
        "rows": [{k: v for k, v in c.items()} for c in CELLS],
        "note": "List rows; n is JSON integer. Stage 0 uses n=5 only.",
    }
    freeze_count = {
        "schema": "crypto.autoresearch.satic_prodpen_counting.v1",
        "experiment_id": EXPERIMENT_ID,
        "rows": counting,
        "note": "Product-descent Macaulay sizes; n integer. Not a W_D run.",
    }
    write_json(EXP_ROOT / "stage0" / "cells.json", freeze_cells)
    write_json(EXP_ROOT / "stage0" / "counting.json", freeze_count)
    write_json(EXP_ROOT / "stage0" / "n5-identity.json", {
        "n": 5,
        "seed": cell5["seed"],
        "sample": {k: sample[k] for k in sample if k != "rows"},
    })
    identity_ok = sample["kept"] == int(cell5["tuples"]) and sample["identity_agree"] == sample["kept"]
    school_ok = sample["school_expand_agree"] == sample["kept"]
    outcome = "O-STAGE0-OK" if identity_ok and school_ok else "O-ARTIFACT"
    if sample["kept"] < int(cell5["tuples"]):
        outcome = "O-IMPEDIMENT"
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "identity_ok": identity_ok,
        "outcome": outcome,
        "stage": 0,
        "stage0_n": 5,
        "sample": {k: sample[k] for k in sample if k != "rows"},
        "utc": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        f"id: RUN-SATIC-aa4881\nexperiment_id: {EXPERIMENT_ID}\nstage: 0\noutcome: {outcome}\namazon_bedrock: NOT SELECTED\n",
    )
    write_text(
        EXP_ROOT / "RESULTS.md" if False else run_dir / "stdout-note.txt",
        f"Stage 0 {outcome} identity_ok={identity_ok}\n",
    )
    return raw


def stage1(plan: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    cells_path = EXP_ROOT / "stage0" / "cells.json"
    if not cells_path.is_file():
        raw = {
            "amazon_bedrock": "NOT SELECTED",
            "approved_by": APPROVED_BY,
            "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
            "experiment_id": EXPERIMENT_ID,
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0 freeze missing; Stage 0 must complete first",
            "stage": 1,
            "utc": utc_now(),
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"id: RUN-SATIC-ec59bf\nexperiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\namazon_bedrock: NOT SELECTED\n",
        )
        return raw
    freeze = json.loads(cells_path.read_text(encoding="utf-8"))
    rows = freeze.get("rows")
    if not isinstance(rows, list) or not rows or not isinstance(rows[0].get("n"), int):
        raise ValueError("cells.json must be list rows with integer n")
    cell17 = CELLS[1]
    F = Field(int(cell17["n"]), int(cell17["modulus"]))
    rng = random.Random(int(cell17["seed"]))
    sample = sample_identity(F, int(cell17["B"]), rng, int(cell17["tuples"]))
    identity_ok = sample["kept"] == int(cell17["tuples"]) and sample["identity_agree"] == sample["kept"]
    school_ok = sample["school_expand_agree"] == sample["kept"]
    false_ok = sample["false_sum_equals_resultant"] == 0
    if sample["kept"] < int(cell17["tuples"]):
        outcome = "O-IMPEDIMENT"
    elif identity_ok and school_ok and false_ok:
        outcome = "O-SUPPORT"
    elif not identity_ok:
        outcome = "O-FAIL-IDENTITY"
    else:
        outcome = "O-ARTIFACT"
    panel = {
        "schema": "crypto.autoresearch.satic_prodpen_stage1.v1",
        "rows": [
            {
                "n": 17,
                "ell": 6,
                "kept": sample["kept"],
                "identity_agree": sample["identity_agree"],
                "school_expand_agree": sample["school_expand_agree"],
                "false_sum_equals_resultant": sample["false_sum_equals_resultant"],
                "skipped_a_eq_xr": sample["skipped_a_eq_xr"],
            }
        ],
    }
    write_json(EXP_ROOT / "stage1" / "identity-panel.json", panel)
    write_text(
        EXP_ROOT / "RESULTS.md",
        (
            f"# RESULTS — EXP-SATIC-ba99a8\n\n"
            f"Outcome: **{outcome}**\n\n"
            f"Stage 1 n=17 identity_agree={sample['identity_agree']}/{sample['kept']}. "
            f"No ECDLP solve. No exponent. Toy dual-route arithmetic only.\n"
        ),
    )
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "identity_ok": identity_ok,
        "n": 17,
        "outcome": outcome,
        "sample": {k: sample[k] for k in sample if k != "rows"},
        "stage": 1,
        "utc": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        f"id: RUN-SATIC-ec59bf\nexperiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: {outcome}\namazon_bedrock: NOT SELECTED\n",
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=[0, 1])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = load_plan(Path(args.trial_plan))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial-plan experiment_id mismatch", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(plan, run_dir)
    else:
        stage1(plan, run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
