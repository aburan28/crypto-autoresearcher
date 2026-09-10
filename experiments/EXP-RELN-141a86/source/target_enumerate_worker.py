"""
Subprocess worker for RUN-RELN-141a86-stage0c-repair: enumerates ONE
(pack, target expression) pair using grammar_engine_lean.enumerate_lean
(hash-deduplicated, streaming, level-by-level, with an INTERNAL soft memory
cap and early-exit the moment the target's fingerprint is found), and
writes a JSON result to --out on every exit path (normal completion, target
found early, or internal soft-cap stop). Designed to be launched as a real
background OS process by run_stage0c_repair_monitor.py, which polls this
process's own /proc/<pid>/status externally and can SIGTERM/SIGKILL it as
an outer safety net independent of the internal cap.

This performs ZERO changes to the frozen grammar: it imports
grammar_engine.py and grammar_engine_lean.py unmodified in their operator
sets, leaf sets, node-counting rule and C_max; it only calls them with a
target-specific max_complexity (the target's own canonical node count,
never above it) and a hash-based dedup strategy.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, ".")
import grammar_engine as ge
import grammar_engine_lean as gl
import recovery_check as rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--max-complexity", type=int, required=True)
    ap.add_argument("--target-expr", required=True,
                     help="grammar_expr notation string, e.g. 'div(binomial(...),N)'")
    ap.add_argument("--target-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mem-soft-cap-gb", type=float, default=None)
    ap.add_argument("--wall-clock-soft-cap-s", type=float, default=None)
    ap.add_argument("--extra-leaves-json", default=None,
                     help='JSON dict {pack: [leaf,...]} for packs not in grammar_engine.LEAVES_BY_PACK')
    args = ap.parse_args()

    extra_leaves = json.loads(args.extra_leaves_json) if args.extra_leaves_json else None
    if extra_leaves:
        for pack, leafnames in extra_leaves.items():
            ge.LEAVES_BY_PACK.setdefault(pack, leafnames)

    target_raw = rc.parse_expr(args.target_expr)
    target_canon = ge.canonicalize(target_raw)
    target_nc = ge.node_count(target_canon)
    leaves = ge.LEAVES_BY_PACK[args.pack]
    target_fp = ge.numeric_fingerprint(target_canon, leaves)
    target_fp_hash = gl._hash_fingerprint(target_fp)
    target_string_hash = gl._hash_string(ge.to_canonical_string(target_canon))

    t0 = time.monotonic()
    result = gl.enumerate_lean(
        pack=args.pack,
        max_complexity=args.max_complexity,
        target_fp_hash=target_fp_hash,
        mem_soft_cap_bytes=(args.mem_soft_cap_gb * (1024 ** 3)) if args.mem_soft_cap_gb else None,
        wall_clock_soft_cap_seconds=args.wall_clock_soft_cap_s,
        extra_leaves=extra_leaves,
    )
    t1 = time.monotonic()

    out = {
        "target_id": args.target_id,
        "pack": args.pack,
        "target_expr_string_input": args.target_expr,
        "target_canonical_string": ge.to_canonical_string(target_canon),
        "target_node_count_computed": target_nc,
        "target_fingerprint_hash": target_fp_hash,
        "requested_max_complexity": args.max_complexity,
        "enumeration_result": result,
        "recovered": (
            result["target_found_at_complexity"] is not None
            and result["target_found_at_complexity"] <= args.max_complexity
        ),
        "recovered_at_complexity": result["target_found_at_complexity"],
        "worker_wall_clock_seconds": round(t1 - t0, 3),
        "method": "blind_hash_deduplicated_bottom_up_enumeration",
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"summary": {
        "target_id": args.target_id, "recovered": out["recovered"],
        "stopped_reason": result["stopped_reason"],
        "highest_level_completed": result["highest_level_completed"],
        "final_rss_gb": round(result["levels"][-1]["rss_bytes"] / 1e9, 3) if result["levels"] else None,
        "wall_clock_s": out["worker_wall_clock_seconds"],
    }}))


if __name__ == "__main__":
    main()
