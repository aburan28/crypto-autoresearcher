"""The G3 ceiling-feasibility predicate of the v2-to-v3 amendment, Section 3.

Contract: experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml, `g3_predicate`.
This module implements that section and nothing else.  Every public function
below is named after, and carries in its docstring, the amendment clause it
implements, so the clause-by-clause audit can be read straight down the file.

REUSE, NOT FORK.  The walk map, the DP predicate, the exact-basin closure, the
pool procedure and BOTH selection code paths are taken from
experiments/EXP-ECDLP-612fb1/source_v2/instrument.py, imported UNCHANGED.
Nothing in source_v2/ is modified, copied or re-implemented here.

*** THE SELECTION INVARIANT ***
The amendment makes it an explicit invalidation rule that reading TRUE BASIN
SIZE anywhere in the SELECTION path is invalid ("Exact basin sizes are used to
SCORE a selection, never to MAKE one" -- `selection`, and `invalidation_rules`
last entry).  This file is laid out in four separated regions to make that
mechanically checkable:

    REGION A -- EXACT BASINS AND THE ORACLE CEILING   (holds basin arrays)
    REGION B -- THE POOL                              (evidence only)
    REGION C -- SELECTION                             (evidence only)
    REGION D -- SCORING AND THE PREDICATE             (basins meet a chosen set)

No function in REGION B or REGION C takes an `instrument.Basins`, a basin-size
array, or any array of length N as a parameter, holds one in a closure, or
constructs one.  Their only array inputs are the pool's own (S_d, h_d)
evidence, the pool's DP values, and the tie-break keys -- all of length r*T.
`_assert_evidence_only` enforces the length part of that at run time.

Observations only.  Nothing here solves a logarithm; certificate kind is
`none` for every run built on this module.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# --- the FROZEN v2 instrument, imported unchanged ---------------------------
_SOURCE_V3_DIR = os.path.dirname(os.path.abspath(__file__))
_EXP_DIR = os.path.dirname(_SOURCE_V3_DIR)
_SOURCE_V2_DIR = os.path.join(_EXP_DIR, "source_v2")
if _SOURCE_V2_DIR not in sys.path:
    sys.path.insert(0, _SOURCE_V2_DIR)
import instrument as I  # noqa: E402  (frozen v2 module; never edited)


# ===========================================================================
# Section 3 `parameters` and `exact_parameter_table_for_this_item`
# ===========================================================================

SEED_SET: Tuple[int, ...] = (1, 2, 3, 4, 5)
G3_PASS_THRESHOLD = 4          # v2's frozen ">= 4 of 5 seeds" rule, reused verbatim
A_GRID: Tuple[float, ...] = (0.0625, 0.125, 0.1875, 0.25)
R_GRID: Tuple[int, ...] = (2, 4, 8)


def make_params(n_bits: int, a: float, seed: int) -> I.Params:
    """Section 3 `parameters`.

    T is the FROZEN table size (I.T_OF_NBITS: 64 at n=20, 256 at n=24), and
    W = sqrt(a*N/T) real-valued, theta = 1/W, cap = ceil(8*W) come from the
    frozen v2 Params constructor.  The amendment says "Use the frozen values;
    do not recompute a rounding" -- so no rounding is recomputed here.

    Params also fixes the seed streams of v2's frozen seed_policy, which this
    item reuses unchanged: walk key s, precomputation restart stream s,
    tie-break stream 400 + s, NULL_A relabelling stream 300 + s.
    """
    return I.Params(n_bits=n_bits, a=a, seed=seed)


def t_sel_of(T: int) -> int:
    """Section 3 `parameters`.T_sel -- THIS ITEM USES T_sel = floor(T/2)."""
    return T // 2


def parameter_row(P: I.Params) -> dict:
    """The MODELED parameter row for a cell: W, theta, cap (Section 3's table).

    These are the only MODELED quantities in the measurement runs; every count,
    coverage, margin and bit count reported elsewhere is MEASURED.
    """
    return {"N": P.N, "n_bits": P.n_bits, "T": P.T, "T_sel": t_sel_of(P.T),
            "a": P.a, "W": P.W, "theta": P.theta, "cap": P.cap}


# ===========================================================================
# REGION A -- EXACT BASINS AND THE ORACLE CEILING
#
# Section 3 `reading_P1_frozen_instrument`, `basins`, `top_share`.
# ===========================================================================

def exact_basins(P: I.Params) -> I.Basins:
    """Section 3 `basins`, under `reading_P1_frozen_instrument`.

    Delegates to the FROZEN v2 closure I.exact_basins, which implements
    exactly the amendment's text: f(x) = mix64(x XOR K) AND (N-1);
    D(x) = 1 iff mix64(x XOR K_dp) < floor(2^64 / W); basin(d) counts the x
    whose first DP is d with dist(x) <= cap; points on DP-free cycles are
    UNREACHABLE and points with dist(x) > cap are CAPPED, and neither belongs
    to any basin.  Every basin count is exact; nothing is sampled.
    """
    return I.exact_basins(P)


def top_share(basins: I.Basins, t: int) -> float:
    """Section 3 `top_share`.

    TopShare(t) = (sum of the t LARGEST basin(d)) / N.  The ORACLE ceiling:
    unreachable by any real selection rule, which is why it is the ceiling in
    G3.  Ties among equal basin sizes do not affect the sum, so no tie-break
    enters this quantity.
    """
    return basins.top_share(t)


def basin_structure(basins: I.Basins) -> dict:
    """Exact basin-size histogram plus cycle and capped mass (metrics,
    `secondary`: "exact basin-size histogram per (N, a, seed); cycle mass and
    capped mass as fractions of N").  MEASURED."""
    sizes = np.asarray(basins.size, dtype=np.int64)
    counts = np.bincount(sizes)
    nz = np.flatnonzero(counts)
    return {
        "dp_count": int(len(basins.dps)),
        "histogram": {str(int(s)): int(counts[s]) for s in nz},
        "basin_size_max": int(sizes.max()) if sizes.size else 0,
        "basin_mass_total": int(sizes.sum()),
        "cycle_mass": int(basins.cycle_mass),
        "capped_mass": int(basins.capped_mass),
        "cycle_mass_fraction_of_N": basins.cycle_mass / basins.N,
        "capped_mass_fraction_of_N": basins.capped_mass / basins.N,
    }


# ===========================================================================
# REGION B -- THE POOL (EVIDENCE ONLY; NO BASIN ARRAY IN SCOPE)
#
# Section 3 `pool`.
# ===========================================================================

@dataclass
class PoolEvidence:
    """The pool as the amendment defines it: r*T DISTINCT DPs, each carrying
    (S_d, h_d), plus the generation cost counters.

    THIS OBJECT IS THE ENTIRE INPUT TO THE SELECTION PATH.  It deliberately
    carries no basin sizes, no basin object and no array of length N -- the
    selection code cannot read a true basin size because none is reachable
    from here.
    """
    r: int
    T: int
    dps: np.ndarray            # int64, the r*T distinct pool DPs
    S: np.ndarray              # float64, summed generating-walk length at each DP
    h: np.ndarray              # int64, hit count at each DP
    walks: int                 # generating walks consumed (all charged to P)
    P_cost: int                # group operations, capped walks charged at `cap`
    capped_walks: int

    def size(self) -> int:
        return int(len(self.dps))


def _assert_evidence_only(ev: PoolEvidence) -> None:
    """Run-time guard for the selection invariant.

    Checks that the object entering the selection path is a PoolEvidence whose
    arrays all have the pool's own length r*T -- i.e. that nothing of length N
    (a basin-size array is indexed by DP over the whole space, and a first_dp
    or dist array has length N) has been smuggled in.  Cheap, and it fails
    loudly rather than silently producing an oracle selection.
    """
    if not isinstance(ev, PoolEvidence):
        raise TypeError("selection path accepts PoolEvidence only")
    n = len(ev.dps)
    if n != ev.r * ev.T:
        raise ValueError(f"pool holds {n} DPs, expected r*T = {ev.r * ev.T}")
    if len(ev.S) != n or len(ev.h) != n:
        raise ValueError("pool evidence arrays disagree in length with the pool")


def build_pool(P: I.Params, r: int) -> PoolEvidence:
    """Section 3 `pool` -- the Bernstein-Lange precomputation pool at ratio r.

    Delegates to the FROZEN v2 I.generate_pools, which implements exactly the
    amendment's text: independent uniform starts from a deterministic stream
    seeded by s; each start walked to its first DP or the cap; a CAPPED walk
    is a MISS charged `cap` group operations to P and contributing nothing;
    a walk ending at DP d with length L credits S_d += L and h_d += 1;
    generation STOPS AT THE FIRST MOMENT the pool holds exactly r*T DISTINCT
    DPs; every generating walk, hit or miss, is charged to P.

    Called with the single-ratio list [r], exactly as the frozen v2 STAGE 0
    a-scan (source_v2/run_ascan.py) calls it, so that STAGE 3A reproduces that
    scan's pool draw rather than merely one of the same law.
    """
    snap = I.generate_pools(P, [r])[r * P.T]
    return PoolEvidence(
        r=r, T=P.T,
        dps=np.asarray(snap.dps, dtype=np.int64),
        S=np.asarray(snap.S, dtype=np.float64),
        h=np.asarray(snap.h, dtype=np.int64),
        walks=int(snap.walks), P_cost=int(snap.P_cost),
        capped_walks=int(snap.capped_walks),
    )


def pool_statistics(ev: PoolEvidence, P: I.Params) -> dict:
    """Metrics `secondary`: "pool statistics per (N, a, r, seed): generating
    walks, capped-walk fraction, P in group operations, P / sqrt(N*T)".
    All MEASURED counts."""
    return {
        "pool_size_distinct_dps": ev.size(),
        "generating_walks": ev.walks,
        "capped_walks": ev.capped_walks,
        "capped_walk_fraction": (ev.capped_walks / ev.walks) if ev.walks else None,
        "P_group_ops": ev.P_cost,
        "P_over_sqrt_NT": ev.P_cost / math.sqrt(P.N * P.T),
    }


# ===========================================================================
# REGION C -- SELECTION (EVIDENCE ONLY; NO BASIN ARRAY IN SCOPE)
#
# Section 3 `selection` -- the formula EXP-ECDLP-6ac801 did not state, plus
# the NULL_A_G3 relabelling and the NULL_B_G3 second code path.
# ===========================================================================

def selection_weight(ev: PoolEvidence, W: float) -> np.ndarray:
    """Section 3 `selection` -- THE PUBLISHED BERNSTEIN-LANGE WEIGHT

            w(d) = S_d + 4 * W * h_d

    computed from POOL EVIDENCE ONLY.  It is an ESTIMATOR, not the basin size;
    a selection by true basin size is a different and strictly stronger rule
    that this predicate FORBIDS (amendment `invalidation_rules`, last entry).
    The only inputs are the pool's own (S_d, h_d) and the MODELED scalar W.
    """
    _assert_evidence_only(ev)
    return ev.S.astype(np.float64) + 4.0 * float(W) * ev.h.astype(np.float64)


def tiebreak_keys(P: I.Params, n_entries: int) -> np.ndarray:
    """Section 3 `selection` -- the independent, seeded, deterministic
    tie-break key, ASCENDING.

    v2 draws it from the stream seeded 400 + s (Params.seed_tiebreak).  This
    reproduces the frozen v2 a-scan's own draw exactly: a FRESH
    numpy.random.default_rng(400 + s), one int64 in [0, 2^63) per pool entry,
    in pool order (source_v2/run_ascan.py).  Disclosed as an implementation
    choice in IMPLEMENTATION.md, per Section 3
    `what_a_reviewer_needs_and_this_section_does_not_give` (ii).
    """
    return np.random.default_rng(P.seed_tiebreak).integers(
        0, 1 << 63, size=n_entries, dtype=np.int64)


def select_static_indices(weights: np.ndarray, keys: np.ndarray, T: int) -> Dict[str, object]:
    """Section 3 `selection` + control NULL_B_G3.

    Takes the T entries of LARGEST w(d), ties broken by the seeded key
    ASCENDING, through BOTH frozen v2 selection code paths:

      * I.numpy_select  -- the numpy lexsort path.  CANONICAL here, because it
        is the path the frozen v2 STAGE 0 a-scan used, so STAGE 3A's
        replication is against the same code path that produced the committed
        numbers.
      * I.CountedSelector.select -- the counted streaming min-heap path.

    NULL_B_G3 requires the two selected DP sets to be IDENTICAL as sets; any
    difference is a bookkeeping leak that INVALIDATES the cell (it is not a
    negative result).  Both are pure functions of (weights, keys, T): no basin
    information is reachable from either.
    """
    if len(weights) != len(keys):
        raise ValueError("weights and tie-break keys disagree in length")
    idx_numpy = I.numpy_select(weights, keys, T)
    sel = I.CountedSelector()
    idx_counted = sel.select(weights, keys, T)
    return {
        "indices": idx_numpy,                       # canonical (frozen a-scan path)
        "indices_second_path": idx_counted,
        "null_b_set_identical": bool(set(idx_numpy) == set(idx_counted)),
        "selection_int_ops_counted_path": int(sel.ops),
    }


def relabel_pool_evidence(ev: PoolEvidence, P: I.Params) -> PoolEvidence:
    """Control NULL_A_G3 `construction` -- the null object of the same shape.

    On the IDENTICAL pool draw at the same (N, a, r, s), each entry's evidence
    PAIR (S_d, h_d) is replaced by a uniform random relabelling of the pool's
    OWN multiset of evidence pairs, the permutation drawn from the declared
    stream seeded 300 + s (Params.seed_null_a, exactly the v2 NULL-A stream).
    The pair moves together, so the pool's evidence multiset is preserved
    exactly.

    This destroys exactly one thing -- the correspondence between an entry's
    accumulated evidence and its basin size -- and preserves N, a, r, W, cap,
    the map, the basin distribution, the pool size, the pool's evidence
    multiset, the weight formula, the tie-break keys and their attachment to
    entries.  The DP values themselves are NOT permuted; the evidence is.
    """
    _assert_evidence_only(ev)
    perm = np.random.default_rng(P.seed_null_a).permutation(ev.size())
    return PoolEvidence(r=ev.r, T=ev.T, dps=ev.dps, S=ev.S[perm], h=ev.h[perm],
                        walks=ev.walks, P_cost=ev.P_cost,
                        capped_walks=ev.capped_walks)


def selected_dps(ev: PoolEvidence, indices: Sequence[int]) -> np.ndarray:
    """Map selected pool indices to their DP values.  Still evidence-only."""
    _assert_evidence_only(ev)
    return np.asarray([int(ev.dps[i]) for i in indices], dtype=np.int64)


# ===========================================================================
# REGION D -- SCORING AND THE PREDICATE
#
# Section 3 `static_coverage`, `predicate_per_seed`, `predicate_per_cell`.
# Exact basin sizes enter HERE, and only to SCORE a set already chosen.
# ===========================================================================

def static_coverage(basins: I.Basins, table: np.ndarray) -> float:
    """Section 3 `static_coverage`.

    StaticCov(T, r) = (sum of basin(d) over the T entries of STATIC(T)_r) / N:
    the EXACT coverage of the table the realistic rule actually chose.  The
    table argument has already been selected, in REGION C, without any access
    to these basin sizes.
    """
    return basins.coverage(table)


def margin_of(top_share_t_sel: float, static_cov: float) -> float:
    """Section 3 `predicate_per_seed`:
    margin_s := TopShare_s(T_sel) - StaticCov_s(T, r), both computed on THE
    SAME instantiation (same s, same map, same pool draw)."""
    return float(top_share_t_sel) - float(static_cov)


def g3_seed_flag(margin: float) -> bool:
    """Section 3 `predicate_per_seed`: g3_s := [ margin_s >= 0 ]."""
    return bool(margin >= 0.0)


def g3_cell_verdict(margins: Sequence[float]) -> dict:
    """Section 3 `predicate_per_cell`.

    pass_count := #{ s in S : g3_s };  G3 PASSES iff pass_count >= 4, FAILS
    iff pass_count <= 3, over the declared seed set {1,2,3,4,5}.  The >= 4-of-5
    threshold is v2's own frozen G3 rule, reused verbatim.
    """
    flags = [g3_seed_flag(m) for m in margins]
    pass_count = int(sum(flags))
    return {"seed_count": len(margins), "pass_count": pass_count,
            "per_seed_g3": flags,
            "verdict": "PASS" if pass_count >= G3_PASS_THRESHOLD else "FAIL",
            "threshold": f">= {G3_PASS_THRESHOLD} of {len(margins)}"}


# ===========================================================================
# ONE CELL, END TO END (the order of the regions above is the order of work)
# ===========================================================================

def measure_cell(P: I.Params, basins: I.Basins, r: int) -> dict:
    """Measure one (N, a, r, seed) cell: the signal, NULL_A_G3, NULL_B_G3 and
    the EXACT_COVERAGE_NON_EXCEEDANCE check, all on the SAME pool draw.

    The controls are computed here, beside the signal they control, rather
    than in a separate pass against a different pool draw -- amendment
    controls NULL_A_G3 `construction` ("On the IDENTICAL pool draw") and the
    handoff constraint "CONTROLS RUN WITH THE SIGNAL".
    """
    T = P.T
    T_sel = t_sel_of(T)
    share_t_sel = top_share(basins, T_sel)
    share_t = top_share(basins, T)

    # -- REGION B: the pool (evidence only) --------------------------------
    ev = build_pool(P, r)
    keys = tiebreak_keys(P, ev.size())

    # -- REGION C: selection (evidence only) -------------------------------
    w = selection_weight(ev, P.W)
    sel = select_static_indices(w, keys, T)
    table = selected_dps(ev, sel["indices"])

    ev_null = relabel_pool_evidence(ev, P)
    w_null = selection_weight(ev_null, P.W)
    sel_null = select_static_indices(w_null, keys, T)
    table_null = selected_dps(ev_null, sel_null["indices"])

    # -- REGION D: scoring -------------------------------------------------
    cov = static_coverage(basins, table)
    cov_null = static_coverage(basins, table_null)
    margin = margin_of(share_t_sel, cov)
    margin_null = margin_of(share_t_sel, cov_null)

    exceed_static = bool(cov > share_t + 0.0)
    exceed_null = bool(cov_null > share_t + 0.0)

    return {
        "r": r,
        "top_share_T_sel": share_t_sel,
        "top_share_T": share_t,
        "static_cov": cov,
        "margin": margin,
        "g3": g3_seed_flag(margin),
        "static_cov_null": cov_null,
        "margin_null": margin_null,
        "margin_over_margin_null": (margin / margin_null) if margin_null not in (0.0, -0.0) else None,
        "null_b_set_identical": sel["null_b_set_identical"] and sel_null["null_b_set_identical"],
        "null_b_set_identical_signal": sel["null_b_set_identical"],
        "null_b_set_identical_null_a": sel_null["null_b_set_identical"],
        "selection_int_ops_counted_path": sel["selection_int_ops_counted_path"],
        "exact_coverage_exceeds_top_share_T": exceed_static,
        "exact_coverage_null_exceeds_top_share_T": exceed_null,
        "table_size": int(len(table)),
        "table_hash": I.table_hash(table),
        "table_hash_null": I.table_hash(table_null),
        "pool": pool_statistics(ev, P),
        # v2's frozen bits_per_entry, reported so no ratio is quoted without
        # its storage sibling (metrics `secondary`, last entry).  MEASURED.
        "bits": {
            "S_bits_oracle_T_sel_table": int(T_sel * P.bits_entry),
            "S_bits_static_T_table": int(T * P.bits_entry),
            "S_peak_bits_pool_working_storage": int(ev.size() * P.bits_pool_entry),
            "bits_per_table_entry": int(P.bits_entry),
            "bits_per_pool_entry": int(P.bits_pool_entry),
        },
    }
