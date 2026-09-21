#!/usr/bin/env python3
"""EXP-DEP-001 driver: the dependence-only plant families at BIT-IDENTICAL
marginals, their calibration arm RUN-DEP-001-calib, and the (dormant here)
measurement arm RUN-DEP-001-measure.

BINDING CONTRACT: experiments/EXP-DEP-001/specification.yaml, hash-bound at
commit 36141a951a09bb340a19dc68406f98628294ad71 (sha256
e4a977f2117b190fef2baa95e2fbb7791d601b5a42c783b82d835222d9c9e20d).

CTRL-DEP-EQDHASH. The fibre-invariant map INT-2 and the four statistics of
STAT-DEP-1 are NOT re-implemented here. They are imported READ-ONLY from
experiments/EXP-EQD-001/implementation/eqd001_driver.py, whose sha256 must
equal bdb2601b195f314a4430fa80fcf8ab15ec0b605335a8386a93c2b9b3c7d7b02f, and
the archived null-replicate array
experiments/EXP-EQD-001/results/calib/null_replicate_statistics.json must
have sha256 284ca32143b386beefe80bae5ae05419a2b2f9286c96e3450e09c33e0fdca019.
A mismatch ABORTS before any arm is computed and is an integrity failure,
never a datum. NO FILE UNDER experiments/EXP-EQD-001/ IS WRITTEN, EDITED,
RENAMED, MOVED, APPENDED TO OR STAGED BY THIS FILE.

ATS-DEP-1.5: THIS FILE IS AUTHORED COMPLETE AT TASK-20260801-035, INCLUDING
THE MEASUREMENT ENTRY POINT THAT IS NOT EXECUTED THERE. Its sha256 is bound
by the TASK-20260801-036 snapshot and TASK-20260801-042 must execute the
IDENTICAL file with no edit. Every number the measurement arm needs that does
not exist yet is read at run time -- the primary thresholds from the ARCHIVED
EXP-EQD-001 artifact named above, and the frozen reading rule from
experiments/EXP-DEP-001/reading_rule.yaml, which TASK-20260801-038 freezes.
NOTHING in this file may be edited to supply them.

ATS-DEP-1.3: THE CALIBRATION ARM NEVER SEES THE REAL DATA, STRUCTURALLY AND
NOT BY INSTRUCTION. `dep_deterministic_factor_base()` is the ONLY function in
this file that reaches the frozen deterministic factor base; it flips the
module-level tripwire `_REAL_OBJECT_TOUCHED`, it is called by
`run_duplicate_decomposition()` and by nothing else, and that function is
reachable only from `--mode measure`. `main()` asserts the tripwire -- and the
imported EXP-EQD-001 module's own `_REAL_DATA_TOUCHED` tripwire -- are both
still False when a calibration run finishes, and records that fact as
`calibration_saw_real_object`.

DESIGN-TRAP-1. Permuting e_2 WITHIN strata that coincide with the chi-square
bins leaves the K x K contingency table EXACTLY invariant, so detection would
return the nominal rate at every rung BY CONSTRUCTION and the power
certificate would measure nothing. This driver therefore makes the
Gaussian-copula reordering PRIMARY (it moves mass across e_1 bins), keeps the
two-stratum block family COARSER than the grid, and computes DIAG-DEP-RHO --
the measured Spearman correlation on source and plant, and the K = 16 joint
total variation distance -- as a SEPARATE check that the plant actually moved
the joint table.

CTRL-DEP-MARG. Every planted arm produced anywhere in this file, at every rung
of every ladder, in both stages, is checked for BIT-IDENTICAL marginals
against its source arm: four sha256 digests over the canonical little-endian
8-byte encoding of the sorted arrays, plus the K = 16 and K = 64
one-dimensional marginal histograms of e_1 and of e_2 on both arms, compared
count by count. A MISMATCH ABORTS THE ARM, IS RECORDED WITH ITS RUNG AND
REPLICATE INDEX, AND IS INSTRUMENT FAILURE -- NEVER A RESULT.

This driver freezes NO threshold, applies NO reading rule, selects NO branch
and states NO disposition. It emits measured numbers.

What this driver does NOT contain, by contract: no factorization, no largest
prime factor, no smoothness indicator, no Dickman evaluation, no u ladder, no
search arm, no relation harvest, no charged unit, no cost identity, no R, and
no timing decision variable. `wall_seconds` is recorded for budget accounting
only.

Usage
-----
  python3 experiments/EXP-DEP-001/implementation/dep001_driver.py \
      --mode calib --out-run <dir> --out-results <dir>

  python3 experiments/EXP-DEP-001/implementation/dep001_driver.py \
      --mode measure --out-run <dir> --out-results <dir> \
      --reading-rule experiments/EXP-DEP-001/reading_rule.yaml \
      --approval-receipt <TASK-20260801-041 snapshot_commit_receipt.json>

`--mode measure` REFUSES TO START unless the approval receipt records
APPROVAL_DETERMINATION == "APPROVED" and the frozen reading rule exists.
Both must be supplied on the command line; neither is defaulted.

Run from the repository root.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import resource
import statistics as _stats
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np

# --------------------------------------------------------------------------
# Frozen constants. Every one is fixed by
# experiments/EXP-DEP-001/specification.yaml and none may be tuned here.
# --------------------------------------------------------------------------
EXPERIMENT_ID = "EXP-DEP-001"
SPEC_PATH = "experiments/EXP-DEP-001/specification.yaml"
SPEC_SHA256_AT_FREEZE = (
    "e4a977f2117b190fef2baa95e2fbb7791d601b5a42c783b82d835222d9c9e20d")

EQD_DRIVER_PATH = "experiments/EXP-EQD-001/implementation/eqd001_driver.py"
EQD_DRIVER_SHA256 = (
    "bdb2601b195f314a4430fa80fcf8ab15ec0b605335a8386a93c2b9b3c7d7b02f")
EQD_NULL_STATS_PATH = (
    "experiments/EXP-EQD-001/results/calib/null_replicate_statistics.json")
EQD_NULL_STATS_SHA256 = (
    "284ca32143b386beefe80bae5ae05419a2b2f9286c96e3450e09c33e0fdca019")

MASTER_SEED = 2301                       # seeds.master_seed
FIELD_BITS = (16, 20)                    # the two frozen toy cells
BFB = 512                                # parameters.factor_base_size_Bfb
N_PER_ARM = BFB * (BFB - 1) // 2         # 130816, diagonal excluded BY CONSTRUCTION
RESOLUTION_LADDER_K = (16, 64)           # parameters.resolution_ladder_K
R_REPS = 200                             # parameters.R_REPS
R_ANCHOR_REPS = 20                       # parameters.R_ANCHOR_REPS
M_PAIRS = 200                            # DEP-CAL-A replicate pairs per cell
IDENT_REPS = 20                          # DEP-CAL-E comparisons per cell
S3_CONTROL_SAMPLE = 1000                 # CTRL-DEP-S3 half-tuples per cell

LADDER_RHO = (0.0025, 0.005, 0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.00)
LADDER_CELL = (0.005, 0.01, 0.02, 0.05, 0.10, 0.25)
LADDER_BLOCK = (0.05, 0.25, 1.00)

RHO_STAR = 0.05                          # cut_values_frozen_in_advance
EPS_STAR = 0.02                          # cut_values_frozen_in_advance
DET_RATE_MIN = 0.95                      # DET-DEP-1 first clause
DET_LOWER_BOUND_MIN = 0.90               # DET-DEP-1 second clause
CERTIFYING_STATISTICS = ("STAT-CHI-16", "STAT-CHI-64", "STAT-KS1-E1")  # CERT-DEP-1
THR_DEP_REPRO_BAND = (0, 8)              # THR-DEP-REPRO declared band
NONE_ON_LADDER = "NONE_ON_LADDER"        # the declared literal of DDV-4 / DDV-5

# seeds.streams. Every offset MUST be disjoint from the archived EXP-EQD-001
# offsets below; the disjointness is verified at startup and recorded.
STREAM_OFFSETS = {
    "calibration_null": 60000,
    "source_null_for_plants": 70000,
    "copula_noise": 80000,
    "cell_transfer": 90000,
    "block_permutation": 110000,
    "apparatus_identity": 120000,
    "faithfulness_sample": 130000,
}
ARCHIVED_EQD_STREAM_OFFSETS = (10000, 20000, 30000, 40000, 50000)

# Tripwire for ATS-DEP-1.3. Flipped only by dep_deterministic_factor_base().
_REAL_OBJECT_TOUCHED = False


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}",
          flush=True)


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# --------------------------------------------------------------------------
# CTRL-DEP-EQDHASH: read-only import of the EXP-EQD-001 driver.
# --------------------------------------------------------------------------
def load_eqd_module():
    """Import experiments/EXP-EQD-001/implementation/eqd001_driver.py READ-ONLY
    after verifying its sha256, and verify the archived null-replicate array's
    sha256 too. A mismatch raises and ABORTS before any arm is computed."""
    if not os.path.exists(SPEC_PATH):
        raise ValueError(
            f"{SPEC_PATH} not found; this driver must be run from the "
            "repository root")
    for path, want in ((EQD_DRIVER_PATH, EQD_DRIVER_SHA256),
                       (EQD_NULL_STATS_PATH, EQD_NULL_STATS_SHA256)):
        if not os.path.exists(path):
            raise ValueError(f"CTRL-DEP-EQDHASH: {path} not found")
        got = sha256_file(path)
        if got != want:
            raise ValueError(
                f"CTRL-DEP-EQDHASH MISMATCH on {path}: expected {want}, got "
                f"{got}. This is an integrity failure, never a datum.")
    spec = importlib.util.spec_from_file_location(
        "eqd001_driver_readonly", EQD_DRIVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EQD = None            # populated by main(); the read-only EXP-EQD-001 module
STATISTIC_IDS = ("STAT-CHI-16", "STAT-CHI-64", "STAT-KS1-E1", "STAT-KS1-E2")


def eqd_tree_unmodified() -> dict:
    """Record, not assert: `git status --porcelain` restricted to the
    EXP-EQD-001 subtree must be empty, and the two hash-bound files must still
    carry their contract hashes."""
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--", "experiments/EXP-EQD-001"],
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception as exc:                                # pragma: no cover
        return {"unmodified": None, "porcelain": None, "error": str(exc)}
    return {
        "unmodified": (out == ""
                       and sha256_file(EQD_DRIVER_PATH) == EQD_DRIVER_SHA256
                       and sha256_file(EQD_NULL_STATS_PATH) == EQD_NULL_STATS_SHA256),
        "porcelain": out,
        "eqd_driver_sha256": sha256_file(EQD_DRIVER_PATH),
        "eqd_null_stats_sha256": sha256_file(EQD_NULL_STATS_PATH),
    }


# --------------------------------------------------------------------------
# Exact binomial confidence bounds. Dependency-free by design: the run may not
# add a dependency, so the Clopper-Pearson bounds are obtained by bisection on
# the exact binomial tail rather than from a beta quantile in scipy.
# --------------------------------------------------------------------------
def _log_binom_pmf(n: int, k: int, p: float) -> float:
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(p) + (n - k) * math.log1p(-p))


def _binom_sf_ge(n: int, x: int, p: float) -> float:
    """P(X >= x) for X ~ Binomial(n, p)."""
    if x <= 0:
        return 1.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    return math.fsum(math.exp(_log_binom_pmf(n, k, p)) for k in range(x, n + 1))


def _binom_cdf_le(n: int, x: int, p: float) -> float:
    """P(X <= x) for X ~ Binomial(n, p)."""
    if x >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    return math.fsum(math.exp(_log_binom_pmf(n, k, p)) for k in range(0, x + 1))


def _bisect(f, lo: float, hi: float, target: float, iters: int = 200) -> float:
    """f is monotone on [lo, hi]; solve f(p) = target."""
    f_lo = f(lo)
    increasing = f(hi) > f_lo
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        v = f(mid)
        if (v < target) == increasing:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson(x: int, n: int) -> dict:
    """Exact two-sided 95 percent interval and the one-sided 95 percent LOWER
    bound, on x successes out of n. DDV-1..DDV-3 reporting form."""
    if n <= 0:
        return {"successes": x, "n": n, "rate": None,
                "ci95_two_sided": [None, None], "ci95_lower_one_sided": None}
    rate = x / n
    lo2 = 0.0 if x == 0 else _bisect(
        lambda p: _binom_sf_ge(n, x, p), 0.0, 1.0, 0.025)
    hi2 = 1.0 if x == n else _bisect(
        lambda p: _binom_cdf_le(n, x, p), 0.0, 1.0, 0.025)
    lo1 = 0.0 if x == 0 else _bisect(
        lambda p: _binom_sf_ge(n, x, p), 0.0, 1.0, 0.05)
    return {"successes": int(x), "n": int(n), "rate": rate,
            "ci95_two_sided": [lo2, hi2], "ci95_lower_one_sided": lo1}


def selfcheck_clopper_pearson() -> dict:
    """A startup self-check of the dependency-free bound implementation.

    Two structurally independent checks:
      (i) RESIDUAL CHECK. A Clopper-Pearson bound is DEFINED by a tail
          equation, so the returned bounds are substituted back into the
          defining equations and the residuals must vanish. This checks the
          solve without re-deriving it.
     (ii) CLOSED FORM. For x = n the two-sided lower bound is exactly
          alpha ** (1 / n) with alpha = 0.025.

    The 190-of-200 value is also recorded because DET-DEP-1's rationale in the
    contract quotes an approximate figure of about 0.9145 for it. The measured
    exact one-sided lower bound is recorded beside that prose figure without
    adjusting either; both exceed the DET-DEP-1 floor of 0.90, so the bar's
    attainability is unaffected either way.
    """
    a = clopper_pearson(190, 200)
    b = clopper_pearson(200, 200)
    exact = 0.025 ** (1.0 / 200)
    res_lo1 = abs(_binom_sf_ge(200, 190, a["ci95_lower_one_sided"]) - 0.05)
    res_lo2 = abs(_binom_sf_ge(200, 190, a["ci95_two_sided"][0]) - 0.025)
    res_hi2 = abs(_binom_cdf_le(200, 190, a["ci95_two_sided"][1]) - 0.025)
    ok = (res_lo1 < 1e-9 and res_lo2 < 1e-9 and res_hi2 < 1e-9
          and abs(b["ci95_two_sided"][0] - exact) < 1e-12
          and abs(b["ci95_two_sided"][1] - 1.0) < 1e-12)
    return {"cp_190_of_200_one_sided_lower": a["ci95_lower_one_sided"],
            "cp_190_of_200_two_sided": a["ci95_two_sided"],
            "cp_190_of_200_contract_prose_figure": 0.9145,
            "cp_190_of_200_prose_figure_note":
                "The contract's DET-DEP-1 rationale quotes about 0.9145 for the "
                "one-sided lower bound at 190 of 200. The exact value measured "
                "here is recorded beside it and neither is adjusted; both are "
                "above the 0.90 floor, so the bar remains attainable and "
                "non-vacuous. Recorded as an observation, not a correction.",
            "residual_one_sided_lower": res_lo1,
            "residual_two_sided_lower": res_lo2,
            "residual_two_sided_upper": res_hi2,
            "cp_200_of_200_two_sided_lower": b["ci95_two_sided"][0],
            "cp_200_of_200_closed_form_lower": exact,
            "selfcheck_passed": bool(ok)}


def two_proportion_one_sided_z(x1: int, n1: int, x2: int, n2: int) -> float:
    """One-sided pooled two-proportion z for (p1 > p2). Reported as a measured
    number for the D-1 artifact-tell input; NO branch is selected here."""
    if n1 <= 0 or n2 <= 0:
        return float("nan")
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    den = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    if den == 0.0:
        return 0.0
    return (p1 - p2) / den


# --------------------------------------------------------------------------
# Rank machinery. Ties are broken BY INDEX exactly as the contract prescribes
# for the plant constructions; the Spearman diagnostic uses AVERAGE ranks,
# which is the standard definition and is the correct one for a correlation on
# a tied sample.
# --------------------------------------------------------------------------
def ranks_ties_by_index(x: np.ndarray) -> np.ndarray:
    """0-based ranks with ties broken by index (stable sort)."""
    order = np.argsort(x, kind="stable")
    r = np.empty(x.size, dtype=np.int64)
    r[order] = np.arange(x.size, dtype=np.int64)
    return r


def average_ranks(x: np.ndarray) -> np.ndarray:
    """1-based average ranks (ties share the mean of their rank block)."""
    n = x.size
    order = np.argsort(x, kind="stable")
    xs = x[order]
    ar = np.empty(n, dtype=np.float64)
    start = 0
    for i in range(1, n + 1):
        if i == n or xs[i] != xs[start]:
            ar[start:i] = 0.5 * (start + i - 1) + 1.0
            start = i
    out = np.empty(n, dtype=np.float64)
    out[order] = ar
    return out


def _average_ranks_fast(x: np.ndarray) -> np.ndarray:
    """Vectorised equivalent of average_ranks(); the slow reference above is
    kept and is checked against this one at startup."""
    n = x.size
    order = np.argsort(x, kind="stable")
    xs = x[order]
    idx = np.arange(n, dtype=np.int64)
    newblock = np.empty(n, dtype=bool)
    newblock[0] = True
    np.not_equal(xs[1:], xs[:-1], out=newblock[1:])
    starts = idx[newblock]
    block_id = np.cumsum(newblock) - 1
    ends = np.append(starts[1:], n)
    avg = 0.5 * (starts + ends - 1) + 1.0
    ar = avg[block_id]
    out = np.empty(n, dtype=np.float64)
    out[order] = ar
    return out


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation, average ranks, Pearson on the ranks."""
    rx = _average_ranks_fast(x)
    ry = _average_ranks_fast(y)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = math.sqrt(float(np.dot(rx, rx)) * float(np.dot(ry, ry)))
    if denom == 0.0:
        return 0.0
    return float(np.dot(rx, ry) / denom)


_PHI_INV_GRID: dict[int, np.ndarray] = {}


def phi_inv_grid(n: int) -> np.ndarray:
    """The ascending vector Phi_inv((k + 0.5) / n), k = 0 .. n-1.

    Only this vector is needed for the copula construction: Z1 is exactly this
    vector indexed by the ties-by-index ranks of e_1. Computed once per n with
    the standard library's NormalDist.inv_cdf (no new dependency) and cached.
    """
    if n not in _PHI_INV_GRID:
        nd = _stats.NormalDist()
        _PHI_INV_GRID[n] = np.array(
            [nd.inv_cdf((k + 0.5) / n) for k in range(n)], dtype=np.float64)
    return _PHI_INV_GRID[n]


# --------------------------------------------------------------------------
# THE THREE DEPENDENCE-ONLY PLANT FAMILIES.
# In all three, e_1 IS UNTOUCHED and e_2 IS PERMUTED, so BOTH MARGINALS ARE
# EXACTLY INVARIANT BY CONSTRUCTION. CTRL-DEP-MARG verifies that empirically on
# every single arm rather than trusting the construction.
# --------------------------------------------------------------------------
def plant_copula(e1: np.ndarray, e2: np.ndarray, rho: float,
                 rng: np.random.Generator) -> np.ndarray:
    """OBJ-PLANT-DEP-rho, alternative class C1, PRIMARY.

    r1 = ranks of e1, ties by index; Z1 = Phi_inv((r1 - 0.5) / n);
    W ~ N(0, 1) iid of length n from the copula stream;
    Z2 = rho * Z1 + sqrt(1 - rho**2) * W;
    e2_new[i] = sorted_e2[rank(Z2)[i]], ranks ties by index.

    rho = 0 degenerates to a uniform random permutation of e_2 (OBJ-PLANT-DEP-0).
    Mass moves ACROSS e_1 bins, so the K x K table is NOT invariant --
    DESIGN-TRAP-1.
    """
    n = e1.size
    grid = phi_inv_grid(n)
    z1 = grid[ranks_ties_by_index(e1)]
    w = rng.standard_normal(n)
    z2 = rho * z1 + math.sqrt(max(0.0, 1.0 - rho * rho)) * w
    s = ranks_ties_by_index(z2)
    return np.sort(e2)[s]


def plant_comonotone(e1: np.ndarray, e2: np.ndarray) -> np.ndarray:
    """OBJ-PLANT-DEP-EXTREME, the attainability ANCHOR: the comonotone
    reordering e2_new[i] = sorted_e2[rank(e1)[i]] exactly, no noise. The
    maximal monotone dependence available at bit-identical marginals."""
    return np.sort(e2)[ranks_ties_by_index(e1)]


def plant_cell(e1: np.ndarray, e2: np.ndarray, eps: float, p: int,
               rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """OBJ-PLANT-DEP-CELL-eps, alternative class C2.

    floor(eps * n / 2) DISJOINT index pairs (u, v) drawn uniformly at random
    subject to bin_16(e1[u]) != bin_16(e1[v]); e2[u] and e2[v] are EXCHANGED.

    Implementation of "uniformly at random subject to the constraint": draw a
    uniform random permutation of the n indices, read it as n/2 consecutive
    disjoint candidate pairs, discard the candidates whose two e_1 bins
    coincide, and take the first floor(eps * n / 2) survivors. Consecutive
    pairs of a uniform permutation are an exchangeable uniform pairing, so the
    retained pairs are a uniform sample of admissible disjoint pairs, and
    disjointness holds by construction. Additional permutations are drawn only
    if a single one does not yield enough survivors (at K = 16 about 15/16 of
    candidates survive, so for every rung of DEP-LADDER-CELL one permutation
    suffices with room to spare).
    """
    n = e1.size
    need = int(math.floor(eps * n / 2.0))
    bins = (e1 * 16) // p
    us: list[np.ndarray] = []
    vs: list[np.ndarray] = []
    have = 0
    guard = 0
    while have < need:
        guard += 1
        if guard > 16:
            raise RuntimeError(
                "plant_cell could not find enough admissible disjoint pairs")
        perm = rng.permutation(n)
        m = n // 2
        u = perm[:m]
        v = perm[m:2 * m]
        keep = bins[u] != bins[v]
        u, v = u[keep], v[keep]
        take = min(need - have, u.size)
        us.append(u[:take])
        vs.append(v[:take])
        have += take
    if not us:
        return e2.copy(), 0
    u = np.concatenate(us)
    v = np.concatenate(vs)
    out2 = e2.copy()
    out2[u], out2[v] = e2[v], e2[u]
    return out2, int(u.size)


def plant_block(e1: np.ndarray, e2: np.ndarray, q: float,
                rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """OBJ-PLANT-DEP-BLOCK-q, alternative class C3.

    Split the records into TWO strata at the median of e_1 (by ties-by-index
    rank, so the strata are exactly n/2 and n - n/2), choose a fraction q of
    the records in each stratum uniformly at random, and apply an independent
    uniform random permutation to the CHOSEN e_2 values WITHIN each stratum.

    TWO strata are far COARSER than K = 16, so the reordering moves mass across
    grid bins -- DESIGN-TRAP-1 again.
    """
    n = e1.size
    r = ranks_ties_by_index(e1)
    lower = np.nonzero(r < n // 2)[0]
    upper = np.nonzero(r >= n // 2)[0]
    out2 = e2.copy()
    moved = 0
    for stratum in (lower, upper):
        k = int(math.floor(q * stratum.size))
        if k < 2:
            continue
        chosen = stratum[rng.choice(stratum.size, size=k, replace=False)]
        out2[chosen] = e2[chosen][rng.permutation(k)]
        moved += k
    return out2, moved


# --------------------------------------------------------------------------
# CTRL-DEP-MARG and DIAG-DEP-RHO.
# --------------------------------------------------------------------------
def plant_arm(e1s: np.ndarray, e2p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Materialise the planted arm as its OWN arrays.

    e_1 is untouched by every plant family, but the planted arm is built as an
    INDEPENDENT COPY rather than as an alias of the source array, so that
    CTRL-DEP-MARG's e_1 digest comparison is a real comparison of two separately
    computed digests and not a vacuous comparison of an object with itself.
    """
    return e1s.copy(), e2p


def sorted_digest(a: np.ndarray) -> str:
    """sha256 over the canonical little-endian 8-byte encoding of sort(a)."""
    return hashlib.sha256(np.sort(a).astype("<i8").tobytes()).hexdigest()


def marginal_histogram(e: np.ndarray, p: int, K: int) -> np.ndarray:
    return np.bincount((e * K) // p, minlength=K)[:K]


def marginal_integrity(e1s, e2s, e1p, e2p, p: int, label: str,
                       rung, replicate: int, full_histograms: bool = True) -> dict:
    """CTRL-DEP-MARG on one planted arm. MANDATORY, no exceptions.

    Recording policy, declared in implementation.md: the four sorted-marginal
    digests are recorded in full for EVERY arm; the four SOURCE histograms are
    recorded in full and the four PLANT histograms are recorded as digests
    together with the count-by-count equality booleans, from which the plant
    histograms are recoverable and independently verifiable. The comparison
    itself is always performed on the full histograms.
    """
    d = {
        "sorted_e1_sha256_source": sorted_digest(e1s),
        "sorted_e1_sha256_plant": sorted_digest(e1p),
        "sorted_e2_sha256_source": sorted_digest(e2s),
        "sorted_e2_sha256_plant": sorted_digest(e2p),
    }
    hist_source: dict[str, list[int]] = {}
    hist_source_digest: dict[str, str] = {}
    hist_plant_digest: dict[str, str] = {}
    equal: dict[str, bool] = {}
    for name, src, pl in (("e1", e1s, e1p), ("e2", e2s, e2p)):
        for K in RESOLUTION_LADDER_K:
            hs = marginal_histogram(src, p, K)
            hp = marginal_histogram(pl, p, K)
            key = f"{name}_K{K}"
            # The comparison is ALWAYS performed count by count on the full
            # histograms; `full_histograms` governs only how much is archived.
            equal[key] = bool(np.array_equal(hs, hp))
            hist_source_digest[key] = hashlib.sha256(
                hs.astype("<i8").tobytes()).hexdigest()
            hist_plant_digest[key] = hashlib.sha256(
                hp.astype("<i8").tobytes()).hexdigest()
            if full_histograms:
                hist_source[key] = [int(v) for v in hs]
    digests_equal = bool(
        d["sorted_e1_sha256_source"] == d["sorted_e1_sha256_plant"]
        and d["sorted_e2_sha256_source"] == d["sorted_e2_sha256_plant"])
    ok = bool(digests_equal and all(equal.values()))
    return {
        "family": label, "rung": rung, "replicate": replicate,
        "digests": d,
        "sorted_digests_equal": digests_equal,
        "marginal_histograms_source": hist_source,
        "marginal_histograms_source_sha256": hist_source_digest,
        "marginal_histograms_plant_sha256": hist_plant_digest,
        "full_histograms_archived": bool(full_histograms),
        "marginal_histograms_equal": equal,
        "marg_histograms_equal": bool(all(equal.values())),
        "CTRL_DEP_MARG_ok": ok,
    }


def joint_tv_distance_k16(e1s, e2s, e1p, e2p, p: int) -> float:
    """DIAG-DEP-RHO: total variation distance between the source and plant
    K = 16 joint tables. A plant that leaves this at zero is a null object
    wearing a plant's name."""
    K = 16
    ha = np.bincount(EQD._cell_index(e1s, e2s, p, K), minlength=K * K).astype(np.float64)
    hb = np.bincount(EQD._cell_index(e1p, e2p, p, K), minlength=K * K).astype(np.float64)
    return float(0.5 * np.sum(np.abs(ha / ha.sum() - hb / hb.sum())))


def induced_dependence(e1s, e2s, e1p, e2p, p: int) -> dict:
    """DIAG-DEP-RHO on one planted arm."""
    return {
        "spearman_source": spearman(e1s.astype(np.float64), e2s.astype(np.float64)),
        "spearman_plant": spearman(e1p.astype(np.float64), e2p.astype(np.float64)),
        "joint_tv_distance_k16": joint_tv_distance_k16(e1s, e2s, e1p, e2p, p),
    }


# --------------------------------------------------------------------------
# CTRL-DEP-S3: faithfulness by ACTUAL POINT ARITHMETIC, on a UNIFORM RANDOM
# sample of the full enumeration and NOT on a prefix.
# --------------------------------------------------------------------------
def ctrl_dep_s3(cell, xs: np.ndarray, e1: np.ndarray, e2: np.ndarray,
                rng: np.random.Generator, sample: int = S3_CONTROL_SAMPLE) -> dict:
    """For `sample` half-tuples SAMPLED UNIFORMLY AT RANDOM WITHOUT REPLACEMENT
    from the full enumeration, verify by independent point arithmetic on
    E(F_p) that e_1 == x(P + Q) + x(P - Q) and e_2 == x(P + Q) * x(P - Q).
    The point arithmetic does not reuse the coefficient formula."""
    p = cell.p
    total_available = int(cell.iu.size)
    take = min(sample, total_available)
    idx = rng.choice(total_available, size=take, replace=False)
    verified = 0
    total = 0
    for t in idx.tolist():
        i, j = int(cell.iu[t]), int(cell.ju[t])
        Pi = cell.curve.lift_x(int(xs[i]))
        Pj = cell.curve.lift_x(int(xs[j]))
        total += 1
        if Pi is None or Pj is None:
            continue
        S = cell.curve.add(Pi, Pj)
        D = cell.curve.add(Pi, cell.curve.negate(Pj))
        if S is None or D is None:
            continue
        xs_, xd_ = S[0], D[0]
        if (int(e1[t]) == (xs_ + xd_) % p) and (int(e2[t]) == (xs_ * xd_) % p):
            verified += 1
    return {"verified": verified, "total": total,
            "sampling": "uniform at random without replacement from the full "
                        "enumeration of C(512, 2) = 130816 half-tuples, NOT a prefix",
            "method": "independent point arithmetic on E(F_p) via harness.toycurve"}


# --------------------------------------------------------------------------
# Arm drawing, shared by both stages.
# --------------------------------------------------------------------------
def draw_null_arm(cell, stream, k: int, integrity: dict) -> tuple:
    """One OBJ-NULL-RFB arm through the imported EXP-EQD-001 code path."""
    draw = cell.draw_null_factor_base(stream, k)
    e1, e2, degenerate = cell.enumerate_factor_base(draw["xs"])
    integrity["degenerate_draw_count"] += degenerate
    integrity["null_redraw_count_total"] += draw["redraw_count"]
    integrity["null_redraw_counts"].append(int(draw["redraw_count"]))
    if degenerate:
        raise RuntimeError(
            f"INTEGRITY FAILURE: {degenerate} c_2 == 0 draws on a null arm at "
            f"bits {cell.bits}, draw {k}. The diagonal is excluded by "
            "construction; this is not a datum.")
    if e1.size != N_PER_ARM:
        raise RuntimeError(f"arm has {e1.size} pairs, expected {N_PER_ARM}")
    if int(e1.min()) < 0 or int(e1.max()) >= cell.p or \
       int(e2.min()) < 0 or int(e2.max()) >= cell.p:
        integrity["range_violations"] += 1
        raise RuntimeError("range violation: e out of [0, p)")
    return e1, e2, draw


def statistics_of(arm_a, arm_b, p: int) -> dict:
    """The four two-sample statistics of STAT-DEP-1, from the imported
    EXP-EQD-001 code path, as bare numbers."""
    st = EQD.all_two_sample_statistics(arm_a, arm_b, p)
    return EQD.flat_two_sample_values(st)


# --------------------------------------------------------------------------
# THR-DEP-1: the ARCHIVED EXP-EQD-001 thresholds, read at run time.
# --------------------------------------------------------------------------
def archived_thresholds() -> dict:
    """DEP-CAL-B. Recompute each archived threshold as the 199th ASCENDING
    order statistic of its named 200-element array, and record the recomputed
    value beside the archived one. The RECOMPUTED value is what is used."""
    with open(EQD_NULL_STATS_PATH) as fh:
        doc = json.load(fh)
    out = {"artifact": EQD_NULL_STATS_PATH,
           "artifact_sha256": sha256_file(EQD_NULL_STATS_PATH),
           "artifact_sha256_expected": EQD_NULL_STATS_SHA256,
           "eqd_driver_sha256": sha256_file(EQD_DRIVER_PATH),
           "eqd_driver_sha256_expected": EQD_DRIVER_SHA256,
           "order_statistic_index_1based": 199,
           "rejection_rule": "strictly greater than the threshold",
           "cells": {}}
    for bits in FIELD_BITS:
        c = doc["cells"][str(bits)]
        per = {}
        for sid in STATISTIC_IDS:
            arr = list(c["replicate_values"][sid])
            if len(arr) != 200:
                raise ValueError(
                    f"archived array {sid} at bits {bits} has {len(arr)} "
                    "elements, expected 200")
            recomputed = sorted(arr)[198]
            archived = c["measured_order_statistics"][sid][
                "value_at_199th_order_statistic"]
            per[sid] = {
                "archived_value_at_199th_order_statistic": archived,
                "recomputed_value_at_199th_order_statistic": recomputed,
                "equal": bool(recomputed == archived),
                "absolute_difference": abs(recomputed - archived),
                "n_values": len(arr),
            }
        out["cells"][str(bits)] = per
    out["all_reproduced_exactly"] = bool(all(
        v["equal"] for c in out["cells"].values() for v in c.values()))
    return out


def threshold_vector(repro: dict, bits: int) -> dict:
    return {sid: repro["cells"][str(bits)][sid][
        "recomputed_value_at_199th_order_statistic"] for sid in STATISTIC_IDS}


def rejects_against(values: dict, thr: dict) -> dict:
    """STRICTLY GREATER THAN, as in EXP-EQD-001."""
    return {sid: bool(values[sid] > thr[sid]) for sid in STATISTIC_IDS}


def detection_summary(rows: list[dict], thr: dict) -> dict:
    """Per-statistic detection counts, rates and exact binomial bounds over a
    list of replicate value dicts. MEASURED NUMBERS. DET-DEP-1's conjunction is
    evaluated ONLY in the measurement stage, where it is a substitution of
    measured numbers into a form frozen before any datum existed."""
    out = {}
    for sid in STATISTIC_IDS:
        x = sum(1 for r in rows if r[sid] > thr[sid])
        cp = clopper_pearson(x, len(rows))
        out[sid] = {"threshold_archived_recomputed": thr[sid],
                    "n_replicates": len(rows), "n_exceeding": x, **cp}
    return out


# --------------------------------------------------------------------------
# Stream bookkeeping and the disjointness verification.
# --------------------------------------------------------------------------
def make_stream(name: str, bits: int):
    return EQD.Stream(name, MASTER_SEED + STREAM_OFFSETS[name] + bits)


def stream_disjointness_record() -> dict:
    archived = {MASTER_SEED + off + bits
                for off in ARCHIVED_EQD_STREAM_OFFSETS for bits in FIELD_BITS}
    rows = []
    collision = False
    for name, off in STREAM_OFFSETS.items():
        for bits in FIELD_BITS:
            seed = MASTER_SEED + off + bits
            hit = seed in archived
            collision = collision or hit
            rows.append({"stream_name": name, "field_bits": bits, "seed": seed,
                         "seed_sha256": sha256_text(f"{name}:{seed}"),
                         "collides_with_archived_EQD_stream": hit})
    return {"streams": rows,
            "archived_EQD_seeds": sorted(archived),
            "archived_EQD_stream_offsets": list(ARCHIVED_EQD_STREAM_OFFSETS),
            "all_disjoint_from_archived_EQD_streams": not collision}


# --------------------------------------------------------------------------
# THE REAL OBJECT. ATS-DEP-1.3 tripwire lives here and NOWHERE ELSE.
# --------------------------------------------------------------------------
def dep_deterministic_factor_base(cell) -> dict:
    """OBJ-REAL support: the frozen deterministic factor base of EXP-EQD-001,
    the first 512 x-coordinates of X_E in increasing integer order.

    CALLING THIS FUNCTION IS "SEEING THE REAL DATA". It is called by
    `run_duplicate_decomposition()` and by nothing else, that function is
    reachable only from `--mode measure`, and this function flips the
    module-level tripwire that a calibration run asserts against.

    NO STATISTIC OF OBJ-REAL AGAINST ANY NULL IS COMPUTED ANYWHERE IN THIS
    DRIVER. The single purpose of this object is the DIAG-DEP-DUP decomposed
    duplicate diagnostic.
    """
    global _REAL_OBJECT_TOUCHED
    _REAL_OBJECT_TOUCHED = True
    xs = cell.X_E[:BFB].astype(np.int64)
    if xs.size != BFB:
        raise ValueError(f"only {xs.size} x-coordinates available, need {BFB}")
    return {"xs": xs,
            "factor_base_sha256": sha256_text("\n".join(str(int(v)) for v in xs))}


# --------------------------------------------------------------------------
# CALIBRATION ARM: DEP-CAL-A .. DEP-CAL-F. EXPRESSLY NON-EVIDENTIAL.
# --------------------------------------------------------------------------
def run_calibration(cell, repro: dict, deadline: float) -> dict:
    """One cell of RUN-DEP-001-calib. Measures the instrument on NULL and
    PLANT-MACHINERY objects only. Runs no ladder rung, touches no real data,
    freezes no threshold, applies no reading rule, states no disposition."""
    p = cell.p
    thr = threshold_vector(repro, cell.bits)
    null_stream = make_stream("calibration_null", cell.bits)
    source_stream = make_stream("source_null_for_plants", cell.bits)
    copula_stream = make_stream("copula_noise", cell.bits)
    ident_stream = make_stream("apparatus_identity", cell.bits)
    faith_stream = make_stream("faithfulness_sample", cell.bits)

    integrity = {"degenerate_draw_count": 0, "null_redraw_count_total": 0,
                 "null_redraw_counts": [], "range_violations": 0,
                 "pairs_recorded_per_arm": [], "arms_short_of_n": 0}
    marg_records: list[dict] = []
    marg_mismatch_locations: list[dict] = []
    out: dict = {"cell": cell.descriptor(),
                 "archived_thresholds_used": thr,
                 "complete": {}, "integrity": integrity}

    def check_deadline(stage: str):
        if time.time() > deadline:
            raise TimeoutError(f"wall-clock budget exhausted during {stage}")

    def record_plant(label, rung, rep, e1s, e2s, e1p, e2p):
        """CTRL-DEP-MARG + DIAG-DEP-RHO on one planted arm. A mismatch ABORTS
        the arm and is recorded with its rung and replicate index."""
        m = marginal_integrity(e1s, e2s, e1p, e2p, p, label, rung, rep)
        diag = induced_dependence(e1s, e2s, e1p, e2p, p)
        m["DIAG_DEP_RHO"] = diag
        m["field_bits"] = cell.bits
        marg_records.append(m)
        if not m["CTRL_DEP_MARG_ok"]:
            loc = {"family": label, "rung": rung, "replicate": rep,
                   "field_bits": cell.bits}
            marg_mismatch_locations.append(loc)
            raise RuntimeError(
                "CTRL-DEP-MARG MISMATCH (INSTRUMENT FAILURE, NEVER A RESULT) "
                f"at {loc}")
        return diag

    # ---- DEP-CAL-A: fresh null-versus-null distribution ------------------
    _log(f"bits={cell.bits} DEP-CAL-A: {M_PAIRS} fresh null-vs-null replicate pairs")
    cal_a_rows: list[dict] = []
    representative = None
    nk = 0
    for r in range(M_PAIRS):
        check_deadline(f"DEP-CAL-A replicate {r}")
        e1a, e2a, da = draw_null_arm(cell, null_stream, nk, integrity); nk += 1
        e1b, e2b, db = draw_null_arm(cell, null_stream, nk, integrity); nk += 1
        integrity["pairs_recorded_per_arm"].extend([int(e1a.size), int(e1b.size)])
        vals = statistics_of((e1a, e2a), (e1b, e2b), p)
        cal_a_rows.append({"replicate": r, **vals})
        if r == 0:
            s3 = ctrl_dep_s3(cell, da["xs"], e1a, e2a, faith_stream.generator(0))
            representative = {
                "object": "OBJ-NULL-RFB",
                "note": "representative NULL draw archived for reproducibility; "
                        "it is not real data and is not the deterministic base",
                "calibration_null_stream_draw_index": 0,
                "draw_seed": null_stream.draw_seed(0),
                "x_list_sha256": da["x_list_sha256"],
                "x_list": [int(v) for v in da["xs"]],
                "redraw_count": int(da["redraw_count"]),
                "n_pairs": int(e1a.size),
                "spearman_e1_e2": spearman(e1a.astype(np.float64),
                                           e2a.astype(np.float64)),
                "CTRL-DEP-S3": s3,
            }
        if (r + 1) % 50 == 0:
            _log(f"  bits={cell.bits} DEP-CAL-A {r + 1}/{M_PAIRS}")

    fresh_order_stats = {}
    for sid in STATISTIC_IDS:
        v = sorted(row[sid] for row in cal_a_rows)
        fresh_order_stats[sid] = {
            "order_statistic_index_1based": 199,
            "value_at_199th_order_statistic": v[198],
            "value_at_200th_order_statistic_max": v[199],
            "min": v[0], "median": 0.5 * (v[99] + v[100]),
            "mean": float(np.mean(v)), "stdev": float(np.std(v, ddof=1)),
        }
    repro_counts = {}
    for sid in STATISTIC_IDS:
        cnt = sum(1 for row in cal_a_rows if row[sid] > thr[sid])
        repro_counts[sid] = {
            "archived_threshold": thr[sid],
            "n_fresh_null_replicates": len(cal_a_rows),
            "count_strictly_exceeding_archived_threshold": cnt,
            "declared_band_THR_DEP_REPRO": list(THR_DEP_REPRO_BAND),
            "within_declared_band_mechanical": bool(
                THR_DEP_REPRO_BAND[0] <= cnt <= THR_DEP_REPRO_BAND[1]),
            "mechanical_restatement_note":
                "Mechanical restatement of a band frozen in the contract "
                "before any datum. NO branch is selected and NO disposition is "
                "stated here. The declared LOWER leg of the band is DEAD.",
        }
    out["DEP-CAL-A"] = {
        "M_PAIRS": M_PAIRS,
        "replicates": cal_a_rows,
        "fresh_secondary_order_statistics": fresh_order_stats,
        "archived_threshold_exceedances": repro_counts,
        "note": "MEASURED NUMBERS ONLY. This driver freezes no threshold. "
                "THR-DEP-1 is applied at TASK-20260801-038.",
    }
    out["complete"]["DEP-CAL-A"] = True

    # ---- DEP-CAL-C: plant-machinery null, OBJ-PLANT-DEP-0 ----------------
    _log(f"bits={cell.bits} DEP-CAL-C: {R_REPS} OBJ-PLANT-DEP-0 replicates")
    cal_c_rows: list[dict] = []
    sk = 0
    for rep in range(R_REPS):
        check_deadline(f"DEP-CAL-C replicate {rep}")
        e1s, e2s, _ = draw_null_arm(cell, source_stream, sk, integrity); sk += 1
        e1p, e2p = plant_arm(e1s, plant_copula(e1s, e2s, 0.0,
                                               copula_stream.generator(rep)))
        diag = record_plant("OBJ-PLANT-DEP-0", 0.0, rep, e1s, e2s, e1p, e2p)
        e1n, e2n, _ = draw_null_arm(cell, source_stream, sk, integrity); sk += 1
        integrity["pairs_recorded_per_arm"].extend([int(e1p.size), int(e1n.size)])
        vals = statistics_of((e1p, e2p), (e1n, e2n), p)
        cal_c_rows.append({"replicate": rep, **vals,
                           "spearman_source": diag["spearman_source"],
                           "spearman_plant": diag["spearman_plant"],
                           "joint_tv_distance_k16": diag["joint_tv_distance_k16"]})
        if (rep + 1) % 50 == 0:
            _log(f"  bits={cell.bits} DEP-CAL-C {rep + 1}/{R_REPS}")
    out["DEP-CAL-C"] = {
        "object": "OBJ-PLANT-DEP-0",
        "R_REPS": R_REPS,
        "replicates": cal_c_rows,
        "detection_against_archived_thresholds": detection_summary(cal_c_rows, thr),
        "note": "The plant machinery applied at rho = 0 exactly, which "
                "DESTROYS dependence rather than inducing it, at bit-identical "
                "marginals. Measured numbers only; no branch is selected.",
    }
    out["complete"]["DEP-CAL-C"] = True

    # ---- DEP-CAL-D: attainability anchor, OBJ-PLANT-DEP-EXTREME ----------
    _log(f"bits={cell.bits} DEP-CAL-D: {R_ANCHOR_REPS} OBJ-PLANT-DEP-EXTREME replicates")
    cal_d_rows: list[dict] = []
    for rep in range(R_ANCHOR_REPS):
        check_deadline(f"DEP-CAL-D replicate {rep}")
        e1s, e2s, _ = draw_null_arm(cell, source_stream, sk, integrity); sk += 1
        e1p, e2p = plant_arm(e1s, plant_comonotone(e1s, e2s))
        diag = record_plant("OBJ-PLANT-DEP-EXTREME", "comonotone", rep,
                            e1s, e2s, e1p, e2p)
        e1n, e2n, _ = draw_null_arm(cell, source_stream, sk, integrity); sk += 1
        integrity["pairs_recorded_per_arm"].extend([int(e1p.size), int(e1n.size)])
        vals = statistics_of((e1p, e2p), (e1n, e2n), p)
        cal_d_rows.append({"replicate": rep, **vals,
                           "spearman_source": diag["spearman_source"],
                           "spearman_plant": diag["spearman_plant"],
                           "joint_tv_distance_k16": diag["joint_tv_distance_k16"]})
    out["DEP-CAL-D"] = {
        "object": "OBJ-PLANT-DEP-EXTREME",
        "R_ANCHOR_REPS": R_ANCHOR_REPS,
        "replicates": cal_d_rows,
        "detection_against_archived_thresholds": detection_summary(cal_d_rows, thr),
        "declared_pre_disclosure": "ATS-DEP-1-CLAUSE-6. This anchor is measured "
                                   "in the CALIBRATION stage and its outcome "
                                   "partially foreshadows the substantive "
                                   "result. It is DECLARED rather than "
                                   "discovered, it is not a ladder rung, and no "
                                   "substantive branch reads it.",
    }
    out["complete"]["DEP-CAL-D"] = True

    # ---- DEP-CAL-E: apparatus-identity control ---------------------------
    _log(f"bits={cell.bits} DEP-CAL-E: {IDENT_REPS} fresh-null vs fresh-null comparisons")
    cal_e_rows: list[dict] = []
    ik = 0
    for rep in range(IDENT_REPS):
        check_deadline(f"DEP-CAL-E replicate {rep}")
        e1i, e2i, _ = draw_null_arm(cell, ident_stream, ik, integrity); ik += 1
        e1j, e2j, _ = draw_null_arm(cell, ident_stream, ik, integrity); ik += 1
        integrity["pairs_recorded_per_arm"].extend([int(e1i.size), int(e1j.size)])
        vals = statistics_of((e1i, e2i), (e1j, e2j), p)
        cal_e_rows.append({"replicate": rep, **vals,
                           **{f"exceeds_{sid}": bool(vals[sid] > thr[sid])
                              for sid in STATISTIC_IDS}})
    out["DEP-CAL-E"] = {
        "IDENT_REPS": IDENT_REPS,
        "replicates": cal_e_rows,
        "detection_against_archived_thresholds": detection_summary(cal_e_rows, thr),
        "note": "DERIVABLY the same law. A rejection is an implementation "
                "defect. NON-REJECTION IS NOT CORROBORATION OF ANYTHING and may "
                "not be reported as such.",
    }
    out["complete"]["DEP-CAL-E"] = True

    # ---- DEP-CAL-F: the RT049-B5 cheap check (bits 16) --------------------
    if cell.bits == 16:
        cnt = repro_counts["STAT-KS1-E2"]["count_strictly_exceeding_archived_threshold"]
        out["DEP-CAL-F"] = {
            "field_bits": 16,
            "statistic": "STAT-KS1-E2",
            "archived_threshold": thr["STAT-KS1-E2"],
            "n_fresh_null_replicates": len(cal_a_rows),
            "count_strictly_exceeding_archived_threshold": cnt,
            "rate": cnt / len(cal_a_rows),
            **{k: v for k, v in clopper_pearson(cnt, len(cal_a_rows)).items()
               if k not in ("successes", "n")},
            "note": "IT MEASURES THE RATE AND DOES NOT EXPLAIN IT. No "
                    "explanation of the rate is claimed anywhere in this run.",
        }
        out["complete"]["DEP-CAL-F"] = True

    # ---- integrity roll-up ------------------------------------------------
    arm_sizes = integrity.pop("pairs_recorded_per_arm")
    integrity["pairs_recorded_per_arm_distinct"] = sorted(set(arm_sizes))
    integrity["arms_recorded"] = len(arm_sizes)
    integrity["arms_short_of_n"] = sum(1 for v in arm_sizes if v != N_PER_ARM)
    integrity["null_redraw_count_total"] = int(integrity["null_redraw_count_total"])

    out["representative_null_draw"] = representative
    out["marginal_integrity_records"] = marg_records
    out["marg_mismatch_locations"] = marg_mismatch_locations
    out["CTRL_DEP_MARG_all_ok"] = bool(
        all(m["CTRL_DEP_MARG_ok"] for m in marg_records) and not marg_mismatch_locations)
    out["stream_hashes"] = [s.hash_record() for s in
                            (null_stream, source_stream, copula_stream,
                             ident_stream, faith_stream)]
    out["ladder_rungs_executed"] = []
    out["real_object_touched"] = _REAL_OBJECT_TOUCHED
    return out


def emit_calibration_results(out_results: str, cells: dict, repro: dict) -> None:
    """The three declared calibration result files. Measured numbers only."""
    disclaimer = (
        "EXPRESSLY NON-EVIDENTIAL about H-DEP-001, H-EQD-001, H-SMTH-001 and "
        "HEUR-DS-1 in either direction. Instrument measurement on NULL and "
        "PLANT-MACHINERY objects only. No threshold is frozen here, no reading "
        "rule is applied, no branch is selected and no disposition is stated.")

    null_stats = {"schema": "dep001_null_replicate_statistics/v1",
                  "disclaimer": disclaimer,
                  "stage": "DEP-CAL-A (with the DEP-CAL-F extract)",
                  "cells": {}}
    for bits, c in cells.items():
        entry = {
            "cell": c["cell"],
            "M_PAIRS": c["DEP-CAL-A"]["M_PAIRS"],
            "replicates": c["DEP-CAL-A"]["replicates"],
            "fresh_secondary_order_statistics":
                c["DEP-CAL-A"]["fresh_secondary_order_statistics"],
            "archived_thresholds_used": c["archived_thresholds_used"],
            "archived_threshold_exceedances":
                c["DEP-CAL-A"]["archived_threshold_exceedances"],
            "representative_null_draw": c["representative_null_draw"],
            "integrity": c["integrity"],
            "stream_hashes": c["stream_hashes"],
        }
        if "DEP-CAL-F" in c:
            entry["DEP-CAL-F"] = c["DEP-CAL-F"]
        null_stats["cells"][bits] = entry
    EQD.write_json(os.path.join(out_results, "null_replicate_statistics.json"),
                   null_stats)

    marg = {"schema": "dep001_marginal_integrity_report/v1",
            "disclaimer": disclaimer,
            "control": "CTRL-DEP-MARG (mandatory) and DIAG-DEP-RHO",
            "rule": "The plant arm's two sorted-marginal digests MUST equal the "
                    "source arm's, and the four marginal histograms MUST be "
                    "equal count by count. A MISMATCH IS INSTRUMENT FAILURE AND "
                    "IS NEVER A RESULT.",
            "what_it_does_not_prove": "It proves the marginals are preserved "
                                      "and NOTHING about whether the dependence "
                                      "actually moved. That is DIAG-DEP-RHO.",
            "recording_policy": "Four sorted-marginal digests in full for every "
                                "arm; source histograms in full, plant "
                                "histograms as sha256 digests plus the "
                                "count-by-count equality booleans. The "
                                "comparison itself is performed on the full "
                                "histograms.",
            "cells": {}}
    for bits, c in cells.items():
        recs = c["marginal_integrity_records"]
        marg["cells"][bits] = {
            "cell": c["cell"],
            "arms_checked": len(recs),
            "CTRL_DEP_MARG_all_ok": c["CTRL_DEP_MARG_all_ok"],
            "marg_mismatch_locations": c["marg_mismatch_locations"],
            "records": recs,
            "DEP-CAL-C_detection": c["DEP-CAL-C"]["detection_against_archived_thresholds"],
            "DEP-CAL-C_replicates": c["DEP-CAL-C"]["replicates"],
            "DEP-CAL-D_detection": c["DEP-CAL-D"]["detection_against_archived_thresholds"],
            "DEP-CAL-D_replicates": c["DEP-CAL-D"]["replicates"],
            "DEP-CAL-E_detection": c["DEP-CAL-E"]["detection_against_archived_thresholds"],
            "DEP-CAL-E_replicates": c["DEP-CAL-E"]["replicates"],
        }
    EQD.write_json(os.path.join(out_results, "marginal_integrity_report.json"), marg)

    repro_doc = dict(repro)
    repro_doc["schema"] = "dep001_archived_threshold_reproduction/v1"
    repro_doc["disclaimer"] = disclaimer
    repro_doc["stage"] = "DEP-CAL-B"
    repro_doc["fresh_secondary_order_statistics_per_cell"] = {
        bits: c["DEP-CAL-A"]["fresh_secondary_order_statistics"]
        for bits, c in cells.items()}
    repro_doc["fresh_secondary_note"] = (
        "The fresh secondary distribution is a reproduction check and a "
        "false-positive measurement. IT NEVER REPLACES THE PRIMARY ARCHIVED "
        "THRESHOLDS and nothing is frozen against it here.")
    EQD.write_json(
        os.path.join(out_results, "archived_threshold_reproduction.json"), repro_doc)


# --------------------------------------------------------------------------
# DIAG-DEP-DUP: the decomposed duplicate diagnostic. MEASUREMENT STAGE ONLY.
# Reachable ONLY from run_measurement(); it is the ONLY consumer of OBJ-REAL.
# --------------------------------------------------------------------------
def two_torsion_x_coordinates(cell) -> list[int]:
    """The x-coordinates t of the nontrivial 2-torsion points of E(F_p): the
    roots in F_p of x**3 + a x + b. E[2](F_p) is trivial when there is none."""
    p, a, b = cell.p, cell.a, cell.b
    xs = np.arange(p, dtype=np.int64)
    rhs = (xs * xs % p * xs % p + a * xs + b) % p
    return [int(t) for t in xs[rhs == 0].tolist()]


def translate_x_by_two_torsion(x: np.ndarray, t: int, cell) -> np.ndarray:
    """x(P + T) for T = (t, 0) of order 2, as a function of x(P) alone.

    With y**2 = x**3 + a x + b and t**3 + a t + b = 0,
      x(P + T) = (t * x + 2 * t**2 + a) / (x - t)  mod p,
    an involution on the x-line away from x = t. Verified against independent
    point arithmetic by `_selfcheck_translate()`.
    """
    p, a = cell.p, cell.a
    num = (t * (x % p) + 2 * t * t + a) % p
    den = (x - t) % p
    if np.any(den == 0):
        raise RuntimeError("translate_x_by_two_torsion applied at x == t")
    return (num * EQD.modinv_arr(den, p)) % p


def _selfcheck_translate(cell, t: int, sample: int = 32) -> dict:
    """Check the closed form against actual point arithmetic on E(F_p)."""
    T = cell.curve.lift_x(int(t))
    checked = ok = 0
    for x in cell.X_E[:sample].tolist():
        if int(x) == int(t):
            continue
        P = cell.curve.lift_x(int(x))
        if P is None or T is None:
            continue
        S = cell.curve.add(P, T)
        if S is None:
            continue
        checked += 1
        got = int(translate_x_by_two_torsion(
            np.array([int(x)], dtype=np.int64), t, cell)[0])
        ok += int(got == S[0] % cell.p)
    return {"two_torsion_x": int(t), "checked": checked, "agreed": ok,
            "closed_form_verified": bool(checked > 0 and checked == ok)}


def duplicate_decomposition(cell, xs: np.ndarray, e1: np.ndarray,
                            e2: np.ndarray, label: str) -> dict:
    """DIAG-DEP-DUP on one factor base. MACHINE-READABLE FIELDS.

    Colliding invariant pairs are counted as sum_v C(multiplicity(v), 2), the
    same reading STAT-DUP uses. A collision between half-tuples {i, j} and
    {k, l} is TRANSLATE-EXPLAINED when there is a nontrivial 2-torsion point T
    with {x(P_i + T), x(P_j + T)} == {x_k, x_l}: translating BOTH points by T
    fixes both P + Q and P - Q, hence fixes (e_1, e_2) exactly.

    dup_residual is PRE-REGISTERED AT ZERO. It is an INTEGRITY TELL and not a
    decision variable.
    """
    p = cell.p
    torsion = two_torsion_x_coordinates(cell)
    selfchecks = [_selfcheck_translate(cell, t) for t in torsion]
    index_of_x = {int(v): i for i, v in enumerate(xs.tolist())}

    key = e1.astype(np.int64) * p + e2.astype(np.int64)
    order = np.argsort(key, kind="stable")
    ks = key[order]
    groups: list[np.ndarray] = []
    start = 0
    for i in range(1, ks.size + 1):
        if i == ks.size or ks[i] != ks[start]:
            if i - start > 1:
                groups.append(order[start:i])
            start = i

    # Precompute the translate image of every factor-base x under each torsion
    # point, as factor-base indices (or -1 when the image leaves the base).
    images: dict[int, np.ndarray] = {}
    for t in torsion:
        img = np.full(xs.size, -1, dtype=np.int64)
        mask = xs != t
        tx = translate_x_by_two_torsion(xs[mask], t, cell)
        vals = [index_of_x.get(int(v), -1) for v in tx.tolist()]
        img[np.nonzero(mask)[0]] = np.array(vals, dtype=np.int64)
        images[t] = img

    iu, ju = cell.iu, cell.ju
    total_pairs = 0
    explained = 0
    for g in groups:
        m = g.size
        total_pairs += m * (m - 1) // 2
        halves = [(int(iu[h]), int(ju[h])) for h in g.tolist()]
        pos = {hp: idx for idx, hp in enumerate(halves)}
        seen: set[tuple[int, int]] = set()
        for idx_a, (i, j) in enumerate(halves):
            for t in torsion:
                ii, jj = int(images[t][i]), int(images[t][j])
                if ii < 0 or jj < 0:
                    continue
                cand = (min(ii, jj), max(ii, jj))
                idx_b = pos.get(cand)
                if idx_b is None or idx_b == idx_a:
                    continue
                seen.add((min(idx_a, idx_b), max(idx_a, idx_b)))
        explained += len(seen)

    # Orbit decomposition of the factor base under the 2-torsion translations.
    closed = set()
    for t in torsion:
        img = images[t]
        for i in range(xs.size):
            if img[i] >= 0:
                closed.add(i)
                closed.add(int(img[i]))
    parent = list(range(xs.size))

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    for t in torsion:
        img = images[t]
        for i in range(xs.size):
            if img[i] >= 0:
                ra, rb = find(i), find(int(img[i]))
                if ra != rb:
                    parent[ra] = rb
    orbit_sizes: dict[int, int] = {}
    for i in sorted(closed):
        orbit_sizes[find(i)] = orbit_sizes.get(find(i), 0) + 1
    full_orbit_size = len(torsion) + 1
    free_orbits = sum(1 for s in orbit_sizes.values() if s == full_orbit_size)
    closed_arr = np.zeros(xs.size, dtype=bool)
    for i in closed:
        closed_arr[i] = True
    internal = int(np.count_nonzero(closed_arr[iu] & closed_arr[ju]))

    return {
        "object": label,
        "field_bits": cell.bits,
        "n_half_tuples": int(e1.size),
        "dup_colliding_pairs_total": int(total_pairs),
        "dup_translate_explained": int(explained),
        "dup_residual": int(total_pairs - explained),
        "dup_residual_pre_registered_value": 0,
        "dup_orbit_decomposition": {
            "two_torsion_x_coordinates": torsion,
            "two_torsion_group_order": full_orbit_size,
            "translate_closed_subset_size": int(len(closed)),
            "free_orbit_count": int(free_orbits),
            "orbit_size_histogram": {str(k): int(v) for k, v in sorted(
                {s: sum(1 for z in orbit_sizes.values() if z == s)
                 for s in set(orbit_sizes.values())}.items())},
            "internal_half_tuple_count": internal,
        },
        "closed_form_selfchecks": selfchecks,
        "note": "PRE-REGISTERED INTEGRITY TELL, NOT A DECISION VARIABLE. It "
                "enters no branch except through D-0's general integrity leg. "
                "NO STATISTIC OF OBJ-REAL AGAINST ANY NULL IS COMPUTED.",
    }


def run_duplicate_decomposition(cell, n_fresh_nulls: int, deadline: float) -> dict:
    """DIAG-DEP-DUP on OBJ-REAL and on `n_fresh_nulls` fresh OBJ-NULL-RFB draws
    at one cell. MEASUREMENT STAGE ONLY; this is the ONLY function that reaches
    the deterministic factor base, and it computes NO statistic of OBJ-REAL
    against any null."""
    if time.time() > deadline:
        raise TimeoutError("wall-clock budget exhausted before DIAG-DEP-DUP")
    integrity = {"degenerate_draw_count": 0, "null_redraw_count_total": 0,
                 "null_redraw_counts": [], "range_violations": 0}
    fb = dep_deterministic_factor_base(cell)
    e1r, e2r, degen = cell.enumerate_factor_base(fb["xs"])
    if degen:
        raise RuntimeError(f"INTEGRITY FAILURE: {degen} c_2 == 0 draws on OBJ-REAL")
    real = duplicate_decomposition(cell, fb["xs"], e1r, e2r, "OBJ-REAL")
    real["factor_base_sha256"] = fb["factor_base_sha256"]
    nulls = []
    dup_stream = make_stream("calibration_null", cell.bits)
    for k in range(n_fresh_nulls):
        e1n, e2n, dn = draw_null_arm(cell, dup_stream, 100000 + k, integrity)
        row = duplicate_decomposition(cell, dn["xs"], e1n, e2n, "OBJ-NULL-RFB")
        row["draw_index"] = k
        row["x_list_sha256"] = dn["x_list_sha256"]
        nulls.append(row)
    return {"cell": cell.descriptor(), "OBJ_REAL": real,
            "OBJ_NULL_RFB_draws": nulls, "n_fresh_nulls": n_fresh_nulls,
            "integrity": integrity}


# --------------------------------------------------------------------------
# MEASUREMENT ARM. AUTHORED COMPLETE HERE AND NOT INVOKED AT TASK-20260801-035.
# --------------------------------------------------------------------------
def load_reading_rule(path: str) -> dict:
    """The frozen RR-DEP-1, frozen at TASK-20260801-038 in
    experiments/EXP-DEP-001/reading_rule.yaml. This driver READS it; it never
    contains it, and it never lets it move a threshold.

    REQUIRED SHAPE (documented in implementation.md so the freezing task knows
    the exact schema this file will accept):

      reading_rule:
        id: RR-DEP-1
        primary_threshold_source: <the archived EXP-EQD-001 artifact path>
        thresholds:                     # OPTIONAL. If present it is CHECKED
          16: {STAT-CHI-16: <float>, ...}   # for exact equality against the
          20: {...}                         # recomputed archived values, and a
                                            # mismatch ABORTS the run.
        ...

    The PRIMARY thresholds this driver applies are ALWAYS the recomputed
    archived EXP-EQD-001 199th order statistics, per THR-DEP-1. A reading rule
    cannot substitute a different number; it can only disagree, and a
    disagreement is an integrity failure.
    """
    import yaml
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    rr = doc.get("reading_rule") if isinstance(doc, dict) else None
    if not isinstance(rr, dict):
        raise ValueError(f"{path} has no top-level 'reading_rule' mapping")
    return rr


def check_reading_rule_thresholds(rr: dict, repro: dict) -> dict:
    """If RR-DEP-1 states thresholds, they MUST equal the recomputed archived
    values exactly. CTRL-DEP-DRIVER-HASH's sibling guard against a tuning route
    through the reading rule."""
    stated = rr.get("thresholds")
    if stated is None:
        return {"reading_rule_states_thresholds": False, "agrees": None}
    rows = []
    agree = True
    for bits in FIELD_BITS:
        block = stated.get(bits, stated.get(str(bits), {})) or {}
        thr = threshold_vector(repro, bits)
        for sid in STATISTIC_IDS:
            if sid in block:
                same = bool(float(block[sid]) == float(thr[sid]))
                agree = agree and same
                rows.append({"field_bits": bits, "statistic": sid,
                             "reading_rule_value": float(block[sid]),
                             "archived_recomputed_value": thr[sid],
                             "equal": same})
    if not agree:
        raise RuntimeError(
            "RR-DEP-1 states a threshold that differs from the recomputed "
            "archived EXP-EQD-001 value. THR-DEP-1 forbids it; this is an "
            "integrity failure, never a datum.")
    return {"reading_rule_states_thresholds": True, "agrees": agree,
            "comparison": rows}


def run_measurement(cell, repro: dict, deadline: float) -> dict:
    """RUN-DEP-001-measure at one cell. NOT EXECUTED AT TASK-20260801-035.

    Runs all three ladders at R_REPS = 200 replicates per rung against the
    ARCHIVED thresholds, with CTRL-DEP-MARG and DIAG-DEP-RHO on every planted
    arm, and records DDV-1 .. DDV-5 and the DET-DEP-1 booleans. It selects NO
    branch and states NO disposition: branch selection belongs to RR-DEP-1 as
    applied by the Reviewer and the Coordinator.
    """
    p = cell.p
    thr = threshold_vector(repro, cell.bits)
    source_stream = make_stream("source_null_for_plants", cell.bits)
    copula_stream = make_stream("copula_noise", cell.bits)
    cell_stream = make_stream("cell_transfer", cell.bits)
    block_stream = make_stream("block_permutation", cell.bits)
    faith_stream = make_stream("faithfulness_sample", cell.bits)

    integrity = {"degenerate_draw_count": 0, "null_redraw_count_total": 0,
                 "null_redraw_counts": [], "range_violations": 0,
                 "arms_short_of_n": 0, "arms_recorded": 0}
    marg_records: list[dict] = []
    marg_mismatch_locations: list[dict] = []
    families: dict[str, dict] = {}
    max_dev_certs: dict[str, dict] = {}
    # The measurement stage uses its own draw offset on the shared source
    # stream so that it never re-consumes a calibration draw index.
    sk = 1000000

    def check_deadline(stage: str):
        if time.time() > deadline:
            raise TimeoutError(f"wall-clock budget exhausted during {stage}")

    def one_rung(family: str, rung, make_plant):
        nonlocal sk
        rows = []
        for rep in range(R_REPS):
            check_deadline(f"{family} rung={rung} replicate={rep}")
            e1s, e2s, _ = draw_null_arm(cell, source_stream, sk, integrity); sk += 1
            e2_planted, moved = make_plant(e1s, e2s, rep)
            e1p, e2p = plant_arm(e1s, e2_planted)
            # Archiving policy in the measurement stage: the count-by-count
            # comparison runs on the full histograms for EVERY arm without
            # exception; the full SOURCE histograms are archived for replicate
            # 0 of each rung and every other arm keeps the four sorted-marginal
            # digests, the source and plant histogram digests and the equality
            # booleans. Nothing about the mandatory check is skipped.
            m = marginal_integrity(e1s, e2s, e1p, e2p, p, family, rung, rep,
                                   full_histograms=(rep == 0))
            m["field_bits"] = cell.bits
            diag = induced_dependence(e1s, e2s, e1p, e2p, p)
            m["DIAG_DEP_RHO"] = diag
            marg_records.append(m)
            if not m["CTRL_DEP_MARG_ok"]:
                loc = {"family": family, "rung": rung, "replicate": rep,
                       "field_bits": cell.bits}
                marg_mismatch_locations.append(loc)
                raise RuntimeError(
                    "CTRL-DEP-MARG MISMATCH (INSTRUMENT FAILURE, NEVER A "
                    f"RESULT) at {loc}")
            e1n, e2n, _ = draw_null_arm(cell, source_stream, sk, integrity); sk += 1
            integrity["arms_recorded"] += 2
            if e1p.size != N_PER_ARM or e1n.size != N_PER_ARM:
                integrity["arms_short_of_n"] += 1
            vals = statistics_of((e1p, e2p), (e1n, e2n), p)
            rows.append({"replicate": rep, "records_moved": int(moved), **vals,
                         "rejects": rejects_against(vals, thr),
                         "spearman_source": diag["spearman_source"],
                         "spearman_plant": diag["spearman_plant"],
                         "joint_tv_distance_k16": diag["joint_tv_distance_k16"]})
        det = detection_summary(rows, thr)
        for sid in STATISTIC_IDS:
            det[sid]["DEP_detects_flag"] = bool(
                det[sid]["rate"] is not None
                and det[sid]["rate"] >= DET_RATE_MIN
                and det[sid]["ci95_lower_one_sided"] >= DET_LOWER_BOUND_MIN)
            det[sid]["certifying_under_CERT_DEP_1"] = sid in CERTIFYING_STATISTICS
        return {"rung": rung, "R_REPS": R_REPS, "replicates": rows,
                "detection": det,
                "mean_spearman_plant": float(np.mean(
                    [r["spearman_plant"] for r in rows])),
                "mean_joint_tv_distance_k16": float(np.mean(
                    [r["joint_tv_distance_k16"] for r in rows]))}

    _log(f"bits={cell.bits} DEP-LADDER-RHO: {len(LADDER_RHO)} rungs")
    families["DEP-LADDER-RHO"] = {
        "object": "OBJ-PLANT-DEP-rho", "alternative_class": "C1 (PRIMARY)",
        "rungs": {f"{rho}": one_rung(
            "OBJ-PLANT-DEP-rho", rho,
            lambda e1, e2, rep, rho=rho: (
                plant_copula(e1, e2, rho, copula_stream.generator(1000000 + rep)),
                e1.size))
            for rho in LADDER_RHO}}

    _log(f"bits={cell.bits} DEP-LADDER-CELL: {len(LADDER_CELL)} rungs")
    families["DEP-LADDER-CELL"] = {
        "object": "OBJ-PLANT-DEP-CELL-eps", "alternative_class": "C2",
        "rungs": {f"{eps}": one_rung(
            "OBJ-PLANT-DEP-CELL-eps", eps,
            lambda e1, e2, rep, eps=eps: (
                lambda t: (t[0], 2 * t[1]))(
                    plant_cell(e1, e2, eps, p, cell_stream.generator(rep))))
            for eps in LADDER_CELL}}

    _log(f"bits={cell.bits} DEP-LADDER-BLOCK: {len(LADDER_BLOCK)} rungs")
    families["DEP-LADDER-BLOCK"] = {
        "object": "OBJ-PLANT-DEP-BLOCK-q", "alternative_class": "C3",
        "rungs": {f"{q}": one_rung(
            "OBJ-PLANT-DEP-BLOCK-q", q,
            lambda e1, e2, rep, q=q: plant_block(
                e1, e2, q, block_stream.generator(rep)))
            for q in LADDER_BLOCK}}

    # DDV-4 and DDV-5: the smallest rung at which SOME CERTIFYING statistic
    # satisfies DET-DEP-1. The per-cell part; the BOTH-CELLS conjunction is
    # taken across cells by the caller.
    def floors(family_key, ladder):
        per = {}
        for rung in ladder:
            det = families[family_key]["rungs"][f"{rung}"]["detection"]
            per[f"{rung}"] = bool(any(det[sid]["DEP_detects_flag"]
                                      for sid in CERTIFYING_STATISTICS))
        return per

    out = {
        "cell": cell.descriptor(),
        "archived_thresholds_used": thr,
        "families": families,
        "per_cell_certifying_detects": {
            "DEP-LADDER-RHO": floors("DEP-LADDER-RHO", LADDER_RHO),
            "DEP-LADDER-CELL": floors("DEP-LADDER-CELL", LADDER_CELL),
            "DEP-LADDER-BLOCK": floors("DEP-LADDER-BLOCK", LADDER_BLOCK),
        },
        "marginal_integrity_records": marg_records,
        "marg_mismatch_locations": marg_mismatch_locations,
        "CTRL_DEP_MARG_all_ok": bool(all(m["CTRL_DEP_MARG_ok"] for m in marg_records)),
        "integrity": integrity,
        "stream_hashes": [s.hash_record() for s in
                          (source_stream, copula_stream, cell_stream,
                           block_stream, faith_stream)],
        "no_disposition_stated":
            "This driver records measured values, detection rates, confidence "
            "bounds and DET-DEP-1 booleans only. Branch selection under "
            "RR-DEP-1 is not performed here.",
    }

    # The maximal-deviation certificate, EMITTED UNDER EVERY OUTCOME.
    for fam_key, ladder in (("DEP-LADDER-RHO", LADDER_RHO),
                            ("DEP-LADDER-CELL", LADDER_CELL),
                            ("DEP-LADDER-BLOCK", LADDER_BLOCK)):
        top = families[fam_key]["rungs"][f"{ladder[-1]}"]
        r0 = top["replicates"][0]
        rec = next(m for m in marg_records
                   if m["family"] == families[fam_key]["object"]
                   and m["rung"] == ladder[-1] and m["replicate"] == 0)
        max_dev_certs[fam_key] = {
            "family": fam_key, "object": families[fam_key]["object"],
            "topmost_rung": ladder[-1], "replicate": 0,
            "field_bits": cell.bits,
            "marginal_digests": rec["digests"],
            "marginal_histograms_equal": rec["marginal_histograms_equal"],
            "measured_spearman_source": r0["spearman_source"],
            "measured_spearman_plant": r0["spearman_plant"],
            "joint_tv_distance_k16": r0["joint_tv_distance_k16"],
            "statistic_values": {sid: r0[sid] for sid in STATISTIC_IDS},
            "archived_thresholds": thr,
            "rejection_booleans": r0["rejects"],
            "rebuild_recipe": {
                "master_seed": MASTER_SEED,
                "source_null_stream_seed": MASTER_SEED
                    + STREAM_OFFSETS["source_null_for_plants"] + cell.bits,
                "copula_noise_stream_seed": MASTER_SEED
                    + STREAM_OFFSETS["copula_noise"] + cell.bits,
                "cell_transfer_stream_seed": MASTER_SEED
                    + STREAM_OFFSETS["cell_transfer"] + cell.bits,
                "block_permutation_stream_seed": MASTER_SEED
                    + STREAM_OFFSETS["block_permutation"] + cell.bits,
                "note": "Rebuild with this driver's plant functions from the "
                        "recorded stream seeds; every draw index is "
                        "individually addressable.",
            },
        }
    out["maximal_deviation_certificates"] = max_dev_certs

    # CTRL-DEP-S3 on a representative arm of this cell.
    e1s, e2s, ds = draw_null_arm(cell, source_stream, sk, integrity)
    out["CTRL-DEP-S3"] = ctrl_dep_s3(cell, ds["xs"], e1s, e2s,
                                     faith_stream.generator(1))
    return out


def emit_measurement_results(out_results: str, cells: dict, repro: dict,
                             dup: dict, rr_check: dict) -> None:
    """The five declared measurement result files."""
    scope = (
        "TOY TIER ONLY. ALT-CLASS-DEP-1 BINDS: measured power is against C1 "
        "(global monotone rank dependence, Gaussian-copula reordering), C2 "
        "(local joint-cell mass transfer) and C3 (coarse two-stratum block "
        "reordering), at the rungs measured and only those. U1 to U6 remain "
        "UNCERTIFIED, in particular U1 - a two-sample design is blind by "
        "construction to any deviation BOTH ARMS SHARE. No statement may "
        "describe this apparatus as having power against 'dependence' without "
        "naming which of C1, C2 or C3 it rests on and without carrying U1 to U6.")

    def per_cell_floor(family_key, ladder):
        for rung in ladder:
            if all(cells[str(b)]["per_cell_certifying_detects"][family_key][f"{rung}"]
                   for b in FIELD_BITS):
                return rung
        return NONE_ON_LADDER

    def artifact_tell_inputs(bits: str) -> dict:
        """The MEASURED INPUTS the D-1 artifact tell reads. Recorded as
        numbers; NO branch is selected and NO disposition is stated here."""
        fam = cells[bits]["families"]
        rho_means = [fam["DEP-LADDER-RHO"]["rungs"][f"{r}"]["mean_spearman_plant"]
                     for r in LADDER_RHO]
        cell_tv = [fam["DEP-LADDER-CELL"]["rungs"][f"{e}"]["mean_joint_tv_distance_k16"]
                   for e in LADDER_CELL]
        lo = fam["DEP-LADDER-RHO"]["rungs"][f"{LADDER_RHO[0]}"]["detection"]
        hi = fam["DEP-LADDER-RHO"]["rungs"][f"{LADDER_RHO[-1]}"]["detection"]
        return {
            "mean_spearman_plant_across_DEP_LADDER_RHO": rho_means,
            "spearman_monotone_nondecreasing_in_rho": bool(
                all(rho_means[i] <= rho_means[i + 1]
                    for i in range(len(rho_means) - 1))),
            "mean_joint_tv_k16_across_DEP_LADDER_CELL": cell_tv,
            "joint_tv_monotone_nondecreasing_in_eps": bool(
                all(cell_tv[i] <= cell_tv[i + 1] for i in range(len(cell_tv) - 1))),
            "one_sided_two_proportion_z_lowest_rung_over_topmost_rung": {
                sid: two_proportion_one_sided_z(
                    lo[sid]["n_exceeding"], lo[sid]["n_replicates"],
                    hi[sid]["n_exceeding"], hi[sid]["n_replicates"])
                for sid in STATISTIC_IDS},
        }

    rho_det = per_cell_floor("DEP-LADDER-RHO", LADDER_RHO)
    eps_det = per_cell_floor("DEP-LADDER-CELL", LADDER_CELL)
    q_det = per_cell_floor("DEP-LADDER-BLOCK", LADDER_BLOCK)

    report = {"schema": "dep001_measurement_report/v1",
              "scope_and_alternative_class": scope,
              "claim_tier": "toy",
              "no_disposition_stated": "No branch of RR-DEP-1 is selected here "
                                       "and no disposition is stated.",
              "archived_threshold_reproduction": repro,
              "reading_rule_threshold_check": rr_check,
              "DDV_4_rho_det": rho_det,
              "DDV_5_eps_det": eps_det,
              "block_family_floor_non_decisional": q_det,
              "rho_star_frozen": RHO_STAR, "eps_star_frozen": EPS_STAR,
              "eps_det_over_EV_EQD_001_delta_floor": (
                  eps_det / 0.02 if isinstance(eps_det, float) else None),
              "detection_bar_DET_DEP_1": {
                  "rate_at_least": DET_RATE_MIN,
                  "one_sided_95_lower_bound_at_least": DET_LOWER_BOUND_MIN},
              "certifying_statistics_CERT_DEP_1": list(CERTIFYING_STATISTICS),
              "diagnostic_only_statistic": "STAT-KS1-E2",
              "cells": {b: {"cell": c["cell"],
                            "archived_thresholds_used": c["archived_thresholds_used"],
                            "per_cell_certifying_detects": c["per_cell_certifying_detects"],
                            "artifact_tell_inputs_DIAG_DEP_RHO": artifact_tell_inputs(b),
                            "CTRL_DEP_MARG_all_ok": c["CTRL_DEP_MARG_all_ok"],
                            "marg_mismatch_locations": c["marg_mismatch_locations"],
                            "marginal_integrity_records": c["marginal_integrity_records"],
                            "stream_hashes": c["stream_hashes"],
                            "CTRL-DEP-S3": c["CTRL-DEP-S3"],
                            "integrity": c["integrity"]}
                        for b, c in cells.items()}}
    EQD.write_json(os.path.join(out_results, "DEP_report.json"), report)

    curve = {"schema": "dep001_dependence_power_curve/v1",
             "scope_and_alternative_class": scope,
             "ladders": {"DEP-LADDER-RHO": list(LADDER_RHO),
                         "DEP-LADDER-CELL": list(LADDER_CELL),
                         "DEP-LADDER-BLOCK": list(LADDER_BLOCK)},
             "cells": {b: c["families"] for b, c in cells.items()}}
    EQD.write_json(os.path.join(out_results, "dependence_power_curve.json"), curve)

    floor_cert = {"schema": "dep001_detection_floor_certificate/v1",
                  "scope_and_alternative_class": scope,
                  "DDV_4_rho_det": rho_det, "DDV_5_eps_det": eps_det,
                  "definition": "The SMALLEST rung at which SOME CERT-DEP-1 "
                                "certifying statistic satisfies DET-DEP-1 at "
                                "BOTH cells, or the literal NONE_ON_LADDER.",
                  "per_cell_certifying_detects": {
                      b: c["per_cell_certifying_detects"] for b, c in cells.items()}}
    EQD.write_json(os.path.join(out_results, "detection_floor_certificate.json"),
                   floor_cert)

    maxdev = {"schema": "dep001_maximal_deviation_certificate/v1",
              "scope_and_alternative_class": scope,
              "emitted_under_every_outcome": True,
              "cells": {b: c["maximal_deviation_certificates"]
                        for b, c in cells.items()}}
    EQD.write_json(os.path.join(out_results, "maximal_deviation_certificate.json"),
                   maxdev)

    dupdoc = {"schema": "dep001_duplicate_decomposition/v1",
              "diagnostic": "DIAG-DEP-DUP, NON-DECISIONAL",
              "pre_registered_integrity_tell": "dup_residual is PRE-REGISTERED "
                                               "AT ZERO.",
              "no_statistic_of_OBJ_REAL_against_any_null_is_computed": True,
              "cells": dup}
    EQD.write_json(os.path.join(out_results, "duplicate_decomposition.json"), dupdoc)


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


def main(argv=None) -> int:
    global EQD
    ap = argparse.ArgumentParser(description="EXP-DEP-001 driver")
    ap.add_argument("--mode", choices=["calib", "measure"], required=True)
    ap.add_argument("--out-run", required=True)
    ap.add_argument("--out-results", required=True)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--wall-clock-seconds", type=float, default=1800.0)
    ap.add_argument("--dup-null-draws", type=int, default=3,
                    help="measure mode only: fresh OBJ-NULL-RFB draws per cell "
                         "for the DIAG-DEP-DUP decomposition")
    ap.add_argument("--reading-rule", default=None,
                    help="measure mode only: the frozen RR-DEP-1")
    ap.add_argument("--approval-receipt", default=None,
                    help="measure mode only: the TASK-20260801-041 snapshot receipt")
    ap.add_argument("--resolved-model-id", default=None)
    ap.add_argument("--requested-policy", default="executor-implementation")
    args = ap.parse_args(argv)

    run_id = args.run_id or (
        "RUN-DEP-001-calib" if args.mode == "calib" else "RUN-DEP-001-measure")
    started = time.time()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    deadline = started + args.wall_clock_seconds

    _log(f"EXP-DEP-001 driver, mode={args.mode}, run_id={run_id}")
    _log(f"spec sha256 at freeze: {SPEC_SHA256_AT_FREEZE}")

    status = "completed_valid"
    invalid_reason = None
    failure_class = None
    payload: dict = {}
    driver_sha = sha256_file(os.path.abspath(__file__))
    _log(f"driver sha256: {driver_sha}")
    eqd_tree = {"unmodified": None}
    selfchecks: dict = {}
    streams_doc: dict = {}

    try:
        if os.path.exists(SPEC_PATH):
            live = sha256_file(SPEC_PATH)
            _log(f"spec sha256 on disk:    {live}  match={live == SPEC_SHA256_AT_FREEZE}")
            if live != SPEC_SHA256_AT_FREEZE:
                raise ValueError(
                    "the hash-bound specification has changed on disk; the "
                    "contract is not the one this driver was authored against")
        EQD = load_eqd_module()
        _log("CTRL-DEP-EQDHASH verified: EXP-EQD-001 driver and archived "
             "null-replicate array both match the contract hashes")
        eqd_tree = eqd_tree_unmodified()

        # Startup self-checks. Dependency-free implementations only.
        cp = selfcheck_clopper_pearson()
        if not cp["selfcheck_passed"]:
            raise RuntimeError("Clopper-Pearson self-check failed")
        probe = np.array([5, 1, 1, 3, 9, 3, 3], dtype=np.int64)
        if not np.allclose(average_ranks(probe), _average_ranks_fast(probe)):
            raise RuntimeError("average-rank self-check failed")
        selfchecks = {"clopper_pearson": cp,
                      "average_rank_vectorisation_agrees": True}

        streams_doc = stream_disjointness_record()
        if not streams_doc["all_disjoint_from_archived_EQD_streams"]:
            raise RuntimeError(
                "a declared stream seed collides with an archived EXP-EQD-001 "
                "stream; this is an integrity failure")

        repro = archived_thresholds()
        _log(f"DEP-CAL-B: archived thresholds reproduced exactly = "
             f"{repro['all_reproduced_exactly']}")

        if args.mode == "measure":
            # ATS-DEP-1: the measurement arm is gated. THIS BRANCH IS NOT TAKEN
            # AT TASK-20260801-035 and refuses to run without BOTH gates.
            if not args.approval_receipt or not os.path.exists(args.approval_receipt):
                raise PermissionError(
                    "measure mode requires --approval-receipt pointing at the "
                    "TASK-20260801-041 snapshot receipt")
            with open(args.approval_receipt) as fh:
                receipt = json.load(fh)
            if receipt.get("APPROVAL_DETERMINATION") != "APPROVED":
                raise PermissionError(
                    "APPROVAL_DETERMINATION is not APPROVED; the measurement "
                    "arm is not authorized")
            if not args.reading_rule or not os.path.exists(args.reading_rule):
                raise PermissionError(
                    "measure mode requires the frozen reading rule RR-DEP-1 "
                    "from TASK-20260801-038")
            rr = load_reading_rule(args.reading_rule)
            rr_check = check_reading_rule_thresholds(rr, repro)
            cells = {}
            dup = {}
            for bits in FIELD_BITS:
                cell = EQD.Cell(bits)
                cells[str(bits)] = run_measurement(cell, repro, deadline)
                dup[str(bits)] = run_duplicate_decomposition(
                    cell, args.dup_null_draws, deadline)
            emit_measurement_results(args.out_results, cells, repro, dup, rr_check)
            # The run package's payload carries the SUMMARY; the full
            # per-replicate rows live in dependence_power_curve.json and the
            # full CTRL-DEP-MARG records in DEP_report.json, both declared
            # artifacts. Nothing measured is discarded.
            slim = {}
            for b, c in cells.items():
                fams = {}
                for fk, fv in c["families"].items():
                    fams[fk] = {
                        "object": fv["object"],
                        "alternative_class": fv["alternative_class"],
                        "rungs": {rk: {k: v for k, v in rv.items()
                                       if k != "replicates"}
                                  for rk, rv in fv["rungs"].items()}}
                slim[b] = {k: v for k, v in c.items()
                           if k not in ("families", "marginal_integrity_records")}
                slim[b]["families_summary"] = fams
            payload = {"mode": "measure", "cells": slim,
                       "duplicate_decomposition": dup,
                       "reading_rule_path": args.reading_rule,
                       "reading_rule_sha256": sha256_file(args.reading_rule),
                       "reading_rule_threshold_check": rr_check,
                       "approval_receipt_path": args.approval_receipt,
                       "approval_receipt_sha256": sha256_file(args.approval_receipt),
                       "calibration_saw_real_object": False,
                       "measurement_touched_real_object_for_DIAG_DEP_DUP_only":
                           _REAL_OBJECT_TOUCHED}
        else:
            cells = {}
            for bits in FIELD_BITS:
                _log(f"building cell bits={bits}")
                cell = EQD.Cell(bits)
                _log(f"  p={cell.p} a={cell.a} b={cell.b} #E={cell.curve_order} "
                     f"|X_E|={cell.x_set_size}")
                cells[str(bits)] = run_calibration(cell, repro, deadline)
            if _REAL_OBJECT_TOUCHED or EQD._REAL_DATA_TOUCHED:
                raise RuntimeError(
                    "ATS-DEP-1.3 VIOLATION: the deterministic factor base was "
                    "touched during a calibration run")
            payload = {
                "mode": "calib",
                "cells": cells,
                "archived_threshold_reproduction": repro,
                "calibration_saw_real_object": bool(_REAL_OBJECT_TOUCHED
                                                    or EQD._REAL_DATA_TOUCHED),
                "ladder_rungs_executed": [],
                "duplicate_decomposition_emitted": False,
                "non_evidential_declaration":
                    "RUN-DEP-001-calib is EXPRESSLY NON-EVIDENTIAL about "
                    "H-DEP-001, H-EQD-001, H-SMTH-001 and HEUR-DS-1 in either "
                    "direction. It measures the instrument on null and "
                    "plant-machinery objects, not any object of study.",
            }
            emit_calibration_results(args.out_results, cells, repro)
    except TimeoutError as exc:
        status = "cancelled_by_budget"
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
        "claim_tier": "toy",
        "spec_sha256_at_freeze": SPEC_SHA256_AT_FREEZE,
        "spec_sha256_on_disk": sha256_file(SPEC_PATH) if os.path.exists(SPEC_PATH) else None,
        "driver_sha256": driver_sha,
        "eqd_driver_sha256": eqd_tree.get("eqd_driver_sha256"),
        "eqd_null_replicate_array_sha256": eqd_tree.get("eqd_null_stats_sha256"),
        "eqd_tree_unmodified": eqd_tree.get("unmodified"),
        "eqd_tree_porcelain": eqd_tree.get("porcelain"),
        "selfchecks": selfchecks,
        "streams": streams_doc,
        "frozen_parameters": {
            "master_seed": MASTER_SEED, "field_bits": list(FIELD_BITS),
            "Bfb": BFB, "n_per_arm": N_PER_ARM,
            "resolution_ladder_K": list(RESOLUTION_LADDER_K),
            "DEP-LADDER-RHO": list(LADDER_RHO),
            "DEP-LADDER-CELL": list(LADDER_CELL),
            "DEP-LADDER-BLOCK": list(LADDER_BLOCK),
            "R_REPS": R_REPS, "R_ANCHOR_REPS": R_ANCHOR_REPS,
            "M_PAIRS": M_PAIRS, "IDENT_REPS": IDENT_REPS,
            "rho_star": RHO_STAR, "eps_star": EPS_STAR,
            "DET_DEP_1": {"rate_at_least": DET_RATE_MIN,
                          "one_sided_95_lower_bound_at_least": DET_LOWER_BOUND_MIN},
            "CERT_DEP_1_certifying_statistics": list(CERTIFYING_STATISTICS),
            "stream_offsets": STREAM_OFFSETS,
        },
        "timing": {"started_at": started_at, "finished_at": finished_at,
                   "wall_seconds": finished - started},
        "resources": {"peak_rss_bytes": int(peak_rss),
                      "cpu_seconds": ru.ru_utime + ru.ru_stime},
        "payload": payload,
        "no_threshold_frozen": True,
        "no_reading_rule_applied": True,
        "no_branch_selected": True,
        "interpretation": "NONE",
    }
    EQD_write_json = EQD.write_json if EQD is not None else _fallback_write_json
    EQD_write_json(os.path.join(args.out_run, "raw-result.json"), raw)

    env = (EQD.environment_block() if EQD is not None else {})
    EQD_write_json(os.path.join(args.out_run, "environment.json"), env)

    git = git_state()
    manifest = {"run": {
        "id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "status": status,
        "claim_tier": "toy",
        "code": {
            "commit": git["commit"], "branch": git["branch"], "dirty": git["dirty"],
            "command": " ".join(
                [sys.executable.split("/")[-1],
                 os.path.relpath(os.path.abspath(__file__))]
                + (list(argv) if argv else sys.argv[1:])),
            "driver_sha256": driver_sha,
            "eqd_driver_sha256": raw["eqd_driver_sha256"],
            "eqd_null_replicate_array_sha256": raw["eqd_null_replicate_array_sha256"],
            "eqd_tree_unmodified": raw["eqd_tree_unmodified"],
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
            "stream_seeds": streams_doc.get("streams", []),
            "parameters": {
                "experiment_id": EXPERIMENT_ID,
                "mode": args.mode,
                "field_bits": max(FIELD_BITS),
                "field_bits_semantics":
                    "scalar maximum field bit size exercised, for the tier "
                    "check in tools/validate_ledger.py; both 16 and 20 were run",
                "field_bits_tested": list(FIELD_BITS),
                "Bfb": BFB,
                "n_per_arm": N_PER_ARM,
                "R_REPS": R_REPS,
                "R_ANCHOR_REPS": R_ANCHOR_REPS,
                "M_PAIRS": M_PAIRS,
            },
        },
        "timing": raw["timing"],
        "resources": raw["resources"],
        "result": {
            "valid": status == "completed_valid",
            "invalid_reason": invalid_reason,
            "certificate": {"kind": "none", "verified": True, "verifier": None},
            "certificate_note":
                "Pure measurement run. No discrete logarithm is computed and no "
                "factor-base relation is claimed, so there is nothing to certify.",
            "interpretation": "NONE",
        },
    }}
    os.makedirs(args.out_run, exist_ok=True)
    with open(os.path.join(args.out_run, "manifest.yaml"), "w") as fh:
        if EQD is not None:
            fh.write(EQD.yaml_dump(manifest) + "\n")
        else:                                              # pragma: no cover
            fh.write(json.dumps(manifest, indent=2) + "\n")

    _log(f"status={status} wall_seconds={finished - started:.1f} "
         f"peak_rss_bytes={int(peak_rss)}")
    return 0 if status == "completed_valid" else 1


def _fallback_write_json(path: str, obj) -> None:               # pragma: no cover
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=False)
        fh.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
