#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE (TASK-20260813-7930a6) -- primary/second/third targets in one
script, each cheap and independently checkable:

  (A) PRIMARY TARGET -- independence of measure_route_reimpl.py's reduction/
      enumeration functions from the barred lineage's make_A/build_basis/
      hkz_profile (measure_am4.py, measure_relvar.py, replicate_l7l8.py,
      including BATCH-4ed139's copy). Extracts every named function's exact
      source text by regex (no manual transcription) and reports:
        - a difflib.SequenceMatcher similarity ratio between each barred
          function and its closest-named reimpl counterpart (0.0-1.0),
        - a raw substring/token-overlap check for any verbatim copy-paste of
          >= 5 consecutive non-blank source lines,
        - whether fpylll is imported/required by the barred lineage's
          hkz_profile (it is, by inspection) and whether it is imported
          anywhere in measure_route_reimpl.py (it must not be, per PREREG-4
          2.2(6)),
        - whether this run's OWN environment has fpylll installed (if it
          does not, the barred hkz_profile's own reduction path is provably
          unusable here, which is independent, additional evidence beyond
          a code diff that ROUTE-I' could not have called into the barred
          kernel even if it wanted to).

  (B) SECOND TARGET -- greps the lead's committed script and its committed
      results_route_reimpl.json for any read of results_l7l8.json or
      results_am4.json as a ROUTE-P source (PREREG-4 2.1 bars both).

  (C) THIRD TARGET -- independently re-derives the 18-cell coverage table
      from results_relvar.json's own G_REL1 block, WITHOUT importing the
      lead's measure_route_reimpl.py or its results_route_reimpl.json, and
      reports which of the 18 cells this probe itself finds covered/
      uncovered, for direct comparison against the lead's and the
      Coordinator's expectation.

Every file this probe reads is read-only; nothing is edited, nothing is
re-run, no basis is reduced, no lattice reduction of any kind is performed
(NO REDUCTION ABOVE d = 40 -- in fact NO reduction of any dimension at all;
this probe only reads committed JSON/text and does elementary linear
algebra library calls once optionally, see probe_rdet_null_control.py for
that).

CLAIM TIER: TOY. Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.
"""
import difflib
import hashlib
import json
import os
import re
import sys

TASK_DIR = os.path.dirname(os.path.abspath(__file__))


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


def rel(p):
    return p.replace(REPO_ROOT + os.sep, "")


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ---------------------------------------------------------------- paths
REIMPL_PY = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/"
    "tasks/TASK-20260813-ea2e96/measure_route_reimpl.py")
RESULTS_REIMPL_JSON = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/"
    "tasks/TASK-20260813-ea2e96/results_route_reimpl.json")
MEASURE_AM4 = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/"
    "tasks/TASK-20260808-2a9085/measure_am4.py")
MEASURE_RELVAR = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/measure_relvar.py")
REPLICATE_L7L8 = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/"
    "tasks/TASK-20260812-0e930c/replicate_l7l8.py")
RESULTS_RELVAR_JSON = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/results_relvar.json")
RESULTS_L7L8_JSON = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/"
    "tasks/TASK-20260812-0e930c/results_l7l8.json")
RESULTS_AM4_JSON = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/"
    "tasks/TASK-20260808-2a9085/results_am4.json")

from collections import OrderedDict  # noqa: E402
BARRED_LINEAGE = OrderedDict([
    ("measure_am4.py", MEASURE_AM4),
    ("measure_relvar.py", MEASURE_RELVAR),
    ("replicate_l7l8.py (BATCH-4ed139 copy)", REPLICATE_L7L8),
])
BARRED_FUNCS = ["make_A", "build_basis", "hkz_profile"]
REIMPL_FUNCS = ["make_A_indep", "build_basis_indep", "gso_full",
                "refresh_row", "lll_reduce", "enumerate_svp"]

FUNC_DEF_RE_TMPL = r"^def %s\(.*?(?=^def [A-Za-z_]|\Z)"


def extract_function(source_text, func_name):
    """Extract a top-level function's full source text by regex: from its
    'def name(' line up to (but not including) the next top-level 'def' or
    EOF. Multiline + dotall so the body (including blank lines) is captured
    verbatim from the committed file -- no manual transcription."""
    pattern = re.compile(FUNC_DEF_RE_TMPL % re.escape(func_name),
                         re.MULTILINE | re.DOTALL)
    m = pattern.search(source_text)
    return m.group(0).rstrip() if m else None


def normalized_lines(text):
    """Non-blank, right-stripped lines, for line-level overlap checks."""
    return [ln.rstrip() for ln in text.splitlines() if ln.strip()]


def longest_common_consecutive_lines(a_lines, b_lines):
    """Length (in lines) of the longest run of lines that appear
    consecutively, identically, in both a_lines and b_lines. A cheap,
    exact, non-fuzzy verbatim-copy detector."""
    sm = difflib.SequenceMatcher(a=a_lines, b=b_lines, autojunk=False)
    block = sm.find_longest_match(0, len(a_lines), 0, len(b_lines))
    return block.size


def main():
    out = OrderedDict()
    out["probe"] = "probe_independence_and_coverage.py"
    out["task_id"] = "TASK-20260813-7930a6"
    out["claim_tier"] = "toy"

    # ================================================================
    # (A) PRIMARY TARGET -- independence diff
    # ================================================================
    reimpl_src = open(REIMPL_PY).read()
    out["A_primary_independence_diff"] = OrderedDict()
    out["A_primary_independence_diff"]["reimpl_script_path"] = rel(REIMPL_PY)
    out["A_primary_independence_diff"]["reimpl_script_sha256"] = sha256_file(REIMPL_PY)

    reimpl_extracted = OrderedDict()
    for fn in REIMPL_FUNCS:
        body = extract_function(reimpl_src, fn)
        reimpl_extracted[fn] = body
    out["A_primary_independence_diff"]["reimpl_functions_extracted"] = {
        fn: (body is not None) for fn, body in reimpl_extracted.items()}

    comparisons = []
    for lineage_name, lineage_path in BARRED_LINEAGE.items():
        if not os.path.isfile(lineage_path):
            comparisons.append({
                "barred_file": lineage_name, "status": "FILE NOT FOUND",
                "path": rel(lineage_path)})
            continue
        barred_src = open(lineage_path).read()
        barred_sha = sha256_file(lineage_path)
        for bfn in BARRED_FUNCS:
            bbody = extract_function(barred_src, bfn)
            if bbody is None:
                comparisons.append({
                    "barred_file": lineage_name, "barred_function": bfn,
                    "status": "FUNCTION NOT FOUND IN BARRED FILE"})
                continue
            b_lines = normalized_lines(bbody)
            # compare against EVERY reimpl function extracted (not just the
            # "obvious" name pairing) so a paraphrase under a different name
            # is not missed by name-matching alone
            best = None
            for rfn, rbody in reimpl_extracted.items():
                if rbody is None:
                    continue
                r_lines = normalized_lines(rbody)
                ratio = difflib.SequenceMatcher(
                    a=bbody, b=rbody, autojunk=False).ratio()
                lcl = longest_common_consecutive_lines(b_lines, r_lines)
                entry = {"reimpl_function": rfn, "char_similarity_ratio": ratio,
                         "longest_common_consecutive_lines": lcl,
                         "barred_function_line_count": len(b_lines),
                         "reimpl_function_line_count": len(r_lines)}
                if best is None or ratio > best["char_similarity_ratio"]:
                    best = entry
            comparisons.append({
                "barred_file": lineage_name, "barred_file_sha256": barred_sha,
                "barred_function": bfn,
                "barred_function_uses_fpylll": ("fpylll" in bbody.lower()
                                                or "IntegerMatrix" in bbody
                                                or "GSO.Mat" in bbody
                                                or "BKZReduction" in bbody
                                                or "Enumeration(" in bbody),
                "best_match_against_reimpl": best,
                "VERBATIM_COPY_FLAG (>=5 consecutive identical lines)":
                    (best is not None and
                     best["longest_common_consecutive_lines"] >= 5),
            })
    out["A_primary_independence_diff"]["per_barred_function_comparison"] = comparisons

    n_verbatim_flags = sum(
        1 for c in comparisons
        if isinstance(c, dict) and
        c.get("VERBATIM_COPY_FLAG (>=5 consecutive identical lines)"))
    out["A_primary_independence_diff"]["n_verbatim_copy_flags"] = n_verbatim_flags
    out["A_primary_independence_diff"]["verdict"] = (
        "CRITICAL: possible verbatim/near-verbatim sharing detected -- see flags"
        if n_verbatim_flags > 0 else
        "NO verbatim or near-verbatim (>=5 consecutive line) overlap found "
        "between any barred make_A/build_basis/hkz_profile body and any "
        "reimpl function; char-level SequenceMatcher ratios reported above "
        "for the reviewer's own judgement rather than collapsed to a single "
        "number.")

    # fpylll import check on the reimpl script itself. Distinguish a REAL
    # Python import statement from a filename merely mentioned inside a
    # string literal (both "fpylll" and the three barred module names are
    # REQUIRED to be named in prose by PREREG-4 2.2(4)/(6)/(7), so a naive
    # substring search over-flags). A statement counts as a real import only
    # if the exact line (not a string spanning it) starts with import/from.
    def real_import_lines(src, module_pattern):
        hits = []
        for lineno, ln in enumerate(src.splitlines(), 1):
            stripped = ln.strip()
            if re.match(r"^(import|from)\s+" + module_pattern, stripped):
                hits.append((lineno, stripped))
        return hits

    fpylll_import_lines = real_import_lines(reimpl_src, r"fpylll\b")
    barred_module_import_lines = real_import_lines(
        reimpl_src, r"(measure_am4|measure_relvar|replicate_l7l8)\b")
    out["A_primary_independence_diff"]["reimpl_real_fpylll_import_statements"] = fpylll_import_lines
    out["A_primary_independence_diff"]["reimpl_real_barred_module_import_statements"] = barred_module_import_lines
    out["A_primary_independence_diff"]["FINDING_report_claim_6_precision"] = (
        "The lead's report (section 'Implementation-choice declaration', "
        "point 6) states verbatim: 'No fpylll import, no fpylll call, and "
        "no import of measure_am4.py / measure_relvar.py / replicate_l7l8.py "
        "or any function from them appears anywhere in this script.' "
        "TAKEN LITERALLY THIS IS FALSE: line %d of the committed script "
        "reads '%s' -- a genuine 'import fpylll' statement DOES appear. "
        "By direct inspection this import sits inside a try/except block "
        "used ONLY to test whether fpylll is installed (the boolean result "
        "feeds environment_check.fpylll_available and nothing else; the "
        "import raises ModuleNotFoundError and is caught, so fpylll is "
        "never successfully imported or called in this run, and no "
        "lam1n'/hkz' value is computed from it) -- so the SUBSTANTIVE claim "
        "(no fpylll routine is used to compute ROUTE-I') holds. But the "
        "LITERAL sentence in point 6 is imprecise: it should have said "
        "'no fpylll import outside the environment-capability probe' "
        "rather than 'no fpylll import ... appears anywhere'. This is "
        "exactly the kind of claim PREREG-4/the task card requires be "
        "checked against the actual script rather than trusted from prose "
        "-- checked here, and found technically overstated, though not "
        "load-bearing for the independence conclusion." % (
            fpylll_import_lines[0][0] if fpylll_import_lines else -1,
            fpylll_import_lines[0][1] if fpylll_import_lines else ""),
    )
    out["A_primary_independence_diff"]["FINDING_barred_module_import_false_positive_check"] = (
        "A naive substring search for 'measure_am4'/'measure_relvar'/"
        "'replicate_l7l8' anywhere in the script text (not restricted to "
        "real import statements) DOES match -- but every match is inside "
        "the IMPLEMENTATION_CHOICE_DECLARATION string literal, naming "
        "those files as the lineage NOT consulted (required disclosure "
        "text, not an import). reimpl_real_barred_module_import_statements "
        "above is empty: no line of the form 'import measure_am4' / "
        "'from measure_am4 import ...' (or measure_relvar / "
        "replicate_l7l8) exists anywhere in the committed script.")

    # this probe's OWN environment fpylll check (independent confirmation of
    # the lead's own environment_check, run separately in this probe's own
    # process rather than trusted from the lead's report)
    have_fpylll_here = False
    fpylll_err_here = None
    try:
        import fpylll  # noqa: F401
        have_fpylll_here = True
    except Exception as ex:
        fpylll_err_here = "%s: %s" % (type(ex).__name__, ex)
    out["A_primary_independence_diff"]["THIS_PROBES_OWN_fpylll_check"] = {
        "fpylll_available_in_this_probe_process": have_fpylll_here,
        "fpylll_import_error": fpylll_err_here,
        "note": ("Run independently in this Red Team probe's own process, "
                 "not trusted from the lead's report. If fpylll is "
                 "unavailable here too, the barred hkz_profile's own "
                 "reduction path (which hard-requires fpylll.GSO/BKZ/"
                 "Enumeration, confirmed above) could not have been called "
                 "successfully by ANY script in this environment, "
                 "regardless of whether it were imported -- an "
                 "environmental fact independent of, and additional to, "
                 "the code diff above."),
    }

    # ================================================================
    # (B) SECOND TARGET -- ROUTE-P exclusion discipline
    # ================================================================
    out["B_second_route_p_exclusion"] = OrderedDict()
    script_hits = re.findall(r"results_l7l8\.json|results_am4\.json", reimpl_src)
    out["B_second_route_p_exclusion"]["reimpl_script_TEXT_mentions_raw_count"] = len(script_hits)
    # A naive text grep flags string-literal MENTIONS (e.g. inside RC3_TEXT
    # or IMPLEMENTATION_CHOICE_DECLARATION, which are required to NAME these
    # files as excluded) as if they were reads. Distinguish mention-in-a-
    # string from an actual file open: find every line containing either
    # filename and classify it by whether that line is inside an assignment
    # to a *_PATH variable that is later passed to open()/sha256_file(), or
    # is plain prose/string content.
    path_var_lines = [ln for ln in reimpl_src.splitlines()
                      if re.search(r"^[A-Z_]+_PATH\s*=", ln)]
    opened_path_vars = set(re.findall(r"open\((\w+)", reimpl_src)) | \
                       set(re.findall(r"sha256_file\((\w+)", reimpl_src))
    defined_path_vars = set(re.findall(r"^([A-Z_]+_PATH)\s*=", reimpl_src, re.MULTILINE))
    unopened_path_vars = sorted(defined_path_vars - opened_path_vars)
    l7l8_or_am4_path_var_defined = any(
        ("l7l8" in ln.lower() or "am4" in ln.lower()) for ln in path_var_lines)
    hit_lines = [ln.strip() for ln in reimpl_src.splitlines()
                if re.search(r"results_l7l8\.json|results_am4\.json", ln)]
    all_hits_are_string_literal_prose = all(
        (ln.lstrip().startswith('"') or ln.lstrip().startswith("'") or
         '"' in ln) and not re.search(r"^[A-Z_]+_PATH\s*=", ln)
        for ln in hit_lines)
    out["B_second_route_p_exclusion"]["lines_containing_either_filename"] = hit_lines
    out["B_second_route_p_exclusion"]["a_results_l7l8_or_am4_PATH_variable_is_defined"] = (
        l7l8_or_am4_path_var_defined)
    out["B_second_route_p_exclusion"]["all_text_hits_are_string_literal_prose_not_code"] = (
        all_hits_are_string_literal_prose)
    out["B_second_route_p_exclusion"]["defined_but_never_opened_PATH_variables"] = (
        unopened_path_vars)
    results_json_text = open(RESULTS_REIMPL_JSON).read()
    json_hits = re.findall(r"results_l7l8\.json|results_am4\.json", results_json_text)
    out["B_second_route_p_exclusion"]["results_route_reimpl_json_mentions_raw_count"] = len(json_hits)
    real_violation = (l7l8_or_am4_path_var_defined and
                      not all_hits_are_string_literal_prose)
    out["B_second_route_p_exclusion"]["VERDICT"] = (
        "CONSTRAINT VIOLATION -- a results_l7l8.json/results_am4.json PATH "
        "variable is defined AND actually opened/read as code"
        if real_violation else
        "CONFIRMED, WITH A CAVEAT NAMED EXPLICITLY: every occurrence of "
        "'results_l7l8.json'/'results_am4.json' in the committed script is "
        "inside a STRING LITERAL (RC3_TEXT or IMPLEMENTATION_CHOICE_"
        "DECLARATION, both required by PREREG-4 to name these files as "
        "excluded) -- never a path variable that is opened, read or "
        "hashed. No open()/sha256_file() call anywhere in the script "
        "touches either file. results_am4.json/results_l7l8.json appear "
        "in results_route_reimpl.json ONLY because the script copies the "
        "RC3_TEXT/declaration strings into its own JSON output verbatim. "
        "A NAIVE TEXT GREP (as this probe's B_second check first performs, "
        "reported above as the raw hit count) WOULD FALSELY FLAG THIS AS A "
        "VIOLATION; this refined check distinguishes mention-in-prose from "
        "an actual file read and finds no actual read.")
    out["B_second_route_p_exclusion"]["ADDITIONAL_FINDING_dead_path_variables"] = (
        "RESULTS_C3LANE_PATH and PREREG4_PATH are DEFINED in the script "
        "(lines matching '^RESULTS_C3LANE_PATH =' / '^PREREG4_PATH =') but "
        "NEVER passed to open() or sha256_file() anywhere in the committed "
        "script -- confirmed by direct regex search, see "
        "defined_but_never_opened_PATH_variables above. run_manifest.yaml's "
        "input_shas nonetheless lists a sha256 for results_c3lane.json "
        "(e70cb2d4...a10662) with a note that it was 'read only to confirm "
        "this batch's own understanding of the barred ROUTE-I lineage'. "
        "That hash could NOT have been produced by this committed script, "
        "since the script never reads that path -- it must have been "
        "computed some other way (e.g. a shell sha256sum, or the "
        "producing agent's own file-read outside this script) during "
        "report-writing. This is a minor PROVENANCE GAP, not a ROUTE-P "
        "exclusion violation (results_c3lane.json is not results_l7l8.json "
        "or results_am4.json and was never claimed as a ROUTE-P source), "
        "but it means the run_manifest's implicit suggestion that every "
        "listed input_sha was read BY THIS SCRIPT is not fully supported "
        "by the script's own text for this one entry.")

    # ================================================================
    # (C) THIRD TARGET -- independent coverage re-derivation
    # ================================================================
    out["C_third_coverage_rederivation"] = OrderedDict()
    relvar = json.load(open(RESULTS_RELVAR_JSON))
    out["C_third_coverage_rederivation"]["source_sha256"] = sha256_file(RESULTS_RELVAR_JSON)
    g_rel1 = relvar["G_REL1"]
    LATTICES = OrderedDict([("L7", (20, 6)), ("L9", (30, 9)), ("L11", (40, 12))])
    BETA_GRID = {20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
    CANDIDATES = ["lam1n", "hkz"]
    cov = OrderedDict()
    n_covered = 0
    for cand in CANDIDATES:
        for lat, (d, k) in LATTICES.items():
            entry = g_rel1[cand][lat]
            beta_lo, beta_hi = entry["beta_lo"], entry["beta_hi"]
            n_bases = len(entry["per_basis"])
            for beta in BETA_GRID[d]:
                key = "%s/%s_b%d" % (cand, lat, beta)
                covered = (beta == beta_lo or beta == beta_hi)
                cov[key] = {"beta_lo": beta_lo, "beta_hi": beta_hi,
                           "beta": beta, "covered": covered,
                           "n_bases_if_covered": n_bases if covered else 0}
                if covered:
                    n_covered += 1
    out["C_third_coverage_rederivation"]["per_cell"] = cov
    out["C_third_coverage_rederivation"]["n_covered_of_18"] = n_covered
    middle_beta_cells = [k for k, v in cov.items()
                         if v["beta"] != v["beta_lo"] and v["beta"] != v["beta_hi"]]
    out["C_third_coverage_rederivation"]["middle_beta_cells_found_uncovered"] = [
        k for k in middle_beta_cells if not cov[k]["covered"]]
    out["C_third_coverage_rederivation"]["middle_beta_cells_found_covered"
        "_CONTRARY_TO_EXPECTATION"] = [
        k for k in middle_beta_cells if cov[k]["covered"]]
    out["C_third_coverage_rederivation"]["matches_lead_reported_12_of_18"] = (
        n_covered == 12)

    with open(sys.argv[1] if len(sys.argv) > 1 else
             os.path.join(TASK_DIR, "probe_independence_and_coverage_output.json"),
             "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(json.dumps({
        "n_verbatim_copy_flags": n_verbatim_flags,
        "route_p_exclusion_verdict": out["B_second_route_p_exclusion"]["VERDICT"],
        "reimpl_real_fpylll_import_statements": fpylll_import_lines,
        "reimpl_real_barred_module_import_statements": barred_module_import_lines,
        "n_covered_of_18_independent": n_covered,
        "matches_lead_reported_12_of_18": n_covered == 12,
        "this_probes_own_fpylll_available": have_fpylll_here,
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
