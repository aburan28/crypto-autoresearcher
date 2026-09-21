"""Bounded static conformance harness for ECTD v7 (maximum 256 cases).

This file defines, but does not authorize or execute, the downstream Executor's
conformance pass.  It refuses source drift, imports outside the source manifest,
duplicate fixture identifiers, unregistered error codes, fixture gaps, and
cache/bytecode writes.  It contains no scheduled curve construction, arithmetic
search, target access, production meter run, or scientific interpretation.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

MAX_CASES = 256
PACKAGE = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE.parents[3]
SCOPED_PATHS = (
    "experiments/EXP-ECTD-9e4248/amendments/v7.yaml",
    "experiments/EXP-ECTD-9e4248/amendments/v7/terminal-registry.json",
    "experiments/EXP-ECTD-9e4248/amendments/v7/schemas.json",
    "experiments/EXP-ECTD-9e4248/amendments/v7/record-semantics.py",
    "experiments/EXP-ECTD-9e4248/amendments/v7/certificate-replay.py",
    "experiments/EXP-ECTD-9e4248/amendments/v7/control-adapter.py",
    "experiments/EXP-ECTD-9e4248/amendments/v7/meter-path.py",
    "experiments/EXP-ECTD-9e4248/amendments/v7/decision-adapter.py",
    "experiments/EXP-ECTD-9e4248/amendments/v7/conformance.py",
    "experiments/EXP-ECTD-9e4248/amendments/v7/arithmetic-input-manifest.json",
    "experiments/EXP-ECTD-9e4248/amendments/v7/jcs-fixtures.json",
    "experiments/EXP-ECTD-9e4248/amendments/v7/mutation-fixtures.json",
    "experiments/EXP-ECTD-9e4248/amendments/v7/known-answer-fixtures.json",
    "experiments/EXP-ECTD-9e4248/amendments/v7/source-manifest.json",
)
PYTHON_FILES = (
    "record-semantics.py",
    "certificate-replay.py",
    "control-adapter.py",
    "meter-path.py",
    "decision-adapter.py",
    "conformance.py",
)
JSON_FILES = (
    "terminal-registry.json",
    "schemas.json",
    "arithmetic-input-manifest.json",
    "jcs-fixtures.json",
    "mutation-fixtures.json",
    "known-answer-fixtures.json",
    "source-manifest.json",
)
STDLIB_ALLOWLIST = {
    "__future__", "ast", "collections", "copy", "dataclasses", "fractions",
    "hashlib", "importlib", "json", "math", "os", "pathlib", "sys", "types",
    "typing", "unicodedata",
}


class ConformanceError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ConformanceError("DUPLICATE_JSON_KEY", key)
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise ConformanceError("NONFINITE_JSON_NUMBER", value)


def _json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except ConformanceError:
        raise
    except Exception as exc:
        raise ConformanceError("MALFORMED_JSON", f"{path}: {exc}") from exc


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object_sha(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return _sha(data)


def _load_local(filename: str, name: str) -> Any:
    location = PACKAGE / filename
    spec = importlib.util.spec_from_file_location(name, location)
    if spec is None or spec.loader is None:
        raise ConformanceError("SOURCE_GAP", filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    finally:
        sys.dont_write_bytecode = old
    return module


def _exception_code(exc: BaseException) -> str:
    code = getattr(exc, "code", None)
    if not isinstance(code, str):
        raise ConformanceError("UNREGISTERED_EXCEPTION", type(exc).__name__) from exc
    return code


def _pointer_tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ConformanceError("FIXTURE_POINTER", pointer)
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def mutate(value: Any, fixture: Mapping[str, Any]) -> Any:
    result = copy.deepcopy(value)
    tokens = _pointer_tokens(fixture["pointer"])
    if not tokens:
        if fixture["op"] == "replace":
            return copy.deepcopy(fixture["value"])
        raise ConformanceError("FIXTURE_POINTER", "root remove/add forbidden")
    parent = result
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    final = tokens[-1]
    operation = fixture["op"]
    if isinstance(parent, list):
        index = int(final)
        if operation == "remove":
            parent.pop(index)
        elif operation == "replace":
            parent[index] = copy.deepcopy(fixture["value"])
        elif operation == "add":
            parent.insert(index, copy.deepcopy(fixture["value"]))
        else:
            raise ConformanceError("FIXTURE_OPERATION", operation)
    else:
        if operation == "remove":
            del parent[final]
        elif operation in {"replace", "add"}:
            parent[final] = copy.deepcopy(fixture["value"])
        else:
            raise ConformanceError("FIXTURE_OPERATION", operation)
    return result


def _reseal_control_triplet(value: Mapping[str, Any], fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Refresh custody locators only, so mutations reach semantic predicates."""
    result = dict(value)
    plan = result["draw_plan"]
    plan_body = {key: plan[key] for key in ("schema", "algorithm", "curve_id", "meter_subseed", "counts", "targets")}
    plan["draw_plan_id"] = _object_sha(plan_body)
    root = result["root"]
    root["draw_plan_id"] = plan["draw_plan_id"]
    bundles = result["target_bundles"]
    for bundle in bundles.values():
        bundle_body = {key: bundle[key] for key in ("schema", "curve_id", "meter_subseed", "counts", "factor_base", "targets")}
        bundle["target_bundle_id"] = _object_sha(bundle_body)
    if not fixture["pointer"].startswith("/arms/"):
        for arm in result["arms"]:
            bundle_name = "planted" if arm["effective"] else "unplanted"
            arm["target_bundle_id"] = bundles[bundle_name]["target_bundle_id"]
    root_body = {key: root[key] for key in ("curve", "meter_subseed", "config", "draw_plan_id")}
    root["root_id"] = _object_sha(root_body)
    triplet_body = {key: result[key] for key in ("schema", "root", "draw_plan", "target_bundles", "arms")}
    result["triplet_id"] = _object_sha(triplet_body)
    return result


def _cache_snapshot() -> set[str]:
    paths: set[str] = set()
    for directory, dirnames, filenames in os.walk(REPOSITORY_ROOT):
        relative = Path(directory).relative_to(REPOSITORY_ROOT)
        if ".git" in relative.parts:
            dirnames[:] = []
            continue
        for dirname in dirnames:
            if dirname in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
                paths.add(str(relative / dirname))
        for filename in filenames:
            if filename.endswith((".pyc", ".pyo")):
                paths.add(str(relative / filename))
    return paths


def static_admission() -> dict[str, Any]:
    manifest = _json(PACKAGE / "source-manifest.json")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ConformanceError("SOURCE_GAP", "manifest entries")
    by_path: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        path_value = entry.get("path")
        if path_value in by_path:
            raise ConformanceError("DUPLICATE_SOURCE_PATH", str(path_value))
        by_path[path_value] = entry
    expected_scoped = set(SCOPED_PATHS)
    if set(manifest.get("scoped_artifacts", [])) != expected_scoped:
        raise ConformanceError("SOURCE_GAP", "exact 14 scoped artifacts")
    missing = expected_scoped - set(by_path)
    if missing:
        raise ConformanceError("SOURCE_GAP", str(sorted(missing)))
    for source_path, entry in by_path.items():
        source = REPOSITORY_ROOT / source_path
        if not source.is_file():
            raise ConformanceError("SOURCE_GAP", source_path)
        if source_path == "experiments/EXP-ECTD-9e4248/amendments/v7/source-manifest.json":
            if entry.get("sha256") is not None or entry.get("self_reference_policy") != "excluded-recursive-self-hash":
                raise ConformanceError("CUSTODY_FAILURE", "manifest self-reference policy")
            continue
        data = source.read_bytes()
        if entry.get("size_bytes") != len(data) or entry.get("sha256") != _sha(data):
            raise ConformanceError("CUSTODY_FAILURE", source_path)
    for filename in JSON_FILES:
        _json(PACKAGE / filename)
    registry_document = _json(PACKAGE / "terminal-registry.json")
    schema_bundle = _json(PACKAGE / "schemas.json")
    terminal_variants = schema_bundle.get("$defs", {}).get("terminal", {}).get("oneOf")
    if not isinstance(terminal_variants, list):
        raise ConformanceError("SOURCE_GAP", "terminal schema oneOf")
    schema_terminals: set[tuple[str, str, str, tuple[str, ...]]] = set()
    for variant in terminal_variants:
        properties = variant.get("properties", {})
        details = properties.get("details", {})
        detail_properties = details.get("properties", {})
        detail_keys = tuple(details.get("required", []))
        if (
            variant.get("additionalProperties") is not False
            or details.get("additionalProperties") is not False
            or set(detail_properties) != set(detail_keys)
            or any(not isinstance(detail_properties[key].get("$ref"), str) for key in detail_keys)
        ):
            raise ConformanceError("SOURCE_GAP", "terminal detail type/closure")
        schema_terminals.add((
            properties.get("code", {}).get("const"),
            properties.get("stage", {}).get("const"),
            properties.get("class", {}).get("const"),
            tuple(detail_keys),
        ))
    registry_terminals = {
        (item["code"], item["stage"], item["class"], tuple(item["detail_keys"]))
        for item in registry_document.get("terminals", [])
    }
    if schema_terminals != registry_terminals or len(schema_terminals) != len(terminal_variants):
        raise ConformanceError("SOURCE_GAP", "schema/registry terminal extensional mismatch")
    row_variants = schema_bundle.get("$defs", {}).get("frozen_row", {}).get("oneOf")
    schema_rows = [
        {key: rule["const"] for key, rule in variant["properties"].items()}
        for variant in row_variants or []
    ]
    if schema_rows != registry_document.get("frozen_rows"):
        raise ConformanceError("SOURCE_GAP", "closed row oneOf mismatch")
    validator_entries = registry_document.get("validator_errors")
    validator_variants = schema_bundle.get("$defs", {}).get("validator_error", {}).get("oneOf")
    if not isinstance(validator_entries, list) or not isinstance(validator_variants, list):
        raise ConformanceError("SOURCE_GAP", "validator error registry/schema")
    registered_validator_errors = {
        (item["code"], item["stage"], item["class"], tuple(item["detail_keys"]))
        for item in validator_entries
    }
    schema_validator_errors = {
        (
            item["properties"]["code"]["const"],
            item["properties"]["stage"]["const"],
            item["properties"]["class"]["const"],
            tuple(item["properties"]["details"]["required"]),
        )
        for item in validator_variants
    }
    if registered_validator_errors != schema_validator_errors:
        raise ConformanceError("SOURCE_GAP", "validator schema/registry extensional mismatch")
    source_exception_codes: set[str] = set()
    for filename in PYTHON_FILES:
        source = (PACKAGE / filename).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=filename)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                roots = {str(node.module).split(".")[0]}
            else:
                continue
            if not roots.issubset(STDLIB_ALLOWLIST):
                raise ConformanceError("SOURCE_GAP", f"unmanifested import in {filename}: {sorted(roots-STDLIB_ALLOWLIST)}")
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else None
            candidate = None
            if name in {"RecordError", "CertificateError", "ControlError", "MeterError", "DecisionError", "ConformanceError"} and node.args:
                candidate = node.args[0]
            elif name == "_exact_keys" and len(node.args) >= 3:
                candidate = node.args[-1]
            if isinstance(candidate, ast.Constant) and isinstance(candidate.value, str) and candidate.value.isupper():
                source_exception_codes.add(candidate.value)
    terminal_codes = {item["code"] for item in registry_document["terminals"]}
    validator_codes = {item["code"] for item in validator_entries}
    if source_exception_codes - terminal_codes != validator_codes:
        raise ConformanceError("SOURCE_GAP", "executable/registry exception-code mismatch")
    return {
        "entries": len(entries),
        "scoped_artifacts": len(expected_scoped),
        "registered_terminals": len(schema_terminals),
        "registered_validator_errors": len(validator_codes),
        "frozen_rows": len(schema_rows),
    }


def _terminal_base() -> dict[str, Any]:
    return {
        "schema": "crypto.autoresearch.ectd_v7_terminal.v1",
        "code": "P_COMPOSITE",
        "stage": "PRIMALITY",
        "class": "arithmetic_rejection",
        "details": {"p": "8518015827983"},
    }


def _construction_base(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "crypto.autoresearch.ectd_v7_construction_record.v1",
        "record_id": "static-fixture",
        "row": copy.deepcopy(row),
        "terminal": _terminal_base(),
        "certificate": {},
        "control_triplet": None,
    }


def run(max_cases: int = MAX_CASES) -> dict[str, Any]:
    if isinstance(max_cases, bool) or not isinstance(max_cases, int) or not 1 <= max_cases <= MAX_CASES:
        raise ConformanceError("RESOURCE_LIMIT", "case cap must be 1..256")
    before_cache = _cache_snapshot()
    admission = static_admission()
    record = _load_local("record-semantics.py", "_ectd_v7_record_semantics")
    certificate = _load_local("certificate-replay.py", "_ectd_v7_certificate_replay")
    control = _load_local("control-adapter.py", "_ectd_v7_control_adapter")
    meter = _load_local("meter-path.py", "_ectd_v7_meter_path")
    decision = _load_local("decision-adapter.py", "_ectd_v7_decision_adapter")
    registry = record.load_registry(PACKAGE)
    registry_codes = {
        entry["code"]
        for collection in (registry["terminals"], registry["validator_errors"])
        for entry in collection
    }
    jcs = _json(PACKAGE / "jcs-fixtures.json")
    mutations = _json(PACKAGE / "mutation-fixtures.json")
    kats = _json(PACKAGE / "known-answer-fixtures.json")
    all_ids: list[str] = []
    for collection in (jcs["positive"], jcs["negative"], mutations["positive_cases"], mutations["mutations"], kats["positive"], kats["negative_mutations"]):
        all_ids.extend(item["fixture_id"] for item in collection)
    if len(all_ids) != len(set(all_ids)):
        raise ConformanceError("DUPLICATE_FIXTURE_ID", "fixture IDs must be globally unique")
    declared_case_count = len(jcs["positive"]) + len(jcs["negative"]) + len(mutations["positive_cases"]) + len(mutations["mutations"]) + len(kats["positive"]) + len(kats["negative_mutations"])
    if declared_case_count > max_cases:
        raise ConformanceError("RESOURCE_LIMIT", f"declared {declared_case_count} > {max_cases}")
    results: list[dict[str, Any]] = []

    def add(fixture_id: str, observed: str) -> None:
        if len(results) >= max_cases:
            raise ConformanceError("RESOURCE_LIMIT", "case cap reached")
        results.append({"fixture_id": fixture_id, "observed": observed})

    for fixture in jcs["positive"]:
        encoded = record.jcs_bytes(fixture["value"])
        if encoded.decode() != fixture["canonical_utf8"] or record.sha256_hex(encoded) != fixture["sha256"]:
            raise ConformanceError("FALSE_RECEIPT", fixture["fixture_id"])
        add(fixture["fixture_id"], "accepted")
    for fixture in jcs["negative"]:
        try:
            if "json_text" in fixture:
                record.strict_json_loads(fixture["json_text"])
            else:
                record.jcs_bytes(fixture["value"])
        except Exception as exc:
            observed = _exception_code(exc)
        else:
            observed = "accepted"
        if observed != fixture["expected_code"]:
            raise ConformanceError("FALSE_RECEIPT", f"{fixture['fixture_id']}: {observed}")
        add(fixture["fixture_id"], observed)
    positive_certificate = kats["positive"][0]["certificate"]
    receipt = certificate.verify_certificate(positive_certificate)
    if receipt.get("status") != "accepted":
        raise ConformanceError("FALSE_RECEIPT", "positive KAT")
    add(kats["positive"][0]["fixture_id"], "accepted")
    for fixture in kats["negative_mutations"]:
        mutated = mutate(positive_certificate, fixture)
        try:
            certificate.verify_certificate(mutated)
        except Exception as exc:
            observed = _exception_code(exc)
        else:
            observed = "accepted"
        if observed != fixture["expected_code"]:
            raise ConformanceError("FALSE_RECEIPT", f"{fixture['fixture_id']}: {observed}")
        add(fixture["fixture_id"], observed)
    candidate_base = jcs["positive"][0]["value"]
    candidate_fixture_base = next(item for item in _json(PACKAGE.parent / "v6" / "proof-fixtures.json")["candidate_counter_fixtures"] if item["slot"] == 0 and item["counter"] == 0)
    arithmetic_manifest = _json(PACKAGE / "arithmetic-input-manifest.json")
    stream_binding = arithmetic_manifest["immutable_v6_streams"][0]
    stream_lines = (REPOSITORY_ROOT / stream_binding["path"]).read_text(encoding="utf-8").rstrip("\n").split("\n")
    stream_records = [record.strict_json_loads(line) for line in stream_lines]
    row_terminal_base = {"terminal": stream_records[-1], "candidates": stream_records[:-1]}
    row_base = registry["frozen_rows"][0]
    terminal_base = _terminal_base()
    construction_base = _construction_base(row_base)
    tiny_identity = {
        "model": "short-weierstrass-y2=x3+ax+b",
        "p": "7",
        "a": "1",
        "b": "3",
    }
    tiny_curve = {
        "curve_id": _sha(json.dumps(tiny_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
        **tiny_identity,
    }
    tiny_config = {
        "fb_size": 2,
        "gb_budget": {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60},
        "macaulay_cap": 6,
        "random_point_attempts": 64,
        "planted_attempts": 50,
    }
    control_base = control.build_atomic_triplet(
        tiny_curve, "ectd-v7-static-o3-sole-tiny-kat", tiny_config, REPOSITORY_ROOT,
    )
    measurement_base = meter.measure_atomic_triplet(control_base, REPOSITORY_ROOT, control)
    measured_by_arm = {item["arm"]: item for item in measurement_base["arms"]}
    if set(measured_by_arm) != {"ordinary", "planted", "disabled_negative"}:
        raise ConformanceError("FIXTURE_GAP", "atomic meter arms")

    def endpoint(arm: str) -> dict[str, Any]:
        measured = measured_by_arm[arm]
        return {
            "meter_vector": measured["meter_vector"],
            "raw_trace": measured["raw_trace"],
            "control_triplet": control_base,
            "arm": arm,
        }

    decision_base = {
        "schema": decision.INPUT_SCHEMA,
        "instrument_receipts": [{
            "instrument_id": "atomic-meter-control",
            "instrument_kind": "atomic_meter_control",
            "payload": control_base,
        }],
        "edges": [
            {
                "edge_id": f"static-edge-{index}",
                "certificate": positive_certificate,
                "vertical": {"left": endpoint("ordinary"), "right": endpoint("ordinary")},
                "matched_horizontal": {"left": endpoint("ordinary"), "right": endpoint("disabled_negative")},
            }
            for index in range(8)
        ],
    }
    instrument_replayers = {
        "atomic_meter_control": lambda payload: control.verify_atomic_triplet(payload, REPOSITORY_ROOT),
    }
    suite_base = {
        "row": row_base,
        "terminal": terminal_base,
        "candidate": candidate_base,
        "candidate_fixture": candidate_fixture_base,
        "row_terminal": row_terminal_base,
        "construction": construction_base,
        "construction_complete": construction_base,
        "certificate": positive_certificate,
        "streams": arithmetic_manifest,
        "control": control_base,
        "raw": measured_by_arm["ordinary"]["raw_trace"],
        "decision": decision_base,
    }
    suite_call: dict[str, Callable[[Any], Any]] = {
        "row": lambda value: record.validate_frozen_row(value, registry),
        "terminal": lambda value: record.validate_record(value, registry),
        "candidate": lambda value: record.validate_record(value, registry),
        "candidate_fixture": lambda value: record.replay_candidate_fixture(value, registry),
        "row_terminal": lambda value: record.validate_record(value["terminal"], registry, row_candidates=value["candidates"]),
        "construction": lambda value: record.validate_record(value, registry),
        "construction_complete": lambda value: record.validate_record(value, registry),
        "certificate": certificate.verify_certificate,
        "streams": lambda value: record.replay_bound_streams(value, REPOSITORY_ROOT, registry),
        "control": lambda value: control.verify_atomic_triplet(value, REPOSITORY_ROOT),
        "raw": lambda value: meter.reduce_raw_trace(
            value,
            control_base["root"],
            control_base["target_bundles"]["unplanted"],
            REPOSITORY_ROOT,
        ),
        "decision": lambda value: decision.decide(
            value,
            meter_replayer=meter,
            control_replayer=control,
            certificate_replayer=certificate,
            instrument_replayers=instrument_replayers,
            repository_root=REPOSITORY_ROOT,
        ),
    }
    if set(mutations.get("base_objects", {})) != set(suite_base):
        raise ConformanceError("FIXTURE_GAP", "mutation base objects")
    declared_entrypoints = mutations.get("public_entrypoints")
    if not isinstance(declared_entrypoints, Mapping) or set(declared_entrypoints) != set(suite_call):
        raise ConformanceError("FIXTURE_GAP", "mutation public entrypoints")
    registry_by_code = {
        entry["code"]: entry
        for collection in (registry["terminals"], registry["validator_errors"])
        for entry in collection
    }
    for fixture in mutations["positive_cases"]:
        suite = fixture["suite"]
        if suite not in suite_call:
            raise ConformanceError("FIXTURE_GAP", f"positive suite: {suite}")
        outcome = suite_call[suite](suite_base[suite])
        observed = outcome.get("decision_branch", "accepted") if isinstance(outcome, Mapping) else "accepted"
        if observed != fixture["expected"]:
            raise ConformanceError("FALSE_RECEIPT", f"{fixture['fixture_id']}: {observed}")
        if suite == "control" and outcome.get("counts") != {"m3": 6, "m4": 6, "fb_decomposition": 24, "solver": 1}:
            raise ConformanceError("FALSE_RECEIPT", "atomic control cardinality")
        if suite == "raw":
            if measurement_base["counts"] != {"m3": 6, "m4": 6, "fb_decomposition": 24, "solver": 1}:
                raise ConformanceError("FALSE_RECEIPT", "meter cardinality")
            if measured_by_arm["ordinary"]["raw_trace"] != measured_by_arm["disabled_negative"]["raw_trace"]:
                raise ConformanceError("FALSE_RECEIPT", "ordinary/disabled raw identity")
        if suite == "decision":
            ks = outcome.get("ks_result")
            if not isinstance(ks, Mapping) or ks.get("rejects") is not False or outcome.get("n_complete_vertical_edges") != 8:
                raise ConformanceError("FALSE_RECEIPT", "exact KS positive")
        add(fixture["fixture_id"], observed)
    for fixture in mutations["mutations"]:
        suite = fixture["suite"]
        if suite not in suite_base:
            raise ConformanceError("FIXTURE_GAP", suite)
        if (
            fixture.get("base_object") != suite
            or fixture.get("expected_public_entrypoint") != declared_entrypoints[suite]
        ):
            raise ConformanceError("FIXTURE_GAP", f"{fixture['fixture_id']}: base/entrypoint")
        mutated = mutate(suite_base[suite], fixture)
        if suite == "control":
            mutated = _reseal_control_triplet(mutated, fixture)
        try:
            outcome = suite_call[suite](mutated)
        except Exception as exc:
            observed = _exception_code(exc)
        else:
            observed = outcome.get("decision_branch", "accepted") if isinstance(outcome, Mapping) else "accepted"
        expected = fixture.get("expected_code", fixture.get("expected_branch"))
        if observed != expected:
            raise ConformanceError("FALSE_RECEIPT", f"{fixture['fixture_id']}: {observed}")
        if fixture.get("expected_code") is not None:
            entry = registry_by_code[observed]
            actual_first = {
                "kind": "exception",
                "code": observed,
                "stage": entry["stage"],
                "class": entry["class"],
                "detail_keys": entry["detail_keys"],
            }
        else:
            actual_first = {
                "kind": "decision_branch",
                "branch": observed,
                "stage": "DECISION",
                "class": "resource_incomplete" if observed == "resource_incomplete" else "invalid",
                "detail_keys": ["reason"],
            }
        actual_canonical = {
            "schema": "crypto.autoresearch.ectd_v7_mutation_observation.v1",
            "fixture_id": fixture["fixture_id"],
            "public_entrypoint": declared_entrypoints[suite],
            "first": actual_first,
        }
        if fixture.get("expected_first") != actual_first or fixture.get("expected_canonical_output") != actual_canonical:
            raise ConformanceError("FALSE_RECEIPT", f"{fixture['fixture_id']}: canonical terminal")
        add(fixture["fixture_id"], observed)
        results[-1]["canonical_output"] = actual_canonical
    covered_ids = {item["fixture_id"] for item in results}
    executable_fixture_ids = {
        item["fixture_id"]
        for collection in (jcs["positive"], jcs["negative"], mutations["positive_cases"], mutations["mutations"], kats["positive"], kats["negative_mutations"])
        for item in collection
    }
    if covered_ids != executable_fixture_ids:
        raise ConformanceError("FIXTURE_GAP", str(sorted(executable_fixture_ids - covered_ids)))
    unknown_expected = {
        item.get("expected_code")
        for item in mutations["mutations"] + kats["negative_mutations"] + jcs["negative"]
        if item.get("expected_code") is not None
        and item.get("expected_code") not in registry_codes
    }
    if unknown_expected:
        raise ConformanceError("UNREGISTERED_EXCEPTION", str(sorted(unknown_expected)))
    after_cache = _cache_snapshot()
    if after_cache != before_cache:
        raise ConformanceError("CACHE_WRITE", str(sorted(after_cache - before_cache)))
    return {
        "schema": "crypto.autoresearch.ectd_v7_conformance_result.v1",
        "status": "passed",
        "executed_cases": len(results),
        "deferred_executor_cases": 0,
        "declared_cases": declared_case_count,
        "maximum_cases": MAX_CASES,
        "static_admission": admission,
        "positive_certificate_sha256": receipt["certificate_sha256"],
        "results_sha256": _sha(json.dumps(results, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
        "note": "All cases are bounded static replay over the sole F7 non-target KAT; no scheduled row, production target, experiment, or scientific meter observation is admitted.",
    }


if __name__ == "__main__":
    raise SystemExit("import and call run() only in the downstream approved Executor task")
