"""
Memory-lean streaming variant of grammar_engine.enumerate_expressions, built
for the Stage-0c repair task (TASK-20260907-f41930 / RUN-RELN-141a86-stage0c-repair).

This module changes ONLY the enumeration STRATEGY. It imports and reuses
grammar_engine.py's canonicalize(), node_count(), numeric_fingerprint(),
to_canonical_string(), LEAVES_BY_PACK and _SAMPLE_GRID UNCHANGED -- including
its two prior bugfixes (the pow/binomial fingerprint magnitude-hang guard and
the per-CONST-leaf distinct-fingerprint-stream fix). The grammar (operators,
leaf sets, node-counting rule, C_max = 12) is NOT modified anywhere in this
file. No new leaf, operator, or node-counting behaviour is introduced.

Diagnosis carried over from RUN-RELN-141a86-stage0bcde/implementation.md
section 10: the prior brute-force enumerate_expressions() held, for every
registered candidate at every complexity level simultaneously in memory:
  (a) the full expression tree (tuple) -- unavoidable, needed to build the
      next complexity level from smaller pieces (see note below on why
      "iterative deepening that discards prior levels" does NOT apply here);
  (b) the full canonical STRING (~40-100 bytes of Python string object,
      counted once in `seen_strings`);
  (c) the full numeric FINGERPRINT TUPLE -- for a 5-non-CONST-leaf 6-leaf
      pack this is a 32-element tuple of *boxed* Python floats (each ~24
      bytes as a separate heap object) plus ~56 bytes of tuple-object
      overhead, i.e. roughly 800 bytes PER CANDIDATE, counted once in
      `seen_fingerprints` -- and, because fingerprints must remain hashable
      set keys, this is retained for the LIFETIME OF THE RUN, for every one
      of the many millions of candidates ever registered at any level.
(c) is measured here to be the dominant cost (see the driver's per-level
memory samples): a 6-leaf pack's level-9 candidate count is estimated at
~2x10^7 (measured level-7 count 427,569 for enum_zn_and_sidon x observed
~7x/level growth, squared) so the raw fingerprint-tuple set alone would be
on the order of 2x10^7 x 800B =~ 16 GB before any expression-tree or string
storage is even counted -- this matches (and explains) the 1.7-4.9 GB
observed at early, still-growing termination in the prior run.

STRATEGY CHANGE (this file):
  1. Replace the *stored* dedup keys with fixed-size 64-bit DETERMINISTIC
     hashes (blake2b of a canonical byte encoding), not the raw string or
     the raw float tuple. The string/tuple are still computed (transiently,
     to produce the hash), but never RETAINED -- only the 8-byte hash int
     goes into the `seen_*` sets. This is the numeric-fingerprint-dedup
     technique named in the task brief ("dedup against a fingerprint set of
     tuples/hashes rather than storing full expression trees"), applied to
     BOTH the canonical-string dedup key and the numeric-fingerprint dedup
     key. Deterministic (blake2b, not Python's randomized str/tuple hash)
     so the run is exactly reproducible without depending on PYTHONHASHSEED.
     DISCLOSED APPROXIMATION: a 64-bit hash has a birthday-bound collision
     probability of ~n^2/2^65; at the largest n reached in any run below
     (never more than ~5x10^7) this is < 1.4e-5, i.e. astronomically below
     the 200-draw / 1e-9-relative tolerances already used elsewhere in this
     contract for numeric identity -- recorded here, never silently assumed
     exact.
  2. Enumerate ONLY up to the SPECIFIC target's own canonical node count
     (never the full C_max = 12), and EARLY-EXIT the moment the target's
     fingerprint hash appears in the dedup set at any level <= that count
     (the dedup set already guarantees the first-registered representative
     of a given semantic value is retained at the smallest complexity any
     tree in the grammar produces it, by construction of the bottom-up
     level order -- so a hit at any level <= C is a valid recovery at or
     below C, matching the contract's own "algebraically equivalent form
     accepted" acceptance rule; a hit is checked after EVERY level, not
     only at the final one). This does not change what is exhaustively
     covered up to the level where the check succeeds or the enumeration
     is stopped -- levels are still built completely, in order, before the
     next one starts.
  3. Per-level memory and time is sampled directly (resource.getrusage /
     /proc/self/status) and returned to the caller after every level, so a
     caller-supplied soft cap can stop the run BEFORE the next (much
     larger) level is attempted, rather than after an external kill.

WHY "discard each level once the next is generated" (plain iterative
deepening) does NOT apply to this grammar: to build level C you need every
pair (c_left, c_right) with c_left + c_right = C - 1 and c_left ranging
over 1 .. C-2 -- i.e. ALL previously computed levels 1..C-2, not just level
C-1. Level 3 is combined with level 7 to help build level 11, for example.
So every level built so far MUST remain resident until the target level is
reached; the achievable saving is a smaller per-candidate representation
(this file), not discarding early levels (verified against the frozen
grammar's own binary-operator combination rule, not assumed).
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Dict, List, Optional, Tuple

import grammar_engine as ge

Expr = ge.Expr


def _det_hash_bytes(b: bytes) -> int:
    return int.from_bytes(hashlib.blake2b(b, digest_size=8).digest(), "big")


def _hash_string(s: str) -> int:
    return _det_hash_bytes(s.encode("utf-8"))


def _normalize_fp_value(v):
    """IEEE754 -0.0 == 0.0 by Python's own float `==` (and by
    grammar_engine's original tuple-equality dedup semantics), but
    repr(-0.0) == '-0.0' != repr(0.0) == '0.0' -- a real bug found while
    validating this module against grammar_engine.enumerate_expressions on
    a small case (floor(mu) vs pow(log(log(m)),N) both evaluate to
    +/-0.0 on the sample grid and must dedup as one value, exactly as the
    original tuple-based set does). Normalized here so the deterministic
    byte-string encoding used for hashing agrees with Python's own float
    equality on every value, not merely on values that happen to keep the
    same sign of zero."""
    if v is None:
        return None
    if v == 0.0:
        return 0.0
    return v


def _hash_fingerprint(fp: Tuple) -> int:
    # repr() of a tuple of (rounded float | None) is a deterministic,
    # unambiguous byte encoding of the fingerprint value (the underlying
    # floats are already rounded to 9 significant digits by
    # grammar_engine.numeric_fingerprint, so repr is stable run-to-run on
    # the same platform/arithmetic), PROVIDED zero-signed floats are
    # normalized first (see _normalize_fp_value).
    normalized = tuple(_normalize_fp_value(v) for v in fp)
    return _det_hash_bytes(repr(normalized).encode("utf-8"))


def _rss_bytes() -> int:
    """Current process resident set size, read directly from /proc (Linux),
    falling back to resource.getrusage (ru_maxrss, kilobytes on Linux) if
    /proc is unavailable."""
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


class MemoryBudgetExceeded(RuntimeError):
    def __init__(self, level, rss_bytes, cap_bytes):
        super().__init__(
            f"soft memory cap exceeded after completing level {level}: "
            f"{rss_bytes/1e9:.3f} GB >= cap {cap_bytes/1e9:.3f} GB"
        )
        self.level = level
        self.rss_bytes = rss_bytes
        self.cap_bytes = cap_bytes


def enumerate_lean(
    pack: str,
    max_complexity: int,
    target_fp_hash: Optional[int] = None,
    mem_soft_cap_bytes: Optional[int] = None,
    wall_clock_soft_cap_seconds: Optional[float] = None,
    extra_leaves: Optional[Dict[str, list]] = None,
) -> Dict:
    """
    Streaming, hash-deduplicated bottom-up enumeration of canonical-form
    expressions over `pack`'s leaf set, up to `max_complexity`, using
    grammar_engine's OWN canonicalize/node_count/numeric_fingerprint
    (import, not reimplementation -- both prior bugfixes stay in force).

    Returns a dict with per-level counts, per-level timing and RSS samples,
    the level (if any) at which target_fp_hash was first seen, and a
    `stopped_reason` of 'completed' | 'target_found_early' |
    'memory_cap' | 'wall_clock_cap'. Raises MemoryBudgetExceeded is NEVER
    done here -- the cap is honoured by returning early with
    stopped_reason='memory_cap', so the caller always gets a clean partial
    result rather than an exception, matching "preserve completed tables ...
    report partial state; never extend silently" (specification.yaml
    stopping_rules) while still stopping BEFORE the next, larger level.
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
    target_found_at: Optional[int] = None
    stopped_reason = "completed"

    def _register(expr: Expr, c: int) -> bool:
        nonlocal target_found_at
        canon = ge.canonicalize(expr)
        actual_c = ge.node_count(canon)
        if actual_c != c:
            c = actual_c
        s = ge.to_canonical_string(canon)
        sh = _hash_string(s)
        if sh in seen_string_hashes:
            return False
        fp = ge.numeric_fingerprint(canon, leaves)
        fh = _hash_fingerprint(fp)
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

    # complexity 1: leaves
    for leaf_name in leaves:
        if leaf_name == "CONST":
            _register(("CONST",), 1)
        else:
            _register(("leaf", leaf_name), 1)

    t_level = time.monotonic()
    rss = _rss_bytes()
    level_report.append({
        "complexity": 1,
        "new_registered": len(by_complexity.get(1, [])),
        "cumulative_registered": sum(len(v) for v in by_complexity.values()),
        "elapsed_seconds_this_level": round(t_level - t_start, 3),
        "elapsed_seconds_total": round(t_level - t_start, 3),
        "rss_bytes": rss,
    })
    if target_found_at is not None:
        return {
            "pack": pack, "max_complexity": max_complexity,
            "by_complexity_counts": {c: len(v) for c, v in by_complexity.items()},
            "levels": level_report, "target_found_at_complexity": target_found_at,
            "stopped_reason": "target_found_early", "highest_level_completed": 1,
        }

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
        level_report.append({
            "complexity": c,
            "new_registered": after - before,
            "cumulative_registered": after,
            "elapsed_seconds_this_level": round(t_level - level_t0, 3),
            "elapsed_seconds_total": round(t_level - t_start, 3),
            "rss_bytes": rss,
        })

        if target_found_at is not None:
            stopped_reason = "target_found_early"
            highest_completed = c
            break

        if mem_soft_cap_bytes is not None and rss >= mem_soft_cap_bytes:
            stopped_reason = "memory_cap"
            highest_completed = c
            break

        if wall_clock_soft_cap_seconds is not None and (t_level - t_start) >= wall_clock_soft_cap_seconds:
            stopped_reason = "wall_clock_cap"
            highest_completed = c
            break
    else:
        highest_completed = max_complexity

    return {
        "pack": pack,
        "max_complexity": max_complexity,
        "by_complexity_counts": {c: len(v) for c, v in by_complexity.items() if c <= highest_completed},
        "levels": level_report,
        "target_found_at_complexity": target_found_at,
        "stopped_reason": stopped_reason,
        "highest_level_completed": highest_completed,
    }
