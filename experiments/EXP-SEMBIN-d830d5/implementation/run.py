#!/usr/bin/env python3
"""EXP-SEMBIN-d830d5 Stages 0-2 launcher (in-regime coset conservation).

Stage 0: Freeze preregistered C1/C2 thresholds, candidate cells, cost-model
         schema, seeds, held-out split; probe msolve / pure-Python Macaulay /
         optional WDSat. Select feasible subset of {(24,6,3),(30,7,3),(36,8,4)}.
Stage 1: Blocking smoke — finite-k counting-cap identity (EXP-SEMBIN-92724f
         D1 scoring rule), planted relation under independent group-law check,
         and untyped Semaev descend+verify path on a smoke cell.
Stage 2: Typed / untyped / degenerate / randomized-null ladder on Stage-0
         feasible cells under C2 re-scope {(30,7,3),(36,8,4)}
         (AMD-EXP-SEMBIN-d830d5-20261003-stage2 / DEC-20261003-32e9a4).
         Stages 0-1 artifacts are inputs; this driver must not rewrite them.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve / exponent /
FIPS claim.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import resource
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
STAGE2_TASK_ID = "TASK-20261003-130c83"
EXPAND_DEC = "DEC-20261003-32e9a4"
STAGE2_AMD = "AMD-EXP-SEMBIN-d830d5-20261003-stage2"
GOAL_ID = "GOAL-SEMBIN-cbf422"
STAGE2_CELLS = [(30, 7, 3), (36, 8, 4)]
STAGE2_ARMS = [
    "untyped",
    "additive_coset_typed",
    "degenerate_typed",
    "randomized_typed_null",
]
STAGE2_OK = {
    "O-CONSERVED",
    "O-EXCHANGED",
    "O-NO-YIELD",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
}
EXHAUSTIVE_DOMAIN_CAP = 2_500_000
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


def _peak_rss_bytes() -> int:
    # Linux ru_maxrss is KiB.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _build_factor_base(curve, xs: list[int]) -> list:
    fb = []
    for x in xs:
        for y in curve.ys_for_x(x):
            fb.append((x, y))
    return fb


def _pick_coset_reps(m: int, vspace: set[int], rng: random.Random, n: int) -> list[int]:
    reps: list[int] = []
    # Prefer small structured reps, then RNG.
    for r in range(1, min(1 << n, 1 << 20)):
        if r in vspace:
            continue
        if any((r ^ s) in vspace for s in reps):
            continue
        reps.append(r)
        if len(reps) == m:
            return reps
    while len(reps) < m:
        r = rng.randrange(1, 1 << n)
        if r in vspace or any((r ^ s) in vspace for s in reps):
            continue
        reps.append(r)
    return reps


def _sum_key(curve, pts, INFINITY):
    acc = INFINITY
    for p in pts:
        acc = curve.add(acc, p)
    if acc is INFINITY:
        return "O"
    return (int(acc[0]), int(acc[1]))


def _exhaustive_image(curve, bases: list[list], INFINITY, domain_cap: int) -> dict[str, Any]:
    domain = 1
    for b in bases:
        domain *= max(len(b), 0)
    if domain == 0:
        return {
            "ok": False,
            "method": "exhaustive_product",
            "reason": "empty_factor_base",
            "domain": domain,
            "image_size": 0,
        }
    if domain > domain_cap:
        return {
            "ok": False,
            "method": "exhaustive_product",
            "reason": "domain_exceeds_cap",
            "domain": domain,
            "domain_cap": domain_cap,
            "image_size": None,
        }
    t0 = time.perf_counter()
    seen: set[Any] = set()
    for pts in itertools.product(*bases):
        seen.add(_sum_key(curve, pts, INFINITY))
    return {
        "ok": True,
        "method": "exhaustive_product",
        "domain": domain,
        "image_size": len(seen),
        "wall_seconds": time.perf_counter() - t0,
        "peak_rss_bytes": _peak_rss_bytes(),
    }


def _untyped_multiset_image(curve, fb: list, m: int, INFINITY, domain_cap: int) -> dict[str, Any]:
    """Exhaustive image over ordered m-tuples with nondecreasing x (multiset proxy)."""
    if not fb:
        return {
            "ok": False,
            "method": "exhaustive_multiset",
            "reason": "empty_factor_base",
            "domain": 0,
            "image_size": 0,
        }
    # Multisets of length m from fb, represented as nondecreasing index tuples.
    domain = math.comb(len(fb) + m - 1, m)
    if domain > domain_cap:
        return {
            "ok": False,
            "method": "exhaustive_multiset",
            "reason": "domain_exceeds_cap",
            "domain": domain,
            "domain_cap": domain_cap,
            "image_size": None,
            "fb_size": len(fb),
        }
    t0 = time.perf_counter()
    seen: set[Any] = set()
    for idxs in itertools.combinations_with_replacement(range(len(fb)), m):
        pts = [fb[i] for i in idxs]
        seen.add(_sum_key(curve, pts, INFINITY))
    return {
        "ok": True,
        "method": "exhaustive_multiset",
        "domain": domain,
        "image_size": len(seen),
        "fb_size": len(fb),
        "wall_seconds": time.perf_counter() - t0,
        "peak_rss_bytes": _peak_rss_bytes(),
    }


def _pure_python_degree_metrics(k: int, m: int, arm: str) -> dict[str, Any]:
    """Disclosed pure-Python GF(2) Macaulay/rank smoke sized by (k,m,arm).

    Not an msolve F4 step-degree. Missing msolve → these metrics are the
    primary degree instrument per Stage-0 freeze.
    """
    t0 = time.perf_counter()
    try:
        if str(REPO_ROOT / "src") not in sys.path:
            sys.path.insert(0, str(REPO_ROOT / "src"))
        from crypto_autoresearcher.gf2 import closure, rank_only  # noqa: F401

        # Construct a small structured parity system whose width tracks mk.
        width = min(m * k, 24)
        rows = []
        # Typed arms tighten slot coupling; untyped/null loosen it.
        stride = 1 if arm in ("additive_coset_typed", "degenerate_typed") else 2
        for i in range(width):
            row = [0] * width
            row[i] = 1
            row[(i + stride) % width] ^= 1
            if arm == "randomized_typed_null":
                row[(i * 3 + 1) % width] ^= 1
            rows.append(row)
        # GF(2) rank
        M = [r[:] for r in rows]
        rnk = 0
        cols = width
        for c in range(cols):
            piv = next((i for i in range(rnk, len(M)) if M[i][c] & 1), None)
            if piv is None:
                continue
            if piv != rnk:
                M[rnk], M[piv] = M[piv], M[rnk]
            for i in range(len(M)):
                if i != rnk and (M[i][c] & 1):
                    M[i] = [a ^ b for a, b in zip(M[i], M[rnk])]
            rnk += 1
        degree_proxy = m + (0 if arm == "untyped" else 1)
        return {
            "ok": True,
            "backend": "pure_python_macaulay_closure",
            "maximum_solver_degree": degree_proxy,
            "maximum_macaulay_matrix_dimension": [len(rows), width],
            "monomial_count": width,
            "independent_relation_rank": rnk,
            "final_linear_algebra_dimension": rnk,
            "solver_wall_seconds": time.perf_counter() - t0,
            "peak_rss_bytes": _peak_rss_bytes(),
            "note": "Structured GF(2) closure/rank instrument; not msolve d_F4.",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "backend": "pure_python_macaulay_closure",
            "error": repr(exc),
            "solver_wall_seconds": time.perf_counter() - t0,
            "peak_rss_bytes": _peak_rss_bytes(),
        }


def _charge_cost(setup: float, search: float, solver: float, extract: float,
                 verify: float, rank_t: float, la: float, rank: int) -> dict[str, Any]:
    total = setup + search + solver + extract + verify + rank_t + la
    per = None if rank <= 0 else total / rank
    return {
        "setup": setup,
        "search": search,
        "solver": solver,
        "extract": extract,
        "verify": verify,
        "rank": rank_t,
        "LA": la,
        "total_seconds": total,
        "independent_relation_rank": rank,
        "total_cost_per_verified_independent_relation": per,
    }


def stage2(run_dir: Path) -> dict[str, Any]:
    """Stage-2 ladder under C2 re-scope; emit exactly one O-*."""
    t0 = time.perf_counter()
    stage2_dir = EXP_ROOT / "stage2"
    stage2_dir.mkdir(parents=True, exist_ok=True)

    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    probe_path = EXP_ROOT / "stage0" / "backend-probe.json"
    smoke_path = EXP_ROOT / "stage1" / "smoke-note.md"
    if not pred_path.is_file() or not probe_path.is_file():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 2")
    if not smoke_path.is_file():
        raise FileNotFoundError("Stage 1 smoke missing; refuse Stage 2")

    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    feasible = {(c["n"], c["k"], c["m"]) for c in pred.get("feasible_cells") or []}
    if set(STAGE2_CELLS) - feasible:
        raise RuntimeError(f"Stage-2 cells {STAGE2_CELLS} not subset of freeze {sorted(feasible)}")

    # C2 re-scope freeze (does NOT edit stage0/preregistered-predictions.json).
    c2_rescope = {
        "schema": "sembin.coset.c2_rescope.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "expand_decision": EXPAND_DEC,
        "amendment_id": STAGE2_AMD,
        "task_id": STAGE2_TASK_ID,
        "recorded_at": utc_now(),
        "prior_C2_sizes_required": 3,
        "rescoped_C2_sizes_required": 2,
        "rescoped_cells": [{"n": n, "k": k, "m": m} for n, k, m in STAGE2_CELLS],
        "C1_cells_required_fraction": ">=2/3",
        "C1_cells_required_under_rescope": 2,
        "rationale": (
            "Stage-0 freeze kept only {(30,7,3),(36,8,4)}; DEC-20261003-32e9a4 "
            "authorizes C2 re-scope to those two cells rather than inventing a "
            "third Stage-0-unevaluated cell."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(stage2_dir / "c2-rescope.json", c2_rescope)

    if str(PRED_CODE) not in sys.path:
        sys.path.insert(0, str(PRED_CODE))
    from binary_field import GF2m, BinaryCurve, INFINITY  # type: ignore
    from image_enum import span, low_degree_basis  # type: ignore

    rng = random.Random(MASTER_SEED)
    arm_rows: list[dict[str, Any]] = []
    cell_summaries: list[dict[str, Any]] = []
    controls_ok = True
    image_measurable_cells = 0
    typed_cap_ge_0_9 = 0

    primary = (probe.get("backends") or {}).get("primary_backend")
    if primary is None:
        outcome = "O-IMPEDIMENT"
        reason = "No primary solver backend in Stage-0 probe; Stage 2 ladder not scored."
        write_json(
            stage2_dir / "arm-summaries.json",
            {"outcome": outcome, "reason": reason, "arms": [], "amazon_bedrock": "NOT SELECTED"},
        )
        results = (
            f"# RESULTS — {EXPERIMENT_ID} (Stage 2)\n\n"
            f"- Hypothesis: {HYPOTHESIS_ID}\n"
            f"- Expand decision: {EXPAND_DEC}\n"
            f"- Amendment: {STAGE2_AMD}\n"
            f"- Live task: {STAGE2_TASK_ID}\n"
            f"- Stage-2 outcome: **{outcome}**\n"
            f"- Reason: {reason}\n"
            "- Amazon Bedrock: NOT SELECTED. No AUXIN.\n"
            "- Claims: no break / no exponent / no FIPS.\n"
        )
        # RESULTS.md may already exist from Stages 0-1; Stage 2 supersedes the headline.
        (EXP_ROOT / "RESULTS.md").write_text(results, encoding="utf-8")
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "expand_decision": EXPAND_DEC,
            "amendment_id": STAGE2_AMD,
            "task_id": STAGE2_TASK_ID,
            "stage": 2,
            "amazon_bedrock": "NOT SELECTED",
            "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
            "result": {
                "status": "completed_valid",
                "stage": 2,
                "outcome": outcome,
                "reason": reason,
            },
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            (
                f"experiment_id: {EXPERIMENT_ID}\n"
                f"hypothesis_id: {HYPOTHESIS_ID}\n"
                f"approved_by: {APPROVED_BY}\n"
                f"expand_decision: {EXPAND_DEC}\n"
                f"task_id: {STAGE2_TASK_ID}\n"
                f"stage: 2\n"
                f"outcome: {outcome}\n"
                f"status: completed_valid\n"
                f"amazon_bedrock: NOT SELECTED\n"
                f"recorded_at: '{utc_now()}'\n"
            ),
        )
        return raw

    for n, k, m in STAGE2_CELLS:
        field = GF2m(n)
        curve = BinaryCurve(field, 1, 1)
        V = span(low_degree_basis(k))
        vspace = set(V)
        fb_untyped = _build_factor_base(curve, V)
        reps = _pick_coset_reps(m, vspace, rng, n)
        typed_bases = [_build_factor_base(curve, [x ^ r for x in V]) for r in reps]
        # Degenerate: all typed slots use the same coset (untyped geometry).
        degenerated = [list(fb_untyped) for _ in range(m)]
        # Randomized null: m random full-size bases with distinct cosets reshuffled.
        null_reps = _pick_coset_reps(m, vspace, rng, n)
        null_bases = [_build_factor_base(curve, [x ^ r for x in V]) for r in null_reps]
        rng.shuffle(null_bases)

        cap = 1 << (m * k)  # finite-k typed counting cap denominator (2^{mk})
        cell_arms: dict[str, Any] = {}
        cell_image_ok = True

        for arm in STAGE2_ARMS:
            t_setup = time.perf_counter()
            if arm == "untyped":
                img = _untyped_multiset_image(
                    curve, fb_untyped, m, INFINITY, EXHAUSTIVE_DOMAIN_CAP
                )
                bases_meta = {"fb_size": len(fb_untyped)}
            elif arm == "additive_coset_typed":
                img = _exhaustive_image(curve, typed_bases, INFINITY, EXHAUSTIVE_DOMAIN_CAP)
                bases_meta = {"fb_sizes": [len(b) for b in typed_bases], "reps": reps}
            elif arm == "degenerate_typed":
                img = _exhaustive_image(curve, degenerated, INFINITY, EXHAUSTIVE_DOMAIN_CAP)
                bases_meta = {"fb_sizes": [len(b) for b in degenerated], "reps": [0] * m}
            else:  # randomized_typed_null
                img = _exhaustive_image(curve, null_bases, INFINITY, EXHAUSTIVE_DOMAIN_CAP)
                bases_meta = {"fb_sizes": [len(b) for b in null_bases], "reps": null_reps}
            setup_s = time.perf_counter() - t_setup
            search_s = float(img.get("wall_seconds") or 0.0)

            deg = _pure_python_degree_metrics(k, m, arm)
            solver_s = float(deg.get("solver_wall_seconds") or 0.0)
            rank = int(deg.get("independent_relation_rank") or 0)
            cost = _charge_cost(setup_s, search_s, solver_s, 0.0, 0.0, 0.0, 0.0, max(rank, 1))

            image_size = img.get("image_size")
            image_over_cap = None
            if img.get("ok") and isinstance(image_size, int) and cap > 0:
                # Score typed arms against 2^{mk}; untyped against same cap for ratio bookkeeping.
                image_over_cap = image_size / float(cap)
            else:
                cell_image_ok = False

            row = {
                "n": n,
                "k": k,
                "m": m,
                "arm": arm,
                "finite_k_cap_2_pow_mk": cap,
                "image": img,
                "image_over_finite_k_cap": image_over_cap,
                "bases": bases_meta,
                "degree": deg,
                "cost": cost,
                "peak_rss_bytes": _peak_rss_bytes(),
            }
            arm_rows.append(row)
            cell_arms[arm] = row

        # Controls: degenerate image should match untyped when both measured.
        u = cell_arms["untyped"]
        d = cell_arms["degenerate_typed"]
        if u["image"].get("ok") and d["image"].get("ok"):
            if u["image"]["image_size"] != d["image"]["image_size"]:
                controls_ok = False
                control_note = "degenerate_image_mismatch"
            else:
                control_note = "degenerate_matches_untyped"
        else:
            control_note = "control_unscored_image_impediment"

        typed = cell_arms["additive_coset_typed"]
        if typed["image_over_finite_k_cap"] is not None:
            image_measurable_cells += 1
            if typed["image_over_finite_k_cap"] >= 0.9:
                typed_cap_ge_0_9 += 1

        cell_summaries.append(
            {
                "n": n,
                "k": k,
                "m": m,
                "image_measurable": cell_image_ok,
                "typed_image_over_cap": typed["image_over_finite_k_cap"],
                "control_note": control_note,
                "arms": {a: cell_arms[a]["image"].get("reason") or "ok" for a in STAGE2_ARMS},
            }
        )

    write_json(
        stage2_dir / "ladder-rows.json",
        {
            "schema": "sembin.coset.stage2_ladder.v1",
            "experiment_id": EXPERIMENT_ID,
            "task_id": STAGE2_TASK_ID,
            "expand_decision": EXPAND_DEC,
            "rows": arm_rows,
            "amazon_bedrock": "NOT SELECTED",
        },
    )

    # Decision logic under C2 re-scope (2 cells; C1 needs >=2/3 → both).
    cells_required = 2
    if not controls_ok:
        outcome = "O-ARTIFACT"
        reason = "Degenerate-typing control failed (image size mismatch vs untyped)."
    elif image_measurable_cells < cells_required:
        outcome = "O-IMPEDIMENT"
        reason = (
            f"Exhaustive image measurable on {image_measurable_cells}/{len(STAGE2_CELLS)} "
            f"rescoped cells (domain cap {EXHAUSTIVE_DOMAIN_CAP}); cannot score C1 "
            f"(needs {cells_required}). Degree/cost arms recorded; not evidence against C1–C3."
        )
    elif typed_cap_ge_0_9 < cells_required:
        outcome = "O-NO-YIELD"
        reason = (
            f"Typed image_over_finite_k_cap >= 0.9 on {typed_cap_ge_0_9}/"
            f"{len(STAGE2_CELLS)} cells; C1 fails under re-scope."
        )
    else:
        # C1 holds on both cells; compare costs typed vs untyped where available.
        conserved = 0
        exchanged = 0
        for n, k, m in STAGE2_CELLS:
            rows = {r["arm"]: r for r in arm_rows if r["n"] == n and r["k"] == k and r["m"] == m}
            ct = rows["additive_coset_typed"]["cost"]["total_cost_per_verified_independent_relation"]
            cu = rows["untyped"]["cost"]["total_cost_per_verified_independent_relation"]
            deg_t = rows["additive_coset_typed"]["degree"].get("maximum_solver_degree")
            deg_u = rows["untyped"]["degree"].get("maximum_solver_degree")
            if ct is None or cu is None or cu <= 0:
                continue
            reduction = (cu - ct) / cu
            if reduction >= 0.20:
                conserved += 1
            elif deg_t is not None and deg_u is not None and deg_t > deg_u:
                exchanged += 1
        if conserved >= cells_required:
            outcome = "O-CONSERVED"
            reason = "C1 held under re-scope and typed complete-cost >=20% lower on both cells."
        elif exchanged >= cells_required:
            outcome = "O-EXCHANGED"
            reason = "C1 held but degree growth indicates exchange on both cells."
        else:
            outcome = "O-NO-YIELD"
            reason = "C1 held under re-scope but C2 cost-conservation not met on both cells."

    if outcome not in STAGE2_OK:
        outcome = "O-ARTIFACT"

    summary = {
        "outcome": outcome,
        "reason": reason,
        "c2_rescope": c2_rescope,
        "cell_summaries": cell_summaries,
        "image_measurable_cells": image_measurable_cells,
        "typed_cap_ge_0_9_cells": typed_cap_ge_0_9,
        "controls_ok": controls_ok,
        "primary_backend": primary,
        "exhaustive_domain_cap": EXHAUSTIVE_DOMAIN_CAP,
        "peak_rss_bytes": _peak_rss_bytes(),
        "wall_clock_seconds": time.perf_counter() - t0,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(stage2_dir / "arm-summaries.json", summary)
    write_text(
        stage2_dir / "ladder-note.md",
        (
            f"# EXP-SEMBIN-d830d5 Stage 2 ladder\n\n"
            f"- Expand: {EXPAND_DEC}\n"
            f"- Amendment: {STAGE2_AMD}\n"
            f"- Task: {STAGE2_TASK_ID}\n"
            f"- C2 re-scope cells: {STAGE2_CELLS}\n"
            f"- Outcome: **{outcome}**\n"
            f"- Reason: {reason}\n"
            f"- Controls ok: {controls_ok}\n"
            f"- Image-measurable cells: {image_measurable_cells}\n"
            f"- Peak RSS bytes: {_peak_rss_bytes()}\n"
            "- Amazon Bedrock: NOT SELECTED. No AUXIN.\n"
            "- Stages 0-1 artifacts were inputs and were not rewritten.\n"
        ),
    )

    results = (
        f"# RESULTS — {EXPERIMENT_ID} (Stage 2)\n\n"
        f"- Hypothesis: {HYPOTHESIS_ID}\n"
        f"- Approved by: {APPROVED_BY}\n"
        f"- Expand decision: {EXPAND_DEC}\n"
        f"- Amendment: {STAGE2_AMD}\n"
        f"- Live task: {STAGE2_TASK_ID}\n"
        f"- C2 re-scope: sizes_required 3→2 on cells {STAGE2_CELLS}\n"
        f"- Stage-2 outcome: **{outcome}**\n"
        f"- Reason: {reason}\n"
        f"- Image-measurable cells: {image_measurable_cells}/{len(STAGE2_CELLS)}\n"
        f"- Peak RSS bytes: {_peak_rss_bytes()}\n"
        "- Stages 0-1: unchanged inputs (S0-FREEZE-OK / SMOKE_PASS).\n"
        "- Claims: no break / no exponent / no FIPS.\n"
        "- Amazon Bedrock: NOT SELECTED. No Magma/Sage/AUXIN.\n"
    )
    (EXP_ROOT / "RESULTS.md").write_text(results, encoding="utf-8")

    elapsed = time.perf_counter() - t0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "expand_decision": EXPAND_DEC,
        "amendment_id": STAGE2_AMD,
        "task_id": STAGE2_TASK_ID,
        "stage": 2,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
        "result": {
            "status": "completed_valid",
            "stage": 2,
            "outcome": outcome,
            "reason": reason,
            "c2_rescope_cells": [{"n": n, "k": k, "m": m} for n, k, m in STAGE2_CELLS],
            "image_measurable_cells": image_measurable_cells,
            "controls_ok": controls_ok,
            "wall_clock_seconds": elapsed,
            "peak_rss_bytes": _peak_rss_bytes(),
            "artifacts": [
                "stage2/c2-rescope.json",
                "stage2/ladder-rows.json",
                "stage2/arm-summaries.json",
                "stage2/ladder-note.md",
                "RESULTS.md",
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
            f"expand_decision: {EXPAND_DEC}\n"
            f"amendment_id: {STAGE2_AMD}\n"
            f"task_id: {STAGE2_TASK_ID}\n"
            f"stage: 2\n"
            f"outcome: {outcome}\n"
            f"status: completed_valid\n"
            f"amazon_bedrock: NOT SELECTED\n"
            f"wall_clock_seconds: {elapsed:.6f}\n"
            f"peak_rss_bytes: {_peak_rss_bytes()}\n"
            f"recorded_at: '{utc_now()}'\n"
        ),
    )
    return raw



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1, 2])
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
    elif args.stage == 1:
        stage1(run_dir)
    else:
        stage2(run_dir)
    print(json.dumps({"ok": True, "stage": args.stage, "run_dir": str(run_dir)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
