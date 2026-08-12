#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oracle.py -- EXACT joint-moment oracle and i.i.d.-by-construction null generator.

Task     : TASK-20260802-ecba30 (executor)
Batch    : BATCH-003        Goal: GOAL-HQC-001        Question: RQ-HQC-001
Purpose  : correctness instrument for a later Monte-Carlo estimator of the joint
           moment mu_m of inner-decoder block-failure indicators.

WHAT THIS IS
------------
An EXACT (enumerative, rational-arithmetic) computation of

    mu_J  =  E[ prod_{j in J} F_j ]   for a set J of DISTINCT block indices,
    mu_m  =  the average of mu_J over the C(n_e, m) sets J with |J| = m,

for TOY, ENUMERABLE ensembles, together with an i.i.d.-by-construction null
ensemble whose exact mu_m must equal p_i^m.

WHAT THIS IS NOT
----------------
It is NOT a measurement of HQC.  Every ensemble below is a toy of a size chosen
so that its state space can be enumerated exhaustively.  Nothing computed here
is a statement about HQC at HQC-1/3/5 or at any other parameter set, and nothing
here bears on whether assumption A17 holds.  See oracle_report.md section 2.

INDEXING CONVENTION (defended in oracle_report.md section 3)
------------------------------------------------------------
Following the BATCH-002 characterization
(coordination/.../BATCH-002/tasks/TASK-20260802-15971b/a17_characterization.md
section 1 and a17_sensitivity.yaml `notation`):

    B_j    = {j*n2, ..., (j+1)*n2 - 1}, j = 0 .. n_e-1   (disjoint blocks)
    F_j    = 1{ D_i(etilde^{(j)}) != 0 }                 (block j decodes wrong)
    S      = sum_j F_j
    mu_k   = P[F_{j1} = ... = F_{jk} = 1] for k DISTINCT indices j1..jk
    m      = delta_e + 1

Five properties of that convention are load-bearing and are enforced in code:
  (i)   indices are DISTINCT (a repeated index would give E[F_j^m] = q, a
        different quantity entirely);
  (ii)  the moment is UNCONDITIONAL (no conditioning on S, on the global weight,
        or on any event);
  (iii) it is a moment of the raw indicators, not of centred indicators (it is
        not a covariance/correlation);
  (iv)  the index set is FIXED IN ADVANCE, never selected from the sample
        (selecting the m most-failing blocks is a different, much larger
        quantity -- implemented as mutant MUT-C so tests can detect it);
  (v)   when mu_J is not constant in J, `mu_m` denotes the AVERAGE over all
        C(n_e,m) sets.  The characterization's Lemma L1 asserts the F_j are
        exchangeable, which would make (v) vacuous; the exact computations in
        this file show exchangeability FAILING in the toy ring ensemble, so (v)
        is not vacuous and is stated explicitly.  See section 3b and
        oracle_report.md section 6.

ESTIMATOR CORRESPONDENCE
------------------------
The average over index sets satisfies the identity

    (1/C(n_e,m)) * sum_{|J|=m} mu_J  =  E[ C(S, m) ] / C(n_e, m),

i.e. the m-th binomial moment of S normalised by C(n_e,m).  That right-hand
side is the natural unbiased estimator target from decoding trials, so this
module computes BOTH sides and checks they agree exactly.  The identity holds
WITHOUT exchangeability, which is why it is the right target to estimate.

ARITHMETIC
----------
Every mathematical value is computed in exact integer / fractions.Fraction
arithmetic.  Floating point is used in exactly two places, both presentation
only and neither feeding back into any computed value:
  * `as_record()` emits `float` and `log2` renderings beside the exact
    "num/den" string;
  * `log2_fraction()` produces those renderings.
Both are accurate to ~2^-52 relative, and the exact string is authoritative.

Wall-clock timings are not exactly reproducible; they live in a separate
`timings` block and no result depends on them.

RANDOMNESS
----------
The exact path uses NO randomness.  The only randomness is in the null SAMPLER
(`iid_null_sampler`), which exists so a downstream estimator has a generator to
draw from; it is seeded from `--seed`, uses random.Random, and realises the
Bernoulli exactly by integer comparison -- never a float.

USAGE
-----
    python3 oracle.py --out oracle_values.json --seed 20260802
    python3 oracle.py --list-configs
    python3 -m unittest -v test_oracle          (or: python3 test_oracle.py)
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from fractions import Fraction
from math import comb

# ===========================================================================
# 0.  Exact-arithmetic helpers
# ===========================================================================


def log2_fraction(fr: Fraction):
    """log2 of a non-negative Fraction, without overflowing to inf.

    PRESENTATION ONLY.  Absolute error <= ~1e-15 on the mantissa part, exact on
    the exponent part.  Never used inside a computation.
    """
    fr = Fraction(fr)
    if fr == 0:
        return None
    if fr < 0:
        raise ValueError("log2 of a negative Fraction")
    num, den = fr.numerator, fr.denominator
    shift = num.bit_length() - den.bit_length()
    if shift > 0:
        red = Fraction(num, den << shift)
    else:
        red = Fraction(num << (-shift), den)
    return shift + math.log2(float(red))


def as_record(fr) -> dict:
    """Exact value plus presentation-only renderings."""
    fr = Fraction(fr)
    return {
        "exact": f"{fr.numerator}/{fr.denominator}",
        "float": float(fr),
        "log2": log2_fraction(fr),
    }


def popcount(x: int) -> int:
    return bin(x).count("1")


def _lcm(a: int, b: int) -> int:
    return a * b // math.gcd(a, b)


# ===========================================================================
# 1.  Inner code and the block failure model
# ===========================================================================


class BlockFailureModel:
    """Exact conditional failure probability of ONE inner block.

    `fail_prob[u]` is P[F_j = 1 | etilde^{(j)} = u] as an exact Fraction, for
    each of the 2^n2 block patterns u (bit k of u = coordinate k of the block).
    The all-zero codeword is taken as transmitted, which is legitimate for a
    linear code under minimum-distance decoding (characterization sec 1).

    Tie handling (characterization R-tie, SPEC A13) is explicit:
      'zero_wins'  : optimistic   -- failure iff 0 is NOT among the minimisers
      'fail'       : conservative -- failure unless 0 is the UNIQUE minimiser
      'uniform'    : A13-style    -- a minimiser is chosen uniformly at random,
                     so fail_prob = (#nonzero minimisers)/(#minimisers).
    With 'uniform' the F_j are defined only once the per-block tie coins are, and
    mu_J = E[prod f] is the joint failure probability under the model "tie coins
    independent across blocks given etilde".  That extra independence assumption
    is exactly R-tie; it is recorded, not hidden.  'zero_wins' and 'fail' give
    genuine 0/1 indicators and need no such rider.
    """

    def __init__(self, name: str, n2: int, fail_prob, meta: dict | None = None):
        assert len(fail_prob) == 1 << n2
        self.name = name
        self.n2 = n2
        self.fail_prob = list(fail_prob)
        self.meta = meta or {}
        self.deterministic = all(f in (0, 1) for f in self.fail_prob)
        A = [Fraction(0)] * (n2 + 1)
        for u, f in enumerate(self.fail_prob):
            if f:
                A[popcount(u)] += f
        self.weight_enumerator = A   # A[t] = sum over patterns of weight t of f(u)

    # -- constructors -------------------------------------------------------

    @staticmethod
    def from_code(name: str, n2: int, codewords, tie_rule: str = "fail",
                  meta: dict | None = None) -> "BlockFailureModel":
        cws = list(codewords)
        assert 0 in cws, "the code must contain the all-zero codeword"
        fail = [Fraction(0)] * (1 << n2)
        for u in range(1 << n2):
            best = None
            n_min = 0
            n_min_nonzero = 0
            for c in cws:
                d = popcount(u ^ c)
                if best is None or d < best:
                    best, n_min, n_min_nonzero = d, 1, (1 if c != 0 else 0)
                elif d == best:
                    n_min += 1
                    if c != 0:
                        n_min_nonzero += 1
            if tie_rule == "uniform":
                fail[u] = Fraction(n_min_nonzero, n_min)
            elif tie_rule == "fail":
                fail[u] = Fraction(0) if (n_min == 1 and n_min_nonzero == 0) else Fraction(1)
            elif tie_rule == "zero_wins":
                fail[u] = Fraction(0) if n_min_nonzero < n_min else Fraction(1)
            else:
                raise ValueError(f"unknown tie_rule {tie_rule!r}")
        md = dict(meta or {})
        md.update({"tie_rule": tie_rule, "n_codewords": len(cws)})
        return BlockFailureModel(name, n2, fail, md)

    @staticmethod
    def repetition(n2: int, tie_rule: str = "fail") -> "BlockFailureModel":
        """[n2, 1, n2] binary repetition code."""
        allones = (1 << n2) - 1
        return BlockFailureModel.from_code(
            f"REP{n2}", n2, [0, allones], tie_rule,
            {"family": "repetition", "d": n2})

    @staticmethod
    def threshold(n2: int, t: int) -> "BlockFailureModel":
        """Failure iff the block carries >= t errors.  Not a code decoder; used
        for the closed-form negative-dependence case (block occupancy, t = 1)."""
        fail = [Fraction(1) if popcount(u) >= t else Fraction(0) for u in range(1 << n2)]
        return BlockFailureModel(f"THRESH{n2}_{t}", n2, fail,
                                 {"family": "threshold", "t": t})

    @staticmethod
    def duplicated_rm1(mm: int, dup: int, tie_rule: str = "fail") -> "BlockFailureModel":
        """First-order Reed-Muller RM(1, mm) of length 2^mm with each bit
        duplicated `dup` times: a toy analogue of HQC's [128,8,64] RM duplicated
        3x or 5x.  Parameters [2^mm * dup, mm+1, 2^(mm-1) * dup]."""
        L = 1 << mm
        base = []
        for a in range(1 << mm):
            for b in (0, 1):
                w = 0
                for x in range(L):
                    if (popcount(a & x) + b) & 1:
                        w |= 1 << x
                base.append(w)
        n2 = L * dup
        cws = []
        for w in base:
            d = 0
            for pos in range(L):
                if (w >> pos) & 1:
                    for r in range(dup):
                        d |= 1 << (pos * dup + r)
            cws.append(d)
        return BlockFailureModel.from_code(
            f"DRM1_{mm}x{dup}", n2, cws, tie_rule,
            {"family": "duplicated_RM1", "rm_m": mm, "dup": dup,
             "k": mm + 1, "d": (1 << (mm - 1)) * dup})


# ===========================================================================
# 2.  Exact laws of etilde in F_2^N
# ===========================================================================


class ExactVectorLaw:
    """Exact law of etilde in F_2^N as INTEGER weights over a common total:
    P[etilde = v] = weights[v] / total, exactly.  `weights` is a dense list of
    length 2^N or a sparse dict."""

    def __init__(self, N: int, weights, total: int, name: str = "",
                 meta: dict | None = None):
        self.N = N
        self._w = weights
        self.total = total
        self.name = name
        self.meta = meta or {}
        self.dense = isinstance(weights, list)

    def items(self):
        if self.dense:
            for v, w in enumerate(self._w):
                if w:
                    yield v, w
        else:
            for v, w in self._w.items():
                if w:
                    yield v, w

    def support_size(self) -> int:
        return sum(1 for _ in self.items())

    def check_normalisation(self) -> bool:
        return sum(w for _, w in self.items()) == self.total

    # -- constructors -------------------------------------------------------

    @staticmethod
    def coordinate_iid(N: int, p: Fraction) -> "ExactVectorLaw":
        """Coordinates i.i.d. Bernoulli(p): space (M), the BSC model."""
        p = Fraction(p)
        a, b = p.numerator, p.denominator
        c = b - a
        pa = [a ** t for t in range(N + 1)]
        pc = [c ** t for t in range(N + 1)]
        w = [0] * (1 << N)
        for v in range(1 << N):
            t = popcount(v)
            w[v] = pa[t] * pc[N - t]
        return ExactVectorLaw(N, w, b ** N, f"coordIID(p={p})",
                              {"ensemble": "coordinate_iid", "p": str(p)})

    @staticmethod
    def latent_mixture(N: int, components) -> "ExactVectorLaw":
        """Mixture over a finite latent Theta: with probability c_k the whole
        vector is i.i.d. Bernoulli(p_k).  Mechanism M_plus of
        a17_sensitivity.yaml step 4 (common mode); produces POSITIVE dependence
        between blocks."""
        components = [(Fraction(c), Fraction(p)) for c, p in components]
        assert sum(c for c, _ in components) == 1
        dens = [c.denominator * p.denominator ** N for c, p in components]
        D = 1
        for d in dens:
            D = _lcm(D, d)
        w = [0] * (1 << N)
        for (c, p), d in zip(components, dens):
            a, b = p.numerator, p.denominator
            cc = b - a
            scale = c.numerator * (D // d)
            pa = [a ** t for t in range(N + 1)]
            pc = [cc ** t for t in range(N + 1)]
            for v in range(1 << N):
                t = popcount(v)
                w[v] += scale * pa[t] * pc[N - t]
        return ExactVectorLaw(N, w, D, f"mixture({components})",
                              {"ensemble": "latent_mixture",
                               "components": [[str(c), str(p)] for c, p in components]})

    @staticmethod
    def global_fixed_weight(N: int, wt: int) -> "ExactVectorLaw":
        """etilde uniform over the vectors of EXACT weight wt: the fixed-budget /
        sampling-without-replacement mechanism M_minus."""
        d = {}
        for supp in itertools.combinations(range(N), wt):
            v = 0
            for i in supp:
                v |= 1 << i
            d[v] = 1
        return ExactVectorLaw(N, d, comb(N, wt), f"fixedweight(N={N},w={wt})",
                              {"ensemble": "global_fixed_weight", "w": wt})


# ---------------------------------------------------------------------------
# 2b.  The HQC-shaped ring ensemble -- toy analogue of space (T)
# ---------------------------------------------------------------------------


def _rot(v: int, i: int, n: int, mask: int) -> int:
    i %= n
    if i == 0:
        return v
    return ((v << i) | (v >> (n - i))) & mask


def ring_mul(a: int, b: int, n: int) -> int:
    """Product in F_2[X]/(X^n - 1), vectors as bitmasks."""
    mask = (1 << n) - 1
    z = 0
    i = 0
    aa = a
    while aa:
        if aa & 1:
            z ^= _rot(b, i, n, mask)
        aa >>= 1
        i += 1
    return z


def _fixed_weight_vectors(n: int, w: int):
    for supp in itertools.combinations(range(n), w):
        v = 0
        for i in supp:
            v |= 1 << i
        yield v


def _wht_inplace(a) -> None:
    """Walsh-Hadamard transform over the INTEGERS.  Exact: no rounding."""
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


def _xor_convolve(arrays):
    """Exact XOR-convolution of integer count arrays of common length 2^k."""
    L = len(arrays[0])
    assert L & (L - 1) == 0
    acc = None
    for arr in arrays:
        t = list(arr)
        _wht_inplace(t)
        acc = t if acc is None else [x * y for x, y in zip(acc, t)]
    _wht_inplace(acc)
    out = []
    for x in acc:
        q, r = divmod(x, L)
        assert r == 0, "inverse WHT was not exact -- integer arithmetic violated"
        assert q >= 0, "negative count from XOR-convolution"
        out.append(q)
    return out


def ring_product_law_restricted(n: int, wa: int, wb: int, N: int):
    """Exact law of (a*b) restricted to coordinates 0..N-1, for a, b uniform
    independent fixed-weight vectors of weights wa, wb in F_2[X]/(X^n - 1).
    Returns (counts over 2^N, number of pairs).

    Restriction to a coordinate window commutes with XOR, which is what lets the
    marginal be built without ever materialising the law on F_2^n."""
    mask_n = (1 << n) - 1
    mask_N = (1 << N) - 1
    counts = [0] * (1 << N)
    a_supports = list(itertools.combinations(range(n), wa))
    total = 0
    for b in _fixed_weight_vectors(n, wb):
        rots = [_rot(b, i, n, mask_n) for i in range(n)]
        for supp in a_supports:
            z = 0
            for i in supp:
                z ^= rots[i]
            counts[z & mask_N] += 1
            total += 1
    return counts, total


def ring_uniform_fixed_weight_law_restricted(n: int, w: int, N: int):
    mask_N = (1 << N) - 1
    counts = [0] * (1 << N)
    total = 0
    for v in _fixed_weight_vectors(n, w):
        counts[v & mask_N] += 1
        total += 1
    return counts, total


def hqc_shaped_ring_law(n: int, N: int, omega: int, omega_r: int,
                        omega_e: int) -> ExactVectorLaw:
    """Exact law of etilde = trunc_N(x*r2 + r1*y + e), with x, y uniform of
    weight omega, r1, r2 uniform of weight omega_r, e uniform of weight omega_e,
    all independent, in F_2[X]/(X^n - 1).  Over F_2 subtraction is addition, so
    this is the specification's e' = x.r2 - r1.y + e (A1) truncated as in A23.

    Closest toy analogue of space (T) in this module: it keeps the ring product,
    the exact fixed weights and the truncation.  It is still a TOY -- n here is
    at most a few tens, HQC-1 has n = 17669."""
    assert N <= n
    c1, t1 = ring_product_law_restricted(n, omega, omega_r, N)     # x * r2
    c2, t2 = ring_product_law_restricted(n, omega_r, omega, N)     # r1 * y
    c3, t3 = ring_uniform_fixed_weight_law_restricted(n, omega_e, N)
    counts = _xor_convolve([c1, c2, c3])
    total = t1 * t2 * t3
    assert sum(counts) == total
    return ExactVectorLaw(
        N, counts, total, f"ringT(n={n},N={N},w={omega}/{omega_r}/{omega_e})",
        {"ensemble": "hqc_shaped_ring_toy", "n": n, "N": N,
         "omega": omega, "omega_r": omega_r, "omega_e": omega_e,
         "truncated_coords": n - N})


def hqc_shaped_ring_law_direct(n: int, N: int, omega: int, omega_r: int,
                               omega_e: int) -> ExactVectorLaw:
    """INDEPENDENT second implementation of `hqc_shaped_ring_law`: the whole
    product space of (x, r2) x (r1, y) x e is enumerated tuple by tuple, with no
    Walsh-Hadamard transform and no appeal to restriction commuting with XOR.
    Cost C(n,omega)^2 * C(n,omega_r)^2 * C(n,omega_e), so tiny cases only."""
    mask_N = (1 << N) - 1
    z1s = [ring_mul(x, r2, n) for x in _fixed_weight_vectors(n, omega)
           for r2 in _fixed_weight_vectors(n, omega_r)]
    z2s = [ring_mul(r1, y, n) for r1 in _fixed_weight_vectors(n, omega_r)
           for y in _fixed_weight_vectors(n, omega)]
    es = list(_fixed_weight_vectors(n, omega_e))
    counts = [0] * (1 << N)
    total = 0
    for z1 in z1s:
        for z2 in z2s:
            z12 = z1 ^ z2
            for e in es:
                counts[(z12 ^ e) & mask_N] += 1
                total += 1
    return ExactVectorLaw(N, counts, total,
                          f"ringT_direct(n={n},N={N})",
                          {"ensemble": "hqc_shaped_ring_toy_direct"})


def smallest_primitive_prime_above(x: int) -> int:
    """Smallest prime n > x for which 2 is a primitive root -- SPEC 4.1's rule
    for picking n from n1*n2, mirrored so the toy has the same shape."""
    def is_prime(k):
        if k < 2:
            return False
        d = 2
        while d * d <= k:
            if k % d == 0:
                return False
            d += 1
        return True

    def two_is_primitive(p):
        order = p - 1
        fac = set()
        t = order
        d = 2
        while d * d <= t:
            while t % d == 0:
                fac.add(d)
                t //= d
            d += 1
        if t > 1:
            fac.add(t)
        return all(pow(2, order // f, p) != 1 for f in fac)

    k = x + 1
    while True:
        if is_prime(k) and two_is_primitive(k):
            return k
        k += 1


def dihedral_canonical_form(coords, n: int):
    """Canonical form of a coordinate subset of Z_n under the dihedral group
    (rotations X -> X^t and the coordinate negation X -> X^{-1}).

    The law of e' = x*r2 + r1*y + e on space (T) is invariant under both: the
    fixed-weight sets are invariant under cyclic shift and under i -> -i, and the
    ring product commutes with both.  Hence mu_J depends on the union of the
    blocks in J only through this canonical form.  Verified exactly below."""
    base = sorted(set(int(c) % n for c in coords))
    best = None
    for s in (1, -1):
        pts = sorted((s * c) % n for c in base)
        for t in range(n):
            cand = tuple(sorted((c + t) % n for c in pts))
            if best is None or cand < best:
                best = cand
    return best


# ===========================================================================
# 3.  The joint failure law -- the object every moment is read off
# ===========================================================================


class JointFailureLaw:
    """The exact joint law of (F_0, ..., F_{n_e-1}) as integer weights over a
    common total: P[F = f] = weights[f] / total, f a bitmask with bit j = F_j.

    All moments come from this object alone, so an ensemble is fully
    characterised by it."""

    ZETA_MAX_NE = 20   # above this, fall back to direct summation per index set

    def __init__(self, n_e: int, weights: dict, total: int, name: str = "",
                 meta: dict | None = None):
        self.n_e = n_e
        self.weights = {f: w for f, w in weights.items() if w}
        self.total = total
        self.name = name
        self.meta = meta or {}
        s = sum(self.weights.values())
        assert s == total, f"joint failure law does not normalise: {s} != {total}"
        self._zeta = None

    # -- construction from Fraction probabilities ---------------------------

    @staticmethod
    def from_probabilities(n_e: int, prob: dict, name: str = "",
                           meta: dict | None = None) -> "JointFailureLaw":
        D = 1
        for p in prob.values():
            D = _lcm(D, Fraction(p).denominator)
        w = {}
        for f, p in prob.items():
            p = Fraction(p)
            num = p.numerator * (D // p.denominator)
            if num:
                w[f] = num
        return JointFailureLaw(n_e, w, D, name, meta)

    def prob(self, f: int) -> Fraction:
        return Fraction(self.weights.get(f, 0), self.total)

    # -- superset zeta transform: mu_J for ALL J at once --------------------

    def _superset_sums(self):
        """g[J] = sum over f superset of J of weights[f].  Then mu_J =
        g[J]/total.  Cost n_e * 2^n_e integer additions."""
        if self._zeta is None:
            n = self.n_e
            if n > self.ZETA_MAX_NE:
                raise MemoryError(f"n_e={n} exceeds ZETA_MAX_NE")
            g = [0] * (1 << n)
            for f, w in self.weights.items():
                g[f] += w
            for j in range(n):
                bit = 1 << j
                for f in range(1 << n):
                    if not (f & bit):
                        g[f] += g[f | bit]
            self._zeta = g
        return self._zeta

    # -- the object this module exists to compute ---------------------------

    def mu(self, J) -> Fraction:
        """mu_J = P[F_j = 1 for every j in J], J a set of DISTINCT indices."""
        J = tuple(sorted(set(int(j) for j in J)))
        assert all(0 <= j < self.n_e for j in J), "index outside 0..n_e-1"
        maskJ = 0
        for j in J:
            maskJ |= 1 << j
        if self.n_e <= self.ZETA_MAX_NE:
            return Fraction(self._superset_sums()[maskJ], self.total)
        acc = 0
        for f, w in self.weights.items():
            if (f & maskJ) == maskJ:
                acc += w
        return Fraction(acc, self.total)

    def mu_all_index_sets(self, m: int) -> dict:
        return {J: self.mu(J) for J in itertools.combinations(range(self.n_e), m)}

    def mu_m(self, m: int) -> Fraction:
        """mu_m := average of mu_J over all C(n_e,m) index sets.  Equals the
        common value when the F_j are exchangeable, and is what the binomial-
        moment estimator targets in every case."""
        g = self._superset_sums() if self.n_e <= self.ZETA_MAX_NE else None
        acc = 0
        cnt = 0
        for J in itertools.combinations(range(self.n_e), m):
            maskJ = 0
            for j in J:
                maskJ |= 1 << j
            if g is not None:
                acc += g[maskJ]
            else:
                acc += sum(w for f, w in self.weights.items() if (f & maskJ) == maskJ)
            cnt += 1
        return Fraction(acc, self.total * cnt)

    def exchangeability_at(self, m: int):
        vals = list(self.mu_all_index_sets(m).values())
        return (min(vals) == max(vals), min(vals), max(vals))

    # -- derived quantities -------------------------------------------------

    def s_distribution(self):
        d = [0] * (self.n_e + 1)
        for f, w in self.weights.items():
            d[popcount(f)] += w
        return [Fraction(x, self.total) for x in d]

    def q(self) -> Fraction:
        return self.mu_m(1)

    def binomial_moment_mu_m(self, m: int) -> Fraction:
        """E[C(S,m)] / C(n_e,m): the quantity an estimator built from decoding
        trials naturally computes.  Identically equal to mu_m(m); no
        exchangeability needed."""
        d = self.s_distribution()
        num = sum((d[s] * comb(s, m) for s in range(self.n_e + 1)), Fraction(0))
        return num / comb(self.n_e, m)

    def tail_ge(self, m: int) -> Fraction:
        return sum(self.s_distribution()[m:], Fraction(0))


def joint_failure_law_from_vector_law(law: ExactVectorLaw, model: BlockFailureModel,
                                      n_e: int, name: str = "",
                                      meta: dict | None = None) -> JointFailureLaw:
    """GENERIC PATH.  No structure of the ensemble is used: every point of the
    support of etilde is visited, its n_e blocks are decoded, and the joint law
    of the failure vector is accumulated exactly.

    Cost O(|support(etilde)| * n_e) for a deterministic model, and
         O(|support| * n_e * 2^{n_e}) for a tie-randomised one."""
    n2 = model.n2
    assert law.N == n_e * n2, f"N={law.N} != n_e*n2={n_e * n2}"
    bm = (1 << n2) - 1
    fp = model.fail_prob
    md = {**law.meta, "inner_code": model.name,
          "tie_rule": model.meta.get("tie_rule"), **(meta or {})}
    nm = name or f"{law.name}|{model.name}"
    if model.deterministic:
        counts = {}
        fails = [1 if fp[u] else 0 for u in range(1 << n2)]
        for v, w in law.items():
            f = 0
            for j in range(n_e):
                if fails[(v >> (j * n2)) & bm]:
                    f |= 1 << j
            counts[f] = counts.get(f, 0) + w
        return JointFailureLaw(n_e, counts, law.total, nm, md)
    acc = {}
    for v, w in law.items():
        probs = [fp[(v >> (j * n2)) & bm] for j in range(n_e)]
        dist = {0: Fraction(1)}
        for j, f in enumerate(probs):
            if f == 0:
                continue
            nd = {}
            bit = 1 << j
            for key, pv in dist.items():
                if f != 1:
                    nd[key] = nd.get(key, Fraction(0)) + pv * (1 - f)
                nd[key | bit] = nd.get(key | bit, Fraction(0)) + pv * f
            dist = nd
        wt = Fraction(w, law.total)
        for key, pv in dist.items():
            acc[key] = acc.get(key, Fraction(0)) + wt * pv
    return JointFailureLaw.from_probabilities(n_e, acc, nm, md)


# ---------------------------------------------------------------------------
# 3b.  Block-level ensembles defined directly on (F_0, ..., F_{n_e-1})
# ---------------------------------------------------------------------------


def block_iid_null(n_e: int, p_i: Fraction) -> JointFailureLaw:
    """THE I.I.D.-BY-CONSTRUCTION NULL OBJECT.

    Same n_e, same block structure (n_e disjoint blocks, one indicator each) and
    the same marginal failure probability p_i -- independent by construction.
    Its exact mu_m must equal p_i^m.  The enumeration in JointFailureLaw does not
    use that fact, so the comparison is a genuine test of the machinery."""
    p_i = Fraction(p_i)
    a, b = p_i.numerator, p_i.denominator
    c = b - a
    pa = [a ** t for t in range(n_e + 1)]
    pc = [c ** t for t in range(n_e + 1)]
    w = {}
    for f in range(1 << n_e):
        k = popcount(f)
        val = pa[k] * pc[n_e - k]
        if val:
            w[f] = val
    return JointFailureLaw(n_e, w, b ** n_e, f"blockIIDnull(n_e={n_e},p_i={p_i})",
                           {"ensemble": "block_iid_null", "p_i": str(p_i)})


def matched_null_for(jl: JointFailureLaw) -> JointFailureLaw:
    """The null object matched to an ensemble: same n_e, same block structure,
    marginal set to that ensemble's own exact q, independent by construction.
    This is the control docs/inventor-protocol.md requires -- the identical
    measurement on an object of the same shape with the dependence removed."""
    return block_iid_null(jl.n_e, jl.q())


def exactly_c_failures(n_e: int, c: int) -> JointFailureLaw:
    """Uniform over the failure patterns with EXACTLY c failing blocks: strongly
    negatively dependent, closed form mu_m = C(n_e-m,c-m)/C(n_e,c), q = c/n_e."""
    w = {}
    for supp in itertools.combinations(range(n_e), c):
        f = 0
        for j in supp:
            f |= 1 << j
        w[f] = 1
    return JointFailureLaw(n_e, w, comb(n_e, c), f"exactlyC(n_e={n_e},c={c})",
                           {"ensemble": "exactly_c_failures", "c": c})


# ===========================================================================
# 4.  Closed forms -- independent second implementations for known-answer tests
# ===========================================================================


def cf_iid_block(p_i: Fraction, m: int) -> Fraction:
    """Analytic null: mu_m = p_i^m."""
    return Fraction(p_i) ** m


def cf_block_failure_prob_coordinate_iid(model: BlockFailureModel, p: Fraction) -> Fraction:
    """q under coordinates i.i.d. Bernoulli(p), from the failure weight
    enumerator alone -- no joint law is touched."""
    p = Fraction(p)
    n2 = model.n2
    A = model.weight_enumerator
    return sum((A[t] * p ** t * (1 - p) ** (n2 - t) for t in range(n2 + 1)), Fraction(0))


def cf_coordinate_iid(model: BlockFailureModel, p: Fraction, m: int) -> Fraction:
    """Blocks are functions of disjoint sets of independent coordinates, hence
    independent, hence mu_m = q^m EXACTLY.  (On space (M), A17 is a theorem --
    characterization sec 2.1.)"""
    return cf_block_failure_prob_coordinate_iid(model, p) ** m


def cf_latent_mixture(model: BlockFailureModel, components, m: int) -> Fraction:
    """mu_m = E[Q^m] with Q = q(p_Theta).  By Jensen mu_m >= q^m, with equality
    iff Q is degenerate: POSITIVE dependence, mechanism M_plus."""
    return sum((Fraction(c) * cf_block_failure_prob_coordinate_iid(model, p) ** m
                for c, p in components), Fraction(0))


def cf_block_occupancy(N: int, n2: int, w: int, m: int) -> Fraction:
    """etilde uniform of weight w; F_j = 1 iff block j is non-empty.
    Inclusion-exclusion over which of the m blocks are forced empty:
        mu_m = sum_{i=0}^{m} (-1)^i C(m,i) C(N - i*n2, w) / C(N, w)."""
    tot = comb(N, w)
    s = Fraction(0)
    for i in range(m + 1):
        s += Fraction((-1) ** i * comb(m, i) * comb(N - i * n2, w), tot)
    return s


def cf_exactly_c(n_e: int, c: int, m: int) -> Fraction:
    if m > c:
        return Fraction(0)
    return Fraction(comb(n_e - m, c - m), comb(n_e, c))


def cf_global_fixed_weight(model: BlockFailureModel, N: int, w: int, m: int) -> Fraction:
    """STRUCTURED PATH for etilde uniform of weight w on F_2^N.

    Conditioned on the per-block weights each block is uniform among patterns of
    that weight, and the block weights are multivariate hypergeometric, so

        mu_m = sum_t (A^{*m})[t] * C(N - m*n2, w - t) / C(N, w),

    with A[t] the failure weight enumerator of one block and A^{*m} its m-fold
    convolution.  Exact, and polynomial in n_e, w and m -- the only path in this
    module that reaches HQC's own n_e and m."""
    n2 = model.n2
    A = model.weight_enumerator
    conv = [Fraction(1)]
    for _ in range(m):
        nxt = [Fraction(0)] * (len(conv) + n2)
        for i, a in enumerate(conv):
            if a == 0:
                continue
            for t, b in enumerate(A):
                if b:
                    nxt[i + t] += a * b
        conv = nxt
    tot = comb(N, w)
    s = Fraction(0)
    for t, cval in enumerate(conv):
        if cval == 0:
            continue
        rem = w - t
        if 0 <= rem <= N - m * n2:
            s += cval * Fraction(comb(N - m * n2, rem), tot)
    return s


def cf_jordan_tail(mu_by_k: dict, n_e: int, m: int) -> Fraction:
    """Jordan's inclusion-exclusion (a17_sensitivity.yaml derivation step 1),
    which uses NO independence assumption:
        P[S >= m] = sum_{k=m}^{n_e} (-1)^(k-m) C(k-1,m-1) C(n_e,k) mu_k,
    with mu_k the AVERAGE of mu_J over |J| = k (exchangeability not required)."""
    s = Fraction(0)
    for k in range(m, n_e + 1):
        s += Fraction((-1) ** (k - m)) * comb(k - 1, m - 1) * comb(n_e, k) * mu_by_k[k]
    return s


# ===========================================================================
# 5.  Mutant estimators -- the bugs that LOOK LIKE SIGNAL
# ===========================================================================
#
# Each mutant is a plausible mis-implementation of mu_m.  They exist so the test
# suite can demonstrate it HAS THE POWER to detect them: a suite that cannot
# separate the correct estimator from these has certified nothing.  All three are
# evaluated on the EXACT S-distribution, so every discrepancy shown is a property
# of the FORMULA and not of sampling noise.


def mut_a_repeated_indices(jl: JointFailureLaw, m: int) -> Fraction:
    """MUT-A: indices drawn WITH REPETITION -- E[(S/n_e)^m].  Over-counts
    coincidences (a block always 'agrees' with itself), so it reads high, i.e.
    as POSITIVE dependence, even under the exact null."""
    d = jl.s_distribution()
    ne = jl.n_e
    return sum((d[s] * Fraction(s, ne) ** m for s in range(ne + 1)), Fraction(0))


def mut_b_ordered_uncorrected(jl: JointFailureLaw, m: int) -> Fraction:
    """MUT-B: ordered distinct tuples normalised by n_e^m instead of the falling
    factorial -- E[(S)_m]/n_e^m.  Reads low, i.e. as NEGATIVE dependence."""
    d = jl.s_distribution()
    ne = jl.n_e
    tot = Fraction(0)
    for s in range(ne + 1):
        fall = 1
        for i in range(m):
            fall *= (s - i)
        if fall > 0:
            tot += d[s] * Fraction(fall, ne ** m)
    return tot


def mut_c_selected_indices(jl: JointFailureLaw, m: int) -> Fraction:
    """MUT-C: index set chosen FROM THE SAMPLE ('did some m blocks all fail?')
    rather than fixed in advance -- P[S >= m].  Grossly inflated; this is the
    selection bug clause (iv) of the indexing convention forbids."""
    return jl.tail_ge(m)


MUTANTS = {
    "MUT-A_repeated_indices": mut_a_repeated_indices,
    "MUT-B_ordered_uncorrected": mut_b_ordered_uncorrected,
    "MUT-C_selected_index_set": mut_c_selected_indices,
}


# ===========================================================================
# 6.  The i.i.d. null SAMPLER (the only randomness in this module)
# ===========================================================================


def iid_null_sampler(n_e: int, p_i: Fraction, seed: int):
    """Generator of block-failure vectors i.i.d. Bernoulli(p_i) BY CONSTRUCTION:
    each block gets its own independent draw and the Bernoulli is realised
    exactly by comparing a uniform integer in [0, den) against num.  No floating
    point, hence no rounding bias in the null."""
    p_i = Fraction(p_i)
    rng = random.Random(seed)
    num, den = p_i.numerator, p_i.denominator
    while True:
        f = 0
        for j in range(n_e):
            if rng.randrange(den) < num:
                f |= 1 << j
        yield f


def estimate_mu_m(samples, m: int, n_e: int) -> Fraction:
    """The estimator a protocol would use: mean of C(S,m)/C(n_e,m).  Unbiased for
    the average of mu_J over index sets, hence for mu_m as defined here."""
    denom = comb(n_e, m)
    tot = 0
    cnt = 0
    for f in samples:
        tot += comb(popcount(f), m)
        cnt += 1
    return Fraction(tot, cnt * denom)


def exact_estimator_variance(jl: JointFailureLaw, m: int) -> Fraction:
    """Exact per-sample variance of C(S,m)/C(n_e,m), so the sampler check is a
    z-score against a computed standard error rather than an eyeballed
    tolerance."""
    d = jl.s_distribution()
    ne = jl.n_e
    c = comb(ne, m)
    e1 = sum((d[s] * Fraction(comb(s, m), c) for s in range(ne + 1)), Fraction(0))
    e2 = sum((d[s] * Fraction(comb(s, m), c) ** 2 for s in range(ne + 1)), Fraction(0))
    return e2 - e1 * e1


# ===========================================================================
# 7.  Configurations actually computed
# ===========================================================================


def _codes():
    return {
        "REP3": BlockFailureModel.repetition(3),
        "REP5": BlockFailureModel.repetition(5),
        "DRM1_2x2": BlockFailureModel.duplicated_rm1(2, 2, "fail"),
        "DRM1_2x2_uniform_ties": BlockFailureModel.duplicated_rm1(2, 2, "uniform"),
        "DRM1_2x2_zero_wins": BlockFailureModel.duplicated_rm1(2, 2, "zero_wins"),
        "DRM1_3x1": BlockFailureModel.duplicated_rm1(3, 1, "fail"),
        "OCC3": BlockFailureModel.threshold(3, 1),
        "OCC4": BlockFailureModel.threshold(4, 1),
    }


def _sign(val: Fraction, ref: Fraction) -> str:
    if val > ref:
        return "positive_dependence"
    if val < ref:
        return "negative_dependence"
    return "independent"


def run_all(seed: int, heavy: bool = True) -> dict:
    t_start = time.perf_counter()
    codes = _codes()
    out = {"timings": {}, "results": {}}
    R = out["results"]
    T = out["timings"]

    R["inner_codes"] = [
        {"name": name, "n2": mdl.n2, "meta": mdl.meta,
         "deterministic_indicator": mdl.deterministic,
         "failure_weight_enumerator_A[t]": [str(a) for a in mdl.weight_enumerator]}
        for name, mdl in codes.items()
    ]

    # =======================================================================
    # DUTY 3 -- the i.i.d. null, block level: enumerated vs analytic p_i^m
    # =======================================================================
    t0 = time.perf_counter()
    rows = []
    for n_e, p_i in [(8, Fraction(1, 3)), (10, Fraction(1, 7)),
                     (12, Fraction(3, 100)), (14, Fraction(1, 2)),
                     (16, Fraction(2, 5))]:
        jl = block_iid_null(n_e, p_i)
        for m in sorted({1, 2, 3, min(5, n_e), min(8, n_e)}):
            enum = jl.mu_m(m)
            anal = cf_iid_block(p_i, m)
            fixed = jl.mu(range(m))
            binm = jl.binomial_moment_mu_m(m)
            exch, lo, hi = jl.exchangeability_at(m)
            rows.append({
                "n_e": n_e, "p_i": str(p_i), "m": m,
                "joint_states_enumerated": 1 << n_e,
                "index_sets_checked": comb(n_e, m),
                "mu_m_enumerated": as_record(enum),
                "mu_m_analytic_p_i^m": as_record(anal),
                "mu_m_fixed_index_set_0..m-1": as_record(fixed),
                "mu_m_binomial_moment_form": as_record(binm),
                "agrees_exactly_with_analytic_null": enum == anal,
                "fixed_set_equals_average": fixed == enum,
                "binomial_moment_equals_average": binm == enum,
                "exchangeable_across_all_index_sets": exch,
            })
    R["duty3_iid_null_block_level"] = {
        "what": ("Ensemble with the SAME n_e, the SAME block structure and the SAME "
                 "marginal p_i, independent BY CONSTRUCTION.  mu_m is enumerated over "
                 "all 2^n_e joint states with no use of independence, then compared "
                 "against the analytic p_i^m."),
        "arithmetic": "exact integers/Fraction; agreement is exact rational equality",
        "rows": rows,
        "ALL_AGREE_WITH_ANALYTIC_NULL": all(r["agrees_exactly_with_analytic_null"]
                                            for r in rows),
    }
    T["duty3_block_null"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 3/4 -- i.i.d. null at COORDINATE level, through the full pipeline
    # =======================================================================
    t0 = time.perf_counter()
    rows = []
    for code_name, n_e, p in [("REP3", 4, Fraction(1, 4)),
                              ("REP3", 5, Fraction(3, 10)),
                              ("REP3", 4, Fraction(1, 2)),
                              ("DRM1_2x2", 2, Fraction(1, 5)),
                              ("DRM1_2x2_uniform_ties", 2, Fraction(1, 5)),
                              ("OCC3", 4, Fraction(1, 5))]:
        mdl = codes[code_name]
        N = n_e * mdl.n2
        law = ExactVectorLaw.coordinate_iid(N, p)
        assert law.check_normalisation()
        jl = joint_failure_law_from_vector_law(law, mdl, n_e)
        q_enum = jl.q()
        q_cf = cf_block_failure_prob_coordinate_iid(mdl, p)
        for m in range(1, n_e + 1):
            enum = jl.mu_m(m)
            anal = cf_coordinate_iid(mdl, p, m)
            exch, lo, hi = jl.exchangeability_at(m)
            rows.append({
                "inner_code": code_name, "n_e": n_e, "n2": mdl.n2, "N": N,
                "p_star": str(p), "m": m, "states_enumerated": 1 << N,
                "q_enumerated": as_record(q_enum), "q_closed_form": as_record(q_cf),
                "q_agrees": q_enum == q_cf,
                "mu_m_enumerated": as_record(enum),
                "mu_m_analytic_q^m": as_record(anal),
                "agrees_exactly": enum == anal,
                "exchangeable_across_all_index_sets": exch,
            })
    R["duty3_iid_null_coordinate_level"] = {
        "what": ("Space (M): coordinates i.i.d. Bernoulli(p*).  The FULL pipeline "
                 "(2^N vector enumeration -> block extraction -> ML inner decoding -> "
                 "joint moment) is exercised and must return exactly q^m, because the "
                 "blocks are functions of disjoint sets of independent coordinates."),
        "why_this_is_the_test_that_catches_the_oracle": (
            "If the joint-moment code over-counted coincidences, these rows would come "
            "out ABOVE q^m even though the ensemble is independent by construction -- "
            "i.e. the oracle itself would be manufacturing the signal this campaign is "
            "looking for."),
        "rows": rows,
        "ALL_AGREE": all(r["agrees_exactly"] for r in rows),
    }
    T["duty3_coord_null"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 4 -- POSITIVE dependence (latent mixture, mechanism M_plus)
    # =======================================================================
    t0 = time.perf_counter()
    rows = []
    mixes = [
        ("REP3", 4, [(Fraction(1, 2), Fraction(1, 10)), (Fraction(1, 2), Fraction(1, 2))]),
        ("REP3", 4, [(Fraction(3, 4), Fraction(1, 20)), (Fraction(1, 4), Fraction(2, 5))]),
        ("REP3", 5, [(Fraction(1, 3), Fraction(1, 10)), (Fraction(1, 3), Fraction(1, 4)),
                     (Fraction(1, 3), Fraction(2, 5))]),
        ("DRM1_2x2", 2, [(Fraction(1, 2), Fraction(1, 10)), (Fraction(1, 2), Fraction(2, 5))]),
        ("REP3", 4, [(Fraction(1, 2), Fraction(1, 4)), (Fraction(1, 2), Fraction(1, 4))]),
    ]
    for code_name, n_e, comps in mixes:
        mdl = codes[code_name]
        N = n_e * mdl.n2
        law = ExactVectorLaw.latent_mixture(N, comps)
        assert law.check_normalisation()
        jl = joint_failure_law_from_vector_law(law, mdl, n_e)
        q = jl.q()
        degenerate = len({p for _, p in comps}) == 1
        for m in range(1, n_e + 1):
            enum = jl.mu_m(m)
            anal = cf_latent_mixture(mdl, comps, m)
            rows.append({
                "inner_code": code_name, "n_e": n_e, "N": N, "m": m,
                "components_[weight,p]": [[str(c), str(p)] for c, p in comps],
                "latent_is_degenerate": degenerate,
                "q_exact": as_record(q),
                "mu_m_enumerated": as_record(enum),
                "mu_m_closed_form_E[Q^m]": as_record(anal),
                "mu_m_on_matched_iid_null_q^m": as_record(q ** m),
                "agrees_exactly_with_closed_form": enum == anal,
                "A_ratio_mu_m_over_q^m": as_record(enum / q ** m),
                "sign_observed": _sign(enum, q ** m),
                "sign_predicted_by_Jensen": ("independent" if (degenerate or m < 2)
                                             else "positive_dependence"),
            })
    R["duty4_positive_dependence_latent_mixture"] = {
        "what": ("Mechanism M_plus of a17_sensitivity.yaml step 4: a latent Theta "
                 "shared by every block.  Closed form mu_m = E[Q^m]; Jensen forces "
                 "mu_m > q^m for m >= 2 when Q is non-degenerate, and equality when it "
                 "is degenerate (the last row is that degenerate control)."),
        "rows": rows,
        "ALL_AGREE": all(r["agrees_exactly_with_closed_form"] for r in rows),
        "ALL_SIGNS_AS_PREDICTED": all(r["sign_observed"] == r["sign_predicted_by_Jensen"]
                                      for r in rows if r["m"] >= 2),
    }
    T["duty4_positive"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 4 -- NEGATIVE dependence, two independent closed forms
    # =======================================================================
    t0 = time.perf_counter()
    rows = []
    for n_e, c in [(6, 2), (8, 3), (10, 4), (12, 5)]:
        jl = exactly_c_failures(n_e, c)
        q = jl.q()
        for m in range(1, min(c, 4) + 1):
            enum = jl.mu_m(m)
            anal = cf_exactly_c(n_e, c, m)
            rows.append({
                "family": "exactly_c_failures", "n_e": n_e, "c": c, "m": m,
                "q_exact": as_record(q),
                "mu_m_enumerated": as_record(enum),
                "mu_m_closed_form": as_record(anal),
                "agrees_exactly": enum == anal,
                "A_ratio_mu_m_over_q^m": as_record(enum / q ** m),
                "sign_observed": _sign(enum, q ** m),
                "sign_predicted": "negative_dependence" if m >= 2 else "independent",
            })
    occ_rows = []
    for n_e, n2, w in [(4, 3, 3), (5, 3, 4), (4, 4, 5), (6, 3, 6)]:
        mdl = codes[f"OCC{n2}"]
        N = n_e * n2
        law = ExactVectorLaw.global_fixed_weight(N, w)
        assert law.check_normalisation()
        jl = joint_failure_law_from_vector_law(law, mdl, n_e)
        q = jl.q()
        for m in range(1, min(n_e, 4) + 1):
            enum = jl.mu_m(m)
            anal = cf_block_occupancy(N, n2, w, m)
            struct = cf_global_fixed_weight(mdl, N, w, m)
            occ_rows.append({
                "family": "block_occupancy_fixed_global_weight",
                "n_e": n_e, "n2": n2, "N": N, "w": w, "m": m,
                "support_size_C(N,w)": comb(N, w),
                "q_exact": as_record(q),
                "mu_m_enumerated": as_record(enum),
                "mu_m_closed_form_inclusion_exclusion": as_record(anal),
                "mu_m_structured_convolution_path": as_record(struct),
                "agrees_with_closed_form": enum == anal,
                "agrees_with_structured_path": enum == struct,
                "A_ratio_mu_m_over_q^m": as_record(enum / q ** m),
                "sign_observed": _sign(enum, q ** m),
                "sign_predicted": "negative_dependence" if m >= 2 else "independent",
            })
    R["duty4_negative_dependence"] = {
        "what": ("Two families with independent closed forms.  (a) uniform over the "
                 "failure patterns with exactly c failing blocks: "
                 "mu_m = C(n_e-m,c-m)/C(n_e,c).  (b) etilde uniform of global weight w "
                 "with F_j = 1{block j non-empty}: mu_m by inclusion-exclusion.  Both "
                 "are sampling-without-replacement structures, i.e. mechanism M_minus."),
        "exactly_c_rows": rows,
        "occupancy_rows": occ_rows,
        "ALL_AGREE": (all(r["agrees_exactly"] for r in rows)
                      and all(r["agrees_with_closed_form"] for r in occ_rows)
                      and all(r["agrees_with_structured_path"] for r in occ_rows)),
        "ALL_SIGNS_AS_PREDICTED": all(r["sign_observed"] == r["sign_predicted"]
                                      for r in rows + occ_rows),
    }
    T["duty4_negative"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 4 -- mutant estimators on the EXACT null (power of the suite)
    # =======================================================================
    t0 = time.perf_counter()
    mut_rows = []
    for n_e, p_i, m in [(8, Fraction(1, 3), 2), (8, Fraction(1, 3), 3),
                        (10, Fraction(1, 7), 2), (12, Fraction(3, 100), 3),
                        (16, Fraction(2, 5), 4)]:
        jl = block_iid_null(n_e, p_i)
        truth = jl.mu_m(m)
        row = {"n_e": n_e, "p_i": str(p_i), "m": m,
               "correct_mu_m": as_record(truth),
               "analytic_null_p_i^m": as_record(p_i ** m),
               "mutants": {}}
        for mname, fn in MUTANTS.items():
            val = fn(jl, m)
            row["mutants"][mname] = {
                "value": as_record(val),
                "ratio_to_truth": as_record(val / truth),
                "log2_ratio": log2_fraction(val / truth),
                "reads_as": _sign(val, truth),
                "detected_by_the_null_check": val != truth,
            }
        mut_rows.append(row)
    R["duty4_mutant_estimators"] = {
        "what": ("Three plausible mis-implementations of mu_m, evaluated on the EXACT "
                 "i.i.d. null.  Any of them applied to real data would report structure "
                 "where there is none.  Every discrepancy is a property of the formula, "
                 "not sampling noise."),
        "definitions": {
            "MUT-A_repeated_indices": "E[(S/n_e)^m] -- indices drawn with repetition",
            "MUT-B_ordered_uncorrected": "E[(S)_m]/n_e^m -- distinct but wrongly normalised",
            "MUT-C_selected_index_set": "P[S >= m] -- index set selected from the sample",
        },
        "rows": mut_rows,
        "EVERY_MUTANT_DETECTED_ON_THE_NULL": all(
            d["detected_by_the_null_check"] for r in mut_rows for d in r["mutants"].values()),
    }
    T["duty4_mutants"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 1 -- the HQC-shaped ring ensemble (toy analogue of space (T))
    # =======================================================================
    t0 = time.perf_counter()
    ring_rows = []
    ring_configs = [
        (4, 3, "REP3", 2, 2, 2),
        (4, 3, "REP3", 3, 3, 3),
        (5, 3, "REP3", 2, 2, 2),
        (5, 3, "REP3", 3, 3, 3),
        (3, 4, "OCC4", 2, 2, 2),
    ]
    if heavy:
        ring_configs.append((6, 3, "REP3", 3, 3, 3))
    for n_e, n2, code_name, om, omr, ome in ring_configs:
        mdl = codes[code_name]
        assert mdl.n2 == n2
        N = n_e * n2
        n = smallest_primitive_prime_above(N)
        tc = time.perf_counter()
        law = hqc_shaped_ring_law(n, N, om, omr, ome)
        assert law.check_normalisation()
        jl = joint_failure_law_from_vector_law(law, mdl, n_e)
        build_s = time.perf_counter() - tc
        q = jl.q()
        mu_by_k = {k: jl.mu_m(k) for k in range(1, n_e + 1)}
        entry = {
            "n": n, "n_e": n_e, "n2": n2, "N": N,
            "truncated_coordinates_ell": n - N,
            "inner_code": code_name,
            "omega": om, "omega_r": omr, "omega_e": ome,
            "state_space_of_etilde": 1 << N,
            "sampling_tuples_underlying_the_law":
                comb(n, om) ** 2 * comb(n, omr) ** 2 * comb(n, ome),
            "build_seconds": build_s,
            "q_exact": as_record(q),
            "per_m": [],
        }
        for m in range(1, n_e + 1):
            enum = mu_by_k[m]
            fixed0 = jl.mu(range(m))
            binm = jl.binomial_moment_mu_m(m)
            exch, lo, hi = jl.exchangeability_at(m)
            spread = (hi - lo) / enum if enum else Fraction(0)
            entry["per_m"].append({
                "m": m,
                "mu_m_average_over_index_sets": as_record(enum),
                "mu_m_fixed_index_set_0..m-1": as_record(fixed0),
                "mu_m_binomial_moment_form": as_record(binm),
                "binomial_moment_matches_average": binm == enum,
                "index_sets_checked": comb(n_e, m),
                "exchangeable_all_index_sets_equal": exch,
                "min_over_index_sets": as_record(lo),
                "max_over_index_sets": as_record(hi),
                "relative_spread_(max-min)/mean": as_record(spread),
                "mu_m_on_matched_iid_null_q^m": as_record(q ** m),
                "A_ratio_mu_m_over_q^m": as_record(enum / q ** m),
                "log2_A": log2_fraction(enum / q ** m),
                "sign_observed": _sign(enum, q ** m),
            })
        # Jordan identity: exact, uses no independence and no exchangeability
        jordan = {}
        for m in range(1, n_e + 1):
            lhs = jl.tail_ge(m)
            rhs = cf_jordan_tail(mu_by_k, n_e, m)
            jordan[str(m)] = {"P[S>=m]_direct": as_record(lhs),
                              "P[S>=m]_from_joint_moments": as_record(rhs),
                              "agree": lhs == rhs}
        entry["jordan_inclusion_exclusion_check"] = jordan
        entry["s_distribution"] = [as_record(x) for x in jl.s_distribution()]

        # Dihedral-class prediction: mu_J depends on the union of blocks in J only
        # through its orbit under rotation + negation on Z_n.  Verified exactly.
        classes = {}
        for m in (2, 3):
            if m > n_e:
                continue
            buckets = {}
            for J in itertools.combinations(range(n_e), m):
                U = [j * n2 + t for j in J for t in range(n2)]
                key = str(dihedral_canonical_form(U, n))
                buckets.setdefault(key, []).append((list(J), jl.mu(J)))
            cls = []
            ok = True
            for key, members in buckets.items():
                vals = {v for _, v in members}
                if len(vals) != 1:
                    ok = False
                cls.append({
                    "canonical_form": key,
                    "index_sets": [mm[0] for mm in members],
                    "distinct_mu_values": [as_record(v) for v in sorted(vals)],
                    "constant_on_class": len(vals) == 1,
                })
            classes[str(m)] = {
                "n_classes": len(buckets),
                "n_index_sets": comb(n_e, m),
                "mu_constant_on_every_class": ok,
                "classes": cls,
            }
        entry["dihedral_orbit_check"] = classes
        ring_rows.append(entry)
    R["duty1_hqc_shaped_ring_toy_space_T"] = {
        "what": ("etilde = trunc_N(x*r2 + r1*y + e) in F_2[X]/(X^n - 1) with x, y of "
                 "weight omega, r1, r2 of weight omega_r and e of weight omega_e, all "
                 "uniform and independent -- the toy analogue of space (T).  Built by "
                 "exact integer XOR-convolution (Walsh-Hadamard over Z, no rounding), "
                 "then enumerated point by point."),
        "NOT_A_STATEMENT_ABOUT_HQC": (
            "n here is at most a few tens; HQC-1 has n = 17669, n2 = 384, n_e = 46, "
            "m = 16.  These rows characterise the TOY ensemble and nothing else."),
        "rows": ring_rows,
        "EXCHANGEABILITY_HOLDS_EVERYWHERE": all(
            pm["exchangeable_all_index_sets_equal"]
            for r in ring_rows for pm in r["per_m"]),
        "ALL_BINOMIAL_MOMENT_MATCHES": all(pm["binomial_moment_matches_average"]
                                           for r in ring_rows for pm in r["per_m"]),
        "ALL_JORDAN_IDENTITIES_HOLD": all(
            v["agree"] for r in ring_rows
            for v in r["jordan_inclusion_exclusion_check"].values()),
        "MU_CONSTANT_ON_EVERY_DIHEDRAL_CLASS": all(
            c["mu_constant_on_every_class"] for r in ring_rows
            for c in r["dihedral_orbit_check"].values()),
        "observed_signs_of_A": sorted({pm["sign_observed"] for r in ring_rows
                                       for pm in r["per_m"] if pm["m"] >= 2}),
    }
    T["duty1_ring"] = time.perf_counter() - t0

    # -- ring law verified against a fully independent enumeration -----------
    t0 = time.perf_counter()
    dcheck = []
    direct_cfgs = [(7, 6, 1, 1, 1), (7, 6, 2, 2, 2), (11, 6, 1, 2, 1)]
    if heavy:
        direct_cfgs.append((11, 6, 2, 2, 1))
    for n, N, om, omr, ome in direct_cfgs:
        a = hqc_shaped_ring_law(n, N, om, omr, ome)
        b = hqc_shaped_ring_law_direct(n, N, om, omr, ome)
        same = (a.total == b.total
                and all(a._w[v] == b._w[v] for v in range(1 << N)))
        dcheck.append({
            "n": n, "N": N, "omega": om, "omega_r": omr, "omega_e": ome,
            "tuples_enumerated_directly": comb(n, om) ** 2 * comb(n, omr) ** 2 * comb(n, ome),
            "wht_path_total": a.total, "direct_path_total": b.total,
            "laws_identical": same,
        })
    R["ring_law_independent_verification"] = {
        "what": ("The Walsh-Hadamard/restriction path for the ring ensemble is checked "
                 "against a direct enumeration of the entire product space of "
                 "(x, r2, r1, y, e), which uses neither the transform nor the argument "
                 "that restriction commutes with XOR."),
        "rows": dcheck,
        "ALL_IDENTICAL": all(r["laws_identical"] for r in dcheck),
    }
    T["ring_direct_verification"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 6 -- reach: the structured path at HQC's own n_e and m
    # =======================================================================
    t0 = time.perf_counter()
    reach_rows = []
    for code_name, n_e, w, ms in [
            ("DRM1_2x2", 46, 60, [1, 2, 4, 8, 16]),
            ("DRM1_3x1", 46, 120, [1, 2, 4, 8, 16]),
            ("DRM1_2x2", 56, 80, [1, 17]),
            ("DRM1_2x2", 90, 130, [1, 30]),
            ("REP5", 46, 60, [1, 16])]:
        mdl = codes[code_name]
        N = n_e * mdl.n2
        q = cf_global_fixed_weight(mdl, N, w, 1)
        row = {"inner_code": code_name, "n2": mdl.n2, "n_e": n_e, "N": N,
               "global_weight_w": w, "q_exact": as_record(q), "per_m": []}
        for m in ms:
            tc = time.perf_counter()
            val = cf_global_fixed_weight(mdl, N, w, m)
            dt = time.perf_counter() - tc
            row["per_m"].append({
                "m": m, "mu_m_exact": as_record(val),
                "mu_m_iid_null_q^m": as_record(q ** m),
                "A_ratio_mu_m_over_q^m": as_record(val / q ** m),
                "log2_A": log2_fraction(val / q ** m),
                "sign_observed": _sign(val, q ** m),
                "seconds": dt,
            })
        reach_rows.append(row)
    R["duty6_reach_structured_path"] = {
        "what": ("The multivariate-hypergeometric structured path reaches HQC's own n_e "
                 "(46/56/90) and m (16/17/30) EXACTLY -- but only with a TOY inner block "
                 "length n2 (5, 8 here, against HQC's 384 or 640) and with etilde "
                 "uniform of fixed global weight instead of the ring law.  It "
                 "demonstrates the machinery at the real INDEX scale and says nothing "
                 "about HQC."),
        "rows": reach_rows,
    }
    T["duty6_reach"] = time.perf_counter() - t0

    # =======================================================================
    # Cross-algorithm agreement: generic enumeration vs structured path
    # =======================================================================
    t0 = time.perf_counter()
    xrows = []
    for code_name, n_e, w in [("REP3", 4, 4), ("REP3", 5, 3), ("OCC3", 4, 5),
                              ("DRM1_2x2", 2, 6), ("REP5", 3, 5)]:
        mdl = codes[code_name]
        N = n_e * mdl.n2
        law = ExactVectorLaw.global_fixed_weight(N, w)
        jl = joint_failure_law_from_vector_law(law, mdl, n_e)
        for m in range(1, min(n_e, 4) + 1):
            g = jl.mu_m(m)
            s = cf_global_fixed_weight(mdl, N, w, m)
            xrows.append({
                "inner_code": code_name, "n_e": n_e, "N": N, "w": w, "m": m,
                "support_size": comb(N, w),
                "generic_enumeration": as_record(g),
                "structured_convolution": as_record(s),
                "agree_exactly": g == s,
            })
    R["cross_algorithm_agreement"] = {
        "what": ("Two independent algorithms for the same mu_m: brute-force enumeration "
                 "of every point of the support, versus the hypergeometric convolution "
                 "identity.  Neither is derived from the other in code."),
        "rows": xrows,
        "ALL_AGREE": all(r["agree_exactly"] for r in xrows),
    }
    T["cross_algorithm"] = time.perf_counter() - t0

    # =======================================================================
    # Tie-rule sensitivity (characterization R-tie), reported not hidden
    # =======================================================================
    t0 = time.perf_counter()
    tie_rows = []
    for tie in ["fail", "uniform", "zero_wins"]:
        mdl = BlockFailureModel.duplicated_rm1(2, 2, tie)
        p = Fraction(1, 5)
        q = cf_block_failure_prob_coordinate_iid(mdl, p)
        tie_rows.append({
            "inner_code": "DRM1_2x2", "tie_rule": tie, "p_star": str(p),
            "q_exact": as_record(q),
            "indicator_is_deterministic": mdl.deterministic,
            "mu_3_under_coordinate_iid": as_record(cf_coordinate_iid(mdl, p, 3)),
        })
    R["tie_rule_sensitivity"] = {
        "what": ("R-tie of the BATCH-002 characterization made concrete.  The three tie "
                 "rules give three different q, so the tie rule is PART OF THE "
                 "DEFINITION of F_j and a protocol must fix it.  'uniform' (A13-style) "
                 "additionally needs tie coins independent ACROSS blocks for "
                 "mu_J = E[prod f] to be the joint failure probability; that rider is "
                 "recorded here, not assumed silently."),
        "rows": tie_rows,
    }
    T["tie_rules"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 5 -- the null SAMPLER, checked against its own exact law
    # =======================================================================
    t0 = time.perf_counter()
    samp_rows = []
    Z_THRESHOLD = 6.0   # pre-registered here; the observed z is reported regardless
    for idx, (n_e, p_i, m, nsamp) in enumerate([
            (8, Fraction(1, 3), 2, 200000),
            (8, Fraction(1, 3), 3, 200000),
            (12, Fraction(1, 4), 4, 200000),
            (16, Fraction(2, 5), 3, 100000)]):
        sub_seed = seed + 1000 * idx
        jl = block_iid_null(n_e, p_i)
        exact = jl.mu_m(m)
        var = exact_estimator_variance(jl, m)
        gen = iid_null_sampler(n_e, p_i, sub_seed)
        samples = [next(gen) for _ in range(nsamp)]
        est = estimate_mu_m(samples, m, n_e)
        se = math.sqrt(float(var) / nsamp)
        z = (float(est) - float(exact)) / se if se > 0 else 0.0
        samp_rows.append({
            "n_e": n_e, "p_i": str(p_i), "m": m, "n_samples": nsamp,
            "seed": sub_seed,
            "rng": "random.Random(seed); Bernoulli by randrange(den) < num, no floats",
            "exact_mu_m": as_record(exact),
            "monte_carlo_estimate": as_record(est),
            "exact_per_sample_variance": as_record(var),
            "standard_error": se, "z_score": z,
            "pre_registered_abs_z_threshold": Z_THRESHOLD,
            "within_threshold": abs(z) < Z_THRESHOLD,
        })
    R["duty5_null_sampler_check"] = {
        "what": ("The i.i.d. null GENERATOR (as opposed to its exact law) is drawn from, "
                 "and its estimate compared with the exact value using the EXACT "
                 "per-sample variance -- so the tolerance is a computed standard error, "
                 "not an eyeballed one.  Fully deterministic given the recorded seeds."),
        "estimator": "mean of C(S,m)/C(n_e,m)",
        "rows": samp_rows,
        "ALL_WITHIN_PRE_REGISTERED_THRESHOLD": all(r["within_threshold"] for r in samp_rows),
    }
    T["duty5_sampler"] = time.perf_counter() - t0

    # =======================================================================
    # DUTY 6 -- measured cost scaling
    # =======================================================================
    t0 = time.perf_counter()
    scaling = {"generic_enumeration_coordinate_iid": [], "ring_law_build": [],
               "structured_convolution_path": [], "inner_code_table": [],
               "superset_zeta_transform": []}
    mdl = codes["REP3"]
    for n_e in [3, 4, 5, 6, 7]:
        N = n_e * 3
        tc = time.perf_counter()
        law = ExactVectorLaw.coordinate_iid(N, Fraction(1, 4))
        jl = joint_failure_law_from_vector_law(law, mdl, n_e)
        jl.mu_m(min(2, n_e))
        scaling["generic_enumeration_coordinate_iid"].append(
            {"n_e": n_e, "n2": 3, "N": N, "states": 1 << N,
             "seconds": time.perf_counter() - tc})
    for n_e in [3, 4, 5, 6]:
        N = n_e * 3
        n = smallest_primitive_prime_above(N)
        tc = time.perf_counter()
        hqc_shaped_ring_law(n, N, 2, 2, 2)
        scaling["ring_law_build"].append(
            {"n": n, "N": N, "states": 1 << N, "omega": 2,
             "pairs_enumerated": comb(n, 2) ** 2 * 2 + comb(n, 2),
             "seconds": time.perf_counter() - tc})
    for m in [2, 4, 8, 16, 30, 60]:
        tc = time.perf_counter()
        cf_global_fixed_weight(codes["DRM1_2x2"], 90 * 8, 130, m)
        scaling["structured_convolution_path"].append(
            {"n2": 8, "n_e": 90, "N": 720, "m": m,
             "seconds": time.perf_counter() - tc})
    for n2, kind in [(3, "repetition"), (5, "repetition"), (8, "DRM1_2x2"),
                     (16, "DRM1_3x2"), (20, "DRM1_2x5")]:
        tc = time.perf_counter()
        if kind == "repetition":
            BlockFailureModel.repetition(n2)
        elif kind == "DRM1_2x2":
            BlockFailureModel.duplicated_rm1(2, 2)
        elif kind == "DRM1_3x2":
            BlockFailureModel.duplicated_rm1(3, 2)
        else:
            BlockFailureModel.duplicated_rm1(2, 5)
        scaling["inner_code_table"].append(
            {"n2": n2, "code": kind, "patterns": 1 << n2,
             "seconds": time.perf_counter() - tc})
    for n_e in [8, 12, 16, 18]:
        jl = block_iid_null(n_e, Fraction(1, 3))
        tc = time.perf_counter()
        jl._superset_sums()
        scaling["superset_zeta_transform"].append(
            {"n_e": n_e, "states": 1 << n_e, "seconds": time.perf_counter() - tc})
    R["duty6_measured_scaling"] = scaling
    T["duty6_scaling"] = time.perf_counter() - t0

    T["total"] = time.perf_counter() - t_start
    return out


# ===========================================================================
# 8.  Provenance and entry point
# ===========================================================================


def _git(*args) -> str:
    try:
        return subprocess.run(["git"] + list(args), capture_output=True, text=True,
                              cwd=os.path.dirname(os.path.abspath(__file__)),
                              timeout=30).stdout.strip()
    except Exception as exc:  # pragma: no cover
        return f"<unavailable: {exc}>"


def _sha256(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError as exc:  # pragma: no cover
        return f"<unavailable: {exc}>"


def provenance(seed: int, argv) -> dict:
    here = os.path.dirname(os.path.abspath(__file__))
    status = _git("status", "--porcelain")
    return {
        "task_id": "TASK-20260802-ecba30",
        "batch_id": "BATCH-003",
        "goal_id": "GOAL-HQC-001",
        "question_id": "RQ-HQC-001",
        "role": "executor",
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty_tree": bool(status),
        "git_dirty_paths": status.splitlines(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "third_party_modules_used": [],
        "third_party_note": "numpy is NOT installed in this environment and is not used",
        "stdlib_modules_used": sorted(
            ["argparse", "hashlib", "itertools", "json", "math", "os", "platform",
             "random", "subprocess", "sys", "time", "fractions"]),
        "command": "python3 " + " ".join([os.path.basename(str(argv[0]))] + [str(a) for a in argv[1:]]),
        "seed": seed,
        "seed_scope": ("Used ONLY by the null-sampler check (duty 5).  Every exact value "
                       "in this file is produced by enumeration and is independent of "
                       "the seed."),
        "oracle_py_sha256": _sha256(os.path.join(here, "oracle.py")),
        "test_oracle_py_sha256": _sha256(os.path.join(here, "test_oracle.py")),
        "certificate": {
            "kind": "none",
            "reason": ("Pure exact computation.  No discrete log, no factor-base "
                       "relation, no solve and no break is claimed, so there is nothing "
                       "to certify.  Independent re-checking is provided instead by "
                       "pairing every enumerated value with a closed form or a second "
                       "algorithm."),
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "claude-opus-5",
            "fallback_used": True,
            "model_verified": False,
            "independent_session": True,
        },
        "claim_tier": "toy",
        "scope_statement": (
            "TOY ENUMERABLE CONFIGURATIONS ONLY.  Nothing in this file is a measurement "
            "of HQC, a statement about HQC at any parameter set, or a statement about "
            "whether assumption A17 holds."),
    }


def main(argv=None) -> int:
    argv = list(sys.argv if argv is None else argv)
    ap = argparse.ArgumentParser(description="exact joint-moment oracle")
    ap.add_argument("--out", default=None, help="write oracle_values.json here")
    ap.add_argument("--seed", type=int, default=20260802,
                    help="seed for the null-sampler check only")
    ap.add_argument("--light", action="store_true",
                    help="skip the largest ring configurations")
    ap.add_argument("--list-configs", action="store_true")
    args = ap.parse_args(argv[1:])

    if args.list_configs:
        for name, mdl in _codes().items():
            print(f"{name:24s} n2={mdl.n2:3d} patterns={1 << mdl.n2:8d} "
                  f"deterministic={mdl.deterministic} meta={mdl.meta}")
        return 0

    res = run_all(seed=args.seed, heavy=not args.light)
    doc = {
        "schema": "oracle_values/1",
        "title": ("Exact joint moments mu_m of inner-decoder block-failure indicators, "
                  "for TOY enumerable ensembles"),
        "provenance": provenance(args.seed, argv),
        "conventions": {
            "mu_k": ("P[F_{j1} = ... = F_{jk} = 1] for k DISTINCT block indices; "
                     "unconditional; raw (uncentred) indicators; index set fixed in "
                     "advance, never selected from the sample.  Where mu_J varies with "
                     "J, mu_k denotes the AVERAGE over all C(n_e,k) sets."),
            "F_j": "1{ D_i(etilde^{(j)}) != 0 }, D_i the ML inner decoder",
            "blocks": "B_j = {j*n2, ..., (j+1)*n2 - 1}, j = 0..n_e-1, disjoint",
            "S": "sum_j F_j",
            "m": "delta_e + 1 in the HQC setting; a free parameter here",
            "estimator_correspondence": ("the average over index sets equals "
                                         "E[C(S,m)]/C(n_e,m) identically, with no "
                                         "exchangeability assumption; both are computed "
                                         "and compared."),
            "source": ("BATCH-002 TASK-20260802-15971b a17_characterization.md sec 1 and "
                       "a17_sensitivity.yaml `notation`."),
        },
        "arithmetic": {
            "regime": "exact integers and fractions.Fraction throughout",
            "floating_point_use": ("presentation only: the `float` and `log2` fields "
                                   "beside every `exact` string, plus reported wall-clock "
                                   "seconds and the sampler z-score.  No exact value "
                                   "depends on a float."),
            "float_error_bound": ("`float`: correctly-rounded double of the exact "
                                  "rational, relative error <= 2^-53.  `log2`: one double "
                                  "rounding into [1/2,2) plus one libm log2, absolute "
                                  "error <= ~1e-15 on the mantissa part, exact on the "
                                  "exponent part."),
            "exactness_assertions_in_code": [
                "ExactVectorLaw.check_normalisation (weights sum to the total)",
                "JointFailureLaw.__init__ asserts the weights sum to the total",
                "_xor_convolve asserts the inverse WHT divides exactly and stays >= 0",
                "hqc_shaped_ring_law asserts the convolved counts sum to the total",
            ],
        },
        "results": res["results"],
        "timings_seconds_not_exactly_reproducible": res["timings"],
    }
    text = json.dumps(doc, indent=2, sort_keys=False)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.out} ({len(text)} bytes)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
