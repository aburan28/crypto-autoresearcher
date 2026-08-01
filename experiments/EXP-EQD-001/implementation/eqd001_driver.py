#!/usr/bin/env python3
"""EXP-EQD-001 driver: the frozen half-arity Semaev fibre-invariant map INT-2,
its matched random-factor-base null, the CAL-EQD-1 calibration arm, and the
(dormant here) real arm RUN-EQD-001-real.

BINDING CONTRACT: experiments/EXP-EQD-001/specification.yaml, hash-bound at
commit 7792331bca3f64db9ae296fbc1465bb3912998d4 (sha256
295d85c748cf9d1d14e2746d3067fbbbc0a7fc9ebd8b62ccbdbe021a6dc99431).

ATS-1 clause 5: THIS FILE IS AUTHORED COMPLETE AT TASK-20260801-021, INCLUDING
THE REAL-ARM ENTRY POINT THAT IS NOT EXECUTED THERE. Its sha256 is bound by the
TASK-20260801-022 snapshot and TASK-20260801-027 must execute the IDENTICAL
file with no edit. Every number the real arm needs that does not exist yet (the
calibrated thresholds, the certified delta, the retained statistic set) is read
at run time from experiments/EXP-EQD-001/reading_rule.yaml, which
TASK-20260801-023 freezes. NOTHING in this file may be edited to supply them.

ATS-1 clause 2: the calibration arm never sees the real data, structurally.
`deterministic_factor_base()` is the ONLY function in this file that touches
the frozen deterministic factor base; it sets the module-level tripwire
`_REAL_DATA_TOUCHED`, and `run_calibration()` asserts that the tripwire is
still False when it finishes and records that fact in its output.

ATS-1 clause 3: the calibration output is NON-EVIDENTIAL about H-EQD-001,
HEUR-DS-1 and H-SMTH-001, in either direction. This driver therefore freezes no
threshold, states no disposition, and selects no branch of any reading rule. It
emits measured numbers.

What this driver does NOT contain, by contract: no factorization, no largest
prime factor, no smoothness indicator, no Dickman evaluation, no u ladder, no
search arm, no relation harvest, no claw table, no charged unit, no cost
identity, no R, and no timing decision variable. `wall_seconds` is recorded for
budget accounting only.

Usage
-----
  python3 eqd001_driver.py --mode calib --out-run <dir> --out-results <dir>
  python3 eqd001_driver.py --mode real  --out-run <dir> --out-results <dir> \
      --reading-rule experiments/EXP-EQD-001/reading_rule.yaml \
      --approval-receipt <TASK-20260801-026 snapshot_commit_receipt.json>

`--mode real` refuses to start unless the approval receipt records
APPROVAL_DETERMINATION == "APPROVED" and the frozen reading rule exists.
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
from datetime import datetime, timezone

import numpy as np

# --------------------------------------------------------------------------
# Frozen constants. Every one of these is fixed by
# experiments/EXP-EQD-001/specification.yaml and none may be tuned here.
# --------------------------------------------------------------------------
EXPERIMENT_ID = "EXP-EQD-001"
SPEC_PATH = "experiments/EXP-EQD-001/specification.yaml"
SPEC_SHA256_AT_FREEZE = (
    "295d85c748cf9d1d14e2746d3067fbbbc0a7fc9ebd8b62ccbdbe021a6dc99431")

MASTER_SEED = 2301                       # replication.master_seed
FIELD_BITS = (16, 20)                    # independent_variables.field_bits
BFB = 512                                # factor_base.Bfb
N_PER_SAMPLE_SET = BFB * (BFB - 1) // 2  # 130816, diagonal excluded BY CONSTRUCTION
RESOLUTION_LADDER_K = (16, 64)           # statistic_family.resolution_ladder_K
DELTA_LADDER = (0.005, 0.01, 0.02, 0.05, 0.10)   # OBJ-PLANT-delta frozen ladder
M_PAIRS = 200                            # CAL-1 replicate pairs per bit size
R_REPS = 20                              # CAL-2 / CAL-3 replicates
S3_CONTROL_SAMPLE = 1000                 # CTRL-EQD-S3 half-tuples per cell

# Stream offsets, replication.seed_policy. The real-arm null stream is DISJOINT
# from every calibration stream and is used by real mode only.
STREAM_OFFSETS = {
    "calibration_null": 10000,
    "calibration_plant": 20000,
    "calibration_independent_pair": 30000,
    "calibration_uniform_pair": 40000,
    "real_arm_null": 50000,
}

# Tripwire for ATS-1 clause 2. Flipped only by deterministic_factor_base().
_REAL_DATA_TOUCHED = False


# --------------------------------------------------------------------------
# Deterministic stream machinery. Every draw is individually reproducible.
# --------------------------------------------------------------------------
class Stream:
    """A named, seeded, index-addressable source of per-draw seeds.

    draw_seed(k) = int(sha256("<seed>:<name>:<k>")[:16], 16). Each draw index
    yields an independent numpy Generator, so any single replicate can be
    regenerated exactly without replaying the ones before it. The stream hash
    is sha256 over the canonical newline-joined "<name>:<seed>:<k>:<draw_seed>"
    record of every seed actually consumed, in consumption order.
    """

    def __init__(self, name: str, seed: int):
        self.name = name
        self.seed = int(seed)
        self.consumed: list[str] = []

    def draw_seed(self, k: int) -> int:
        h = hashlib.sha256(f"{self.seed}:{self.name}:{k}".encode()).hexdigest()
        return int(h[:16], 16)

    def generator(self, k: int) -> np.random.Generator:
        ds = self.draw_seed(k)
        self.consumed.append(f"{self.name}:{self.seed}:{k}:{ds}")
        return np.random.default_rng(ds)

    def hash_record(self) -> dict:
        blob = "\n".join(self.consumed).encode()
        return {
            "stream_name": self.name,
            "stream_seed": self.seed,
            "draws_consumed": len(self.consumed),
            "seed_sequence_sha256": hashlib.sha256(blob).hexdigest(),
        }


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# --------------------------------------------------------------------------
# Vectorised modular arithmetic over F_p (toy scale, exact in int64).
# --------------------------------------------------------------------------
def _assert_int64_safe(p: int) -> None:
    """int64 products must not overflow: all operands are reduced mod p."""
    if p >= 2 ** 31:
        raise ValueError(
            f"p = {p} is too large for the int64 vectorisation in this driver; "
            "this driver is toy-scale only")


def modpow_arr(base: np.ndarray, exp: int, p: int) -> np.ndarray:
    """Elementwise base**exp mod p by square-and-multiply on an int64 array."""
    result = np.ones_like(base)
    b = base % p
    e = int(exp)
    while e:
        if e & 1:
            result = (result * b) % p
        b = (b * b) % p
        e >>= 1
    return result


def modinv_arr(a: np.ndarray, p: int) -> np.ndarray:
    """Elementwise inverse via Fermat. Callers must exclude a == 0."""
    return modpow_arr(a, p - 2, p)


def is_qr_arr(a: np.ndarray, p: int) -> np.ndarray:
    """Boolean: a is a square mod p (0 counts as a square)."""
    leg = modpow_arr(a % p, (p - 1) // 2, p)
    return (leg == 1) | ((a % p) == 0)


def sqrt_arr(a: np.ndarray, p: int) -> np.ndarray:
    """Elementwise square root mod p, defined where a is a QR.

    Fast path for p == 3 (mod 4). Otherwise falls back to sympy elementwise,
    which is correct but slow; both toy primes of this experiment are 3 mod 4.
    """
    if p % 4 == 3:
        return modpow_arr(a % p, (p + 1) // 4, p)
    import sympy  # fallback path only
    out = np.zeros_like(a)
    for i, v in enumerate(a.tolist()):
        r = sympy.ntheory.residue_ntheory.sqrt_mod(int(v) % p, p)
        out[i] = 0 if r is None else int(r)
    return out


# --------------------------------------------------------------------------
# INT-2: the frozen half-arity Semaev fibre-invariant map at m = 4.
# fibre_invariant_map.step_2_coefficients / step_3_invariants.
# --------------------------------------------------------------------------
def int2_fibre_invariants(xi: np.ndarray, xj: np.ndarray,
                          p: int, a: int, b: int) -> tuple[np.ndarray, np.ndarray, int]:
    """(e_1, e_2) of S_3(x_i, x_j, Z), and the count of degenerate c_2 == 0 draws.

    c_2 = (x_i - x_j)**2
    c_1 = -2 * ((x_i + x_j) * (x_i * x_j + a) + 2 * b)
    c_0 = (x_i * x_j - a)**2 - 4 * b * (x_i + x_j)
    e_1 = (-c_1) * c_2**-1 mod p,  e_2 = c_0 * c_2**-1 mod p

    The diagonal x_i == x_j is excluded BY CONSTRUCTION by every caller
    (i < j over distinct x-coordinates); a nonzero degenerate count is an
    integrity failure and is returned rather than silently dropped.
    """
    _assert_int64_safe(p)
    xi = xi.astype(np.int64) % p
    xj = xj.astype(np.int64) % p
    s = (xi + xj) % p                      # x_i + x_j
    m = (xi * xj) % p                      # x_i * x_j
    d = (xi - xj) % p
    c2 = (d * d) % p
    degenerate = int(np.count_nonzero(c2 == 0))
    if degenerate:
        # Never invert zero; report the integrity failure to the caller.
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64), degenerate
    inv_c2 = modinv_arr(c2, p)
    # -c_1 = 2 * ((x_i + x_j) * (x_i * x_j + a) + 2 * b)
    neg_c1 = (2 * ((s * ((m + a) % p)) % p + (2 * b) % p)) % p
    t0 = (m - a) % p
    c0 = ((t0 * t0) % p - ((4 * b) % p) * s) % p
    e1 = (neg_c1 * inv_c2) % p
    e2 = (c0 * inv_c2) % p
    return e1, e2, 0


def int2_source_sha256() -> str:
    """sha256 of the frozen INT-2 implementation function source."""
    import inspect
    return sha256_text(inspect.getsource(int2_fibre_invariants))


def upper_triangle_indices(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Strictly i < j. The diagonal is excluded BY CONSTRUCTION, never counted
    and then dropped."""
    iu, ju = np.triu_indices(n, k=1)
    return iu.astype(np.int64), ju.astype(np.int64)


# --------------------------------------------------------------------------
# STAT-EQD-1: the frozen statistic family. Forms only; no thresholds.
# --------------------------------------------------------------------------
def _cell_index(e1: np.ndarray, e2: np.ndarray, p: int, K: int) -> np.ndarray:
    """binning_rule: (floor(lift(e_1) * K / p), floor(lift(e_2) * K / p))."""
    c1 = (e1 * K) // p
    c2 = (e2 * K) // p
    return c1 * K + c2


def stat_chi(e1a, e2a, e1b, e2b, p: int, K: int) -> dict:
    """STAT-CHI-K: two-sample Pearson chi-square of homogeneity on the K x K
    table, pooled expectation, cells empty in BOTH arms omitted from the sum
    and from the degrees of freedom, the omission count recorded."""
    ha = np.bincount(_cell_index(e1a, e2a, p, K), minlength=K * K).astype(np.float64)
    hb = np.bincount(_cell_index(e1b, e2b, p, K), minlength=K * K).astype(np.float64)
    na, nb = ha.sum(), hb.sum()
    tot = ha + hb
    nz = tot > 0
    N = na + nb
    ea = na * tot[nz] / N
    eb = nb * tot[nz] / N
    chi = float(np.sum((ha[nz] - ea) ** 2 / ea) + np.sum((hb[nz] - eb) ** 2 / eb))
    nonempty = int(np.count_nonzero(nz))
    return {
        "K": K,
        "value": chi,
        "nonempty_cells": nonempty,
        "degrees_of_freedom": nonempty - 1,
        "empty_cell_omission_count": K * K - nonempty,
    }


def stat_ks1(u: np.ndarray, v: np.ndarray) -> float:
    """STAT-KS1: one-dimensional two-sample Kolmogorov-Smirnov statistic."""
    x = np.sort(u)
    y = np.sort(v)
    allv = np.concatenate([x, y])
    f1 = np.searchsorted(x, allv, side="right") / x.size
    f2 = np.searchsorted(y, allv, side="right") / y.size
    return float(np.max(np.abs(f1 - f2)))


def stat_dup(e1: np.ndarray, e2: np.ndarray, p: int) -> int:
    """STAT-DUP: the count of exactly repeated (e_1, e_2) values within one arm.

    IMPLEMENTATION READING, DECLARED IN implementation.md: the count of
    UNORDERED INDEX PAIRS carrying the same (e_1, e_2) value, i.e.
    sum_v C(multiplicity(v), 2). This is the quantity whose idealised
    expectation is n**2 / (2 * S), the figure the contract states for this
    statistic, so it is the reading the frozen form's own stated expectation
    identifies.
    """
    key = e1.astype(np.int64) * p + e2.astype(np.int64)
    _, counts = np.unique(key, return_counts=True)
    return int(np.sum(counts * (counts - 1) // 2))


def all_two_sample_statistics(arm_a: tuple, arm_b: tuple, p: int) -> dict:
    """Every two-sample statistic of STAT-EQD-1 between two arms, plus the
    one-arm STAT-DUP of each arm. Values only; no threshold is applied."""
    e1a, e2a = arm_a
    e1b, e2b = arm_b
    out = {}
    for K in RESOLUTION_LADDER_K:
        out[f"STAT-CHI-{K}"] = stat_chi(e1a, e2a, e1b, e2b, p, K)
    out["STAT-KS1-E1"] = stat_ks1(e1a, e1b)
    out["STAT-KS1-E2"] = stat_ks1(e2a, e2b)
    out["STAT-DUP-arm-a"] = stat_dup(e1a, e2a, p)
    out["STAT-DUP-arm-b"] = stat_dup(e1b, e2b, p)
    out["n_arm_a"] = int(e1a.size)
    out["n_arm_b"] = int(e1b.size)
    return out


def flat_two_sample_values(stats: dict) -> dict:
    """The four two-sample decision statistics as bare numbers."""
    return {
        "STAT-CHI-16": stats["STAT-CHI-16"]["value"],
        "STAT-CHI-64": stats["STAT-CHI-64"]["value"],
        "STAT-KS1-E1": stats["STAT-KS1-E1"],
        "STAT-KS1-E2": stats["STAT-KS1-E2"],
    }


TWO_SAMPLE_STATISTIC_IDS = ("STAT-CHI-16", "STAT-CHI-64",
                            "STAT-KS1-E1", "STAT-KS1-E2")


# --------------------------------------------------------------------------
# The curve cell: p, a, b, the full affine point multiset, X_E.
# --------------------------------------------------------------------------
class Cell:
    """One toy field cell. `bits` names the FIELD prime p and nothing else
    (fibre_invariant_map.bit_size_labelling_caveat)."""

    def __init__(self, bits: int):
        sys.path.insert(0, os.getcwd())
        from harness.toycurve import EllipticCurve, generate_instance
        inst = generate_instance(MASTER_SEED, bits)
        self.bits = bits
        self.p, self.a, self.b = inst.p, inst.a, inst.b
        _assert_int64_safe(self.p)
        self.curve = EllipticCurve(self.p, self.a, self.b)

        p, a, b = self.p, self.a, self.b
        xs = np.arange(p, dtype=np.int64)
        rhs = (xs * xs % p * xs % p + a * xs + b) % p
        leg = modpow_arr(rhs, (p - 1) // 2, p)
        two_pt = leg == 1                     # two points with this x
        one_pt = rhs == 0                     # one point (y = 0)
        self.is_x_of_E = two_pt | one_pt      # boolean membership array for X_E
        self.X_E = xs[self.is_x_of_E]
        self.x_set_size = int(self.X_E.size)
        # #E(F_p) = 1 (point at infinity) + affine point count
        self.curve_order = 1 + int(np.count_nonzero(one_pt)) + 2 * int(np.count_nonzero(two_pt))
        self.two_adic_valuation = int((self.curve_order & -self.curve_order).bit_length() - 1)
        # Uniform sampling over E(F_p) \ {O}: each x repeated by multiplicity.
        self.point_x_multiset = np.concatenate(
            [xs[one_pt], np.repeat(xs[two_pt], 2)]).astype(np.int64)
        self.n_affine_points = int(self.point_x_multiset.size)
        self.iu, self.ju = upper_triangle_indices(BFB)

    def descriptor(self) -> dict:
        return {
            "field_bits": self.bits,
            "p": self.p,
            "a": self.a,
            "b": self.b,
            "curve_instance_source": f"harness.toycurve.generate_instance({MASTER_SEED}, {self.bits})",
            "curve_order_E_Fp": self.curve_order,
            "two_adic_valuation_of_curve_order": self.two_adic_valuation,
            "x_coordinate_set_size_X_E": self.x_set_size,
            "affine_point_count": self.n_affine_points,
        }

    # -- object samplers ---------------------------------------------------
    def draw_null_factor_base(self, stream: Stream, k: int) -> dict:
        """OBJ-NULL-RFB support: 512 points drawn uniformly at random from
        E(F_p) with DISTINCT x-coordinates, REJECT AND REDRAW on an
        x-collision, the rejection count recorded. This is the ONLY redraw
        permitted anywhere in this experiment
        (fibre_invariant_map.step_5_null_side_degeneracy)."""
        rng = stream.generator(k)
        chosen: list[int] = []
        seen: set[int] = set()
        rejections = 0
        while len(chosen) < BFB:
            need = BFB - len(chosen)
            idx = rng.integers(0, self.n_affine_points, size=need * 2)
            for x in self.point_x_multiset[idx].tolist():
                if len(chosen) == BFB:
                    break
                if x in seen:
                    rejections += 1
                    continue
                seen.add(x)
                chosen.append(x)
        xs = np.array(chosen, dtype=np.int64)
        return {"xs": xs, "redraw_count": rejections,
                "x_list_sha256": sha256_text("\n".join(str(int(v)) for v in xs))}

    def enumerate_factor_base(self, xs: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
        """INT-2 over every unordered half-tuple (i, j) with i < j.
        n = C(512, 2) = 130816 BY CONSTRUCTION."""
        if xs.size != BFB:
            raise ValueError(f"factor base has {xs.size} points, expected {BFB}")
        if np.unique(xs).size != BFB:
            raise ValueError("factor base x-coordinates are not distinct")
        return int2_fibre_invariants(xs[self.iu], xs[self.ju], self.p, self.a, self.b)

    def draw_independent_pairs(self, stream: Stream, k: int) -> tuple[np.ndarray, np.ndarray, int]:
        """OBJ-NULL-IND: n independently drawn uniform point pairs (P, Q) on
        E(F_p) with x(P) distinct from x(Q), through the identical map."""
        rng = stream.generator(k)
        n = N_PER_SAMPLE_SET
        xp = self.point_x_multiset[rng.integers(0, self.n_affine_points, size=n)]
        xq = self.point_x_multiset[rng.integers(0, self.n_affine_points, size=n)]
        bad = np.nonzero(xp == xq)[0]
        while bad.size:
            xq[bad] = self.point_x_multiset[
                rng.integers(0, self.n_affine_points, size=bad.size)]
            bad = np.nonzero(xp == xq)[0]
        return int2_fibre_invariants(xp, xq, self.p, self.a, self.b)

    def draw_uniform_pairs(self, stream: Stream, k: int) -> tuple[np.ndarray, np.ndarray]:
        """OBJ-NULL-UNIF2: n pairs (e_1, e_2) drawn uniformly at random from
        [0, p) x [0, p), with no curve arithmetic at all."""
        rng = stream.generator(k)
        e1 = rng.integers(0, self.p, size=N_PER_SAMPLE_SET).astype(np.int64)
        e2 = rng.integers(0, self.p, size=N_PER_SAMPLE_SET).astype(np.int64)
        return e1, e2

    def plant(self, e1: np.ndarray, e2: np.ndarray, delta: float,
              stream: Stream, k: int) -> tuple[np.ndarray, np.ndarray, int]:
        """OBJ-PLANT-delta: a declared fraction delta of the n pairs has its
        e_1 coordinate REPLACED by a uniform draw from [0, floor(p/2)) and its
        e_2 left unchanged, the replaced indices chosen by the frozen plant
        stream. Replacement count = int(round(delta * n)), declared."""
        rng = stream.generator(k)
        n = e1.size
        n_replace = int(round(delta * n))
        idx = rng.choice(n, size=n_replace, replace=False)
        out1 = e1.copy()
        out1[idx] = rng.integers(0, self.p // 2, size=n_replace).astype(np.int64)
        return out1, e2.copy(), n_replace

    # -- controls ----------------------------------------------------------
    def support_fraction(self, e1: np.ndarray, e2: np.ndarray) -> float:
        """The admissible-support fraction: the fraction of pairs whose
        associated root multiset (the roots of t**2 - e_1 t + e_2) lies in
        X_E. CAL-4."""
        p = self.p
        disc = (e1 * e1 - 4 * e2) % p
        ok_sq = is_qr_arr(disc, p)
        r = sqrt_arr(disc, p)
        inv2 = pow(2, -1, p)
        t1 = ((e1 + r) % p) * inv2 % p
        t2 = ((e1 - r) % p) * inv2 % p
        adm = ok_sq & self.is_x_of_E[t1] & self.is_x_of_E[t2]
        return float(np.count_nonzero(adm) / e1.size)

    def ctrl_eqd_s3(self, xs: np.ndarray, e1: np.ndarray, e2: np.ndarray,
                    sample: int = S3_CONTROL_SAMPLE) -> dict:
        """CTRL-EQD-S3. For the first `sample` half-tuples in the enumeration
        order, verify BY ACTUAL POINT ARITHMETIC on E(F_p) that the root
        multiset of f_ij equals {x(P_i + P_j), x(P_i - P_j)} -- checked as
        e_1 == x(P+Q) + x(P-Q) and e_2 == x(P+Q) * x(P-Q) mod p. The point
        arithmetic does not reuse the coefficient formula."""
        p = self.p
        verified = 0
        total = 0
        for t in range(min(sample, self.iu.size)):
            i, j = int(self.iu[t]), int(self.ju[t])
            Pi = self.curve.lift_x(int(xs[i]))
            Pj = self.curve.lift_x(int(xs[j]))
            if Pi is None or Pj is None:
                total += 1
                continue
            S = self.curve.add(Pi, Pj)
            D = self.curve.add(Pi, self.curve.negate(Pj))
            total += 1
            if S is None or D is None:
                continue
            xs_, xd_ = S[0], D[0]
            if (int(e1[t]) == (xs_ + xd_) % p) and (int(e2[t]) == (xs_ * xd_) % p):
                verified += 1
        return {"verified": verified, "total": total,
                "method": "independent point arithmetic on E(F_p) via harness.toycurve"}


# --------------------------------------------------------------------------
# THE REAL OBJECT. ATS-1 clause 2 tripwire lives here and NOWHERE ELSE.
# --------------------------------------------------------------------------
def deterministic_factor_base(cell: Cell) -> dict:
    """OBJ-REAL support: the FROZEN DETERMINISTIC factor base -- the first 512
    x-coordinates in F_p, in increasing integer order, that are x-coordinates
    of points of E(F_p) (factor_base.real_rule).

    CALLING THIS FUNCTION IS "SEEING THE REAL DATA". It is called by
    `run_real_arm()` and by nothing else, and it flips the module-level
    tripwire that `run_calibration()` asserts against.
    """
    global _REAL_DATA_TOUCHED
    _REAL_DATA_TOUCHED = True
    xs = cell.X_E[:BFB].astype(np.int64)
    if xs.size != BFB:
        raise ValueError(f"only {xs.size} x-coordinates available, need {BFB}")
    return {"xs": xs,
            "factor_base_sha256": sha256_text("\n".join(str(int(v)) for v in xs))}


# --------------------------------------------------------------------------
# CALIBRATION ARM: CAL-1, CAL-2, CAL-3, CAL-4. NON-EVIDENTIAL.
# --------------------------------------------------------------------------
def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}",
          flush=True)


def _draw_null_arm(cell: Cell, stream: Stream, k: int, integrity: dict) -> tuple:
    draw = cell.draw_null_factor_base(stream, k)
    e1, e2, degenerate = cell.enumerate_factor_base(draw["xs"])
    integrity["degenerate_draw_count"] += degenerate
    integrity["null_redraw_count_total"] += draw["redraw_count"]
    integrity["null_redraw_counts"].append(draw["redraw_count"])
    if degenerate:
        raise RuntimeError(
            f"INTEGRITY FAILURE: {degenerate} c_2 == 0 draws on a null arm at "
            f"bits {cell.bits}, draw {k}. The diagonal is excluded by "
            f"construction; this is not a datum.")
    if e1.size != N_PER_SAMPLE_SET:
        raise RuntimeError(f"arm has {e1.size} pairs, expected {N_PER_SAMPLE_SET}")
    if int(e1.min()) < 0 or int(e1.max()) >= cell.p or \
       int(e2.min()) < 0 or int(e2.max()) >= cell.p:
        raise RuntimeError("CTRL-EQD-RANGE violation: e out of [0, p)")
    return e1, e2, draw


def run_calibration(cell: Cell, deadline: float) -> dict:
    """CAL-EQD-1 at one cell. Measures the instrument. Freezes nothing,
    applies no reading rule, and states no disposition."""
    p = cell.p
    null_stream = Stream("calibration_null", MASTER_SEED + STREAM_OFFSETS["calibration_null"] + cell.bits)
    plant_stream = Stream("calibration_plant", MASTER_SEED + STREAM_OFFSETS["calibration_plant"] + cell.bits)
    ind_stream = Stream("calibration_independent_pair", MASTER_SEED + STREAM_OFFSETS["calibration_independent_pair"] + cell.bits)
    unif_stream = Stream("calibration_uniform_pair", MASTER_SEED + STREAM_OFFSETS["calibration_uniform_pair"] + cell.bits)

    integrity = {"degenerate_draw_count": 0, "null_redraw_count_total": 0,
                 "null_redraw_counts": [], "range_violations": 0}
    out: dict = {"cell": cell.descriptor(), "complete": {}, "integrity": integrity}
    nk = 0  # global null-stream draw index, consumed in a fixed order

    def check_deadline(stage: str):
        if time.time() > deadline:
            raise TimeoutError(f"wall-clock budget exhausted during {stage}")

    # ---- CAL-1: the measured null distribution ---------------------------
    _log(f"bits={cell.bits} CAL-1: {M_PAIRS} independent replicate pairs")
    cal1 = {sid: [] for sid in TWO_SAMPLE_STATISTIC_IDS}
    cal1_dup: list[int] = []
    cal1_aux = {"empty_cell_omission_count_K16": [], "empty_cell_omission_count_K64": []}
    representative = None
    for r in range(M_PAIRS):
        check_deadline(f"CAL-1 replicate {r}")
        e1a, e2a, da = _draw_null_arm(cell, null_stream, nk, integrity); nk += 1
        e1b, e2b, db = _draw_null_arm(cell, null_stream, nk, integrity); nk += 1
        st = all_two_sample_statistics((e1a, e2a), (e1b, e2b), p)
        for sid in TWO_SAMPLE_STATISTIC_IDS:
            cal1[sid].append(flat_two_sample_values(st)[sid])
        cal1_dup.append(st["STAT-DUP-arm-a"])
        cal1_dup.append(st["STAT-DUP-arm-b"])
        cal1_aux["empty_cell_omission_count_K16"].append(st["STAT-CHI-16"]["empty_cell_omission_count"])
        cal1_aux["empty_cell_omission_count_K64"].append(st["STAT-CHI-64"]["empty_cell_omission_count"])
        if r == 0:
            # memory_policy: archive ONE representative OBJ-NULL-RFB draw per cell.
            s3 = cell.ctrl_eqd_s3(da["xs"], e1a, e2a)
            representative = {
                "object": "OBJ-NULL-RFB",
                "note": "representative NULL draw archived for reproducibility; it is not real data",
                "null_stream_draw_index": 0,
                "draw_seed": null_stream.draw_seed(0),
                "x_list_sha256": da["x_list_sha256"],
                "x_list": [int(v) for v in da["xs"]],
                "redraw_count": da["redraw_count"],
                "n_pairs": int(e1a.size),
                "STAT-DUP": st["STAT-DUP-arm-a"],
                "admissible_support_fraction": cell.support_fraction(e1a, e2a),
                "CTRL-EQD-S3_on_this_null_draw": s3,
            }
        if (r + 1) % 50 == 0:
            _log(f"  bits={cell.bits} CAL-1 {r + 1}/{M_PAIRS} pairs")
    out["CAL-1"] = {"replicate_values": cal1, "dup_values": cal1_dup,
                    "aux": cal1_aux, "M_PAIRS": M_PAIRS,
                    "n_dup_values": len(cal1_dup)}
    out["complete"]["CAL-1"] = True

    # The order statistics THR-EQD-1 will select. MEASURED NUMBERS, NOT A
    # FREEZE: TASK-20260801-023 owns the freeze and may recompute these from
    # the archived replicate values.
    order_stats = {}
    for sid in TWO_SAMPLE_STATISTIC_IDS:
        v = sorted(cal1[sid])
        order_stats[sid] = {
            "order_statistic_index_1based": 199,
            "value_at_199th_order_statistic": v[198],
            "value_at_200th_order_statistic_max": v[199],
            "min": v[0], "median": 0.5 * (v[99] + v[100]), "mean": float(np.mean(v)),
            "stdev": float(np.std(v, ddof=1)),
        }
    dsorted = sorted(cal1_dup)
    order_stats["STAT-DUP"] = {
        "band_order_statistic_indices_1based": [3, 398],
        "value_at_3rd_order_statistic": dsorted[2],
        "value_at_398th_order_statistic": dsorted[397],
        "min": dsorted[0], "max": dsorted[-1],
        "median": 0.5 * (dsorted[199] + dsorted[200]),
        "mean": float(np.mean(dsorted)),
    }
    out["CAL-1_measured_order_statistics"] = order_stats
    out["CAL-1_measured_order_statistics_note"] = (
        "MEASURED NUMBERS ONLY. This driver freezes no threshold. THR-EQD-1 is "
        "applied at TASK-20260801-023.")

    # ---- CAL-2: the measured power curve ---------------------------------
    _log(f"bits={cell.bits} CAL-2: power curve over {len(DELTA_LADDER)} deltas")
    cal2: dict = {}
    pk = 0
    for delta in DELTA_LADDER:
        rows = []
        for rep in range(R_REPS):
            check_deadline(f"CAL-2 delta={delta} rep={rep}")
            e1p, e2p, _ = _draw_null_arm(cell, null_stream, nk, integrity); nk += 1
            e1p, e2p, n_rep = cell.plant(e1p, e2p, delta, plant_stream, pk); pk += 1
            e1n, e2n, _ = _draw_null_arm(cell, null_stream, nk, integrity); nk += 1
            st = all_two_sample_statistics((e1p, e2p), (e1n, e2n), p)
            rows.append({"replicate": rep, "n_replaced": n_rep,
                         **flat_two_sample_values(st),
                         "STAT-DUP_plant_arm": st["STAT-DUP-arm-a"],
                         "STAT-DUP_null_arm": st["STAT-DUP-arm-b"]})
        cal2[f"{delta}"] = rows
        _log(f"  bits={cell.bits} CAL-2 delta={delta} done ({R_REPS} replicates)")
    out["CAL-2"] = {"R_REPS": R_REPS, "delta_ladder": list(DELTA_LADDER),
                    "replicates": cal2}
    out["complete"]["CAL-2"] = True

    # ---- CAL-3: dependency-structure characterization --------------------
    _log(f"bits={cell.bits} CAL-3: {R_REPS} OBJ-NULL-IND vs OBJ-NULL-RFB")
    cal3 = []
    for rep in range(R_REPS):
        check_deadline(f"CAL-3 rep={rep}")
        e1i, e2i, degen = cell.draw_independent_pairs(ind_stream, rep)
        if degen:
            raise RuntimeError(
                f"INTEGRITY FAILURE: {degen} c_2 == 0 draws on OBJ-NULL-IND at "
                f"bits {cell.bits}, rep {rep}")
        integrity["degenerate_draw_count"] += degen
        e1n, e2n, _ = _draw_null_arm(cell, null_stream, nk, integrity); nk += 1
        st = all_two_sample_statistics((e1i, e2i), (e1n, e2n), p)
        cal3.append({"replicate": rep, **flat_two_sample_values(st),
                     "STAT-DUP_ind_arm": st["STAT-DUP-arm-a"],
                     "STAT-DUP_rfb_arm": st["STAT-DUP-arm-b"]})
    out["CAL-3"] = {"R_REPS": R_REPS, "replicates": cal3}
    out["complete"]["CAL-3"] = True

    # ---- CAL-4: support density ------------------------------------------
    _log(f"bits={cell.bits} CAL-4: support density")
    check_deadline("CAL-4")
    u1, u2 = cell.draw_uniform_pairs(unif_stream, 0)
    frac_unif2 = cell.support_fraction(u1, u2)
    e1n, e2n, dn = _draw_null_arm(cell, null_stream, nk, integrity); nk += 1
    frac_rfb = cell.support_fraction(e1n, e2n)
    out["CAL-4"] = {
        "curve_order_E_Fp": cell.curve_order,
        "two_adic_valuation_of_curve_order": cell.two_adic_valuation,
        "x_coordinate_set_size_X_E": cell.x_set_size,
        "x_set_size_over_p": cell.x_set_size / cell.p,
        "support_fraction_OBJ_NULL_UNIF2": frac_unif2,
        "support_fraction_OBJ_NULL_RFB": frac_rfb,
        "n_per_sample_set": N_PER_SAMPLE_SET,
        "note": "CAL-4 measures an elliptic-curve fact. It is not evidence "
                "about the Semaev map and it is not a finding of this batch.",
    }
    out["complete"]["CAL-4"] = True

    out["representative_null_draw"] = representative
    out["null_stream_draws_consumed"] = nk
    out["stream_hashes"] = [s.hash_record() for s in
                            (null_stream, plant_stream, ind_stream, unif_stream)]
    out["real_data_touched"] = _REAL_DATA_TOUCHED
    return out


# --------------------------------------------------------------------------
# Mechanical evaluation of the frozen THR-EQD-1 FORM against CAL-1 values.
# This is a REPORT of measured detection rates, not a freeze and not a reading
# rule. TASK-20260801-023 owns the freeze and may recompute independently from
# the archived replicate values.
# --------------------------------------------------------------------------
def measured_detection_rates(cal1: dict, rows: list[dict]) -> dict:
    rates = {}
    for sid in TWO_SAMPLE_STATISTIC_IDS:
        ref = sorted(cal1[sid])[198]     # 199th order statistic, ascending
        exceed = sum(1 for r in rows if r[sid] > ref)
        rates[sid] = {"reference_199th_order_statistic": ref,
                      "n_replicates": len(rows),
                      "n_exceeding": exceed,
                      "detection_rate": exceed / len(rows) if rows else None}
    return rates


# --------------------------------------------------------------------------
# REAL ARM. AUTHORED COMPLETE HERE AND NOT INVOKED AT TASK-20260801-021.
# --------------------------------------------------------------------------
def load_reading_rule(path: str) -> dict:
    """The frozen RR-EQD-1 numbers, frozen at TASK-20260801-023 in
    experiments/EXP-EQD-001/reading_rule.yaml. This driver reads them; it never
    contains them. Expected shape:

      reading_rule:
        retained_statistics: [STAT-CHI-16, STAT-CHI-64, STAT-KS1-E1, STAT-KS1-E2]
        thresholds:
          16: {STAT-CHI-16: <float>, ...}
          20: {...}
        dup_band:
          16: [<lo>, <hi>]
          20: [<lo>, <hi>]
        certified_delta: <float>
        certifying_statistic: STAT-CHI-16 | STAT-CHI-64
    """
    import yaml
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    rr = doc.get("reading_rule") if isinstance(doc, dict) else None
    if not isinstance(rr, dict):
        raise ValueError(f"{path} has no top-level 'reading_rule' mapping")
    for field in ("retained_statistics", "thresholds", "dup_band",
                  "certified_delta", "certifying_statistic"):
        if rr.get(field) is None:
            raise ValueError(f"{path} reading_rule missing required field '{field}'")
    return rr


def run_real_arm(cell: Cell, rr: dict, deadline: float) -> dict:
    """RUN-EQD-001-real at one cell. NOT EXECUTED AT TASK-20260801-021.

    Computes DV-1..DV-7 and the integrity controls. It records the reject
    booleans defined by the frozen reading rule's numbers; it selects NO branch
    and states NO disposition -- branch selection belongs to the reading rule
    applied by the Reviewer and the Coordinator.
    """
    p = cell.p
    thr = rr["thresholds"][cell.bits]
    dup_lo, dup_hi = rr["dup_band"][cell.bits]
    retained = list(rr["retained_statistics"])
    real_null_stream = Stream(
        "real_arm_null", MASTER_SEED + STREAM_OFFSETS["real_arm_null"] + cell.bits)
    integrity = {"degenerate_draw_count": 0, "null_redraw_count_total": 0,
                 "null_redraw_counts": [], "range_violations": 0}

    if time.time() > deadline:
        raise TimeoutError("wall-clock budget exhausted before the real arm")

    # OBJ-REAL: exhaustive over the frozen deterministic factor base, i < j.
    fb = deterministic_factor_base(cell)
    e1r, e2r, degen_real = cell.enumerate_factor_base(fb["xs"])
    if degen_real:
        raise RuntimeError(
            f"INTEGRITY FAILURE: {degen_real} c_2 == 0 draws on OBJ-REAL")
    if e1r.size != N_PER_SAMPLE_SET:
        raise RuntimeError(f"OBJ-REAL has {e1r.size} pairs, expected {N_PER_SAMPLE_SET}")
    if int(e1r.min()) < 0 or int(e1r.max()) >= p or \
       int(e2r.min()) < 0 or int(e2r.max()) >= p:
        raise RuntimeError("CTRL-EQD-RANGE violation on OBJ-REAL")

    # The matched null, from the disjoint real-arm null stream.
    e1n, e2n, dn = _draw_null_arm(cell, real_null_stream, 0, integrity)
    st_real = all_two_sample_statistics((e1r, e2r), (e1n, e2n), p)
    vals = flat_two_sample_values(st_real)
    rejects = {sid: bool(vals[sid] > thr[sid]) for sid in retained}

    dup_real = st_real["STAT-DUP-arm-a"]
    dup_tell_fired = bool(dup_real < dup_lo or dup_real > dup_hi)

    # DV-6 / CTRL-EQD-POWER: PC-1, the in-run power certificate.
    cs = rr["certifying_statistic"]
    e1p, e2p, _ = _draw_null_arm(cell, real_null_stream, 1, integrity)
    plant_stream = Stream("real_arm_plant_pc1",
                          MASTER_SEED + STREAM_OFFSETS["real_arm_null"] + 100 + cell.bits)
    e1p, e2p, n_replaced = cell.plant(e1p, e2p, float(rr["certified_delta"]),
                                      plant_stream, 0)
    e1q, e2q, _ = _draw_null_arm(cell, real_null_stream, 2, integrity)
    st_pc1 = all_two_sample_statistics((e1p, e2p), (e1q, e2q), p)
    pc1_value = flat_two_sample_values(st_pc1)[cs]
    pc1_rejected = bool(pc1_value > thr[cs])

    # DV-7 / CTRL-EQD-IDENTITY: two fresh independent OBJ-NULL-RFB draws.
    e1i, e2i, _ = _draw_null_arm(cell, real_null_stream, 3, integrity)
    e1j, e2j, _ = _draw_null_arm(cell, real_null_stream, 4, integrity)
    st_id = all_two_sample_statistics((e1i, e2i), (e1j, e2j), p)
    id_value = flat_two_sample_values(st_id)[cs]
    identity_ok = bool(not (id_value > thr[cs]))

    # CTRL-EQD-S3 on the real enumeration.
    s3 = cell.ctrl_eqd_s3(fb["xs"], e1r, e2r)

    return {
        "cell": cell.descriptor(),
        "factor_base_sha256": fb["factor_base_sha256"],
        "null_factor_base_sha256": dn["x_list_sha256"],
        "EQD_statistics": vals,
        "EQD_statistic_detail": {k: v for k, v in st_real.items()
                                 if k.startswith("STAT-CHI")},
        "EQD_rejects": rejects,
        "EQD_bit_size_not_distinguishable": bool(not any(rejects.values())),
        "EQD_dup_real": dup_real,
        "EQD_dup_band": [dup_lo, dup_hi],
        "EQD_dup_tell_fired": dup_tell_fired,
        "EQD_power_certificate": {"certifying_statistic": cs,
                                  "certified_delta": rr["certified_delta"],
                                  "n_replaced": n_replaced,
                                  "value": pc1_value,
                                  "threshold": thr[cs],
                                  "rejected": pc1_rejected},
        "EQD_apparatus_identity": {"certifying_statistic": cs,
                                   "value": id_value,
                                   "threshold": thr[cs],
                                   "ok_not_rejecting": identity_ok},
        "CTRL-EQD-S3": s3,
        "support_fraction_real": cell.support_fraction(e1r, e2r),
        "pairs_recorded_per_arm": int(e1r.size),
        "integrity": integrity,
        "stream_hashes": [real_null_stream.hash_record(), plant_stream.hash_record()],
        "no_disposition_stated": (
            "This driver records DV values and reject booleans only. Branch "
            "selection under RR-EQD-1 is not performed here."),
    }


# --------------------------------------------------------------------------
# Run-package emission.
# --------------------------------------------------------------------------
def git_state() -> dict:
    def g(*args):
        try:
            return subprocess.run(["git", *args], capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"),
            "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain"))}


def environment_block() -> dict:
    import numpy as _np
    deps = {"numpy": _np.__version__}
    try:
        import sympy as _sp
        deps["sympy"] = _sp.__version__
    except Exception:
        deps["sympy"] = None
    try:
        import yaml as _y
        deps["pyyaml"] = _y.__version__
    except Exception:
        deps["pyyaml"] = None
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "dependencies": deps,
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
    }


def yaml_dump(obj, indent=0, out=None) -> str:
    """Minimal, dependency-free, quoting-safe YAML emitter for the manifest.
    Every scalar that is not a plain int/float/bool/None is emitted as a
    double-quoted string, so a colon-space inside prose can never break the
    parse."""
    out = [] if out is None else out
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                yaml_dump(v, indent + 1, out)
            else:
                out.append(f"{pad}{k}: {_scalar(v)}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)) and v:
                sub = yaml_dump(v, indent + 1).splitlines()
                first = sub[0].strip()
                out.append(f"{pad}- {first}")
                out.extend(sub[1:])
            else:
                out.append(f"{pad}- {_scalar(v)}")
    return "\n".join(out)


def _scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "{}" if isinstance(v, dict) else "[]"
    s = str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{s}"'


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=False)
        fh.write("\n")


# --------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EXP-EQD-001 driver")
    ap.add_argument("--mode", choices=["calib", "real"], required=True)
    ap.add_argument("--out-run", required=True)
    ap.add_argument("--out-results", required=True)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--wall-clock-seconds", type=float, default=3600.0)
    ap.add_argument("--reading-rule", default=None,
                    help="real mode only: frozen RR-EQD-1 numbers")
    ap.add_argument("--approval-receipt", default=None,
                    help="real mode only: TASK-20260801-026 snapshot receipt")
    ap.add_argument("--resolved-model-id", default=None)
    ap.add_argument("--requested-policy", default="executor-implementation")
    args = ap.parse_args(argv)

    run_id = args.run_id or (f"RUN-EQD-001-{'calib' if args.mode == 'calib' else 'real'}")
    started = time.time()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    deadline = started + args.wall_clock_seconds

    _log(f"EXP-EQD-001 driver, mode={args.mode}, run_id={run_id}")
    _log(f"spec sha256 at freeze: {SPEC_SHA256_AT_FREEZE}")
    if os.path.exists(SPEC_PATH):
        live = sha256_file(SPEC_PATH)
        _log(f"spec sha256 on disk:    {live}  match={live == SPEC_SHA256_AT_FREEZE}")

    status = "completed_valid"
    invalid_reason = None
    failure_class = None
    payload: dict = {}

    try:
        if args.mode == "real":
            # ATS-1: the real arm is gated. This branch is NOT taken at
            # TASK-20260801-021 and refuses to run without both gates.
            if not args.approval_receipt or not os.path.exists(args.approval_receipt):
                raise PermissionError(
                    "real mode requires --approval-receipt pointing at the "
                    "TASK-20260801-026 snapshot receipt")
            with open(args.approval_receipt) as fh:
                receipt = json.load(fh)
            if receipt.get("APPROVAL_DETERMINATION") != "APPROVED":
                raise PermissionError(
                    "APPROVAL_DETERMINATION is not APPROVED; the real arm is "
                    "not authorized")
            if not args.reading_rule or not os.path.exists(args.reading_rule):
                raise PermissionError(
                    "real mode requires the frozen reading rule from "
                    "TASK-20260801-023")
            rr = load_reading_rule(args.reading_rule)
            cells = {}
            for bits in FIELD_BITS:
                cell = Cell(bits)
                cells[str(bits)] = run_real_arm(cell, rr, deadline)
            payload = {"mode": "real", "cells": cells,
                       "reading_rule_sha256": sha256_file(args.reading_rule)}
            write_json(os.path.join(args.out_results, "EQD_report.json"), payload)
        else:
            cells = {}
            for bits in FIELD_BITS:
                _log(f"building cell bits={bits}")
                cell = Cell(bits)
                _log(f"  p={cell.p} a={cell.a} b={cell.b} #E={cell.curve_order} "
                     f"|X_E|={cell.x_set_size}")
                cells[str(bits)] = run_calibration(cell, deadline)
            if _REAL_DATA_TOUCHED:
                raise RuntimeError(
                    "ATS-1 CLAUSE 2 VIOLATION: the deterministic factor base "
                    "was touched during a calibration run")
            payload = {"mode": "calib", "cells": cells,
                       "ats1_clause_2_real_data_touched": _REAL_DATA_TOUCHED}
            _emit_calibration_results(args.out_results, cells)
    except TimeoutError as exc:
        status = "failed_infrastructure"
        failure_class = "resource_exhaustion"
        invalid_reason = str(exc)
        _log(f"RESOURCE EXHAUSTION: {exc}")
    except (PermissionError, ValueError) as exc:
        status = "failed_infrastructure"
        failure_class = "specification_error"
        invalid_reason = str(exc)
        _log(f"REFUSED: {exc}")
    except RuntimeError as exc:
        status = "invalid"
        failure_class = "invalid_measurement"
        invalid_reason = str(exc)
        _log(f"INTEGRITY FAILURE: {exc}")

    finished = time.time()
    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = ru.ru_maxrss if sys.platform == "darwin" else ru.ru_maxrss * 1024

    raw = {
        "run_id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "mode": args.mode,
        "status": status,
        "invalid_reason": invalid_reason,
        "failure_class": failure_class,
        "spec_sha256_at_freeze": SPEC_SHA256_AT_FREEZE,
        "spec_sha256_on_disk": sha256_file(SPEC_PATH) if os.path.exists(SPEC_PATH) else None,
        "driver_sha256": sha256_file(os.path.abspath(__file__)),
        "fibre_invariant_map_sha256": int2_source_sha256(),
        "frozen_parameters": {
            "master_seed": MASTER_SEED, "field_bits": list(FIELD_BITS),
            "Bfb": BFB, "n_per_sample_set": N_PER_SAMPLE_SET,
            "resolution_ladder_K": list(RESOLUTION_LADDER_K),
            "delta_ladder": list(DELTA_LADDER),
            "M_PAIRS": M_PAIRS, "R_REPS": R_REPS,
            "stream_offsets": STREAM_OFFSETS,
        },
        "timing": {"started_at": started_at, "finished_at": finished_at,
                   "wall_seconds": finished - started},
        "resources": {"peak_rss_bytes": int(peak_rss),
                      "cpu_seconds": ru.ru_utime + ru.ru_stime},
        "payload": payload,
        "non_evidential_declaration": (
            "RUN-EQD-001-calib is EXPRESSLY NON-EVIDENTIAL about H-EQD-001, "
            "HEUR-DS-1 and H-SMTH-001 in either direction. It measures the "
            "instrument, not the object." if args.mode == "calib" else None),
    }
    write_json(os.path.join(args.out_run, "raw-result.json"), raw)

    env = environment_block()
    write_json(os.path.join(args.out_run, "environment.json"), env)

    git = git_state()
    manifest = {"run": {
        "id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "status": status,
        "code": {
            "commit": git["commit"], "branch": git["branch"], "dirty": git["dirty"],
            "command": " ".join([sys.executable.split("/")[-1], os.path.relpath(os.path.abspath(__file__))] + (argv or sys.argv[1:])),
            "driver_sha256": raw["driver_sha256"],
            "fibre_invariant_map_sha256": raw["fibre_invariant_map_sha256"],
            "specification_sha256": raw["spec_sha256_on_disk"],
        },
        "inference": {
            "requested_policy": args.requested_policy,
            "resolved_model_id": args.resolved_model_id,
            "reasoning_effort": None,
            "fallback_used": True,
            "model_verified": False,
            "independent_session_required": False,
        },
        "environment": env,
        "inputs": {
            "seeds": [MASTER_SEED],
            "parameters": {
                "experiment_id": EXPERIMENT_ID,
                "mode": args.mode,
                "field_bits": max(FIELD_BITS),
                "field_bits_semantics": (
                    "scalar maximum field bit size exercised, for the tier "
                    "check in tools/validate_ledger.py; both 16 and 20 were run"),
                "field_bits_tested": list(FIELD_BITS),
                "Bfb": BFB,
                "n_per_sample_set": N_PER_SAMPLE_SET,
            },
        },
        "timing": raw["timing"],
        "resources": raw["resources"],
        "result": {
            "valid": status == "completed_valid",
            "invalid_reason": invalid_reason,
            "certificate": {"kind": "none", "verified": True, "verifier": None},
        },
    }}
    os.makedirs(args.out_run, exist_ok=True)
    with open(os.path.join(args.out_run, "manifest.yaml"), "w") as fh:
        fh.write(yaml_dump(manifest) + "\n")

    _log(f"status={status} wall_seconds={finished - started:.1f} "
         f"peak_rss_bytes={int(peak_rss)}")
    return 0 if status == "completed_valid" else 1


def _emit_calibration_results(out_results: str, cells: dict) -> None:
    """The three declared calibration result files. Measured numbers only."""
    disclaimer = ("NON-EVIDENTIAL about H-EQD-001, HEUR-DS-1 and H-SMTH-001 in "
                  "either direction. Instrument measurement only. No threshold "
                  "is frozen here and no reading rule is applied.")

    null_stats = {"schema": "eqd001_null_replicate_statistics/v1",
                  "disclaimer": disclaimer, "cells": {}}
    for bits, c in cells.items():
        null_stats["cells"][bits] = {
            "cell": c["cell"],
            "M_PAIRS": c["CAL-1"]["M_PAIRS"],
            "replicate_values": c["CAL-1"]["replicate_values"],
            "dup_values": c["CAL-1"]["dup_values"],
            "empty_cell_omission_counts": c["CAL-1"]["aux"],
            "measured_order_statistics": c["CAL-1_measured_order_statistics"],
            "measured_order_statistics_note": c["CAL-1_measured_order_statistics_note"],
            "integrity": c["integrity"],
            "stream_hashes": c["stream_hashes"],
        }
    write_json(os.path.join(out_results, "null_replicate_statistics.json"), null_stats)

    power = {"schema": "eqd001_power_curve/v1", "disclaimer": disclaimer,
             "detection_rate_note": (
                 "Detection rates are computed by MECHANICAL application of the "
                 "frozen THR-EQD-1 order-statistic form (199th ascending order "
                 "statistic of the same run's 200 CAL-1 replicate values) to the "
                 "measured CAL-2 values. This is a MEASUREMENT REPORT, not a "
                 "freeze: TASK-20260801-023 owns the freeze and may recompute "
                 "from the archived replicate values. No certified delta is "
                 "declared here and the CERT-EQD-1 predicate is not evaluated."),
             "delta_ladder": list(DELTA_LADDER), "cells": {}}
    for bits, c in cells.items():
        per_delta = {}
        for d, rows in c["CAL-2"]["replicates"].items():
            per_delta[d] = {
                "replicates": rows,
                "measured_detection_rates":
                    measured_detection_rates(c["CAL-1"]["replicate_values"], rows),
            }
        power["cells"][bits] = {"cell": c["cell"], "R_REPS": c["CAL-2"]["R_REPS"],
                                "per_delta": per_delta}
    write_json(os.path.join(out_results, "power_curve.json"), power)

    instr = {"schema": "eqd001_instrument_characterization/v1",
             "disclaimer": disclaimer,
             "cal3_note": ("CAL-3 is DEPENDENCY-STRUCTURE CHARACTERIZATION, not "
                           "an interpretive null. A disagreement is an instrument "
                           "fact and is never a result about the Semaev map."),
             "cal4_note": ("CAL-4 measures an elliptic-curve fact. Limb L1 is a "
                           "DERIVATION and is not an experimental finding."),
             "cells": {}}
    for bits, c in cells.items():
        instr["cells"][bits] = {
            "cell": c["cell"],
            "CAL-3": {
                "replicates": c["CAL-3"]["replicates"],
                "measured_exceedance_of_CAL1_199th_order_statistic":
                    measured_detection_rates(c["CAL-1"]["replicate_values"],
                                             c["CAL-3"]["replicates"]),
            },
            "CAL-4": c["CAL-4"],
            "representative_null_draw": c["representative_null_draw"],
            "integrity": c["integrity"],
            "null_stream_draws_consumed": c["null_stream_draws_consumed"],
            "ats1_clause_2_real_data_touched": c["real_data_touched"],
        }
    write_json(os.path.join(out_results, "instrument_characterization.json"), instr)


if __name__ == "__main__":
    raise SystemExit(main())
