#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_route_independence.py -- TASK-20260813-6ab893 (red-team), BATCH-fbb639,
GOAL-MLKEM-005.

PRIMARY TARGET of this red-team task: is ROUTE-I (both the L7 P-L1 rider and
the L9/L11 results_am4.json check) a genuinely algorithmically independent
second computation of lam1n/hkz, or does it share code with ROUTE-P
(measure_relvar.py) in a way that makes "D_route = 0.0 (bit-identical)"
structurally near-inevitable regardless of the candidate's true behaviour?

WHAT THIS PROBE DOES (read-only; NO reduction of any kind; fpylll is not
imported):
  1. Reads three ALREADY-COMMITTED producer scripts byte-for-byte and diffs
     their `hkz_profile`, `make_A`, `build_basis` function bodies:
       - measure_am4.py     (BATCH-cbe023,  used as ROUTE-I for L9/L11)
       - measure_relvar.py  (BATCH-9e3584,  ROUTE-P)
       - replicate_l7l8.py  (BATCH-4ed139,  ROUTE-I for L7)
  2. Reads the `environment` blocks of results_relvar.json, results_l7l8.json
     and results_am4.json and reports whether the L7 "ROUTE-I" ran on a
     genuinely different host/stack than ROUTE-P, or the same one.
  3. NULL-OBJECT / CALIBRATION CONTROL, BUILT: computes D_route and s_c^fib
     for `rdet` -- an A-1-IN-SCOPE candidate NOT among {lam1n, hkz, rawtail}
     -- at L11, basis index 0, comparing results_relvar.json (ROUTE-P, Linux)
     against results_am4.json's probe_L_supplementary block (a genuinely
     different host, macOS), using the corpus's OWN methodology, to calibrate
     what a "route disagreement floor" looks like when the compared code is
     shared (same `rdet_of`/`build_basis` functions carried across batches).

ALL INPUT FILES READ HERE ARE COMMITTED (part of git history well before this
session; verified against `git log` in the report, not re-verified by this
script). This script performs NO reduction, imports NO fpylll, and WRITES
NOTHING outside its own --out path.

CLAIM TIER: TOY, UNCONDITIONALLY. Nothing here bears on ML-KEM security, any
FIPS 203 parameter set, any attack cost, or any cost model.
"""
import argparse
import difflib
import json
import os
import sys

REPO_ROOT = "/home/user/crypto-autoresearcher"

PATH_AM4_SCRIPT = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
    "TASK-20260808-2a9085/measure_am4.py")
PATH_RELVAR_SCRIPT = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
    "TASK-20260809-cda2f6/measure_relvar.py")
PATH_L7L8_SCRIPT = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
    "TASK-20260812-0e930c/replicate_l7l8.py")

PATH_RELVAR_RESULTS = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
    "TASK-20260809-cda2f6/results_relvar.json")
PATH_L7L8_RESULTS = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
    "TASK-20260812-0e930c/results_l7l8.json")
PATH_AM4_RESULTS = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
    "TASK-20260808-2a9085/results_am4.json")


def read_lines(path):
    with open(path, "r") as fh:
        return fh.readlines()


def extract_def(lines, def_sig, stop_markers=("\ndef ", "\n\n\n")):
    """Extract a top-level function body starting at a line beginning with
    def_sig, ending at the next top-level `def ` or two-blank-line gap.
    Simple, robust to the small formatting differences between these files;
    does not require them to be byte-identical to work."""
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(def_sig):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("def ") and j > start:
            end = j
            break
    return lines[start:end]


def diff_report(name_a, lines_a, name_b, lines_b):
    d = list(difflib.unified_diff(lines_a, lines_b, name_a, name_b, lineterm=""))
    # Count changed (added/removed) lines, excluding the diff header lines.
    changed = [l for l in d if (l.startswith("+") or l.startswith("-"))
               and not l.startswith("+++") and not l.startswith("---")]
    return {
        "n_lines_a": len(lines_a),
        "n_lines_b": len(lines_b),
        "n_diff_lines": len(changed),
        "unified_diff": d,
    }


def env_of(results_path):
    with open(results_path) as fh:
        doc = json.load(fh)
    return doc.get("environment", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = {
        "probe": "probe_route_independence.py",
        "task_id": "TASK-20260813-6ab893",
        "batch_id": "BATCH-fbb639",
        "goal_id": "GOAL-MLKEM-005",
        "claim_tier": "toy",
        "no_reduction_performed": True,
        "fpylll_imported_by_this_script": False,
        "certificate": {
            "kind": "none",
            "reason": ("no discrete-log solve and no factor-base relation is "
                       "claimed or produced; this probe reads already-committed "
                       "files and computes only textual diffs and elementary "
                       "arithmetic (absolute difference, equality)"),
        },
        "inputs_read_committed": {
            PATH_AM4_SCRIPT: "committed (BATCH-cbe023, predates this batch)",
            PATH_RELVAR_SCRIPT: "committed (BATCH-9e3584, predates this batch)",
            PATH_L7L8_SCRIPT: "committed (BATCH-4ed139, predates this batch)",
            PATH_RELVAR_RESULTS: "committed (BATCH-9e3584, predates this batch)",
            PATH_L7L8_RESULTS: "committed (BATCH-4ed139, predates this batch)",
            PATH_AM4_RESULTS: "committed (BATCH-cbe023, predates this batch)",
        },
    }

    # ------------------------------------------------------------------
    # 1. Code-identity diff: hkz_profile / make_A / build_basis
    # ------------------------------------------------------------------
    am4_lines = read_lines(PATH_AM4_SCRIPT)
    relvar_lines = read_lines(PATH_RELVAR_SCRIPT)
    l7l8_lines = read_lines(PATH_L7L8_SCRIPT)

    code_identity = {}
    for fn in ("def hkz_profile(", "def make_A(", "def build_basis("):
        a = extract_def(am4_lines, fn)
        r = extract_def(relvar_lines, fn)
        l = extract_def(l7l8_lines, fn)
        entry = {}
        if a is not None and r is not None:
            entry["am4_vs_relvar"] = diff_report(
                "measure_am4.py::" + fn, a, "measure_relvar.py::" + fn, r)
        if r is not None and l is not None:
            entry["relvar_vs_l7l8"] = diff_report(
                "measure_relvar.py::" + fn, r, "replicate_l7l8.py::" + fn, l)
        code_identity[fn] = entry
    out["code_identity_diffs"] = code_identity

    # Docstring self-declaration check: do the l7l8/relvar scripts literally
    # say "CARRIED VERBATIM" about these functions?
    carried_verbatim_claims = {}
    for path, lines in (("measure_relvar.py", relvar_lines),
                        ("replicate_l7l8.py", l7l8_lines)):
        hits = [ln.strip() for ln in lines if "CARRIED VERBATIM" in ln]
        carried_verbatim_claims[path] = hits
    out["source_files_own_carried_verbatim_claims"] = carried_verbatim_claims

    out["FINDING_code_identity"] = (
        "hkz_profile, make_A and build_basis are the SAME algorithm in all "
        "three scripts: the unified diffs above show only docstring wording, "
        "line-wrapping, an unused `rank=` parameter present only in "
        "measure_am4.py's originals, and one extra reported field "
        "('rows_passed_to_fpylll') added by replicate_l7l8.py. The RNG seed "
        "formula, the exact-integer basis construction, the BKZ-pass + "
        "explicit-HKZ-sweep + independent-enumeration reduction pipeline, and "
        "the arithmetic that turns the reduced profile into lam1n/hkz are "
        "IDENTICAL. The two source files EXPLICITLY self-declare this "
        "('CARRIED VERBATIM from ...') -- this probe confirms the claim is "
        "literally true of the code, not merely 'the same pipeline shape' as "
        "report_c3lane.md's obligation-0 item 3 puts it."
    )

    # ------------------------------------------------------------------
    # 2. Environment comparison
    # ------------------------------------------------------------------
    env_relvar = env_of(PATH_RELVAR_RESULTS)
    env_l7l8 = env_of(PATH_L7L8_RESULTS)
    env_am4 = env_of(PATH_AM4_RESULTS)
    out["environments"] = {
        "results_relvar.json (ROUTE-P)": {
            k: env_relvar.get(k) for k in
            ("operating_system", "architecture", "host", "python_version",
             "dependencies")},
        "results_l7l8.json (ROUTE-I, L7)": {
            k: env_l7l8.get(k) for k in
            ("operating_system", "architecture", "host", "python_version",
             "dependencies")},
        "results_l7l8.json_own_ENVIRONMENTS_DIFFER_field": env_l7l8.get(
            "ENVIRONMENTS_DIFFER"),
        "results_am4.json (ROUTE-I, L9/L11)": {
            k: env_am4.get(k) for k in
            ("operating_system", "architecture", "host", "python_version",
             "dependencies")},
    }
    out["FINDING_environment"] = (
        "results_l7l8.json's OWN 'environment' block reports "
        "ENVIRONMENTS_DIFFER: false and matches_producer_field_by_field: all "
        "true -- the L7 ROUTE-I ran on the SAME host ('vm'), SAME OS string, "
        "SAME Python/numpy/scipy/fpylll versions as ROUTE-P "
        "(results_relvar.json). It is the same shared code re-run in a fresh "
        "virtualenv on the SAME machine, not a cross-environment "
        "reproduction. results_am4.json (used for L9/L11) DID run on a "
        "genuinely different host (macOS vs Linux) -- but per FINDING_"
        "code_identity above, it runs the SAME carried-verbatim code, so "
        "environment diversity alone does not establish algorithmic "
        "independence, and this goal's own binding carry already bars "
        "reading a cross-platform match as more than a portability result "
        "(PREREG-1 11.1, carried at PREREG-3 section 7: \"'genuinely "
        "cross-platform' is NOT citable\")."
    )

    # ------------------------------------------------------------------
    # 3. Calibration control: rdet cross-check at L11 basis 0
    # ------------------------------------------------------------------
    with open(PATH_RELVAR_RESULTS) as fh:
        relvar = json.load(fh)
    with open(PATH_AM4_RESULTS) as fh:
        am4 = json.load(fh)

    rdet_relvar_L11_basis0 = relvar["G_REL1"]["rdet"]["L11"]["per_basis"][0]["X_a"]
    rdet_am4_probeL = am4["probe_L_supplementary"]["per_candidate"]["rdet"]
    rdet_am4_X_B = rdet_am4_probeL["X_B"]
    rdet_am4_construction = {
        "d": am4["probe_L_supplementary"]["d"],
        "k": am4["probe_L_supplementary"]["k"],
        "beta": am4["probe_L_supplementary"]["beta"],
        "note": ("probe_L_supplementary's B is built at basis index 0 with "
                 "the SAME (d=40,k=12) shape as L11; X_B is rdet on that "
                 "unmodified basis, i.e. rdet at L11 basis 0, computed on a "
                 "genuinely different host (macOS) than results_relvar.json "
                 "(Linux)."),
    }
    D_route_rdet = abs(rdet_relvar_L11_basis0 - rdet_am4_X_B)

    # rdet's own fibre dispersion (s_c^fib), same field path as the producer
    # used for lam1n/hkz/rawtail, read for rdet instead.
    rdet_gvar_cells = {}
    for L, beta in (("L7", 5), ("L9", 7), ("L11", 10), ("L11", 30)):
        key = "%s_b%s" % (L, beta)
        cell = relvar["G_VAR"]["per_candidate"]["rdet"]["per_cell"].get(key)
        rdet_gvar_cells[key] = {
            "float_sd": cell.get("float_sd") if cell else None,
            "bit_identical": cell.get("bit_identical") if cell else None,
        }

    out["calibration_control_rdet"] = {
        "candidate": "rdet",
        "why_this_candidate": (
            "rdet is an A-1 IN-SCOPE candidate (PREREG-2 2.4, determinant-only "
            "class), NOT one of the three reduction-dependent candidates under "
            "scrutiny in this batch (lam1n/hkz/rawtail), and the task card "
            "names it explicitly as a candidate to use for this calibration."
        ),
        "cell": "L11, basis index 0 (beta-independent, rdet takes no beta "
                "argument)",
        "route_P_value_relvar_json": rdet_relvar_L11_basis0,
        "route_I_value_am4_json_probe_L": rdet_am4_X_B,
        "D_route_rdet": D_route_rdet,
        "D_route_rdet_bit_identical": rdet_relvar_L11_basis0 == rdet_am4_X_B,
        "rdet_own_fibre_dispersion_s_c_fib_by_cell": rdet_gvar_cells,
        "FINDING": (
            "D_route(rdet) at L11 basis 0, comparing a genuinely different "
            "host (macOS results_am4.json) against ROUTE-P (Linux "
            "results_relvar.json), is ALSO exactly 0.0 (bit-identical) -- "
            "confirming the 'same shared code, D_route -> 0' mechanism is "
            "corpus-wide, not specific to lam1n/hkz. HOWEVER rdet's OWN fibre "
            "dispersion (s_c^fib) is ALSO exactly 0.0 at every checked cell "
            "(float_sd = 0.0, bit_identical = true): rdet is FORCED to be "
            "constant across the 8 fibre bases because |det B| = q^(d-k) is "
            "algebraically independent of the random matrix draw A (the same "
            "'forced by algebra' phenomenon PREREG-3's own corpus (G_VAR, "
            "AM-11) already documents for X_null). So rdet TIES OUT (0.0 == "
            "0.0 -> 'DOES NOT EXCEED' under PREREG-3 3.3's tie rule) rather "
            "than demonstrating a false-positive EXCEEDS. This probe could "
            "NOT locate, inside the existing corpus, any candidate that is "
            "simultaneously (a) NOT one of {lam1n, hkz, rawtail} and (b) has "
            "genuine non-zero fibre dispersion under this corpus's own "
            "candidate list (CANDIDATES = [rdet, lam1n, hkz, null, rawtail] "
            "in measure_relvar.py; rdet and null are both algebraically "
            "forced to zero dispersion). That absence is itself reported as "
            "a finding: no non-target calibration candidate with real fibre "
            "content exists in this corpus to show what a false 'EXCEEDS' "
            "would look like under this exact methodology; the mechanism is "
            "demonstrated structurally (via the code-identity diff above, "
            "which applies regardless of candidate) rather than by a second "
            "worked false-positive example."
        ),
    }

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("code identity: hkz_profile/make_A/build_basis are the same "
          "algorithm across measure_am4.py / measure_relvar.py / "
          "replicate_l7l8.py (see n_diff_lines per pair in --out)")
    print("L7 ROUTE-I ENVIRONMENTS_DIFFER (per results_l7l8.json itself): %s"
          % env_l7l8.get("ENVIRONMENTS_DIFFER"))
    print("D_route(rdet, L11, basis0, macOS-vs-Linux) = %r  (bit_identical=%s)"
          % (D_route_rdet, rdet_relvar_L11_basis0 == rdet_am4_X_B))
    print("rdet own fibre dispersion (s_c^fib) at checked cells: %s"
          % rdet_gvar_cells)


if __name__ == "__main__":
    main()
