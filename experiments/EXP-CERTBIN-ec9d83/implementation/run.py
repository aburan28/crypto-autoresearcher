#!/usr/bin/env python3
"""EXP-CERTBIN-ec9d83 Stages 0-1: freeze then dual-route R_mem arithmetic.

No Magma/Sage/AUXIN/Bedrock. No SAT/MITM. No ECDLP solve.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-CERTBIN-ec9d83"
HYPOTHESIS_ID = "H-CERTBIN-e50e56"
APPROVED_BY = "DEC-20261003-61f2d6"
ENTRY_BYTES = 16
GIB = 2 ** 30
STAGE1_OUTCOMES = ("O-IDENTITY", "O-COUNTEREXAMPLE", "O-ARTIFACT", "O-IMPEDIMENT")
IMP = Path(__file__).resolve().parent
EXP_ROOT = IMP.parent

FROZEN_ROWS = [
    {
        "id": "n83-m3",
        "degree": 83,
        "m": 3,
        "k": 1,
        "B": 52544464,
        "R_mem_printed": 3.806e-8,
        "pair_gib_printed": 20570462.6,
        "R_mem_abs_tol": 5e-11,
        "R_mem_rel_tol": 5e-4,
    },
    {
        "id": "n83-m4",
        "degree": 83,
        "m": 4,
        "k": 2,
        "B": 872790,
        "R_mem_printed": 1.000002,
        "pair_gib_printed": 5675.6,
        "R_mem_abs_tol": 5e-7,
        "R_mem_rel_tol": None,
    },
    {
        "id": "n131-m4",
        "degree": 131,
        "m": 4,
        "k": 2,
        "B": 3574951633,
        "R_mem_printed": 1.000000,
        "pair_gib_printed": None,
        "R_mem_abs_tol": 5e-7,
        "R_mem_rel_tol": None,
    },
    {
        "id": "n83-m7",
        "degree": 83,
        "m": 7,
        "k": 3,
        "B": 5325,
        "R_mem_printed": 1776.33,
        "pair_gib_printed": 0.211,
        "fold_gib_printed": 375.2,
        "complementary_C_Bplus3_4_printed": 3.353949e13,
        "R_mem_abs_tol": 0.1,
        "R_mem_rel_tol": None,
    },
    {
        "id": "n131-m7",
        "degree": 131,
        "m": 7,
        "k": 3,
        "B": 617668,
        "R_mem_printed": 2.058907e5,
        "pair_gib_printed": None,
        "R_mem_abs_tol": None,
        "R_mem_rel_tol": 5e-7,
    },
]
OMITTED = [
    {"id": "n131-m3", "degree": 131, "m": 3, "reason": "B not printed in IDEA-20260930-77ec1c"},
    {"id": "m10", "m": 10, "reason": "out of this contract"},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    text = json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def load_route(name: str, filename: str) -> Any:
    path = IMP / filename
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def three_sig_match(computed: float, printed: float) -> bool:
    if printed == 0:
        return computed == 0
    return abs(computed - printed) / abs(printed) < 0.005


def pair_gib(B: int) -> float:
    return (B * (B - 1) // 2) * ENTRY_BYTES / GIB


def stage0(run_dir: Path) -> dict[str, Any]:
    freeze = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "entry_bytes": ENTRY_BYTES,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "k_rule": "floor(m/2)",
        "m_k_formula": "C(B+k-1, k)",
        "m_pair_formula": "B*(B-1)/2",
        "omitted_rows": OMITTED,
        "rows": FROZEN_ROWS,
        "source_idea": "IDEA-20260930-77ec1c",
        "successor_pointer": "IDEA-20260930-14c753",
    }
    write_json(run_dir / "r_mem_frozen.json", freeze)
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "exponent_move": False, "ecdlp_solve": False},
        "experiment_id": EXPERIMENT_ID,
        "frozen_row_ids": [row["id"] for row in FROZEN_ROWS],
        "hypothesis_id": HYPOTHESIS_ID,
        "n_ge_131_solve": False,
        "omitted_row_ids": [row["id"] for row in OMITTED],
        "outcome": "O-FREEZE",
        "row_count": len(FROZEN_ROWS),
        "stage": 0,
        "status": "completed",
        "utc": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                f"approved_by: {APPROVED_BY}",
                "stage: 0",
                "outcome: O-FREEZE",
                "amazon_bedrock: NOT SELECTED",
                "status: completed",
                f"frozen_sha256: {sha256_bytes((run_dir / 'r_mem_frozen.json').read_bytes())}",
                "",
            ]
        ),
    )
    return raw


def r_mem_ok(value: float, row: dict[str, Any]) -> bool:
    printed = float(row["R_mem_printed"])
    abs_tol = row.get("R_mem_abs_tol")
    rel_tol = row.get("R_mem_rel_tol")
    if abs_tol is not None and abs(value - printed) > abs_tol:
        return False
    if rel_tol is not None and abs(value - printed) > rel_tol * abs(printed):
        return False
    return True


def stage1(run_dir: Path) -> dict[str, Any]:
    freeze_path = EXP_ROOT / "runs" / "RUN-CERTBIN-004f53" / "r_mem_frozen.json"
    if not freeze_path.is_file():
        raw = {
            "amazon_bedrock": "NOT SELECTED",
            "approved_by": APPROVED_BY,
            "claims": {"break": False, "exponent_move": False, "ecdlp_solve": False},
            "experiment_id": EXPERIMENT_ID,
            "impediment": f"missing freeze table at {freeze_path.as_posix()}",
            "outcome": "O-IMPEDIMENT",
            "stage": 1,
            "status": "failed_infrastructure",
            "utc": utc_now(),
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            "\n".join(
                [
                    f"experiment_id: {EXPERIMENT_ID}",
                    "stage: 1",
                    "outcome: O-IMPEDIMENT",
                    "amazon_bedrock: NOT SELECTED",
                    "status: failed_infrastructure",
                    "",
                ]
            ),
        )
        return raw

    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    product = load_route("route_product", "route_product.py")
    closed = load_route("route_closedform", "route_closedform.py")
    src_p = (IMP / "route_product.py").read_text(encoding="utf-8")
    src_c = (IMP / "route_closedform.py").read_text(encoding="utf-8")
    def _imports_peer(src: str, peer: str) -> bool:
        return f"import {peer}" in src or f"from {peer}" in src

    if _imports_peer(src_p, "route_closedform") or _imports_peer(src_c, "route_product"):
        raise RuntimeError("routes import each other")

    comparisons: list[dict[str, Any]] = []
    routes_agree = True
    matches_printed = True
    pair_ok = True
    for row in freeze["rows"]:
        m, B = int(row["m"]), int(row["B"])
        mk_p, mk_c = product.m_k(m, B), closed.m_k(m, B)
        mp_p, mp_c = product.m_pair(B), closed.m_pair(B)
        r_p, r_c = float(product.r_mem(m, B)), float(closed.r_mem(m, B))
        agree = mk_p == mk_c and mp_p == mp_c and math.isclose(r_p, r_c, rel_tol=0, abs_tol=0)
        if not agree:
            routes_agree = False
        r_match = r_mem_ok(r_p, row) and r_mem_ok(r_c, row)
        if not r_match:
            matches_printed = False
        pg = pair_gib(B)
        printed_g = row.get("pair_gib_printed")
        g_match = printed_g is None or three_sig_match(pg, float(printed_g))
        if not g_match:
            pair_ok = False
        extra: dict[str, Any] = {}
        if row["id"] == "n83-m7":
            extra["fold_gib"] = mk_p * ENTRY_BYTES / GIB
            extra["complementary_C_Bplus3_4"] = product.binomial(B + 3, 4)
        comparisons.append(
            {
                "B": B,
                "M_k": mk_p,
                "M_pair": mp_p,
                "R_mem_closedform": r_c,
                "R_mem_product": r_p,
                "degree": row["degree"],
                "id": row["id"],
                "m": m,
                "pair_gib": pg,
                "pair_gib_match": g_match,
                "printed_match": r_match,
                "routes_agree": agree,
                **extra,
            }
        )

    if not routes_agree:
        outcome = "O-ARTIFACT"
    elif (not matches_printed) or (not pair_ok):
        outcome = "O-COUNTEREXAMPLE"
    else:
        outcome = "O-IDENTITY"

    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": {"break": False, "exponent_move": False, "ecdlp_solve": False},
        "comparisons": comparisons,
        "experiment_id": EXPERIMENT_ID,
        "freeze_sha256": sha256_bytes(freeze_path.read_bytes()),
        "hypothesis_id": HYPOTHESIS_ID,
        "implementations_agree": routes_agree,
        "matches_printed": matches_printed,
        "n_ge_131_solve": False,
        "outcome": outcome,
        "pair_gib_ok": pair_ok,
        "primary": {
            "R_mem_degree83_m4": next(c["R_mem_product"] for c in comparisons if c["id"] == "n83-m4"),
            "R_mem_degree83_m7": next(c["R_mem_product"] for c in comparisons if c["id"] == "n83-m7"),
            "implementations_agree": routes_agree,
            "outcome": outcome,
        },
        "stage": 1,
        "status": "completed",
        "utc": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                f"approved_by: {APPROVED_BY}",
                "stage: 1",
                f"outcome: {outcome}",
                "amazon_bedrock: NOT SELECTED",
                "status: completed",
                f"implementations_agree: {str(routes_agree).lower()}",
                "",
            ]
        ),
    )
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage not in (0, 1):
        print("only Stages 0 and 1 are authorized", file=sys.stderr)
        return 2
    plan = Path(args.trial_plan)
    if not plan.is_file():
        print(f"missing trial plan: {plan}", file=sys.stderr)
        return 2
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    print(json.dumps({"ok": True, "stage": args.stage, "outcome": raw.get("outcome")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
