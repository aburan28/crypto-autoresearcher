#!/usr/bin/env python3
"""EXP-BINSTD-6cca48 Stages 0-1: Koblitz-shape m=4 affordability arithmetic.

Stdlib-only. Freezes and independently rechecks the leaf-count table from
IDEA-20260922-493606 sections (B)/(D)/(E) under closed forms
N_conf = 2^{m*l} / (m! * mu) and admissibility m*(l-1) <= n.

Stage 0: freeze affordability table, predictions, forward-condition
         disclaimer, dependency gate, closed-form source pin.
Stage 1: recompute every cell from (m,l,mu) alone; write RESULTS.md with
         exactly one O-* label.

No Magma/Sage/AUXIN/Bedrock/CDCL. No break / exponent / rho / n>=131.
Proposal Stages 2-5 (CNF-XOR cells) are NOT authorized under this card.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

EXPERIMENT_ID = "EXP-BINSTD-6cca48"
HYPOTHESIS_ID = "H-BINSTD-0f9bf7"
APPROVED_BY = "DEC-20261003-4da874"
SEED = 20261003493606
OUTCOMES = ("O-ARITH-OK", "O-ARITH-FAIL", "O-ARTIFACT", "O-IMPEDIMENT")
EXP_ROOT = Path(__file__).resolve().parents[1]

# ---- Closed-form evaluation (pinned by Stage 0) ----

CELLS: List[Dict[str, Any]] = [
    {"id": "anchor_m3_l8", "m": 3, "l": 8, "mu": 1, "n": None, "predicted_leaves": 2796203},
    {"id": "null_m4_l8_n37", "m": 4, "l": 8, "mu": 1, "n": 37, "predicted_leaves": 178956971},
    {"id": "koblitz_m4_l8_n37", "m": 4, "l": 8, "mu": 37, "n": 37, "predicted_leaves": 4836675},
    {"id": "null_m5_l6_n29", "m": 5, "l": 6, "mu": 1, "n": 29, "predicted_leaves": 8947849},
    {"id": "koblitz_m5_l6_n29", "m": 5, "l": 6, "mu": 29, "n": 29, "predicted_leaves": 308547},
]


def leaf_count(m: int, l: int, mu: int) -> int:
    """N_conf(l,m,|G|) ≈ 2^{m*l} / (m! * mu), nearest-integer (proposal (B)/(D))."""
    if m < 1 or l < 1 or mu < 1:
        raise ValueError("m,l,mu must be positive")
    numerator = 1 << (m * l)
    denom = math.factorial(m) * mu
    return int(round(numerator / denom))


def admissible(m: int, l: int, n: Optional[int]) -> bool:
    if n is None:
        return True
    return m * (l - 1) <= n


def closed_form_source_hash() -> str:
    src = Path(__file__).read_text(encoding="utf-8")
    marker = "# ---- Closed-form evaluation"
    end = "# ---- I/O helpers"
    i = src.find(marker)
    j = src.find(end)
    if i < 0 or j < 0 or j <= i:
        raise RuntimeError("closed-form block markers missing")
    return sha256_bytes(src[i:j].encode())


# ---- I/O helpers ----

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode())


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def recompute_table() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for cell in CELLS:
        m, l, mu, n = cell["m"], cell["l"], cell["mu"], cell["n"]
        leaves = leaf_count(m, l, mu)
        adm = admissible(m, l, n)
        rows.append(
            {
                "id": cell["id"],
                "m": m,
                "l": l,
                "mu": mu,
                "n": n,
                "predicted_leaves": cell["predicted_leaves"],
                "recomputed_leaves": leaves,
                "leaves_match": leaves == cell["predicted_leaves"],
                "admissible": adm,
                "admissible_expected": True if n is not None else True,
            }
        )
    return rows


def stage0(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    pin_hash = closed_form_source_hash()
    # Sanity: frozen predictions must match live closed form at freeze time.
    rows = recompute_table()
    if not all(r["leaves_match"] and r["admissible"] for r in rows):
        raise RuntimeError("Stage-0 freeze refused: live closed form disagrees with CELLS")

    table = {
        "seed": SEED,
        "closed_form": "N_conf = round(2^{m*l} / (m! * mu))  # nearest-integer; IDEA-20260922-493606 (B)/(D)",
        "admissibility": "m*(l-1) <= n when n is not null",
        "cells": CELLS,
        "derived_ratios": {
            "ratio_koblitz_m4_to_anchor": 4836675 / 2796203,
            "ratio_null_m4_to_anchor": 178956971 / 2796203,
            "koblitz_within_factor_1_73_of_anchor": (4836675 / 2796203) <= 1.73,
        },
        "citation_chain": [
            "IDEA-20260904-3c7a91",
            "IDEA-20260922-7ab503",
            "IDEA-20260904-b40e6d",
            "IDEA-20260904-96c4f3",
            "IDEA-20260922-493606",
        ],
    }
    predictions = {
        "heuristic": "HEUR-BINSTD-493606-H1",
        "primary_metric": "leaf_count_table_match",
        "expected_outcome_if_arithmetic_correct": "O-ARITH-OK",
        "frozen_before_stage1": True,
        "note": "Do not edit after any Stage-1 outcome. No CDCL under this card.",
    }
    disclaimer = {
        "no_rho_claim": True,
        "forward_condition": {
            "m4_c": "1/3",
            "m4_gap_in_l_exponent": 2,
            "note": (
                "mu-fold gain is a CONSTANT (log2(37)~5.2 bits), not a change to "
                "exponent c; affordability != competitiveness with rho."
            ),
        },
        "no_break": True,
        "no_n_ge_131_transfer": True,
        "stages_2_to_5_not_authorized": True,
    }
    dependency = {
        "chained_on": "IDEA-20260922-7ab503",
        "what_stages_01_do_not_require": "H1 confirmation at m=4",
        "what_later_cdcl_cells_require": "7ab503 H1 at m=4 plus normal-basis constructibility at n=37",
        "note": "O-ARITH-OK is not a license to run the m=4 CDCL cell under this card.",
    }
    h_table = write_json(stage0_dir / "affordability-table.json", table)
    h_pred = write_json(stage0_dir / "preregistered-predictions.json", predictions)
    h_disc = write_json(stage0_dir / "forward-condition-disclaimer.json", disclaimer)
    h_dep = write_json(stage0_dir / "dependency-gate.json", dependency)
    h_pin = write_json(
        stage0_dir / "closed-form-pin.json",
        {
            "closed_form_source_sha256": pin_hash,
            "source_file": "experiments/EXP-BINSTD-6cca48/implementation/run.py",
            "functions": ["leaf_count", "admissible", "CELLS"],
        },
    )
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed_valid",
        "outcome": "S0-FREEZE-OK",
        "artifact_sha256": {
            "stage0/affordability-table.json": h_table,
            "stage0/preregistered-predictions.json": h_pred,
            "stage0/forward-condition-disclaimer.json": h_disc,
            "stage0/dependency-gate.json": h_dep,
            "stage0/closed-form-pin.json": h_pin,
        },
        "closed_form_source_sha256": pin_hash,
        "claims": {"break": False, "exponent_move": False, "rho_competitive": False},
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", result)
    write_json(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 0,
            "status": "completed_valid",
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": result["recorded_at"],
        },
    )
    return result


def stage1(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    stage1_dir = EXP_ROOT / "stage1"
    required = [
        stage0_dir / "affordability-table.json",
        stage0_dir / "preregistered-predictions.json",
        stage0_dir / "forward-condition-disclaimer.json",
        stage0_dir / "dependency-gate.json",
        stage0_dir / "closed-form-pin.json",
    ]
    if not all(p.is_file() for p in required):
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze artifacts missing",
            "claims": {"break": False, "exponent_move": False, "rho_competitive": False},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", result)
        write_json(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment", "amazon_bedrock": "NOT SELECTED"},
        )
        write_text(
            EXP_ROOT / "RESULTS.md",
            "# RESULTS — EXP-BINSTD-6cca48\n\nLabel: **O-IMPEDIMENT**\n\nStage-0 freeze missing; no arithmetic claim.\n",
        )
        return result

    pin = json.loads((stage0_dir / "closed-form-pin.json").read_text())
    if pin.get("closed_form_source_sha256") != closed_form_source_hash():
        result = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "artifact",
            "outcome": "O-ARTIFACT",
            "reason": "closed-form source hash drift vs Stage-0 pin",
            "claims": {"break": False, "exponent_move": False, "rho_competitive": False},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", result)
        write_json(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "artifact"})
        write_text(
            EXP_ROOT / "RESULTS.md",
            "# RESULTS — EXP-BINSTD-6cca48\n\nLabel: **O-ARTIFACT**\n\nClosed-form source hash drifted after Stage-0 freeze.\n",
        )
        return result

    frozen = json.loads((stage0_dir / "affordability-table.json").read_text())
    if frozen.get("cells") != CELLS:
        result = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "artifact",
            "outcome": "O-ARTIFACT",
            "reason": "frozen CELLS drifted from live CELLS constant",
            "claims": {"break": False, "exponent_move": False, "rho_competitive": False},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", result)
        write_json(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "artifact"})
        write_text(
            EXP_ROOT / "RESULTS.md",
            "# RESULTS — EXP-BINSTD-6cca48\n\nLabel: **O-ARTIFACT**\n\nFrozen affordability table drifted from live CELLS.\n",
        )
        return result

    rows = recompute_table()
    leaves_ok = all(r["leaves_match"] for r in rows)
    adm_ok = all(r["admissible"] for r in rows)
    anchor = next(r for r in rows if r["id"] == "anchor_m3_l8")["recomputed_leaves"]
    koblitz_m4 = next(r for r in rows if r["id"] == "koblitz_m4_l8_n37")["recomputed_leaves"]
    null_m4 = next(r for r in rows if r["id"] == "null_m4_l8_n37")["recomputed_leaves"]
    ratio_k = koblitz_m4 / anchor
    ratio_n = null_m4 / anchor
    if leaves_ok and adm_ok:
        label, status, reason = (
            "O-ARITH-OK",
            "completed_valid",
            "all leaf counts and admissibility checks match Stage-0 freeze",
        )
    else:
        label, status, reason = (
            "O-ARITH-FAIL",
            "completed_valid",
            "at least one recomputed leaf count or admissibility check disagrees",
        )

    panels = {
        "rows": rows,
        "leaf_count_table_match": leaves_ok,
        "admissibility_all_ok": adm_ok,
        "ratio_koblitz_m4_to_anchor": ratio_k,
        "ratio_null_m4_to_anchor": ratio_n,
        "koblitz_within_factor_1_73": ratio_k <= 1.73 + 1e-12,
    }
    controls = {
        "closed_form_pin_ok": True,
        "cells_frozen_match_live": True,
        "no_cdcl": True,
        "forward_disclaimer_present": (stage0_dir / "forward-condition-disclaimer.json").is_file(),
    }
    h_panels = write_json(stage1_dir / "recompute-table.json", panels)
    h_ctl = write_json(stage1_dir / "control-table.json", controls)
    write_text(
        EXP_ROOT / "RESULTS.md",
        (
            f"# RESULTS — EXP-BINSTD-6cca48\n\n"
            f"Label: **{label}**\n\n"
            f"- hypothesis: {HYPOTHESIS_ID}\n"
            f"- approved_by: {APPROVED_BY}\n"
            f"- leaf_count_table_match: {leaves_ok}\n"
            f"- admissibility_all_ok: {adm_ok}\n"
            f"- ratio_koblitz_m4_to_anchor: {ratio_k}\n"
            f"- ratio_null_m4_to_anchor: {ratio_n}\n"
            f"- reason: {reason}\n"
            f"- claims: break=false, exponent_move=false, rho_competitive=false\n"
            f"- amazon_bedrock: NOT SELECTED\n"
            f"- note: Proposal Stages 2-5 (CNF-XOR cells) not authorized under this card.\n"
        ),
    )
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": status,
        "outcome": label,
        "reason": reason,
        "leaf_count_table_match": leaves_ok,
        "admissibility_all_ok": adm_ok,
        "ratio_koblitz_m4_to_anchor": ratio_k,
        "ratio_null_m4_to_anchor": ratio_n,
        "artifact_sha256": {
            "stage1/recompute-table.json": h_panels,
            "stage1/control-table.json": h_ctl,
        },
        "claims": {"break": False, "exponent_move": False, "rho_competitive": False},
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", result)
    write_json(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": status,
            "outcome": label,
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": result["recorded_at"],
        },
    )
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", type=str, required=True)
    ap.add_argument("--run-dir", type=str, required=True)
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if not Path(args.trial_plan).is_file():
        print(f"missing trial plan: {args.trial_plan}", file=sys.stderr)
        return 2
    try:
        if args.stage == 0:
            stage0(run_dir)
        else:
            stage1(run_dir)
    except FileExistsError as exc:
        print(f"refuse overwrite: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        err = {
            "experiment_id": EXPERIMENT_ID,
            "stage": args.stage,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": f"{type(exc).__name__}: {exc}",
            "claims": {"break": False, "exponent_move": False, "rho_competitive": False},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        raw = run_dir / "raw-result.json"
        if not raw.exists():
            raw.write_text(json.dumps(err, indent=2, sort_keys=True) + "\n")
        man = run_dir / "manifest.yaml"
        if not man.exists():
            man.write_text(json.dumps({"experiment_id": EXPERIMENT_ID, "status": "impediment"}, indent=2) + "\n")
        print(f"impediment: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
