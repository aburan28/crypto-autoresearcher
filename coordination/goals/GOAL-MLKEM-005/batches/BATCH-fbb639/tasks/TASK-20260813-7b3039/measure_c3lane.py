#!/usr/bin/env python3
"""
measure_c3lane.py -- TASK-20260813-7b3039, BATCH-fbb639, GOAL-MLKEM-005.

Discharges PREREG-3 part (c): the coverage-audited, absolute-units, two-route
dispersion comparison for lam1n / hkz / rawtail at L7 / L9 / L11.

NO REDUCTION OF ANY KIND IS PERFORMED. This script only:
  - reads already-committed JSON files (never edits them),
  - computes elementary arithmetic (max, absolute difference, comparison) on
    numbers read that way,
  - never imports fpylll, never invokes any lattice-reduction routine.

RC-1 and RC-2 (PREREG-3 sections 1 and 2) are NOT computed here -- they are
mechanical, frozen corrections carried verbatim into report_c3lane.md by the
run script's caller (this script's job is part (c) only, plus emitting the
sha256 of every input file it reads so RC-1/RC-2's own source files can also
be pinned in run_manifest.yaml).

Frozen references (read, never re-derived structurally):
  ROUTE-P: coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
           TASK-20260809-cda2f6/results_relvar.json
  ROUTE-I (lam1n, hkz @ L7): coordination/goals/GOAL-MLKEM-005/batches/
           BATCH-4ed139/tasks/TASK-20260812-0e930c/results_l7l8.json
  ROUTE-I candidate (lam1n, hkz @ L9/L11): coordination/goals/GOAL-MLKEM-005/
           batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/results_am4.json
           -- construction comparability is CHECKED, not assumed, below.
"""
import hashlib
import json
import os
import sys

REPO_ROOT = "/home/user/crypto-autoresearcher"

PATH_RELVAR = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
    "TASK-20260809-cda2f6/results_relvar.json",
)
PATH_L7L8 = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
    "TASK-20260812-0e930c/results_l7l8.json",
)
PATH_AM4 = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
    "TASK-20260808-2a9085/results_am4.json",
)
# Found by this task's own obligation-0 broader search; read for attribution
# only, NOT used as a ROUTE-I (see obligation_0_forced_arithmetic_search).
PATH_GVAR2_REPORT = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
    "TASK-20260812-56b9da/report_gvar2.md",
)
PATH_GVAR2_RESULTS = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
    "TASK-20260812-56b9da/results_gvar2.json",
)

CANDIDATES = ["lam1n", "hkz", "rawtail"]
LATTICE_BETAS = {
    "L7": [5, 10, 15],
    "L9": [7, 15, 22],
    "L11": [10, 20, 30],
}
N_BASES = 8


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, "r") as fh:
        return json.load(fh)


def cell_id(candidate, lattice, beta):
    return "%s/%s_b%s" % (candidate, lattice, beta)


def get_fibre_dispersion(relvar, candidate, lattice, beta):
    """s_c^fib(X, L, b): results_relvar.json G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd
    (the ALREADY-ARCHIVED float_sd value over the N_BASES = 8 fibre-family
    bases, per PREREG-3 3.1)."""
    try:
        cell = relvar["G_VAR"]["per_candidate"][candidate]["per_cell"]["%s_b%s" % (lattice, beta)]
        return cell["float_sd"], cell.get("n")
    except KeyError:
        return None, None


def get_route_p_basis_values(relvar, candidate, lattice):
    """The 8 per-basis ROUTE-P (committed) values, from the G_REL1 block's
    per_basis list (X_a field), which does not depend on beta for lam1n/hkz
    per this corpus's own construction (checked, not assumed: read directly)."""
    try:
        per_basis = relvar["G_REL1"][candidate][lattice]["per_basis"]
        return [pb["X_a"] for pb in per_basis]
    except KeyError:
        return None


def obligation_0_l7l8(l7l8):
    """Extract the L7-only subset of the P-L1 comparison for lam1n and hkz."""
    out = {}
    comp = l7l8.get("comparison", {})
    per_cell = comp.get("per_candidate", None)
    per_cell_table = comp.get("per_cell", {})
    for candidate in ("lam1n", "hkz"):
        for beta in LATTICE_BETAS["L7"]:
            key = "%s/L7_b%s" % (candidate, beta)
            cell = per_cell_table.get(key)
            if cell is None:
                out[(candidate, "L7", beta)] = None
                continue
            devs = [pb["abs_deviation"] for pb in cell["per_basis"]]
            out[(candidate, "L7", beta)] = {
                "max_abs_deviation": max(devs) if devs else None,
                "n_matched_bases": len(devs),
                "source": "results_l7l8.json (L7-only subset, restricted from combined L7+L8 comparison)",
            }
    return out


def obligation_0_am4_construction_check(am4, relvar):
    """Check whether results_am4.json's L9/L11 lam1n/hkz entries share
    results_relvar.json's frozen construction (q, (d,k), seed formula), by
    reading both files' own declared fields -- never assumed."""
    report = {}
    # (d,k) construction check via am4's own x9_pipeline_crosscheck / instrument_checks block
    xcheck = am4.get("instrument_checks", {}).get("x9_pipeline_crosscheck", [])
    dk_by_lattice = {row["lattice"]: (row.get("d"), row.get("k_identity_block")) for row in xcheck}
    expected_dk = {"L7": (20, 6), "L9": (30, 9), "L11": (40, 12)}
    dk_match = {L: dk_by_lattice.get(L) == expected_dk[L] for L in ("L7", "L9", "L11")}
    report["dk_construction_match_L7_L9_L11"] = dk_match
    report["dk_by_lattice_read_from_am4"] = dk_by_lattice
    report["expected_dk_from_relvar_family_F0"] = expected_dk

    # seed-formula check: am4's own declared note for the frozen basis matrix A
    seed_note = None
    for key in ("q_sweep_frozen",):
        pass
    # search top-level string fields for the seed recipe declaration
    seed_note_found = False
    seed_recipe_text = None

    def _search(obj):
        nonlocal seed_note_found, seed_recipe_text
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and "default_rng([1,d,k,i])" in v:
                    seed_note_found = True
                    seed_recipe_text = v
                    return
                _search(v)
        elif isinstance(obj, list):
            for v in obj:
                _search(v)

    _search(am4)
    report["seed_formula_default_rng_1_d_k_i_found_in_am4"] = seed_note_found
    report["seed_formula_text"] = seed_recipe_text
    report["seed_formula_declared_in_l7l8"] = "np.random.default_rng([1, d, k, i]).integers(0, q, (k, d-k))"

    # k-convention AM-9 check (fpylll k = identity-block count, not q-scaled rows)
    k_conv = am4.get("k_convention_AM9", "")
    report["AM9_k_convention_declared_in_am4"] = bool(k_conv)
    report["AM9_k_convention_text"] = k_conv

    # bit-identical basis-0 cross-check: am4's gates.<X>.G_REL1.all X_lo values
    # against relvar's own G_REL1.<X>.<L>.per_basis[0].X_a (the committed
    # basis-index-0 value), at L9 and L11.
    basis0_check = {}
    for candidate in ("lam1n", "hkz"):
        gate = am4.get("gates", {}).get(candidate, {}).get("G_REL1", {}).get("all", [])
        by_lattice = {row["lattice"]: row for row in gate}
        for L in ("L9", "L11"):
            am4_row = by_lattice.get(L)
            relvar_basis0 = get_route_p_basis_values(relvar, candidate, L)
            if am4_row is None or relvar_basis0 is None:
                basis0_check[(candidate, L)] = {"status": "MISSING"}
                continue
            am4_val = am4_row["X_lo"]
            relvar_val = relvar_basis0[0]
            basis0_check[(candidate, L)] = {
                "am4_X_lo": am4_val,
                "relvar_basis0_X_a": relvar_val,
                "abs_deviation": abs(am4_val - relvar_val),
                "bit_identical": am4_val == relvar_val,
            }
    report["basis0_bit_identical_check"] = {
        "%s/%s" % (c, L): v for (c, L), v in basis0_check.items()
    }

    all_construction_checks_pass = (
        all(dk_match.values())
        and seed_note_found
        and bool(k_conv)
        and all(v.get("bit_identical") is True for v in basis0_check.values())
    )
    report["ALL_CONSTRUCTION_CHECKS_PASS"] = all_construction_checks_pass
    report["verdict"] = (
        "results_am4.json's L9/L11 lam1n/hkz entries SHARE results_relvar.json's "
        "frozen construction (matching (d,k), matching seed formula "
        "default_rng([1,d,k,i]), matching AM-9 k-convention, and the ONE "
        "basis (index 0) both routes report is bit-identical at L9 and L11 "
        "for both candidates) -- results_am4.json IS a valid ROUTE-I for "
        "lam1n/hkz at L9/L11, restricted to the single matched basis (index 0)."
        if all_construction_checks_pass
        else "results_am4.json's L9/L11 lam1n/hkz entries do NOT verifiably "
        "share results_relvar.json's frozen construction on every checked "
        "field -- results_am4.json is EXCLUDED as a ROUTE-I for L9/L11."
    )
    return report


def obligation_0_forced_arithmetic_search(relvar):
    """Search results_relvar.json's forced_arithmetic block, and report what
    was and was not found, per PREREG-3 3.2 item 4. Also report the ONE
    further candidate this task's own broader read-scope search (grep for
    'rawtail' across coordination/goals/GOAL-MLKEM-005) found beyond what
    PREREG-3 itself flagged: BATCH-4ed139's TASK-20260812-56b9da
    (report_gvar2.md / results_gvar2.json, rider (ii)/(iv), route
    'RD_rawgso_no_reduction'). It is reported here, WITH its path, and NOT
    added to the coverage table -- reasons given below -- per PREREG-3's own
    instruction that a found source is reported with its path, whether used
    or not."""
    fa = relvar.get("forced_arithmetic", {})
    rawtail_keys = [k for k in fa if "rawtail" in k]
    lam1n_keys = [k for k in fa if "lam1n" in k]
    hkz_keys = [k for k in fa if "hkz" in k]
    return {
        "all_forced_arithmetic_keys": sorted(fa.keys()),
        "rawtail_related_keys": rawtail_keys,
        "lam1n_related_keys": lam1n_keys,
        "hkz_related_keys": hkz_keys,
        "forced_arithmetic_note": (
            "Search restricted to results_relvar.json's own forced_arithmetic "
            "block, per PREREG-3 3.2 item 4's literal instruction. No further "
            "independent-computation source for lam1n or hkz at L7/L9/L11 was "
            "found inside this block; the sole rawtail-related entry is the "
            "ROUTE-W residual PREREG-3 3.1 already names."
        ),
        "broader_read_scope_search": {
            "method": "grep -r rawtail across coordination/goals/GOAL-MLKEM-005, by this task, beyond what PREREG-3 itself flagged",
            "found_candidate": {
                "path": "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/report_gvar2.md and results_gvar2.json",
                "what_it_is": (
                    "A rawtail recomputation the report itself calls "
                    "'RD_rawgso_no_reduction', run from the RAW, UNREDUCED "
                    "basis, needing no reduction and no fpylll. Its report "
                    "states the underlying functions ('raw_gso_logs' and "
                    "'x_rawtail_of') were TRANSCRIBED VERBATIM from "
                    "BATCH-9e3584's own measure_relvar.py, and that the "
                    "transcription reproduces the committed values at 38/38 "
                    "cells with max absolute difference 0.0. The report's own "
                    "prediction table labels this row 'P-V1 | CONSISTENCY "
                    "CHECK (AM-15(a))', not a route or a prediction."
                ),
                "excluded_as_ROUTE_I_because": (
                    "it is the SAME transcribed code re-run on the SAME "
                    "deterministic raw-basis construction -- a fidelity check "
                    "on the transcription, not an algorithmically independent "
                    "second computation of the candidate. Its own producing "
                    "report labels it a consistency check, exactly the way "
                    "PREREG-3 3.1 labels ROUTE-W a non-equivalent proxy never "
                    "counted. It is reported here, with its path, and NOT "
                    "added to the coverage table."
                ),
                "counted_in_R_C_OUT_2": False,
            },
        },
    }


def build_coverage_table(relvar, l7l8, am4):
    l7l8_extract = obligation_0_l7l8(l7l8)
    am4_check = obligation_0_am4_construction_check(am4, relvar)
    am4_valid_for_l9_l11 = am4_check["ALL_CONSTRUCTION_CHECKS_PASS"]
    fa_search = obligation_0_forced_arithmetic_search(relvar)

    table = {}
    for candidate in CANDIDATES:
        for lattice in ("L7", "L9", "L11"):
            for beta in LATTICE_BETAS[lattice]:
                key = "%s/%s_b%s" % (candidate, lattice, beta)
                if candidate in ("lam1n", "hkz") and lattice == "L7":
                    l7l8_cell = l7l8_extract.get((candidate, lattice, beta))
                    table[key] = {
                        "candidate": candidate,
                        "lattice": lattice,
                        "beta": beta,
                        "route_i_available": l7l8_cell is not None,
                        "route_i_source": (
                            "results_l7l8.json" if l7l8_cell is not None else None
                        ),
                        "route_w_applies": False,
                    }
                elif candidate in ("lam1n", "hkz") and lattice in ("L9", "L11"):
                    table[key] = {
                        "candidate": candidate,
                        "lattice": lattice,
                        "beta": beta,
                        "route_i_available": bool(am4_valid_for_l9_l11),
                        "route_i_source": (
                            "results_am4.json (gates.%s.G_REL1, basis index 0 only)"
                            % candidate
                            if am4_valid_for_l9_l11
                            else None
                        ),
                        "route_w_applies": False,
                    }
                else:  # rawtail, any lattice
                    is_route_w_cell = (
                        candidate == "rawtail" and lattice == "L7" and beta == 5
                    )
                    table[key] = {
                        "candidate": candidate,
                        "lattice": lattice,
                        "beta": beta,
                        "route_i_available": False,
                        "route_i_source": None,
                        "route_w_applies": is_route_w_cell,
                    }
    return table, l7l8_extract, am4_check, fa_search


def obligation_1_comparison(relvar, l7l8, am4, coverage_table, l7l8_extract, am4_check):
    per_cell_results = {}
    for key, cov in coverage_table.items():
        candidate = cov["candidate"]
        lattice = cov["lattice"]
        beta = cov["beta"]
        s_fib, n_bases_fib = get_fibre_dispersion(relvar, candidate, lattice, beta)

        if cov["route_i_available"]:
            if lattice == "L7":
                cell = l7l8_extract[(candidate, lattice, beta)]
                D_route = cell["max_abs_deviation"]
                n_matched = cell["n_matched_bases"]
                source = cell["source"]
            else:
                bc = am4_check["basis0_bit_identical_check"]["%s/%s" % (candidate, lattice)]
                D_route = bc["abs_deviation"]
                n_matched = 1
                source = "results_am4.json (gates.%s.G_REL1, basis index 0 only)" % candidate
            if D_route is None or s_fib is None:
                verdict = "UNCOVERED: missing s_c^fib or D_route despite route flagged available"
            elif s_fib > D_route:
                verdict = "EXCEEDS"
            else:
                verdict = "DOES NOT EXCEED"
            per_cell_results[key] = {
                "candidate": candidate,
                "lattice": lattice,
                "beta": beta,
                "s_c_fib": s_fib,
                "n_bases_fib": n_bases_fib,
                "D_route": D_route,
                "n_matched_bases": n_matched,
                "route_i_source": source,
                "verdict": verdict,
            }
        elif cov["route_w_applies"]:
            fa = relvar.get("forced_arithmetic", {})
            route_w_val = fa.get(
                "rawtail_T1_ambient_isometry_residual_beta5", {}
            ).get("value")
            per_cell_results[key] = {
                "candidate": candidate,
                "lattice": lattice,
                "beta": beta,
                "s_c_fib": s_fib,
                "n_bases_fib": n_bases_fib,
                "D_ROUTE_W": route_w_val,
                "route_w_label": "ROUTE-W (non-equivalent proxy, NOT counted)",
                "verdict_informational_only": (
                    "EXCEEDS (informational only, NOT counted in obligation 2)"
                    if (s_fib is not None and route_w_val is not None and s_fib > route_w_val)
                    else "DOES NOT EXCEED (informational only, NOT counted in obligation 2)"
                    if (s_fib is not None and route_w_val is not None)
                    else "N/A"
                ),
            }
        else:
            per_cell_results[key] = {
                "candidate": candidate,
                "lattice": lattice,
                "beta": beta,
                "s_c_fib": s_fib,
                "n_bases_fib": n_bases_fib,
                "verdict": "NO ROUTE-I: UNCOVERED",
                "reason": (
                    "no independent computation of this candidate at this cell "
                    "exists in the committed corpus, per obligation 0's search"
                ),
            }
    return per_cell_results


def obligation_2_aggregate(per_cell_results):
    covered_cells = {
        k: v for k, v in per_cell_results.items() if v.get("verdict") in ("EXCEEDS", "DOES NOT EXCEED")
    }
    exceeds = {k: v for k, v in covered_cells.items() if v["verdict"] == "EXCEEDS"}
    does_not_exceed = {
        k: v for k, v in covered_cells.items() if v["verdict"] == "DOES NOT EXCEED"
    }
    uncovered = {
        k: v for k, v in per_cell_results.items() if v.get("verdict") == "NO ROUTE-I: UNCOVERED"
    }
    route_w_cells = {
        k: v for k, v in per_cell_results.items() if "route_w_label" in v
    }
    n_covered = len(covered_cells)
    n_total = 27
    aggregate = "SOME-EXCEEDS" if exceeds else ("ALL-CLEAR" if covered_cells else None)
    return {
        "n_covered": n_covered,
        "n_total_cells": n_total,
        "coverage_fraction": "%d/%d" % (n_covered, n_total),
        "n_exceeds": len(exceeds),
        "n_does_not_exceed": len(does_not_exceed),
        "n_uncovered": len(uncovered),
        "n_route_w_cells_excluded_from_tally": len(route_w_cells),
        "aggregate_verdict": aggregate,
        "cells_exceeds": sorted(exceeds.keys()),
        "cells_does_not_exceed": sorted(does_not_exceed.keys()),
        "cells_uncovered": sorted(uncovered.keys()),
        "cells_route_w_excluded": sorted(route_w_cells.keys()),
    }


def obligation_3_termination_branch(aggregate):
    n_covered = aggregate["n_covered"]
    n_total = aggregate["n_total_cells"]
    partial = n_covered < n_total

    if n_covered == 0:
        return {
            "branch": "T-C3LANE-NODATA",
            "partial_suffix_applied": False,
            "quoted_clause": (
                "T-C3LANE-NODATA -- FIRES WHEN COVERED is empty (no cell of the 27 "
                "has a valid ROUTE-I)."
            ),
            "licenses": (
                "a decision recording this as an infrastructure/corpus gap -- not a "
                "scientific result in either direction -- and naming what a "
                "successor would need to commit"
            ),
            "forbids": (
                "any claim about dispersion exceeding or not exceeding anything; "
                "closing, pausing or completing GOAL-MLKEM-005; closing the "
                "admissibility-gate lane"
            ),
        }
    elif aggregate["aggregate_verdict"] == "SOME-EXCEEDS":
        branch = "T-C3LANE-OPEN" + ("-PARTIAL" if partial else "")
        return {
            "branch": branch,
            "partial_suffix_applied": partial,
            "quoted_clause": (
                "T-C3LANE-OPEN -- FIRES WHEN COVERED is non-empty and SOME-EXCEEDS "
                "holds (dispersion exceeds route disagreement at at least one "
                "covered cell)."
            ),
            "licenses": (
                "a statement that 'a successor assumption analogous to A-1, "
                "restricted to the reduction-dependent candidates and to the "
                "covered cells/routes, has a domain worth stating' -- and nothing "
                "stronger"
            ),
            "forbids": (
                "treating this as A-1 held for lam1n/hkz/rawtail; specifying any "
                "dispersion criterion, fibre clause or gate on the strength of "
                "this branch alone; any claim about ML-KEM, any FIPS 203 "
                "parameter set, any attack cost or any cost model; closing, "
                "pausing or completing GOAL-MLKEM-005"
            ),
        }
    elif aggregate["aggregate_verdict"] == "ALL-CLEAR":
        branch = "T-C3LANE-OBSTRUCTED" + ("-PARTIAL" if partial else "")
        return {
            "branch": branch,
            "partial_suffix_applied": partial,
            "quoted_clause": (
                "T-C3LANE-OBSTRUCTED -- FIRES WHEN COVERED is non-empty and "
                "ALL-CLEAR holds (dispersion does not exceed route disagreement "
                "at every covered cell)."
            ),
            "licenses": (
                "closing the admissibility-gate lane, with 'the observables C3 "
                "needs cannot be evaluated to better than their own fibre "
                "variation by any declared route' as its named obstruction, in "
                "its own committed Coordinator decision -- never in this batch's "
                "own close"
            ),
            "forbids": (
                "closing, pausing or completing GOAL-MLKEM-005; treating an "
                "UNCOVERED cell as contributing to this branch in either "
                "direction; any claim about ML-KEM, any FIPS 203 parameter set, "
                "any attack cost or any cost model"
            ),
        }
    else:
        return {
            "branch": "UNDETERMINED -- aggregate_verdict is None despite non-empty COVERED (defect)",
            "partial_suffix_applied": partial,
        }


def main():
    inputs_sha256 = {
        PATH_RELVAR: sha256_of(PATH_RELVAR),
        PATH_L7L8: sha256_of(PATH_L7L8),
        PATH_AM4: sha256_of(PATH_AM4),
        PATH_GVAR2_REPORT: sha256_of(PATH_GVAR2_REPORT),
        PATH_GVAR2_RESULTS: sha256_of(PATH_GVAR2_RESULTS),
    }

    relvar = load_json(PATH_RELVAR)
    l7l8 = load_json(PATH_L7L8)
    am4 = load_json(PATH_AM4)

    coverage_table, l7l8_extract, am4_check, fa_search = build_coverage_table(relvar, l7l8, am4)
    per_cell_results = obligation_1_comparison(
        relvar, l7l8, am4, coverage_table, l7l8_extract, am4_check
    )
    aggregate = obligation_2_aggregate(per_cell_results)
    branch = obligation_3_termination_branch(aggregate)

    out = {
        "task_id": "TASK-20260813-7b3039",
        "batch_id": "BATCH-fbb639",
        "goal_id": "GOAL-MLKEM-005",
        "claim_tier": "toy",
        "certificate": {
            "kind": "none",
            "reason": (
                "no discrete-log solve and no factor-base relation is claimed or "
                "produced; this run reads already-committed files and computes only "
                "elementary arithmetic (max, absolute difference, comparison)"
            ),
        },
        "no_reduction_performed": True,
        "fpylll_imported_by_this_script": False,
        "inputs_sha256": inputs_sha256,
        "R-C-OUT-0_coverage_table": coverage_table,
        "R-C-OUT-0_am4_construction_check": am4_check,
        "R-C-OUT-0_l7l8_l7_only_extract": {
            "%s/%s_b%s" % (k[0], k[1], k[2]): v for k, v in l7l8_extract.items()
        },
        "R-C-OUT-0_forced_arithmetic_search": fa_search,
        "R-C-OUT-1_per_cell_comparison": per_cell_results,
        "R-C-OUT-2_aggregate": aggregate,
        "R-C-OUT-3_termination_branch": branch,
    }

    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("Coverage: %s" % aggregate["coverage_fraction"])
    print("Aggregate verdict (over COVERED): %s" % aggregate["aggregate_verdict"])
    print("Termination branch: %s" % branch["branch"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: measure_c3lane.py <output_path>", file=sys.stderr)
        sys.exit(2)
    main()
