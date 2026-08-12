#!/usr/bin/env python3
"""EXP-YIELD-001 driver - exhaustive Semaev m-fold decomposition-yield census.

Contract in force (the PAIR, per the amendment's `precedence` block):
  (1) experiments/EXP-YIELD-001/specification.yaml, frozen v1, committed at
      82327a02bb3041af70566a3f8edfb4468dd2d52d, blob 586914984c4c...
  (2) experiments/EXP-YIELD-001/amendments/v1_to_v2.yaml (AMD-EXP-YIELD-001-V2),
      committed at e7fdadd1..., WHICH GOVERNS WHEREVER THE TWO DIFFER.
Pre-execution review: TASK-20260729-011, PASS with conditions PC-1..PC-4.

INSTRUMENT INDEPENDENCE (v1 `instrument_independence`, re-affirmed by v2
`not_changed`): no Groebner basis, no polynomial system solve, no summation
polynomial, no import of harness/endomorphism_la.py or any part of the
EXP-STR-002 instrument.  Decomposition is decided by MEMBERSHIP IN THE SET OF
FACTOR-BASE m-SUMS, computed in the discrete-logarithm image.

ST-4: THIS DRIVER RECORDS OBSERVATIONS ONLY.  It evaluates no outcome branch of
the amendment's outcome_disposition_table, writes no evidence or decision
record, and states no hypothesis status.

Usage:
    python3 yield_census.py --run <RUN-ID>
    python3 yield_census.py --summarize
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
import traceback
from array import array

import numpy as np

# --------------------------------------------------------------------------
# 0.  Contract constants.  Every one of these is quoted from the committed
#     contract pair; none is invented here.
# --------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-YIELD-001"
HYPOTHESIS_ID = "H-YIELD-001"
TASK_ID = "TASK-20260729-005"
GOAL_ID = "GOAL-ECDLP-001"
BATCH_ID = "BATCH-011"

SPEC_COMMIT = "82327a02bb3041af70566a3f8edfb4468dd2d52d"
SPEC_BLOB = "586914984c4cd00fca16ee91c739b8363dd0fae1"
AMENDMENT_ID = "AMD-EXP-YIELD-001-V2"
AMENDMENT_COMMIT = "e7fdadd120ddcd8a110b592b176231dd0a7fad4d"
REVIEW_TASKS = ["TASK-20260729-003", "TASK-20260729-011"]

FIELD_BITS = (12, 14, 16, 18)
BETA_GRID = tuple(round(0.200 + 0.025 * i, 3) for i in range(17))  # 0.200..0.600
ARITIES = (2, 3)

# v1 replication.seeds - unchanged by v2 (`not_changed`).
MASTER_SEEDS = {
    "RUN-YIELD-001-CENSUS-M2": 110201,
    "RUN-YIELD-001-CENSUS-M3": 110301,
    "RUN-YIELD-001-NULL-UNIFORM-FB": 110401,
    "RUN-YIELD-001-NULL-RANDOM-SUMSET": 110501,
    "RUN-YIELD-001-CALIB-AP": 110601,
    "RUN-YIELD-001-BASELINE-RHO-BSGS": 110701,
}
RUN_IDS = tuple(MASTER_SEEDS)

# Budget: v1 `budget`, unchanged by v2 `not_changed`; card TASK-20260729-005.
WALL_CLOCK_SECONDS_PER_RUN = 900
MAXIMUM_MEMORY_GB = 8
ST1_PROJECTION_CAP = 5 * 10 ** 8          # ST-1 per-cell projected operation cap
EXHAUSTIVE_PROFILE_CAP = 5 * 10 ** 7      # v1 metrics: DETERMINED iff C_all <= this
SAMPLED_PROFILE_DRAWS = 10 ** 6           # v1 metrics: SAMPLED over 10^6 multisets
CTRL_DL_SAMPLES = 10 ** 4                 # CTRL-DL
BASELINE_TARGETS = 16                     # CTRL-BASELINE
RHO_PARTITIONS = 32

# Criterion-evaluable predicate (v2 C-2 rule R-1, on MEASURED B).
H_CAP = 0.5
C_RED_FLOOR = 500

# EV-STR-001 per-cell medians, quoted verbatim from ledger/EV-STR-001.yaml
# via v1 CTRL-CALIB-AP.  n -> m -> median penalty.
EV_STR_001_PENALTY_MEDIAN = {
    211: {3: 17.5, 4: 214.9},
    1009: {3: 41.9, 4: 924.5},
    4099: {3: 87.8, 4: 4128.6},
}
EV_STR_001_SUPPLY_MEDIAN = {
    211: {3: 28, 4: 8},
    1009: {3: 124, 4: 40},
    4099: {3: 477, 4: 154},
}
# v2 C-8 "B DISCLOSURE": the leg FREEZES B = ceil(sqrt(n)) = 15, 32, 65.
CALIB_B = {211: 15, 1009: 32, 4099: 65}
CALIB_D_MAX = 64                          # shift set D = {1..64}
CALIB_SEEDS_PER_CELL = {211: 24, 1009: 6, 4099: 6}   # v2 C-8 (a)

# Student t, two-sided 95 per cent (v2 C-12).
T_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}

SHARED_ROUTINE_NAME = "shared_membership_distinct"


# --------------------------------------------------------------------------
# 1.  The SHARED distinct-count and membership routine (v2 C-8 (b)).
#     The census's primary metric |S_m| and the AP calibration leg's supply
#     count are BOTH produced by this one function object.  PC-1 (the reviewer's
#     operational reading of INV-2a, adopted because no other reading is
#     recorded in any committed record) makes this routine the only thing that
#     can void the census: INV-2a fires iff it disagrees with an independently
#     computed exact value on a known-answer input.
# --------------------------------------------------------------------------

def shared_membership_distinct(keys, universe_size, member_bits=None):
    """Membership-filter `keys` and count the DISTINCT admissible keys.

    keys           : integer array of keys in [0, universe_size)
    universe_size  : size of the key universe
    member_bits    : optional bool array over the universe; a key is admissible
                     iff member_bits[key] is True.  None means "all admissible".

    Returns (mask, n_admissible, n_distinct, occupancy).
    """
    keys = np.asarray(keys, dtype=np.int64).ravel()
    if member_bits is None:
        mask = np.ones(keys.shape, dtype=bool)
    else:
        mask = np.asarray(member_bits, dtype=bool)[keys]
    occ = np.zeros(int(universe_size), dtype=bool)
    adm = keys[mask]
    occ[adm] = True
    return mask, int(adm.size), int(np.count_nonzero(occ)), occ


def known_answer_test_shared_routine():
    """INV-2a known-answer test, in the PC-1 form.

    Each case computes the expected answer in PURE PYTHON with sets and loops -
    a different algorithm from the numpy routine under test - and compares.
    """
    cases = []
    ok = True
    rng = np.random.default_rng(20260729)
    specs = [
        # (universe, keys, member set or None)
        (13, [0, 1, 1, 5, 12, 5], None),
        (13, [0, 1, 1, 5, 12, 5], {1, 5, 7}),
        (1, [0, 0, 0], None),
        (97, list(range(97)) + list(range(97)), set(range(0, 97, 3))),
        (211, [], None),
    ]
    for u in (256, 4099):
        keys = rng.integers(0, u, size=500).tolist()
        memb = set(rng.integers(0, u, size=u // 3).tolist())
        specs.append((u, keys, memb))
    for idx, (u, keys, memb) in enumerate(specs):
        # independent pure-Python expectation
        if memb is None:
            adm_exp = list(keys)
        else:
            adm_exp = [k for k in keys if k in memb]
        n_adm_exp = len(adm_exp)
        seen = set()
        for k in adm_exp:
            seen.add(k)
        n_dis_exp = len(seen)
        mask_exp = [(memb is None) or (k in memb) for k in keys]
        bits = None
        if memb is not None:
            bits = np.zeros(u, dtype=bool)
            for k in memb:
                bits[k] = True
        mask, n_adm, n_dis, occ = shared_membership_distinct(keys, u, bits)
        agree = (
            n_adm == n_adm_exp
            and n_dis == n_dis_exp
            and mask.tolist() == mask_exp
            and int(np.count_nonzero(occ)) == n_dis_exp
        )
        ok = ok and agree
        cases.append({
            "case": idx,
            "universe": u,
            "n_keys": len(keys),
            "membership_filtered": memb is not None,
            "expected_n_admissible": n_adm_exp,
            "returned_n_admissible": n_adm,
            "expected_n_distinct": n_dis_exp,
            "returned_n_distinct": n_dis,
            "agree": bool(agree),
        })
    return {
        "control": "INV-2a known-answer test of the shared distinct-count and "
                   "membership routine",
        "routine": SHARED_ROUTINE_NAME,
        "reading_applied": "PC-1 (TASK-20260729-011): INV-2a fires if and only if "
                           "the routine shared by the AP calibration leg and the "
                           "census disagrees with an independently computed exact "
                           "value on a known-answer input.",
        "n_cases": len(cases),
        "all_agree": bool(ok),
        "INV_2a_fired": (not ok),
        "cases": cases,
    }


# --------------------------------------------------------------------------
# 2.  Elementary number theory and curve arithmetic (pure Python / numpy;
#     no external algebra system, no polynomial solver).
# --------------------------------------------------------------------------

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in _MR_BASES:
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime_at_or_above(x: int) -> int:
    n = int(x)
    while not is_prime(n):
        n += 1
    return n


def qr_bits(p: int) -> np.ndarray:
    ys = np.arange((p + 1) // 2, dtype=np.int64)
    sq = np.zeros(p, dtype=bool)
    sq[(ys * ys) % p] = True
    return sq


def rhs_values(p: int, a: int, b: int, xs: np.ndarray) -> np.ndarray:
    return ((xs * xs % p) * xs + a * xs + b) % p


def curve_order(p: int, a: int, b: int, sq: np.ndarray, xs: np.ndarray) -> int:
    v = rhs_values(p, a, b, xs)
    zero = v == 0
    return 1 + int(np.count_nonzero(zero)) + 2 * int(np.count_nonzero(sq[v] & ~zero))


def tonelli(v: int, p: int) -> int:
    if v == 0:
        return 0
    if p % 4 == 3:
        return pow(v, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(v, q, p), pow(v, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        bb = pow(c, 1 << (m - i - 1), p)
        m, c = i, bb * bb % p
        t = t * c % p
        r = r * bb % p
    return r


def select_curve(p: int):
    """v1 inputs.curve_selection_rule, implemented verbatim.

    t = 1, 2, 3, ...;  a from 0 to t with b = t - a;  skip 4a^3+27b^2 == 0 mod p;
    skip a = 0 and b = 0;  take the FIRST curve whose order N is prime and != p.
    """
    sq = qr_bits(p)
    xs = np.arange(p, dtype=np.int64)
    tried = 0
    t = 1
    while True:
        for a in range(0, t + 1):
            b = t - a
            if a == 0 or b == 0:
                continue
            if (4 * a * a * a + 27 * b * b) % p == 0:
                continue
            tried += 1
            N = curve_order(p, a, b, sq, xs)
            if N != p and is_prime(N):
                return {"a": a, "b": b, "N": N, "candidates_tried": tried,
                        "t_reached": t}
        t += 1
        if t > 4000:
            raise RuntimeError("curve selection exhausted t <= 4000 at p=%d" % p)


def ec_add(P, Q, a, p):
    """Affine short-Weierstrass addition; None is the point at infinity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_neg(P, p):
    return None if P is None else (P[0], (p - P[1]) % p)


def ec_mul_double_and_add(k: int, P, a: int, p: int):
    """Independent scalar multiplication, used ONLY to re-verify discrete-log
    certificates.  It shares no code with the rho walk or with BSGS."""
    R = None
    Q = P
    k = int(k)
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R


def find_generator(p: int, a: int, b: int):
    """v1 inputs.generator: smallest x admitting a point, smaller of the two y."""
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            return (x, 0)
        if pow(v, (p - 1) // 2, p) == 1:
            y = tonelli(v, p)
            return (x, min(y, p - y))
    raise RuntimeError("no point found on curve")


# --------------------------------------------------------------------------
# 3.  Per-field instance: prime, curve, generator, discrete-log table.
# --------------------------------------------------------------------------

class Instance:
    def __init__(self, k: int, log=print):
        t0 = time.time()
        self.k = k
        self.p = next_prime_at_or_above(2 ** k)
        cur = select_curve(self.p)
        self.a, self.b, self.N = cur["a"], cur["b"], cur["N"]
        self.curve_search = cur
        self.G = find_generator(self.p, self.a, self.b)
        self.dl_table_point_additions = self.N - 1
        self._build_dl_table()
        self.setup_seconds = time.time() - t0
        log("  instance k=%d: p=%d curve y^2=x^3+%dx+%d N=%d G=%s "
            "(prime N: %s, N!=p: %s, N!=p+1 [ordinary]: %s) setup %.2fs"
            % (k, self.p, self.a, self.b, self.N, self.G, is_prime(self.N),
               self.N != self.p, self.N != self.p + 1, self.setup_seconds))

    def _build_dl_table(self):
        """v1 inputs.computation_domain.  Walk N multiples of G; store, for each
        x admitting a point, the discrete log of the CANONICAL point
        (x, min(y, p-y)).  The other point on that x is its negative."""
        p, a, N = self.p, self.a, self.N
        gx, gy = self.G
        dl = array('q', [-1]) * p
        x, y = gx, gy
        dl[x] = 1
        for i in range(2, N):
            if x == gx:
                lam = (3 * x * x + a) * pow(2 * y, -1, p) % p
            else:
                lam = (y - gy) * pow(x - gx, -1, p) % p
            x2 = (lam * lam - x - gx) % p
            y2 = (lam * (x - x2) - y) % p
            x, y = x2, y2
            if y <= p - y:
                dl[x] = i
        # closure check: (N-1)G must equal -G
        self.dl_closure_ok = (x == gx and y == (p - gy) % p)
        self.dl_can = np.frombuffer(dl, dtype=np.int64).copy()
        self.has_point = self.dl_can >= 0
        self.n_x_with_point = int(np.count_nonzero(self.has_point))
        # 2 * (#x with a point) must be N-1 because N is odd (no 2-torsion, no
        # x for the identity)
        self.dl_count_ok = (2 * self.n_x_with_point == self.N - 1)

    def factor_base(self, beta: float):
        """v1 inputs.factor_base:  F = {P : x(P) in {0..L-1}}, L = round(p^beta).
        B = |F| is COUNTED.  Returned in the discrete-log image."""
        L = int(round(self.p ** beta))
        xs = np.flatnonzero(self.has_point[:L])
        d = self.dl_can[xs]
        F = np.concatenate([d, self.N - d]).astype(np.int64)
        return L, F

    def random_negation_closed_fb(self, B: int, rng):
        """CTRL-NULL-FB: uniformly random negation-closed subset of G of the
        IDENTICAL measured size B, on the IDENTICAL curve."""
        half = (self.N - 1) // 2
        idx = rng.choice(half, size=B // 2, replace=False) + 1
        return np.concatenate([idx, self.N - idx]).astype(np.int64)


# --------------------------------------------------------------------------
# 4.  Cell-level quantities.
# --------------------------------------------------------------------------

def c_red(B: int, m: int) -> int:
    """v1 conventions_fixed.repeated_elements_and_cancellation:
       C_red = sum_{k=1..m} C(B/2,k) C(m-1,k-1) 2^k."""
    if B % 2 != 0:
        raise ValueError("measured B must be even (INV-1, v2 C-4): got %d" % B)
    h = B // 2
    tot = 0
    for kk in range(1, m + 1):
        tot += math.comb(h, kk) * math.comb(m - 1, kk - 1) * (2 ** kk)
    return tot


def occupancy_prediction(N: int, cred: int, s_prev: int) -> float:
    """v1 conventions_fixed.occupancy_prediction:
       P_pred = N(1-exp(-C_red/N)) + |S_(m-2)| exp(-C_red/N)."""
    e = math.exp(-cred / N)
    return N * (1.0 - e) + s_prev * e


def multiset_factor(B: int, m: int) -> float:
    """prod_{j=0}^{m-1} (1 + j/B)"""
    out = 1.0
    for j in range(m):
        out *= (1.0 + j / B)
    return out


def wilson_interval(successes: int, n: int, z: float = 1.959963985):
    ph = successes / n
    den = 1.0 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - hw), min(1.0, c + hw))


def classify_cell(B: int, m: int, p: int) -> dict:
    """v2 C-2 rule R-1: criterion-evaluable iff h <= 0.5 AND C_red >= 500,
    both AT MEASURED B.  R-2: this is computed from B ALONE and is frozen
    BEFORE S_m exists."""
    h = B ** m / (math.factorial(m) * p)
    cred = c_red(B, m) if B >= 2 else 0
    return {
        "h": h,
        "C_red": cred,
        "evaluable": bool(h <= H_CAP and cred >= C_RED_FLOOR),
    }


def distinct_sumset(occ_src: np.ndarray, F: np.ndarray, N: int) -> np.ndarray:
    """THE one sumset code path, used identically by the census arm and by the
    CTRL-NULL-FB arm (E5).  Returns the occupancy bitmap of occ_src + F."""
    dst = np.zeros(N, dtype=bool)
    for f in F:
        f = int(f)
        if f == 0:
            dst |= occ_src
        else:
            dst[f:] |= occ_src[:N - f]
            dst[:f] |= occ_src[N - f:]
    return dst


def sum_set_chain(F: np.ndarray, N: int, m: int):
    """|S_1| .. |S_m| through the shared distinct-count routine."""
    occ = np.zeros(N, dtype=bool)
    occ[F] = True
    sizes = []
    _, _, n1, _ = shared_membership_distinct(np.flatnonzero(occ), N)
    sizes.append(n1)
    cur = occ
    for _ in range(m - 1):
        cur = distinct_sumset(cur, F, N)
        _, _, nd, _ = shared_membership_distinct(np.flatnonzero(cur), N)
        sizes.append(nd)
    return sizes, cur


def identity_multiset_count(F: np.ndarray, N: int, m: int) -> dict:
    """Exact number of m-multisets from F summing to the identity, by Burnside.
       m=2: (O2 + C1)/2 with C1 = #{f : 2f = 0}
       m=3: (O3 + 3*C2 + 2*C3)/6 with C2 = #{f : -2f in F}, C3 = #{f : 3f = 0}
    Membership tests are routed through the shared routine."""
    memb = np.zeros(N, dtype=bool)
    memb[F] = True
    if m == 2:
        keys = (N - F) % N
        _, o2, _, _ = shared_membership_distinct(keys, N, memb)
        c1 = int(np.count_nonzero((2 * F) % N == 0))
        return {"count": (o2 + c1) // 2, "O": o2, "fix2": c1, "fix3": 0,
                "exact": True}
    o3 = 0
    B = int(F.size)
    step = max(1, 1 + (2 ** 21) // max(B, 1))
    for lo in range(0, B, step):
        blk = F[lo:lo + step]
        keys = ((N - (blk[:, None] + F[None, :])) % N).ravel()
        _, cnt, _, _ = shared_membership_distinct(keys, N, memb)
        o3 += cnt
    keys = (N - 2 * F) % N
    _, c2, _, _ = shared_membership_distinct(keys, N, memb)
    c3 = int(np.count_nonzero((3 * F) % N == 0))
    return {"count": (o3 + 3 * c2 + 2 * c3) // 6, "O": o3, "fix2": c2,
            "fix3": c3, "exact": True}


def _pair_index_arrays(B: int):
    lengths = B - np.arange(B, dtype=np.int64)
    starts = np.concatenate([[0], np.cumsum(lengths)[:-1]]).astype(np.int64)
    total = int(lengths.sum())
    j = np.repeat(np.arange(B, dtype=np.int64), lengths)
    k = np.arange(total, dtype=np.int64) - np.repeat(starts, lengths) + j
    return j, k, starts, total


def exhaustive_profile(F: np.ndarray, N: int, m: int):
    """CTRL-COLLISION-ACCOUNTING, DETERMINED branch.  Returns the exact bucket
    count vector over Z/N for every m-multiset from F."""
    B = int(F.size)
    j, kk, starts, _ = _pair_index_arrays(B)
    PS = (F[j] + F[kk]) % N
    if m == 2:
        return np.bincount(PS, minlength=N).astype(np.int64)
    cnt = np.zeros(N, dtype=np.int64)
    buf = []
    buflen = 0
    for i in range(B):
        seg = (PS[starts[i]:] + int(F[i])) % N
        buf.append(seg)
        buflen += seg.size
        if buflen >= 4_000_000:
            cnt += np.bincount(np.concatenate(buf), minlength=N)
            buf, buflen = [], 0
    if buf:
        cnt += np.bincount(np.concatenate(buf), minlength=N)
    return cnt


def profile_stats(cnt: np.ndarray, c_all: int, s_m: int) -> dict:
    nz = cnt[cnt > 0]
    loads, hist = np.unique(nz, return_counts=True)
    total_sq = int(np.sum(cnt.astype(np.int64) * cnt.astype(np.int64)))
    keep = min(24, loads.size)
    return {
        "label": "DETERMINED",
        "max_load": int(cnt.max()),
        "occupied_buckets": int(nz.size),
        "sum_of_counts": int(cnt.sum()),
        "sum_of_counts_equals_C_all": bool(int(cnt.sum()) == c_all),
        "occupied_equals_S_m": bool(int(nz.size) == s_m),
        "mean_load_over_occupied": float(cnt.sum() / nz.size) if nz.size else 0.0,
        "size_biased_mean_load": float(total_sq / c_all) if c_all else 0.0,
        "collision_probability": float(total_sq / (c_all * c_all)) if c_all else 0.0,
        "load_histogram_head": {int(l): int(h) for l, h in
                                zip(loads[:keep], hist[:keep])},
        "load_histogram_truncated_at": int(loads[keep - 1]) if loads.size else 0,
        "n_distinct_loads": int(loads.size),
    }


def sampled_profile(F: np.ndarray, N: int, m: int, c_all: int, rng,
                    n_draws: int = SAMPLED_PROFILE_DRAWS) -> dict:
    """CTRL-COLLISION-ACCOUNTING, SAMPLED branch, and the estimator that
    CTRL-EXHAUSTIVE-TRUTH compares against the exhaustive value.

    DECLARED ESTIMATOR DEFINITION (the contract names the sample size but not
    the statistic).  From n uniform m-multisets we estimate
      rho = P(two independent uniform multisets have the same sum)
          = sum_t (c_t / C_all)^2
    by the unbiased  rho_hat = (sum_t s_t (s_t-1) / 2) / C(n,2),  where s_t are
    the SAMPLE bucket counts; the size-biased mean load is mu = rho * C_all.
    The standard error is the block standard error over 10 equal blocks.
    The sample maximum load is reported as a SAMPLE STATISTIC and is NOT an
    estimate of the true maximum load."""
    B = int(F.size)
    U = B + m - 1
    rows = []
    need = n_draws
    while need > 0:
        cand = rng.integers(0, U, size=(int(need * 1.15) + 16, m))
        cand.sort(axis=1)
        good = np.ones(cand.shape[0], dtype=bool)
        for r in range(1, m):
            good &= cand[:, r] > cand[:, r - 1]
        cand = cand[good][:need]
        rows.append(cand)
        need -= cand.shape[0]
    idx = np.concatenate(rows) - np.arange(m, dtype=np.int64)[None, :]
    sums = np.zeros(idx.shape[0], dtype=np.int64)
    for r in range(m):
        sums += F[idx[:, r]]
    sums %= N
    n = int(sums.size)
    blocks = 10
    bs = n // blocks
    est = []
    for bi in range(blocks):
        sb = sums[bi * bs:(bi + 1) * bs]
        c = np.bincount(sb, minlength=N)
        pairs = int(np.sum(c.astype(np.int64) * (c.astype(np.int64) - 1)) // 2)
        est.append(pairs / (bs * (bs - 1) / 2))
    c_full = np.bincount(sums, minlength=N)
    pairs_full = int(np.sum(c_full.astype(np.int64) * (c_full.astype(np.int64) - 1)) // 2)
    rho = pairs_full / (n * (n - 1) / 2)
    se = float(np.std(est, ddof=1) / math.sqrt(blocks))
    return {
        "label": "SAMPLED",
        "n_draws": n,
        "blocks": blocks,
        "collision_probability_hat": float(rho),
        "collision_probability_se": se,
        "size_biased_mean_load_hat": float(rho * c_all),
        "size_biased_mean_load_se": float(se * c_all),
        "sample_max_load": int(c_full.max()),
        "sample_max_load_note": "SAMPLE STATISTIC over the drawn multisets; NOT "
                                "an estimate of the true maximum load.",
        "sample_distinct_sums": int(np.count_nonzero(c_full)),
    }


def census_cell(inst: Instance, beta: float, m: int, F: np.ndarray, L: int,
                cls: dict, rng, want_profile: bool, log=print) -> dict:
    """One census cell.  `cls` is the class computed from measured B BEFORE this
    function is called (v2 C-2 rule R-2)."""
    p, N = inst.p, inst.N
    B = int(F.size)
    t0 = time.time()
    c_all = math.comb(B + m - 1, m)
    c_bm = math.comb(B, m) if B >= m else 0
    cred = cls["C_red"]
    h = cls["h"]
    h_alt = B ** m / (math.factorial(m) * N)

    sizes, occ_m = sum_set_chain(F, N, m)
    s_m = sizes[-1]
    s_prev = 1 if m == 2 else sizes[m - 3]   # |S_0| = 1 ; |S_1| = B
    p_pred = occupancy_prediction(N, cred, s_prev)

    R = (s_m / N) / h
    R_max = (p / N) * multiset_factor(B, m)
    E = s_m / p_pred
    E_max = min(c_all, N) / p_pred
    E_floor = min(N, m * B - m + 1) / p_pred
    lo, hi = wilson_interval(s_m, N)

    ident = identity_multiset_count(F, N, m)

    prof = None
    if want_profile:
        if m == 2 or c_all <= EXHAUSTIVE_PROFILE_CAP:
            cnt = exhaustive_profile(F, N, m)
            prof = profile_stats(cnt, c_all, s_m)
            prof["identity_bucket_count"] = int(cnt[0])
            prof["identity_bucket_matches_burnside"] = bool(int(cnt[0]) == ident["count"])
            del cnt
        else:
            prof = sampled_profile(F, N, m, c_all, rng)

    # INV-1 checks (v1 INV-1 as amended by v2 C-5 and C-6)
    inv1 = {
        "R_exceeds_R_max": bool(R > R_max * (1 + 1e-12)),
        "S_m_exceeds_min_C_all_N": bool(s_m > min(c_all, N)),
        "S_m_below_S_m_minus_2": bool(s_m < s_prev),
        "cauchy_davenport_violation": bool(s_m < min(N, m * B - m + 1)),
        "C_red_odd": bool(cred % 2 != 0),
    }
    inv1["fired"] = any(inv1.values())

    cell = {
        "k": inst.k, "p": p, "N": N, "beta": beta, "m": m,
        "L": L, "B": B, "B_over_L": B / L if L else None,
        "p_over_N": p / N,
        "C_all": c_all, "C_B_m": c_bm, "C_red": cred,
        "multiset_factor_prod_1_plus_j_over_B": multiset_factor(B, m),
        "C_all_times_m_fact_over_B_pow_m": c_all * math.factorial(m) / B ** m,
        "h_heuristic_B_m_over_m_fact_p": h,
        "h_alt_B_m_over_m_fact_N": h_alt,
        "S_sizes_1_to_m": sizes,
        "S_m": s_m, "S_m_minus_2": s_prev,
        "S_m_over_N": s_m / N,
        "S_m_over_N_wilson_95": [lo, hi],
        "P_pred": p_pred,
        "PM2_R": R, "R_max": R_max,
        "PM3_E": E, "E_max": E_max, "E_floor": E_floor,
        "band_one_sided_high_E_max_below_1_10": bool(E_max < 1.10),
        "band_one_sided_low_E_floor_above_0_90": bool(E_floor > 0.90),
        "identity_multisets": ident,
        "collision_profile": prof,
        "label_PM1_PM2_PM3": "DETERMINED",
        "INV_1": inv1,
        "seconds": time.time() - t0,
        "modular_additions_contract_model": (B * B if m == 2
                                             else B * B + sizes[1] * B),
    }
    return cell


# --------------------------------------------------------------------------
# 5.  Controls that are not per-cell.
# --------------------------------------------------------------------------

def ctrl_dl(inst: Instance, m: int, rng, n_samples: int = CTRL_DL_SAMPLES) -> dict:
    """CTRL-DL.  Draw n random m-multisets from a mid-grid factor base, sum both
    on the curve by explicit point addition and in the DL image by modular
    addition, and require exact agreement on all of them.  INV-3."""
    L, F = inst.factor_base(0.500)
    B = int(F.size)
    p, a, N = inst.p, inst.a, inst.N
    # affine points of the factor base, keyed by their discrete log
    xs = np.flatnonzero(inst.has_point[:L])
    pt_by_dl = {}
    for x in xs:
        x = int(x)
        v = (x * x * x + inst.a * x + inst.b) % p
        y = tonelli(v, p)
        y = min(y, p - y)
        d = int(inst.dl_can[x])
        pt_by_dl[d] = (x, y)
        pt_by_dl[N - d] = (x, (p - y) % p)
    idx = rng.integers(0, B, size=(n_samples, m))
    mism = 0
    first_bad = None
    for row in idx:
        dls = [int(F[int(t)]) for t in row]
        # curve side: explicit point addition
        P = None
        for d in dls:
            P = ec_add(P, pt_by_dl[d], a, p)
        # discrete-log image side: modular addition
        s = sum(dls) % N
        if s == 0:
            ok = P is None
            d_of_P = 0 if P is None else None
        elif P is None:
            ok = False
            d_of_P = 0
        else:
            dcan = int(inst.dl_can[P[0]])
            d_of_P = dcan if P[1] <= p - P[1] else (N - dcan) % N
            ok = (d_of_P == s)
        if not ok:
            mism += 1
            if first_bad is None:
                first_bad = {"dls": dls, "dl_image_sum": s,
                             "curve_point": P, "dl_of_curve_point": d_of_P}
    return {
        "control": "CTRL-DL",
        "k": inst.k, "m": m, "beta_used": 0.500, "B": B,
        "samples": n_samples,
        "mismatches": mism,
        "first_mismatch": first_bad,
        "dl_walk_closure_ok": bool(inst.dl_closure_ok),
        "dl_point_count_ok_2x_plus_1_equals_N": bool(inst.dl_count_ok),
        "INV_3_fired": bool(mism > 0 or not inst.dl_closure_ok
                            or not inst.dl_count_ok),
    }


def occupancy_null(N: int, cred: int, replicates: int, rng, antipodal: bool):
    """CTRL-NULL-SUMSET.
    antipodal=True  : v2 C-4 - repeat C_red/2 times, draw g and insert BOTH
                      g and -g (the process that feeds INV-4, both tail checks
                      and the standardized bulk check).
    antipodal=False : the v1 independent-throw process, retained by v2 C-4 as a
                      DECLARED CONTRAST ARM, measured and archived here so the
                      variance factor is never imported from an unarchived probe.
    """
    vals = np.empty(replicates, dtype=np.float64)
    for r in range(replicates):
        if antipodal:
            g = rng.integers(0, N, size=cred // 2)
            occ = np.zeros(N, dtype=bool)
            occ[g] = True
            occ[(N - g) % N] = True
        else:
            g = rng.integers(0, N, size=cred)
            occ = np.zeros(N, dtype=bool)
            occ[g] = True
        vals[r] = int(np.count_nonzero(occ))
    return vals


def replicate_count(cred: int) -> int:
    """v2 C-14."""
    if cred <= 10 ** 4:
        return 100
    if cred <= 10 ** 6:
        return 30
    return 10


def fb_null_draws(B: int) -> int:
    """v2 C-13: 10 draws where measured B <= 64, 3 elsewhere."""
    return 10 if B <= 64 else 3


def derive_seed(master: int, *parts) -> int:
    s = "|".join([str(master)] + [str(x) for x in parts])
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


# --------------------------------------------------------------------------
# 6.  Matched baselines (CTRL-BASELINE).
# --------------------------------------------------------------------------

def bsgs(target, G, a, p, N):
    """Baby-step giant-step.  Returns (d, group_operations, stored_elements)."""
    mm = int(math.isqrt(N - 1)) + 1
    ops = 0
    table = {}
    P = None
    for j in range(mm):
        key = None if P is None else (P[0], P[1])
        if key not in table:
            table[key] = j
        P = ec_add(P, G, a, p)
        ops += 1
    # mG computed by the same repeated-addition already done: P == mm*G
    mG = P
    negmG = ec_neg(mG, p)
    Q = target
    for i in range(mm + 1):
        key = None if Q is None else (Q[0], Q[1])
        if key in table:
            d = (i * mm + table[key]) % N
            return d, ops, len(table)
        Q = ec_add(Q, negmG, a, p)
        ops += 1
    return None, ops, len(table)


def rho_negation(target, G, a, p, N, rng, r=RHO_PARTITIONS):
    """Pollard rho with the negation map.  Returns (d, walk_steps, setup_ops,
    escapes, restarts).  walk_steps is the quantity comparable with the model
    position 0.886 sqrt(N); setup_ops is the cost of building the r step
    points and is reported separately rather than folded in."""
    setup_ops = 0
    steps_total = 0
    escapes = 0
    restarts = 0
    # step points M_i = alpha_i G + beta_i T
    alphas = [int(rng.integers(1, N)) for _ in range(r)]
    betas = [int(rng.integers(1, N)) for _ in range(r)]
    Ms = []
    for i in range(r):
        A = ec_mul_double_and_add(alphas[i], G, a, p)
        setup_ops += 2 * alphas[i].bit_length()
        Bp = ec_mul_double_and_add(betas[i], target, a, p)
        setup_ops += 2 * betas[i].bit_length()
        Ms.append(ec_add(A, Bp, a, p))
        setup_ops += 1

    def canon(P, u, v):
        if P is None:
            return None, u % N, v % N
        if P[1] <= p - P[1]:
            return P, u % N, v % N
        return (P[0], (p - P[1]) % p), (-u) % N, (-v) % N

    for _ in range(64):   # restart budget
        seen = {}
        u = int(rng.integers(1, N))
        v = int(rng.integers(1, N))
        P = ec_add(ec_mul_double_and_add(u, G, a, p),
                   ec_mul_double_and_add(v, target, a, p), a, p)
        setup_ops += 2 * (u.bit_length() + v.bit_length()) + 1
        P, u, v = canon(P, u, v)
        prev2 = None
        for _step in range(40 * int(math.isqrt(N)) + 1000):
            if P is None and v % N != 0:
                d = (-u) * pow(v % N, -1, N) % N
                return d, steps_total, setup_ops, escapes, restarts
            key = None if P is None else P[0]
            if key in seen:
                u2, v2 = seen[key]
                dv = (v - v2) % N
                if dv != 0:
                    d = (u2 - u) * pow(dv, -1, N) % N
                    return d, steps_total, setup_ops, escapes, restarts
                # useless collision: escape by doubling
                P = ec_add(P, P, a, p)
                u, v = (2 * u) % N, (2 * v) % N
                P, u, v = canon(P, u, v)
                steps_total += 1
                escapes += 1
                continue
            seen[key] = (u, v)
            i = (key if key is not None else 0) % r
            P2 = ec_add(P, Ms[i], a, p)
            u2 = (u + alphas[i]) % N
            v2 = (v + betas[i]) % N
            steps_total += 1
            P2, u2, v2 = canon(P2, u2, v2)
            if prev2 is not None and P2 is not None and prev2 == P2[0]:
                # fruitless 2-cycle: escape by doubling
                P2 = ec_add(P2, P2, a, p)
                u2, v2 = (2 * u2) % N, (2 * v2) % N
                P2, u2, v2 = canon(P2, u2, v2)
                steps_total += 1
                escapes += 1
            prev2 = None if P is None else P[0]
            P, u, v = P2, u2, v2
        restarts += 1
    return None, steps_total, setup_ops, escapes, restarts


# --------------------------------------------------------------------------
# 7.  Provenance / environment capture.
# --------------------------------------------------------------------------

def _git(repo, *args):
    try:
        return subprocess.run(["git", "-C", repo] + list(args),
                              capture_output=True, text=True, timeout=120).stdout
    except Exception as exc:                                # pragma: no cover
        return "ERROR: %r" % (exc,)


def git_state(repo: str) -> dict:
    head = _git(repo, "rev-parse", "HEAD").strip()
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    porcelain = _git(repo, "status", "--porcelain")
    lines = [l for l in porcelain.splitlines() if l.strip()]
    by_code = {}
    for l in lines:
        by_code[l[:2]] = by_code.get(l[:2], 0) + 1
    in_scope = [l for l in lines if "EXP-YIELD-001" in l]
    return {
        "commit": head,
        "branch": branch,
        "dirty": bool(lines),
        "dirty_entry_count": len(lines),
        "dirty_entries_by_status_code": by_code,
        "dirty_entries_touching_EXP_YIELD_001": in_scope,
        "porcelain_sha256": hashlib.sha256(porcelain.encode()).hexdigest(),
        "dirty_tree_note": (
            "The worktree was ALREADY DIRTY when this task began, from macOS "
            "AppleDouble sidecar deletions under experiments/EXP-SIG-008 and "
            "other paths outside this task's write_scope. They were NOT touched. "
            "No file outside experiments/EXP-YIELD-001/{driver,runs,results} was "
            "written by this driver."),
        "spec_blob_at_frozen_commit": _git(
            repo, "rev-parse", "%s:experiments/EXP-YIELD-001/specification.yaml"
            % SPEC_COMMIT).strip(),
        "spec_blob_in_worktree": hashlib.sha1(
            b"blob " + str(os.path.getsize(os.path.join(
                repo, "experiments/EXP-YIELD-001/specification.yaml"))).encode()
            + b"\0" + open(os.path.join(
                repo, "experiments/EXP-YIELD-001/specification.yaml"), "rb").read()
        ).hexdigest(),
    }


def environment_block(repo: str, driver_path: str) -> dict:
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "dependency_versions": {"numpy": np.__version__},
        "dependencies_note": "numpy is the only third-party dependency. No "
                             "computer-algebra system, no Groebner engine, no "
                             "summation-polynomial code, and nothing from "
                             "harness/ or tools/ is imported.",
        "driver_sha256": hashlib.sha256(open(driver_path, "rb").read()).hexdigest(),
        "driver_path": os.path.relpath(driver_path, repo),
        "rlimit_as_set_bytes": _RLIMIT_STATE.get("set"),
        "rlimit_as_status": _RLIMIT_STATE.get("status"),
        "randomness_sources": [
            "numpy.random.default_rng(seed) [PCG64] - every stochastic quantity "
            "in this package; seeds are the contract's master seeds and "
            "SHA-256 derivations from them, all recorded in the manifest.",
            "No other source of randomness is used. Set iteration order, dict "
            "order and hash randomisation do not enter any reported number.",
        ],
    }


def inference_block() -> dict:
    return {
        "requested_policy": "executor-implementation",
        "requested_policy_source": "TASK-20260729-005 handoff.inference.policy",
        "policy_resolution_command": "python3 -m orchestration.adapter resolve --role executor",
        "policy_resolution_output": "executor-implementation -> anthropic:claude-sonnet-5 (effort=medium)",
        "backend_env_AUTORESEARCH_BACKEND": os.environ.get("AUTORESEARCH_BACKEND"),
        "policy_env_AUTORESEARCH_POLICY": os.environ.get("AUTORESEARCH_POLICY"),
        "resolved_runtime_model_id": "claude-opus-5",
        "resolved_runtime_model_id_source": "self-reported by the Claude Code runtime session; NOT probe-verified",
        "model_verified": False,
        "model_verification_attempt": (
            "python3 -m orchestration.adapter doctor --probe was RUN in this "
            "session and could verify nothing: $ANTHROPIC_API_KEY unset "
            "(backend unusable); fireworks/openai model-listing probes failed "
            "with SSL CERTIFICATE_VERIFY_FAILED; local backend refused "
            "connection. Recorded as an unverified identifier, not asserted."),
        "fallback_used": False,
        "fallback_allowed": False,
        "degraded_requirements": [],
        "reasoning_effort": None,
        "policy_binding_mismatch": (
            "DISCLOSED, NOT SILENTLY SUBSTITUTED. The handoff requests policy "
            "`executor-implementation`, which orchestration/adapter resolves to "
            "anthropic:claude-sonnet-5 at effort=medium. This session was NOT "
            "launched with that resolved environment (AUTORESEARCH_POLICY and "
            "AUTORESEARCH_BACKEND are unset) and reports itself as claude-opus-5. "
            "This is a process-level per-role model-selection gap of the kind "
            "CLAUDE.md's model policy note describes, NOT a backend fallback. "
            "It is recorded here rather than resolved by the Executor."),
        "independent_session_required": False,
    }


_RLIMIT_STATE = {}


def apply_memory_cap(gb: int):
    want = gb * 1024 ** 3
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        new_hard = hard if hard != resource.RLIM_INFINITY and hard < want else hard
        resource.setrlimit(resource.RLIMIT_AS, (want, new_hard))
        _RLIMIT_STATE["set"] = want
        _RLIMIT_STATE["status"] = "RLIMIT_AS set to %d bytes" % want
    except Exception as exc:
        _RLIMIT_STATE["set"] = None
        _RLIMIT_STATE["status"] = (
            "RLIMIT_AS could not be set on this host (%r); the 8 GB cap is "
            "enforced by measurement (ru_maxrss recorded per run) and by the "
            "design's peak footprint of one N-bit set plus the DL table, "
            "which is under 100 MB at k=18." % (exc,))


class Tee:
    def __init__(self, stream, fh):
        self.stream, self.fh = stream, fh

    def write(self, s):
        self.stream.write(s)
        self.fh.write(s)
        self.fh.flush()
        return len(s)

    def flush(self):
        self.stream.flush()
        self.fh.flush()


# --------------------------------------------------------------------------
# 8.  The six runs.
# --------------------------------------------------------------------------

def run_census(run_id: str, m: int, ctx) -> dict:
    log = ctx["log"]
    master = MASTER_SEEDS[run_id]
    rng = np.random.default_rng(master)
    out = {"arm": "census", "m": m, "master_seed": master,
           "classification_first_note":
               "v2 C-2 rule R-2 ORDER OF OPERATIONS. Every cell's class is "
               "computed from MEASURED B ALONE and frozen below BEFORE any sum "
               "set is computed, so no class is a function of an outcome.",
           "instances": [], "classification": [], "cells": [],
           "controls": [], "skipped_cells": []}

    # --- pass 1: measure B and freeze the class for all 68 cells of this arity
    for k in FIELD_BITS:
        inst = ctx["instance"](k)
        out["instances"].append(instance_record(inst))
        for beta in BETA_GRID:
            L, F = inst.factor_base(beta)
            B = int(F.size)
            cls = classify_cell(B, m, inst.p)
            L_basis = int(round(2 ** (k * beta)))
            h_L = L_basis ** m / (math.factorial(m) * 2 ** k)
            cred_L = (L_basis ** 2 / 2 if m == 2 else
                      L_basis + L_basis * (L_basis - 2)
                      + L_basis * (L_basis - 2) * (L_basis - 4) / 6)
            ev_L = bool(h_L <= H_CAP and cred_L >= C_RED_FLOOR)
            out["classification"].append({
                "k": k, "beta": beta, "m": m, "L": L, "B": B,
                "B_over_L": B / L if L else None,
                "h_on_measured_B": cls["h"], "C_red_on_measured_B": cls["C_red"],
                "evaluable_on_measured_B": cls["evaluable"],
                "L_on_B_equals_L_basis_2_to_k_beta": L_basis,
                "h_on_B_equals_L": h_L, "C_red_on_B_equals_L": cred_L,
                "evaluable_on_B_equals_L": ev_L,
                "class_changed_on_measurement": bool(cls["evaluable"] != ev_L),
            })
    log("  [pass 1] class frozen for %d cells from measured B, before any sum set"
        % len(out["classification"]))

    # --- pass 2: the census itself, in the contract's cell_priority_order
    order = sorted(
        out["classification"],
        key=lambda c: (0 if c["evaluable_on_measured_B"] else
                       (1 if c["h_on_measured_B"] <= 1.0 else 2),
                       c["k"], c["beta"]))
    for rec in order:
        if ctx["deadline_passed"]():
            out["skipped_cells"].append({
                "k": rec["k"], "beta": rec["beta"], "m": m,
                "reason": "ST-2 RUN CAP: wall-clock deadline reached before this "
                          "cell was started. NOT a measurement."})
            continue
        inst = ctx["instance"](rec["k"])
        L, F = inst.factor_base(rec["beta"])
        B = int(F.size)
        if B < 2:
            out["skipped_cells"].append({
                "k": rec["k"], "beta": rec["beta"], "m": m, "B": B, "L": L,
                "reason": "DEGENERATE CELL: measured B < 2, so the factor base "
                          "carries no antipodal pair and the per-cell ratios are "
                          "undefined. Recorded as an observation; no criterion is "
                          "evaluated at it (it is not criterion-evaluable)."})
            continue
        proj = (B * B if m == 2 else
                (B + min(B * B // 2, inst.N)) * B)
        if proj > ST1_PROJECTION_CAP:
            out["skipped_cells"].append({
                "k": rec["k"], "beta": rec["beta"], "m": m, "B": B,
                "projected_operations": proj,
                "reason": "ST-1 PER-CELL CAP: projected operation count exceeds "
                          "5e8. SKIPPED_BUDGET."})
            log("    ST-1 SKIP k=%d beta=%.3f B=%d proj=%.3g"
                % (rec["k"], rec["beta"], B, proj))
            continue
        cls = {"h": rec["h_on_measured_B"], "C_red": rec["C_red_on_measured_B"],
               "evaluable": rec["evaluable_on_measured_B"]}
        cell = census_cell(inst, rec["beta"], m, F, L, cls, rng,
                           want_profile=True, log=log)
        cell["evaluable_on_measured_B"] = rec["evaluable_on_measured_B"]
        cell["evaluable_on_B_equals_L"] = rec["evaluable_on_B_equals_L"]
        cell["class_changed_on_measurement"] = rec["class_changed_on_measurement"]
        cell["projected_operations"] = proj
        # CTRL-EXHAUSTIVE-TRUTH at the two smallest field sizes
        if (m == 3 and rec["k"] in (12, 14) and cell["collision_profile"]
                and cell["collision_profile"]["label"] == "DETERMINED"):
            sp = sampled_profile(F, inst.N, m, cell["C_all"], rng)
            mu_e = cell["collision_profile"]["size_biased_mean_load"]
            dev = abs(sp["size_biased_mean_load_hat"] - mu_e)
            cell["CTRL_EXHAUSTIVE_TRUTH"] = {
                "exhaustive_size_biased_mean_load": mu_e,
                "sampled_size_biased_mean_load_hat": sp["size_biased_mean_load_hat"],
                "sampled_se": sp["size_biased_mean_load_se"],
                "abs_deviation": dev,
                "within_3_se": bool(dev <= 3 * sp["size_biased_mean_load_se"] + 1e-12),
                "n_draws": sp["n_draws"],
            }
        out["cells"].append(cell)
        log("    cell k=%2d beta=%.3f m=%d B=%4d |S_m|=%8d E=%.4f R=%.4f "
            "eval=%s (%.2fs)"
            % (rec["k"], rec["beta"], m, B, cell["S_m"], cell["PM3_E"],
               cell["PM2_R"], rec["evaluable_on_measured_B"], cell["seconds"]))

    # --- controls
    for k in FIELD_BITS:
        inst = ctx["instance"](k)
        out["controls"].append(ctrl_dl(inst, m, np.random.default_rng(
            derive_seed(master, "CTRL-DL", k, m))))
    out["controls"].append(known_answer_test_shared_routine())
    return out


def run_null_uniform_fb(run_id: str, ctx) -> dict:
    """CTRL-NULL-FB (v2 C-13): 10 draws where measured B <= 64, 3 elsewhere."""
    log = ctx["log"]
    master = MASTER_SEEDS[run_id]
    out = {"arm": "destroy-parameter null (uniform random negation-closed "
                  "factor base of the IDENTICAL measured size B on the "
                  "IDENTICAL curve, through the IDENTICAL sumset code path "
                  "distinct_sumset() and the IDENTICAL distinct-count routine "
                  "shared_membership_distinct())",
           "master_seed": master, "instances": [], "cells": [],
           "controls": [], "skipped_cells": []}
    for k in FIELD_BITS:
        out["instances"].append(instance_record(ctx["instance"](k)))
    for m in ARITIES:
        for k in FIELD_BITS:
            inst = ctx["instance"](k)
            for beta in BETA_GRID:
                L, F = inst.factor_base(beta)
                B = int(F.size)
                cls = classify_cell(B, m, inst.p)
                if not cls["evaluable"]:
                    continue
                if ctx["deadline_passed"]():
                    out["skipped_cells"].append(
                        {"k": k, "beta": beta, "m": m,
                         "reason": "ST-2 RUN CAP: deadline reached. NOT a measurement."})
                    continue
                draws = fb_null_draws(B)
                cred = cls["C_red"]
                s_prev = 1 if m == 2 else B
                p_pred = occupancy_prediction(inst.N, cred, s_prev)
                per = []
                for d in range(draws):
                    rng = np.random.default_rng(derive_seed(master, k, beta, m, d))
                    Fr = inst.random_negation_closed_fb(B, rng)
                    sizes, _ = sum_set_chain(Fr, inst.N, m)
                    per.append({"draw": d,
                                "seed": derive_seed(master, k, beta, m, d),
                                "S_m": sizes[-1], "E": sizes[-1] / p_pred})
                Es = [x["E"] for x in per]
                out["cells"].append({
                    "k": k, "p": inst.p, "N": inst.N, "beta": beta, "m": m,
                    "L": L, "B": B, "C_red": cred, "P_pred": p_pred,
                    "evaluable_on_measured_B": True,
                    "draws": draws,
                    "E_randomFB_per_draw": per,
                    "E_randomFB_mean": float(np.mean(Es)),
                    "E_randomFB_sd": float(np.std(Es, ddof=1)) if len(Es) > 1 else 0.0,
                    "E_randomFB_min": float(np.min(Es)),
                    "E_randomFB_max": float(np.max(Es)),
                    "label": "DETERMINED per drawn factor base, SAMPLED over draws",
                })
                log("    FB-null k=%2d beta=%.3f m=%d B=%4d draws=%2d "
                    "E_mean=%.4f sd=%.4f"
                    % (k, beta, m, B, draws, float(np.mean(Es)),
                       float(np.std(Es, ddof=1)) if len(Es) > 1 else 0.0))
    out["controls"].append(known_answer_test_shared_routine())
    return out


def run_null_random_sumset(run_id: str, ctx) -> dict:
    """CTRL-NULL-SUMSET, v2 C-4 antipodal-pair process, PLUS the declared v1
    independent-throw contrast arm."""
    log = ctx["log"]
    master = MASTER_SEEDS[run_id]
    out = {"arm": "shape-matched occupancy null", "master_seed": master,
           "process_note":
               "v2 C-4 GOVERNS. The PRIMARY process draws g uniformly from G and "
               "inserts BOTH g and -g, C_red/2 times; it is the process that "
               "feeds INV-4, both tail checks and the standardized bulk check. "
               "The v1 independent-throw process is ALSO run at the same cells "
               "and the same replicate counts as a DECLARED CONTRAST ARM, so "
               "the variance factor is measured inside the driver and archived "
               "rather than imported from the unarchived probe of "
               "TASK-20260729-003.",
           "RT_15_identity_bin_note":
               "RT-15 (TASK-20260729-011, minor): the antipodal process "
               "partitions the N-1 non-identity elements into (N-1)/2 bin "
               "pairs, but a draw of g = 0 covers ONE bin rather than two, and "
               "S_m can contain the identity. Expected effect is O(1) against "
               "P_pred; the measured identity-summing multiset count per cell "
               "is reported in the census runs' `identity_multisets` field. NO "
               "THRESHOLD MOVES. Recorded, not corrected.",
           "literal_reading_note":
               "v1 CTRL-NULL-SUMSET.declared_design_choice: the queue's literal "
               "wording - a uniformly random subset of G of the SAME CARDINALITY "
               "as the reachable m-sum set - is TAUTOLOGICAL, since the distinct "
               "count of a set of given cardinality is that cardinality. It is "
               "demonstrated below as the trivial identity it is, at one cell, "
               "and is not used for anything.",
           "instances": [], "cells": [], "controls": [], "skipped_cells": []}
    for k in FIELD_BITS:
        out["instances"].append(instance_record(ctx["instance"](k)))
    demo_done = False
    for m in ARITIES:
        for k in FIELD_BITS:
            inst = ctx["instance"](k)
            N = inst.N
            for beta in BETA_GRID:
                L, F = inst.factor_base(beta)
                B = int(F.size)
                cls = classify_cell(B, m, inst.p)
                if not cls["evaluable"]:
                    continue
                if ctx["deadline_passed"]():
                    out["skipped_cells"].append(
                        {"k": k, "beta": beta, "m": m,
                         "reason": "ST-2 RUN CAP: deadline reached. NOT a measurement."})
                    continue
                cred = cls["C_red"]
                reps = replicate_count(cred)
                s_prev = 1 if m == 2 else B
                p_pred = occupancy_prediction(N, cred, s_prev)
                rng_a = np.random.default_rng(derive_seed(master, "AP", k, beta, m))
                rng_i = np.random.default_rng(derive_seed(master, "IND", k, beta, m))
                va = occupancy_null(N, cred, reps, rng_a, antipodal=True)
                vi = occupancy_null(N, cred, reps, rng_i, antipodal=False)
                ma, sa = float(va.mean()), float(va.std(ddof=1))
                mi, si = float(vi.mean()), float(vi.std(ddof=1))
                z_single = (ma - p_pred) / sa if sa > 0 else float("inf")
                z_mean = (ma - p_pred) / (sa / math.sqrt(reps)) if sa > 0 else float("inf")
                rel_sd = sa / p_pred
                cellrec = {
                    "k": k, "p": inst.p, "N": N, "beta": beta, "m": m,
                    "L": L, "B": B, "C_red": cred,
                    "C_red_is_even": bool(cred % 2 == 0),
                    "lambda_C_red_over_N": cred / N,
                    "replicates": reps, "P_pred": p_pred,
                    "antipodal": {"mean": ma, "sd": sa,
                                  "relative_sd": rel_sd,
                                  "z_vs_P_pred_single_sd": z_single,
                                  "z_vs_P_pred_sd_of_mean": z_mean,
                                  "seed": derive_seed(master, "AP", k, beta, m)},
                    "independent_throw_contrast": {
                        "mean": mi, "sd": si, "relative_sd": si / p_pred,
                        "z_vs_P_pred_single_sd": (mi - p_pred) / si if si > 0 else None,
                        "seed": derive_seed(master, "IND", k, beta, m)},
                    "measured_sd_ratio_antipodal_over_independent":
                        (sa / si) if si > 0 else None,
                    "measured_variance_ratio_antipodal_over_independent":
                        (sa * sa / (si * si)) if si > 0 else None,
                    "analytic_prediction_v2_C4": {
                        "mean_unchanged": True,
                        "variance_ratio": 2.0,
                        "sd_ratio": math.sqrt(2.0)},
                    "P_pred_decomposition": {
                        "N_times_1_minus_exp_minus_lambda":
                            inst.N * (1.0 - math.exp(-cred / inst.N)),
                        "S_m_minus_2_used": s_prev,
                        "exp_minus_lambda": math.exp(-cred / inst.N),
                        "S_m_minus_2_term": s_prev * math.exp(-cred / inst.N),
                        "note": "P_pred = N(1-e^-lambda) + |S_(m-2)| e^-lambda. "
                                "The FIRST term is the mean of the occupancy "
                                "process CTRL-NULL-SUMSET actually runs. The "
                                "SECOND term is not produced by that process, "
                                "because the process throws C_red balls into an "
                                "EMPTY N-bit set and never pre-marks the "
                                "|S_(m-2)| bins that a cancelling multiset "
                                "reaches deterministically. The residual below "
                                "makes that visible; it is ARITHMETIC ON "
                                "ALREADY-SPECIFIED QUANTITIES and is not a new "
                                "arm, not a repair, and not used by any "
                                "criterion.",
                    },
                    "mean_minus_P_pred": ma - p_pred,
                    "mean_minus_P_pred_over_sd": (ma - p_pred) / sa if sa > 0 else None,
                    "residual_after_adding_back_S_m_minus_2_term":
                        ma - (inst.N * (1.0 - math.exp(-cred / inst.N))),
                    "residual_after_adding_back_over_sd":
                        ((ma - inst.N * (1.0 - math.exp(-cred / inst.N))) / sa)
                        if sa > 0 else None,
                    "INV_4_within_3_empirical_sd": bool(abs(ma - p_pred) <= 3 * sa),
                    "INV_4_reading": "|empirical mean - P_pred| <= 3 * empirical sd "
                                     "of a SINGLE replicate (the literal reading of "
                                     "v1 INV-4). The standard error of the mean is "
                                     "reported alongside as z_vs_P_pred_sd_of_mean "
                                     "but is NOT the rule applied.",
                    "NOISE_LIMITED": bool(rel_sd > 0.02),
                    "label": "SAMPLED",
                }
                if not demo_done:
                    demo_rng = np.random.default_rng(derive_seed(master, "LITERAL"))
                    card = min(cred, N - 1)
                    pick = demo_rng.choice(N, size=card, replace=False)
                    _, _, dcount, _ = shared_membership_distinct(pick, N)
                    cellrec["literal_reading_demonstration"] = {
                        "cardinality_drawn": int(card),
                        "distinct_count_returned": dcount,
                        "identical": bool(dcount == card),
                        "note": "Tautology confirmed, as declared. Not used.",
                    }
                    demo_done = True
                out["cells"].append(cellrec)
                log("    AP-null k=%2d beta=%.3f m=%d C_red=%d reps=%d "
                    "mean=%.1f (P_pred=%.1f) sd=%.3f  ind-sd=%.3f  ratio=%.3f"
                    % (k, beta, m, cred, reps, ma, p_pred, sa, si,
                       (sa / si) if si > 0 else float("nan")))
    failed = [c for c in out["cells"] if not c["INV_4_within_3_empirical_sd"]]
    out["INV_4"] = {
        "rule": "CTRL-NULL-SUMSET fails to reproduce P_pred within 3 empirical "
                "standard deviations at any criterion-evaluable cell. Every E "
                "value is VOID RATHER THAN NEGATIVE (v1 INV-4, unchanged in form "
                "by v2; the empirical sd is now the antipodal process's).",
        "cells_evaluated": len(out["cells"]),
        "cells_failed": [{"k": c["k"], "beta": c["beta"], "m": c["m"],
                          "B": c["B"], "C_red": c["C_red"],
                          "P_pred": c["P_pred"],
                          "empirical_mean": c["antipodal"]["mean"],
                          "empirical_sd": c["antipodal"]["sd"],
                          "z": c["antipodal"]["z_vs_P_pred_single_sd"],
                          "mean_minus_P_pred": c["mean_minus_P_pred"],
                          "S_m_minus_2_term":
                              c["P_pred_decomposition"]["S_m_minus_2_term"],
                          "residual_after_adding_back_over_sd":
                              c["residual_after_adding_back_over_sd"]}
                         for c in failed],
        "n_failed": len(failed),
        "fired": bool(failed),
        "consequence_if_fired": "P0 of the v2 outcome_disposition_table: NO "
                                "OUTCOME BRANCH IS EVALUATED, the VOID "
                                "disposition governs, and an invalid or void run "
                                "set IS NOT EVIDENCE and its invalidity is never "
                                "a negative mathematical result. The Executor "
                                "RECORDS the firing; the disposition is the "
                                "Coordinator's and the reviewers'.",
    }
    if failed:
        res = [c["residual_after_adding_back_over_sd"] for c in out["cells"]
               if c["residual_after_adding_back_over_sd"] is not None]
        z0 = [c["mean_minus_P_pred_over_sd"] for c in out["cells"]
              if c["mean_minus_P_pred_over_sd"] is not None]
        out["INV_4"]["derived_diagnostic"] = {
            "statement": "DERIVED FROM ALREADY-RECORDED QUANTITIES, NOT A NEW "
                         "ARM AND NOT A REPAIR. Across all evaluated cells, the "
                         "shortfall of the empirical null mean below P_pred is "
                         "the |S_(m-2)| e^-lambda term of P_pred's own formula, "
                         "which the specified occupancy process does not "
                         "produce: the process throws C_red balls into an EMPTY "
                         "N-bit set, whereas P_pred is the mean of a process "
                         "that ALSO pre-marks the |S_(m-2)| deterministically "
                         "reachable bins. At m = 2 that term is |S_0| = 1 and is "
                         "invisible; at m = 3 it is |S_1| = B and dominates the "
                         "null spread wherever lambda is small. NOTHING IS "
                         "CHANGED ON THIS BASIS: INV-4 is evaluated against "
                         "P_pred exactly as frozen, and this statement is an "
                         "observation for the Coordinator and the reviewers.",
            "z_vs_P_pred_min": float(np.min(z0)), "z_vs_P_pred_max": float(np.max(z0)),
            "z_after_adding_back_min": float(np.min(res)),
            "z_after_adding_back_max": float(np.max(res)),
            "n_cells": len(res),
        }
    if out["cells"]:
        ratios = [c["measured_sd_ratio_antipodal_over_independent"]
                  for c in out["cells"]
                  if c["measured_sd_ratio_antipodal_over_independent"]]
        out["contrast_arm_summary"] = {
            "n_cells": len(ratios),
            "sd_ratio_mean": float(np.mean(ratios)),
            "sd_ratio_median": float(np.median(ratios)),
            "sd_ratio_min": float(np.min(ratios)),
            "sd_ratio_max": float(np.max(ratios)),
            "analytic_sd_ratio": math.sqrt(2.0),
        }
    out["controls"].append(known_answer_test_shared_routine())
    return out


def run_calib_ap(run_id: str, ctx) -> dict:
    """CTRL-CALIB-AP, in EV-STR-001's own regime and nowhere else."""
    log = ctx["log"]
    master = MASTER_SEEDS[run_id]
    out = {
        "arm": "EV-STR-001 calibration leg (INVALIDATION control)",
        "master_seed": master,
        "regime": {
            "n": [211, 1009, 4099], "m": [3, 4],
            "B": CALIB_B,
            "B_reading": "v2 C-8 B DISCLOSURE freezes B = ceil(sqrt(n)) = 15, 32, 65 "
                         "and instructs the Executor to RECORD WHICH B IT USED and "
                         "not adjust it. EV-STR-001's own reported B medians are "
                         "15 / 32 / 64.5, consistent with that record having used "
                         "B = ceil(sqrt(curve order)) per seed rather than "
                         "ceil(sqrt(field prime)); the difference is recorded here "
                         "as an observation and NOT acted on.",
            "D": "1..64",
            "seeds_per_cell": CALIB_SEEDS_PER_CELL,
        },
        "convention_warning":
            "THIS LEG'S CONVENTION DIFFERS FROM THE CENSUS'S. The census uses an "
            "x-interval factor base at B = p^beta on a grid; this leg uses AP "
            "supports at B = ceil(sqrt(n)). ANY COMPARISON BETWEEN THE TWO IS "
            "QUALITATIVE ONLY. The penalty is strongly cell-dependent, spanning "
            "17.5x to 4128.6x, grows with n at fixed m and superlinearly in m at "
            "fixed n; quoting 17.5x alone is FORBIDDEN.",
        "admissibility_predicate_reading":
            "RESOLVED FROM THE COMMITTED experiments/EXP-STR-001/specification.yaml "
            "and recorded rather than guessed (v2 C-8 named_execution_risk_"
            "discharged; ST-3 therefore does not fire). Factor base: 'x-interval: "
            "first B liftable x >= 0, canonical y = min(y, p-y), ordered by x'. AP "
            "support: {x, x+d, ..., x+(m-1)d} on X-COORDINATES with d in D = 1..64, "
            "non-wrapping (the negative control's closed form sum_d max(0, "
            "p-(m-1)d) fixes non-wrapping), one point per x, each support counted "
            "once. ap_supply = the number of DISTINCT admissible AP support "
            "tuples, counted through the SHARED routine "
            + SHARED_ROUTINE_NAME + ". yield_penalty = C(B,m)/ap_supply. Curves: "
            "ordinary prime-field short Weierstrass with prime order != p, drawn "
            "fresh per seed from master seed 110601.",
        "estimator_form":
            "v2 C-8: the recovered penalty is reported BOTH as the ratio of "
            "medians C(B,m)/median(supply) and as the median of ratios "
            "median(C(B,m)/supply). The factor-2 window is evaluated against the "
            "RATIO OF MEDIANS.",
        "cells": [], "controls": [],
    }
    kat = known_answer_test_shared_routine()
    out["controls"].append(kat)
    for n in (211, 1009, 4099):
        sq = qr_bits(n)
        xs_all = np.arange(n, dtype=np.int64)
        for m in (3, 4):
            B = CALIB_B[n]
            cbm = math.comb(B, m)
            nseeds = CALIB_SEEDS_PER_CELL[n]
            per = []
            for s in range(nseeds):
                seed = derive_seed(master, n, m, s)
                rng = np.random.default_rng(seed)
                # fresh curve: prime order, != n (anomalous excluded),
                # != n+1 (supersingular excluded -> ordinary)
                while True:
                    a = int(rng.integers(0, n))
                    b = int(rng.integers(0, n))
                    if (4 * a * a * a + 27 * b * b) % n == 0:
                        continue
                    order = curve_order(n, a, b, sq, xs_all)
                    if order != n and order != n + 1 and is_prime(order):
                        break
                v = rhs_values(n, a, b, xs_all)
                liftable = (v == 0) | sq[v]
                fb_x = np.flatnonzero(liftable)[:B]
                if fb_x.size < B:
                    raise RuntimeError("fewer than B liftable x at n=%d" % n)
                memb = np.zeros(n, dtype=bool)
                memb[fb_x] = True
                # enumerate candidate APs (x, d), non-wrapping
                xs_list, ds_list = [], []
                for d in range(1, CALIB_D_MAX + 1):
                    top = n - (m - 1) * d
                    if top <= 0:
                        break
                    xx = np.arange(top, dtype=np.int64)
                    xs_list.append(xx)
                    ds_list.append(np.full(xx.size, d, dtype=np.int64))
                xcand = np.concatenate(xs_list)
                dcand = np.concatenate(ds_list)
                ok = np.ones(xcand.size, dtype=bool)
                for r in range(m):
                    mask, _, _, _ = shared_membership_distinct(
                        xcand + r * dcand, n, memb)
                    ok &= mask
                tuple_ids = (xcand[ok] * (CALIB_D_MAX + 1)) + dcand[ok]
                _, n_adm, supply, _ = shared_membership_distinct(
                    tuple_ids, n * (CALIB_D_MAX + 1))
                per.append({
                    "seed_index": s, "seed": seed, "a": a, "b": b,
                    "curve_order": order, "B": B,
                    "factor_base_x_max": int(fb_x[-1]),
                    "ap_candidates_nonwrapping": int(xcand.size),
                    "ap_admissible_before_dedup": n_adm,
                    "ap_supply_distinct": supply,
                    "yield_penalty": (cbm / supply) if supply else None,
                })
            sup = [x["ap_supply_distinct"] for x in per]
            pens = [x["yield_penalty"] for x in per if x["yield_penalty"]]
            med_sup = float(np.median(sup))
            ratio_of_medians = cbm / med_sup if med_sup else None
            median_of_ratios = float(np.median(pens)) if pens else None
            target = EV_STR_001_PENALTY_MEDIAN[n][m]
            fac = (max(ratio_of_medians, target) / min(ratio_of_medians, target)
                   if ratio_of_medians else None)
            out["cells"].append({
                "n": n, "m": m, "B_used": B, "C_B_m": cbm,
                "seeds": nseeds,
                "per_seed": per,
                "supply_median": med_sup,
                "supply_min": int(np.min(sup)), "supply_max": int(np.max(sup)),
                "EV_STR_001_supply_median": EV_STR_001_SUPPLY_MEDIAN[n][m],
                "recovered_penalty_ratio_of_medians": ratio_of_medians,
                "recovered_penalty_median_of_ratios": median_of_ratios,
                "EV_STR_001_penalty_median": target,
                "factor_vs_target_on_ratio_of_medians": fac,
                "within_factor_2": bool(fac is not None and fac <= 2.0),
                "label": "DETERMINED per seed; the median over seeds is SAMPLED",
            })
            log("    calib n=%4d m=%d B=%d supply_med=%.1f penalty(ratio of "
                "medians)=%.1f target=%.1f factor=%.2f"
                % (n, m, B, med_sup, ratio_of_medians, target, fac))

    cells = out["cells"]
    misses = [c for c in cells if not c["within_factor_2"]]
    by = {(c["n"], c["m"]): c["recovered_penalty_ratio_of_medians"] for c in cells}
    growth_in_n = all(by[(211, m)] < by[(1009, m)] < by[(4099, m)] for m in (3, 4))
    superlinear_in_m = all(by[(n, 4)] > (4.0 / 3.0) * by[(n, 3)]
                           for n in (211, 1009, 4099))
    out["trend_clauses"] = {
        "monotone_growth_in_n_at_fixed_m": bool(growth_in_n),
        "superlinear_growth_in_m_at_fixed_n": bool(superlinear_in_m),
        "superlinear_operationalisation":
            "penalty(m=4) > (4/3) * penalty(m=3) at each n, i.e. faster than "
            "linear in m. The contract states the clause qualitatively; this is "
            "the reading applied, declared here rather than chosen after the "
            "numbers were seen.",
    }
    out["INV_2a"] = {
        "reading": kat["reading_applied"],
        "shared_routine": SHARED_ROUTINE_NAME,
        "known_answer_test_all_agree": kat["all_agree"],
        "fired": kat["INV_2a_fired"],
        "consequence_if_fired": "THE CENSUS NUMBERS ARE VOID RATHER THAN NEGATIVE.",
    }
    out["INV_2b"] = {
        "cells_outside_factor_2": [{"n": c["n"], "m": c["m"],
                                    "factor": c["factor_vs_target_on_ratio_of_medians"]}
                                   for c in misses],
        "n_outside_factor_2": len(misses),
        "trend_clause_failed": bool(not (growth_in_n and superlinear_in_m)),
        "fired": bool(len(misses) >= 2 or not (growth_in_n and superlinear_in_m)),
        "consequence": "INV-2b IS AN INSTRUMENT NOTE AND DOES NOT VOID CENSUS "
                       "DATA (v2 C-8).",
    }
    return out


def run_baseline(run_id: str, ctx) -> dict:
    """CTRL-BASELINE.  Matched rho-with-negation and BSGS, MEASURED, in one
    operation unit: one elliptic-curve point addition or doubling."""
    log = ctx["log"]
    master = MASTER_SEEDS[run_id]
    out = {"arm": "matched baselines, MEASURED",
           "operation_unit": "one elliptic-curve point addition or doubling",
           "master_seed": master, "instances": [], "per_size": [],
           "certificate": {
               "kind": "discrete_log",
               "statement": "For every reported rho and BSGS solve, the returned "
                            "integer d satisfies d*G = T in the census curve's "
                            "prime-order group.",
               "verification": "Re-verified by ec_mul_double_and_add(), a "
                               "double-and-add scalar multiplication that shares "
                               "no code with the rho walk or with BSGS, AND "
                               "independently cross-checked against the "
                               "discrete-logarithm table built for the census.",
               "scope_note": "These are TOY-SCALE BASELINE MEASUREMENTS at 12-18 "
                             "field bits. They are not a cryptanalytic claim of "
                             "any kind and confer no attack advantage."},
           "controls": []}
    for k in FIELD_BITS:
        if ctx["deadline_passed"]():
            out.setdefault("skipped_sizes", []).append(
                {"k": k, "reason": "ST-2 RUN CAP: deadline reached. NOT a measurement."})
            continue
        inst = ctx["instance"](k)
        out["instances"].append(instance_record(inst))
        p, a, N, G = inst.p, inst.a, inst.N, inst.G
        rng = np.random.default_rng(derive_seed(master, k))
        rows = []
        for t in range(BASELINE_TARGETS):
            d_true = int(rng.integers(1, N))
            T = ec_mul_double_and_add(d_true, G, a, p)
            d_bsgs, ops_bsgs, mem_bsgs = bsgs(T, G, a, p, N)
            trng = np.random.default_rng(derive_seed(master, k, t, "rho"))
            d_rho, steps, setup, esc, restarts = rho_negation(T, G, a, p, N, trng)
            ver_rho = (d_rho is not None
                       and ec_mul_double_and_add(d_rho, G, a, p) == T)
            ver_bsgs = (d_bsgs is not None
                        and ec_mul_double_and_add(d_bsgs, G, a, p) == T)
            tab = int(inst.dl_can[T[0]])
            tab_d = tab if T[1] <= p - T[1] else N - tab
            rows.append({
                "target_index": t, "d_true": d_true,
                "rho_d": d_rho, "rho_walk_steps": steps,
                "rho_setup_ops": setup, "rho_escapes": esc,
                "rho_restarts": restarts,
                "rho_certificate_verified": bool(ver_rho),
                "rho_matches_dl_table": bool(d_rho == tab_d),
                "bsgs_d": d_bsgs, "bsgs_ops": ops_bsgs,
                "bsgs_stored_group_elements": mem_bsgs,
                "bsgs_certificate_verified": bool(ver_bsgs),
                "bsgs_matches_dl_table": bool(d_bsgs == tab_d),
            })
        steps = [r["rho_walk_steps"] for r in rows]
        bops = [r["bsgs_ops"] for r in rows]
        model_rho = 0.886 * math.sqrt(N)
        model_bsgs = 2.0 * math.sqrt(N)
        mean_rho = float(np.mean(steps))
        rec = {
            "k": k, "p": p, "N": N,
            "targets": BASELINE_TARGETS,
            "rho_walk_steps_mean_MEASURED": mean_rho,
            "rho_walk_steps_median_MEASURED": float(np.median(steps)),
            "rho_walk_steps_min_MEASURED": int(np.min(steps)),
            "rho_walk_steps_max_MEASURED": int(np.max(steps)),
            "rho_setup_ops_mean_MEASURED": float(np.mean([r["rho_setup_ops"] for r in rows])),
            "rho_setup_ops_note": "Cost of building the 32 rho step points and the "
                                  "walk start, reported SEPARATELY rather than "
                                  "folded into the walk count, because the model "
                                  "position 0.886 sqrt(N) counts walk steps only.",
            "rho_measurement_convention": "DECLARED. The walk stores every visited "
                                          "class in a table and stops at the FIRST "
                                          "repetition, so the measured step count "
                                          "is exactly the quantity 0.886 sqrt(N) "
                                          "models (the birthday time on N/2 "
                                          "classes). That harness uses O(sqrt(N)) "
                                          "memory rather than the O(1) of a "
                                          "Floyd/Brent or distinguished-point rho; "
                                          "a Floyd variant would measure a LARGER "
                                          "step count for the same solve. The "
                                          "convention chosen is the one that makes "
                                          "the measurement comparable with the "
                                          "model position, and it is recorded "
                                          "rather than assumed.",
            "rho_model_position_0_886_sqrtN_DERIVED_MODEL": model_rho,
            "rho_measured_over_model": mean_rho / model_rho,
            "bsgs_ops_mean_MEASURED": float(np.mean(bops)),
            "bsgs_model_position_2_sqrtN_DERIVED_MODEL": model_bsgs,
            "bsgs_measured_over_model": float(np.mean(bops)) / model_bsgs,
            "bsgs_memory_stored_group_elements_MEASURED":
                float(np.mean([r["bsgs_stored_group_elements"] for r in rows])),
            "bsgs_memory_model_sqrtN_DERIVED_MODEL": math.sqrt(N),
            "all_rho_certificates_verified":
                bool(all(r["rho_certificate_verified"] for r in rows)),
            "all_bsgs_certificates_verified":
                bool(all(r["bsgs_certificate_verified"] for r in rows)),
            "all_solutions_match_dl_table":
                bool(all(r["rho_matches_dl_table"] and r["bsgs_matches_dl_table"]
                         for r in rows)),
            "INV_6_rho_more_than_20pc_below_model":
                bool(mean_rho < 0.8 * model_rho),
            "census_dl_table_point_additions_MEASURED": inst.dl_table_point_additions,
            "census_dl_table_over_measured_rho": inst.dl_table_point_additions / mean_rho,
            "per_target": rows,
        }
        out["per_size"].append(rec)
        log("    baseline k=%2d N=%d  rho steps mean=%.1f (model %.1f, ratio "
            "%.3f)  bsgs ops mean=%.1f (model %.1f) mem=%.0f"
            % (k, N, mean_rho, model_rho, mean_rho / model_rho,
               float(np.mean(bops)), model_bsgs,
               float(np.mean([r["bsgs_stored_group_elements"] for r in rows]))))
    out["controls"].append(known_answer_test_shared_routine())
    out["standing_control_note"] = (
        "v1 matched_baseline_position_RC7.standing_control: THE CENSUS COSTS MORE "
        "GROUP-EQUIVALENT OPERATIONS THAN SOLVING THE INSTANCE OUTRIGHT. The "
        "census/rho operation ratio is reported per instance here and per cell in "
        "summary.json precisely so that no reader can mistake a yield measurement "
        "for an attack result. A ratio below 1 would be an accounting red flag, "
        "not an attack.")
    return out


def instance_record(inst: Instance) -> dict:
    return {
        "k": inst.k, "p": inst.p,
        "curve": {"a": inst.a, "b": inst.b, "form": "y^2 = x^3 + a x + b"},
        "N": inst.N, "N_is_prime": is_prime(inst.N),
        "N_not_equal_p": inst.N != inst.p,
        "N_not_equal_p_plus_1_ordinary": inst.N != inst.p + 1,
        "hasse_t_trace": inst.p + 1 - inst.N,
        "p_over_N": inst.p / inst.N,
        "generator": {"x": inst.G[0], "y": inst.G[1]},
        "curve_candidates_tried": inst.curve_search["candidates_tried"],
        "curve_selection_t_reached": inst.curve_search["t_reached"],
        "dl_table_point_additions": inst.dl_table_point_additions,
        "dl_walk_closure_ok": bool(inst.dl_closure_ok),
        "dl_x_with_point": inst.n_x_with_point,
        "dl_count_ok_2x_plus_1_equals_N": bool(inst.dl_count_ok),
        "instance_setup_seconds": inst.setup_seconds,
    }


RUN_DISPATCH = {
    "RUN-YIELD-001-CENSUS-M2": lambda rid, ctx: run_census(rid, 2, ctx),
    "RUN-YIELD-001-CENSUS-M3": lambda rid, ctx: run_census(rid, 3, ctx),
    "RUN-YIELD-001-NULL-UNIFORM-FB": run_null_uniform_fb,
    "RUN-YIELD-001-NULL-RANDOM-SUMSET": run_null_random_sumset,
    "RUN-YIELD-001-CALIB-AP": run_calib_ap,
    "RUN-YIELD-001-BASELINE-RHO-BSGS": run_baseline,
}


# --------------------------------------------------------------------------
# 9.  Manifest.
# --------------------------------------------------------------------------

PROTOCOL_DEVIATIONS = [
    {
        "id": "DEV-1",
        "kind": "declared artifact-layout deviation, forced by the contract",
        "text": "docs/evidence-and-reproducibility.md's generic run package has "
                "command.txt, environment.json and stderr.log. The frozen "
                "contract's required_artifacts_rule declares EXACTLY TWENTY "
                "FILES with three files per run directory and no stderr file, "
                "and TASK-20260729-005 forbids any undeclared artifact. The "
                "exact command and the full environment block are therefore "
                "recorded INSIDE manifest.json, and stderr is captured into "
                "stdout.log by an in-process tee. Nothing is lost; the location "
                "changes."},
    {
        "id": "DEV-2",
        "kind": "declared artifact-layout deviation, forced by the contract",
        "text": "agents/executor.md asks for a separate implementation note. The "
                "21-path declaration admits no such file, so the implementation "
                "notes and this deviation list live in every manifest and in "
                "results/summary.json, and are repeated in the execution report."},
    {
        "id": "DEV-3",
        "kind": "declared reading of an under-specified control statistic",
        "text": "v1 metrics label the m=3 collision profile SAMPLED over 10^6 "
                "uniform multisets above C_all = 5e7 but name no statistic, and "
                "CTRL-EXHAUSTIVE-TRUTH requires the SAME estimator to be run "
                "where the exhaustive value exists. The estimator is defined in "
                "sampled_profile(): the unbiased collision probability rho_hat "
                "and the size-biased mean load rho_hat*C_all, with a 10-block "
                "standard error. The sample maximum load is reported as a sample "
                "statistic and is explicitly NOT an estimate of the true maximum."},
    {
        "id": "DEV-4",
        "kind": "declared reading of an under-specified invalidation threshold",
        "text": "v1 INV-4 says 'within 3 empirical standard deviations' without "
                "saying whether the denominator is the sd of a single replicate "
                "or the standard error of the mean. The LITERAL reading (single "
                "replicate sd) is applied and both z values are reported."},
    {
        "id": "DEV-5",
        "kind": "declared reading of an under-specified trend clause",
        "text": "INV-2's 'superlinear growth in m at fixed n' is qualitative. It "
                "is operationalised as penalty(m=4) > (4/3)*penalty(m=3) at each "
                "n, declared before the numbers were seen."},
    {
        "id": "DEV-6",
        "kind": "NOT APPLIED - reported to the Coordinator instead",
        "text": "INV-5's trigger turns on the word 'shrink', which the contract "
                "never quantifies, and v2 C-13 gives its disposition a THREE-WAY "
                "reading the Executor may not choose among. The comparison "
                "statistics are therefore reported per cell under two stated "
                "readings and NO INV-5 FIRING DETERMINATION IS MADE HERE. That "
                "determination belongs to TASK-20260729-007/-008 and the "
                "Coordinator."},
]

EXECUTION_HISTORY = {
    "declared_runs": "Each of the six declared run directories was written ONCE, "
                     "by the final driver, in the contract's run_plan order. No "
                     "declared run was executed more than once, discarded, or "
                     "re-keyed.",
    "development_runs_disclosed": (
        "DISCLOSED IN FULL. Before the declared runs, the driver was developed "
        "and exercised end-to-end OUTSIDE THE REPOSITORY, in the session "
        "scratchpad, against a scratch output root (--out-root). Those "
        "development executions are not runs of the experiment, wrote nothing "
        "into experiments/EXP-YIELD-001, and are not reported as measurements. "
        "Because every seed is fixed by the contract and the census is "
        "deterministic, the declared runs reproduce those numbers exactly."),
    "what_changed_after_the_development_dry_run": (
        "STATED PLAINLY BECAUSE IT IS THE KIND OF THING THAT MUST NOT BE "
        "SILENT. The development dry run revealed that INV-4 fires. In response "
        "the driver gained (i) an INV_4 rollup block naming the failing cells, "
        "(ii) a manifest-level protocol observation recording the firing, and "
        "(iii) a DERIVED diagnostic that decomposes P_pred into the two terms "
        "its own formula contains, computed from already-specified quantities. "
        "NO THRESHOLD, NO CRITERION, NO SEED, NO CONTROL PROCESS, NO REPLICATE "
        "COUNT, NO CELL CLASS AND NO REPORTED MEASUREMENT WAS CHANGED, AND NO "
        "NEW EXPERIMENTAL ARM WAS ADDED. INV-4 is evaluated against P_pred "
        "exactly as frozen, on the antipodal process exactly as v2 C-4 "
        "specifies it."),
}

IMPLEMENTATION_NOTES = [
    "The census is computed entirely in the discrete-logarithm image, per v1 "
    "inputs.computation_domain, and CTRL-DL checks that image against explicit "
    "curve arithmetic on 10^4 random m-multisets per field size per arity.",
    "ONE sumset code path, distinct_sumset(), is used by the census arm and by "
    "the CTRL-NULL-FB arm (completion gate E5). ONE distinct-count and "
    "membership routine, " + SHARED_ROUTINE_NAME + "(), produces the census's "
    "|S_m|, the identity-multiset counts and the AP leg's supply (v2 C-8 (b)).",
    "Every cell's criterion-evaluable class is computed from measured B alone in "
    "a first pass and frozen in results.json BEFORE any sum set is computed "
    "(v2 C-2 rule R-2). Measured B is even at every cell, as v2 C-4 derives.",
    "No Groebner basis, no polynomial system solve, no summation polynomial, and "
    "no import of harness/endomorphism_la.py or any other part of the "
    "EXP-STR-002 instrument.",
]

PRE_EXECUTION_CONDITIONS = {
    "source": "TASK-20260729-011 amendment_review.yaml, pre_execution_conditions",
    "binding_note_quoted": "THESE ARE CONDITIONS ON THE COORDINATOR, NOT ON THE "
                           "EXECUTOR, AND NONE OF THEM CHANGES A THRESHOLD, A "
                           "BAND, A FRACTION OR A CRITERION.",
    "executor_position": (
        "The Executor verified each condition against COMMITTED records before "
        "producing any number. PC-3 is discharged in the committed "
        "TASK-20260729-013 archive receipt. PC-1, PC-2 and PC-4 have NO separate "
        "committed Coordinator recording; their texts exist verbatim inside the "
        "committed TASK-20260729-011 review (commit 009b90a5), which also states "
        "that any DIFFERENT reading must be recorded before dispatch. No "
        "different reading is recorded anywhere in the repository. The Executor "
        "therefore applied the sole committed candidate reading in each case, "
        "which is not a guess, and flags the missing Coordinator-side recording "
        "as a protocol observation."),
    "PC-1": {
        "subject": "RT-12, the operational reading of INV-2a",
        "status": "APPLIED from the committed review text; no separate "
                  "Coordinator recording found",
        "reading_applied": "INV-2a fires if and only if the distinct-count and "
                           "membership routine SHARED by the AP calibration leg "
                           "and the census returns a result that disagrees with "
                           "an independently computed exact value on a "
                           "known-answer input.",
        "also_recorded": "INV-2b cannot void under any reading (v2 C-8).",
        "implemented_by": "known_answer_test_shared_routine(), run in every one "
                          "of the six runs.",
    },
    "PC-2": {
        "subject": "RT-14, knife-edge disclosure",
        "status": "HONOURED as a reporting obligation",
        "recorded": "R-4's two named knife-edge cells are ILLUSTRATIVE, NOT "
                    "EXHAUSTIVE. TASK-20260729-011 found ELEVEN cells that flip "
                    "criterion-evaluable class under an ordinary even-constrained "
                    "fluctuation of measured B - six at m=2 (k=12 beta 0.500; "
                    "k=14 beta 0.350 and 0.500; k=16 beta 0.500; k=18 beta 0.275 "
                    "and 0.500) and five at m=3 (k=12 beta 0.325 and 0.375; k=14 "
                    "beta 0.275 and 0.375; k=16 beta 0.250) - and that the m=2 "
                    "beta=0.500 column is a coin flip at all four sizes and may "
                    "be dropped under R-6, taking nine evaluable columns to "
                    "eight. Every cell's evaluable_on_measured_B, "
                    "evaluable_on_B_equals_L and class_changed_on_measurement "
                    "flags are recorded in the census results.",
    },
    "PC-3": {
        "subject": "RT-13, the C-7 correction note",
        "status": "DISCHARGED IN A COMMITTED RECORD by the Coordinator",
        "where": "coordination/goals/GOAL-ECDLP-001/batches/BATCH-011/archives/"
                 "TASK-20260729-013/snapshot_commit_receipt.json, field "
                 "RT_13_DISCHARGE",
        "carried_here": "The multiset counting bound bounds distinct COVERAGE, "
                        "not decomposition MULTIPLICITY; it CLOSES NO EXPONENT "
                        "QUESTION; the TASK-20260729-002 receipt's sentence about "
                        "a sub-1/2 exponent being 'closed by counting' is "
                        "SUPERSEDED. No record in this package may quote this "
                        "derivation as an exponent result, a closure or an "
                        "impossibility claim.",
    },
    "PC-4": {
        "subject": "RT-3 routes A, B and C into O-9",
        "status": "RECORDED AS A REFERENCE ONLY - NOT APPLIED",
        "note": "PC-4 pre-registers readings for three routes into outcome "
                "branch O-9. Branch evaluation is the interpretation instrument "
                "ST-4 bars this run package from. The reference is carried so "
                "TASK-20260729-007/-008 and the Coordinator can apply it; the "
                "Executor applies nothing from it and evaluates no branch.",
    },
}


def build_manifest(run_id, ctx, status, reason, started, ended, results_path,
                   extra) -> dict:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "task_id": TASK_ID, "goal_id": GOAL_ID, "batch_id": BATCH_ID,
        "contract_in_force": {
            "note": "The contract in force is the PAIR (committed v1 blob, "
                    "committed v2 amendment). THE AMENDMENT GOVERNS WHEREVER "
                    "THEY DIFFER (v2 `precedence`).",
            "specification_path": "experiments/EXP-YIELD-001/specification.yaml",
            "specification_frozen_commit": SPEC_COMMIT,
            "specification_blob_sha1": SPEC_BLOB,
            "amendment_id": AMENDMENT_ID,
            "amendment_path": "experiments/EXP-YIELD-001/amendments/v1_to_v2.yaml",
            "amendment_commit": AMENDMENT_COMMIT,
            "specification_status_in_the_frozen_file": "review_required",
            "specification_approved_by_in_the_frozen_file": None,
            "authorization_chain": [
                "TASK-20260729-003 (independent, non-originating) returned REVISE "
                "on the frozen v1 contract - committed at b00efa32.",
                "AMD-EXP-YIELD-001-V2, the single RC-11 amendment cycle, "
                "approved_by: coordinator - committed at " + AMENDMENT_COMMIT + ".",
                "TASK-20260729-011 (independent re-review) returned PASS with four "
                "pre-execution conditions PC-1..PC-4 - committed at 009b90a5.",
                "INT-BATCH011-A lifted by BUDGET-AMEND-20260729-001 in "
                "ledger/goals/GOAL-ECDLP-001.yaml, campaign_budget."
                "maximum_batches raised 10 -> 11 on explicit user authorization.",
                "TASK-20260729-005 dispatched to the Executor by the Coordinator.",
            ],
            "residual_authorization_observation":
                "RECORDED, NOT RESOLVED BY THE EXECUTOR. No committed record "
                "sets experiment.status to `approved` or fills `approved_by` for "
                "EXP-YIELD-001: the frozen specification is immutable and still "
                "reads `review_required` / null, and the amendment states in "
                "terms that its own approval APPROVES THE AMENDMENT TEXT ONLY. "
                "The contract's own execution gate - 'the execution gate is "
                "TASK-20260729-011 returning PASS, and the batch gate is "
                "INT-BATCH011-A' - is satisfied, and that is the authority this "
                "run relies on. The unfilled status field is reported to the "
                "Coordinator rather than edited.",
            "dependency_observation":
                "TASK-20260729-004, a declared dependency of this card, is still "
                "`queued` and its archives/TASK-20260729-004/"
                "snapshot_commit_receipt.json does not exist. The substance it "
                "was to provide - a durable, hash-bound TASK-20260729-003 review "
                "- is present: both review files are committed at b00efa32. The "
                "missing receipt is recorded, not repaired.",
        },
        "command": ctx["command"],
        "command_note": "Reproduces this run exactly from the recorded revision. "
                        "stdout and stderr are tee'd in-process to stdout.log.",
        "invocation_cwd": ctx["cwd"],
        "git": ctx["git"],
        "environment": ctx["environment"],
        "inference": inference_block(),
        "input_parameters": {
            "field_bits_k": list(FIELD_BITS),
            "beta_grid": list(BETA_GRID),
            "arities": list(ARITIES),
            "criterion_evaluable_predicate_on_measured_B":
                "h = B^m/(m! p) <= 0.5 AND C_red(B) >= 500  (v2 C-2 rule R-1)",
            "ST1_per_cell_projection_cap": ST1_PROJECTION_CAP,
            "exhaustive_profile_cap_C_all": EXHAUSTIVE_PROFILE_CAP,
            "sampled_profile_draws": SAMPLED_PROFILE_DRAWS,
            "ctrl_dl_samples": CTRL_DL_SAMPLES,
            "baseline_targets_per_size": BASELINE_TARGETS,
            "occupancy_replicates_rule": "100 if C_red <= 1e4; 30 if <= 1e6; else "
                                         "10  (v2 C-14)",
            "fb_null_draws_rule": "10 if measured B <= 64 else 3  (v2 C-13)",
            "calibration_B_used": CALIB_B,
            "calibration_seeds_per_cell": CALIB_SEEDS_PER_CELL,
        },
        "seeds": {
            "master_seed_this_run": MASTER_SEEDS[run_id],
            "all_master_seeds": MASTER_SEEDS,
            "derivation": "Every per-cell / per-draw / per-seed value is "
                          "derive_seed(master, *parts) = first 8 bytes of "
                          "SHA-256('master|part|part|...') as a big-endian "
                          "integer, and every derived seed is recorded beside "
                          "the number it produced in results.json.",
            "generator": "numpy.random.Generator(PCG64) via "
                         "numpy.random.default_rng(seed)",
            "distinct_per_run": True,
        },
        "budget": {
            "wall_clock_seconds_per_run_contract": WALL_CLOCK_SECONDS_PER_RUN,
            "wall_clock_seconds_card_total": 5400,
            "maximum_memory_gb": MAXIMUM_MEMORY_GB,
            "maximum_runs": 6,
            "measured_wall_clock_seconds": ended - started,
            "measured_peak_rss_bytes": ru.ru_maxrss,
            "measured_peak_rss_gb": ru.ru_maxrss / 1024 ** 3,
            "measured_user_cpu_seconds": ru.ru_utime,
            "measured_system_cpu_seconds": ru.ru_stime,
            "budget_bound": extra.get("budget_bound", False),
        },
        "stdout_location": "stdout.log",
        "stderr_location": "stdout.log (stderr is tee'd into the same file; see "
                           "DEV-1 - the declared artifact set has no stderr file)",
        "raw_results_location": os.path.basename(results_path),
        "timestamps": {
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "ended_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ended)),
            "started_epoch": started, "ended_epoch": ended,
        },
        "terminal_status": status,
        "validity_status": extra.get("validity_status"),
        "validity_reason": reason,
        "invalidation_rules_fired": extra.get("invalidation_fired", []),
        "invalidation_rules_evaluated": extra.get("invalidation", {}),
        "certificate": extra.get("certificate", {
            "kind": "none",
            "reason": "PURE MEASUREMENT RUN. It claims no discrete-logarithm "
                      "solve and no factor-base relation, so there is nothing to "
                      "certify. The only run in this package that claims solves "
                      "is RUN-YIELD-001-BASELINE-RHO-BSGS, whose certificates are "
                      "re-verified by code independent of the solver."}),
        "claim_tier": "toy",
        "claim_ceiling_carried_verbatim":
            "EXP-YIELD-001 MOVES NO EXPONENT AND IS AN EXPONENT-DECIDING SCREEN, "
            "EXPRESSLY NOT AN EXPONENT-TARGETING MECHANISM UNDER "
            "docs/target-result-profile.md RULE A1, AND NO DOWNSTREAM RECORD MAY "
            "QUOTE IT AS TARGET-CLASS. It is not an attack, not an attack "
            "improvement, not a cryptanalytic result, not a closure, and not an "
            "impossibility claim. Its CLAIM TIER IS CAPPED AT TOY. It CAN MEET NO "
            "COMPLETION CRITERION OF GOAL-ECDLP-001 UNDER ANY OUTCOME. A TIMEOUT, "
            "CRASH, RESOURCE EXHAUSTION OR IMPLEMENTATION FAILURE IS "
            "INFRASTRUCTURE SIGNAL AND IS NEVER NEGATIVE EVIDENCE about the yield "
            "heuristic.",
        "ST_4_no_interpretation":
            "This run record contains OBSERVATIONS ONLY. It does not state which "
            "of outcomes (a), (b) or (c) obtained, evaluates no branch of the v2 "
            "outcome_disposition_table, assigns no evidence strength, writes no "
            "evidence or decision record, and touches no hypothesis status.",
        "instrument_independence_attested":
            "No Groebner basis, no polynomial system solve, no summation "
            "polynomial. harness/endomorphism_la.py and every other part of the "
            "EXP-STR-002 instrument were neither imported nor read into this "
            "driver. Nothing under harness/ or tools/ was modified.",
        "execution_history": EXECUTION_HISTORY,
        "pre_execution_conditions": PRE_EXECUTION_CONDITIONS,
        "protocol_deviations": PROTOCOL_DEVIATIONS,
        "protocol_observations": extra.get("protocol_observations", []),
        "implementation_notes": IMPLEMENTATION_NOTES,
        "required_artifacts_this_run": ["manifest.json", "results.json",
                                        "stdout.log"],
    }


# --------------------------------------------------------------------------
# 10.  Summary (derived, never hand-entered).
# --------------------------------------------------------------------------

def ols_fit(xs, ys):
    n = len(xs)
    xb, yb = sum(xs) / n, sum(ys) / n
    sxx = sum((x - xb) ** 2 for x in xs)
    sxy = sum((x - xb) * (y - yb) for x, y in zip(xs, ys))
    slope = sxy / sxx
    icept = yb - slope * xb
    res = [y - (icept + slope * x) for x, y in zip(xs, ys)]
    df = n - 2
    if df <= 0:
        return slope, icept, None, df, None, None
    s2 = sum(r * r for r in res) / df
    se = math.sqrt(s2 / sxx)
    t = T_95.get(df)
    hw = t * se if t else None
    return slope, icept, se, df, t, hw


def summarize(exp_root: str, log=print) -> dict:
    runs_dir = os.path.join(exp_root, "runs")
    raw = {}
    for rid in RUN_IDS:
        path = os.path.join(runs_dir, rid, "results.json")
        with open(path) as fh:
            raw[rid] = json.load(fh)
        log("  loaded %s (%d bytes)" % (rid, os.path.getsize(path)))

    cells = {}
    for rid in ("RUN-YIELD-001-CENSUS-M2", "RUN-YIELD-001-CENSUS-M3"):
        for c in raw[rid].get("cells", []):
            cells[(c["k"], round(c["beta"], 3), c["m"])] = c
    nulls = {(c["k"], round(c["beta"], 3), c["m"]): c
             for c in raw["RUN-YIELD-001-NULL-RANDOM-SUMSET"].get("cells", [])}
    fbn = {(c["k"], round(c["beta"], 3), c["m"]): c
           for c in raw["RUN-YIELD-001-NULL-UNIFORM-FB"].get("cells", [])}

    rows = []
    for key in sorted(cells):
        c = cells[key]
        nu = nulls.get(key)
        fb = fbn.get(key)
        rel_sd = nu["antipodal"]["relative_sd"] if nu else None
        noise = bool(nu["NOISE_LIMITED"]) if nu else None
        std_dev = None
        if nu and nu["antipodal"]["sd"] > 0:
            std_dev = (c["S_m"] - c["P_pred"]) / nu["antipodal"]["sd"]
        rows.append({
            "k": c["k"], "p": c["p"], "N": c["N"], "beta": c["beta"], "m": c["m"],
            "L": c["L"], "B": c["B"], "B_over_L": c["B_over_L"],
            "C_all": c["C_all"], "C_B_m": c["C_B_m"], "C_red": c["C_red"],
            "h": c["h_heuristic_B_m_over_m_fact_p"],
            "h_alt_on_N": c["h_alt_B_m_over_m_fact_N"],
            "S_m": c["S_m"], "S_m_over_N": c["S_m_over_N"],
            "S_m_over_N_wilson_95": c["S_m_over_N_wilson_95"],
            "P_pred": c["P_pred"],
            "R": c["PM2_R"], "R_max": c["R_max"],
            "E": c["PM3_E"], "E_max": c["E_max"], "E_floor": c["E_floor"],
            "label": c["label_PM1_PM2_PM3"],
            "evaluable_on_measured_B": c["evaluable_on_measured_B"],
            "evaluable_on_B_equals_L": c["evaluable_on_B_equals_L"],
            "class_changed_on_measurement": c["class_changed_on_measurement"],
            "identity_multisets": c["identity_multisets"]["count"],
            "collision_profile_label": (c["collision_profile"] or {}).get("label"),
            "collision_max_load": (c["collision_profile"] or {}).get("max_load"),
            "null_empirical_mean": nu["antipodal"]["mean"] if nu else None,
            "null_empirical_sd": nu["antipodal"]["sd"] if nu else None,
            "null_relative_sd": rel_sd,
            "null_replicates": nu["replicates"] if nu else None,
            "null_recovers_P_pred_within_3sd":
                nu["INV_4_within_3_empirical_sd"] if nu else None,
            "NOISE_LIMITED": noise,
            "standardized_deviation_S_m_minus_P_pred_over_null_sd": std_dev,
            "E_randomFB_mean": fb["E_randomFB_mean"] if fb else None,
            "E_randomFB_sd": fb["E_randomFB_sd"] if fb else None,
            "E_randomFB_draws": fb["draws"] if fb else None,
            "in_band_0_90_to_1_10": bool(0.90 <= c["PM3_E"] <= 1.10),
            "band_one_sided_high_E_max_below_1_10":
                c["band_one_sided_high_E_max_below_1_10"],
        })

    V = [r for r in rows if r["evaluable_on_measured_B"] and r["NOISE_LIMITED"] is False]
    n_eval = len(V)
    out_cells = [r for r in V if not r["in_band_0_90_to_1_10"]]
    out_low = [r for r in out_cells if r["E"] < 0.90]
    out_high = [r for r in out_cells if r["E"] > 1.10]

    columns = {}
    for r in V:
        columns.setdefault((r["m"], r["beta"]), []).append(r)
    colrecs = []
    for (m, beta), rs in sorted(columns.items()):
        rs = sorted(rs, key=lambda x: x["k"])
        rec = {"m": m, "beta": beta, "sizes_in_realised_set": len(rs),
               "k_values": [x["k"] for x in rs],
               "E_values": [x["E"] for x in rs],
               "is_evaluable_column_at_least_3_sizes": len(rs) >= 3}
        if len(rs) >= 3:
            xs = [math.log(x["p"]) for x in rs]
            ys = [math.log(x["E"]) for x in rs]
            slope, icept, se, df, t, hw = ols_fit(xs, ys)
            rec.update({
                "PM4_ols_slope_log_E_vs_log_p": slope,
                "intercept": icept, "standard_error": se,
                "residual_degrees_of_freedom": df, "t_multiplier_95": t,
                "half_width_95": hw,
                "ci95": [slope - hw, slope + hw] if hw is not None else None,
                "abs_slope_at_most_0_05": bool(abs(slope) <= 0.05),
                "ci95_contains_zero": bool(hw is not None
                                           and (slope - hw) <= 0 <= (slope + hw)),
                "E_non_increasing_across_sizes":
                    all(rec["E_values"][i] >= rec["E_values"][i + 1]
                        for i in range(len(rec["E_values"]) - 1)),
                "E_non_decreasing_across_sizes":
                    all(rec["E_values"][i] <= rec["E_values"][i + 1]
                        for i in range(len(rec["E_values"]) - 1)),
                "label": "DERIVED_FIT over DETERMINED inputs",
            })
        colrecs.append(rec)

    # tail checks (v1 tail_checks) - reported, never a criterion
    stds = [r["standardized_deviation_S_m_minus_P_pred_over_null_sd"]
            for r in V
            if r["standardized_deviation_S_m_minus_P_pred_over_null_sd"] is not None]
    tail = {}
    if stds:
        n = len(stds)
        gum = math.sqrt(2 * math.log(n)) - (math.log(math.log(n))
                                            + math.log(4 * math.pi)) / (
                  2 * math.sqrt(2 * math.log(n)))
        loge = [abs(math.log(r["E"])) for r in V]
        tail = {
            "n_standardized_cells": n,
            "max_abs_standardized_deviation": max(abs(s) for s in stds),
            "gumbel_expected_max_of_n_standard_normals": gum,
            "max_exceeds_gumbel_expectation":
                bool(max(abs(s) for s in stds) > gum),
            "max_abs_log_E": max(loge),
            "cell_of_max_abs_log_E": [
                {"k": r["k"], "beta": r["beta"], "m": r["m"], "E": r["E"]}
                for r in V if abs(math.log(r["E"])) == max(loge)][:1],
            "bulk_standardized_mean": float(np.mean(stds)),
            "bulk_standardized_sd": float(np.std(stds, ddof=1)) if n > 1 else None,
            "bulk_note": "Compared against the standard normal, per v1 "
                         "tail_checks item 3. REPORTED, NOT A CRITERION.",
        }
    maxload = [{"k": r["k"], "beta": r["beta"], "m": r["m"],
                "max_load": r["collision_max_load"],
                "C_all_over_N": r["C_all"] / r["N"],
                "label": r["collision_profile_label"]}
               for r in rows if r["collision_max_load"] is not None]

    # INV-5 comparison statistics only (DEV-6: no firing determination here)
    inv5 = []
    for r in V:
        if r["E_randomFB_mean"] is None:
            continue
        inv5.append({
            "k": r["k"], "beta": r["beta"], "m": r["m"],
            "abs_E_interval_minus_1": abs(r["E"] - 1.0),
            "abs_E_randomFB_mean_minus_1": abs(r["E_randomFB_mean"] - 1.0),
            "deviation_shrinks_under_randomisation_strict_reading":
                bool(abs(r["E_randomFB_mean"] - 1.0) < abs(r["E"] - 1.0)),
        })
    n_no_shrink = sum(1 for x in inv5
                      if not x["deviation_shrinks_under_randomisation_strict_reading"])
    n_no_shrink_outofband = sum(
        1 for x, r in zip(inv5, [r for r in V if r["E_randomFB_mean"] is not None])
        if not x["deviation_shrinks_under_randomisation_strict_reading"]
        and not r["in_band_0_90_to_1_10"])

    census_ops = {}
    for rid in ("RUN-YIELD-001-CENSUS-M2", "RUN-YIELD-001-CENSUS-M3"):
        for c in raw[rid].get("cells", []):
            census_ops[c["k"]] = census_ops.get(c["k"], 0) + \
                c["modular_additions_contract_model"]
    base = {r["k"]: r for r in raw["RUN-YIELD-001-BASELINE-RHO-BSGS"].get("per_size", [])}
    ratio = []
    for k, ops in sorted(census_ops.items()):
        if k in base:
            rho = base[k]["rho_walk_steps_mean_MEASURED"]
            ratio.append({
                "k": k,
                "census_group_equivalent_operations_MEASURED_MODEL_UNIT":
                    ops + base[k]["census_dl_table_point_additions_MEASURED"],
                "of_which_dl_table_point_additions":
                    base[k]["census_dl_table_point_additions_MEASURED"],
                "measured_rho_walk_steps_mean": rho,
                "census_over_rho": (ops + base[k][
                    "census_dl_table_point_additions_MEASURED"]) / rho,
                "bsgs_ops_mean_MEASURED": base[k]["bsgs_ops_mean_MEASURED"],
                "bsgs_memory_stored_group_elements_MEASURED":
                    base[k]["bsgs_memory_stored_group_elements_MEASURED"],
            })

    manifests = {}
    for rid in RUN_IDS:
        with open(os.path.join(runs_dir, rid, "manifest.json")) as fh:
            mm = json.load(fh)
        manifests[rid] = {
            "terminal_status": mm["terminal_status"],
            "validity_status": mm["validity_status"],
            "invalidation_rules_fired": mm.get("invalidation_rules_fired", []),
            "validity_reason": mm["validity_reason"],
            "wall_clock_seconds": mm["budget"]["measured_wall_clock_seconds"],
            "peak_rss_gb": mm["budget"]["measured_peak_rss_gb"],
            "certificate_kind": mm["certificate"]["kind"],
        }

    calib = raw["RUN-YIELD-001-CALIB-AP"]
    summary = {
        "schema": "crypto.autoresearch.experiment_summary.v1",
        "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID,
        "derived_note": "EVERY NUMBER IN THIS FILE IS COMPUTED BY summarize() FROM "
                        "THE SIX runs/*/results.json FILES. NOTHING IS "
                        "HAND-ENTERED. Re-run `python3 "
                        "experiments/EXP-YIELD-001/driver/yield_census.py "
                        "--summarize` to reproduce it byte for byte.",
        "ST_4_no_interpretation":
            "OBSERVATIONS ONLY. No branch of the v2 outcome_disposition_table is "
            "evaluated here, no outcome (a)/(b)/(c) is asserted, no evidence "
            "strength is assigned and no hypothesis status is touched. The "
            "statistics below are the pre-registered metrics PM-1..PM-4, the "
            "controls and the tail checks, and nothing more.",
        "contract_in_force": {
            "specification_frozen_commit": SPEC_COMMIT,
            "specification_blob_sha1": SPEC_BLOB,
            "amendment_id": AMENDMENT_ID,
            "amendment_commit": AMENDMENT_COMMIT,
            "amendment_governs_where_they_differ": True,
            "reviews": REVIEW_TASKS,
        },
        "runs": manifests,
        "instances": raw["RUN-YIELD-001-CENSUS-M2"].get("instances", []),
        "census_cells_measured": len(rows),
        "census_cells_planned": len(FIELD_BITS) * len(BETA_GRID) * len(ARITIES),
        "cells_skipped": (raw["RUN-YIELD-001-CENSUS-M2"].get("skipped_cells", [])
                          + raw["RUN-YIELD-001-CENSUS-M3"].get("skipped_cells", [])),
        "realised_evaluable_set": {
            "n_evaluable_on_measured_B": sum(1 for r in rows
                                             if r["evaluable_on_measured_B"]),
            "n_evaluable_on_B_equals_L": sum(1 for r in rows
                                             if r["evaluable_on_B_equals_L"]),
            "n_class_changed_on_measurement": sum(
                1 for r in rows if r["class_changed_on_measurement"]),
            "cells_that_changed_class": [
                {"k": r["k"], "beta": r["beta"], "m": r["m"], "B": r["B"],
                 "L": r["L"], "h": r["h"], "C_red": r["C_red"],
                 "evaluable_on_measured_B": r["evaluable_on_measured_B"],
                 "evaluable_on_B_equals_L": r["evaluable_on_B_equals_L"]}
                for r in rows if r["class_changed_on_measurement"]],
            "n_eval_after_noise_limited_exclusion": n_eval,
            "noise_limited_exclusions": [
                {"k": r["k"], "beta": r["beta"], "m": r["m"],
                 "null_relative_sd": r["null_relative_sd"],
                 "null_replicates": r["null_replicates"], "P_pred": r["P_pred"]}
                for r in rows if r["NOISE_LIMITED"]],
            "R_7_drift_disclosure": {
                "amendment_expectation": 44,
                "realised": sum(1 for r in rows if r["evaluable_on_measured_B"]),
                "drift": sum(1 for r in rows if r["evaluable_on_measured_B"]) - 44,
                "drift_exceeds_4_cells":
                    bool(abs(sum(1 for r in rows
                                 if r["evaluable_on_measured_B"]) - 44) > 4),
                "note": "v2 C-2 rule R-7: a drift above 4 cells is recorded as a "
                        "PROTOCOL OBSERVATION naming every cell that moved. It is "
                        "not a deviation, not an invalidation and not a stop.",
            },
        },
        "cells": rows,
        "out_of_band": {
            "n_eval_denominator": n_eval,
            "n_out": len(out_cells),
            "n_out_low_E_below_0_90": len(out_low),
            "n_out_high_E_above_1_10": len(out_high),
            "fraction_of_n_eval": (len(out_cells) / n_eval) if n_eval else None,
            "one_third_of_n_eval": n_eval / 3 if n_eval else None,
            "cells": [{"k": r["k"], "beta": r["beta"], "m": r["m"], "B": r["B"],
                       "C_red": r["C_red"], "E": r["E"], "E_max": r["E_max"],
                       "E_floor": r["E_floor"],
                       "null_sd": r["null_empirical_sd"],
                       "replicates": r["null_replicates"],
                       "standardized_deviation":
                           r["standardized_deviation_S_m_minus_P_pred_over_null_sd"]}
                      for r in out_cells],
            "note": "COUNTS AND FRACTIONS ONLY. No outcome branch is evaluated "
                    "(ST-4).",
        },
        "PM4_columns": colrecs,
        "tail_checks": tail,
        "max_load_observations": maxload,
        "INV_5_comparison_statistics": {
            "per_cell": inv5,
            "n_cells_compared": len(inv5),
            "n_not_shrinking_strict_reading": n_no_shrink,
            "n_not_shrinking_and_out_of_band": n_no_shrink_outofband,
            "firing_determination": None,
            "why_no_determination": (
                "DEV-6. INV-5's trigger turns on 'shrink', which the contract "
                "never quantifies, and v2 C-13 gives its disposition a THREE-WAY "
                "reading the Executor may not choose among. Statistics are "
                "reported; the determination belongs to TASK-20260729-007/-008 "
                "and the Coordinator."),
        },
        "occupancy_null_contrast_arm":
            raw["RUN-YIELD-001-NULL-RANDOM-SUMSET"].get("contrast_arm_summary"),
        "calibration_leg": {
            "cells": [{k: v for k, v in c.items() if k != "per_seed"}
                      for c in calib.get("cells", [])],
            "trend_clauses": calib.get("trend_clauses"),
            "INV_2a": calib.get("INV_2a"),
            "INV_2b": calib.get("INV_2b"),
            "census_void_verdict": ("VOID" if calib.get("INV_2a", {}).get("fired")
                                    else "NOT-VOID"),
            "census_void_verdict_basis":
                "v2 C-8: ONLY INV-2a - a defect in the routine SHARED with the "
                "census - can void. INV-2b is an instrument note and does not "
                "void census data.",
            "convention_difference": calib.get("convention_warning"),
        },
        "baselines": raw["RUN-YIELD-001-BASELINE-RHO-BSGS"].get("per_size", []),
        "census_versus_baseline_operations": ratio,
        "controls_rollup": {
            "CTRL_DL": [c for rid in ("RUN-YIELD-001-CENSUS-M2",
                                      "RUN-YIELD-001-CENSUS-M3")
                        for c in raw[rid].get("controls", [])
                        if c.get("control") == "CTRL-DL"],
            "INV_3_fired": any(c.get("INV_3_fired") for rid in
                               ("RUN-YIELD-001-CENSUS-M2", "RUN-YIELD-001-CENSUS-M3")
                               for c in raw[rid].get("controls", [])
                               if c.get("control") == "CTRL-DL"),
            "INV_1_fired_any_cell": any(c["INV_1"]["fired"] for rid in
                                        ("RUN-YIELD-001-CENSUS-M2",
                                         "RUN-YIELD-001-CENSUS-M3")
                                        for c in raw[rid].get("cells", [])),
            "INV_4": raw["RUN-YIELD-001-NULL-RANDOM-SUMSET"].get("INV_4"),
            "INV_4_failed_any_cell": [
                {"k": r["k"], "beta": r["beta"], "m": r["m"]}
                for r in rows if r["null_recovers_P_pred_within_3sd"] is False],
            "INV_6_fired_any_size": any(
                s["INV_6_rho_more_than_20pc_below_model"]
                for s in raw["RUN-YIELD-001-BASELINE-RHO-BSGS"].get("per_size", [])),
            "CTRL_EXHAUSTIVE_TRUTH": [
                {"k": c["k"], "beta": c["beta"], "m": c["m"],
                 **c["CTRL_EXHAUSTIVE_TRUTH"]}
                for c in raw["RUN-YIELD-001-CENSUS-M3"].get("cells", [])
                if "CTRL_EXHAUSTIVE_TRUTH" in c],
            "shared_routine_known_answer_tests": {
                rid: [c for c in raw[rid].get("controls", [])
                      if c.get("routine") == SHARED_ROUTINE_NAME]
                for rid in RUN_IDS},
        },
        "pre_execution_conditions": PRE_EXECUTION_CONDITIONS,
        "protocol_deviations": PROTOCOL_DEVIATIONS,
        "implementation_notes": IMPLEMENTATION_NOTES,
        "claim_tier": "toy",
        "scale_relevance_carried_verbatim":
            "At most 18 field bits, m at most 3, one curve per size, one interval "
            "anchor, one implementation, one budget. NOTHING MEASURED HERE IS "
            "EVIDENCE ABOUT CRYPTOGRAPHIC-SIZE CURVES IN EITHER DIRECTION, and "
            "toy-scale agreement is TOY-SCALE VALIDATION OF A HEURISTIC and must "
            "never be presented as crypto-scale validation. FOUR FIELD SIZES ON "
            "ONE CURVE EACH IS NOT REPLICATION - it is a size series, and this is "
            "A SINGLE UNREPLICATED RUN SET.",
    }
    return summary


# --------------------------------------------------------------------------
# 11.  CLI.
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", choices=RUN_IDS)
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--out-root", default=None,
                    help="override the experiment directory (used only for "
                         "off-repository development; the declared runs use the "
                         "default)")
    ap.add_argument("--wall-clock-cap", type=int,
                    default=WALL_CLOCK_SECONDS_PER_RUN)
    args = ap.parse_args(argv)

    here = os.path.dirname(os.path.abspath(__file__))
    repo = args.repo_root or os.path.abspath(os.path.join(here, "..", "..", ".."))
    exp_root = args.out_root or os.path.join(repo, "experiments", EXPERIMENT_ID)

    if args.summarize:
        os.makedirs(os.path.join(exp_root, "results"), exist_ok=True)
        s = summarize(exp_root)
        path = os.path.join(exp_root, "results", "summary.json")
        with open(path, "w") as fh:
            json.dump(s, fh, indent=1, sort_keys=False)
            fh.write("\n")
        print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))
        return 0

    if not args.run:
        ap.error("one of --run or --summarize is required")

    run_id = args.run
    rundir = os.path.join(exp_root, "runs", run_id)
    os.makedirs(rundir, exist_ok=True)
    stdout_path = os.path.join(rundir, "stdout.log")
    results_path = os.path.join(rundir, "results.json")
    manifest_path = os.path.join(rundir, "manifest.json")

    apply_memory_cap(MAXIMUM_MEMORY_GB)

    fh = open(stdout_path, "w")
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = Tee(old_out, fh)
    sys.stderr = Tee(old_err, fh)
    started = time.time()
    status = "failed_implementation"
    reason = "run did not reach its terminal writer"
    payload = {}
    extra = {}
    command = "python3 %s --run %s" % (
        os.path.relpath(os.path.abspath(__file__), repo), run_id)
    # PRE-RUN provenance: the revision and dirty state this run executed AT,
    # captured before any artifact of this run exists.
    ctx_meta = {
        "command": command,
        "cwd": os.getcwd(),
        "git": git_state(repo),
        "environment": environment_block(repo, os.path.abspath(__file__)),
    }
    try:
        print("EXP-YIELD-001 driver | run %s" % run_id)
        print("  started %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                             time.gmtime(started)))
        print("  command: %s" % command)
        print("  cwd: %s" % os.getcwd())
        print("  contract: v1 blob %s at %s, AS AMENDED BY %s (the amendment "
              "governs)" % (SPEC_BLOB[:12], SPEC_COMMIT[:8], AMENDMENT_ID))
        print("  master seed: %d ; wall-clock cap %d s ; memory cap %d GB"
              % (MASTER_SEEDS[run_id], args.wall_clock_cap, MAXIMUM_MEMORY_GB))
        print("  ST-4: OBSERVATIONS ONLY. No outcome branch is evaluated here.")

        deadline = started + args.wall_clock_cap
        cache = {}

        def get_instance(k):
            if k not in cache:
                cache[k] = Instance(k, log=print)
            return cache[k]

        ctx = {
            "repo": repo, "command": command, "cwd": ctx_meta["cwd"],
            "git": ctx_meta["git"], "environment": ctx_meta["environment"],
            "instance": get_instance,
            "deadline_passed": lambda: time.time() > deadline,
            "log": print,
        }
        payload = RUN_DISPATCH[run_id](run_id, ctx)
        budget_bound = ctx["deadline_passed"]()
        extra["budget_bound"] = budget_bound

        # --- terminal status and validity
        inval = {}
        if run_id.startswith("RUN-YIELD-001-CENSUS"):
            inval["INV_1_fired_cells"] = [
                {"k": c["k"], "beta": c["beta"], "m": c["m"], "detail": c["INV_1"]}
                for c in payload["cells"] if c["INV_1"]["fired"]]
            inval["INV_3_fired"] = any(c.get("INV_3_fired")
                                       for c in payload["controls"]
                                       if c.get("control") == "CTRL-DL")
        if run_id == "RUN-YIELD-001-NULL-RANDOM-SUMSET":
            inval["INV_4"] = payload["INV_4"]
            if payload["INV_4"]["fired"]:
                extra["protocol_observations"] = [{
                    "id": "OBS-INV4",
                    "severity": "material, and the single most consequential "
                                "observation in this package",
                    "text": "INV-4 FIRED. CTRL-NULL-SUMSET, run exactly as v2 C-4 "
                            "specifies it, does NOT reproduce P_pred within 3 "
                            "empirical standard deviations at %d of the %d "
                            "criterion-evaluable cells it was run at. Per v1 "
                            "INV-4 the consequence is that EVERY E VALUE IS VOID "
                            "RATHER THAN NEGATIVE, and per P0 of the v2 "
                            "outcome_disposition_table no outcome branch is "
                            "evaluated. THE EXECUTOR RECORDS THIS AND DOES NOT "
                            "ACT ON IT: the protocol was executed as written, "
                            "nothing was repaired in flight, and the disposition "
                            "belongs to TASK-20260729-007/-008 and the "
                            "Coordinator. The derived diagnostic in "
                            "results.json INV_4.derived_diagnostic shows the "
                            "shortfall is exactly P_pred's own |S_(m-2)| "
                            "e^-lambda term, which the specified process does "
                            "not generate."
                            % (payload["INV_4"]["n_failed"],
                               payload["INV_4"]["cells_evaluated"]),
                }]
        if run_id == "RUN-YIELD-001-CALIB-AP":
            inval["INV_2a"] = payload["INV_2a"]
            inval["INV_2b"] = payload["INV_2b"]
        if run_id == "RUN-YIELD-001-BASELINE-RHO-BSGS":
            inval["INV_6_fired_sizes"] = [
                s["k"] for s in payload["per_size"]
                if s["INV_6_rho_more_than_20pc_below_model"]]
            inval["all_certificates_verified"] = all(
                s["all_rho_certificates_verified"]
                and s["all_bsgs_certificates_verified"]
                and s["all_solutions_match_dl_table"]
                for s in payload["per_size"])
            extra["certificate"] = payload["certificate"]
            extra["certificate"]["all_verified"] = inval["all_certificates_verified"]
        kats = [c for c in payload.get("controls", [])
                if c.get("routine") == SHARED_ROUTINE_NAME]
        inval["shared_routine_known_answer_test_passed"] = all(
            c["all_agree"] for c in kats) if kats else None
        extra["invalidation"] = inval
        fired = []
        if inval.get("INV_1_fired_cells"):
            fired.append("INV-1")
        if inval.get("INV_2a", {}).get("fired"):
            fired.append("INV-2a")
        if inval.get("INV_2b", {}).get("fired"):
            fired.append("INV-2b")
        if inval.get("INV_3_fired"):
            fired.append("INV-3")
        if inval.get("INV_4", {}).get("fired"):
            fired.append("INV-4")
        if inval.get("INV_6_fired_sizes"):
            fired.append("INV-6")
        if inval.get("shared_routine_known_answer_test_passed") is False:
            fired.append("INV-2a")
        extra["invalidation_fired"] = fired

        hard_fail = (inval.get("INV_3_fired") is True
                     or inval.get("shared_routine_known_answer_test_passed") is False
                     or bool(inval.get("INV_1_fired_cells"))
                     or (run_id == "RUN-YIELD-001-BASELINE-RHO-BSGS"
                         and inval.get("all_certificates_verified") is False))
        if hard_fail:
            status = "completed_invalid"
            extra["validity_status"] = "invalid"
            reason = ("An invalidation rule fired: see "
                      "invalidation_rules_evaluated. AN INVALID RUN IS NOT "
                      "EVIDENCE and its invalidity is never a negative "
                      "mathematical result.")
        elif budget_bound:
            status = "cancelled_by_budget"
            extra["validity_status"] = "partial"
            reason = ("ST-2 RUN CAP bound. Cells reached are valid measurements; "
                      "cells not reached are named in results.json under "
                      "skipped_cells and are NOT reported as measurements.")
        elif fired:
            status = "completed_valid"
            extra["validity_status"] = "valid"
            reason = ("All planned work of this run completed inside the budget "
                      "and the run's OWN measurements are sound. HOWEVER the "
                      "following invalidation rule(s) FIRED and are recorded in "
                      "invalidation_rules_evaluated: %s. Their consequences fall "
                      "on the metrics they govern, not on this run's raw "
                      "measurements, and the dispositions belong to "
                      "TASK-20260729-007/-008 and the Coordinator. AN INVALID OR "
                      "VOID METRIC IS NOT EVIDENCE, and it is never a negative "
                      "mathematical result." % ", ".join(fired))
        else:
            status = "completed_valid"
            extra["validity_status"] = "valid"
            reason = ("All planned work of this run completed inside the budget; "
                      "no invalidation rule fired in this run.")
        print("  terminal status: %s" % status)
    except MemoryError:
        status = "resource_exhaustion"
        reason = "MemoryError against the 8 GB cap. INFRASTRUCTURE SIGNAL, never negative evidence."
        traceback.print_exc()
    except KeyboardInterrupt:
        status = "cancelled_by_budget"
        reason = "Interrupted. INFRASTRUCTURE SIGNAL, never negative evidence."
        traceback.print_exc()
    except Exception as exc:                                 # noqa: BLE001
        status = "failed_implementation"
        reason = "Unhandled exception: %r. INFRASTRUCTURE/IMPLEMENTATION SIGNAL, never negative evidence." % (exc,)
        traceback.print_exc()
    finally:
        ended = time.time()
        payload.setdefault("run_id", run_id)
        payload["terminal_status"] = status
        payload["validity_reason"] = reason
        payload["elapsed_seconds"] = ended - started
        try:
            with open(results_path, "w") as rf:
                json.dump(payload, rf, indent=1, sort_keys=False, default=str)
                rf.write("\n")
        except Exception:
            traceback.print_exc()
        try:
            man = build_manifest(run_id, ctx_meta, status, reason, started, ended,
                                 results_path, extra)
            with open(manifest_path, "w") as mf:
                json.dump(man, mf, indent=1, sort_keys=False, default=str)
                mf.write("\n")
        except Exception:
            traceback.print_exc()
        print("  ended %s (%.1f s)" % (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ended)),
            ended - started))
        sys.stdout, sys.stderr = old_out, old_err
        fh.close()
    return 0 if status == "completed_valid" else 1


if __name__ == "__main__":
    sys.exit(main())
