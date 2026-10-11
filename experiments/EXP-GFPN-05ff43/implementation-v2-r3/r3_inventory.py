#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r3 successor stage -- the r3 CONSUMER INVENTORY of DV-11 (consumercover CC-5 as extended by
valueclose VC-3; DEC-20260924-e52eec VA-6 (d), VA-7 (b), VA-8; card R3S-10). Development only; called by DV-11
(r3_devchecks_more.dv11). New file.

METHOD (static; its limits are stated in the output):
  1. Every function of every r3 .py file (nested functions and methods included, by qualified name) is parsed with ast.
  2. DETECTOR (over-approximating): a function is a candidate consumer if its own body names (a) a site file (raw-result
     .json, solver-events.json, manifest.yaml, health reports, <tag>.ms.out / .ms.log / .ms.err, callgrind logs, renamed
     attempt files, certificates), or (b) a constant key of a site record (the census's site_record_fields for S-1,
     S-2, S-3 and their child mappings) or of the event record or the derived manifest blocks.
  3. FIXPOINT over data AND control dependence (VC-3): a function that calls a listed function of the r3 layer and
     tests, returns or stores its result is listed too, until nothing changes.
  4. Every listed function carries EXACTLY ONE class from the approved set (alpha, beta, frozen-body, gamma, epsilon,
     or a V-1..V-7 value with its row) or is recorded as reading no site value (VA-8 (b)), from the declared table
     CLASSES below (delivered code) or from the declared development rule DEV_RULE (development-check files: effect E6,
     development report; class by the first value kind the function names, the others listed).
     Deterministic reading adopted (declared in implementation-v2-r3.md): the one class of a function is the class of the
     site values it reads DIRECTLY in its own body; a function that only acts on the finding a listed callee returns
     carries that callee-independent listing "reads no site value directly" (the VA-8 (b) model: a guard is a separate
     function listed under its own class).
  5. CHECKS (each failure is a STOP of DV-11): every listed delivered function is in CLASSES; each entry has exactly one
     class; every gamma entry names its clause; no function with effect E1-E4 reads a V-5 (CG-3) value; no function uses
     an epsilon value to choose a recorded result; no r3 file imports an r1, r2 or v1 module; no r3 file describes S-3
     as "output never classified" without the CORR-20260924-432f43 distinction.
  6. REPORTS: the VA-6 (d) listing and the CG-3 fields no r3 function reads at E1-E4; the VA-7 (b) listing with the
     files the byte sweep reads; the comparison with the archived consumer census by file and function for every r3 file
     started from an r2 file.
"""
import ast
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_common as R                                    # noqa: E402

LAYER = HERE
DEV_FILES = ("r3_devchecks.py", "r3_devchecks_more.py", "r3_dv6.py", "r3_dv7.py", "r3_dv12.py", "r3_dv16.py", "r3_inventory.py")
SITE_FILE_TOKENS = ("raw-result.json", "solver-events.json", "manifest.yaml", "health-", ".ms.out", ".ms.log", ".ms.err",
                    ".callgrind.", ".ssf-attempt", "certificates", "EVENTS_FILE")
EVENT_KEYS = {"sites", "events", "records", "counters", "consistency", "consistency_violation", "attempts", "final_outcome", "final_reason",
              "final_D", "final_ssf_clause", "renamed_files", "resolve_cap_reached", "resolve_cap_detail", "accepted_attempt",
              "still_ssf_after_last_attempt", "ssf_clause", "ssf_attempts_by_clause", "re_solves", "calls_still_ssf_after_last_attempt",
              "wrapped_calls", "attempts_total", "callgrind_children_observed", "log_visible_ssf_indicator", "fglm_squarefree_degree",
              "printed_quotient_dimension_equals_recorded_attempt", "child_readback_equals_requested_cap", "reg1_compared_fields_verbatim"}
DERIVED_KEYS = {"solver_events", "child_rlimit_as_read_back_by_getrlimit", "msolve_threads_executed", "regression_REG-1", "run_status",
                "gate_pass", "failure_class", "verdict", "failures", "D_defined", "targets", "planted_targets", "replaced_fresh_targets",
                "arms", "cells", "v2_bytes_phase_B_check"}
CG3_FIELDS = ["tag", "attempt_recorded_by_the_wrapper", "files (sha256 and size, or absent)", "dimension_of_quotient", "fglm_squarefree_degree",
              "positive_dimension_reported", "random_linear_form_string_in_log", "log_visible_ssf_indicator",
              "printed_quotient_dimension_equals_recorded_attempt", "reg1_compared_fields_verbatim", "child_readback_equals_requested_cap",
              "the manifest's callgrind-site counts (CG-3 three counts; CC-4 count)"]

# --------------------------------------------------------------------------- the declared classification (delivered code)
# key: "file::qualname" -> (class, effect, clause-or-None, reads, note)
G = "gamma"
CLASSES = {
    # r3_resolve.py -- the approved wrapper bodies (VC-1 (a)) and their helpers
    "r3_resolve.py::ssf_clause": (G, "E1", "SF-1 (i)-(v); HR-2", "outcome / v2_outcome_class, reason / v2_outcome_reason, the log text", "the SSF signature test"),
    "r3_resolve.py::log_text": (G, "E1", "SF-1 (v); HR-2 (v)", "<tag>.ms.log, <tag>.ms.err (beta files of the attempt in progress)", "builds the log text exactly as the frozen functions do"),
    "r3_resolve.py::_wait_spacing": (G, "E2", "SF-2 (a); SC-11 (d); HR-4 (c)", "the previous attempt's recorded end UTC", "waits; decides nothing else"),
    "r3_resolve.py::_call_original": (G, "E5", "SE-2 (1), (2)(d); HR-4 (d)", "the frozen function's result (returned unmodified)", ""),
    "r3_resolve.py::_attempt_record_s1": (G, "E5", "SE-2 (2)(a); SC-11 (c)", "S-1 result fields", "recording"),
    "r3_resolve.py::_attempt_record_s2": (G, "E5", "HR-4 (a)", "S-2 result fields; <tag>.ms.out sha256", "recording"),
    "r3_resolve.py::_consistency": (G, "E2", "SE-2 (4); SF-2 (b); SC-11 (d); HR-5", "input sha256, printed quotient dimensions, start / end UTC", "the consistency test"),
    "r3_resolve.py::_rename": (G, "E2", "SE-2 (2)(b); SC-11 (a); HR-4 (b)", "the attempt's .ms.out / .ms.log / .ms.err", "renames and hashes; a pre-existing target raises"),
    "r3_resolve.py::_cap_reached": (G, "E2", "SF-2 (c); SC-11 (c), (e); HR-6", "attempts 2..k wall seconds; the call's timeout", "the cap test"),
    "r3_resolve.py::_bounded": (G, "E1", "SE-2 (1)-(5); SF-1..SF-3 (K = 5); SC-11 (a)-(e); HR-1..HR-6; SE-2 (5) counter rewrite (VA-8 (c))",
                                "every attempt's result (recorded or not)", "the bounded loop at both sites; writes the event record (epsilon), returns the last attempt's result unmodified"),
    "r3_resolve.py::_record_callgrind": (G, "E5", "CG-3; CC-4", "instructions_callgrind (V-1), <tag>.callgrind.stdout / .stderr (V-6)",
                                         "records V-5 under site v2_driver.solve/callgrind; triggers nothing (VA-6 (c))"),
    "r3_resolve.py::solve": (G, "E1", "SE-2; SE-3; SF-1..SF-3; SC-11", "via _bounded; gb_only pass-through (SE-2 (6))", "the SE-3 wrapper body"),
    "r3_resolve.py::solve.after": (G, "E5", "CG-3", "the original call's result", "calls _record_callgrind"),
    "r3_resolve.py::run_system": (G, "E1", "HR-1..HR-8", "via _bounded; a1_health.DEV_TIMEOUT_S read at call time (HR-6)", "the HR-3 wrapper body"),
    "r3_resolve.py::run_system.make": (G, "E5", "HR-4 (a)", "via _attempt_record_s2", ""),
    "r3_resolve.py::_write": (G, "E5", "SE-2 (5); SC-11 (b); HR-8; CG-3", "the event record (epsilon)", "atomic rewrite; NO substring guard (VA-7 (c))"),
    "r3_resolve.py::_sha": (G, "E5", "SE-2 (2)(b); HR-4 (a), (b)", "renamed attempt files, <tag>.ms.out", "hashing for the record"),
    "r3_resolve.py::_empty_doc": ("reads no site value", "E5", None, "constants only", "the record schema"),
    "r3_resolve.py::_site_counters": ("reads no site value", "E5", None, "constants only", "the counter schema"),
    "r3_resolve.py::begin": ("reads no site value", "E5", None, "", "writes the initial empty record"),
    "r3_resolve.py::readback": ("reads no site value", "E2", None, "function identities", "SE-3 read-back"),
    "r3_resolve.py::readback_health": ("reads no site value", "E2", None, "function identities", "HR-3 read-back"),
    "r3_resolve.py::readback_no_health": ("reads no site value", "E2", None, "sys.modules", "HR-3 read-back (v2 entry)"),
    "r3_resolve.py::install": ("reads no site value", "E5", None, "", "SE-3 installation"),
    "r3_resolve.py::install_health": ("reads no site value", "E5", None, "", "HR-3 installation"),
    # r3_run_wrapper.py
    "r3_run_wrapper.py::_raw": ("alpha", "E5", None, "raw-result.json (recorded from the results the wrappers returned)", "loader; a parse failure becomes run_status 'unparseable'"),
    "r3_run_wrapper.py::_manifest": ("alpha", "E5", None, "manifest.yaml run block (status / failure_class derived from the recorded results)", "loader"),
    "r3_run_wrapper.py::r7_gate_packages": ("alpha", "E2", None, "gate packages' run_status, gate_pass", "R-7"),
    "r3_run_wrapper.py::r7_reg1_verdict": ("V-2 (CG-4)", "E2", None, "the REG-1 verdict", "R-7"),
    "r3_run_wrapper.py::r7_controls_a1_image": ("alpha", "E2", None, "controls_a1 image's run_status, gate_pass", "R-7"),
    "r3_run_wrapper.py::r8_requires": ("reads no site value", "E2", None, "existence of manifest.yaml only", "R-8"),
    "r3_run_wrapper.py::r12_contingency": ("alpha", "E2", None, "the replaced package's recorded failure_class", "R-12"),
    "r3_run_wrapper.py::reg1": ("V-1 row K-1 (CG-4)", "E5", None, "REG-1 compare (the comparator itself is listed in r3_reg1.py)", "builds the V-2 block"),
    "r3_run_wrapper.py::preflight": ("reads no site value directly", "E2", None, "the refusals the listed single-class checks return", "orchestrator (VA-8 (b) model)"),
    "r3_run_wrapper.py::collect": ("V-1 row K-2", "E5", None, "generic key-name collection (rlimit_as_child_getrlimit, threads_executed)", "records only; builds V-3"),
    "r3_run_wrapper.py::watchdog_after_resolve": ("epsilon", "E5", None, "S-1 events (re-solved tags); raw cells' watchdog rows", "SF-2 (d) flag, recorded"),
    "r3_run_wrapper.py::_site_block": ("epsilon", "E5", None, "per-site counters and events", "manifest block"),
    "r3_run_wrapper.py::solver_events_block": ("epsilon", "E5", None, "solver-events.json by constant key; the S-3 counts COPIED (recorded only, VA-6 (c))", "manifest block"),
    "r3_run_wrapper.py::consistency_flag": ("epsilon", "E1", None, "the top-level consistency flag (VA-6 (b))", "sets failure_class implementation_error on a raise (SE-2 (4))"),
    "r3_run_wrapper.py::launch": ("alpha", "E1", None, "raw-result.json run_status, failure_class, gate_pass, metrics (recorded results)", "writes the manifest; acts on consistency_flag's finding"),
    "r3_run_wrapper.py::main": ("reads no site value directly", "E2", None, "the refusals of preflight", "orchestrator"),
    # r3_check_run.py
    "r3_check_run.py::frozen_v2": ("V-4", "E2", None, "the frozen v2_check_run, run unchanged in a separate process", ""),
    "r3_check_run.py::frozen_a1": ("V-4", "E2", None, "the frozen a1_check_run, run unchanged in a separate process", ""),
    "r3_check_run.py::find_solver_records": ("V-1 row K-5", "E7", None, "a walk over raw-result.json for solve records", "reacts to no callgrind key"),
    "r3_check_run.py::_acc_row": ("beta", "E6", None, "the recorded attempt's <tag>.ms.out / .ms / .ms.log", "SC-4 accounting row; never acted on"),
    "r3_check_run.py::health_records": ("alpha", "E6", None, "health/health-<p>.json (the results the HR-3 wrapper returned)", "SC-4 input"),
    "r3_check_run.py::sc4_accounting": ("alpha", "E6", None, "recorded ok results of both sites", "SC-4: recorded, never acted on"),
    "r3_check_run.py::events_file_integrity": ("V-7", "E2", None, "whole-file sha256 of solver-events.json vs the manifest's recorded sha256", "VA-6 (a)"),
    "r3_check_run.py::events_file_epsilon": ("epsilon", "E2", None, "exists / parses; top-level flag; S-1 and S-2 counters; K, spacing", "VA-6 (b)"),
    "r3_check_run.py::forbidden_id_keys": ("reads no site value", "E2", None, "task_id, run_card, written_by_task, archived_by by CONSTANT key (census M-3)", "VA-7 (b)"),
    "r3_check_run.py::forbidden_id_sweep": ("reads no site value", "E2", None, "bytes of command.txt, stdout.log, stderr.log, environment.json, pari-stack.json", "VA-7 (b)"),
    "r3_check_run.py::manifest_protocol_checks": ("reads no site value", "E2", None, "manifest protocol fields", ""),
    "r3_check_run.py::pari_stack_checks": ("reads no site value", "E2", None, "the pari-stack.json copy", ""),
    "r3_check_run.py::reg1_recorded_check": ("V-2 (CG-4)", "E2", None, "gate.regression_REG-1 recorded in the manifest", ""),
    "r3_check_run.py::status_agreement": ("alpha", "E2", None, "manifest status vs raw-result run_status", ""),
    "r3_check_run.py::r3_checks": ("reads no site value directly", "E2", None, "the findings of the listed single-class checks", "orchestrator (VA-8 (b) model)"),
    "r3_check_run.py::main": ("V-4", "E2", None, "the frozen checker's exit status; the r3 findings; prints the SC-4 table (E6)", ""),
    # r3_reg1.py (the comparator, unchanged from r2 except the SE-4 (e) structure)
    "r3_reg1.py::_strip": ("V-1 row K-1 (CG-4)", "E7", None, "target entries (removal of X1..X17 paths)", "REG-1 (b) machinery"),
    "r3_reg1.py::strip": ("V-1 row K-1 (CG-4)", "E7", None, "target entries", "REG-1 (b) machinery"),
    "r3_reg1.py::d_table": ("alpha", "E2", None, "recorded outcome / D per target and arm", "REG-1 (b) item, compared in compare"),
    "r3_reg1.py::fresh_k_xR": ("alpha", "E2", None, "recorded x_R; certificates' k", "REG-1 (b) item"),
    "r3_reg1.py::Reader.read": ("V-7", "E2", None, "reference file bytes vs the TASK-20260923-0fa03f post-run receipt", "VC-1 (e) names it"),
    "r3_reg1.py::Reader.ok": ("V-7", "E2", None, "the integrity record", ""),
    "r3_reg1.py::parsed_key": ("beta", "E2", None, "the recorded attempts' <tag>.ms.out / .ms.log / .ms.err / .ms", "REG-1 (d) d-parsed"),
    "r3_reg1.py::solver_events_check": ("epsilon", "E2", None, "exists / parses; flag; S-1 / S-2 events' consistency (VA-6 (b))", "SE-4 (e)"),
    "r3_reg1.py::compare": ("V-1 row K-1 (CG-4)", "E2", None, "(a) .ms, (b) raw-result target entries incl. instructions_callgrind, (c) certificates, (d) .ms.out", "REG-1 itself"),
    "r3_reg1.py::compare.b": ("V-1 row K-1 (CG-4)", "E2", None, "REG-1 (b) item equality", ""),
    "r3_reg1.py::render": ("V-2", "E6", None, "the REG-1 report (quotes solver-events.json in full)", "report only"),
    "r3_reg1.py::main": ("V-2", "E2", None, "the REG-1 verdict (exit status)", ""),
    # r3_accounting.py
    "r3_accounting.py::accounting": ("beta", "E6", None, "a recorded attempt's .ms.out (SC-3 / SC-4)", "never acted on in packages"),
    "r3_accounting.py::nvars_p": ("beta", "E6", None, ".ms header or .ms.log", ""),
    "r3_accounting.py::ms_header": ("beta", "E6", None, ".ms header", ""),
}
CLASSES.update({
    "r3_common.py::PariStack.start_readback": ("reads no site value", "E2", None, "PARI read-backs (the key 'pass' is its own record's)", "RC-2 (a)"),
    "r3_resolve.py::_ensure_doc": ("reads no site value", "E5", None, "", "creates the empty record"),
    "r3_make_plans.py::reg1_block": ("reads no site value", "E5", None, "plan text; REG-1 constants", "plan writer"),
    "r3_make_plans.py::repair_block": ("reads no site value", "E5", None, "constants", "plan writer"),
    "r3_make_plans.py::build": ("reads no site value", "E2", None, "the frozen plans (plan text; no site value)", "plan writer; VA-7 (a) plan-text check"),
    "r3_make_plans.py::main": ("reads no site value", "E2", None, "plan text", "plan writer"),
})
CLASSES.update({
    'r3_check_run.py::which_plan': ('reads no site value', 'E5', None, 'plan text', ''),
    'r3_common.py::PariStack._read': ('reads no site value', 'E5', None, 'PARI defaults', ''),
    'r3_common.py::PariStack.configure': ('reads no site value', 'E5', None, '', 'PS-1 P-A'),
    'r3_common.py::PariStack.exit_readback': ('reads no site value', 'E5', None, 'PARI defaults, /proc/self/status', 'RC-2 (b)'),
    'r3_common.py::check_redirections': ('reads no site value', 'E2', None, 'module attributes; r3 constants', 'RC-3 (d); VA-7 (a)'),
    'r3_common.py::forbidden_ids_in_text': ('reads no site value', 'E2', None, 'text it is given: plan text, constants, pari-stack.json only', 'VA-7 (a)'),
    'r3_common.py::forbidden_ids_in_values': ('reads no site value', 'E2', None, 'r3 constants and redirected values', 'VA-7 (a)'),
    'r3_common.py::hashseed_readback': ('reads no site value', 'E5', None, 'os.environ; sys.flags', 'SE-6'),
    'r3_common.py::load_json': ('reads no site value directly', 'E5', None, "any JSON file (primitive: the caller's class governs each call)", ''),
    'r3_common.py::now': ('reads no site value', 'E5', None, 'clock', ''),
    'r3_common.py::receipt_paths': ('reads no site value', 'E5', None, 'an archive receipt', ''),
    'r3_common.py::sha256_bytes': ('reads no site value directly', 'E5', None, "bytes (primitive: the caller's class governs each call)", ''),
    'r3_common.py::sha256_file': ('reads no site value directly', 'E5', None, "a file (primitive: the caller's class governs each call)", ''),
    'r3_common.py::write_pari_stack_json': ('reads no site value', 'E5', None, 'the pari-stack record (PARI read-backs, redirections, hash seed, entry status)', 'VA-7 (a) guard over a file with no site value'),
    'r3_entry_a1.py::r3_gate_ids': ('reads no site value', 'E5', None, 'plan text', ''),
    'r3_make_plans.py::_split': ('reads no site value', 'E5', None, '', 'plan writer'),
    'r3_make_plans.py::delete_path': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r3_make_plans.py::inputs': ('reads no site value', 'E2', None, 'plan text; minted ids', 'plan writer'),
    'r3_make_plans.py::map_strings': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r3_make_plans.py::ordered': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r3_make_plans.py::rc4c_equal': ('reads no site value', 'E2', None, 'plan text', 'RC-4 (c)'),
    'r3_make_plans.py::render': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r3_reg1.py::Reader.path': ('reads no site value', 'E5', None, 'a path', ''),
    'r3_reg1.py::load_exclusions': ('reads no site value', 'E2', None, 'the exclusion list', 'SE-4 (e): X1..X17 exactly'),
    'r3_resolve.py::_identity': ('reads no site value', 'E5', None, 'function identities', ''),
    'r3_resolve.py::_iso': ('reads no site value', 'E5', None, 'a timestamp', ''),
    'r3_resolve.py::_now': ('reads no site value', 'E5', None, 'clock', 'indirection (development shims only)'),
    'r3_resolve.py::_sleep': ('reads no site value', 'E5', None, '', 'indirection'),
    'r3_resolve.py::_utc': ('reads no site value', 'E5', None, 'clock', ''),
    'r3_run_wrapper.py::disk_files': ('reads no site value', 'E5', None, 'file names of the implementation trees', ''),
    'r3_run_wrapper.py::g1_id': ('reads no site value', 'E5', None, 'plan text', ''),
    'r3_run_wrapper.py::git': ('reads no site value', 'E5', None, 'git output', ''),
    'r3_run_wrapper.py::git_tree_state': ('reads no site value', 'E2', None, 'git output', 'R-4..R-6'),
    'r3_run_wrapper.py::phase_a_commit': ('reads no site value', 'E5', None, 'an archive receipt; git log', 'PS-5'),
    'r3_run_wrapper.py::plans': ('reads no site value', 'E5', None, 'plan text', ''),
    'r3_run_wrapper.py::refuse_forbidden_ids': ('reads no site value', 'E2', None, 'plan text; r3 constants', 'R-13; VA-7 (a)'),
    'r3_run_wrapper.py::sh': ('reads no site value', 'E5', None, 'shell output (versions)', ''),
    'r3_run_wrapper.py::tree_check': ('reads no site value', 'E2', None, 'implementation-tree hashes vs archive receipts', 'R-4..R-6'),
})
# listed by reading, not by the detector (control dependence the detector cannot see)
MANUAL = {
    "r3_entry_v2.py::main": ("epsilon", "E5", None, "the SE-2 (4) / HR-5 consistency raise (as an exception class name)",
                             "records status command_raised_<class> into pari-stack.json and re-raises; chooses no result"),
    "r3_entry_a1.py::main": ("epsilon", "E5", None, "the SE-2 (4) / HR-5 consistency raise (as an exception class name)",
                             "records status command_raised_<class> into pari-stack.json and re-raises; chooses no result"),
}
APPROVED = {"alpha", "beta", "frozen-body", "gamma", "epsilon", "reads no site value", "reads no site value directly", "V-2", "V-4", "V-7",
            "V-1 row K-1 (CG-4)", "V-1 row K-2", "V-1 row K-5", "V-2 (CG-4)", "V-5"}
FORBIDDEN_IMPORT_PREFIXES = ("r1_", "r2_")


def site_keys():
    c = R.load_json(os.path.join(R.EXP_DIR, "dev-evidence", "consumer-census", "consumer-census.json"))["site_record_fields"]
    keys = set()
    for v in c.values():
        keys |= {k for k in v if "(" not in k}
    return keys | EVENT_KEYS | DERIVED_KEYS


def functions(tree):
    out = []

    def visit(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = prefix + ch.name
                out.append((q, ch))
                visit(ch, q + ".")
            elif isinstance(ch, ast.ClassDef):
                visit(ch, prefix + ch.name + ".")
            else:
                visit(ch, prefix)
    visit(tree, "")
    return out


def own_nodes(fn):
    """The nodes of fn's own body, excluding nested function bodies."""
    stack = list(fn.body)
    while stack:
        n = stack.pop()
        yield n
        for ch in ast.iter_child_nodes(n):
            if not isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) or isinstance(ch, ast.Lambda):
                stack.append(ch)


def detect(fn, keys):
    hits = []
    for n in own_nodes(fn):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            s = n.value
            for t in SITE_FILE_TOKENS:
                if t in s:
                    hits.append("file:" + t)
            if s in keys:
                hits.append("key:" + s)
        elif isinstance(n, ast.Attribute) and n.attr in ("EVENTS_FILE",):
            hits.append("file:" + n.attr)
    return sorted(set(hits))


def calls_of(fn):
    out = set()
    for n in own_nodes(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                out.add(f.id)
            elif isinstance(f, ast.Attribute):
                out.add(f.attr)
    return out


def calls_with_args(fn):
    out = set()
    for n in own_nodes(fn):
        if isinstance(n, ast.Call) and (n.args or n.keywords):
            f = n.func
            if isinstance(f, ast.Name):
                out.add(f.id)
            elif isinstance(f, ast.Attribute):
                out.add(f.attr)
    return out


def inventory(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    keys = site_keys()
    files = sorted(f for f in os.listdir(LAYER) if f.endswith(".py"))
    funcs = {}
    imports = {}
    texts = {}
    for f in files:
        src = open(os.path.join(LAYER, f)).read()
        texts[f] = src
        tree = ast.parse(src)
        imports[f] = sorted({a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
                            | {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module})
        for q, fn in functions(tree):
            funcs["%s::%s" % (f, q)] = {"file": f, "qualname": q, "line": fn.lineno, "hits": detect(fn, keys), "calls": calls_of(fn),
                                        "calls_with_args": calls_with_args(fn)}
    listed = {k for k, v in funcs.items() if v["hits"]}
    reason = {k: "direct: " + ", ".join(funcs[k]["hits"][:6]) for k in listed}
    by_name = {}
    for k, v in funcs.items():
        by_name.setdefault(v["qualname"].split(".")[-1], []).append(k)
    changed = True
    while changed:                                        # data and control dependence to a fixpoint (VC-3)
        changed = False
        for k, v in funcs.items():
            if k in listed:
                continue
            dep = []
            for c in v["calls"]:
                for t in by_name.get(c, []):
                    if t not in listed:
                        continue
                    same_file = funcs[t]["file"] == v["file"]
                    delivered_pair = v["file"] not in DEV_FILES and funcs[t]["file"] not in DEV_FILES
                    if same_file or delivered_pair:
                        dep.append(c)
            dep = sorted(set(dep))
            # callee direction: a function that a listed function of the same file (or, for delivered files, of any
            # delivered file) calls with arguments receives site values or values derived from them
            name = v["qualname"].split(".")[-1]
            for t in listed:
                if name in funcs[t]["calls_with_args"]:
                    same_file = funcs[t]["file"] == v["file"]
                    delivered_pair = v["file"] not in DEV_FILES and funcs[t]["file"] not in DEV_FILES
                    if same_file or delivered_pair:
                        dep.append("called with arguments by " + t)
                        break
            if dep:
                listed.add(k)
                reason[k] = "dependence on listed: " + ", ".join(sorted(set(dep))[:5])
                changed = True
    for k in MANUAL:
        listed.add(k)
        reason.setdefault(k, "listed by reading (control dependence the detector cannot see)")
    rows, stops, unclassified = [], [], []
    for k in sorted(listed):
        v = funcs.get(k, {"file": k.split("::")[0], "qualname": k.split("::")[1], "line": None, "hits": []})
        if v["file"] in DEV_FILES:
            hits = " ".join(v["hits"])
            cls = ("V-5" if any(x in hits for x in ("callgrind", "log_visible", "reg1_compared", "child_readback")) else
                   "epsilon" if any(x in hits for x in ("solver-events", "EVENTS_FILE", "key:sites", "key:events", "key:consistency", "key:attempts", "ssf")) else
                   "beta" if any(x in hits for x in (".ms.out", ".ms.log", ".ms.err")) else "alpha")
            row = {"function": k, "line": v["line"], "class": cls, "effect": "E6", "clause": None,
                   "reads": v["hits"], "note": "development check (DEV_RULE): development report, never a run-package outcome"}
        else:
            ent = CLASSES.get(k) or MANUAL.get(k)
            if ent is None:
                unclassified.append(k)
                row = {"function": k, "line": v["line"], "class": None, "effect": None, "clause": None, "reads": v["hits"], "note": "UNCLASSIFIED"}
            else:
                cls, eff, clause, reads, note = ent
                row = {"function": k, "line": v["line"], "class": cls, "effect": eff, "clause": clause, "reads": reads, "detector_hits": v["hits"], "note": note}
        row["listed_because"] = reason.get(k)
        rows.append(row)
    for r in rows:
        if r["class"] is not None and r["class"] not in APPROVED:
            stops.append("%s carries a class outside the approved set: %s" % (r["function"], r["class"]))
        if r["class"] == "gamma" and not r["clause"]:
            stops.append("%s is gamma without its clause" % r["function"])
        if r["class"] == "V-5" and r["effect"] in ("E1", "E2", "E3", "E4"):
            stops.append("%s reads a V-5 value with effect %s (VA-6 (c); CC-5)" % (r["function"], r["effect"]))
    if unclassified:
        stops.append("listed delivered functions without a classification: %s" % unclassified)
    for k in CLASSES:
        if k not in funcs:
            stops.append("the declared table names a function that does not exist: %s" % k)
    # imports (CC-5; VC-3)
    v1_mods = sorted(os.path.splitext(x)[0] for x in os.listdir(os.path.join(R.EXP_DIR, "implementation")) if x.endswith(".py"))
    bad_imports = {f: [m for m in ms if m.startswith(FORBIDDEN_IMPORT_PREFIXES) or m in v1_mods] for f, ms in imports.items()}
    bad_imports = {f: m for f, m in bad_imports.items() if m}
    if bad_imports:
        stops.append("an r3 file imports an r1, r2 or v1 module: %s" % bad_imports)
    never_classified = [f for f, s in texts.items() if "output never classified" in s and "CORR-20260924-432f43" not in s]
    if never_classified:
        stops.append("an r3 file describes S-3 as 'output never classified' without the CORR-20260924-432f43 distinction: %s" % never_classified)
    # epsilon used to choose a recorded result: only gamma chooses (the last attempt); every other epsilon reader is listed E1/E2/E5
    eps_choosers = [r["function"] for r in rows if r["class"] == "epsilon" and "choose" in (r.get("note") or "") and "chooses no result" not in (r.get("note") or "")]
    if eps_choosers:
        stops.append("an r3 consumer uses an epsilon value to choose a recorded result: %s" % eps_choosers)
    va6 = {"V-7 (VA-6 (a))": [r["function"] for r in rows if r["class"] == "V-7" and "solver-events" in str(r["reads"])],
           "epsilon (VA-6 (b))": [r["function"] for r in rows if r["class"] == "epsilon" and r["effect"] in ("E1", "E2", "E5")
                                  and not r["function"].startswith(DEV_FILES)],
           "CG-3 fields no r3 function reads at E1-E4": CG3_FIELDS,
           "readers of CG-3 fields (all at E5 / E6)": [r["function"] for r in rows if r["function"] in ("r3_resolve.py::_record_callgrind",
                                                                                                        "r3_run_wrapper.py::solver_events_block",
                                                                                                        "r3_reg1.py::render") or (r["class"] == "V-5")]}
    va7 = {"constant-key checks (VA-7 (b))": {"function": "r3_check_run.py::forbidden_id_keys", "files": ["manifest.yaml", "raw-result.json", "pari-stack.json",
                                                                                                         "solver-events.json", "the plan"],
                                               "keys": ["task_id", "run_card", "written_by_task", "archived_by"]},
           "byte sweep (VA-7 (b))": {"function": "r3_check_run.py::forbidden_id_sweep",
                                     "files": ["command.txt", "stdout.log", "stderr.log", "environment.json", "pari-stack.json"],
                                     "carries_no_site_record_field": True,
                                     "disclosed": ("stdout.log may hold the frozen drivers' check-name lines 'name PASS|FAIL' (a bit derived from results the "
                                                   "wrappers returned: alpha), and pari-stack.json's status and stderr.log's traceback may name the "
                                                   "SolverEventConsistencyError class when a consistency raise occurred (epsilon). None of these is a field of an "
                                                   "S-1, S-2 or S-3 record (census M-3), each is covered for an integrity reader by its own disposition, and "
                                                   "the sweep's output cannot depend on them (a task-id string can never equal them)")},
           "plan text and r3 constants (VA-7 (a))": ["r3_run_wrapper.py::refuse_forbidden_ids", "r3_common.py::check_redirections",
                                                     "r3_common.py::forbidden_ids_in_text", "r3_common.py::forbidden_ids_in_values",
                                                     "r3_make_plans.py::build"],
           "pari-stack.json writer guard (a file with no site value)": "r3_common.py::write_pari_stack_json",
           "event-record writer (VA-7 (c))": "r3_resolve.py::_write carries NO substring guard"}
    rep = {"method": __doc__, "files": files, "n_functions": len(funcs), "n_listed": len(rows), "rows": rows, "imports": imports,
           "VA-6 (d)": va6, "VA-7 (b)": va7, "declared_table_size": len(CLASSES), "manual_listings": sorted(MANUAL)}
    rep["census_comparison"] = census_comparison(rows)
    counts = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    gam = [{"function": r["function"], "clause": r["clause"]} for r in rows if r["class"] == "gamma"]
    rep["summary"] = {"n_functions": len(funcs), "n_listed": len(rows), "counts_by_class": counts, "gamma": gam,
                      "unclassified": unclassified, "bad_imports": bad_imports, "stops": stops}
    with open(os.path.join(out_dir, "inventory.json"), "w") as fh:
        json.dump(rep, fh, indent=1, default=str)
    return rep


def census_comparison(rows):
    """For every r3 file started from an r2 file: the archived census's rows for the r2 file, by function (site, effect,
    class counts), next to the r3 function's listing."""
    started = {"r3_common.py": "r2_common.py", "r3_resolve.py": "r2_resolve.py", "r3_entry_v2.py": "r2_entry_v2.py", "r3_entry_a1.py": "r2_entry_a1.py",
               "r3_run_wrapper.py": "r2_run_wrapper.py", "r3_check_run.py": "r2_check_run.py", "r3_reg1.py": "r2_reg1.py",
               "r3_accounting.py": "r2_accounting.py", "r3_make_plans.py": "r2_make_plans.py", "r3_devchecks.py": "r2_devchecks.py",
               "r3_devchecks_more.py": "r2_devchecks_more.py", "r3_dv6.py": "r2_dv6.py", "r3_dv12.py": "r2_dv12.py"}
    c = R.load_json(os.path.join(R.EXP_DIR, "dev-evidence", "consumer-census", "consumer-census.json"))
    cols = c["all_hits"]["columns"]
    ix = {n: i for i, n in enumerate(cols)}
    agg = {}
    for r in c["all_hits"]["rows"]:
        f = os.path.basename(r[ix["file"]].split("#")[0])
        if not f.startswith("r2_"):
            continue
        key = (f, r[ix["function"]])
        d = agg.setdefault(key, {})
        t = "%s %s %s" % (r[ix["site"]], r[ix["effect"]], r[ix["class"]])
        d[t] = d.get(t, 0) + 1
    rename = {"r2_checks": "r3_checks", "_attempt_record": "_attempt_record_s1"}
    by_fn = {r["function"]: r for r in rows}
    out = []
    for r3f, r2f in sorted(started.items()):
        for (f, fn), d in sorted(agg.items()):
            if f != r2f:
                continue
            target = "%s::%s" % (r3f, rename.get(fn, fn))
            r3row = by_fn.get(target)
            out.append({"r2": "%s::%s" % (f, fn), "census_rows_by_site_effect_class": d, "r3_function": target,
                        "r3_listing": r3row and {k: r3row.get(k) for k in ("class", "effect", "clause")},
                        "note": None if r3row else "no r3 function of this name is listed (renamed, split or reading no site value; see the note)"})
    return out


if __name__ == "__main__":
    rep = inventory(sys.argv[1])
    print(json.dumps(rep["summary"], indent=1, default=str))
