"""Frozen 21-literal/4-stored-comparison driver for DEC-20260909-2ebfcc.

Imports only the test module and calls its pure comparator. It never invokes
main, run_suite, admitted, a lock, an adapter or any worker. Historical JSON and
gzip payloads are data only; these results cannot alter the broad QA ledger.
"""
from __future__ import annotations

import argparse
import ast
import base64
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

DECISION_PATH = "ledger/decisions/DEC-20260909-2ebfcc.yaml"
DECISION_SHA256 = "4b217dbab6a9c16c0a7dfd61bd2f1e524200db2e63e48686d99a0ccbea05ea01"
SUBJECT_PATH = "tests/test_finite_yaml_locked_v3.py"
EXPECTED_SUBJECT_SHA256 = "6d139bd65121653fc10ecdc1c0d0f1c996414711a9924fd5c22ee297ef81cb30"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + repr(key))
            result[key] = value
        return result
    def constant(value):
        raise ValueError("nonfinite JSON constant: " + value)
    def floating(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("nonfinite JSON number")
        return number
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=floating)


def retained(path, blobs):
    raw = path.read_bytes()
    key = digest(raw)
    st = path.stat()
    blobs.setdefault(key, {"sha256": key, "bytes": len(raw), "base64": base64.b64encode(raw).decode()})
    return raw, {"path": str(path), "sha256": key, "bytes": len(raw),
                 "device": st.st_dev, "inode": st.st_ino, "nlink": st.st_nlink,
                 "mtime_ns": st.st_mtime_ns}


def read_bound(root, reference, blobs):
    raw, binding = retained(root / reference["path"], blobs)
    if binding["sha256"] != reference["sha256"]:
        raise ValueError("input SHA256 mismatch: " + reference["path"])
    return raw, binding


def decode_bound_gzip(root, reference, blobs):
    stored, binding = retained(root / reference["path"], blobs)
    if digest(stored) != reference["stored_sha256"] or len(stored) != reference["stored_bytes"]:
        raise ValueError("stored gzip SHA256/length mismatch: " + reference["path"])
    expanded = gzip.decompress(stored)
    if digest(expanded) != reference["uncompressed_sha256"] or len(expanded) != reference["uncompressed_bytes"]:
        raise ValueError("expanded gzip SHA256/length mismatch: " + reference["path"])
    key = digest(expanded)
    blobs.setdefault(key, {"sha256": key, "bytes": len(expanded), "base64": base64.b64encode(expanded).decode()})
    return expanded, {"stored": binding, "expanded_sha256": key, "expanded_bytes": len(expanded)}


def literal_expected_checks(case_id):
    """Independent expected false joints from the frozen literal table."""
    failed = set()
    if case_id.endswith("-target-matches-wrong-status"):
        failed.add("status_ok")
    elif case_id.endswith(("-wrong-validity", "-validity-null", "-validity-zero", "-validity-one", "-validity-missing")):
        failed.add("validity_ok")
    elif case_id.endswith("-both-wrong"):
        failed.update(("status_ok", "validity_ok"))
    elif case_id.endswith("-prior-failure"):
        failed.add("prior_ok")
    elif case_id.endswith(("-missing-target", "-wrong-fixed-target")):
        failed.add("predicate_ok")
    elif not case_id.endswith(("-correct-control", "positive-correct")):
        raise ValueError("unrecognized frozen literal: " + case_id)
    return {name: name not in failed for name in ("prior_ok", "status_ok", "validity_ok", "predicate_ok")}


def projection_checks(root, protocol, blobs):
    correction = protocol["expectation_correction"]
    old_index_raw, old_index_binding = read_bound(root, correction["historical_index"], blobs)
    old_authority_raw, old_authority_binding = read_bound(root, correction["historical_authority"], blobs)
    old_index, old_authority = strict_json(old_index_raw), strict_json(old_authority_raw)
    index_raw, index_binding = retained(root / correction["index_artifact"]["path"], blobs)
    authority_raw, authority_binding = retained(root / correction["authority_artifact"]["path"], blobs)
    index_envelope, authority_envelope = strict_json(index_raw), strict_json(authority_raw)
    for envelope in (index_envelope, authority_envelope):
        assert envelope["execution_authorized"] is False
        assert all(envelope[key] is None for key in ("current_claim", "current_runtime", "current_source_snapshot"))
    assert index_envelope["schema"] == "crypto.autoresearch.historical_index_projection.v1"
    assert authority_envelope["schema"] == "crypto.autoresearch.historical_authority_projection.v1"
    assert index_envelope["historical_source"] == correction["historical_index"]
    assert authority_envelope["historical_source"] == correction["historical_authority"]
    expected_index = copy.deepcopy(old_index)
    for row in correction["rows"]:
        assert expected_index[row["case_id"]]["expected_status"] == row["old_value"]
        expected_index[row["case_id"]]["expected_status"] = row["corrected_value"]
    assert index_envelope["index"] == expected_index
    expected_authority = copy.deepcopy(old_authority)
    assert expected_authority["admitted_index_sha256"] == correction["historical_index"]["sha256"]
    expected_authority["admitted_index_sha256"] = digest(index_raw)
    assert authority_envelope["authority_projection"] == expected_authority
    assert authority_envelope["corrected_index"] == {"path": correction["index_artifact"]["path"], "sha256": digest(index_raw)}
    assert authority_envelope["corrections"] == correction["rows"]
    assert authority_envelope["requires_fresh_admission"] is True
    return old_index, expected_index, {"passed": True,
        "index_changed_json_pointers": [row["json_pointer"] for row in correction["rows"]],
        "authority_changed_json_pointers": ["/admitted_index_sha256"],
        "non_executable_envelopes": True,
        "bindings": [old_index_binding, old_authority_binding, index_binding, authority_binding]}


def inspect_integration(subject_raw, old_raw):
    old_tree, new_tree = ast.parse(old_raw), ast.parse(subject_raw)
    def definitions(tree):
        return {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    old, new = definitions(old_tree), definitions(new_tree)
    assert set(new) - set(old) == {"evaluate_manifest_expectations"}
    changed = [name for name in old if ast.dump(old[name]) != ast.dump(new[name])]
    assert changed == ["admitted"]
    calls = [node for node in ast.walk(new["admitted"]) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "evaluate_manifest_expectations"]
    assert len(calls) == 1
    keyword_names = {item.arg for item in calls[0].keywords}
    assert keyword_names == {"prior_pass", "expected_status", "actual_status", "actual_valid",
                             "expected_predicate", "fixed_predicate", "postflight_failures"}
    body = ast.get_source_segment(subject_raw.decode(), new["admitted"])
    assert 'result["outcome"] == "pass" and comparison["passed"] is True' in body
    assert 'prior_outcome_ok and exception_matches' in body
    assert 'result.setdefault("failure_reasons", []).extend(comparison["reasons"])' in body
    return {"passed": True, "changed_existing_functions": changed,
            "new_functions": ["evaluate_manifest_expectations"],
            "same_helper_used_by_admitted": True,
            "inspection_scope": "AST/source inspection only; admitted and all worker/routing paths were not invoked"}


def run(root):
    started = time.monotonic()
    blobs, literal_rows, replay_rows, errors = {}, [], [], []
    decision_raw, decision_binding = read_bound(root, {"path": DECISION_PATH, "sha256": DECISION_SHA256}, blobs)
    protocol = strict_json(decision_raw)["coordinator_decision"]["corrective_protocol"]
    assert protocol["regression"]["literal_case_count"] == 21
    assert protocol["regression"]["replay_comparisons"] == 4
    subject_raw, subject_binding = read_bound(root, {"path": SUBJECT_PATH, "sha256": EXPECTED_SUBJECT_SHA256}, blobs)
    old_raw, old_binding = decode_bound_gzip(root, protocol["source_write_authority"]["old_source_preservation"]["payload"], blobs)
    integration = inspect_integration(subject_raw, old_raw)
    old_index, corrected_index, projections = projection_checks(root, protocol, blobs)
    spec = importlib.util.spec_from_file_location("finite_yaml_v3_pure_comparator_subject", root / SUBJECT_PATH)
    subject = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = subject
    spec.loader.exec_module(subject)
    helper = subject.evaluate_manifest_expectations
    for case in protocol["regression"]["literal_cases"]:
        expected_checks = literal_expected_checks(case["case_id"])
        try:
            actual = helper(**case["input"])
            failed_checks = [name for name, ok in expected_checks.items() if not ok]
            passed = (actual["passed"] is case["expected_pass"] and actual["acceptance_covered"] is case["expected_pass"]
                      and actual["checks"] == expected_checks
                      and [reason["check"] for reason in actual["reasons"]] == failed_checks)
            row = {"case_id": case["case_id"], "input": case["input"], "expected_pass": case["expected_pass"],
                   "expected_checks": expected_checks, "actual": actual, "comparison_passed": passed,
                   "attempt": 1, "scope": "pure literal comparison"}
        except Exception as exc:
            row = {"case_id": case["case_id"], "input": case["input"], "expected_pass": case["expected_pass"],
                   "comparison_passed": False, "error": {"type": type(exc).__name__, "message": str(exc)}, "attempt": 1}
        literal_rows.append(row)
    for case in protocol["regression"]["replay_inputs"]:
        try:
            manifest_raw, manifest_binding = decode_bound_gzip(root, case["manifest_payload"], blobs)
            raw_bytes, raw_binding = decode_bound_gzip(root, case["raw_payload"], blobs)
            manifest, raw = strict_json(manifest_raw)["run"], strict_json(raw_bytes)
            assert manifest["status"] == case["observed_status"]
            assert manifest["result"]["valid"] is case["observed_valid"]
        except Exception as exc:
            errors.append({"case_id": case["case_id"], "stage": "replay_input_custody", "type": type(exc).__name__, "message": str(exc)})
            for expectation in ("old", "corrected"):
                replay_rows.append({"case_id": case["case_id"], "expectation": expectation, "attempt": 0,
                                    "status": "deferred_input_custody_failure", "comparison_passed": False})
            continue
        for expectation, index, expected_pass in (("old", old_index, False), ("corrected", corrected_index, True)):
            arguments = {"prior_pass": case["prior_pass"], "expected_status": index[case["case_id"]]["expected_status"],
                         "actual_status": manifest["status"], "actual_valid": manifest["result"]["valid"],
                         "expected_predicate": index[case["case_id"]]["expected_predicate"],
                         "fixed_predicate": case["expected_predicate"], "postflight_failures": raw["postflight_failures"]}
            expected_checks = {"prior_ok": True, "status_ok": expected_pass, "validity_ok": True, "predicate_ok": True}
            try:
                actual = helper(**arguments)
                passed = actual["passed"] is expected_pass and actual["acceptance_covered"] is expected_pass and actual["checks"] == expected_checks
                row = {"case_id": case["case_id"], "expectation": expectation, "input": arguments,
                       "expected_pass": expected_pass, "expected_checks": expected_checks,
                       "actual": actual, "comparison_passed": passed, "attempt": 1,
                       "manifest_payload": manifest_binding, "raw_payload": raw_binding,
                       "prior_pass_basis": case["prior_pass_basis"],
                       "scope": "retained immutable observation comparison; zero workers and no current admission"}
            except Exception as exc:
                row = {"case_id": case["case_id"], "expectation": expectation, "input": arguments,
                       "comparison_passed": False, "error": {"type": type(exc).__name__, "message": str(exc)}, "attempt": 1}
            replay_rows.append(row)
    # Read back source/decision and old expectation bytes after all comparisons.
    assert digest((root / SUBJECT_PATH).read_bytes()) == EXPECTED_SUBJECT_SHA256
    assert digest((root / DECISION_PATH).read_bytes()) == DECISION_SHA256
    for ref in (protocol["expectation_correction"]["historical_index"], protocol["expectation_correction"]["historical_authority"]):
        assert digest((root / ref["path"]).read_bytes()) == ref["sha256"]
    all_rows = literal_rows + replay_rows
    return {"schema": "crypto.autoresearch.finite_yaml_comparator_unit_replay.v1",
            "recorded_at": datetime.now(timezone.utc).isoformat(), "argv": sys.argv, "cwd": str(Path.cwd()),
            "subject": subject_binding, "old_subject": old_binding, "decision": decision_binding,
            "literal_comparisons": literal_rows, "replay_comparisons": replay_rows,
            "integration_inspection": integration, "projection_inspection": projections,
            "input_custody_errors": errors, "content_addressed_blobs": blobs,
            "summary": {"literal_count": len(literal_rows), "replay_count": len(replay_rows),
                        "passed": sum(row["comparison_passed"] for row in all_rows),
                        "failed": sum(not row["comparison_passed"] for row in all_rows)},
            "wall_seconds": time.monotonic() - started,
            "scientific_runs": 0, "worker_runs": 0, "live_admissions": 0,
            "limitations": ["Unit/replay only; historical fixed-test pass strings are not new successes.",
                            "No current claim/runtime/fixture authority is created or checked for admission.",
                            "The broad 174-case QA accounting stays 36 full / 9 partial / 129 unadmitted."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.repository_root.absolute())
    except Exception as exc:
        result = {"schema": "crypto.autoresearch.finite_yaml_comparator_unit_replay.v1",
                  "recorded_at": datetime.now(timezone.utc).isoformat(), "argv": sys.argv,
                  "summary": {"literal_count": 0, "replay_count": 0, "passed": 0, "failed": 1},
                  "infrastructure_error": {"type": type(exc).__name__, "message": str(exc)},
                  "scientific_runs": 0, "worker_runs": 0, "live_admissions": 0}
    fd = os.open(args.evidence, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps(result["summary"], sort_keys=True))
    return 1 if result["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
