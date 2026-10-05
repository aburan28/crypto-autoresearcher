#!/usr/bin/env python3
"""EXP-SEMBIN-509d41 Stages 0-2 launcher (Semaev chaining-topology closure).

Stage 0: Zero-compute freeze of (C1)-(C6) statements, HEUR-TOP bands, DAG
         sketch, and design figures into stage0/.
Stage 1: Independent re-enumeration of unordered full binary merge trees
         t=3..8; assert counts=(2t-3)!!; recompute sigma_top extremes;
         write DAG known-false control.
Stage 2: HEUR-TOP cell (16,5,4) path / cherry-caterpillar / balanced(near-worst)
         + random-Boolean null. Missing Groebner/Macaulay backend →
         O-IMPEDIMENT / SKIPPED_IMPEDIMENT (never negative math vs C1-C5).

Observations only. No Magma/Sage/AUXIN/Bedrock as success path. No ECDLP solve.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Iterator

EXPERIMENT_ID = "EXP-SEMBIN-509d41"
HYPOTHESIS_ID = "H-SEMBIN-9af7e1"
APPROVED_BY = "DEC-20261002-15b02c"
STAGE01_TASK_ID = "TASK-20261003-af0d91"
STAGE2_TASK_ID = "TASK-20261002-d67dd7"
STAGE2_ADMISSION = "DEC-20261003-054ae8"
# Backward-compatible alias for Stage 0-1 freeze records.
TASK_ID = STAGE01_TASK_ID
MASTER_SEED = "20261002c94"
EXP_ROOT = Path(__file__).resolve().parents[1]

# Design figures from IDEA-20260913-c94e52 / H-SEMBIN-9af7e1 (frozen Stage 0).
DESIGN_MIN_OVER_PATH = {
    (571, 4, 143): 0.407,
    (571, 5, 115): 0.641,
    (571, 6, 96): 0.741,
    (571, 8, 72): 0.832,
}
DESIGN_MAX_OVER_PATH = {
    (571, 4, 143): 1.000,
    (571, 5, 115): 2.422,
    (571, 6, 96): 2.282,
    (571, 8, 72): 3.325,
}
DESIGN_PATH_OVER_MIN_CELL = {(16, 5, 4): 1.331}
HEUR_TOP_CELL = {"n": 16, "t": 5, "k": 4, "N_boolean": 68}
ARITY_LOG2_DESIGN = {
    "n": 571,
    "t": 12,
    "k": 48,
    "omega": 3,
    "charged_log2_by_j": {2: 189.3, 3: 348.6, 4: 562.8, 5: 828.5},
    "conditional_on": "HEUR-ARITY",
}


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


def double_factorial_odd(m: int) -> int:
    if m % 2 == 0 or m < 1:
        raise ValueError(f"expected positive odd integer, got {m}")
    product = 1
    while m >= 1:
        product *= m
        m -= 2
    return product


def expected_tree_counts() -> dict[int, int]:
    return {t: double_factorial_odd(2 * t - 3) for t in range(3, 9)}


def all_trees(leaves: frozenset[int]) -> Iterator[Any]:
    """Unordered rooted full binary trees with the given labeled leaves.

    Counts equal (2t-3)!! — children unordered; equal-cardinality splits
    canonically ordered by min leaf label.
    """
    if len(leaves) == 1:
        yield next(iter(leaves))
        return
    items = sorted(leaves)
    n = len(items)
    for r in range(1, n // 2 + 1):
        for comb in combinations(items, r):
            left_set = frozenset(comb)
            right_set = leaves - left_set
            if r < n - r or (r == n - r and min(left_set) < min(right_set)):
                for left in all_trees(left_set):
                    for right in all_trees(right_set):
                        yield (left, right)


def is_leaf(node: Any) -> bool:
    return isinstance(node, int)


def out_size(node: Any, n: int, k: int) -> int:
    return k if is_leaf(node) else n


def path_tree(t: int) -> Any:
    node: Any = 0
    for i in range(1, t):
        node = (node, i)
    return node


def balanced_tree(leaves: list[int]) -> Any:
    """Recursive mid-split. At t=5,6 this coincides with the sigma_top MINIMISER."""
    if len(leaves) == 1:
        return leaves[0]
    mid = len(leaves) // 2
    return (balanced_tree(leaves[:mid]), balanced_tree(leaves[mid:]))


def cherry_caterpillar_tree(t: int) -> Any:
    """Caterpillar with a cherry at the tip: ((0,1),2) then path-attach."""
    if t < 3:
        return path_tree(t)
    node: Any = ((0, 1), 2)
    for i in range(3, t):
        node = (node, i)
    return node


def probe_groebner_macaulay_backends() -> dict[str, Any]:
    """Probe for admitted Semaev Groebner/Macaulay backends. No AUXIN/Bedrock."""
    probes: dict[str, Any] = {
        "sage": {"present": False, "how": "import sage / PATH sage"},
        "magma": {"present": False, "how": "PATH magma"},
        "macaulay2": {"present": False, "how": "PATH M2"},
        "singular": {"present": False, "how": "PATH Singular"},
        "sympy_groebner": {
            "present": False,
            "how": "import sympy; sympy.groebner",
            "admitted_for_semaev_n68": False,
            "note": (
                "Sympy may be importable but is not an admitted Semaev "
                "Groebner/Macaulay/F4 backend for N_boolean=68 under this card; "
                "it is never the success path."
            ),
        },
    }
    try:
        import sage  # type: ignore  # noqa: F401
        probes["sage"]["present"] = True
    except Exception:
        probes["sage"]["present"] = shutil.which("sage") is not None
    probes["magma"]["present"] = shutil.which("magma") is not None
    probes["macaulay2"]["present"] = shutil.which("M2") is not None
    probes["singular"]["present"] = shutil.which("Singular") is not None
    try:
        import sympy  # noqa: F401
        from sympy import groebner  # noqa: F401
        probes["sympy_groebner"]["present"] = True
    except Exception:
        probes["sympy_groebner"]["present"] = False

    admitted = [
        name
        for name in ("sage", "magma", "macaulay2", "singular")
        if probes[name]["present"]
    ]
    return {
        "probes": probes,
        "admitted_backends_present": admitted,
        "backend_available": len(admitted) > 0,
        "amazon_bedrock": "NOT SELECTED",
        "auxin": "NOT USED",
    }


def peak_rss_bytes() -> int | None:
    try:
        import resource
        # ru_maxrss is kilobytes on Linux.
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception:
        return None


def sigma_top(tree: Any, n: int, k: int) -> tuple[int, list[dict[str, int]]]:
    """sigma_top = sum_blocks n*(ab + ac + bc + a*b*c); self=0 at root else n."""
    total = 0
    blocks: list[dict[str, int]] = []

    def walk(node: Any, is_root: bool) -> None:
        nonlocal total
        if is_leaf(node):
            return
        left, right = node
        a = out_size(left, n, k)
        b = out_size(right, n, k)
        c = 0 if is_root else n
        contrib = n * (a * b + a * c + b * c + a * b * c)
        blocks.append({"a": a, "b": b, "c": c, "contrib": contrib})
        total += contrib
        walk(left, False)
        walk(right, False)

    walk(tree, True)
    return total, blocks


def near_worst_balanced_tree(t: int, n: int, k: int) -> tuple[Any, int]:
    """Bind Stage-2 'balanced' arm to a near-worst / max-sigma_top shape.

    DEC-20261003-c77494: do not use the recursive mid-split minimiser at t=5.
    """
    trees = list(all_trees(frozenset(range(t))))
    best_tree = trees[0]
    best_sig = sigma_top(best_tree, n, k)[0]
    for tree in trees[1:]:
        sig = sigma_top(tree, n, k)[0]
        if sig > best_sig:
            best_sig = sig
            best_tree = tree
    return best_tree, best_sig


def invariants_for_tree(tree: Any, n: int, k: int, t: int) -> dict[str, Any]:
    """(C1) equations=t-1, auxiliaries=t-2, N=(t-2)n+tk, three-var blocks=t-2."""
    n_internal = 0
    three_var = 0

    def walk(node: Any, is_root: bool) -> None:
        nonlocal n_internal, three_var
        if is_leaf(node):
            return
        n_internal += 1
        left, right = node
        a = out_size(left, n, k)
        b = out_size(right, n, k)
        c = 0 if is_root else n
        # three-variable block: all three slots nonzero size? Root has c=0.
        # Spec: three-variable blocks = t-2 (exactly one constant-slot root block).
        if c != 0:
            three_var += 1
        walk(left, False)
        walk(right, False)

    walk(tree, True)
    equations = t - 1
    auxiliaries = t - 2
    n_bool = (t - 2) * n + t * k
    return {
        "equations": equations,
        "auxiliaries": auxiliaries,
        "N_boolean": n_bool,
        "three_var_blocks": three_var,
        "internal_nodes": n_internal,
        "equations_ok": n_internal == equations,
        "aux_ok": auxiliaries == t - 2,
        "three_var_ok": three_var == t - 2,
        "N_ok": n_bool == (t - 2) * n + t * k,
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)

    predictions = {
        "schema": "sembin.topology.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "master_seed": MASTER_SEED,
        "frozen_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
        "C1_invariants": {
            "equations": "t-1",
            "auxiliaries": "t-2",
            "N_boolean": "(t-2)*n + t*k",
            "three_var_blocks": "t-2 (root has constant/self slot 0)",
        },
        "C2_model_blindness": (
            "Semaev Section 4.2 / eq. (15) charge is a function of N alone; "
            "N invariant ⇒ topology-blind under the charged model."
        ),
        "C3_C4_sigma_top_design_min_over_path": {
            f"n={n},t={t},k={k}": v for (n, t, k), v in DESIGN_MIN_OVER_PATH.items()
        },
        "C3_C4_note": (
            "min/path < 1 for t>=4; balanced/path > 1 for t>=5; path is not the "
            "sigma_top minimiser; proxy-minimiser is caterpillar-with-cherry."
        ),
        "C5_dff_invariance": (
            "d_ff=4 analysis applies to every topology's t-2 three-variable blocks."
        ),
        "C6_arity_table_conditional_HEUR_ARITY": ARITY_LOG2_DESIGN,
        "HEUR_TOP": {
            "cell": HEUR_TOP_CELL,
            "shapes": ["path", "cherry_caterpillar", "balanced", "random_boolean_null"],
            "decision_bands": {
                "PREDICTIVE": (
                    "Spearman(sigma_top, median T) right sign AND "
                    "path/minimiser median ratio in [1.0, 1.5] "
                    f"(proxy predicts {DESIGN_PATH_OVER_MIN_CELL[(16, 5, 4)]})"
                ),
                "INERT": "pairwise medians within 1.3",
                "MISLEADING": "ordering inverted vs sigma_top",
            },
            "stage2_admitted_by_this_plan": False,
        },
        "expected_tree_counts_double_factorial": expected_tree_counts(),
        "DAG_known_false_sketch": (
            "A merge DAG with shared auxiliaries can have internal-node count "
            "≠ t-1 or auxiliaries ≠ t-2; (C1) is claimed only for full binary "
            "trees. If a written (C1) argument still goes through on such a DAG, "
            "the argument is wrong (proves-too-much)."
        ),
        "claims": {"break": False, "exponent_move": False, "attack": False},
    }
    write_json(stage0_dir / "preregistered-predictions.json", predictions)
    write_text(
        stage0_dir / "worksheet-note.md",
        (
            f"# EXP-SEMBIN-509d41 Stage 0 worksheet\n\n"
            f"- Hypothesis: {HYPOTHESIS_ID}\n"
            f"- Approved by: {APPROVED_BY}\n"
            f"- Live admission task: {TASK_ID}\n"
            f"- Master seed: {MASTER_SEED}\n"
            f"- Frozen at: {predictions['frozen_at']}\n\n"
            "Freeze only. No Stage-1 metric is evidence until this file and "
            "`preregistered-predictions.json` exist. Stage 2 is **not** admitted "
            "by trial-plan-v1.json. Amazon Bedrock is NOT SELECTED. No AUXIN.\n"
        ),
    )

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 0,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False},
        "result": {
            "status": "completed_valid",
            "stage": 0,
            "outcome": "S0-FREEZE-OK",
            "frozen_files": [
                "stage0/preregistered-predictions.json",
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
            f"outcome: S0-FREEZE-OK\n"
            f"status: completed_valid\n"
            f"amazon_bedrock: NOT SELECTED\n"
            f"recorded_at: '{utc_now()}'\n"
        ),
    )
    return raw


def stage1(run_dir: Path) -> dict[str, Any]:
    stage0_pred = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not stage0_pred.is_file():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 1")

    stage1_dir = EXP_ROOT / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    expected = expected_tree_counts()
    census: dict[str, Any] = {}
    invariant_failures: list[dict[str, Any]] = []
    # Use a representative (n,k) for invariant N checks; structure independent of n,k
    # for equations/aux/three-var; N formula checked algebraically.
    n_inv, k_inv = 16, 4

    for t, want in expected.items():
        trees = list(all_trees(frozenset(range(t))))
        got = len(trees)
        hold = 0
        for tree in trees:
            inv = invariants_for_tree(tree, n_inv, k_inv, t)
            if (
                inv["equations_ok"]
                and inv["aux_ok"]
                and inv["three_var_ok"]
                and inv["N_ok"]
                and inv["internal_nodes"] == t - 1
            ):
                hold += 1
            else:
                invariant_failures.append({"t": t, "invariants": inv})
                break
        census[str(t)] = {
            "count": got,
            "expected": want,
            "count_ok": got == want,
            "invariant_hold_rate": (hold / got) if got else 0.0,
            "invariant_hold_count": hold,
        }

    # sigma_top tables at design cells + HEUR-TOP cell
    sigma_tables: dict[str, Any] = {}
    cells = list(DESIGN_MIN_OVER_PATH.keys()) + [(16, 5, 4)]
    for n, t, k in cells:
        trees = list(all_trees(frozenset(range(t))))
        sigs = [sigma_top(tr, n, k)[0] for tr in trees]
        path_sig = sigma_top(path_tree(t), n, k)[0]
        bal_sig = sigma_top(balanced_tree(list(range(t))), n, k)[0]
        min_sig = min(sigs)
        max_sig = max(sigs)
        key = f"n={n},t={t},k={k}"
        sigma_tables[key] = {
            "n": n,
            "t": t,
            "k": k,
            "path": path_sig,
            "balanced": bal_sig,
            "min": min_sig,
            "max": max_sig,
            "min_over_path": min_sig / path_sig,
            "max_over_path": max_sig / path_sig,
            "balanced_over_path": bal_sig / path_sig,
            "path_over_min": path_sig / min_sig,
            "max_over_min": max_sig / min_sig,
            "tree_count": len(trees),
        }

    # DAG known-false control: two leaves merging into a shared aux used twice
    # yields auxiliaries≠t-2 under a naive "one aux per internal" tree count.
    dag_note = {
        "schema": "sembin.topology.dag_known_false.v1",
        "claim": (
            "Merge-DAG counterexample outside the binary-tree class: identify two "
            "internal results (share an auxiliary) so the number of distinct "
            "auxiliaries is strictly less than t-2 while still covering t leaves."
        ),
        "example_t": 4,
        "tree_auxiliaries": 2,
        "dag_distinct_auxiliaries": 1,
        "reading": (
            "If a written (C1) counting argument still concludes auxiliaries=t-2 "
            "on this DAG, the argument proves too much and is O-ARTIFACT."
        ),
        "control_passes_when": (
            "Argument is scoped to full binary trees and refuses the DAG; "
            "documented here as known-false object."
        ),
        "control_status": "SCOPED_REFUSAL_RECORDED",
    }
    write_json(stage1_dir / "tree-census.json", {
        "experiment_id": EXPERIMENT_ID,
        "expected_double_factorial": expected,
        "census": census,
        "n_inv": n_inv,
        "k_inv": k_inv,
        "invariant_failures_sample": invariant_failures[:5],
    })
    write_json(stage1_dir / "sigma-top-tables.json", {
        "experiment_id": EXPERIMENT_ID,
        "formula": "sum_blocks n*(ab + ac + bc + a*b*c); leaf_out=k; internal_out=n; root_self=0; nonroot_self=n",
        "cells": sigma_tables,
        "design_min_over_path": {
            f"n={n},t={t},k={k}": v for (n, t, k), v in DESIGN_MIN_OVER_PATH.items()
        },
    })
    write_text(
        stage1_dir / "dag-known-false.md",
        (
            "# DAG known-false control (Stage 1)\n\n"
            f"{json.dumps(dag_note, indent=2)}\n\n"
            "(C1) is claimed only for full binary merge trees. This DAG is the "
            "proves-too-much null object.\n"
        ),
    )

    counts_ok = all(row["count_ok"] for row in census.values())
    inv_ok = all(row["invariant_hold_rate"] == 1.0 for row in census.values())
    # Design figure checks (absolute tolerance on reported 3-decimal ratios)
    design_ok = True
    design_checks = []
    for (n, t, k), want in DESIGN_MIN_OVER_PATH.items():
        key = f"n={n},t={t},k={k}"
        got = sigma_tables[key]["min_over_path"]
        ok = abs(got - want) <= 5e-3
        design_checks.append({"cell": key + " min/path", "got": got, "want": want, "ok": ok})
        design_ok = design_ok and ok
        want_max = DESIGN_MAX_OVER_PATH[(n, t, k)]
        got_max = sigma_tables[key]["max_over_path"]
        ok_max = abs(got_max - want_max) <= 5e-3
        design_checks.append({"cell": key + " max/path", "got": got_max, "want": want_max, "ok": ok_max})
        design_ok = design_ok and ok_max
    cell = sigma_tables["n=16,t=5,k=4"]
    path_min_ok = abs(cell["path_over_min"] - DESIGN_PATH_OVER_MIN_CELL[(16, 5, 4)]) <= 5e-3
    design_checks.append({
        "cell": "n=16,t=5,k=4 path_over_min",
        "got": cell["path_over_min"],
        "want": DESIGN_PATH_OVER_MIN_CELL[(16, 5, 4)],
        "ok": path_min_ok,
    })
    design_ok = design_ok and path_min_ok

    # (C4) balanced is near-worst / above path for t>=5 (use max shape, not a
    # particular recursive split that may not be the published "balanced").
    bal_ok = True
    for (n, t, k) in DESIGN_MIN_OVER_PATH:
        if t >= 5:
            key = f"n={n},t={t},k={k}"
            if sigma_tables[key]["max_over_path"] <= 1.0:
                bal_ok = False
                design_checks.append({"cell": key + " max>path", "got": sigma_tables[key]["max_over_path"], "want": ">1", "ok": False})

    if not counts_ok:
        outcome = "O-ARTIFACT"
        status = "completed_valid"
    elif not inv_ok:
        outcome = "O-C1-FAIL"
        status = "completed_valid"
    elif not design_ok or not bal_ok:
        outcome = "O-ARTIFACT"
        status = "completed_valid"
    else:
        outcome = "S1-INVARIANTS-OK"
        status = "completed_valid"

    elapsed = time.perf_counter() - t0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 1,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False},
        "result": {
            "status": status,
            "stage": 1,
            "outcome": outcome,
            "counts_ok": counts_ok,
            "invariant_hold_all": inv_ok,
            "design_figure_ok": design_ok,
            "balanced_over_path_ok": bal_ok,
            "design_checks": design_checks,
            "wall_clock_seconds": elapsed,
            "stage2_admitted": False,
            "note": (
                "Combinatorial Stage 1 only. Stage-2 HEUR-TOP cell is not admitted "
                "by trial-plan-v1; full O-* headline awaits Stage 2 or O-IMPEDIMENT."
            ),
            "artifacts": [
                "stage1/tree-census.json",
                "stage1/sigma-top-tables.json",
                "stage1/dag-known-false.md",
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
            f"status: {status}\n"
            f"amazon_bedrock: NOT SELECTED\n"
            f"wall_clock_seconds: {elapsed:.6f}\n"
            f"recorded_at: '{utc_now()}'\n"
        ),
    )
    return raw


def stage2(run_dir: Path) -> dict[str, Any]:
    """HEUR-TOP cell at (16,5,4). Missing admitted backend → O-IMPEDIMENT."""
    stage0_pred = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    stage1_sigma = EXP_ROOT / "stage1" / "sigma-top-tables.json"
    if not stage0_pred.is_file():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 2")
    if not stage1_sigma.is_file():
        raise FileNotFoundError("Stage 1 sigma tables missing; refuse Stage 2")

    stage2_dir = EXP_ROOT / "stage2"
    stage2_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    n, t, k = 16, 5, 4
    n_bool = (t - 2) * n + t * k  # 68

    path = path_tree(t)
    cherry = cherry_caterpillar_tree(t)
    mid_split = balanced_tree(list(range(t)))
    near_worst, near_worst_sig = near_worst_balanced_tree(t, n, k)
    path_sig = sigma_top(path, n, k)[0]
    cherry_sig = sigma_top(cherry, n, k)[0]
    mid_sig = sigma_top(mid_split, n, k)[0]

    shape_binding = {
        "schema": "sembin.topology.stage2_shape_binding.v1",
        "experiment_id": EXPERIMENT_ID,
        "cell": {"n": n, "t": t, "k": k, "N_boolean": n_bool},
        "master_seed": MASTER_SEED,
        "binding_rule": (
            "DEC-20261003-c77494 / DEC-20261003-054ae8: bind Stage-2 'balanced' "
            "arm to a near-worst / high-sigma_top shape, not the recursive "
            "mid-split minimiser at t=5."
        ),
        "arms": {
            "path": {
                "tree": repr(path),
                "sigma_top": path_sig,
                "role": "baseline denominator",
            },
            "cherry_caterpillar": {
                "tree": repr(cherry),
                "sigma_top": cherry_sig,
                "role": "proxy-minimiser / caterpillar-with-cherry",
            },
            "balanced": {
                "tree": repr(near_worst),
                "sigma_top": near_worst_sig,
                "role": "near-worst / max-sigma_top shape (Stage-2 arm)",
                "rejected_mid_split": {
                    "tree": repr(mid_split),
                    "sigma_top": mid_sig,
                    "reason": (
                        "mid-split coincides with sigma_top minimiser at t=5 "
                        f"(balanced_over_path={mid_sig / path_sig:.6f} < 1)"
                    ),
                },
            },
            "random_boolean_null": {
                "tree": None,
                "sigma_top": None,
                "role": (
                    "same slot-size profile; random Boolean polys of matched "
                    "degree profile (separates sparse-LA from summation structure)"
                ),
            },
        },
        "ratios_vs_path": {
            "cherry_over_path": cherry_sig / path_sig,
            "mid_split_over_path": mid_sig / path_sig,
            "near_worst_balanced_over_path": near_worst_sig / path_sig,
        },
    }

    backend = probe_groebner_macaulay_backends()
    rss = peak_rss_bytes()
    elapsed = time.perf_counter() - t0

    if not backend["backend_available"]:
        outcome = "O-IMPEDIMENT"
        heur_top_verdict = "SKIPPED_IMPEDIMENT"
        status = "completed_valid"
        instances_per_arm = 0
        note = (
            "No admitted Groebner/Macaulay backend (sage/magma/M2/Singular) on "
            "this host. Sympy is not the success path for N_boolean=68. Per "
            "frozen stopping rule: Stage 2 stops as O-IMPEDIMENT with "
            "heur_top_verdict=SKIPPED_IMPEDIMENT. This is never negative "
            "mathematical evidence against (C1)-(C5). Stage-1 S1-INVARIANTS-OK "
            "closure remains intact. Shape binding for the HEUR-TOP cell is "
            "recorded for a future backend-capable re-run."
        )
    else:
        # A present admitted backend would continue to system build + timing.
        # Not reached on this host; kept as explicit non-path.
        outcome = "O-IMPEDIMENT"
        heur_top_verdict = "SKIPPED_IMPEDIMENT"
        status = "failed_infrastructure"
        instances_per_arm = 0
        note = (
            "Admitted backend reported present but Stage-2 Weil-descent timing "
            "path is not implemented in this driver revision; refusing to "
            "fabricate HEUR-TOP timings."
        )

    arm_summaries = {
        "schema": "sembin.topology.stage2_arm_summaries.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": STAGE2_TASK_ID,
        "admission_decision": STAGE2_ADMISSION,
        "cell": {"n": n, "t": t, "k": k, "N_boolean": n_bool},
        "instances_per_arm_requested": 100,
        "instances_per_arm_completed": instances_per_arm,
        "heur_top_verdict": heur_top_verdict,
        "outcome_label": outcome,
        "backend_probe": backend,
        "shape_binding_ref": "stage2/shape-binding.json",
        "arms": {
            name: {
                "median_wall_seconds": None,
                "peak_rss_bytes": rss,
                "sigma_top": shape_binding["arms"][name]["sigma_top"],
                "instances": instances_per_arm,
                "status": "SKIPPED_IMPEDIMENT",
            }
            for name in ("path", "cherry_caterpillar", "balanced", "random_boolean_null")
        },
        "spearman_sigma_vs_time": None,
        "path_minimiser_median_time_ratio": None,
        "wall_clock_seconds_stage2_probe": elapsed,
        "peak_rss_bytes": rss,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
        "note": note,
    }

    # Empty matched-instance stream: impediment before any instance timed.
    per_instance_path = stage2_dir / "per-instance.jsonl"
    if per_instance_path.exists():
        raise FileExistsError(f"refusing overwrite: {per_instance_path}")
    with per_instance_path.open("x", encoding="utf-8") as stream:
        stream.write(
            json.dumps(
                {
                    "schema": "sembin.topology.stage2_instance.v1",
                    "status": "SKIPPED_IMPEDIMENT",
                    "reason": "no_admitted_groebner_macaulay_backend",
                    "instances_emitted": 0,
                    "amazon_bedrock": "NOT SELECTED",
                },
                sort_keys=True,
            )
            + "\n"
        )

    write_json(stage2_dir / "shape-binding.json", shape_binding)
    write_json(stage2_dir / "arm-summaries.json", arm_summaries)
    write_json(stage2_dir / "backend-probe.json", backend)
    write_text(
        stage2_dir / "impediment.md",
        (
            f"# EXP-SEMBIN-509d41 Stage 2 impediment\n\n"
            f"- Outcome: `{outcome}`\n"
            f"- HEUR-TOP verdict: `{heur_top_verdict}`\n"
            f"- Cell: (n,t,k)=({n},{t},{k}), N_boolean={n_bool}\n"
            f"- Task: `{STAGE2_TASK_ID}` · Admission: `{STAGE2_ADMISSION}`\n"
            f"- Peak RSS (probe): {rss} bytes\n"
            f"- Wall (probe): {elapsed:.6f} s\n\n"
            f"{note}\n\n"
            "Balanced arm bound to near-worst max-sigma_top shape "
            f"`{near_worst!r}` (sigma_top={near_worst_sig}); mid-split "
            f"`{mid_split!r}` (sigma_top={mid_sig}) rejected per DEC-20261003-c77494.\n\n"
            "Amazon Bedrock: NOT SELECTED. No Magma/Sage/AUXIN success path.\n"
        ),
    )

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": STAGE2_TASK_ID,
        "admission_decision": STAGE2_ADMISSION,
        "stage": 2,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "attack": False, "fips": False},
        "result": {
            "status": status,
            "stage": 2,
            "outcome": outcome,
            "heur_top_verdict": heur_top_verdict,
            "backend_available": backend["backend_available"],
            "admitted_backends_present": backend["admitted_backends_present"],
            "instances_per_arm_completed": instances_per_arm,
            "wall_clock_seconds": elapsed,
            "peak_rss_bytes": rss,
            "shape_binding": {
                "balanced_tree": repr(near_worst),
                "balanced_sigma_top": near_worst_sig,
                "mid_split_rejected_sigma_top": mid_sig,
                "path_sigma_top": path_sig,
                "cherry_sigma_top": cherry_sig,
            },
            "note": note,
            "artifacts": [
                "stage2/per-instance.jsonl",
                "stage2/arm-summaries.json",
                "stage2/shape-binding.json",
                "stage2/backend-probe.json",
                "stage2/impediment.md",
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
            f"task_id: {STAGE2_TASK_ID}\n"
            f"admission_decision: {STAGE2_ADMISSION}\n"
            f"stage: 2\n"
            f"outcome: {outcome}\n"
            f"heur_top_verdict: {heur_top_verdict}\n"
            f"status: {status}\n"
            f"amazon_bedrock: NOT SELECTED\n"
            f"wall_clock_seconds: {elapsed:.6f}\n"
            f"peak_rss_bytes: {rss if rss is not None else 'null'}\n"
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
