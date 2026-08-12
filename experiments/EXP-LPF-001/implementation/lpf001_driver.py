#!/usr/bin/env python3
"""EXP-LPF-001 driver.

Direct measurement of the B-smoothness and largest-prime-factor distribution of
half-arity Semaev partial-map intermediates against the Dickman law, with a
matched-bitlength uniform-integer arm as APPARATUS CALIBRATION.

BINDING CONTRACT
----------------
experiments/EXP-LPF-001/specification.yaml, hash-bound at commit
ba1567ee415b680b2d25108d59b9884f432d44d8, sha256
0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda.

ATS-LPF-1 clause 3: THIS FILE IS AUTHORED COMPLETE AT TASK-20260801-049,
INCLUDING THE MEASUREMENT ENTRY POINT `run_measurement`, WHICH IS NOT EXECUTED
THERE. Its sha256 is bound by the TASK-20260801-050 snapshot as DRIVER_SHA256
and TASK-20260801-056 must execute the IDENTICAL file with no edit. Every
number the measurement arm needs that does not exist yet (the archived bands,
the retained certifying set, the identity cut) is read at run time from
experiments/EXP-LPF-001/reading_rule.yaml, which TASK-20260801-052 freezes and
TASK-20260801-054 reviews. NOTHING in this file may be edited to supply them.

ATS-LPF-1 clause 5: THE CALIBRATION ARM IS STRUCTURALLY BLIND TO THE REAL
OBJECT. `run_calibration()` names neither `deterministic_factor_base`, nor
`int1_fibre_invariants` (the Semaev specialization), nor `run_measurement`, and
constructs no factor base and no S_3 specialization by any route. The only
function in this file that touches the deterministic factor base is
`deterministic_factor_base()`; it flips the module-level tripwire
`_REAL_OBJECT_TOUCHED`, which `run_calibration()` asserts is still False when it
finishes and records as `LPF_real_object_touched`.

CAL-LPF-1 non_evidential: the calibration output is NON-EVIDENTIAL about
H-LPF-001, HEUR-DS-1, H-SMTH-001, H-DS-001, H-EQD-001 and H-DEP-001, in either
direction. This driver therefore FREEZES NO THRESHOLD AND NO BAND, states no
disposition, and selects no branch of any reading rule. Where the frozen
THR-LPF-1 rule ("the 2nd and 199th ascending order statistics of the 200
LPF-CAL-A replicate values") is applied to produce the detection rates that
LPF-CAL-D requires, the resulting interval is emitted under the key
`band_by_frozen_rule` and carries `band_status` recording that it is COMPUTED BY
THE FROZEN RULE AND NOT FROZEN; TASK-20260801-052 owns the freeze.

Usage
-----
  python3 experiments/EXP-LPF-001/implementation/lpf001_driver.py \
      --mode calib --out-run <run dir> --out-results <results/calib dir> \
      --authorization-receipt <TASK-20260801-048 snapshot_commit_receipt.json>

  python3 experiments/EXP-LPF-001/implementation/lpf001_driver.py \
      --mode measure --out-run <run dir> --out-results <results/measure dir> \
      --reading-rule experiments/EXP-LPF-001/reading_rule.yaml \
      --approval-receipt <TASK-20260801-055 snapshot_commit_receipt.json>

`--mode measure` REFUSES TO START unless BOTH gates are present: an approval
receipt recording APPROVAL_DETERMINATION == "APPROVED", and a frozen reading
rule file that parses and carries the archived bands. `--mode calib` refuses to
start unless the authorization receipt records
CALIBRATION_AUTHORIZATION == "AUTHORIZED".
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

# ==========================================================================
# 1. FROZEN CONSTANTS. Every one is fixed by the specification; none is tuned
#    here, and no threshold, cut or band appears among them.
# ==========================================================================
EXPERIMENT_ID = "EXP-LPF-001"
SPEC_PATH = "experiments/EXP-LPF-001/specification.yaml"
SPEC_SHA256_AT_FREEZE = (
    "0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda")
CONTRACT_COMMIT = "ba1567ee415b680b2d25108d59b9884f432d44d8"

MASTER_SEED = 2301                        # cells: generate_instance(2301, bits)
FIELD_BITS = (16, 20)                     # cells.bits
BFB = 512                                 # factor_base.Bfb  (FACTOR-BASE SIZE)
N_PER_SAMPLE_SET = BFB * (BFB - 1) // 2   # 130816, i < j, diagonal excluded
M_ARITY = 4                               # intermediate_generation, m = 4
D_HALF_M = 2                              # d_half[4] = 2
CONSTANT_FACTOR_C = 8                     # EXP-DS-001 frozen constant factor
MIN_SAMPLES_PER_BIT_SIZE = 100000         # inherited adequacy minimum

R_CAL = 200                               # LPF-CAL-A replicates per cell
R_IDENT = 20                              # LPF-CAL-B replicates per cell
R_PROD = 20                               # LPF-CAL-C replicates per cell
R_PLANT = 20                              # LPF-CAL-D replicates per rung/cell
TAIL_RANK = 10                            # TAIL-LPF-1: the TENTH largest Z
BAND_RANK_LO = 2                          # THR-LPF-1 ascending order statistic
BAND_RANK_HI = 199                        # THR-LPF-1 ascending order statistic
DET_COUNT_BAR = 19                        # DET-LPF-1: at least 19 of 20
DET_CP_LOWER_BAR = 0.75                   # DET-LPF-1: one-sided 95% CP >= 0.75
DET_CP_ALPHA = 0.05                       # DET-LPF-1: 95 percent, one sided

# smoothness_ladder, frozen integer ladders, element by element.
BSM_LADDER = {
    16: [(2, 65536), (3, 1626), (4, 256), (5, 84), (6, 40)],
    20: [(2, 1048576), (3, 10321), (4, 1024), (5, 256), (6, 102)],
}
D_BY_BITS = {16: 2 ** 32, 20: 2 ** 40}    # D_formula 2**(bits * d_half[m])

# rho_reference_values. USED ONLY AS A REPRODUCTION CHECK on the driver's own
# numerical solution of the Dickman delay equation, never as a substitute.
FROZEN_RHO_TABLE = {
    1: 1.0, 2: 0.30685, 3: 0.048608,
    4: 0.0049109, 5: 0.00035473, 6: 0.000019650,
}
DICKMAN_REPRODUCTION_TOLERANCE = 0.01     # L-5 at a relative discrepancy > 1%

# POW-LPF-1: powered rungs are those where the model expects >= 30 smooth.
POW_MIN_EXPECTED_SMOOTH = 30

# ladders. Both families run at EVERY rung (PERTURB-MOVE-1).
LADDER_SMOOTH = (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05)
LADDER_ROUGH = (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05)
GAMMA_STAR = 0.01

# budget. Hard limits, applied as deadlines and as a pre-bulk projection gate.
CALIB_WALL_CLOCK_SECONDS = 14400
MEASURE_WALL_CLOCK_SECONDS = 5400
MAXIMUM_MEMORY_GB = 8
PILOT_FACTORIZATIONS_PER_CELL = 10000
# The pilot projection model. MODELED, NOT MEASURED: the pilot measures the
# factorization rate only, and this multiplier is the declared allowance for
# statistics, plant construction and I/O on top of it. Declared here, pre-datum.
PILOT_OVERHEAD_MULTIPLIER = 2.0

# Stream offsets. The calibration streams and the measurement stream are
# DISJOINT by construction; a collision is an L-0 integrity failure.
STREAM_OFFSETS = {
    "calib_pilot": 100000,
    "calib_uniform": 200000,
    "calib_identity_uniform": 300000,
    "calib_identity_synth": 400000,
    "calib_product": 500000,
    "calib_plant_smooth": 600000,
    "calib_plant_rough": 700000,
    "measure_uniform_ks2": 900000,
}

# The EXP-EQD-001 archived factor_base_sha256 values, READ-ONLY, asserted by the
# measurement arm only (experiments/EXP-EQD-001/results/real/EQD_report.json).
EQD_FACTOR_BASE_SHA256 = {
    16: "4521b0d1231554cfbbbd0aeb601f913ad64f30426dd7ebe6f3b61bc77fe75ea1",
    20: "d7a8c2bbe474821bfe95185b6f05c4ee7b2b0f0ab5c805f7f34c1c7303d8fa69",
}

CERTIFYING_STATISTICS = ("STAT-RATE-u", "STAT-KS-DICK", "STAT-TAIL-DEEP")

# ATS-LPF-1 clause 5 tripwire. Flipped ONLY by deterministic_factor_base().
_REAL_OBJECT_TOUCHED = False


# ==========================================================================
# 2. Hashing, logging, deterministic streams.
# ==========================================================================
def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}",
          flush=True)


class Stream:
    """A named, seeded, index-addressable source of per-draw seeds.

    draw_seed(k) = int(sha256("<seed>:<name>:<k>")[:16], 16). Each draw index
    yields an independent numpy Generator, so any single replicate is
    regenerable exactly without replaying the ones before it.
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


class Deadline:
    """Hard wall-clock limit. Exhaustion is a BUDGET EVENT and L-0
    infrastructure signal, never a result about anything."""

    def __init__(self, seconds: int):
        self.seconds = int(seconds)
        self.t0 = time.time()
        self.events: list[dict] = []

    def elapsed(self) -> float:
        return time.time() - self.t0

    def check(self, where: str) -> None:
        e = self.elapsed()
        if e > self.seconds:
            self.events.append({"kind": "wall_clock_exceeded", "where": where,
                                "elapsed_seconds": e, "limit_seconds": self.seconds})
            raise BudgetExceeded(
                f"WALL-CLOCK BUDGET EXCEEDED at {where}: {e:.1f}s > {self.seconds}s. "
                "BUDGET EVENT, L-0 INSTRUMENT SIGNAL, NEVER A RESULT.")


class BudgetExceeded(RuntimeError):
    pass


class IntegrityFailure(RuntimeError):
    pass


# ==========================================================================
# 3. FACTORIZATION. The first new dependency this lane has needed.
#    Carried in-repository: a sieve of primes, a deterministic Miller-Rabin,
#    and a vectorised complete trial-division batch factorizer. No external
#    factorization library is used, so the module and version recorded in
#    environment.json are this file and its sha256.
# ==========================================================================
_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_MR_SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin. The base set {2,...,37} is a proven
    deterministic witness set for every n < 3.317e24; every integer this
    experiment touches is below 2**40."""
    n = int(n)
    if n < 2:
        return False
    for q in _MR_SMALL:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def primes_upto(n: int) -> np.ndarray:
    """Sieve of Eratosthenes."""
    if n < 2:
        return np.zeros(0, dtype=np.int64)
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(math.isqrt(n)) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.flatnonzero(s).astype(np.int64)


class Factorizer:
    """Complete factorization of int64 arrays by vectorised trial division.

    The prime table is sieved once to isqrt(X) for the cell and INDEPENDENTLY
    VERIFIED PRIME by the Miller-Rabin routine above (a second code path from
    the sieve that produced it). An element leaves the active set only when its
    remaining cofactor is strictly below q**2 for the current prime q, at which
    point every prime below q has already been divided out, so the cofactor is
    1 or prime; that residual is then Miller-Rabin tested PER SAMPLE.

    VERIFICATION SEMANTICS, declared here and in implementation.md:
      * product: `removed_product * residual == N` is asserted elementwise on
        100 percent of samples;
      * primality of every returned factor: the small factors are members of
        the sieved table, every entry of which was Miller-Rabin verified prime
        at construction; the residual factor of each sample is Miller-Rabin
        tested individually, per sample.
    A sample counts as verified only if both hold.
    """

    def __init__(self, x_max: int):
        self.x_max = int(x_max)
        self.bound = int(math.isqrt(self.x_max)) + 1
        self.primes = primes_upto(self.bound)
        self.primes_list = self.primes.tolist()
        # Independent primality verification of the whole table.
        bad = [q for q in self.primes_list if not is_prime(q)]
        if bad:
            raise IntegrityFailure(f"sieve produced non-primes: {bad[:5]}")
        self.table_sha256 = sha256_text(
            "\n".join(str(q) for q in self.primes_list))

    def factor(self, arr: np.ndarray) -> dict:
        """Returns p_max, and the verification counts, for an int64 array."""
        n = arr.size
        rem = arr.astype(np.int64).copy()
        if int(rem.min()) < 1:
            raise IntegrityFailure("factorizer received a value below 1")
        if int(rem.max()) > self.x_max:
            raise IntegrityFailure("factorizer received a value above X")
        p_max = np.ones(n, dtype=np.int64)
        removed = np.ones(n, dtype=np.int64)
        act = np.arange(n)
        for q in self.primes_list:
            if act.size == 0:
                break
            sub = rem[act]
            keep = sub >= q * q
            if not keep.all():
                act = act[keep]
                if act.size == 0:
                    break
                sub = rem[act]
            hit = act[(sub % q) == 0]
            while hit.size:
                rem[hit] //= q
                p_max[hit] = q
                removed[hit] *= q
                hit = hit[(rem[hit] % q) == 0]
        # residual is 1 or prime; p_max is the larger of the two
        p_max = np.maximum(p_max, rem)
        prod_ok = bool(np.array_equal(removed * rem, arr.astype(np.int64)))
        # PER-SAMPLE primality of the residual factor.
        res_list = rem.tolist()
        prime_fail = 0
        for v in res_list:
            if v > 1 and not is_prime(v):
                prime_fail += 1
        verified = n if (prod_ok and prime_fail == 0) else 0
        return {
            "p_max": p_max,
            "residual": rem,
            "verified_count": verified,
            "total_count": n,
            "product_check_passed": prod_ok,
            "residual_primality_failures": prime_fail,
        }


def verify_known_factorization(values: np.ndarray,
                               factor_lists: list[list[int]]) -> dict:
    """Verification path for the plant integers, whose factorization is KNOWN
    BY CONSTRUCTION: product asserted equal to N and every factor Miller-Rabin
    tested, per sample, with no reliance on the batch factorizer."""
    ok = 0
    for v, fl in zip(values.tolist(), factor_lists):
        pr = 1
        good = True
        for f in fl:
            pr *= f
            if not is_prime(f):
                good = False
                break
        if good and pr == int(v):
            ok += 1
    return {"verified_count": ok, "total_count": len(factor_lists)}


# ==========================================================================
# 4. THE DICKMAN FUNCTION, by numerical solution of the delay equation.
#    LPF-CAL-E. The frozen table is a reproduction check and nothing else.
# ==========================================================================
class Dickman:
    """rho solved from u*rho(u) = int_{u-1}^{u} rho(t) dt, rho == 1 on [0, 1].

    Composite Simpson on a uniform grid of step 1/M, implicit in the unknown
    right endpoint. No table value is read; FROZEN_RHO_TABLE is compared
    against the result and never substituted into it.
    """

    def __init__(self, u_max: float = 44.0, M: int = 4000):
        self.M = int(M)
        self.h = 1.0 / self.M
        self.u_max = float(u_max)
        n = int(round(u_max * self.M))
        rho = np.zeros(n + 1, dtype=np.float64)
        rho[:self.M + 1] = 1.0
        w = np.ones(self.M + 1, dtype=np.float64)
        w[1:-1:2] = 4.0
        w[2:-1:2] = 2.0
        w *= self.h / 3.0
        w_head = w[:-1]
        w_tail = float(w[-1])
        for k in range(self.M + 1, n + 1):
            s = float(np.dot(w_head, rho[k - self.M:k]))
            rho[k] = s / (k * self.h - w_tail)
        self.grid = np.arange(n + 1, dtype=np.float64) * self.h
        self.rho_grid = rho

    def rho(self, u):
        """rho at scalar or array u, by linear interpolation on the grid.
        rho == 1 below 1; the grid extends to u_max and is not extrapolated."""
        uu = np.asarray(u, dtype=np.float64)
        if float(np.max(uu)) > self.u_max:
            raise IntegrityFailure(f"u = {float(np.max(uu))} beyond the solved grid")
        out = np.interp(np.clip(uu, 0.0, self.u_max), self.grid, self.rho_grid)
        out = np.where(uu <= 1.0, 1.0, out)
        return float(out) if np.isscalar(u) or np.ndim(u) == 0 else out

    def reproduction_report(self) -> dict:
        rows = []
        worst = 0.0
        for u, frozen in sorted(FROZEN_RHO_TABLE.items()):
            got = float(self.rho(float(u)))
            rel = abs(got - frozen) / frozen
            worst = max(worst, rel)
            rows.append({"u": u, "rho_computed_by_driver": got,
                         "rho_frozen_reference": frozen,
                         "relative_discrepancy": rel})
        return {
            "id": "LPF-CAL-E",
            "method": ("numerical solution of the Dickman delay equation "
                       "u*rho(u) = integral_{u-1}^{u} rho(t) dt by composite "
                       "Simpson on a uniform grid, implicit in the right "
                       "endpoint; rho == 1 on [0,1]"),
            "grid_step": self.h,
            "grid_u_max": self.u_max,
            "rows": rows,
            "worst_relative_discrepancy": worst,
            "tolerance_for_L5_apparatus_defect": DICKMAN_REPRODUCTION_TOLERANCE,
            "worst_discrepancy_within_tolerance": worst <= DICKMAN_REPRODUCTION_TOLERANCE,
            "note": ("The frozen table is a REPRODUCTION CHECK on this "
                     "solution and is never substituted for it. This driver "
                     "reads rho only from its own solved grid."),
        }


# ==========================================================================
# 5. STAT-LPF-1. Forms only; no thresholds, no bands, no reject booleans that
#    are not read straight off a band supplied by the caller.
# ==========================================================================
def z_values(values: np.ndarray, p_max: np.ndarray) -> np.ndarray:
    """Z_j = ln(N_j) / ln(P_max(N_j)). TAIL-LPF-1 contributes only samples with
    N_j > 1 and P_max(N_j) > 1."""
    m = (values > 1) & (p_max > 1)
    v = values[m].astype(np.float64)
    q = p_max[m].astype(np.float64)
    return np.log(v) / np.log(q)


def stat_rate_u(p_max: np.ndarray, bits: int, dick: Dickman) -> list[dict]:
    """STAT-RATE-u. p_hat(u) = fraction with P_max <= Bsm at each frozen rung,
    R(u) = p_hat(u) / rho(u) with u RECOMPUTED from the integer Bsm by the
    frozen u_star_formula u = ln(D)/ln(Bsm)."""
    D = D_BY_BITS[bits]
    lnD = math.log(D)
    n = p_max.size
    rows = []
    for u_target, bsm in BSM_LADDER[bits]:
        u = lnD / math.log(bsm)
        rho = float(dick.rho(u))
        cnt = int(np.count_nonzero(p_max <= bsm))
        p_hat = cnt / n
        rows.append({
            "u_target": u_target,
            "Bsm": bsm,
            "u_recomputed": u,
            "rho_u_computed": rho,
            "smooth_count": cnt,
            "n": n,
            "p_hat_u": p_hat,
            "R_u": (p_hat / rho) if rho > 0 else None,
            "expected_smooth_under_model": n * rho,
            "powered_flag": (n * rho) >= POW_MIN_EXPECTED_SMOOTH,
        })
    return rows


def stat_ks_dickman(z: np.ndarray, dick: Dickman) -> float:
    """STAT-KS-DICK. One-sample Kolmogorov-Smirnov distance between the
    empirical CDF of Z and the classical Dickman largest-prime-factor CDF
    F(z) = 1 - rho(z) for z >= 1, F(z) = 0 for z < 1.

    IMPLEMENTATION READING, declared in implementation.md and routed to
    TASK-20260801-054: Dickman's theorem gives
    P(P_max(N) <= N**(1/z)) -> rho(z), i.e. P(Z >= z) -> rho(z), hence
    F(z) = 1 - rho(z). This is a CDF OF Z AND NOT OF A RAW DEGREE; comparing a
    CDF of raw polynomial degrees to rho is the forbidden category error.
    """
    if z.size == 0:
        return float("nan")
    zs = np.sort(z)
    F = 1.0 - dick.rho(np.clip(zs, 0.0, dick.u_max))
    F = np.clip(F, 0.0, 1.0)
    m = zs.size
    i = np.arange(1, m + 1, dtype=np.float64)
    d_plus = float(np.max(i / m - F))
    d_minus = float(np.max(F - (i - 1) / m))
    return max(d_plus, d_minus)


def stat_tail_deep(z: np.ndarray) -> float:
    """STAT-TAIL-DEEP. T_deep = the TENTH LARGEST Z. Rank ten and not rank one
    DELIBERATELY (TAIL-LPF-1): a single extreme order statistic has an unstable
    law and was the proximate cause of the TAIL-DS-1 defect."""
    if z.size < TAIL_RANK:
        return float("nan")
    part = np.partition(z, z.size - TAIL_RANK)
    return float(part[z.size - TAIL_RANK])


def stat_ks2(za: np.ndarray, zb: np.ndarray) -> float:
    """STAT-KS2-CAL. NON-CERTIFYING FOR BOTH LIMBS by CERT-LPF-1; recorded with
    no threshold and no reject boolean, and read by no branch."""
    x, y = np.sort(za), np.sort(zb)
    allv = np.concatenate([x, y])
    f1 = np.searchsorted(x, allv, side="right") / x.size
    f2 = np.searchsorted(y, allv, side="right") / y.size
    return float(np.max(np.abs(f1 - f2)))


def all_statistics(values: np.ndarray, p_max: np.ndarray, bits: int,
                   dick: Dickman) -> dict:
    """Every member of STAT-LPF-1 that a single sample set determines."""
    z = z_values(values, p_max)
    rate = stat_rate_u(p_max, bits, dick)
    return {
        "rate_rows": rate,
        "ks_dick": stat_ks_dickman(z, dick),
        "t_deep": stat_tail_deep(z),
        "z_contributing_count": int(z.size),
        "z_excluded_count": int(values.size - z.size),
        "n": int(values.size),
    }


def flatten_statistics(st: dict) -> dict:
    """The flat (statistic id -> scalar) view the bands and the movement table
    are computed over. STAT-RATE-u contributes one entry per frozen rung; the
    rung is part of the statistic id and is not a new statistic."""
    out = {"STAT-KS-DICK": st["ks_dick"], "STAT-TAIL-DEEP": st["t_deep"]}
    for r in st["rate_rows"]:
        out[f"STAT-RATE-u@u_target={r['u_target']}"] = r["p_hat_u"]
    return out


def statistic_ids(bits: int) -> list[str]:
    ids = [f"STAT-RATE-u@u_target={u}" for u, _ in BSM_LADDER[bits]]
    return ids + ["STAT-KS-DICK", "STAT-TAIL-DEEP"]


# ==========================================================================
# 6. Exact binomial helpers. DET-LPF-1's second clause and nothing else.
# ==========================================================================
def _binom_tail_ge(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    if p <= 0.0:
        return 1.0 if k <= 0 else 0.0
    if p >= 1.0:
        return 1.0 if k <= n else 0.0
    tot = 0.0
    for i in range(k, n + 1):
        tot += math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
    return tot


def clopper_pearson_lower(k: int, n: int, alpha: float = DET_CP_ALPHA) -> float:
    """Exact one-sided lower Clopper-Pearson bound: the p solving
    P(X >= k) = alpha, by bisection. k == 0 gives 0."""
    if k <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _binom_tail_ge(k, n, mid) < alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson_two_sided(k: int, n: int, alpha: float = 0.05) -> list:
    if k == 0:
        lo = 0.0
    else:
        lo = clopper_pearson_lower(k, n, alpha / 2.0)
    if k == n:
        hi = 1.0
    else:
        hi = 1.0 - clopper_pearson_lower(n - k, n, alpha / 2.0)
    return [lo, hi]


# ==========================================================================
# 7. CELLS AND OBJECTS.
#    CalibrationCell carries the FIELD PRIME AND NOTHING ELSE. It builds no
#    x-coordinate membership array, no factor base and no S_3 specialization.
# ==========================================================================
class CalibrationCell:
    """One toy field cell, as seen by the calibration arm.

    RT047-B5 discipline: `bits` names the FIELD prime p and nothing else. No
    discrete logarithm is computed, no relation is harvested, no search is run.

    range_matching_note: samples are drawn on [1, p**2], NOT on [1, D], so the
    calibration and (later) the real arm share an exactly matched range. D is
    retained only as the frozen bound that defines u.
    """

    def __init__(self, bits: int):
        sys.path.insert(0, os.getcwd())
        from harness.toycurve import generate_instance
        inst = generate_instance(MASTER_SEED, bits)
        self.bits = bits
        self.p = int(inst.p)
        self.X = self.p * self.p
        self.D = D_BY_BITS[bits]
        if self.X > self.D:
            raise IntegrityFailure("p**2 exceeds the frozen D at this cell")
        self.factorizer = Factorizer(self.X)
        self.small_smooth_primes = None   # set lazily per plant family

    def descriptor(self) -> dict:
        return {
            "field_bits": self.bits,
            "p": self.p,
            "X_equals_p_squared": self.X,
            "D_frozen": self.D,
            "X_over_D": self.X / self.D,
            "curve_instance_source":
                f"harness.toycurve.generate_instance({MASTER_SEED}, {self.bits})",
            "n_per_sample_set": N_PER_SAMPLE_SET,
            "trial_division_prime_table_bound": self.factorizer.bound,
            "trial_division_prime_count": int(self.factorizer.primes.size),
            "trial_division_prime_table_sha256": self.factorizer.table_sha256,
            "bit_size_labelling_caveat":
                "`bits` names the FIELD prime p and nothing else (RT047-B5).",
        }

    # -- OBJ-NULL-UNIF -----------------------------------------------------
    def draw_uniform(self, stream: Stream, k: int) -> np.ndarray:
        """Uniform random integers on [1, p**2]. THE APPARATUS CALIBRATION,
        AND NOT THE COMPARISON (ABS-REL-LPF-1)."""
        rng = stream.generator(k)
        return rng.integers(1, self.X + 1, size=N_PER_SAMPLE_SET, dtype=np.int64)

    # -- OBJ-NULL-SYNTH ----------------------------------------------------
    def draw_synth(self, stream: Stream, k: int) -> np.ndarray:
        """ENC-B applied to (e_1, e_2) drawn uniformly on [0, p) x [0, p).

        APPARATUS IDENTITY CONTROL, NOT AN INTERPRETIVE NULL. ENC-B is a
        bijection from [0,p) x [0,p) onto [1, p**2], so this is THE SAME
        DISTRIBUTION as OBJ-NULL-UNIF BY DERIVATION; disagreement beyond the
        band is an implementation defect in the encoder or sampler, never a
        mathematical result. Stated in advance so its agreement can never later
        be presented as corroboration.
        """
        rng = stream.generator(k)
        e1 = rng.integers(0, self.p, size=N_PER_SAMPLE_SET, dtype=np.int64)
        e2 = rng.integers(0, self.p, size=N_PER_SAMPLE_SET, dtype=np.int64)
        return encode_enc_b(e1, e2, self.p)

    # -- OBJ-CTRL-PRODUCT --------------------------------------------------
    def draw_product_control(self, stream: Stream, k: int) -> np.ndarray:
        """N = max(lift(e_1), 1) * max(lift(e_2), 1) on uniformly drawn
        (e_1, e_2). THE DERIVABLE-SMOOTH POSITIVE CONTROL. A product of two
        integers each below p is provably and substantially smoother than a
        uniform integer below p**2, so its rejection is derivable in advance.

        ENC-A IS NOT A DECISION ENCODING. This object appears in this
        experiment ONLY as an apparatus control and is never cited as evidence
        for or against HEUR-DS-1 in either direction.
        """
        rng = stream.generator(k)
        e1 = rng.integers(0, self.p, size=N_PER_SAMPLE_SET, dtype=np.int64)
        e2 = rng.integers(0, self.p, size=N_PER_SAMPLE_SET, dtype=np.int64)
        return np.maximum(e1, 1) * np.maximum(e2, 1)


def encode_enc_b(e1: np.ndarray, e2: np.ndarray, p: int) -> np.ndarray:
    """ENC-B, THE ONLY DECISION ENCODING.
    N = lift(e_1) * p + lift(e_2) + 1, range exactly [1, p**2], a BIJECTION."""
    return e1.astype(np.int64) * p + e2.astype(np.int64) + 1


# -- plant construction ----------------------------------------------------
def bsm_at_u4(bits: int) -> int:
    for u_target, bsm in BSM_LADDER[bits]:
        if u_target == 4:
            return bsm
    raise IntegrityFailure("no u_target == 4 rung in the frozen ladder")


def build_smooth_replacement(v: int, prime_pool: list[int],
                             rng: np.random.Generator) -> tuple[int, list[int]]:
    """An integer of matched size constructed as a product of primes at most
    Bsm(u = 4), WHOSE FACTORIZATION AND LARGEST PRIME FACTOR ARE KNOWN BY
    CONSTRUCTION. Costs no factorization (plant_construction_note).

    Matched size: primes are multiplied in while the product stays at or below
    the replaced value v, so the replacement lies in (v / Bsm, v]. It moves
    mass into the HIGH-Z part of the Z-distribution: its largest prime factor
    is at most Bsm(u=4) by construction, so Z = ln N / ln P_max is large.
    """
    if v < 2:
        return 1, []
    m = 1
    factors: list[int] = []
    misses = 0
    npool = len(prime_pool)
    while misses < 40:
        q = prime_pool[int(rng.integers(0, npool))]
        if m * q <= v:
            m *= q
            factors.append(q)
            misses = 0
        else:
            misses += 1
    if not factors:
        # v is below the smallest pool prime; use the largest pool prime <= v
        cand = [q for q in prime_pool if q <= v]
        if cand:
            m = cand[-1]
            factors = [m]
        else:
            m, factors = 1, []
    return m, factors


def build_rough_replacement(v: int, p: int,
                            rng: np.random.Generator) -> tuple[int, list[int]]:
    """An integer of matched size constructed as q * r with q A PRIME ABOVE
    sqrt(X) = p, WHOSE LARGEST PRIME FACTOR IS KNOWN BY CONSTRUCTION.

    Since r <= v / q < X / p = p < q, the largest prime factor is exactly q and
    Z = ln(q r)/ln q < 2. THE FAMILY MOVES MASS INTO THE LOW-Z PART OF THE
    Z-DISTRIBUTION (Z < 2, i.e. the rough end), which is why it is not
    invariant in law and is not the DESIGN-TRAP-LPF-1 same-law replacement.

    Returns (0, []) when v is too small to admit the construction; the caller
    counts those as construction fallbacks and leaves the original sample.
    """
    if v < 64 * p:
        return 0, []
    q_lo, q_hi = p + 1, v // 64
    if q_hi <= q_lo:
        return 0, []
    lq = math.log(q_lo)
    hq = math.log(q_hi)
    for _ in range(60):
        q = int(math.exp(lq + float(rng.random()) * (hq - lq)))
        q = max(q_lo, min(q_hi, q)) | 1
        # nearest prime at or above q, staying inside the window
        found_q = 0
        cand = q
        while cand <= q_hi:
            if is_prime(cand):
                found_q = cand
                break
            cand += 2
        if not found_q:
            continue
        r_hi = v // found_q
        r_lo = max(2, v // (2 * found_q))
        if r_hi < 2:
            continue
        # a prime in (r_lo, r_hi]
        found_r = 0
        for _try in range(80):
            r = int(rng.integers(r_lo, r_hi + 1))
            if r > 2 and r % 2 == 0:
                r -= 1
            if r < 2:
                r = 2
            if is_prime(r):
                found_r = r
                break
        if not found_r:
            cand = r_hi if r_hi % 2 == 1 else r_hi - 1
            while cand >= max(3, r_lo):
                if is_prime(cand):
                    found_r = cand
                    break
                cand -= 2
            if not found_r and r_hi >= 2 >= r_lo:
                found_r = 2
        if not found_r:
            continue
        return found_q * found_r, [found_q, found_r]
    return 0, []


def apply_plant(base_values: np.ndarray, base_pmax: np.ndarray, gamma: float,
                family: str, cell: CalibrationCell,
                stream: Stream, k: int) -> dict:
    """OBJ-PLANT-{SMOOTH,ROUGH}-gamma: a uniform calibration replicate in which
    a gamma fraction of the samples is REPLACED by integers of matched size and
    KNOWN factorization. No plant rung costs additional factorization."""
    rng = stream.generator(k)
    n = base_values.size
    n_rep = int(round(gamma * n))
    idx = rng.choice(n, size=n_rep, replace=False)
    values = base_values.copy()
    p_max = base_pmax.copy()
    new_vals: list[int] = []
    new_facs: list[list[int]] = []
    fallbacks = 0
    if family == "OBJ-PLANT-SMOOTH":
        pool = cell.small_smooth_primes
        for i in idx.tolist():
            m, facs = build_smooth_replacement(int(base_values[i]), pool, rng)
            if m < 2 or not facs:
                fallbacks += 1
                continue
            values[i] = m
            p_max[i] = max(facs)
            new_vals.append(m)
            new_facs.append(facs)
    elif family == "OBJ-PLANT-ROUGH":
        for i in idx.tolist():
            m, facs = build_rough_replacement(int(base_values[i]), cell.p, rng)
            if m < 2 or not facs:
                fallbacks += 1
                continue
            values[i] = m
            p_max[i] = max(facs)
            new_vals.append(m)
            new_facs.append(facs)
    else:
        raise IntegrityFailure(f"unknown plant family {family}")
    ver = verify_known_factorization(np.array(new_vals, dtype=np.int64), new_facs)
    return {"values": values, "p_max": p_max,
            "replaced_requested": n_rep, "replaced_effected": len(new_vals),
            "construction_fallbacks": fallbacks,
            "known_factorization_verification": ver}


# ==========================================================================
# 8. THE REAL OBJECT. ATS-LPF-1 clause 5 tripwire lives here and NOWHERE ELSE.
#    Nothing in section 8 is reachable from run_calibration.
# ==========================================================================
def deterministic_factor_base(bits: int) -> dict:
    """OBJ-REAL support: the FROZEN DETERMINISTIC factor base -- the first 512
    x-coordinates in F_p, in increasing integer order, that are x-coordinates
    of points of E(F_p). Identical to the EXP-EQD-001 OBJ-REAL base.

    CALLING THIS FUNCTION IS "SEEING THE REAL DATA". It is called by
    `run_measurement()` and by nothing else, and it flips the module-level
    tripwire that `run_calibration()` asserts against.
    """
    global _REAL_OBJECT_TOUCHED
    _REAL_OBJECT_TOUCHED = True
    sys.path.insert(0, os.getcwd())
    from harness.toycurve import generate_instance
    inst = generate_instance(MASTER_SEED, bits)
    p, a, b = int(inst.p), int(inst.a), int(inst.b)
    xs = np.arange(p, dtype=np.int64)
    rhs = (xs * xs % p * xs % p + a * xs + b) % p
    leg = _modpow_arr(rhs, (p - 1) // 2, p)
    is_x = (leg == 1) | (rhs == 0)
    X_E = xs[is_x]
    if X_E.size < BFB:
        raise IntegrityFailure(f"only {X_E.size} x-coordinates, need {BFB}")
    base = X_E[:BFB].astype(np.int64)
    return {
        "xs": base, "p": p, "a": a, "b": b,
        "factor_base_sha256": sha256_text(
            "\n".join(str(int(v)) for v in base)),
    }


def _modpow_arr(base: np.ndarray, exp: int, p: int) -> np.ndarray:
    result = np.ones_like(base)
    b = base % p
    e = int(exp)
    while e:
        if e & 1:
            result = (result * b) % p
        b = (b * b) % p
        e >>= 1
    return result


def int1_fibre_invariants(xi: np.ndarray, xj: np.ndarray, p: int, a: int,
                          b: int) -> tuple[np.ndarray, np.ndarray, int]:
    """INT-1, THE SEMAEV SPECIALIZATION, quoted from the frozen contract:

      f_ij(Z) = S_3(x_i, x_j, Z) = c_2 Z**2 + c_1 Z + c_0 over F_p, with
        c_2 = (x_i - x_j)**2
        c_1 = -2 * ((x_i + x_j) * (x_i x_j + a) + 2 b)
        c_0 = (x_i x_j - a)**2 - 4 b (x_i + x_j)
      e_1 = (-c_1) * c_2**(-1) mod p,   e_2 = c_0 * c_2**(-1) mod p.

    Half-tuples with c_2 == 0 mod p are DEGENERATE draws; they are counted,
    reported and excluded from every statistic, never silently dropped. Under
    the i < j enumeration over distinct x-coordinates the count is structurally
    zero.
    """
    if p >= 2 ** 31:
        raise IntegrityFailure("p too large for the int64 vectorisation")
    xi = xi.astype(np.int64) % p
    xj = xj.astype(np.int64) % p
    s = (xi + xj) % p
    m = (xi * xj) % p
    d = (xi - xj) % p
    c2 = (d * d) % p
    degenerate = int(np.count_nonzero(c2 == 0))
    keep = c2 != 0
    c2k = c2[keep]
    sk = s[keep]
    mk = m[keep]
    inv_c2 = _modpow_arr(c2k, p - 2, p)
    neg_c1 = (2 * ((sk * ((mk + a) % p)) % p + (2 * b) % p)) % p
    t0 = (mk - a) % p
    c0 = ((t0 * t0) % p - ((4 * b) % p) * sk) % p
    e1 = (neg_c1 * inv_c2) % p
    e2 = (c0 * inv_c2) % p
    return e1, e2, degenerate


def upper_triangle_indices(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Strictly i < j. REP-2: THE DIAGONAL IS EXCLUDED BY CONSTRUCTION, NOT BY
    A FILTER. n = C(512, 2) = 130816."""
    iu, ju = np.triu_indices(n, k=1)
    return iu.astype(np.int64), ju.astype(np.int64)


# ==========================================================================
# 9. BANDS AND MOVEMENT. Forms fixed by THR-LPF-1 / PERTURB-MOVE-1; the
#    numbers are MEASURED and the FREEZE IS NOT PERFORMED HERE.
# ==========================================================================
BAND_STATUS = ("COMPUTED BY THE FROZEN THR-LPF-1 RULE FROM THE MEASURED "
               "LPF-CAL-A REPLICATES. NOT FROZEN. TASK-20260801-052 OWNS THE "
               "FREEZE; THIS DRIVER SUPPLIES A NUMBER AND NEVER A CHOICE.")


def band_by_frozen_rule(values: list[float]) -> dict:
    """THR-LPF-1: the [2nd, 199th] ASCENDING order statistic pair of the 200
    LPF-CAL-A replicate values. Rejection is STRICTLY BELOW the lower or
    STRICTLY ABOVE the upper. The exact per-comparison false-fire probability
    on a fresh correct draw is 2/201 + 2/201 = 4/201 = 0.0199."""
    v = sorted(float(x) for x in values)
    if len(v) != R_CAL:
        raise IntegrityFailure(
            f"band rule needs exactly {R_CAL} replicate values, got {len(v)}")
    return {
        "lower": v[BAND_RANK_LO - 1],
        "upper": v[BAND_RANK_HI - 1],
        "lower_rank_ascending": BAND_RANK_LO,
        "upper_rank_ascending": BAND_RANK_HI,
        "replicates": R_CAL,
        "per_comparison_false_fire_probability": 4.0 / 201.0,
        "rejection_rule": "STRICTLY BELOW lower OR STRICTLY ABOVE upper",
        "band_status": BAND_STATUS,
    }


def spread(values: list[float]) -> dict:
    a = np.asarray([float(x) for x in values], dtype=np.float64)
    return {
        "count": int(a.size),
        "min": float(np.min(a)), "max": float(np.max(a)),
        "median": float(np.median(a)), "mean": float(np.mean(a)),
        "sd": float(np.std(a, ddof=1)) if a.size > 1 else 0.0,
    }


def rejects(value: float, band: dict) -> bool:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return False
    return bool(value < band["lower"] or value > band["upper"])


def band_position(value: float, band: dict, sd: float) -> float:
    """LPF_band_position: the signed margin to the NEARER edge, in units of the
    measured null standard deviation. Positive inside, negative outside."""
    if sd <= 0 or value is None or (isinstance(value, float) and math.isnan(value)):
        return float("nan")
    return float(min(value - band["lower"], band["upper"] - value) / sd)


# ==========================================================================
# 10. THE CALIBRATION ARM. RUN-LPF-001-calib. NON-EVIDENTIAL.
#     Objects: OBJ-NULL-UNIF, OBJ-NULL-SYNTH, OBJ-CTRL-PRODUCT,
#     OBJ-PLANT-SMOOTH-gamma, OBJ-PLANT-ROUGH-gamma. NO OBJ-REAL.
# ==========================================================================
def run_pilot(cells: dict, dick: Dickman, deadline: Deadline) -> dict:
    """THE BUDGET GATE. A pilot of 10000 factorizations per cell, the achieved
    rate measured, the full calibration cost extrapolated, and an ABORT BEFORE
    ANY BULK WORK if the projection exceeds the wall-clock budget.

    AN ABORT AT THIS GATE IS A BUDGET EVENT AND IS REPORTED AS ONE: it is L-0
    instrument signal, never a result about anything, and it is NEVER converted
    into a reduced-scope run by the Executor's own decision.
    """
    rows = []
    projected = 0.0
    sets_per_cell = R_CAL + R_IDENT + R_IDENT + R_PROD
    for bits, cell in cells.items():
        stream = Stream("calib_pilot", MASTER_SEED + STREAM_OFFSETS["calib_pilot"])
        rng = stream.generator(bits)
        arr = rng.integers(1, cell.X + 1, size=PILOT_FACTORIZATIONS_PER_CELL,
                           dtype=np.int64)
        t0 = time.time()
        res = cell.factorizer.factor(arr)
        dt = time.time() - t0
        rate = PILOT_FACTORIZATIONS_PER_CELL / dt
        cell_total = sets_per_cell * N_PER_SAMPLE_SET
        cell_seconds = cell_total / rate
        projected += cell_seconds
        rows.append({
            "field_bits": bits,
            "pilot_factorizations": PILOT_FACTORIZATIONS_PER_CELL,
            "pilot_seconds_measured": dt,
            "pilot_rate_per_second_measured": rate,
            "pilot_verified_fraction_measured":
                res["verified_count"] / res["total_count"],
            "sample_sets_requiring_factorization_at_this_cell": sets_per_cell,
            "factorizations_projected_at_this_cell": cell_total,
            "seconds_projected_at_this_cell_MODELED": cell_seconds,
        })
        deadline.check("pilot")
    projected_with_overhead = projected * PILOT_OVERHEAD_MULTIPLIER
    gate = {
        "id": "pilot_budget_gate",
        "rows": rows,
        "factorization_seconds_projected_MODELED": projected,
        "overhead_multiplier_declared_pre_datum": PILOT_OVERHEAD_MULTIPLIER,
        "total_seconds_projected_MODELED": projected_with_overhead,
        "wall_clock_budget_seconds": CALIB_WALL_CLOCK_SECONDS,
        "abort": projected_with_overhead > CALIB_WALL_CLOCK_SECONDS,
        "measured_versus_modeled":
            ("pilot_seconds_measured and pilot_rate_per_second_measured are "
             "MEASURED; every 'projected' figure is MODELED by linear "
             "extrapolation of the measured rate and is a BUDGET QUANTITY AND "
             "NEVER A DECISION VARIABLE."),
    }
    return gate


def run_calibration(out_run: str, out_results: str, deadline: Deadline) -> dict:
    """LPF-CAL-A through LPF-CAL-E.

    STRUCTURALLY BLIND TO THE REAL OBJECT: this function constructs only
    uniform integers on [1, p**2], ENC-B images of uniform (e_1, e_2), the
    product control and the two plant families. It builds no x-coordinate
    membership array, no factor base, and no S_3 specialization, by any route.
    It asserts the module tripwire is still False when it finishes.
    """
    t_start = time.time()
    dick = Dickman()
    dick_report = dick.reproduction_report()
    cells = {b: CalibrationCell(b) for b in FIELD_BITS}
    for b, c in cells.items():
        c.small_smooth_primes = primes_upto(bsm_at_u4(b)).tolist()

    _log("LPF-CAL-E: Dickman delay-equation solution reproduced against the "
         f"frozen table; worst relative discrepancy "
         f"{dick_report['worst_relative_discrepancy']:.3e}")

    _log("pilot budget gate: starting")
    gate = run_pilot(cells, dick, deadline)
    _log("pilot budget gate: projected total "
         f"{gate['total_seconds_projected_MODELED']:.0f}s (MODELED) against a "
         f"{CALIB_WALL_CLOCK_SECONDS}s budget; abort={gate['abort']}")
    if gate["abort"]:
        raise BudgetExceeded(
            "PILOT PROJECTION ABOVE BUDGET. Aborting BEFORE any bulk work. "
            "BUDGET EVENT, L-0 INSTRUMENT SIGNAL, NEVER A RESULT. The scope is "
            "NOT reduced; reducing R_CAL, the ladders, the cells or n requires "
            "a Coordinator protocol_amendment.")

    verification = {"verified_count": 0, "total_count": 0, "failures": []}

    def _account(res: dict, where: str) -> None:
        verification["verified_count"] += res["verified_count"]
        verification["total_count"] += res["total_count"]
        if res["verified_count"] != res["total_count"]:
            verification["failures"].append({"where": where, **{
                k: v for k, v in res.items()
                if k not in ("p_max", "residual")}})
            raise IntegrityFailure(
                f"FACTORIZATION VERIFICATION FAILURE at {where}. "
                "STOPPING IMMEDIATELY per the frozen stopping rule: a wrong "
                "factorization silently poisons every statistic.")

    per_cell: dict = {}
    movement_rows: list[dict] = []
    identity_report: dict = {}

    for bits in FIELD_BITS:
        cell = cells[bits]
        _log(f"cell bits={bits}: p={cell.p} X=p^2={cell.X} D={cell.D}")

        # ---------- LPF-CAL-A: 200 uniform replicates -------------------
        s_unif = Stream("calib_uniform",
                        MASTER_SEED + STREAM_OFFSETS["calib_uniform"] + bits)
        rep_stats: list[dict] = []
        rep_flat: list[dict] = []
        rep_rate_rows: list[list[dict]] = []
        plant_base_values: list[np.ndarray] = []
        plant_base_pmax: list[np.ndarray] = []
        n_one_total = 0
        for k in range(R_CAL):
            vals = cell.draw_uniform(s_unif, k)
            res = cell.factorizer.factor(vals)
            _account(res, f"LPF-CAL-A bits={bits} replicate={k}")
            n_one_total += int(np.count_nonzero(vals == 1))
            st = all_statistics(vals, res["p_max"], bits, dick)
            rep_stats.append(st)
            rep_flat.append(flatten_statistics(st))
            rep_rate_rows.append(st["rate_rows"])
            if k < R_PLANT:
                plant_base_values.append(vals)
                plant_base_pmax.append(res["p_max"])
            if (k + 1) % 25 == 0:
                _log(f"  LPF-CAL-A bits={bits}: {k + 1}/{R_CAL} replicates "
                     f"({deadline.elapsed():.0f}s elapsed)")
            deadline.check(f"LPF-CAL-A bits={bits}")

        ids = statistic_ids(bits)
        replicate_values = {sid: [rf[sid] for rf in rep_flat] for sid in ids}
        bands = {sid: band_by_frozen_rule(replicate_values[sid]) for sid in ids}
        spreads = {sid: spread(replicate_values[sid]) for sid in ids}

        # LIMB B on the uniform arm, per rung. ABS-REL-LPF-1.
        limb_b_rows = []
        for r_idx, (u_target, bsm) in enumerate(BSM_LADDER[bits]):
            r_vals = [rr[r_idx]["R_u"] for rr in rep_rate_rows]
            p_vals = [rr[r_idx]["p_hat_u"] for rr in rep_rate_rows]
            rho_u = rep_rate_rows[0][r_idx]["rho_u_computed"]
            u_rec = rep_rate_rows[0][r_idx]["u_recomputed"]
            powered = rep_rate_rows[0][r_idx]["powered_flag"]
            pooled_p_hat = float(np.mean(p_vals))
            pooled_R = pooled_p_hat / rho_u if rho_u > 0 else None
            inside = [bool(1.0 / CONSTANT_FACTOR_C <= x <= CONSTANT_FACTOR_C)
                      for x in r_vals]
            limb_b_rows.append({
                "u_target": u_target,
                "Bsm": bsm,
                "u_recomputed": u_rec,
                "LPF_rho_u_computed": rho_u,
                "LPF_powered_flag": powered,
                "expected_smooth_under_model": N_PER_SAMPLE_SET * rho_u,
                "uniform_arm_p_hat_u_mean_over_replicates": pooled_p_hat,
                "uniform_arm_p_hat_u_spread": spread(p_vals),
                "LPF_R_u_uniform_mean_over_replicates": pooled_R,
                "LPF_R_u_uniform_spread": spread([x for x in r_vals]),
                "frozen_absolute_band": [1.0 / CONSTANT_FACTOR_C,
                                         float(CONSTANT_FACTOR_C)],
                "LPF_limb_b_decidable_flag": bool(
                    pooled_R is not None
                    and 1.0 / CONSTANT_FACTOR_C <= pooled_R <= CONSTANT_FACTOR_C),
                "limb_b_decidable_flag_basis":
                    ("the mean over the 200 LPF-CAL-A replicates of the "
                     "uniform arm's R(u) at this rung, read against the FROZEN "
                     "[1/8, 8] band inherited unchanged from EXP-DS-001"),
                "replicates_with_R_u_inside_frozen_band": int(sum(inside)),
                "replicates_total": R_CAL,
            })

        # DECAY-LPF-1 on the uniform arm.
        mean_p_hat = [row["uniform_arm_p_hat_u_mean_over_replicates"]
                      for row in limb_b_rows]
        decay_monotone = all(mean_p_hat[i] > mean_p_hat[i + 1]
                             for i in range(len(mean_p_hat) - 1))

        # ---------- LPF-CAL-B: apparatus identity -----------------------
        s_iu = Stream("calib_identity_uniform",
                      MASTER_SEED + STREAM_OFFSETS["calib_identity_uniform"] + bits)
        s_is = Stream("calib_identity_synth",
                      MASTER_SEED + STREAM_OFFSETS["calib_identity_synth"] + bits)
        ident = {"uniform": [], "synth": []}
        for k in range(R_IDENT):
            for tag, drawer, strm in (("uniform", cell.draw_uniform, s_iu),
                                      ("synth", cell.draw_synth, s_is)):
                vals = drawer(strm, k)
                res = cell.factorizer.factor(vals)
                _account(res, f"LPF-CAL-B {tag} bits={bits} replicate={k}")
                st = all_statistics(vals, res["p_max"], bits, dick)
                ident[tag].append(flatten_statistics(st))
            deadline.check(f"LPF-CAL-B bits={bits}")
        _log(f"  LPF-CAL-B bits={bits}: {R_IDENT} uniform and {R_IDENT} synth "
             f"replicates done ({deadline.elapsed():.0f}s elapsed)")

        ident_counts = {}
        rate_ids = [s for s in ids if s.startswith("STAT-RATE-u@")]
        for tag in ("uniform", "synth"):
            per_stat = {sid: int(sum(1 for f in ident[tag]
                                     if rejects(f[sid], bands[sid])))
                        for sid in ids}
            # reading (i): STAT-RATE-u counted ONCE per replicate, rejecting if
            # any frozen rung rejects. reading (ii): every rung counted.
            rate_any = int(sum(1 for f in ident[tag]
                               if any(rejects(f[s], bands[s]) for s in rate_ids)))
            reading_i = (rate_any + per_stat["STAT-KS-DICK"]
                         + per_stat["STAT-TAIL-DEEP"])
            ident_counts[tag] = {
                "per_statistic_rejection_count": per_stat,
                "replicates": R_IDENT,
                "reading_i_rejection_count": reading_i,
                "reading_i_comparison_count": R_IDENT * 3,
                "reading_ii_rejection_count": int(sum(per_stat.values())),
                "reading_ii_comparison_count": R_IDENT * len(ids),
            }
        identity_report[str(bits)] = {
            "id": "LPF-CAL-B",
            "counts": ident_counts,
            "band_source": "the LPF-CAL-A bands computed by the frozen THR-LPF-1 rule",
            "band_status": BAND_STATUS,
            "comparison_count_reading_open_item": {
                "open_item_id": "OPEN-LPF049-A",
                "text": ("The contract's LPF-CAL-B note computes its exact "
                         "binomial band from '20 x 4 x 1 = 80 comparisons at "
                         "that cell'. STAT-LPF-1 has four members, but one of "
                         "them (STAT-KS2-CAL) is NON-CERTIFYING and is not "
                         "computed in the calibration, while STAT-RATE-u spans "
                         "five frozen Bsm rungs, so the number of comparisons "
                         "actually available per replicate is seven, not four. "
                         "BOTH READINGS ARE RECORDED AND NEITHER IS RESOLVED "
                         "HERE. Per ATS-LPF-1 clause 4 this is routed to "
                         "TASK-20260801-054; the cut itself is RR-LPF-1's to "
                         "freeze and this driver freezes none."),
                "reading_i_four_comparisons_per_replicate":
                    "STAT-RATE-u counted once, STAT-KS-DICK, STAT-TAIL-DEEP, "
                    "STAT-KS2-CAL - giving 80 comparisons per cell",
                "reading_ii_seven_comparisons_per_replicate":
                    "STAT-RATE-u at each of the five frozen rungs, plus "
                    "STAT-KS-DICK and STAT-TAIL-DEEP - giving 140 comparisons "
                    "per cell",
                "raw_counts_are_recorded_per_statistic_so_either_reading_is_computable":
                    True,
            },
            "declared_in_advance": (
                "OBJ-NULL-SYNTH and OBJ-NULL-UNIF are THE SAME DISTRIBUTION BY "
                "DERIVATION because ENC-B is a bijection onto [1, p**2]. "
                "Agreement here is NOT corroboration of anything and "
                "disagreement beyond the band would be an implementation "
                "defect in the encoder or sampler, never a mathematical "
                "result."),
        }

        # ---------- LPF-CAL-C: OBJ-CTRL-PRODUCT -------------------------
        s_prod = Stream("calib_product",
                        MASTER_SEED + STREAM_OFFSETS["calib_product"] + bits)
        prod_flat: list[dict] = []
        prod_rate_rows: list[list[dict]] = []
        for k in range(R_PROD):
            vals = cell.draw_product_control(s_prod, k)
            res = cell.factorizer.factor(vals)
            _account(res, f"LPF-CAL-C bits={bits} replicate={k}")
            st = all_statistics(vals, res["p_max"], bits, dick)
            prod_flat.append(flatten_statistics(st))
            prod_rate_rows.append(st["rate_rows"])
            deadline.check(f"LPF-CAL-C bits={bits}")
        _log(f"  LPF-CAL-C bits={bits}: {R_PROD} product-control replicates "
             f"done ({deadline.elapsed():.0f}s elapsed)")

        product_detect = {}
        for sid in ids:
            vals = [f[sid] for f in prod_flat]
            k_rej = int(sum(1 for v in vals if rejects(v, bands[sid])))
            product_detect[sid] = {
                "rejection_count": k_rej,
                "replicates": R_PROD,
                "rate": k_rej / R_PROD,
                "clopper_pearson_two_sided_95": clopper_pearson_two_sided(k_rej, R_PROD),
                "clopper_pearson_one_sided_lower_95":
                    clopper_pearson_lower(k_rej, R_PROD),
                "detected_under_DET_LPF_1": bool(
                    k_rej >= DET_COUNT_BAR
                    and clopper_pearson_lower(k_rej, R_PROD) >= DET_CP_LOWER_BAR),
                "mean_value": float(np.mean(vals)),
                "shift_in_null_sd": (
                    (float(np.mean(vals)) - spreads[sid]["mean"]) / spreads[sid]["sd"]
                    if spreads[sid]["sd"] > 0 else float("nan")),
            }
            movement_rows.append(_movement_row(
                "OBJ-CTRL-PRODUCT", None, bits, sid, vals, spreads[sid],
                bands[sid], R_PROD))

        # ---------- LPF-CAL-D: both plant ladders, EVERY rung -----------
        s_ps = Stream("calib_plant_smooth",
                      MASTER_SEED + STREAM_OFFSETS["calib_plant_smooth"] + bits)
        s_pr = Stream("calib_plant_rough",
                      MASTER_SEED + STREAM_OFFSETS["calib_plant_rough"] + bits)
        plant_detect = {"OBJ-PLANT-SMOOTH": {}, "OBJ-PLANT-ROUGH": {}}
        plant_construction = {"OBJ-PLANT-SMOOTH": [], "OBJ-PLANT-ROUGH": []}
        for family, ladder, strm in (
                ("OBJ-PLANT-SMOOTH", LADDER_SMOOTH, s_ps),
                ("OBJ-PLANT-ROUGH", LADDER_ROUGH, s_pr)):
            for g_i, gamma in enumerate(ladder):
                flats: list[dict] = []
                req = eff = fb = 0
                kv = {"verified_count": 0, "total_count": 0}
                for k in range(R_PLANT):
                    base_v = plant_base_values[k]
                    base_pm = plant_base_pmax[k]
                    pl = apply_plant(base_v, base_pm, gamma, family, cell,
                                     strm, g_i * 1000 + k)
                    st = all_statistics(pl["values"], pl["p_max"], bits, dick)
                    flats.append(flatten_statistics(st))
                    req += pl["replaced_requested"]
                    eff += pl["replaced_effected"]
                    fb += pl["construction_fallbacks"]
                    kv["verified_count"] += pl["known_factorization_verification"]["verified_count"]
                    kv["total_count"] += pl["known_factorization_verification"]["total_count"]
                    if kv["verified_count"] != kv["total_count"]:
                        raise IntegrityFailure(
                            f"KNOWN-FACTORIZATION VERIFICATION FAILURE in "
                            f"{family} gamma={gamma} bits={bits} replicate={k}")
                    deadline.check(f"LPF-CAL-D {family} bits={bits}")
                verification["verified_count"] += kv["verified_count"]
                verification["total_count"] += kv["total_count"]
                plant_construction[family].append({
                    "gamma": gamma, "replacements_requested": req,
                    "replacements_effected": eff,
                    "construction_fallbacks": fb,
                    "known_factorization_verified_count": kv["verified_count"],
                    "known_factorization_total_count": kv["total_count"],
                })
                for sid in ids:
                    vals = [f[sid] for f in flats]
                    k_rej = int(sum(1 for v in vals if rejects(v, bands[sid])))
                    cp_lo = clopper_pearson_lower(k_rej, R_PLANT)
                    plant_detect[family].setdefault(sid, []).append({
                        "gamma": gamma,
                        "rejection_count": k_rej,
                        "replicates": R_PLANT,
                        "rate": k_rej / R_PLANT,
                        "clopper_pearson_two_sided_95":
                            clopper_pearson_two_sided(k_rej, R_PLANT),
                        "clopper_pearson_one_sided_lower_95": cp_lo,
                        "detected_under_DET_LPF_1": bool(
                            k_rej >= DET_COUNT_BAR and cp_lo >= DET_CP_LOWER_BAR),
                    })
                    movement_rows.append(_movement_row(
                        family, gamma, bits, sid, vals, spreads[sid],
                        bands[sid], R_PLANT))
                _log(f"  LPF-CAL-D {family} bits={bits} gamma={gamma}: "
                     f"{R_PLANT} replicates done ({deadline.elapsed():.0f}s)")

        # gamma_det per family per statistic at this cell
        gamma_det_cell = {}
        for family in ("OBJ-PLANT-SMOOTH", "OBJ-PLANT-ROUGH"):
            gamma_det_cell[family] = {}
            for sid in ids:
                hit = [r["gamma"] for r in plant_detect[family][sid]
                       if r["detected_under_DET_LPF_1"]]
                gamma_det_cell[family][sid] = min(hit) if hit else "NONE_ON_LADDER"

        per_cell[str(bits)] = {
            "descriptor": cell.descriptor(),
            "LPF-CAL-A": {
                "replicates": R_CAL,
                "LPF_null_replicate_values": replicate_values,
                "LPF_null_spread": spreads,
                "band_by_frozen_rule": bands,
                "band_status": BAND_STATUS,
                "T_deep_replicate_values_for_the_freeze":
                    replicate_values["STAT-TAIL-DEEP"],
                "samples_equal_to_one_total_over_replicates": n_one_total,
            },
            "limb_b_absolute": {
                "rows": limb_b_rows,
                "ABS_REL_LPF_1_note": (
                    "THE UNIFORM ARM IS THE APPARATUS CALIBRATION AND NOT THE "
                    "COMPARISON. Its first duty is to measure how far a "
                    "KNOWN-UNIFORM sample of this exact size at this exact X "
                    "departs from the asymptotic Dickman prediction. A false "
                    "LPF_limb_b_decidable_flag is a MEASURED FACT ABOUT THE "
                    "APPARATUS AND THE REFERENCE, never a result about the "
                    "Semaev map in either direction, and it SATISFIES "
                    "SUCC-LPF-1."),
            },
            "LPF_decay_monotone_flag_uniform_arm": bool(decay_monotone),
            "LPF_decay_monotone_values": mean_p_hat,
            "LPF-CAL-C_product_control": {
                "LPF_product_control_detected": {
                    sid: product_detect[sid]["detected_under_DET_LPF_1"]
                    for sid in ids},
                "detail": product_detect,
            },
            "LPF-CAL-D_detection": {
                "LPF_detect_rate_smooth": plant_detect["OBJ-PLANT-SMOOTH"],
                "LPF_detect_rate_rough": plant_detect["OBJ-PLANT-ROUGH"],
                "LPF_gamma_det": gamma_det_cell,
                "plant_construction_accounting": plant_construction,
            },
        }
        _log(f"cell bits={bits} complete at {deadline.elapsed():.0f}s")

    # gamma_det across BOTH cells, per family per statistic.
    gamma_det_both = {}
    for family in ("OBJ-PLANT-SMOOTH", "OBJ-PLANT-ROUGH"):
        gamma_det_both[family] = {}
        for sid in statistic_ids(FIELD_BITS[0]):
            hits = []
            for gi, gamma in enumerate(LADDER_SMOOTH if family == "OBJ-PLANT-SMOOTH"
                                       else LADDER_ROUGH):
                ok = all(
                    per_cell[str(b)]["LPF-CAL-D_detection"][
                        "LPF_detect_rate_smooth" if family == "OBJ-PLANT-SMOOTH"
                        else "LPF_detect_rate_rough"][sid][gi][
                        "detected_under_DET_LPF_1"]
                    for b in FIELD_BITS)
                if ok:
                    hits.append(gamma)
            gamma_det_both[family][sid] = min(hits) if hits else "NONE_ON_LADDER"

    if _REAL_OBJECT_TOUCHED:
        raise IntegrityFailure(
            "ATS-LPF-1 clause 5 TRIPWIRE TRUE IN THE CALIBRATION. The run is "
            "INVALID and the whole batch is a non-execution.")

    frac = (verification["verified_count"] / verification["total_count"]
            if verification["total_count"] else 0.0)

    return {
        "stage": "calibration",
        "run_id": "RUN-LPF-001-calib",
        "dickman_reference_reproduction": dick_report,
        "pilot_budget_gate": gate,
        "per_cell": per_cell,
        "identity_report": identity_report,
        "movement_rows": movement_rows,
        "LPF_gamma_det_both_cells": gamma_det_both,
        "gamma_star": GAMMA_STAR,
        "gamma_star_caveat": (
            "gamma counts REPLACED SAMPLES OF A SMOOTHNESS PERTURBATION and "
            "EV-EQD-001's delta counted RE-RANDOMIZED e_1 COORDINATES of a "
            "marginal-moving plant, so any ratio between them is a SCALE "
            "COMPARISON AND NOT A LIKE-FOR-LIKE ONE (RTB-040-3)."),
        "LPF_factorization_verified_count": verification["verified_count"],
        "LPF_factorization_total_count": verification["total_count"],
        "LPF_factorization_verified_fraction": frac,
        "LPF_factorization_verification_failures": verification["failures"],
        "LPF_real_object_touched": bool(_REAL_OBJECT_TOUCHED),
        "LPF_degenerate_count": None,
        "LPF_degenerate_count_note": (
            "NOT APPLICABLE TO THE CALIBRATION. The degenerate c_2 == 0 count "
            "is a property of the Semaev specialization, which the calibration "
            "does not touch."),
        "LPF_certificate_kind": "none",
        "LPF_certificate_kind_reason": (
            "No discrete logarithm is computed and no relation is claimed, so "
            "there is nothing to certify in the solve sense. The 100 percent "
            "factorization verification is this experiment's certificate "
            "analogue (certificate_policy)."),
        "LPF_budget_event": [],
        "wall_seconds": time.time() - t_start,
        "interpretation": "NONE",
    }


def _movement_row(family: str, gamma, bits: int, sid: str, values: list,
                  null_spread: dict, band: dict, replicates: int) -> dict:
    """PERTURB-MOVE-1. ONE ROW PER FAMILY, RUNG, CELL AND STATISTIC, carrying
    the measured shift in units of the MEASURED NULL STANDARD DEVIATION.

    A ROW IS MANDATORY FOR EVERY RUNG OF BOTH LADDERS. A rung with no recorded
    movement is UNCERTIFIED by RR-LPF-1; a family whose top rung shows no
    movement is STRUCK from the certified list by the reading rule rather than
    reported as low power. THIS DRIVER STRIKES NOTHING AND CERTIFIES NOTHING.
    """
    v = np.asarray([float(x) for x in values], dtype=np.float64)
    mean = float(np.mean(v))
    sd = null_spread["sd"]
    shift = (mean - null_spread["mean"]) / sd if sd > 0 else float("nan")
    outside_null_range = bool(mean < null_spread["min"] or mean > null_spread["max"])
    return {
        "family": family,
        "gamma_rung": gamma,
        "field_bits": bits,
        "statistic_id": sid,
        "replicates": replicates,
        "plant_mean": mean,
        "plant_sd": float(np.std(v, ddof=1)) if v.size > 1 else 0.0,
        "plant_min": float(np.min(v)),
        "plant_max": float(np.max(v)),
        "null_mean": null_spread["mean"],
        "null_sd": sd,
        "null_min": null_spread["min"],
        "null_max": null_spread["max"],
        "LPF_movement_shift_in_null_sd": shift,
        "LPF_movement_beyond_noise_flag": bool(
            (not math.isnan(shift)) and abs(shift) >= 1.0),
        "movement_flag_reading": (
            "|shift| >= 1.0, i.e. the measured shift exceeds one MEASURED NULL "
            "STANDARD DEVIATION, which is the unit the metric definition "
            "states. THE ALTERNATIVE READING - the plant mean outside the "
            "[min, max] range of the 200 measured null replicates - is "
            "recorded separately as an AUXILIARY RECORD and is NOT a decision "
            "variable, NOT a cut, and NOT frozen here. Both readings are "
            "routed to TASK-20260801-054 under ATS-LPF-1 clause 4."),
        "movement_beyond_null_range_auxiliary_record": outside_null_range,
        "band_lower": band["lower"],
        "band_upper": band["upper"],
        "band_status": BAND_STATUS,
    }


# ==========================================================================
# 11. THE MEASUREMENT ARM. RUN-LPF-001-measure.
#     AUTHORED COMPLETE AT TASK-20260801-049 AND NOT EXECUTED THERE.
#     It refuses to start without BOTH an APPROVED approval receipt and a
#     frozen reading rule; there is no third way in.
# ==========================================================================
READING_RULE_SCHEMA_NOTE = """
run_measurement reads experiments/EXP-LPF-001/reading_rule.yaml, frozen by
TASK-20260801-052 and reviewed at TASK-20260801-054. THE SCHEMA IT EXPECTS,
declared here at authoring time so the freeze can match it:

reading_rule:
  id: RR-LPF-1
  frozen: true
  certifying_set_retained: [STAT-RATE-u, STAT-KS-DICK, STAT-TAIL-DEEP]
  bands:
    '16':
      'STAT-RATE-u@u_target=2': {lower: <float>, upper: <float>}
      ... one entry per statistic id in statistic_ids(bits) ...
    '20':
      ...
  null_spread:
    '16': {'<statistic id>': {mean: <f>, sd: <f>, min: <f>, max: <f>, median: <f>}}
    '20': {...}
  identity_binomial_cut: <int>          # LPF-CAL-B frozen integer cut

If a key is missing the measurement arm REFUSES rather than substituting a
default. NOTHING in this driver may be edited to supply these numbers.
"""


def _load_reading_rule(path: str) -> dict:
    import yaml
    if not path or not os.path.exists(path):
        raise IntegrityFailure(
            "MEASUREMENT REFUSED: no frozen reading rule at "
            f"{path!r}. THERE IS NO READING RULE YET UNTIL TASK-20260801-052 "
            "freezes one." + READING_RULE_SCHEMA_NOTE)
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    rr = (doc or {}).get("reading_rule")
    if not isinstance(rr, dict):
        raise IntegrityFailure(
            "MEASUREMENT REFUSED: reading rule file has no `reading_rule` "
            "mapping." + READING_RULE_SCHEMA_NOTE)
    for key in ("bands", "null_spread", "certifying_set_retained"):
        if key not in rr:
            raise IntegrityFailure(
                f"MEASUREMENT REFUSED: reading rule lacks `{key}`."
                + READING_RULE_SCHEMA_NOTE)
    if rr.get("frozen") is not True:
        raise IntegrityFailure(
            "MEASUREMENT REFUSED: reading rule is not marked frozen."
            + READING_RULE_SCHEMA_NOTE)
    return rr


def _check_approval(path: str) -> dict:
    if not path or not os.path.exists(path):
        raise IntegrityFailure(
            "MEASUREMENT REFUSED: no approval receipt supplied. "
            "RUN-LPF-001-measure is authorized ONLY by APPROVAL_DETERMINATION "
            "APPROVED in the TASK-20260801-055 snapshot receipt, and a "
            "measurement run executed without it is INVALID and is not "
            "evidence (invalidation_rules).")
    with open(path) as fh:
        rec = json.load(fh)
    det = rec.get("APPROVAL_DETERMINATION")
    if det != "APPROVED":
        raise IntegrityFailure(
            f"MEASUREMENT REFUSED: APPROVAL_DETERMINATION is {det!r}, not "
            "'APPROVED'.")
    return {"approval_receipt_path": path,
            "APPROVAL_DETERMINATION": det,
            "approval_receipt_sha256": sha256_file(path),
            "approval_task_id": rec.get("task_id")}


def run_measurement(out_run: str, out_results: str, reading_rule_path: str,
                    approval_receipt_path: str, deadline: Deadline) -> dict:
    """OBJ-REAL at both cells, plus ONE fresh OBJ-NULL-UNIF arm per cell for
    STAT-KS2-CAL only. THE QUANTITY HEUR-DS-1 IS ABOUT.

    THIS ENTRY POINT IS NOT INVOKED BY TASK-20260801-049. It is authored here
    complete so that the file hash bound at TASK-20260801-050 is the file the
    measurement stage executes (ATS-LPF-1 clause 3).
    """
    approval = _check_approval(approval_receipt_path)
    rr = _load_reading_rule(reading_rule_path)
    t_start = time.time()
    dick = Dickman()
    dick_report = dick.reproduction_report()

    per_cell: dict = {}
    verification = {"verified_count": 0, "total_count": 0, "failures": []}
    deviations: list[dict] = []

    for bits in FIELD_BITS:
        fb = deterministic_factor_base(bits)
        p, a, b = fb["p"], fb["a"], fb["b"]
        if fb["factor_base_sha256"] != EQD_FACTOR_BASE_SHA256[bits]:
            raise IntegrityFailure(
                "L-0: factor_base_sha256 mismatch against the EXP-EQD-001 "
                f"archived value at bits={bits}: "
                f"{fb['factor_base_sha256']} != {EQD_FACTOR_BASE_SHA256[bits]}")
        iu, ju = upper_triangle_indices(BFB)
        if iu.size != N_PER_SAMPLE_SET:
            raise IntegrityFailure(
                f"L-0: enumeration has {iu.size} half-tuples, expected "
                f"{N_PER_SAMPLE_SET}")
        e1, e2, degenerate = int1_fibre_invariants(
            fb["xs"][iu], fb["xs"][ju], p, a, b)
        values = encode_enc_b(e1, e2, p)
        X = p * p
        if int(values.min()) < 1 or int(values.max()) > X:
            raise IntegrityFailure("L-0: ENC-B image outside [1, p**2]")
        fac = Factorizer(X)
        res = fac.factor(values)
        verification["verified_count"] += res["verified_count"]
        verification["total_count"] += res["total_count"]
        if res["verified_count"] != res["total_count"]:
            raise IntegrityFailure(
                f"L-0: FACTORIZATION VERIFICATION FAILURE on OBJ-REAL at "
                f"bits={bits}. Stopping immediately.")
        st = all_statistics(values, res["p_max"], bits, dick)
        flat = flatten_statistics(st)
        deadline.check(f"measurement OBJ-REAL bits={bits}")

        # one fresh OBJ-NULL-UNIF arm, for STAT-KS2-CAL ONLY
        s_ks2 = Stream("measure_uniform_ks2",
                       MASTER_SEED + STREAM_OFFSETS["measure_uniform_ks2"] + bits)
        rng = s_ks2.generator(0)
        u_vals = rng.integers(1, X + 1, size=N_PER_SAMPLE_SET, dtype=np.int64)
        u_res = fac.factor(u_vals)
        verification["verified_count"] += u_res["verified_count"]
        verification["total_count"] += u_res["total_count"]
        if u_res["verified_count"] != u_res["total_count"]:
            raise IntegrityFailure(
                f"L-0: FACTORIZATION VERIFICATION FAILURE on the fresh uniform "
                f"arm at bits={bits}. Stopping immediately.")
        u_st = all_statistics(u_vals, u_res["p_max"], bits, dick)
        ks2 = stat_ks2(z_values(values, res["p_max"]),
                       z_values(u_vals, u_res["p_max"]))

        bands = rr["bands"][str(bits)]
        spreads = rr["null_spread"][str(bits)]
        ids = statistic_ids(bits)
        reject = {}
        position = {}
        for sid in ids:
            if sid not in bands:
                raise IntegrityFailure(
                    f"MEASUREMENT REFUSED: frozen reading rule has no band for "
                    f"{sid} at bits={bits}." + READING_RULE_SCHEMA_NOTE)
            bd = {"lower": float(bands[sid]["lower"]),
                  "upper": float(bands[sid]["upper"])}
            val = flat[sid]
            reject[sid] = rejects(val, bd)
            position[sid] = band_position(val, bd, float(spreads[sid]["sd"]))
            if reject[sid]:
                deviations.append({
                    "field_bits": bits, "statistic_id": sid,
                    "value": val, "band": bd,
                    "direction": "BELOW_BAND" if val < bd["lower"] else "ABOVE_BAND",
                })

        # LIMB B, real arm and uniform arm side by side, EVERY rung.
        limb_b_rows = []
        for r_real, r_unif in zip(st["rate_rows"], u_st["rate_rows"]):
            dec = bool(1.0 / CONSTANT_FACTOR_C <= r_unif["R_u"] <= CONSTANT_FACTOR_C)
            limb_b_rows.append({
                "u_target": r_real["u_target"], "Bsm": r_real["Bsm"],
                "u_recomputed": r_real["u_recomputed"],
                "LPF_rho_u_computed": r_real["rho_u_computed"],
                "LPF_powered_flag": r_real["powered_flag"],
                "LPF_p_hat_u_real": r_real["p_hat_u"],
                "LPF_R_u_real": r_real["R_u"],
                "uniform_arm_p_hat_u": r_unif["p_hat_u"],
                "LPF_R_u_uniform": r_unif["R_u"],
                "frozen_absolute_band": [1.0 / CONSTANT_FACTOR_C,
                                         float(CONSTANT_FACTOR_C)],
                "LPF_limb_b_decidable_flag": dec,
                "real_R_u_inside_frozen_band": bool(
                    1.0 / CONSTANT_FACTOR_C <= r_real["R_u"] <= CONSTANT_FACTOR_C),
            })
        mean_p_hat = [r["LPF_p_hat_u_real"] for r in limb_b_rows]
        decay = all(mean_p_hat[i] > mean_p_hat[i + 1]
                    for i in range(len(mean_p_hat) - 1))

        per_cell[str(bits)] = {
            "p": p, "X": X, "D": D_BY_BITS[bits],
            "LPF_factor_base_sha256": fb["factor_base_sha256"],
            "EQD_archived_factor_base_sha256": EQD_FACTOR_BASE_SHA256[bits],
            "LPF_pairs_per_arm": int(values.size),
            "LPF_degenerate_count": degenerate,
            "LPF_stat_values_real": flat,
            "LPF_stat_values_uniform": flatten_statistics(u_st),
            "LPF_ks_dick": st["ks_dick"],
            "LPF_tail_deep": st["t_deep"],
            "LPF_ks2_cal": ks2,
            "LPF_ks2_cal_note": (
                "NON-CERTIFYING FOR BOTH LIMBS by CERT-LPF-1. Recorded with no "
                "threshold and no reject boolean; no branch reads it."),
            "LPF_reject_per_statistic": reject,
            "LPF_band_position": position,
            "limb_b_absolute": {"rows": limb_b_rows},
            "LPF_decay_monotone_flag": bool(decay),
        }
        deadline.check(f"measurement cell bits={bits}")

    frac = (verification["verified_count"] / verification["total_count"]
            if verification["total_count"] else 0.0)
    return {
        "stage": "measurement",
        "run_id": "RUN-LPF-001-measure",
        "approval": approval,
        "reading_rule_path": reading_rule_path,
        "reading_rule_sha256": sha256_file(reading_rule_path),
        "dickman_reference_reproduction": dick_report,
        "per_cell": per_cell,
        "deviations": deviations,
        "LPF_factorization_verified_count": verification["verified_count"],
        "LPF_factorization_total_count": verification["total_count"],
        "LPF_factorization_verified_fraction": frac,
        "LPF_real_object_touched": bool(_REAL_OBJECT_TOUCHED),
        "LPF_certificate_kind": "none",
        "wall_seconds": time.time() - t_start,
        "interpretation": "NONE",
    }


# ==========================================================================
# 12. Run packaging.
# ==========================================================================
def git_info() -> dict:
    def run(args):
        try:
            return subprocess.run(args, capture_output=True, text=True,
                                  check=True).stdout.strip()
        except Exception as exc:                       # noqa: BLE001
            return f"<unavailable: {exc}>"
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "status_porcelain": run(["git", "status", "--porcelain"]),
    }


def environment_record(mode: str) -> dict:
    deps = {"numpy": np.__version__}
    try:
        import sympy as _s
        deps["sympy"] = _s.__version__
    except Exception:                                  # noqa: BLE001
        deps["sympy"] = "<absent>"
    try:
        import yaml as _y
        deps["pyyaml"] = _y.__version__
    except Exception:                                  # noqa: BLE001
        deps["pyyaml"] = "<absent>"
    return {
        "experiment_id": EXPERIMENT_ID,
        "mode": mode,
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "dependencies": deps,
        "factorization_primitive": {
            "module": ("experiments/EXP-LPF-001/implementation/lpf001_driver.py "
                       "(in-repository, no external factorization library)"),
            "version": "carried in this driver; identified by driver_sha256",
            "algorithm": ("complete vectorised trial division to isqrt(X) over "
                          "a sieved and independently Miller-Rabin verified "
                          "prime table, with per-sample Miller-Rabin "
                          "verification of the residual factor and an "
                          "elementwise product assertion"),
            "deterministic_miller_rabin_bases": list(_MR_BASES),
            "gmpy2_present": False,
        },
        "driver_sha256": sha256_file(os.path.abspath(__file__)),
        "spec_sha256": (sha256_file(SPEC_PATH) if os.path.exists(SPEC_PATH)
                        else "<spec not found from cwd>"),
        "spec_sha256_at_freeze": SPEC_SHA256_AT_FREEZE,
        "git": git_info(),
    }


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=False, default=_json_default)
        fh.write("\n")


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EXP-LPF-001 driver")
    ap.add_argument("--mode", required=True, choices=("calib", "measure"))
    ap.add_argument("--out-run", required=True)
    ap.add_argument("--out-results", required=True)
    ap.add_argument("--authorization-receipt", default=None,
                    help="TASK-20260801-048 snapshot receipt (calib mode)")
    ap.add_argument("--reading-rule", default=None)
    ap.add_argument("--approval-receipt", default=None)
    args = ap.parse_args(argv)

    if os.path.exists(SPEC_PATH):
        got = sha256_file(SPEC_PATH)
        if got != SPEC_SHA256_AT_FREEZE:
            print(f"REFUSING: spec sha256 {got} != frozen "
                  f"{SPEC_SHA256_AT_FREEZE}", file=sys.stderr)
            return 2

    os.makedirs(args.out_run, exist_ok=True)
    os.makedirs(args.out_results, exist_ok=True)

    if args.mode == "calib":
        # CALIBRATION_AUTHORIZATION gate.
        if not args.authorization_receipt or not os.path.exists(
                args.authorization_receipt):
            print("REFUSING: no TASK-20260801-048 authorization receipt.",
                  file=sys.stderr)
            return 2
        with open(args.authorization_receipt) as fh:
            rec = json.load(fh)
        if rec.get("CALIBRATION_AUTHORIZATION") != "AUTHORIZED":
            print("REFUSING: CALIBRATION_AUTHORIZATION is "
                  f"{rec.get('CALIBRATION_AUTHORIZATION')!r}, not 'AUTHORIZED'.",
                  file=sys.stderr)
            return 2
        deadline = Deadline(CALIB_WALL_CLOCK_SECONDS)
        env = environment_record("calib")
        env["calibration_authorization"] = {
            "receipt_path": args.authorization_receipt,
            "receipt_sha256": sha256_file(args.authorization_receipt),
            "CALIBRATION_AUTHORIZATION": rec.get("CALIBRATION_AUTHORIZATION"),
            "scope": rec.get("calibration_authorization_scope"),
        }
        write_json(os.path.join(args.out_run, "environment.json"), env)
        try:
            raw = run_calibration(args.out_run, args.out_results, deadline)
            status = "completed_valid"
            failure_class = None
        except BudgetExceeded as exc:
            raw = {"stage": "calibration", "run_id": "RUN-LPF-001-calib",
                   "LPF_budget_event": deadline.events + [{"message": str(exc)}],
                   "aborted": True, "interpretation": "NONE"}
            status, failure_class = "failed_infrastructure", "resource_exhaustion"
            print(str(exc), file=sys.stderr)
        except IntegrityFailure as exc:
            raw = {"stage": "calibration", "run_id": "RUN-LPF-001-calib",
                   "integrity_failure": str(exc), "aborted": True,
                   "interpretation": "NONE"}
            status, failure_class = "invalid", "invalid_measurement"
            print(str(exc), file=sys.stderr)

        raw["status"] = status
        raw["failure_class"] = failure_class
        raw["peak_rss_gb"] = _peak_rss_gb()
        raw["environment_sha256_of_record"] = sha256_text(json.dumps(env, sort_keys=True))
        write_json(os.path.join(args.out_run, "raw-result.json"), raw)

        if status == "completed_valid":
            write_json(os.path.join(args.out_results,
                                    "dickman_reference_reproduction.json"),
                       raw["dickman_reference_reproduction"])
            write_json(os.path.join(args.out_results,
                                    "null_replicate_statistics.json"),
                       {"id": "LPF-CAL-A",
                        "experiment_id": EXPERIMENT_ID,
                        "run_id": "RUN-LPF-001-calib",
                        "non_evidential": (
                            "CAL-LPF-1: the calibration is NON-EVIDENTIAL in "
                            "either direction and no calibration number may be "
                            "cited as evidence about any hypothesis."),
                        "band_status": BAND_STATUS,
                        "per_cell": {b: {
                            "descriptor": raw["per_cell"][b]["descriptor"],
                            "LPF-CAL-A": raw["per_cell"][b]["LPF-CAL-A"],
                            "limb_b_absolute": raw["per_cell"][b]["limb_b_absolute"],
                            "LPF_decay_monotone_flag_uniform_arm":
                                raw["per_cell"][b]["LPF_decay_monotone_flag_uniform_arm"],
                            "LPF_decay_monotone_values":
                                raw["per_cell"][b]["LPF_decay_monotone_values"],
                        } for b in raw["per_cell"]},
                        "LPF_factorization_verified_fraction":
                            raw["LPF_factorization_verified_fraction"],
                        "LPF_factorization_verified_count":
                            raw["LPF_factorization_verified_count"],
                        "LPF_factorization_total_count":
                            raw["LPF_factorization_total_count"],
                        "interpretation": "NONE"})
            write_json(os.path.join(args.out_results,
                                    "perturbation_movement_report.json"),
                       {"id": "PERTURB-MOVE-1",
                        "experiment_id": EXPERIMENT_ID,
                        "run_id": "RUN-LPF-001-calib",
                        "statement": (
                            "EVERY PLANT, PERTURBATION OR CONTROL OBJECT THIS "
                            "CONTRACT USES TO CERTIFY POWER MUST BE "
                            "DEMONSTRATED TO MOVE THE STATISTIC IT IS MEANT TO "
                            "MOVE, BY MEASUREMENT AT EVERY RUNG IT CERTIFIES, "
                            "NOT AT ENDPOINTS ONLY."),
                        "where_each_family_moves_mass": {
                            "OBJ-PLANT-SMOOTH": (
                                "replaces a gamma fraction by products of "
                                "primes at most Bsm(u=4), whose largest prime "
                                "factor is at most Bsm(u=4) by construction, "
                                "moving mass into the HIGH-Z (smooth) end of "
                                "the Z-distribution"),
                            "OBJ-PLANT-ROUGH": (
                                "replaces a gamma fraction by q*r with q a "
                                "prime above sqrt(X), so P_max = q > sqrt(N) "
                                "and Z < 2, moving mass into the LOW-Z (rough) "
                                "end of the Z-distribution"),
                            "OBJ-CTRL-PRODUCT": (
                                "a product of two integers each below p, "
                                "provably and substantially smoother than a "
                                "uniform integer below p**2; a single object "
                                "and not a ladder"),
                        },
                        "rows": raw["movement_rows"],
                        "row_count": len(raw["movement_rows"]),
                        "LPF_gamma_det_both_cells": raw["LPF_gamma_det_both_cells"],
                        "gamma_star": GAMMA_STAR,
                        "gamma_star_caveat": raw["gamma_star_caveat"],
                        "detection_detail_per_cell": {
                            b: raw["per_cell"][b]["LPF-CAL-D_detection"]
                            for b in raw["per_cell"]},
                        "band_status": BAND_STATUS,
                        "interpretation": "NONE"})
            write_json(os.path.join(args.out_results,
                                    "apparatus_identity_report.json"),
                       {"id": "LPF-CAL-B",
                        "experiment_id": EXPERIMENT_ID,
                        "run_id": "RUN-LPF-001-calib",
                        "per_cell": raw["identity_report"],
                        "product_control_LPF_CAL_C": {
                            b: raw["per_cell"][b]["LPF-CAL-C_product_control"]
                            for b in raw["per_cell"]},
                        "no_cut_is_frozen_here": (
                            "The exact binomial cut for this leg is RR-LPF-1's "
                            "to freeze at TASK-20260801-052. This report "
                            "records COUNTS ONLY."),
                        "band_status": BAND_STATUS,
                        "interpretation": "NONE"})
        _log(f"calibration finished with status {status}")
        return 0 if status == "completed_valid" else 1

    # ---- measurement -----------------------------------------------------
    deadline = Deadline(MEASURE_WALL_CLOCK_SECONDS)
    env = environment_record("measure")
    write_json(os.path.join(args.out_run, "environment.json"), env)
    try:
        raw = run_measurement(args.out_run, args.out_results,
                              args.reading_rule, args.approval_receipt,
                              deadline)
        status, failure_class = "completed_valid", None
    except BudgetExceeded as exc:
        raw = {"stage": "measurement", "run_id": "RUN-LPF-001-measure",
               "LPF_budget_event": deadline.events + [{"message": str(exc)}],
               "aborted": True, "interpretation": "NONE"}
        status, failure_class = "failed_infrastructure", "resource_exhaustion"
        print(str(exc), file=sys.stderr)
    except IntegrityFailure as exc:
        raw = {"stage": "measurement", "run_id": "RUN-LPF-001-measure",
               "integrity_failure": str(exc), "aborted": True,
               "interpretation": "NONE"}
        status, failure_class = "invalid", "invalid_measurement"
        print(str(exc), file=sys.stderr)
    raw["status"] = status
    raw["failure_class"] = failure_class
    raw["peak_rss_gb"] = _peak_rss_gb()
    write_json(os.path.join(args.out_run, "raw-result.json"), raw)
    if status == "completed_valid":
        write_json(os.path.join(args.out_results, "LPF_report.json"), raw)
        write_json(os.path.join(args.out_results, "absolute_comparison.json"),
                   {"limb": "B",
                    "per_cell": {b: raw["per_cell"][b]["limb_b_absolute"]
                                 for b in raw["per_cell"]},
                    "frozen_absolute_band": [1.0 / CONSTANT_FACTOR_C,
                                             float(CONSTANT_FACTOR_C)],
                    "interpretation": "NONE"})
        write_json(os.path.join(args.out_results,
                                "relative_band_comparison.json"),
                   {"limb": "A",
                    "per_cell": {b: {
                        "LPF_reject_per_statistic":
                            raw["per_cell"][b]["LPF_reject_per_statistic"],
                        "LPF_band_position":
                            raw["per_cell"][b]["LPF_band_position"],
                        "LPF_stat_values_real":
                            raw["per_cell"][b]["LPF_stat_values_real"],
                        "LPF_ks2_cal": raw["per_cell"][b]["LPF_ks2_cal"],
                    } for b in raw["per_cell"]},
                    "interpretation": "NONE"})
        write_json(os.path.join(args.out_results, "deviation_certificate.json"),
                   _deviation_certificate(raw))
        write_json(os.path.join(args.out_results,
                                "factorization_verification.json"),
                   {"LPF_factorization_verified_fraction":
                        raw["LPF_factorization_verified_fraction"],
                    "LPF_factorization_verified_count":
                        raw["LPF_factorization_verified_count"],
                    "LPF_factorization_total_count":
                        raw["LPF_factorization_total_count"],
                    "pre_registered_point_prediction": 1.0,
                    "interpretation": "NONE"})
    _log(f"measurement finished with status {status}")
    return 0 if status == "completed_valid" else 1


def _deviation_certificate(raw: dict) -> dict:
    """WRITTEN UNCONDITIONALLY. If no deviation is found it records that with
    the measured margins; if one is found it lists the deviating rungs, the
    statistic values, the archived bands, THE DIRECTION of the departure, and
    an INDEPENDENT re-verification of the largest prime factor of a stated
    random subsample by a SECOND factorization path."""
    devs = raw.get("deviations", [])
    return {
        "experiment_id": EXPERIMENT_ID,
        "run_id": "RUN-LPF-001-measure",
        "claim_tier": "toy",
        "proof_status": ("counterexample_certificate" if devs
                         else "no_deviation_found"),
        "deviating_rows": devs,
        "band_positions": {b: raw["per_cell"][b]["LPF_band_position"]
                           for b in raw.get("per_cell", {})},
        "independent_reverification":
            _independent_pmax_recheck(raw),
        "direction_statement": (
            "SMOOTHER THAN REFERENCE AND ROUGHER THAN REFERENCE HAVE OPPOSITE "
            "CONSEQUENCES FOR AN INDEX CALCULUS AND ARE NEVER REPORTED AS ONE "
            "OUTCOME. Each row above carries its own direction."),
        "interpretation": "NONE",
    }


def _independent_pmax_recheck(raw: dict) -> dict:
    """A SECOND factorization path over a stated random subsample: sympy's
    factorint, which shares no code with the trial-division factorizer above."""
    try:
        import sympy
    except Exception as exc:                           # noqa: BLE001
        return {"performed": False, "reason": f"sympy unavailable: {exc}"}
    out = {}
    for bits in FIELD_BITS:
        fb = deterministic_factor_base(bits)
        p, a, b = fb["p"], fb["a"], fb["b"]
        iu, ju = upper_triangle_indices(BFB)
        e1, e2, _deg = int1_fibre_invariants(fb["xs"][iu], fb["xs"][ju], p, a, b)
        values = encode_enc_b(e1, e2, p)
        fac = Factorizer(p * p)
        res = fac.factor(values)
        rng = np.random.default_rng(
            MASTER_SEED + STREAM_OFFSETS["measure_uniform_ks2"] + bits)
        idx = rng.choice(values.size, size=1000, replace=False)
        agree = 0
        for i in idx.tolist():
            n = int(values[i])
            want = int(res["p_max"][i])
            got = 1 if n == 1 else max(sympy.factorint(n).keys())
            agree += int(got == want)
        out[str(bits)] = {"subsample_size": 1000, "agreeing": agree,
                          "second_path": "sympy.factorint",
                          "subsample_seed": int(
                              MASTER_SEED + STREAM_OFFSETS["measure_uniform_ks2"] + bits)}
    return {"performed": True, "per_cell": out}


def _peak_rss_gb() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes; Linux reports kilobytes.
    scale = 1.0 if sys.platform == "darwin" else 1024.0
    return ru * scale / (1024.0 ** 3)


if __name__ == "__main__":
    sys.exit(main())
