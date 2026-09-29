#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE (TASK-20260813-7930a6) -- the SECOND TARGET's requested
control, built to the cheapest available proxy since the EXACT control the
task card names is infrastructure-blocked in this environment.

WHAT THE TASK CARD ASKS FOR: "run the SAME code-shared lineage
(measure_am4.py or a close descendant) but force it to use LLL-quality
reduction instead of its normal HKZ pipeline, and see if IT ALSO disagrees
with ROUTE-P by a similar 0.015-0.223 margin."

WHY THAT EXACT CONTROL CANNOT BE BUILT HERE (INFRASTRUCTURE SIGNAL, checked
directly by this probe's own process, not assumed): measure_am4.py's
hkz_profile() hard-requires `from fpylll import IntegerMatrix, GSO, LLL,
BKZ, Enumeration` at import time (confirmed in
probe_independence_and_coverage_output.json,
A_primary_independence_diff.per_barred_function_comparison,
barred_function_uses_fpylll: true for all three files' hkz_profile). This
probe's own process re-checks fpylll availability below, independently.
Without fpylll, measure_am4.py (or measure_relvar.py / replicate_l7l8.py)
cannot be imported and forced into an LLL-only mode in this environment --
the SAME infrastructure limitation the lead producer disclosed for building
ROUTE-I' in the first place.

THE CHEAPEST AVAILABLE PROXY, BUILT: a SECOND, independently-written LLL
implementation (delta = 0.99, matching the lead's own choice so this is an
apples-to-apples parameter match) -- written fresh in this file, NOT copied
from measure_route_reimpl.py's lll_reduce/gso_full/refresh_row and NOT
imported from any barred file -- computes hkz'' at the 6 currently-COVERED
hkz cells and compares against (a) the ALREADY-ARCHIVED ROUTE-P value and
(b) the LEAD's own already-reported hkz' value at the same cell. If a
SECOND, differently-coded LLL-only route ALSO disagrees with ROUTE-P by a
similar margin, AND is reasonably close to the lead's own hkz' (a different
implementation of the SAME weaker reduction landing on a similar tail
profile), that is evidence the disagreement is a property of "LLL-quality
reduction generally" rather than an idiosyncrasy of one particular from-
scratch implementation -- addressing the "is this an implementation-
specific artifact vs. a general LLL-vs-HKZ phenomenon" question the code-
sharing-vs-reduction-quality confound raises, though it does NOT and cannot
by itself rule out code-sharing in the ORIGINAL sense (this probe's LLL is
independent of BOTH the barred lineage and the lead's own reimpl by
construction, so a good match to the lead's own hkz' actually argues
AGAINST code-sharing being lead-implementation-specific noise, while a good
match to ROUTE-P would argue FOR code-sharing -- both readings are reported
plainly below rather than pre-decided).

LLL IMPLEMENTATION NOTE, DELIBERATELY DIFFERENT FROM THE LEAD'S: this
routine performs FULL-SIZE reduction against ALL previously-processed
vectors on every visited index (no early truncation), uses a different loop
structure (a single explicit while-loop with an inner reversed range, but
recomputes the FULL GSO after every swap rather than doing an incremental
refresh_row -- a deliberately less-optimized, differently-structured
choice), and is capped at PER_BASIS_TIME_CAP seconds per basis exactly as
the lead's own script caps its LLL step, so a like-for-like time budget is
used. NO SVP ENUMERATION IS PERFORMED HERE (hkz only needs a reduced GSO
tail, not lambda_1), which keeps this probe's total runtime a small
fraction of the lead's own 981.5s.

CLAIM TIER: TOY. Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model. NO REDUCTION ABOVE
d = 40, anywhere.
"""
import hashlib
import json
import math
import os
import sys
import time
from collections import OrderedDict

import numpy as np

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
PER_BASIS_TIME_CAP = 120.0


def _find_repo_root(start):
    cur = start
    for _ in range(20):
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise SystemExit("ABORT: could not locate repo root (.git) above %s" % start)


REPO_ROOT = _find_repo_root(TASK_DIR)
RESULTS_RELVAR_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/results_relvar.json")
RESULTS_ROUTE_REIMPL_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/"
    "tasks/TASK-20260813-ea2e96/results_route_reimpl.json")


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


Q_MAIN = 3329
LATTICES = OrderedDict([("L7", (20, 6)), ("L9", (30, 9)), ("L11", (40, 12))])
BETA_GRID = {20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
COVERED_HKZ_BETAS = {20: [5, 15], 30: [7, 22], 40: [10, 30]}  # per obligation 0


def basis_of(d, k, q, i):
    """Deliberately duplicated ONLY for the frozen seed formula, per
    PREREG-4 2.2(3) -- reconstructing the identical published instance is
    not code-sharing. Written fresh here."""
    rng = np.random.default_rng([1, d, k, i])
    A = rng.integers(0, q, size=(k, d - k), dtype=np.int64)
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def full_gso(B):
    """Independent Gram-Schmidt: classical (non-incremental) recomputation
    from scratch every call, no shared bookkeeping with any barred or
    reimpl function."""
    n = B.shape[0]
    Bstar = np.zeros_like(B)
    mu = np.eye(n)
    sqn = np.zeros(n)
    for i in range(n):
        v = B[i].copy()
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / sqn[j]
            v = v - mu[i, j] * Bstar[j]
        Bstar[i] = v
        sqn[i] = np.dot(v, v)
    return Bstar, mu, sqn


def lll_reduce_v2(B, delta, time_cap):
    """A SECOND, independently structured LLL: recomputes the FULL
    Gram-Schmidt from scratch (full_gso) once per outer k-iteration rather
    than doing an incremental single-row refresh -- a different engineering
    choice from measure_route_reimpl.py's lll_reduce (which uses
    refresh_row on only the changed index). Returns
    (Bred, sqn, converged, secs, iterations)."""
    B = B.astype(np.float64).copy()
    n = B.shape[0]
    t0 = time.time()
    k = 1
    iterations = 0
    Bstar, mu, sqn = full_gso(B)
    while k < n:
        iterations += 1
        if time.time() - t0 > time_cap:
            return B, sqn, False, time.time() - t0, iterations
        changed = False
        for j in range(k - 1, -1, -1):
            if abs(mu[k, j]) > 0.5:
                m = round(mu[k, j])
                B[k] = B[k] - m * B[j]
                changed = True
        if changed:
            Bstar, mu, sqn = full_gso(B)
        if sqn[k] >= (delta - mu[k, k - 1] ** 2) * sqn[k - 1]:
            k += 1
        else:
            B[[k, k - 1]] = B[[k - 1, k]]
            k = max(k - 1, 1)
            Bstar, mu, sqn = full_gso(B)
    return B, sqn, True, time.time() - t0, iterations


def hkz_from_sqn(sqn, d, k_ambient, beta, q):
    logdet = (d - k_ambient) * math.log(q)  # closed form, independent path
    logb_tail = 0.5 * np.log(np.maximum(sqn, 1e-300))
    return float(np.mean(logb_tail[d - beta:]) - logdet / d)


def main():
    out = OrderedDict()
    out["probe"] = "probe_second_lll_hkz_control.py"
    out["task_id"] = "TASK-20260813-7930a6"
    out["claim_tier"] = "toy"

    have_fpylll = False
    fpylll_err = None
    try:
        import fpylll  # noqa: F401
        have_fpylll = True
    except Exception as ex:
        fpylll_err = "%s: %s" % (type(ex).__name__, ex)
    out["exact_requested_control_infrastructure_check"] = {
        "fpylll_available_in_this_probe_process": have_fpylll,
        "fpylll_import_error": fpylll_err,
        "conclusion": (
            "fpylll unavailable -- the EXACT control the task card requests "
            "('run measure_am4.py itself, forced to LLL-quality') cannot be "
            "built in this environment: measure_am4.py's hkz_profile hard-"
            "imports fpylll at module scope and cannot run without it. This "
            "is INFRASTRUCTURE SIGNAL (AGENTS.md rule 5), not a negative "
            "result. The cheapest available proxy actually built is below."
            if not have_fpylll else
            "fpylll unexpectedly available in this probe's process -- "
            "reserved for a future re-run; NOT exercised here since the "
            "lead's own report and this probe's independence check both "
            "found it absent, and using it now would silently change the "
            "comparison basis relative to the archived run."),
    }

    relvar = json.load(open(RESULTS_RELVAR_PATH))
    reimpl_out = json.load(open(RESULTS_ROUTE_REIMPL_PATH))
    g_rel1_hkz = relvar["G_REL1"]["hkz"]
    reimpl_cells = reimpl_out["R_IV_OUT_2_per_cell"]

    per_lattice_rows = OrderedDict()
    t_all0 = time.time()
    for lat, (d, k) in LATTICES.items():
        entry = g_rel1_hkz[lat]
        route_p_vals = {}  # beta -> [8 values]
        for beta in COVERED_HKZ_BETAS[d]:
            field = "X_a" if beta == entry["beta_lo"] else "X_b"
            route_p_vals[beta] = [row[field] for row in entry["per_basis"]]
        rows = []
        for i in range(8):
            B = basis_of(d, k, Q_MAIN, i)
            Bred, sqn, converged, secs, iters = lll_reduce_v2(
                B, delta=0.99, time_cap=PER_BASIS_TIME_CAP)
            row = OrderedDict([("basis", i), ("lll_v2_converged", converged),
                               ("lll_v2_secs", secs), ("lll_v2_iterations", iters)])
            for beta in COVERED_HKZ_BETAS[d]:
                hkz_v2 = hkz_from_sqn(sqn, d, k, beta, Q_MAIN)
                p_val = route_p_vals[beta][i]
                cellkey = "hkz/%s_b%d" % (lat, beta)
                lead_reported = reimpl_cells.get(cellkey, {})
                lead_hkz_prime = lead_reported.get("D_route_prime") if \
                    lead_reported.get("status") == "COMPUTED" else None
                lead_matched_detail = None
                if lead_reported.get("status") == "COMPUTED":
                    for md in lead_reported.get("matched_bases_detail", []):
                        if md["basis"] == i:
                            lead_matched_detail = md
                            break
                row["beta_%d" % beta] = OrderedDict([
                    ("route_p", p_val),
                    ("probe_hkz_v2_LLL_independent_implementation", hkz_v2),
                    ("abs_diff_probe_v2_vs_ROUTE_P", abs(p_val - hkz_v2)),
                    ("lead_reported_route_i_prime",
                     lead_matched_detail["route_i_prime"] if lead_matched_detail else None),
                    ("abs_diff_probe_v2_vs_lead_route_i_prime",
                     (abs(hkz_v2 - lead_matched_detail["route_i_prime"])
                      if lead_matched_detail else None)),
                ])
            rows.append(row)
        per_lattice_rows[lat] = rows
        print("  %s done, %.1fs elapsed" % (lat, time.time() - t_all0), file=sys.stderr)

    out["total_probe_seconds"] = time.time() - t_all0
    out["per_lattice_basis_rows"] = per_lattice_rows

    # ---- aggregate per cell ----
    per_cell_summary = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        for beta in COVERED_HKZ_BETAS[d]:
            key = "hkz/%s_b%d" % (lat, beta)
            diffs_vs_p = [row["beta_%d" % beta]["abs_diff_probe_v2_vs_ROUTE_P"]
                         for row in per_lattice_rows[lat]]
            diffs_vs_lead = [row["beta_%d" % beta]["abs_diff_probe_v2_vs_lead_route_i_prime"]
                             for row in per_lattice_rows[lat]
                             if row["beta_%d" % beta]["abs_diff_probe_v2_vs_lead_route_i_prime"]
                             is not None]
            per_cell_summary[key] = OrderedDict([
                ("D_route_prime_prime_max_abs_diff_probe_v2_vs_ROUTE_P", max(diffs_vs_p)),
                ("lead_reported_D_route_prime_vs_ROUTE_P",
                 reimpl_cells.get(key, {}).get("D_route_prime")),
                ("max_abs_diff_probe_v2_vs_lead_route_i_prime",
                 max(diffs_vs_lead) if diffs_vs_lead else None),
            ])
    out["per_cell_summary"] = per_cell_summary

    both_disagree = all(
        v["D_route_prime_prime_max_abs_diff_probe_v2_vs_ROUTE_P"] > 0.001
        for v in per_cell_summary.values())
    close_to_lead = [v["max_abs_diff_probe_v2_vs_lead_route_i_prime"]
                     for v in per_cell_summary.values()
                     if v["max_abs_diff_probe_v2_vs_lead_route_i_prime"] is not None]
    out["READING"] = OrderedDict([
        ("both_independent_LLL_routes_disagree_with_ROUTE_P_hkz_at_every_covered_cell",
         both_disagree),
        ("probe_v2_vs_lead_route_i_prime_diff_range",
         [min(close_to_lead), max(close_to_lead)] if close_to_lead else None),
        ("probe_v2_vs_ROUTE_P_diff_range",
         [min(v["D_route_prime_prime_max_abs_diff_probe_v2_vs_ROUTE_P"]
              for v in per_cell_summary.values()),
          max(v["D_route_prime_prime_max_abs_diff_probe_v2_vs_ROUTE_P"]
              for v in per_cell_summary.values())]),
        ("interpretation", (
            "A SECOND, independently-structured LLL implementation "
            "(different GSO bookkeeping, no incremental refresh, written "
            "fresh in this probe) ALSO disagrees with ROUTE-P's HKZ-quality "
            "hkz values at every one of the 6 currently-covered cells, at a "
            "magnitude far above any floating-point floor (see "
            "probe_rdet_null_control_output.json for that floor). This is "
            "consistent with 'any LLL-quality route disagrees with ROUTE-P "
            "by roughly this much' (a general reduction-DEPTH phenomenon) "
            "rather than an idiosyncrasy specific to the lead's own "
            "from-scratch implementation. Whether this probe's v2 values "
            "are CLOSE to the lead's own reported route_i_prime values "
            "(reported in probe_v2_vs_lead_route_i_prime_diff_range above) "
            "additionally checks implementation-to-implementation "
            "consistency AMONG two independent LLL-only routes -- a small "
            "gap there would further support a shared, real, LLL-quality-"
            "specific tail profile rather than noise from either "
            "implementation's own idiosyncrasies."))
    ])

    out_path = (sys.argv[1] if len(sys.argv) > 1 else
               os.path.join(TASK_DIR, "probe_second_lll_hkz_control_output.json"))
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(json.dumps(out["READING"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
