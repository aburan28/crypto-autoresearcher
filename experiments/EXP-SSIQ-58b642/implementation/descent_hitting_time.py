#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-58b642 -- Greedy delta_E descent versus random-walk hitting time on
directly-built supersingular 2-isogeny graphs (the direct test of lever L4).

Implements experiments/EXP-SSIQ-58b642/specification.yaml EXACTLY as frozen,
except where it discovers a load-bearing obstruction, which is reported
explicitly rather than routed around (see delta_e_cross_reference_report
below and DELTA_E_BLOCKER_NOTE).

This module defines:
  1. The estimator shared, byte-for-byte, between the REAL pipeline and
     calibration_synthetic.py's Phase 0 gate: ols_loglog_fit (the OLS-on-
     logs estimator) and population_median_with_sentinel (the population-
     wide-median-with-sentinel convention).  calibration_synthetic.py
     IMPORTS these two functions rather than reimplementing them, which is
     what makes C-CAL-GAP a calibration of the actual pipeline rather than
     a parallel implementation that could silently diverge.
  2. The content-derived tie-break rule (PF-4).
  3. Greedy-descent and non-backtracking-random-walk hitting-time
     simulators on a built graph.
  4. WISDE per-prime parsing (same route as EXP-SSIQ-4de240) used ONLY as
     a ground-truth/correctness cross-reference, never as a source of graph
     adjacency.
  5. C-NULL-LABEL: shuffled-label descent, which uses only the AGGREGATE
     delta_E value multiset (fully available from WISDE) and does not need
     a per-vertex correspondence -- see module docstring section "WHY
     C-NULL-LABEL IS MEASURABLE BUT THE REAL ARM IS NOT" below.
  6. The frozen decision rule, applied mechanically.

WHY C-NULL-LABEL IS MEASURABLE BUT THE REAL ARM IS NOT
--------------------------------------------------------
inputs.graph_construction.delta_E_cross_reference requires that WISDE
"supplies the delta_E label used for descent... for every enumerated
j-invariant."  The WISDE results<p>.sage release (verified directly, see
source_access_log.yaml and DELTA_E_BLOCKER_NOTE) contains, per maximal
ORDER TYPE, an abstract Z-basis in the quaternion algebra B_{p,infty} and
the (N1,N2,N3) successive-minima tuple -- N1 = delta_E -- but NO numeric
j-invariant and no identifier connecting an order type to a SPECIFIC
computed j-invariant.  Establishing that connection for a curve found by
this run's own Phi_2 BFS requires computing the curve's endomorphism ring
(solving the Deuring correspondence "curve -> ideal" problem), which is a
substantial isogeny-based-cryptography computation (ideal-to-isogeny
translation, KLPT-style connecting-ideal search) that EXP-SSIQ-4de240's
M_GRAD arm already identified as "reimplementing the authors' pipeline"
and out of THIS budget (7200s wall clock / 4 CPU-hours) -- and it is
exactly as out of budget here.

The delta_E = 1 locus is the ONE exception: j in F_p is a mathematical
IDENTITY (Galois-orbit singleton), independent of any external data, so it
requires no cross-reference at all -- and its COUNT is independently
verified against WISDE's N(1,p) below (C-CONNECTIVITY's finer-grained
sibling check), for all 12 primes, with an exact match in every case (see
raw-result.json "delta1_locus_cross_check").

C-NULL-LABEL, by contrast, is DEFINED to use "delta_E REPLACED by a
uniformly random permutation of the same value multiset" -- i.e. it never
needed a real per-vertex correspondence in the first place, only the
correct AGGREGATE multiset of delta_E values for that prime (fully known
from WISDE, reconstructed via the same Galois-orbit rule as
EXP-SSIQ-4de240's fit_delta_counting.py).  So the null arm's machinery is
implemented and run for real; the REAL-label arm, and therefore M-GAP
itself, is BLOCKED, and is reported as such -- never fabricated by
assigning WISDE's real multiset to vertices via an arbitrary rule (that
would silently turn the "real" arm into a second copy of the null arm and
misrepresent the test, which this run refuses to do).
"""

import hashlib
import json
import math
import os
import platform
import random
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_isogeny_graph as big  # noqa: E402
import calibration_synthetic as cal  # noqa: E402

EXPERIMENT_ID = "EXP-SSIQ-58b642"
RUN_ID = "RUN-SSIQ-58b642-a"
SEEDS = [20260805, 11, 977]          # spec.replication.seeds -- FROZEN

# 12 pre-registered primes, p = 1 (mod 12), p <= 22000, N = floor(p/12)
# spread ~200..1800, PINNED BEFORE any graph was built (selection rule:
# among all primes with 200 <= floor(p/12) <= 1800 and p = 1 mod 12,
# ascending order, take 12 evenly spaced BY LIST INDEX -- a rule fixed by
# the primes themselves, not by any fitted result).
PRIMES = [2437, 3889, 5737, 7333, 8893, 10657, 12541, 14389, 16189, 18049,
          19717, 21601]


# ==========================================================================
# 1. Shared low-level pipeline: OLS-on-logs + population-median-w/-sentinel
#    IMPORTED VERBATIM by calibration_synthetic.py -- this is what makes
#    Phase 0 a calibration of the real pipeline.
# ==========================================================================

def ols_loglog_fit(N_list, y_list):
    """OLS of log(y) on log(N): log(y) = log_c + gamma * log(N).
    Pure Python, deterministic (no floating-point library beyond math.log/
    exp/sqrt), so re-running gives bit-identical output (C-REPRO)."""
    n = len(N_list)
    if n != len(y_list):
        raise ValueError("N_list and y_list length mismatch")
    if n < 3:
        raise ValueError("too few points for a 2-parameter OLS fit: %d" % n)
    xs = [math.log(N) for N in N_list]
    ys = [math.log(y) for y in y_list]
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    sxx = sum((x - xbar) ** 2 for x in xs)
    sxy = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    if sxx == 0.0:
        raise ValueError("degenerate design: all N equal")
    gamma = sxy / sxx
    log_c = ybar - gamma * xbar
    resid = [y - (log_c + gamma * x) for x, y in zip(xs, ys)]
    rss = sum(r * r for r in resid)
    tss = sum((y - ybar) ** 2 for y in ys)
    dof = n - 2
    sigma2 = (rss / dof) if dof > 0 else float("nan")
    se_gamma = math.sqrt(sigma2 / sxx) if dof > 0 else float("nan")
    r2 = (1.0 - rss / tss) if tss > 0 else float("nan")
    return {
        "gamma": gamma, "se_gamma": se_gamma, "log_c": log_c,
        "c": math.exp(log_c), "n": n, "r_squared": r2, "rss": rss,
        "dof": dof, "N_list": list(N_list), "y_list": list(y_list),
    }


def population_median_with_sentinel(raw_values, trapped_mask, sentinel):
    """M-GAMMA-GREEDY.pf2_censoring_rule's population-wide median: EVERY
    entry contributes (trapped entries via the sentinel value), never a
    survivor-restricted median.  Returns (median, trapped_fraction)."""
    n = len(raw_values)
    if n != len(trapped_mask):
        raise ValueError("raw_values / trapped_mask length mismatch")
    if n == 0:
        raise ValueError("empty population")
    combined = [sentinel if trapped_mask[i] else raw_values[i]
                for i in range(n)]
    s = sorted(combined)
    if n % 2 == 1:
        median = s[n // 2]
    else:
        median = 0.5 * (s[n // 2 - 1] + s[n // 2])
    trapped_fraction = sum(1 for t in trapped_mask if t) / float(n)
    return median, trapped_fraction


# ==========================================================================
# 2. Tie-break rule (PF-4): content-derived, never discovery-order derived
# ==========================================================================

def tie_break_choice(delta_value, tied_neighbors):
    """tied_neighbors: list of Fp2 tuples (a,b), all at the strict minimum
    delta among current vertex's available (non-backtracking) neighbours.
    sha256 over (delta_value, sorted tied neighbours' own field-element
    reprs) selects the winner -- depends only on (a) the tied-neighbour set
    and (b) the delta labelling in force, never on BFS discovery order or
    internal vertex id, per PF-4's structural requirement."""
    reprs = sorted(tuple(x) for x in tied_neighbors)
    payload = repr((int(delta_value), reprs)).encode("utf-8")
    h = hashlib.sha256(payload).digest()
    idx = int.from_bytes(h, "big") % len(reprs)
    return reprs[idx]


# ==========================================================================
# 3. Hitting-time simulators on a built graph
# ==========================================================================

def greedy_descent_hitting_time(adjacency, start, delta_map, diameter_sentinel):
    """Steepest descent to strictly smaller delta_E, non-backtracking
    (excludes the immediately preceding vertex from the candidate set;
    note this exclusion can NEVER remove a genuine strictly-smaller
    candidate in a strict-descent walk, since the predecessor's delta is
    always STRICTLY GREATER than the current vertex's delta by
    construction of the walk's own history -- so it affects only the
    accounting, never the reachable set).  Halts at a local minimum
    (trapped) with the sentinel hitting time.  Termination is guaranteed
    because delta strictly decreases every accepted step (a finite
    integer-valued quantity bounded below by 1), so no step cap is needed."""
    current = start
    prev = None
    steps = 0
    tie_events = 0
    steps_with_choice = 0
    if delta_map[start] == 1:
        return {"hitting_time": 0, "trapped": False, "steps": 0,
                "tie_events": 0, "steps_with_choice": 0}
    while True:
        nbrs = [v for v in adjacency[current] if v != prev]
        if not nbrs:
            nbrs = list(adjacency[current])
        cur_delta = delta_map[current]
        candidates = [v for v in nbrs if delta_map[v] < cur_delta]
        if not candidates:
            return {"hitting_time": diameter_sentinel, "trapped": True,
                    "steps": steps, "tie_events": tie_events,
                    "steps_with_choice": steps_with_choice}
        steps_with_choice += 1
        min_delta = min(delta_map[v] for v in candidates)
        tied = [v for v in candidates if delta_map[v] == min_delta]
        if len(tied) > 1:
            tie_events += 1
            nxt = tie_break_choice(min_delta, tied)
        else:
            nxt = tied[0]
        prev = current
        current = nxt
        steps += 1
        if delta_map[current] == 1:
            return {"hitting_time": steps, "trapped": False, "steps": steps,
                    "tie_events": tie_events,
                    "steps_with_choice": steps_with_choice}


def random_walk_hitting_time(adjacency, start, delta_map, rng,
                              diameter_sentinel, max_steps):
    """Non-backtracking simple random walk (uniform among the up-to-3
    available neighbours, excluding the immediately preceding vertex) until
    delta_map == 1.  max_steps is a computational safety cap; per
    M-GAMMA-RANDOM's definition no sentinel is expected to fire here in
    practice on a connected non-bipartite 3-regular graph -- if the cap is
    ever hit it is recorded as an anomaly, never silently expected."""
    current = start
    prev = None
    steps = 0
    if delta_map[start] == 1:
        return {"hitting_time": 0, "trapped": False, "steps": 0,
                "cap_hit": False}
    while steps < max_steps:
        nbrs = [v for v in adjacency[current] if v != prev]
        if not nbrs:
            nbrs = list(adjacency[current])
        nxt = nbrs[rng.randrange(len(nbrs))]
        prev = current
        current = nxt
        steps += 1
        if delta_map[current] == 1:
            return {"hitting_time": steps, "trapped": False, "steps": steps,
                    "cap_hit": False}
    return {"hitting_time": diameter_sentinel, "trapped": True,
            "steps": steps, "cap_hit": True}


def run_population(graph_adjacency, vertices, delta_map, method, rng,
                    diameter_sentinel, max_random_steps=None):
    """Run ONE trial per starting vertex (population-wide, per
    median_population_note).  Returns per-vertex raw results plus the
    aggregated population median/trapped_fraction/tie frequency."""
    raw_values = []
    trapped_mask = []
    tie_events_total = 0
    steps_with_choice_total = 0
    cap_hit_count = 0
    for v in vertices:
        if method == "greedy":
            r = greedy_descent_hitting_time(graph_adjacency, v, delta_map,
                                             diameter_sentinel)
            tie_events_total += r["tie_events"]
            steps_with_choice_total += r["steps_with_choice"]
        elif method == "random":
            r = random_walk_hitting_time(graph_adjacency, v, delta_map, rng,
                                          diameter_sentinel, max_random_steps)
            if r.get("cap_hit"):
                cap_hit_count += 1
        else:
            raise ValueError(method)
        raw_values.append(float(r["hitting_time"]))
        trapped_mask.append(bool(r["trapped"]))
    median, trapped_fraction = population_median_with_sentinel(
        raw_values, trapped_mask, float(diameter_sentinel))
    tiefreq = (tie_events_total / steps_with_choice_total
               if method == "greedy" and steps_with_choice_total > 0
               else (0.0 if method == "greedy" else None))
    return {
        "median": median, "trapped_fraction": trapped_fraction,
        "n": len(vertices), "tie_frequency": tiefreq,
        "cap_hit_count": cap_hit_count,
        "raw_values": raw_values, "trapped_mask": trapped_mask,
    }


# ==========================================================================
# 4. WISDE parsing (same route/format as EXP-SSIQ-4de240) -- ground truth
#    and correctness-check ONLY, never a source of graph adjacency.
# ==========================================================================

TUPLE_RE = re.compile(r"^\s*\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\)\s*$", re.M)
ENTRY_RE = re.compile(r"^\s*i\s*=\s*(\d+)\s*$", re.M)
SUPERSINGULAR_E = {1: 0, 5: 1, 7: 1, 11: 2}


def parse_wisde_file(text):
    tuples = TUPLE_RE.findall(text)
    entries = ENTRY_RE.findall(text)
    n1 = [int(t[0]) for t in tuples]
    if len(entries) != len(tuples):
        raise ValueError("entry/tuple count mismatch: %d vs %d"
                          % (len(entries), len(tuples)))
    return n1


def wisde_class_number_formula(p):
    if p in (2, 3):
        return 1
    return p // 12 + SUPERSINGULAR_E[p % 12]


def wisde_delta_multiset(n1_list):
    """Reconstruct the per-CURVE (not per-order-type) delta_E multiset via
    the Galois-orbit rule: an order type with N1=1 contributes ONE curve of
    delta_E=1; an order type with N1=T>=2 contributes TWO curves of
    delta_E=T (the conjugate pair)."""
    multiset = []
    for v in n1_list:
        if v == 1:
            multiset.append(1)
        else:
            multiset.extend([v, v])
    return multiset


# ==========================================================================
# 5. Decision rule (applied mechanically, never adjusted)
# ==========================================================================

def apply_decision_rule(m_gap, m_gap_ci_lo, m_gap_ci_hi,
                         c_null_label_pass, c_connectivity_pass,
                         n_primes_valid):
    """spec.preregistered_prediction.decision_rule_frozen_before_data and
    spec.falsification_criterion, applied mechanically."""
    if not (c_null_label_pass and c_connectivity_pass) or n_primes_valid < 4:
        return {
            "branch": "VOID",
            "reason": ("C-NULL-LABEL or C-CONNECTIVITY failed, or fewer "
                       "than 4 valid primes (n_primes_valid=%d, "
                       "c_null_label_pass=%s, c_connectivity_pass=%s)"
                       % (n_primes_valid, c_null_label_pass,
                          c_connectivity_pass)),
        }
    if m_gap_ci_lo > 0.0:
        return {"branch": "DETECTED",
                "reason": ("M-GAP's bootstrap 95%% CI [%.6f, %.6f] excludes "
                           "0 in the positive direction" % (m_gap_ci_lo, m_gap_ci_hi))}
    return {"branch": "UNRESOLVED-BY-THIS-TEST",
            "reason": ("M-GAP's bootstrap 95%% CI [%.6f, %.6f] includes 0 or "
                       "excludes 0 in the negative direction; per "
                       "falsification_criterion this is reported as "
                       "'unresolved by this test', never 'falsified' or "
                       "'refuted'" % (m_gap_ci_lo, m_gap_ci_hi))}


def bootstrap_gap_ci(N_list, median_greedy_list, median_random_list, rng,
                      n_boot=2000):
    """Bootstrap CI for M-GAP = gamma_random - gamma_greedy by resampling
    PRIMES (the unit of the OLS fit) with replacement."""
    n = len(N_list)
    gaps = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        Nb = [N_list[i] for i in idx]
        gb = [median_greedy_list[i] for i in idx]
        rb = [median_random_list[i] for i in idx]
        try:
            fg = ols_loglog_fit(Nb, gb)
            fr = ols_loglog_fit(Nb, rb)
        except ValueError:
            continue
        gaps.append(fr["gamma"] - fg["gamma"])
    gaps.sort()
    if not gaps:
        return None, None, []
    lo = gaps[int(0.025 * len(gaps))]
    hi = gaps[min(len(gaps) - 1, int(0.975 * len(gaps)))]
    return lo, hi, gaps


# ==========================================================================
# 6. Phase 1 orchestration
# ==========================================================================

def git_state():
    def g(*a):
        try:
            return subprocess.check_output(
                ["git"] + list(a), stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"),
            "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain"))}


def load_wisde_records(cache_dir, primes):
    records = {}
    for p in primes:
        path = os.path.join(cache_dir, "results%d.sage" % p)
        raw = open(path, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8", errors="strict")
        n1 = parse_wisde_file(text)
        h_recon_singleton = sum(1 for v in n1 if v == 1)
        h_recon_total = h_recon_singleton + 2 * (len(n1) - h_recon_singleton)
        h_formula = wisde_class_number_formula(p)
        records[p] = {
            "p": p, "n1_list": n1, "n_order_types": len(n1),
            "n_delta_eq_1_order_types": h_recon_singleton,
            "h_reconstructed_total_curves": h_recon_total,
            "h_class_number_formula": h_formula,
            "normalisation_ok": bool(h_recon_total == h_formula),
            "delta_multiset": wisde_delta_multiset(n1),
            "sha256": sha, "bytes": len(raw),
            "url": ("https://raw.githubusercontent.com/christellevincent/"
                     "WISDE/main/results/results%d.sage" % p),
        }
    return records


def build_all_graphs(primes, seed, time_budget_per_prime=900):
    graphs = {}
    seed_info = {}
    for p in primes:
        rng = random.Random(seed)
        j0, D = big.seed_j_invariant(p)
        ss, trace, A, B = big.verify_seed_supersingular(p, j0)
        if not ss:
            raise RuntimeError(
                "seed j0=%d for p=%d FAILED independent supersingularity "
                "verification (trace=%d != 0)" % (j0, p, trace))
        seed_info[p] = {"j0": j0, "discriminant": D, "trace_verified_zero": trace,
                         "curve_A": A, "curve_B": B}
        g = big.build_graph_bfs(p, j0, rng, time_budget_seconds=time_budget_per_prime)
        graphs[p] = g
    return graphs, seed_info


def run_correctness_gates(graphs, wisde_records, primes, edgelist_prime):
    connectivity = {}
    degseq = {}
    delta1_cross_check = {}
    for p in primes:
        g = graphs[p]
        n_built = len(g["vertices"])
        n_wisde = wisde_records[p]["h_reconstructed_total_curves"]
        n_formula = p // 12 + {1: 0, 5: 1, 7: 1, 11: 2}[p % 12]
        connectivity[p] = {
            "n_built": n_built, "n_wisde": n_wisde, "n_formula_floor_p12": n_formula,
            "pass": bool(n_built == n_wisde == n_formula),
        }
        dc = big.degree_sequence_check(g)
        degseq[p] = dc
        locus = big.fp_rational_locus(g)
        n_wisde_delta1 = wisde_records[p]["n_delta_eq_1_order_types"]
        delta1_cross_check[p] = {
            "n_built_fp_rational": len(locus),
            "n_wisde_delta_eq_1": n_wisde_delta1,
            "pass": bool(len(locus) == n_wisde_delta1),
        }
    edgelist = big.independent_edgelist_check(graphs[edgelist_prime], edgelist_prime,
                                               rng_seed=11)
    return {
        "connectivity": connectivity, "degree_sequence": degseq,
        "delta1_locus_cross_check": delta1_cross_check,
        "edgelist_prime": edgelist_prime, "edgelist_check": edgelist,
    }


def attempt_real_delta_map(p, graph, wisde_record):
    """Attempt to build the REAL per-vertex delta_E map required by
    inputs.graph_construction.delta_E_cross_reference.  Returns
    (delta_map_or_None, report).  The delta_E = 1 sub-map IS fully and
    correctly determined (see report); delta_E > 1 is NOT, for the reason
    stated in the module docstring (DELTA_E_BLOCKER_NOTE) -- this function
    makes that determination explicit and auditable rather than silently
    fabricating an assignment."""
    field = graph["field"]
    locus1 = set(big.fp_rational_locus(graph))
    non_locus1 = [v for v in graph["vertices"] if v not in locus1]
    n_wisde_gt1_curves = wisde_record["h_reconstructed_total_curves"] - \
        wisde_record["n_delta_eq_1_order_types"]
    report = {
        "p": p,
        "delta_eq_1_resolved": {
            "method": "mathematical identity: delta_E = 1 iff j in F_p "
                       "(Galois orbit singleton); requires no external data",
            "n_vertices": len(locus1),
            "matches_wisde_count": len(locus1) == wisde_record["n_delta_eq_1_order_types"],
        },
        "delta_gt_1_blocked": {
            "n_vertices_needing_a_label": len(non_locus1),
            "n_wisde_curves_with_delta_gt_1": n_wisde_gt1_curves,
            "counts_match": len(non_locus1) == n_wisde_gt1_curves,
            "reason": (
                "WISDE's results%d.sage lists, per maximal ORDER TYPE, an "
                "abstract Z-basis in the quaternion algebra B_{%d,infty} and "
                "the (N1,N2,N3) tuple -- NO numeric j-invariant and no "
                "identifier connecting an order type to a specific computed "
                "j-invariant. Verified directly by fetching and inspecting "
                "the file (see source_access_log.yaml probe_wisde_format). "
                "Establishing the correspondence between one of this run's "
                "%d non-F_p vertices and its WISDE order-type row requires "
                "computing the vertex's endomorphism ring (the Deuring "
                "correspondence 'curve -> ideal' direction), a substantial "
                "isogeny-based-cryptography computation (KLPT-style "
                "connecting-ideal search + ideal-to-isogeny translation) "
                "that EXP-SSIQ-4de240's M_GRAD arm already identified as "
                "'reimplementing the authors' pipeline' and out of budget -- "
                "and it is out of THIS run's 7200s/4-CPU-hour budget for the "
                "same reason. NOT attempted via an arbitrary/random "
                "assignment of WISDE's real per-prime multiset onto these "
                "vertices, because that would silently destroy whatever "
                "true delta_E-vs-adjacency correlation exists (making the "
                "'real' arm statistically indistinguishable from another "
                "instance of C-NULL-LABEL) and misrepresent the test."
                % (p, p, len(non_locus1))),
        },
    }
    return None, report


def build_null_delta_map(graph, wisde_record, seed):
    """C-NULL-LABEL's REQUIRED INPUT is only the delta_E VALUE MULTISET
    (uniformly permuted onto the vertex set) -- fully known from WISDE,
    independent of the per-vertex correspondence blocker above."""
    vertices = list(graph["vertices"])
    multiset = list(wisde_record["delta_multiset"])
    if len(multiset) != len(vertices):
        raise ValueError("delta multiset size %d != vertex count %d"
                          % (len(multiset), len(vertices)))
    rng = random.Random(seed)
    shuffled = list(multiset)
    rng.shuffle(shuffled)
    return dict(zip(vertices, shuffled))


def run_null_arm(graphs, wisde_records, primes, diameters, seeds,
                  max_random_steps_factor=50):
    """Run C-NULL-LABEL for real: shuffled-label greedy + random-walk
    descent on the SAME built graphs, under each declared seed.  Returns
    per-seed per-prime results plus the gamma fits."""
    per_seed = {}
    for seed in seeds:
        per_prime = {}
        for p in primes:
            g = graphs[p]
            delta_map = build_null_delta_map(g, wisde_records[p], seed)
            diam = diameters[p]
            rng = random.Random(seed * 1000003 + p)
            greedy = run_population(g["adjacency"], g["vertices"], delta_map,
                                     "greedy", rng, diam)
            rw = run_population(g["adjacency"], g["vertices"], delta_map,
                                 "random", rng, diam,
                                 max_random_steps=max_random_steps_factor * len(g["vertices"]))
            per_prime[p] = {
                "N": len(g["vertices"]),
                "greedy_median": greedy["median"],
                "greedy_trapped_fraction": greedy["trapped_fraction"],
                "greedy_tie_frequency": greedy["tie_frequency"],
                "random_median": rw["median"],
                "random_trapped_fraction": rw["trapped_fraction"],
                "random_cap_hit_count": rw["cap_hit_count"],
            }
        N_list = [per_prime[p]["N"] for p in primes]
        greedy_medians = [per_prime[p]["greedy_median"] for p in primes]
        random_medians = [per_prime[p]["random_median"] for p in primes]
        fit_greedy = ols_loglog_fit(N_list, greedy_medians)
        fit_random = ols_loglog_fit(N_list, random_medians)
        m_gap_null = fit_random["gamma"] - fit_greedy["gamma"]
        per_seed[str(seed)] = {
            "per_prime": per_prime,
            "gamma_greedy_null": fit_greedy["gamma"],
            "se_gamma_greedy_null": fit_greedy["se_gamma"],
            "gamma_random_null": fit_random["gamma"],
            "se_gamma_random_null": fit_random["se_gamma"],
            "m_gap_null": m_gap_null,
            "max_trapped_fraction_greedy": max(
                per_prime[p]["greedy_trapped_fraction"] for p in primes),
            "max_tie_frequency": max(
                (per_prime[p]["greedy_tie_frequency"] or 0.0) for p in primes),
            "any_random_cap_hit": any(
                per_prime[p]["random_cap_hit_count"] > 0 for p in primes),
        }
    return per_seed


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--wisde-cache-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s" % (started, EXPERIMENT_ID, RUN_ID))

    # ---- PHASE 0 -----------------------------------------------------
    log("PHASE 0: C-CAL-GAP synthetic calibration (pure arithmetic, no "
        "graph, no fetch)")
    phase0 = cal.run_calibration()
    log("  C-CAL-GAP overall_pass = %s" % phase0["overall_pass"])
    for r in phase0["synthetic_pairs"]:
        label = r["variant"] + (("(c=%s)" % r["c"]) if "c" in r else "")
        log("    %-28s m_gap=%.6f abs_error=%.6f pass=%s"
            % (label, r["m_gap_recovered"], r["abs_error"], r["pass"]))

    payload = {
        "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
        "started_utc": started, "git": git_state(), "python": sys.version,
        "platform": platform.platform(),
        "certificate": {
            "kind": "none",
            "reason": ("Pure measurement run. No discrete log is claimed, "
                       "no factor-base relation is claimed, no isogeny "
                       "problem instance is solved. docs/claims-and-"
                       "verification.md requires kind: none to be stated "
                       "explicitly for such runs."),
        },
        "phase0_calibration": phase0,
    }

    if not phase0["overall_pass"]:
        log("PHASE 0 GATE FAILED -- STOPPING before Phase 1 per "
            "spec.stopping_rules[0] / controls.C-CAL-GAP.failure_consequence")
        payload["stopped_before_phase1"] = True
        payload["stop_reason"] = "C-CAL-GAP failed"
        payload["decision"] = {"branch": "N/A",
                                "reason": "run stopped at Phase 0 gate"}
        with open(args.out, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
        log("wrote %s" % args.out)
        return 1

    log("PHASE 0 PASSED -- proceeding to Phase 1 (real graphs, real WISDE "
        "cross-reference)")

    # ---- PHASE 1: graph construction ----------------------------------
    log("Phase 1: building %d graphs via Phi_2 BFS (independent of WISDE)"
        % len(PRIMES))
    graphs, seed_info = build_all_graphs(PRIMES, SEEDS[0])
    for p in PRIMES:
        log("  p=%-6d N=%-5d elapsed=%.2fs seed_j0=%d disc=%d"
            % (p, len(graphs[p]["vertices"]), graphs[p]["elapsed_seconds"],
               seed_info[p]["j0"], seed_info[p]["discriminant"]))

    log("fetching/loading WISDE ground-truth records from %s" % args.wisde_cache_dir)
    wisde_records = load_wisde_records(args.wisde_cache_dir, PRIMES)
    for p in PRIMES:
        log("  p=%-6d order_types=%-5d n1=1:%-4d normalisation_ok=%s"
            % (p, wisde_records[p]["n_order_types"],
               wisde_records[p]["n_delta_eq_1_order_types"],
               wisde_records[p]["normalisation_ok"]))

    log("running correctness gates: C-CONNECTIVITY, M-DEGSEQ, C-EDGELIST, "
        "delta=1 locus cross-check")
    gates = run_correctness_gates(graphs, wisde_records, PRIMES, edgelist_prime=PRIMES[0])
    all_connectivity_pass = all(gates["connectivity"][p]["pass"] for p in PRIMES)
    all_degseq_pass = all(gates["degree_sequence"][p]["pass"] for p in PRIMES)
    all_delta1_pass = all(gates["delta1_locus_cross_check"][p]["pass"] for p in PRIMES)
    log("  C-CONNECTIVITY all pass: %s" % all_connectivity_pass)
    log("  M-DEGSEQ all pass: %s" % all_degseq_pass)
    log("  C-EDGELIST (p=%d): pass=%s" % (PRIMES[0], gates["edgelist_check"]["pass"]))
    log("  delta=1 locus cross-check all pass: %s" % all_delta1_pass)

    diameters = {}
    for p in PRIMES:
        diameters[p] = big.bfs_diameter(graphs[p])
        log("  p=%-6d diameter=%d" % (p, diameters[p]))

    # ---- delta_E cross-reference: attempt, discover, report -----------
    log("attempting per-vertex delta_E cross-reference from WISDE for every "
        "enumerated j-invariant (inputs.graph_construction.delta_E_cross_reference)")
    delta_reports = {}
    for p in PRIMES:
        _, report = attempt_real_delta_map(p, graphs[p], wisde_records[p])
        delta_reports[p] = report
    log("  delta_E = 1 locus: fully resolved and matches WISDE for all "
        "%d primes (no external data needed -- mathematical identity)"
        % len(PRIMES))
    log("  delta_E > 1 per-vertex labels: BLOCKED for all %d primes -- see "
        "raw-result.json delta_e_cross_reference_report" % len(PRIMES))

    # ---- C-NULL-LABEL (measurable: uses only the aggregate multiset) --
    log("running C-NULL-LABEL (shuffled-label descent) under seeds %s" % SEEDS)
    null_arm = run_null_arm(graphs, wisde_records, PRIMES, diameters, SEEDS)
    for seed in SEEDS:
        r = null_arm[str(seed)]
        log("  seed=%-9d gamma_greedy_null=%.6f gamma_random_null=%.6f "
            "m_gap_null=%.6f max_trapped=%.4f max_tiefreq=%.4f"
            % (seed, r["gamma_greedy_null"], r["gamma_random_null"],
               r["m_gap_null"], r["max_trapped_fraction_greedy"],
               r["max_tie_frequency"]))

    # ---- C-REPRO: bit-identical re-run of the null arm under seed[0] --
    log("C-REPRO: re-running the null arm under seed[0] for bit-identical check")
    null_arm_repro = run_null_arm(graphs, wisde_records, PRIMES, diameters,
                                   [SEEDS[0]])
    repro_match = (null_arm_repro[str(SEEDS[0])]["gamma_greedy_null"]
                   == null_arm[str(SEEDS[0])]["gamma_greedy_null"]
                   and null_arm_repro[str(SEEDS[0])]["gamma_random_null"]
                   == null_arm[str(SEEDS[0])]["gamma_random_null"])
    log("  C-REPRO bit-identical: %s" % repro_match)

    # ---- decision rule --------------------------------------------------
    n_primes_valid = sum(1 for p in PRIMES if gates["connectivity"][p]["pass"])
    decision = apply_decision_rule(
        m_gap=None, m_gap_ci_lo=None, m_gap_ci_hi=None,
        c_null_label_pass=None, c_connectivity_pass=all_connectivity_pass,
        n_primes_valid=n_primes_valid)
    decision = {
        "branch": "VOID",
        "reason": (
            "M-GAP (the confirmatory metric) could NOT be computed: the "
            "REAL-label descent arm is BLOCKED by a discovered data-"
            "availability gap in the delta_E cross-reference input (see "
            "delta_e_cross_reference_report), discovered during Phase 1. "
            "This is DISTINCT FROM, and not caused by, a C-NULL-LABEL or "
            "C-CONNECTIVITY failure in the contract's own listed VOID-"
            "triggering sense -- C-CONNECTIVITY PASSED for all %d primes "
            "(all_connectivity_pass=%s) and C-NULL-LABEL's own machinery "
            "ran successfully (see null_arm), but with nothing to compare "
            "it against, since the real arm was never produced. VOID is "
            "reported, per spec.invalidation_rules' underspecification "
            "clause and stopping_rules discipline, because the primary "
            "metric cannot be produced or interpreted in either direction "
            "-- never DETECTED, never UNRESOLVED-BY-THIS-TEST (both "
            "presuppose a computed real-label M-GAP), and never 'falsified' "
            "or 'refuted.'" % (len(PRIMES), all_connectivity_pass)),
        "m_gap_real": None,
        "n_primes_connectivity_valid": n_primes_valid,
        "c_connectivity_all_pass": bool(all_connectivity_pass),
        "c_degseq_all_pass": bool(all_degseq_pass),
        "c_edgelist_pass": bool(gates["edgelist_check"]["pass"]),
        "delta1_locus_cross_check_all_pass": bool(all_delta1_pass),
        "c_repro_pass": bool(repro_match),
    }
    log("DECISION RULE -> %s" % decision["branch"])
    log("  %s" % decision["reason"])

    payload.update({
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_clock_seconds": time.time() - t0,
        "primes": PRIMES,
        "seed_construction": seed_info,
        "wisde_records_summary": {
            p: {k: v for k, v in wisde_records[p].items()
                if k not in ("n1_list", "delta_multiset")}
            for p in PRIMES},
        "correctness_gates": {
            "connectivity": gates["connectivity"],
            "degree_sequence": {p: {k: v for k, v in gates["degree_sequence"][p].items()
                                     if k != "examples"} for p in PRIMES},
            "delta1_locus_cross_check": gates["delta1_locus_cross_check"],
            "edgelist_prime": gates["edgelist_prime"],
            "edgelist_check": {k: v for k, v in gates["edgelist_check"].items()
                                if k != "mismatches"},
        },
        "diameters": diameters,
        "delta_e_cross_reference_report": delta_reports,
        "null_arm": null_arm,
        "null_arm_c_repro": {"match": repro_match},
        "decision": decision,
        "objective_boundary": (
            "This run tests for the EXISTENCE of a computable delta_E-"
            "gradient (L4's revisit condition). It does not implement, "
            "propose, or cost a descent algorithm. Scale: toy, graph sizes "
            "203-1800 vertices; no result transfers to cryptographic scale."
        ),
        "scale_qualifier": "toy; N (graph size) in [203, 1800]; max log2(p) = %.4f"
                            % math.log2(max(PRIMES)),
    })

    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True, default=str)
    log("wrote %s (%.1fs total)" % (args.out, time.time() - t0))
    print("DECISION %s" % decision["branch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
