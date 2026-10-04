"""
Subprocess worker for RUN-RELN-141a86-stage0c-minimality: runs
grammar_engine_checkpoint.enumerate_lean_checkpointed for ONE (pack,
target-fingerprint) pair, up to a caller-supplied max_complexity (which for
the minimality search is ALWAYS target_canonical_complexity - 1, never the
target's own canonical complexity -- enforced by the caller, not this
worker, so this file stays a thin, reusable driver). Writes the checkpoint
file continuously (one atomic overwrite per completed level, see
grammar_engine_checkpoint.py) and a final result JSON to --out on every
normal exit path.

Zero changes to the frozen grammar: imports grammar_engine.py and
grammar_engine_lean.py (for its hash helpers) unmodified.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, ".")
import grammar_engine as ge
import grammar_engine_lean as gl
import grammar_engine_checkpoint as gc
import recovery_check as rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--max-complexity", type=int, required=True,
                     help="MUST be target_canonical_complexity - 1 for a minimality search")
    ap.add_argument("--target-expr", required=True)
    ap.add_argument("--target-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--mem-soft-cap-gb", type=float, default=None)
    ap.add_argument("--wall-clock-soft-cap-s", type=float, default=None)
    ap.add_argument("--resume-from-checkpoint", default=None,
                     help="Path to a PRIOR run's checkpoint-<target_id>.json "
                          "(e.g. from an earlier, interrupted attempt on the "
                          "SAME pack/target). Loaded for a level-by-level "
                          "cross-check against the levels this run itself "
                          "reconstructs from scratch (see disclosure below); "
                          "it does NOT skip re-enumerating those levels, "
                          "because enumerate_lean_checkpointed's checkpoint "
                          "format stores only per-level summary counts "
                          "(new_registered, cumulative_registered, timings, "
                          "rss) and never the in-memory by_complexity expr-tree "
                          "dict or the seen_string_hashes/seen_fp_hashes dedup "
                          "sets those counts were derived from. Re-deriving "
                          "those sets from the summary counts alone is not "
                          "possible (the counts are lossy: they do not record "
                          "which fingerprints were seen, only how many). A "
                          "genuine resume would require serializing millions "
                          "of canonical expression trees and two large hash "
                          "sets per checkpoint write, which was judged not "
                          "worth adding given the levels being re-derived here "
                          "cost ~1800s versus the many-hour cost of the level "
                          "this run is actually extending into -- so this run "
                          "restarts enumeration at level 1, checkpoints "
                          "identically, and uses the prior checkpoint only "
                          "as an independent cross-check that the restart "
                          "reproduces the same cumulative_registered counts "
                          "at each previously-completed level.")
    args = ap.parse_args()

    prior_checkpoint_levels = None
    prior_checkpoint_path = None
    if args.resume_from_checkpoint:
        prior_checkpoint_path = args.resume_from_checkpoint
        with open(prior_checkpoint_path) as f:
            prior_checkpoint_levels = json.load(f).get("levels_completed", [])

    target_raw = rc.parse_expr(args.target_expr)
    target_canon = ge.canonicalize(target_raw)
    target_nc = ge.node_count(target_canon)
    leaves = ge.LEAVES_BY_PACK[args.pack]
    target_fp = ge.numeric_fingerprint(target_canon, leaves)
    target_fp_hash = gl._hash_fingerprint(target_fp)

    t0 = time.monotonic()
    result = gc.enumerate_lean_checkpointed(
        pack=args.pack,
        max_complexity=args.max_complexity,
        checkpoint_path=args.checkpoint,
        target_id=args.target_id,
        target_fp_hash=target_fp_hash,
        mem_soft_cap_bytes=(args.mem_soft_cap_gb * (1024 ** 3)) if args.mem_soft_cap_gb else None,
        wall_clock_soft_cap_seconds=args.wall_clock_soft_cap_s,
    )
    t1 = time.monotonic()

    resume_cross_check = None
    if prior_checkpoint_levels is not None:
        by_c_new = {lvl["complexity"]: lvl["cumulative_registered"] for lvl in result["levels"]}
        mismatches = []
        matched = []
        for lvl in prior_checkpoint_levels:
            c = lvl["complexity"]
            prior_cum = lvl["cumulative_registered"]
            new_cum = by_c_new.get(c)
            if new_cum is None:
                mismatches.append({"complexity": c, "reason": "not_reached_this_run", "prior_cumulative_registered": prior_cum})
            elif new_cum != prior_cum:
                mismatches.append({"complexity": c, "prior_cumulative_registered": prior_cum, "this_run_cumulative_registered": new_cum})
            else:
                matched.append(c)
        resume_cross_check = {
            "mode": "restart_from_level_1_with_cross_check",
            "prior_checkpoint_path": prior_checkpoint_path,
            "reason_full_resume_not_used": (
                "checkpoint-<target_id>.json stores only per-level summary "
                "counts, not the by_complexity expr-tree dict or the "
                "seen_string_hashes/seen_fp_hashes dedup sets; those cannot "
                "be reconstructed from counts alone, so this run rebuilds "
                "levels 1..N from scratch and only cross-checks the "
                "resulting counts against the prior partial run's checkpoint"
            ),
            "levels_matched_exactly": matched,
            "levels_mismatched_or_unreached": mismatches,
            "cross_check_passed": len(mismatches) == 0,
        }

    out = {
        "target_id": args.target_id,
        "pack": args.pack,
        "target_expr_string_input": args.target_expr,
        "target_canonical_string": ge.to_canonical_string(target_canon),
        "target_node_count_computed": target_nc,
        "target_fingerprint_hash": target_fp_hash,
        "requested_max_complexity": args.max_complexity,
        "note": "max_complexity here is target_node_count_computed - 1: a MINIMALITY search, "
                "never a blind search to the target's own complexity",
        "resume_cross_check": resume_cross_check,
        "enumeration_result": result,
        "matched_below_target": (
            result["target_found_at_complexity"] is not None
            and result["target_found_at_complexity"] <= args.max_complexity
        ),
        "matched_at_complexity": result["target_found_at_complexity"],
        "worker_wall_clock_seconds": round(t1 - t0, 3),
        "method": "targeted_minimality_blind_hash_deduplicated_enumeration_strictly_below_target",
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"summary": {
        "target_id": args.target_id,
        "matched_below_target": out["matched_below_target"],
        "stopped_reason": result["stopped_reason"],
        "highest_level_completed": result["highest_level_completed"],
        "final_rss_gb": round(result["levels"][-1]["rss_bytes"] / 1e9, 3) if result["levels"] else None,
        "wall_clock_s": out["worker_wall_clock_seconds"],
    }}))


if __name__ == "__main__":
    main()
