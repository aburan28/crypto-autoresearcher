#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v7 (BATCH-010) -- delta_e_permutation_null_control_v7.

Implements experiments/EXP-SSIQ-a85692/specification_v7.yaml
inputs.delta_e_permutation_null_control_v7 EXACTLY as frozen (version 7,
frozen_at 2026-08-06, frozen at commit 6bdaecb8).

This is the SINGLE new script required_artifacts_note names. It both (a)
implements the control as importable functions and (b) is this run's own
CLI entry point (--run-dir / --raw-result-b), writing this run's own
required artifacts directly -- no separate orchestration script is needed,
unlike v6's four-file diff, since this amendment is ONE part, not two.

REUSE / DUPLICATION SPLIT, DISCLOSED EXPLICITLY (matches
required_artifacts_note's own (i)/(ii) split):
  (i)  GENUINELY IMPORTED, UNCHANGED: trapping_diagnostic_v5.build_graph_for_prime
       and trapping_diagnostic_v5.load_archived_prime_data (both confirmed
       standalone, module-level functions by direct read of that file);
       build_isogeny_graph.degree_sequence_check (also imported unchanged,
       by reference, via trapping_diagnostic_v5's own import chain and
       directly here).
  (ii) AUTHORIZED, DISCLOSED DUPLICATES of trapping_diagnostic_v5.py's own
       inline logic (PF-9 FIX APPLIED, round 2 pre-freeze review: the
       coverage assertion and graph-rebuild verification are equally
       non-importable, confirmed inline in trapping_diagnostic_v5.py, not
       standalone symbols, exactly like is_structural_local_min):
       is_structural_local_min(v, delta_map, adjacency), depth(v), the
       coverage assertion, and the graph-rebuild verification. These match
       trapping_diagnostic_v5.py's own formula and procedure exactly, with
       ONE deliberate, explicitly-disclosed broadening (PF-4 FIX APPLIED):
       is_structural_local_min/depth are evaluated over EVERY structural
       local minimum here, WITHOUT v6's own basin-eligible delta_map[v] > 1
       restriction.

This amendment does NOT import funnel_structure_diagnostic_v6.py or
descent_walk_hardened.py: it needs neither greedy_descent_hitting_time_v2
nor any walk simulation, only the static is_structural_local_min/depth
formulas, per required_artifacts_note's own text.

FAILURE-HANDLING MODEL, STATED DIRECTLY AND SELF-SUFFICIENTLY (PF-8 FIX
APPLIED, round 2 pre-freeze review: NOT attributed to an inherited model --
trapping_diagnostic_v5.py's own run_all has no try/except and would
propagate a coverage/graph-rebuild failure globally, the opposite of what
this amendment requires): the REQUIRED COVERAGE ASSERTION AND GRAPH-REBUILD
VERIFICATION is a PER-PRIME halt below -- a failure for one prime does NOT
prevent the other three primes' computation. The REAL_DEPTH0_FRACTION
"materially disagrees with expectation" anomaly branch is explicitly NOT a
halt of any kind (PF-2 FIX APPLIED): it NEVER skips or withholds that
prime's 1000 null trials, which are always computed and archived regardless
of whether the real-data comparison matches its expected value.

This module performs NO new delta_E search of any kind: delta_map is read
directly from the already-committed RUN-SSIQ-a85692-b/raw-result.json via
trapping_diagnostic_v5.load_archived_prime_data (READ ONLY). This is pure
arithmetic (permutation + local-minimum/depth recomputation) on
already-archived data.
"""

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

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
_B_IMPL_DIR = os.path.join(_THIS_DIR, "..", "..", "EXP-SSIQ-58b642",
                            "implementation")
sys.path.insert(0, _B_IMPL_DIR)

# Import order: see trapping_diagnostic_v5.py's own note on the genuine
# circular import between the frozen descent_hitting_time.py and
# calibration_synthetic.py -- importing calibration_synthetic first avoids
# it (trapping_diagnostic_v5.py performs this internally on its own import,
# but calibration_synthetic is imported here too, first, for the same
# defensive reason funnel_structure_diagnostic_v6.py already states).
# Neither frozen file is modified here.
import calibration_synthetic as cal  # noqa: E402,F401 (import-order fix only)
import build_isogeny_graph as big  # noqa: E402  (FROZEN, UNCHANGED -- (i)
                                    # genuine-import source for
                                    # degree_sequence_check)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED --
                                        # (i) genuine-import source for
                                        # build_graph_for_prime /
                                        # load_archived_prime_data)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-g"
SPEC_VERSION = 7

PRIMES_V7 = [2437, 3889, 5737, 7333]
ARCHIVED_N_VERTICES = {2437: 203, 3889: 324, 5737: 478, 7333: 611}
GRAPH_SEED = 20260805  # SEEDS[0], same pinned convention every amendment
                       # since v5 uses -- NEVER the permutation seed below.
PERMUTATION_SEED = 20260806  # PRE-REGISTERED, distinct from GRAPH_SEED per
                              # the frozen spec's own explicit text.
N_TRIALS = 1000  # PRE-REGISTERED before execution, per the frozen spec.

RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")

# RUN-SSIQ-a85692-f's own already-archived ANOM-1 figures (broader domain --
# every structural local minimum, including delta_E=1 -- NOT the
# basin-eligible-only 86/114/176/270 counts). Used ONLY for the disclosed
# comparison this amendment's own text requires; never substituted for a
# measured value and never used to alter the computation itself.
EXPECTED_REAL_N_LOCAL_MIN = {2437: 95, 3889: 132, 5737: 194, 7333: 287}
EXPECTED_REAL_DEPTH0_FRACTION = 1.0


class PermutationNullControlError(RuntimeError):
    """Raised on a PER-PRIME halt condition (coverage assertion failure or
    graph-rebuild verification failure). THIS amendment's OWN explicit
    per-prime choice (PF-8 fix), not inherited from
    trapping_diagnostic_v5.py's own run_all, which is a bare loop with no
    try/except and would let such a failure abort all four primes."""


# ==========================================================================
# (ii) AUTHORIZED, DISCLOSED DUPLICATES of trapping_diagnostic_v5.py's own
#      inline logic (not separately importable from that file). PF-4 FIX
#      APPLIED: domain is every structural local minimum, WITHOUT v6's own
#      basin-eligible delta_map[v] > 1 restriction.
# ==========================================================================

def local_min_and_depth(v, delta_map, adjacency):
    """Returns (is_structural_local_min, depth) for vertex v, computed on
    delta_map (real or permuted). is_structural_local_min(v) := delta_map[v]
    <= min(delta_map[u] for u in adjacency[v]); depth(v) := min(delta_map[u]
    for u in adjacency[v]) - delta_map[v]. Restates
    trapping_diagnostic_v5.py's own missing-neighbour loud-raise guard for
    completeness (structurally unreachable given the required coverage
    assertion for the REAL delta_map; a permuted delta_map is defined over
    the identical vertex set by construction, so it cannot trigger this
    guard either)."""
    nbr_deltas = []
    for u in adjacency[v]:
        if u not in delta_map:
            raise PermutationNullControlError(
                "missing-neighbour guard (duplicated from "
                "trapping_diagnostic_v5.py): vertex %r has neighbour %r "
                "with no delta_map entry -- structurally unreachable given "
                "the required coverage assertion; signals a stale read or "
                "wrong prime, never a legitimate data gap" % (v, u))
        nbr_deltas.append(delta_map[u])
    m = min(nbr_deltas)
    is_min = bool(delta_map[v] <= m)
    depth = m - delta_map[v]
    return is_min, depth


def depth0_fraction(delta_map, vertices, adjacency):
    """The fraction of vertices satisfying is_structural_local_min(v) that
    ALSO satisfy depth(v) == 0, per the frozen spec's own text. Returns a
    dict with n_local_min, n_depth0, and fraction (None only in the
    mathematically-impossible-here case of zero local minima -- the
    globally-minimum-valued vertex is always <= every neighbour's value
    under any permutation of the SAME multiset, so n_local_min >= 1
    always; kept as an explicit guard, not assumed, and disclosed if ever
    reached)."""
    n_local_min = 0
    n_depth0 = 0
    for v in vertices:
        is_min, depth = local_min_and_depth(v, delta_map, adjacency)
        if is_min:
            n_local_min += 1
            if depth == 0:
                n_depth0 += 1
    fraction = (n_depth0 / float(n_local_min)) if n_local_min > 0 else None
    return {"n_local_min": n_local_min, "n_depth0": n_depth0,
            "fraction": fraction}


# ==========================================================================
# REQUIRED COVERAGE ASSERTION AND GRAPH-REBUILD VERIFICATION (PF-1 restored
# two-part check, PF-8 self-sufficient per-prime failure handling).
# ==========================================================================

def rebuild_and_verify(p, raw_result_path, graph_seed=GRAPH_SEED):
    """(i) build_graph_for_prime / load_archived_prime_data GENUINELY
    IMPORTED, UNCHANGED, from trapping_diagnostic_v5.py.
    (ii) the two-part coverage assertion / graph-rebuild verification below
    is an AUTHORIZED, DISCLOSED DUPLICATE of that file's own inline
    procedure (confirmed NOT separately importable -- both are inline in
    run_diagnostic_for_prime), restored to v6's own two-part formula per
    PF-1: (a) key-membership match against the rebuilt graph's actual
    vertex set; (b) degree_sequence_check.pass AND rebuilt vertex count ==
    archived n_vertices. EITHER failing halts ONLY this prime (PF-8)."""
    g, seed_info = tdv5.build_graph_for_prime(p, graph_seed)  # (i)
    archived = tdv5.load_archived_prime_data(raw_result_path, p)  # (i)
    delta_map = archived["delta_map"]
    archived_n_vertices = archived["archived_n_vertices"]
    archived_n_resolved = archived["archived_n_resolved"]

    if p in ARCHIVED_N_VERTICES and archived_n_vertices != ARCHIVED_N_VERTICES[p]:
        raise PermutationNullControlError(
            "archived n_vertices read from raw-result.json (%d) disagrees "
            "with this amendment's own pinned value (%d) for p=%d -- halt "
            "before computing anything further for this prime"
            % (archived_n_vertices, ARCHIVED_N_VERTICES[p], p))

    vertices = g["vertices"]
    adjacency = g["adjacency"]
    n_built = len(vertices)

    # (a) coverage assertion: key-membership match, NEVER a bare count.
    vertex_set = set(vertices)
    matched_vertices = [v for v in delta_map if v in vertex_set]
    n_matched = len(matched_vertices)
    coverage_assertion_pass = bool(n_matched == archived_n_vertices)

    # (b) graph-rebuild verification.
    degseq = big.degree_sequence_check(g)  # (i) genuine import
    degseq_pass = bool(degseq["pass"])
    vertex_count_match = bool(n_built == archived_n_vertices)

    if not coverage_assertion_pass:
        raise PermutationNullControlError(
            "REQUIRED COVERAGE ASSERTION FAILED for p=%d: %d of %d "
            "delta_map keys matched the rebuilt graph's vertex set "
            "(compared against archived n_vertices=%d, NEVER n_resolved=%d) "
            "-- halting ONLY this prime's computation"
            % (p, n_matched, len(delta_map), archived_n_vertices,
               archived_n_resolved))
    if not (degseq_pass and vertex_count_match):
        raise PermutationNullControlError(
            "GRAPH-REBUILD VERIFICATION FAILED for p=%d: "
            "degree_sequence_check.pass=%s, rebuilt vertex count %d == "
            "archived n_vertices %d? %s -- halting ONLY this prime's "
            "computation"
            % (p, degseq_pass, n_built, archived_n_vertices, vertex_count_match))

    graph_rebuild_independently_verified_correct = bool(
        degseq_pass and vertex_count_match and coverage_assertion_pass)

    return {
        "delta_map": delta_map,
        "archived_n_vertices": archived_n_vertices,
        "archived_n_resolved": archived_n_resolved,
        "graph": g,
        "vertices": vertices,
        "adjacency": adjacency,
        "seed_info": seed_info,
        "coverage_assertion": {
            "n_delta_map_keys_total": len(delta_map),
            "n_delta_map_keys_matched_against_rebuilt_graph": n_matched,
            "archived_n_vertices_comparison_target": archived_n_vertices,
            "archived_n_resolved_NOT_used_for_comparison": archived_n_resolved,
            "coverage_assertion_pass": coverage_assertion_pass,
        },
        "graph_rebuild_verification": {
            "degree_sequence_check": degseq,
            "n_built_vertices": n_built,
            "archived_n_vertices": archived_n_vertices,
            "vertex_count_match": vertex_count_match,
            "independently_verified_correct":
                graph_rebuild_independently_verified_correct,
        },
    }


# ==========================================================================
# Summary statistics -- POPULATION SD (divide by N_TRIALS, PF-3/PF-10).
# ==========================================================================

def summary_stats(values, n_trials):
    """values: list of n_trials floats (NULL_DEPTH0_FRACTIONS). Population
    standard deviation per PF-3/PF-10 (divide by N_TRIALS, not N_TRIALS-1),
    as a plain descriptive statistic of this run's own n_trials realized
    outcomes."""
    n = len(values)
    s = sorted(values)
    mean = sum(values) / float(n_trials)
    if n % 2 == 1:
        median = s[n // 2]
    else:
        median = 0.5 * (s[n // 2 - 1] + s[n // 2])
    sq_dev_sum = sum((x - mean) ** 2 for x in values)
    population_sd = math.sqrt(sq_dev_sum / float(n_trials))
    return {
        "n": n,
        "mean": mean,
        "median": median,
        "min": s[0],
        "max": s[-1],
        "population_standard_deviation": population_sd,
    }


# ==========================================================================
# Per-prime driver.
# ==========================================================================

def run_for_prime(p, raw_result_path=RUN_B_RAW_RESULT_RELPATH,
                   graph_seed=GRAPH_SEED, permutation_seed=PERMUTATION_SEED,
                   n_trials=N_TRIALS):
    rb = rebuild_and_verify(p, raw_result_path, graph_seed)
    delta_map = rb["delta_map"]
    vertices = rb["vertices"]
    adjacency = rb["adjacency"]

    # ---- (3) REAL_DEPTH0_FRACTION, on the REAL, unpermuted delta_map ------
    real_stats = depth0_fraction(delta_map, vertices, adjacency)
    real_depth0_fraction = real_stats["fraction"]

    expected_n_local_min = EXPECTED_REAL_N_LOCAL_MIN.get(p)
    materially_disagrees = False
    disagreement_reasons = []
    if real_depth0_fraction != EXPECTED_REAL_DEPTH0_FRACTION:
        materially_disagrees = True
        disagreement_reasons.append(
            "REAL_DEPTH0_FRACTION (%r) != expected 1.0"
            % (real_depth0_fraction,))
    if (expected_n_local_min is not None
            and real_stats["n_local_min"] != expected_n_local_min):
        materially_disagrees = True
        disagreement_reasons.append(
            "n_local_min (%d) != RUN-SSIQ-a85692-f's own archived ANOM-1 "
            "figure (%d) for p=%d"
            % (real_stats["n_local_min"], expected_n_local_min, p))

    anomaly = None
    if materially_disagrees:
        anomaly = {
            "id": "ANOM-REALDEPTH0-p%d" % p,
            "statement": (
                "REQUIRED, EXPLICITLY DISCLOSED anomaly per the frozen "
                "spec's own FAILURE-HANDLING SCOPE text: %s. This DOES NOT "
                "HALT OR SKIP this prime's NULL_DEPTH0_FRACTIONS "
                "computation -- the %d null trials below are computed and "
                "archived for this prime regardless."
                % ("; ".join(disagreement_reasons), n_trials)
            ),
        }

    # ---- (4) NULL_DEPTH0_FRACTIONS, N_TRIALS permutation trials -----------
    # A SINGLE, FRESHLY-CONSTRUCTED random.Random(PERMUTATION_SEED) instance,
    # constructed once per prime (here), advanced sequentially across all
    # n_trials trials via repeated .shuffle() calls on the SAME instance,
    # never re-seeded or reconstructed mid-prime.
    rng = random.Random(permutation_seed)
    base_values = list(delta_map.values())
    null_fractions = []
    null_n_local_min = []
    null_n_depth0 = []
    for _trial in range(n_trials):
        values = list(base_values)  # fresh copy of the SAME real multiset
        rng.shuffle(values)  # Fisher-Yates, using the persistent rng
        permuted_map = dict(zip(vertices, values))  # onto g["vertices"]
        stats = depth0_fraction(permuted_map, vertices, adjacency)
        null_fractions.append(stats["fraction"])
        null_n_local_min.append(stats["n_local_min"])
        null_n_depth0.append(stats["n_depth0"])

    n_none = sum(1 for f in null_fractions if f is None)
    if n_none:
        # Mathematically not expected to occur (the globally-minimum-valued
        # vertex is always a local minimum under any permutation of the
        # same multiset), but disclosed honestly rather than silently
        # dropped if it ever does.
        anomaly = anomaly or {}
        anomaly.setdefault("id", "ANOM-NULLNONE-p%d" % p)
        anomaly.setdefault("statement", "")
        anomaly["statement"] += (
            " ADDITIONALLY: %d of %d null trials produced an undefined "
            "depth0_fraction (zero local minima in that permuted trial), "
            "excluded from the summary statistics below and reported "
            "separately -- mathematically unexpected, since the "
            "globally-minimum-valued vertex is always a structural local "
            "minimum under any permutation, but disclosed rather than "
            "silently dropped." % (n_none, n_trials)
        )

    stat_input = [f for f in null_fractions if f is not None]
    # PF-3/PF-10: population SD divides by N_TRIALS. If n_none > 0 this
    # would make the divisor inconsistent with len(stat_input); the frozen
    # spec does not anticipate n_none > 0 (see guard above), so this
    # divides by n_trials as specified, using only the defined values in
    # the numerator sums -- disclosed via the anomaly above if it is ever
    # nonzero (not expected to occur on this run's actual data).
    stats_summary = summary_stats(stat_input, n_trials) if stat_input else None

    null_exceeds_or_equals_real_count = sum(
        1 for f in null_fractions
        if f is not None and f >= real_depth0_fraction)

    return {
        "prime": p,
        "graph_seed_used": graph_seed,
        "permutation_seed_used": permutation_seed,
        "n_trials": n_trials,
        "seed_construction": rb["seed_info"],
        "coverage_assertion": rb["coverage_assertion"],
        "graph_rebuild_verification": rb["graph_rebuild_verification"],
        "real_depth0_fraction": {
            "n_vertices": len(vertices),
            "n_structural_local_min": real_stats["n_local_min"],
            "n_depth0": real_stats["n_depth0"],
            "fraction": real_depth0_fraction,
            "expected_fraction": EXPECTED_REAL_DEPTH0_FRACTION,
            "expected_n_local_min_ref_run_f_anom1": expected_n_local_min,
            "materially_disagrees_with_expectation": materially_disagrees,
        },
        "null_depth0_fractions": null_fractions,
        "null_n_local_min": null_n_local_min,
        "null_n_depth0": null_n_depth0,
        "null_summary_statistics": stats_summary,
        "null_n_undefined_trials_excluded": n_none,
        "null_exceeds_or_equals_real_count": null_exceeds_or_equals_real_count,
        "anomaly": anomaly,
        "objective_boundary": (
            "This is a CONTROL, formalizing an already-run analysis for "
            "the durable record -- it does not itself constitute a new "
            "claim, does not test H-SSIQ-36e970's real-arm prediction, and "
            "does not gate any decision rule."
        ),
    }


def run_all(raw_result_path=RUN_B_RAW_RESULT_RELPATH, graph_seed=GRAPH_SEED,
            permutation_seed=PERMUTATION_SEED, n_trials=N_TRIALS,
            primes=PRIMES_V7):
    per_prime = {}
    errors = {}
    for p in primes:
        try:
            per_prime[p] = run_for_prime(
                p, raw_result_path=raw_result_path, graph_seed=graph_seed,
                permutation_seed=permutation_seed, n_trials=n_trials)
        except PermutationNullControlError as e:
            errors[p] = str(e)
    return per_prime, errors


# ==========================================================================
# CLI entry point / this run's own artifact writer.
# ==========================================================================

def git_state():
    def g(*a):
        try:
            return subprocess.check_output(
                ["git"] + list(a), stderr=subprocess.DEVNULL,
                cwd=_THIS_DIR).decode().strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"),
            "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True,
                     help="output directory for this run's artifacts")
    ap.add_argument("--raw-result-b", default=RUN_B_RAW_RESULT_RELPATH,
                     help="path to RUN-SSIQ-a85692-b/raw-result.json "
                          "(READ ONLY, source of the shared delta_map)")
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (specification_v7.yaml)" % (started, EXPERIMENT_ID, RUN_ID))
    log("delta_e_permutation_null_control_v7: primes=%s N_TRIALS=%d "
        "GRAPH_SEED=%d PERMUTATION_SEED=%d"
        % (PRIMES_V7, N_TRIALS, GRAPH_SEED, PERMUTATION_SEED))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    per_prime, errors = run_all(raw_result_path=args.raw_result_b)

    for p in PRIMES_V7:
        if p in errors:
            log("  p=%-6d HALTED (per-prime): %s" % (p, errors[p]))
            continue
        r = per_prime[p]
        rd = r["real_depth0_fraction"]
        log("  p=%-6d n_vertices=%-5d n_local_min=%-4d real_depth0_fraction=%s "
            "materially_disagrees=%s null_exceeds_or_equals_real_count=%d/%d"
            % (p, rd["n_vertices"], rd["n_structural_local_min"], rd["fraction"],
               rd["materially_disagrees_with_expectation"],
               r["null_exceeds_or_equals_real_count"], r["n_trials"]))
        s = r["null_summary_statistics"]
        if s:
            log("    NULL summary: mean=%.6f median=%.6f min=%.6f max=%.6f "
                "population_sd=%.6f"
                % (s["mean"], s["median"], s["min"], s["max"],
                   s["population_standard_deviation"]))

    permutation_null_control_payload = {
        "primes": PRIMES_V7,
        "n_trials": N_TRIALS,
        "graph_seed": GRAPH_SEED,
        "permutation_seed": PERMUTATION_SEED,
        "per_prime": {str(p): per_prime[p] for p in per_prime},
        "per_prime_errors": {str(p): errors[p] for p in errors},
        "n_primes_completed": len(per_prime),
        "n_primes_halted": len(errors),
        "failure_handling_model": (
            "PER-PRIME (this amendment's own explicit choice, PF-8): the "
            "coverage assertion / graph-rebuild verification is a per-prime "
            "halt, reported in per_prime_errors; other primes proceed "
            "normally. The REAL_DEPTH0_FRACTION-materially-disagrees "
            "anomaly branch NEVER halts anything (PF-2): a prime's 1000 "
            "null trials are always computed and archived regardless of "
            "whether REAL_DEPTH0_FRACTION matches its expected value."
        ),
        "objective_boundary": (
            "This is a CONTROL, formalizing an already-run analysis for "
            "the durable record -- it does not itself constitute a new "
            "claim, does not test H-SSIQ-36e970's real-arm prediction, "
            "does not gate any decision rule, and does not resolve the "
            "funnel-structure mechanism question. Scale: toy, graph sizes "
            "203-611 vertices; no result transfers to cryptographic scale."
        ),
    }
    pnc_out_path = os.path.join(run_dir, "permutation_null_control.json")
    with open(pnc_out_path, "w") as fh:
        json.dump(permutation_null_control_payload, fh, indent=1,
                   sort_keys=True, default=str)

    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    raw_result_payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "spec_version": SPEC_VERSION,
        "started_utc": started,
        "finished_utc": finished,
        "wall_clock_seconds": time.time() - t0,
        "git": git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "certificate": {
            "kind": "none",
            "reason": (
                "Pure measurement/control run: a label-permutation null "
                "control over already-committed delta_E data. No discrete "
                "log is claimed, no factor-base relation is claimed, no "
                "isogeny problem instance is solved. "
                "docs/claims-and-verification.md requires kind: none to be "
                "stated explicitly for such runs."
            ),
        },
        "delta_e_permutation_null_control_v7": {
            "artifact": "permutation_null_control.json",
            "primes": PRIMES_V7,
            "n_trials": N_TRIALS,
            "graph_seed": GRAPH_SEED,
            "permutation_seed": PERMUTATION_SEED,
            "n_primes_completed": len(per_prime),
            "n_primes_halted": len(errors),
            "per_prime_summary": {
                str(p): {
                    "n_vertices": per_prime[p]["real_depth0_fraction"]["n_vertices"],
                    "n_structural_local_min":
                        per_prime[p]["real_depth0_fraction"]["n_structural_local_min"],
                    "real_depth0_fraction":
                        per_prime[p]["real_depth0_fraction"]["fraction"],
                    "materially_disagrees_with_expectation":
                        per_prime[p]["real_depth0_fraction"]["materially_disagrees_with_expectation"],
                    "null_summary_statistics": per_prime[p]["null_summary_statistics"],
                    "null_exceeds_or_equals_real_count":
                        per_prime[p]["null_exceeds_or_equals_real_count"],
                    "anomaly": per_prime[p]["anomaly"],
                } for p in per_prime
            },
            "per_prime_errors": errors,
        },
        "objective_boundary": (
            "This is a CONTROL, formalizing an already-run analysis "
            "(BATCH-009's own informal 30-trial and 15-trial runs) for the "
            "durable record. It does not itself constitute a new claim, "
            "does not test H-SSIQ-36e970's real-arm prediction, does not "
            "gate any decision rule, and does not resolve the "
            "funnel-structure mechanism question (DEC-20260806-498531's "
            "own next_actions item (2), deferred). Scale: toy, graph sizes "
            "203-611 vertices; no result transfers to cryptographic scale."
        ),
        "scale_qualifier": "toy; N (graph size) in [203, 611]",
    }
    raw_result_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_result_path, "w") as fh:
        json.dump(raw_result_payload, fh, indent=1, sort_keys=True, default=str)
    log("wrote %s and %s (%.2fs total)"
        % (raw_result_path, pnc_out_path, time.time() - t0))

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
