#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v11 (BATCH-014) -- delta_e_floor_straddling_sweep_v11.

Implements experiments/EXP-SSIQ-a85692/specification_v11.yaml
amendment_scope, inputs.load_defer_gate_v11, inputs.floor_calibration_set_v11
and inputs.mixed_regime_sweep_search_v11 EXACTLY as frozen (version 11,
frozen_at 2026-08-07, approved_by coordinator, approved_under
DEC-20260808-c2a470). PART A ONLY, TWO INDEPENDENT budget passes
(SWEEP_BUDGETS = [1.1, 1.45] seconds/vertex) over ONE SHARED, ONCE-BUILT
p=2437 graph, PRECEDED BY A MANDATORY HOST-IDENTITY AND FLOOR-CALIBRATION
STEP (step (0b)) that gates whether the sweep runs at all.

REUSE / DUPLICATION SPLIT, DISCLOSED EXPLICITLY (matches
required_artifacts_note's own (i)/(ii) split):
  (i)  GENUINELY IMPORTED, UNCHANGED: delta_e_truncation_probe_v9.
       run_truncation_probe_v9 (three call sites: CAL-1 on the
       vertex-restricted shallow copy, and once per sweep budget on the
       full graph), delta_e_truncation_probe_v9.parse_v8_new_delta_map,
       delta_e_truncation_probe_v9.compare_against_archived,
       delta_e_truncation_probe_v9.compare_against_v8;
       trapping_diagnostic_v5.build_graph_for_prime,
       trapping_diagnostic_v5.load_archived_prime_data;
       delta_e_independent_rng_probe_v8.verify_graph_identity (once, step
       (0)) and delta_e_independent_rng_probe_v8.derive_per_vertex_seed
       (CAL-2's fresh RNG ONLY -- CAL-1 no longer calls it directly, since
       run_truncation_probe_v9 derives its own seeds internally);
       compute_delta_e.build_smooth_table, compute_delta_e.L_PRIMES,
       compute_delta_e.X_LIST_BOUND (CAL-2 ONLY, never in the sweep loop);
       delta_e_truncation_sweep_v10.value_histogram_and_conjugate_pairs
       (the FIRST reuse of a v10-defined function in this lineage, called
       TWICE per sweep point).
  (ii) AUTHORIZED, DISCLOSED DUPLICATES (new code this file writes): the
       step (0b) portable host capture (platform.platform(),
       platform.machine(), sys.version, os.cpu_count(), os.getloadavg()
       wrapped against OSError); the floor-calibration driver (CAL-1 as a
       single call to the frozen run_truncation_probe_v9 on a
       vertex-restricted shallow copy, preceded by the required THE_EIGHT
       assertions, plus the CAL-2 build_smooth_table loop -- NO duplicated
       search loop, per PF-18's fix); the pre-registered defer-gate
       evaluator (G-0c, G-0, G-0b, G-1, G-2, G-2b, G-3, on the frozen
       thresholds, never recomputed at runtime) and the load-adjusted-
       predicted-count computation it needs; the sweep-loop driver
       (iterating SWEEP_BUDGETS, calling run_truncation_probe_v9 once per
       budget on the FULL graph inside a per-sweep-point try/except); the
       per-sweep-point Comparison 1 / Comparison 2 driver; the
       mixed-regime natural-completion cross-check plus the PF-16
       population counting and identity assertions; and the final-pop
       overshoot summary at b = 1.10 s. Also a small vertex_json_safe /
       delta_map_json_safe pair (identical in kind to git_state(), an
       authorized, disclosed duplicate of the same trivial one-liner
       pattern v8/v9/v10 each already established -- the ONLY
       discretionary duplicate anywhere in this amendment) and a small
       git_state() helper.

NOTE: compute_delta_e.two_sided_search is NOT imported directly anywhere in
this module; PF-18's shallow-copy CAL-1 removed the only call site the
round-2 draft had for it, and in the sweep that call lives inside the
genuinely-imported run_truncation_probe_v9. hw.ncpu IS NOT USED ANYWHERE
(PF-26): it is a macOS/BSD sysctl key, absent on Linux, mentioned in this
codebase only in specification_v11.yaml's own PF-26 narrative.

STEP (0) FAILURE MODE (identical discipline to v10's PF-10, applied here
unchanged): the graph rebuild (trapping_diagnostic_v5.build_graph_for_prime)
and the two-part graph-identity re-verification
(delta_e_independent_rng_probe_v8.verify_graph_identity) run EXACTLY ONCE,
BEFORE step (0b) and BEFORE the sweep loop, and are NOT wrapped in any
try/except. If either raises, the exception propagates UNCAUGHT and this run
terminates with NO truncation_sweep_comparison.json written at all -- an
infra/setup failure under AGENTS.md rule 3 (the frozen specification's own
citation; this repository's own AGENTS.md currently numbers the identical
"a timeout/crash/implementation failure is not evidence against a
mathematical hypothesis" principle as rule 5 -- a citation-numbering drift
between the frozen spec text and the live AGENTS.md file, disclosed here
rather than silently reconciled, and NOT a reason to edit the frozen spec
text), never negative mathematical evidence and never recorded as a
sweep_point_error for any budget.

STEP (0b) ORDERING, DISCLOSED INTERPRETATION (the frozen spec does not
explicitly resolve this, so the choice is stated rather than silently
made, per this lineage's own established HONESTY RULE pattern, e.g. v9's
PD-3 domain disclosure): G-0c is evaluated using ONLY the step (0b) host
capture and RUN-h's already-committed environment.json, and it GATES
whether CAL-1/CAL-2 run at all -- CAL-1 and CAL-2 are each real, costly
measurements (up to 120.0s and 16.0s worst case) that G-0c's own text
introduces with "FIRST, BEFORE ANY CALIBRATION IS INTERPRETED", and the
required artifact behaviour text for a defer explicitly allows for "the
full CAL-1/CAL-2 records to whatever extent they exist" -- language that is
only meaningful if a G-0c defer can occur with zero calibration records.
This is the economically sensible reading (why spend up to 136s of
calibration compute once the host is already known to differ?) and matches
the dispatching Coordinator's own handoff, which lists G-0c ahead of "any of
the 8 CAL-1 calibration vertices timing out" in its evaluation order. If
G-0c does not fire, CAL-1 runs and gates G-0; if G-0 does not fire, CAL-2
runs and gates G-0b; and so on down the cascade, in the exact order the
frozen gate text specifies.

PER-SWEEP-POINT FAILURE ISOLATION (identical PF-2 discipline to v10): each
sweep point's ENTIRE bundle (PART A search + both required comparisons +
both histogram/conjugate-pair calls + the mixed-regime cross-check) is
wrapped in its own try/except. Any exception there is caught, recorded as a
sweep_point_error string for that budget alone, and the loop continues.
Step (0b)'s host capture and calibration are OUTSIDE this per-sweep-point
isolation; their failure modes are governed by load_defer_gate_v11, never by
a sweep_point_error.

JSON SAFETY (inherited unchanged from v8/v9/v10): every vertex-keyed
artifact output uses the str(list(v))-keyed convention; a raw tuple is
never written directly as a JSON dict key.

OBJECTIVE_BOUNDARY: this is a purely DESCRIPTIVE DIAGNOSTIC CONTROL, not a
claim. It does not test H-SSIQ-36e970's real-arm prediction, does not gate
any decision rule, and does not itself constitute evidence for or against a
computable delta_E-gradient or a p^{1/4} algorithm. It does not produce a
PERSISTS/WEAKENS label. Scoped to p=2437 ONLY. It does NOT answer
RT-BATCH-011's original truncation-boundary question. It does NOT, under
ANY outcome, establish or refute that "delta_E >= 5 convergence begins at
the floor" (reading rule P-4). Per PF-25 the equality half of the
mixed-regime cross-check is an INSTRUMENT-INTEGRITY CONTROL, not a
measurement. Per PF-27 the archived-derived counts are REFERENCE COUNTS
WITH TWO-SIDED CORRECTIONS, not upper bounds. Per PF-26 every archived
figure is a 4-CPU x86_64 Linux measurement, transferring only to a matched
host, which gate G-0c enforces.
"""

import argparse
import json
import math
import os
import platform
import random
import statistics
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
# it. Neither frozen file is modified here.
import calibration_synthetic as cal  # noqa: E402,F401 (import-order fix only)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED --
                         # (i) genuine-import source for
                         # build_graph_for_prime / load_archived_prime_data)
import delta_e_independent_rng_probe_v8 as v8probe  # noqa: E402  (FROZEN,
                         # UNCHANGED -- (i) genuine-import source for
                         # verify_graph_identity and derive_per_vertex_seed
                         # (CAL-2 only). Its own driver functions are NOT
                         # called anywhere in this file.)
import delta_e_truncation_probe_v9 as v9probe  # noqa: E402  (FROZEN,
                         # UNCHANGED -- (i) genuine-import source for
                         # run_truncation_probe_v9, parse_v8_new_delta_map,
                         # compare_against_archived, compare_against_v8.
                         # Its own main()/CLI entry point is NOT called
                         # anywhere in this file.)
import delta_e_truncation_sweep_v10 as v10sweep  # noqa: E402  (FROZEN,
                         # UNCHANGED -- (i) genuine-import source for
                         # value_histogram_and_conjugate_pairs, the FIRST
                         # reuse of a v10-defined function in this lineage.
                         # Its own main()/CLI entry point is NOT called
                         # anywhere in this file.)
import compute_delta_e  # noqa: E402  (FROZEN, UNCHANGED -- (i) genuine-
                         # import source for build_smooth_table, L_PRIMES,
                         # X_LIST_BOUND -- CAL-2 ONLY, never in the sweep
                         # loop, which reaches two_sided_search only
                         # indirectly through run_truncation_probe_v9.)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-k"
SPEC_VERSION = 11

PRIME = 2437
ARCHIVED_N_VERTICES = 203
ARCHIVED_N_NON_FP_RATIONAL = 194
ARCHIVED_N_FP_RATIONAL = ARCHIVED_N_VERTICES - ARCHIVED_N_NON_FP_RATIONAL  # 9

GRAPH_SEED = 20260805      # SEEDS[0], the pinned graph-construction seed
                           # every amendment since v5 has used.
BASE_SEED = 20260811       # IDENTICAL constant v8/v9/v10 all used
                           # (deliberate reuse: isolates budget as the sole
                           # manipulated variable across this lineage).

SWEEP_BUDGETS = [1.1, 1.45]  # FIXED, PRE-REGISTERED list (PF-17's fix),
                              # never computed or adjusted at runtime, and
                              # never derived from the calibration.

CAL1_BUDGET_SECONDS = 15.0   # the RUN-h reference budget
CAL2_BUDGET_SECONDS = 2.0

A_ARCHIVED_FLOOR = 1.149932861328125  # RUN-h's own archived minimum,
                                       # attained by [749, 1684].
G1_THRESHOLD_SECONDS = 1.45           # DEFINED as the largest sweep budget
                                       # (PF-17's move from 1.4 to 1.45).
G2_THRESHOLD_LITERAL = 1.32242279052734375  # FROZEN LITERAL == 1.15 * A as
                                       # a rational; MUST NOT be evaluated
                                       # as 1.15 * A at runtime (one ULP
                                       # apart in IEEE-754 double).
G2B_THRESHOLD_COUNT = 58              # == 0.5 * 115, P-1/P-2's own frozen
                                       # boundary (PF-29(a)'s fix).

# ==========================================================================
# floor_calibration_set_v11: THE EIGHT SMALLEST archived wall_seconds among
# RUN-SSIQ-a85692-h's 194 per_vertex_records, FIXED AND NAMED BY COORDINATE
# in the frozen specification text so the set cannot be chosen, extended or
# trimmed after the fact. Independently re-verified against
# RUN-SSIQ-a85692-h/probe_delta_e_comparison.json by THIS Executor before
# writing this module (a further, fifth, independent recomputation in this
# lineage's own history of re-verifying this exact set).
# ==========================================================================
THE_EIGHT = (
    (749, 1684), (749, 753), (360, 1897), (360, 540),
    (817, 445), (2154, 970), (697, 105), (2405, 1073),
)
ARCHIVED_FLOOR_CAL_SET = {
    (749, 1684): {"archived_wall_seconds": 1.149932861328125, "archived_delta_E": 2},
    (749, 753): {"archived_wall_seconds": 1.1633622646331787, "archived_delta_E": 2},
    (360, 1897): {"archived_wall_seconds": 1.257300853729248, "archived_delta_E": 3},
    (360, 540): {"archived_wall_seconds": 1.2623295783996582, "archived_delta_E": 3},
    (817, 445): {"archived_wall_seconds": 1.2640187740325928, "archived_delta_E": 2},
    (2154, 970): {"archived_wall_seconds": 1.2711119651794434, "archived_delta_E": 2},
    (697, 105): {"archived_wall_seconds": 1.2978770732879639, "archived_delta_E": 3},
    (2405, 1073): {"archived_wall_seconds": 1.314664602279663, "archived_delta_E": 2},
}

# ==========================================================================
# pre_registered_prediction_curve_v11: FROZEN, copied verbatim from
# specification_v11.yaml inputs.pre_registered_prediction_curve_v11 and
# inputs.delta_e_ge_5_inclusion_rule_v11. NOT recomputed at runtime -- this
# is the pre-registered reference this run's own measurements (if the gate
# ever reaches the sweep) are read against, and it must be reproduced
# byte-for-byte in any artifact that requires it, including a deferred one.
# ==========================================================================
PRE_REGISTERED_REFERENCE_CURVE_V11 = {
    "provenance": (
        "Derived entirely from RUN-SSIQ-a85692-h's committed archived "
        "per-vertex wall_seconds under "
        "inputs.delta_e_ge_5_inclusion_rule_v11, frozen in "
        "specification_v11.yaml before any RUN-SSIQ-a85692-k execution. "
        "THESE ARE REFERENCE COUNTS, NOT UPPER BOUNDS (PF-27): each carries "
        "a DOWNWARD correction (the 0.725s source-side cap at b=1.45s, "
        "unquantifiable from the archive) and an UPWARD correction (the "
        "final-pop straddle, crudely boundable from archived density)."
    ),
    "transferability_note": (
        "These figures are 4-CPU x86_64 Linux measurements and transfer "
        "only to a matched execution host. Gate G-0c defers the run if the "
        "host does not match; nothing in this curve is asserted about an "
        "unmatched host."
    ),
    "b_1_10": {
        "reference_n_naturally_completed": 0,
        "reference_naturally_completed_histogram": {},
        "reference_delta_E_ge_5_count": 0,
        "conditions": (
            "Exact under two stated conditions: (i) execution host not "
            "FASTER than the archived host (G-0c enforces by measurement); "
            "(ii) final-pop slack does not exceed "
            "1.149932861328125 - 1.10 = 0.04993... s (49.93 ms)."
        ),
    },
    "b_1_45": {
        "reference_n_naturally_completed": 115,
        "reference_delta_E_ge_5_count": 36,
        "reference_delta_E_ge_5_histogram": {"5": 20, "6": 4, "7": 6, "8": 6},
        "reference_delta_E_5_count": 20,
        "reference_remainder_count": 79,
        "reference_remainder_split": {"2": 28, "3": 43, "4": 8},
        "source_side_cap_seconds": 0.725,
        "upward_correction_band": {
            "10ms_slack_count": 133,
            "50ms_slack_count": 186,
        },
        "P1_P2_boundary_measured_n_naturally_completed": 58,
        "P3d_band_115_lt_measured_le_133": (
            "Fully consistent with identical hardware, identical load, and "
            "every premise of this amendment intact -- the code's own "
            "documented behaviour, no explanation required beyond the "
            "instrument."
        ),
    },
    "full_population_at_1_70": {
        "reference_n_naturally_completed": 194,
        "reference_delta_E_ge_5_count": 80,
        "reference_delta_E_5_count": 42,
        "full_value_histogram": {"2": 34, "3": 70, "4": 10, "5": 42, "6": 10, "7": 16, "8": 12},
    },
    "min_archived_wall_seconds_whole_population": 1.149932861328125,
    "min_archived_wall_seconds_delta_E_ge_5": 1.3924050331115723,
    "max_archived_wall_seconds_whole_population": 1.6985499858856201,
}

RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")
RUN_H_COMPARISON_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-h", "probe_delta_e_comparison.json")
RUN_H_ENVIRONMENT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-h", "environment.json")


class FloorStraddlingSweepError(RuntimeError):
    """Raised on a genuinely unanticipated halt condition this frozen
    contract does not itself specify a recovery path for."""


# ==========================================================================
# STEP (0b), part (a): PORTABLE HOST CAPTURE (PF-26's fix).
# ==========================================================================

def host_capture():
    """platform.platform(), platform.machine(), sys.version,
    os.cpu_count(), os.getloadavg() -- the last wrapped against OSError and
    recorded as null WITH A REASON STRING on failure, never as 0.0."""
    cap = {
        "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform_platform": platform.platform(),
        "platform_machine": platform.machine(),
        "sys_version": sys.version,
        "os_cpu_count": os.cpu_count(),
    }
    try:
        la = os.getloadavg()
        cap["os_getloadavg_1_5_15"] = [la[0], la[1], la[2]]
        cap["os_getloadavg_unavailable_reason"] = None
    except OSError as e:
        cap["os_getloadavg_1_5_15"] = None
        cap["os_getloadavg_unavailable_reason"] = "%s: %s" % (
            type(e).__name__, str(e))
    return cap


def read_archived_host_from_run_h(env_path):
    """Reads RUN-SSIQ-a85692-h's own committed environment.json platform
    and cpus_available fields, READ ONLY, never assumed and never taken
    from this module's own text (PF-26's fix)."""
    try:
        with open(env_path) as fh:
            data = json.load(fh)
    except Exception as e:  # noqa: BLE001 -- any read failure must DEFER,
                             # per G-0c's "if unreadable, defer" clause.
        return {"platform": None, "cpus_available": None,
                "read_error": "%s: %s" % (type(e).__name__, str(e))}
    return {"platform": data.get("platform"),
            "cpus_available": data.get("cpus_available"),
            "read_error": None}


def evaluate_g0c(host_cap, archived_host):
    """load_defer_gate_v11, branch G-0c. DEFERS if RUN-k's platform family
    or ISA differs from RUN-h's, or RUN-k's os.cpu_count() differs from
    RUN-h's recorded cpus_available, or RUN-h's cpus_available cannot be
    read at all. A differing kernel patch level or glibc minor version
    ALONE is not a mismatch."""
    archived_cpus = archived_host.get("cpus_available")
    archived_platform = archived_host.get("platform")
    measured_platform = host_cap["platform_platform"]
    measured_machine = host_cap["platform_machine"]
    measured_cpu_count = host_cap["os_cpu_count"]

    if archived_host.get("read_error") is not None or archived_cpus is None:
        return {
            "fired": True,
            "reason": (
                "RUN-h's cpus_available could not be read from its "
                "archived environment.json (%s) -- deferring rather than "
                "assuming, per G-0c's explicit instruction."
                % (archived_host.get("read_error") or "field absent/null")
            ),
            "archived_platform": archived_platform,
            "archived_cpus_available": archived_cpus,
            "measured_platform": measured_platform,
            "measured_machine": measured_machine,
            "measured_cpu_count": measured_cpu_count,
        }

    mismatches = []
    if not measured_platform.startswith("Linux"):
        mismatches.append(
            "platform.platform() = %r does not begin with 'Linux' "
            "(archived host platform: %r)"
            % (measured_platform, archived_platform))
    if measured_machine != "x86_64":
        mismatches.append(
            "platform.machine() = %r != 'x86_64' (archived host ISA, "
            "read from its platform string %r)"
            % (measured_machine, archived_platform))
    if measured_cpu_count != archived_cpus:
        mismatches.append(
            "os.cpu_count() = %r != RUN-h's recorded cpus_available = %r"
            % (measured_cpu_count, archived_cpus))

    fired = bool(mismatches)
    return {
        "fired": fired,
        "reason": ("; ".join(mismatches) if fired else
                    "host matches archived host on OS family, ISA and CPU "
                    "count (a differing kernel patch level or glibc minor "
                    "version alone would not be a mismatch, but none was "
                    "checked here since none of the three compared fields "
                    "differed)"),
        "archived_platform": archived_platform,
        "archived_cpus_available": archived_cpus,
        "measured_platform": measured_platform,
        "measured_machine": measured_machine,
        "measured_cpu_count": measured_cpu_count,
    }


# ==========================================================================
# STEP (0b), part (b): CAL-1 (measured floor). PF-18's fix: a SINGLE call
# to the frozen run_truncation_probe_v9, UNCHANGED, on a vertex-restricted
# shallow copy. NO duplicated search loop.
# ==========================================================================

def run_cal1(graph):
    assert len(THE_EIGHT) == 8, (
        "THE_EIGHT must contain exactly 8 coordinates (round-3 required "
        "control)")
    assert set(THE_EIGHT) <= set(graph["vertices"]), (
        "THE_EIGHT is not a subset of graph['vertices'] -- a tuple/list "
        "representation mismatch; failing loudly per the round-3 required "
        "control rather than silently producing a vacuous calibration that "
        "resolves 0 of 0")
    cal_graph = {**graph, "vertices": THE_EIGHT}  # a NEW dict; the real
                                                   # graph object is never
                                                   # mutated.
    result = v9probe.run_truncation_probe_v9(
        cal_graph, BASE_SEED, CAL1_BUDGET_SECONDS)
    records = []
    for rec in result["per_vertex_records"]:
        v = tuple(rec["vertex"])
        archived = ARCHIVED_FLOOR_CAL_SET[v]
        arch_wall = archived["archived_wall_seconds"]
        ratio = (rec["wall_seconds"] / arch_wall) if arch_wall else None
        records.append({
            "vertex": list(v),
            "measured_wall_seconds": rec["wall_seconds"],
            "timed_out": bool(rec["timed_out"]),
            "resolved": bool(rec["resolved"]),
            "delta_e_upper_bound": rec["delta_e_upper_bound"],
            "archived_wall_seconds": arch_wall,
            "archived_delta_E": archived["archived_delta_E"],
            "measured_over_archived_ratio": ratio,
        })
    return {"records": records, "n_attempted": result["n_attempted"],
            "n_resolved": result["n_resolved"],
            "n_timed_out": result["n_timed_out"],
            "coverage_fraction_over_8": result["coverage_fraction"]}


# ==========================================================================
# STEP (0b), part (c): CAL-2 (measured source-side split). An INDEPENDENT
# measurement (fresh RNG), NOT a decomposition of CAL-1.
# ==========================================================================

def run_cal2(graph, cal1_records_by_vertex):
    field = graph["field"]
    q = graph["q"]
    records = []
    for v in THE_EIGHT:
        seed_v = v8probe.derive_per_vertex_seed(BASE_SEED, v)
        rng_v2 = random.Random(seed_v)
        t0 = time.time()
        table, n_phi_calls, timed_out = compute_delta_e.build_smooth_table(
            field, v, rng_v2, q, compute_delta_e.L_PRIMES,
            compute_delta_e.X_LIST_BOUND, CAL2_BUDGET_SECONDS, None)
        t_source_measured = time.time() - t0
        cal1_total = cal1_records_by_vertex.get(v, {}).get(
            "measured_wall_seconds")
        measured_source_fraction = (
            (t_source_measured / cal1_total) if cal1_total else None)
        records.append({
            "vertex": list(v),
            "t_source_measured": t_source_measured,
            "timed_out": bool(timed_out),
            "table_source_entries": len(table),
            "n_phi_calls": n_phi_calls,
            "cal1_measured_total_same_vertex": cal1_total,
            "measured_source_fraction": measured_source_fraction,
        })
    return records


# ==========================================================================
# STEP (0b), part (d): the pre-registered defer/abort gate, evaluated IN
# ORDER: G-0c (above), G-0, G-0b, G-1, G-2, G-2b, G-3.
# ==========================================================================

def evaluate_g0(cal1_records):
    if len(cal1_records) < 8:
        return {"fired": True,
                "reason": "fewer than 8 CAL-1 records were produced (%d)"
                          % len(cal1_records)}
    timed_out_vertices = [r["vertex"] for r in cal1_records if r["timed_out"]]
    if timed_out_vertices:
        return {"fired": True,
                "reason": ("CAL-1 timed_out=True at the %.1fs budget for: "
                           "%s" % (CAL1_BUDGET_SECONDS, timed_out_vertices)),
                "timed_out_vertices": timed_out_vertices}
    return {"fired": False,
            "reason": "all 8 CAL-1 records present and non-timed-out"}


def evaluate_g0b(cal2_records):
    timed_out_vertices = [r["vertex"] for r in cal2_records if r["timed_out"]]
    if timed_out_vertices:
        return {"fired": True,
                "reason": ("CAL-2 source-side build timed_out=True at the "
                           "%.1fs cap for: %s"
                           % (CAL2_BUDGET_SECONDS, timed_out_vertices)),
                "timed_out_vertices": timed_out_vertices}
    return {"fired": False,
            "reason": "all 8 CAL-2 source-side builds completed within the "
                       "%.1fs cap" % CAL2_BUDGET_SECONDS}


def compute_f_cal(cal1_records):
    non_timed_out = [r["measured_wall_seconds"] for r in cal1_records
                      if not r["timed_out"]]
    if not non_timed_out:
        return None
    return min(non_timed_out)


def evaluate_g1(f_cal):
    if f_cal is None:
        return {"fired": True,
                "reason": "F_cal is undefined (no non-timed-out CAL-1 "
                           "record) -- treated as a defer"}
    fired = f_cal >= G1_THRESHOLD_SECONDS
    return {"fired": fired, "f_cal": f_cal,
            "reason": ("F_cal (%.15f) >= %.2f (the largest sweep budget)"
                       % (f_cal, G1_THRESHOLD_SECONDS) if fired else
                       "F_cal (%.15f) < %.2f"
                       % (f_cal, G1_THRESHOLD_SECONDS))}


def compute_measured_load_inflation_ratio(cal1_records):
    """Median of CAL-1's measured/archived ratios OVER NON-TIMED-OUT
    VERTICES ONLY (PF-29(b), for symmetry with F_cal)."""
    ratios = [r["measured_over_archived_ratio"] for r in cal1_records
              if not r["timed_out"] and r["measured_over_archived_ratio"]
              is not None]
    if not ratios:
        return None
    return statistics.median(ratios)


def load_archived_per_vertex_wall_seconds(run_h_comparison_path):
    """Reads RUN-SSIQ-a85692-h's own 194 archived per-vertex wall_seconds
    (NOT the same file/field tdv5.load_archived_prime_data or
    v9probe.parse_v8_new_delta_map read -- this is new code reading a third
    field of the same already-committed file, authorized under
    required_artifacts_note (iii)'s "load-adjusted-predicted-count
    computation" clause)."""
    with open(run_h_comparison_path) as fh:
        data = json.load(fh)
    return [rec["wall_seconds"] for rec in data["per_vertex_records"]]


def compute_lac(median_ratio, archived_wall_seconds_list, budgets):
    """LOAD-ADJUSTED PREDICTED COUNT (LAC), PF-23/PF-29(a). NULL WITH A
    REASON STRING if the median ratio is undefined -- never 0."""
    if median_ratio is None:
        return {str(b): {"value": None,
                          "reason": "undefined: fewer than one "
                                     "non-timed-out CAL-1 record"}
                for b in budgets}
    out = {}
    for b in budgets:
        count = sum(1 for w in archived_wall_seconds_list
                    if w * median_ratio < b)
        out[str(b)] = {"value": count, "reason": None}
    return out


def evaluate_g2_g2b_g3(f_cal, lac_at_1_45):
    g2_fired = f_cal > G2_THRESHOLD_LITERAL
    g2b_fired = False
    g2b_reason = None
    if lac_at_1_45 is not None and lac_at_1_45.get("value") is not None:
        g2b_fired = lac_at_1_45["value"] < G2B_THRESHOLD_COUNT
        g2b_reason = ("LAC at b=1.45s = %d (%s %d)"
                       % (lac_at_1_45["value"],
                          "<" if g2b_fired else ">=", G2B_THRESHOLD_COUNT))
    load_confounded = bool(g2_fired or g2b_fired)
    if g2_fired:
        branch = "G-2"
    elif g2b_fired:
        branch = "G-2b"
    else:
        branch = "G-3"
    return {
        "branch": branch,
        "load_confounded": load_confounded,
        "g2_fired": g2_fired,
        "g2_reason": ("F_cal (%.15f) > %.15f (1.15x archived floor "
                      "tolerance, frozen literal)"
                      % (f_cal, G2_THRESHOLD_LITERAL) if g2_fired else
                      "F_cal (%.15f) <= %.15f" % (f_cal, G2_THRESHOLD_LITERAL)),
        "g2b_fired": g2b_fired,
        "g2b_reason": g2b_reason,
    }


# ==========================================================================
# Mixed-regime natural-completion cross-check, PF-16 population counting,
# and the final-pop overshoot measurement (all sweep-loop-only, per sweep
# point).
# ==========================================================================

def pf16_counts(per_vertex_records):
    n_attempted = len(per_vertex_records)
    n_resolved = sum(1 for r in per_vertex_records if r["resolved"])
    n_timed_out = sum(1 for r in per_vertex_records if r["timed_out"])
    n_naturally_completed = sum(
        1 for r in per_vertex_records if r["resolved"] and not r["timed_out"])
    n_still_truncated = sum(
        1 for r in per_vertex_records if r["resolved"] and r["timed_out"])
    unresolved = [r for r in per_vertex_records if not r["resolved"]]
    n_unresolved_and_timed_out = sum(1 for r in unresolved if r["timed_out"])
    n_unresolved_and_not_timed_out = sum(
        1 for r in unresolved if not r["timed_out"])
    i1 = (n_naturally_completed + n_still_truncated == n_resolved)
    i2 = (n_still_truncated + n_unresolved_and_timed_out == n_timed_out)
    i3 = (n_resolved + n_unresolved_and_timed_out
          + n_unresolved_and_not_timed_out == n_attempted
          == ARCHIVED_N_NON_FP_RATIONAL)
    return {
        "n_attempted": n_attempted,
        "n_resolved": n_resolved,
        "n_timed_out": n_timed_out,
        "n_naturally_completed": n_naturally_completed,
        "n_still_truncated": n_still_truncated,
        "n_unresolved_and_timed_out": n_unresolved_and_timed_out,
        "n_unresolved_and_not_timed_out": n_unresolved_and_not_timed_out,
        "identity_I1_naturally_plus_still_truncated_eq_resolved": i1,
        "identity_I2_still_truncated_plus_unresolved_timed_out_eq_n_timed_out": i2,
        "identity_I3_partition_of_attempted_eq_194": i3,
    }


def mixed_regime_cross_check(per_vertex_records, new_delta_map,
                              archived_delta_map):
    naturally_completed = [
        tuple(r["vertex"]) for r in per_vertex_records
        if r["resolved"] and not r["timed_out"]]
    n_matching = 0
    mismatches = []
    hist = {}
    for v in naturally_completed:
        new_val = new_delta_map[v]
        hist[new_val] = hist.get(new_val, 0) + 1
        if v not in archived_delta_map:
            mismatches.append({"vertex": list(v), "new_value": new_val,
                                "archived_value": None, "label": "M-0"})
            continue
        arch_val = archived_delta_map[v]
        if arch_val == new_val:
            n_matching += 1
        else:
            label = "M-1" if new_val > arch_val else "M-2"
            mismatches.append({"vertex": list(v), "new_value": new_val,
                                "archived_value": arch_val, "label": label})
    return {
        "n_naturally_completed": len(naturally_completed),
        "n_naturally_completed_matching_archived": n_matching,
        "n_naturally_completed_NOT_matching_archived": len(mismatches),
        "mismatches_full_detail": mismatches,
        "naturally_completed_value_histogram": hist,
        "naturally_completed_value_histogram_provenance": (
            "Built from THIS RUN's own per-vertex delta_e_upper_bound "
            "values (new_delta_map), never from the archived map. Per "
            "PF-25, the equality half of this cross-check is an "
            "instrument-integrity control whose only informative outcome "
            "is FAILURE -- a k/k match confirms nothing new at any k."
        ),
    }


def _dist_summary_p95(values):
    """min/median/95th-percentile/max/n over a list of floats. p95 via
    linear interpolation on the sorted list (nearest-rank alternative
    documented here rather than silently chosen)."""
    if not values:
        return {"n": 0, "min": None, "median": None, "p95": None, "max": None}
    s = sorted(values)
    n = len(s)
    median = statistics.median(s)
    if n == 1:
        p95 = s[0]
    else:
        pos = 0.95 * (n - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        frac = pos - lo
        p95 = s[lo] + (s[hi] - s[lo]) * frac
    return {"n": n, "min": s[0], "median": median, "p95": p95, "max": s[-1]}


def final_pop_overshoot(per_vertex_records, budget):
    """Step (9), b = 1.10 s arm ONLY, PF-27's round-3 required control:
    (measured wall_seconds - budget) over that arm's TRUNCATED
    (timed_out True) vertices."""
    truncated = [r for r in per_vertex_records if r["timed_out"]]
    not_truncated = [r for r in per_vertex_records if not r["timed_out"]]
    overshoots = [r["wall_seconds"] - budget for r in truncated]
    return {
        "budget_seconds": budget,
        "n_truncated": len(truncated),
        "measured_final_pop_overshoot_seconds": _dist_summary_p95(overshoots),
        "n_not_truncated": len(not_truncated),
        "not_truncated_vertices": [
            {"vertex": r["vertex"], "wall_seconds": r["wall_seconds"],
             "delta_e_upper_bound": r["delta_e_upper_bound"]}
            for r in not_truncated
        ],
    }


# ==========================================================================
# JSON SAFETY (PF-13's convention, authorized disclosed duplicate of the
# identical one-liner v8/v9/v10 each already established, per
# required_artifacts_note's own explicit MAY-import-or-reauthor clause).
# ==========================================================================

def vertex_json_safe(v):
    return str(list(v))


def delta_map_json_safe(delta_map):
    return {vertex_json_safe(k): v for k, v in delta_map.items()}


# ==========================================================================
# git / environment bookkeeping -- small, non-research duplicate of the
# same trivial pattern every prior module in this lineage repeats.
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


# ==========================================================================
# CLI entry point / this run's own artifact writer.
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True,
                     help="output directory for this run's artifacts")
    ap.add_argument("--raw-result-b", default=RUN_B_RAW_RESULT_RELPATH,
                     help="path to RUN-SSIQ-a85692-b/raw-result.json "
                          "(READ ONLY, source of the archived comparison "
                          "delta_map, Comparison 1)")
    ap.add_argument("--run-h-comparison", default=RUN_H_COMPARISON_RELPATH,
                     help="path to "
                          "RUN-SSIQ-a85692-h/probe_delta_e_comparison.json "
                          "(READ ONLY, source of v8's own new_delta_map for "
                          "Comparison 2, and of the 194 archived "
                          "per-vertex wall_seconds for the LAC computation)")
    ap.add_argument("--run-h-environment", default=RUN_H_ENVIRONMENT_RELPATH,
                     help="path to RUN-SSIQ-a85692-h/environment.json "
                          "(READ ONLY, source of the archived host's "
                          "platform and cpus_available for gate G-0c)")
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (specification_v11.yaml)" % (started, EXPERIMENT_ID, RUN_ID))
    log("delta_e_floor_straddling_sweep_v11: prime=%d GRAPH_SEED=%d "
        "BASE_SEED=%d SWEEP_BUDGETS=%s (PART A ONLY, host-gated)"
        % (PRIME, GRAPH_SEED, BASE_SEED, SWEEP_BUDGETS))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    # ---- run-start host capture (required "at run start AND run end") ----
    host_capture_start = host_capture()
    log("HOST CAPTURE (run start): platform=%r machine=%r cpu_count=%r "
        "loadavg=%r (unavailable_reason=%r)"
        % (host_capture_start["platform_platform"],
           host_capture_start["platform_machine"],
           host_capture_start["os_cpu_count"],
           host_capture_start["os_getloadavg_1_5_15"],
           host_capture_start["os_getloadavg_unavailable_reason"]))

    # ======================================================================
    # STEP (0): rebuild the graph + re-run graph-identity verification,
    # EXACTLY ONCE, BEFORE step (0b) and BEFORE the sweep loop. NOT wrapped
    # in try/except -- per the frozen contract, an exception here
    # propagates UNCAUGHT and this run terminates with NO output artifact
    # written at all.
    # ======================================================================
    log("STEP (0): Rebuilding graph for p=%d via "
        "trapping_diagnostic_v5.build_graph_for_prime (GENUINELY IMPORTED, "
        "UNCHANGED, seed=%d) -- NOT wrapped in try/except"
        % (PRIME, GRAPH_SEED))
    g, seed_info = tdv5.build_graph_for_prime(PRIME, GRAPH_SEED)
    field = g["field"]

    log("STEP (0): Re-running two-part graph-identity verification via "
        "delta_e_independent_rng_probe_v8.verify_graph_identity (GENUINELY "
        "IMPORTED, UNCHANGED) -- NOT wrapped in try/except")
    graph_identity = v8probe.verify_graph_identity(g, ARCHIVED_N_VERTICES)
    log("  graph_identity_verification pass=%s (n_built=%d, degseq_pass=%s)"
        % (graph_identity["pass"], graph_identity["n_built_vertices"],
           graph_identity["degree_sequence_check"]["pass"]))

    non_fp_rational_set = set(v for v in g["vertices"] if not field.is_in_fp(v))
    log("STEP (0): non_fp_rational_set derived once, size=%d (expected %d)"
        % (len(non_fp_rational_set), ARCHIVED_N_NON_FP_RATIONAL))

    # ======================================================================
    # STEP (0b): host capture (already done above) + gate G-0c, evaluated
    # FIRST, before any calibration is run or interpreted.
    # ======================================================================
    archived_host = read_archived_host_from_run_h(args.run_h_environment)
    log("STEP (0b): archived host read from RUN-h/environment.json: "
        "platform=%r cpus_available=%r (read_error=%r)"
        % (archived_host["platform"], archived_host["cpus_available"],
           archived_host["read_error"]))

    g0c = evaluate_g0c(host_capture_start, archived_host)
    log("GATE G-0c: fired=%s reason=%s" % (g0c["fired"], g0c["reason"]))

    deferred_branch = None
    deferred_reason = None
    load_confounded = None
    cal1_records = []
    cal1_summary = None
    cal2_records = []
    g0_result = None
    g0b_result = None
    g1_result = None
    g2g2bg3_result = None
    f_cal = None
    measured_load_inflation_ratio = None
    lac = None

    if g0c["fired"]:
        deferred_branch = "G-0c"
        deferred_reason = g0c["reason"]
        load_confounded = True
        log("DEFERRING at G-0c: %s" % deferred_reason)
        log("Per G-0c's own text, CAL-1/CAL-2 are NOT run once G-0c has "
            "already fired ('FIRST, BEFORE ANY CALIBRATION IS "
            "INTERPRETED') -- see this module's own docstring for the "
            "disclosed ordering interpretation. cal1_records/cal2_records "
            "exist to zero extent for this run.")
    else:
        # ---- CAL-1 ----
        log("STEP (0b): CAL-1 -- run_truncation_probe_v9 on the "
            "vertex-restricted 8-vertex shallow copy, %.1fs budget"
            % CAL1_BUDGET_SECONDS)
        cal1_out = run_cal1(g)
        cal1_records = cal1_out["records"]
        cal1_summary = {k: v for k, v in cal1_out.items() if k != "records"}
        log("  CAL-1 done: n_attempted=%d n_resolved=%d n_timed_out=%d"
            % (cal1_out["n_attempted"], cal1_out["n_resolved"],
               cal1_out["n_timed_out"]))

        g0_result = evaluate_g0(cal1_records)
        log("GATE G-0: fired=%s reason=%s" % (g0_result["fired"], g0_result["reason"]))

        if g0_result["fired"]:
            deferred_branch = "G-0"
            deferred_reason = g0_result["reason"]
            load_confounded = True
            log("DEFERRING at G-0: %s" % deferred_reason)
        else:
            # ---- CAL-2 ----
            cal1_by_vertex = {tuple(r["vertex"]): r for r in cal1_records}
            log("STEP (0b): CAL-2 -- build_smooth_table on the same 8 "
                "vertices, fresh RNG, %.1fs cap" % CAL2_BUDGET_SECONDS)
            cal2_records = run_cal2(g, cal1_by_vertex)
            log("  CAL-2 done: %d records"
                % len(cal2_records))

            g0b_result = evaluate_g0b(cal2_records)
            log("GATE G-0b: fired=%s reason=%s"
                % (g0b_result["fired"], g0b_result["reason"]))

            if g0b_result["fired"]:
                deferred_branch = "G-0b"
                deferred_reason = g0b_result["reason"]
                load_confounded = True
                log("DEFERRING at G-0b: %s" % deferred_reason)
            else:
                f_cal = compute_f_cal(cal1_records)
                g1_result = evaluate_g1(f_cal)
                log("GATE G-1: F_cal=%s fired=%s reason=%s"
                    % (f_cal, g1_result["fired"], g1_result["reason"]))

                if g1_result["fired"]:
                    deferred_branch = "G-1"
                    deferred_reason = g1_result["reason"]
                    load_confounded = True
                    log("DEFERRING at G-1: %s" % deferred_reason)
                else:
                    measured_load_inflation_ratio = \
                        compute_measured_load_inflation_ratio(cal1_records)
                    archived_wall_seconds_list = \
                        load_archived_per_vertex_wall_seconds(
                            args.run_h_comparison)
                    lac = compute_lac(measured_load_inflation_ratio,
                                       archived_wall_seconds_list,
                                       SWEEP_BUDGETS)
                    g2g2bg3_result = evaluate_g2_g2b_g3(
                        f_cal, lac.get(str(1.45)))
                    load_confounded = g2g2bg3_result["load_confounded"]
                    log("GATE G-2/G-2b/G-3: branch=%s load_confounded=%s "
                        "g2_reason=%s g2b_reason=%s"
                        % (g2g2bg3_result["branch"], load_confounded,
                           g2g2bg3_result["g2_reason"],
                           g2g2bg3_result["g2b_reason"]))

    total_wall_gate = time.time() - t0
    log("Gate evaluation complete after %.2fs. deferred_branch=%s"
        % (total_wall_gate, deferred_branch))

    sweep_point_results = []
    n_sweep_points_attempted = 0
    n_sweep_points_succeeded = 0

    if deferred_branch is None:
        # ==================================================================
        # SWEEP LOOP: SWEEP_BUDGETS = [1.1, 1.45], each inside its own
        # try/except (PF-2 discipline, applied identically to v10).
        # ==================================================================
        for b in SWEEP_BUDGETS:
            n_sweep_points_attempted += 1
            log("SWEEP POINT b=%.2fs: entering own try/except (PF-2)" % b)
            entry = {"per_vertex_budget_seconds": b}
            t_b = time.time()
            try:
                part_a = v9probe.run_truncation_probe_v9(g, BASE_SEED, b)
                new_delta_map = part_a["new_delta_map_raw"]
                per_vertex_records = part_a["per_vertex_records"]
                counts = pf16_counts(per_vertex_records)

                archived = tdv5.load_archived_prime_data(args.raw_result_b, PRIME)
                archived_delta_map = archived["delta_map"]
                comparison_1 = v9probe.compare_against_archived(
                    new_delta_map, archived_delta_map, non_fp_rational_set)

                v8_delta_map = v9probe.parse_v8_new_delta_map(
                    args.run_h_comparison)
                comparison_2 = v9probe.compare_against_v8(
                    new_delta_map, v8_delta_map, non_fp_rational_set)

                resolved_non_fp_set = {
                    tuple(r["vertex"]) for r in per_vertex_records
                    if r["resolved"]}
                naturally_completed_set = {
                    tuple(r["vertex"]) for r in per_vertex_records
                    if r["resolved"] and not r["timed_out"]}

                (hist_resolved, n_resolved_hist, n_pairs_resolved,
                 n_without_partner_resolved, anomaly_resolved) = \
                    v10sweep.value_histogram_and_conjugate_pairs(
                        resolved_non_fp_set, new_delta_map, field)
                (hist_natural, n_natural_hist, n_pairs_natural,
                 n_without_partner_natural, anomaly_natural) = \
                    v10sweep.value_histogram_and_conjugate_pairs(
                        naturally_completed_set, new_delta_map, field)

                cross_check = mixed_regime_cross_check(
                    per_vertex_records, new_delta_map, archived_delta_map)

                entry.update({
                    "sweep_point_error": None,
                    "pf16_counts": counts,
                    "coverage_fraction": part_a["coverage_fraction"],
                    "new_delta_map": delta_map_json_safe(new_delta_map),
                    "per_vertex_records": per_vertex_records,
                    "comparison_against_archived": comparison_1,
                    "comparison_against_v8": comparison_2,
                    "resolved_non_fp_rational_value_histogram": hist_resolved,
                    "n_resolved_non_fp_rational": n_resolved_hist,
                    "n_conjugate_pairs_among_resolved": n_pairs_resolved,
                    "n_resolved_without_a_paired_partner_in_resolved_set":
                        n_without_partner_resolved,
                    "conjugate_pair_anomaly_resolved": anomaly_resolved,
                    "naturally_completed_value_histogram": hist_natural,
                    "n_conjugate_pairs_among_naturally_completed": n_pairs_natural,
                    "n_naturally_completed_without_a_paired_partner":
                        n_without_partner_natural,
                    "conjugate_pair_anomaly_naturally_completed": anomaly_natural,
                    "mixed_regime_cross_check": cross_check,
                    "reference_curve_for_this_budget":
                        PRE_REGISTERED_REFERENCE_CURVE_V11.get(
                            "b_%s" % str(b).replace(".", "_")),
                    "wall_seconds_this_sweep_point": time.time() - t_b,
                })
                if b == 1.10:
                    entry["final_pop_overshoot"] = final_pop_overshoot(
                        per_vertex_records, b)

                n_sweep_points_succeeded += 1
                log("SWEEP POINT b=%.2fs: SUCCESS (%.2fs) "
                    "n_naturally_completed=%d"
                    % (b, time.time() - t_b, counts["n_naturally_completed"]))

            except Exception as e:  # noqa: BLE001 -- PF-2 requires catching
                                     # ANY exception here.
                sweep_point_error = "%s: %s" % (type(e).__name__, str(e))
                entry["sweep_point_error"] = sweep_point_error
                log("SWEEP POINT b=%.2fs FAILED (caught per PF-2): %s"
                    % (b, sweep_point_error))

            sweep_point_results.append(entry)

    host_capture_end = host_capture()
    log("HOST CAPTURE (run end): platform=%r machine=%r cpu_count=%r "
        "loadavg=%r (unavailable_reason=%r)"
        % (host_capture_end["platform_platform"],
           host_capture_end["platform_machine"],
           host_capture_end["os_cpu_count"],
           host_capture_end["os_getloadavg_1_5_15"],
           host_capture_end["os_getloadavg_unavailable_reason"]))

    total_wall = time.time() - t0
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if total_wall > 1000:
        log("WARNING: total_wall_seconds (%.2f) exceeded the 1000s budget "
            "cap -- this should not happen, disclosed here per the "
            "HONESTY RULE" % total_wall)

    # ======================================================================
    # truncation_sweep_comparison.json
    # ======================================================================
    if deferred_branch is not None:
        # CLOSED LIST -- per load_defer_gate_v11's REQUIRED ARTIFACT
        # BEHAVIOUR: ONLY these fields, no sweep-derived field present even
        # as null/{}/0.
        sweep_payload = {
            "deferred": True,
            "deferral_branch": deferred_branch,
            "deferral_reason": deferred_reason,
            "load_confounded": True,
            "host_capture_run_start": host_capture_start,
            "host_capture_run_end": host_capture_end,
            "archived_host_from_run_h_environment_json": archived_host,
            "g0c_comparison": g0c,
            "cal1_records": cal1_records,
            "cal1_summary": cal1_summary,
            "cal2_records": cal2_records,
            "gate_g0_result": g0_result,
            "gate_g0b_result": g0b_result,
            "gate_g1_result": g1_result,
            "f_cal_seconds": f_cal,
            "measured_load_inflation_ratio_median_non_timed_out": (
                measured_load_inflation_ratio),
            "load_adjusted_predicted_counts": (
                lac if lac is not None else
                {str(b): {"value": None,
                          "reason": "undefined: %s fired before CAL-1 "
                                     "calibration was run/interpreted"
                                     % deferred_branch}
                 for b in SWEEP_BUDGETS}),
            "pre_registered_reference_curve_v11": PRE_REGISTERED_REFERENCE_CURVE_V11,
            "graph_identity_verification": graph_identity,
            "statement": (
                "NO SWEEP WAS EXECUTED. This outcome is an "
                "infrastructure/environment condition under AGENTS.md rule "
                "3 (the frozen specification's own citation; this "
                "repository's live AGENTS.md currently numbers the "
                "identical principle -- 'a timeout, crash, or "
                "implementation failure is not evidence against a "
                "mathematical hypothesis' -- as rule 5, a citation-drift "
                "disclosed here, not corrected in the frozen spec text) "
                "and is NOT evidence about delta_E convergence, truncation "
                "bias, or H-SSIQ-36e970."
            ),
            "ordering_interpretation_note": (
                "Deferred at %s. Per this module's own disclosed ordering "
                "interpretation (see module docstring), G-0c is evaluated "
                "using only the host capture and gates whether CAL-1/CAL-2 "
                "run at all; CAL-1 gates G-0, which gates whether CAL-2 "
                "runs and gates G-0b, which gates whether F_cal/G-1 are "
                "evaluated. Fields for calibration stages not reached this "
                "run are empty lists / null, 'to whatever extent they "
                "exist' (load_defer_gate_v11's own phrase for this closed "
                "list)." % deferred_branch
            ),
        }
    else:
        n_sweep_points_failed = (
            n_sweep_points_attempted - n_sweep_points_succeeded)
        sweep_payload = {
            "deferred": False,
            "deferral_branch": None,
            "load_confounded": load_confounded,
            "host_capture_run_start": host_capture_start,
            "host_capture_run_end": host_capture_end,
            "archived_host_from_run_h_environment_json": archived_host,
            "g0c_comparison": g0c,
            "cal1_records": cal1_records,
            "cal1_summary": cal1_summary,
            "cal2_records": cal2_records,
            "gate_g0_result": g0_result,
            "gate_g0b_result": g0b_result,
            "gate_g1_result": g1_result,
            "gate_g2_g2b_g3_result": g2g2bg3_result,
            "f_cal_seconds": f_cal,
            "measured_load_inflation_ratio_median_non_timed_out": (
                measured_load_inflation_ratio),
            "load_adjusted_predicted_counts": lac,
            "pre_registered_reference_curve_v11": PRE_REGISTERED_REFERENCE_CURVE_V11,
            "graph_identity_verification": graph_identity,
            "prime": PRIME, "graph_seed": GRAPH_SEED, "base_seed": BASE_SEED,
            "sweep_budgets": SWEEP_BUDGETS,
            "non_fp_rational_set_size": len(non_fp_rational_set),
            "n_sweep_points_attempted": n_sweep_points_attempted,
            "n_sweep_points_succeeded": n_sweep_points_succeeded,
            "n_sweep_points_failed": n_sweep_points_failed,
            "sweep_points": sweep_point_results,
            "objective_boundary_note": (
                "DESCRIPTIVE DIAGNOSTIC CONTROL ONLY. Does not produce a "
                "PERSISTS/WEAKENS label. Per PF-25 the equality half of "
                "the mixed-regime cross-check is an instrument-integrity "
                "control, not a measurement. Per PF-27 the archived-"
                "derived counts are reference counts with two-sided "
                "corrections, not upper bounds. Per reading rule P-4, NO "
                "outcome of this run licenses a statement about whether "
                "delta_E >= 5 convergence begins at the natural-completion "
                "floor."
            ),
        }

    sweep_path = os.path.join(run_dir, "truncation_sweep_comparison.json")
    with open(sweep_path, "w") as fh:
        json.dump(sweep_payload, fh, indent=1, sort_keys=True, default=str)

    # ---- raw-result.json (top-level summary) ------------------------------
    raw_result_payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "spec_version": SPEC_VERSION,
        "started_utc": started,
        "finished_utc": finished,
        "wall_clock_seconds": total_wall,
        "git": git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "certificate": {
            "kind": "none",
            "reason": (
                "Pure measurement/probe run (or, on a gate defer, pure "
                "infrastructure measurement). No discrete log is claimed, "
                "no factor-base relation is claimed, no isogeny problem "
                "instance is solved -- delta_E upper bounds (if any) are "
                "labelling data for a descent-gradient screen, not a solve "
                "claim. docs/claims-and-verification.md requires "
                "kind: none to be stated explicitly for such runs."
            ),
        },
        "prime": PRIME,
        "graph_seed": GRAPH_SEED,
        "base_seed": BASE_SEED,
        "sweep_budgets": SWEEP_BUDGETS,
        "graph_identity_verification": graph_identity,
        "deferred": deferred_branch is not None,
        "deferral_branch": deferred_branch,
        "deferral_reason": deferred_reason,
        "load_confounded": load_confounded,
        "host_capture_run_start": host_capture_start,
        "host_capture_run_end": host_capture_end,
        "archived_host_from_run_h_environment_json": archived_host,
        "g0c_comparison": g0c,
        "n_sweep_points_attempted": n_sweep_points_attempted,
        "n_sweep_points_succeeded": n_sweep_points_succeeded,
        "n_sweep_points_failed": (
            n_sweep_points_attempted - n_sweep_points_succeeded),
        "artifact_references": {
            "truncation_sweep_comparison": "truncation_sweep_comparison.json",
        },
        "objective_boundary": (
            "This is a DESCRIPTIVE DIAGNOSTIC CONTROL, not a claim. It "
            "does not test H-SSIQ-36e970's real-arm prediction, does not "
            "gate any decision rule, and does not itself constitute "
            "evidence for or against a computable delta_E-gradient or a "
            "p^{1/4} algorithm. It does not produce a PERSISTS/WEAKENS "
            "label. Scale: toy, single prime p=2437 (N=203 vertices, max "
            "log2(p)=%.4f); no result transfers to cryptographic scale. "
            "A gate defer is an infrastructure outcome, never mathematical "
            "counterevidence, per AGENTS.md's timeout/crash principle "
            "(numbered rule 5 in this repository's live AGENTS.md; the "
            "frozen specification text cites this footing as 'rule 3', a "
            "citation-numbering drift disclosed rather than silently "
            "reconciled)." % math.log2(PRIME)
        ),
        "scale_qualifier": "toy; N (graph size) = 203; single prime p=2437",
    }
    raw_result_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_result_path, "w") as fh:
        json.dump(raw_result_payload, fh, indent=1, sort_keys=True, default=str)

    log("wrote %s, %s (%.2fs total)" % (raw_result_path, sweep_path, total_wall))
    if deferred_branch is not None:
        print("OUTCOME DEFERRED branch=%s reason=%s"
              % (deferred_branch, deferred_reason))
    else:
        print("OUTCOME SWEEP-COMPLETE n_succeeded=%d/%d load_confounded=%s"
              % (n_sweep_points_succeeded, len(SWEEP_BUDGETS), load_confounded))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
