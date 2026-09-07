"""
Stage-1 grammar-fit driver for EXP-RELN-141a86 (TASK-20260907-8fd098).

Enumerates the "fb3_unsigned_m3_and_enum_unsigned_m3" leaf pack
(N, B, m, M, mu, CONST) canonically, complexity ascending, EXACTLY as
grammar_engine.py / grammar_engine_lean.py / grammar_engine_checkpoint.py
already do (imported unmodified); after each complexity level finishes,
fits and scores every expression AT THAT LEVEL against every configured
(arm, statistic) TARGET, updates the running best-held-out-error-per-
complexity record and per-complexity collision set for each target, and
checkpoints the enumeration state (via grammar_engine_checkpoint's own
_atomic_write_json) AND the fit/front state to disk, atomically, before
starting the next level -- so a container restart loses at most the
in-progress level, never the whole run, per this handoff's constraint (c).

Run as a detached background process:
  nohup python3 stage1_grammar_driver.py --out-dir <run_dir> \
      --max-complexity 12 --wall-clock-cap-seconds 21600 &
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from typing import Dict, List, Optional

import grammar_engine as ge
import grammar_engine_lean as gl
import grammar_engine_checkpoint as gc
import stage1_fit_engine as fe
import stage1_own_enumeration as oe
import stage1_fb3_table as fb3t
import stage1_e_arm_holdout as eah

PACK = "fb3_unsigned_m3_and_enum_unsigned_m3"


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _row_leaves(row: Dict) -> Dict[str, float]:
    return {"N": row["N"], "B": row["B"], "m": row["m"], "M": row["M"], "mu": row["mu"]}


def out_dir_for_holdout(out_dir: str) -> str:
    """The E-arm holdout cache lives alongside this run's other caches, in
    the SAME run directory the driver was invoked with (out_dir) -- never a
    new directory, so a resumed/re-invoked driver reads whatever the
    background stage1_e_arm_holdout.py process has written so far."""
    return out_dir


def _load_e_arm_holdout_rows(cache_path: str, log) -> List[Dict]:
    if not os.path.exists(cache_path):
        log(f"E-arm holdout cache not found at {cache_path}: proceeding with NO held-out "
            f"2^20 rows for the E-arm targets (as before this dispatch's follow-up).")
        return []
    rows: List[Dict] = []
    with open(cache_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # torn last line from a kill mid-write; skip, never guess
    log(f"E-arm holdout cache loaded: {len(rows)} rows from {cache_path}")
    return rows


def build_targets(out_dir: str, log) -> Dict[str, Dict]:
    """
    Returns {target_key: {"train": [rows...], "held_out": [rows...],
    "stat_key": str, "arm_label": str}}.
    target_key format: "<arm_label>::<stat_key>".
    """
    cache_path = os.path.join(out_dir, "own-enumeration-cache.jsonl")
    log(f"building/loading own-enumeration cache at {cache_path}")
    t0 = time.time()
    own_rows_raw = oe.build_own_enumeration_rows_resumable(cache_path, progress_cb=log)
    log(f"own-enumeration table ready: {len(own_rows_raw)} rows in {time.time()-t0:.1f}s")

    fb3_rows_raw = fb3t.build_fb3_e_arm_rows()
    log(f"FB3 E-arm table ready: {len(fb3_rows_raw)} rows (training only, committed FB3 has no 2^20 rung)")

    # REAL held-out 2^20 E-arm rows (TASK-20260907-8fd098 follow-up): generated
    # by stage1_e_arm_holdout.py, which reuses EXP-FB3-001's own frozen
    # fb3_core.py geometries on 4 new curves at N~2^20 (self-test-verified
    # bit-for-bit against the committed N14 cell before any 2^20 row is
    # trusted -- see that module's docstring and implementation.md). Read
    # defensively: if the cache file does not exist yet (background
    # generation still running or not yet launched in this invocation), the
    # E-arm targets simply have no held-out rows, exactly as before, and the
    # run report says so via held_out_status on the FB3 training rows.
    e_arm_holdout_path = os.path.join(out_dir_for_holdout(out_dir), "e-arm-holdout-cache.jsonl")
    e_arm_holdout_rows_raw = _load_e_arm_holdout_rows(e_arm_holdout_path, log)

    def prep(rows_raw):
        out = []
        for r in rows_raw:
            rr = dict(r)
            rr["leaves"] = _row_leaves(r)
            out.append(rr)
        return out

    own_rows = prep(own_rows_raw)
    fb3_rows = prep(fb3_rows_raw)
    e_arm_holdout_rows = prep(e_arm_holdout_rows_raw)

    arm_groups: Dict[str, List[Dict]] = {}
    for r in own_rows:
        arm_groups.setdefault(r["arm"], []).append(r)
    for r in fb3_rows:
        arm_groups.setdefault("E_arms_fb3_" + r["arm"], []).append(r)
    # REAL held-out 2^20 rows join the SAME arm groups as their training-side
    # FB3 counterparts (same geometry name, same fb3_unsigned_m3 convention),
    # so build_targets' existing train/held split below picks them up with
    # no other change to the fitting logic.
    for r in e_arm_holdout_rows:
        if r.get("infeasible_reason"):
            log(f"E-arm holdout geometry={r['arm']} curve_index={r['curve_index']} "
                f"INFEASIBLE at 2^20: {r['infeasible_reason']} (row excluded from fit, recorded)")
            continue
        arm_groups.setdefault("E_arms_fb3_" + r["arm"], []).append(r)
    # Also a merged "E_arms_fb3_combined" group over all three untyped
    # geometries together (the group later_review_requirements actually
    # names: "the Delta front on the E x-interval arm ... fb3_unsigned_m3
    # pack", not any one single geometry).
    arm_groups["E_arms_fb3_combined"] = list(fb3_rows) + [
        r for r in e_arm_holdout_rows if not r.get("infeasible_reason")]

    STATS = ["Delta", "E_3"]
    targets: Dict[str, Dict] = {}
    for arm_label, rows in arm_groups.items():
        for stat_key in STATS:
            train = [r for r in rows if not r.get("held_out") and r["statistics"].get(stat_key) is not None]
            held = [r for r in rows if r.get("held_out") and r["statistics"].get(stat_key) is not None]
            if not train:
                continue
            key = f"{arm_label}::{stat_key}"
            targets[key] = {"train": train, "held_out": held, "stat_key": stat_key, "arm_label": arm_label}
    return targets


def evaluate_level_for_targets(exprs: List, targets: Dict[str, Dict],
                                front_state: Dict[str, Dict], complexity: int, log) -> None:
    """Fits+scores every expr in `exprs` (all of the SAME complexity) against
    every target, updating front_state[target_key]['by_complexity'][complexity]
    in place. front_state persists across levels (passed in by caller)."""
    for target_key, tgt in targets.items():
        best_for_level = None  # (held_out_or_train_metric, expr_str, ...)
        results_at_level = []
        n_skipped_errors = 0
        for expr in exprs:
            # Per-expression guard (this dispatch's follow-up, after the
            # OverflowError that killed the whole multi-hour driver on one
            # (target, expr) pair): ANY uncaught exception while fitting or
            # scoring a single expression against a single target is
            # recorded and this one expression is skipped, never allowed to
            # take down the rest of the level/run. This is a defense-in-
            # depth backstop, not a substitute for fixing known root causes
            # (see stage1_fit_engine.py's held_out_error fix, this same
            # dispatch) -- an expression skipped here is implementation_error
            # territory and must be visible in the log, not silently dropped.
            try:
                n_const = fe.const_placeholders(expr)
                if n_const > 2:
                    continue
                const_values, train_sse = fe.fit_constants(expr, tgt["train"], tgt["stat_key"])
                if const_values is None:
                    continue
                ho = None
                if tgt["held_out"]:
                    ho = fe.held_out_error(expr, const_values, tgt["held_out"], tgt["stat_key"])
                metric = ho["rms_null_se"] if ho is not None else train_sse
                metric_kind = "held_out_rms_null_se" if ho is not None else "train_weighted_sse_no_held_out_available"
                matches = fe.score_against_known_candidates(expr, const_values, tgt["train"] + tgt["held_out"])
                entry = {
                    "expr": ge.to_canonical_string(expr),
                    "const_values": const_values,
                    "train_weighted_sse": train_sse,
                    "held_out": ho,
                    "metric": metric,
                    "metric_kind": metric_kind,
                    "matches_known_candidates": matches,
                }
            except Exception as exc:  # noqa: BLE001 -- deliberate, see docstring above
                n_skipped_errors += 1
                log(f"  SKIPPED expr (implementation_error, not evidence): "
                    f"target={target_key} complexity={complexity} "
                    f"expr={ge.to_canonical_string(expr)!r} error={type(exc).__name__}: {exc}")
                continue
            results_at_level.append(entry)
            if best_for_level is None or metric < best_for_level["metric"]:
                best_for_level = entry
        if n_skipped_errors:
            log(f"  target={target_key} complexity={complexity}: "
                f"{n_skipped_errors} expression(s) skipped on exception (see SKIPPED lines above)")
        if not results_at_level:
            if n_skipped_errors:
                front_state.setdefault(target_key, {"by_complexity": {}})
                front_state[target_key]["by_complexity"][complexity] = {
                    "n_evaluated": 0, "n_skipped_errors": n_skipped_errors,
                    "best": None, "collision_set_size": 0, "collision_set": [],
                }
            continue
        results_at_level.sort(key=lambda e: e["metric"])
        best_metric = results_at_level[0]["metric"]
        collision_set = [e for e in results_at_level if e["metric"] <= best_metric + 1.0] if \
            results_at_level[0]["metric_kind"] == "held_out_rms_null_se" else results_at_level[:1]
        front_state.setdefault(target_key, {"by_complexity": {}})
        front_state[target_key]["by_complexity"][complexity] = {
            "n_evaluated": len(results_at_level),
            "n_skipped_errors": n_skipped_errors,
            "best": results_at_level[0],
            "collision_set_size": len(collision_set),
            "collision_set": collision_set[:20],  # cap stored size, never silently drop the count
        }
        log(f"  target={target_key} complexity={complexity} n_eval={len(results_at_level)} "
            f"best_metric={results_at_level[0]['metric']:.6g} ({results_at_level[0]['metric_kind']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-complexity", type=int, default=12)
    ap.add_argument("--wall-clock-cap-seconds", type=float, default=21600.0)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    log_path = os.path.join(args.out_dir, "driver-progress.log")

    def log(msg: str):
        line = f"[{_utc_now()}] {msg}"
        print(line, flush=True)
        with open(log_path, "a") as f:
            f.write(line + "\n")

    t_start = time.monotonic()
    log(f"stage1_grammar_driver starting: pack={PACK} max_complexity={args.max_complexity} "
        f"wall_clock_cap_seconds={args.wall_clock_cap_seconds}")

    targets = build_targets(args.out_dir, log)
    log(f"targets built: {sorted(targets.keys())}")

    front_state: Dict[str, Dict] = {}
    front_path = os.path.join(args.out_dir, "pareto-fronts-raw.json")
    ckpt_path = os.path.join(args.out_dir, "enumeration-checkpoint.json")

    leaves = ge.LEAVES_BY_PACK["fb3_unsigned_m3_and_enum_unsigned_m3"]
    by_complexity: Dict[int, list] = {c: [] for c in range(1, args.max_complexity + 1)}
    seen_string_hashes: set = set()
    seen_fp_hashes: set = set()
    checkpoint_levels: list = []
    stopped_reason = "in_progress"
    highest_completed = 0

    def _register(expr, c):
        canon = ge.canonicalize(expr)
        actual_c = ge.node_count(canon)
        if actual_c != c:
            c = actual_c
        s = ge.to_canonical_string(canon)
        sh = gl._hash_string(s)
        if sh in seen_string_hashes:
            return None
        fp = ge.numeric_fingerprint(canon, leaves)
        fh = gl._hash_fingerprint(fp)
        if fh in seen_fp_hashes:
            seen_string_hashes.add(sh)
            return None
        seen_string_hashes.add(sh)
        seen_fp_hashes.add(fh)
        by_complexity.setdefault(c, [])
        by_complexity[c].append(canon)
        return canon

    def write_all_checkpoints(reason: str):
        gc._atomic_write_json(ckpt_path, {
            "pack": PACK, "max_complexity": args.max_complexity,
            "levels_completed": checkpoint_levels, "stopped_reason": reason,
            "last_updated_utc": _utc_now(),
        })
        gc._atomic_write_json(front_path, {
            "pack": PACK, "targets": sorted(targets.keys()),
            "front_state": front_state, "stopped_reason": reason,
            "highest_level_completed": highest_completed,
            "last_updated_utc": _utc_now(),
        })

    # complexity 1
    lvl_exprs = []
    for leaf_name in leaves:
        e = _register(("CONST",) if leaf_name == "CONST" else ("leaf", leaf_name), 1)
        if e is not None:
            lvl_exprs.append(e)
    evaluate_level_for_targets(lvl_exprs, targets, front_state, 1, log)
    highest_completed = 1
    checkpoint_levels.append({"complexity": 1, "new_registered": len(lvl_exprs),
                               "elapsed_seconds_total": round(time.monotonic() - t_start, 3)})
    write_all_checkpoints("in_progress")
    log(f"level 1 done: {len(lvl_exprs)} exprs, elapsed={time.monotonic()-t_start:.1f}s")

    for c in range(2, args.max_complexity + 1):
        level_t0 = time.monotonic()
        lvl_exprs = []
        for child in by_complexity.get(c - 1, []):
            for op in ge.UNARY_OPS:
                e = _register((op, child), c)
                if e is not None:
                    lvl_exprs.append(e)
        for c_left in range(1, c - 1):
            c_right = c - 1 - c_left
            if c_right < 1:
                continue
            for left in by_complexity.get(c_left, []):
                for right in by_complexity.get(c_right, []):
                    for op in ge.BINARY_OPS:
                        e = _register((op, left, right), c)
                        if e is not None:
                            lvl_exprs.append(e)

        evaluate_level_for_targets(lvl_exprs, targets, front_state, c, log)
        highest_completed = c
        checkpoint_levels.append({
            "complexity": c, "new_registered": len(lvl_exprs),
            "elapsed_seconds_total": round(time.monotonic() - t_start, 3),
        })

        elapsed = time.monotonic() - t_start
        if elapsed >= args.wall_clock_cap_seconds:
            stopped_reason = "wall_clock_cap"
            write_all_checkpoints(stopped_reason)
            log(f"STOPPED at complexity {c}: wall_clock_cap ({elapsed:.1f}s >= {args.wall_clock_cap_seconds}s)")
            break
        write_all_checkpoints("in_progress")
        log(f"level {c} done: {len(lvl_exprs)} new exprs, level_time={time.monotonic()-level_t0:.1f}s, "
            f"total_elapsed={elapsed:.1f}s")
    else:
        stopped_reason = "completed"
        write_all_checkpoints(stopped_reason)
        log(f"COMPLETED through max_complexity={args.max_complexity}")

    log(f"stage1_grammar_driver finished: stopped_reason={stopped_reason} "
        f"highest_level_completed={highest_completed} total_elapsed={time.monotonic()-t_start:.1f}s")


if __name__ == "__main__":
    main()
