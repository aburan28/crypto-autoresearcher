"""harness/run_md4_calib.py -- Bounded MD4 collision-path search instrument.

GOAL-MD5-001 / BATCH-04272f / TASK-20260821-c4a158 (RANK 3, the MD4 control).

This module IS the instrument the two MD4 control runs execute:
  RUN TARGET      standard MD4 constants        (--variant-shift 0)
  RUN NULL OBJECT the ruled null variant        (--variant-shift 16)
                  (round-constant sequence cyclically shifted by 16 over the
                  48-entry sequence: round 1 -> 0x5A827999, round 2 ->
                  0x6ED9EBA1, round 3 -> 0).
It is a single module, runnable as a script, and importable (the runs drive
``search()`` through ``harness.runner.run_wrapped`` so the charged
``wall_seconds`` is wrapper-measured, per BCP-2 charging_convention).

The solver core (the MD4 below and the search) uses NO standard-library MD4
binding (Python 3.12's hashlib has no md4 in this build -- verified at
authoring time; the module imports no hash library at all). The MD5 module
(harness/run_md5_calib.py) is NOT imported and its code path is NOT reused:
the MD4 core is written independently FROM the filed RFC 1320 text.

VERIFICATION ORACLE (per the rank3_ruling in the committed dispatch queue,
coordination/goals/GOAL-MD5-001/batches/BATCH-04272f/dispatch_queue.json):
  (i)   the RFC 1320 official test vectors (section A.5) are a GATE that must
        pass before any search; the gate result is recorded in the raw result
        and the manifest;
  (ii)  a second, INDEPENDENT MD4 implementation (the MD4Checker class below,
        a distinct code path from the solver core: class-based streaming
        structure mirroring the RFC 1320 appendix A C reference, versus the
        solver core's functional one-pass schedule-table structure) serves as
        the certificate / partial-hit checker. The fallback (test vectors +
        structural self-check only) is NOT used: the independent second
        implementation is feasible and is present.
  hashlib.md4 (if available) would serve ONLY as an additional verification
  oracle (provenance: system-library, verification-only, never in the solver
  core); in this build it is NOT available (AttributeError at authoring time)
  and is recorded as such.

=============================================================================
DECLARED SEARCH STRATEGY  (fixed BEFORE any run -- fixed_before_acquisition)
=============================================================================
OBJECT
  Identical-prefix 2-block messages  M1 = B1 || B2 ,  M2 = B1 || B2' ,
  where B1 is a fixed 512-bit block derived from the seed, and B2, B2' are
  distinct random 512-bit blocks (16 little-endian 32-bit words each).
  Messages are hex-encoded (128 hex chars each). The collision target is
  equality of the FULL 128-bit MD4 digest of the two full messages, with
  M1 != M2.

SEARCH
  A bounded BIRTHDAY (collision-by-enumeration) search over the 128-bit
  digest space of the identical-prefix 2-block messages. The search
  enumerates up to N = 2^21 distinct seeded random second blocks, computes
  each full 2-block digest (all 48 steps of the schedule, one compression
  pass per block), and inserts (digest, block) into a hash TABLE keyed by
  the digest's low k = 40 bits. A table HIT (two distinct blocks with the
  same 40-bit key) is a 40-bit digest-prefix collision -- a PARTIAL result.
  The search continues to collect hits and tracks the longest matching
  prefix of the full 128-bit digests and the cost (blocks evaluated) at
  which it was achieved. A full 128-bit digest match (two distinct blocks
  with identical full digests) is SUCCESS.

  TECHNIQUE NOTE: this is a birthday search, NOT a meet-in-the-middle and
  NOT a differential-path search (per the ruled run scope). It does not
  split the 48-step schedule into independent halves meeting on an
  intermediate state; it computes each full digest and detects collisions
  in the digest space via the low-40-bit hash table.

WINDOW
  Not a search window. The 48-step schedule is MD4's inherent three 16-step
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
  evidence about MD4.

WHAT IT CANNOT REACH  (named OPEN, not silently omitted)
  A full 128-bit digest match requires ~2^64 second blocks (birthday bound)
  at this encoding. That is far beyond the declared N = 2^21 and the 900 s
  ceiling, so the instrument is BOUNDED by design: it is a calibration
  instrument, not a cryptanalytic campaign. The full-48-step state matching
  at 2^64 scale is named OPEN.

DETERMINISM
  A single ``--seed`` (the runs use seed 0) drives every stochastic element
  (B1 derivation and the B2 enumeration order). No other source of
  randomness exists.

VARIANT
  ``--variant-shift N`` (default 0): the round constants used are
  T[(i+N) mod 48] over the 48-entry MD4 constant sequence. N=0 is standard
  MD4; N=16 is the ruled null variant (round 1 -> 0x5A827999, round 2 ->
  0x6ED9EBA1, round 3 -> 0). The variant is the ONLY difference between the
  target and null runs: the schedule word order, rotations, IV,
  Merkle-Damgard chaining, and step count are identical.

NOT A DIFFERENTIAL-PATH SEARCH
  This instrument uses NO differential characteristic, NO neutral words, and
  NO bit conditions. It is a plain bounded birthday/fragment search,
  deliberately, so the control measures the instrument's raw bounded-search
  capability at a declared scale rather than its ability to recall or
  reconstruct a published differential path.

COVERAGE BOUNDARY
  The search depth is BOUNDED by design. What it cannot reach (full 48-step
  state matching at 2^64 scale) is named OPEN above. A budgeted FAIL of the
  search runs is an admissible, complete observation (SC-4); the
  instrument's job is to be honest about its ceiling.
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
# Standalone MD4, written FROM the filed RFC 1320 primary text
# (coordination/goals/GOAL-MD5-001/batches/BATCH-04272f/inputs/rfc1320-md4.txt,
# sha256 f727b15e19ab8ac5036ab7921476e8d8644512190ade32a2e0a2fb9d8a2421c7).
# Sections used: 3.1/3.2 (Merkle-Damgard padding + length), 3.3 (initial MD
# buffer), 3.4 (step functions F/G/H, the round constants, the 48-step
# schedule), 3.5 (output), A.5 (the official test suite). The solver core
# imports no standard-library MD4 binding (none exists in this build) and
# does not reuse the MD5 module's code path.
# ---------------------------------------------------------------------------

_M32 = (1 << 32) - 1

# RFC 1320 section 3.3: initial MD buffer (A, B, C, D), low-order bytes first:
#   word A: 01 23 45 67   word B: 89 ab cd ef
#   word C: fe dc ba 98   word D: 76 54 32 10
_IV = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)

# RFC 1320 section 3.4: the 48-entry round-constant sequence. Round 1 has NO
# additive constant; round 2 adds 0x5A827999 (the RFC: "This constant
# represents the square root of 2", i.e. floor(2^30*sqrt(2))); round 3 adds
# 0x6ED9EBA1 (floor(2^30*sqrt(3))). The MD5 instrument's 64-entry sine table
# does NOT apply to MD4 (task-card instruction defect, ruled in the RANK 1
# adjudication and the rank3_ruling).
_C2 = 0x5A827999
_C3 = 0x6ED9EBA1
_T48 = (
    (0,) * 16 + (_C2,) * 16 + (_C3,) * 16
)

# RFC 1320 section 3.4: the 48-step schedule (message-word index k, rotation
# s) for steps 0..47, with the register rotation ABCD, DABC, CDAB, BCDA.
# Transcribed from the RFC's operation tables (and its appendix A.3
# MD4Transform); every entry is re-verified against the transcribed tables
# at import by _check_table().
_SCHEDULE48 = (
    # Round 1: [ABCD k 3] [DABC k 7] [CDAB k 11] [BCDA k 19], k = 0..15
    (0, 3), (1, 7), (2, 11), (3, 19),
    (4, 3), (5, 7), (6, 11), (7, 19),
    (8, 3), (9, 7), (10, 11), (11, 19),
    (12, 3), (13, 7), (14, 11), (15, 19),
    # Round 2: k = 0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15; s = 3,5,9,13
    (0, 3), (4, 5), (8, 9), (12, 13),
    (1, 3), (5, 5), (9, 9), (13, 13),
    (2, 3), (6, 5), (10, 9), (14, 13),
    (3, 3), (7, 5), (11, 9), (15, 13),
    # Round 3: k = 0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15; s = 3,9,11,15
    (0, 3), (8, 9), (4, 11), (12, 15),
    (2, 3), (10, 9), (6, 11), (14, 15),
    (1, 3), (9, 9), (5, 11), (13, 15),
    (3, 3), (11, 9), (7, 11), (15, 15),
)

# The RFC 1320 section 3.4 operation tables, transcribed independently of
# _SCHEDULE48 (the appendix A.3 FF/GG/HH call order), for the import-time
# cross-check.
_R1_K = tuple(range(16))
_R1_S = (3, 7, 11, 19)
_R2_K = (0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15)
_R2_S = (3, 5, 9, 13)
_R3_K = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
_R3_S = (3, 9, 11, 15)


def _check_table() -> None:
    """Self-check at import: the transcribed constants and schedule must
    match the RFC 1320 section 3.4 tables. A transcription error fails
    loudly here, not inside a run."""
    if len(_T48) != 48:
        raise ValueError(f"constant sequence must have 48 entries, has {len(_T48)}")
    if any(t != 0 for t in _T48[:16]):
        raise ValueError("round 1 must carry no additive constant")
    if any(t != _C2 for t in _T48[16:32]):
        raise ValueError("round 2 must carry 0x5A827999 at every step")
    if any(t != _C3 for t in _T48[32:48]):
        raise ValueError("round 3 must carry 0x6ED9EBA1 at every step")
    # The RFC's stated constant definitions (floor(2^30*sqrt(2)) /
    # floor(2^30*sqrt(3))), per the RANK 1 adjudication of the filed text.
    if int(2 ** 30 * math.sqrt(2)) != _C2:
        raise ValueError(f"0x5A827999 != floor(2^30*sqrt(2)): {_C2:#x}")
    if int(2 ** 30 * math.sqrt(3)) != _C3:
        raise ValueError(f"0x6ED9EBA1 != floor(2^30*sqrt(3)): {_C3:#x}")
    if len(_SCHEDULE48) != 48:
        raise ValueError(f"schedule must have 48 steps, has {len(_SCHEDULE48)}")
    expected = (
        tuple((k, _R1_S[j % 4]) for j, k in enumerate(_R1_K))
        + tuple((k, _R2_S[j % 4]) for j, k in enumerate(_R2_K))
        + tuple((k, _R3_S[j % 4]) for j, k in enumerate(_R3_K))
    )
    if _SCHEDULE48 != expected:
        raise ValueError("schedule transcription error vs RFC 1320 section 3.4")


_check_table()


def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & _M32


def _compress(state, words, shift: int = 0):
    """One 48-step MD4 compression (RFC 1320 section 3.4).

    ``state`` is (a, b, c, d) 32-bit words; ``words`` is a 16-tuple of 32-bit
    message words. ``shift`` cyclically shifts the round constants to
    T[(i+shift) mod 48] (0 = standard MD4; 16 = the ruled null variant).
    Returns the new state including the RFC's end-of-block additions
    (A = A + AA, B = B + BB, C = C + CC, D = D + DD).

    NOTE (MD4 vs MD5): the RFC 1320 operation is
    ``a = (a + f(b,c,d) + X[k] + const) <<< s`` -- there is NO ``b +`` term.
    (RFC 1321's MD5 operation carries ``a = b + ((a + f + X[k] + T[i]) <<< s)``
    in all four rounds; that term is an MD5 property, not an MD4 one. The
    difference is visible in the two RFCs' appendix C macros: MD4's FF/GG/HH
    have no ``(a) += (b)`` line, MD5's do.)
    """
    a, b, c, d = state
    x = words
    T = _T48
    for i in range(48):
        k, s = _SCHEDULE48[i]
        if i < 16:
            f = (b & c) | ((~b & _M32) & d)        # F(X,Y,Z) = XY v not(X) Z
        elif i < 32:
            f = (b & c) | (b & d) | (c & d)        # G(X,Y,Z) = XY v XZ v YZ
        else:
            f = b ^ c ^ d                          # H(X,Y,Z) = X xor Y xor Z
        new_a = _rotl((a + f + x[k] + T[(i + shift) % 48]) & _M32, s)
        a, b, c, d = d, new_a, b, c
    return ((a + state[0]) & _M32, (b + state[1]) & _M32,
            (c + state[2]) & _M32, (d + state[3]) & _M32)


def _pad(message: bytes) -> bytes:
    """RFC 1320 sections 3.1 (append padding bits) and 3.2 (append length)."""
    bit_len = len(message) * 8
    msg = message + b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    msg += bit_len.to_bytes(8, "little")   # 64-bit length, low-order word first
    return msg


def _state_to_int(state) -> int:
    """RFC 1320 section 3.5: the digest is A, B, C, D, beginning with the
    low-order byte of A and ending with the high-order byte of D -- each
    word emitted little-endian (low byte first). As a 128-bit integer the
    most significant byte is the low-order byte of A, so ``format(digest,
    '032x')`` reproduces the canonical hex digest."""
    out = bytearray()
    for w in state:
        out += w.to_bytes(4, "little")
    return int.from_bytes(out, "big")


def md4_digest(message: bytes, shift: int = 0) -> int:
    """Full 128-bit MD4 digest of ``message`` as an integer (Merkle-Damgard).

    ``shift`` is the round-constant cyclic shift (0 = standard MD4)."""
    state = _IV
    padded = _pad(message)
    for off in range(0, len(padded), 64):
        block = padded[off:off + 64]
        words = tuple(int.from_bytes(block[j * 4:j * 4 + 4], "little")
                      for j in range(16))
        state = _compress(state, words, shift)
    return _state_to_int(state)


def md4_hex(message: bytes, shift: int = 0) -> str:
    return format(md4_digest(message, shift), "032x")


# ---------------------------------------------------------------------------
# Second, INDEPENDENT MD4 implementation (the certificate / partial-hit
# checker, per the rank3_ruling verification oracle (ii)).
#
# Distinct code path from the solver core, deliberately:
#   - class-based streaming structure (update/digest) mirroring the RFC 1320
#     appendix A C reference (MD4Init / MD4Update / MD4Final with a 64-byte
#     input buffer and a 64-bit bit counter), versus the solver core's
#     functional one-pass schedule-table structure;
#   - the transform is written as three explicit 16-step round loops with
#     per-round k/s arrays and FF/GG/HH-style helpers, versus the solver
#     core's single flat 48-entry schedule loop;
#   - register rotation is done by index into a list, versus the solver
#     core's tuple reassignment.
# The constants are the same because they are the specification, not the
# code path. This implementation is used ONLY for verification (test-vector
# cross-check, partial-hit re-check, success verification), never for the
# search.
# ---------------------------------------------------------------------------

class MD4Checker:
    """Independent MD4 (RFC 1320), streaming form, verification-only."""

    _PAD = b"\x80" + b"\x00" * 63

    def __init__(self, shift: int = 0):
        self._shift = shift
        self._state = list(_IV)
        self._count = 0            # total message bits (mod 2^64)
        self._buffer = b""
        self._final = None         # digest cache (digest() pads in place)

    # -- RFC 1320 appendix A.3 transform, explicit-round form -------------
    # FF/GG/HH mirror the appendix macros (a = (a + f(b,c,d) + x + const)
    # <<< s; NO b+ term -- the MD4 form, see _compress's note). The
    # ``const`` argument carries the (possibly shifted) round constant so
    # the checker verifies the variant runs too.
    def _ff(self, a, b, c, d, x, s, const):
        return _rotl((a + ((b & c) | ((~b & _M32) & d)) + x + const) & _M32, s)

    def _gg(self, a, b, c, d, x, s, const):
        return _rotl((a + ((b & c) | (b & d) | (c & d)) + x + const) & _M32, s)

    def _hh(self, a, b, c, d, x, s, const):
        return _rotl((a + (b ^ c ^ d) + x + const) & _M32, s)

    def _transform(self, block: bytes) -> None:
        st = self._state
        x = [int.from_bytes(block[j * 4:j * 4 + 4], "little") for j in range(16)]
        a, b, c, d = st
        T = _T48
        sh = self._shift
        for j in range(16):
            a = self._ff(a, b, c, d, x[_R1_K[j]], _R1_S[j % 4],
                         T[(j + sh) % 48])
            a, b, c, d = d, a, b, c
        for j in range(16):
            a = self._gg(a, b, c, d, x[_R2_K[j]], _R2_S[j % 4],
                         T[(16 + j + sh) % 48])
            a, b, c, d = d, a, b, c
        for j in range(16):
            a = self._hh(a, b, c, d, x[_R3_K[j]], _R3_S[j % 4],
                         T[(32 + j + sh) % 48])
            a, b, c, d = d, a, b, c
        st[0] = (st[0] + a) & _M32
        st[1] = (st[1] + b) & _M32
        st[2] = (st[2] + c) & _M32
        st[3] = (st[3] + d) & _M32

    # -- streaming interface ------------------------------------------------
    def update(self, data: bytes) -> None:
        self._final = None
        self._count = (self._count + len(data) * 8) & ((1 << 64) - 1)
        self._buffer += data
        while len(self._buffer) >= 64:
            self._transform(self._buffer[:64])
            self._buffer = self._buffer[64:]

    def digest(self) -> bytes:
        if self._final is not None:
            return self._final
        # RFC 1320 3.1/3.2: pad to 448 mod 512 bits, append the 64-bit
        # length (low-order word first). Padding length per the appendix
        # A.3 MD4Final: index = byte count mod 64; padLen = (index < 56)
        # ? (56 - index) : (120 - index).
        bits = self._count.to_bytes(8, "little")   # save BEFORE padding
        index = (self._count >> 3) & 0x3F
        pad_len = (56 - index) if index < 56 else (120 - index)
        # pad_len INCLUDES the 0x80 byte (PADDING[0] = 0x80 in the C
        # reference: MD4Update(context, PADDING, padLen)).
        self.update(self._PAD[:pad_len])
        self.update(bits)
        out = bytearray()
        for w in self._state:
            out += w.to_bytes(4, "little")
        self._final = bytes(out)
        return self._final

    def hexdigest(self) -> str:
        return self.digest().hex()


def md4_check_hex(message: bytes, shift: int = 0) -> str:
    """Independent-implementation digest (verification only)."""
    checker = MD4Checker(shift)
    checker.update(message)
    return checker.hexdigest()


# ---------------------------------------------------------------------------
# RFC 1320 section A.5 official test suite (the verification oracle (i)).
# Transcribed from the filed text's "A.5 Test suite" section.
# ---------------------------------------------------------------------------

# The seventh message is the 80-character string "1234567890" x 8, exactly as
# given by BOTH the filed text's A.4 driver (MDTestSuite, the 40+40-char C
# string literal) and its A.5 suite listing (the line wrap splits the ninth
# group: "...123456" / "78901234567890"). The A.5 digest
# e33b4ddc9c38f2199c3e7b164fcc0536 is reproduced by this instrument for
# exactly that 80-character message (verified at the smoke gate).
RFC1320_TEST_VECTORS = (
    ("", "31d6cfe0d16ae931b73c59d7e0c089c0"),
    ("a", "bde52cb31de33e46245e05fbdbd6fb24"),
    ("abc", "a448017aaf21d8525fc10ae87aa6729d"),
    ("message digest", "d9130a8164549fe818874806e1c7014b"),
    ("abcdefghijklmnopqrstuvwxyz", "d79e1c308aa5bbcdeea8ed63df412da9"),
    ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
     "043f8582f241db351ce627e153e7f0e4"),
    ("1234567890" * 8, "e33b4ddc9c38f2199c3e7b164fcc0536"),
)


def run_test_vector_gate() -> dict:
    """The verification oracle (i): every RFC 1320 A.5 vector must pass on
    BOTH the solver core and the independent checker (shift 0). Returns the
    per-vector pass/fail table plus the overall gate result."""
    rows = []
    all_pass = True
    for msg, expected in RFC1320_TEST_VECTORS:
        core = md4_hex(msg.encode("ascii"), 0)
        checker = md4_check_hex(msg.encode("ascii"), 0)
        ok = (core == expected) and (checker == expected)
        all_pass = all_pass and ok
        rows.append({
            "message": msg if msg else "(empty string)",
            "expected": expected,
            "solver_core": core,
            "independent_checker": checker,
            "pass": ok,
        })
    return {"gate": "PASS" if all_pass else "FAIL",
            "vectors": rows,
            "all_pass": all_pass}


# ---------------------------------------------------------------------------
# The declared bounded search
# ---------------------------------------------------------------------------

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


def search(seed: int = 0, variant_shift: int = 0, deadline: float | None = None,
           n_max: int = 2 ** 21, k_bits: int = 40) -> dict:
    """Run the declared bounded search (see the module docstring).

    The RFC 1320 test-vector gate runs FIRST (verification oracle (i)); a
    gate failure returns immediately with stop_reason
    "test_vector_gate_failed" and no block is evaluated (a broken core must
    not search). Returns the raw result dict: outcome, stop reason, the
    search space explored, the strongest partial result (longest matching
    digest-prefix and the cost at which it was achieved), and the internal
    counters. On SUCCESS it carries the two hex messages, the claimed
    digest, and the in-run independent verification (weaker acceptance
    path: no md4_collision_pair certificate kind exists in
    harness/runner.py in this batch, SC-6).
    """
    gate = run_test_vector_gate()
    if not gate["all_pass"]:
        return {
            "outcome": "FAIL",
            "stop_reason": "test_vector_gate_failed",
            "seed": seed,
            "variant_shift": variant_shift,
            "k_bits": k_bits,
            "n_max": n_max,
            "blocks_evaluated": 0,
            "fragments_tried": 0,
            "table_size": 0,
            "partial_hits": 0,
            "best_prefix_bits": 0,
            "best_prefix_cost_blocks": None,
            "b1_hex": None,
            "search_space_explored":
                "none (the RFC 1320 test-vector gate failed before the "
                "search; build defect, no search executed)",
            "test_vector_gate": gate,
            "internal_wall_seconds_not_charged": 0.0,
        }

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
        fragments_tried += 3          # 3 x 16-step round fragments per block
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
            f"window = 16-step round fragments (3 per block)"),
        "test_vector_gate": gate,
        "internal_wall_seconds_not_charged": round(time.monotonic() - t0, 6),
    }
    if outcome == "SUCCESS":
        # In-run independent verification (verification oracle (ii)): the
        # second, distinct-code-path implementation recomputes both digests.
        # WEAKER ACCEPTANCE PATH (named, per the task card / SC-6): no
        # md4_collision_pair certificate kind exists in harness/runner.py in
        # this batch, so the wrapper cannot re-verify the pair; this in-run
        # check is the available verification and is recorded as such.
        v1 = md4_check_hex(bytes.fromhex(m1_hex), variant_shift)
        v2 = md4_check_hex(bytes.fromhex(m2_hex), variant_shift)
        result["messages"] = [m1_hex, m2_hex]
        result["digest"] = digest_hex
        result["success_verification"] = {
            "m1_not_equal_m2": m1_hex != m2_hex,
            "independent_checker_digest_m1": v1,
            "independent_checker_digest_m2": v2,
            "claimed_digest": digest_hex,
            "all_equal": (v1 == v2 == digest_hex),
            "weaker_acceptance_path": (
                "no md4_collision_pair certificate kind exists in "
                "harness/runner.py in this batch (SC-6: no in-batch "
                "addition); the pair is verified in-run by the second "
                "independent MD4 implementation, never as "
                "md5_collision_pair-grade acceptance"),
        }
        result["certificate"] = {
            "kind": "none",
            "note": (
                "certificate kind none: no md4_collision_pair kind exists in "
                "harness/runner.py in this batch (SC-6); the full-128 pair "
                "and its in-run independent verification are recorded in "
                "raw['success_verification'] with the weaker-acceptance-path "
                "limitation named"),
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
        description="Bounded MD4 collision-path search instrument "
                    "(GOAL-MD5-001 BATCH-04272f, the MD4 control).")
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
    ap.add_argument("--self-test", action="store_true",
                    help="run the RFC 1320 test-vector gate only and exit "
                         "(the smoke step; no search, no run record)")
    args = ap.parse_args(argv)

    if args.self_test:
        gate = run_test_vector_gate()
        print(json.dumps(gate, indent=2, sort_keys=True))
        return 0 if gate["all_pass"] else 1

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
                        or f"md4-v{args.variant_shift}-s{args.seed}"),
            curve_id="MD4", seed=args.seed,
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
            args.out_root, f"search-report-{args.run_suffix or 'md4'}.json")
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
