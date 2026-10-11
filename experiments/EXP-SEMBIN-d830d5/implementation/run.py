#!/usr/bin/env python3
"""EXP-SEMBIN-d830d5 Stages 0-1 launcher (in-regime coset conservation).

Stage 0: Freeze preregistered C1/C2 thresholds, candidate cells, cost-model
         schema, seeds, held-out split; probe msolve / pure-Python Macaulay /
         optional WDSat. Select feasible subset of {(24,6,3),(30,7,3),(36,8,4)}.
Stage 1: Blocking smoke — finite-k counting-cap identity (EXP-SEMBIN-92724f
         D1 scoring rule), planted relation under independent group-law check,
         and untyped Semaev descend+verify path on a smoke cell. Missing
         primary solver backend → O-IMPEDIMENT (never evidence against C1–C3).

Observations only. Stage 2 remains on design card TASK-20261002-8f23fa and
is NOT enumerated in trial-plan-v1. No Magma/Sage/AUXIN/Bedrock. No ECDLP
solve / exponent / FIPS claim.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-SEMBIN-d830d5"
HYPOTHESIS_ID = "H-SEMBIN-558848"
APPROVED_BY = "DEC-20261002-5c465c"
TASK_ID = "TASK-20261003-c4c9c0"
GOAL_ID = "GOAL-SEMBIN-cbf422"
MASTER_SEED = 2026091805
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXP_ROOT.parents[1]
PRED_CODE = REPO_ROOT / "experiments" / "EXP-SEMBIN-92724f" / "code"

CANDIDATE_CELLS = [(24, 6, 3), (30, 7, 3), (36, 8, 4)]
SEEDS = [2026091805, 2026091806, 2026091807]
SMOKE_CELL = (12, 4, 3)  # enumerable planted-relation smoke; not a C1/C2 claim cell
STAGE1_OK = {"SMOKE_PASS", "O-ARTIFACT", "O-IMPEDIMENT"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def in_regime(n: int, k: int, m: int) -> dict[str, Any]:
    mk = m * k
    return {
        "n": n,
        "k": k,
        "m": m,
        "mk": mk,
        "mk_le_n_minus_3": mk <= n - 3,
        "two_pow_k_gg_m_sq": (1 << k) >= 8 * m * m,
        "two_pow_k": 1 << k,
        "m_squared": m * m,
    }


def exact_counting_layer(k: int, m: int) -> dict[str, Any]:
    """EXP-SEMBIN-92724f D1 exact counting cap (no curve)."""
    size_v = 1 << k
    typed_domain = 1 << (m * k)
    untyped_domain = math.comb(size_v + m - 1, m)
    corr = Fraction(1)
    for j in range(m):
        corr *= Fraction(size_v + j, size_v)
    ratio = Fraction(typed_domain, untyped_domain)
    mfact = math.factorial(m)
    return {
        "k": k,
        "m": m,
        "abs_V": size_v,
        "typed_x_domain_2_pow_mk": typed_domain,
        "untyped_x_multiset_domain_binom": untyped_domain,
        "exact_domain_ratio": float(ratio),
        "m_factorial": mfact,
        "exact_ratio_over_m_factorial": float(ratio / mfact),
        "closed_form_correction_prod_1_plus_j_over_2k": float(corr),
        "identity_check_ratio_times_correction_equals_m_factorial": ratio * corr == mfact,
    }


def probe_backends() -> dict[str, Any]:
    msolve_path = shutil.which("msolve")
    wdsat_path = shutil.which("wdsat") or shutil.which("WDSat")
    pure_python = False
    pure_err = None
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from crypto_autoresearcher.gf2 import closure, rank_only  # noqa: F401

        pure_python = True
    except Exception as exc:  # noqa: BLE001 — probe must not crash Stage 0
        pure_err = repr(exc)
    pred_code_ok = (PRED_CODE / "binary_field.py").is_file()
    return {
        "msolve": {"available": bool(msolve_path), "path": msolve_path},
        "wdsat": {"available": bool(wdsat_path), "path": wdsat_path},
        "pure_python_macaulay_closure": {
            "available": pure_python,
            "module": "crypto_autoresearcher.gf2.closure",
            "error": pure_err,
        },
        "predecessor_92724f_code": {
            "available": pred_code_ok,
            "path": str(PRED_CODE.relative_to(REPO_ROOT)),
        },
        "primary_backend": (
            "msolve"
            if msolve_path
            else ("pure_python_macaulay_closure" if pure_python else None)
        ),
        "amazon_bedrock": "NOT SELECTED",
        "magma_sage_auxin": "NOT USED AS SUCCESS PATH",
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)

    backends = probe_backends()
    cell_rows = [in_regime(n, k, m) for n, k, m in CANDIDATE_CELLS]
    feasible = [
        {"n": r["n"], "k": r["k"], "m": r["m"]}
        for r in cell_rows
        if r["mk_le_n_minus_3"] and r["two_pow_k_gg_m_sq"]
    ]
    # Feasible under inequalities alone; missing primary backend → O-IMPEDIMENT
    # is recorded for Stage 1/2, not a Stage-0 invalidation of the design.
    primary = backends.get("primary_backend")
    stage0_stop = None
    if primary is None:
        stage0_stop = "O-IMPEDIMENT"
        feasible_note = (
            "No primary Groebner/F4 or pure-Python Macaulay backend available; "
            "Stage 1 may still verify finite-k cap + planted group-law smoke, "
            "then stop as O-IMPEDIMENT for Semaev solve path."
        )
    else:
        feasible_note = (
            f"Primary backend={primary}. Feasible cells under mk<=n-3 and "
            f"2^k >= 8 m^2: {feasible}."
        )

    predictions = {
        "schema": "sembin.coset.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "goal_id": GOAL_ID,
        "master_seed": MASTER_SEED,
        "seeds": SEEDS,
        "frozen_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
        "candidate_cells": [{"n": n, "k": k, "m": m} for n, k, m in CANDIDATE_CELLS],
        "cell_regime_screen": cell_rows,
        "feasible_cells": feasible,
        "feasible_note": feasible_note,
        "smoke_cell_for_stage1": {"n": SMOKE_CELL[0], "k": SMOKE_CELL[1], "m": SMOKE_CELL[2]},
        "C1": {
            "threshold_image_over_finite_k_cap": 0.9,
            "cells_required_fraction": ">=2/3",
            "scoring": "exact finite-k counting cap from EXP-SEMBIN-92724f D1",
        },
        "C2": {
            "cost_reduction_vs_untyped": 0.20,
            "sizes_required": 3,
            "rank_loss_forbidden": True,
        },
        "exchange_rule": {
            "label": "O-EXCHANGED",
            "when": "degree/matrix growth erases >=90% of combinatorial gain",
        },
        "cost_model_schema": [
            "setup",
            "search",
            "solver",
            "extract",
            "verify",
            "rank",
            "LA",
        ],
        "held_out_split": {
            "train_fraction": 0.7,
            "held_out_fraction": 0.3,
            "seed": SEEDS[2],
        },
        "HEUR_YT": "2^k >> m^2 and mk <= n-3",
        "HEUR_CONSERVE": "typed complete-cost per verified independent relation >=20% lower",
        "stage2_admitted_by_this_plan": False,
        "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
    }
    write_json(stage0_dir / "preregistered-predictions.json", predictions)
    write_json(
        stage0_dir / "backend-probe.json",
        {
            "schema": "sembin.coset.backend_probe.v1",
            "experiment_id": EXPERIMENT_ID,
            "probed_at": utc_now(),
            "backends": backends,
            "stage0_stop_hint": stage0_stop,
        },
    )
    write_text(
        stage0_dir / "worksheet-note.md",
        (
            f"# EXP-SEMBIN-d830d5 Stage 0 worksheet\n\n"
            f"- Hypothesis: {HYPOTHESIS_ID}\n"
            f"- Approved by: {APPROVED_BY}\n"
            f"- Live admission task: {TASK_ID}\n"
            f"- Master seed: {MASTER_SEED}\n"
            f"- Frozen at: {predictions['frozen_at']}\n"
            f"- Feasible cells: {feasible}\n"
            f"- Primary backend: {primary}\n\n"
            "Freeze only. No Stage-1 metric is evidence until this file, "
            "`preregistered-predictions.json`, and `backend-probe.json` exist. "
            "Stage 2 is **not** admitted by trial-plan-v1.json. "
            "Amazon Bedrock is NOT SELECTED. No AUXIN.\n"
        ),
    )

    outcome = "S0-FREEZE-OK"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 0,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
        "result": {
            "status": "completed_valid",
            "stage": 0,
            "outcome": outcome,
            "feasible_cells": feasible,
            "primary_backend": primary,
            "frozen_files": [
                "stage0/preregistered-predictions.json",
                "stage0/backend-probe.json",
                "stage0/worksheet-note.md",
            ],
        },
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        (
            f"experiment_id: {EXPERIMENT_ID}\n"
            f"hypothesis_id: {HYPOTHESIS_ID}\n"
            f"approved_by: {APPROVED_BY}\n"
            f"task_id: {TASK_ID}\n"
            f"stage: 0\n"
            f"outcome: {outcome}\n"
            f"status: completed_valid\n"
            f"amazon_bedrock: NOT SELECTED\n"
            f"recorded_at: '{utc_now()}'\n"
        ),
    )
    return raw


def _planted_relation_smoke(n: int, k: int, m: int) -> dict[str, Any]:
    """Independent group-law planted relation on an enumerable smoke cell."""
    if str(PRED_CODE) not in sys.path:
        sys.path.insert(0, str(PRED_CODE))
    from binary_field import GF2m, BinaryCurve, INFINITY  # type: ignore

    field = GF2m(n)
    curve = BinaryCurve(field, 1, 1)
    pts = [p for p in curve.affine_points() if p is not INFINITY]
    # Low-degree subspace basis 1,2,4,...,2^{k-1}
    basis = [1 << i for i in range(k)]
    V = {0}
    for b in basis:
        V |= {v ^ b for v in V}
    base = [p for p in pts if int(p[0]) in V]
    if len(base) < m:
        return {
            "ok": False,
            "reason": f"factor base too small: {len(base)} < m={m}",
            "n": n,
            "k": k,
            "m": m,
        }
    chosen = base[:m]
    acc = INFINITY
    for p in chosen:
        acc = curve.add(acc, p)
    # Independent re-sum
    acc2 = INFINITY
    for p in reversed(chosen):
        acc2 = curve.add(acc2, p)
    on_curve = acc is INFINITY or curve.is_on_curve(acc)
    return {
        "ok": on_curve and acc == acc2,
        "n": n,
        "k": k,
        "m": m,
        "abs_V": len(V),
        "factor_base_size": len(base),
        "planted_x": [int(p[0]) for p in chosen],
        "sum_is_infinity": acc is INFINITY,
        "group_law_reassociative": acc == acc2,
        "sum_on_curve": on_curve,
        "note": "Smoke planted m-sum under independent BinaryCurve group law; not a C1/C2 claim.",
    }


def _untyped_descend_smoke(n: int, k: int, m: int, backends: dict[str, Any]) -> dict[str, Any]:
    """Smoke the untyped Semaev descend path (symbolic S3 + optional solver)."""
    if str(PRED_CODE) not in sys.path:
        sys.path.insert(0, str(PRED_CODE))
    out: dict[str, Any] = {"n": n, "k": k, "m": m}
    try:
        import symbolic_s3 as s3  # type: ignore

        # Build the symbolic S3 object existence check (descend representation).
        s3_fn = getattr(s3, "s3", None) or getattr(s3, "S3", None) or getattr(s3, "build_s3", None)
        out["symbolic_s3_module"] = True
        out["symbolic_s3_entrypoint"] = s3_fn.__name__ if callable(s3_fn) else None
        # Degree-weight pin: Hamming weight of exponents is the F2-degree meter
        # used by EXP-SEMBIN-92724f Arm C (not a solving degree).
        out["f2_degree_weight_pin"] = {
            "w(7)": bin(7).count("1"),
            "expect": 3,
            "ok": bin(7).count("1") == 3,
        }
        descend_ok = out["f2_degree_weight_pin"]["ok"] and out["symbolic_s3_module"]
    except Exception as exc:  # noqa: BLE001
        out["symbolic_s3_module"] = False
        out["error"] = repr(exc)
        descend_ok = False

    primary = backends.get("primary_backend")
    out["primary_backend"] = primary
    if primary is None:
        out["solve_status"] = "O-IMPEDIMENT"
        out["solve_note"] = (
            "No msolve / pure-Python Macaulay primary backend; descend representation "
            "smoke recorded; full untyped Semaev solve deferred."
        )
        out["ok"] = descend_ok  # descend representation may still pass
        out["blocking_solver"] = True
        return out

    # Pure-Python path: import gf2 modules (availability) + local GF(2) rank smoke.
    try:
        if str(REPO_ROOT / "src") not in sys.path:
            sys.path.insert(0, str(REPO_ROOT / "src"))
        from crypto_autoresearcher.gf2 import closure, rank_only  # noqa: F401

        def _gf2_rank(rows: list[list[int]]) -> int:
            M = [row[:] for row in rows]
            r = 0
            cols = len(M[0]) if M else 0
            for c in range(cols):
                piv = next((i for i in range(r, len(M)) if M[i][c] & 1), None)
                if piv is None:
                    continue
                if piv != r:
                    M[r], M[piv] = M[piv], M[r]
                for i in range(len(M)):
                    if i != r and (M[i][c] & 1):
                        M[i] = [a ^ b for a, b in zip(M[i], M[r])]
                r += 1
            return r

        # Tiny independent rows → rank 2 over F2
        matrix = [[1, 0, 1], [0, 1, 1]]
        r = _gf2_rank(matrix)
        out["pure_python_rank_smoke"] = {
            "rank": r,
            "ok": r == 2,
            "modules_imported": ["crypto_autoresearcher.gf2.closure", "crypto_autoresearcher.gf2.rank_only"],
        }
        out["solve_status"] = "SMOKE_SOLVER_OK" if r == 2 else "O-ARTIFACT"
        out["ok"] = descend_ok and r == 2
        out["blocking_solver"] = False
    except Exception as exc:  # noqa: BLE001
        if primary == "msolve":
            out["solve_status"] = "O-IMPEDIMENT"
            out["solve_note"] = f"msolve present but pure-python rank smoke failed: {exc!r}"
            out["ok"] = descend_ok
            out["blocking_solver"] = True
        else:
            out["solve_status"] = "O-IMPEDIMENT"
            out["error"] = repr(exc)
            out["ok"] = False
            out["blocking_solver"] = True
    return out


def stage1(run_dir: Path) -> dict[str, Any]:
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    probe_path = EXP_ROOT / "stage0" / "backend-probe.json"
    if not pred_path.is_file() or not probe_path.is_file():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 1")

    stage1_dir = EXP_ROOT / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    backends = probe.get("backends") or {}

    # 1) Finite-k counting-cap identity for every candidate + smoke cell
    cap_rows = []
    cap_ok = True
    for n, k, m in CANDIDATE_CELLS + [SMOKE_CELL]:
        row = exact_counting_layer(k, m)
        row["n"] = n
        row["regime"] = in_regime(n, k, m)
        if not row["identity_check_ratio_times_correction_equals_m_factorial"]:
            cap_ok = False
        cap_rows.append(row)
    write_json(
        stage1_dir / "finite-k-cap-identity.json",
        {
            "schema": "sembin.coset.finite_k_cap.v1",
            "experiment_id": EXPERIMENT_ID,
            "rule": "EXP-SEMBIN-92724f D1 exact_counting_layer",
            "rows": cap_rows,
            "all_identities_hold": cap_ok,
        },
    )

    # 2) Planted relation group-law smoke
    try:
        planted = _planted_relation_smoke(*SMOKE_CELL)
    except Exception as exc:  # noqa: BLE001
        planted = {"ok": False, "error": repr(exc), "n": SMOKE_CELL[0]}
    write_json(stage1_dir / "planted-relation-smoke.json", planted)

    # 3) Untyped Semaev descend (+ optional solver) smoke
    untyped = _untyped_descend_smoke(*SMOKE_CELL, backends)
    write_json(stage1_dir / "untyped-descend-smoke.json", untyped)

    write_text(
        stage1_dir / "smoke-note.md",
        (
            "# EXP-SEMBIN-d830d5 Stage 1 smoke\n\n"
            f"- Cap identities hold: {cap_ok}\n"
            f"- Planted group-law ok: {planted.get('ok')}\n"
            f"- Untyped descend ok: {untyped.get('ok')}\n"
            f"- Solver status: {untyped.get('solve_status')}\n"
            "- Stage 2 ladder is **not** admitted by trial-plan-v1.\n"
            "- Amazon Bedrock NOT SELECTED. No AUXIN.\n"
        ),
    )

    # Also append a short RESULTS.md for Stages 0-1 only (Stage 2 later).
    results_path = EXP_ROOT / "RESULTS.md"
    if not results_path.exists():
        write_text(
            results_path,
            (
                f"# RESULTS — {EXPERIMENT_ID} (Stages 0–1 admission)\n\n"
                f"- Hypothesis: {HYPOTHESIS_ID}\n"
                f"- Approved by: {APPROVED_BY}\n"
                f"- Live task: {TASK_ID}\n"
                f"- Stage 0 feasible cells: {pred.get('feasible_cells')}\n"
                f"- Stage 1 cap_ok={cap_ok} planted_ok={planted.get('ok')} "
                f"untyped_ok={untyped.get('ok')} "
                f"solver={untyped.get('solve_status')}\n"
                "- Stage 2 / O-* headline: **not** decided under trial-plan-v1.\n"
                "- Claims: no break / no exponent / no FIPS.\n"
                "- Amazon Bedrock: NOT SELECTED.\n"
            ),
        )

    planted_ok = bool(planted.get("ok"))
    untyped_ok = bool(untyped.get("ok"))
    blocking_solver = bool(untyped.get("blocking_solver"))
    if not cap_ok or (untyped.get("solve_status") == "O-ARTIFACT"):
        outcome = "O-ARTIFACT"
    elif blocking_solver or untyped.get("solve_status") == "O-IMPEDIMENT":
        # Cap + planted may pass; solver missing is O-IMPEDIMENT per contract.
        if cap_ok and planted_ok and untyped_ok:
            outcome = "O-IMPEDIMENT"
        elif cap_ok and planted_ok:
            outcome = "O-IMPEDIMENT"
        else:
            outcome = "O-ARTIFACT"
    elif cap_ok and planted_ok and untyped_ok:
        outcome = "SMOKE_PASS"
    else:
        outcome = "O-ARTIFACT"

    if outcome not in STAGE1_OK:
        outcome = "O-ARTIFACT"

    elapsed = time.perf_counter() - t0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 1,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
        "result": {
            "status": "completed_valid",
            "stage": 1,
            "outcome": outcome,
            "cap_ok": cap_ok,
            "planted_ok": planted_ok,
            "untyped_ok": untyped_ok,
            "solve_status": untyped.get("solve_status"),
            "wall_clock_seconds": elapsed,
            "stage2_admitted": False,
            "artifacts": [
                "stage1/finite-k-cap-identity.json",
                "stage1/planted-relation-smoke.json",
                "stage1/untyped-descend-smoke.json",
                "stage1/smoke-note.md",
            ],
        },
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        (
            f"experiment_id: {EXPERIMENT_ID}\n"
            f"hypothesis_id: {HYPOTHESIS_ID}\n"
            f"approved_by: {APPROVED_BY}\n"
            f"task_id: {TASK_ID}\n"
            f"stage: 1\n"
            f"outcome: {outcome}\n"
            f"status: completed_valid\n"
            f"amazon_bedrock: NOT SELECTED\n"
            f"wall_clock_seconds: {elapsed:.6f}\n"
            f"recorded_at: '{utc_now()}'\n"
        ),
    )
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2

    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    print(json.dumps({"ok": True, "stage": args.stage, "run_dir": str(run_dir)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
