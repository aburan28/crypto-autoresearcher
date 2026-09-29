"""
Checkpointed variant of grammar_engine_lean.enumerate_lean, built for
RUN-RELN-141a86-stage0c-minimality (TASK-20260907-6333af / DEC-20260907-2a3727).

This module changes ONLY the I/O behaviour of the enumeration loop: it
duplicates grammar_engine_lean.enumerate_lean's bottom-up, hash-deduplicated
enumeration algorithm verbatim (same _register logic, same
canonicalize/node_count/numeric_fingerprint calls into grammar_engine.py,
same early-exit-on-target-fingerprint semantics, same memory/wall-clock soft
caps) and adds exactly one new behaviour: after EVERY complexity level
finishes building (i.e. is fully, exhaustively populated), the level's
result record is written to disk IMMEDIATELY, durably, via a
write-to-temp-file-then-atomic-rename so a concurrent reader (or a process
that inspects the file after this process is killed) never observes a
partially-written file.

No new leaf, operator, node-counting or dedup-semantics behaviour is
introduced; grammar_engine.py and grammar_engine_lean.py are imported
unchanged and not modified by this file.

Checkpoint file format (one file per run, overwritten atomically after each
level -- NOT one file per level, so a reader always finds the single latest
complete state under one fixed path):
{
  "pack": ..., "target_id": ..., "max_complexity": ...,
  "levels_completed": [ {level, form_count_cumulative, form_count_new,
                          target_found, elapsed_seconds_total, rss_bytes,
                          timestamp_utc}, ... ],
  "stopped_reason": "in_progress" | "completed" | "target_found_early" |
                     "memory_cap" | "wall_clock_cap",
  "target_found_at_complexity": int | null,
  "last_updated_utc": ...
}
"""
from __future__ import annotations

import datetime
import json
import os
import time
from typing import Dict, List, Optional, Tuple

import grammar_engine as ge

Expr = ge.Expr


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _atomic_write_json(path: str, obj: Dict) -> None:
    """Write JSON to `path` durably: write to a sibling temp file, fsync it,
    then os.replace() (atomic on POSIX for same-filesystem renames) onto the
    final path, then fsync the containing directory so the rename itself is
    durable across a hard kill of THIS process (a SIGKILL cannot leave the
    target path holding a half-written file, and cannot leave the directory
    entry pointing at a temp file that then vanishes, because both the file
    write and the rename are complete, fsynced operations before this
    function returns control to the caller)."""
    d = os.path.dirname(os.path.abspath(path)) or "."
    tmp_path = path + f".tmp-{os.getpid()}"
    with open(tmp_path, "w") as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    try:
        dir_fd = os.open(d, os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        # Directory fsync is a best-effort durability strengthening; the
        # file-level fsync + os.replace above already guarantees no
        # half-written or missing file is observable even if this step is
        # unavailable on some platform/filesystem.
        pass


def enumerate_lean_checkpointed(
    pack: str,
    max_complexity: int,
    checkpoint_path: str,
    target_id: str = "",
    target_fp_hash: Optional[int] = None,
    mem_soft_cap_bytes: Optional[int] = None,
    wall_clock_soft_cap_seconds: Optional[float] = None,
    extra_leaves: Optional[Dict[str, list]] = None,
) -> Dict:
    """
    Same algorithm and return value shape as grammar_engine_lean.enumerate_lean,
    plus: after every complexity level completes, atomically overwrites
    `checkpoint_path` with the cumulative levels-completed record so far.
    """
    if pack in ge.LEAVES_BY_PACK:
        leaves = ge.LEAVES_BY_PACK[pack]
    elif extra_leaves and pack in extra_leaves:
        leaves = extra_leaves[pack]
        ge.LEAVES_BY_PACK.setdefault(pack, leaves)
    else:
        raise ValueError(f"unknown leaf pack: {pack!r}")

    t_start = time.monotonic()
    by_complexity: Dict[int, List[Expr]] = {c: [] for c in range(1, max_complexity + 1)}
    seen_string_hashes: set = set()
    seen_fp_hashes: set = set()
    level_report: List[Dict] = []
    checkpoint_levels: List[Dict] = []
    target_found_at: Optional[int] = None
    stopped_reason = "completed"

    def _register(expr: Expr, c: int) -> bool:
        nonlocal target_found_at
        canon = ge.canonicalize(expr)
        actual_c = ge.node_count(canon)
        if actual_c != c:
            c = actual_c
        s = ge.to_canonical_string(canon)
        import grammar_engine_lean as gl  # local import: reuse its hash fns exactly
        sh = gl._hash_string(s)
        if sh in seen_string_hashes:
            return False
        fp = ge.numeric_fingerprint(canon, leaves)
        fh = gl._hash_fingerprint(fp)
        if fh in seen_fp_hashes:
            seen_string_hashes.add(sh)
            return False
        seen_string_hashes.add(sh)
        seen_fp_hashes.add(fh)
        by_complexity.setdefault(c, [])
        by_complexity[c].append(canon)
        if target_fp_hash is not None and target_found_at is None and fh == target_fp_hash:
            target_found_at = c
        return True

    def _write_checkpoint(reason: str):
        _atomic_write_json(checkpoint_path, {
            "pack": pack,
            "target_id": target_id,
            "max_complexity": max_complexity,
            "levels_completed": checkpoint_levels,
            "stopped_reason": reason,
            "target_found_at_complexity": target_found_at,
            "last_updated_utc": _utc_now(),
        })

    # complexity 1: leaves
    for leaf_name in leaves:
        if leaf_name == "CONST":
            _register(("CONST",), 1)
        else:
            _register(("leaf", leaf_name), 1)

    t_level = time.monotonic()
    rss = _rss_bytes()
    lvl_rec = {
        "complexity": 1,
        "new_registered": len(by_complexity.get(1, [])),
        "cumulative_registered": sum(len(v) for v in by_complexity.values()),
        "elapsed_seconds_this_level": round(t_level - t_start, 3),
        "elapsed_seconds_total": round(t_level - t_start, 3),
        "rss_bytes": rss,
        "target_found": target_found_at is not None,
        "timestamp_utc": _utc_now(),
    }
    level_report.append(lvl_rec)
    checkpoint_levels.append(lvl_rec)
    _write_checkpoint("in_progress" if target_found_at is None else "target_found_early")

    if target_found_at is not None:
        return {
            "pack": pack, "max_complexity": max_complexity,
            "by_complexity_counts": {c: len(v) for c, v in by_complexity.items()},
            "levels": level_report, "target_found_at_complexity": target_found_at,
            "stopped_reason": "target_found_early", "highest_level_completed": 1,
        }

    highest_completed = 1
    for c in range(2, max_complexity + 1):
        level_t0 = time.monotonic()
        before = sum(len(v) for v in by_complexity.values())

        # unary: 1 + size(child) == c
        for child in by_complexity.get(c - 1, []):
            for op in ge.UNARY_OPS:
                _register((op, child), c)

        # binary: 1 + size(left) + size(right) == c
        for c_left in range(1, c - 1):
            c_right = c - 1 - c_left
            if c_right < 1:
                continue
            for left in by_complexity.get(c_left, []):
                for right in by_complexity.get(c_right, []):
                    for op in ge.BINARY_OPS:
                        _register((op, left, right), c)

        t_level = time.monotonic()
        rss = _rss_bytes()
        after = sum(len(v) for v in by_complexity.values())
        lvl_rec = {
            "complexity": c,
            "new_registered": after - before,
            "cumulative_registered": after,
            "elapsed_seconds_this_level": round(t_level - level_t0, 3),
            "elapsed_seconds_total": round(t_level - t_start, 3),
            "rss_bytes": rss,
            "target_found": target_found_at is not None,
            "timestamp_utc": _utc_now(),
        }
        level_report.append(lvl_rec)
        checkpoint_levels.append(lvl_rec)
        highest_completed = c

        # This level is now FULLY, EXHAUSTIVELY built (every candidate at
        # this complexity has been registered) -- so it is checkpointed to
        # disk BEFORE the next, larger level is attempted, per the task
        # brief's checkpointing requirement.
        if target_found_at is not None:
            stopped_reason = "target_found_early"
            _write_checkpoint(stopped_reason)
            break

        if mem_soft_cap_bytes is not None and rss >= mem_soft_cap_bytes:
            stopped_reason = "memory_cap"
            _write_checkpoint(stopped_reason)
            break

        if wall_clock_soft_cap_seconds is not None and (t_level - t_start) >= wall_clock_soft_cap_seconds:
            stopped_reason = "wall_clock_cap"
            _write_checkpoint(stopped_reason)
            break

        _write_checkpoint("in_progress")
    else:
        stopped_reason = "completed"
        _write_checkpoint(stopped_reason)

    return {
        "pack": pack,
        "max_complexity": max_complexity,
        "by_complexity_counts": {c: len(v) for c, v in by_complexity.items() if c <= highest_completed},
        "levels": level_report,
        "target_found_at_complexity": target_found_at,
        "stopped_reason": stopped_reason,
        "highest_level_completed": highest_completed,
    }


def _rss_bytes() -> int:
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    return int(parts[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


if __name__ == "__main__":
    # Self-test: checkpointed enumeration must produce IDENTICAL
    # by_complexity_counts to grammar_engine_lean.enumerate_lean (uncheckpointed)
    # on the same small case.
    import sys
    import grammar_engine_lean as gl
    import tempfile

    pack = "degree_table"
    maxc = 6
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        ckpt_path = tf.name
    r_ckpt = enumerate_lean_checkpointed(pack, maxc, ckpt_path, target_id="SELFTEST")
    r_plain = gl.enumerate_lean(pack, maxc)
    ok = r_ckpt["by_complexity_counts"] == r_plain["by_complexity_counts"]
    print(f"checkpointed vs plain enumerate_lean on {pack} maxc={maxc}: "
          f"{'MATCH' if ok else 'MISMATCH'}", file=sys.stderr)
    print(json.dumps(r_ckpt["by_complexity_counts"]), file=sys.stderr)
    print(json.dumps(r_plain["by_complexity_counts"]), file=sys.stderr)
    with open(ckpt_path) as f:
        ckpt_contents = json.load(f)
    print(f"checkpoint file has {len(ckpt_contents['levels_completed'])} level records, "
          f"stopped_reason={ckpt_contents['stopped_reason']!r}", file=sys.stderr)
    os.unlink(ckpt_path)
    assert ok, "checkpointed enumerator diverged from grammar_engine_lean.enumerate_lean"
    print("grammar_engine_checkpoint.py self-test: OK", file=sys.stderr)
