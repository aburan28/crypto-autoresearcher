#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oracle.py --- EXACT joint-moment oracle and i.i.d.-by-construction null generator.

Task:   TASK-20260803-6f50df  (executor, successor to TASK-20260802-ecba30)
Batch:  BATCH-003     Goal: GOAL-HQC-001     Question: RQ-HQC-001

================================================================================
WHAT THIS IS, AND WHAT IT IS NOT
================================================================================

This module computes, EXACTLY and by enumeration, the joint moment

        mu_m  =  E[ product of m DISTINCT block-failure indicators ]

for TOY, ENUMERABLE configurations.  Its purpose is to be a CORRECTNESS
INSTRUMENT: a later Monte-Carlo estimator of mu_m can be checked against a
ground truth that is not itself an estimate.

IT IS NOT A RESULT ABOUT HQC.  Every configuration below is a toy object of a
few dozen coordinates.  HQC-1 has n = 17669 coordinates, n_e = 46 blocks of
n_2 = 384 bits, and m = delta_e + 1 = 16.  Nothing computed here is a
statement about HQC at any parameter set, about the truth or falsity of
assumption A17, or about HQC's security in either direction.  Where a
configuration below borrows HQC's DIMENSIONS it uses a DIFFERENT ensemble and
a DIFFERENT block decoder, and it is flagged `not_an_hqc_quantity: true`.

================================================================================
THE OBJECT, AND THE INDEXING CONVENTION (stated so it can be attacked)
================================================================================

Following TASK-20260802-15971b section 1 (the formal statement of A17):

  * `etilde` is a vector in F_2^N with N = n_e * n_2, partitioned into n_e
    DISJOINT CONSECUTIVE blocks  B_j = {j*n_2, ..., (j+1)*n_2 - 1},
    j = 0, ..., n_e - 1.   `etilde^(j)` is the restriction to B_j.
  * `F_j = 1{ D_i(etilde^(j)) != 0 }` is the indicator that inner block j
    decodes to a nonzero codeword, i.e. to the wrong F_256 symbol.
    F_j is a function of etilde^(j) alone (plus tie-breaking randomness).
  * `S = sum_j F_j`.

CONVENTION C1 (distinct indices).  For J subset of {0,...,n_e-1} with |J| = k,

        mu_k(J) := E[ prod_{j in J} F_j ] = P[ F_j = 1 for all j in J ].

  The indices in J are DISTINCT.  Repetition is FORBIDDEN.  Because
  F_j^2 = F_j, a "moment" taken over a multiset with repeats collapses onto a
  LOWER-order moment and is therefore an OVER-ESTIMATE of mu_k.  This is
  exactly the bug that reads as positive dependence, and mutant M1 below
  reproduces it deliberately.

CONVENTION C2 (canonical scalar = subset average = normalised binomial moment).

        mu_k := (1 / C(n_e, k)) * sum_{|J| = k} mu_k(J)  =  E[C(S,k)] / C(n_e,k).

  Justification, and defence against the A17 definition:
    (a) A17's primary form (TASK-20260802-15971b section 2.2) asserts
        P[AND_{j in J} F_j = 1] = p_i^{|J|} FOR EVERY subset J, and reading R3
        (section 3.3) asserts mu_k <= q^k "for all index sets of size k".  So
        the PER-SUBSET quantity is primary.  This module therefore computes and
        reports the FULL per-subset table mu_k(J) whenever it is enumerable,
        and the average is a summary, never a replacement.
    (b) The average is exactly the normalised k-th BINOMIAL MOMENT of S, i.e.
        E[C(S,k)]/C(n_e,k).  That is the quantity in the leading Bonferroni
        term of P[S >= m]:   P[S >= m] <= E[C(S,m)] = C(n_e,m) * mu_m, with
        equality to leading order.  It is also what an unbiased Monte-Carlo
        estimator of the form mean_t C(S_t, m)/C(n_e, m) estimates.
    (c) Under exchangeability of (F_0,...,F_{n_e-1}) -- which A17 asserts and
        which TASK-20260802-15971b Lemma L1 establishes only for k = 1 -- the
        per-subset values coincide and (C2) equals (C1) for every J.  This
        module TESTS subset-exchangeability rather than assuming it, and
        reports min/max/spread over subsets.

CONVENTION C3 (no conditioning).  mu_k is UNCONDITIONAL: no conditioning on
  the global weight of etilde, on S, or on anything else.

CONVENTION C4 (tie-breaking).  If the inner decoder ties, F_j is Bernoulli
  with a RATIONAL parameter phi in [0,1] conditional on the block content, and
  the tie-breaking randomness is independent across blocks (rider R-tie of
  TASK-20260802-15971b section 3.6).  A deterministic "ties count as failure"
  convention is also provided.  Both are exact rational computations.

================================================================================
ARITHMETIC REGIME
================================================================================

EVERY moment, probability, tail and variance below is computed in EXACT
INTEGER or fractions.Fraction arithmetic.  There is no floating point anywhere
in the computation path.  Floating point appears in exactly two places, both
REPORTING-ONLY:
  (i)  `safe_float()` -- a float rendering of an exact Fraction, for reading
       convenience; it is None when the value underflows.
  (ii) `log2_fraction()` -- a base-2 logarithm of an exact Fraction, computed
       from the top 64 bits of numerator and denominator.  Absolute error
       bound: < 1e-9 for |log2| < 1e4 (derivation in oracle_report.md).
No decision, test, or comparison in this module uses either.

================================================================================
DESIGN FOR TRACTABILITY (this is why the enumeration is cheap)
================================================================================

  Layer 1  AtomLaw:   an exact law on F_2^N given by NON-NEGATIVE INTEGER
                      weights w(v) and a denominator D = sum_v w(v).
                      Every ensemble -- i.i.d. Bernoulli(a/b), uniform
                      fixed weight, mixtures, and the HQC-shaped ring product
                      -- is representable this way with integers only.
  Layer 2  BlockModel: content -> integer `fail_num` in [0, scale];
                      phi = fail_num / scale.
  Layer 3  FailureLaw: the atom law pushed forward onto the per-block
                      failure-value SIGNATURE.  Because a block's failure
                      value depends only on that block's content, and a block
                      model takes at most V distinct values, the 2^N atoms
                      collapse onto at most V^{n_e} signatures.  ALL mu_k(J),
                      the law of S, and all tails then come from that small
                      table in O(V^{n_e}) each.
  Route B  For ensembles that are COORDINATE-EXCHANGEABLE WITHIN BLOCKS and
           uniform-fixed-weight globally, mu_k has a closed integer form:
                mu_k = [ sum_t G_k(t) * C((n_e-k)*n_2, w-t) ]
                       / ( C(N, w) * scale^k ),
           where G_k is the k-fold convolution of the integer sequence
           A_j = sum over weight-j block patterns of fail_num.  Pure integer
           arithmetic, cost O(k * w * n_2), INDEPENDENT of 2^N.  This is what
           lets the oracle reach large dimensions for that ensemble class, and
           it is cross-checked against Route A wherever both run.

Run:   python3 oracle.py --out oracle_values.json --seed 20260803
Tests: python3 test_oracle.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from fractions import Fraction
from itertools import combinations

# --------------------------------------------------------------------------
# Hard safety caps.  Exceeding them raises rather than silently thrashing.
# --------------------------------------------------------------------------
ENUM_MAX_N = 22          # max N for full 2^N atom enumeration (Route A)
ENUM_MAX_BLOCK = 18      # max n_2 for full 2^{n_2} block-pattern enumeration

SCHEMA = "hqc-joint-moment-oracle/1"
TASK_ID = "TASK-20260803-6f50df"


# ==========================================================================
# 0.  EXACT ARITHMETIC HELPERS
# ==========================================================================

def comb(n: int, k: int) -> int:
    """Exact binomial coefficient; 0 outside range."""
    if k < 0 or n < 0 or k > n:
        return 0
    return math.comb(n, k)


def popcount(x: int) -> int:
    return x.bit_count() if hasattr(x, "bit_count") else bin(x).count("1")


def _log2_int(x: int) -> float:
    """log2 of a positive integer using its top 64 bits.  Reporting only."""
    if x <= 0:
        raise ValueError("log2 of non-positive integer")
    b = x.bit_length()
    if b <= 64:
        return math.log2(x)
    top = x >> (b - 64)
    return (b - 64) + math.log2(top)


def log2_fraction(fr: Fraction):
    """Base-2 log of an exact Fraction.  REPORTING ONLY.  |err| < 1e-9 for
    |log2| < 1e4 (see oracle_report.md)."""
    if fr == 0:
        return None
    if fr < 0:
        raise ValueError("log2 of negative")
    return _log2_int(fr.numerator) - _log2_int(fr.denominator)


def safe_float(fr: Fraction):
    """Float rendering of an exact Fraction.  REPORTING ONLY.  None on
    overflow/underflow."""
    try:
        v = float(fr)
    except (OverflowError, ValueError):
        return None
    if v == 0.0 and fr != 0:
        return None
    if math.isinf(v):
        return None
    return v


def frac_record(fr: Fraction, exact_char_cap: int = 4000) -> dict:
    """JSON record of an exact Fraction: the exact value when short enough,
    otherwise a pinned digest plus the exact-value length."""
    assert isinstance(fr, Fraction)
    s = "%d/%d" % (fr.numerator, fr.denominator)
    rec = {"float": safe_float(fr), "log2": log2_fraction(fr) if fr > 0 else None}
    if len(s) <= exact_char_cap:
        rec["exact"] = s
    else:
        rec["exact_omitted"] = True
        rec["exact_len_chars"] = len(s)
        rec["exact_sha256"] = hashlib.sha256(s.encode()).hexdigest()
        rec["num_digits"] = len(str(fr.numerator))
        rec["den_digits"] = len(str(fr.denominator))
    return rec


# ==========================================================================
# 1.  BLOCK FAILURE MODELS
#     phi(content) = fail_num(content) / scale,  exact rational in [0,1].
# ==========================================================================

class BlockModel:
    """Abstract per-block failure model on F_2^{n2}."""

    name: str
    n2: int
    scale: int

    def table(self) -> list:
        """List of length 2^{n2}: fail_num for each block content."""
        raise NotImplementedError

    def weight_mass(self) -> list:
        """A[j] = sum over block patterns of Hamming weight j of fail_num.
        Integer sequence of length n2+1.  Used by Route B."""
        A = [0] * (self.n2 + 1)
        for v, f in enumerate(self.table()):
            if f:
                A[popcount(v)] += f
        return A

    def describe(self) -> dict:
        return {"name": self.name, "n2": self.n2, "scale": self.scale}


class ThresholdBlockModel(BlockModel):
    """Bounded-distance abstraction: the block fails iff its Hamming weight
    exceeds t.  Deterministic (scale = 1).  A[j] is combinatorial, so Route B
    needs no 2^{n2} enumeration at all."""

    def __init__(self, n2: int, t: int):
        self.n2 = n2
        self.t = t
        self.scale = 1
        self.name = "threshold(n2=%d,t=%d)" % (n2, t)

    def table(self) -> list:
        if self.n2 > ENUM_MAX_BLOCK:
            raise ValueError("block enumeration too large: n2=%d" % self.n2)
        return [1 if popcount(v) > self.t else 0 for v in range(1 << self.n2)]

    def weight_mass(self) -> list:
        return [comb(self.n2, j) if j > self.t else 0 for j in range(self.n2 + 1)]

    def describe(self) -> dict:
        d = super().describe()
        d["t"] = self.t
        d["closed_form_weight_mass"] = True
        return d


class RM1BlockModel(BlockModel):
    """First-order Reed-Muller RM(1,mm) = [2^mm, mm+1, 2^{mm-1}] with a
    MAXIMUM-LIKELIHOOD (minimum-Hamming-distance) decoder, implemented by
    direct search over all 2^{mm+1} codewords.

    This mirrors the SHAPE of HQC's inner code (SPEC uses a DUPLICATED RM(1,7)
    decoded by a Hadamard transform).  It is a toy analogue, not HQC's code,
    and this module does NOT implement duplication.

    Because the all-zero codeword is transmitted (WLOG by linearity, per
    TASK-20260802-15971b section 1), the received word IS the error pattern.
    tie policy:
      'split' -- ties broken uniformly at random among the argmax set
                 (assumption A13's model): phi = 1 - [0 in M]/|M|.
      'fail'  -- any tie counts as a failure: phi = 0 iff M == {0}.
    """

    def __init__(self, mm: int, tie: str = "split"):
        assert tie in ("split", "fail")
        self.mm = mm
        self.n2 = 1 << mm
        self.tie = tie
        self.name = "rm1(mm=%d,n2=%d,tie=%s)" % (mm, self.n2, tie)
        self._table = None
        self.scale = 1
        self._build()

    def _codewords(self) -> list:
        """All 2^{mm+1} codewords of RM(1,mm) as bitmasks of length 2^mm."""
        n2 = self.n2
        out = []
        for a in range(1 << self.mm):
            base = 0
            for u in range(n2):
                if popcount(a & u) & 1:
                    base |= 1 << u
            out.append(base)
            out.append(base ^ ((1 << n2) - 1))
        return out

    def _build(self):
        if self.n2 > ENUM_MAX_BLOCK:
            raise ValueError("block enumeration too large: n2=%d" % self.n2)
        cws = self._codewords()
        assert cws[0] == 0, "codeword 0 must be first"
        nums = []
        mults = []
        for v in range(1 << self.n2):
            best = None
            mult = 0
            zero_in = False
            for idx, c in enumerate(cws):
                d = popcount(v ^ c)
                if best is None or d < best:
                    best = d
                    mult = 1
                    zero_in = (idx == 0)
                elif d == best:
                    mult += 1
                    if idx == 0:
                        zero_in = True
            nums.append((zero_in, mult))
            mults.append(mult)
        if self.tie == "split":
            scale = 1
            for mlt in set(mults):
                scale = scale * mlt // math.gcd(scale, mlt)
            self.scale = scale
            self._table = [
                (scale - scale // mlt) if zin else scale for (zin, mlt) in nums
            ]
        else:
            self.scale = 1
            self._table = [0 if (zin and mlt == 1) else 1 for (zin, mlt) in nums]

    def table(self) -> list:
        return self._table

    def describe(self) -> dict:
        d = super().describe()
        d.update({"mm": self.mm, "tie": self.tie,
                  "code": "[%d,%d,%d] RM(1,%d)" % (self.n2, self.mm + 1,
                                                   self.n2 // 2, self.mm),
                  "decoder": "exhaustive minimum-distance (ML)"})
        return d


class TruthTableBlockModel(BlockModel):
    """Hand-specified block model, used for known-answer tests."""

    def __init__(self, n2: int, nums: list, scale: int, name: str):
        assert len(nums) == (1 << n2)
        assert all(0 <= x <= scale for x in nums)
        self.n2 = n2
        self.scale = scale
        self._nums = list(nums)
        self.name = name

    def table(self) -> list:
        return self._nums


# ==========================================================================
# 2.  ATOM LAWS  --- exact integer-weighted laws on F_2^N
# ==========================================================================

class AtomLaw:
    """Exact probability law on F_2^N: P[v] = weights[v] / D, D = sum weights."""

    def __init__(self, N: int, weights: list, D: int, name: str, meta=None):
        assert len(weights) == (1 << N)
        assert D == sum(weights), "denominator must equal the weight sum"
        assert D > 0
        self.N = N
        self.weights = weights
        self.D = D
        self.name = name
        self.meta = meta or {}

    def describe(self) -> dict:
        d = {"name": self.name, "N": self.N, "atoms": 1 << self.N,
             "support": sum(1 for w in self.weights if w), "denominator_bits":
             self.D.bit_length()}
        d.update(self.meta)
        return d


def _check_N(N: int):
    if N > ENUM_MAX_N:
        raise ValueError("full enumeration refused: N=%d > ENUM_MAX_N=%d"
                         % (N, ENUM_MAX_N))


def atomlaw_iid_bernoulli(N: int, p: Fraction) -> AtomLaw:
    """Coordinates i.i.d. Bernoulli(p), p = a/b.  INDEPENDENT BY CONSTRUCTION
    at the coordinate level, hence independent across any disjoint blocks.
    Integer weights: w(v) = a^{wt(v)} * (b-a)^{N-wt(v)},  D = b^N."""
    _check_N(N)
    a, b = p.numerator, p.denominator
    assert 0 <= a <= b
    pw = [(a ** j) * ((b - a) ** (N - j)) for j in range(N + 1)]
    weights = [pw[popcount(v)] for v in range(1 << N)]
    return AtomLaw(N, weights, b ** N,
                   "iid_bernoulli(N=%d,p=%s)" % (N, p),
                   {"family": "iid_bernoulli", "p": str(p),
                    "independent_by_construction": True})


def atomlaw_fixed_weight(N: int, w: int) -> AtomLaw:
    """Uniform over all weight-w vectors of F_2^N (sampling without
    replacement)."""
    _check_N(N)
    weights = [1 if popcount(v) == w else 0 for v in range(1 << N)]
    return AtomLaw(N, weights, comb(N, w),
                   "fixed_weight(N=%d,w=%d)" % (N, w),
                   {"family": "fixed_weight", "w": w})


def atomlaw_mixture(laws: list, lambdas: list, name: str) -> AtomLaw:
    """Exact finite mixture, kept in integers.  lambdas are Fractions summing
    to 1.  A mixture of ensembles with different marginals induces POSITIVE
    dependence (Jensen), which is the mechanism EV-HQC-6fd5b1 O-6 names as
    'latent-mixture common-mode'."""
    assert len(laws) == len(lambdas) and laws
    assert sum(lambdas) == 1
    N = laws[0].N
    assert all(L.N == N for L in laws)
    A = 1
    for lam in lambdas:
        A = A * lam.denominator // math.gcd(A, lam.denominator)
    C = 1
    for L in laws:
        C = C * L.D // math.gcd(C, L.D)
    coefs = [(lam.numerator * (A // lam.denominator)) * (C // L.D)
             for lam, L in zip(lambdas, laws)]
    weights = [0] * (1 << N)
    for coef, L in zip(coefs, laws):
        lw = L.weights
        for v in range(1 << N):
            if lw[v]:
                weights[v] += coef * lw[v]
    D = A * C
    assert sum(weights) == D
    return AtomLaw(N, weights, D, name,
                   {"family": "mixture",
                    "components": [L.name for L in laws],
                    "lambdas": [str(x) for x in lambdas]})


# --------------------------------------------------------------------------
# 2b.  HQC-SHAPED RING ENSEMBLE  (the only structurally faithful toy)
# --------------------------------------------------------------------------

def _rot(a: int, i: int, n: int) -> int:
    mask = (1 << n) - 1
    i %= n
    return ((a << i) | (a >> (n - i))) & mask if i else a & mask


def ring_mul(a: int, b: int, n: int) -> int:
    """Product in F_2[X]/(X^n - 1); bit i of a mask is the coefficient of X^i."""
    r = 0
    bb = b
    i = 0
    while bb:
        if bb & 1:
            r ^= _rot(a, i, n)
        bb >>= 1
        i += 1
    return r


def _fixed_weight_masks(n: int, w: int):
    for pos in combinations(range(n), w):
        v = 0
        for p in pos:
            v |= 1 << p
        yield v


def _wht(a: list) -> None:
    """In-place integer Walsh-Hadamard transform (exact; no floating point)."""
    n = len(a)
    h = 1
    while h < n:
        for i in range(0, n, h << 1):
            for j in range(i, i + h):
                x = a[j]
                y = a[j + h]
                a[j] = x + y
                a[j + h] = x - y
        h <<= 1


def xor_convolve(arrays: list) -> list:
    """Exact XOR-convolution of integer count vectors, all of length 2^N."""
    L = len(arrays[0])
    n = L.bit_length() - 1
    assert all(len(x) == L for x in arrays)
    trs = []
    for arr in arrays:
        t = list(arr)
        _wht(t)
        trs.append(t)
    out = trs[0]
    for t in trs[1:]:
        out = [x * y for x, y in zip(out, t)]
    _wht(out)
    res = []
    for x in out:
        q, r = divmod(x, L)
        assert r == 0, "inverse WHT must be exact"
        assert q >= 0, "counts must be non-negative"
        res.append(q)
    return res


def atomlaw_ring_hqc_shaped(n: int, omega: int, omega_r: int, omega_e: int,
                            N: int) -> AtomLaw:
    """Exact law of  etilde = truncate_N( x*r2 + r1*y + e )  in F_2[X]/(X^n-1),
    with x, y uniform of weight omega, r1, r2 uniform of weight omega_r, and e
    uniform of weight omega_e, all independent (SPEC A1-A4, true by
    construction of the fixed-weight sampler).

    KEY EFFICIENCY FACT (why this is cheap): coordinate restriction
    F_2^n -> F_2^N is a group homomorphism, so the pushforward of an
    XOR-convolution is the XOR-convolution of the pushforwards.  We may
    therefore truncate FIRST and convolve in F_2^N, never materialising 2^n.

    All arithmetic is integer.  This is space (T) of TASK-20260802-15971b
    section 2.1 -- the TRUE space, not the model space (M).
    """
    _check_N(N)
    assert N <= n
    mask = (1 << N) - 1
    size = 1 << N

    c_prod = [0] * size
    for x in _fixed_weight_masks(n, omega):
        for r in _fixed_weight_masks(n, omega_r):
            c_prod[ring_mul(x, r, n) & mask] += 1
    n_prod = comb(n, omega) * comb(n, omega_r)
    assert sum(c_prod) == n_prod

    c_e = [0] * size
    for ev in _fixed_weight_masks(n, omega_e):
        c_e[ev & mask] += 1
    assert sum(c_e) == comb(n, omega_e)

    weights = xor_convolve([c_prod, list(c_prod), c_e])
    D = n_prod * n_prod * comb(n, omega_e)
    assert sum(weights) == D
    return AtomLaw(N, weights, D,
                   "ring(n=%d,w=%d,wr=%d,we=%d,N=%d)"
                   % (n, omega, omega_r, omega_e, N),
                   {"family": "hqc_shaped_ring",
                    "n": n, "omega": omega, "omega_r": omega_r,
                    "omega_e": omega_e, "truncated_coords": n - N,
                    "space": "T (true fixed-weight space)"})


def ring_sampler(n: int, omega: int, omega_r: int, omega_e: int, N: int,
                 n_e: int, model: BlockModel, seed: int):
    """A DIRECT SAMPLER for the same toy ring ensemble that
    atomlaw_ring_hqc_shaped computes exactly.  Draws x, y, r1, r2, e as
    uniform fixed-weight vectors, forms etilde, decodes each block, and
    returns the failure mask.

    This exists for ONE purpose: to check that the oracle's exact mu_m is the
    SAME OBJECT that a sampling estimator targets.  It samples a TOY ring of n
    coordinates; it is NOT the HQC decoding measurement (runs_authorized = 0
    for that), and it uses this module's toy block model, not HQC's decoder.
    """
    rng = random.Random(seed)
    tab = model.table()
    scale = model.scale
    n2 = model.n2
    bmask = (1 << n2) - 1
    mask = (1 << N) - 1

    def fw(w):
        v = 0
        for p in rng.sample(range(n), w):
            v |= 1 << p
        return v

    while True:
        x, y = fw(omega), fw(omega)
        r1, r2 = fw(omega_r), fw(omega_r)
        e = fw(omega_e)
        ep = ring_mul(x, r2, n) ^ ring_mul(r1, y, n) ^ e
        et = ep & mask
        msk = 0
        for j in range(n_e):
            fn = tab[(et >> (j * n2)) & bmask]
            if fn == scale:
                fail = True
            elif fn == 0:
                fail = False
            else:
                fail = rng.randrange(scale) < fn
            if fail:
                msk |= 1 << j
        yield msk


def atomlaw_product_blocks(block_laws: list) -> AtomLaw:
    """Blocks independent by construction, each with its own exact law on
    F_2^{n2}.  Used to build i.i.d./independent nulls at the COORDINATE level
    so that the generic mu machinery -- not a shortcut -- computes them."""
    n_e = len(block_laws)
    n2 = block_laws[0].N
    assert all(L.N == n2 for L in block_laws)
    N = n_e * n2
    _check_N(N)
    weights = list(block_laws[0].weights)
    D = block_laws[0].D
    for L in block_laws[1:]:
        weights = [wl * wh for wh in L.weights for wl in weights]
        D *= L.D
    assert len(weights) == (1 << N)
    assert sum(weights) == D
    return AtomLaw(N, weights, D,
                   "product_blocks(n_e=%d,n2=%d)" % (n_e, n2),
                   {"family": "product_blocks",
                    "components": [L.name for L in block_laws],
                    "independent_by_construction": True})


# ==========================================================================
# 3.  FAILURE LAW --- the pushforward onto per-block failure values
# ==========================================================================

class FailureLaw:
    """Exact law of the failure profile (phi_0, ..., phi_{n_e-1}), where each
    phi_j = vals[digit_j] / scale.

    Stored as: sig_weights[s] = integer weight, with s the base-V encoding
    s = sum_j digit_j * V^j.  Denominator D.  Everything downstream (all
    mu_k(J), the law of S, tails, and the exact variance of the canonical
    estimator) is derived from this table in exact arithmetic.
    """

    def __init__(self, n_e: int, vals: list, scale: int,
                 sig_weights: dict, D: int, name: str, meta=None):
        self.n_e = n_e
        self.vals = list(vals)
        self.V = len(vals)
        self.scale = scale
        self.sig_weights = dict(sig_weights)
        self.D = D
        self.name = name
        self.meta = meta or {}
        assert sum(sig_weights.values()) == D, "failure-law mass must be exact"
        assert all(0 <= v <= scale for v in vals)

    # ---- core: joint moment over a set of DISTINCT indices ----------------
    def mu(self, J) -> Fraction:
        """mu_k(J) = E[prod_{j in J} F_j].  J must have DISTINCT indices."""
        J = tuple(J)
        assert len(set(J)) == len(J), "CONVENTION C1: indices must be distinct"
        assert all(0 <= j < self.n_e for j in J)
        k = len(J)
        if k == 0:
            return Fraction(1)
        V = self.V
        vals = self.vals
        pows = [V ** j for j in J]
        num = 0
        for s, w in self.sig_weights.items():
            pr = 1
            for pv in pows:
                d = vals[(s // pv) % V]
                if d == 0:
                    pr = 0
                    break
                pr *= d
            if pr:
                num += w * pr
        return Fraction(num, self.D * (self.scale ** k))

    def mu_all_subsets(self, k: int) -> dict:
        """{frozenset(J): mu_k(J)} over ALL C(n_e,k) subsets."""
        return {J: self.mu(J) for J in combinations(range(self.n_e), k)}

    def mu_bar(self, k: int) -> Fraction:
        """CONVENTION C2: subset-averaged mu_k = E[C(S,k)]/C(n_e,k)."""
        if k == 0:
            return Fraction(1)
        tot = Fraction(0)
        cnt = 0
        for J in combinations(range(self.n_e), k):
            tot += self.mu(J)
            cnt += 1
        return tot / cnt

    def binomial_moment(self, k: int) -> Fraction:
        """E[C(S,k)] = sum over all size-k subsets of mu_k(J)."""
        return sum((self.mu(J) for J in combinations(range(self.n_e), k)),
                   Fraction(0))

    def q(self, j: int) -> Fraction:
        return self.mu((j,))

    # ---- law of S --------------------------------------------------------
    def mask_law(self) -> dict:
        """Exact law of the binary failure vector, as {mask: Fraction}."""
        n_e = self.n_e
        V, vals, scale = self.V, self.vals, self.scale
        den = self.D * (scale ** n_e)
        acc = {}
        for s, w in self.sig_weights.items():
            digs = []
            t = s
            for _ in range(n_e):
                digs.append(vals[t % V])
                t //= V
            # distribute over all 2^{n_e} masks
            cur = {0: w}
            for j, dv in enumerate(digs):
                nxt = {}
                bit = 1 << j
                for msk, ww in cur.items():
                    if dv:
                        nxt[msk | bit] = nxt.get(msk | bit, 0) + ww * dv
                    if scale - dv:
                        nxt[msk] = nxt.get(msk, 0) + ww * (scale - dv)
                cur = nxt
            for msk, ww in cur.items():
                acc[msk] = acc.get(msk, 0) + ww
        assert sum(acc.values()) == den
        return {msk: Fraction(ww, den) for msk, ww in acc.items()}

    def law_of_S(self) -> list:
        out = [Fraction(0)] * (self.n_e + 1)
        for msk, pr in self.mask_law().items():
            out[popcount(msk)] += pr
        assert sum(out) == 1
        return out

    def tail(self, m: int) -> Fraction:
        return sum(self.law_of_S()[m:], Fraction(0))

    def describe(self) -> dict:
        d = {"name": self.name, "n_e": self.n_e, "scale": self.scale,
             "distinct_block_failure_values": [str(Fraction(v, self.scale))
                                               for v in self.vals],
             "signatures": len(self.sig_weights)}
        d.update(self.meta)
        return d


def build_failure_law(law: AtomLaw, model: BlockModel, n_e: int,
                      name: str = None) -> FailureLaw:
    """ROUTE A: push an exact atom law on F_2^N forward onto the failure
    profile by FULL ENUMERATION of all 2^N atoms.  This is the ground truth."""
    n2 = model.n2
    N = n_e * n2
    assert law.N == N, "block structure must match the atom law (%d != %d)" % (law.N, N)
    tab = model.table()
    vals = sorted(set(tab))
    idx = {v: i for i, v in enumerate(vals)}
    V = len(vals)
    dig = [idx[t] for t in tab]

    # digit-wise construction of the signature array (block 0 = least
    # significant digit, matching v = c_0 + c_1*2^{n2} + ...)
    sig = list(dig)
    mult = V
    for _ in range(1, n_e):
        sig = [s + d * mult for d in dig for s in sig]
        mult *= V
    assert len(sig) == (1 << N)

    acc = {}
    for s, w in zip(sig, law.weights):
        if w:
            acc[s] = acc.get(s, 0) + w
    return FailureLaw(n_e, vals, model.scale, acc, law.D,
                      name or ("%s|%s" % (law.name, model.name)),
                      {"route": "A_full_enumeration", "atoms_enumerated": 1 << N,
                       "atom_law": law.describe(), "block_model": model.describe()})


# --------------------------------------------------------------------------
# 3b.  Failure-level ensembles (defined directly on {0,1}^{n_e})
# --------------------------------------------------------------------------

def failurelaw_from_masks(n_e: int, mask_weights: dict, D: int,
                          name: str, meta=None) -> FailureLaw:
    """V = 2, vals = [0,1], so the signature IS the failure mask."""
    return FailureLaw(n_e, [0, 1], 1, mask_weights, D, name, meta)


def fl_iid_indicator(n_e: int, p: Fraction) -> FailureLaw:
    """Indicators independent by construction with common marginal p."""
    a, b = p.numerator, p.denominator
    mw = {}
    for msk in range(1 << n_e):
        c = popcount(msk)
        mw[msk] = (a ** c) * ((b - a) ** (n_e - c))
    return failurelaw_from_masks(n_e, mw, b ** n_e,
                                 "iid_indicator(n_e=%d,p=%s)" % (n_e, p),
                                 {"family": "iid_indicator", "p": str(p),
                                  "independent_by_construction": True})


def fl_exactly_c(n_e: int, c: int) -> FailureLaw:
    """S == c always, with the failing set uniform.  Extreme NEGATIVE
    dependence.  Analytic: mu_k = C(n_e-k, c-k)/C(n_e,c)."""
    mw = {msk: 1 for msk in range(1 << n_e) if popcount(msk) == c}
    return failurelaw_from_masks(n_e, mw, comb(n_e, c),
                                 "exactly_c(n_e=%d,c=%d)" % (n_e, c),
                                 {"family": "exactly_c", "c": c})


def fl_comonotone(n_e: int, p: Fraction) -> FailureLaw:
    """All blocks fail together with probability p.  Extreme POSITIVE
    dependence.  Analytic: mu_k = p for every k >= 1."""
    a, b = p.numerator, p.denominator
    mw = {(1 << n_e) - 1: a, 0: b - a}
    return failurelaw_from_masks(n_e, mw, b,
                                 "comonotone(n_e=%d,p=%s)" % (n_e, p),
                                 {"family": "comonotone", "p": str(p)})


# ==========================================================================
# 4.  ROUTE B --- exact integer convolution for the fixed-weight ensemble
# ==========================================================================

def route_b_mu(n_e: int, n2: int, w: int, A: list, scale: int,
               k: int) -> Fraction:
    """EXACT mu_k for: etilde uniform over weight-w vectors of F_2^{n_e*n2},
    with per-block failure mass A[j] (integer, = scale * sum over weight-j
    block patterns of phi).

    PRECONDITION (stated because it is the only place the oracle uses a
    structural fact rather than raw enumeration): conditional on the block
    weight profile, block contents are uniform over patterns of those weights
    and independent across blocks.  This holds EXACTLY for the uniform
    fixed-weight ensemble and for i.i.d. Bernoulli coordinates.  It does NOT
    hold for the ring ensemble, and Route B is never applied there.

    mu_k = [ sum_t G_k(t) * C((n_e-k)*n2, w-t) ] / ( C(N,w) * scale^k )
    with G_k the k-fold convolution of A truncated at w.  Pure integers.
    """
    N = n_e * n2
    assert 0 <= k <= n_e
    if k == 0:
        return Fraction(1)
    G = [1]
    for _ in range(k):
        new = [0] * (min(len(G) - 1 + len(A) - 1, w) + 1)
        for i, gi in enumerate(G):
            if not gi:
                continue
            lim = min(len(A) - 1, w - i)
            for j in range(lim + 1):
                if A[j]:
                    new[i + j] += gi * A[j]
        G = new
    rest = (n_e - k) * n2
    num = 0
    for t, gt in enumerate(G):
        if gt:
            c = comb(rest, w - t)
            if c:
                num += gt * c
    return Fraction(num, comb(N, w) * (scale ** k))


def route_b_marginal(n_e: int, n2: int, w: int, A: list,
                     scale: int) -> Fraction:
    return route_b_mu(n_e, n2, w, A, scale, 1)


# ==========================================================================
# 5.  INDEPENDENT ANALYTIC REFERENCES
#     Each is a closed form derived on paper and implemented WITHOUT touching
#     AtomLaw/FailureLaw/Route B.  They are what catches an oracle bug.
# ==========================================================================

def ref_iid(p: Fraction, k: int) -> Fraction:
    """Independence: mu_k = p^k exactly."""
    return p ** k


def ref_occupancy(n_e: int, n2: int, w: int, k: int) -> Fraction:
    """Uniform weight-w over N = n_e*n2 coordinates, block fails iff NON-EMPTY
    (threshold t=0).  Inclusion-exclusion over which of the k blocks are empty:
    mu_k = sum_i (-1)^i C(k,i) C(N - i*n2, w) / C(N, w)."""
    N = n_e * n2
    num = 0
    for i in range(k + 1):
        num += (-1) ** i * comb(k, i) * comb(N - i * n2, w)
    return Fraction(num, comb(N, w))


def ref_exactly_c(n_e: int, c: int, k: int) -> Fraction:
    return Fraction(comb(n_e - k, c - k), comb(n_e, c))


def ref_comonotone(p: Fraction, k: int) -> Fraction:
    return p if k >= 1 else Fraction(1)


def ref_mixture(mus_by_component: list, lambdas: list) -> Fraction:
    """Mixture moments are the mixture of component moments (linearity)."""
    return sum((lam * mu for lam, mu in zip(lambdas, mus_by_component)),
               Fraction(0))


def ref_block_failure_prob_bernoulli(A: list, scale: int, n2: int,
                                     p: Fraction) -> Fraction:
    """Marginal block failure probability under i.i.d. Bernoulli(p)
    coordinates:  q = sum_j A[j] p^j (1-p)^{n2-j} / scale."""
    tot = Fraction(0)
    for j, aj in enumerate(A):
        if aj:
            tot += Fraction(aj, scale) * (p ** j) * ((1 - p) ** (n2 - j))
    return tot


# ==========================================================================
# 6.  MUTANT COMPUTATIONS --- the failure mode that LOOKS LIKE SIGNAL
#     Each mutant is a plausible, wrong way to form the m-th joint moment.
#     Exact expectations are computed from the exact law of S, so the mutant
#     analysis is itself exact rather than sampled.
# ==========================================================================

def _falling(x: int, m: int) -> int:
    r = 1
    for i in range(m):
        r *= (x - i)
    return r


def mutant_expectations(fl: FailureLaw, m: int) -> dict:
    """Exact expectations of four wrong estimators, from the exact law of S."""
    n_e = fl.n_e
    pS = fl.law_of_S()
    truth = fl.mu_bar(m)

    m1 = sum((pS[s] * Fraction(s ** m, n_e ** m) for s in range(n_e + 1)),
             Fraction(0))
    m2 = sum((pS[s] * Fraction(_falling(s, m), n_e ** m)
              for s in range(n_e + 1)), Fraction(0))
    m3 = sum((pS[s] * Fraction(comb(s, m), n_e ** m)
              for s in range(n_e + 1)), Fraction(0))
    m4 = fl.mu(tuple(range(m))) if m <= n_e else None
    return {
        "truth_mu_bar_m": truth,
        "M1_indices_with_replacement": m1,
        "M2_ordered_distinct_wrong_denominator": m2,
        "M3_binomial_count_wrong_denominator": m3,
        "M4_single_fixed_subset_0..m-1": m4,
    }


MUTANT_DESCRIPTIONS = {
    "M1_indices_with_replacement": (
        "Draws m block indices WITH REPLACEMENT and averages the product of "
        "the indicators: E[(S/n_e)^m].  Because F_j^2 = F_j, every repeated "
        "index collapses onto a lower-order moment, so M1 >= truth ALWAYS and "
        "the excess is read as positive dependence.  THIS IS THE BUG THAT "
        "LOOKS LIKE SIGNAL."),
    "M2_ordered_distinct_wrong_denominator": (
        "Correctly forbids repeats (ordered distinct m-tuples) but normalises "
        "by n_e^m instead of the falling factorial n_e^{(m)}; biased DOWNWARD "
        "by the factor n_e^{(m)}/n_e^m."),
    "M3_binomial_count_wrong_denominator": (
        "Counts m-subsets correctly (C(S,m)) but divides by n_e^m instead of "
        "C(n_e,m); biased DOWNWARD by m!."),
    "M4_single_fixed_subset_0..m-1": (
        "Uses one fixed subset J = {0,...,m-1} instead of averaging over all "
        "subsets.  Unbiased iff the failure indicators are subset-exchangeable; "
        "biased otherwise.  The ring configurations are where this bites."),
}


# ==========================================================================
# 7.  THE I.I.D.-BY-CONSTRUCTION NULL GENERATOR (a sampler, plus its exact law)
# ==========================================================================

class IIDNullGenerator:
    """Generates failure vectors with the SAME n_e, the SAME block structure,
    and the SAME marginal failure probability p_i as a reference
    configuration, but INDEPENDENT BY CONSTRUCTION: each block's indicator is
    drawn from its own fresh Bernoulli(p_i) with no shared state.

    Two independent constructions of the same null are provided, because a
    null object that shares code with the thing it controls is not a control:

      * `sample()`             -- indicator-level: n_e independent Bernoulli
                                  draws.
      * `sample_coordinates()` -- coordinate-level: n_e independent blocks of
                                  n_2 i.i.d. Bernoulli(p_coord) coordinates,
                                  decoded by the same block model.  Its
                                  induced marginal is q = phi-mass of the
                                  block law; independence across blocks is a
                                  property of the CONSTRUCTION, not an
                                  assumption.

    Determinism: a single random.Random(seed) (Mersenne Twister) drives
    everything; the seed is recorded and the stream is consumed in a fixed
    order.
    """

    def __init__(self, n_e: int, p_i: Fraction, seed: int,
                 n2: int = None, model: BlockModel = None,
                 p_coord: Fraction = None):
        self.n_e = n_e
        self.p_i = p_i
        self.seed = seed
        self.n2 = n2
        self.model = model
        self.p_coord = p_coord
        self.rng = random.Random(seed)
        self._a = p_i.numerator
        self._b = p_i.denominator

    def sample(self) -> int:
        """One failure mask, indicators independent by construction."""
        msk = 0
        for j in range(self.n_e):
            if self.rng.randrange(self._b) < self._a:
                msk |= 1 << j
        return msk

    def sample_coordinates(self) -> int:
        """One failure mask via independent coordinate blocks."""
        assert self.model is not None and self.p_coord is not None
        a, b = self.p_coord.numerator, self.p_coord.denominator
        tab = self.model.table()
        scale = self.model.scale
        msk = 0
        for j in range(self.n_e):
            content = 0
            for c in range(self.n2):
                if self.rng.randrange(b) < a:
                    content |= 1 << c
            fn = tab[content]
            if fn == scale:
                fail = True
            elif fn == 0:
                fail = False
            else:
                fail = self.rng.randrange(scale) < fn
            if fail:
                msk |= 1 << j
        return msk

    def exact_law(self) -> FailureLaw:
        """The generator's own exact law, for the analytic-null check."""
        return fl_iid_indicator(self.n_e, self.p_i)

    def describe(self) -> dict:
        return {"n_e": self.n_e, "p_i": str(self.p_i), "seed": self.seed,
                "n2": self.n2, "p_coord": str(self.p_coord) if self.p_coord
                else None,
                "block_model": self.model.describe() if self.model else None,
                "rng": "python random.Random (Mersenne Twister)",
                "independent_by_construction": True}


def canonical_estimator(masks: list, n_e: int, m: int) -> Fraction:
    """The CORRECT estimator matching CONVENTION C2: mean of
    C(S_t, m)/C(n_e, m).  Exactly rational -- no floating point."""
    den = comb(n_e, m)
    tot = 0
    for msk in masks:
        tot += comb(popcount(msk), m)
    return Fraction(tot, den * len(masks))


def mutant_estimator_M1(masks: list, n_e: int, m: int) -> Fraction:
    """Indices drawn WITH REPLACEMENT: mean of (S_t/n_e)^m."""
    tot = 0
    for msk in masks:
        tot += popcount(msk) ** m
    return Fraction(tot, (n_e ** m) * len(masks))


def exact_estimator_variance(fl: FailureLaw, m: int) -> Fraction:
    """Exact per-sample variance of C(S,m)/C(n_e,m) under fl."""
    pS = fl.law_of_S()
    c = comb(fl.n_e, m)
    e1 = sum((pS[s] * Fraction(comb(s, m), c) for s in range(fl.n_e + 1)),
             Fraction(0))
    e2 = sum((pS[s] * Fraction(comb(s, m) ** 2, c * c)
              for s in range(fl.n_e + 1)), Fraction(0))
    return e2 - e1 * e1


# ==========================================================================
# 8.  CONFIGURATION DRIVER
# ==========================================================================

def analyse_failure_law(fl: FailureLaw, m: int, ks: list = None,
                        subset_table_cap: int = 200) -> dict:
    """Everything the oracle reports about one exactly-known failure law."""
    n_e = fl.n_e
    ks = ks or list(range(1, min(n_e, 6) + 1))
    qs = [fl.q(j) for j in range(n_e)]
    identical_marginals = all(x == qs[0] for x in qs)
    out = {
        "law": fl.describe(),
        "m": m,
        "marginals_q_j": [frac_record(x) for x in qs],
        "identical_marginals": identical_marginals,
        "moments": {},
        "subset_exchangeable": {},
    }
    for k in ks:
        subs = fl.mu_all_subsets(k)
        vals = list(subs.values())
        mubar = sum(vals, Fraction(0)) / len(vals)
        vmin, vmax = min(vals), max(vals)
        exch = (vmin == vmax)
        q0 = qs[0]
        rec = {
            "k": k,
            "mu_bar_k": frac_record(mubar),
            "mu_min_over_subsets": frac_record(vmin),
            "mu_max_over_subsets": frac_record(vmax),
            "n_subsets": len(vals),
            "product_of_marginals_q^k": frac_record(q0 ** k)
            if identical_marginals else None,
            "dependence_sign_vs_q^k": (
                None if not identical_marginals else
                ("independent" if mubar == q0 ** k else
                 ("positive" if mubar > q0 ** k else "negative"))),
            "binomial_moment_E[C(S,k)]": frac_record(mubar * comb(n_e, k)),
        }
        if len(vals) <= subset_table_cap:
            rec["per_subset"] = {",".join(map(str, J)): frac_record(v)
                                 for J, v in subs.items()}
        out["moments"][str(k)] = rec
        out["subset_exchangeable"][str(k)] = exch

    # identity check: sum over subsets of mu_k(J)  ==  E[C(S,k)] from law(S)
    pS = fl.law_of_S()
    ident = {}
    for k in ks:
        lhs = fl.binomial_moment(k)
        rhs = sum((pS[s] * comb(s, k) for s in range(n_e + 1)), Fraction(0))
        ident[str(k)] = {"agrees": lhs == rhs, "value": frac_record(lhs)}
    out["identity_binomial_moment_vs_law_of_S"] = ident

    if m <= n_e:
        tail = fl.tail(m)
        lead = comb(n_e, m) * fl.mu_bar(m)
        out["tail_P[S>=m]"] = frac_record(tail)
        out["leading_bonferroni_term_C(n_e,m)*mu_bar_m"] = frac_record(lead)
        out["leading_term_share"] = (frac_record(tail / lead) if lead > 0
                                     else None)
    out["law_of_S"] = [frac_record(x) for x in pS]
    return out


# ==========================================================================
# 9.  RUN ALL --- every number in oracle_values.json comes from here
# ==========================================================================

def run_all(seed: int, include_reach: bool = True) -> dict:
    t_start = time.time()
    results = {"configurations": [], "timings": {}}

    def timed(label, fn):
        t0 = time.time()
        val = fn()
        results["timings"][label] = round(time.time() - t0, 3)
        return val

    # ---------------------------------------------------------------- A1 --
    # NULL, coordinate-level, threshold decoder.  n_e=5, n2=4, N=20.
    def _a1():
        n_e, n2, t, p = 5, 4, 1, Fraction(1, 4)
        model = ThresholdBlockModel(n2, t)
        law = atomlaw_iid_bernoulli(n_e * n2, p)
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=3)
        q_ref = ref_block_failure_prob_bernoulli(model.weight_mass(),
                                                 model.scale, n2, p)
        checks = []
        for k in range(1, n_e + 1):
            got = fl.mu_bar(k)
            want = ref_iid(q_ref, k)
            per_subset_all_equal = (len(set(fl.mu_all_subsets(k).values())) == 1)
            checks.append({"k": k, "expected_p_i^k": frac_record(want),
                           "observed_mu_bar_k": frac_record(got),
                           "agrees": got == want,
                           "every_subset_equals_p_i^k": per_subset_all_equal and
                           (fl.mu(tuple(range(k))) == want)})
        rec["id"] = "A1-null-iid-bernoulli-threshold"
        rec["role"] = "I.I.D. NULL (duty 3): independent by construction at the coordinate level"
        rec["analytic_null_check"] = {
            "p_i_marginal": frac_record(q_ref),
            "p_i_from_enumeration": frac_record(fl.q(0)),
            "marginal_agrees": q_ref == fl.q(0),
            "per_k": checks,
            "all_agree": all(c["agrees"] and c["every_subset_equals_p_i^k"]
                             for c in checks),
        }
        rec["not_an_hqc_quantity"] = True
        return rec
    results["configurations"].append(timed("A1", _a1))

    # ---------------------------------------------------------------- A2 --
    # NULL with a RATIONAL phi (tie-splitting) -- exercises the scale>1 path.
    def _a2():
        n_e, n2, p = 5, 4, Fraction(1, 3)
        model = RM1BlockModel(2, tie="split")
        assert model.n2 == n2
        law = atomlaw_iid_bernoulli(n_e * n2, p)
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=3)
        q_ref = ref_block_failure_prob_bernoulli(model.weight_mass(),
                                                 model.scale, n2, p)
        checks = []
        for k in range(1, n_e + 1):
            got = fl.mu_bar(k)
            want = ref_iid(q_ref, k)
            checks.append({"k": k, "expected_p_i^k": frac_record(want),
                           "observed_mu_bar_k": frac_record(got),
                           "agrees": got == want})
        rec["id"] = "A2-null-iid-bernoulli-rm12-tiesplit"
        rec["role"] = "I.I.D. NULL with rational per-block failure probability (tie splitting)"
        rec["analytic_null_check"] = {
            "p_i_marginal": frac_record(q_ref),
            "marginal_agrees": q_ref == fl.q(0),
            "per_k": checks,
            "all_agree": all(c["agrees"] for c in checks),
        }
        rec["not_an_hqc_quantity"] = True
        return rec
    results["configurations"].append(timed("A2", _a2))

    # ---------------------------------------------------------------- A3 --
    # NEGATIVE dependence: uniform global fixed weight + threshold decoder.
    def _a3():
        n_e, n2, w, t = 5, 4, 6, 1
        model = ThresholdBlockModel(n2, t)
        law = atomlaw_fixed_weight(n_e * n2, w)
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=3)
        cross = []
        A = model.weight_mass()
        for k in range(1, n_e + 1):
            ra = fl.mu_bar(k)
            rb = route_b_mu(n_e, n2, w, A, model.scale, k)
            cross.append({"k": k, "routeA_full_enumeration": frac_record(ra),
                          "routeB_integer_convolution": frac_record(rb),
                          "agrees": ra == rb})
        rec["id"] = "A3-negative-global-fixed-weight-threshold"
        rec["role"] = "KNOWN-ANSWER NEGATIVE DEPENDENCE (duty 4)"
        rec["cross_route_check"] = {"per_k": cross,
                                    "all_agree": all(c["agrees"] for c in cross)}
        rec["not_an_hqc_quantity"] = True
        return rec
    results["configurations"].append(timed("A3", _a3))

    # ---------------------------------------------------------------- A4 --
    # NEGATIVE dependence with a fully independent analytic reference.
    def _a4():
        n_e, n2, w = 5, 4, 4
        model = ThresholdBlockModel(n2, 0)
        law = atomlaw_fixed_weight(n_e * n2, w)
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=3)
        checks = []
        for k in range(1, n_e + 1):
            got = fl.mu_bar(k)
            want = ref_occupancy(n_e, n2, w, k)
            rb = route_b_mu(n_e, n2, w, model.weight_mass(), 1, k)
            checks.append({"k": k,
                           "expected_inclusion_exclusion": frac_record(want),
                           "observed_routeA": frac_record(got),
                           "observed_routeB": frac_record(rb),
                           "agrees": got == want == rb})
        rec["id"] = "A4-negative-occupancy-analytic"
        rec["role"] = ("KNOWN-ANSWER NEGATIVE DEPENDENCE with an INDEPENDENT "
                       "closed form (inclusion-exclusion over empty blocks)")
        rec["analytic_check"] = {"per_k": checks,
                                 "all_agree": all(c["agrees"] for c in checks)}
        rec["not_an_hqc_quantity"] = True
        return rec
    results["configurations"].append(timed("A4", _a4))

    # ---------------------------------------------------------------- A5 --
    # POSITIVE dependence: latent mixture of two i.i.d. coordinate laws.
    def _a5():
        n_e, n2, t = 5, 4, 1
        p1, p2, lam = Fraction(1, 8), Fraction(1, 2), Fraction(1, 2)
        model = ThresholdBlockModel(n2, t)
        L1 = atomlaw_iid_bernoulli(n_e * n2, p1)
        L2 = atomlaw_iid_bernoulli(n_e * n2, p2)
        law = atomlaw_mixture([L1, L2], [lam, 1 - lam],
                              "mixture_iid(p=1/8,1/2;lam=1/2)")
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=3)
        A = model.weight_mass()
        q1 = ref_block_failure_prob_bernoulli(A, 1, n2, p1)
        q2 = ref_block_failure_prob_bernoulli(A, 1, n2, p2)
        checks = []
        for k in range(1, n_e + 1):
            got = fl.mu_bar(k)
            want = ref_mixture([q1 ** k, q2 ** k], [lam, 1 - lam])
            qbar = lam * q1 + (1 - lam) * q2
            checks.append({"k": k,
                           "expected_mixture_of_component_moments": frac_record(want),
                           "observed": frac_record(got), "agrees": got == want,
                           "q_bar^k": frac_record(qbar ** k),
                           "strictly_greater_than_q_bar^k": got > qbar ** k})
        rec["id"] = "A5-positive-latent-mixture"
        rec["role"] = ("KNOWN-ANSWER POSITIVE DEPENDENCE (duty 4): a latent "
                       "mixture over a common parameter, strict by Jensen for k>=2")
        rec["analytic_check"] = {"q_component_1": frac_record(q1),
                                 "q_component_2": frac_record(q2),
                                 "per_k": checks,
                                 "all_agree": all(c["agrees"] for c in checks)}
        rec["not_an_hqc_quantity"] = True
        return rec
    results["configurations"].append(timed("A5", _a5))

    # ---------------------------------------------------------------- A6 --
    # Both mechanisms in one object: a mixture of two NEGATIVELY dependent
    # fixed-weight ensembles, which is POSITIVELY dependent overall.
    def _a6():
        n_e, n2, t = 5, 4, 1
        w1, w2, lam = 3, 11, Fraction(1, 2)
        model = ThresholdBlockModel(n2, t)
        L1 = atomlaw_fixed_weight(n_e * n2, w1)
        L2 = atomlaw_fixed_weight(n_e * n2, w2)
        fl1 = build_failure_law(L1, model, n_e)
        fl2 = build_failure_law(L2, model, n_e)
        law = atomlaw_mixture([L1, L2], [lam, 1 - lam],
                              "mixture_fixed_weight(w=3,11;lam=1/2)")
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=3)
        checks = []
        for k in range(1, n_e + 1):
            got = fl.mu_bar(k)
            want = ref_mixture([fl1.mu_bar(k), fl2.mu_bar(k)], [lam, 1 - lam])
            qbar = lam * fl1.q(0) + (1 - lam) * fl2.q(0)
            checks.append({
                "k": k, "expected_mixture_of_component_moments": frac_record(want),
                "observed": frac_record(got), "agrees": got == want,
                "q_bar^k": frac_record(qbar ** k),
                "component_1_sign": ("negative" if fl1.mu_bar(k) < fl1.q(0) ** k
                                     else "not_negative"),
                "component_2_sign": ("negative" if fl2.mu_bar(k) < fl2.q(0) ** k
                                     else "not_negative"),
                "mixture_sign": ("positive" if got > qbar ** k else
                                 ("negative" if got < qbar ** k else "independent")),
            })
        rec["id"] = "A6-mixture-of-negative-components"
        rec["role"] = ("BOTH MECHANISMS IN ONE OBJECT: each component is "
                       "negatively dependent (sampling without replacement); the "
                       "mixture over the latent global weight is positively "
                       "dependent.  This is the shape EV-HQC-6fd5b1 O-6 describes; "
                       "it is a property of THIS TOY, not of HQC.")
        rec["analytic_check"] = {"per_k": checks,
                                 "all_agree": all(c["agrees"] for c in checks)}
        rec["not_an_hqc_quantity"] = True
        return rec
    results["configurations"].append(timed("A6", _a6))

    # ---------------------------------------------------------------- B --
    # Failure-level extremes with closed forms.
    def _b():
        out = []
        n_e = 8
        fl = fl_exactly_c(n_e, 3)
        rec = analyse_failure_law(fl, m=3, ks=[1, 2, 3, 4])
        rec["id"] = "B1-exactly-c-extreme-negative"
        rec["role"] = "KNOWN-ANSWER extreme negative dependence"
        rec["analytic_check"] = {
            "per_k": [{"k": k, "expected": frac_record(ref_exactly_c(n_e, 3, k)),
                       "observed": frac_record(fl.mu_bar(k)),
                       "agrees": fl.mu_bar(k) == ref_exactly_c(n_e, 3, k)}
                      for k in [1, 2, 3, 4]]}
        rec["analytic_check"]["all_agree"] = all(
            c["agrees"] for c in rec["analytic_check"]["per_k"])
        rec["not_an_hqc_quantity"] = True
        out.append(rec)

        p = Fraction(1, 10)
        fl = fl_comonotone(n_e, p)
        rec = analyse_failure_law(fl, m=3, ks=[1, 2, 3, 4])
        rec["id"] = "B2-comonotone-extreme-positive"
        rec["role"] = "KNOWN-ANSWER extreme positive dependence (mu_k = p for all k)"
        rec["analytic_check"] = {
            "per_k": [{"k": k, "expected": frac_record(ref_comonotone(p, k)),
                       "observed": frac_record(fl.mu_bar(k)),
                       "agrees": fl.mu_bar(k) == ref_comonotone(p, k)}
                      for k in [1, 2, 3, 4]]}
        rec["analytic_check"]["all_agree"] = all(
            c["agrees"] for c in rec["analytic_check"]["per_k"])
        rec["not_an_hqc_quantity"] = True
        out.append(rec)

        fl = fl_iid_indicator(n_e, p)
        rec = analyse_failure_law(fl, m=3, ks=[1, 2, 3, 4])
        rec["id"] = "B3-iid-indicator-null"
        rec["role"] = "I.I.D. NULL at the indicator level (duty 3, second construction)"
        rec["analytic_null_check"] = {
            "per_k": [{"k": k, "expected_p_i^k": frac_record(ref_iid(p, k)),
                       "observed": frac_record(fl.mu_bar(k)),
                       "agrees": fl.mu_bar(k) == ref_iid(p, k)}
                      for k in [1, 2, 3, 4]]}
        rec["analytic_null_check"]["all_agree"] = all(
            c["agrees"] for c in rec["analytic_null_check"]["per_k"])
        rec["not_an_hqc_quantity"] = True
        out.append(rec)
        return out
    for r in timed("B", _b):
        results["configurations"].append(r)

    # ---------------------------------------------------------------- R --
    # HQC-SHAPED RING ENSEMBLE on the TRUE space (T).
    def _ring(cfg_id, n, omega, omega_r, omega_e, n_e, n2, model, m, role,
              mc_samples=0, mc_seed=None):
        N = n_e * n2
        law = atomlaw_ring_hqc_shaped(n, omega, omega_r, omega_e, N)
        fl = build_failure_law(law, model, n_e)
        rec = analyse_failure_law(fl, m=m, ks=list(range(1, n_e + 1)))
        # partial shift-equivariance: blocks are cyclic translates by n2, so
        # mu(J) == mu(J+1) whenever the shifted set stays inside [0, n_e).
        shift = []
        for k in range(1, n_e):
            for J in combinations(range(n_e), k):
                if max(J) + 1 <= n_e - 1:
                    Js = tuple(j + 1 for j in J)
                    shift.append({"J": list(J), "J_shift": list(Js),
                                  "agrees": fl.mu(J) == fl.mu(Js)})
        full_exch = all(rec["subset_exchangeable"][str(k)]
                        for k in range(1, n_e + 1))
        aligned = (n == N)
        cyc = None
        if aligned:
            # n = n_e*n_2 exactly: shifting by n_2 is a CYCLIC PERMUTATION of
            # the blocks, so mu must be constant on cyclic orbits of subsets,
            # and the number of distinct mu values at level k must be at most
            # the number of cyclic orbits.  Both are checked.
            cyc = {"per_k": []}
            for k in range(1, n_e + 1):
                subs = fl.mu_all_subsets(k)
                ok = True
                for J, v in subs.items():
                    Jr = tuple(sorted((j + 1) % n_e for j in J))
                    if subs[Jr] != v:
                        ok = False
                orbits = set()
                for J in subs:
                    orb = min(tuple(sorted((j + s) % n_e for j in J))
                              for s in range(n_e))
                    orbits.add(orb)
                cyc["per_k"].append({
                    "k": k, "rotation_invariance_holds": ok,
                    "n_cyclic_orbits": len(orbits),
                    "n_distinct_mu_values": len(set(subs.values())),
                    "distinct_values_le_orbits":
                        len(set(subs.values())) <= len(orbits)})
            cyc["all_hold"] = all(x["rotation_invariance_holds"] and
                                  x["distinct_values_le_orbits"]
                                  for x in cyc["per_k"])
        rec["id"] = cfg_id
        rec["role"] = role
        rec["ring_symmetry_check"] = {
            "n_equals_n_e_times_n2": aligned,
            "block_shift_equivariance_tested": len(shift),
            "block_shift_equivariance_holds": all(s["agrees"] for s in shift),
            "detail": shift,
            "full_subset_exchangeability_observed": full_exch,
            "cyclic_orbit_check": cyc,
            "note": ("Block shift equivariance is a DERIVATION (the law of "
                     "e' = x*r2 + r1*y + e is invariant under cyclic shift of "
                     "F_2^n because the fixed-weight sets are shift-invariant "
                     "and ring multiplication commutes with shift, and B_{j+1} "
                     "is the translate of B_j by n_2), and it is VERIFIED here "
                     "rather than assumed.  FULL subset exchangeability is NOT "
                     "implied by it: when n = n_e*n_2 the group acting is only "
                     "the CYCLIC group of order n_e, so mu_k(J) is constant on "
                     "cyclic orbits of k-subsets and may differ BETWEEN orbits. "
                     "That is what is observed at k = 2 (adjacent vs opposite "
                     "block pairs).  This is a property of THESE TOY "
                     "CONFIGURATIONS and is not a statement about HQC."),
        }
        if mc_samples:
            gen = ring_sampler(n, omega, omega_r, omega_e, N, n_e, model,
                               mc_seed)
            masks = [next(gen) for _ in range(mc_samples)]
            est = canonical_estimator(masks, n_e, m)
            exact = fl.mu_bar(m)
            var1 = exact_estimator_variance(fl, m)
            sd = math.sqrt(float(var1) / mc_samples)
            qhat = Fraction(sum(popcount(x) for x in masks),
                            n_e * mc_samples)
            rec["sampler_vs_oracle_check"] = {
                "purpose": ("Does the oracle's exact mu_m equal what a SAMPLING "
                            "estimator of the same ensemble converges to?  This "
                            "is the check that the oracle certifies the SAME "
                            "OBJECT an estimator targets.  Toy ring only; NOT "
                            "the HQC decoding measurement."),
                "samples": mc_samples, "seed": mc_seed, "m": m,
                "exact_mu_bar_m": frac_record(exact),
                "estimator_C(S,m)/C(n_e,m)": frac_record(est),
                "exact_per_sample_variance": frac_record(var1),
                "standard_error": sd,
                "z_score": (float(est) - float(exact)) / sd if sd > 0 else None,
                "within_4_sigma": (abs((float(est) - float(exact)) / sd) < 4
                                   if sd > 0 else None),
                "exact_marginal_q": frac_record(fl.q(0)),
                "sampled_marginal_q": frac_record(qhat),
            }
        rec["not_an_hqc_quantity"] = True
        return rec

    def _r1():
        return _ring("R1-ring-truncated-prime-n17", 17, 3, 2, 2, 4, 4,
                     ThresholdBlockModel(4, 1), 3,
                     "HQC-SHAPED RING ENSEMBLE on space (T), n prime > n_e*n_2 "
                     "so 1 coordinate is truncated (assumption A23's shape)",
                     mc_samples=200000, mc_seed=seed + 11)
    results["configurations"].append(timed("R1", _r1))

    def _r2():
        return _ring("R2-ring-aligned-n16", 16, 3, 2, 2, 4, 4,
                     ThresholdBlockModel(4, 1), 3,
                     "HQC-SHAPED RING with n = n_e*n_2 exactly (no truncation), "
                     "so shifting by n_2 cyclically permutes the blocks; n=16 is "
                     "NOT prime, which HQC requires -- deviation stated")
    results["configurations"].append(timed("R2", _r2))

    def _r3():
        return _ring("R3-ring-rm12-tiesplit-n17", 17, 3, 2, 2, 4, 4,
                     RM1BlockModel(2, tie="split"), 3,
                     "HQC-SHAPED RING with an ML-decoded RM(1,2) inner block and "
                     "randomised tie-breaking (rider R-tie)")
    results["configurations"].append(timed("R3", _r3))

    def _r4():
        return _ring("R4-ring-3blocks-n19-n2-6", 19, 3, 3, 3, 3, 6,
                     ThresholdBlockModel(6, 2), 2,
                     "HQC-SHAPED RING, larger block (n_2 = 6), N = 18 coordinates")
    results["configurations"].append(timed("R4", _r4))

    # -------------------------------------------------------- MUTANTS ----
    def _mut():
        out = []
        specs = [
            ("A1-null-iid-bernoulli-threshold", 5, 4, 3,
             lambda: build_failure_law(
                 atomlaw_iid_bernoulli(20, Fraction(1, 4)),
                 ThresholdBlockModel(4, 1), 5)),
            ("A3-negative-global-fixed-weight-threshold", 5, 4, 3,
             lambda: build_failure_law(
                 atomlaw_fixed_weight(20, 6), ThresholdBlockModel(4, 1), 5)),
            ("A5-positive-latent-mixture", 5, 4, 3,
             lambda: build_failure_law(
                 atomlaw_mixture([atomlaw_iid_bernoulli(20, Fraction(1, 8)),
                                  atomlaw_iid_bernoulli(20, Fraction(1, 2))],
                                 [Fraction(1, 2), Fraction(1, 2)], "mix"),
                 ThresholdBlockModel(4, 1), 5)),
            ("R1-ring-truncated-prime-n17", 4, 4, 3,
             lambda: build_failure_law(
                 atomlaw_ring_hqc_shaped(17, 3, 2, 2, 16),
                 ThresholdBlockModel(4, 1), 4)),
        ]
        for cfg_id, n_e, n2, m, mk in specs:
            fl = mk()
            ex = mutant_expectations(fl, m)
            truth = ex["truth_mu_bar_m"]
            q0 = fl.q(0)
            entry = {"configuration": cfg_id, "m": m,
                     "truth_mu_bar_m": frac_record(truth),
                     "marginal_q": frac_record(q0),
                     "q^m": frac_record(q0 ** m),
                     "true_dependence_sign_vs_q^m":
                         ("independent" if truth == q0 ** m else
                          ("positive" if truth > q0 ** m else "negative")),
                     "mutants": {}}
            for key, val in ex.items():
                if key == "truth_mu_bar_m" or val is None:
                    continue
                ratio = (val / truth) if truth else None
                # what would a naive reader conclude from the mutant alone?
                reads_as = ("independent" if val == q0 ** m else
                            ("positive" if val > q0 ** m else "negative"))
                entry["mutants"][key] = {
                    "description": MUTANT_DESCRIPTIONS[key],
                    "value": frac_record(val),
                    "ratio_to_truth": frac_record(ratio) if ratio is not None else None,
                    "direction_vs_truth": ("over" if val > truth else
                                           ("under" if val < truth else "equal")),
                    "would_be_read_as_dependence": reads_as,
                    "misleads_sign": reads_as != entry["true_dependence_sign_vs_q^m"],
                    "detected_by_oracle": val != truth,
                }
            out.append(entry)
        return out
    results["mutant_analysis"] = timed("mutants", _mut)

    # ------------------------------------------------ MONTE-CARLO DEMO ---
    def _mc():
        n_e, p_i, m, T = 8, Fraction(1, 4), 3, 200000
        gen = IIDNullGenerator(n_e, p_i, seed)
        fl = gen.exact_law()
        exact = fl.mu_bar(m)
        assert exact == ref_iid(p_i, m)
        masks = [gen.sample() for _ in range(T)]
        est = canonical_estimator(masks, n_e, m)
        mut = mutant_estimator_M1(masks, n_e, m)
        var1 = exact_estimator_variance(fl, m)
        sd = math.sqrt(float(var1) / T)
        z = (float(est) - float(exact)) / sd if sd > 0 else None
        exM1 = mutant_expectations(fl, m)["M1_indices_with_replacement"]

        # second, coordinate-level construction of an independent null
        n2, p_coord = 4, Fraction(1, 4)
        model = ThresholdBlockModel(n2, 1)
        q2 = ref_block_failure_prob_bernoulli(model.weight_mass(), 1, n2, p_coord)
        gen2 = IIDNullGenerator(5, q2, seed + 1, n2=n2, model=model,
                                p_coord=p_coord)
        fl2 = fl_iid_indicator(5, q2)
        T2 = 200000
        masks2 = [gen2.sample_coordinates() for _ in range(T2)]
        est2 = canonical_estimator(masks2, 5, 3)
        exact2 = fl2.mu_bar(3)
        var2 = exact_estimator_variance(fl2, 3)
        sd2 = math.sqrt(float(var2) / T2)
        z2 = (float(est2) - float(exact2)) / sd2 if sd2 > 0 else None

        return {
            "purpose": ("DEMONSTRATION that the oracle discriminates a correct "
                        "estimator from the over-counting mutant.  This is NOT "
                        "evidence about anything; it is a self-test of the "
                        "instrument."),
            "indicator_level": {
                "generator": gen.describe(), "m": m, "samples": T,
                "exact_mu_m": frac_record(exact),
                "estimator_C(S,m)/C(n_e,m)": frac_record(est),
                "exact_per_sample_variance": frac_record(var1),
                "standard_error": sd, "z_score": z,
                "within_4_sigma": abs(z) < 4 if z is not None else None,
                "mutant_M1_observed": frac_record(mut),
                "mutant_M1_exact_expectation": frac_record(exM1),
                "mutant_M1_z_against_truth":
                    (float(mut) - float(exact)) / sd if sd > 0 else None,
            },
            "coordinate_level": {
                "generator": gen2.describe(), "m": 3, "samples": T2,
                "induced_marginal_q": frac_record(q2),
                "exact_mu_m": frac_record(exact2),
                "estimator": frac_record(est2),
                "standard_error": sd2, "z_score": z2,
                "within_4_sigma": abs(z2) < 4 if z2 is not None else None,
            },
        }
    results["monte_carlo_demonstration"] = timed("monte_carlo", _mc)

    # ------------------------------------------------------------ REACH --
    if include_reach:
        def _reach():
            out = []
            # (i) medium: Route A is impossible, Route B is exact and instant.
            for (n_e, n2, w, t, m) in [(16, 32, 40, 3, 6), (46, 384, 75, 3, 16),
                                       (46, 384, 75, 5, 16)]:
                model = ThresholdBlockModel(n2, t)
                A = model.weight_mass()
                t0 = time.time()
                q = route_b_mu(n_e, n2, w, A, 1, 1)
                mu = route_b_mu(n_e, n2, w, A, 1, m)
                dt = time.time() - t0
                out.append({
                    "id": "reach-routeB-n_e%d-n2%d-w%d-t%d-m%d" % (n_e, n2, w, t, m),
                    "route": "B_integer_convolution",
                    "n_e": n_e, "n2": n2, "N": n_e * n2, "global_weight": w,
                    "block_model": model.describe(), "m": m,
                    "marginal_q": frac_record(q), "mu_m": frac_record(mu),
                    "q^m": frac_record(q ** m),
                    "dependence_sign_vs_q^m": ("negative" if mu < q ** m else
                                               ("positive" if mu > q ** m
                                                else "independent")),
                    "seconds": round(dt, 4),
                    "routeA_atoms_would_be": "2^%d" % (n_e * n2),
                    "not_an_hqc_quantity": True,
                    "why_not_hqc": (
                        "The ensemble is UNIFORM FIXED WEIGHT over N coordinates, "
                        "which is NOT the law of HQC's etilde = x*r2 + r1*y + e; "
                        "the block decoder is a bounded-distance WEIGHT THRESHOLD "
                        "at an arbitrarily chosen t, which is NOT HQC's duplicated "
                        "Reed-Muller ML decoder.  Only the DIMENSIONS are "
                        "HQC-1-shaped.  This number is a demonstration of "
                        "computational reach and is not comparable to any "
                        "published DFR."),
                })
            return out
        results["reach_demonstrations"] = timed("reach", _reach)

    # ------------------------------------------- ESTIMATOR SAMPLE SIZE ---
    # Exact per-sample variance of the canonical estimator under an i.i.d.
    # null, and the exact number of samples needed for a target relative
    # standard error.  This is a statement about the ESTIMATOR, not about HQC:
    # it takes n_e and m as free parameters and sweeps a hypothetical marginal.
    def _samples():
        out = {
            "what_this_is": (
                "Exact per-sample variance of the canonical estimator "
                "C(S,m)/C(n_e,m) when S ~ Binomial(n_e, p) -- i.e. under the "
                "i.i.d. null -- and the exact sample count T needed for a "
                "target relative standard error.  n_e and m are free "
                "parameters and p is swept over hypothetical values.  NO "
                "HQC MARGINAL IS ASSERTED OR USED; this is a property of the "
                "estimator, provided as input to a feasibility analysis."),
            "relative_standard_error_target": "1/10",
            "rows": [],
        }
        r = Fraction(1, 10)
        for (n_e, m) in [(8, 3), (16, 6), (46, 16)]:
            for p in [Fraction(1, 2), Fraction(1, 4), Fraction(1, 10),
                      Fraction(1, 100), Fraction(1, 1000)]:
                c = comb(n_e, m)
                mu = p ** m
                e2 = Fraction(0)
                for s in range(m, n_e + 1):
                    ps = comb(n_e, s) * (p ** s) * ((1 - p) ** (n_e - s))
                    e2 += ps * Fraction(comb(s, m) ** 2, c * c)
                var = e2 - mu * mu
                T = None
                if mu > 0 and var > 0:
                    Tf = var / (r * r * mu * mu)
                    T = int(Tf) + (1 if Tf != int(Tf) else 0)
                out["rows"].append({
                    "n_e": n_e, "m": m, "p": str(p),
                    "mu_m_iid": frac_record(mu),
                    "per_sample_variance": frac_record(var),
                    "samples_for_10pct_relative_se": T,
                    "samples_log2": (math.log2(T) if T else None),
                })
        return out
    results["estimator_sample_size_requirements"] = timed("samples", _samples)

    # ------------------------------------------------- SCALING MEASURED --
    def _scaling():
        out = {"route_A_full_enumeration": [], "route_B_convolution": [],
               "ring_law_construction": []}
        model = ThresholdBlockModel(4, 1)
        for n_e in (2, 3, 4, 5):
            N = n_e * 4
            t0 = time.time()
            law = atomlaw_iid_bernoulli(N, Fraction(1, 4))
            fl = build_failure_law(law, model, n_e)
            fl.mu_bar(min(n_e, 3))
            out["route_A_full_enumeration"].append(
                {"n_e": n_e, "n2": 4, "N": N, "atoms": 1 << N,
                 "seconds": round(time.time() - t0, 3)})
        A = model.weight_mass()
        for (n_e, n2, w, m) in [(8, 16, 20, 4), (16, 64, 60, 8),
                                (46, 384, 75, 16), (100, 1024, 200, 30)]:
            mdl = ThresholdBlockModel(n2, 3)
            AA = mdl.weight_mass()
            t0 = time.time()
            route_b_mu(n_e, n2, w, AA, 1, m)
            out["route_B_convolution"].append(
                {"n_e": n_e, "n2": n2, "N": n_e * n2, "w": w, "m": m,
                 "seconds": round(time.time() - t0, 4)})
        for (n, om, omr, ome, N) in [(13, 3, 2, 2, 12), (17, 3, 2, 2, 16),
                                     (19, 3, 3, 3, 18)]:
            t0 = time.time()
            atomlaw_ring_hqc_shaped(n, om, omr, ome, N)
            out["ring_law_construction"].append(
                {"n": n, "omega": om, "omega_r": omr, "omega_e": ome, "N": N,
                 "ring_products_enumerated": comb(n, om) * comb(n, omr),
                 "wht_size": 1 << N,
                 "seconds": round(time.time() - t0, 3)})
        return out
    results["measured_scaling"] = timed("scaling", _scaling)

    results["timings"]["total_seconds"] = round(time.time() - t_start, 3)
    return results


# ==========================================================================
# 10.  PROVENANCE AND CLI
# ==========================================================================

def _git(*args) -> str:
    try:
        return subprocess.run(["git"] + list(args), capture_output=True,
                              text=True, timeout=30,
                              cwd=os.path.dirname(os.path.abspath(__file__))
                              ).stdout.strip()
    except Exception:
        return "unavailable"


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def provenance(seed: int, argv) -> dict:
    here = os.path.abspath(__file__)
    dirty = _git("status", "--porcelain")
    return {
        "task": TASK_ID,
        "batch": "BATCH-003",
        "goal": "GOAL-HQC-001",
        "command": "python3 " + " ".join([os.path.basename(here)] + list(argv[1:])),
        "cwd_note": "run from the task directory",
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty_tree": bool(dirty),
        "git_dirty_paths": [ln[3:] for ln in dirty.splitlines()] if dirty else [],
        "oracle_py_sha256": _sha256(here),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "third_party_dependencies": [],
        "stdlib_modules_used": ["fractions", "itertools", "math", "random",
                                "json", "hashlib", "platform", "subprocess",
                                "argparse", "time", "os", "sys"],
        "randomness_sources": [
            {"source": "python random.Random(seed) (Mersenne Twister)",
             "seed": seed,
             "used_for": ("the i.i.d. NULL GENERATOR sampler and the "
                          "Monte-Carlo self-test ONLY"),
             "not_used_for": ("any exact computation; every mu_k, tail, "
                              "variance and reference value is deterministic "
                              "exact arithmetic")},
        ],
        "arithmetic_regime": {
            "computation": "exact integer / fractions.Fraction only",
            "floating_point_used_for": ["the 'float' and 'log2' reporting "
                                        "fields", "the standard error / z-score "
                                        "of the Monte-Carlo self-test"],
            "log2_absolute_error_bound": 1e-9,
            "no_decision_depends_on_floats": True,
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "claude-opus-5",
            "fallback_used": True,
            "model_verified": False,
            "independent_session": True,
        },
    }


SCOPE_STATEMENT = (
    "THIS FILE CONTAINS NO STATEMENT ABOUT HQC.  Every value is an exact "
    "moment of a TOY, ENUMERABLE ensemble defined in oracle.py.  No "
    "configuration here is HQC's error distribution, no configuration here "
    "uses HQC's inner or outer code, and nothing here asserts that assumption "
    "A17 does or does not hold, or that HQC's decoding-failure-rate model is "
    "or is not correct.  Claim tier: toy.  certificate.kind: none (no solve "
    "and no relation is claimed).  The oracle is a CORRECTNESS INSTRUMENT for "
    "a later estimator, not a research result."
)


def main(argv=None) -> int:
    argv = list(sys.argv if argv is None else argv)
    ap = argparse.ArgumentParser(description="Exact joint-moment oracle "
                                             "(TASK-20260803-6f50df)")
    ap.add_argument("--out", default="oracle_values.json")
    ap.add_argument("--seed", type=int, default=20260803)
    ap.add_argument("--no-reach", action="store_true")
    args = ap.parse_args(argv[1:])

    t0 = time.time()
    res = run_all(args.seed, include_reach=not args.no_reach)
    doc = {
        "schema": SCHEMA,
        "scope_statement": SCOPE_STATEMENT,
        "convention": {
            "C1_distinct_indices": (
                "mu_k(J) = E[prod_{j in J} F_j] over DISTINCT block indices J; "
                "repetition is forbidden because F_j^2 = F_j makes a repeated "
                "index collapse onto a lower-order moment (an over-estimate)."),
            "C2_canonical_scalar": (
                "mu_k = (1/C(n_e,k)) sum_{|J|=k} mu_k(J) = E[C(S,k)]/C(n_e,k), "
                "the normalised k-th binomial moment of S = sum_j F_j.  The "
                "full per-subset table is reported alongside it whenever it is "
                "enumerable, and subset-exchangeability is TESTED, not assumed."),
            "C3_unconditional": (
                "No conditioning on the global weight of etilde, on S, or on "
                "anything else."),
            "C4_tie_breaking": (
                "Where the inner ML decoder ties, F_j is Bernoulli with an "
                "exact rational parameter given the block content, with "
                "tie-breaking independent across blocks (rider R-tie)."),
            "blocks": ("B_j = {j*n_2, ..., (j+1)*n_2 - 1}, disjoint and "
                       "consecutive, per TASK-20260802-15971b section 1."),
            "m": "m = delta_e + 1, the smallest number of symbol errors that "
                 "defeats the outer decoder.  Set explicitly per configuration.",
        },
        "provenance": provenance(args.seed, argv),
        "results": res,
    }
    with open(args.out, "w") as f:
        json.dump(doc, f, indent=1, sort_keys=False)
        f.write("\n")
    print("wrote %s (%.1f s total, %.1f s in run_all)"
          % (args.out, time.time() - t0, res["timings"]["total_seconds"]),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
