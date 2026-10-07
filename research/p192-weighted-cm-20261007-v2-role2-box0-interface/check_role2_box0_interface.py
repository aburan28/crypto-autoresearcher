#!/usr/bin/env python3
"""Static and byte-level checks for the non-executing Role-2 BOX-0 interface.

This checker performs no elliptic-curve search and never authorizes execution.
It closes the interface package and exposes helpers that the native producer,
independent verifier, and supervisor conformance tests can use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import struct
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research/p192-weighted-cm-20261007-v2-role2-box0-interface"
ADDENDUM = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role2_box0_interface.yaml"
OVERLAY = PACKAGE / "run-family.role2-box0-interface.yaml"
ARTIFACT_SCHEMA = PACKAGE / "schemas/role2-artifacts.schema.json"
DECISION_SCHEMA = PACKAGE / "schemas/role2-dispatch-decision.schema.json"
SUMS = PACKAGE / "SHA256SUMS"

PROTECTED_PROTOCOL_PATHS = {
    "specification.v2.yaml": ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml",
    "protocol-amendment.v2.yaml": ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml",
    "run-family.yaml": ROOT / "research/p192-weighted-cm-20261007-v2/run-family.yaml",
    "v2_addendum_role1_interface.yaml": ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml",
    "v2_addendum_role2_box0_interface.yaml": ADDENDUM,
    "README.md": PACKAGE / "README.md",
    "check_role2_box0_interface.py": PACKAGE / "check_role2_box0_interface.py",
    "run-family.role2-box0-interface.yaml": OVERLAY,
    "role2-artifacts.schema.json": ARTIFACT_SCHEMA,
    "role2-dispatch-decision.schema.json": DECISION_SCHEMA,
    "SHA256SUMS": SUMS,
    "test_p192_wcm_role2_interface.py": ROOT / "tests/test_p192_wcm_role2_interface.py",
}
PROTECTED_PROTOCOL_RELATIVE_PATHS = {
    name: str(path.relative_to(ROOT)) for name, path in PROTECTED_PROTOCOL_PATHS.items()
}
PROTOCOL_REPOSITORY = "https://github.com/aburan28/crypto-autoresearcher"
DECISION_RELATIVE_DIRECTORY = Path("ledger/decisions")

IMMUTABLE = {
    "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml":
        "34fb190ff222a37f2a626d18ba26b3e710a96c2d6eb11a5ab12dd561a4317484",
    "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml":
        "af43c91b9ab941158dd8a589fa6115f49b917b693f8cd1655f625e14a08611e8",
    "research/p192-weighted-cm-20261007-v2/run-family.yaml":
        "4bbb9c81318dceeba93734fce50dd96574513afa0c31e8c9ea8f310d91e7c6d6",
}

PAYLOAD_PATHS = (
    "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role2_box0_interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/README.md",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/run-family.role2-box0-interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/schemas/role2-artifacts.schema.json",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/schemas/role2-dispatch-decision.schema.json",
    "tests/test_p192_wcm_role2_interface.py",
)

PRODUCER_TEMPLATE = [
    "p192_weighted_cm", "sieve", "--shell", "BOX-0", "--v-max", "8",
    "--x-max-inclusive", "65536", "--factor-base",
    "PREDECESSOR_DIR/factor-base.json", "--out", "RUN_DIR",
]
VERIFIER_TEMPLATE = [
    "p192_weighted_cm_verify", "verify-shell", "--shell", "BOX-0",
    "--predecessor", "PREDECESSOR_DIR", "--source", "RUN_DIR", "--out",
    "RUN_DIR/independent-verification.json",
]
FAULT_TEMPLATE = [
    *PRODUCER_TEMPLATE[:-1], "CONTROL_DIR",
    "--control-stop-after-committed-shard", "0",
]
RESUME_TEMPLATE = [*PRODUCER_TEMPLATE[:-1], "CONTROL_DIR", "--resume"]
SUPERVISOR_TEMPLATE = [
    "p192_wcm_box0_supervisor", "--protocol-repository",
    "PROTOCOL_REPOSITORY_PATH", "--decision", "DECISION_JSON", "--producer",
    "PRODUCER_BIN", "--verifier", "VERIFIER_BIN", "--producer-repository",
    "PRODUCER_REPOSITORY_PATH", "--producer-package", "PRODUCER_PACKAGE_PATH",
    "--verifier-repository", "VERIFIER_REPOSITORY_PATH", "--verifier-package",
    "VERIFIER_PACKAGE_PATH", "--supervisor-repository",
    "SUPERVISOR_REPOSITORY_PATH", "--supervisor-package",
    "SUPERVISOR_PACKAGE_PATH",
    "--predecessor", "PREDECESSOR_DIR", "--run-dir", "RUN_DIR",
    "--control-dir", "CONTROL_DIR", "--audit-out", "AUDIT_FILE",
]

APPEND_PATHS = [
    "disposition.bin", "retained-candidates.jsonl",
    "complete-relations.jsonl", "partial-relations.jsonl",
]
TEMPORARY_PATHS = [
    "disposition-schema.json.tmp", "checkpoint-chain.jsonl.tmp",
    "candidate-stream.json.tmp", "verification.json.tmp",
]
PRODUCER_PATHS = [
    "candidate-stream.json", "complete-relations.jsonl",
    "partial-relations.jsonl", "disposition.bin", "disposition-schema.json",
    "checkpoint-chain.jsonl", "retained-candidates.jsonl", "verification.json",
]
PREDECESSOR_PATHS = [
    "factor-base.json", "factor-base.sha256", "verification.json",
    "independent-verification.json", "independent-agreement.json",
    "independent-verifier-receipt.json",
]
SUPERVISOR_PATHS = [
    "checkpoint-resume-control.json", "independent-agreement.json",
    "dependency-audit.json", "independent-verifier-receipt.json",
]
CUSTODY_PATHS = [
    "manifest.yaml", "command.txt", "environment.json", "stdout.log",
    "stderr.log", "raw-result.json",
]
STAGE_PATHS = [
    *PRODUCER_PATHS, "independent-verification.json", *SUPERVISOR_PATHS,
]
BASE_REQUIRED_OUTPUTS = [
    *PRODUCER_PATHS, "independent-verification.json",
    "independent-verifier-receipt.json",
]
ADDENDUM_CHILDREN = [
    "checkpoint-resume-control.json", "independent-agreement.json",
    "dependency-audit.json",
]
MANIFEST_ARTIFACT_PATHS = [
    *STAGE_PATHS, "command.txt", "environment.json", "stdout.log",
    "stderr.log", "raw-result.json",
]
FAILURE_PHASE_REQUIRED_PATHS = {
    "canonical_producer": PRODUCER_PATHS,
    "restart_control": [*PRODUCER_PATHS, "checkpoint-resume-control.json"],
    "independent_verifier": [*PRODUCER_PATHS, "independent-verification.json"],
    "agreement": [
        *PRODUCER_PATHS, "independent-verification.json",
        "checkpoint-resume-control.json", "independent-agreement.json",
    ],
    "final_custody": MANIFEST_ARTIFACT_PATHS[:-1],
}

PRODUCER_CHECKS = [
    "predecessor_role1_pass", "factor_base_canonical_and_regenerated",
    "source_provenance_bindings_consistent", "box0_iterator_complete",
    "candidate_root_recomputed", "disposition_stream_reparsed",
    "disposition_root_recomputed", "status_conservation",
    "retained_certificates_replayed", "complete_relations_replayed",
    "partial_rows_replayed", "checkpoint_chain_replayed",
    "append_prefixes_rehashed", "invalid_zero", "unresolved_zero",
]
INDEPENDENT_CHECKS = [
    "source_inventory_complete", "source_hashes_stable",
    "predecessor_hashes_replayed",
    "source_provenance_bindings_independently_replayed",
    "factor_base_independently_regenerated",
    "box0_iterator_independently_regenerated",
    "candidate_root_independently_regenerated",
    "every_disposition_independently_regenerated",
    "disposition_root_independently_regenerated",
    "every_retained_certificate_independently_reencoded",
    "every_complete_relation_independently_reencoded",
    "every_partial_row_independently_reencoded",
    "checkpoint_chain_independently_replayed",
    "append_prefixes_independently_rehashed",
    "status_conservation_independently_recomputed", "invalid_zero",
    "unresolved_zero",
]
AGREEMENT_FIELDS = [
    "protocol_commit", "producer_commit", "producer_binary_sha256",
    "factor_base_source_commit", "factor_base_sha256", "shell_id",
    "candidate_shell_sha256", "disposition_shell_sha256",
    "disposition_schema_sha256", "status_counts_sha256", "retained_candidates_sha256",
    "complete_relations_sha256", "partial_relations_sha256",
    "checkpoint_chain_sha256",
]
SUPERVISOR_CHILDREN = [
    {"role": "canonical_producer", "expected_exit_code": 0},
    {"role": "checkpoint_fault_control", "expected_exit_code": 75},
    {"role": "checkpoint_resume_control", "expected_exit_code": 0},
    {"role": "isolated_independent_verifier", "expected_exit_code": 0},
]
RUST_KEYWORDS = [
    "as", "async", "await", "break", "const", "continue", "crate", "dyn",
    "else", "enum", "extern", "false", "fn", "for", "if", "impl", "in",
    "let", "loop", "match", "mod", "move", "mut", "pub", "ref", "return",
    "self", "Self", "static", "struct", "super", "trait", "true", "type",
    "union", "unsafe", "use", "where", "while", "abstract", "become", "box",
    "do", "final", "macro", "override", "priv", "typeof", "unsized",
    "virtual", "yield", "try",
]
RUST_MULTI_OPERATORS = [
    "<<=", ">>=", "..=", "...", "::", "->", "=>", "==", "!=", "<=",
    ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=",
    "<<", ">>", "..",
]
CLONE_TOKEN_DOMAIN = b"P192-WCM-RUST-TOKENS-v1\0"
CLONE_TREE_DOMAIN = b"P192-WCM-RUST-SOURCE-TREE-v1\0"
FORBIDDEN_VERIFIER_SOURCE_MARKERS = [
    b"crypto_lib", b"include!", b"#[path", b"../producer/",
    b"p192-weighted-cm =",
]

STATUS_NAMES = {
    0: "nonprimitive_duplicate", 1: "complete", 2: "one_large_prime",
    3: "two_large_prime", 4: "rejected", 5: "invalid", 6: "unresolved",
}
ZERO64 = "0" * 64
TRACE_T = 31607402316713927207482677199
GROUP_ORDER_N = 6277101735386680763835789423176059013767194773182842284081


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class _UniqueYamlLoader(yaml.SafeLoader):
    """Safe loader that rejects duplicate mapping keys."""


def _unique_yaml_mapping(
    loader: _UniqueYamlLoader, node: yaml.nodes.MappingNode, deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                "found an unhashable key", key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _unique_yaml_mapping,
)


def load_yaml(path: Path) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueYamlLoader)


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_object_without_duplicates,
    )


def _reject_noncanonical_numbers(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("floating-point JSON values are forbidden")
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) > 9007199254740991:
        raise ValueError("JSON integer exceeds the interoperable range")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            _reject_noncanonical_numbers(child)
    elif isinstance(value, list):
        for child in value:
            _reject_noncanonical_numbers(child)


def canonical_json_bytes(value: Any) -> bytes:
    """Canonical bytes for this ASCII-keyed, integer-only interface subset."""
    _reject_noncanonical_numbers(value)
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = child
    return value


def decode_canonical_json(data: bytes) -> Any:
    if data.startswith(b"\xef\xbb\xbf") or data.endswith(b"\n") or b"\r" in data:
        raise ValueError("JSON has BOM, CR, or trailing LF")
    value = json.loads(
        data.decode("utf-8"),
        parse_float=lambda _: (_ for _ in ()).throw(ValueError("float")),
        object_pairs_hook=_object_without_duplicates,
    )
    if canonical_json_bytes(value) != data:
        raise ValueError("JSON bytes are not canonical")
    return value


def decode_canonical_jsonl(data: bytes) -> list[Any]:
    if not data:
        return []
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data or not data.endswith(b"\n"):
        raise ValueError("JSONL framing is not canonical")
    records = []
    for line in data[:-1].split(b"\n"):
        if not line:
            raise ValueError("blank JSONL line")
        value = json.loads(
            line.decode("utf-8"),
            parse_float=lambda _: (_ for _ in ()).throw(ValueError("float")),
            object_pairs_hook=_object_without_duplicates,
        )
        if canonical_json_bytes(value) != line:
            raise ValueError("JSONL record is not canonical")
        records.append(value)
    return records


def box0_pairs() -> Iterable[tuple[int, int, int]]:
    index = 0
    for v in range(1, 9):
        for x in range(v & 1, 65537, 2):
            yield index, v, x
            index += 1


def box0_counts() -> tuple[int, int, int]:
    total = primitive = 0
    for _, v, x in box0_pairs():
        u = abs((x - TRACE_T * v) // 2)
        primitive += math.gcd(u, v) == 1
        total += 1
    return total, primitive, total - primitive


def parse_disposition_details(
    data: bytes, expected_count: int = 262148,
) -> tuple[dict[str, int], list[int], dict[int, tuple[str, str]]]:
    """Parse the frozen variable-width disposition stream, without arithmetic."""
    counts = {name: 0 for name in STATUS_NAMES.values()}
    statuses: list[int] = []
    retained_hashes: dict[int, tuple[str, str]] = {}
    offset = 0
    for expected_index in range(expected_count):
        if len(data) - offset < 10:
            raise ValueError(f"truncated disposition prefix at {expected_index}")
        status = data[offset]
        candidate_index = int.from_bytes(data[offset + 1:offset + 9], "big")
        has_certificates = data[offset + 9]
        offset += 10
        if status not in STATUS_NAMES:
            raise ValueError(f"unknown status {status}")
        if candidate_index != expected_index:
            raise ValueError("disposition candidate index is not contiguous")
        expected_flag = 1 if status in (1, 2, 3) else 0
        if has_certificates != expected_flag:
            raise ValueError("certificate flag disagrees with status")
        if expected_flag:
            if len(data) - offset < 64:
                raise ValueError("truncated disposition certificate hashes")
            retained_hashes[expected_index] = (
                data[offset:offset + 32].hex(), data[offset + 32:offset + 64].hex(),
            )
            offset += 64
        counts[STATUS_NAMES[status]] += 1
        statuses.append(status)
    if offset != len(data):
        raise ValueError("trailing disposition bytes")
    return counts, statuses, retained_hashes


def parse_disposition_bytes(data: bytes, expected_count: int = 262148) -> dict[str, int]:
    return parse_disposition_details(data, expected_count)[0]


def validate_checkpoint(checkpoint: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    counters = checkpoint.get("phase_counters", {})
    try:
        values = {key: int(value) for key, value in counters.items()}
        if values.get("seen") != 262148 or checkpoint.get("next_candidate_index") != 262148:
            errors.append("checkpoint does not commit all 262148 candidates")
        if values.get("seen") != values.get("duplicate", -1) + values.get("primitive", -1):
            errors.append("checkpoint seen conservation failed")
        rhs = sum(values.get(key, -10**9) for key in (
            "complete", "one_lp", "two_lp", "rejected", "invalid", "unresolved"
        ))
        if values.get("primitive") != rhs:
            errors.append("checkpoint primitive conservation failed")
    except (TypeError, ValueError):
        errors.append("checkpoint counters are not minimal decimal integers")
    return errors


def _exact(actual: Any, expected: Any, label: str, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{label} differs from frozen value")


def _schema_validator(schema: dict[str, Any]) -> Draft202012Validator:
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_errors(schema: dict[str, Any], value: Any) -> list[str]:
    validator = _schema_validator(schema)
    return [error.message for error in sorted(validator.iter_errors(value), key=lambda error: list(error.path))]


def validate_artifact_document(value: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_json(ARTIFACT_SCHEMA)
    errors = _schema_errors(schema, value)
    if errors:
        return errors
    if "producer_commit" in value and "factor_base_source_commit" in value:
        _exact(
            value.get("producer_commit"), value.get("factor_base_source_commit"),
            "immutable producer/factor-base source commit equality", errors,
        )
    bindings = value.get("bindings")
    if isinstance(bindings, dict) and {
        "producer_commit", "factor_base_source_commit",
    }.issubset(bindings):
        _exact(
            bindings.get("producer_commit"), bindings.get("factor_base_source_commit"),
            "immutable producer/factor-base source commit binding equality", errors,
        )
    custody = value.get("decision_custody")
    if isinstance(custody, dict):
        checkout = custody.get("protocol_checkout", {})
        if "protocol_commit" in value:
            _exact(checkout.get("protocol_commit"), value.get("protocol_commit"), "decision custody protocol commit", errors)
        _exact(checkout.get("decision_commit"), custody.get("decision_commit"), "decision custody commit", errors)
    name = value.get("schema")
    if name == "p192-wcm-shell-verification-v1":
        _exact([item.get("check_id") for item in value.get("checks", [])], PRODUCER_CHECKS, "producer checks", errors)
        _exact([item.get("path") for item in value.get("artifacts", [])], PRODUCER_PATHS[:-1], "producer artifact order", errors)
        passed = all(item.get("status") == "PASS" for item in value.get("checks", []))
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "producer overall status", errors)
    elif name == "p192-wcm-shell-independent-verification-v1":
        _exact([item.get("check_id") for item in value.get("checks", [])], INDEPENDENT_CHECKS, "independent checks", errors)
        _exact([item.get("path") for item in value.get("source_artifacts", [])], PRODUCER_PATHS, "verifier source artifact order", errors)
        passed = all(item.get("status") == "PASS" for item in value.get("checks", []))
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "independent overall status", errors)
    elif name == "p192-wcm-shell-independent-agreement-v1":
        _exact([item.get("field") for item in value.get("comparisons", [])], AGREEMENT_FIELDS, "agreement field order", errors)
        for item in value.get("comparisons", []):
            _exact(item.get("equal"), item.get("producer") == item.get("verifier"), f'agreement equality {item.get("field")}', errors)
        passed = all(item.get("equal") is True for item in value.get("comparisons", []))
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "agreement overall status", errors)
    elif name == "p192-wcm-checkpoint-resume-control-v1":
        _exact([item.get("field") for item in value.get("comparisons", [])], PRODUCER_PATHS, "restart comparison order", errors)
        _exact(value.get("injected_paths"), APPEND_PATHS, "restart injected path order", errors)
        for item in value.get("comparisons", []):
            _exact(item.get("equal"), item.get("fresh_sha256") == item.get("resumed_sha256"), f'restart equality {item.get("field")}', errors)
        passed = (
            all(item.get("equal") is True for item in value.get("comparisons", []))
            and value.get("roots_equal") is True and value.get("counters_equal") is True
            and value.get("prefixes_equal") is True
        )
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "restart overall status", errors)
    elif name == "p192-wcm-shell-supervisor-receipt-v1":
        _exact(value.get("decision_id"), value.get("decision_custody", {}).get("decision_id"), "receipt decision id/custody", errors)
        _exact([item.get("path") for item in value.get("predecessor_artifacts_before", [])], PREDECESSOR_PATHS, "predecessor-before order", errors)
        _exact([item.get("path") for item in value.get("predecessor_artifacts_after", [])], PREDECESSOR_PATHS, "predecessor-after order", errors)
        _exact([item.get("path") for item in value.get("producer_artifacts_before_verifier", [])], PRODUCER_PATHS, "producer-before order", errors)
        _exact([item.get("path") for item in value.get("producer_artifacts_after_verifier", [])], PRODUCER_PATHS, "producer-after order", errors)
        _exact(
            [{"role": item.get("role"), "expected_exit_code": item.get("expected_exit_code")} for item in value.get("children", [])],
            SUPERVISOR_CHILDREN, "supervisor child order", errors,
        )
        children = value.get("children", [])
        if len(children) == 4:
            for item in children[:3]:
                _exact(item.get("commit"), value.get("producer_commit"), f'{item.get("role")} commit', errors)
            _exact(children[3].get("commit"), value.get("verifier_commit"), "verifier child commit", errors)
            if len({item.get("binary_sha256") for item in children[:3]}) != 1:
                errors.append("producer control children do not use one binary")
        predecessor_stable = value.get("predecessor_artifacts_before") == value.get("predecessor_artifacts_after")
        producer_stable = value.get("producer_artifacts_before_verifier") == value.get("producer_artifacts_after_verifier")
        passed = (
            all(item.get("expected_exit_code") == item.get("observed_exit_code") for item in children)
            and predecessor_stable and producer_stable
        )
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "supervisor overall status", errors)
    elif name == "p192-wcm-candidate-stream-v1":
        predecessor = value.get("predecessor", {})
        predecessor_paths = [
            predecessor.get("factor_base", {}).get("path"),
            predecessor.get("factor_base_sidecar", {}).get("path"),
            predecessor.get("producer_verification", {}).get("path"),
            predecessor.get("independent_verification", {}).get("path"),
            predecessor.get("independent_agreement", {}).get("path"),
            predecessor.get("supervisor_receipt", {}).get("path"),
        ]
        _exact(predecessor_paths, PREDECESSOR_PATHS, "candidate-stream predecessor paths", errors)
        _exact(value.get("disposition", {}).get("artifact", {}).get("path"), "disposition.bin", "disposition artifact path", errors)
        _exact(value.get("disposition_schema", {}).get("path"), "disposition-schema.json", "disposition schema artifact path", errors)
        _exact(value.get("retained_candidates", {}).get("artifact", {}).get("path"), "retained-candidates.jsonl", "retained artifact path", errors)
        _exact(value.get("complete_relations", {}).get("artifact", {}).get("path"), "complete-relations.jsonl", "complete artifact path", errors)
        _exact(value.get("partial_relations", {}).get("artifact", {}).get("path"), "partial-relations.jsonl", "partial artifact path", errors)
        _exact(value.get("checkpoint_chain", {}).get("artifact", {}).get("path"), "checkpoint-chain.jsonl", "checkpoint artifact path", errors)
        counts = value.get("status_counts", {})
        retained = sum(counts.get(key, -10**9) for key in ("complete", "one_large_prime", "two_large_prime"))
        if sum(counts.values()) != 262148:
            errors.append("candidate-stream status total is not 262148")
        if counts.get("nonprimitive_duplicate") != 93158:
            errors.append("candidate-stream duplicate count is not 93158")
        if retained + sum(counts.get(key, -10**9) for key in ("rejected", "invalid", "unresolved")) != 168990:
            errors.append("candidate-stream primitive conservation failed")
        _exact(value.get("retained_candidates", {}).get("record_count"), retained, "retained record count", errors)
        _exact(value.get("complete_relations", {}).get("record_count"), counts.get("complete"), "complete record count", errors)
        _exact(value.get("partial_relations", {}).get("record_count"), counts.get("one_large_prime", -1) + counts.get("two_large_prime", -1), "partial record count", errors)
        _exact(value.get("checkpoint_chain", {}).get("record_count"), 1, "checkpoint record count", errors)
        _exact(value.get("disposition", {}).get("artifact", {}).get("byte_length"), 2621480 + 64 * retained, "disposition byte length", errors)
    elif name == "p192-wcm-retained-candidate-v1":
        try:
            candidate_bytes = bytes.fromhex(value["candidate_certificate_hex"])
            factor_bytes = bytes.fromhex(value["factorization_certificate_hex"])
            _exact(value.get("candidate_certificate_byte_length"), len(candidate_bytes), "candidate certificate length", errors)
            _exact(value.get("candidate_certificate_sha256"), sha256_bytes(candidate_bytes), "candidate certificate hash", errors)
            _exact(value.get("candidate_id"), sha256_bytes(candidate_bytes), "candidate id", errors)
            _exact(value.get("factorization_certificate_byte_length"), len(factor_bytes), "factorization certificate length", errors)
            _exact(value.get("factorization_certificate_sha256"), sha256_bytes(factor_bytes), "factorization certificate hash", errors)
        except (KeyError, ValueError):
            errors.append("retained certificate bytes are malformed")
    elif name == "p192-wcm-complete-relation-v1":
        try:
            relation_bytes = bytes.fromhex(value["relation_bytes_hex"])
            _exact(value.get("relation_byte_length"), len(relation_bytes), "relation byte length", errors)
            _exact(value.get("relation_id"), sha256_bytes(relation_bytes), "relation id", errors)
            _exact(value.get("candidate_id"), value.get("candidate_certificate_sha256"), "complete relation candidate id", errors)
            lam = int(value["lambda_mod_n"])
            lam_bar = int(value["lambda_bar_mod_n"])
            product = int(value["lambda_product_mod_n"])
            if not all(0 <= item < GROUP_ORDER_N for item in (lam, lam_bar, product)):
                errors.append("lambda residues are outside [0,n)")
            if product != (lam * lam_bar) % GROUP_ORDER_N:
                errors.append("lambda product residue is inconsistent")
        except (KeyError, ValueError):
            errors.append("relation bytes are malformed")
    elif name == "p192-wcm-partial-relation-v1":
        row = value.get("large_prime_row", [])
        keys = [(item.get("prime"), item.get("smaller_root"), item.get("larger_root")) for item in row]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            errors.append("large-prime row is not strictly sorted")
        _exact(value.get("large_prime_row_sha256"), sha256_bytes(canonical_json_bytes(row)), "large-prime row hash", errors)
        _exact(value.get("candidate_id"), value.get("candidate_certificate_sha256"), "partial relation candidate id", errors)
        magnitudes = [abs(int(item.get("coefficient", "0"))) for item in row]
        if value.get("status") == 2 and not (len(row) == 1 and magnitudes == [1]):
            errors.append("status-2 row is not one unit-magnitude large prime")
        if value.get("status") == 3 and not (
            (len(row) == 2 and magnitudes == [1, 1])
            or (len(row) == 1 and magnitudes == [2])
        ):
            errors.append("status-3 row is not two large-prime factors")
    elif name == "p192-wcm-checkpoint-v1":
        errors.extend(validate_checkpoint(value))
    elif name == "p192-wcm-role2-dependency-audit-v1":
        for field in ("producer_rust_sources", "verifier_rust_sources", "supervisor_rust_sources"):
            paths = [item.get("path") for item in value.get(field, [])]
            if paths != sorted(paths) or len(set(paths)) != len(paths):
                errors.append(f"{field} is not strictly path-sorted")
        screen = value.get("source_clone_screen", {})
        matches = screen.get("matches", [])
        ordered = sorted(matches, key=lambda item: (
            -item.get("token_count", 0), item.get("producer_path", ""),
            item.get("producer_token_start", 0), item.get("producer_token_end_exclusive", 0),
            item.get("verifier_path", ""), item.get("verifier_token_start", 0),
            item.get("verifier_token_end_exclusive", 0),
        ))
        _exact(matches, ordered, "source-clone match order", errors)
        _exact(screen.get("max_match_tokens"), max((item.get("token_count", 0) for item in matches), default=0), "source-clone maximum", errors)
    elif name == "p192-wcm-role2-box0-environment-v1":
        build = value.get("supervisor_build", {})
        _exact(build.get("embedded_protocol_commit"), value.get("protocol_commit"), "environment embedded protocol commit", errors)
        _exact(build.get("embedded_producer_commit"), value.get("producer_commit"), "environment embedded producer commit", errors)
        _exact(build.get("embedded_verifier_commit"), value.get("verifier_commit"), "environment embedded verifier commit", errors)
        _exact(build.get("embedded_supervisor_commit"), value.get("supervisor_commit"), "environment embedded supervisor commit", errors)
    elif name in {"p192-wcm-role2-box0-raw-result-v1", "p192-wcm-role2-box0-failure-v1"}:
        if Path(value.get("run_dir", "/invalid")).name != value.get("run_id"):
            errors.append("raw-result run_dir basename does not equal run_id")
    if name == "p192-wcm-role2-box0-failure-v1":
        completed = [item.get("path") for item in value.get("completed_artifacts", [])]
        order = {path: index for index, path in enumerate(MANIFEST_ARTIFACT_PATHS)}
        if any(path not in order for path in completed) or completed != sorted(set(completed), key=order.get):
            errors.append("failure completed-artifact inventory is not an ordered unique subset")
        if "raw-result.json" in completed:
            errors.append("failure raw result cannot hash itself")
    elif name is None and set(value) == {"run"}:
        paths = [item.get("path") for item in value.get("run", {}).get("artifacts", [])]
        _exact(paths, MANIFEST_ARTIFACT_PATHS, "manifest artifact order", errors)
    return errors


def resolved_argv(decision: dict[str, Any]) -> dict[str, list[str]]:
    paths = decision["paths"]
    producer = [paths["producer_bin"], *PRODUCER_TEMPLATE[1:]]
    producer[9] = paths["factor_base_json"]
    producer[11] = paths["run_dir"]
    fault = [*producer]
    fault[11] = paths["control_dir"]
    fault += ["--control-stop-after-committed-shard", "0"]
    resume = [*producer]
    resume[11] = paths["control_dir"]
    resume += ["--resume"]
    verifier = [paths["verifier_bin"], *VERIFIER_TEMPLATE[1:]]
    verifier[5] = paths["predecessor_dir"]
    verifier[7] = paths["run_dir"]
    verifier[9] = str(Path(paths["run_dir"]) / "independent-verification.json")
    supervisor = [paths["supervisor_bin"], *SUPERVISOR_TEMPLATE[1:]]
    replacements = {
        "PROTOCOL_REPOSITORY_PATH": paths["protocol_repository_path"],
        "DECISION_JSON": paths["decision_json"], "PRODUCER_BIN": paths["producer_bin"],
        "VERIFIER_BIN": paths["verifier_bin"],
        "PRODUCER_REPOSITORY_PATH": paths["producer_repository_path"],
        "PRODUCER_PACKAGE_PATH": paths["producer_package_path"],
        "VERIFIER_REPOSITORY_PATH": paths["verifier_repository_path"],
        "VERIFIER_PACKAGE_PATH": paths["verifier_package_path"],
        "SUPERVISOR_REPOSITORY_PATH": paths["supervisor_repository_path"],
        "SUPERVISOR_PACKAGE_PATH": paths["supervisor_package_path"],
        "PREDECESSOR_DIR": paths["predecessor_dir"],
        "RUN_DIR": paths["run_dir"], "CONTROL_DIR": paths["control_dir"], "AUDIT_FILE": paths["audit_file"],
    }
    supervisor = [replacements.get(token, token) for token in supervisor]
    return {
        "producer_fresh_argv": producer,
        "producer_fault_argv": fault,
        "producer_resume_argv": resume,
        "independent_verifier_argv": verifier,
        "supervisor_argv": supervisor,
    }


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _normalized_absolute_path(value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected a nonempty path string")
        return None
    if any(ord(character) < 32 for character in value) or "<" in value or ">" in value:
        errors.append(f"{label}: control characters and placeholders are forbidden")
        return None
    path = Path(value)
    _require(path.is_absolute(), f"{label}: path must be absolute", errors)
    _require(not value.startswith("//"), f"{label}: double-slash root is forbidden", errors)
    _require(os.path.normpath(value) == value, f"{label}: path is not lexically normalized", errors)
    if not path.is_absolute() or value.startswith("//") or os.path.normpath(value) != value:
        return None
    return path


def _symlink_component(path: Path) -> Path | None:
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(metadata.st_mode):
            return current
    return None


def _paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def _rust_identifier_start(character: str) -> bool:
    return character == "_" or character.isalpha()


def _rust_identifier_continue(character: str) -> bool:
    return character == "_" or character.isalnum()


def _quoted_literal_end(text: str, quote_index: int, quote: str) -> int | None:
    index = quote_index + 1
    escaped = False
    while index < len(text):
        character = text[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == quote:
            return index + 1
        elif character in "\r\n" and quote == "'":
            return None
        index += 1
    return None


def _raw_literal_end(text: str, start: int) -> int | None:
    index = start
    if text.startswith(("br", "cr"), index):
        index += 2
    elif text.startswith("r", index):
        index += 1
    else:
        return None
    hashes = 0
    while index < len(text) and text[index] == "#":
        hashes += 1
        index += 1
    if index >= len(text) or text[index] != '"':
        return None
    terminator = '"' + "#" * hashes
    end = text.find(terminator, index + 1)
    if end < 0:
        raise ValueError("unterminated raw Rust literal")
    return end + len(terminator)


def _rust_structural_tokens(raw: bytes) -> list[str]:
    """Tokenize the frozen rust-structural-v1 normalization."""
    text = raw.decode("utf-8")
    tokens: list[str] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character in " \t\n\r\v\f":
            index += 1
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = len(text) if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            depth = 1
            index += 2
            while index < len(text) and depth:
                if text.startswith("/*", index):
                    depth += 1
                    index += 2
                elif text.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            if depth:
                raise ValueError("unterminated nested Rust block comment")
            continue
        raw_end = _raw_literal_end(text, index)
        if raw_end is not None:
            tokens.append("LITERAL")
            index = raw_end
            continue
        cooked_prefix = 1 if character in {"b", "c"} and index + 1 < len(text) else 0
        quote_index = index + cooked_prefix
        if quote_index < len(text) and text[quote_index] == '"':
            end = _quoted_literal_end(text, quote_index, '"')
            if end is None:
                raise ValueError("unterminated cooked Rust string literal")
            tokens.append("LITERAL")
            index = end
            continue
        if quote_index < len(text) and text[quote_index] == "'":
            end = _quoted_literal_end(text, quote_index, "'")
            if end is not None:
                tokens.append("LITERAL")
                index = end
                continue
        if text.startswith("r#", index) and index + 2 < len(text) and _rust_identifier_start(text[index + 2]):
            end = index + 3
            while end < len(text) and _rust_identifier_continue(text[end]):
                end += 1
            tokens.append("IDENT")
            index = end
            continue
        if _rust_identifier_start(character):
            end = index + 1
            while end < len(text) and _rust_identifier_continue(text[end]):
                end += 1
            identifier = text[index:end]
            tokens.append(identifier if identifier in RUST_KEYWORDS else "IDENT")
            index = end
            continue
        if character.isdigit():
            end = index + 1
            while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                end += 1
            if (
                end < len(text) and text[end] == "."
                and not text.startswith("..", end)
                and end + 1 < len(text) and text[end + 1].isdigit()
            ):
                end += 1
                while end < len(text) and (text[end].isdigit() or text[end] == "_"):
                    end += 1
                if end < len(text) and text[end] in {"e", "E"}:
                    end += 1
                    if end < len(text) and text[end] in {"+", "-"}:
                        end += 1
                    while end < len(text) and (text[end].isdigit() or text[end] == "_"):
                        end += 1
                while end < len(text) and _rust_identifier_continue(text[end]):
                    end += 1
            tokens.append("NUMBER")
            index = end
            continue
        operator = next(
            (candidate for candidate in RUST_MULTI_OPERATORS if text.startswith(candidate, index)),
            None,
        )
        if operator is not None:
            tokens.append(operator)
            index += len(operator)
        else:
            tokens.append(character)
            index += 1
    return tokens


def _token_digest(tokens: list[str]) -> str:
    digest = hashlib.sha256(CLONE_TOKEN_DOMAIN)
    for token in tokens:
        encoded = token.encode("utf-8")
        digest.update(struct.pack(">I", len(encoded)))
        digest.update(encoded)
    return digest.hexdigest()


def _collect_rust_sources(
    root: Path, *, exclude_root_target: bool = False,
) -> list[tuple[str, bytes, list[str]]]:
    if not root.is_absolute() or _symlink_component(root) is not None:
        raise ValueError(f"source root must be absolute and non-symlink: {root}")
    try:
        metadata = os.lstat(root)
    except OSError as exc:
        raise ValueError(f"cannot stat source root {root}: {exc}") from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise ValueError(f"source root is not a directory: {root}")
    records: list[tuple[str, bytes, list[str]]] = []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            raise ValueError(f"cannot scan source directory {directory}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"source symlink is forbidden: {path}")
            if exclude_root_target and directory == root and entry.name == "target":
                if not stat.S_ISDIR(metadata.st_mode):
                    raise ValueError(f"root target exclusion is not a directory: {path}")
                continue
            if stat.S_ISDIR(metadata.st_mode):
                visit(path)
            elif stat.S_ISREG(metadata.st_mode) and entry.name.endswith(".rs"):
                raw = path.read_bytes()
                records.append((path.relative_to(root).as_posix(), raw, _rust_structural_tokens(raw)))

    visit(root)
    records.sort(key=lambda record: record[0])
    if not records:
        raise ValueError(f"source root has no regular UTF-8 Rust source: {root}")
    return records


def _collect_rust_hash_rows(package: Path) -> list[dict[str, str]]:
    records = _collect_rust_sources(package, exclude_root_target=True)
    return [
        {"path": relative, "sha256": sha256_bytes(raw)}
        for relative, raw, _ in records
    ]


def _source_tree_digest(records: list[tuple[str, bytes, list[str]]]) -> str:
    digest = hashlib.sha256(CLONE_TREE_DOMAIN)
    for relative, raw, _ in records:
        encoded = relative.encode("utf-8")
        digest.update(struct.pack(">I", len(encoded)))
        digest.update(encoded)
        digest.update(struct.pack(">Q", len(raw)))
        digest.update(raw)
    return digest.hexdigest()


def compute_source_clone_screen(producer_root: Path, verifier_root: Path) -> dict[str, Any]:
    producer_records = _collect_rust_sources(producer_root)
    verifier_records = _collect_rust_sources(verifier_root)
    producer_windows: dict[str, list[tuple[int, int]]] = {}
    for file_index, (_, _, tokens) in enumerate(producer_records):
        for start in range(max(0, len(tokens) - 63)):
            producer_windows.setdefault(_token_digest(tokens[start:start + 64]), []).append((file_index, start))
    endpoints: set[tuple[int, int, int, int, int, int]] = set()
    for verifier_index, (_, _, verifier_tokens) in enumerate(verifier_records):
        for verifier_start in range(max(0, len(verifier_tokens) - 63)):
            window = verifier_tokens[verifier_start:verifier_start + 64]
            for producer_index, producer_start in producer_windows.get(_token_digest(window), []):
                producer_tokens = producer_records[producer_index][2]
                if producer_tokens[producer_start:producer_start + 64] != window:
                    continue
                p_start, v_start = producer_start, verifier_start
                while p_start and v_start and producer_tokens[p_start - 1] == verifier_tokens[v_start - 1]:
                    p_start -= 1
                    v_start -= 1
                p_end, v_end = producer_start + 64, verifier_start + 64
                while p_end < len(producer_tokens) and v_end < len(verifier_tokens) and producer_tokens[p_end] == verifier_tokens[v_end]:
                    p_end += 1
                    v_end += 1
                endpoints.add((producer_index, p_start, p_end, verifier_index, v_start, v_end))
    maximal: list[tuple[int, int, int, int, int, int]] = []
    for candidate in sorted(endpoints):
        p_file, p_start, p_end, v_file, v_start, v_end = candidate
        contained = any(
            other != candidate and other[0] == p_file and other[3] == v_file
            and other[1] <= p_start and p_end <= other[2]
            and other[4] <= v_start and v_end <= other[5]
            and other[2] - other[1] > p_end - p_start
            for other in endpoints
        )
        if not contained:
            maximal.append(candidate)
    matches: list[dict[str, Any]] = []
    for p_file, p_start, p_end, v_file, v_start, v_end in maximal:
        tokens = producer_records[p_file][2][p_start:p_end]
        matches.append({
            "producer_path": producer_records[p_file][0],
            "producer_token_start": p_start,
            "producer_token_end_exclusive": p_end,
            "verifier_path": verifier_records[v_file][0],
            "verifier_token_start": v_start,
            "verifier_token_end_exclusive": v_end,
            "token_count": p_end - p_start,
            "normalized_tokens_sha256": _token_digest(tokens),
        })
    matches.sort(key=lambda match: (
        -match["token_count"], match["producer_path"], match["producer_token_start"],
        match["producer_token_end_exclusive"], match["verifier_path"],
        match["verifier_token_start"], match["verifier_token_end_exclusive"],
    ))
    maximum = max((match["token_count"] for match in matches), default=0)
    return {
        "schema": "p192-wcm-source-clone-screen-v1",
        "normalization": "rust-structural-v1",
        "producer_root": str(producer_root),
        "verifier_root": str(verifier_root),
        "include": "**/*.rs",
        "excluded_components": [],
        "report_min_tokens": 64,
        "reject_at_tokens": 128,
        "producer_tree_sha256": _source_tree_digest(producer_records),
        "verifier_tree_sha256": _source_tree_digest(verifier_records),
        "matches": matches,
        "max_match_tokens": maximum,
        "claim_limit": "high_similarity_screen_not_proof_of_zero_conceptual_or_common_lineage",
        "overall_status": "PASS" if maximum < 128 else "FAIL",
    }


def _verifier_dependency_errors(
    manifest_bytes: bytes,
    lock_bytes: bytes,
    verifier_package: Path,
    producer_package: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        manifest = tomllib.loads(manifest_bytes.decode("utf-8"))
        lock = tomllib.loads(lock_bytes.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return [f"verifier Cargo provenance is not valid UTF-8 TOML: {exc}"]

    tables: list[tuple[str, Any]] = []
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        tables.append((section, manifest.get(section, {})))
    target_tables = manifest.get("target", {})
    if isinstance(target_tables, dict):
        for target, target_document in target_tables.items():
            if not isinstance(target_document, dict):
                continue
            for section in ("dependencies", "dev-dependencies", "build-dependencies"):
                tables.append((f"target.{target}.{section}", target_document.get(section, {})))

    expected_producer = producer_package.resolve(strict=False)
    for scope, table in tables:
        if not isinstance(table, dict):
            errors.append(f"verifier Cargo {scope} is not a dependency table")
            continue
        for alias, specification in table.items():
            package_name = alias
            dependency_path: str | None = None
            if isinstance(specification, dict):
                package_name = specification.get("package", alias)
                dependency_path = specification.get("path")
                if specification.get("workspace") is True:
                    errors.append(
                        f"verifier Cargo dependency {scope}.{alias} uses unresolved workspace inheritance"
                    )
            if alias == "p192-weighted-cm" or package_name == "p192-weighted-cm":
                errors.append(
                    f"verifier Cargo dependency {scope}.{alias} directly names p192-weighted-cm"
                )
            if isinstance(dependency_path, str):
                resolved = (verifier_package / dependency_path).resolve(strict=False)
                if resolved == expected_producer:
                    errors.append(
                        f"verifier Cargo dependency {scope}.{alias} resolves to the producer package"
                    )

    packages = lock.get("package", [])
    if not isinstance(packages, list):
        errors.append("verifier Cargo.lock package inventory is not an array")
    elif any(
        isinstance(package, dict) and package.get("name") == "p192-weighted-cm"
        for package in packages
    ):
        errors.append("verifier Cargo.lock contains the p192-weighted-cm producer package")
    return errors


def _git(repository: Path, arguments: list[str]) -> subprocess.CompletedProcess[bytes] | None:
    try:
        return subprocess.run(
            [
                "/usr/bin/git", "--no-pager", "--no-replace-objects",
                "-c", "core.fsmonitor=false",
                "-c", "core.hooksPath=/dev/null",
                "-c", "core.attributesFile=/dev/null",
                "-c", "core.commitGraph=false",
                "-c", "protocol.ext.allow=never",
                "-c", "diff.external=",
                "-C", str(repository), *arguments,
            ],
            check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={
                "LC_ALL": "C",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": "/dev/null",
                "GIT_NO_REPLACE_OBJECTS": "1",
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_PAGER": "cat",
                "GIT_LITERAL_PATHSPECS": "1",
                "GIT_GRAFT_FILE": "/dev/null",
                "GIT_NO_LAZY_FETCH": "1",
            },
        )
    except OSError:
        return None


def _git_stdout(repository: Path, arguments: list[str], label: str, errors: list[str]) -> bytes | None:
    result = _git(repository, arguments)
    if result is None or result.returncode != 0:
        detail = "git unavailable" if result is None else result.stderr.decode("utf-8", "replace").strip()
        errors.append(f"{label}: {detail or 'Git command failed'}")
        return None
    return result.stdout


def _git_tree_entry(
    repository: Path, commit: str, relative: str, label: str, errors: list[str],
) -> tuple[str, str, str] | None:
    output = _git_stdout(repository, ["ls-tree", "-z", commit, "--", relative], label, errors)
    if output is None:
        return None
    records = [record for record in output.split(b"\0") if record]
    if len(records) != 1:
        errors.append(f"{label}: expected exactly one Git tree entry")
        return None
    try:
        header, encoded_path = records[0].split(b"\t", 1)
        mode, kind, object_id = header.decode("ascii").split(" ")
        path = encoded_path.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        errors.append(f"{label}: malformed Git tree entry")
        return None
    _exact(path, relative, f"{label} path", errors)
    return mode, kind, object_id


def _git_blob(repository: Path, object_id: str, label: str, errors: list[str]) -> bytes | None:
    return _git_stdout(repository, ["cat-file", "blob", object_id], label, errors)


def _raw_commit_parents(
    repository: Path, commit: str, label: str, errors: list[str],
) -> list[str] | None:
    raw = _git_stdout(repository, ["cat-file", "commit", commit], f"raw {label} commit", errors)
    if raw is None:
        return None
    if b"\n\n" not in raw:
        errors.append(f"raw {label} commit lacks a header terminator")
        return None
    header = raw.split(b"\n\n", 1)[0]
    trees: list[str] = []
    parents: list[str] = []
    for line in header.splitlines():
        if line.startswith(b"tree "):
            trees.append(line[5:].decode("ascii", "replace"))
        elif line.startswith(b"parent "):
            parents.append(line[7:].decode("ascii", "replace"))
    if len(trees) != 1 or re.fullmatch(r"[0-9a-f]{40}", trees[0]) is None:
        errors.append(f"raw {label} commit must contain exactly one valid tree")
        return None
    if any(re.fullmatch(r"[0-9a-f]{40}", parent) is None for parent in parents):
        errors.append(f"raw {label} commit contains an invalid parent")
        return None
    if len(set(parents)) != len(parents):
        errors.append(f"raw {label} commit contains duplicate parents")
        return None
    return parents


def _raw_commit_is_strict_ancestor(
    repository: Path, ancestor: str, descendant: str, errors: list[str],
) -> bool | None:
    if ancestor == descendant:
        return False
    pending = _raw_commit_parents(repository, descendant, "descendant", errors)
    if pending is None:
        return None
    visited: set[str] = set()
    while pending:
        commit = pending.pop()
        if commit == ancestor:
            return True
        if commit in visited:
            continue
        visited.add(commit)
        if len(visited) > 1_000_000:
            errors.append("raw commit ancestry exceeds the one-million-commit safety cap")
            return None
        parents = _raw_commit_parents(repository, commit, "ancestor traversal", errors)
        if parents is None:
            return None
        pending.extend(parents)
    return False


def _validate_regular_file(path: Path, label: str, errors: list[str], executable: bool = False) -> None:
    linked = _symlink_component(path)
    _require(linked is None, f"{label}: symlink path component forbidden: {linked}", errors)
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        errors.append(f"{label}: cannot stat: {exc}")
        return
    _require(stat.S_ISREG(metadata.st_mode), f"{label}: not a regular file", errors)
    if executable:
        _require(metadata.st_mode & 0o111 != 0, f"{label}: executable bit is missing", errors)


def _validate_git_checkout(
    repository: Path, package: Path, expected_commit: str, package_suffix: tuple[str, ...],
    label: str, errors: list[str],
) -> None:
    _require(_symlink_component(repository) is None, f"{label}: repository has a symlink component", errors)
    _require(_symlink_component(package) is None, f"{label}: package has a symlink component", errors)
    _require(repository.is_dir(), f"{label}: repository is not a directory", errors)
    _require(package.is_dir(), f"{label}: package is not a directory", errors)
    _require(repository in package.parents, f"{label}: package is not a strict repository descendant", errors)
    _require(package.parts[-len(package_suffix):] == package_suffix, f"{label}: package suffix differs", errors)
    top = _git_stdout(repository, ["rev-parse", "--show-toplevel"], f"{label} Git top level", errors)
    if top is not None:
        _exact(top.rstrip(b"\n").decode("utf-8", "replace"), str(repository), f"{label} Git top level", errors)
    head = _git_stdout(repository, ["rev-parse", "HEAD"], f"{label} Git HEAD", errors)
    if head is not None:
        _exact(head.rstrip(b"\n").decode("ascii", "replace"), expected_commit, f"{label} Git HEAD", errors)
    status_output = _git_stdout(
        repository, ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        f"{label} Git status", errors,
    )
    if status_output is not None:
        _exact(status_output, b"", f"{label} worktree cleanliness", errors)


def _decision_custody(
    decision: dict[str, Any], decision_path: Path, decision_bytes: bytes, decision_commit: str,
) -> dict[str, Any]:
    paths = decision["paths"]
    return {
        "decision_id": decision["decision_id"],
        "decision_path": str(decision_path),
        "decision_commit": decision_commit,
        "decision_sha256": sha256_bytes(decision_bytes),
        "protocol_checkout": {
            "repository": decision["protocol_repository"],
            "repository_path": paths["protocol_repository_path"],
            "package_path": paths["protocol_package_path"],
            "protocol_commit": decision["protocol_commit"],
            "decision_commit": decision_commit,
            "worktree_clean": True,
        },
    }


def validate_decision(value: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_json(DECISION_SCHEMA)
    errors = _schema_errors(schema, value)
    if errors:
        return errors
    paths = value["paths"]
    normalized: dict[str, Path] = {}
    for field, raw_path in paths.items():
        parsed = _normalized_absolute_path(raw_path, f"decision paths.{field}", errors)
        if parsed is not None:
            normalized[field] = parsed
    if len(normalized) != len(paths):
        return errors
    protocol_repository = normalized["protocol_repository_path"]
    _exact(
        normalized["protocol_package_path"], protocol_repository,
        "protocol package/repository identity", errors,
    )
    expected_decision = protocol_repository / DECISION_RELATIVE_DIRECTORY / f'{value["decision_id"]}.json'
    _exact(normalized["decision_json"], expected_decision, "exact decision path", errors)
    if paths["factor_base_json"] != str(Path(paths["predecessor_dir"]) / "factor-base.json"):
        errors.append("factor_base_json is not predecessor_dir/factor-base.json")
    if paths["audit_file"] != str(Path(paths["run_dir"]) / "dependency-audit.json"):
        errors.append("audit_file is not run_dir/dependency-audit.json")
    if Path(paths["run_dir"]).name != value["run_id"]:
        errors.append("run_dir basename does not equal run_id")
    if Path(paths["predecessor_dir"]).name != value["predecessor_run_id"]:
        errors.append("predecessor_dir basename does not equal predecessor_run_id")
    created_date = value["created_at_utc"][:10].replace("-", "")
    _exact(value["decision_id"][4:12], created_date, "decision id/date binding", errors)
    if value["factor_base_source_commit"] != value["producer_commit"]:
        errors.append(
            "producer_commit does not equal predecessor factor_base_source_commit"
        )
    role_paths = {
        "producer": (
            normalized["producer_repository_path"], normalized["producer_package_path"],
            ("tools", "p192-weighted-cm"),
        ),
        "verifier": (
            normalized["verifier_repository_path"], normalized["verifier_package_path"],
            ("tools", "p192-weighted-cm-verify"),
        ),
        "supervisor": (
            normalized["supervisor_repository_path"], normalized["supervisor_package_path"],
            ("tools", "p192-weighted-cm-supervisor"),
        ),
    }
    for role, (repository, package, suffix) in role_paths.items():
        _require(repository in package.parents, f"{role} package is not a strict repository descendant", errors)
        _require(package.parts[-len(suffix):] == suffix, f"{role} package suffix differs", errors)
    run = normalized["run_dir"]
    control = normalized["control_dir"]
    if run == control or run in control.parents or control in run.parents:
        errors.append("run_dir and control_dir overlap")
    output_paths = {
        "run_dir": run,
        "control_dir": control,
        "audit_file": normalized["audit_file"],
    }
    immutable_inputs = {
        key: normalized[key] for key in (
            "protocol_repository_path", "protocol_package_path", "decision_json",
            "producer_bin", "verifier_bin", "supervisor_bin",
            "producer_repository_path", "producer_package_path",
            "verifier_repository_path", "verifier_package_path",
            "supervisor_repository_path", "supervisor_package_path",
            "predecessor_dir", "factor_base_json",
        )
    }
    for output_name, output_path in output_paths.items():
        for input_name, input_path in immutable_inputs.items():
            if _paths_overlap(output_path, input_path):
                errors.append(f"{output_name} overlaps immutable input {input_name}")
    for field, expected in resolved_argv(value).items():
        _exact(value[field], expected, field, errors)
    protected = {
        name: sha256_path(path) for name, path in PROTECTED_PROTOCOL_PATHS.items()
    }
    _exact(value.get("protected_protocol_blobs"), protected, "protected protocol blobs", errors)
    return errors


def validate_dispatch_decision(
    decision_path: Path, phase: str, run_dir: Path | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    """Validate exact committed decision and all pre/post-dispatch filesystem custody."""
    errors: list[str] = []
    _require(phase in {"pre-dispatch", "post-run"}, "decision phase is invalid", errors)
    supplied = _normalized_absolute_path(str(decision_path), "supplied decision path", errors)
    if supplied is None:
        return None, None, errors
    _validate_regular_file(supplied, "decision", errors)
    try:
        _require(
            os.lstat(supplied).st_mode & 0o111 == 0,
            "decision working-tree mode is not non-executable 100644", errors,
        )
    except OSError:
        pass
    try:
        raw = supplied.read_bytes()
        decision = decode_canonical_json(raw)
    except Exception as exc:
        errors.append(f"decision bytes invalid: {exc}")
        return None, None, errors
    if not isinstance(decision, dict):
        return None, None, errors + ["decision root is not an object"]
    errors.extend(validate_decision(decision))
    if errors:
        return decision, None, errors
    paths = decision["paths"]
    _exact(paths["decision_json"], str(supplied), "supplied/exact decision path", errors)
    protocol_repository = Path(paths["protocol_repository_path"])
    protocol_package = Path(paths["protocol_package_path"])
    _exact(protocol_package, protocol_repository, "protocol package/repository path", errors)
    _require(_symlink_component(protocol_repository) is None, "protocol repository has a symlink component", errors)
    _require(protocol_repository.is_dir(), "protocol repository is not a directory", errors)
    top = _git_stdout(protocol_repository, ["rev-parse", "--show-toplevel"], "protocol Git top level", errors)
    if top is not None:
        _exact(top.rstrip(b"\n").decode("utf-8", "replace"), str(protocol_repository), "protocol Git top level", errors)
    head = _git_stdout(protocol_repository, ["rev-parse", "HEAD"], "protocol decision commit", errors)
    decision_commit = ""
    if head is not None:
        decision_commit = head.rstrip(b"\n").decode("ascii", "replace")
        _require(re.fullmatch(r"[0-9a-f]{40}", decision_commit) is not None, "protocol decision commit is not lowercase 40-hex", errors)
    status_output = _git_stdout(
        protocol_repository, ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        "protocol Git status", errors,
    )
    if status_output is not None:
        _exact(status_output, b"", "protocol worktree cleanliness", errors)
    protocol_commit = decision["protocol_commit"]
    for commit, label in ((protocol_commit, "protocol commit"), (decision_commit, "decision commit")):
        if commit:
            result = _git(protocol_repository, ["cat-file", "-e", f"{commit}^{{commit}}"])
            _require(result is not None and result.returncode == 0, f"{label} is not a Git commit", errors)
    _require(protocol_commit != decision_commit, "protocol commit must be a strict decision-commit ancestor", errors)
    if decision_commit:
        ancestor = _raw_commit_is_strict_ancestor(
            protocol_repository, protocol_commit, decision_commit, errors,
        )
        if ancestor is not None:
            _require(ancestor, "protocol commit is not an ancestor of decision commit", errors)
    relative_decision = str(DECISION_RELATIVE_DIRECTORY / f'{decision["decision_id"]}.json')
    at_protocol = _git_stdout(
        protocol_repository, ["ls-tree", "-z", protocol_commit, "--", relative_decision],
        "decision absence at protocol commit", errors,
    )
    if at_protocol is not None:
        _exact(at_protocol, b"", "fresh decision absence at protocol commit", errors)
    if decision_commit:
        entry = _git_tree_entry(
            protocol_repository, decision_commit, relative_decision,
            "decision at decision commit", errors,
        )
        if entry is not None:
            mode, kind, object_id = entry
            _exact((mode, kind), ("100644", "blob"), "decision Git mode/type", errors)
            committed = _git_blob(protocol_repository, object_id, "committed decision blob", errors)
            if committed is not None:
                _exact(committed, raw, "decision working bytes", errors)
    for name, relative in PROTECTED_PROTOCOL_RELATIVE_PATHS.items():
        expected_hash = decision["protected_protocol_blobs"][name]
        current = protocol_repository / relative
        _validate_regular_file(current, f"protected current {relative}", errors)
        try:
            metadata = os.lstat(current)
            current_mode = "100755" if metadata.st_mode & 0o111 else "100644"
            current_bytes = current.read_bytes()
        except OSError:
            continue
        _exact(current_mode, "100644", f"protected current mode {relative}", errors)
        _exact(sha256_bytes(current_bytes), expected_hash, f"protected current hash {relative}", errors)
        entries: list[tuple[str, str, str] | None] = []
        for commit, label in ((protocol_commit, "protocol"), (decision_commit, "decision")):
            if not commit:
                entries.append(None)
                continue
            tree_entry = _git_tree_entry(
                protocol_repository, commit, relative,
                f"protected {label} entry {relative}", errors,
            )
            entries.append(tree_entry)
            if tree_entry is not None:
                mode, kind, object_id = tree_entry
                _exact((mode, kind), ("100644", "blob"), f"protected {label} mode/type {relative}", errors)
                blob = _git_blob(protocol_repository, object_id, f"protected {label} blob {relative}", errors)
                if blob is not None:
                    _exact(blob, current_bytes, f"protected {label}/current bytes {relative}", errors)
                    _exact(sha256_bytes(blob), expected_hash, f"protected {label} hash {relative}", errors)
        if len(entries) == 2 and entries[0] is not None and entries[1] is not None:
            _exact(entries[0], entries[1], f"protected Git entry stability {relative}", errors)
    role_specs = (
        ("producer", decision["producer_commit"], ("tools", "p192-weighted-cm")),
        ("verifier", decision["verifier_commit"], ("tools", "p192-weighted-cm-verify")),
        ("supervisor", decision["supervisor_commit"], ("tools", "p192-weighted-cm-supervisor")),
    )
    for role, commit, suffix in role_specs:
        _validate_git_checkout(
            Path(paths[f"{role}_repository_path"]), Path(paths[f"{role}_package_path"]),
            commit, suffix, role, errors,
        )
        binary = Path(paths[f"{role}_bin"])
        _validate_regular_file(binary, f"{role} binary", errors, executable=True)
        try:
            _exact(sha256_path(binary), decision[f"{role}_binary_sha256"], f"{role} binary hash", errors)
        except OSError:
            pass
    predecessor = Path(paths["predecessor_dir"])
    _require(_symlink_component(predecessor) is None, "predecessor has a symlink component", errors)
    _require(predecessor.is_dir(), "predecessor is not a directory", errors)
    for name in PREDECESSOR_PATHS:
        path = predecessor / name
        _validate_regular_file(path, f"predecessor {name}", errors)
        try:
            _exact(sha256_path(path), decision["predecessor_artifacts"][name], f"predecessor hash {name}", errors)
        except OSError:
            pass
    try:
        factor_base_bytes = (predecessor / "factor-base.json").read_bytes()
        factor_base = decode_canonical_json(factor_base_bytes)
        _exact(factor_base.get("source_commit"), decision["factor_base_source_commit"], "pre-dispatch factor-base source commit", errors)
        expected_sidecar = f'{sha256_bytes(factor_base_bytes)}  factor-base.json\n'.encode("ascii")
        _exact((predecessor / "factor-base.sha256").read_bytes(), expected_sidecar, "pre-dispatch factor-base sidecar", errors)
        for name in ("verification.json", "independent-verification.json", "independent-agreement.json", "independent-verifier-receipt.json"):
            predecessor_doc = decode_canonical_json((predecessor / name).read_bytes())
            _exact(predecessor_doc.get("overall_status"), "PASS", f"pre-dispatch predecessor {name} status", errors)
            _exact(predecessor_doc.get("protocol_commit"), decision["protocol_commit"], f"pre-dispatch predecessor {name} protocol commit", errors)
            _exact(predecessor_doc.get("source_commit"), decision["factor_base_source_commit"], f"pre-dispatch predecessor {name} source commit", errors)
    except Exception as exc:
        errors.append(f"pre-dispatch predecessor semantic validation failed: {exc}")
    expected_run = Path(paths["run_dir"])
    expected_control = Path(paths["control_dir"])
    for label, path in (
        ("RUN_DIR", expected_run), ("CONTROL_DIR", expected_control),
        ("AUDIT_FILE", Path(paths["audit_file"])),
    ):
        linked = _symlink_component(path)
        _require(linked is None, f"{label} has a symlink component: {linked}", errors)
    if phase == "pre-dispatch":
        _require(not os.path.lexists(expected_run), "pre-dispatch RUN_DIR already exists", errors)
        _require(not os.path.lexists(expected_control), "pre-dispatch CONTROL_DIR already exists", errors)
    else:
        if run_dir is None:
            errors.append("post-run validation requires run_dir")
        else:
            parsed_run = _normalized_absolute_path(str(run_dir), "supplied run_dir", errors)
            if parsed_run is not None:
                _exact(parsed_run, expected_run, "supplied/decision run_dir", errors)
        _require(expected_run.is_dir(), "post-run RUN_DIR is not a directory", errors)
        _require(_symlink_component(expected_run) is None, "post-run RUN_DIR has a symlink component", errors)
    custody = None if not decision_commit else _decision_custody(decision, supplied, raw, decision_commit)
    return decision, custody, errors


def _artifact_record(path: Path, relative: str) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": relative, "byte_length": len(data), "sha256": sha256_bytes(data)}


def _check_artifact_record(
    record: Any, path: Path, relative: str, label: str, errors: list[str],
) -> None:
    if not isinstance(record, dict):
        errors.append(f"{label}: artifact record is not an object")
        return
    try:
        expected = _artifact_record(path, relative)
    except OSError as exc:
        errors.append(f"{label}: cannot read artifact: {exc}")
        return
    _exact(record, expected, label, errors)


def _load_json_artifact(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    _validate_regular_file(path, label, errors)
    try:
        value = decode_canonical_json(path.read_bytes())
    except Exception as exc:
        errors.append(f"{label}: invalid canonical JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: JSON root is not an object")
        return None
    document_errors = validate_artifact_document(value)
    errors.extend(f"{label}: {error}" for error in document_errors)
    if document_errors:
        return None
    return value


def _load_jsonl_artifact(
    path: Path,
    label: str,
    errors: list[str],
    *,
    index_field: str = "candidate_index",
) -> list[dict[str, Any]] | None:
    _validate_regular_file(path, label, errors)
    try:
        values = decode_canonical_jsonl(path.read_bytes())
    except Exception as exc:
        errors.append(f"{label}: invalid canonical JSONL: {exc}")
        return None
    if not all(isinstance(value, dict) for value in values):
        errors.append(f"{label}: JSONL contains a non-object")
        return None
    invalid = False
    for index, value in enumerate(values):
        document_errors = validate_artifact_document(value)
        errors.extend(f"{label}[{index}]: {error}" for error in document_errors)
        invalid = invalid or bool(document_errors)
    indices = [value.get(index_field) for value in values]
    if not all(isinstance(index, int) and not isinstance(index, bool) for index in indices):
        errors.append(f"{label}: {index_field} values are not integers")
        invalid = True
    elif indices != sorted(indices) or len(set(indices)) != len(indices):
        errors.append(f"{label}: {index_field} order is not strictly increasing")
        invalid = True
    return None if invalid else values


def _candidate_roots() -> tuple[str, str, int]:
    shell = b"BOX-0"
    shell_binding = len(shell).to_bytes(4, "big") + shell
    records = b"".join(
        v.to_bytes(8, "big") + x.to_bytes(8, "big") for _, v, x in box0_pairs()
    )
    raw_hash = sha256_bytes(records)
    shard = hashlib.sha256(
        b"P192-WCM-CANDIDATE-SHARD-v1\0" + shell_binding
        + (0).to_bytes(8, "big") + (262148).to_bytes(8, "big") + records
    ).digest()
    shell_root = hashlib.sha256(
        b"P192-WCM-SHELL-ROOT-v1\0" + shell_binding + (1).to_bytes(8, "big")
        + (0).to_bytes(8, "big") + (262148).to_bytes(8, "big") + shard
    ).hexdigest()
    return raw_hash, shard.hex(), shell_root


def _disposition_roots(data: bytes) -> tuple[str, str, str]:
    shell = b"BOX-0"
    shell_binding = len(shell).to_bytes(4, "big") + shell
    raw_hash = sha256_bytes(data)
    shard = hashlib.sha256(
        b"P192-WCM-DISPOSITION-SHARD-v1\0" + shell_binding
        + (0).to_bytes(8, "big") + (0).to_bytes(8, "big")
        + (262148).to_bytes(8, "big") + data
    ).digest()
    shell_root = hashlib.sha256(
        b"P192-WCM-DISPOSITION-SHELL-ROOT-v1\0" + shell_binding
        + (1).to_bytes(8, "big") + (0).to_bytes(8, "big")
        + (0).to_bytes(8, "big") + (262148).to_bytes(8, "big") + shard
    ).hexdigest()
    return raw_hash, shard.hex(), shell_root


def _parse_framed_stream(
    data: bytes, stream_name: str, errors: list[str],
) -> dict[str, str]:
    domain = f"P192-WCM-BOX0-SUPERVISOR-{stream_name.upper()}-v1".encode("ascii") + b"\0"
    if not data.startswith(domain):
        errors.append(f"{stream_name}.log: domain prefix differs")
        return {}
    offset = len(domain)
    if len(data) - offset < 4:
        errors.append(f"{stream_name}.log: missing frame count")
        return {}
    count = int.from_bytes(data[offset:offset + 4], "big")
    offset += 4
    _exact(count, len(SUPERVISOR_CHILDREN), f"{stream_name}.log frame count", errors)
    hashes: dict[str, str] = {}
    for expected in SUPERVISOR_CHILDREN:
        if len(data) - offset < 4:
            errors.append(f"{stream_name}.log: truncated role length")
            return hashes
        role_length = int.from_bytes(data[offset:offset + 4], "big")
        offset += 4
        if len(data) - offset < role_length + 8:
            errors.append(f"{stream_name}.log: truncated role frame")
            return hashes
        try:
            role = data[offset:offset + role_length].decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{stream_name}.log: role is not UTF-8")
            return hashes
        offset += role_length
        length = int.from_bytes(data[offset:offset + 8], "big")
        offset += 8
        if len(data) - offset < length:
            errors.append(f"{stream_name}.log: truncated stream bytes")
            return hashes
        payload = data[offset:offset + length]
        offset += length
        _exact(role, expected["role"], f"{stream_name}.log role order", errors)
        hashes[role] = sha256_bytes(payload)
    if offset != len(data):
        errors.append(f"{stream_name}.log: trailing bytes")
    return hashes


def _binding_values_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol_commit": candidate["protocol_commit"],
        "producer_commit": candidate["producer_commit"],
        "producer_binary_sha256": candidate["producer_binary_sha256"],
        "factor_base_source_commit": candidate["factor_base_source_commit"],
        "factor_base_sha256": candidate["factor_base_sha256"],
        "shell_id": candidate["shell_id"],
        "candidate_shell_sha256": candidate["candidate_shell_sha256"],
        "disposition_shell_sha256": candidate["disposition"]["shell_sha256"],
        "disposition_schema_sha256": candidate["disposition_schema"]["sha256"],
        "status_counts_sha256": sha256_bytes(canonical_json_bytes(candidate["status_counts"])),
        "retained_candidates_sha256": candidate["retained_candidates"]["artifact"]["sha256"],
        "complete_relations_sha256": candidate["complete_relations"]["artifact"]["sha256"],
        "partial_relations_sha256": candidate["partial_relations"]["artifact"]["sha256"],
        "checkpoint_chain_sha256": candidate["checkpoint_chain"]["artifact"]["sha256"],
    }


def _failure_count_source(run_dir: Path, errors: list[str]) -> tuple[int, int]:
    sources: list[tuple[str, int, int]] = []
    disposition_path = run_dir / "disposition.bin"
    try:
        metadata = os.lstat(disposition_path)
        if stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            counts = parse_disposition_bytes(disposition_path.read_bytes())
            sources.append(("disposition.bin", counts["invalid"], counts["unresolved"]))
    except (OSError, ValueError):
        pass
    candidate_path = run_dir / "candidate-stream.json"
    try:
        metadata = os.lstat(candidate_path)
        if stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            candidate = decode_canonical_json(candidate_path.read_bytes())
            if isinstance(candidate, dict) and not validate_artifact_document(candidate):
                counts = candidate["status_counts"]
                sources.append(("candidate-stream.json", counts["invalid"], counts["unresolved"]))
    except (KeyError, OSError, TypeError, ValueError):
        pass
    if not sources:
        return 0, 0
    expected = sources[0][1:]
    for name, invalid, unresolved in sources[1:]:
        _exact((invalid, unresolved), expected, f"failure terminal counts from {name}", errors)
    return expected


def _terminal_failure_expectation(
    raw: dict[str, Any], invalid: int, unresolved: int,
    incomplete_artifact: bool = False,
) -> tuple[str, str, str]:
    if invalid > 0:
        return "FAIL", "canonical_producer", "invalid_disposition"
    if unresolved > 0:
        return "INCOMPLETE", "canonical_producer", "unresolved_disposition"
    if incomplete_artifact:
        return "INCOMPLETE", raw.get("failed_phase"), "incomplete_child_artifact"
    reason = raw.get("failure_reason")
    if reason == "incomplete_child_artifact":
        return "INCOMPLETE", raw.get("failed_phase"), reason
    return "FAIL", raw.get("failed_phase"), reason


def _schema_valid_completed_artifact(
    run_dir: Path, relative: str, decision: dict[str, Any],
) -> bool:
    path = run_dir / relative
    try:
        metadata = os.lstat(path)
        if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            return False
        data = path.read_bytes()
        if relative == "disposition.bin":
            parse_disposition_details(data)
            return True
        if relative == "command.txt":
            return decode_canonical_json(data) == decision["supervisor_argv"]
        if relative in {"stdout.log", "stderr.log"}:
            stream_errors: list[str] = []
            _parse_framed_stream(data, relative.removesuffix(".log"), stream_errors)
            return not stream_errors
        if relative.endswith(".jsonl"):
            rows = decode_canonical_jsonl(data)
            if not all(isinstance(row, dict) and not validate_artifact_document(row) for row in rows):
                return False
            indices = [row.get("candidate_index") for row in rows]
            return indices == sorted(indices) and len(set(indices)) == len(indices)
        if relative.endswith(".json"):
            document = decode_canonical_json(data)
            return isinstance(document, dict) and not validate_artifact_document(document)
    except (OSError, TypeError, ValueError):
        return False
    return False


def validate_post_run(
    run_dir: Path, decision: dict[str, Any], custody: dict[str, Any],
) -> list[str]:
    """Validate a complete Role-2 directory against raw bytes and its decision."""
    errors: list[str] = []
    try:
        entries = list(os.scandir(run_dir))
    except OSError as exc:
        return [f"post-run inventory unavailable: {exc}"]
    for entry in entries:
        if entry.is_symlink():
            errors.append(f"post-run path is a symlink: {entry.name}")
    raw_path = run_dir / "raw-result.json"
    raw_result = _load_json_artifact(raw_path, "raw-result.json", errors)
    if raw_result is None:
        return errors
    if raw_result.get("schema") == "p192-wcm-role2-box0-failure-v1":
        recognized = set(MANIFEST_ARTIFACT_PATHS) | {"manifest.yaml"}
        unknown = sorted(entry.name for entry in entries if entry.name not in recognized)
        if unknown:
            errors.append(f"failure directory contains unknown paths: {unknown}")
        _exact(raw_result.get("decision_custody"), custody, "failure decision custody", errors)
        for field in (
            "protocol_commit", "factor_base_source_commit", "producer_commit",
            "verifier_commit", "supervisor_commit",
        ):
            _exact(raw_result.get(field), decision.get(field), f"failure {field}", errors)
        _exact(raw_result.get("run_dir"), str(run_dir), "failure run_dir", errors)
        invalid, unresolved = _failure_count_source(run_dir, errors)
        _exact(raw_result.get("invalid_count"), invalid, "failure invalid count", errors)
        _exact(raw_result.get("unresolved_count"), unresolved, "failure unresolved count", errors)
        actual_completed: list[dict[str, Any]] = []
        for relative in MANIFEST_ARTIFACT_PATHS:
            if relative == "raw-result.json":
                continue
            path = run_dir / relative
            if _schema_valid_completed_artifact(run_dir, relative, decision):
                actual_completed.append(_artifact_record(path, relative))
        completed_paths = {record["path"] for record in actual_completed}
        required_paths = FAILURE_PHASE_REQUIRED_PATHS.get(raw_result.get("failed_phase"), [])
        incomplete_artifact = any(path not in completed_paths for path in required_paths)
        expected_status, expected_phase, expected_reason = _terminal_failure_expectation(
            raw_result, invalid, unresolved, incomplete_artifact,
        )
        _exact(raw_result.get("status"), expected_status, "failure terminal status", errors)
        _exact(raw_result.get("failed_phase"), expected_phase, "failure phase", errors)
        _exact(raw_result.get("failure_reason"), expected_reason, "failure reason", errors)
        _exact(raw_result.get("completed_artifacts"), actual_completed, "failure completed artifacts", errors)
        _require(not (run_dir / "manifest.yaml").exists(), "failure directory must not contain manifest.yaml", errors)
        return errors

    expected_names = set(STAGE_PATHS + CUSTODY_PATHS)
    actual_names = {entry.name for entry in entries}
    _exact(actual_names, expected_names, "PASS final directory path set", errors)
    if actual_names != expected_names:
        return errors
    for relative in STAGE_PATHS + CUSTODY_PATHS:
        _validate_regular_file(run_dir / relative, f"PASS path {relative}", errors)
    if errors:
        return errors

    disposition_schema = _load_json_artifact(run_dir / "disposition-schema.json", "disposition-schema.json", errors)
    candidate = _load_json_artifact(run_dir / "candidate-stream.json", "candidate-stream.json", errors)
    producer_verification = _load_json_artifact(run_dir / "verification.json", "verification.json", errors)
    independent_verification = _load_json_artifact(run_dir / "independent-verification.json", "independent-verification.json", errors)
    restart = _load_json_artifact(run_dir / "checkpoint-resume-control.json", "checkpoint-resume-control.json", errors)
    agreement = _load_json_artifact(run_dir / "independent-agreement.json", "independent-agreement.json", errors)
    audit = _load_json_artifact(run_dir / "dependency-audit.json", "dependency-audit.json", errors)
    receipt = _load_json_artifact(run_dir / "independent-verifier-receipt.json", "independent-verifier-receipt.json", errors)
    environment = _load_json_artifact(run_dir / "environment.json", "environment.json", errors)
    success_raw = raw_result
    manifest = _load_json_artifact(run_dir / "manifest.yaml", "manifest.yaml", errors)
    retained = _load_jsonl_artifact(run_dir / "retained-candidates.jsonl", "retained-candidates.jsonl", errors)
    complete = _load_jsonl_artifact(run_dir / "complete-relations.jsonl", "complete-relations.jsonl", errors)
    partial = _load_jsonl_artifact(run_dir / "partial-relations.jsonl", "partial-relations.jsonl", errors)
    checkpoints = _load_jsonl_artifact(
        run_dir / "checkpoint-chain.jsonl",
        "checkpoint-chain.jsonl",
        errors,
        index_field="shard_index",
    )
    required_documents = (
        disposition_schema, candidate, producer_verification, independent_verification,
        restart, agreement, audit, receipt, environment, manifest, retained, complete,
        partial, checkpoints,
    )
    if any(document is None for document in required_documents):
        return errors
    assert disposition_schema is not None and candidate is not None
    assert producer_verification is not None and independent_verification is not None
    assert restart is not None and agreement is not None and audit is not None
    assert receipt is not None and environment is not None and manifest is not None
    assert retained is not None and complete is not None and partial is not None and checkpoints is not None

    try:
        disposition_bytes = (run_dir / "disposition.bin").read_bytes()
        status_counts, statuses, disposition_hashes = parse_disposition_details(disposition_bytes)
    except Exception as exc:
        errors.append(f"disposition.bin: {exc}")
        return errors
    _exact(candidate.get("status_counts"), status_counts, "candidate/disposition status counts", errors)
    _exact(status_counts.get("invalid"), 0, "PASS invalid count", errors)
    _exact(status_counts.get("unresolved"), 0, "PASS unresolved count", errors)
    for index, v, x in box0_pairs():
        primitive = math.gcd(abs((x - TRACE_T * v) // 2), v) == 1
        if (statuses[index] == 0) == primitive:
            errors.append(f"disposition primitivity mismatch at candidate {index}")
            break
    candidate_raw, candidate_shard, candidate_shell = _candidate_roots()
    disposition_raw, disposition_shard, disposition_shell = _disposition_roots(disposition_bytes)
    shard = candidate["candidate_shards"][0]
    _exact(shard.get("records_sha256"), candidate_raw, "candidate raw shard hash", errors)
    _exact(shard.get("candidate_shard_sha256"), candidate_shard, "candidate domain shard hash", errors)
    _exact(candidate.get("candidate_shell_sha256"), candidate_shell, "candidate shell root", errors)
    disposition_entry = candidate["disposition"]
    _exact(disposition_entry["shards"][0].get("records_sha256"), disposition_raw, "disposition raw shard hash", errors)
    _exact(disposition_entry["shards"][0].get("disposition_shard_sha256"), disposition_shard, "disposition domain shard hash", errors)
    _exact(disposition_entry.get("shell_sha256"), disposition_shell, "disposition shell root", errors)
    _check_artifact_record(candidate["disposition_schema"], run_dir / "disposition-schema.json", "disposition-schema.json", "candidate disposition schema", errors)
    _check_artifact_record(disposition_entry["artifact"], run_dir / "disposition.bin", "disposition.bin", "candidate disposition artifact", errors)
    for key, relative in (
        ("retained_candidates", "retained-candidates.jsonl"),
        ("complete_relations", "complete-relations.jsonl"),
        ("partial_relations", "partial-relations.jsonl"),
        ("checkpoint_chain", "checkpoint-chain.jsonl"),
    ):
        _check_artifact_record(candidate[key]["artifact"], run_dir / relative, relative, f"candidate {key}", errors)

    expected_retained = [index for index, status in enumerate(statuses) if status in (1, 2, 3)]
    expected_complete = [index for index, status in enumerate(statuses) if status == 1]
    expected_partial = [index for index, status in enumerate(statuses) if status in (2, 3)]
    _exact([row["candidate_index"] for row in retained], expected_retained, "retained membership", errors)
    _exact([row["candidate_index"] for row in complete], expected_complete, "complete relation membership", errors)
    _exact([row["candidate_index"] for row in partial], expected_partial, "partial relation membership", errors)
    retained_by_index = {row["candidate_index"]: row for row in retained}
    for row in retained:
        expected_hashes = disposition_hashes.get(row["candidate_index"])
        _exact(
            (row.get("candidate_certificate_sha256"), row.get("factorization_certificate_sha256")),
            expected_hashes, f"retained/disposition hashes {row['candidate_index']}", errors,
        )
        _exact(row.get("status"), statuses[row["candidate_index"]], f"retained status {row['candidate_index']}", errors)
    for label, rows in (("complete", complete), ("partial", partial)):
        for row in rows:
            source = retained_by_index.get(row["candidate_index"], {})
            _exact(row.get("candidate_id"), source.get("candidate_id"), f"{label}/retained candidate id", errors)
            _exact(row.get("candidate_certificate_sha256"), source.get("candidate_certificate_sha256"), f"{label}/retained candidate hash", errors)
            _exact(row.get("factorization_certificate_sha256"), source.get("factorization_certificate_sha256"), f"{label}/retained factorization hash", errors)

    _exact(len(checkpoints), 1, "checkpoint line count", errors)
    if len(checkpoints) == 1:
        checkpoint = checkpoints[0]
        _exact(checkpoint.get("protocol_commit"), decision["protocol_commit"], "checkpoint protocol commit", errors)
        _exact(checkpoint.get("producer_commit"), decision["producer_commit"], "checkpoint producer commit", errors)
        _exact(checkpoint.get("producer_binary_sha256"), decision["producer_binary_sha256"], "checkpoint producer binary", errors)
        _exact(checkpoint.get("factor_base_sha256"), candidate["factor_base_sha256"], "checkpoint factor base", errors)
        _exact(checkpoint.get("candidate_shard_sha256"), candidate_shard, "checkpoint candidate shard", errors)
        _exact(checkpoint.get("disposition_shard_sha256"), disposition_shard, "checkpoint disposition shard", errors)
        counters = checkpoint.get("phase_counters", {})
        expected_counters = {
            "seen": "262148", "primitive": "168990", "duplicate": "93158",
            "complete": str(status_counts["complete"]),
            "one_lp": str(status_counts["one_large_prime"]),
            "two_lp": str(status_counts["two_large_prime"]),
            "rejected": str(status_counts["rejected"]),
            "invalid": str(status_counts["invalid"]),
            "unresolved": str(status_counts["unresolved"]),
        }
        _exact(counters, expected_counters, "checkpoint/status counters", errors)
        for relative in APPEND_PATHS:
            data = (run_dir / relative).read_bytes()
            expected_prefix = {"byte_length": str(len(data)), "prefix_sha256": sha256_bytes(data)}
            _exact(checkpoint["committed_outputs"].get(relative), expected_prefix, f"checkpoint prefix {relative}", errors)

    predecessor = Path(decision["paths"]["predecessor_dir"])
    predecessor_error_count = len(errors)
    for relative in PREDECESSOR_PATHS:
        _validate_regular_file(predecessor / relative, f"post-run predecessor {relative}", errors)
    if len(errors) != predecessor_error_count:
        return errors
    predecessor_records = candidate["predecessor"]
    predecessor_fields = (
        ("factor_base", "factor-base.json"),
        ("factor_base_sidecar", "factor-base.sha256"),
        ("producer_verification", "verification.json"),
        ("independent_verification", "independent-verification.json"),
        ("independent_agreement", "independent-agreement.json"),
        ("supervisor_receipt", "independent-verifier-receipt.json"),
    )
    _exact(predecessor_records.get("run_id"), decision["predecessor_run_id"], "candidate predecessor run id", errors)
    for field, relative in predecessor_fields:
        _check_artifact_record(predecessor_records[field], predecessor / relative, relative, f"candidate predecessor {field}", errors)
    try:
        factor_base = decode_canonical_json((predecessor / "factor-base.json").read_bytes())
        _exact(factor_base.get("source_commit"), decision["factor_base_source_commit"], "predecessor factor-base source commit", errors)
        sidecar = (predecessor / "factor-base.sha256").read_bytes()
        expected_sidecar = f'{sha256_path(predecessor / "factor-base.json")}  factor-base.json\n'.encode("ascii")
        _exact(sidecar, expected_sidecar, "predecessor factor-base sidecar", errors)
        for name in ("verification.json", "independent-verification.json", "independent-agreement.json", "independent-verifier-receipt.json"):
            predecessor_doc = decode_canonical_json((predecessor / name).read_bytes())
            _exact(predecessor_doc.get("overall_status"), "PASS", f"predecessor {name} status", errors)
            _exact(predecessor_doc.get("protocol_commit"), decision["protocol_commit"], f"predecessor {name} protocol commit", errors)
            _exact(predecessor_doc.get("source_commit"), decision["factor_base_source_commit"], f"predecessor {name} source commit", errors)
    except Exception as exc:
        errors.append(f"predecessor canonical replay failed: {exc}")

    for field in ("protocol_commit", "producer_commit", "producer_binary_sha256", "factor_base_source_commit", "factor_base_sha256", "shell_id"):
        _exact(candidate.get(field), disposition_schema.get(field), f"candidate/disposition-schema {field}", errors)
    for field in ("protocol_commit", "producer_commit", "factor_base_source_commit"):
        _exact(candidate.get(field), decision.get(field), f"candidate/decision {field}", errors)
    _exact(candidate.get("producer_binary_sha256"), decision["producer_binary_sha256"], "candidate producer binary", errors)
    _exact(candidate.get("factor_base_sha256"), sha256_path(predecessor / "factor-base.json"), "candidate factor base hash", errors)
    bindings = _binding_values_from_candidate(candidate)
    _exact(producer_verification.get("bindings"), bindings, "producer verification bindings", errors)
    _exact(independent_verification.get("bindings"), bindings, "independent verification bindings", errors)
    _exact(producer_verification.get("overall_status"), "PASS", "producer verification status", errors)
    _exact(independent_verification.get("overall_status"), "PASS", "independent verification status", errors)
    _exact(independent_verification.get("verifier_commit"), decision["verifier_commit"], "independent verifier commit", errors)
    _exact(independent_verification.get("verifier_binary_sha256"), decision["verifier_binary_sha256"], "independent verifier binary", errors)
    for item in producer_verification.get("artifacts", []):
        _check_artifact_record(item, run_dir / item["path"], item["path"], "producer verification artifact", errors)
    for item in independent_verification.get("source_artifacts", []):
        _check_artifact_record(item, run_dir / item["path"], item["path"], "independent source artifact", errors)

    _exact(agreement.get("producer_verification_sha256"), sha256_path(run_dir / "verification.json"), "agreement producer verification hash", errors)
    _exact(agreement.get("independent_verification_sha256"), sha256_path(run_dir / "independent-verification.json"), "agreement independent verification hash", errors)
    _exact(agreement.get("overall_status"), "PASS", "agreement status", errors)
    agreement_map = {row["field"]: row for row in agreement.get("comparisons", [])}
    for field, expected in bindings.items():
        row = agreement_map.get(field, {})
        _exact((row.get("producer"), row.get("verifier"), row.get("equal")), (str(expected), str(expected), True), f"agreement binding {field}", errors)

    _exact(restart.get("fault_argv"), decision["producer_fault_argv"], "restart fault argv", errors)
    _exact(restart.get("resume_argv"), decision["producer_resume_argv"], "restart resume argv", errors)
    _exact(restart.get("overall_status"), "PASS", "restart status", errors)
    for field in (
        "protocol_commit", "producer_commit", "producer_binary_sha256",
        "factor_base_source_commit",
    ):
        _exact(restart.get(field), decision[field], f"restart/decision {field}", errors)
    _exact(restart.get("factor_base_sha256"), candidate["factor_base_sha256"], "restart factor base", errors)
    _exact(restart.get("shell_id"), candidate["shell_id"], "restart shell", errors)
    for comparison in restart.get("comparisons", []):
        relative = comparison["field"]
        actual_hash = sha256_path(run_dir / relative)
        _exact((comparison.get("fresh_sha256"), comparison.get("resumed_sha256"), comparison.get("equal")), (actual_hash, actual_hash, True), f"restart comparison {relative}", errors)

    role_commits = {
        "producer": decision["producer_commit"],
        "verifier": decision["verifier_commit"],
        "supervisor": decision["supervisor_commit"],
    }
    recomputed_sources: dict[str, list[dict[str, str]]] = {}
    for role, commit in role_commits.items():
        git_record = audit.get(f"{role}_git", {})
        expected_git = {
            "git_head": commit,
            "git_top_level": decision["paths"][f"{role}_repository_path"],
            "package_root": decision["paths"][f"{role}_package_path"],
            "worktree_clean": True,
        }
        _exact(git_record, expected_git, f"dependency audit {role} Git binding", errors)
        repository = Path(expected_git["git_top_level"])
        package = Path(expected_git["package_root"])
        try:
            rows = _collect_rust_hash_rows(package)
            recomputed_sources[role] = rows
            _exact(audit.get(f"{role}_rust_sources"), rows, f"dependency audit {role} complete Rust inventory", errors)
            _validate_regular_file(package / "Cargo.toml", f"dependency audit {role} Cargo.toml", errors)
            _validate_regular_file(repository / "Cargo.lock", f"dependency audit {role} Cargo.lock", errors)
            cargo_toml_bytes = (package / "Cargo.toml").read_bytes()
            cargo_lock_bytes = (repository / "Cargo.lock").read_bytes()
            _exact(
                audit.get(f"{role}_cargo_toml_sha256"), sha256_bytes(cargo_toml_bytes),
                f"dependency audit {role} Cargo.toml hash", errors,
            )
            _exact(
                audit.get(f"{role}_cargo_lock_sha256"), sha256_bytes(cargo_lock_bytes),
                f"dependency audit {role} Cargo.lock hash", errors,
            )
            if role == "verifier":
                errors.extend(_verifier_dependency_errors(
                    cargo_toml_bytes,
                    cargo_lock_bytes,
                    package,
                    Path(decision["paths"]["producer_package_path"]),
                ))
                scanned = cargo_toml_bytes + b"\n" + b"\n".join(
                    (package / row["path"]).read_bytes() for row in rows
                )
                for marker in FORBIDDEN_VERIFIER_SOURCE_MARKERS:
                    _require(
                        marker not in scanned,
                        f"dependency audit verifier contains forbidden source marker {marker.decode('ascii')}",
                        errors,
                    )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"dependency audit {role} source recomputation failed: {exc}")
    if set(recomputed_sources) == set(role_commits):
        producer_hashes = {row["sha256"] for row in recomputed_sources["producer"]}
        verifier_hashes = {row["sha256"] for row in recomputed_sources["verifier"]}
        _require(
            producer_hashes.isdisjoint(verifier_hashes),
            "dependency audit hides identical producer/verifier Rust source hashes", errors,
        )
    producer_source_root = Path(decision["paths"]["producer_package_path"]) / "src"
    verifier_source_root = Path(decision["paths"]["verifier_package_path"]) / "src"
    try:
        expected_clone_screen = compute_source_clone_screen(producer_source_root, verifier_source_root)
        _exact(
            audit.get("source_clone_screen"), expected_clone_screen,
            "dependency audit independently recomputed source clone screen", errors,
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        errors.append(f"dependency audit source clone recomputation failed: {exc}")

    _exact(receipt.get("decision_id"), decision["decision_id"], "receipt decision id", errors)
    _exact(receipt.get("decision_custody"), custody, "receipt decision custody", errors)
    _exact(receipt.get("run_id"), decision["run_id"], "receipt run id", errors)
    for field in ("protocol_commit", "factor_base_source_commit", "producer_commit", "verifier_commit", "supervisor_commit", "supervisor_binary_sha256"):
        _exact(receipt.get(field), decision.get(field), f"receipt/decision {field}", errors)
    predecessor_inventory = [_artifact_record(predecessor / path, path) for path in PREDECESSOR_PATHS]
    producer_inventory = [_artifact_record(run_dir / path, path) for path in PRODUCER_PATHS]
    _exact(receipt.get("predecessor_artifacts_before"), predecessor_inventory, "receipt predecessor before", errors)
    _exact(receipt.get("predecessor_artifacts_after"), predecessor_inventory, "receipt predecessor after", errors)
    _exact(receipt.get("producer_artifacts_before_verifier"), producer_inventory, "receipt producer before", errors)
    _exact(receipt.get("producer_artifacts_after_verifier"), producer_inventory, "receipt producer after", errors)
    expected_children = (
        ("canonical_producer", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fresh_argv"], 0),
        ("checkpoint_fault_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fault_argv"], 75),
        ("checkpoint_resume_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_resume_argv"], 0),
        ("isolated_independent_verifier", decision["verifier_binary_sha256"], decision["verifier_commit"], decision["independent_verifier_argv"], 0),
    )
    stdout_hashes = _parse_framed_stream((run_dir / "stdout.log").read_bytes(), "stdout", errors)
    stderr_hashes = _parse_framed_stream((run_dir / "stderr.log").read_bytes(), "stderr", errors)
    for child, expected in zip(receipt.get("children", []), expected_children):
        role, binary_hash, commit, argv, exit_code = expected
        _exact(child.get("role"), role, "receipt child role", errors)
        _exact(child.get("binary_sha256"), binary_hash, f"receipt child binary {role}", errors)
        _exact(child.get("commit"), commit, f"receipt child commit {role}", errors)
        _exact(child.get("argv"), argv, f"receipt child argv {role}", errors)
        _exact((child.get("expected_exit_code"), child.get("observed_exit_code")), (exit_code, exit_code), f"receipt child exit {role}", errors)
        _exact(child.get("stdout_sha256"), stdout_hashes.get(role), f"receipt child stdout {role}", errors)
        _exact(child.get("stderr_sha256"), stderr_hashes.get(role), f"receipt child stderr {role}", errors)
    _exact(receipt.get("checkpoint_resume_control_sha256"), sha256_path(run_dir / "checkpoint-resume-control.json"), "receipt restart hash", errors)
    _exact(receipt.get("independent_agreement_sha256"), sha256_path(run_dir / "independent-agreement.json"), "receipt agreement hash", errors)
    _exact(receipt.get("independent_verification_sha256"), sha256_path(run_dir / "independent-verification.json"), "receipt independent verification hash", errors)
    _exact(receipt.get("dependency_audit_sha256"), sha256_path(run_dir / "dependency-audit.json"), "receipt audit hash", errors)
    _exact(receipt.get("overall_status"), "PASS", "receipt status", errors)

    _exact(environment.get("decision_custody"), custody, "environment decision custody", errors)
    for field in ("protocol_commit", "factor_base_source_commit", "producer_commit", "verifier_commit", "supervisor_commit", "producer_binary_sha256", "verifier_binary_sha256", "supervisor_binary_sha256"):
        _exact(environment.get(field), decision.get(field), f"environment/decision {field}", errors)
    _exact(success_raw.get("decision_custody"), custody, "raw-result decision custody", errors)
    for field in ("protocol_commit", "factor_base_source_commit", "producer_commit", "verifier_commit", "supervisor_commit"):
        _exact(success_raw.get(field), decision.get(field), f"raw-result/decision {field}", errors)
    _exact(success_raw.get("run_id"), decision["run_id"], "raw-result run id", errors)
    _exact(success_raw.get("run_dir"), str(run_dir), "raw-result run_dir", errors)
    _exact(success_raw.get("candidate_stream_sha256"), sha256_path(run_dir / "candidate-stream.json"), "raw-result candidate hash", errors)
    _exact(success_raw.get("checkpoint_resume_control_sha256"), sha256_path(run_dir / "checkpoint-resume-control.json"), "raw-result restart hash", errors)
    _exact(success_raw.get("agreement_sha256"), sha256_path(run_dir / "independent-agreement.json"), "raw-result agreement hash", errors)
    _exact(success_raw.get("audit_sha256"), sha256_path(run_dir / "dependency-audit.json"), "raw-result audit hash", errors)
    _exact(success_raw.get("receipt_sha256"), sha256_path(run_dir / "independent-verifier-receipt.json"), "raw-result receipt hash", errors)

    try:
        command = decode_canonical_json((run_dir / "command.txt").read_bytes())
        _exact(command, decision["supervisor_argv"], "command/supervisor argv", errors)
    except Exception as exc:
        errors.append(f"command.txt: {exc}")
    run = manifest.get("run", {})
    _exact(run.get("id"), decision["run_id"], "manifest run id", errors)
    _exact(run.get("code", {}).get("repository"), decision["paths"]["supervisor_repository_path"], "manifest supervisor repository", errors)
    _exact(run.get("code", {}).get("commit"), decision["supervisor_commit"], "manifest supervisor commit", errors)
    _exact(run.get("code", {}).get("supervisor_binary_sha256"), decision["supervisor_binary_sha256"], "manifest supervisor binary", errors)
    _exact(run.get("environment", {}).get("sha256"), sha256_path(run_dir / "environment.json"), "manifest environment hash", errors)
    parameters = run.get("inputs", {}).get("parameters", {})
    _exact(parameters.get("predecessor_run_id"), decision["predecessor_run_id"], "manifest predecessor id", errors)
    _exact(parameters.get("factor_base_sha256"), candidate["factor_base_sha256"], "manifest factor base hash", errors)
    _exact(parameters.get("decision_id"), decision["decision_id"], "manifest decision id", errors)
    _exact(parameters.get("decision_commit"), custody["decision_commit"], "manifest decision commit", errors)
    _exact(parameters.get("decision_sha256"), custody["decision_sha256"], "manifest decision hash", errors)
    _exact(run.get("result", {}).get("certificate", {}).get("sha256"), sha256_path(run_dir / "candidate-stream.json"), "manifest certificate hash", errors)
    expected_manifest_inventory = [_artifact_record(run_dir / path, path) for path in MANIFEST_ARTIFACT_PATHS]
    _exact(run.get("artifacts"), expected_manifest_inventory, "manifest artifact inventory", errors)
    return errors


def collect_contract_errors(addendum_doc: Any, overlay: Any) -> list[str]:
    errors: list[str] = []
    addendum = addendum_doc.get("role2_box0_interface_addendum", {})
    _exact(addendum.get("schema"), "p192-wcm-role2-box0-interface-addendum-v1", "addendum schema", errors)
    _exact(addendum.get("execution_authorized"), False, "addendum authorization", errors)
    _exact(addendum.get("scientific_status"), "not_started", "scientific status", errors)
    _exact(addendum.get("result_status"), "no_result", "result status", errors)
    _exact(addendum.get("scientific_results"), [], "scientific results", errors)

    stage = addendum.get("stage_binding", {})
    _exact(stage.get("producer_argv_template"), PRODUCER_TEMPLATE, "producer argv", errors)
    _exact(stage.get("independent_verifier_argv_template"), VERIFIER_TEMPLATE, "verifier argv", errors)
    _exact(stage.get("checkpoint_fault_argv_template"), FAULT_TEMPLATE, "fault argv", errors)
    _exact(stage.get("checkpoint_resume_argv_template"), RESUME_TEMPLATE, "resume argv", errors)
    _exact(stage.get("supervisor_argv_template"), SUPERVISOR_TEMPLATE, "supervisor argv", errors)

    shell = addendum.get("shell_contract", {})
    total, primitive, duplicate = box0_counts()
    _exact((total, primitive, duplicate), (262148, 168990, 93158), "computed BOX-0 counts", errors)
    _exact((shell.get("candidate_count"), shell.get("primitive_count"), shell.get("duplicate_count")), (total, primitive, duplicate), "declared BOX-0 counts", errors)
    boundaries = [{"candidate_index": i, "v": v, "x": x} for i, v, x in box0_pairs() if i in {0, 32767, 32768, 65536, 229379, 262147}]
    _exact(shell.get("literal_boundary_records"), boundaries, "BOX-0 boundary records", errors)
    _exact(shell.get("shard_count"), 1, "BOX-0 shard count", errors)

    _exact(addendum.get("checkpoint_and_resume", {}).get("append_paths_in_order"), APPEND_PATHS, "append paths", errors)
    _exact(addendum.get("checkpoint_and_resume", {}).get("recognized_temporary_paths_in_order"), TEMPORARY_PATHS, "temporary paths", errors)
    _exact(
        addendum.get("protected_protocol_paths_in_order"),
        list(PROTECTED_PROTOCOL_RELATIVE_PATHS.values()),
        "protected protocol paths", errors,
    )
    _exact(addendum.get("producer_owned_paths_in_order"), PRODUCER_PATHS, "producer paths", errors)
    _exact(addendum.get("verifier_source_paths_in_order"), PRODUCER_PATHS, "verifier source paths", errors)
    _exact(addendum.get("supervisor_owned_paths_in_order"), SUPERVISOR_PATHS, "supervisor paths", errors)
    _exact(addendum.get("canonical_run_custody_paths_in_order"), CUSTODY_PATHS, "custody paths", errors)
    _exact(addendum.get("exact_role2_stage_paths_in_order"), STAGE_PATHS, "Role-2 stage paths", errors)
    _exact(addendum.get("canonical_v2_custody", {}).get("manifest_artifact_paths_in_order"), MANIFEST_ARTIFACT_PATHS, "manifest artifact paths", errors)
    _exact(addendum.get("producer_verification_checks_in_order"), PRODUCER_CHECKS, "producer checks", errors)
    _exact(addendum.get("independent_verifier_checks_in_order"), INDEPENDENT_CHECKS, "independent checks", errors)
    _exact(addendum.get("agreement_fields_in_order"), AGREEMENT_FIELDS, "agreement fields", errors)
    _exact(addendum.get("supervisor_child_receipts_in_order"), SUPERVISOR_CHILDREN, "supervisor children", errors)
    restart = addendum.get("checkpoint_restart_control", {})
    _exact(restart.get("injected_suffix_hex"), "503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100", "restart suffix", errors)
    if "source_identity_preservation" not in addendum.get("predecessor_binding", {}):
        errors.append("immutable producer/factor-base source identity preservation is missing")
    admission_text = " ".join(str(item) for item in addendum.get("admission_gates", []))
    if "Role-2 producer provenance, and Role-2 verifier provenance are separately hash-bound and may name distinct clean commits" in admission_text:
        errors.append("admission gate permits forbidden producer/factor-base commit separation")
    terminal = addendum.get("terminal_status_semantics", {})
    if "failure_precedence_and_reason" not in terminal:
        errors.append("deterministic terminal failure precedence is missing")

    _exact(overlay.get("execution_authorized"), False, "overlay authorization", errors)
    _exact(overlay.get("scientific_results"), [], "overlay scientific results", errors)
    _exact(overlay.get("producer_argv_template"), PRODUCER_TEMPLATE, "overlay producer argv", errors)
    _exact(overlay.get("independent_verifier_argv_template"), VERIFIER_TEMPLATE, "overlay verifier argv", errors)
    _exact(overlay.get("checkpoint_fault_argv_template"), FAULT_TEMPLATE, "overlay fault argv", errors)
    _exact(overlay.get("checkpoint_resume_argv_template"), RESUME_TEMPLATE, "overlay resume argv", errors)
    _exact(overlay.get("supervisor_argv_template"), SUPERVISOR_TEMPLATE, "overlay supervisor argv", errors)
    _exact(overlay.get("base_required_outputs"), BASE_REQUIRED_OUTPUTS, "overlay base outputs", errors)
    _exact(overlay.get("addendum_required_children"), ADDENDUM_CHILDREN, "overlay addendum outputs", errors)
    _exact(overlay.get("canonical_v2_custody_outputs"), CUSTODY_PATHS, "overlay custody paths", errors)
    return errors


def check_sums() -> list[str]:
    if not SUMS.exists():
        return ["SHA256SUMS is missing"]
    entries: dict[str, str] = {}
    errors: list[str] = []
    for line in SUMS.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append("malformed SHA256SUMS line")
            continue
        digest, relative = match.groups()
        if relative in entries:
            errors.append(f"duplicate SHA256SUMS entry: {relative}")
        entries[relative] = digest
    _exact(list(entries), list(PAYLOAD_PATHS), "SHA256SUMS path order", errors)
    for relative in PAYLOAD_PATHS:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing payload: {relative}")
        elif entries.get(relative) != sha256_path(path):
            errors.append(f"SHA256 mismatch: {relative}")
    return errors


def check_package() -> list[str]:
    errors: list[str] = []
    for relative, expected in IMMUTABLE.items():
        path = ROOT / relative
        if not path.is_file() or sha256_path(path) != expected:
            errors.append(f"immutable base hash mismatch: {relative}")
    addendum = load_yaml(ADDENDUM)
    overlay = load_yaml(OVERLAY)
    errors.extend(collect_contract_errors(addendum, overlay))
    for path in (ARTIFACT_SCHEMA, DECISION_SCHEMA):
        try:
            _schema_validator(load_json(path))
        except Exception as exc:  # jsonschema reports precise context.
            errors.append(f"invalid schema {path.name}: {exc}")
    errors.extend(check_sums())
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, help="exact committed Role-2 Coordinator decision")
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument("--pre-dispatch", action="store_true", help="validate decision and require fresh output paths")
    phase.add_argument("--post-run", action="store_true", help="validate decision plus a completed run directory")
    parser.add_argument("--run-dir", type=Path, help="exact completed run directory for --post-run")
    args = parser.parse_args(argv)
    if args.decision is None and (args.pre_dispatch or args.post_run or args.run_dir is not None):
        parser.error("phase and --run-dir require --decision")
    if args.decision is not None and not (args.pre_dispatch or args.post_run):
        parser.error("--decision requires exactly one of --pre-dispatch or --post-run")
    if args.post_run and args.run_dir is None:
        parser.error("--post-run requires --run-dir")
    if not args.post_run and args.run_dir is not None:
        parser.error("--run-dir is accepted only with --post-run")
    errors = check_package()
    if args.decision:
        decision, custody, decision_errors = validate_dispatch_decision(
            args.decision, "post-run" if args.post_run else "pre-dispatch", args.run_dir,
        )
        errors.extend(decision_errors)
        if args.post_run and decision is not None and custody is not None and not decision_errors:
            errors.extend(validate_post_run(args.run_dir, decision, custody))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    if args.pre_dispatch:
        print("PASS: committed Role-2 decision and fresh dispatch custody are closed")
    elif args.post_run:
        print("PASS: Role-2 post-run bytes and cross-document custody are closed")
    else:
        print("PASS: Role-2 BOX-0 interface is closed and execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
