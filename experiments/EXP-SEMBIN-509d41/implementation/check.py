#!/usr/bin/env python3
"""Independent checker for EXP-SEMBIN-509d41 Stage 0-2 run artifacts.

Recomputes (2t-3)!! and one sigma_top design figure without importing run.py
stage drivers. Verifies raw-result.json / manifest.yaml agreement. Stage 2
checks shape-binding (balanced = near-worst) and O-IMPEDIMENT discipline.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any, Iterator

EXPERIMENT_ID = "EXP-SEMBIN-509d41"
STAGE0_OK = {"S0-FREEZE-OK"}
STAGE1_OK = {"S1-INVARIANTS-OK", "O-C1-FAIL", "O-ARTIFACT", "O-IMPEDIMENT"}
STAGE2_OK = {
    "O-IMPEDIMENT",
    "O-CLOSURE",
    "O-PROXY-MISLEAD",
    "O-ARTIFACT",
    "O-C1-FAIL",
}
HEUR_OK = {"PREDICTIVE", "INERT", "MISLEADING", "SKIPPED_IMPEDIMENT"}


def double_factorial_odd(m: int) -> int:
    product = 1
    while m >= 1:
        product *= m
        m -= 2
    return product


def all_trees(leaves: frozenset[int]) -> Iterator[Any]:
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


def balanced_mid_split(leaves: list[int]) -> Any:
    if len(leaves) == 1:
        return leaves[0]
    mid = len(leaves) // 2
    return (balanced_mid_split(leaves[:mid]), balanced_mid_split(leaves[mid:]))


def sigma_top(tree: Any, n: int, k: int) -> int:
    total = 0

    def walk(node: Any, is_root: bool) -> None:
        nonlocal total
        if is_leaf(node):
            return
        left, right = node
        a = out_size(left, n, k)
        b = out_size(right, n, k)
        c = 0 if is_root else n
        total += n * (a * b + a * c + b * c + a * b * c)
        walk(left, False)
        walk(right, False)

    walk(tree, True)
    return total


def max_sigma_tree(t: int, n: int, k: int) -> tuple[Any, int]:
    trees = list(all_trees(frozenset(range(t))))
    best = trees[0]
    best_sig = sigma_top(best, n, k)
    for tree in trees[1:]:
        sig = sigma_top(tree, n, k)
        if sig > best_sig:
            best, best_sig = tree, sig
    return best, best_sig


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    errs: list[str] = []
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
    if claims.get("break") or claims.get("exponent_move") or claims.get("attack"):
        errs.append("forbidden break/exponent/attack claim present")

    result = raw.get("result") or {}
    status = result.get("status")
    if status not in ("completed_valid", "failed_infrastructure"):
        errs.append(f"unexpected status {status!r}")
    stage = result.get("stage", raw.get("stage"))
    outcome = result.get("outcome")
    root = Path(__file__).resolve().parents[1]

    # Independent combinatorial pins
    want = {t: double_factorial_odd(2 * t - 3) for t in range(3, 9)}
    if want[3] != 3 or want[8] != 135135:
        errs.append("independent double-factorial pin failed")

    n, t, k = 571, 4, 143
    trees = list(all_trees(frozenset(range(t))))
    if len(trees) != 15:
        errs.append(f"t=4 tree count {len(trees)} != 15")
    path_sig = sigma_top(path_tree(t), n, k)
    min_sig = min(sigma_top(tr, n, k) for tr in trees)
    ratio = min_sig / path_sig
    if abs(ratio - 0.407) > 5e-3:
        errs.append(f"independent min/path at (571,4,143)={ratio} not ~0.407")

    if stage == 0:
        if outcome not in STAGE0_OK:
            errs.append(f"stage0 outcome {outcome!r}")
        missing_freeze = False
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/worksheet-note.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
                missing_freeze = True
        if not missing_freeze:
            pred = json.loads((root / "stage0/preregistered-predictions.json").read_text())
            counts = pred.get("expected_tree_counts_double_factorial") or {}
            got8 = counts.get(8, counts.get("8"))
            if got8 != 135135:
                errs.append("stage0 freeze missing expected count for t=8")
    elif stage == 1:
        if outcome not in STAGE1_OK:
            errs.append(f"stage1 outcome {outcome!r}")
        for rel in (
            "stage1/tree-census.json",
            "stage1/sigma-top-tables.json",
            "stage1/dag-known-false.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing stage1 file {rel}")
    elif stage == 2:
        if outcome not in STAGE2_OK:
            errs.append(f"stage2 outcome {outcome!r}")
        heur = result.get("heur_top_verdict")
        if heur not in HEUR_OK:
            errs.append(f"heur_top_verdict {heur!r}")
        for rel in (
            "stage2/per-instance.jsonl",
            "stage2/arm-summaries.json",
            "stage2/shape-binding.json",
            "stage2/backend-probe.json",
        ):
            if not (root / rel).is_file() or (root / rel).stat().st_size == 0:
                errs.append(f"missing/empty stage2 file {rel}")
        # Independent: balanced arm must match max sigma_top at (16,5,4)
        n2, t2, k2 = 16, 5, 4
        _, max_sig = max_sigma_tree(t2, n2, k2)
        mid_sig = sigma_top(balanced_mid_split(list(range(t2))), n2, k2)
        binding = json.loads((root / "stage2/shape-binding.json").read_text())
        bal = (binding.get("arms") or {}).get("balanced") or {}
        got_sig = bal.get("sigma_top")
        if got_sig != max_sig:
            errs.append(
                f"balanced arm sigma_top {got_sig} != independent max {max_sig}"
            )
        if mid_sig == max_sig:
            errs.append("unexpected: mid-split equals max at t=5 (binding test void)")
        if got_sig == mid_sig:
            errs.append("balanced arm bound to mid-split minimiser; forbidden by DEC-c77494")
        probe = json.loads((root / "stage2/backend-probe.json").read_text())
        if probe.get("amazon_bedrock") not in ("NOT SELECTED", "NOT_USED"):
            errs.append("backend probe Bedrock marker invalid")
        if outcome == "O-IMPEDIMENT" and heur != "SKIPPED_IMPEDIMENT":
            errs.append("O-IMPEDIMENT requires heur_top_verdict=SKIPPED_IMPEDIMENT")
        if result.get("peak_rss_bytes") is None and outcome != "O-IMPEDIMENT":
            errs.append("peak_rss_bytes missing beside Stage-2 timing")
        summaries = json.loads((root / "stage2/arm-summaries.json").read_text())
        if summaries.get("outcome_label") != outcome:
            errs.append("arm-summaries outcome_label mismatch")
    else:
        errs.append(f"unexpected stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print(json.dumps({"ok": True, "stage": stage, "outcome": outcome}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
