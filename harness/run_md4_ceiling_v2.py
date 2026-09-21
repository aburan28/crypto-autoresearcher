"""harness/run_md4_ceiling_v2.py -- R1-SEP10: a genuinely two-free-word
Round-1 splice-and-cut MITM instrument against MD4 (control) and, strictly
under md5_run_authorization, MD5's Round 1 (nearby-object control).

GOAL-MD5-001 / BATCH-7215fa / TASK-20260821-372d67, executing the FROZEN
contract EXP-MDFIVE-a8e71e (hypothesis H-MDFIVE-0ca596, approving decision
DEC-20260821-333267).

=============================================================================
WHY THIS IS A NEW SIBLING MODULE
=============================================================================
harness/run_md4_ceiling.py is BATCH-af29f6's FROZEN instrument of record and
is neither edited nor imported from (EXP-MDFIVE-a8e71e IR-7). Its construction
(free words 8 and 9, split S=9, component p=1) is DEGENERATE: the declared
matching observable is provably independent of free word 9, recorded as ANOM-1
(KN-TECH-bb7e9f; DEC-20260821-1215e5). Every raw metric of BATCH-af29f6 that
is cited anywhere carries that caveat. harness/run_md5_calib.py (BATCH-1f30fe)
is likewise untouched.

=============================================================================
INPUT PROVENANCE -- COMMITTED PINS, NOT RE-FETCHED
=============================================================================
MD4: RFC 1320, pinned at
  coordination/goals/GOAL-MD5-001/batches/BATCH-af29f6/inputs/rfc1320-md4.txt
  sha256 f727b15e19ab8ac5036ab7921476e8d8644512190ade32a2e0a2fb9d8a2421c7
MD5: RFC 1321 Appendix A.3, pinned at
  coordination/goals/GOAL-MD5-001/batches/BATCH-1f30fe/inputs/rfc1321-md5.txt
  sha256 284a79d148400d9cd2a423211d1103b5cef0fb9256a4cbe6d7ebe5197c3149dd
Both are re-hashed at run time by `check_input_pins()` and the result is
recorded in every run's raw output. The step arithmetic, shift tables and
constants below are transcribed from those pinned texts. The solver core
imports NO hashlib and no third-party MD4/MD5 binding; `hashlib` appears in
this file only inside `check_input_pins()`, which hashes FILES, never message
blocks, and is never called by any search path.

=============================================================================
THE CONSTRUCTION, PARAMETERIZED (A-6 / PO-8: NO BRANCHING BEYOND THE TUPLE)
=============================================================================
ConstructionParams(primitive, i_word, j_word, S, p, k1, k2, m, k).

  chunk1_observable(w_a, params, fixed)
      forward from the standard IV over words 0..S-1 with word[i_word] = w_a;
      return tuple position `p` of state_S.
  chunk2_observable(w_b, Y, params, fixed)
      backward from Y (the Round-1 output state) inverting steps 16 down to
      S+1, i.e. words 15 down to S, with word[j_word] = w_b; return tuple
      position `p` of state_S.

These two functions are THE ONLY way any phase of this module reads the
declared matching observable -- the null control G-0, the k1=k2=4 gate, the
k1=k2=6 controls, the declared-scale primary run, the H1 sampler and the MD5
arm all call exactly these, and they contain NO primitive-specific and NO
phase-specific branching beyond the parameter tuple. Selecting shifts,
constants and the add_b convention from `params.primitive` IS the tuple.

TUPLE-POSITION CONVENTION (the named confounder CTL-PO9 checks)
  state_n[1] = register produced at step n
  state_n[2] = register produced at step n-1
  state_n[3] = register produced at step n-2
  state_n[0] = register produced at step n-3
  So R1-SEP10's (S=8, p=3) reads v6, the register produced at step 6, and the
  batch-4 slice's (S=9, p=1) reads v9. `component_step(S, p)` encodes this and
  CTL-PO9 asserts it against an INDEPENDENT straight-line named-register
  reference implementation before the gate runs.

R1-SEP10: i_word=2 (consumed at step 3), j_word=12 (consumed at step 13),
S=8, p=3, m=12, k=20. Free-word separation j-i = 10.
Batch-4 slice (G-0, the detector null control): i_word=8, j_word=9, S=9, p=1.

=============================================================================
THE NAIVE BASELINE IS INDEPENDENT (CTL-PO4)
=============================================================================
`naive_y_reproducing_search` enumerates all 2^(k1+k2) pairs and, for each,
runs `_reference_round1_output` -- a straight-line 16-step forward
recomputation with named a,b,c,d registers -- comparing the resulting Round-1
output state to Y. It NEVER calls backward_step, NEVER reads component p, and
NEVER reads the matching window. BATCH-af29f6's baseline compared low_k_fwd
against low_k_bwd, i.e. it read the same observable the MITM read, and was
therefore vacuous (EV-MDFIVE-ab007d O-2, ANOM-1 CAVEAT). That is not
reproduced here.

=============================================================================
DETERMINISM -- the nine frozen seeds (EXP-MDFIVE-a8e71e.inputs.seeds)
=============================================================================
  20260821  fixed_word_generation
  8975321   G-0 batch-4-slice target (md4)
  8975322   gate target (md4)
  8975323   k1=k2=6 control target (md4)
  8975324   primary target (md4)
  8975325   H1 target stream (md4)
  8975326   H1 target stream (md5)
  8975327   H2 inversion fixture
  8975328   gate target (md5, phase C)
No other source of randomness exists in this module.

=============================================================================
CAVEAT_REFS (SC-5, DEC-20260821-1215e5 F-4, red-team required_controls D2)
=============================================================================
`CAVEAT_REFS` below is emitted into the MANIFEST OUTPUT of every run this
module writes. It is placed inside `parameters` and `cost_model`, which
harness/runner.py records VERBATIM in manifest.yaml, because harness/runner.py
is outside this task's write_scope and a top-level manifest key cannot be
added without editing it. The field is present, named `caveat_refs`, and
machine-readable from manifest.yaml alone; the placement is recorded as a
protocol deviation in the execution report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass, replace

_M32 = (1 << 32) - 1
_IV = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476)

CAVEAT_REFS = [
    "KN-TECH-bb7e9f: ANOM-1 -- BATCH-af29f6's construction was degenerate in "
    "free word 9; every BATCH-af29f6 raw metric cited anywhere downstream "
    "carries this caveat.",
    "DEC-20260821-1215e5 F-4: any record citing RUN-MDFIVE-primary-md4-v2, "
    "RUN-MDFIVE-h1-md4 or RUN-MDFIVE-md5-conditional raw metrics must carry "
    "the ANOM-1 caveat forward.",
    "EXP-MDFIVE-a8e71e IR-9: the MD5/MD4 full-target-hit ratio R is declared "
    "in advance to be uninformative at these parameters and is FORBIDDEN as a "
    "finding in either direction.",
    "EXP-MDFIVE-a8e71e IR-10: no cost figure from this batch or BATCH-af29f6 "
    "may project toward the approximately 2^64-block instrument-class gap.",
]

INPUT_PINS = {
    "md4_rfc1320": (
        "coordination/goals/GOAL-MD5-001/batches/BATCH-af29f6/inputs/"
        "rfc1320-md4.txt",
        "f727b15e19ab8ac5036ab7921476e8d8644512190ade32a2e0a2fb9d8a2421c7"),
    "md5_rfc1321": (
        "coordination/goals/GOAL-MD5-001/batches/BATCH-1f30fe/inputs/"
        "rfc1321-md5.txt",
        "284a79d148400d9cd2a423211d1103b5cef0fb9256a4cbe6d7ebe5197c3149dd"),
}


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_input_pins() -> dict:
    """Re-hash the two committed RFC pins. Hashes FILES only; never touches a
    message block and is never called by any search path."""
    out = {}
    for name, (rel, expected) in INPUT_PINS.items():
        path = os.path.join(_repo_root(), rel)
        try:
            with open(path, "rb") as fh:
                got = hashlib.sha256(fh.read()).hexdigest()
        except OSError as exc:
            out[name] = {"path": rel, "expected": expected, "got": None,
                         "ok": False, "error": str(exc)}
            continue
        out[name] = {"path": rel, "expected": expected, "got": got,
                     "ok": got == expected}
    out["all_ok"] = all(v["ok"] for k, v in out.items() if k != "all_ok")
    return out


# ---------------------------------------------------------------------------
# Round-1 arithmetic (RFC 1320 sec 3.4 / RFC 1321 sec 3.4).
# ---------------------------------------------------------------------------

def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & _M32


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & _M32


def _f(x: int, y: int, z: int) -> int:
    """Round 1: F(X,Y,Z) = XY v not(X)Z. Identical in RFC 1320 and RFC 1321."""
    return (x & y) | ((~x & _M32) & z)


def _g(x: int, y: int, z: int) -> int:
    """RFC 1320 Round 2: G(X,Y,Z) = XY v XZ v YZ."""
    return (x & y) | (x & z) | (y & z)


def _h(x: int, y: int, z: int) -> int:
    """RFC 1320 Round 3: H(X,Y,Z) = X xor Y xor Z."""
    return x ^ y ^ z


MD4_R1_SHIFTS = (3, 7, 11, 19)
MD4_R1_CONSTS = (0,) * 16      # RFC 1320 sec 3.4: Round 1 has no constant.
MD4_ADD_B = False              # RFC 1320's "[abcd k s]" has NO trailing "+= b".
MD5_ADD_B = True               # RFC 1321 FF macro: "(a) += (b);" after rotate.

MD5_R1_SHIFTS = (7, 12, 17, 22)
MD5_R1_CONSTS = (
    0xD76AA478, 0xE8C7B756, 0x242070DB, 0xC1BDCEEE,
    0xF57C0FAF, 0x4787C62A, 0xA8304613, 0xFD469501,
    0x698098D8, 0x8B44F7AF, 0xFFFF5BB1, 0x895CD7BE,
    0x6B901122, 0xFD987193, 0xA679438E, 0x49B40821,
)


def check_md5_t16() -> dict:
    """CTL-PO7 part 2 (md5_run_authorization F2): MD5's T[1..16] self-checked
    against RFC 1321 sec 3.4's sine definition, T[i] = floor(2^32 |sin(i)|)."""
    rows = []
    for i in range(1, 17):
        expected = int(2 ** 32 * abs(math.sin(i)))
        got = MD5_R1_CONSTS[i - 1]
        rows.append({"i": i, "expected": expected, "got": got,
                     "ok": got == expected})
    return {"all_ok": all(r["ok"] for r in rows), "table": rows}


_T16 = check_md5_t16()
if not _T16["all_ok"]:                                    # pragma: no cover
    raise ValueError("MD5 T[1..16] transcription error at module import")

# Full-schedule MD4 tables, used ONLY by the RFC 1320 A.5 vector self-check.
_MD4_R2_WORDS = (0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15)
_MD4_R2_SHIFTS = (3, 5, 9, 13)
_MD4_R2_CONST = 0x5A827999
_MD4_R3_WORDS = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
_MD4_R3_SHIFTS = (3, 9, 11, 15)
_MD4_R3_CONST = 0x6ED9EBA1


def _r1_tables(primitive: str):
    if primitive == "md4":
        return MD4_R1_SHIFTS, MD4_R1_CONSTS, MD4_ADD_B
    if primitive == "md5":
        return MD5_R1_SHIFTS, MD5_R1_CONSTS, MD5_ADD_B
    raise ValueError(f"unknown primitive: {primitive!r}")


def forward_step(state, xk: int, s: int, t: int, add_b: bool):
    """One Round-1 step. Returned tuple position 1 always holds the register
    just computed (the ABCD/DABC/CDAB/BCDA rotation)."""
    a, b, c, d = state
    rotated = _rotl((a + _f(b, c, d) + xk + t) & _M32, s)
    new_a = ((b + rotated) & _M32) if add_b else rotated
    return (d, new_a, b, c)


def backward_step(state_next, xk: int, s: int, t: int, add_b: bool):
    """Exact algebraic inverse of forward_step (HEUR-H2), same add_b."""
    a2, b2, c2, d2 = state_next
    old_b, old_c, old_d = c2, d2, a2
    new_a = b2
    rotated = ((new_a - old_b) & _M32) if add_b else new_a
    old_a = (_rotr(rotated, s) - _f(old_b, old_c, old_d) - xk - t) & _M32
    return (old_a, old_b, old_c, old_d)


# ---------------------------------------------------------------------------
# The parameter tuple. A-6 / PO-8: this IS the only permitted branching axis.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConstructionParams:
    primitive: str
    i_word: int
    j_word: int
    S: int
    p: int
    k1: int
    k2: int
    m: int
    k: int

    def as_tuple_dict(self) -> dict:
        return {"primitive": self.primitive, "i_word": self.i_word,
                "j_word": self.j_word, "S": self.S, "p": self.p,
                "k1": self.k1, "k2": self.k2, "m": self.m, "k": self.k}


R1_SEP10 = dict(i_word=2, j_word=12, S=8, p=3, m=12, k=20)
BATCH4_SLICE = dict(i_word=8, j_word=9, S=9, p=1, m=12, k=20)


def component_step(S: int, p: int) -> int:
    """1-indexed step whose output register sits at tuple position `p` of
    state_S. state_S[1]=step S, [2]=S-1, [3]=S-2, [0]=S-3."""
    return S - {1: 0, 2: 1, 3: 2, 0: 3}[p]


def code_path_fingerprint(params: ConstructionParams) -> dict:
    """PO-8. Fully qualified names of the two observable functions actually
    invoked, plus the exact parameter tuple they were invoked with."""
    return {
        "chunk1_observable": (f"{chunk1_observable.__module__}."
                              f"{chunk1_observable.__qualname__}"),
        "chunk2_observable": (f"{chunk2_observable.__module__}."
                              f"{chunk2_observable.__qualname__}"),
        "parameter_tuple": params.as_tuple_dict(),
    }


# ---------------------------------------------------------------------------
# THE TWO OBSERVABLE FUNCTIONS. Every phase reads the declared observable
# through exactly these, with no branching beyond the parameter tuple.
# ---------------------------------------------------------------------------

def chunk1_observable(w_a: int, params: ConstructionParams, fixed: dict) -> int:
    """Forward half. IV -> state_S over words 0..S-1 with word[i_word]=w_a;
    return tuple position `p` of state_S. STRUCTURALLY DOES NOT READ free
    word B (index j_word >= S), which phase B direction A records honestly
    rather than presenting as a passed test."""
    shifts, consts, add_b = _r1_tables(params.primitive)
    words = list(fixed["words"])
    words[params.i_word] = w_a
    state = _IV
    for i in range(params.S):
        state = forward_step(state, words[i], shifts[i % 4], consts[i], add_b)
    return state[params.p]


def chunk2_observable(w_b: int, Y, params: ConstructionParams,
                      fixed: dict) -> int:
    """Backward half. Y (the Round-1 output state) -> state_S by inverting
    steps 16 down to S+1 (words 15 down to S) with word[j_word]=w_b; return
    tuple position `p` of state_S."""
    shifts, consts, add_b = _r1_tables(params.primitive)
    words = list(fixed["words"])
    words[params.j_word] = w_b
    state = tuple(Y)
    for i in range(15, params.S - 1, -1):
        state = backward_step(state, words[i], shifts[i % 4], consts[i], add_b)
    return state[params.p]


# ---------------------------------------------------------------------------
# Deterministic fixed-word and target generation (frozen procedures).
# ---------------------------------------------------------------------------

def fixed_word_generation(seed: int, free_indices, free_bits: int) -> dict:
    """EXP-MDFIVE-a8e71e inputs.fixed_word_generation_procedure, verbatim."""
    free_indices = tuple(sorted(free_indices))
    rng = random.Random(seed)
    draws = [rng.getrandbits(32) for _ in range(16)]
    words = []
    high = {}
    mask = _M32 & ~((1 << free_bits) - 1)
    for i in range(16):
        if i in free_indices:
            h = draws[i] & mask
            if h == 0:
                h = 1 << free_bits
            high[i] = h
            words.append(h)
        else:
            w = draws[i] if draws[i] != 0 else 1
            words.append(w)
    return {"words": words, "high": high, "free_indices": free_indices,
            "free_bits": free_bits, "seed": seed}


def forward_full_round1(word_list, primitive: str):
    """Full 16-step Round-1 forward trajectory through forward_step.
    Returns (states, state16) where states[n] is state after n steps."""
    shifts, consts, add_b = _r1_tables(primitive)
    states = [_IV]
    state = _IV
    for i in range(16):
        state = forward_step(state, word_list[i], shifts[i % 4], consts[i],
                             add_b)
        states.append(state)
    return states, state


def generate_target(target_seed: int, fixed: dict, params: ConstructionParams,
                    override_low_i: int | None = None,
                    override_low_j: int | None = None) -> dict:
    """EXP-MDFIVE-a8e71e inputs.target_generation_procedure, verbatim: seed a
    random.Random(target_seed); draw the low k1 bits of the FORWARD free word
    then the low k2 bits of the BACKWARD free word, in that order; OR them
    onto the corresponding fixed high bits; compute the full Round-1 forward
    trajectory from the standard IV; record Y as state16 and target_lowk as
    the low k bits of the declared matching component on that trajectory.

    `override_low_i` / `override_low_j` implement phase B direction B's
    coordinator-specified regeneration rule (hold free word A's low bits at a
    pre-registered index, keep free word B's low bits at the seeded draw).
    THE SEARCH NEVER READS true_word_i OR true_word_j.
    """
    rng = random.Random(target_seed)
    low_i = rng.getrandbits(params.k1)
    low_j = rng.getrandbits(params.k2)
    if override_low_i is not None:
        low_i = override_low_i
    if override_low_j is not None:
        low_j = override_low_j
    true_word_i = fixed["high"][params.i_word] | low_i
    true_word_j = fixed["high"][params.j_word] | low_j
    word_list = list(fixed["words"])
    word_list[params.i_word] = true_word_i
    word_list[params.j_word] = true_word_j
    states, state16 = forward_full_round1(word_list, params.primitive)
    component = states[params.S][params.p]
    return {
        "true_word_i": true_word_i, "true_word_j": true_word_j,
        "true_low_i": low_i, "true_low_j": low_j,
        "component_full32": component,
        "target_lowk": component & ((1 << params.k) - 1),
        "Y": tuple(state16),
        "component_step_1indexed": component_step(params.S, params.p),
        "params": params.as_tuple_dict(),
        "target_seed": target_seed,
    }


# ---------------------------------------------------------------------------
# INDEPENDENT straight-line reference implementation. Named a,b,c,d
# registers, no state-tuple role convention, no shared helper with
# forward_step/backward_step beyond _rotl/_f. Used ONLY by the naive baseline
# (CTL-PO4), by certificate re-verification, and by CTL-PO9.
# ---------------------------------------------------------------------------

def _reference_registers(word_list, primitive: str):
    """Straight-line 16-step Round-1 forward pass. Returns
    (registers_by_step, final_state) with registers_by_step[n] = the value of
    the register updated at 1-indexed step n."""
    if primitive == "md4":
        shifts, consts, add_b = MD4_R1_SHIFTS, MD4_R1_CONSTS, MD4_ADD_B
    elif primitive == "md5":
        shifts, consts, add_b = MD5_R1_SHIFTS, MD5_R1_CONSTS, MD5_ADD_B
    else:
        raise ValueError(primitive)
    a, b, c, d = _IV
    by_step = {}
    for i in range(16):
        x = word_list[i]
        s = shifts[i % 4]
        t = consts[i]
        if i % 4 == 0:
            a = _rotl((a + _f(b, c, d) + x + t) & _M32, s)
            a = ((a + b) & _M32) if add_b else a
            by_step[i + 1] = a
        elif i % 4 == 1:
            d = _rotl((d + _f(a, b, c) + x + t) & _M32, s)
            d = ((d + a) & _M32) if add_b else d
            by_step[i + 1] = d
        elif i % 4 == 2:
            c = _rotl((c + _f(d, a, b) + x + t) & _M32, s)
            c = ((c + d) & _M32) if add_b else c
            by_step[i + 1] = c
        else:
            b = _rotl((b + _f(c, d, a) + x + t) & _M32, s)
            b = ((b + c) & _M32) if add_b else b
            by_step[i + 1] = b
    return by_step, (a, b, c, d)


def _reference_round1_output(word_list, primitive: str):
    """The Round-1 output state ONLY. This is the entire surface the naive
    baseline touches: it never sees a per-step register, never sees component
    p, and never sees the matching window."""
    return _reference_registers(word_list, primitive)[1]


def component_identity_check(params: ConstructionParams, fixed: dict,
                             probe_words) -> dict:
    """CTL-PO9. Assert tuple position p of state_S, as produced by this
    module's own forward chain, equals the register produced at 1-indexed step
    component_step(S, p) as computed by the INDEPENDENT straight-line
    named-register reference. Runs BEFORE the gate."""
    step = component_step(params.S, params.p)
    rows = []
    for word_list in probe_words:
        states, _ = forward_full_round1(word_list, params.primitive)
        chain = states[params.S][params.p]
        by_step, _ = _reference_registers(word_list, params.primitive)
        ref = by_step[step]
        rows.append({"chain_value": chain, "reference_value": ref,
                     "ok": chain == ref})
    return {"primitive": params.primitive, "S": params.S, "p": params.p,
            "component_step_1indexed": step, "n_probes": len(rows),
            "all_ok": all(r["ok"] for r in rows), "probes": rows}


# ---------------------------------------------------------------------------
# Full 48-step MD4, ONLY for the RFC 1320 A.5 vector self-check (CTL-PO7).
# Never used by the search.
# ---------------------------------------------------------------------------

def _step_generic(state, xk, s, t, func):
    a, b, c, d = state
    return (d, _rotl((a + func(b, c, d) + xk + t) & _M32, s), b, c)


def _md4_compress(state, words):
    s0 = tuple(state)
    st = tuple(state)
    for i in range(16):
        st = forward_step(st, words[i], MD4_R1_SHIFTS[i % 4], 0, MD4_ADD_B)
    for idx, wi in enumerate(_MD4_R2_WORDS):
        st = _step_generic(st, words[wi], _MD4_R2_SHIFTS[idx % 4],
                           _MD4_R2_CONST, _g)
    for idx, wi in enumerate(_MD4_R3_WORDS):
        st = _step_generic(st, words[wi], _MD4_R3_SHIFTS[idx % 4],
                           _MD4_R3_CONST, _h)
    return tuple((st[i] + s0[i]) & _M32 for i in range(4))


def _pad(message: bytes) -> bytes:
    bit_len = len(message) * 8
    msg = message + b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    return msg + (bit_len & ((1 << 64) - 1)).to_bytes(8, "little")


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
    for msg, expected in RFC1320_TEST_VECTORS:
        got = md4_digest(msg)
        results.append({"message": msg.decode("ascii"), "expected": expected,
                        "got": got, "ok": got == expected})
    return {"all_ok": all(r["ok"] for r in results), "vectors": results}


# ---------------------------------------------------------------------------
# CTL-PO6: HEUR-H2 exact-invertibility regression fixture.
# ---------------------------------------------------------------------------

def h2_regression_fixture(seed: int, n: int, primitive: str) -> dict:
    shifts, consts, add_b = _r1_tables(primitive)
    rng = random.Random(seed)
    failures = []
    for i in range(n):
        state = tuple(rng.getrandbits(32) for _ in range(4))
        xk = rng.getrandbits(32)
        s = shifts[i % 4]
        t = consts[i % 16]
        fwd = forward_step(state, xk, s, t, add_b)
        back = backward_step(fwd, xk, s, t, add_b)
        if back != state:
            failures.append({"index": i, "state": state, "xk": xk, "s": s,
                             "t": t, "forward": fwd, "recovered": back})
            if len(failures) >= 20:
                break
    return {"n": n, "primitive": primitive, "seed": seed,
            "failures": failures, "all_ok": not failures}


# ---------------------------------------------------------------------------
# GATE-PO2: the mandatory two-directional dependence gate.
# ---------------------------------------------------------------------------

HELD_FIXED_INDICES = (0, 5, 10, 15)


def gate_direction_A(params: ConstructionParams, fixed: dict) -> dict:
    """Hold free word B fixed; sweep free word A over all 2^k1 window values;
    count distinct chunk1_observable values at 32-bit and m-bit resolution.
    Repeated at the four pre-registered held-fixed indices of free word B.

    RECORDED HONESTLY (contract phase_B_direction_A.recorded_honestly):
    chunk1_observable STRUCTURALLY DOES NOT READ free word B, so holding B
    fixed is automatic and the four repetitions buy NO quantifier strength in
    this direction. They are retained for procedural symmetry and converted
    into a real check by CTL-PO3 (byte-identity across the four)."""
    rows = []
    for hb in HELD_FIXED_INDICES:
        vals = [chunk1_observable(fixed["high"][params.i_word] | low,
                                  params, fixed)
                for low in range(1 << params.k1)]
        mmask = (1 << params.m) - 1
        rows.append({
            "held_fixed_free_word_B_low": hb,
            "distinct_fwd_32bit": len({v for v in vals}),
            "distinct_fwd_12bit": len({v & mmask for v in vals}),
            "values_32bit": vals,
        })
    signatures = [json.dumps(r["values_32bit"]) for r in rows]
    po3_identical = len(set(signatures)) == 1
    criterion = all(r["distinct_fwd_32bit"] >= 2 and r["distinct_fwd_12bit"] >= 2
                    for r in rows)
    return {"rows": rows, "criterion_met": criterion,
            "PO3_byte_identical_across_repetitions": po3_identical,
            "held_fixed_values": list(HELD_FIXED_INDICES)}


def gate_direction_B(params: ConstructionParams, fixed: dict,
                     target_seed: int) -> dict:
    """Hold free word A fixed; sweep free word B over all 2^k2 window values;
    count distinct chunk2_observable values at 32-bit and m-bit resolution.
    FOR EACH held-fixed index a the TARGET IS REGENERATED by the declared
    procedure with free word A's low bits set to a and free word B's low bits
    at the seeded draw, yielding Y_a; the sweep runs against Y_a."""
    rows = []
    mmask = (1 << params.m) - 1
    for ha in HELD_FIXED_INDICES:
        t_a = generate_target(target_seed, fixed, params, override_low_i=ha)
        vals = [chunk2_observable(fixed["high"][params.j_word] | low,
                                  t_a["Y"], params, fixed)
                for low in range(1 << params.k2)]
        rows.append({
            "held_fixed_free_word_A_low": ha,
            "regenerated_Y": list(t_a["Y"]),
            "distinct_bwd_32bit": len({v for v in vals}),
            "distinct_bwd_12bit": len({v & mmask for v in vals}),
            "values_32bit": vals,
        })
    criterion = all(r["distinct_bwd_32bit"] >= 2 and r["distinct_bwd_12bit"] >= 2
                    for r in rows)
    return {"rows": rows, "criterion_met": criterion,
            "held_fixed_values": list(HELD_FIXED_INDICES)}


def gate_joint_fiber(params: ConstructionParams, fixed: dict,
                     target: dict) -> dict:
    """For each free-word-B window value, the SET of free-word-A window values
    whose low-m chunk1_observable equals the low-m chunk2_observable; count
    how many DISTINCT such sets occur. The operational signature of ANOM-1:
    a degenerate backward channel yields EXACTLY 1."""
    mmask = (1 << params.m) - 1
    fwd_low = [chunk1_observable(fixed["high"][params.i_word] | low,
                                 params, fixed) & mmask
               for low in range(1 << params.k1)]
    sets = []
    for low_b in range(1 << params.k2):
        obs = chunk2_observable(fixed["high"][params.j_word] | low_b,
                                target["Y"], params, fixed) & mmask
        sets.append(tuple(a for a, v in enumerate(fwd_low) if v == obs))
    return {"distinct_fiber_sets": len(set(sets)),
            "criterion_met": len(set(sets)) >= 2,
            "fiber_sets": [list(s) for s in sets]}


def run_gate_phase(name: str, params: ConstructionParams, fixed: dict,
                   target_seed: int, phase_log: list) -> dict:
    """One full two-directional predicate evaluation, through the SAME
    chunk1_observable / chunk2_observable functions the declared-scale runs
    call. Used unchanged by phase A (the null control, which MUST FAIL), by
    phase B (MD4) and by phase C (MD5)."""
    t0 = time.monotonic()
    fp = code_path_fingerprint(params)
    target = generate_target(target_seed, fixed, params)
    dir_a = gate_direction_A(params, fixed)
    dir_b = gate_direction_B(params, fixed, target_seed)
    fiber = gate_joint_fiber(params, fixed, target)
    predicate = bool(dir_a["criterion_met"]
                     and dir_a["PO3_byte_identical_across_repetitions"]
                     and dir_b["criterion_met"] and fiber["criterion_met"])
    failing = []
    if not dir_a["criterion_met"]:
        failing.append("direction_A_criterion")
    if not dir_a["PO3_byte_identical_across_repetitions"]:
        failing.append("CTL-PO3_byte_identity")
    if not dir_b["criterion_met"]:
        failing.append("direction_B_criterion")
    if not fiber["criterion_met"]:
        failing.append("joint_fiber_distinct_sets_ge_2")
    t1 = time.monotonic()
    out = {
        "phase": name,
        "code_path_fingerprint": fp,
        "target_seed": target_seed,
        "target_Y": list(target["Y"]),
        "direction_A": dir_a,
        "direction_B": dir_b,
        "joint_fiber": fiber,
        "predicate": "PASS" if predicate else "FAIL",
        "failing_clauses": failing,
        "distinct_fwd_32bit_by_held_fixed": [r["distinct_fwd_32bit"]
                                             for r in dir_a["rows"]],
        "distinct_fwd_12bit_by_held_fixed": [r["distinct_fwd_12bit"]
                                             for r in dir_a["rows"]],
        "distinct_bwd_32bit_by_held_fixed": [r["distinct_bwd_32bit"]
                                             for r in dir_b["rows"]],
        "distinct_bwd_12bit_by_held_fixed": [r["distinct_bwd_12bit"]
                                             for r in dir_b["rows"]],
        "wall_seconds": round(t1 - t0, 6),
    }
    phase_log.append({"phase": name, "started_monotonic": round(t0, 6),
                      "finished_monotonic": round(t1, 6),
                      "code_path_fingerprint": fp,
                      "predicate": out["predicate"],
                      "failing_clauses": failing})
    return out


def evaluate_gate(phase_a: dict, phase_b: dict, phase_c: dict) -> dict:
    """The frozen pass_predicate, evaluated exactly as written."""
    a_bwd32 = phase_a["distinct_bwd_32bit_by_held_fixed"]
    a_bwd12 = phase_a["distinct_bwd_12bit_by_held_fixed"]
    a_fwd32 = phase_a["distinct_fwd_32bit_by_held_fixed"]
    clauses = {
        "phase_A_returned_FAIL": phase_a["predicate"] == "FAIL",
        "phase_A_distinct_bwd_32bit_exactly_1": all(v == 1 for v in a_bwd32),
        "phase_A_distinct_bwd_12bit_exactly_1": all(v == 1 for v in a_bwd12),
        "phase_A_distinct_fwd_32bit_gt_1": all(v > 1 for v in a_fwd32),
        "phase_B_direction_A_criterion": phase_b["direction_A"]["criterion_met"],
        "phase_B_CTL_PO3_byte_identity":
            phase_b["direction_A"]["PO3_byte_identical_across_repetitions"],
        "phase_B_direction_B_criterion": phase_b["direction_B"]["criterion_met"],
        "phase_B_joint_fiber_ge_2": phase_b["joint_fiber"]["criterion_met"],
        "phase_C_md5_same_verdict_as_phase_B":
            phase_c["predicate"] == phase_b["predicate"],
    }
    verdict = "PASS" if all(clauses.values()) else "FAIL"
    return {"verdict": verdict, "clauses": clauses,
            "failing_clauses": sorted(k for k, v in clauses.items() if not v)}


# ---------------------------------------------------------------------------
# The MITM instrument and its INDEPENDENT naive baseline.
# ---------------------------------------------------------------------------

def mitm_search(params: ConstructionParams, fixed: dict, target: dict) -> dict:
    """Exhaustive MITM over the 2^k1 x 2^k2 restricted space, reading the
    declared observable ONLY through chunk1_observable / chunk2_observable.
    `raw_solutions` is the PRE-CERTIFICATE candidate set: pairs passing full
    k-bit equality of the two independently derived observable values."""
    mmask = (1 << params.m) - 1
    kmask = (1 << params.k) - 1
    hi_i = fixed["high"][params.i_word]
    hi_j = fixed["high"][params.j_word]

    table: dict[int, list[tuple[int, int]]] = {}
    for low_a in range(1 << params.k1):
        w_a = hi_i | low_a
        v = chunk1_observable(w_a, params, fixed)
        table.setdefault(v & mmask, []).append((w_a, v & kmask))

    window_hits = 0
    raw_solutions = []
    chunk_evals_to_first_raw = None
    chunk1_cost = 1 << params.k1
    for low_b in range(1 << params.k2):
        w_b = hi_j | low_b
        v = chunk2_observable(w_b, target["Y"], params, fixed)
        bucket = table.get(v & mmask)
        if not bucket:
            continue
        for w_a, low_k_fwd in bucket:
            window_hits += 1
            if low_k_fwd == (v & kmask):
                raw_solutions.append((w_a, w_b))
                if chunk_evals_to_first_raw is None:
                    chunk_evals_to_first_raw = chunk1_cost + low_b + 1
    return {
        "matching_window_hits": window_hits,
        "raw_solutions": raw_solutions,
        "raw_solution_count": len(raw_solutions),
        "chunk_evals_to_first_raw_candidate": chunk_evals_to_first_raw,
        "chunk1_evaluations": 1 << params.k1,
        "chunk2_evaluations": 1 << params.k2,
        "total_chunk_evaluations": (1 << params.k1) + (1 << params.k2),
        "step_evaluations": ((1 << params.k1) * params.S
                             + (1 << params.k2) * (16 - params.S)),
    }


def verify_certificate(params: ConstructionParams, fixed: dict, target: dict,
                       w_a: int, w_b: int) -> dict:
    """Independent re-verification of a claimed pair through
    _reference_registers ONLY (straight-line, named registers, no
    forward_step/backward_step/chunk*_observable)."""
    word_list = list(fixed["words"])
    word_list[params.i_word] = w_a
    word_list[params.j_word] = w_b
    by_step, state16 = _reference_registers(word_list, params.primitive)
    step = component_step(params.S, params.p)
    ref_lowk = by_step[step] & ((1 << params.k) - 1)
    y_match = tuple(state16) == tuple(target["Y"])
    target_match = ref_lowk == target["target_lowk"]
    return {
        "verified": bool(y_match and target_match),
        "reference_component_lowk": ref_lowk,
        "declared_target_lowk": target["target_lowk"],
        "target_match": target_match,
        "reference_round1_output": list(state16),
        "declared_round1_output_Y": list(target["Y"]),
        "round1_output_match": y_match,
        "method": ("_reference_registers -- straight-line named-register "
                   "16-step Round-1 forward pass, independent of "
                   "forward_step/backward_step/chunk1_observable/"
                   "chunk2_observable/mitm_search"),
    }


def naive_y_reproducing_search(params: ConstructionParams, fixed: dict,
                               target: dict) -> dict:
    """CTL-PO4's INDEPENDENT baseline. Enumerates all 2^(k1+k2) pairs and, for
    each, runs a straight-line 16-step forward recomputation, comparing the
    Round-1 OUTPUT STATE to Y. It never calls backward_step, never reads
    component p, and never reads the matching window -- which is precisely
    what BATCH-af29f6's baseline did wrong (it compared low_k_fwd against
    low_k_bwd and was vacuous; EV-MDFIVE-ab007d O-2, ANOM-1 CAVEAT)."""
    hi_i = fixed["high"][params.i_word]
    hi_j = fixed["high"][params.j_word]
    Y = tuple(target["Y"])
    solutions = []
    evaluations = 0
    base = list(fixed["words"])
    for low_a in range(1 << params.k1):
        w_a = hi_i | low_a
        for low_b in range(1 << params.k2):
            w_b = hi_j | low_b
            word_list = list(base)
            word_list[params.i_word] = w_a
            word_list[params.j_word] = w_b
            evaluations += 1
            if _reference_round1_output(word_list, params.primitive) == Y:
                solutions.append((w_a, w_b))
    return {"solutions": solutions, "evaluations": evaluations,
            "uses_backward_inversion": False,
            "uses_declared_component": False,
            "uses_matching_window": False}


# ---------------------------------------------------------------------------
# Statistics (no scipy in this environment).
# ---------------------------------------------------------------------------

def _poisson_pmf(i: int, lam: float) -> float:
    if i < 0:
        return 0.0
    return math.exp(i * math.log(lam) - lam - math.lgamma(i + 1))


def _poisson_sf(k: int, lam: float) -> float:
    """P(X >= k), X ~ Poisson(lam), by direct summation."""
    if k <= 0:
        return 1.0
    total = 0.0
    i = k
    term = _poisson_pmf(i, lam)
    negligible = 0
    while i < k + 200000:
        total += term
        i += 1
        term = _poisson_pmf(i, lam)
        if term < 1e-18:
            negligible += 1
            if negligible > 50:
                break
        else:
            negligible = 0
    return min(1.0, total)


def _regularized_gamma_q(a: float, x: float) -> float:
    """Q(a,x) via series / continued fraction (Numerical Recipes 6.2)."""
    if x <= 0:
        return 1.0
    if x < a + 1.0:
        ap = a
        total = 1.0 / a
        delta = total
        for _ in range(500):
            ap += 1
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * 1e-14:
                break
        return 1.0 - total * math.exp(-x + a * math.log(x) - math.lgamma(a))
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


def chi_square_goodness_of_fit(observed_counts, lam: float) -> dict:
    """Poisson(lam) goodness of fit with lam FIXED A PRIORI by HEUR-H1 (no
    parameter estimated from the data, so df = bins - 1)."""
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
    bin_edges = [None] + edges + [None]
    counts = [0] * (len(bin_edges) - 1)
    for v in observed_counts:
        for bi in range(len(edges) + 1):
            lo, hi = bin_edges[bi], bin_edges[bi + 1]
            if (lo is None or v >= lo) and (hi is None or v < hi):
                counts[bi] += 1
                break
    expected = []
    for bi in range(len(counts)):
        lo, hi = bin_edges[bi], bin_edges[bi + 1]
        if lo is None:
            pr = sum(_poisson_pmf(i, lam) for i in range(0, hi))
        elif hi is None:
            pr = _poisson_sf(lo, lam)
        else:
            pr = sum(_poisson_pmf(i, lam) for i in range(lo, hi))
        expected.append(pr * n)
    merged_c, merged_e = [], []
    i = 0
    while i < len(counts):
        c, e = counts[i], expected[i]
        j = i
        while e < 5 and j + 1 < len(counts):
            j += 1
            c += counts[j]
            e += expected[j]
        merged_c.append(c)
        merged_e.append(e)
        i = j + 1
    if merged_e and merged_e[-1] < 5 and len(merged_e) > 1:
        merged_c[-2] += merged_c[-1]
        merged_e[-2] += merged_e[-1]
        merged_c.pop()
        merged_e.pop()
    chi2 = sum((c - e) ** 2 / e for c, e in zip(merged_c, merged_e) if e > 0)
    df = max(1, len(merged_c) - 1)
    return {"n": n, "lambda": lam, "bins": len(merged_c), "df": df,
            "chi2_statistic": chi2,
            "p_value": _regularized_gamma_q(df / 2.0, chi2 / 2.0),
            "alpha": 0.05,
            "observed_counts_by_bin": merged_c,
            "expected_counts_by_bin": merged_e}


def _sample_variance(xs) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - 1)


def classify_variance(var: float | None) -> str:
    """H-MDFIVE-0ca596 HEUR-H1 falsification_condition's frozen three-way
    split, applied mechanically. THIS IS A CLASSIFICATION LABEL, NOT A
    VERDICT: the Executor reports it and composes no validated/refuted
    judgement (agents/executor.md 13)."""
    if var is None:
        return "not_computable"
    if var < 64:
        return ("below_64_INSTRUMENT_DEGENERACY_STOP -- explicitly NOT an H1 "
                "falsification")
    if 128 <= var <= 512:
        return "inside_[128,512]_H1_consistent_band"
    return "outside_[128,512]_and_not_below_64"


# ---------------------------------------------------------------------------
# HEUR-H1 sampling harness.
# ---------------------------------------------------------------------------

def h1_sampling(target_seed: int, params: ConstructionParams, fixed: dict,
                n_target: int, deadline: float | None) -> dict:
    """N independent targets from ONE seeded stream, at the declared scale.
    Halts truthfully at `deadline` (monotonic clock, checked between target
    draws) and reports the achieved N -- a budget outcome (SC-7), never a
    defect and never a negative mathematical result."""
    rng = random.Random(target_seed)
    lam = float(2 ** (params.k1 + params.k2 - params.m))
    window_counts, full_counts = [], []
    t0 = time.monotonic()
    deadline_abs = (t0 + deadline) if deadline is not None else None
    halted = False
    hi_i = fixed["high"][params.i_word]
    hi_j = fixed["high"][params.j_word]
    for _ in range(n_target):
        if deadline_abs is not None and time.monotonic() >= deadline_abs:
            halted = True
            break
        low_i = rng.getrandbits(params.k1)
        low_j = rng.getrandbits(params.k2)
        word_list = list(fixed["words"])
        word_list[params.i_word] = hi_i | low_i
        word_list[params.j_word] = hi_j | low_j
        states, state16 = forward_full_round1(word_list, params.primitive)
        target = {"Y": tuple(state16),
                  "target_lowk": (states[params.S][params.p]
                                  & ((1 << params.k) - 1))}
        res = mitm_search(params, fixed, target)
        window_counts.append(res["matching_window_hits"])
        full_counts.append(res["raw_solution_count"])
    wall = time.monotonic() - t0
    var = _sample_variance(window_counts)
    largest = max(window_counts) if window_counts else None
    return {
        "primitive": params.primitive, "target_seed": target_seed,
        "requested_n": n_target, "achieved_n": len(window_counts),
        "halted_before_target_n": halted,
        "internal_wall_seconds": round(wall, 6),
        "lambda_predicted": lam,
        "preregistered_prediction": (
            "Poisson(lambda = 2^(k1+k2-m) = 256); source H-MDFIVE-0ca596 "
            "HEUR-H1 via EXP-MDFIVE-a8e71e preregistered_prediction, FROZEN "
            "before any run"),
        "matching_window_collision_counts": window_counts,
        "full_target_hit_counts": full_counts,
        "mean_matching_window_hits": (sum(window_counts) / len(window_counts)
                                      if window_counts else None),
        "mean_full_target_hits": (sum(full_counts) / len(full_counts)
                                  if full_counts else None),
        "sample_variance_matching_window": var,
        "sample_variance_classification": classify_variance(var),
        "chi_square_goodness_of_fit": chi_square_goodness_of_fit(
            window_counts, lam),
        "tail_check": {
            "largest_observed_matching_window_count": largest,
            "poisson_sf_p_value": (_poisson_sf(largest, lam)
                                   if largest is not None else None),
            "formula": "P(X >= largest observed), X ~ Poisson(256)",
        },
        "code_path_fingerprint": code_path_fingerprint(params),
    }


# ---------------------------------------------------------------------------
# Phase drivers for the wrapped runs.
# ---------------------------------------------------------------------------

def _params(primitive: str, slice_name: str, k1: int, k2: int
            ) -> ConstructionParams:
    base = R1_SEP10 if slice_name == "r1_sep10" else BATCH4_SLICE
    return ConstructionParams(primitive=primitive, k1=k1, k2=k2, **base)


def do_buildcheck() -> dict:
    """Run 1. CTL-PO7 (RFC 1320 A.5 vectors + MD5 T[1..16] self-check),
    CTL-PO6 (H2 fixture, BOTH primitives, seed 8975327, 10000 tuples each --
    md5_run_authorization F1/F2), CTL-PO9 (component identity)."""
    phase_log = []
    t0 = time.monotonic()
    pins = check_input_pins()
    vectors = check_rfc1320_vectors()
    t16 = check_md5_t16()
    h2_md4 = h2_regression_fixture(8975327, 10000, "md4")
    h2_md5 = h2_regression_fixture(8975327, 10000, "md5")
    probes = []
    rng = random.Random(20260821)
    for _ in range(64):
        probes.append([rng.getrandbits(32) for _ in range(16)])
    po9 = {}
    for primitive in ("md4", "md5"):
        for slice_name in ("r1_sep10", "batch4_slice"):
            pp = _params(primitive, slice_name, 4, 4)
            po9[f"{primitive}_{slice_name}"] = component_identity_check(
                pp, None, probes)
    t1 = time.monotonic()
    phase_log.append({"phase": "buildcheck",
                      "started_monotonic": round(t0, 6),
                      "finished_monotonic": round(t1, 6)})
    all_ok = (pins["all_ok"] and vectors["all_ok"] and t16["all_ok"]
              and h2_md4["all_ok"] and h2_md5["all_ok"]
              and all(v["all_ok"] for v in po9.values()))
    return {
        "input_pins": pins,
        "CTL_PO7_rfc1320_vectors": vectors,
        "CTL_PO7_md5_t16_selfcheck": {"all_ok": t16["all_ok"],
                                      "table": t16["table"]},
        "CTL_PO6_h2_md4": {"all_ok": h2_md4["all_ok"], "n": h2_md4["n"],
                           "failures": h2_md4["failures"]},
        "CTL_PO6_h2_md5": {"all_ok": h2_md5["all_ok"], "n": h2_md5["n"],
                           "failures": h2_md5["failures"]},
        "CTL_PO9_component_identity": po9,
        "all_gates_passed": all_ok,
        "phase_log": phase_log,
        "md5_computation_performed": [
            "F1 CTL-PO6 HEUR-H2 backward-inversion fixture in MD5 mode, seed "
            "8975327, 10000 tuples",
            "F2 MD5 T[1..16] self-check against the RFC 1321 sec 3.4 sine "
            "definition",
            "CTL-PO9 component-identity assertion in MD5 mode (deterministic "
            "arithmetic identity, no search)",
        ],
    }


def do_gate_and_controls() -> dict:
    """Run 2. Phase A (CTL-PO1 null control, MUST FAIL) -> phase B (MD4
    two-directional gate) -> phase C (MD5 gate) -> gate verdict -> and ONLY
    on PASS the k1=k2=6 controls. On FAIL the run terminates immediately and
    the raw output contains NO k1=k2=6 phase."""
    phase_log = []
    out = {"phase_log": phase_log}

    # --- Phase A: the batch-4-slice detector null control. MUST FAIL. ---
    fixed_a = fixed_word_generation(20260821, (8, 9), 4)
    params_a = _params("md4", "batch4_slice", 4, 4)
    phase_a = run_gate_phase("A_CTL-PO1_batch4_slice_null_control",
                             params_a, fixed_a, 8975321, phase_log)
    out["phase_A"] = phase_a

    # --- Phase B: R1-SEP10, MD4. ---
    fixed_b = fixed_word_generation(20260821, (2, 12), 4)
    params_b = _params("md4", "r1_sep10", 4, 4)
    phase_b = run_gate_phase("B_R1SEP10_md4_two_directional",
                             params_b, fixed_b, 8975322, phase_log)
    out["phase_B"] = phase_b

    # --- Phase C: R1-SEP10, MD5 (md5_run_authorization F3). ---
    fixed_c = fixed_word_generation(20260821, (2, 12), 4)
    params_c = _params("md5", "r1_sep10", 4, 4)
    phase_c = run_gate_phase("C_R1SEP10_md5_two_directional",
                             params_c, fixed_c, 8975328, phase_log)
    out["phase_C"] = phase_c

    # --- The frozen pass predicate. RECORDED BEFORE ANY CONTROL PHASE. ---
    gate = evaluate_gate(phase_a, phase_b, phase_c)
    out["gate"] = gate
    phase_log.append({"phase": "GATE_VERDICT_RECORDED",
                      "monotonic": round(time.monotonic(), 6),
                      "verdict": gate["verdict"],
                      "failing_clauses": gate["failing_clauses"]})

    if gate["verdict"] != "PASS":
        out["k1_k2_6_controls"] = None
        out["terminated_immediately_on_gate_fail"] = True
        out["unspent_note"] = (
            "Gate FAILED. No k1=k2=6 control phase, no declared-scale run and "
            "no MD5 search arm executed (EXP-MDFIVE-a8e71e "
            "mandatory_dependence_gate.on_fail, IR-1). Remaining run ceilings "
            "are UNSPENT and are never reallocated.")
        return out
    out["terminated_immediately_on_gate_fail"] = False

    # --- k1 = k2 = 6 controls, MD4 ONLY (never MD5: IR-4). ---
    t0 = time.monotonic()
    fixed6 = fixed_word_generation(20260821, (2, 12), 6)
    p6 = _params("md4", "r1_sep10", 6, 6)
    fp6 = code_path_fingerprint(p6)
    target6 = generate_target(8975323, fixed6, p6)
    mitm6 = mitm_search(p6, fixed6, target6)
    certs = [(w_a, w_b, verify_certificate(p6, fixed6, target6, w_a, w_b))
             for (w_a, w_b) in mitm6["raw_solutions"]]
    verified = sorted((w_a, w_b) for (w_a, w_b, v) in certs if v["verified"])
    naive6 = naive_y_reproducing_search(p6, fixed6, target6)
    naive_sorted = sorted(naive6["solutions"])

    raw_wa = sorted({w_a for (w_a, _) in mitm6["raw_solutions"]})
    raw_wb = sorted({w_b for (_, w_b) in mitm6["raw_solutions"]})
    po5 = {
        "raw_candidate_count": mitm6["raw_solution_count"],
        "distinct_wA_in_raw_set": len(raw_wa),
        "distinct_wB_in_raw_set": len(raw_wb),
        "window_size": 1 << p6.k1,
        "part_a_both_projections_strictly_below_64": (
            len(raw_wa) < (1 << p6.k1) and len(raw_wb) < (1 << p6.k2)),
        "part_b_raw_count_at_most_4": mitm6["raw_solution_count"] <= 4,
        "expected_raw_count_modeled": 1 + 4096 / 2 ** 20,
    }
    po5["passed"] = (po5["part_a_both_projections_strictly_below_64"]
                     and po5["part_b_raw_count_at_most_4"])

    colliding_non_y = [
        {"wA": w_a, "wB": w_b,
         "reference_component_lowk": v["reference_component_lowk"],
         "round1_output_match": v["round1_output_match"]}
        for (w_a, w_b, v) in certs if not v["verified"]]

    # CTL-H1B: paired contrast, 64-value sweeps at k1=k2=6.
    mmask6 = (1 << p6.m) - 1
    fwd_v6 = [chunk1_observable(fixed6["high"][p6.i_word] | low, p6, fixed6)
              for low in range(1 << p6.k1)]
    bwd_v6 = [chunk2_observable(fixed6["high"][p6.j_word] | low, target6["Y"],
                                p6, fixed6)
              for low in range(1 << p6.k2)]
    p6_pos1 = replace(p6, p=1)
    bwd_v8 = [chunk2_observable(fixed6["high"][p6.j_word] | low, target6["Y"],
                                p6_pos1, fixed6)
              for low in range(1 << p6.k2)]
    h1b = {
        "sweep_size": 1 << p6.k1,
        "forward_v6_component_step": component_step(p6.S, 3),
        "backward_v8_component_step": component_step(p6.S, 1),
        "forward_v6_distinct_32bit": len(set(fwd_v6)),
        "forward_v6_distinct_12bit": len({v & mmask6 for v in fwd_v6}),
        "backward_v6_distinct_32bit": len(set(bwd_v6)),
        "backward_v6_distinct_12bit": len({v & mmask6 for v in bwd_v6}),
        "backward_v8_distinct_32bit": len(set(bwd_v8)),
        "backward_v8_distinct_12bit": len({v & mmask6 for v in bwd_v8}),
        "note": ("Paired two-outcome contrast, reported as numbers only. The "
                 "Executor composes no verdict on HEUR-H1b."),
    }

    t1 = time.monotonic()
    phase_log.append({"phase": "k1_k2_6_controls_md4",
                      "started_monotonic": round(t0, 6),
                      "finished_monotonic": round(t1, 6),
                      "code_path_fingerprint": fp6})
    out["k1_k2_6_controls"] = {
        "code_path_fingerprint": fp6,
        "target_seed": 8975323,
        "planted_pair": [target6["true_word_i"], target6["true_word_j"]],
        "CTL_PO4_completeness": {
            "certificate_verified_mitm_solutions": [list(s) for s in verified],
            "naive_Y_reproducing_solutions": [list(s) for s in naive_sorted],
            "sets_equal": verified == naive_sorted,
            "naive_evaluations": naive6["evaluations"],
            "naive_independence": {
                "uses_backward_inversion": naive6["uses_backward_inversion"],
                "uses_declared_component": naive6["uses_declared_component"],
                "uses_matching_window": naive6["uses_matching_window"]},
        },
        "CTL_PO5_raw_set_degeneracy": po5,
        "CTL_OBS_observation_collisions": {
            "pairs_enumerated": (1 << p6.k1) * (1 << p6.k2),
            "twenty_bit_colliding_pairs": [list(s)
                                           for s in mitm6["raw_solutions"]],
            "twenty_bit_colliding_non_Y_reproducing_pairs": colliding_non_y,
            "expected_non_planted_collisions_modeled": 4096 / 2 ** 20,
        },
        "CTL_H1B_paired_contrast": h1b,
        "mitm": {k: v for k, v in mitm6.items() if k != "raw_solutions"},
        "wall_seconds": round(t1 - t0, 6),
    }
    return out


def do_primary(target_seed: int, params: ConstructionParams,
               fixed: dict) -> dict:
    """Run 3. Declared-scale MD4 primary certificate run."""
    phase_log = []
    t0 = time.monotonic()
    fp = code_path_fingerprint(params)
    target = generate_target(target_seed, fixed, params)
    mitm = mitm_search(params, fixed, target)
    certs = [(w_a, w_b, verify_certificate(params, fixed, target, w_a, w_b))
             for (w_a, w_b) in mitm["raw_solutions"]]
    verified = [(w_a, w_b) for (w_a, w_b, v) in certs if v["verified"]]
    first_verified_index = next(
        (i for i, (_, _, v) in enumerate(certs) if v["verified"]), None)
    chunk_evals_to_first_verified = None
    if first_verified_index is not None:
        w_a, w_b, _ = certs[first_verified_index]
        low_b = w_b - fixed["high"][params.j_word]
        chunk_evals_to_first_verified = (1 << params.k1) + low_b + 1
    t1 = time.monotonic()
    phase_log.append({"phase": "primary_certificate_run",
                      "started_monotonic": round(t0, 6),
                      "finished_monotonic": round(t1, 6),
                      "code_path_fingerprint": fp})
    return {
        "code_path_fingerprint": fp,
        "phase_log": phase_log,
        "target_seed": target_seed,
        "planted_pair": [target["true_word_i"], target["true_word_j"]],
        "raw_solution_count": mitm["raw_solution_count"],
        "raw_solutions": [list(s) for s in mitm["raw_solutions"]],
        "certificate_verified_count": len(verified),
        "certificate_verified_solutions": [list(s) for s in verified],
        "certificate_of_first_verified": (certs[first_verified_index][2]
                                          if first_verified_index is not None
                                          else None),
        "planted_pair_recovered": ([target["true_word_i"],
                                    target["true_word_j"]]
                                   in [list(s) for s in verified]),
        "matching_window_hits": mitm["matching_window_hits"],
        "chunk_evals_to_first_raw_candidate":
            mitm["chunk_evals_to_first_raw_candidate"],
        "chunk_evals_to_first_certificate_verified_match":
            chunk_evals_to_first_verified,
        "total_chunk_evaluations": mitm["total_chunk_evaluations"],
        "step_evaluations": mitm["step_evaluations"],
        "naive_all_pairs_cost_modeled": (1 << params.k1) * (1 << params.k2),
        "wall_seconds": round(t1 - t0, 6),
    }


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------

def _run_result_parameters(args, params: ConstructionParams | None) -> dict:
    return {
        "mode": args.mode,
        "primitive": args.primitive,
        "construction": args.slice,
        "parameter_tuple": (params.as_tuple_dict() if params else None),
        "seed_fixed_word_generation": args.seed,
        "target_seed": args.target_seed,
        "n_target": args.n_target,
        "deadline_seconds": args.deadline,
        "experiment_id": args.exp_id,
        "requested_policy": "executor-implementation",
        "caveat_refs": CAVEAT_REFS,
        "quarantine_attestation": (
            "This run read nothing under coordination/goals/GOAL-MD5-001/"
            "quarantine/ (SC-6, IR-5). No derivation from "
            "MD5-COLLISION-PATH-WANG-2004-199.yaml exists in this module."),
    }


def _cost_model_block(args) -> dict:
    return {
        "operation_unit": "chunk_evaluation (one chunk1_observable or "
                          "chunk2_observable call) and step_evaluation (one "
                          "Round-1 forward_step or backward_step)",
        "assumptions": [
            "MEASURED: every wall-clock figure in this run's manifest is "
            "wrapper-measured by harness.runner.run_wrapped.",
            "OPTIMISTIC ASSUMPTION: single-core, unoptimized CPython; no "
            "vectorization and no compiled inner loop.",
            "OPTIMISTIC ASSUMPTION: no memory-bandwidth accounting; the "
            "chunk1 table fits trivially in cache at every scale run here.",
            "OPTIMISTIC ASSUMPTION: no time-memory tradeoff is exercised at "
            "this scale.",
            "MODELED, NOT MEASURED: naive_all_pairs_cost_modeled is the "
            "arithmetic 2^(k1+k2), not a timed run.",
            "NO PROJECTION toward the approximately 2^64-block "
            "instrument-class gap is made or licensed (IR-10, SC-3).",
        ],
        "caveat_refs": CAVEAT_REFS,
        "notes": "Toy scale: Round-1 restricted, 2 of 16 message words free, "
                 "20-bit target. No transfer to the full primitive is claimed.",
    }


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="R1-SEP10 Round-1 MITM instrument (GOAL-MD5-001 "
                    "BATCH-7215fa, EXP-MDFIVE-a8e71e).")
    ap.add_argument("--mode", required=True,
                    choices=["buildcheck", "gate_and_controls", "primary",
                             "h1", "vector_check"])
    ap.add_argument("--primitive", choices=["md4", "md5"], default="md4")
    ap.add_argument("--slice", choices=["r1_sep10", "batch4_slice"],
                    default="r1_sep10")
    ap.add_argument("--seed", type=int, default=20260821)
    ap.add_argument("--target-seed", type=int, default=8975324)
    ap.add_argument("--k1", type=int, default=10)
    ap.add_argument("--k2", type=int, default=10)
    ap.add_argument("--n-target", type=int, default=1000)
    ap.add_argument("--deadline", type=float, default=None)
    ap.add_argument("--out-root", default=None)
    ap.add_argument("--exp-id", default="EXP-MDFIVE-a8e71e")
    ap.add_argument("--exp-area", default="MDFIVE")
    ap.add_argument("--run-suffix", required=False, default=None)
    args = ap.parse_args(argv)

    if args.mode == "vector_check":
        print(json.dumps({"pins": check_input_pins(),
                          "rfc1320": check_rfc1320_vectors(),
                          "md5_t16": check_md5_t16()["all_ok"]}, indent=2))
        return 0

    repo = _repo_root()
    if repo not in sys.path:
        sys.path.insert(0, repo)
    from harness import runner

    def fn():
        params = None
        if args.mode == "buildcheck":
            raw = do_buildcheck()
            metrics = {
                "input_pins_ok": raw["input_pins"]["all_ok"],
                "CTL_PO7_rfc1320_all_ok": raw["CTL_PO7_rfc1320_vectors"]["all_ok"],
                "CTL_PO7_md5_t16_all_ok": raw["CTL_PO7_md5_t16_selfcheck"]["all_ok"],
                "CTL_PO6_h2_md4_all_ok": raw["CTL_PO6_h2_md4"]["all_ok"],
                "CTL_PO6_h2_md5_all_ok": raw["CTL_PO6_h2_md5"]["all_ok"],
                "CTL_PO9_all_ok": all(v["all_ok"] for v in
                                      raw["CTL_PO9_component_identity"].values()),
                "all_gates_passed": raw["all_gates_passed"],
            }
        elif args.mode == "gate_and_controls":
            raw = do_gate_and_controls()
            metrics = {
                "gate_verdict": raw["gate"]["verdict"],
                "gate_failing_clauses": raw["gate"]["failing_clauses"],
                "phase_A_predicate": raw["phase_A"]["predicate"],
                "phase_A_distinct_fwd_32bit": raw["phase_A"]["distinct_fwd_32bit_by_held_fixed"],
                "phase_A_distinct_bwd_32bit": raw["phase_A"]["distinct_bwd_32bit_by_held_fixed"],
                "phase_A_distinct_bwd_12bit": raw["phase_A"]["distinct_bwd_12bit_by_held_fixed"],
                "phase_A_distinct_fiber_sets": raw["phase_A"]["joint_fiber"]["distinct_fiber_sets"],
                "phase_B_predicate": raw["phase_B"]["predicate"],
                "phase_B_distinct_fwd_32bit": raw["phase_B"]["distinct_fwd_32bit_by_held_fixed"],
                "phase_B_distinct_fwd_12bit": raw["phase_B"]["distinct_fwd_12bit_by_held_fixed"],
                "phase_B_distinct_bwd_32bit": raw["phase_B"]["distinct_bwd_32bit_by_held_fixed"],
                "phase_B_distinct_bwd_12bit": raw["phase_B"]["distinct_bwd_12bit_by_held_fixed"],
                "phase_B_distinct_fiber_sets": raw["phase_B"]["joint_fiber"]["distinct_fiber_sets"],
                "phase_C_predicate": raw["phase_C"]["predicate"],
                "phase_C_distinct_fwd_32bit": raw["phase_C"]["distinct_fwd_32bit_by_held_fixed"],
                "phase_C_distinct_bwd_32bit": raw["phase_C"]["distinct_bwd_32bit_by_held_fixed"],
                "phase_C_distinct_fiber_sets": raw["phase_C"]["joint_fiber"]["distinct_fiber_sets"],
            }
            ctl = raw.get("k1_k2_6_controls")
            if ctl:
                metrics.update({
                    "CTL_PO4_sets_equal": ctl["CTL_PO4_completeness"]["sets_equal"],
                    "CTL_PO5_passed": ctl["CTL_PO5_raw_set_degeneracy"]["passed"],
                    "CTL_PO5_raw_candidate_count": ctl["CTL_PO5_raw_set_degeneracy"]["raw_candidate_count"],
                    "CTL_PO5_distinct_wA": ctl["CTL_PO5_raw_set_degeneracy"]["distinct_wA_in_raw_set"],
                    "CTL_PO5_distinct_wB": ctl["CTL_PO5_raw_set_degeneracy"]["distinct_wB_in_raw_set"],
                    "CTL_H1B_forward_v6_distinct_32bit": ctl["CTL_H1B_paired_contrast"]["forward_v6_distinct_32bit"],
                    "CTL_H1B_backward_v6_distinct_32bit": ctl["CTL_H1B_paired_contrast"]["backward_v6_distinct_32bit"],
                    "CTL_H1B_backward_v8_distinct_32bit": ctl["CTL_H1B_paired_contrast"]["backward_v8_distinct_32bit"],
                })
        elif args.mode == "primary":
            params = _params(args.primitive, args.slice, args.k1, args.k2)
            fixed = fixed_word_generation(args.seed,
                                          (params.i_word, params.j_word),
                                          args.k1)
            raw = do_primary(args.target_seed, params, fixed)
            metrics = {
                "raw_solution_count": raw["raw_solution_count"],
                "certificate_verified_count": raw["certificate_verified_count"],
                "planted_pair_recovered": raw["planted_pair_recovered"],
                "matching_window_hits": raw["matching_window_hits"],
                "chunk_evals_to_first_certificate_verified_match":
                    raw["chunk_evals_to_first_certificate_verified_match"],
                "total_chunk_evaluations": raw["total_chunk_evaluations"],
                "step_evaluations": raw["step_evaluations"],
                "naive_all_pairs_cost_modeled": raw["naive_all_pairs_cost_modeled"],
            }
        else:  # h1
            params = _params(args.primitive, args.slice, args.k1, args.k2)
            fixed = fixed_word_generation(args.seed,
                                          (params.i_word, params.j_word),
                                          args.k1)
            raw = h1_sampling(args.target_seed, params, fixed, args.n_target,
                              args.deadline)
            metrics = {
                "achieved_n": raw["achieved_n"],
                "requested_n": raw["requested_n"],
                "halted_before_target_n": raw["halted_before_target_n"],
                "lambda_predicted": raw["lambda_predicted"],
                "mean_matching_window_hits": raw["mean_matching_window_hits"],
                "sample_variance_matching_window":
                    raw["sample_variance_matching_window"],
                "sample_variance_classification":
                    raw["sample_variance_classification"],
                "chi2_statistic": raw["chi_square_goodness_of_fit"].get("chi2_statistic"),
                "chi2_p_value": raw["chi_square_goodness_of_fit"].get("p_value"),
                "chi2_df": raw["chi_square_goodness_of_fit"].get("df"),
                "tail_largest_observed": raw["tail_check"]["largest_observed_matching_window_count"],
                "tail_p_value": raw["tail_check"]["poisson_sf_p_value"],
                "mean_full_target_hits": raw["mean_full_target_hits"],
            }
        hv = None
        if args.mode == "h1":
            hv = {
                "heuristic_id": "HEUR-H1",
                "statement_ref": "ledger/hypotheses/H-MDFIVE-0ca596.yaml "
                                 "HEUR-H1; frozen prediction at "
                                 "experiments/EXP-MDFIVE-a8e71e/"
                                 "specification.yaml preregistered_prediction",
                "prediction": "Poisson(lambda = 2^(k1+k2-m) = 2^8 = 256) for "
                              "the matching-window (12-bit) collision count "
                              "per target; lambda FIXED A PRIORI",
                "theoretical_distribution": "poisson(256)",
                "sample_size": raw["achieved_n"],
                "scale_relevance": (
                    "toy: Round-1 restricted (16 of 48 MD4 / 64 MD5 steps), 2 "
                    "of 16 message words free, k1=k2=10, m=12, k=20, one "
                    "fixed-word seed. NO transfer or extrapolation to the "
                    "full primitive is claimed."),
                "executor_note": ("Comparison statistics only. The Executor "
                                  "composes no validated/refuted verdict on "
                                  "HEUR-H1 (agents/executor.md 13)."),
                "caveat_refs": CAVEAT_REFS,
            }
        return runner.RunResult(
            run_suffix=args.run_suffix or f"b5-{args.mode}",
            curve_id=f"R1SEP10-{args.primitive.upper()}",
            seed=args.seed,
            parameters=_run_result_parameters(args, params),
            metrics=metrics,
            certificate={"kind": "none"},
            raw=raw,
            stdout=json.dumps(raw, indent=2, sort_keys=True, default=str) + "\n",
            cost_model=_cost_model_block(args),
            heuristic_validation=hv,
        )

    run_id = runner.run_wrapped(args.exp_id, args.exp_area, fn,
                                status="completed_valid",
                                command=" ".join(sys.argv),
                                out_root=args.out_root)
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
