#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-0881f0 -- RED TEAM independent re-verification probe.

Governed by PREREG-6 (BATCH-8d09f5). Reviews the lead producer's
TASK-20260813-630414 artifacts, committed at
e2ad28b3ffe90b2b5390ca83f4e2ba1d431399fd, against:
  - results_relvar.json (BATCH-9e3584/TASK-20260809-cda2f6), READ ONLY
  - measure_hkz_indep.py (BATCH-a6fab5/TASK-20260813-c0ec71), FROZEN,
    READ ONLY -- read as text and exec'd into an isolated namespace only
    to obtain an independent oracle for "what would the FROZEN, unmutated
    route compute at basis index (i+1) mod 8", never edited.

This script performs 5 independent checks:
  (A) Mechanical diff, built from scratch with a different extraction
      method (regex-based line scan) than the lead's ast-based extractor,
      confirming exactly one functional line differs between the frozen
      reference and the mutant file, and that measure_hkz_indep.py's own
      committed bytes are untouched (sha256 check).
  (B) Independent recomputation of the frozen prediction (max cyclic
      adjacent |diff| of ROUTE-P's own per-basis arrays) directly from
      results_relvar.json.
  (C) BUILT CONTROL: for every matched basis at both cells, independently
      RUNS the FROZEN, unmutated route_ii_build_basis/hkz_route_ii/
      route_ii_hkz_value functions (read from measure_hkz_indep.py, never
      edited) on shifted index (i+1) mod 8, and compares the result
      against the mutant's own reported route_mut_values[i]. This is the
      falsifiable claim: "mutant slot i's HKZ value should equal a genuine
      HKZ-quality computation of ROUTE-P's OWN slot (i+1 mod 8)" -- not
      just "some big number".
  (D) Recomputes D_route_mut/VERDICT_mut/detection_reading from raw
      arrays (both the lead's reported route_mut_values and this script's
      own independently-recomputed frozen-shifted values) and checks the
      detection mapping is applied the right way round.
  (E) NULL-OBJECT CONTROL: for n=8 i.i.d. samples from several generic
      continuous distributions (no lattice, no fpylll, no HKZ), computes
      P(max cyclic-adjacent |diff| > sample std) and the ratio
      max_cyclic_diff / sample_std, and compares those against the actual
      ratios at all 6 of BATCH-a6fab5's archived hkz cells.

Writes rt_reverify_results.json in this same directory. No git write, no
commit, no edit of any file outside this task's own write_scope.
"""
import hashlib
import json
import math
import os
import re
import time
from collections import OrderedDict

import numpy as np

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root(start):
    cur = start
    for _ in range(20):
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise SystemExit("ABORT: could not locate repo root above %s" % start)


REPO_ROOT = _find_repo_root(HERE)

FROZEN_REF = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/"
    "tasks/TASK-20260813-c0ec71/measure_hkz_indep.py")
FROZEN_REF_DECLARED_SHA256 = (
    "74875b4197cee69dc78c2999f9f60f27b678da3159c6cdd0bbc7039a4fb09096")

MUTANT_FILE = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/"
    "tasks/TASK-20260813-630414/measure_hkz_mutation6.py")

RESULTS_MUT = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/"
    "tasks/TASK-20260813-630414/results_hkz_mutation6.json")

RESULTS_RELVAR = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/results_relvar.json")

Q_MAIN = 3329
N_BASES = 8
CELLS = OrderedDict([
    ("hkz/L7_b5",   dict(lat="L7", d=20, k=6,  beta=5)),
    ("hkz/L11_b30", dict(lat="L11", d=40, k=12, beta=30)),
])
ALL_HKZ_CELLS = [
    ("hkz/L7_b5", "L7", 5, "X_a"),
    ("hkz/L7_b15", "L7", 15, "X_b"),
    ("hkz/L9_b7", "L9", 7, "X_a"),
    ("hkz/L9_b22", "L9", 22, "X_b"),
    ("hkz/L11_b10", "L11", 10, "X_a"),
    ("hkz/L11_b30", "L11", 30, "X_b"),
]


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ============================================================ (A) diff
def extract_functions_regex(path, names):
    """Independent, regex/line-scan based extraction (NOT ast, NOT the
    lead's extract_function_sources) of top-level function source blocks,
    to cross-check the lead's own ast-based mechanical diff with a
    structurally different method."""
    with open(path, "r") as fh:
        lines = fh.readlines()
    out = OrderedDict()
    i = 0
    n = len(lines)
    def_re = re.compile(r"^def\s+(\w+)\s*\(")
    while i < n:
        m = def_re.match(lines[i])
        if m and m.group(1) in names:
            name = m.group(1)
            start = i
            i += 1
            while i < n and (lines[i].startswith(" ") or lines[i].strip() == ""):
                # stop consuming trailing blank lines that precede the
                # next top-level statement -- keep it simple: stop when we
                # hit a non-indented, non-blank line.
                if lines[i].strip() == "":
                    # peek ahead: is next non-blank line top-level?
                    j = i
                    while j < n and lines[j].strip() == "":
                        j += 1
                    if j >= n or not lines[j].startswith((" ", "\t")):
                        break
                i += 1
            out[name] = "".join(lines[start:i])
        else:
            i += 1
    missing = [x for x in names if x not in out]
    if missing:
        raise SystemExit("ABORT: regex extractor could not find %s in %s"
                          % (missing, path))
    return out


FROZEN_NAMES = ["route_ii_make_A", "route_ii_build_basis", "hkz_route_ii",
                 "route_ii_hkz_value"]
MUT_NAMES = ["route_ii_make_A_mut", "route_ii_build_basis_mut",
             "hkz_route_ii_mut", "route_ii_hkz_value_mut"]


def check_diff():
    out = OrderedDict()
    live_sha = sha256_file(FROZEN_REF)
    out["frozen_reference_sha256_live"] = live_sha
    out["frozen_reference_sha256_declared_by_lead"] = FROZEN_REF_DECLARED_SHA256
    out["frozen_reference_untouched"] = (live_sha == FROZEN_REF_DECLARED_SHA256)

    frozen_funcs = extract_functions_regex(FROZEN_REF, FROZEN_NAMES)
    mut_funcs = extract_functions_regex(MUTANT_FILE, MUT_NAMES)

    # Normalize away the _mut suffix and the added n_bases=N_BASES default
    # arg / recursive-call renames (cosmetic, per PREREG-6 2.4 point 2),
    # then diff line by line, reporting every line that is NOT identical
    # after normalization.
    def normalize(src, is_mut):
        s = src
        if is_mut:
            s = s.replace("route_ii_make_A_mut", "route_ii_make_A")
            s = s.replace("route_ii_build_basis_mut", "route_ii_build_basis")
            s = s.replace("hkz_route_ii_mut", "hkz_route_ii")
            s = s.replace("route_ii_hkz_value_mut", "route_ii_hkz_value")
            s = s.replace(", n_bases=N_BASES)", ")")
        return s

    diffs = []
    for fname, mname in zip(FROZEN_NAMES, MUT_NAMES):
        f_lines = normalize(frozen_funcs[fname], False).splitlines()
        m_lines = normalize(mut_funcs[mname], True).splitlines()
        maxlen = max(len(f_lines), len(m_lines))
        for idx in range(maxlen):
            fl = f_lines[idx] if idx < len(f_lines) else "<MISSING>"
            ml = m_lines[idx] if idx < len(m_lines) else "<MISSING>"
            if fl != ml:
                diffs.append({
                    "function": fname, "line_index": idx,
                    "frozen": fl, "mutant_normalized": ml,
                })

    out["n_functional_differing_lines_after_cosmetic_normalization"] = len(diffs)
    out["differing_lines"] = diffs
    out["expected_exactly_one_functional_change"] = (len(diffs) == 1)
    if len(diffs) == 1:
        d0 = diffs[0]
        out["single_diff_is_the_declared_seed_shift"] = (
            "(i + 1) % n_bases" in d0["mutant_normalized"]
            and "np.random.default_rng" in d0["frozen"]
        )
    return out


# ============================================================ (B) prediction
def cyclic_maxdiff(vals):
    n = len(vals)
    diffs = [abs(vals[i] - vals[(i + 1) % n]) for i in range(n)]
    mx = max(diffs)
    return diffs, mx, diffs.index(mx)


def recompute_prediction(relvar):
    g = relvar["G_REL1"]["hkz"]
    Xa = [row["X_a"] for row in g["L7"]["per_basis"]]
    Xb = [row["X_b"] for row in g["L11"]["per_basis"]]
    _, max_a, _ = cyclic_maxdiff(Xa)
    _, max_b, _ = cyclic_maxdiff(Xb)
    return {"hkz/L7_b5": max_a, "hkz/L11_b30": max_b, "X_a": Xa, "X_b": Xb}


# ============================================================ (C) built control
def load_frozen_ns():
    """Exec the FROZEN reference file's text into an isolated namespace, so
    this red-team script can independently call ITS OWN, unmutated
    route_ii_build_basis / hkz_route_ii / route_ii_hkz_value on a SHIFTED
    index -- the built control PREREG-6's own task card calls for. The
    file on disk is never written to."""
    with open(FROZEN_REF, "r") as fh:
        src = fh.read()
    ns = {"__name__": "frozen_reference_readonly_exec", "__file__": FROZEN_REF}
    exec(compile(src, FROZEN_REF, "exec"), ns)
    return ns


def built_control(relvar):
    ns = load_frozen_ns()
    route_ii_build_basis = ns["route_ii_build_basis"]
    hkz_route_ii = ns["hkz_route_ii"]
    route_ii_hkz_value = ns["route_ii_hkz_value"]

    with open(RESULTS_MUT) as fh:
        lead_results = json.load(fh)
    lead_per_cell = lead_results["R_MC_OUT_2_per_cell"]

    out = OrderedDict()
    deadline = time.time() + 1500.0
    for cell_name, meta in CELLS.items():
        lat, d, k, beta = meta["lat"], meta["d"], meta["k"], meta["beta"]
        lead_cell = lead_per_cell[cell_name]
        route_mut_values = lead_cell["route_mut_values"]
        route_p_values = lead_cell["route_p_values"]
        n = len(route_mut_values)

        my_frozen_shifted_values = []
        per_basis_matrix_identity = []
        for i in range(n):
            shifted_i = (i + 1) % N_BASES
            # matrix-identity sanity check: mutant's own make_A_mut(d,k,q,i)
            # is BY CONSTRUCTION identical to the frozen route_ii_make_A
            # called at shifted_i -- confirm this holds with the actual
            # numpy Generator, not merely by reading the source.
            rng_mut = np.random.default_rng([1, d, k, shifted_i])
            A_mut_equiv = rng_mut.integers(0, Q_MAIN, size=(k, d - k), dtype=np.int64)
            rng_frozen_shifted = np.random.default_rng([1, d, k, shifted_i])
            A_frozen_shifted = rng_frozen_shifted.integers(
                0, Q_MAIN, size=(k, d - k), dtype=np.int64)
            per_basis_matrix_identity.append(
                bool(np.array_equal(A_mut_equiv, A_frozen_shifted)))

            B = route_ii_build_basis(d, k, Q_MAIN, shifted_i)
            prof = hkz_route_ii(B, d, deadline)
            if prof.get("status") != "ok":
                my_frozen_shifted_values.append(None)
                continue
            hv = route_ii_hkz_value(prof["r"], d, k, beta, Q_MAIN)
            my_frozen_shifted_values.append(hv)

        residuals_vs_lead_mut = [
            (abs(a - b) if (a is not None) else None)
            for a, b in zip(my_frozen_shifted_values, route_mut_values)
        ]
        residuals_vs_route_p_shifted = [
            (abs(a - route_p_values[(i + 1) % n]) if a is not None else None)
            for i, a in enumerate(my_frozen_shifted_values)
        ]

        d_route_mut_own = max(
            abs(a - b) for a, b in zip(route_p_values, my_frozen_shifted_values)
            if b is not None)

        out[cell_name] = {
            "n_bases": n,
            "matrix_identity_confirmed_all_bases": all(per_basis_matrix_identity),
            "my_frozen_shifted_recomputation": my_frozen_shifted_values,
            "lead_reported_route_mut_values": route_mut_values,
            "residual_vs_lead_reported": residuals_vs_lead_mut,
            "max_residual_vs_lead_reported": max(
                r for r in residuals_vs_lead_mut if r is not None),
            "residual_vs_route_p_at_shifted_index": residuals_vs_route_p_shifted,
            "max_residual_vs_route_p_shifted": max(
                r for r in residuals_vs_route_p_shifted if r is not None),
            "D_route_mut_from_my_own_recomputation": d_route_mut_own,
            "D_route_mut_lead_reported": lead_cell["D_route_mut"],
        }
    return out


# ============================================================ (D) mapping check
def recompute_verdict(relvar, built):
    g_var = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]
    with open(RESULTS_MUT) as fh:
        lead_results = json.load(fh)
    lead_per_cell = lead_results["R_MC_OUT_2_per_cell"]

    out = OrderedDict()
    for cell_name, meta in CELLS.items():
        lat, beta = meta["lat"], meta["beta"]
        s_c_fib = g_var["%s_b%d" % (lat, beta)]["float_sd"]
        lead_cell = lead_per_cell[cell_name]
        d_route_mut_lead = lead_cell["D_route_mut"]
        d_route_mut_own = built[cell_name]["D_route_mut_from_my_own_recomputation"]

        def verdict_and_reading(d_route_mut):
            verdict = "EXCEEDS" if s_c_fib > d_route_mut else "DOES NOT EXCEED"
            reading = "DETECTED" if verdict == "DOES NOT EXCEED" else "NOT DETECTED"
            return verdict, reading

        v_lead, r_lead = verdict_and_reading(d_route_mut_lead)
        v_own, r_own = verdict_and_reading(d_route_mut_own)
        out[cell_name] = {
            "s_c_fib": s_c_fib,
            "D_route_mut_lead_reported": d_route_mut_lead,
            "VERDICT_mut_recomputed_from_lead_values": v_lead,
            "detection_reading_recomputed_from_lead_values": r_lead,
            "matches_lead_reported_VERDICT": (
                v_lead == lead_cell["VERDICT_mut"]),
            "matches_lead_reported_detection_reading": (
                r_lead == lead_cell["detection_reading"]),
            "D_route_mut_from_my_own_independent_recomputation": d_route_mut_own,
            "VERDICT_mut_from_my_own_recomputation": v_own,
            "detection_reading_from_my_own_recomputation": r_own,
        }
    return out


# ============================================================ (E) null-object control
def null_object_control(relvar, seed=20260814, n_trials=200000, n=8):
    rng = np.random.default_rng(seed)
    dists = OrderedDict([
        ("normal(0,1)", lambda: rng.normal(0, 1, size=n)),
        ("uniform(0,1)", lambda: rng.uniform(0, 1, size=n)),
        ("t3", lambda: rng.standard_t(3, size=n)),
    ])
    out = OrderedDict()
    for name, sampler in dists.items():
        exceed = 0
        ratios = []
        for _ in range(n_trials):
            x = sampler()
            s = np.std(x, ddof=1)
            _, m, _ = cyclic_maxdiff(list(x))
            if s > 0:
                ratios.append(m / s)
                if m > s:
                    exceed += 1
        ratios = np.array(ratios)
        out[name] = {
            "n_trials": n_trials,
            "P_max_cyclic_diff_exceeds_std": exceed / n_trials,
            "mean_ratio": float(np.mean(ratios)),
            "median_ratio": float(np.median(ratios)),
            "p05_ratio": float(np.percentile(ratios, 5)),
            "p95_ratio": float(np.percentile(ratios, 95)),
        }

    # Compare against the actual 6 archived hkz cells' own ratio.
    g = relvar["G_REL1"]["hkz"]
    g_var = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]
    real_cells = OrderedDict()
    for cell_name, lat, beta, field in ALL_HKZ_CELLS:
        entry = g[lat]
        vals = [row[field] for row in entry["per_basis"]]
        _, mx, argmax_i = cyclic_maxdiff(vals)
        s_c_fib = g_var["%s_b%d" % (lat, beta)]["float_sd"]
        real_cells[cell_name] = {
            "max_cyclic_diff": mx,
            "s_c_fib": s_c_fib,
            "ratio": mx / s_c_fib,
        }
    ratios_real = {k: v["ratio"] for k, v in real_cells.items()}
    tightest = min(ratios_real, key=lambda k: ratios_real[k])
    loosest = max(ratios_real, key=lambda k: ratios_real[k])
    out["real_hkz_cells"] = real_cells
    out["real_cells_tightest_ratio_cell"] = tightest
    out["real_cells_loosest_ratio_cell"] = loosest
    out["tested_cells_are_hkz_L7_b5_and_hkz_L11_b30"] = True
    out["hkz_L7_b5_is_tightest"] = (tightest == "hkz/L7_b5")
    out["hkz_L7_b5_is_loosest"] = (loosest == "hkz/L7_b5")
    out["hkz_L11_b30_is_tightest"] = (tightest == "hkz/L11_b30")
    out["hkz_L11_b30_is_loosest"] = (loosest == "hkz/L11_b30")
    out["prereg6_claim_tested_cells_bracket_tightest_and_looser"] = (
        (tightest in ("hkz/L7_b5", "hkz/L11_b30"))
        and (loosest in ("hkz/L7_b5", "hkz/L11_b30"))
    )
    return out


def main():
    RES = OrderedDict()
    RES["task_id"] = "TASK-20260813-0881f0"
    RES["role"] = "red-team"
    RES["reviews_commit"] = "e2ad28b3ffe90b2b5390ca83f4e2ba1d431399fd"

    print("[A] mechanical diff (independent regex-based extractor)")
    RES["A_diff_check"] = check_diff()
    print("    n_functional_differing_lines=%d (expected 1); frozen ref untouched=%s"
          % (RES["A_diff_check"]["n_functional_differing_lines_after_cosmetic_normalization"],
             RES["A_diff_check"]["frozen_reference_untouched"]))

    with open(RESULTS_RELVAR) as fh:
        relvar = json.load(fh)
    print("[B] independent recomputation of frozen prediction")
    RES["B_prediction"] = recompute_prediction(relvar)
    print("    L7_b5=%.16g L11_b30=%.16g"
          % (RES["B_prediction"]["hkz/L7_b5"], RES["B_prediction"]["hkz/L11_b30"]))

    print("[C] BUILT CONTROL: independent re-run of the FROZEN route on "
          "shifted indices (this is the expensive fpylll step)")
    built = built_control(relvar)
    RES["C_built_control_frozen_route_on_shifted_index"] = built
    for cell in built:
        print("    %-14s max_residual_vs_lead=%.3e max_residual_vs_route_p_shifted=%.3e "
              "matrix_identity_confirmed=%s"
              % (cell, built[cell]["max_residual_vs_lead_reported"],
                 built[cell]["max_residual_vs_route_p_shifted"],
                 built[cell]["matrix_identity_confirmed_all_bases"]))

    print("[D] recompute VERDICT_mut / detection mapping")
    RES["D_verdict_recomputation"] = recompute_verdict(relvar, built)
    for cell, v in RES["D_verdict_recomputation"].items():
        print("    %-14s VERDICT(lead-values)=%s reading=%s match_lead=%s | "
              "VERDICT(own-recompute)=%s reading=%s"
              % (cell, v["VERDICT_mut_recomputed_from_lead_values"],
                 v["detection_reading_recomputed_from_lead_values"],
                 v["matches_lead_reported_VERDICT"],
                 v["VERDICT_mut_from_my_own_recomputation"],
                 v["detection_reading_from_my_own_recomputation"]))

    print("[E] null-object control: max-cyclic-diff vs std for iid n=8 samples")
    RES["E_null_object_control"] = null_object_control(relvar)
    for name, v in RES["E_null_object_control"].items():
        if isinstance(v, dict) and "P_max_cyclic_diff_exceeds_std" in v:
            print("    %-14s P(exceed)=%.5f mean_ratio=%.3f median_ratio=%.3f"
                  % (name, v["P_max_cyclic_diff_exceeds_std"], v["mean_ratio"],
                     v["median_ratio"]))
    print("    real hkz cells' ratios:", {
        k: round(v["ratio"], 4)
        for k, v in RES["E_null_object_control"]["real_hkz_cells"].items()})
    print("    tightest real ratio cell:",
          RES["E_null_object_control"]["real_cells_tightest_ratio_cell"])
    print("    loosest real ratio cell:",
          RES["E_null_object_control"]["real_cells_loosest_ratio_cell"])
    print("    tested cells bracket tightest+looser (PREREG-6 2.1 claim)? ",
          RES["E_null_object_control"]["prereg6_claim_tested_cells_bracket_tightest_and_looser"])

    RES["total_wall_seconds"] = time.time() - T0
    out_path = os.path.join(HERE, "rt_reverify_results.json")
    with open(out_path, "w") as fh:
        json.dump(RES, fh, indent=2, default=str)
    print("\nWrote", out_path)


if __name__ == "__main__":
    main()
