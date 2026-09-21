"""harness/run_md5_calib.py -- Bounded MD5 collision-path search instrument.

GOAL-MD5-001 / BATCH-1f30fe / TASK-20260821-f5f96a (RANK 1).

This module IS the instrument the two calibration runs execute:
  RANK 2  blind TARGET run  against standard MD5        (--variant-shift 0)
  RANK 3  NULL-OBJECT run   against the BCP-2 null      (--variant-shift 16)
           variant (round constants cyclically shifted by 16).
It is a single module, runnable as a script, and importable (the runs drive
``search()`` through ``harness.runner.run_wrapped`` so the charged
``wall_seconds`` is wrapper-measured, per BCP-2 charging_convention).

The solver core (the MD5 below and the search) uses NO standard-library MD5
binding. The pinned independent pair in ``harness/runner.py`` (IMPL-1 /
IMPL-3) is used ONLY for certificate verification by the run wrapper, never
for the search.

=============================================================================
DECLARED SEARCH STRATEGY  (fixed BEFORE any run -- fixed_before_acquisition)
=============================================================================
OBJECT
  Identical-prefix 2-block messages  M1 = B1 || B2 ,  M2 = B1 || B2' ,
  where B1 is a fixed 512-bit block derived from the seed, and B2, B2' are
  distinct random 512-bit blocks (16 little-endian 32-bit words each).
  Messages are hex-encoded (128 hex chars each). The collision target is
  equality of the FULL 128-bit MD5 digest of the two full messages, with
  M1 != M2 -- the ``md5_collision_pair`` certificate target.

SEARCH
  A bounded BIRTHDAY (collision-by-enumeration) search over the 128-bit
  digest space of the identical-prefix 2-block messages. The search
  enumerates up to N = 2^21 distinct seeded random second blocks, computes
  each full 2-block digest (all 64 steps of the schedule, one compression
  pass per block), and inserts (digest, block) into a hash TABLE keyed by
  the digest's low k = 40 bits. A table HIT (two distinct blocks with the
  same 40-bit key) is a 40-bit digest-prefix collision -- a PARTIAL result.
  The search continues to collect hits and tracks the longest matching
  prefix of the full 128-bit digests and the cost (blocks evaluated) at
  which it was achieved. A full 128-bit digest match (two distinct blocks
  with identical full digests) is SUCCESS.

  TECHNIQUE NOTE: this is a birthday search, NOT a meet-in-the-middle and
  NOT a differential-path search. It does not split the 64-step schedule
  into independent halves meeting on an intermediate state; it computes
  each full digest and detects collisions in the digest space via the
  low-40-bit hash table.

WINDOW
  Not a search window. The 64-step schedule is MD5's inherent four 16-step
  rounds; each block is compressed in a single pass. The search probes the
  128-bit digest space via the low-40-bit hash table.

MEMORY CEILING
  The meet table holds at most N = 2^21 entries (declared; a few hundred MB
  in CPython). The run's memory ceiling is the batch's 4 GB.

STOPPING RULE
  Stop when (a) the monotonic-clock ``--deadline`` is reached (checked each
  block), or (b) the table is full (N entries), or (c) a full 128-bit digest
  match is found (SUCCESS). A stop at (a) or (b) is a budgeted FAIL -- an
  admissible, complete observation about the instrument (SC-4), never
  evidence about MD5.

WHAT IT CANNOT REACH  (named OPEN, not silently omitted)
  A full 128-bit digest match requires ~2^64 second blocks (birthday bound)
  at this encoding. That is far beyond the declared N = 2^21 and the 900 s
  ceiling, so the instrument is BOUNDED by design: it is a calibration
  instrument, not a cryptanalytic campaign. The full-64-step state matching
  at 2^64 scale is named OPEN.

DETERMINISM
  A single ``--seed`` (the runs use seed 0) drives every stochastic element
  (B1 derivation and the B2 enumeration order). No other source of
  randomness exists.

VARIANT
  ``--variant-shift N`` (default 0): the round constants used are
  T[(i+N) mod 64]. N=0 is standard MD5; N=16 is the BCP-2 null variant.
  The variant is the ONLY difference between the target and null runs: the
  schedule word order, rotations, IV, Merkle-Damgard chaining, and step
  count are identical.

NOT A DIFFERENTIAL-PATH SEARCH
  This instrument uses NO differential characteristic, NO neutral words, and
  NO bit conditions. It is a plain bounded birthday/fragment search,
  deliberately, so the calibration measures the instrument's raw bounded-
  search capability at a declared scale rather than its ability to recall or
  reconstruct a published differential path.

COVERAGE BOUNDARY
  The search depth is BOUNDED by design. What it cannot reach (full 64-step
  state matching at 2^64 scale) is named OPEN above. A budgeted FAIL of the
  search runs is an admissible, complete observation (SC-4); the instrument's
  job is to be honest about its ceiling.
=============================================================================
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

# ---------------------------------------------------------------------------
# Standalone MD5, written FROM the RFC 1321 primary text
# (coordination/goals/GOAL-MD5-001/batches/BATCH-1f30fe/inputs/rfc1321-md5.txt,
# sha256 284a79d148400d9cd2a423211d1103b5cef0fb9256a4cbe6d7ebe5197c3149dd).
# Sections used: 3.1/3.2 (Merkle-Damgard padding + length), 3.3 (initial MD
# buffer), 3.4 (step function F/G/H/I, the 64 round constants T, the 64-step
# schedule), 3.5 (output). The solver core imports no standard-library MD5
# binding; the pinned pair in harness/runner.py verifies certificates only.
# ---------------------------------------------------------------------------

_M32 = (1 << 32) - 1

# RFC 1321 section 3.3: initial MD buffer (A, B, C, D), low-order bytes first.
_IV = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)

# RFC 1321 section 3.4: T[1..64], the integer part of 2^32 * abs(sin(i)),
# i in radians, i = 1..64. Transcribed from the RFC's reference
# implementation (appendix A.3, MD5Transform); every entry is re-verified
# against the section 3.4 sine definition at import by _check_table().
_T = (
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
)

# RFC 1321 section 3.4: the 64-step schedule (message-word index k, rotation
# s) for steps 0..63, with the register rotation ABCD, DABC, CDAB, BCDA.
_SCHEDULE = (
    (0, 7), (1, 12), (2, 17), (3, 22), (4, 7), (5, 12), (6, 17), (7, 22),
    (8, 7), (9, 12), (10, 17), (11, 22), (12, 7), (13, 12), (14, 17), (15, 22),
    (1, 5), (6, 9), (11, 14), (0, 20), (5, 5), (10, 9), (15, 14), (4, 20),
    (9, 5), (14, 9), (3, 14), (8, 20), (13, 5), (2, 9), (7, 14), (12, 20),
    (5, 4), (8, 11), (11, 16), (14, 23), (1, 4), (4, 11), (7, 16), (10, 23),
    (13, 4), (0, 11), (3, 16), (6, 23), (9, 4), (12, 11), (15, 16), (2, 23),
    (0, 6), (7, 10), (14, 15), (5, 21), (12, 6), (3, 10), (10, 15), (1, 21),
    (8, 6), (15, 10), (6, 15), (13, 21), (4, 6), (11, 10), (2, 15), (9, 21),
)


def _check_table() -> None:
    """Self-check at import: the transcribed T table must equal the RFC 3.4
    sine definition for all 64 entries. A transcription error fails loudly
    here, not inside a run."""
    for i in range(1, 65):
        expected = int(2 ** 32 * abs(math.sin(i)))
        if _T[i - 1] != expected:
            raise ValueError(
                f"T[{i}] transcription error: {_T[i - 1]:#x} != {expected:#x}")
    if len(_SCHEDULE) != 64:
        raise ValueError(f"schedule must have 64 steps, has {len(_SCHEDULE)}")


_check_table()


def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & _M32


def _compress(state, words, shift: int = 0):
    """One 64-step MD5 compression (RFC 1321 section 3.4).

    ``state`` is (a, b, c, d) 32-bit words; ``words`` is a 16-tuple of 32-bit
    message words. ``shift`` cyclically shifts the round constants to
    T[(i+shift) mod 64] (0 = standard MD5; 16 = the BCP-2 null variant).
    Returns the new state including the RFC's end-of-block additions
    (A = A + AA, B = B + BB, C = C + CC, D = D + DD).
    """
    a, b, c, d = state
    x = words
    T = _T
    for i in range(64):
        k, s = _SCHEDULE[i]
        if i < 16:
            f = (b & c) | ((~b & _M32) & d)        # F(X,Y,Z) = XY v not(X) Z
        elif i < 32:
            f = (b & d) | (c & (~d & _M32))        # G(X,Y,Z) = XZ v Y not(Z)
        elif i < 48:
            f = b ^ c ^ d                          # H(X,Y,Z) = X xor Y xor Z
        else:
            f = c ^ (b | (~d & _M32))              # I(X,Y,Z) = Y xor (X v not(Z))
        new_a = (b + _rotl((a + f + x[k] + T[(i + shift) % 64]) & _M32, s)) & _M32
        a, b, c, d = d, new_a, b, c
    return ((a + state[0]) & _M32, (b + state[1]) & _M32,
            (c + state[2]) & _M32, (d + state[3]) & _M32)


def _pad(message: bytes) -> bytes:
    """RFC 1321 sections 3.1 (append padding bits) and 3.2 (append length)."""
    bit_len = len(message) * 8
    msg = message + b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    msg += bit_len.to_bytes(8, "little")   # 64-bit length, low-order word first
    return msg


def _state_to_int(state) -> int:
    """RFC 1321 section 3.5: the digest is A, B, C, D, beginning with the
    low-order byte of A and ending with the high-order byte of D -- each
    word emitted little-endian (low byte first). As a 128-bit integer the
    most significant byte is the low-order byte of A, so ``format(digest,
    '032x')`` reproduces the canonical hex digest."""
    out = bytearray()
    for w in state:
        out += w.to_bytes(4, "little")
    return int.from_bytes(out, "big")


def md5_digest(message: bytes, shift: int = 0) -> int:
    """Full 128-bit MD5 digest of ``message`` as an integer (Merkle-Damgard).

    ``shift`` is the round-constant cyclic shift (0 = standard MD5)."""
    state = _IV
    padded = _pad(message)
    for off in range(0, len(padded), 64):
        block = padded[off:off + 64]
        words = tuple(int.from_bytes(block[j * 4:j * 4 + 4], "little")
                      for j in range(16))
        state = _compress(state, words, shift)
    return _state_to_int(state)


def md5_hex(message: bytes, shift: int = 0) -> str:
    return format(md5_digest(message, shift), "032x")


def _words_to_hex(words) -> str:
    """16 32-bit words -> 64 hex chars (little-endian bytes per word)."""
    out = bytearray()
    for w in words:
        out += w.to_bytes(4, "little")
    return out.hex()


def _words_to_block_int(words) -> int:
    """16 32-bit words -> one 512-bit int (word j in bits [32j, 32j+32)).
    Compact table storage: a 512-bit int is far cheaper than a 16-tuple of
    Python ints, which keeps the meet table within the memory ceiling."""
    v = 0
    for j, w in enumerate(words):
        v |= w << (32 * j)
    return v


def _block_int_to_hex(block_int: int) -> str:
    """512-bit block int -> 64 hex chars (little-endian bytes per word)."""
    return block_int.to_bytes(64, "little").hex()


def _longest_common_prefix_bits(x: int, y: int, total: int = 128) -> int:
    """Longest common prefix of two ``total``-bit integers, counted from the
    most significant bit."""
    z = x ^ y
    if z == 0:
        return total
    return total - z.bit_length()


# ---------------------------------------------------------------------------
# The declared bounded search
# ---------------------------------------------------------------------------

def search(seed: int = 0, variant_shift: int = 0, deadline: float | None = None,
           n_max: int = 2 ** 21, k_bits: int = 40) -> dict:
    """Run the declared bounded search (see the module docstring).

    Returns the raw result dict: outcome, stop reason, the search space
    explored, the strongest partial result (longest matching digest-prefix
    and the cost at which it was achieved), and the internal counters. On
    SUCCESS it also carries the two hex messages and the claimed digest,
    ready for the ``md5_collision_pair`` certificate kind.
    """
    rng = random.Random(seed)

    # Fixed first block B1, derived from the seed (identical prefix).
    b1_words = tuple(rng.getrandbits(32) for _ in range(16))
    # Chaining value after block 1 (the starting state for block 2).
    h1 = _compress(_IV, b1_words, variant_shift)

    mask = (1 << k_bits) - 1
    table: dict[int, tuple[int, int]] = {}   # key -> (digest_int, block_int)
    blocks_evaluated = 0
    fragments_tried = 0
    partial_hits = 0
    best_prefix = -1            # -1 = no hit yet; a prefix-0 hit is recorded
    best_prefix_cost = None
    best_pair = None
    outcome = "FAIL"
    stop_reason = None
    m1_hex = m2_hex = digest_hex = None

    t0 = time.monotonic()
    deadline_abs = (t0 + deadline) if deadline is not None else None

    while blocks_evaluated < n_max:
        if deadline_abs is not None and time.monotonic() >= deadline_abs:
            stop_reason = "deadline"
            break
        b2_words = tuple(rng.getrandbits(32) for _ in range(16))
        b2_int = _words_to_block_int(b2_words)
        state2 = _compress(h1, b2_words, variant_shift)
        digest = _state_to_int(state2)
        blocks_evaluated += 1
        fragments_tried += 4          # 4 x 16-step round fragments per block
        key = digest & mask
        if key in table:
            other_digest, other_int = table[key]
            if other_int != b2_int:
                partial_hits += 1
                prefix = _longest_common_prefix_bits(digest, other_digest)
                if prefix > best_prefix:
                    best_prefix = prefix
                    best_prefix_cost = blocks_evaluated
                    best_pair = (other_int, b2_int, other_digest)
                if prefix == 128:
                    outcome = "SUCCESS"
                    stop_reason = "full_match"
                    w1, w2, dg = best_pair
                    m1_hex = _words_to_hex(b1_words) + _block_int_to_hex(w1)
                    m2_hex = _words_to_hex(b1_words) + _block_int_to_hex(w2)
                    digest_hex = format(dg, "032x")
                    break
        else:
            table[key] = (digest, b2_int)
    if stop_reason is None:
        stop_reason = "table_full"
    if best_prefix < 0:          # no hits at all
        best_prefix = 0
        best_prefix_cost = None

    result = {
        "outcome": outcome,
        "stop_reason": stop_reason,
        "seed": seed,
        "variant_shift": variant_shift,
        "k_bits": k_bits,
        "n_max": n_max,
        "blocks_evaluated": blocks_evaluated,
        "fragments_tried": fragments_tried,
        "table_size": len(table),
        "partial_hits": partial_hits,
        "best_prefix_bits": best_prefix,
        "best_prefix_cost_blocks": best_prefix_cost,
        "b1_hex": _words_to_hex(b1_words),
        "search_space_explored": (
            f"{blocks_evaluated} distinct random second blocks (of n_max="
            f"{n_max}); meet table over the low {k_bits} digest bits; "
            f"window = 16-step round fragments (4 per block)"),
        "internal_wall_seconds_not_charged": round(time.monotonic() - t0, 6),
    }
    if outcome == "SUCCESS":
        result["messages"] = [m1_hex, m2_hex]
        result["digest"] = digest_hex
        result["certificate"] = {
            "kind": "md5_collision_pair",
            "statement": {
                "messages": [m1_hex, m2_hex],
                "digest": digest_hex,
                "implementations": ["IMPL-1", "IMPL-3"],
            },
        }
    return result


def write_report(result: dict, path: str) -> None:
    """Search-report writer: machine-readable (JSON) output of the outcome,
    the search space explored, the strongest partial result, and the
    counters."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Script entry point: charges the run through harness.runner.run_wrapped so
# the wrapper-measured wall_seconds is the charged cost (BCP-2).
# ---------------------------------------------------------------------------

def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Bounded MD5 collision-path search instrument "
                    "(GOAL-MD5-001 BATCH-1f30fe).")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--variant-shift", type=int, default=0)
    ap.add_argument("--deadline", type=float, default=None,
                    help="monotonic-clock seconds; checked each block")
    ap.add_argument("--n-max", type=int, default=2 ** 21)
    ap.add_argument("--k-bits", type=int, default=40)
    ap.add_argument("--out-root", default=None,
                    help="run-record root (run_wrapped out_root)")
    ap.add_argument("--exp-id", default="EXP-MDFIVE-001")
    ap.add_argument("--exp-area", default="MDFIVE")
    ap.add_argument("--run-suffix", default=None)
    ap.add_argument("--report-path", default=None,
                    help="where to write the JSON search report")
    args = ap.parse_args(argv)

    repo = _repo_root()
    if repo not in sys.path:
        sys.path.insert(0, repo)
    from harness import runner

    def fn():
        raw = search(seed=args.seed, variant_shift=args.variant_shift,
                     deadline=args.deadline, n_max=args.n_max,
                     k_bits=args.k_bits)
        if raw["outcome"] == "SUCCESS":
            cert = raw["certificate"]
        else:
            cert = {"kind": "none"}
        return runner.RunResult(
            run_suffix=(args.run_suffix
                        or f"calib-v{args.variant_shift}-s{args.seed}"),
            curve_id="MD5", seed=args.seed,
            parameters={"variant_shift": args.variant_shift,
                        "k_bits": args.k_bits, "n_max": args.n_max,
                        "deadline": args.deadline},
            metrics={"blocks_evaluated": raw["blocks_evaluated"],
                     "fragments_tried": raw["fragments_tried"],
                     "table_size": raw["table_size"],
                     "partial_hits": raw["partial_hits"],
                     "best_prefix_bits": raw["best_prefix_bits"],
                     # BCP-2 charging_convention required key: the count of
                     # near-collision message blocks (second blocks that
                     # formed a k-bit prefix collision with a stored block).
                     "near_collision_blocks": raw["partial_hits"]},
            certificate=cert,
            raw=raw,
            stdout=json.dumps(raw, indent=2, sort_keys=True) + "\n")

    run_id = runner.run_wrapped(args.exp_id, args.exp_area, fn,
                                 status="completed_valid",
                                 command=" ".join(sys.argv),
                                 out_root=args.out_root)
    # Write the search report next to the run record (within the task dir).
    if args.report_path:
        report_path = args.report_path
    elif args.out_root:
        report_path = os.path.join(
            args.out_root, f"search-report-{args.run_suffix or 'calib'}.json")
    else:
        report_path = None
    if report_path:
        # Re-read the raw result from the run record so the report and the
        # record agree byte-for-byte.
        run_dir = os.path.join(args.out_root, "runs", run_id)
        with open(os.path.join(run_dir, "raw-result.json")) as fh:
            raw = json.load(fh)["raw"]
        write_report(raw, report_path)
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
