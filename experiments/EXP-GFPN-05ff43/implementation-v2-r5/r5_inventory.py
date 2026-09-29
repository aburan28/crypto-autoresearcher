#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r4 stage (TASK-20260924-d91a96) -- the r4 CONSUMER INVENTORY of DV-11 (consumercover CC-5 as
extended by valueclose VC-3; DEC-20260924-e52eec VA-6 (d), VA-7 (b), VA-8; readbackcover RB-7; readbackfull RL-5;
readbackclose RK-5; failclosed RF-7; childend RG-8; gapattr RH-7 with attcount RI-5 (b); DEC-20260924-daf670 LKA-8,
LKA-9). Development only; called by DV-11 (r5_devchecks_more.dv11). Started from implementation-v2-r3/r3_inventory.py.

METHOD (static; its limits are stated in the output):
  1. Every function of every r4 .py file (nested functions and methods included, by qualified name) is parsed with ast.
  2. DETECTOR (over-approximating): a function is a candidate consumer if its own body names (a) a site file (raw-result
     .json, solver-events.json, manifest.yaml, health reports, <tag>.ms.out / .ms.log / .ms.err, callgrind logs, renamed
     attempt files, certificates), or (b) a constant key of a site record (the census's site_record_fields for S-1,
     S-2, S-3 and their child mappings) or of the event record or the derived manifest blocks.
  3. FIXPOINT over data AND control dependence (VC-3): a function that calls a listed function of the r4 layer and
     tests, returns or stores its result is listed too, until nothing changes.
  4. Every listed function carries EXACTLY ONE class from the approved set (alpha, beta, frozen-body, gamma, epsilon,
     or a V-1..V-7 value with its row) or is recorded as reading no site value (VA-8 (b)), from the declared table
     CLASSES below (delivered code) or from the declared development rule DEV_RULE (development-check files: effect E6,
     development report; class by the first value kind the function names, the others listed).
     Deterministic reading adopted (declared in implementation-v2-r3.md, carried to r4): the one class of a function is the class of the
     site values it reads DIRECTLY in its own body; a function that only acts on the finding a listed callee returns
     carries that callee-independent listing "reads no site value directly" (the VA-8 (b) model: a guard is a separate
     function listed under its own class).
  5. CHECKS (each failure is a STOP of DV-11): every listed delivered function is in CLASSES; each entry has exactly one
     class; every gamma entry names its clause; no function with effect E1-E4 reads a V-5 (CG-3) value; no function uses
     an epsilon value to choose a recorded result; no r4 file imports an r1, r2, r3 or v1 module; no r4 file describes
     S-3 as "output never classified" without the CORR-20260924-432f43 distinction; r4 additions: (LKA-8) every
     function that reads an RB-1 value (an attempt or pass-through record field) at E1-E4 is one of the consumers the
     incorporating texts name (attcount RI-1 (a) (i), (ii): r5_gaps.ri1_counts; launchkind RJ-1 (b):
     r5_gaps.rj1_callgrind) or a gamma writer; (LKA-9) callgrind_result_present is written by exactly one function,
     r5_resolve._rb1_callgrind_result_present, whose body is exactly the key-membership test
     `"instructions_callgrind" in res`, called only by r5_resolve._rb1_s1, and read at E1-E4 only by
     r5_gaps.rj1_callgrind; no delivered function with effect E1-E4 names a CG-3 field, the S-3 (callgrind-site)
     section or a callgrind-site count (VA-6 (c); CC-5); the REQUIRED LISTINGS of RB-7, RL-5, RG-8, RH-7 / RI-5 (b)
     and LKA-8 / LKA-9 are each present with exactly the class those texts give.
  6. REPORTS: the VA-6 (d) listing and the CG-3 fields no r4 function reads at E1-E4; the VA-7 (b) listing with the
     files the byte sweep reads; the comparison with the archived consumer census by file and function for every r4 file
     whose r3 origin started from an r2 file; the classification LABELS of RG-2 and RH-2 (no value class).
"""
import ast
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402

LAYER = HERE
DEV_FILES = ("r5_devchecks.py", "r5_devchecks_more.py", "r5_dv6.py", "r5_dv7.py", "r5_dv12.py", "r5_dv16.py", "r5_inventory.py")
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
    # r5_resolve.py -- the approved wrapper bodies (VC-1 (a)) and their helpers
    "r5_resolve.py::ssf_clause": (G, "E1", "SF-1 (i)-(v); HR-2", "outcome / v2_outcome_class, reason / v2_outcome_reason, the log text", "the SSF signature test"),
    "r5_resolve.py::log_text": (G, "E1", "SF-1 (v); HR-2 (v)", "<tag>.ms.log, <tag>.ms.err (beta files of the attempt in progress)", "builds the log text exactly as the frozen functions do"),
    "r5_resolve.py::_wait_spacing": (G, "E2", "SF-2 (a); SC-11 (d); HR-4 (c)", "the previous attempt's recorded end UTC", "waits; decides nothing else"),
    "r5_resolve.py::_call_original": (G, "E5", "SE-2 (1), (2)(d); HR-4 (d)", "the frozen function's result (returned unmodified)", ""),
    "r5_resolve.py::_attempt_record_s1": (G, "E5", "SE-2 (2)(a); SC-11 (c)", "S-1 result fields", "recording"),
    "r5_resolve.py::_attempt_record_s2": (G, "E5", "HR-4 (a)", "S-2 result fields; <tag>.ms.out sha256", "recording"),
    "r5_resolve.py::_consistency": (G, "E2", "SE-2 (4); SF-2 (b); SC-11 (d); HR-5", "input sha256, printed quotient dimensions, start / end UTC", "the consistency test"),
    "r5_resolve.py::_rename": (G, "E2", "SE-2 (2)(b); SC-11 (a); HR-4 (b)", "the attempt's .ms.out / .ms.log / .ms.err", "renames and hashes; a pre-existing target raises"),
    "r5_resolve.py::_cap_reached": (G, "E2", "SF-2 (c); SC-11 (c), (e); HR-6", "attempts 2..k wall seconds; the call's timeout", "the cap test"),
    "r5_resolve.py::_bounded": (G, "E1", "SE-2 (1)-(5); SF-1..SF-3 (K = 5); SC-11 (a)-(e); HR-1..HR-6; SE-2 (5) counter rewrite (VA-8 (c))",
                                "every attempt's result (recorded or not)", "the bounded loop at both sites; writes the event record (epsilon), returns the last attempt's result unmodified"),
    "r5_resolve.py::_record_callgrind": (G, "E5", "CG-3; CC-4", "instructions_callgrind (V-1), <tag>.callgrind.stdout / .stderr (V-6)",
                                         "records V-5 under site v2_driver.solve/callgrind; triggers nothing (VA-6 (c))"),
    "r5_resolve.py::solve": (G, "E1", "SE-2; SE-3; SF-1..SF-3; SC-11", "via _bounded; gb_only pass-through (SE-2 (6))", "the SE-3 wrapper body"),
    "r5_resolve.py::solve.after": (G, "E5", "CG-3", "the original call's result", "calls _record_callgrind"),
    "r5_resolve.py::run_system": (G, "E1", "HR-1..HR-8", "via _bounded; a1_health.DEV_TIMEOUT_S read at call time (HR-6)", "the HR-3 wrapper body"),
    "r5_resolve.py::run_system.make": (G, "E5", "HR-4 (a)", "via _attempt_record_s2", ""),
    "r5_resolve.py::_write": (G, "E5", "SE-2 (5); SC-11 (b); HR-8; CG-3", "the event record (epsilon)", "atomic rewrite; NO substring guard (VA-7 (c))"),
    "r5_resolve.py::_sha": (G, "E5", "SE-2 (2)(b); HR-4 (a), (b)", "renamed attempt files, <tag>.ms.out", "hashing for the record"),
    "r5_resolve.py::_empty_doc": ("reads no site value", "E5", None, "constants only", "the record schema"),
    "r5_resolve.py::_site_counters": ("reads no site value", "E5", None, "constants only", "the counter schema"),
    "r5_resolve.py::begin": ("reads no site value", "E5", None, "", "writes the initial empty record"),
    "r5_resolve.py::readback": ("reads no site value", "E2", None, "function identities", "SE-3 read-back"),
    "r5_resolve.py::readback_health": ("reads no site value", "E2", None, "function identities", "HR-3 read-back"),
    "r5_resolve.py::readback_no_health": ("reads no site value", "E2", None, "sys.modules", "HR-3 read-back (v2 entry)"),
    "r5_resolve.py::install": ("reads no site value", "E5", None, "", "SE-3 installation"),
    "r5_resolve.py::install_health": ("reads no site value", "E5", None, "", "HR-3 installation"),
    # r5_run_wrapper.py
    "r5_run_wrapper.py::_raw": ("alpha", "E5", None, "raw-result.json (recorded from the results the wrappers returned)", "loader; a parse failure becomes run_status 'unparseable'"),
    "r5_run_wrapper.py::_manifest": ("alpha", "E5", None, "manifest.yaml run block (status / failure_class derived from the recorded results)", "loader"),
    "r5_run_wrapper.py::r7_gate_packages": ("alpha", "E2", None, "gate packages' run_status, gate_pass", "R-7"),
    "r5_run_wrapper.py::r7_reg1_verdict": ("V-2 (CG-4)", "E2", None, "the REG-1 verdict", "R-7"),
    "r5_run_wrapper.py::r7_controls_a1_image": ("alpha", "E2", None, "controls_a1 image's run_status, gate_pass", "R-7"),
    "r5_run_wrapper.py::r8_requires": ("reads no site value", "E2", None, "existence of manifest.yaml only", "R-8"),
    "r5_run_wrapper.py::r12_contingency": ("alpha", "E2", None, "the replaced package's recorded failure_class", "R-12"),
    "r5_run_wrapper.py::reg1": ("V-1 row K-1 (CG-4)", "E5", None, "REG-1 compare (the comparator itself is listed in r5_reg1.py)", "builds the V-2 block"),
    "r5_run_wrapper.py::preflight": ("reads no site value directly", "E2", None, "the refusals the listed single-class checks return", "orchestrator (VA-8 (b) model)"),
    "r5_run_wrapper.py::collect": ("V-1 row K-2", "E5", None, "generic key-name collection (rlimit_as_child_getrlimit, threads_executed)", "records only; builds V-3"),
    "r5_run_wrapper.py::watchdog_after_resolve": ("epsilon", "E5", None, "S-1 events (re-solved tags); raw cells' watchdog rows", "SF-2 (d) flag, recorded"),
    "r5_run_wrapper.py::_site_block": ("epsilon", "E5", None, "per-site counters and events", "manifest block"),
    "r5_run_wrapper.py::solver_events_block": ("epsilon", "E5", None, "solver-events.json by constant key; the S-3 counts COPIED (recorded only, VA-6 (c))", "manifest block"),
    "r5_run_wrapper.py::consistency_flag": ("epsilon", "E1", None, "the top-level consistency flag (VA-6 (b))", "sets failure_class implementation_error on a raise (SE-2 (4))"),
    "r5_run_wrapper.py::launch": ("alpha", "E1", None, "raw-result.json run_status, failure_class, gate_pass, metrics (recorded results)", "writes the manifest; acts on consistency_flag's finding"),
    "r5_run_wrapper.py::main": ("reads no site value directly", "E2", None, "the refusals of preflight", "orchestrator"),
    # r5_check_run.py
    "r5_check_run.py::frozen_v2": ("V-4", "E2", None, "the frozen v2_check_run, run unchanged in a separate process", ""),
    "r5_check_run.py::frozen_a1": ("V-4", "E2", None, "the frozen a1_check_run, run unchanged in a separate process", ""),
    "r5_check_run.py::find_solver_records": ("V-1 row K-5", "E7", None, "a walk over raw-result.json for solve records", "reacts to no callgrind key"),
    "r5_check_run.py::_acc_row": ("beta", "E6", None, "the recorded attempt's <tag>.ms.out / .ms / .ms.log", "SC-4 accounting row; never acted on"),
    "r5_check_run.py::health_records": ("alpha", "E6", None, "health/health-<p>.json (the results the HR-3 wrapper returned)", "SC-4 input"),
    "r5_check_run.py::sc4_accounting": ("alpha", "E6", None, "recorded ok results of both sites", "SC-4: recorded, never acted on"),
    "r5_check_run.py::events_file_integrity": ("V-7", "E2", None, "whole-file sha256 of solver-events.json vs the manifest's recorded sha256", "VA-6 (a)"),
    "r5_check_run.py::events_file_epsilon": ("epsilon", "E2", None, "exists / parses; top-level flag; S-1 and S-2 counters; K, spacing", "VA-6 (b)"),
    "r5_check_run.py::forbidden_id_keys": ("reads no site value", "E2", None, "task_id, run_card, written_by_task, archived_by by CONSTANT key (census M-3)", "VA-7 (b)"),
    "r5_check_run.py::forbidden_id_sweep": ("reads no site value", "E2", None, "bytes of command.txt, stdout.log, stderr.log, environment.json, pari-stack.json", "VA-7 (b)"),
    "r5_check_run.py::manifest_protocol_checks": ("reads no site value", "E2", None, "manifest protocol fields", ""),
    "r5_check_run.py::pari_stack_checks": ("reads no site value", "E2", None, "the pari-stack.json copy", ""),
    "r5_check_run.py::reg1_recorded_check": ("V-2 (CG-4)", "E2", None, "gate.regression_REG-1 recorded in the manifest", ""),
    "r5_check_run.py::status_agreement": ("alpha", "E2", None, "manifest status vs raw-result run_status", ""),
    "r5_check_run.py::r5_checks": ("reads no site value directly", "E2", None, "the findings of the listed single-class checks", "orchestrator (VA-8 (b) model)"),
    "r5_check_run.py::main": ("V-4", "E2", None, "the frozen checker's exit status; the r4 findings; prints the SC-4 table (E6)", ""),
    # r5_reg1.py (the comparator, unchanged from r2 except the SE-4 (e) structure)
    "r5_reg1.py::_strip": ("V-1 row K-1 (CG-4)", "E7", None, "target entries (removal of X1..X17 paths)", "REG-1 (b) machinery"),
    "r5_reg1.py::strip": ("V-1 row K-1 (CG-4)", "E7", None, "target entries", "REG-1 (b) machinery"),
    "r5_reg1.py::d_table": ("alpha", "E2", None, "recorded outcome / D per target and arm", "REG-1 (b) item, compared in compare"),
    "r5_reg1.py::fresh_k_xR": ("alpha", "E2", None, "recorded x_R; certificates' k", "REG-1 (b) item"),
    "r5_reg1.py::Reader.read": ("V-7", "E2", None, "reference file bytes vs the TASK-20260923-0fa03f post-run receipt", "VC-1 (e) names it"),
    "r5_reg1.py::Reader.ok": ("V-7", "E2", None, "the integrity record", ""),
    "r5_reg1.py::parsed_key": ("beta", "E2", None, "the recorded attempts' <tag>.ms.out / .ms.log / .ms.err / .ms", "REG-1 (d) d-parsed"),
    "r5_reg1.py::solver_events_check": ("epsilon", "E2", None, "exists / parses; flag; S-1 / S-2 events' consistency (VA-6 (b))", "SE-4 (e)"),
    "r5_reg1.py::compare": ("V-1 row K-1 (CG-4)", "E2", None, "(a) .ms, (b) raw-result target entries incl. instructions_callgrind, (c) certificates, (d) .ms.out", "REG-1 itself"),
    "r5_reg1.py::compare.b": ("V-1 row K-1 (CG-4)", "E2", None, "REG-1 (b) item equality", ""),
    "r5_reg1.py::render": ("V-2", "E6", None, "the REG-1 report (quotes solver-events.json in full)", "report only"),
    "r5_reg1.py::main": ("V-2", "E2", None, "the REG-1 verdict (exit status)", ""),
    # r5_accounting.py
    "r5_accounting.py::accounting": ("beta", "E6", None, "a recorded attempt's .ms.out (SC-3 / SC-4)", "never acted on in packages"),
    "r5_accounting.py::nvars_p": ("beta", "E6", None, ".ms header or .ms.log", ""),
    "r5_accounting.py::ms_header": ("beta", "E6", None, ".ms header", ""),
}
CLASSES.update({
    "r5_common.py::PariStack.start_readback": ("reads no site value", "E2", None, "PARI read-backs (the key 'pass' is its own record's)", "RC-2 (a)"),
    "r5_resolve.py::_ensure_doc": ("reads no site value", "E5", None, "", "creates the empty record"),
    "r5_make_plans.py::reg1_block": ("reads no site value", "E5", None, "plan text; REG-1 constants", "plan writer"),
    "r5_make_plans.py::repair_block": ("reads no site value", "E5", None, "constants", "plan writer"),
    "r5_make_plans.py::build": ("reads no site value", "E2", None, "the frozen plans (plan text; no site value)", "plan writer; VA-7 (a) plan-text check"),
    "r5_make_plans.py::main": ("reads no site value", "E2", None, "plan text", "plan writer"),
})
CLASSES.update({
    'r5_check_run.py::which_plan': ('reads no site value', 'E5', None, 'plan text', ''),
    'r5_common.py::PariStack._read': ('reads no site value', 'E5', None, 'PARI defaults', ''),
    'r5_common.py::PariStack.configure': ('reads no site value', 'E5', None, '', 'PS-1 P-A'),
    'r5_common.py::PariStack.exit_readback': ('reads no site value', 'E5', None, 'PARI defaults, /proc/self/status', 'RC-2 (b)'),
    'r5_common.py::check_redirections': ('reads no site value', 'E2', None, 'module attributes; r4 constants', 'RC-3 (d); VA-7 (a)'),
    'r5_common.py::forbidden_ids_in_text': ('reads no site value', 'E2', None, 'text it is given: plan text, constants, pari-stack.json only', 'VA-7 (a)'),
    'r5_common.py::forbidden_ids_in_values': ('reads no site value', 'E2', None, 'r4 constants and redirected values', 'VA-7 (a)'),
    'r5_common.py::hashseed_readback': ('reads no site value', 'E5', None, 'os.environ; sys.flags', 'SE-6'),
    'r5_common.py::load_json': ('reads no site value directly', 'E5', None, "any JSON file (primitive: the caller's class governs each call)", ''),
    'r5_common.py::now': ('reads no site value', 'E5', None, 'clock', ''),
    'r5_common.py::receipt_paths': ('reads no site value', 'E5', None, 'an archive receipt', ''),
    'r5_common.py::sha256_bytes': ('reads no site value directly', 'E5', None, "bytes (primitive: the caller's class governs each call)", ''),
    'r5_common.py::sha256_file': ('reads no site value directly', 'E5', None, "a file (primitive: the caller's class governs each call)", ''),
    'r5_common.py::write_pari_stack_json': ('reads no site value', 'E5', None, 'the pari-stack record (PARI read-backs, redirections, hash seed, entry status)', 'VA-7 (a) guard over a file with no site value'),
    'r5_entry_a1.py::r5_gate_ids': ('reads no site value', 'E5', None, 'plan text', ''),
    'r5_make_plans.py::_split': ('reads no site value', 'E5', None, '', 'plan writer'),
    'r5_make_plans.py::delete_path': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r5_make_plans.py::inputs': ('reads no site value', 'E2', None, 'plan text; minted ids', 'plan writer'),
    'r5_make_plans.py::map_strings': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r5_make_plans.py::ordered': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r5_make_plans.py::rc4c_equal': ('reads no site value', 'E2', None, 'plan text', 'RC-4 (c)'),
    'r5_make_plans.py::render': ('reads no site value', 'E5', None, 'plan text', 'plan writer'),
    'r5_reg1.py::Reader.path': ('reads no site value', 'E5', None, 'a path', ''),
    'r5_reg1.py::load_exclusions': ('reads no site value', 'E2', None, 'the exclusion list', 'SE-4 (e): X1..X17 exactly'),
    'r5_resolve.py::_identity': ('reads no site value', 'E5', None, 'function identities', ''),
    'r5_resolve.py::_iso': ('reads no site value', 'E5', None, 'a timestamp', ''),
    'r5_resolve.py::_now': ('reads no site value', 'E5', None, 'clock', 'indirection (development shims only)'),
    'r5_resolve.py::_sleep': ('reads no site value', 'E5', None, '', 'indirection'),
    'r5_resolve.py::_utc': ('reads no site value', 'E5', None, 'clock', ''),
    'r5_run_wrapper.py::disk_files': ('reads no site value', 'E5', None, 'file names of the implementation trees', ''),
    'r5_run_wrapper.py::g1_id': ('reads no site value', 'E5', None, 'plan text', ''),
    'r5_run_wrapper.py::git': ('reads no site value', 'E5', None, 'git output', ''),
    'r5_run_wrapper.py::git_tree_state': ('reads no site value', 'E2', None, 'git output', 'R-4..R-6'),
    'r5_run_wrapper.py::phase_a_commit': ('reads no site value', 'E5', None, 'an archive receipt; git log', 'PS-5'),
    'r5_run_wrapper.py::plans': ('reads no site value', 'E5', None, 'plan text', ''),
    'r5_run_wrapper.py::refuse_forbidden_ids': ('reads no site value', 'E2', None, 'plan text; r4 constants', 'R-13; VA-7 (a)'),
    'r5_run_wrapper.py::sh': ('reads no site value', 'E5', None, 'shell output (versions)', ''),
    'r5_run_wrapper.py::tree_check': ('reads no site value', 'E2', None, 'implementation-tree hashes vs archive receipts', 'R-4..R-6'),
})
E = "epsilon"
CLASSES.update({
    # r5_recorder.py -- the RL-1 launch recorder (gamma; RL-5, RK-5, RF-7, RG-8, RH-7)
    "r5_recorder.py::launch_recorder": (G, "E5", "RL-1 (a)-(d); RK-1; RF-1; RG-1", "the frozen run_child's returned record or raise; the call's arguments", "the recording pass-through; returns / re-raises unchanged"),
    "r5_recorder.py::_finish": (G, "E5", "RL-1 (c); RF-1 (b); RG-1 (b)", "the counter; the returned record / raise", "writes one launch record or the foreign file"),
    "r5_recorder.py::_record_return": (G, "E5", "RL-1 (c); RK-1 (a), (c); RG-1 (c)", "the returned record (key presence)", "recording"),
    "r5_recorder.py::_record_raise": (G, "E5", "RK-1 (b); RF-1 (a); RG-1 (c)", "the frozen rec on the traceback", "recording"),
    "r5_recorder.py::_inspect_raise": (G, "E5", "RK-1 (b); RF-1 (a)", "traceback frames of the captured frozen code objects (read-only)", "recording"),
    "r5_recorder.py::_chain": (G, "E5", "RF-1 (a)", "__context__ / __cause__ chain", "recording"),
    "r5_recorder.py::_base_record": (G, "E5", "RL-1 (c); RG-1 (b); RG-4 (a)", "the call's arguments; the observer", "recording"),
    "r5_recorder.py::_bind": (G, "E5", "RL-1 (a)", "the call's arguments against the frozen signature", "recording"),
    "r5_recorder.py::_foreign": (G, "E5", "RF-1 (b)", "pids; the raised type", "writes recorder-foreign-<pid>.json in a non-installing process"),
    "r5_recorder.py::_after_fork_in_parent": (G, "E5", "RG-1 (a); RH-4", "/proc/self/task/<tid>/children; perf_event_open", "the RG-1 callback and the RH-4 mark; records only"),
    "r5_recorder.py::_thread_children": (G, "E5", "RG-1 (a) (1)", "/proc/self/task/<tid>/children", ""),
    "r5_recorder.py::_perf_open_task_clock": (G, "E5", "RG-1 (a) (2)", "perf_event_open (software task clock)", "the counter open"),
    "r5_recorder.py::_read_counter": (G, "E5", "RG-1 (b)", "the counter's value, time enabled, time running", "the counter read"),
    "r5_recorder.py::child_end_value": (G, "E5", "RG-1 (c); RH-4", "the observer, marks, report and returncode", "writes child_end (epsilon)"),
    "r5_recorder.py::install": ("reads no site value", "E5", None, "function identities", "the RL-1 installation (the one load of the frozen run_child, LKA-7 (b))"),
    "r5_recorder.py::readback": ("reads no site value", "E2", None, "function identities; code objects; sys.modules", "RL-5 install read-back"),
    "r5_recorder.py::_identity": ("reads no site value", "E5", None, "function identities", ""),
    "r5_recorder.py::_iso": ("reads no site value", "E5", None, "a timestamp", ""),
    "r5_recorder.py::_utc": ("reads no site value", "E5", None, "clock", ""),
    # r5_resolve.py -- RB-1, RL-2 writers
    "r5_resolve.py::_rb1_s1": (G, "E5", "RB-1 (a)-(e) at S-1 (RJ-1 (a))", "the result the frozen solve RETURNED for the attempt", "recording"),
    "r5_resolve.py::_rb1_s2": (G, "E5", "RB-1 (a)-(d) at S-2", "the result the frozen run_system RETURNED for the attempt", "recording"),
    "r5_resolve.py::_rb1_pair": (G, "E5", "RB-1 (b)", "the returned result's read-back pair", "recording"),
    "r5_resolve.py::_rb1_callgrind_result_present": (G, "E5", "RB-1 (e) (launchkind RJ-1 (a); LKA-9)", "key membership of 'instructions_callgrind' in the returned result", "recording; reads no value inside it"),
    "r5_resolve.py::_passthrough_record": (G, "E5", "RL-2", "the gb_only result the frozen solve returned", "recording"),
    "r5_resolve.py::append_launch_record": (G, "E5", "RL-1 (c)", "the launch record", "the single event writer"),
    "r5_resolve.py::_recording_failure": (G, "E1", "RB-1; RL-1 (d); RL-2 (a recording failure is an SE-2 (4) violation)", "the failing write", "raises SolverEventConsistencyError"),
    "r5_resolve.py::solve.make": (G, "E5", "SE-2 (2)(a); RB-1", "via _attempt_record_s1", ""),
    # r5_gaps.py -- the RL-3 recorder-gap computation (epsilon; E2 through RF-3 (a))
    "r5_gaps.py::recorder_gaps": (E, "E2", None, "the package's files, launch records, RB-1 / RL-2 records, events, counters, raw-result 'comparator.child' presence", "RL-3 as launchkind reads it; FAIL through RF-3 (a)"),
    "r5_gaps.py::_evaluate": (E, "E2", None, "via the listed functions", "orchestrator of RL-3 (RH-1 with RI-1, RJ-1, RJ-2, RJ-3, RJ-4)"),
    "r5_gaps.py::attribute": (E, "E2", None, "launch records' stdout_path / stderr_path / argv; spec files; events' renamed_files", "RH-1 (i)-(vi) with RI-1 (d) (the RG-4 attribution)"),
    "r5_gaps.py::_spec_ok": (E, "E2", None, "child/<tag>.spec.json (written by the frozen driver before the launch)", "RH-1 (v)"),
    "r5_gaps.py::_renamed_ok": (E, "E2", None, "SE-3 / HR-3 events' renamed_files; launch order", "RH-1 (vi)"),
    "r5_gaps.py::ri1_counts": (E, "E2", None, "launch records; RB-1 attempt records; RL-2 pass-through records; events; site counters", "attcount RI-1 (a) (i)-(iii), (b), (c) (LKA-8)"),
    "r5_gaps.py::rj1_callgrind": (E, "E2", None, "callgrind launch records; RB-1 (e) callgrind_result_present", "launchkind RJ-1 (b), (c) (LKA-8; LKA-9: its only E1-E4 reader)"),
    "r5_gaps.py::rj3_comparator": (E, "E2", None, "comparator launch records; raw-result 'comparator' mapping with key 'child' (presence)", "launchkind RJ-3 (LKA-8)"),
    "r5_gaps.py::rj4_unknown": (E, "E2", None, "launch records' stdout_path forms", "launchkind RJ-4 (b) (LKA-8; LKA-10)"),
    "r5_gaps.py::form_of": (E, "E2", None, "a relativized stdout_path", "RJ-4 (a) forms"),
    "r5_gaps.py::relativize": (E, "E2", None, "a recorded stdout_path; the recorded run directory", "LKA-10 strict prefix"),
    "r5_gaps.py::run_dir_recorded": ("reads no site value", "E2", None, "command.txt line 2 (GFPN_RUN_DIR)", "LKA-10"),
    "r5_gaps.py::package_files": (E, "E2", None, "the package's file listing under the five directories", "RL-3"),
    "r5_gaps.py::load_doc": (E, "E5", None, "solver-events.json", "loader"),
    "r5_gaps.py::load_raw": ("alpha", "E5", None, "raw-result.json", "loader (RJ-3 reads one key's presence)"),
    "r5_gaps.py::_argv": (E, "E2", None, "a launch record's argv", ""),
    # r5_check_run.py -- the r4 verdict layer (V-4 / epsilon readers; E2)
    "r5_check_run.py::verdict": ("V-4", "E2", None, "the frozen checker's exit and items; the r4 findings; launch records; manifest raw_result_writer; foreign files; gaps",
                                 "RK-3 (b) with RF-2, RF-3; stop classes RF-3 (b); LABELS RG-2, RH-2 (no value class)"),
    "r5_check_run.py::frozen_items": ("V-4", "E2", None, "the frozen checker's failing item lines", "RF-2 (iv)"),
    "r5_check_run.py::launch_class_check": (E, "E2", None, "launch records", "RF-3 (a) with RG-1 (d)"),
    "r5_check_run.py::launch_record_class": (E, "E2", None, "one launch record", "classes (A), (B), (C)"),
    "r5_check_run.py::undetermined_check": (E, "E2", None, "launch records' child_created / child_end / frame_inspection; raw_result_writer", "RF-0 (c)"),
    "r5_check_run.py::writer_check": (E, "E2", None, "manifest raw_result_writer (epsilon, written by the wrapper, RF-7)", "RF-0 (b); RF-3 (a)"),
    "r5_check_run.py::foreign_check": (E, "E2", None, "recorder-foreign-<pid>.json presence", "RF-1 (b)"),
    "r5_check_run.py::foreign_files": (E, "E2", None, "recorder-foreign-<pid>.json names", "RF-1 (b)"),
    "r5_check_run.py::gaps_check": (E, "E2", None, "the RL-3 gap lists", "RF-3 (a)"),
    "r5_check_run.py::zl_child_files": (E, "E2", None, "the package's file listing", "RK-3 (b) (iii)"),
    "r5_check_run.py::x13_check": ("alpha", "E2", None, "the controls_a1 image's run_status / gate_pass; the admission values recorded in the manifest", "RF-5 X-13"),
    "r5_check_run.py::recorded_attempts": (E, "E6", None, "RB-1 attempt records (the recorded attempt of each call)", "RB-3 enumeration (E6)"),
    # r5_run_wrapper.py
    "r5_run_wrapper.py::checker_verdict": ("V-4", "E2", None, "the r4 checker's exit status and verdict (run in this process)", "RB-4 (b); RL-4; RK-3 (b) (RB-7: consumer of V-4, E2)"),
    "r5_run_wrapper.py::rl4_read_packages": ("V-4", "E2", None, "each read package's r4 verdict", "RL-4 with RF-3 (b)"),
    "r5_run_wrapper.py::f4_recorded": ("V-4", "E5", None, "the F-4 package's r4 verdict", "RK-3 (d): recorded only, gates nothing"),
    "r5_run_wrapper.py::read_packages": ("reads no site value", "E2", None, "plan text; manifest existence", "RL-4 read list (X-03, X-04, X-07..X-11)"),
    "r5_run_wrapper.py::read_packages.add": ("reads no site value", "E5", None, "", ""),
    "r5_run_wrapper.py::readback_sources": ("V-1 row K-2", "E5", None, "RB-2 (a)-(c) with RL-3 (d), (e): raw-result by key name, child/*.meta.json, attempt, launch and pass-through records", "the RB-2 / RL-3 collector (K-2 derivative); records only"),
    "r5_run_wrapper.py::threads_sources": ("V-1 row K-2", "E5", None, "threads_executed by key name and RB-1 (c)", "RB-2; records only"),
    "r5_run_wrapper.py::child_readback_accounting": ("V-1 row K-2", "E5", None, "via readback_sources, launch_class_accounting, r5_gaps.recorder_gaps", "resources.child_readback_accounting; records only"),
    "r5_run_wrapper.py::launch_class_accounting": (E, "E5", None, "launch records", "RK-2 with RF-1 (c); records only"),
    "r5_run_wrapper.py::raw_result_writer": (E, "E5", None, "the wrapper's own parse result", "RF-0 (b) (epsilon, written by the wrapper, RF-7)"),
    "r5_run_wrapper.py::listing": ("reads no site value directly", "E5", None, "every file's bytes (sha256 only)", "RL-3 / RGL-7 listing"),
    "r5_run_wrapper.py::_pair_key": ("reads no site value directly", "E5", None, "a pair (primitive)", ""),
    # r5_make_plans.py
    "r5_make_plans.py::admission_block": ("reads no site value", "E5", None, "constants", "plan writer"),
    "r5_make_plans.py::branch_evidence": ("reads no site value", "E2", None, "the DV-2 / DV-3 development outputs (PS-1 branch)", "plan writer"),
})
# REQUIRED LISTINGS (RB-7, RL-5, RG-8, RH-7 with RI-5 (b), LKA-8, LKA-9): name -> (function, class, effect or None)
REQUIRED = {
    "RB-7 / LKA-9: the RB-1 (e) writer": ("r5_resolve.py::_rb1_callgrind_result_present", "gamma", "E5"),
    "RB-7: the RB-1 writers (S-1, S-2)": ("r5_resolve.py::_rb1_s1", "gamma", "E5"),
    "RB-7: the RB-2 collector (K-2 derivative, E5)": ("r5_run_wrapper.py::readback_sources", "V-1 row K-2", "E5"),
    "RB-7: the RB-3 enumeration (E6)": ("r5_check_run.py::recorded_attempts", "epsilon", "E6"),
    "RB-7: RB-4 (b) consumer of V-4 (E2)": ("r5_run_wrapper.py::checker_verdict", "V-4", "E2"),
    "RL-5: the launch recorder": ("r5_recorder.py::launch_recorder", "gamma", "E5"),
    "RL-5: reader of launch records (RK-2 accounting)": ("r5_run_wrapper.py::launch_class_accounting", "epsilon", "E5"),
    "RL-5: reader of launch records (RF-3 (a))": ("r5_check_run.py::launch_class_check", "epsilon", "E2"),
    "RL-5: reader of pass-through records (RL-3 (e))": ("r5_run_wrapper.py::readback_sources", "V-1 row K-2", "E5"),
    "RG-8: the callback": ("r5_recorder.py::_after_fork_in_parent", "gamma", "E5"),
    "RG-8: the counter read": ("r5_recorder.py::_read_counter", "gamma", "E5"),
    "RG-8: child_end (writer)": ("r5_recorder.py::child_end_value", "gamma", "E5"),
    "RG-8 / RH-7: the RG-4 / RH-1 attribution": ("r5_gaps.py::attribute", "epsilon", "E2"),
    "RH-7: RH-1 (v)": ("r5_gaps.py::_spec_ok", "epsilon", "E2"),
    "RH-7: RH-1 (vi)": ("r5_gaps.py::_renamed_ok", "epsilon", "E2"),
    "RH-7 / RI-5 (b): the RH-4 mark (in the callback)": ("r5_recorder.py::_after_fork_in_parent", "gamma", "E5"),
    "RI-5 (b) / LKA-8: the RI-1 counts (a) (i), (ii)": ("r5_gaps.py::ri1_counts", "epsilon", "E2"),
    "LKA-8 / LKA-9: RJ-1 (b)": ("r5_gaps.py::rj1_callgrind", "epsilon", "E2"),
    "LKA-8: RJ-3": ("r5_gaps.py::rj3_comparator", "epsilon", "E2"),
    "LKA-8: RJ-4 (b)": ("r5_gaps.py::rj4_unknown", "epsilon", "E2"),
}
LABELS = {"RG-2 infrastructure-stop outcome": "r5_check_run.py::verdict (label only; read only by the RF-3 (b) stop record and the planned-basis scope; no value class)",
          "RH-2 cap-mismatch stop outcome": "r5_check_run.py::verdict (label only; read only by the RF-3 (b) stop record and the planned-basis scope; no value class)"}
RB1_TOKENS = ("rb1", "callgrind_result_present", "attempt_records", "passthrough_records")
RB1_E1E4_CONSUMERS = ("r5_gaps.py::ri1_counts", "r5_gaps.py::rj1_callgrind")
CG3_KEYS = ("callgrind_children_observed", "with_log_visible_ssf_indicator", "with_quotient_dimension_mismatch",
            "with_readback_differing_from_requested_cap", "log_visible_ssf_indicator", "printed_quotient_dimension_equals_recorded_attempt",
            "child_readback_equals_requested_cap", "reg1_compared_fields_verbatim", "fglm_squarefree_degree", "random_linear_form_string_in_log",
            "attempt_recorded_by_the_wrapper")


def _nodoc_nodes(fn):
    """own_nodes without the function's docstring expression."""
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    stack = list(body)
    while stack:
        n = stack.pop()
        yield n
        for ch in ast.iter_child_nodes(n):
            if not isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stack.append(ch)


def lka_checks(trees, rows):
    """LKA-8, LKA-9 and VA-6 (c) / CC-5 on the delivered files. Returns (report, stops)."""
    stops, rep = [], {"rb1_token_readers": [], "callgrind_result_present_names": [], "calls_of_rb1_writer": [], "cg3_or_s3_names": []}
    by_key = {r["function"]: r for r in rows}
    for f, tree in trees.items():
        if f in DEV_FILES:
            continue
        for q, fn in functions(tree):
            key = "%s::%s" % (f, q)
            consts = {n.value for n in _nodoc_nodes(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            attrs = {n.attr for n in _nodoc_nodes(fn) if isinstance(n, ast.Attribute)}
            calls = {(n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None)) for n in _nodoc_nodes(fn) if isinstance(n, ast.Call)}
            cls = (CLASSES.get(key) or MANUAL.get(key) or (None, None))
            c0, eff = cls[0], cls[1]
            if consts & set(RB1_TOKENS):
                rep["rb1_token_readers"].append({"function": key, "tokens": sorted(consts & set(RB1_TOKENS)), "class": c0, "effect": eff})
                if c0 != "gamma" and eff in ("E1", "E2", "E3", "E4") and key not in RB1_E1E4_CONSUMERS:
                    stops.append("LKA-8: %s reads an RB-1 value at %s and is not a consumer the incorporating texts name" % (key, eff))
            if "callgrind_result_present" in consts:
                rep["callgrind_result_present_names"].append(key)
                if key not in ("r5_resolve.py::_rb1_s1", "r5_gaps.py::rj1_callgrind"):
                    stops.append("LKA-9: %s names callgrind_result_present (only the writer _rb1_s1 and the reader rj1_callgrind may)" % key)
            if "_rb1_callgrind_result_present" in calls:
                rep["calls_of_rb1_writer"].append(key)
                if key != "r5_resolve.py::_rb1_s1":
                    stops.append("LKA-9: %s calls _rb1_callgrind_result_present" % key)
            hit = sorted((consts & set(CG3_KEYS)) | ({"SITE_S3"} & attrs))
            if hit:
                rep["cg3_or_s3_names"].append({"function": key, "names": hit, "effect": eff})
                if eff in ("E1", "E2", "E3", "E4"):
                    stops.append("VA-6 (c) / CC-5 / LKA-9: %s names %s at %s" % (key, hit, eff))
            if key == "r5_resolve.py::_rb1_callgrind_result_present":
                body = [st for st in fn.body if not (isinstance(st, ast.Expr) and isinstance(getattr(st, "value", None), ast.Constant))]
                ok = (len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Compare)
                      and isinstance(body[0].value.left, ast.Constant) and body[0].value.left.value == "instructions_callgrind"
                      and len(body[0].value.ops) == 1 and isinstance(body[0].value.ops[0], ast.In)
                      and isinstance(body[0].value.comparators[0], ast.Name) and body[0].value.comparators[0].id == "res")
                rep["rb1_e_writer_body_is_the_key_membership_test"] = ok
                rep["rb1_e_writer_source"] = ast.unparse(fn)
                if not ok:
                    stops.append("LKA-9: _rb1_callgrind_result_present is not exactly the key-membership test")
    if "rb1_e_writer_body_is_the_key_membership_test" not in rep:
        stops.append("LKA-9: r5_resolve._rb1_callgrind_result_present not found")
    req = {}
    for name, (fkey, cls, eff) in REQUIRED.items():
        r = by_key.get(fkey)
        ok = bool(r) and r["class"] == cls and (eff is None or r["effect"] == eff)
        req[name] = {"function": fkey, "listed": bool(r), "class": r and r["class"], "effect": r and r["effect"], "expected": [cls, eff], "ok": ok}
        if not ok:
            stops.append("required listing %s: %s not listed with class %s / effect %s" % (name, fkey, cls, eff))
    rep["required_listings"] = req
    rep["classification_labels_no_value_class"] = LABELS
    return rep, stops


# listed by reading, not by the detector (control dependence the detector cannot see)
MANUAL = {
    "r5_entry_v2.py::main": ("epsilon", "E5", None, "the SE-2 (4) / HR-5 consistency raise (as an exception class name)",
                             "records status command_raised_<class> into pari-stack.json and re-raises; chooses no result"),
    "r5_entry_a1.py::main": ("epsilon", "E5", None, "the SE-2 (4) / HR-5 consistency raise (as an exception class name)",
                             "records status command_raised_<class> into pari-stack.json and re-raises; chooses no result"),
}
APPROVED = {"alpha", "beta", "frozen-body", "gamma", "epsilon", "reads no site value", "reads no site value directly", "V-2", "V-4", "V-7",
            "V-1 row K-1 (CG-4)", "V-1 row K-2", "V-1 row K-5", "V-2 (CG-4)", "V-5"}
FORBIDDEN_IMPORT_PREFIXES = ("r1_", "r2_", "r3_")


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
    lka, lka_stops = lka_checks({f: ast.parse(texts[f]) for f in files}, rows)
    stops += lka_stops
    for k in CLASSES:
        if k not in funcs:
            stops.append("the declared table names a function that does not exist: %s" % k)
    # imports (CC-5; VC-3)
    v1_mods = sorted(os.path.splitext(x)[0] for x in os.listdir(os.path.join(R.EXP_DIR, "implementation")) if x.endswith(".py"))
    bad_imports = {f: [m for m in ms if m.startswith(FORBIDDEN_IMPORT_PREFIXES) or m in v1_mods] for f, ms in imports.items()}
    bad_imports = {f: m for f, m in bad_imports.items() if m}
    if bad_imports:
        stops.append("an r4 file imports an r1, r2, r3 or v1 module: %s" % bad_imports)
    never_classified = [f for f, s in texts.items() if "output never classified" in s and "CORR-20260924-432f43" not in s]
    if never_classified:
        stops.append("an r4 file describes S-3 as 'output never classified' without the CORR-20260924-432f43 distinction: %s" % never_classified)
    # epsilon used to choose a recorded result: only gamma chooses (the last attempt); every other epsilon reader is listed E1/E2/E5
    eps_choosers = [r["function"] for r in rows if r["class"] == "epsilon" and "choose" in (r.get("note") or "") and "chooses no result" not in (r.get("note") or "")]
    if eps_choosers:
        stops.append("an r4 consumer uses an epsilon value to choose a recorded result: %s" % eps_choosers)
    va6 = {"V-7 (VA-6 (a))": [r["function"] for r in rows if r["class"] == "V-7" and "solver-events" in str(r["reads"])],
           "epsilon (VA-6 (b))": [r["function"] for r in rows if r["class"] == "epsilon" and r["effect"] in ("E1", "E2", "E5")
                                  and not r["function"].startswith(DEV_FILES)],
           "CG-3 fields no r4 function reads at E1-E4": CG3_FIELDS,
           "readers of CG-3 fields (all at E5 / E6)": [r["function"] for r in rows if r["function"] in ("r5_resolve.py::_record_callgrind",
                                                                                                        "r5_run_wrapper.py::solver_events_block",
                                                                                                        "r5_reg1.py::render") or (r["class"] == "V-5")]}
    va7 = {"constant-key checks (VA-7 (b))": {"function": "r5_check_run.py::forbidden_id_keys", "files": ["manifest.yaml", "raw-result.json", "pari-stack.json",
                                                                                                         "solver-events.json", "the plan"],
                                               "keys": ["task_id", "run_card", "written_by_task", "archived_by"]},
           "byte sweep (VA-7 (b))": {"function": "r5_check_run.py::forbidden_id_sweep",
                                     "files": ["command.txt", "stdout.log", "stderr.log", "environment.json", "pari-stack.json"],
                                     "carries_no_site_record_field": True,
                                     "disclosed": ("stdout.log may hold the frozen drivers' check-name lines 'name PASS|FAIL' (a bit derived from results the "
                                                   "wrappers returned: alpha), and pari-stack.json's status and stderr.log's traceback may name the "
                                                   "SolverEventConsistencyError class when a consistency raise occurred (epsilon). None of these is a field of an "
                                                   "S-1, S-2 or S-3 record (census M-3), each is covered for an integrity reader by its own disposition, and "
                                                   "the sweep's output cannot depend on them (a task-id string can never equal them)")},
           "plan text and r4 constants (VA-7 (a))": ["r5_run_wrapper.py::refuse_forbidden_ids", "r5_common.py::check_redirections",
                                                     "r5_common.py::forbidden_ids_in_text", "r5_common.py::forbidden_ids_in_values",
                                                     "r5_make_plans.py::build"],
           "pari-stack.json writer guard (a file with no site value)": "r5_common.py::write_pari_stack_json",
           "event-record writer (VA-7 (c))": "r5_resolve.py::_write carries NO substring guard"}
    rep = {"method": __doc__, "files": files, "n_functions": len(funcs), "n_listed": len(rows), "rows": rows, "imports": imports,
           "VA-6 (d)": va6, "VA-7 (b)": va7, "declared_table_size": len(CLASSES), "manual_listings": sorted(MANUAL),
           "LKA-8_LKA-9_and_required_listings": lka}
    rep["census_comparison"] = census_comparison(rows)
    counts = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    gam = [{"function": r["function"], "clause": r["clause"]} for r in rows if r["class"] == "gamma"]
    rep["summary"] = {"n_functions": len(funcs), "n_listed": len(rows), "counts_by_class": counts, "gamma": gam,
                      "unclassified": unclassified, "bad_imports": bad_imports, "stops": stops,
                      "required_listings_ok": all(v["ok"] for v in lka["required_listings"].values()),
                      "rb1_e_writer_body_is_the_key_membership_test": lka.get("rb1_e_writer_body_is_the_key_membership_test"),
                      "callgrind_result_present_names": lka["callgrind_result_present_names"],
                      "rb1_token_readers": lka["rb1_token_readers"], "labels": LABELS}
    with open(os.path.join(out_dir, "inventory.json"), "w") as fh:
        json.dump(rep, fh, indent=1, default=str)
    return rep


def census_comparison(rows):
    """For every r4 file whose r3 origin started from an r2 file: the archived census's rows for the r2 file, by
    function (site, effect, class counts), next to the r4 function's listing."""
    started = {"r5_common.py": "r2_common.py", "r5_resolve.py": "r2_resolve.py", "r5_entry_v2.py": "r2_entry_v2.py", "r5_entry_a1.py": "r2_entry_a1.py",
               "r5_run_wrapper.py": "r2_run_wrapper.py", "r5_check_run.py": "r2_check_run.py", "r5_reg1.py": "r2_reg1.py",
               "r5_accounting.py": "r2_accounting.py", "r5_make_plans.py": "r2_make_plans.py", "r5_devchecks.py": "r2_devchecks.py",
               "r5_devchecks_more.py": "r2_devchecks_more.py", "r5_dv6.py": "r2_dv6.py", "r5_dv12.py": "r2_dv12.py"}
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
    rename = {"r2_checks": "r4_checks", "_attempt_record": "_attempt_record_s1"}
    by_fn = {r["function"]: r for r in rows}
    out = []
    for r3f, r2f in sorted(started.items()):
        for (f, fn), d in sorted(agg.items()):
            if f != r2f:
                continue
            target = "%s::%s" % (r3f, rename.get(fn, fn))
            r3row = by_fn.get(target)
            out.append({"r2": "%s::%s" % (f, fn), "census_rows_by_site_effect_class": d, "r4_function": target,
                        "r4_listing": r3row and {k: r3row.get(k) for k in ("class", "effect", "clause")},
                        "note": None if r3row else "no r4 function of this name is listed (renamed, split or reading no site value; see the note)"})
    return out


if __name__ == "__main__":
    rep = inventory(sys.argv[1])
    print(json.dumps(rep["summary"], indent=1, default=str))
