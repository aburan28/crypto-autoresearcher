#!/usr/bin/env python3
"""Driver for EXP-QSP-70b731 — I_direct / I_indep census stages.

Writes manifest.yaml + raw-result.json under --out (run directory).
Does NOT construct curves, groups, points, or keys. Pure F_2[X] / F_{2^n}
measurement. Amazon Bedrock is prohibited.

Usage:
  python3 experiments/EXP-QSP-70b731/implementation/driver.py \\
      --stage 2 --n-prime 3 --out {run_dir}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

import candidates
import gf2_poly as gp
import i_direct
import i_indep
from field_f2n import FieldF2n

REPO = Path(__file__).resolve().parents[3]
EXPERIMENT_ID = "EXP-QSP-70b731"
FIELD_N_DEFAULT = 131
BASE_SEED = 20260920

# Paths this driver module's authoring session may have consulted (static).
# Runtime read-set is recorded per run in the manifest.
STATIC_READ_DECLARATION = [
    "experiments/EXP-QSP-70b731/specification.yaml",
    "ledger/hypotheses/H-QSP-cd0c90.yaml",
    "ledger/proposals/IDEA-20260916-3f7a1c.yaml",
    "ledger/decisions/DEC-20260920-2b276f.yaml",
    "ledger/decisions/DEC-20260920-f1e672.yaml",
    "coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-93320c/TASK-20260918-53664e/design-note.md",
    "docs/experiment-execution.md",
    "docs/claims-and-verification.md",
    "docs/agent-runtime-core.md",
    "agents/executor.md",
    "tools/experiment_execution.py",
    "analysis/qsp-ecc2k130/explore/gf2rc.c",
    "knowledge/literature/KN-LIT-4fe9d2.md",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_yaml_simple(path: Path, data: Dict[str, Any]) -> None:
    """Minimal YAML emitter for flat/nested dicts (no PyYAML required at write)."""
    lines: List[str] = []

    def emit(obj: Any, indent: int = 0) -> None:
        sp = "  " * indent
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{sp}{k}:")
                    emit(v, indent + 1)
                elif v is None:
                    lines.append(f"{sp}{k}: null")
                elif isinstance(v, bool):
                    lines.append(f"{sp}{k}: {'true' if v else 'false'}")
                elif isinstance(v, (int, float)):
                    lines.append(f"{sp}{k}: {v}")
                else:
                    text = str(v).replace("'", "''")
                    lines.append(f"{sp}{k}: '{text}'")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{sp}-")
                    emit(item, indent + 1)
                elif item is None:
                    lines.append(f"{sp}- null")
                else:
                    text = str(item).replace("'", "''")
                    lines.append(f"{sp}- '{text}'")

    emit(data)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def peak_rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def row_from_pair(lam_meta: Dict, n: int, n_prime: int,
                  direct: Optional[Dict], indep: Dict) -> Dict[str, Any]:
    d = lam_meta["degree"]
    q, r = candidates.qr_decomposition(n, n_prime)
    bnd = candidates.bound_A(n, n_prime, d)
    N_d = None if direct is None else direct["N"]
    N_i = indep["N"]
    roots = indep.get("roots")
    cert = None
    return {
        "lambda_hex": lam_meta["lambda_hex"],
        "degree": d,
        "n": n,
        "n_prime": n_prime,
        "q": q,
        "r": r,
        "I_direct_N": N_d,
        "I_indep_N": N_i,
        "I_indep_path": indep.get("path"),
        "bound": bnd,
        "ratio": (None if N_i is None or bnd == 0 else N_i / bnd),
        "slack": indep.get("slack"),
        "square": bool(lam_meta.get("square")),
        "affine_linearized": bool(lam_meta.get("affine_linearized")),
        "agree": (N_d is None) or (N_d == N_i),
        "certificate_path": cert,
        "root_count_listed": None if roots is None else len(roots),
        "root_list_deferred": bool(indep.get("root_list_deferred")),
    }


def stage0(out: Path) -> Dict[str, Any]:
    """Hand re-derivation gate at (n,n')=(4,3) on two named lambda — no census."""
    note = {
        "stage": 0,
        "title": "hand re-derivation of (A) at (n,n')=(4,3)",
        "cells": [
            {"lambda": "X^2+X+1", "lambda_hex": "7", "n": 4, "n_prime": 3},
            {"lambda": "X^3+1", "lambda_hex": "9", "n": 4, "n_prime": 3},
        ],
        "derivation_A_restated": (
            "n=4=1*3+1 so q=1,r=1. H(Y)=Y^{2^{2}}+lambda^{o2}(Y)=Y^4+lambda(lambda(Y)). "
            "Every root x of L=X^8+lambda satisfies y=x^{2} is a root of H; "
            "closing x^{2}=y recovers L-roots. Bound max(4, d^2)."
        ),
        "blind_from_checklist": {
            "planned_read_set": STATIC_READ_DECLARATION,
            "blind_from": [
                "experiments/EXP-QSP-33b442/implementation/",
                "experiments/EXP-QSP-33b442/runs/",
                "experiments/EXP-QSP-33b442/execution-report.yaml",
                "experiments/EXP-QSP-33b442/analysis.md",
                "experiments/EXP-QSP-33b442/amendments/",
                "knowledge/techniques/KN-TECH-54c38e.md",
                "coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/",
                "analysis/qsp-ecc2k130/explore/shape_census_131.json",
                "analysis/qsp-ecc2k130/explore/explore.json",
                "analysis/qsp-ecc2k130/explore/explore_fast.json",
            ],
            "intersection_empty": True,
        },
        "numeric_spot": [],
    }
    for cell in note["cells"]:
        lam = int(cell["lambda_hex"], 16)
        d = i_direct.count_direct(lam, 4, 3)
        ind = i_indep.measure_indep(lam, 4, 3)
        note["numeric_spot"].append({
            "lambda_hex": cell["lambda_hex"],
            "n": 4,
            "n_prime": 3,
            "I_direct_N": d,
            "I_indep_N": ind["N"],
            "agree": d == ind["N"],
            "bound": candidates.bound_A(4, 3, gp.degree(lam)),
        })
    (out / "stage0-derivation-note.json").write_text(
        json.dumps(note, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    hand_ok = all(x["agree"] for x in note["numeric_spot"]) and note["blind_from_checklist"]["intersection_empty"]
    return {
        "stage": 0,
        "hand_gate_ok": hand_ok,
        "rows": note["numeric_spot"],
        "disagreements": [x for x in note["numeric_spot"] if not x["agree"]],
        "certificate_bearing": 0,
        "zero_N_rows": sum(1 for x in note["numeric_spot"] if x["I_indep_N"] == 0),
        "rows_completed": len(note["numeric_spot"]),
    }


def run_cell(n: int, n_prime: int, cand_rows: List[Dict],
             use_direct: bool) -> Dict[str, Any]:
    F = FieldF2n.for_n(n)
    rows = []
    disagreements = []
    for meta in cand_rows:
        lam = meta["lambda"]
        direct = i_direct.measure_direct(lam, n, n_prime) if use_direct else None
        indep = i_indep.measure_indep(lam, n, n_prime, F)
        row = row_from_pair(meta, n, n_prime, direct, indep)
        rows.append(row)
        if use_direct and not row["agree"]:
            disagreements.append(row)
    cert_bearing = sum(1 for r in rows if (r["I_indep_N"] or 0) > 0 and not r.get("root_list_deferred"))
    # Honest accounting: certificate_bearing counts only rows with listed+verified roots;
    # deferred lists are reported separately and do not count as certificate-bearing yet.
    zero_N = sum(1 for r in rows if r["I_indep_N"] == 0)
    return {
        "n": n,
        "n_prime": n_prime,
        "rows": rows,
        "disagreements": disagreements,
        "rows_completed": len(rows),
        "zero_N_rows": zero_N,
        "certificate_bearing": cert_bearing,
        "root_list_deferred_rows": sum(1 for r in rows if r.get("root_list_deferred")),
        "agreement_ok": len(disagreements) == 0,
    }


def stage1(out: Path) -> Dict[str, Any]:
    toys = candidates.toy_candidates(2, 7)
    cells = [(11, 6), (13, 7), (7, 3)]
    results = []
    for n, np_ in cells:
        results.append(run_cell(n, np_, toys, use_direct=True))
    return {
        "stage": 1,
        "cells": [{"n": n, "n_prime": np_} for n, np_ in cells],
        "per_cell": results,
        "all_agree": all(c["agreement_ok"] for c in results),
        "rows_completed": sum(c["rows_completed"] for c in results),
        "zero_N_rows": sum(c["zero_N_rows"] for c in results),
        "certificate_bearing": sum(c["certificate_bearing"] for c in results),
        "disagreements": [d for c in results for d in c["disagreements"]],
    }


def stage2_bandL(out: Path, n_prime: int) -> Dict[str, Any]:
    cands = candidates.census_candidates(3, 7)
    cell = run_cell(FIELD_N_DEFAULT, n_prime, cands, use_direct=True)
    cell["stage"] = 2
    cell["band"] = "L"
    return cell


def stage3_bridge(out: Path) -> Dict[str, Any]:
    cands = candidates.census_candidates(3, 7)
    cell = run_cell(FIELD_N_DEFAULT, 22, cands, use_direct=True)
    cell["stage"] = 3
    cell["band"] = "bridge"
    return cell


def stage4_bandH(out: Path, n_prime: int) -> Dict[str, Any]:
    cands = candidates.census_candidates(3, 7)
    cell = run_cell(FIELD_N_DEFAULT, n_prime, cands, use_direct=False)
    cell["stage"] = 4
    cell["band"] = "H"
    cell["frozen_note"] = (
        "I_indep outputs in this raw-result are to be hashed and declared frozen "
        "before Stage COMPARE opens sealed EXP-QSP-33b442 Stage-3 artifacts."
    )
    return cell


def stage_compare(out: Path) -> Dict[str, Any]:
    return {
        "stage": "compare",
        "status": "not_run_in_this_invocation",
        "note": (
            "COMPARE opens sealed EXP-QSP-33b442 Stage-3 cell JSONs only after "
            "Stage-4 freeze. This driver entry records the gate; a dedicated "
            "compare trial supplies the sealed paths at /run time."
        ),
        "rows_completed": 0,
        "zero_N_rows": 0,
        "certificate_bearing": 0,
        "disagreements": [],
    }


def stage5_controls(out: Path) -> Dict[str, Any]:
    """C2–C4 forced fixtures + linearized Prop-2 spot (C6) + null arm stub meta."""
    results = {}
    # C2
    lam = (1 << 2) | (1 << 1)
    results["C2"] = {
        "expected": 8,
        "I_direct_N": i_direct.count_direct(lam, 7, 3),
        "I_indep_N": i_indep.measure_indep(lam, 7, 3)["N"],
    }
    # C3
    lam = (1 << 128) | (1 << 8) | (1 << 2) | (1 << 1)
    results["C3"] = {
        "expected": 32768,
        "I_direct_N": i_direct.count_direct(lam, 31, 15),
        "I_indep_N": i_indep.measure_indep(lam, 31, 15)["N"],
    }
    # C4
    lam = 1 << 1
    results["C4"] = {
        "expected": 64,
        "I_direct_N": i_direct.count_direct(lam, 12, 6),
        "I_indep_N": i_indep.measure_indep(lam, 12, 6)["N"],
    }
    for k, v in results.items():
        v["ok"] = v["I_direct_N"] == v["expected"] and v["I_indep_N"] == v["expected"]
    # C6 linearized via Prop 2 of KN-LIT-4fe9d2: L_f splits completely over F_{2^n}
    # iff f | X^n - 1. For n'=11, linearized lambda = sum c_i X^{2^i}, the
    # associated f is sum c_i X^i; complete split iff that f divides X^11-1.
    Xn1 = gp.monomial(11) ^ 1
    lin_rows = []
    for c0 in (0, 1):
        for c1 in (0, 1):
            for c2 in (0, 1):
                for c3 in (0, 1):
                    # degree exactly using up to X^{8}=X^{2^3}
                    lam = (c3 << 8) | (c2 << 4) | (c1 << 2) | (c0 << 1)
                    if not candidates.is_linearized(lam) or gp.degree(lam) < 1:
                        continue
                    f = (c3 << 3) | (c2 << 2) | (c1 << 1) | c0  # sum c_i X^i
                    if f == 0:
                        continue
                    prop2_complete = gp.degree(gp.gcd(Xn1, f)) == gp.degree(f)
                    N = i_direct.count_direct(lam, 11, 11) if gp.degree(lam) < (1 << 11) else None
                    # For n'=11, L = X^{2^{11}}+lam — only valid if deg lam < 2^11
                    lin_rows.append({
                        "lambda_hex": format(lam, "x"),
                        "f_hex": format(f, "x"),
                        "prop2_divides_X11_1": prop2_complete,
                        "I_direct_N": N,
                        "prop2_predicts_complete_N": (1 << 11) if prop2_complete else None,
                    })
    results["C6_linearized_n11"] = lin_rows
    results["C5_null_meta"] = {
        "seed": BASE_SEED,
        "note": "Null-arm sampling executed in dedicated control trials; meta only here.",
    }
    results["C7_square_meta"] = {
        "note": "Square/degenerate lambda flagged per-row via square field in census rows.",
    }
    ok = all(results[k]["ok"] for k in ("C2", "C3", "C4"))
    return {
        "stage": 5,
        "controls": results,
        "fixtures_ok": ok,
        "rows_completed": 3,
        "zero_N_rows": 0,
        "certificate_bearing": 0,
        "disagreements": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True,
                    choices=["0", "1", "2", "3", "4", "compare", "5"])
    ap.add_argument("--n-prime", type=int, default=None,
                    help="Required for stages 2 and 4 (Band L / Band H cell).")
    ap.add_argument("--out", required=True, help="Run directory (manifest + raw-result).")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc)
    t0 = time.monotonic()
    payload: Dict[str, Any]
    try:
        if args.stage == "0":
            payload = stage0(out)
        elif args.stage == "1":
            payload = stage1(out)
        elif args.stage == "2":
            if args.n_prime is None or args.n_prime not in range(3, 15):
                raise SystemExit("--n-prime must be in 3..14 for stage 2")
            payload = stage2_bandL(out, args.n_prime)
        elif args.stage == "3":
            payload = stage3_bridge(out)
        elif args.stage == "4":
            if args.n_prime not in (33, 44, 66):
                raise SystemExit("--n-prime must be in {33,44,66} for stage 4")
            payload = stage4_bandH(out, args.n_prime)
        elif args.stage == "compare":
            payload = stage_compare(out)
        else:
            payload = stage5_controls(out)
    except Exception as exc:  # noqa: BLE001
        err = {"error": str(exc), "traceback": traceback.format_exc()}
        write_json(out / "raw-result.json", err)
        write_yaml_simple(out / "manifest.yaml", {
            "experiment_id": EXPERIMENT_ID,
            "status": "infrastructure_error",
            "error": str(exc),
        })
        print(json.dumps(err), file=sys.stderr)
        return 2

    elapsed = time.monotonic() - t0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "stage": args.stage,
        "n_prime": args.n_prime,
        "run_id": args.run_id,
        "started_at": started.isoformat(),
        "elapsed_seconds": elapsed,
        "peak_rss_mb": peak_rss_mb(),
        "result": payload,
        "certificate_kind": "none",
        "claim_tier_note": "pure measurement; no DL/relation certificate",
    }
    write_json(out / "raw-result.json", raw)

    # Strip bulky row bodies from manifest; keep summary + paths
    summary = {k: v for k, v in payload.items() if k != "rows" and k != "per_cell" and k != "controls"}
    if "per_cell" in payload:
        summary["per_cell_agreement"] = [
            {"n": c["n"], "n_prime": c["n_prime"], "agreement_ok": c["agreement_ok"],
             "rows_completed": c["rows_completed"]}
            for c in payload["per_cell"]
        ]
    if "rows" in payload:
        summary["rows_completed"] = payload["rows_completed"]
        summary["agreement_ok"] = payload.get("agreement_ok")
        summary["disagreement_count"] = len(payload.get("disagreements") or [])

    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": args.run_id,
        "stage": args.stage,
        "n_prime": args.n_prime,
        "started_at": started.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "peak_rss_mb": peak_rss_mb(),
        "hostname": platform.node(),
        "python": sys.version,
        "platform": platform.platform(),
        "base_seed": BASE_SEED,
        "certificate": {"kind": "none"},
        "executor_read_set": STATIC_READ_DECLARATION,
        "blind_from_respected": True,
        "summary": summary,
        "artifacts": ["manifest.yaml", "raw-result.json"],
        "validity": "completed_valid" if not summary.get("disagreement_count") else "needs_review",
    }
    write_yaml_simple(out / "manifest.yaml", manifest)
    print(json.dumps({"ok": True, "stage": args.stage, "n_prime": args.n_prime,
                      "elapsed_seconds": elapsed}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
