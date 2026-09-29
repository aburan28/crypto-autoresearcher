"""harness/run_md4_ceiling.py -- Round-1-restricted, two-free-word
splice-and-cut MITM instrument against MD4 (control) and, conditionally,
MD5's Round 1 (nearby-object control).

GOAL-MD5-001 / BATCH-af29f6 / TASK-20260821-de817d, executing the FROZEN
contract EXP-MDFIVE-88f7d1 (hypothesis H-MDFIVE-bf7767). This module is a
STRUCTURALLY DIFFERENT instrument from harness/run_md5_calib.py (BATCH-1f30fe,
a full-message birthday/collision search over 64-step MD5); that module is
untouched and stays the frozen instrument of record for its own batch.

=============================================================================
INPUT PROVENANCE
=============================================================================
MD5: RFC 1321 Appendix A.3, local pinned copy
  coordination/goals/GOAL-MD5-001/batches/BATCH-1f30fe/inputs/rfc1321-md5.txt
  sha256 284a79d148400d9cd2a423211d1103b5cef0fb9256a4cbe6d7ebe5197c3149dd
MD4: RFC 1320. The idea-generator's WebFetch transcript
  (coordination/goals/GOAL-MD5-001/batches/BATCH-af29f6/inputs/
  rfc1320-md4-round-schedule-excerpt.md) was explicitly flagged as NOT
  sha256-pinnable (WebFetch passes content through a summarizing model).
  This Executor session fetched the raw text directly with `curl` against
  https://www.rfc-editor.org/rfc/rfc1320.txt and pinned it at
  coordination/goals/GOAL-MD5-001/batches/BATCH-af29f6/inputs/rfc1320-md4.txt,
  sha256 f727b15e19ab8ac5036ab7921476e8d8644512190ade32a2e0a2fb9d8a2421c7.
  The raw text's Round-1 operation list (section 3.4) and F-function text are
  BYTE-IDENTICAL to the WebFetch excerpt already on file, cross-checked line
  by line by this session before writing this module (no discrepancy found;
  see execution-report.yaml `md4_pinning` for the diff-check record).

=============================================================================
DECLARED SEARCH STRATEGY, WINDOW, MEMORY CEILING, STOPPING RULE
(fixed BEFORE any run -- fixed_before_acquisition, EXP-MDFIVE-88f7d1)
=============================================================================
OBJECT
  Round 1 (steps 1-16, 0-indexed steps 0-15) of MD4 or MD5, using the
  IDENTICAL word-index schedule (word k used at step k+1, k=0..15) and the
  IDENTICAL Round-1 auxiliary function F(X,Y,Z) = (X AND Y) OR ((NOT X) AND
  Z) in both primitives. Split at S=9: chunk1 = steps 1-9 (0-indexed 0..8,
  words 0..8), chunk2 = steps 10-16 (0-indexed 9..15, words 9..15). Free
  word for chunk1 = word 8 (a declared k1-bit low-order window, high bits
  fixed); free word for chunk2 = word 9 (a declared k2-bit low-order
  window). All other 14 words are held to a fixed, pre-registered, non-zero
  32-bit constant (fixed_word_generation, seed 20260821).

TARGET
  Per target draw: true_word8 and true_word9 (k-bit windows for the
  fixed-scale run, k1=k2=10) are drawn from a declared seeded stream. The
  FULL Round-1 output state Y (registers A,B,C,D after all 16 steps,
  computed forward from the standard MD4/MD5 initial buffer using the 14
  fixed words plus the true word8/word9) is the instrument's "known digest"
  input to chunk2's BACKWARD computation. The declared 20-bit target is the
  low 20 bits of register A immediately after step 9 of that SAME forward
  trajectory (chunk1's own value at word8=true_word8). Because backward_step
  is the exact algebraic inverse of forward_step (HEUR-H2), chunk2's
  backward computation from Y through steps 16..10 -- evaluated at
  word9=true_word9 -- reproduces the identical register-A-after-step-9 value
  by construction; the search recovers this equality from two independent
  directions without being told the true words.

SEARCH
  Chunk1: for word8 in [0, 2^k1), forward-compute register A after step 9
  from the standard initial buffer using the 8 fixed low words plus word8;
  index a hash table by the low m bits of that value (the matching window),
  storing (word8, low-k-bits value).
  Chunk2: backward-invert Y through steps 16..11 ONCE (uses only the 6 fixed
  high words, independent of word9); then, for each word9 in [0, 2^k2),
  apply one more backward_step (the only step depending on word9) to reach a
  candidate register-A-after-step-9 value; probe chunk1's table on the same
  low m bits. A table hit is a MATCHING-WINDOW COLLISION; it is a FULL
  20-BIT TARGET MATCH only if the two independently-derived low-k-bits
  values are byte-identical.
  Declared window: m=12 (matching/meeting filter), k=20 (full target,
  checked independently after the m-bit filter -- exact equality, never
  inferred from the m-bit hit alone).

MEMORY CEILING
  Chunk1's table holds at most 2^k1 entries (2^10 = 1024 for the declared
  scale, 2^6 = 64 for the k1=k2=6 brute-force control) -- negligible against
  the batch's 4 GB ceiling; no time-memory tradeoff is exercised at this
  scale.

STOPPING RULE
  Every run in this module is charged through harness.runner.run_wrapped
  with an explicit `--deadline` (monotonic clock, checked between target
  draws for the H1/MD5 runs and is not expected to bind for the primary/
  control/H2 runs at this declared scale, which complete in well under a
  second of raw compute). A deadline hit before the declared N is reached is
  a budget outcome (SC-7), reported with the achieved N and never treated as
  a defect or a negative result.

DETERMINISM -- the five frozen seeds (EXP-MDFIVE-88f7d1.inputs.seeds)
  20260821  fixed_word_generation (14 fixed words + word8/word9 high bits)
  8975313   MD4 primary-target draw
  8975314   MD4 H1-validation target-stream (N independent targets)
  8975315   MD5 conditional-run target-stream (same N intent as 8975314)
  8975316   k1=k2=6 brute-force-control target draw
  8975317   H2 backward-inversion regression fixture

The solver core below (forward_step/backward_step, the MITM search, the
naive all-pairs control, the H1 sampler) imports NO standard-library or
third-party MD4/MD5 binding. `_reference_round1_forward` (used ONLY for
certificate re-verification, see `verify_match_certificate`) is a SEPARATE
implementation of the same Round-1 arithmetic, written independently of
`forward_step`/`backward_step`, for the independent-recomputation discipline
(docs/claims-and-verification.md). `md4_digest` (the FULL 48-step, feed-
forward MD4) exists only to verify this module's Round-1 arithmetic against
RFC 1320's own published test vectors (A.5) -- it is not used by the search.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

_M32 = (1 << 32) - 1
_IV = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476)


def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & _M32


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & _M32


def _f(x: int, y: int, z: int) -> int:
    """RFC 1320 sec 3.4 / RFC 1321 sec 3.4, Round 1: F(X,Y,Z)=XY v not(X)Z."""
    return (x & y) | ((~x & _M32) & z)


def _g(x: int, y: int, z: int) -> int:
    """RFC 1320 Round 2: G(X,Y,Z) = XY v XZ v YZ."""
    return (x & y) | (x & z) | (y & z)


def _h(x: int, y: int, z: int) -> int:
    """RFC 1320 Round 3: H(X,Y,Z) = X xor Y xor Z."""
    return x ^ y ^ z


# ---------------------------------------------------------------------------
# Round-1 shift/constant tables, transcribed independently for each
# primitive from its own pinned RFC text (see module docstring). Word order
# is IDENTICAL and sequential (word i used at step i+1) for both.
# ---------------------------------------------------------------------------

MD4_R1_SHIFTS = (3, 7, 11, 19)
MD4_R1_CONSTS = (0,) * 16          # RFC 1320 sec 3.4: Round 1 has no additive constant.
# RFC 1320's own operation notation is explicit and DIFFERENT from RFC 1321's:
# "Let [abcd k s] denote the operation a = (a + F(b,c,d) + X[k]) <<< s."
# (sec 3.4; identical wording, only F/G/H and the additive constant change,
# for Rounds 2 and 3). There is NO "+= b" term anywhere in MD4's definition
# -- unlike RFC 1321's FF/GG/HH/II reference-implementation macros, which
# explicitly execute "(a) += (b);" AFTER the rotate. This is a genuine
# structural difference between the two primitives' step functions, not a
# shift/constant-only difference, and MD4_ADD_B / MD5_ADD_B below encode it
# so forward_step/backward_step are correct for both. (A first draft of
# this module used MD5's "+b" formula for both primitives, which failed
# ALL SEVEN RFC 1320 A.5 test vectors -- recorded in execution-report.yaml
# as a protocol deviation / implementation_error caught before any run.)
MD4_ADD_B = False
MD5_ADD_B = True

MD5_R1_SHIFTS = (7, 12, 17, 22)
# RFC 1321 sec 3.4, T[1..16] = floor(2^32 * abs(sin(i))), i = 1..16 radians.
# Transcribed from rfc1321-md5.txt Appendix A.3 (MD5Transform, steps 1-16);
# self-checked against the sec 3.4 sine definition by _check_md5_t16() below.
MD5_R1_CONSTS = (
    0xD76AA478, 0xE8C7B756, 0x242070DB, 0xC1BDCEEE,
    0xF57C0FAF, 0x4787C62A, 0xA8304613, 0xFD469501,
    0x698098D8, 0x8B44F7AF, 0xFFFF5BB1, 0x895CD7BE,
    0x6B901122, 0xFD987193, 0xA679438E, 0x49B40821,
)


def _check_md5_t16() -> None:
    for i in range(1, 17):
        expected = int(2 ** 32 * abs(math.sin(i)))
        if MD5_R1_CONSTS[i - 1] != expected:
            raise ValueError(f"MD5 T[{i}] transcription error: "
                              f"{MD5_R1_CONSTS[i - 1]:#x} != {expected:#x}")


_check_md5_t16()

# MD4 full-schedule (all 48 steps) constants, needed only for the RFC 1320
# test-vector self-check (md4_digest below), never by the Round-1 instrument.
_MD4_R2_WORDS = (0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15)
_MD4_R2_SHIFTS = (3, 5, 9, 13)
_MD4_R2_CONST = 0x5A827999
_MD4_R3_WORDS = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
_MD4_R3_SHIFTS = (3, 9, 11, 15)
_MD4_R3_CONST = 0x6ED9EBA1


def _r1_tables(target: str) -> tuple[tuple[int, ...], tuple[int, ...], bool]:
    if target == "md4":
        return MD4_R1_SHIFTS, MD4_R1_CONSTS, MD4_ADD_B
    if target == "md5":
        return MD5_R1_SHIFTS, MD5_R1_CONSTS, MD5_ADD_B
    raise ValueError(f"unknown target: {target!r}")


# ---------------------------------------------------------------------------
# forward_step / backward_step: the ONLY two primitives the MITM search and
# the H2 regression fixture use. State is a 4-tuple (a,b,c,d) that always
# means "whichever named register is about to be updated, in the RFC's own
# ABCD/DABC/CDAB/BCDA rotation" -- the standard reference-implementation
# convention (RFC 1321 Appendix A.3's FF/GG/HH/II macros: a += F(b,c,d)+x+T;
# a = a<<<s; a += b). The value most recently computed by a step is always
# at tuple position 1 of the RETURNED state (HEUR-H2 exploits this).
# ---------------------------------------------------------------------------

def forward_step(state: tuple[int, int, int, int], xk: int, s: int, t: int,
                  add_b: bool = True) -> tuple[int, int, int, int]:
    """One Round-1 step. `add_b` selects the primitive's own operation
    definition: MD5 (RFC 1321 FF/GG/HH/II macros) does `a=rotl(...); a+=b`;
    MD4 (RFC 1320 sec 3.4, "[abcd k s]" notation) does NOT -- `a=rotl(...)`
    only. See MD4_ADD_B/MD5_ADD_B above for why this is a real structural
    difference, not a naming convenience."""
    a, b, c, d = state
    rotated = _rotl((a + _f(b, c, d) + xk + t) & _M32, s)
    new_a = ((b + rotated) & _M32) if add_b else rotated
    return (d, new_a, b, c)


def backward_step(state_next: tuple[int, int, int, int], xk: int, s: int,
                   t: int, add_b: bool = True) -> tuple[int, int, int, int]:
    """Exact algebraic inverse of forward_step (HEUR-H2), for the SAME
    add_b convention.

    Given state_next = forward_step(state, xk, s, t, add_b), recovers
    state. state_next = (d, new_a, b, c); old_b/old_c/old_d = c2/d2/a2 of
    state_next in both conventions. Only the reconstruction of `rotated`
    (and hence old_a) differs:
      add_b=True  (MD5): new_a = old_b + rotl(...)  =>  rotated = new_a-old_b
      add_b=False (MD4): new_a = rotl(...)          =>  rotated = new_a
    then old_a = rotr(rotated, s) - F(old_b,old_c,old_d) - xk - t (mod 2^32).
    """
    a2, b2, c2, d2 = state_next
    old_b, old_c, old_d = c2, d2, a2
    new_a = b2
    rotated = ((new_a - old_b) & _M32) if add_b else new_a
    old_a = (_rotr(rotated, s) - _f(old_b, old_c, old_d) - xk - t) & _M32
    return (old_a, old_b, old_c, old_d)


def apply_forward(state0, words, shifts, consts, add_b: bool = True,
                  start_index: int = 0) -> tuple[int, int, int, int]:
    """Apply `len(words)` forward steps. `consts` must already be sliced to
    align with `words` (consts[j] is the constant for words[j]), but the
    4-cycling SHIFT table must be indexed by the GLOBAL step index -- so
    `start_index` (the global step index of words[0]) is required whenever
    the caller is not starting at step 0 (e.g. resuming from state9 to
    compute state16, words[0] there is word9 at global step index 9). A
    local (0-based) shift index here was an earlier bug caught by comparing
    forward and backward computations against each other (see
    execution-report.yaml)."""
    state = state0
    n = len(words)
    for i in range(n):
        state = forward_step(state, words[i], shifts[(start_index + i) % 4],
                             consts[i], add_b)
    return state


def apply_backward(state_from, words, shifts, consts, start_index: int,
                   add_b: bool = True) -> tuple[int, int, int, int]:
    """Invert `len(words)` forward steps ending at 0-indexed `start_index`
    (the LAST step inverted is `start_index`, working down to
    `start_index - len(words) + 1`), i.e. `words[j]` is the word used at
    step index `start_index - j`."""
    state = state_from
    for j, w in enumerate(words):
        i = start_index - j
        state = backward_step(state, w, shifts[i % 4], consts[i], add_b)
    return state


# ---------------------------------------------------------------------------
# Full 48-step MD4 (RFC 1320), used ONLY to self-check this module's Round-1
# arithmetic against RFC 1320's own published test vectors (A.5). Not used
# by the MITM instrument.
# ---------------------------------------------------------------------------

def _step_generic(state, xk, s, t, func):
    """MD4 step for an ARBITRARY round function (F/G/H), used only by the
    full 48-step vector-check self-test (`md4_digest`). Deliberately
    separate from `forward_step`, which is documented and used as a
    Round-1-only (F-function-only) primitive by the MITM instrument;
    reusing it for rounds 2/3 with F hardcoded was an earlier bug caught by
    this module's own RFC 1320 vector self-check (recorded in
    execution-report.yaml)."""
    a, b, c, d = state
    new_a = _rotl((a + func(b, c, d) + xk + t) & _M32, s)   # MD4: no += b.
    return (d, new_a, b, c)


def _md4_compress(state, words):
    a, b, c, d = state
    s0 = (a, b, c, d)
    st = (a, b, c, d)
    for i in range(16):
        st = forward_step(st, words[i], MD4_R1_SHIFTS[i % 4], 0, MD4_ADD_B)
    for idx, wi in enumerate(_MD4_R2_WORDS):
        st = _step_generic(st, words[wi], _MD4_R2_SHIFTS[idx % 4],
                           _MD4_R2_CONST, _g)
    for idx, wi in enumerate(_MD4_R3_WORDS):
        st = _step_generic(st, words[wi], _MD4_R3_SHIFTS[idx % 4],
                           _MD4_R3_CONST, _h)
    # After 48 steps `st` tuple-position-1 always holds the register most
    # recently updated; but the natural (A,B,C,D)-order state needed for the
    # RFC's feed-forward addition is only aligned every 4 steps, and 48 is a
    # multiple of 4, so `st` IS back in natural (a,b,c,d) order here (see
    # module docstring's tuple-rotation note; verified by the vector test).
    a2, b2, c2, d2 = st
    return ((a2 + s0[0]) & _M32, (b2 + s0[1]) & _M32,
            (c2 + s0[2]) & _M32, (d2 + s0[3]) & _M32)


def _pad(message: bytes) -> bytes:
    bit_len = len(message) * 8
    msg = message + b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    msg += (bit_len & ((1 << 64) - 1)).to_bytes(8, "little")
    return msg


def md4_digest(message: bytes) -> str:
    state = _IV
    padded = _pad(message)
    for off in range(0, len(padded), 64):
        block = padded[off:off + 64]
        words = tuple(int.from_bytes(block[j * 4:j * 4 + 4], "little")
                      for j in range(16))
        state = _md4_compress(state, words)
    out = bytearray()
    for w in state:
        out += w.to_bytes(4, "little")
    return out.hex()


# RFC 1320 Appendix A.5, the published MD4 test suite.
RFC1320_TEST_VECTORS = (
    (b"", "31d6cfe0d16ae931b73c59d7e0c089c0"),
    (b"a", "bde52cb31de33e46245e05fbdbd6fb24"),
    (b"abc", "a448017aaf21d8525fc10ae87aa6729d"),
    (b"message digest", "d9130a8164549fe818874806e1c7014b"),
    (b"abcdefghijklmnopqrstuvwxyz", "d79e1c308aa5bbcdeea8ed63df412da9"),
    (b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
     "043f8582f241db351ce627e153e7f0e4"),
    (b"123456789012345678901234567890123456789012345678901234567890123456"
     b"78901234567890", "e33b4ddc9c38f2199c3e7b164fcc0536"),
)


def check_rfc1320_vectors() -> dict:
    results = []
    all_ok = True
    for msg, expected in RFC1320_TEST_VECTORS:
        got = md4_digest(msg)
        ok = (got == expected)
        all_ok = all_ok and ok
        results.append({"message": msg.decode("ascii"), "expected": expected,
                        "got": got, "ok": ok})
    return {"all_ok": all_ok, "vectors": results}


# ---------------------------------------------------------------------------
# Deterministic fixed-word / target generation (EXP-MDFIVE-88f7d1
# test_boundary.parameters, verbatim).
# ---------------------------------------------------------------------------

def fixed_word_generation(seed: int = 20260821, free_bits: int = 10) -> dict:
    """H-MDFIVE-bf7767 test_boundary.parameters.fixed_word_generation.

    `free_bits` generalizes the spec's "top 22 bits" (free_bits=10, the
    declared scale) to the k1=k2=6 brute-force control ("top 26 bits",
    free_bits=6) via the SAME mask/fallback procedure the spec states for
    both cases.
    """
    rng = random.Random(seed)
    draws = [rng.getrandbits(32) for _ in range(16)]
    fixed_words = {}
    for i in range(16):
        if i in (8, 9):
            continue
        w = draws[i]
        fixed_words[i] = w if w != 0 else 1
    mask = _M32 & ~((1 << free_bits) - 1)
    high8 = draws[8] & mask
    if high8 == 0:
        high8 = 1 << free_bits
    high9 = draws[9] & mask
    if high9 == 0:
        high9 = 1 << free_bits
    return {"fixed_words": fixed_words, "high8": high8, "high9": high9,
           "free_bits": free_bits, "seed": seed}


def generate_target(target_seed: int, fixed: dict, mode: str,
                     free_bits: int | None = None) -> dict:
    """Draw one target: true_word8/word9 (free_bits-bit low windows), the
    Round-1 output state Y (all 16 steps forward), and the declared low-20
    target (register A after step 9, chunk1's own forward value)."""
    fb = free_bits if free_bits is not None else fixed["free_bits"]
    rng_t = random.Random(target_seed)
    low8 = rng_t.getrandbits(fb)
    low9 = rng_t.getrandbits(fb)
    true_word8 = fixed["high8"] | low8
    true_word9 = fixed["high9"] | low9
    words = dict(fixed["fixed_words"])
    words[8] = true_word8
    words[9] = true_word9
    shifts, consts, add_b = _r1_tables(mode)
    word_list = [words[i] for i in range(16)]
    state9 = apply_forward(_IV, word_list[:9], shifts, consts[:9], add_b)
    a9 = state9[1]
    state16 = apply_forward(state9, word_list[9:16], shifts, consts[9:16], add_b,
                            start_index=9)
    return {
        "true_word8": true_word8, "true_word9": true_word9,
        "target_low20": a9 & 0xFFFFF, "Y": state16,
        "mode": mode, "free_bits": fb,
    }


# ---------------------------------------------------------------------------
# The MITM instrument.
# ---------------------------------------------------------------------------

def mitm_search(fixed: dict, target: dict, mode: str, k1: int, k2: int,
                m: int, k: int) -> dict:
    """Exhaustive (declared scale is small enough that 'exhaustive' and
    'find-first' cost the same order of magnitude) MITM search over
    word8 in [0,2^k1) x word9 in [0,2^k2). Returns matching-window and
    full-target hit counts, the full solution set, and the chunk-evaluation
    count at which the FIRST full-target match occurred (or None)."""
    shifts, consts, add_b = _r1_tables(mode)
    fixed_words = fixed["fixed_words"]

    # chunk1: forward, word8-only.
    table: dict[int, list[tuple[int, int]]] = {}
    for word8_low in range(1 << k1):
        word8 = fixed["high8"] | word8_low
        words0_8 = [fixed_words[i] for i in range(8)] + [word8]
        state9 = apply_forward(_IV, words0_8, shifts, consts[:9], add_b)
        a9 = state9[1]
        low_m = a9 & ((1 << m) - 1)
        low_k = a9 & ((1 << k) - 1)
        table.setdefault(low_m, []).append((word8, low_k))

    # chunk2 fixed prefix: backward from Y through steps 16..11 (word9-free).
    words10_15 = [fixed_words[i] for i in range(15, 9, -1)]  # reverse order: words[0]=step16(word15)..words[-1]=step11(word10), per apply_backward's documented contract
    state10 = apply_backward(target["Y"], words10_15, shifts, consts,
                             start_index=15, add_b=add_b)

    matching_window_hits = 0
    full_target_hits = 0
    solutions: list[tuple[int, int]] = []
    chunk_evals_to_first = None
    chunk1_cost = 1 << k1

    for word9_low in range(1 << k2):
        word9 = fixed["high9"] | word9_low
        state9_b = backward_step(state10, word9, shifts[9 % 4], consts[9], add_b)
        a9_b = state9_b[1]
        low_m = a9_b & ((1 << m) - 1)
        low_k = a9_b & ((1 << k) - 1)
        bucket = table.get(low_m)
        if not bucket:
            continue
        for word8, low_k_fwd in bucket:
            matching_window_hits += 1
            if low_k_fwd == low_k:
                full_target_hits += 1
                solutions.append((word8, word9))
                if chunk_evals_to_first is None:
                    chunk_evals_to_first = chunk1_cost + word9_low + 1

    return {
        "matching_window_hits": matching_window_hits,
        "full_target_hits": full_target_hits,
        "solutions": solutions,
        "chunk_evals_to_first_full_match": chunk_evals_to_first,
        "chunk1_evaluations": 1 << k1,
        "chunk2_evaluations": 1 << k2,
        "total_chunk_evaluations": (1 << k1) + (1 << k2),
    }


def naive_all_pairs_search(fixed: dict, target: dict, mode: str, k1: int,
                           k2: int, k: int) -> dict:
    """Naive O(2^{k1+k2}) baseline: recomputes chunk1's forward value AND
    chunk2's backward value FRESH inside the nested loop (no hash table, no
    caching) and checks exact k-bit equality. Same restricted 2-word search
    space and same target definition as mitm_search; used ONLY for the
    k1=k2=6 result-set equality control (invalidation_rules)."""
    shifts, consts, add_b = _r1_tables(mode)
    fixed_words = fixed["fixed_words"]
    words10_15 = [fixed_words[i] for i in range(15, 9, -1)]  # reverse order: words[0]=step16(word15)..words[-1]=step11(word10), per apply_backward's documented contract
    state10 = apply_backward(target["Y"], words10_15, shifts, consts,
                             start_index=15, add_b=add_b)
    solutions = []
    evaluations = 0
    for word8_low in range(1 << k1):
        word8 = fixed["high8"] | word8_low
        words0_8 = [fixed_words[i] for i in range(8)] + [word8]
        state9 = apply_forward(_IV, words0_8, shifts, consts[:9], add_b)
        low_k_fwd = state9[1] & ((1 << k) - 1)
        for word9_low in range(1 << k2):
            word9 = fixed["high9"] | word9_low
            state9_b = backward_step(state10, word9, shifts[9 % 4], consts[9], add_b)
            low_k_bwd = state9_b[1] & ((1 << k) - 1)
            evaluations += 1
            if low_k_fwd == low_k_bwd:
                solutions.append((word8, word9))
    return {"solutions": solutions, "evaluations": evaluations}


# ---------------------------------------------------------------------------
# Independent certificate re-verification. Deliberately a SEPARATE code path
# from forward_step/backward_step/mitm_search: it forward-simulates all 16
# Round-1 steps in one straight-line pass with named registers, computes
# register A after step 9 directly, and separately confirms that continuing
# forward through steps 10-16 with the claimed word9 reproduces the declared
# Round-1 output state Y exactly -- the strongest independently-checkable
# claim this instrument can certify (H-MDFIVE-bf7767 method_ceiling).
# ---------------------------------------------------------------------------

def _reference_round1_forward(word_list, mode: str):
    """Straight-line, un-abstracted re-implementation (named a,b,c,d
    variables, no state-tuple role convention) of 16-step Round-1 forward
    compression, for certificate re-verification only."""
    if mode == "md4":
        shifts, consts, add_b = MD4_R1_SHIFTS, MD4_R1_CONSTS, MD4_ADD_B
    elif mode == "md5":
        shifts, consts, add_b = MD5_R1_SHIFTS, MD5_R1_CONSTS, MD5_ADD_B
    else:
        raise ValueError(mode)
    a, b, c, d = _IV
    a_after_step9 = None
    for i in range(16):
        x = word_list[i]
        s = shifts[i % 4]
        t = consts[i]
        if i % 4 == 0:
            a = (a + _f(b, c, d) + x + t) & _M32
            a = _rotl(a, s)
            a = ((a + b) & _M32) if add_b else a
            reg_just_updated = a
        elif i % 4 == 1:
            d = (d + _f(a, b, c) + x + t) & _M32
            d = _rotl(d, s)
            d = ((d + a) & _M32) if add_b else d
            reg_just_updated = d
        elif i % 4 == 2:
            c = (c + _f(d, a, b) + x + t) & _M32
            c = _rotl(c, s)
            c = ((c + d) & _M32) if add_b else c
            reg_just_updated = c
        else:
            b = (b + _f(c, d, a) + x + t) & _M32
            b = _rotl(b, s)
            b = ((b + c) & _M32) if add_b else b
            reg_just_updated = b
        if i == 8:            # step 9 (1-indexed) is loop index 8
            a_after_step9 = reg_just_updated
    return a_after_step9, (a, b, c, d)


def verify_match_certificate(fixed: dict, target: dict, mode: str,
                             word8: int, word9: int, m: int, k: int) -> dict:
    """Independently re-verify a claimed MITM match, using
    _reference_round1_forward (a separate implementation from the solver's
    forward_step/backward_step/mitm_search)."""
    words = dict(fixed["fixed_words"])
    words[8] = word8
    words[9] = word9
    word_list = [words[i] for i in range(16)]
    a9, state16 = _reference_round1_forward(word_list, mode)
    low_k_reference = a9 & ((1 << k) - 1)
    low_m_reference = a9 & ((1 << m) - 1)
    y_match = (state16 == target["Y"])
    target_match = (low_k_reference == target["target_low20"])
    return {
        "verified": bool(y_match and target_match),
        "reference_a9_low20": low_k_reference,
        "declared_target_low20": target["target_low20"],
        "target_match": target_match,
        "reference_round1_output": state16,
        "declared_round1_output_Y": target["Y"],
        "round1_output_match": y_match,
        "method": "_reference_round1_forward (independent of forward_step/"
                  "backward_step/mitm_search)",
    }


# ---------------------------------------------------------------------------
# H2 backward-inversion regression fixture.
# ---------------------------------------------------------------------------

def h2_regression_fixture(seed: int = 8975317, n: int = 10000,
                          mode: str = "md4") -> dict:
    shifts, consts, add_b = _r1_tables(mode)
    rng = random.Random(seed)
    failures = []
    for i in range(n):
        a, b, c, d = (rng.getrandbits(32) for _ in range(4))
        xk = rng.getrandbits(32)
        s = shifts[i % 4]
        t = consts[i % 16]
        state = (a, b, c, d)
        forward = forward_step(state, xk, s, t, add_b)
        back = backward_step(forward, xk, s, t, add_b)
        if back != state:
            failures.append({"index": i, "state": state, "xk": xk, "s": s,
                            "t": t, "forward": forward, "recovered": back})
            if len(failures) >= 20:
                break
    return {"n": n, "mode": mode, "seed": seed, "failures": failures,
           "all_ok": len(failures) == 0}


# ---------------------------------------------------------------------------
# H1 heuristic-validation sampling harness.
# ---------------------------------------------------------------------------

def _poisson_pmf(i: int, lam: float) -> float:
    if i < 0:
        return 0.0
    return math.exp(i * math.log(lam) - lam - math.lgamma(i + 1))


def _poisson_sf(k: int, lam: float) -> float:
    """P(X >= k) for X ~ Poisson(lam), summed directly (lam is O(10^2-10^3)
    at this instrument's declared scale, so direct summation with an
    early-termination tolerance is numerically fine -- no scipy available
    in this environment)."""
    if k <= 0:
        return 1.0
    total = 0.0
    i = k
    term = _poisson_pmf(i, lam)
    # Walk upward from k; Poisson pmf is unimodal and decays fast once
    # i >> lam, so summing until the term (and a look-ahead window) is
    # negligible is safe and terminates quickly for lam in the low hundreds.
    consecutive_negligible = 0
    while i < k + 200000:
        total += term
        i += 1
        term = _poisson_pmf(i, lam)
        if term < 1e-18:
            consecutive_negligible += 1
            if consecutive_negligible > 50:
                break
        else:
            consecutive_negligible = 0
    return min(1.0, total)


def _regularized_gamma_q(a: float, x: float) -> float:
    """Q(a,x), the upper regularized incomplete gamma function, via the
    standard series (x < a+1) / continued-fraction (x >= a+1) split
    (Numerical Recipes 6.2). Used only for the chi-square upper-tail
    p-value; no scipy available in this environment."""
    if x <= 0:
        return 1.0
    if x < a + 1.0:
        # Series for P(a,x), then Q = 1 - P.
        ap = a
        total = 1.0 / a
        delta = total
        for _ in range(500):
            ap += 1
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * 1e-14:
                break
        p = total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return 1.0 - p
    # Continued fraction for Q(a,x) directly (Lentz's method).
    tiny = 1e-300
    b0 = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b0
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b0 += 2.0
        d = an * d + b0
        if abs(d) < tiny:
            d = tiny
        c = b0 + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi_square_goodness_of_fit(observed_counts: list[int], lam: float
                               ) -> dict:
    """Bin the observed matching-window-collision counts against
    Poisson(lam), lam FIXED by HEUR-H1 (no parameters estimated from data,
    so df = n_bins - 1). Bins are centered on lam with width ~ sqrt(lam)/2,
    plus two open tail bins, each merged upward/downward until its expected
    count is >= 5 (the standard chi-square usability rule)."""
    n = len(observed_counts)
    if n == 0:
        return {"n": 0, "note": "no targets completed; chi-square not computed"}
    std = math.sqrt(lam)
    width = max(1, round(std / 2))
    lo_edge = max(0, int(lam - 4 * std))
    hi_edge = int(lam + 4 * std)
    edges = list(range(lo_edge, hi_edge + 1, width))
    if edges[-1] < hi_edge:
        edges.append(hi_edge)
    # bins: (-inf, edges[0]), [edges[0],edges[1]), ..., [edges[-1], +inf)
    bin_edges = [None] + edges + [None]
    counts = [0] * (len(bin_edges) - 1)
    for v in observed_counts:
        placed = False
        for bi in range(len(edges) + 1):
            lo = bin_edges[bi]
            hi = bin_edges[bi + 1]
            if (lo is None or v >= lo) and (hi is None or v < hi):
                counts[bi] += 1
                placed = True
                break
        assert placed
    expected = []
    for bi in range(len(counts)):
        lo = bin_edges[bi]
        hi = bin_edges[bi + 1]
        if lo is None:
            p = sum(_poisson_pmf(i, lam) for i in range(0, hi))
        elif hi is None:
            p = _poisson_sf(lo, lam)
        else:
            p = sum(_poisson_pmf(i, lam) for i in range(lo, hi))
        expected.append(p * n)
    # Merge adjacent bins with expected < 5 into a neighbor (standard rule).
    merged_counts, merged_expected = [], []
    i = 0
    while i < len(counts):
        c, e = counts[i], expected[i]
        j = i
        while e < 5 and j + 1 < len(counts):
            j += 1
            c += counts[j]
            e += expected[j]
        merged_counts.append(c)
        merged_expected.append(e)
        i = j + 1
    if merged_expected and merged_expected[-1] < 5 and len(merged_expected) > 1:
        merged_counts[-2] += merged_counts[-1]
        merged_expected[-2] += merged_expected[-1]
        merged_counts.pop()
        merged_expected.pop()
    chi2 = sum((c - e) ** 2 / e for c, e in zip(merged_counts, merged_expected)
              if e > 0)
    df = max(1, len(merged_counts) - 1)
    p_value = _regularized_gamma_q(df / 2.0, chi2 / 2.0)
    return {
        "n": n, "lambda": lam, "bins": len(merged_counts), "df": df,
        "chi2_statistic": chi2, "p_value": p_value,
        "alpha": 0.05, "below_critical_at_alpha_0_05": p_value > 0.05,
        "observed_counts_by_bin": merged_counts,
        "expected_counts_by_bin": merged_expected,
    }


def h1_sampling(seed: int, mode: str, fixed: dict, k1: int, k2: int, m: int,
                k: int, n_target: int, deadline: float | None) -> dict:
    """Draw independent targets from ONE seeded stream (per
    md4_heuristic_validation_targets / md5_conditional_targets), running the
    exhaustive MITM search on each and recording matching-window and
    full-target hit counts. Halts truthfully at `deadline` (monotonic
    clock), reporting the achieved N -- a budget outcome, not a defect."""
    rng_t = random.Random(seed)
    lam = 2 ** (k1 + k2 - m)
    window_counts: list[int] = []
    full_counts: list[int] = []
    t0 = time.monotonic()
    deadline_abs = (t0 + deadline) if deadline is not None else None
    achieved = 0
    halted = False
    for _ in range(n_target):
        if deadline_abs is not None and time.monotonic() >= deadline_abs:
            halted = True
            break
        low8 = rng_t.getrandbits(k1)
        low9 = rng_t.getrandbits(k2)
        true_word8 = fixed["high8"] | low8
        true_word9 = fixed["high9"] | low9
        words = dict(fixed["fixed_words"])
        words[8] = true_word8
        words[9] = true_word9
        shifts, consts, add_b = _r1_tables(mode)
        word_list = [words[i] for i in range(16)]
        state9 = apply_forward(_IV, word_list[:9], shifts, consts[:9], add_b)
        state16 = apply_forward(state9, word_list[9:16], shifts, consts[9:16], add_b,
                            start_index=9)
        target = {"true_word8": true_word8, "true_word9": true_word9,
                  "target_low20": state9[1] & 0xFFFFF, "Y": state16,
                  "mode": mode, "free_bits": k1}
        res = mitm_search(fixed, target, mode, k1, k2, m, k)
        window_counts.append(res["matching_window_hits"])
        full_counts.append(res["full_target_hits"])
        achieved += 1
    wall = time.monotonic() - t0
    chi2 = chi_square_goodness_of_fit(window_counts, lam)
    largest = max(window_counts) if window_counts else None
    tail_p = _poisson_sf(largest, lam) if largest is not None else None
    return {
        "mode": mode, "seed": seed, "requested_n": n_target,
        "achieved_n": achieved, "halted_before_target_n": halted,
        "internal_wall_seconds": round(wall, 6),
        "lambda_predicted": lam,
        "matching_window_hit_counts": window_counts,
        "full_target_hit_counts": full_counts,
        "mean_matching_window_hits": (sum(window_counts) / achieved
                                      if achieved else None),
        "mean_full_target_hits": (sum(full_counts) / achieved
                                  if achieved else None),
        "chi_square_goodness_of_fit": chi2,
        "tail_check": {
            "largest_observed_matching_window_count": largest,
            "poisson_sf_p_value": tail_p,
            "formula": "P(X >= largest_observed), X ~ Poisson(lambda_predicted)",
        },
    }


# ---------------------------------------------------------------------------
# Script entry point.
# ---------------------------------------------------------------------------

def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Round-1-restricted MD4/MD5 splice-and-cut MITM "
                    "instrument (GOAL-MD5-001 BATCH-af29f6).")
    ap.add_argument("--target", choices=["md4", "md5"], default="md4")
    ap.add_argument("--mode", choices=["primary", "h1", "h2", "brute_control",
                                       "vector_check", "buildcheck"],
                    required=True)
    ap.add_argument("--seed", type=int, default=20260821)
    ap.add_argument("--target-seed", type=int, default=8975313)
    ap.add_argument("--n-target", type=int, default=1000)
    ap.add_argument("--deadline", type=float, default=None)
    ap.add_argument("--k1", type=int, default=10)
    ap.add_argument("--k2", type=int, default=10)
    ap.add_argument("--m", type=int, default=12)
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--out-root", default=None)
    ap.add_argument("--exp-id", default="EXP-MDFIVE-88f7d1")
    ap.add_argument("--exp-area", default="MDFIVE")
    ap.add_argument("--run-suffix", default=None)
    ap.add_argument("--report-path", default=None)
    args = ap.parse_args(argv)

    if args.mode == "vector_check":
        print(json.dumps(check_rfc1320_vectors(), indent=2))
        return 0

    repo = _repo_root()
    if repo not in sys.path:
        sys.path.insert(0, repo)
    from harness import runner

    def fn():
        fixed = fixed_word_generation(args.seed, free_bits=args.k1)
        t0 = time.monotonic()
        if args.mode == "h2":
            raw = h2_regression_fixture(seed=args.target_seed, n=args.n_target
                                        or 10000, mode=args.target)
            metrics = {"n": raw["n"], "failures": len(raw["failures"]),
                      "all_ok": raw["all_ok"]}
            cert = {"kind": "none"}
        elif args.mode == "h1":
            raw = h1_sampling(args.target_seed, args.target, fixed, args.k1,
                              args.k2, args.m, args.k, args.n_target,
                              args.deadline)
            metrics = {"achieved_n": raw["achieved_n"],
                      "halted_before_target_n": raw["halted_before_target_n"],
                      "mean_matching_window_hits": raw["mean_matching_window_hits"],
                      "chi2_statistic": raw["chi_square_goodness_of_fit"].get("chi2_statistic"),
                      "chi2_p_value": raw["chi_square_goodness_of_fit"].get("p_value"),
                      "tail_p_value": raw["tail_check"]["poisson_sf_p_value"]}
            cert = {"kind": "none"}
        elif args.mode == "buildcheck":
            # The single "build/self-test pass" run (budget stopping_rules:
            # maximum_runs 4 = build/self-test pass + primary + H1 + MD5).
            # Bundles ALL correctness gates that must pass BEFORE any search
            # result is trusted: RFC 1320 vectors, H2 (both primitives), and
            # the k1=k2=6 brute-force-equality control (MD4).
            vec = check_rfc1320_vectors()
            h2_md4 = h2_regression_fixture(seed=8975317, n=10000, mode="md4")
            h2_md5 = h2_regression_fixture(seed=8975317, n=10000, mode="md5")
            fixed6 = fixed_word_generation(20260821, free_bits=6)
            target6 = generate_target(8975316, fixed6, "md4", free_bits=6)
            mitm6 = mitm_search(fixed6, target6, "md4", 6, 6, 6, 20)
            naive6 = naive_all_pairs_search(fixed6, target6, "md4", 6, 6, 20)
            equal6 = sorted(mitm6["solutions"]) == sorted(naive6["solutions"])
            raw = {
                "rfc1320_vectors": vec,
                "h2_md4": {"all_ok": h2_md4["all_ok"], "n": h2_md4["n"]},
                "h2_md5": {"all_ok": h2_md5["all_ok"], "n": h2_md5["n"]},
                "brute_control_k6": {
                    "mitm_solutions": mitm6["solutions"],
                    "naive_solutions": naive6["solutions"],
                    "result_sets_equal": equal6,
                    "naive_evaluations": naive6["evaluations"],
                    "true_word8_low6": target6["true_word8"] & 0x3F,
                    "true_word9_low6": target6["true_word9"] & 0x3F,
                },
            }
            all_ok = (vec["all_ok"] and h2_md4["all_ok"] and h2_md5["all_ok"]
                     and equal6)
            metrics = {"rfc1320_vectors_all_ok": vec["all_ok"],
                      "h2_md4_all_ok": h2_md4["all_ok"],
                      "h2_md5_all_ok": h2_md5["all_ok"],
                      "brute_control_result_sets_equal": equal6,
                      "brute_control_mitm_solutions": len(mitm6["solutions"]),
                      "all_gates_passed": all_ok}
            cert = {"kind": "none"}
        elif args.mode == "brute_control":
            target = generate_target(args.target_seed, fixed, args.target,
                                      free_bits=args.k1)
            mitm = mitm_search(fixed, target, args.target, args.k1, args.k2,
                               args.m, args.k)
            naive = naive_all_pairs_search(fixed, target, args.target,
                                           args.k1, args.k2, args.k)
            equal = sorted(mitm["solutions"]) == sorted(naive["solutions"])
            raw = {"mitm": mitm, "naive": naive, "result_sets_equal": equal,
                  "target": {k2_: (v if k2_ != "Y" else list(v))
                             for k2_, v in target.items()}}
            metrics = {"mitm_solutions": len(mitm["solutions"]),
                      "naive_solutions": len(naive["solutions"]),
                      "result_sets_equal": equal,
                      "naive_evaluations": naive["evaluations"]}
            cert = {"kind": "none"}
        else:  # primary
            target = generate_target(args.target_seed, fixed, args.target,
                                     free_bits=args.k1)
            mitm = mitm_search(fixed, target, args.target, args.k1, args.k2,
                               args.m, args.k)
            found = len(mitm["solutions"]) > 0
            # Independently re-verify EVERY raw MITM "solution" (cheap at
            # this declared scale: at most 2^k2 candidates), not just the
            # first found. ANOMALY, disclosed in execution-report.yaml: this
            # module's own analysis found that register-A-after-step-9 (the
            # declared matching quantity) is provably independent of free
            # word9 (word9 is first used at step 10, strictly AFTER step 9),
            # so mitm_search's raw solution SET is expected to contain every
            # word9 paired with whichever word8 hits the target -- a false-
            # positive rate, not a defect in verify_match_certificate, which
            # is exactly what catches it here.
            verifications = [
                (w8, w9, verify_match_certificate(fixed, target, args.target,
                                                  w8, w9, args.m, args.k))
                for (w8, w9) in mitm["solutions"]
            ]
            genuinely_verified = [(w8, w9) for (w8, w9, v) in verifications
                                  if v["verified"]]
            first_verify = verifications[0][2] if verifications else None
            naive_cost = (1 << args.k1) * (1 << args.k2)
            raw = {
                "mitm": mitm,
                "target": {k2_: (v if k2_ != "Y" else list(v))
                          for k2_, v in target.items()},
                "independent_verification_of_first_found": first_verify,
                "genuinely_verified_solutions": genuinely_verified,
                "genuinely_verified_count": len(genuinely_verified),
                "raw_solution_count": len(mitm["solutions"]),
                "naive_baseline_cost": naive_cost,
                "speedup_vs_naive": (naive_cost / mitm["total_chunk_evaluations"]),
            }
            metrics = {
                "full_target_hits": mitm["full_target_hits"],
                "matching_window_hits": mitm["matching_window_hits"],
                "chunk_evals_to_first_full_match": mitm["chunk_evals_to_first_full_match"],
                "total_chunk_evaluations": mitm["total_chunk_evaluations"],
                "naive_baseline_cost": naive_cost,
                "found": found,
                "raw_solution_count": len(mitm["solutions"]),
                "genuinely_verified_count": len(genuinely_verified),
                "independently_verified_first_found": (first_verify["verified"]
                                                       if first_verify else None),
            }
            cert = {"kind": "none"}
        t1 = time.monotonic()
        return runner.RunResult(
            run_suffix=(args.run_suffix or f"{args.mode}-{args.target}-s{args.seed}"),
            curve_id=f"MD4CEIL-{args.target.upper()}", seed=args.seed,
            parameters={"mode": args.mode, "target": args.target,
                       "k1": args.k1, "k2": args.k2, "m": args.m, "k": args.k,
                       "seed": args.seed, "target_seed": args.target_seed,
                       "n_target": args.n_target, "deadline": args.deadline},
            metrics=metrics, certificate=cert, raw=raw,
            stdout=json.dumps(raw, indent=2, sort_keys=True, default=str) + "\n")

    run_id = runner.run_wrapped(args.exp_id, args.exp_area, fn,
                                status="completed_valid",
                                command=" ".join(sys.argv),
                                out_root=args.out_root)
    if args.report_path or args.out_root:
        run_dir = os.path.join(args.out_root, "runs", run_id)
        with open(os.path.join(run_dir, "raw-result.json")) as fh:
            raw = json.load(fh)["raw"]
        report_path = args.report_path or os.path.join(
            args.out_root, f"search-report-{args.run_suffix or args.mode}.json")
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(raw, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
