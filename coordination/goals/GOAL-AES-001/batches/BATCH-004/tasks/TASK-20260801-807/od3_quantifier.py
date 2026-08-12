#!/usr/bin/env python3
"""
od3_quantifier.py -- TASK-20260801-807, GOAL-AES-001 BATCH-004.

WHAT THIS IS.  A finite, exhaustive computation in a SCALED-DOWN GF(2^4)
ANALOGUE of the AES super-box interface, addressing two things:

  (b) D-705-5 HOLE (ii), the RESTRICTED STATE QUANTIFIER.  PROP-701-I's
      hypothesis (H2) demands deterministic propagation for EVERY state s.
      Step 2 of its proof consumes that quantifier at a named place: it needs
      u_k = sum_l M[k][l] y_l + (k_j)_k to range over ALL of F as u ranges over
      the hyperplane U_i.  This script COMPUTES, rather than argues, how much of
      F the coordinate u_k actually reaches when the state set is restricted to
      a structured subset S, over an EXHAUSTIVE enumeration of all 2^16
      coordinate-active patterns and over a seeded sample of GF(2)-affine
      subspaces, and then computes the fixpoint of the whole Step1/Step2/Step3
      machinery under the restriction.

  (a) OD-3, SET-VALUED OBJECTS.  A single-interface witness computation
      separating the set-valued per-word objects that the set-valued analogue of
      (H2) can permit from those it forbids.

WHAT THIS IS NOT.  It is NOT a cryptanalytic result, NOT a distinguisher, NOT a
barrier statement, and it asserts NOTHING about AES at any round count or about
deployed AES.  The GF(2^4) setting IS AN ANALOGUE: its readings are not evidence
about GF(2^8) and are certainly not about AES.  Nothing here is built on
PROP-701-I being TRUE (KN-FIND-017 declines to assert it); the computation is
about what its PROOF does under a weakened hypothesis.

SUPERSESSION.  This file supersedes NOTHING.  It is a new artifact.  It reuses
the GF(2^4) analogue and the field modulus of the committed BATCH-003 artifact
od1_gate701c_v2.py, which is NOT modified, NOT re-run and NOT imported; the
field arithmetic and the strong-connectivity computation are re-implemented
here from scratch so that agreement with the BATCH-003 readings, where the two
overlap, is an independent check rather than a shared assumption.

DETERMINISM.  The only randomness is in --phase gf2 and --phase od3, both of
which use random.Random(seed) with the seed recorded in the output JSON.  Every
other phase is an exhaustive enumeration in a fixed order and uses no random
source at all.

inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    Structural.  Under this Claude Code harness the
    orchestration/model-policies.yaml policy aliases cannot be resolved by
    subagent frontmatter (CLAUDE.md, "Model policy note"); all subagents run
    `model: inherit`.  The requested policy is recorded and the resolved model
    is recorded; no silent substitution.
  model_verified: false        # `python3 -m orchestration.adapter doctor --probe` NOT run
  reasoning_effort: unrecorded
  independent_session: false
  standing_basis: inference-amendment commit 0137a051eb5828789eb267fa83c8278086578d4c
  provenance_basis: >-
    protocol-amendment-GOAL-AES-001-004 Part B: this is a SOURCE-CODE artifact,
    so it carries this comment-block inference stanza in its own text AND is
    listed with its SHA-256 in the artifact_provenance list of
    od3_results.json.

Usage:
    python3 od3_quantifier.py --phase sweep
    python3 od3_quantifier.py --phase gf2
    python3 od3_quantifier.py --phase closure
    python3 od3_quantifier.py --phase od3
    python3 od3_quantifier.py --phase all
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
import time
from typing import Dict, List, Sequence, Tuple

# ===========================================================================
# GF(2^4) analogue arithmetic.  Modulus x^4 + x + 1 (primitive), matching the
# analogue used by GATE-701-C v2 in TASK-20260801-801.
# ===========================================================================

MOD4 = 0x13


def gmul(a: int, b: int) -> int:
    a &= 0xF
    b &= 0xF
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & 0x10:
            a ^= MOD4
    return r & 0xF


F = list(range(16))
FSTAR = list(range(1, 16))


def circulant(first_row: Sequence[int]) -> Tuple[Tuple[int, ...], ...]:
    """M[i][j] = c[(j - i) mod 4], the AES MixColumns shape."""
    c = tuple(first_row)
    return tuple(tuple(c[(j - i) % 4] for j in range(4)) for i in range(4))


M_TARGET = circulant((0x02, 0x03, 0x01, 0x01))
M_IDENTITY = tuple(tuple(1 if i == j else 0 for j in range(4)) for i in range(4))


def det4(M) -> int:
    """Determinant over GF(2^4) by Leibniz expansion (4x4, 24 terms)."""
    tot = 0
    for perm in itertools.permutations(range(4)):
        term = 1
        for i, j in enumerate(perm):
            term = gmul(term, M[i][j])
        tot ^= term          # characteristic 2: sign is irrelevant
    return tot


def is_invertible(M) -> bool:
    return det4(M) != 0


# --- word encoding: a word is (y0,y1,y2,y3) in F^4, packed little-nibble ------

def enc(y: Sequence[int]) -> int:
    return y[0] | (y[1] << 4) | (y[2] << 8) | (y[3] << 12)


def dec(w: int) -> Tuple[int, int, int, int]:
    return (w & 0xF, (w >> 4) & 0xF, (w >> 8) & 0xF, (w >> 12) & 0xF)


# Addition in F^4 is nibble-wise XOR, i.e. XOR of the 16-bit codes.
NWORDS = 1 << 16


def matvec(M, y: Sequence[int]) -> Tuple[int, int, int, int]:
    return tuple(
        gmul(M[i][0], y[0]) ^ gmul(M[i][1], y[1]) ^ gmul(M[i][2], y[2]) ^ gmul(M[i][3], y[3])
        for i in range(4)
    )


# ===========================================================================
# The interface geometry, exactly as PROP-701-I states it.
#
#   state  : 4 words w_0..w_3, each in F^4; position (row i, word p).
#   ShiftRows offsets (0,1,2,3): the pre-MixColumns vector of OUTPUT word j is
#            y^(j)_i = w_{(j+i) mod 4}[i].
#   output : word_j(Phi(s)) = M y^(j) + k_j.
#   input word p contributes to output word j exactly at row i = (p - j) mod 4,
#   equivalently j = (p - i) mod 4.  (PROP-701-I states this for p = 1 as
#   i_j = (1 - j) mod 4; the general form is used here.)
# ===========================================================================

def diag_positions(j: int) -> Tuple[Tuple[int, int], ...]:
    """The four state positions (row l, word (j+l) mod 4) feeding output word j."""
    return tuple((l, (j + l) % 4) for l in range(4))


def free_set(active: frozenset, p: int, i: int) -> Tuple[int, ...]:
    """
    J_p(i): the coordinates l != i of y^(j), j = (p-i) mod 4, whose state
    position is ACTIVE (free) in the restricted state set.  These are exactly
    the coordinates Step 1 calls "free", and Step 2's sweep of u_k is driven by
    them.
    """
    j = (p - i) % 4
    return tuple(l for l in range(4) if l != i and (l, (j + l) % 4) in active)


# ===========================================================================
# PHASE `sweep`.  How much of F does u_k reach?
#
# For a state set S that is a coset of a COORDINATE subspace -- equivalently, a
# set in which each of the 16 state positions is either FREE (ranges over all of
# F) or FIXED to a constant -- the achievable pre-MixColumns vectors for output
# word j, given input word p held at the value a, are
#     { y : y_i = a_i, y_l free for l in J_p(i), y_l = c_l otherwise }
# and Step 2's sweep set is  reach_k = { (M y)_k + (k_j)_k : y in that set }.
#
# The reach sets are computed by EXPLICIT ENUMERATION over y for every
# (i, J, fixed-values, k) shape; the exhaustive pass over all 2^16 active
# patterns then looks the computed value up.  The enumeration is the
# computation; the lookup is deduplication of identical enumerations.
# ===========================================================================

def reach_by_enumeration(M, i: int, J: Tuple[int, ...], fixed_vals: Dict[int, int],
                         a_i: int, kj: Tuple[int, int, int, int]) -> Dict[int, int]:
    """Explicitly enumerate y and return {k: |reach_k|}."""
    reach = [set() for _ in range(4)]
    others = [l for l in range(4) if l != i]
    ranges = []
    for l in others:
        ranges.append(F if l in J else [fixed_vals.get(l, 0)])
    for combo in itertools.product(*ranges):
        y = [0, 0, 0, 0]
        y[i] = a_i
        for l, v in zip(others, combo):
            y[l] = v
        u = matvec(M, y)
        for k in range(4):
            reach[k].add(u[k] ^ kj[k])
    return {k: len(reach[k]) for k in range(4)}


def phase_sweep(M, matrix_name: str) -> dict:
    t0 = time.time()
    # 1. Direct enumeration for every (i, J) shape, with zero constants and zero
    #    round key, and separately with SEEDED NONZERO constants and round key,
    #    to CHECK rather than assume that the reach SIZES do not depend on them.
    rng = random.Random(80720260801)
    shapes = {}
    shapes_nonzero = {}
    for i in range(4):
        others = [l for l in range(4) if l != i]
        for r in range(4):
            for Jt in itertools.combinations(others, r):
                J = tuple(Jt)
                key = f"i={i},J={list(J)}"
                shapes[key] = reach_by_enumeration(M, i, J, {}, 0, (0, 0, 0, 0))
                fixed = {l: rng.randrange(1, 16) for l in others if l not in J}
                kj = tuple(rng.randrange(1, 16) for _ in range(4))
                shapes_nonzero[key] = reach_by_enumeration(
                    M, i, J, fixed, rng.randrange(1, 16), kj)
    constants_irrelevant = (shapes == shapes_nonzero)

    # 2. Exhaustive pass over all 2^16 coordinate-active patterns A.
    positions = [(i, p) for p in range(4) for i in range(4)]
    reach_value_multiset: Dict[str, int] = {}
    full_argument_patterns = 0
    step1_admissible_patterns = 0
    examples_full = []
    for bits in range(NWORDS):
        active = frozenset(positions[b] for b in range(16) if (bits >> b) & 1)
        admissible = False
        full_arg = False
        for p in range(4):
            rows_p = [i for i in range(4) if (i, p) in active]
            if not rows_p:
                continue
            admissible = True
            # the FULL unrestricted argument needs |J_p(i)| = 3 for every row i
            if all(len(free_set(active, p, i)) == 3 for i in range(4)) and rows_p:
                full_arg = True
        if admissible:
            step1_admissible_patterns += 1
        if full_arg:
            full_argument_patterns += 1
            if len(examples_full) < 5:
                examples_full.append(sorted(active))
        # tally reach sizes over the admissible (p,i,k)
        for p in range(4):
            if not any((i, p) in active for i in range(4)):
                continue
            for i in range(4):
                if (i, p) not in active:
                    continue    # Delta cannot be supported on a frozen row of word p
                J = free_set(active, p, i)
                sizes = shapes[f"i={i},J={list(J)}"]
                for k in range(4):
                    key = str(sizes[k])
                    reach_value_multiset[key] = reach_value_multiset.get(key, 0) + 1

    # 3. The four NAMED families, reported individually.
    named = {}
    for name, active in named_families().items():
        rows = []
        for p in range(4):
            if not any((i, p) in active for i in range(4)):
                continue
            for i in range(4):
                if (i, p) not in active:
                    continue
                J = free_set(active, p, i)
                sizes = shapes[f"i={i},J={list(J)}"]
                rows.append({"collision_word_p": p, "row_i": i,
                             "output_word_j": (p - i) % 4,
                             "free_coords_J": list(J),
                             "reach_sizes_per_k": [sizes[k] for k in range(4)]})
        named[name] = {
            "active_positions_row_word": sorted(active),
            "n_active": len(active),
            "step1_admissible": bool(rows),
            "configurations": rows,
            "sweep_full_everywhere": bool(rows) and all(
                all(s == 16 for s in r["reach_sizes_per_k"]) for r in rows),
            "sweep_full_somewhere": any(
                all(s == 16 for s in r["reach_sizes_per_k"]) for r in rows),
        }

    return {
        "phase": "sweep",
        "matrix": matrix_name,
        "distinct_reach_sizes_observed": sorted({int(k) for k in reach_value_multiset}),
        "reach_size_histogram_over_all_admissible_configurations": reach_value_multiset,
        "reach_by_shape_i_J": shapes,
        "constants_and_round_key_do_not_change_reach_sizes": constants_irrelevant,
        "constants_check_seed": 80720260801,
        "patterns_total": NWORDS,
        "patterns_with_step1_admissible": step1_admissible_patterns,
        "patterns_admitting_the_full_unrestricted_argument": full_argument_patterns,
        "examples_of_full_argument_patterns": examples_full,
        "named_families": named,
        "wall_clock_seconds": round(time.time() - t0, 3),
    }


def named_families() -> Dict[str, frozenset]:
    """
    The named and justified family of structured state subsets S.  Positions are
    (row i, word p).  A position in the set is FREE; every other position is
    FIXED to a constant, so each entry is a coset of a coordinate subspace.
    """
    fam: Dict[str, frozenset] = {}
    fam["A_full_unrestricted"] = frozenset((i, p) for p in range(4) for i in range(4))
    fam["delta_set_1_active_byte_r0w0"] = frozenset({(0, 0)})
    fam["delta_set_1_active_byte_r1w2"] = frozenset({(1, 2)})
    fam["delta_set_2_active_bytes_same_word"] = frozenset({(0, 0), (1, 0)})
    fam["delta_set_2_active_bytes_same_diagonal"] = frozenset({(0, 0), (1, 1)})
    fam["delta_set_4_active_bytes_one_diagonal_j0"] = frozenset(diag_positions(0))
    fam["delta_set_4_active_bytes_one_word_w0"] = frozenset({(i, 0) for i in range(4)})
    fam["delta_set_4_active_bytes_one_row_r0"] = frozenset({(0, p) for p in range(4)})
    fam["delta_set_8_active_bytes_two_diagonals"] = frozenset(
        set(diag_positions(0)) | set(diag_positions(1)))
    fam["fixed_byte_set_one_byte_fixed_r0w0"] = frozenset(
        {(i, p) for p in range(4) for i in range(4)} - {(0, 0)})
    fam["fixed_byte_set_word1_entirely_fixed"] = frozenset(
        {(i, p) for p in range(4) for i in range(4) if p != 1})
    fam["minimal_full_argument_12_off_word1_plus_one"] = frozenset(
        {(i, p) for p in range(4) for i in range(4) if p != 1} | {(0, 1)})
    return fam


# ===========================================================================
# PHASE `gf2`.  State sets that are GF(2)-affine but not F-affine.
#
# A structured subset need not be an F-subspace.  For a GF(2)-subspace V of the
# state space F^16 = GF(2)^64, the reach of u_k is a GF(2)-subspace of F, so its
# size is a power of two and INTERMEDIATE values between 1 and |F| are possible.
# Measured over a seeded sample by explicit enumeration of V.
# ===========================================================================

def phase_gf2(M, seed: int = 807042026, samples: int = 40,
              condition_on_step1_pair: bool = False) -> dict:
    """
    RECORDED DEVIATION.  The first design (condition_on_step1_pair=False) draws
    the GF(2)-subspace uniformly and then looks for a Step-1 pair.  It was run
    first and produced ZERO admissible instances, for a reason that is clear
    after the fact: a uniformly random GF(2)-subspace of dimension <= 12 inside
    the 64-dimensional state space almost never contains a nonzero vector
    supported entirely on one word.  Both designs are run and both readings are
    reported; the pre-registered prediction P_b6 is NOT altered.
    """
    t0 = time.time()
    rng = random.Random(seed)
    positions = [(i, p) for p in range(4) for i in range(4)]
    pos_index = {pos: n for n, pos in enumerate(positions)}
    results = []
    hist: Dict[str, int] = {}
    for dim in (2, 4, 6, 8, 10, 12):
        for trial in range(samples):
            # random GF(2)-subspace of the 64-bit state space, dimension <= dim
            basis = [rng.getrandbits(64) for _ in range(dim)]
            p_pre = rng.randrange(4)
            if condition_on_step1_pair:
                # force one basis vector supported entirely on word p_pre, so a
                # Step-1 pair (two states differing only in word p_pre) exists
                v = 0
                while v == 0:
                    v = 0
                    for r in range(4):
                        v |= rng.randrange(16) << (4 * (4 * p_pre + r))
                basis[0] = v
            elements = [0]
            for b in basis:
                elements = elements + [e ^ b for e in elements]
            elements = sorted(set(elements))
            # decode: state position n occupies nibble n of the 64-bit word
            p = p_pre if condition_on_step1_pair else rng.randrange(4)
            i = rng.randrange(4)
            j = (p - i) % 4
            # y^(j)_l = state[(l, (j+l) mod 4)]
            ycoords = [pos_index[(l, (j + l) % 4)] for l in range(4)]
            wp = [pos_index[(r, p)] for r in range(4)]
            # Step 1 needs a pair of states in S differing ONLY in word p.
            # Collect the achievable (word-p value, y-vector) pairs.
            byword: Dict[int, List[Tuple[int, ...]]] = {}
            for e in elements:
                nib = [(e >> (4 * n)) & 0xF for n in range(16)]
                rest = tuple(nib[n] for n in range(16) if n not in wp)
                wpv = tuple(nib[n] for n in wp)
                y = tuple(nib[n] for n in ycoords)
                byword.setdefault(hash((rest,)), []).append((wpv, y, e))
            # a Step-1 pair: two elements agreeing off word p, differing on it
            pair_found = False
            reach_sizes = None
            for group in byword.values():
                if len(group) < 2:
                    continue
                a = group[0]
                b = group[1]
                if a[0] == b[0]:
                    continue
                pair_found = True
                a_i = a[1][i]
                # U_i: all y achievable from S with word p value fixed to a's word p
                seen = [set() for _ in range(4)]
                for (wpv, y, e) in [g for g in group]:
                    pass
                # sweep set: y ranges over achievable vectors with y_i = a_i
                for e in elements:
                    nib = [(e >> (4 * n)) & 0xF for n in range(16)]
                    y = [nib[n] for n in ycoords]
                    if y[i] != a_i:
                        continue
                    u = matvec(M, y)
                    for k in range(4):
                        seen[k].add(u[k])
                reach_sizes = [len(seen[k]) for k in range(4)]
                break
            if not pair_found:
                continue
            for s in reach_sizes:
                hist[str(s)] = hist.get(str(s), 0) + 1
            results.append({"gf2_dim_requested": dim, "subspace_size": len(elements),
                            "collision_word_p": p, "row_i": i, "output_word_j": j,
                            "reach_sizes_per_k": reach_sizes})
    return {
        "phase": "gf2",
        "design": ("conditioned_on_step1_pair" if condition_on_step1_pair
                   else "uniform_random_subspace"),
        "seed": seed,
        "samples_per_dim": samples,
        "dims": [2, 4, 6, 8, 10, 12],
        "instances_with_a_step1_pair": len(results),
        "reach_size_histogram": hist,
        "distinct_reach_sizes_observed": sorted({int(k) for k in hist}),
        "intermediate_sizes_observed": sorted({int(k) for k in hist if 1 < int(k) < 16}),
        "instances": results[:60],
        "instances_truncated_to": 60,
        "wall_clock_seconds": round(time.time() - t0, 3),
    }


# ===========================================================================
# PHASE `closure`.  The fixpoint of Steps 1-3 under a restricted state set.
#
# Knowledge state: for each translation t, a bitmask W_t over F^4 recording the
# w for which the machinery has established pi(w) = pi(w + t).
#
# RULE (the restricted Step 1, applied uniformly, which is also what Step 2 and
# Step 3 do -- Step 2 is this rule applied to a pair produced by itself, Step 3
# is its transitive closure):
#   given t and a in W_t, and an input word p such that
#       (i)  t is supported on the ACTIVE rows of word p, and
#       (ii) a is an achievable word-p value in S,
#   then for every row i with t_i != 0,
#       W_{t_i m_i}  |=  { M y + k_j : y_i = a_i, y_l free for l in J_p(i),
#                          y_l = c_l otherwise },  j = (p-i) mod 4.
#
# CONSTANCY VERDICT: pi is forced constant when the GF(2)-span of
#   T_full = { t : W_t = F^4 }
# is all of F^4.  That is exactly PROP-701-I's Step 3 conclusion route (the
# translations leaving pi invariant form a group, so global invariances span).
# When constancy is NOT forced, the surviving partition of F^4 under the
# established invariances is computed as a CERTIFICATE for a bounded number of
# cases.
#
# CLOSURE UNDER UNION.  The rule fires per (t, a) pair independently, so
# closure(X union Y) = closure(X) union closure(Y).  Hence it suffices to run
# the fixpoint from SINGLE seeds (p, i, lambda): the closure from an arbitrary
# collision difference Delta is the union of the closures of its single
# coordinates, and the binding case for PROP-701-I (which must handle EVERY
# collision) is the weakest single seed.
# ===========================================================================

ALL_MASK = (1 << NWORDS) - 1

_BYTE_BITS = [[b for b in range(8) if (v >> b) & 1] for v in range(256)]


def mask_from_indices(idxs) -> int:
    """Build a 65536-bit mask from an iterable of indices, via a bytearray.

    Doing this with repeated `m |= 1 << idx` on a 65536-bit int copies 8 KB per
    set bit and is quadratic in practice; the bytearray route is linear.
    """
    ba = bytearray(NWORDS // 8)
    for x in idxs:
        ba[x >> 3] |= 1 << (x & 7)
    return int.from_bytes(bytes(ba), "little")


def mask_to_indices(m: int) -> List[int]:
    ba = m.to_bytes(NWORDS // 8, "little")
    out: List[int] = []
    for n, v in enumerate(ba):
        if v:
            base = n << 3
            for b in _BYTE_BITS[v]:
                out.append(base + b)
    return out


class ClosureEngine:
    def __init__(self, M, active: frozenset):
        self.M = M
        self.active = active
        self.cols = [tuple(M[r][c] for r in range(4)) for c in range(4)]   # m_c
        # translations of interest: lambda * m_c
        self.trans = {}
        for c in range(4):
            for lam in FSTAR:
                self.trans[enc(tuple(gmul(lam, self.cols[c][r]) for r in range(4)))] = True
        # U masks, indexed by (p, i, a_i)
        self.umask: Dict[Tuple[int, int, int], int] = {}
        for p in range(4):
            for i in range(4):
                J = free_set(active, p, i)
                others = [l for l in range(4) if l != i]
                ranges = [F if l in J else [0] for l in others]
                combos = list(itertools.product(*ranges))
                for ai in F:
                    idxs = []
                    for combo in combos:
                        y = [0, 0, 0, 0]
                        y[i] = ai
                        for l, v in zip(others, combo):
                            y[l] = v
                        idxs.append(enc(matvec(M, y)))
                    self.umask[(p, i, ai)] = mask_from_indices(idxs)
        # allowed word-p values with a given i-th coordinate
        self.allowed_val: Dict[Tuple[int, int, int], int] = {}
        for p in range(4):
            rows = [r for r in range(4) if (r, p) in active]
            for i in range(4):
                for ai in F:
                    idxs = []
                    if i in rows or ai == 0:
                        ranges = [F if r in rows else [0] for r in range(4)]
                        for y in itertools.product(*ranges):
                            if y[i] != ai:
                                continue
                            idxs.append(enc(y))
                    self.allowed_val[(p, i, ai)] = mask_from_indices(idxs)
        # which words p can carry a given translation t (t supported on active rows)
        self.word_rows = {p: [r for r in range(4) if (r, p) in active] for p in range(4)}

    def run(self, seed_p: int, seed_i: int, seed_lam: int, a_i: int = 0) -> dict:
        W: Dict[int, int] = {}
        t0 = enc(tuple(gmul(seed_lam, self.cols[seed_i][r]) for r in range(4)))
        W[t0] = self.umask[(seed_p, seed_i, a_i)]
        done = set()
        changed = True
        iters = 0
        while changed:
            changed = False
            iters += 1
            for t in list(W.keys()):
                td = dec(t)
                for p in range(4):
                    rows = self.word_rows[p]
                    if not rows:
                        continue
                    if any(td[r] != 0 for r in range(4) if r not in rows):
                        continue      # t not realisable as a word-p difference
                    for i in range(4):
                        if td[i] == 0:
                            continue
                        tnew = enc(tuple(gmul(td[i], self.cols[i][r]) for r in range(4)))
                        for ai in F:
                            job = (t, p, i, ai)
                            if job in done:
                                continue
                            if W[t] & self.allowed_val[(p, i, ai)] == 0:
                                continue
                            done.add(job)
                            add = self.umask[(p, i, ai)]
                            prev = W.get(tnew, 0)
                            if prev | add != prev:
                                W[tnew] = prev | add
                                changed = True
        full = [t for t, m in W.items() if m == ALL_MASK]
        return {"W": W, "translations_reached": len(W), "translations_full": len(full),
                "full_set": full, "iterations": iters,
                "span_dim_full": gf2_span_dim(full),
                "constancy_forced": gf2_span_dim(full) == 16}


def gf2_span_dim(vectors: Sequence[int]) -> int:
    """Dimension over GF(2) of the span of the given 16-bit codes."""
    basis: List[int] = []
    for v in vectors:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return len(basis)


def components(W: Dict[int, int]) -> dict:
    """Connected components of F^4 under the established invariances."""
    parent = list(range(NWORDS))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for t, m in W.items():
        if m == 0:
            continue
        for idx in mask_to_indices(m):
            union(idx, idx ^ t)
    sizes: Dict[int, int] = {}
    for x in range(NWORDS):
        r = find(x)
        sizes[r] = sizes.get(r, 0) + 1
    hist: Dict[str, int] = {}
    for s in sizes.values():
        hist[str(s)] = hist.get(str(s), 0) + 1
    return {"n_components": len(sizes), "component_size_histogram": hist}


def scc_count_lambda_k(M) -> dict:
    """Strong connectivity of the (lambda,k) graph, recomputed from scratch."""
    nodes = [(lam, k) for lam in FSTAR for k in range(4)]
    index = {n: i for i, n in enumerate(nodes)}
    adj = [[] for _ in nodes]
    for (lam, k) in nodes:
        for j in range(4):
            v = gmul(lam, M[j][k])
            if v != 0:
                adj[index[(lam, k)]].append(index[(v, j)])
    # Kosaraju
    seen = [False] * len(nodes)
    order: List[int] = []

    def dfs1(s):
        stack = [(s, iter(adj[s]))]
        seen[s] = True
        while stack:
            v, it = stack[-1]
            adv = next(it, None)
            if adv is None:
                order.append(v)
                stack.pop()
            elif not seen[adv]:
                seen[adv] = True
                stack.append((adv, iter(adj[adv])))
    for s in range(len(nodes)):
        if not seen[s]:
            dfs1(s)
    radj = [[] for _ in nodes]
    for v, lst in enumerate(adj):
        for w in lst:
            radj[w].append(v)
    comp = [-1] * len(nodes)
    c = 0
    for s in reversed(order):
        if comp[s] != -1:
            continue
        stack = [s]
        comp[s] = c
        while stack:
            v = stack.pop()
            for w in radj[v]:
                if comp[w] == -1:
                    comp[w] = c
                    stack.append(w)
        c += 1
    sizes: Dict[int, int] = {}
    for x in comp:
        sizes[x] = sizes.get(x, 0) + 1
    return {"n_nodes": len(nodes), "n_scc": c,
            "scc_size_histogram": sorted(sizes.values(), reverse=True),
            "strongly_connected": c == 1}


def pick_null_2() -> Tuple[Tuple[int, ...], ...]:
    """
    First invertible circulant whose first row contains EXACTLY ONE zero entry,
    in a FIXED a-priori lexicographic scan order over GF(2^4)^4.  The selection
    rule inspects only invertibility and the zero count; it never inspects any
    reading.
    """
    for c0 in F:
        for c1 in F:
            for c2 in F:
                for c3 in F:
                    row = (c0, c1, c2, c3)
                    if sum(1 for x in row if x == 0) != 1:
                        continue
                    Mn = circulant(row)
                    if is_invertible(Mn):
                        return row, Mn
    raise RuntimeError("no invertible circulant with exactly one zero entry")


def pick_null_3() -> Tuple[Tuple[int, ...], ...]:
    """
    First invertible circulant with ALL entries nonzero whose (lambda,k) graph
    is NOT strongly connected -- the sibling null that negates strong
    connectivity ALONE.  Fixed a-priori lexicographic scan order; the rule
    inspects only the matrix, never a reading.
    """
    for c0 in FSTAR:
        for c1 in FSTAR:
            for c2 in FSTAR:
                for c3 in FSTAR:
                    row = (c0, c1, c2, c3)
                    Mn = circulant(row)
                    if not is_invertible(Mn):
                        continue
                    if not scc_count_lambda_k(Mn)["strongly_connected"]:
                        return row, Mn
    raise RuntimeError("no such matrix")


def phase_closure(max_seconds: float = 420.0) -> dict:
    t0 = time.time()
    out: dict = {"phase": "closure", "time_cap_seconds": max_seconds,
                 "capped": False, "runs": [], "not_run": []}

    n2row, M_NULL2 = pick_null_2()
    n3row, M_NULL3 = pick_null_3()
    out["matrices"] = {
        "target": {"first_row": [0x02, 0x03, 0x01, 0x01],
                   "invertible": is_invertible(M_TARGET),
                   "all_entries_nonzero": all(M_TARGET[i][j] != 0 for i in range(4) for j in range(4)),
                   "lambda_k_graph": scc_count_lambda_k(M_TARGET)},
        "null_1_identity": {"first_row": [1, 0, 0, 0],
                            "invertible": is_invertible(M_IDENTITY),
                            "all_entries_nonzero": False,
                            "lambda_k_graph": scc_count_lambda_k(M_IDENTITY)},
        "null_2_one_zero_entry": {"first_row": list(n2row),
                                  "invertible": is_invertible(M_NULL2),
                                  "all_entries_nonzero": False,
                                  "lambda_k_graph": scc_count_lambda_k(M_NULL2)},
        "null_3_not_strongly_connected": {"first_row": list(n3row),
                                          "invertible": is_invertible(M_NULL3),
                                          "all_entries_nonzero": all(
                                              M_NULL3[i][j] != 0 for i in range(4) for j in range(4)),
                                          "lambda_k_graph": scc_count_lambda_k(M_NULL3)},
    }

    fam = named_families()
    A_full = fam["A_full_unrestricted"]

    jobs: List[Tuple[str, str, object, frozenset, List[Tuple[int, int, int]]]] = []
    # positive control and the three nulls, on the UNRESTRICTED state set,
    # p = 0 only (all four words are interchangeable when nothing is restricted;
    # this is CHECKED below for the target, not assumed).
    seeds_full = [(0, i, lam) for i in range(4) for lam in FSTAR]
    jobs.append(("positive_control_target_A_full", "target", M_TARGET, A_full, seeds_full))
    jobs.append(("null_1_identity_A_full", "null_1_identity", M_IDENTITY, A_full, seeds_full))
    jobs.append(("null_2_one_zero_entry_A_full", "null_2_one_zero_entry", M_NULL2, A_full, seeds_full))
    jobs.append(("null_3_not_strongly_connected_A_full", "null_3_not_strongly_connected",
                 M_NULL3, A_full, seeds_full))
    # p-symmetry check on the target, unrestricted
    jobs.append(("p_symmetry_check_target_A_full", "target", M_TARGET, A_full,
                 [(p, 0, 1) for p in range(4)]))
    # the restricted families, target matrix, ALL seeds (p, i, lambda)
    for name, active in fam.items():
        if name == "A_full_unrestricted":
            continue
        seeds = [(p, i, lam) for p in range(4) for i in range(4) for lam in FSTAR]
        jobs.append((f"restricted_{name}", "target", M_TARGET, active, seeds))

    comp_budget = 6
    for (label, mname, M, active, seeds) in jobs:
        if time.time() - t0 > max_seconds:
            out["capped"] = True
            out["not_run"].append({"job": label, "reason": "phase time cap reached"})
            continue
        eng = ClosureEngine(M, active)
        recs = []
        forced = 0
        attempted = 0
        for (p, i, lam) in seeds:
            if not eng.word_rows[p] or (i, p) not in active:
                continue     # Step 1 has no admissible collision pair here
            attempted += 1
            r = eng.run(p, i, lam)
            forced += 1 if r["constancy_forced"] else 0
            rec = {"seed_word_p": p, "seed_row_i": i, "seed_lambda": lam,
                   "translations_reached": r["translations_reached"],
                   "translations_full": r["translations_full"],
                   "span_dim_of_full_translations": r["span_dim_full"],
                   "constancy_forced": r["constancy_forced"]}
            if (not r["constancy_forced"]) and comp_budget > 0:
                rec["surviving_partition"] = components(r["W"])
                comp_budget -= 1
                rec["surviving_partition_note"] = (
                    "Connected components of F^4 under every invariance the machinery "
                    "established. A partition with more than one class and some class of "
                    "size > 1 is exactly a lossy pi that THIS ARGUMENT cannot exclude; it "
                    "is NOT a claim that such a pi propagates.")
            recs.append(rec)
        out["runs"].append({
            "job": label, "matrix": mname,
            "active_positions": sorted(active), "n_active": len(active),
            "seeds_attempted": attempted,
            "seeds_with_constancy_forced": forced,
            "constancy_forced_for_every_admissible_seed": attempted > 0 and forced == attempted,
            "step1_admissible_at_all": attempted > 0,
            "per_seed": recs[:64],
            "per_seed_truncated_to": 64,
            "elapsed_seconds": round(time.time() - t0, 3),
        })
    out["wall_clock_seconds"] = round(time.time() - t0, 3)
    out["component_certificates_budget"] = 6
    out["component_certificates_remaining"] = comp_budget
    return out


# ===========================================================================
# PHASE `od3`.  The group (a) coupling witness.
#
# The set-valued analogue of (H2) would demand that the object of OUTPUT word j
# on a state SET be a function of the objects of the four INPUT words on that
# same set -- i.e. a function of the four per-word MARGINALS.  ShiftRows makes
# each output word collect one byte from EACH input word, so the output depends
# on the JOINT content of the set across words.  The witness: two state sets with
# IDENTICAL per-word marginals and different coupling.  Whatever object is
# computed from the marginals alone must take the same value on both; whatever
# object separates them therefore CANNOT satisfy the set-valued (H2).
# ===========================================================================

def phase_od3(seed: int = 807032026, trials: int = 200) -> dict:
    t0 = time.time()
    rng = random.Random(seed)
    M = M_TARGET
    objects = ["xor_sum_of_output_word", "multiset_of_output_word",
               "support_size_of_output_word", "F_affine_rank_of_output_word",
               "multiset_of_output_byte_row0"]
    separated = {o: 0 for o in objects}
    marginals_equal_count = 0
    example = None
    for _ in range(trials):
        # two states s, s'; the two sets are S = {s, s'} and
        # T = {s with word0 of s', s' with word0 of s} -- identical per-word
        # marginals (each word position realises the same pair of values in both
        # sets), different coupling.
        s = [[rng.randrange(16) for _ in range(4)] for _ in range(4)]     # s[p][i]
        sp = [[rng.randrange(16) for _ in range(4)] for _ in range(4)]
        t1 = [list(sp[0])] + [list(s[p]) for p in range(1, 4)]
        t2 = [list(s[0])] + [list(sp[p]) for p in range(1, 4)]
        S = [s, sp]
        T = [t1, t2]
        # per-word marginals as multisets of word values
        def marg(setofstates):
            return [sorted(tuple(st[p]) for st in setofstates) for p in range(4)]
        if marg(S) != marg(T):
            continue
        marginals_equal_count += 1

        def out_words(st, j):
            y = [st[(j + l) % 4][l] for l in range(4)]
            return tuple(matvec(M, y))

        for j in range(4):
            outS = [out_words(st, j) for st in S]
            outT = [out_words(st, j) for st in T]
            # xor sum
            xs = tuple(a ^ b for a, b in zip(outS[0], outS[1]))
            xt = tuple(a ^ b for a, b in zip(outT[0], outT[1]))
            if xs != xt:
                separated["xor_sum_of_output_word"] += 1
            if sorted(outS) != sorted(outT):
                separated["multiset_of_output_word"] += 1
                if example is None:
                    example = {"output_word_j": j,
                               "set_S_states": S, "set_T_states": T,
                               "output_multiset_S": sorted(outS),
                               "output_multiset_T": sorted(outT),
                               "output_xor_sum_S": list(xs), "output_xor_sum_T": list(xt)}
            if len(set(outS)) != len(set(outT)):
                separated["support_size_of_output_word"] += 1
            rS = gf2_span_dim([enc(outS[0]) ^ enc(outS[1])])
            rT = gf2_span_dim([enc(outT[0]) ^ enc(outT[1])])
            if rS != rT:
                separated["F_affine_rank_of_output_word"] += 1
            if sorted(w[0] for w in outS) != sorted(w[0] for w in outT):
                separated["multiset_of_output_byte_row0"] += 1
    return {
        "phase": "od3",
        "seed": seed,
        "trials": trials,
        "trials_with_identical_per_word_marginals": marginals_equal_count,
        "comparisons_per_trial": 4,
        "separations_by_object": separated,
        "witness_example": example,
        "reading": ("An object SEPARATED by the coupling witness cannot be a function of "
                    "the four per-word marginals, so it cannot satisfy the set-valued "
                    "analogue of (H2) at a single interface. An object NEVER separated by "
                    "it is not thereby shown to propagate; it merely survives this one "
                    "obstruction."),
        "wall_clock_seconds": round(time.time() - t0, 3),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True,
                    choices=["sweep", "gf2", "closure", "od3", "all"])
    ap.add_argument("--closure-max-seconds", type=float, default=420.0)
    args = ap.parse_args()
    res: dict = {}
    if args.phase in ("sweep", "all"):
        res["sweep"] = phase_sweep(M_TARGET, "target")
    if args.phase in ("gf2", "all"):
        res["gf2_uniform"] = phase_gf2(M_TARGET, condition_on_step1_pair=False)
        res["gf2_conditioned"] = phase_gf2(M_TARGET, condition_on_step1_pair=True)
    if args.phase in ("closure", "all"):
        res["closure"] = phase_closure(args.closure_max_seconds)
    if args.phase in ("od3", "all"):
        res["od3"] = phase_od3()
    json.dump(res, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
