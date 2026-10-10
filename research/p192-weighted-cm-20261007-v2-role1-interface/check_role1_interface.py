#!/usr/bin/env python3
"""Admission checker for the non-executing P-192 role-1 interface addendum.

The default mode binds the immutable v2 archive and validates the static
addendum.  Closed optional modes validate a fresh Coordinator decision before
dispatch or its resulting custody after completion.  No mode factors a norm,
runs a sieve, constructs a relation, or launches a native binary.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
ADDENDUM_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml"
OVERLAY_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/run-family.role1-interface.yaml"
SCHEMA_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json"
DECISION_SCHEMA_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-dispatch-decision.schema.json"
ADDENDUM_MANIFEST_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/SHA256SUMS"
SPEC_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml"
BASE_AMENDMENT_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml"
RUN_FAMILY_PATH = ROOT / "research/p192-weighted-cm-20261007-v2/run-family.yaml"
RECEIPT_PATH = ROOT / "coordination/p192-weighted-cm-20261007/archives/TASK-20261007-66d44b/snapshot-receipt.json"

ADDENDUM_PAYLOADS = {
    "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role1-interface/README.md",
    "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py",
    "research/p192-weighted-cm-20261007-v2-role1-interface/run-family.role1-interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json",
    "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-dispatch-decision.schema.json",
    "tests/test_p192_wcm_role1_interface.py",
}

BASE_HASHES = {
    "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml":
        "af43c91b9ab941158dd8a589fa6115f49b917b693f8cd1655f625e14a08611e8",
    "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml":
        "34fb190ff222a37f2a626d18ba26b3e710a96c2d6eb11a5ab12dd561a4317484",
    "research/p192-weighted-cm-20261007-v2/run-family.yaml":
        "4bbb9c81318dceeba93734fce50dd96574513afa0c31e8c9ea8f310d91e7c6d6",
}

ADDENDUM_RELATIVE = "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml"
INTERFACE_MANIFEST_RELATIVE = "research/p192-weighted-cm-20261007-v2-role1-interface/SHA256SUMS"
PROTECTED_PROTOCOL_PATHS = [
    "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml",
    "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml",
    ADDENDUM_RELATIVE,
    "research/p192-weighted-cm-20261007-v2/run-family.yaml",
    "research/p192-weighted-cm-20261007-v2-role1-interface/README.md",
    INTERFACE_MANIFEST_RELATIVE,
    "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py",
    "research/p192-weighted-cm-20261007-v2-role1-interface/run-family.role1-interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json",
    "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-dispatch-decision.schema.json",
    "tests/test_p192_wcm_role1_interface.py",
]
UNAUTHORIZED_STAGE_LABELS = [
    "P192-WCM-BOX0", "P192-WCM-BOX1-SHELL", "P192-WCM-BOX2-SHELL",
    "P192-WCM-RELATIONS", "P192-WCM-MAPS", "P192-WCM-HOLDOUT",
    "P192-WCM-REPLICATION",
]
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DECISION_ID_RE = re.compile(r"^DEC-[0-9]{8}-[0-9a-f]{6}$")
ROLE1_RUN_ID_RE = re.compile(r"^RUN-SCURVE-[0-9a-f]{6}$")

PRODUCER_ARGV = [
    "p192_weighted_cm", "preflight", "--curve", "p192",
    "--sieve-bound", "65521", "--map-bound", "113",
    "--large-prime-bound", "2147483647", "--positive-control", "D=-23",
    "--reference-shell", "REF-0", "--reference-v-max", "2",
    "--reference-x-max-inclusive", "1024", "--out", "RUN_DIR",
]
VERIFIER_ARGV = [
    "p192_weighted_cm_verify", "preflight", "--source", "RUN_DIR",
    "--out", "RUN_DIR/independent-verification.json",
]
SUPERVISOR_ARGV = [
    "SUPERVISOR_BIN", "--producer", "PRODUCER_BIN", "--verifier",
    "VERIFIER_BIN", "--producer-source", "PRODUCER_SOURCE",
    "--verifier-source", "VERIFIER_SOURCE", "--protocol-repository",
    "PROTOCOL_REPOSITORY", "--decision", "DECISION_PATH", "--run-dir",
    "RUN_DIR", "--protocol-commit", "PROTOCOL_COMMIT", "--source-commit",
    "SOURCE_COMMIT", "--verifier-commit", "VERIFIER_COMMIT", "--audit-out",
    "RUN_DIR/dependency-audit.json",
]
V2_OUTPUTS = [
    "identity.json", "maximal-order.json", "factor-base.json",
    "factor-base.sha256", "controls.json", "reference-box.json",
    "verification.json", "independent-verification.json",
    "independent-verifier-receipt.json",
]
CHILD_OUTPUTS = [
    "reference-box/candidate-records.bin",
    "reference-box/disposition.bin",
    "reference-box/certificates.bin",
    "independent-agreement.json",
    "dependency-audit.json",
]
CUSTODY_OUTPUTS = [
    "manifest.yaml", "command.txt", "environment.json", "stdout.log",
    "stderr.log", "raw-result.json",
]
CUSTODY_DESCRIPTION_ORDER = [
    "command.txt", "environment.json", "stdout.log", "stderr.log",
    "raw-result.json", "manifest.yaml",
]
RUN_MANIFEST_INVENTORY = V2_OUTPUTS + CHILD_OUTPUTS + CUSTODY_OUTPUTS[1:]
STDOUT_LOG_DOMAIN = b"P192-WCM-SUPERVISOR-STDOUT-v1\0"
STDERR_LOG_DOMAIN = b"P192-WCM-SUPERVISOR-STDERR-v1\0"
PACKAGE_RELATIVES = {
    "supervisor": Path("tools/p192-weighted-cm-supervisor"),
    "producer": Path("tools/p192-weighted-cm"),
    "verifier": Path("tools/p192-weighted-cm-verify"),
}
ENVIRONMENT_KEYS = [
    "schema", "protocol_commit", "source_commit", "verifier_commit",
    "supervisor_binary_sha256", "producer_binary_sha256",
    "verifier_binary_sha256", "supervisor_build", "child_environment_policy",
    "removed_variable_names", "forbidden_loader_override_names_present",
    "secret_values_recorded",
]
SUPERVISOR_BUILD_KEYS = [
    "embedded_protocol_commit", "embedded_supervisor_commit",
    "embedded_verifier_commit", "embedded_build_profile",
    "embedded_supervisor_dirty", "embedded_git_metadata_present",
]
DECISION_BINDING_KEYS = [
    "decision_id", "decision_path", "decision_commit", "decision_sha256",
    "decision_git_mode", "protocol_repository_path",
    "protocol_checkout_head", "protocol_worktree_clean_before_run",
    "protocol_commit_is_strict_ancestor",
    "protected_protocol_paths_unchanged",
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
RAW_RESULT_KEYS = [
    "schema", "experiment_id", "run_id", "stage", "protocol_commit",
    "source_commit", "verifier_commit", "run_dir", "agreement_sha256",
    "audit_sha256", "receipt_sha256", "scientific_result",
    "scientific_results", "status",
]
RECEIPT_KEYS = [
    "schema", "experiment_id", "protocol_version", "protocol_commit",
    "source_commit", "verifier_commit", "run_dir", "decision_binding",
    "wrapper", "producer", "verifier", "producer_artifacts_before",
    "producer_artifacts_after", "dependency_audit", "agreement_path",
    "agreement_sha256", "overall_status",
]
PRODUCER_OWNED = [
    "identity.json", "maximal-order.json", "factor-base.json",
    "factor-base.sha256", "controls.json", "reference-box.json",
    "reference-box/candidate-records.bin", "reference-box/disposition.bin",
    "reference-box/certificates.bin", "verification.json",
]
PRODUCER_ARTIFACTS = PRODUCER_OWNED[:-1]
VERIFIER_SOURCES = PRODUCER_OWNED

IDENTITY_CHECKS = [
    "serialized_tuple_matches_protocol", "identities_recomputed",
    "nonsingular", "generator_nonidentity", "generator_order_n",
    "exact_group_order_n",
]
ORDER_CHECKS = [
    "p_prime", "n_prime", "C_prime", "p_not_divide_t",
    "trace_absolute_value_below_p", "ordinary", "discriminant_identity",
    "group_order_identity", "discriminant_factorization", "D_squarefree",
    "D_congruent_1_mod_4", "D_fundamental", "frobenius_conductor_one",
    "endomorphism_order_maximal", "discriminants_equal",
    "unit_group_plus_minus_one", "integral_basis_multiplication",
]
PRODUCER_CHECKS = [
    "identity_pass", "maximal_order_pass", "factor_base_pass", "controls_pass",
    "ref0_count_1025", "ref0_candidate_encoding", "ref0_candidate_root",
    "ref0_disposition_encoding", "ref0_disposition_root",
    "ref0_certificate_store", "source_commit_consistent",
]
VERIFIER_CHECKS = [
    "source_inventory_complete", "source_hashes_stable", "identity_rederived",
    "maximal_order_rederived", "primality_proofs_replayed",
    "factor_base_regenerated", "controls_replayed", "ref0_order_regenerated",
    "ref0_candidate_bytes_equal", "ref0_candidate_roots_equal",
    "ref0_dispositions_regenerated", "ref0_disposition_bytes_equal",
    "ref0_disposition_roots_equal", "ref0_certificates_replayed",
    "source_commit_consistent",
]
COMPARISONS = [
    "curve_tuple_sha256", "cm_order_tuple_sha256", "factor_base_sha256",
    "control_results_sha256", "reference_candidate_shard_sha256",
    "reference_candidate_shell_sha256", "reference_disposition_shard_sha256",
    "reference_disposition_shell_sha256",
]
CONTROLS = [
    ("D23-ORDER3", [
        "canonical_reduced_form_norm_2", "ideal_matches_form",
        "alpha_certificate_valid", "encoding_replays",
        "relation_g2_cubed_identity",
    ]),
    ("P192-SQRT-D", [
        "alpha_coordinates_minus_t_2", "norm_equals_abs_D",
        "factorization_equals_5_11_31_C", "algebra_passes",
        "C_degree_map_unavailable", "C_scalar_action_rejected",
    ]),
    ("P192-RAMIFIED-SQUARES", ["ell_5_scalar", "ell_11_scalar", "ell_31_scalar"]),
    ("INERT-FACTOR-REJECTION", ["base_injection_rejected", "residual_injection_rejected"]),
    ("MUTATION-REJECTION", [
        "root_mutation_rejected", "orientation_sign_mutation_rejected",
        "exponent_mutation_rejected", "alpha_coordinate_mutation_rejected",
        "norm_factor_mutation_rejected", "lp_endpoint_mutation_rejected",
        "hnf_column_mutation_rejected",
    ]),
    ("LP-CANCELLATION", ["unmatched_orientation_rejected", "exact_conjugate_cancels"]),
    ("REF0-SCALAR-SEGMENTED", [
        "candidate_bytes_equal", "candidate_shard_root_equal",
        "candidate_shell_root_equal", "disposition_bytes_equal",
        "disposition_shard_root_equal", "disposition_shell_root_equal",
        "retained_records_equal",
    ]),
    ("REF0-DIRECTION-WORKERS", [
        "forward_reverse_candidate_root_equal",
        "forward_reverse_disposition_root_equal",
        "one_eight_worker_candidate_root_equal",
        "one_eight_worker_disposition_root_equal",
        "independent_in_memory_ref0_regenerations_streams_roots_counters_equal",
    ]),
    ("LP-BOUNDARY", [
        "q_L_minus_1_not_prime_rejected_as_lp",
        "q_L_prime_split_accepted_as_one_lp",
        "q_L_plus_1_out_of_range_rejected_as_lp",
        "residual_L_is_one_large_prime",
        "residual_L_squared_is_two_large_prime_with_multiplicity_two",
        "residual_L_squared_plus_one_is_rejected_by_inequality",
    ]),
]

D23_FIXTURE = {
    "D": "-23",
    "t": "1",
    "p": "6",
    "minimal_polynomial": "pi^2 - pi + 6 = 0",
    "roots_mod_2": [0, 1],
    "smaller_root_positive_ideal": "P+=(2,pi)",
    "smaller_root_positive_form": [2, -1, 3],
    "conjugate_ideal": "P-=(2,pi-1)",
    "conjugate_form": [2, 1, 3],
    "g2": "P-",
    "alpha": "1+pi",
    "alpha_coordinates": {"u": "1", "v": "1", "x": "3"},
    "norm": "8",
    "rational_factorization": "2^3",
    "signed_smaller_root_coordinate": "-3",
    "certified_relation": "g2^3=(alpha)",
    "principal_form": [1, 1, 6],
    "generator_column_matrix_rows": [[1, -6], [1, 2]],
    "ideal_power_column_matrix_rows": [[8, -7], [0, 1]],
    "negative_exponent_sint_hex": "020000000103",
    "mutation_target_record": {
        "selected_root": 1,
        "signed_coordinate": "-3",
        "alpha": {"u": "1", "v": "1"},
        "norm": "8",
        "rational_factors": [{"ell": "2", "exponent": 3}],
        "ideal_power_column_matrix_rows": [[8, -7], [0, 1]],
        "signed_coordinate_sint_hex": "020000000103",
    },
    "mutation_target_binding": (
        "This structured replay record is an exact shadow of the corresponding "
        "D23-ORDER3 literals above.  Mutation tests change exactly the scalar "
        "selected by target_field_path in this record while the mathematical "
        "fixture and all non-target scalars remain fixed."
    ),
}
SQRT_D_FIXTURE = {
    "alpha_coordinates": {
        "u": "-31607402316713927207482677199",
        "v": "2",
    },
    "norm": "24109379060336110122544161233113975664949272517896865359515",
    "factorization": {
        "primes_in_order": ["5", "11", "31"],
        "residual_C": "14140398275856956083603613626459809774163796198179979683",
    },
    "subgroup_order_n": "6277101735386680763835789423176059013767194773182842284081",
    "frobenius_scalar_mod_n": "1",
    "derived_alpha_scalar_mod_n": "6277101735386680763835789423144451611450480845975359606884",
    "scalar_derivation": "(u + v*frobenius_scalar_mod_n) mod subgroup_order_n",
    "scalar_square_congruence": "derived_alpha_scalar_mod_n^2 == D mod subgroup_order_n",
    "C_in_factor_base": False,
    "C_degree_map_available": False,
    "C_scalar_action_admitted": False,
    "replay_rule": (
        "Independently verify the P-192 generator is F_p-rational, derive that "
        "Frobenius acts as scalar 1 on the named prime-order subgroup, derive the "
        "exact nonzero alpha scalar above rather than trusting its label, verify "
        "its square is D modulo n, and then reject admission because the exact C "
        "factor is neither in the factor base nor covered by an available "
        "C-degree map.  Merely observing C is unavailable does not satisfy the "
        "separate scalar-action assertion."
    ),
}

MUTATION_FIXTURES = [
    {
        "id": "root",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/selected_root",
        "before_value": 1,
        "after_value": 0,
        "unchanged_claim": "Keep sign -3, exponent magnitude 3, and alpha=1+pi; alpha is not divisible at root 0.",
    },
    {
        "id": "orientation_sign",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/signed_coordinate",
        "before_value": "-3",
        "after_value": "3",
    },
    {
        "id": "exponent",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/signed_coordinate",
        "before_value": "-3",
        "after_value": "-2",
    },
    {
        "id": "alpha_u",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/alpha/u",
        "before_value": "1",
        "after_value": "2",
        "unchanged_claim": "Keep claimed norm and factors.",
    },
    {
        "id": "norm",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/norm",
        "before_value": "8",
        "after_value": "4",
    },
    {
        "id": "rational_factor_exponent",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/rational_factors/0/exponent",
        "before_value": 3,
        "after_value": 2,
    },
    {
        "id": "lp_smaller_root",
        "base_fixture": "LP-BOUNDARY",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/LP-BOUNDARY/endpoint_fixtures/1/smaller_root",
        "before_value": 1109020142,
        "after_value": 1109020143,
        "unchanged_field_values": [
            {
                "field_path": "/role1_interface_addendum/role1_control_fixtures/LP-BOUNDARY/endpoint_fixtures/1/q",
                "value": 2147483647,
            },
            {
                "field_path": "/role1_interface_addendum/role1_control_fixtures/LP-BOUNDARY/endpoint_fixtures/1/larger_root",
                "value": 2025854371,
            },
            {
                "field_path": "/role1_interface_addendum/role1_control_fixtures/LP-BOUNDARY/endpoint_fixtures/1/sign",
                "value": 1,
            },
            {
                "field_path": "/role1_interface_addendum/role1_control_fixtures/LP-BOUNDARY/endpoint_fixtures/1/multiplicity",
                "value": 1,
            },
        ],
    },
    {
        "id": "hnf_matrix_entry",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/ideal_power_column_matrix_rows/0/1",
        "before_value": -7,
        "after_value": -6,
    },
    {
        "id": "sint_sign_byte",
        "target_field_path": "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/mutation_target_record/signed_coordinate_sint_hex",
        "before_value": "020000000103",
        "after_value": "010000000103",
    },
]
MUTATION_HASH_RULE = (
    "For every mutation, recompute all enclosing record and file hashes so a "
    "digest mismatch alone cannot reject it; independent semantic replay must "
    "detect the changed mathematical field."
)
MUTATION_TARGET_PATH_RULE = (
    "target_field_path and every unchanged_field_values.field_path are "
    "absolute RFC 6901 JSON Pointers from the root of this YAML document. "
    "Each pointer identifies exactly one scalar in the frozen base fixture. "
    "before_value must equal the scalar at target_field_path; a mutation "
    "replaces only that scalar with after_value.  No other scalar changes."
)
MUTATION_CARRIER_KEYS = {
    "visibility", "encoding", "file_schema", "file_exact_keys",
    "record_exact_keys", "records_per_file", "fixture_kinds", "D23_fixture",
    "LP_fixture", "record_hash", "file_hash", "replay_per_implementation",
    "exact_internal_counts",
}
MUTATION_INTERNAL_COUNTS = {
    "cases": 9,
    "exact_single_scalar_changes": 9,
    "stale_record_hash_rejections": 9,
    "stale_file_hash_rejections": 9,
    "recomputed_hash_chain_acceptances": 9,
    "semantic_rejections_after_hash_acceptance": 9,
}

LP_FIXTURE = {
    "L": 2147483647,
    "L_squared": "4611686014132420609",
    "D_mod_L": 2121375023,
    "roots_mod_L": [1109020142, 2025854371],
    "endpoint_fixtures": [
        {"q": 2147483646, "relation_to_L": "immediately_below", "expected": "not_prime_and_cannot_be_one_large_prime"},
        {
            "q": 2147483647,
            "relation_to_L": "at",
            "smaller_root": 1109020142,
            "larger_root": 2025854371,
            "sign": 1,
            "multiplicity": 1,
            "expected": "prime_split_and_accepted_as_one_large_prime",
        },
        {"q": 2147483648, "relation_to_L": "immediately_above", "expected": "out_of_range_and_cannot_be_large_prime"},
    ],
    "residual_fixtures": [
        {"residual": "2147483647", "expected_status": "one_large_prime"},
        {"residual": "4611686014132420609", "expected_status": "two_large_prime", "multiplicity": 2},
        {"residual": "4611686014132420610", "expected_status": "rejected", "reason": "greater_than_L_squared"},
    ],
}

SCHEMA_FILES = {
    "identity.json": "identity",
    "maximal-order.json": "maximalOrder",
    "factor-base.json": "factorBase",
    "controls.json": "controls",
    "reference-box.json": "referenceBox",
    "verification.json": "producerVerification",
    "independent-verification.json": "independentVerification",
    "independent-agreement.json": "independentAgreement",
    "dependency-audit.json": "dependencyAudit",
    "environment.json": "role1Environment",
    "raw-result.json": "role1RawResult",
    "manifest.yaml": "runManifest",
    "independent-verifier-receipt.json": "verifierReceipt",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False,
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


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml_strict(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checksum_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if len(digest) != 64 or relative in entries:
            raise ValueError(f"malformed or duplicate checksum line for {relative}")
        entries[relative] = digest
    return entries


def ref0_pairs() -> list[tuple[int, int]]:
    return [(1, 2 * i + 1) for i in range(512)] + [
        (2, 2 * (i - 512)) for i in range(512, 1025)
    ]


def candidate_record_bytes() -> bytes:
    return b"".join(struct.pack(">QQ", v, x) for v, x in ref0_pairs())


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _exact(value: Any, expected: Any, label: str, errors: list[str]) -> None:
    _require(value == expected, f"{label}: expected {expected!r}, got {value!r}", errors)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _resolve_json_pointer(document: Any, pointer: str) -> Any:
    """Resolve an absolute RFC 6901 pointer, rejecting noncanonical indices."""

    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("pointer must start with /")
    current = document
    for encoded in pointer[1:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if not token.isdigit() or (len(token) > 1 and token.startswith("0")):
                raise ValueError(f"noncanonical array index {token!r}")
            index = int(token)
            if index >= len(current):
                raise ValueError(f"array index {index} is out of range")
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                raise ValueError(f"object key {token!r} does not exist")
            current = current[token]
        else:
            raise ValueError(f"cannot descend through scalar at {token!r}")
    return current


def _validate_contract_impl(
    addendum_document: dict[str, Any] | None = None,
    overlay_document: dict[str, Any] | None = None,
    schema_document: dict[str, Any] | None = None,
    *,
    check_files: bool = True,
) -> list[str]:
    """Return actionable validation errors; an empty list is a pass."""

    errors: list[str] = []
    try:
        addendum_root = copy.deepcopy(addendum_document or load_yaml(ADDENDUM_PATH))
        overlay = copy.deepcopy(overlay_document or load_yaml(OVERLAY_PATH))
        schema = copy.deepcopy(schema_document or json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
        decision_schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
        addendum = addendum_root["role1_interface_addendum"]
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return [f"load: {exc}"]

    if check_files:
        for relative, expected in BASE_HASHES.items():
            path = ROOT / relative
            _require(path.is_file(), f"immutable base missing: {relative}", errors)
            if path.is_file():
                _exact(sha256_file(path), expected, f"immutable base hash {relative}", errors)
        try:
            receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
            _exact(receipt["commit_sha"], "ad0f9f488b8e9796f490e40338d858c1062cbfbe", "archive commit", errors)
            for relative, expected in BASE_HASHES.items():
                _exact(receipt["path_sha256"][relative], expected, f"receipt hash {relative}", errors)
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"archive receipt: {exc}")
        try:
            manifest = load_checksum_manifest(ADDENDUM_MANIFEST_PATH)
            _exact(set(manifest), ADDENDUM_PAYLOADS, "addendum checksum payload", errors)
            for relative, expected in manifest.items():
                _exact(sha256_file(ROOT / relative), expected, f"addendum checksum {relative}", errors)
        except (OSError, ValueError) as exc:
            errors.append(f"addendum checksum manifest: {exc}")

    _exact(addendum.get("schema"), "p192-wcm-role1-interface-addendum-v1", "addendum schema", errors)
    _exact(addendum.get("experiment_id"), "EXP-SCURVE-1a8daf", "experiment id", errors)
    _exact(addendum.get("protocol_version"), 2, "protocol version", errors)
    _exact(addendum.get("interface_revision"), 1, "interface revision", errors)
    _exact(addendum.get("status"), "interface_frozen_unexecuted", "addendum status", errors)
    _exact(addendum.get("approval_decision"), None, "approval decision", errors)
    _exact(addendum.get("execution_authorized"), False, "execution authorization", errors)
    _exact(addendum.get("scientific_run_performed"), False, "scientific run flag", errors)
    _exact(addendum.get("scientific_results"), [], "scientific results", errors)
    _exact(addendum.get("affected_runs"), ["P192-WCM-PREFLIGHT"], "affected runs", errors)

    base = addendum.get("immutable_base", {})
    _exact(base.get("archive_commit"), "ad0f9f488b8e9796f490e40338d858c1062cbfbe", "base archive commit", errors)
    for field, relative in (
        ("amendment_sha256", "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml"),
        ("specification_sha256", "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml"),
        ("run_family_sha256", "research/p192-weighted-cm-20261007-v2/run-family.yaml"),
    ):
        _exact(base.get(field), BASE_HASHES[relative], f"addendum {field}", errors)

    stage = addendum.get("stage_binding", {})
    _exact(stage.get("planned_run_label"), "P192-WCM-PREFLIGHT", "stage label", errors)
    _exact(stage.get("ordinal"), 1, "stage ordinal", errors)
    _exact(stage.get("role"), "composite_producer_and_isolated_verifier", "stage role", errors)
    _exact(stage.get("status"), "pending_not_executed", "stage status", errors)
    _exact(stage.get("predecessor"), None, "stage predecessor", errors)
    _exact(stage.get("producer_argv_template"), PRODUCER_ARGV, "producer argv", errors)
    _exact(stage.get("independent_verifier_argv_template"), VERIFIER_ARGV, "verifier argv", errors)
    _exact(stage.get("supervisor_argv_template"), SUPERVISOR_ARGV, "supervisor argv", errors)
    _exact(stage.get("immutable_v2_required_outputs"), V2_OUTPUTS, "v2 output list", errors)
    _exact(stage.get("addendum_required_children"), CHILD_OUTPUTS, "addendum child list", errors)
    _exact(stage.get("canonical_v2_custody_outputs"), CUSTODY_OUTPUTS, "canonical v2 custody outputs", errors)
    ownership = stage.get("ownership", {})
    _exact(ownership.get("producer"), PRODUCER_OWNED, "producer ownership", errors)
    _exact(ownership.get("independent_verifier"), ["independent-verification.json"], "verifier ownership", errors)
    _exact(
        ownership.get("non_arithmetic_supervisor"),
        ["independent-agreement.json", "independent-verifier-receipt.json", "dependency-audit.json", *CUSTODY_OUTPUTS],
        "supervisor ownership",
        errors,
    )
    custody = addendum.get("canonical_v2_custody", {})
    _exact(list(custody), CUSTODY_DESCRIPTION_ORDER, "canonical custody description order", errors)
    environment_contract = custody.get("environment.json", {})
    environment_contract = environment_contract if isinstance(environment_contract, dict) else {}
    _exact(environment_contract.get("schema_value"), "p192-wcm-role1-environment-v1", "custody environment schema", errors)
    _exact(environment_contract.get("exact_top_level_keys"), ENVIRONMENT_KEYS, "custody environment keys", errors)
    raw_contract = custody.get("raw-result.json", {})
    raw_contract = raw_contract if isinstance(raw_contract, dict) else {}
    _exact(raw_contract.get("schema_value"), "p192-wcm-role1-raw-result-v1", "custody raw-result schema", errors)
    _exact(raw_contract.get("exact_top_level_keys"), RAW_RESULT_KEYS, "custody raw-result keys", errors)
    _require("twenty-three-string supervisor argv" in custody.get("command.txt", {}).get("bytes", ""), "custody command bytes are not exact", errors)
    _require("P192-WCM-SUPERVISOR-STDOUT-v1\\0" in custody.get("stdout.log", {}).get("bytes", ""), "custody stdout domain missing", errors)
    _require("P192-WCM-SUPERVISOR-STDERR-v1\\0" in custody.get("stderr.log", {}).get("bytes", ""), "custody stderr domain missing", errors)
    _exact(
        custody.get("manifest.yaml", {}).get("run_exact_top_level_keys"),
        ["id", "experiment_id", "status", "code", "environment", "inputs", "timing", "result", "artifacts"],
        "custody manifest run keys",
        errors,
    )

    if check_files:
        try:
            family = load_yaml(RUN_FAMILY_PATH)
            run = family["runs"][0]
            _exact(run["argv_template"], PRODUCER_ARGV, "immutable run-family producer argv", errors)
            _exact(run["independent_verifier_argv_template"], VERIFIER_ARGV, "immutable run-family verifier argv", errors)
            _exact(run["required_outputs"], V2_OUTPUTS, "immutable run-family outputs", errors)
            _exact(family["family_status"], "pending_not_executed", "base family status", errors)
            _exact(family["dispatch_status"], "blocked_pending_implementation_and_fresh_decision", "base dispatch status", errors)
            spec = load_yaml(SPEC_PATH)["experiment"]
            _exact(spec["execution_authorized"], False, "base execution authorization", errors)
            _exact(spec["scientific_status"], "not_started", "base scientific status", errors)
            _exact(spec["result_status"], "no_result", "base result status", errors)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            errors.append(f"immutable v2 content: {exc}")

    _exact(overlay.get("schema"), "p192-wcm-role1-interface-run-family-overlay-v1", "overlay schema", errors)
    _exact(overlay.get("experiment_id"), "EXP-SCURVE-1a8daf", "overlay experiment", errors)
    _exact(overlay.get("protocol_version"), 2, "overlay protocol", errors)
    _exact(overlay.get("status"), "pending_not_executed", "overlay status", errors)
    _exact(overlay.get("execution_authorized"), False, "overlay authorization", errors)
    _exact(overlay.get("scientific_results"), [], "overlay results", errors)
    _exact(overlay.get("producer_argv_template"), PRODUCER_ARGV, "overlay producer argv", errors)
    _exact(overlay.get("independent_verifier_argv_template"), VERIFIER_ARGV, "overlay verifier argv", errors)
    _exact(overlay.get("supervisor_argv_template"), SUPERVISOR_ARGV, "overlay supervisor argv", errors)
    _exact(overlay.get("immutable_v2_required_outputs"), V2_OUTPUTS, "overlay v2 outputs", errors)
    _exact(overlay.get("addendum_required_children"), CHILD_OUTPUTS, "overlay children", errors)
    _exact(overlay.get("canonical_v2_custody_outputs"), CUSTODY_OUTPUTS, "overlay custody outputs", errors)
    _exact(overlay.get("base_run_family", {}).get("sha256"), BASE_HASHES["research/p192-weighted-cm-20261007-v2/run-family.yaml"], "overlay base hash", errors)
    _exact(overlay.get("scope", {}).get("later_roles_changed"), False, "later role mutation", errors)

    ref = addendum.get("reference_box", {})
    _exact(ref.get("shell_id"), "REF-0", "REF shell", errors)
    _exact([ref.get("v_min"), ref.get("v_max"), ref.get("x_min"), ref.get("x_max_inclusive")], [1, 2, 0, 1024], "REF bounds", errors)
    _exact(ref.get("raw_pair_count"), 1025, "REF count", errors)
    _exact(ref.get("shard_count"), 1, "REF shard count", errors)
    _exact(ref.get("literal_index_mapping"), [
        {"indices": "0..511", "v": 1, "x": "2*i+1"},
        {"indices": "512..1024", "v": 2, "x": "2*(i-512)"},
    ], "REF literal order", errors)
    pairs = ref0_pairs()
    _exact(len(pairs), 1025, "derived REF count", errors)
    _exact(pairs[0], (1, 1), "REF first pair", errors)
    _exact(pairs[511], (1, 1023), "REF v=1 boundary", errors)
    _exact(pairs[512], (2, 0), "REF v=2 boundary", errors)
    _exact(pairs[-1], (2, 1024), "REF last pair", errors)
    records = candidate_record_bytes()
    _exact(len(records), 16400, "REF candidate byte length", errors)
    _exact(records[:16].hex(), "00000000000000010000000000000001", "REF first bytes", errors)
    _exact(records[-16:].hex(), "00000000000000020000000000000400", "REF last bytes", errors)
    resume_scope = ref.get("resume_scope", "")
    _require("no external second-build or two-RUN_DIR comparison" in resume_scope, "Role-1 external comparison exclusion missing", errors)
    _require("does not inject or claim recovery" in resume_scope, "Role-1 no-recovery-claim boundary missing", errors)
    _require("Roles 2 through 4" in resume_scope, "later-role resume obligation missing", errors)
    _exact(ref.get("determinism_control"), {
        "execution": "two_independent_complete_in_memory_ref0_regenerations_per_implementation",
        "implementations_in_order": ["producer", "isolated_independent_verifier"],
        "regenerations_per_implementation": 2,
        "start_candidate_index": 0,
        "complete_candidate_count": 1025,
        "streams_compared_in_order": [
            "candidate_records_bytes", "disposition_records_bytes",
            "certificate_store_bytes",
        ],
        "roots_compared_in_order": [
            "candidate_shard_sha256", "candidate_shell_sha256",
            "disposition_shard_sha256", "disposition_shell_sha256",
        ],
        "counters_compared_in_order": [
            "nonprimitive_duplicate", "complete", "one_large_prime",
            "two_large_prime", "rejected", "invalid", "unresolved",
        ],
        "equality_rule": (
            "Within each implementation, the two regenerations independently create "
            "the complete REF-0 state from index zero in memory.  All three exact byte "
            "streams, all four roots, and all seven counters must be pairwise equal."
        ),
        "external_process_or_run_directory_comparison_claimed": False,
        "crash_or_resume_claimed": False,
    }, "Role-1 in-memory determinism contract", errors)

    binaries = addendum.get("binary_artifacts", {})
    _exact(list(binaries), CHILD_OUTPUTS[:3], "binary artifact paths", errors)
    _exact(binaries.get(CHILD_OUTPUTS[0], {}).get("byte_length"), 16400, "candidate binary length", errors)
    _require("P192-WCM-REF-CERT-STORE-v1\\0" in binaries.get(CHILD_OUTPUTS[2], {}).get("bytes", ""), "certificate store domain separator missing", errors)
    _exact(len(b"P192-WCM-REF-CERT-STORE-v1\0") + 8, 35, "empty certificate-store length", errors)
    _exact(binaries.get(CHILD_OUTPUTS[1], {}).get("status_codes"), {
        0: "nonprimitive_duplicate", 1: "complete", 2: "one_large_prime",
        3: "two_large_prime", 4: "rejected", 5: "invalid", 6: "unresolved",
    }, "status codes", errors)

    controls = addendum.get("role1_control_subset", {}).get("controls_in_order", [])
    observed_controls = [(item.get("control_id"), item.get("assertions")) for item in controls]
    _exact(observed_controls, CONTROLS, "role-1 controls", errors)
    fixtures = addendum.get("role1_control_fixtures", {})
    _exact(fixtures.get("P192-SQRT-D"), SQRT_D_FIXTURE, "P192 sqrt(D) fixture", errors)
    d23 = fixtures.get("D23-ORDER3", {})
    for key, expected in D23_FIXTURE.items():
        _exact(d23.get(key), expected, f"D23 fixture {key}", errors)
    mutation_fixture = fixtures.get("MUTATION-REJECTION", {})
    _exact(set(mutation_fixture), {
        "default_base_fixture", "hash_rule", "target_path_rule",
        "implementation_private_hash_carrier", "mutations_in_order", "expected",
    }, "mutation fixture keys", errors)
    _exact(mutation_fixture.get("default_base_fixture"), "D23-ORDER3", "default mutation base fixture", errors)
    _exact(mutation_fixture.get("hash_rule"), MUTATION_HASH_RULE, "mutation hash rule", errors)
    _exact(mutation_fixture.get("target_path_rule"), MUTATION_TARGET_PATH_RULE, "mutation target path rule", errors)
    carrier = mutation_fixture.get("implementation_private_hash_carrier", {})
    carrier = carrier if isinstance(carrier, dict) else {}
    _exact(set(carrier), MUTATION_CARRIER_KEYS, "mutation carrier keys", errors)
    _exact(carrier.get("visibility"), "transient_in_memory_per_implementation_not_serialized", "mutation carrier visibility", errors)
    _exact(carrier.get("encoding"), "RFC8785 JSON with no BOM or trailing newline", "mutation carrier encoding", errors)
    _exact(carrier.get("file_schema"), "p192-wcm-implementation-mutation-file-v1", "mutation carrier schema", errors)
    _exact(carrier.get("file_exact_keys"), ["schema", "records", "file_sha256"], "mutation carrier file keys", errors)
    _exact(
        carrier.get("record_exact_keys"),
        ["mutation_id", "fixture_kind", "target_field_path", "fixture", "record_sha256"],
        "mutation carrier record keys",
        errors,
    )
    _exact(carrier.get("records_per_file"), 1, "mutation carrier record count", errors)
    _exact(carrier.get("fixture_kinds"), ["D23-ORDER3", "LP-BOUNDARY"], "mutation carrier fixture kinds", errors)
    _require("P192-WCM-MUTATION-RECORD-v1\\0" in carrier.get("record_hash", ""), "mutation carrier record domain missing", errors)
    _require("P192-WCM-MUTATION-FILE-v1\\0" in carrier.get("file_hash", ""), "mutation carrier file domain missing", errors)
    _require("only then" in carrier.get("replay_per_implementation", ""), "mutation semantic-after-hash staging missing", errors)
    _require("does not count" in carrier.get("replay_per_implementation", ""), "stale mutation hash exclusion missing", errors)
    _exact(carrier.get("exact_internal_counts"), MUTATION_INTERNAL_COUNTS, "mutation carrier internal counts", errors)
    mutations = mutation_fixture.get("mutations_in_order", [])
    _exact(mutations, MUTATION_FIXTURES, "semantic mutation fixtures", errors)
    _exact(mutation_fixture.get("expected"), "Every mutation is rejected by the independent verifier.", "mutation outcome", errors)
    for mutation in mutations if isinstance(mutations, list) else []:
        if not isinstance(mutation, dict):
            continue
        mutation_id = mutation.get("id", "<missing>")
        try:
            target_value = _resolve_json_pointer(addendum_root, mutation.get("target_field_path"))
            _exact(target_value, mutation.get("before_value"), f"mutation {mutation_id} target before value", errors)
        except (TypeError, ValueError) as exc:
            errors.append(f"mutation {mutation_id} target path: {exc}")
        for unchanged in mutation.get("unchanged_field_values", []):
            try:
                fixed_value = _resolve_json_pointer(addendum_root, unchanged.get("field_path"))
                _exact(fixed_value, unchanged.get("value"), f"mutation {mutation_id} unchanged field", errors)
            except (AttributeError, TypeError, ValueError) as exc:
                errors.append(f"mutation {mutation_id} unchanged path: {exc}")
    lp = fixtures.get("LP-BOUNDARY", {})
    for key, expected in LP_FIXTURE.items():
        _exact(lp.get(key), expected, f"LP fixture {key}", errors)

    json_artifacts = addendum.get("json_artifacts", {})
    expected_schema_values = {
        "identity.json": "p192-wcm-identity-v1",
        "maximal-order.json": "p192-wcm-maximal-order-v1",
        "controls.json": "p192-wcm-controls-v1",
        "reference-box.json": "p192-wcm-reference-box-v1",
        "verification.json": "p192-wcm-verification-v1",
        "independent-verification.json": "p192-wcm-independent-verification-v1",
        "independent-agreement.json": "p192-wcm-independent-agreement-v1",
        "dependency-audit.json": "p192-wcm-dependency-audit-v1",
        "independent-verifier-receipt.json": "p192-wcm-independent-verifier-receipt-v1",
    }
    _exact(list(json_artifacts), list(expected_schema_values), "JSON artifact schema order", errors)
    for name, schema_value in expected_schema_values.items():
        record = json_artifacts.get(name, {})
        _exact(record.get("schema_value"), schema_value, f"{name} schema value", errors)
        keys = record.get("exact_top_level_keys", [])
        _require(len(keys) == len(set(keys)), f"{name}: duplicate top-level key declaration", errors)
    _exact(json_artifacts.get("identity.json", {}).get("check_ids_in_order"), IDENTITY_CHECKS, "identity checks", errors)
    _exact(json_artifacts.get("maximal-order.json", {}).get("check_ids_in_order"), ORDER_CHECKS, "order checks", errors)
    _exact(json_artifacts.get("verification.json", {}).get("artifact_paths_in_order"), PRODUCER_ARTIFACTS, "producer artifact inventory", errors)
    _exact(json_artifacts.get("verification.json", {}).get("check_ids_in_order"), PRODUCER_CHECKS, "producer checks", errors)
    _exact(json_artifacts.get("independent-verification.json", {}).get("source_artifact_paths_in_order"), VERIFIER_SOURCES, "verifier source inventory", errors)
    _exact(json_artifacts.get("independent-verification.json", {}).get("check_ids_in_order"), VERIFIER_CHECKS, "verifier checks", errors)
    _exact(json_artifacts.get("independent-agreement.json", {}).get("comparison_fields_in_order"), COMPARISONS, "agreement comparisons", errors)
    dependency_contract = json_artifacts.get("dependency-audit.json", {})
    dependency_contract = dependency_contract if isinstance(dependency_contract, dict) else {}
    _exact(dependency_contract.get("source_record_exact_keys"), ["path", "sha256"], "dependency audit source record keys", errors)
    _exact(
        dependency_contract.get("git_record_exact_keys"),
        ["git_head", "git_top_level", "package_root", "worktree_clean"],
        "dependency audit Git record keys",
        errors,
    )
    clone_contract = dependency_contract.get("source_clone_screen", {})
    clone_contract = clone_contract if isinstance(clone_contract, dict) else {}
    _exact(clone_contract.get("claim_limit"), "high_similarity_screen_not_proof_of_zero_conceptual_or_common_lineage", "clone-screen claim limit", errors)
    _require("PRODUCER_SOURCE/src" in clone_contract.get("roots", ""), "clone-screen producer package root missing", errors)
    _require("VERIFIER_SOURCE/src" in clone_contract.get("roots", ""), "clone-screen verifier package root missing", errors)
    receipt_contract = json_artifacts.get("independent-verifier-receipt.json", {})
    receipt_contract = receipt_contract if isinstance(receipt_contract, dict) else {}
    _exact(receipt_contract.get("exact_top_level_keys"), RECEIPT_KEYS, "receipt exact top-level keys", errors)
    _exact(receipt_contract.get("decision_binding_exact_keys"), DECISION_BINDING_KEYS, "receipt decision-binding keys", errors)
    _require("at least 64 tokens" in clone_contract.get("matching", ""), "clone-screen report threshold missing", errors)
    _require("less than 128" in clone_contract.get("matching", ""), "clone-screen rejection threshold missing", errors)

    _exact(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema", "JSON Schema draft", errors)
    definitions = schema.get("$defs", {})
    for definition in ("identity", "maximalOrder", "factorBase", "controls", "referenceBox", "producerVerification", "independentVerification", "independentAgreement", "dependencyAudit", "role1Environment", "role1RawResult", "runManifest", "verifierReceipt"):
        _require(definition in definitions, f"JSON Schema missing $defs/{definition}", errors)
    schema_consts = {
        "identity": "p192-wcm-identity-v1",
        "maximalOrder": "p192-wcm-maximal-order-v1",
        "factorBase": "p192-wcm-factor-base-v1",
        "controls": "p192-wcm-controls-v1",
        "referenceBox": "p192-wcm-reference-box-v1",
        "producerVerification": "p192-wcm-verification-v1",
        "independentVerification": "p192-wcm-independent-verification-v1",
        "independentAgreement": "p192-wcm-independent-agreement-v1",
        "dependencyAudit": "p192-wcm-dependency-audit-v1",
        "role1Environment": "p192-wcm-role1-environment-v1",
        "role1RawResult": "p192-wcm-role1-raw-result-v1",
        "verifierReceipt": "p192-wcm-independent-verifier-receipt-v1",
    }
    for definition, expected in schema_consts.items():
        actual = definitions.get(definition, {}).get("properties", {}).get("schema", {}).get("const")
        _exact(actual, expected, f"JSON Schema {definition} discriminator", errors)
        _exact(definitions.get(definition, {}).get("additionalProperties"), False, f"JSON Schema {definition} closed keys", errors)
    _exact(definitions.get("runManifest", {}).get("additionalProperties"), False, "JSON Schema runManifest closed keys", errors)
    _exact(definitions.get("role1Environment", {}).get("required"), ENVIRONMENT_KEYS, "environment schema key order", errors)
    _exact(definitions.get("role1RawResult", {}).get("required"), RAW_RESULT_KEYS, "raw-result schema key order", errors)
    _exact(definitions.get("verifierReceipt", {}).get("required"), RECEIPT_KEYS, "receipt schema key order", errors)
    _exact(definitions.get("decisionBinding", {}).get("required"), DECISION_BINDING_KEYS, "receipt decision-binding schema keys", errors)
    _exact(
        definitions.get("role1Environment", {}).get("properties", {}).get("supervisor_build", {}).get("required"),
        SUPERVISOR_BUILD_KEYS,
        "environment supervisor build keys",
        errors,
    )
    _exact(
        definitions.get("sourceGitRecord", {}).get("required"),
        ["git_head", "git_top_level", "package_root", "worktree_clean"],
        "dependency Git record schema keys",
        errors,
    )
    try:
        schema_controls = definitions["controls"]["properties"]["controls"]["prefixItems"]
        schema_control_ids = [item["allOf"][1]["properties"]["control_id"]["const"] for item in schema_controls]
        schema_direction_assertions = [
            item["allOf"][1]["properties"]["assertion_id"]["const"]
            for item in schema_controls[7]["allOf"][1]["properties"]["assertions"]["prefixItems"]
        ]
        _exact(schema_control_ids, [control_id for control_id, _ in CONTROLS], "JSON Schema control order", errors)
        _exact(schema_direction_assertions, CONTROLS[7][1], "JSON Schema rebuild assertions", errors)
    except (KeyError, IndexError, TypeError) as exc:
        errors.append(f"JSON Schema control literals: {exc}")
    try:
        import jsonschema
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator.check_schema(decision_schema)
    except ImportError:
        pass
    except Exception as exc:  # jsonschema raises a hierarchy of schema errors.
        errors.append(f"JSON Schema meta-validation: {exc}")
    _exact(
        decision_schema.get("properties", {}).get("coordinator_decision", {}).get("$ref"),
        "#/$defs/decision",
        "dispatch decision schema root",
        errors,
    )
    _exact(
        decision_schema.get("$defs", {}).get("authorization", {}).get("additionalProperties"),
        False,
        "dispatch authorization schema closed keys",
        errors,
    )
    decision_definitions = decision_schema.get("$defs", {})
    decision_definitions = decision_definitions if isinstance(decision_definitions, dict) else {}
    authorization_required = decision_definitions.get("authorization", {}).get("required", [])
    _require("decision_path" in authorization_required, "dispatch authorization lacks decision_path", errors)
    protocol_required = (
        decision_definitions.get("authorization", {}).get("properties", {})
        .get("protocol", {}).get("required", [])
    )
    _require("repository_path" in protocol_required, "dispatch protocol lacks repository_path", errors)
    supervisor_argv_schema = (
        decision_definitions.get("authorization", {}).get("properties", {})
        .get("supervisor_argv", {})
    )
    _exact(supervisor_argv_schema.get("minItems"), 23, "dispatch supervisor argv minimum", errors)
    _exact(supervisor_argv_schema.get("maxItems"), 23, "dispatch supervisor argv maximum", errors)
    for role_definition in ("supervisorBinary", "producerBinary", "verifierBinary"):
        required = decision_definitions.get(role_definition, {}).get("required", [])
        _require("repository_path" in required, f"dispatch {role_definition} lacks repository_path", errors)
        _require("package_path" in required, f"dispatch {role_definition} lacks package_path", errors)
        _require("source_path" not in required, f"dispatch {role_definition} retains ambiguous source_path", errors)
    supervisor_required = decision_definitions.get("supervisorBinary", {}).get("required", [])
    for field in SUPERVISOR_BUILD_KEYS:
        _require(field in supervisor_required, f"dispatch supervisor receipt lacks {field}", errors)

    source_binding = addendum.get("source_commit_binding", {})
    for key in (
        "protocol_commit", "source_commit", "verifier_commit", "binary_binding",
        "supervisor_build_binding", "supervisor_invocation",
        "decision_custody_binding",
    ):
        _require(isinstance(source_binding.get(key), str) and source_binding[key], f"source binding missing {key}", errors)
    _require("P192_WCM_PROTOCOL_COMMIT" in source_binding.get("protocol_commit", ""), "protocol build variable missing", errors)
    _require("P192_WCM_SOURCE_COMMIT" in source_binding.get("source_commit", ""), "source build variable missing", errors)
    _require("P192_WCM_VERIFIER_COMMIT" in source_binding.get("verifier_commit", ""), "verifier build variable missing", errors)
    binary_binding = source_binding.get("binary_binding", "")
    _require("sole build receipts" in binary_binding, "closed executable records are not named as the sole build receipts", errors)
    _require("no additional unnamed build-receipt" in binary_binding, "unnamed build-receipt obligation remains", errors)
    _require("do not claim an exact compiler/toolchain" in binary_binding, "minimal build-receipt limitation missing", errors)
    supervisor_build_binding = source_binding.get("supervisor_build_binding", "")
    for variable in (
        "P192_WCM_EMBEDDED_PROTOCOL_COMMIT",
        "P192_WCM_EMBEDDED_SUPERVISOR_COMMIT",
        "P192_WCM_EMBEDDED_VERIFIER_COMMIT",
        "P192_WCM_EMBEDDED_BUILD_PROFILE",
        "P192_WCM_EMBEDDED_SUPERVISOR_DIRTY",
        "P192_WCM_EMBEDDED_GIT_METADATA_PRESENT",
    ):
        _require(variable in supervisor_build_binding, f"supervisor build binding missing {variable}", errors)
    decision_custody_binding = source_binding.get("decision_custody_binding", "")
    for literal in (
        "regular 100644 blob", "absent at protocol_commit",
        "raw-result.json", "cannot be paired silently with another decision",
    ):
        _require(literal in decision_custody_binding, f"decision custody binding missing {literal}", errors)
    offline = addendum.get("offline_reference_binding", {})
    _exact(offline.get("document"), "SEC2 version 2.0", "SEC2 document", errors)
    _exact(offline.get("document_url"), "https://www.secg.org/sec2-v2.pdf", "SEC2 URL", errors)
    _exact(offline.get("document_sha256"), "87b8f3703364ed5b21ba8582e411cc0cbf477bcaa3f4f45e0d6580d1c00d9952", "SEC2 digest", errors)
    _exact(offline.get("document_byte_length"), 306784, "SEC2 byte length", errors)
    _exact(offline.get("section"), "2.2.2", "SEC2 section", errors)
    _exact(offline.get("parameter_name"), "secp192r1", "SEC2 parameter", errors)
    _require("source_path" not in " ".join(offline), "SEC2 runtime/source path must not be frozen", errors)
    _exact(definitions.get("certificateStore", {}).get("properties", {}).get("byte_length", {}).get("minimum"), 35, "certificate-store schema minimum", errors)
    _exact(
        definitions.get("pocklingtonFactor", {}).get("properties", {}).get("proof"),
        {"$ref": "#/$defs/recursivePrimalityProof"},
        "recursive Pocklington proof schema",
        errors,
    )
    _exact(
        definitions.get("recursivePrimalityProof", {}).get("oneOf"),
        [
            {"$ref": "#/$defs/trialDivisionProof"},
            {"$ref": "#/$defs/pocklingtonProof"},
        ],
        "non-authoritative recursive proof variants",
        errors,
    )
    _require("execution_authorized remains false" in " ".join(addendum.get("admission_gate", [])), "admission gate must retain false authorization", errors)
    _require(any("Do not launch" in item for item in addendum.get("prohibitions", [])), "scientific-launch prohibition missing", errors)
    return errors


def validate_contract(
    addendum_document: dict[str, Any] | None = None,
    overlay_document: dict[str, Any] | None = None,
    schema_document: dict[str, Any] | None = None,
    *,
    check_files: bool = True,
) -> list[str]:
    """Fail closed on malformed protected documents instead of raising."""

    try:
        return _validate_contract_impl(
            addendum_document, overlay_document, schema_document,
            check_files=check_files,
        )
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
        return [f"static contract structure: {exc}"]


def _canonical_json_bytes(value: Any) -> bytes:
    """RFC-8785 bytes for this contract's integer/string-only JSON subset."""

    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON constant {value!r}")


def _load_canonical_json(path: Path, label: str, errors: list[str]) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"{label}: cannot read: {exc}")
        return {}
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{label}: BOM forbidden")
    if raw.endswith((b"\n", b"\r")):
        errors.append(f"{label}: trailing newline forbidden")
    try:
        value = json.loads(
            raw, object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}: expected JSON object")
        return {}
    try:
        canonical = _canonical_json_bytes(value)
    except (TypeError, ValueError) as exc:
        errors.append(f"{label}: cannot canonicalize: {exc}")
        return value
    if raw != canonical:
        errors.append(f"{label}: bytes are not canonical RFC-8785 subset encoding")
    return value


def _load_canonical_json_array(path: Path, label: str, errors: list[str]) -> list[Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw, object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return []
    if not isinstance(value, list):
        errors.append(f"{label}: expected JSON array")
        return []
    try:
        canonical = _canonical_json_bytes(value)
    except (TypeError, ValueError) as exc:
        errors.append(f"{label}: cannot canonicalize: {exc}")
        return value
    if raw != canonical:
        errors.append(f"{label}: bytes are not canonical RFC-8785 subset encoding")
    return value


def _parse_framed_stream_log(
    data: bytes, domain: bytes, label: str, errors: list[str],
) -> tuple[bytes, bytes]:
    if not data.startswith(domain):
        errors.append(f"{label}: domain separator mismatch")
        return b"", b""
    offset = len(domain)
    streams: list[bytes] = []
    for stream_label in ("producer", "verifier"):
        if offset + 8 > len(data):
            errors.append(f"{label}: truncated {stream_label} length")
            return b"", b""
        length = struct.unpack_from(">Q", data, offset)[0]
        offset += 8
        end = offset + length
        if end > len(data):
            errors.append(f"{label}: truncated {stream_label} bytes")
            return b"", b""
        streams.append(data[offset:end])
        offset = end
    _exact(offset, len(data), f"{label} exact framing length", errors)
    return streams[0], streams[1]


def _validate_schema_definition(
    document: dict[str, Any], definition: str, schema: dict[str, Any],
    label: str, errors: list[str],
) -> None:
    try:
        import jsonschema
    except ImportError:
        errors.append(f"{label}: runtime validation requires jsonschema")
        return
    try:
        jsonschema.validate(document, {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": f"#/$defs/{definition}",
        })
    except (KeyError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
        message = exc.message if isinstance(exc, jsonschema.ValidationError) else str(exc)
        errors.append(f"{label}: schema: {message}")


def _artifact_record(run_dir: Path, relative: str) -> dict[str, Any]:
    data = (run_dir / relative).read_bytes()
    return {"path": relative, "byte_length": len(data), "sha256": hashlib.sha256(data).hexdigest()}


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
            while end < len(text) and (
                text[end].isalnum() or text[end] == "_"
            ):
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


def _collect_rust_sources(root: Path) -> list[tuple[str, bytes, list[str]]]:
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
            if entry.name == "target":
                continue
            entry_path = Path(entry.path)
            try:
                entry_metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise ValueError(f"cannot stat source entry {entry_path}: {exc}") from exc
            if stat.S_ISLNK(entry_metadata.st_mode):
                raise ValueError(f"source symlink is forbidden: {entry_path}")
            if stat.S_ISDIR(entry_metadata.st_mode):
                visit(entry_path)
            elif stat.S_ISREG(entry_metadata.st_mode) and entry.name.endswith(".rs"):
                raw = entry_path.read_bytes()
                relative = entry_path.relative_to(root).as_posix()
                records.append((relative, raw, _rust_structural_tokens(raw)))

    visit(root)
    records.sort(key=lambda record: record[0])
    if not records:
        raise ValueError(f"source root has no regular UTF-8 Rust source: {root}")
    return records


def _collect_rust_hash_rows(root: Path) -> list[dict[str, str]]:
    if not root.is_absolute() or _symlink_component(root) is not None:
        raise ValueError(f"package root must be absolute and non-symlink: {root}")
    rows: list[dict[str, str]] = []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            raise ValueError(f"cannot scan package directory {directory}: {exc}") from exc
        for entry in entries:
            if entry.name == "target":
                continue
            path = Path(entry.path)
            metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"package source symlink is forbidden: {path}")
            if stat.S_ISDIR(metadata.st_mode):
                visit(path)
            elif stat.S_ISREG(metadata.st_mode) and path.suffix == ".rs":
                raw = path.read_bytes()
                rows.append({
                    "path": path.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                })

    visit(root)
    rows.sort(key=lambda row: row["path"])
    return rows


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
            digest = _token_digest(tokens[start:start + 64])
            producer_windows.setdefault(digest, []).append((file_index, start))

    endpoints: set[tuple[int, int, int, int, int, int]] = set()
    for verifier_index, (_, _, verifier_tokens) in enumerate(verifier_records):
        for verifier_start in range(max(0, len(verifier_tokens) - 63)):
            window = verifier_tokens[verifier_start:verifier_start + 64]
            for producer_index, producer_start in producer_windows.get(_token_digest(window), []):
                producer_tokens = producer_records[producer_index][2]
                if producer_tokens[producer_start:producer_start + 64] != window:
                    continue
                p_start = producer_start
                v_start = verifier_start
                while p_start and v_start and producer_tokens[p_start - 1] == verifier_tokens[v_start - 1]:
                    p_start -= 1
                    v_start -= 1
                p_end = producer_start + 64
                v_end = verifier_start + 64
                while (
                    p_end < len(producer_tokens) and v_end < len(verifier_tokens)
                    and producer_tokens[p_end] == verifier_tokens[v_end]
                ):
                    p_end += 1
                    v_end += 1
                endpoints.add((producer_index, p_start, p_end, verifier_index, v_start, v_end))

    maximal: list[tuple[int, int, int, int, int, int]] = []
    for candidate in sorted(endpoints):
        p_file, p_start, p_end, v_file, v_start, v_end = candidate
        contained = any(
            other != candidate
            and other[0] == p_file and other[3] == v_file
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
        -match["token_count"], match["producer_path"],
        match["producer_token_start"], match["producer_token_end_exclusive"],
        match["verifier_path"], match["verifier_token_start"],
        match["verifier_token_end_exclusive"],
    ))
    maximum = max((match["token_count"] for match in matches), default=0)
    return {
        "schema": "p192-wcm-source-clone-screen-v1",
        "normalization": "rust-structural-v1",
        "producer_root": str(producer_root),
        "verifier_root": str(verifier_root),
        "include": "**/*.rs",
        "excluded_components": ["target"],
        "report_min_tokens": 64,
        "reject_at_tokens": 128,
        "producer_tree_sha256": _source_tree_digest(producer_records),
        "verifier_tree_sha256": _source_tree_digest(verifier_records),
        "matches": matches,
        "max_match_tokens": maximum,
        "claim_limit": "high_similarity_screen_not_proof_of_zero_conceptual_or_common_lineage",
        "overall_status": "PASS" if maximum < 128 else "FAIL",
    }


def _validate_verdicts(
    document: dict[str, Any], expected_ids: list[str], label: str,
    errors: list[str],
) -> None:
    checks = document.get("checks", [])
    checks = checks if isinstance(checks, list) else []
    observed = [item.get("check_id") for item in checks if isinstance(item, dict)]
    _exact(observed, expected_ids, f"{label} ordered check ids", errors)
    statuses = [item.get("status") for item in checks if isinstance(item, dict)]
    expected_overall = "PASS" if len(statuses) == len(expected_ids) and all(
        status == "PASS" for status in statuses
    ) else "FAIL"
    _exact(document.get("overall_status"), expected_overall, f"{label} status logic", errors)


def _parse_dispositions(data: bytes, errors: list[str]) -> tuple[dict[int, tuple[bytes, bytes]], list[int]]:
    certificates: dict[int, tuple[bytes, bytes]] = {}
    statuses: list[int] = []
    offset = 0
    for expected_index in range(1025):
        if offset + 10 > len(data):
            errors.append(f"disposition.bin: truncated before index {expected_index}")
            return certificates, statuses
        status = data[offset]
        index = struct.unpack_from(">Q", data, offset + 1)[0]
        flag = data[offset + 9]
        offset += 10
        if status not in range(7):
            errors.append(f"disposition.bin: invalid status {status} at {expected_index}")
        if index != expected_index:
            errors.append(f"disposition.bin: index {index} where {expected_index} required")
        retained = status in (1, 2, 3)
        if flag != int(retained):
            errors.append(f"disposition.bin: noncanonical certificate flag at {expected_index}")
        if retained:
            if offset + 64 > len(data):
                errors.append(f"disposition.bin: truncated certificate hashes at {expected_index}")
                return certificates, statuses
            certificates[expected_index] = (data[offset:offset + 32], data[offset + 32:offset + 64])
            offset += 64
        statuses.append(status)
    if offset != len(data):
        errors.append(f"disposition.bin: {len(data) - offset} trailing bytes")
    return certificates, statuses


def _parse_certificate_store(
    data: bytes, dispositions: dict[int, tuple[bytes, bytes]], errors: list[str],
) -> int:
    domain = b"P192-WCM-REF-CERT-STORE-v1\0"
    if len(data) < len(domain) + 8 or not data.startswith(domain):
        errors.append("certificates.bin: missing exact domain/count header")
        return 0
    count = struct.unpack_from(">Q", data, len(domain))[0]
    offset = len(domain) + 8
    previous = -1
    for record_number in range(count):
        if offset + 12 > len(data):
            errors.append(f"certificates.bin: truncated entry {record_number}")
            return record_number
        index = struct.unpack_from(">Q", data, offset)[0]
        candidate_length = struct.unpack_from(">I", data, offset + 8)[0]
        offset += 12
        if offset + candidate_length + 4 > len(data):
            errors.append(f"certificates.bin: truncated candidate certificate {record_number}")
            return record_number
        candidate = data[offset:offset + candidate_length]
        offset += candidate_length
        factor_length = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        if offset + factor_length > len(data):
            errors.append(f"certificates.bin: truncated factor certificate {record_number}")
            return record_number
        factor = data[offset:offset + factor_length]
        offset += factor_length
        if index <= previous:
            errors.append(f"certificates.bin: index {index} is not strictly increasing")
        previous = index
        expected = dispositions.get(index)
        if expected is None:
            errors.append(f"certificates.bin: unreferenced index {index}")
        elif (hashlib.sha256(candidate).digest(), hashlib.sha256(factor).digest()) != expected:
            errors.append(f"certificates.bin: digest mismatch at index {index}")
    if offset != len(data):
        errors.append(f"certificates.bin: {len(data) - offset} trailing bytes")
    if count != len(dispositions):
        errors.append(f"certificates.bin: count {count}, retained dispositions {len(dispositions)}")
    return count


def _expected_roots(candidate: bytes, disposition: bytes) -> dict[str, str]:
    shell = b"REF-0"
    shell_prefix = struct.pack(">I", len(shell)) + shell
    candidate_shard = hashlib.sha256(
        b"P192-WCM-CANDIDATE-SHARD-v1\0" + shell_prefix
        + struct.pack(">Q", 0) + struct.pack(">Q", 1025) + candidate
    ).digest()
    candidate_shell = hashlib.sha256(
        b"P192-WCM-SHELL-ROOT-v1\0" + shell_prefix + struct.pack(">Q", 1)
        + struct.pack(">Q", 0) + struct.pack(">Q", 1025) + candidate_shard
    ).digest()
    disposition_shard = hashlib.sha256(
        b"P192-WCM-DISPOSITION-SHARD-v1\0" + shell_prefix
        + struct.pack(">Q", 0) + struct.pack(">Q", 0)
        + struct.pack(">Q", 1025) + disposition
    ).digest()
    disposition_shell = hashlib.sha256(
        b"P192-WCM-DISPOSITION-SHELL-ROOT-v1\0" + shell_prefix
        + struct.pack(">Q", 1) + struct.pack(">Q", 0) + struct.pack(">Q", 0)
        + struct.pack(">Q", 1025) + disposition_shard
    ).digest()
    return {
        "reference_candidate_shard_sha256": candidate_shard.hex(),
        "reference_candidate_shell_sha256": candidate_shell.hex(),
        "reference_disposition_shard_sha256": disposition_shard.hex(),
        "reference_disposition_shell_sha256": disposition_shell.hex(),
    }


def _validate_status_completion(
    reference: dict[str, Any], statuses: list[int], errors: list[str],
) -> dict[str, int]:
    """Check both internal status consistency and hard Role-1 admission."""

    status_names = [
        "nonprimitive_duplicate", "complete", "one_large_prime",
        "two_large_prime", "rejected", "invalid", "unresolved",
    ]
    expected_counts = {name: statuses.count(code) for code, name in enumerate(status_names)}
    _exact(reference.get("status_counts"), expected_counts, "reference status counts", errors)
    all_consumed = len(statuses) == 1025
    logically_complete = (
        all_consumed
        and expected_counts["invalid"] == 0
        and expected_counts["unresolved"] == 0
    )
    _exact(reference.get("complete"), logically_complete, "reference complete logic", errors)
    _exact(sum(expected_counts.values()), 1025, "reference status-count sum", errors)
    _exact(expected_counts["invalid"], 0, "reference admission invalid count", errors)
    _exact(expected_counts["unresolved"], 0, "reference admission unresolved count", errors)
    _exact(reference.get("complete"), True, "reference admission complete", errors)
    return expected_counts


def _validate_reference_artifacts(
    run_dir: Path, reference: dict[str, Any], errors: list[str],
) -> tuple[dict[str, str], list[int]]:
    try:
        candidate = (run_dir / CHILD_OUTPUTS[0]).read_bytes()
        disposition = (run_dir / CHILD_OUTPUTS[1]).read_bytes()
        certificate_store = (run_dir / CHILD_OUTPUTS[2]).read_bytes()
    except OSError as exc:
        errors.append(f"reference binaries: {exc}")
        return {}, []
    expected_candidate = candidate_record_bytes()
    _exact(candidate, expected_candidate, "candidate-records.bin exact bytes", errors)
    candidate_hash = hashlib.sha256(candidate).hexdigest()
    disposition_hash = hashlib.sha256(disposition).hexdigest()
    roots = _expected_roots(candidate, disposition)
    candidate_descriptor = reference.get("candidate_records", {})
    _exact(candidate_descriptor, {
        "path": CHILD_OUTPUTS[0], "byte_length": len(candidate), "sha256": candidate_hash,
    }, "reference candidate descriptor", errors)
    candidate_shards = reference.get("candidate_shards", [])
    if isinstance(candidate_shards, list) and len(candidate_shards) == 1 and isinstance(candidate_shards[0], dict):
        shard = candidate_shards[0]
        _exact(shard.get("records_sha256"), candidate_hash, "candidate raw shard hash", errors)
        _exact(shard.get("candidate_shard_sha256"), roots["reference_candidate_shard_sha256"], "candidate shard root", errors)
    else:
        errors.append("reference candidate_shards must contain exactly one entry")
    _exact(reference.get("candidate_shell_sha256"), roots["reference_candidate_shell_sha256"], "candidate shell root", errors)

    disposition_map, statuses = _parse_dispositions(disposition, errors)
    disposition_descriptor = reference.get("disposition_records", {})
    _exact(disposition_descriptor, {
        "path": CHILD_OUTPUTS[1], "byte_length": len(disposition), "sha256": disposition_hash,
    }, "reference disposition descriptor", errors)
    disposition_shards = reference.get("disposition_shards", [])
    if isinstance(disposition_shards, list) and len(disposition_shards) == 1 and isinstance(disposition_shards[0], dict):
        shard = disposition_shards[0]
        _exact(shard.get("records_sha256"), disposition_hash, "disposition raw shard hash", errors)
        _exact(shard.get("byte_offset"), 0, "disposition byte offset", errors)
        _exact(shard.get("byte_length"), len(disposition), "disposition byte length", errors)
        _exact(shard.get("disposition_shard_sha256"), roots["reference_disposition_shard_sha256"], "disposition shard root", errors)
    else:
        errors.append("reference disposition_shards must contain exactly one entry")
    _exact(reference.get("disposition_shell_sha256"), roots["reference_disposition_shell_sha256"], "disposition shell root", errors)

    certificate_count = _parse_certificate_store(certificate_store, disposition_map, errors)
    _exact(reference.get("certificates"), {
        "path": CHILD_OUTPUTS[2], "byte_length": len(certificate_store),
        "sha256": hashlib.sha256(certificate_store).hexdigest(),
        "record_count": certificate_count,
    }, "reference certificate-store descriptor", errors)
    _validate_status_completion(reference, statuses, errors)
    return roots, statuses


def _validate_factor_base_document(
    factor_base: dict[str, Any], errors: list[str],
) -> None:
    factor_keys = [
        "schema", "curve_uid", "p", "t", "D", "algebraic_bound",
        "mappable_bound", "source_commit", "entry_count", "entries",
    ]
    _exact(set(factor_base), set(factor_keys), "factor-base exact top-level keys", errors)
    _exact(factor_base.get("schema"), "p192-wcm-factor-base-v1", "factor-base schema", errors)
    for field, expected in (
        ("curve_uid", "urn:ec-record:1:sha256:5531c4a08bdb64b6e86a6e30e9a08aa57edef7af15ac5f6d4d2a83a53bf2f646"),
        ("p", "6277101735386680763835789423207666416083908700390324961279"),
        ("t", "31607402316713927207482677199"),
        ("D", "-24109379060336110122544161233113975664949272517896865359515"),
        ("algebraic_bound", 65521),
        ("mappable_bound", 113),
    ):
        _exact(factor_base.get(field), expected, f"factor-base {field}", errors)
    entries = factor_base.get("entries", [])
    entries = entries if isinstance(entries, list) else []
    _exact(factor_base.get("entry_count"), len(entries), "factor-base entry count", errors)
    ells = [item.get("ell") for item in entries if isinstance(item, dict)]
    _require(
        len(ells) == len(entries)
        and all(isinstance(ell, int) and not isinstance(ell, bool) for ell in ells)
        and ells == sorted(set(ells)),
        "factor-base entries not strictly increasing",
        errors,
    )
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"factor-base entry {index} must be an object")
            continue
        _exact(set(entry), {"ell", "kind", "kronecker", "roots", "positive_root_index"}, f"factor-base entry {index} keys", errors)
        ell = entry.get("ell")
        kind = entry.get("kind")
        roots = entry.get("roots")
        _exact(entry.get("kronecker"), 1 if kind == 0 else 0 if kind == 1 else None, f"factor-base entry {index} Kronecker class", errors)
        _exact(entry.get("positive_root_index"), 0, f"factor-base entry {index} positive root", errors)
        _require(
            isinstance(ell, int) and not isinstance(ell, bool)
            and 2 <= ell <= 65521,
            f"factor-base entry {index} ell out of range",
            errors,
        )
        expected_root_count = 2 if kind == 0 else 1 if kind == 1 else None
        _require(
            isinstance(roots, list)
            and expected_root_count is not None
            and len(roots) == expected_root_count
            and all(isinstance(root, int) and not isinstance(root, bool) for root in roots)
            and roots == sorted(set(roots))
            and isinstance(ell, int) and not isinstance(ell, bool)
            and all(0 <= root < ell for root in roots),
            f"factor-base entry {index} roots violate kind/range/order",
            errors,
        )
    if entries:
        _exact(
            entries[0],
            {"ell": 5, "kind": 1, "kronecker": 0, "positive_root_index": 0, "roots": [2]},
            "factor-base first entry fixture",
            errors,
        )


def validate_run_directory(run_dir: Path) -> list[str]:
    """Validate an already-produced Role-1 directory; never launches a run."""

    errors: list[str] = []
    required = set(V2_OUTPUTS) | set(CHILD_OUTPUTS) | set(CUSTODY_OUTPUTS)
    _require(run_dir.is_dir(), f"run directory missing: {run_dir}", errors)
    _require(not run_dir.is_symlink(), f"run directory may not be a symlink: {run_dir}", errors)
    reference_dir = run_dir / "reference-box"
    _require(reference_dir.is_dir(), "run artifact directory missing: reference-box", errors)
    _require(not reference_dir.is_symlink(), "run artifact directory may not be a symlink: reference-box", errors)
    if run_dir.is_dir() and not run_dir.is_symlink():
        expected_top = {path for path in required if "/" not in path} | {"reference-box"}
        try:
            _exact({entry.name for entry in run_dir.iterdir()}, expected_top, "run top-level entries", errors)
        except OSError as exc:
            errors.append(f"run directory listing: {exc}")
    if reference_dir.is_dir() and not reference_dir.is_symlink():
        expected_children = {path.split("/", 1)[1] for path in required if path.startswith("reference-box/")}
        try:
            _exact({entry.name for entry in reference_dir.iterdir()}, expected_children, "reference-box entries", errors)
        except OSError as exc:
            errors.append(f"reference-box directory listing: {exc}")
    for relative in sorted(required):
        path = run_dir / relative
        _require(path.is_file(), f"run artifact missing: {relative}", errors)
        _require(not path.is_symlink(), f"run artifact may not be a symlink: {relative}", errors)
    if errors:
        return errors
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    documents: dict[str, dict[str, Any]] = {}
    for relative, definition in SCHEMA_FILES.items():
        document = _load_canonical_json(run_dir / relative, relative, errors)
        documents[relative] = document
        _validate_schema_definition(document, definition, schema, relative, errors)
    # Semantic cross-binding assumes the closed per-filename schemas.  A
    # malformed document is already an admission failure and must not reach
    # arithmetic/list operations that could turn a clean FAIL into an exception.
    if errors:
        return errors

    factor_base = documents["factor-base.json"]
    _validate_factor_base_document(factor_base, errors)
    factor_bytes = (run_dir / "factor-base.json").read_bytes()
    factor_digest = hashlib.sha256(factor_bytes).hexdigest()
    expected_sidecar = f"{factor_digest}  factor-base.json\n".encode("ascii")
    _exact((run_dir / "factor-base.sha256").read_bytes(), expected_sidecar, "factor-base sidecar", errors)

    identity = documents["identity.json"]
    maximal = documents["maximal-order.json"]
    controls = documents["controls.json"]
    reference = documents["reference-box.json"]
    producer = documents["verification.json"]
    verifier = documents["independent-verification.json"]
    agreement = documents["independent-agreement.json"]
    dependency_audit = documents["dependency-audit.json"]
    environment = documents["environment.json"]
    raw_result = documents["raw-result.json"]
    run_manifest = documents["manifest.yaml"].get("run", {})
    run_manifest = run_manifest if isinstance(run_manifest, dict) else {}
    receipt = documents["independent-verifier-receipt.json"]
    decision_binding = _mapping(receipt.get("decision_binding"))

    command_argv = _load_canonical_json_array(run_dir / "command.txt", "command.txt", errors)
    _exact(len(command_argv), 23, "command.txt supervisor argv length", errors)
    command_strings = len(command_argv) == 23 and all(
        isinstance(value, str) for value in command_argv
    )
    if len(command_argv) == 23:
        _exact(
            [command_argv[index] for index in range(1, 23, 2)],
            [
                "--producer", "--verifier", "--producer-source",
                "--verifier-source", "--protocol-repository", "--decision",
                "--run-dir", "--protocol-commit", "--source-commit",
                "--verifier-commit", "--audit-out",
            ],
            "command.txt supervisor option order",
            errors,
        )
        for index, label in (
            (0, "supervisor binary"), (2, "producer binary"),
            (4, "verifier binary"), (6, "producer source"),
            (8, "verifier source"), (10, "protocol repository"),
            (12, "decision"), (14, "run directory"),
            (22, "dependency audit"),
        ):
            _normalized_absolute_path(command_argv[index], f"command.txt {label}", errors)
        for index, label in (
            (16, "protocol"), (18, "source"), (20, "verifier"),
        ):
            _require(
                isinstance(command_argv[index], str)
                and COMMIT_RE.fullmatch(command_argv[index]) is not None,
                f"command.txt {label} commit must be exact lower 40-hex",
                errors,
            )
        _exact(command_argv[14], receipt.get("run_dir"), "command.txt receipt run_dir", errors)
        _exact(
            command_argv[22],
            str(Path(str(receipt.get("run_dir", ""))) / "dependency-audit.json"),
            "command.txt contained dependency audit path",
            errors,
        )
        _exact(command_argv[16], receipt.get("protocol_commit"), "command.txt protocol commit", errors)
        _exact(command_argv[18], receipt.get("source_commit"), "command.txt source commit", errors)
        _exact(command_argv[20], receipt.get("verifier_commit"), "command.txt verifier commit", errors)
        _exact(command_argv[10], decision_binding.get("protocol_repository_path"), "command.txt protocol repository", errors)
        _exact(command_argv[12], decision_binding.get("decision_path"), "command.txt decision path", errors)

    protocol_repository_path = _normalized_absolute_path(
        decision_binding.get("protocol_repository_path"),
        "receipt protocol repository path",
        errors,
    )
    bound_decision_path = _normalized_absolute_path(
        decision_binding.get("decision_path"), "receipt decision path", errors,
    )
    bound_decision_id = decision_binding.get("decision_id")
    if (
        protocol_repository_path is not None
        and bound_decision_path is not None
        and isinstance(bound_decision_id, str)
    ):
        _exact(
            bound_decision_path,
            protocol_repository_path / f"ledger/decisions/{bound_decision_id}.yaml",
            "receipt canonical decision path",
            errors,
        )
    _exact(
        decision_binding.get("protocol_checkout_head"),
        decision_binding.get("decision_commit"),
        "receipt protocol checkout head",
        errors,
    )
    _require(
        decision_binding.get("decision_sha256") != "0" * 64,
        "receipt decision hash may not be zero-filled",
        errors,
    )

    producer_stdout, verifier_stdout = _parse_framed_stream_log(
        (run_dir / "stdout.log").read_bytes(), STDOUT_LOG_DOMAIN,
        "stdout.log", errors,
    )
    producer_stderr, verifier_stderr = _parse_framed_stream_log(
        (run_dir / "stderr.log").read_bytes(), STDERR_LOG_DOMAIN,
        "stderr.log", errors,
    )
    child_producer = receipt.get("producer", {})
    child_verifier = receipt.get("verifier", {})
    child_producer = child_producer if isinstance(child_producer, dict) else {}
    child_verifier = child_verifier if isinstance(child_verifier, dict) else {}
    _exact(hashlib.sha256(producer_stdout).hexdigest(), child_producer.get("stdout_sha256"), "producer stdout custody hash", errors)
    _exact(hashlib.sha256(producer_stderr).hexdigest(), child_producer.get("stderr_sha256"), "producer stderr custody hash", errors)
    _exact(hashlib.sha256(verifier_stdout).hexdigest(), child_verifier.get("stdout_sha256"), "verifier stdout custody hash", errors)
    _exact(hashlib.sha256(verifier_stderr).hexdigest(), child_verifier.get("stderr_sha256"), "verifier stderr custody hash", errors)

    audit_hash = sha256_file(run_dir / "dependency-audit.json")
    receipt_audit = receipt.get("dependency_audit", {})
    receipt_audit = receipt_audit if isinstance(receipt_audit, dict) else {}
    _exact(
        audit_hash,
        receipt_audit.get("audit_output_sha256"),
        "dependency audit raw hash custody",
        errors,
    )
    for role, expected_commit in (
        ("producer", receipt.get("source_commit")),
        ("verifier", receipt.get("verifier_commit")),
    ):
        git_record = dependency_audit.get(f"{role}_git", {})
        git_record = git_record if isinstance(git_record, dict) else {}
        _exact(git_record.get("git_head"), expected_commit, f"dependency audit {role} Git head", errors)
        _exact(git_record.get("worktree_clean"), True, f"dependency audit {role} clean tree", errors)
        _normalized_absolute_path(git_record.get("git_top_level"), f"dependency audit {role} Git top level", errors)
        package_root = _normalized_absolute_path(
            git_record.get("package_root"), f"dependency audit {role} package root", errors,
        )
        command_index = 6 if role == "producer" else 8
        if len(command_argv) == 23 and package_root is not None:
            _exact(command_argv[command_index], str(package_root), f"dependency audit {role} argv package root", errors)
        source_rows = dependency_audit.get(f"{role}_rust_sources", [])
        source_rows = source_rows if isinstance(source_rows, list) else []
        paths = [row.get("path") for row in source_rows if isinstance(row, dict)]
        _require(
            len(paths) == len(source_rows)
            and all(isinstance(path, str) for path in paths)
            and paths == sorted(set(paths)),
            f"dependency audit {role} source paths are not strictly increasing objects",
            errors,
        )
    clone_screen = dependency_audit.get("source_clone_screen", {})
    clone_screen = clone_screen if isinstance(clone_screen, dict) else {}
    matches = clone_screen.get("matches", [])
    matches = matches if isinstance(matches, list) else []
    match_order: list[tuple[Any, ...]] = []
    for index, match in enumerate(matches):
        match = match if isinstance(match, dict) else {}
        producer_count = match.get("producer_token_end_exclusive", 0) - match.get("producer_token_start", 0) if all(
            isinstance(match.get(field), int)
            for field in ("producer_token_end_exclusive", "producer_token_start")
        ) else None
        verifier_count = match.get("verifier_token_end_exclusive", 0) - match.get("verifier_token_start", 0) if all(
            isinstance(match.get(field), int)
            for field in ("verifier_token_end_exclusive", "verifier_token_start")
        ) else None
        _exact(producer_count, match.get("token_count"), f"clone match {index} producer span", errors)
        _exact(verifier_count, match.get("token_count"), f"clone match {index} verifier span", errors)
        order_values = (
            match.get("producer_path"), match.get("producer_token_start"),
            match.get("producer_token_end_exclusive"), match.get("verifier_path"),
            match.get("verifier_token_start"), match.get("verifier_token_end_exclusive"),
        )
        valid_order = (
            isinstance(match.get("token_count"), int)
            and isinstance(order_values[0], str)
            and all(isinstance(order_values[position], int) for position in (1, 2, 4, 5))
            and isinstance(order_values[3], str)
        )
        _require(valid_order, f"clone match {index} ordering fields have invalid types", errors)
        if valid_order:
            match_order.append((-match["token_count"], *order_values))
    _require(match_order == sorted(set(match_order)), "clone matches are not uniquely ordered", errors)
    max_match = max(
        (
            match.get("token_count", 0) for match in matches
            if isinstance(match, dict) and isinstance(match.get("token_count", 0), int)
        ),
        default=0,
    )
    _exact(clone_screen.get("max_match_tokens"), max_match, "clone-screen maximum", errors)
    _exact(clone_screen.get("overall_status"), "PASS" if max_match < 128 else "FAIL", "clone-screen status logic", errors)
    _exact(clone_screen.get("overall_status"), "PASS", "clone-screen admission", errors)
    if command_strings:
        _exact(
            clone_screen.get("producer_root"),
            str(Path(command_argv[6]) / "src"),
            "clone-screen producer root",
            errors,
        )
        _exact(
            clone_screen.get("verifier_root"),
            str(Path(command_argv[8]) / "src"),
            "clone-screen verifier root",
            errors,
        )

    receipt_hash = sha256_file(run_dir / "independent-verifier-receipt.json")
    _exact(raw_result.get("protocol_commit"), receipt.get("protocol_commit"), "raw-result protocol commit", errors)
    _exact(raw_result.get("source_commit"), receipt.get("source_commit"), "raw-result source commit", errors)
    _exact(raw_result.get("verifier_commit"), receipt.get("verifier_commit"), "raw-result verifier commit", errors)
    _exact(raw_result.get("run_dir"), receipt.get("run_dir"), "raw-result run_dir", errors)
    _exact(raw_result.get("run_id"), Path(str(receipt.get("run_dir", ""))).name, "raw-result run id", errors)
    _exact(raw_result.get("agreement_sha256"), sha256_file(run_dir / "independent-agreement.json"), "raw-result agreement hash", errors)
    _exact(raw_result.get("audit_sha256"), audit_hash, "raw-result audit hash", errors)
    _exact(raw_result.get("receipt_sha256"), receipt_hash, "raw-result receipt hash", errors)

    expected_manifest_inventory = [
        _artifact_record(run_dir, path) for path in RUN_MANIFEST_INVENTORY
    ]
    _exact(run_manifest.get("id"), raw_result.get("run_id"), "manifest run id", errors)
    _exact(run_manifest.get("artifacts"), expected_manifest_inventory, "manifest exact artifact inventory", errors)
    manifest_environment = run_manifest.get("environment", {})
    manifest_environment = manifest_environment if isinstance(manifest_environment, dict) else {}
    manifest_code = run_manifest.get("code", {})
    manifest_code = manifest_code if isinstance(manifest_code, dict) else {}
    receipt_wrapper = receipt.get("wrapper", {})
    receipt_wrapper = receipt_wrapper if isinstance(receipt_wrapper, dict) else {}
    _exact(manifest_environment.get("sha256"), sha256_file(run_dir / "environment.json"), "manifest environment hash", errors)
    _exact(manifest_code.get("supervisor_binary_sha256"), receipt_wrapper.get("binary_sha256"), "manifest supervisor binary", errors)
    _exact(environment.get("forbidden_loader_override_names_present"), [], "environment loader overrides", errors)
    _exact(environment.get("protocol_commit"), receipt.get("protocol_commit"), "environment protocol commit", errors)
    _exact(environment.get("source_commit"), receipt.get("source_commit"), "environment source commit", errors)
    _exact(environment.get("verifier_commit"), receipt.get("verifier_commit"), "environment verifier commit", errors)
    _exact(environment.get("supervisor_binary_sha256"), receipt_wrapper.get("binary_sha256"), "environment supervisor binary", errors)
    _exact(environment.get("producer_binary_sha256"), child_producer.get("binary_sha256"), "environment producer binary", errors)
    _exact(environment.get("verifier_binary_sha256"), child_verifier.get("binary_sha256"), "environment verifier binary", errors)
    supervisor_build = environment.get("supervisor_build", {})
    supervisor_build = supervisor_build if isinstance(supervisor_build, dict) else {}
    _exact(supervisor_build.get("embedded_protocol_commit"), receipt.get("protocol_commit"), "environment embedded protocol commit", errors)
    _exact(supervisor_build.get("embedded_supervisor_commit"), receipt.get("source_commit"), "environment embedded supervisor commit", errors)
    _exact(supervisor_build.get("embedded_verifier_commit"), receipt.get("verifier_commit"), "environment embedded verifier commit", errors)
    _exact(supervisor_build.get("embedded_build_profile"), "release", "environment embedded build profile", errors)
    _exact(supervisor_build.get("embedded_supervisor_dirty"), False, "environment embedded supervisor dirty", errors)
    _exact(supervisor_build.get("embedded_git_metadata_present"), True, "environment embedded Git metadata", errors)

    _validate_verdicts(identity, IDENTITY_CHECKS, "identity", errors)
    _validate_verdicts(maximal, ORDER_CHECKS, "maximal-order", errors)
    _validate_verdicts(producer, PRODUCER_CHECKS, "producer verification", errors)
    _validate_verdicts(verifier, VERIFIER_CHECKS, "independent verification", errors)

    control_records = controls.get("controls", [])
    control_records = control_records if isinstance(control_records, list) else []
    observed_controls: list[tuple[str | None, list[str | None]]] = []
    for record in control_records:
        assertions = record.get("assertions", []) if isinstance(record, dict) else []
        assertions = assertions if isinstance(assertions, list) else []
        observed_controls.append((
            record.get("control_id") if isinstance(record, dict) else None,
            [item.get("assertion_id") for item in assertions if isinstance(item, dict)],
        ))
        passed = [item.get("passed") for item in assertions if isinstance(item, dict)]
        expected_status = "PASS" if passed and all(value is True for value in passed) else "FAIL"
        if isinstance(record, dict):
            _exact(record.get("status"), expected_status, f"control {record.get('control_id')} status", errors)
    _exact(observed_controls, CONTROLS, "runtime ordered controls/assertions", errors)
    controls_overall = "PASS" if len(control_records) == len(CONTROLS) and all(
        isinstance(record, dict) and record.get("status") == "PASS"
        for record in control_records
    ) else "FAIL"
    _exact(controls.get("overall_status"), controls_overall, "controls overall status", errors)
    control_digest = hashlib.sha256(
        b"P192-WCM-CONTROL-RESULTS-v1\0" + _canonical_json_bytes(control_records)
    ).hexdigest()
    _exact(controls.get("control_results_sha256"), control_digest, "control results digest", errors)

    roots, _ = _validate_reference_artifacts(run_dir, reference, errors)
    curve_digest = hashlib.sha256(
        b"P192-WCM-CURVE-TUPLE-v1\0" + _canonical_json_bytes(identity.get("curve"))
    ).hexdigest()
    order_digest = hashlib.sha256(
        b"P192-WCM-CM-ORDER-TUPLE-v1\0" + _canonical_json_bytes(maximal.get("order"))
    ).hexdigest()
    expected_bindings = {
        "curve_tuple_sha256": curve_digest,
        "cm_order_tuple_sha256": order_digest,
        "factor_base_sha256": factor_digest,
        "control_results_sha256": control_digest,
        **roots,
    }
    _exact(producer.get("bindings"), expected_bindings, "producer bindings", errors)
    _exact(verifier.get("bindings"), expected_bindings, "verifier bindings", errors)

    expected_producer_inventory = [_artifact_record(run_dir, path) for path in PRODUCER_ARTIFACTS]
    expected_verifier_inventory = [_artifact_record(run_dir, path) for path in VERIFIER_SOURCES]
    _exact(producer.get("artifacts"), expected_producer_inventory, "producer artifact inventory", errors)
    _exact(verifier.get("source_artifacts"), expected_verifier_inventory, "verifier source inventory", errors)

    comparison_records = agreement.get("comparisons", [])
    comparison_records = comparison_records if isinstance(comparison_records, list) else []
    _exact(
        [record.get("field") if isinstance(record, dict) else None for record in comparison_records],
        COMPARISONS, "agreement field order", errors,
    )
    for record in comparison_records:
        if not isinstance(record, dict):
            continue
        field = record.get("field")
        if field in expected_bindings:
            _exact(record.get("producer"), expected_bindings[field], f"agreement {field} producer", errors)
            _exact(record.get("verifier"), expected_bindings[field], f"agreement {field} verifier", errors)
            _exact(record.get("equal"), True, f"agreement {field} equality", errors)
    expected_agreement_status = "PASS" if len(comparison_records) == len(COMPARISONS) and all(
        isinstance(record, dict) and record.get("equal") is True
        for record in comparison_records
    ) else "FAIL"
    _exact(agreement.get("overall_status"), expected_agreement_status, "agreement status", errors)
    _exact(agreement.get("producer_verification_sha256"), sha256_file(run_dir / "verification.json"), "agreement producer hash", errors)
    _exact(agreement.get("independent_verification_sha256"), sha256_file(run_dir / "independent-verification.json"), "agreement verifier hash", errors)

    commits = [
        identity.get("protocol_commit"), maximal.get("protocol_commit"),
        controls.get("protocol_commit"), reference.get("protocol_commit"),
        producer.get("protocol_commit"), verifier.get("protocol_commit"),
        agreement.get("protocol_commit"), receipt.get("protocol_commit"),
    ]
    _require(
        all(isinstance(value, str) for value in commits) and len(set(commits)) == 1,
        "protocol_commit differs across artifacts", errors,
    )
    sources = [
        identity.get("source_commit"), maximal.get("source_commit"),
        controls.get("source_commit"), reference.get("source_commit"),
        producer.get("source_commit"), verifier.get("source_commit"),
        agreement.get("source_commit"), receipt.get("source_commit"),
        factor_base.get("source_commit"),
    ]
    _require(
        all(isinstance(value, str) for value in sources) and len(set(sources)) == 1,
        "source_commit differs across artifacts", errors,
    )
    _exact(receipt.get("verifier_commit"), verifier.get("verifier_commit"), "receipt verifier commit", errors)
    _exact(receipt.get("producer_artifacts_before"), expected_verifier_inventory, "receipt before inventory", errors)
    _exact(receipt.get("producer_artifacts_after"), expected_verifier_inventory, "receipt after inventory", errors)
    _exact(receipt.get("producer_artifacts_before"), receipt.get("producer_artifacts_after"), "receipt before/after byte stability", errors)
    _exact(receipt.get("agreement_sha256"), sha256_file(run_dir / "independent-agreement.json"), "receipt agreement hash", errors)
    _exact(receipt.get("agreement_path"), "independent-agreement.json", "receipt agreement path", errors)
    child_producer = _mapping(receipt.get("producer"))
    child_verifier = _mapping(receipt.get("verifier"))
    _exact(child_producer.get("binary_sha256"), producer.get("producer_binary_sha256"), "producer binary binding", errors)
    _exact(child_producer.get("commit"), sources[0], "producer child commit", errors)
    _exact(child_verifier.get("binary_sha256"), verifier.get("verifier_binary_sha256"), "verifier binary binding", errors)
    _exact(child_verifier.get("commit"), verifier.get("verifier_commit"), "verifier child commit", errors)
    run_dir_text = receipt.get("run_dir", "")
    run_dir_text = run_dir_text if isinstance(run_dir_text, str) else ""
    resolved_producer_argv, resolved_verifier_argv = _resolved_argv(run_dir_text)
    _exact(child_producer.get("argv"), resolved_producer_argv, "receipt producer argv", errors)
    _exact(child_verifier.get("argv"), resolved_verifier_argv, "receipt verifier argv", errors)
    sequence = [
        child_producer.get("started_sequence"), child_producer.get("completed_sequence"),
        child_verifier.get("started_sequence"), child_verifier.get("completed_sequence"),
    ]
    _require(all(isinstance(value, int) for value in sequence) and sequence == sorted(set(sequence)), "receipt child sequence is not strictly ordered", errors)
    receipt_dependency = _mapping(receipt.get("dependency_audit"))
    receipt_pass = (
        child_producer.get("exit_code") == 0
        and child_verifier.get("exit_code") == 0
        and child_producer.get("build_profile") == "release"
        and child_verifier.get("build_profile") == "release"
        and child_producer.get("worktree_clean") is True
        and child_verifier.get("worktree_clean") is True
        and producer.get("overall_status") == "PASS"
        and verifier.get("overall_status") == "PASS"
        and agreement.get("overall_status") == "PASS"
        and receipt.get("producer_artifacts_before") == receipt.get("producer_artifacts_after")
        and receipt_dependency.get("verifier_crypto_lib_found") is False
        and receipt_dependency.get("shared_implementation_components") == []
        and decision_binding.get("decision_git_mode") == "100644"
        and decision_binding.get("protocol_worktree_clean_before_run") is True
        and decision_binding.get("protocol_commit_is_strict_ancestor") is True
        and decision_binding.get("protected_protocol_paths_unchanged") is True
    )
    _exact(receipt.get("overall_status"), "PASS" if receipt_pass else "FAIL", "receipt status logic", errors)
    return errors


def _resolved_argv(run_dir: str) -> tuple[list[str], list[str]]:
    producer = [
        run_dir if item == "RUN_DIR"
        else item.replace("RUN_DIR/", run_dir + "/")
        for item in PRODUCER_ARGV
    ]
    verifier = [
        run_dir if item == "RUN_DIR"
        else item.replace("RUN_DIR/", run_dir + "/")
        for item in VERIFIER_ARGV
    ]
    return producer, verifier


def _resolved_supervisor_argv(authorization: dict[str, Any]) -> list[Any]:
    executables = authorization.get("executables", {})
    executables = executables if isinstance(executables, dict) else {}
    supervisor = executables.get("supervisor", {})
    producer = executables.get("producer", {})
    verifier = executables.get("verifier", {})
    supervisor = supervisor if isinstance(supervisor, dict) else {}
    producer = producer if isinstance(producer, dict) else {}
    verifier = verifier if isinstance(verifier, dict) else {}
    protocol = authorization.get("protocol", {})
    protocol = protocol if isinstance(protocol, dict) else {}
    run = authorization.get("run", {})
    run = run if isinstance(run, dict) else {}
    audit = authorization.get("dependency_audit", {})
    audit = audit if isinstance(audit, dict) else {}
    return [
        supervisor.get("binary_path"),
        "--producer", producer.get("binary_path"),
        "--verifier", verifier.get("binary_path"),
        "--producer-source", producer.get("package_path"),
        "--verifier-source", verifier.get("package_path"),
        "--protocol-repository", protocol.get("repository_path"),
        "--decision", authorization.get("decision_path"),
        "--run-dir", run.get("run_dir"),
        "--protocol-commit", protocol.get("commit"),
        "--source-commit", producer.get("source_commit"),
        "--verifier-commit", verifier.get("verifier_commit"),
        "--audit-out", audit.get("path"),
    ]


def _normalized_absolute_path(
    value: Any, label: str, errors: list[str],
) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected a nonempty string")
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


def _hash_admitted_binary(
    record: Any, label: str, errors: list[str],
) -> Path | None:
    if not isinstance(record, dict):
        errors.append(f"{label}: binary record must be a mapping")
        return None
    path = _normalized_absolute_path(record.get("binary_path"), f"{label} binary_path", errors)
    if path is None:
        return None
    linked = _symlink_component(path)
    _require(linked is None, f"{label}: symlink path component forbidden: {linked}", errors)
    try:
        before = os.lstat(path)
    except OSError as exc:
        errors.append(f"{label}: cannot stat binary: {exc}")
        return path
    _require(stat.S_ISREG(before.st_mode), f"{label}: binary is not a regular file", errors)
    _require(before.st_mode & 0o111 != 0, f"{label}: binary has no executable bit", errors)
    if not stat.S_ISREG(before.st_mode) or linked is not None:
        return path
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened_before = os.fstat(descriptor)
            digest = hashlib.sha256()
            byte_length = 0
            while True:
                block = os.read(descriptor, 1024 * 1024)
                if not block:
                    break
                digest.update(block)
                byte_length += len(block)
            opened_after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        errors.append(f"{label}: cannot read binary safely: {exc}")
        return path
    stable = (
        before.st_dev == opened_before.st_dev == opened_after.st_dev
        and before.st_ino == opened_before.st_ino == opened_after.st_ino
        and before.st_size == opened_before.st_size == opened_after.st_size == byte_length
        and opened_before.st_mtime_ns == opened_after.st_mtime_ns
    )
    _require(stable, f"{label}: binary changed while it was hashed", errors)
    _exact(byte_length, record.get("byte_length"), f"{label} binary byte length", errors)
    _exact(digest.hexdigest(), record.get("binary_sha256"), f"{label} binary sha256", errors)
    return path


def _validate_source_checkout(
    record: dict[str, Any], commit_field: str, label: str,
    errors: list[str], *, check_git: bool,
) -> Path | None:
    repository_path = _normalized_absolute_path(
        record.get("repository_path"), f"{label} repository_path", errors,
    )
    package_path = _normalized_absolute_path(
        record.get("package_path"), f"{label} package_path", errors,
    )
    if repository_path is None or package_path is None:
        return None
    for path, path_label in (
        (repository_path, "repository path"), (package_path, "package path"),
    ):
        linked = _symlink_component(path)
        _require(linked is None, f"{label}: {path_label} contains symlink component: {linked}", errors)
        try:
            metadata = os.lstat(path)
            _require(stat.S_ISDIR(metadata.st_mode), f"{label}: {path_label} is not a directory", errors)
        except OSError as exc:
            errors.append(f"{label}: cannot stat {path_label}: {exc}")
            return package_path
    expected_package = repository_path / PACKAGE_RELATIVES[label]
    _exact(package_path, expected_package, f"{label} canonical package path", errors)
    try:
        relative = package_path.relative_to(repository_path)
        _require(relative != Path("."), f"{label}: package path must be a strict repository descendant", errors)
    except ValueError:
        errors.append(f"{label}: package path is outside repository path")
    manifest = package_path / "Cargo.toml"
    linked_manifest = _symlink_component(manifest)
    _require(linked_manifest is None, f"{label}: Cargo.toml contains symlink component: {linked_manifest}", errors)
    try:
        manifest_metadata = os.lstat(manifest)
        _require(stat.S_ISREG(manifest_metadata.st_mode), f"{label}: package Cargo.toml is not regular", errors)
    except OSError as exc:
        errors.append(f"{label}: cannot stat package Cargo.toml: {exc}")
    if not check_git:
        return package_path
    expected_commit = record.get(commit_field)
    top = _git(package_path, ["rev-parse", "--show-toplevel"])
    head = _git(package_path, ["rev-parse", "HEAD"])
    status_result = _git(package_path, ["status", "--porcelain=v1", "--untracked-files=normal"])
    if top is None or top.returncode != 0:
        errors.append(f"{label}: source path is not a readable Git worktree")
    else:
        observed_top = top.stdout.decode("utf-8", "replace").strip()
        _exact(observed_top, str(repository_path), f"{label} Git top level", errors)
    if head is None or head.returncode != 0:
        errors.append(f"{label}: cannot read source HEAD")
    else:
        _exact(head.stdout.decode("ascii", "replace").strip(), expected_commit, f"{label} source HEAD", errors)
    if status_result is None or status_result.returncode != 0:
        errors.append(f"{label}: cannot inspect source cleanliness")
    else:
        _exact(status_result.stdout, b"", f"{label} source worktree cleanliness", errors)
    return package_path


def _decision_relative_path(
    decision_path: Path, decision_id: Any, repository_root: Path,
    errors: list[str],
) -> str | None:
    if not isinstance(decision_id, str) or not DECISION_ID_RE.fullmatch(decision_id):
        errors.append("decision id is not DEC-YYYYMMDD-six-lower-hex")
        return None
    relative = f"ledger/decisions/{decision_id}.yaml"
    expected = repository_root / relative
    supplied = str(decision_path)
    valid_spelling = supplied == relative if not decision_path.is_absolute() else supplied == str(expected)
    _require(valid_spelling, f"decision path must be exactly {relative} or {expected}", errors)
    if not valid_spelling:
        return None
    linked = _symlink_component(expected)
    _require(linked is None, f"decision path contains symlink component: {linked}", errors)
    try:
        metadata = os.lstat(expected)
        _require(stat.S_ISREG(metadata.st_mode), "decision path is not a regular file", errors)
    except OSError as exc:
        errors.append(f"decision path cannot be stated: {exc}")
    return relative


def _git(
    repository_root: Path, arguments: list[str],
) -> subprocess.CompletedProcess[bytes] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except OSError:
        return None


def _git_tree_entry(
    repository_root: Path, commit: str, relative: str, label: str,
    errors: list[str],
) -> tuple[str, str] | None:
    result = _git(repository_root, ["ls-tree", "-z", commit, "--", relative])
    if result is None or result.returncode != 0:
        detail = "git unavailable" if result is None else result.stderr.decode("utf-8", "replace").strip()
        errors.append(f"{label}: cannot inspect Git tree: {detail}")
        return None
    records = [record for record in result.stdout.split(b"\0") if record]
    if len(records) != 1:
        errors.append(f"{label}: expected exactly one Git tree entry")
        return None
    try:
        metadata, encoded_path = records[0].split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split(" ")
        observed_path = encoded_path.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as exc:
        errors.append(f"{label}: malformed Git tree entry: {exc}")
        return None
    _exact(observed_path, relative, f"{label} Git path", errors)
    _exact(object_type, "blob", f"{label} Git object type", errors)
    _require(mode in {"100644", "100755"}, f"{label}: Git mode {mode!r} is not a regular file", errors)
    if observed_path != relative or object_type != "blob" or mode not in {"100644", "100755"}:
        return None
    return mode, object_id


def _git_blob(
    repository_root: Path, object_id: str, label: str, errors: list[str],
) -> bytes | None:
    result = _git(repository_root, ["cat-file", "blob", object_id])
    if result is None or result.returncode != 0:
        detail = "git unavailable" if result is None else result.stderr.decode("utf-8", "replace").strip()
        errors.append(f"{label}: cannot read Git blob: {detail}")
        return None
    return result.stdout


def _validate_git_decision_binding(
    repository_root: Path, decision_relative: str, decision_bytes: bytes,
    decision_commit: str, authorization: dict[str, Any], phase: str,
    errors: list[str],
) -> None:
    protocol = authorization.get("protocol", {})
    if not isinstance(protocol, dict):
        return
    protocol_commit = protocol.get("commit")
    if not isinstance(protocol_commit, str) or not COMMIT_RE.fullmatch(protocol_commit):
        return
    for commit, label in ((protocol_commit, "protocol commit"), (decision_commit, "decision commit")):
        result = _git(repository_root, ["cat-file", "-e", f"{commit}^{{commit}}"])
        if result is None or result.returncode != 0:
            errors.append(f"{label}: exact commit object does not exist")
            return
    top = _git(repository_root, ["rev-parse", "--show-toplevel"])
    if top is None or top.returncode != 0:
        errors.append(f"{phase}: cannot resolve protocol repository top level")
    else:
        _exact(
            top.stdout.decode("utf-8", "replace").strip(),
            str(repository_root),
            f"{phase} protocol repository top level",
            errors,
        )
    head = _git(repository_root, ["rev-parse", "HEAD"])
    if head is None or head.returncode != 0:
        errors.append(f"{phase}: cannot read protocol repository HEAD")
    else:
        _exact(
            head.stdout.decode("ascii", "replace").strip(),
            decision_commit,
            f"{phase} protocol HEAD equals decision commit",
            errors,
        )
    if phase == "pre-dispatch":
        status_result = _git(
            repository_root,
            ["status", "--porcelain=v1", "--untracked-files=normal"],
        )
        if status_result is None or status_result.returncode != 0:
            errors.append("pre-dispatch: cannot inspect protocol worktree cleanliness")
        else:
            _exact(status_result.stdout, b"", "pre-dispatch protocol worktree cleanliness", errors)
    _require(protocol_commit != decision_commit, "protocol commit must be a strict ancestor of decision commit", errors)
    ancestor = _git(repository_root, ["merge-base", "--is-ancestor", protocol_commit, decision_commit])
    if ancestor is None:
        errors.append("protocol ancestry: git unavailable")
    elif ancestor.returncode == 1:
        errors.append("protocol commit is not an ancestor of decision commit")
    elif ancestor.returncode != 0:
        errors.append(
            "protocol ancestry check failed: "
            + ancestor.stderr.decode("utf-8", "replace").strip()
        )

    decision_entry = _git_tree_entry(
        repository_root, decision_commit, decision_relative,
        "decision at decision commit", errors,
    )
    decision_at_protocol = _git(
        repository_root, ["ls-tree", "-z", protocol_commit, "--", decision_relative],
    )
    if decision_at_protocol is None or decision_at_protocol.returncode != 0:
        errors.append("decision at protocol commit: cannot inspect Git tree")
    else:
        _exact(
            decision_at_protocol.stdout, b"",
            "fresh decision absent at protocol commit",
            errors,
        )
    if decision_entry is not None:
        _exact(decision_entry[0], "100644", "decision Git mode", errors)
        committed_decision = _git_blob(repository_root, decision_entry[1], "decision", errors)
        if committed_decision is not None:
            _exact(committed_decision, decision_bytes, "decision working bytes", errors)

    protocol_blobs: dict[str, bytes] = {}
    for relative in PROTECTED_PROTOCOL_PATHS:
        at_protocol = _git_tree_entry(
            repository_root, protocol_commit, relative,
            f"protected path at protocol commit {relative}", errors,
        )
        at_decision = _git_tree_entry(
            repository_root, decision_commit, relative,
            f"protected path at decision commit {relative}", errors,
        )
        if at_protocol is None or at_decision is None:
            continue
        _exact(at_decision, at_protocol, f"protected Git entry unchanged {relative}", errors)
        blob = _git_blob(repository_root, at_protocol[1], f"protected path {relative}", errors)
        if blob is None:
            continue
        protocol_blobs[relative] = blob
        current = repository_root / relative
        linked = _symlink_component(current)
        _require(linked is None, f"current protected path contains symlink: {relative}", errors)
        try:
            current_metadata = os.lstat(current)
            _require(stat.S_ISREG(current_metadata.st_mode), f"current protected path is not regular: {relative}", errors)
            if stat.S_ISREG(current_metadata.st_mode) and linked is None:
                _exact(current.read_bytes(), blob, f"current protected bytes {relative}", errors)
        except OSError as exc:
            errors.append(f"current protected path {relative}: {exc}")

    for key, relative in (
        ("addendum", ADDENDUM_RELATIVE),
        ("interface_manifest", INTERFACE_MANIFEST_RELATIVE),
    ):
        descriptor = protocol.get(key, {})
        blob = protocol_blobs.get(relative)
        if blob is None or not isinstance(descriptor, dict):
            continue
        _exact(descriptor.get("path"), relative, f"protocol {key} path", errors)
        _exact(descriptor.get("byte_length"), len(blob), f"protocol {key} byte length", errors)
        _exact(
            descriptor.get("sha256"), hashlib.sha256(blob).hexdigest(),
            f"protocol {key} sha256", errors,
        )


def _validate_decision_semantics(
    decision: dict[str, Any], decision_commit: str, phase: str,
    supplied_run_dir: Path | None, repository_root: Path, errors: list[str],
    *, check_source_git: bool,
) -> tuple[dict[str, Any], Path | None]:
    authorization = decision.get("authorization", {})
    if not isinstance(authorization, dict):
        errors.append("authorization must be a mapping")
        return {}, None
    protocol = authorization.get("protocol", {})
    run = authorization.get("run", {})
    executables = authorization.get("executables", {})
    _exact(protocol.get("protected_paths") if isinstance(protocol, dict) else None, PROTECTED_PROTOCOL_PATHS, "decision protected paths", errors)
    protocol_repository = _normalized_absolute_path(
        protocol.get("repository_path") if isinstance(protocol, dict) else None,
        "decision protocol repository_path",
        errors,
    )
    if protocol_repository is not None:
        _exact(protocol_repository, repository_root, "decision protocol repository checkout", errors)
    decision_path = _normalized_absolute_path(
        authorization.get("decision_path"), "decision authorization path", errors,
    )
    decision_id = decision.get("id")
    if decision_path is not None and isinstance(decision_id, str):
        _exact(
            decision_path,
            repository_root / f"ledger/decisions/{decision_id}.yaml",
            "decision authorization canonical path",
            errors,
        )
    _exact(
        authorization.get("stage", {}).get("unauthorized_stage_labels")
        if isinstance(authorization.get("stage"), dict) else None,
        UNAUTHORIZED_STAGE_LABELS,
        "decision unauthorized later stages",
        errors,
    )
    _exact(
        authorization.get("stage", {}).get("custody_outputs")
        if isinstance(authorization.get("stage"), dict) else None,
        CUSTODY_OUTPUTS,
        "decision v2 custody outputs",
        errors,
    )
    _require(COMMIT_RE.fullmatch(decision_commit) is not None, "decision commit must be exactly 40 lowercase hex", errors)
    _require(decision_commit != "0" * 40, "decision commit may not be zero-filled", errors)
    supervisor = executables.get("supervisor", {}) if isinstance(executables, dict) else {}
    producer = executables.get("producer", {}) if isinstance(executables, dict) else {}
    verifier = executables.get("verifier", {}) if isinstance(executables, dict) else {}
    supervisor = supervisor if isinstance(supervisor, dict) else {}
    producer = producer if isinstance(producer, dict) else {}
    verifier = verifier if isinstance(verifier, dict) else {}
    commits: list[tuple[str, Any]] = [
        ("protocol", protocol.get("commit") if isinstance(protocol, dict) else None),
        ("supervisor", supervisor.get("source_commit")),
        ("supervisor embedded protocol", supervisor.get("embedded_protocol_commit")),
        ("supervisor embedded supervisor", supervisor.get("embedded_supervisor_commit")),
        ("supervisor embedded verifier", supervisor.get("embedded_verifier_commit")),
        ("producer", producer.get("source_commit")),
        ("producer embedded protocol", producer.get("embedded_protocol_commit")),
        ("producer embedded source", producer.get("embedded_source_commit")),
        ("verifier", verifier.get("verifier_commit")),
        ("verifier embedded", verifier.get("embedded_verifier_commit")),
    ]
    for label, value in commits:
        _require(
            isinstance(value, str) and COMMIT_RE.fullmatch(value) is not None and value != "0" * 40,
            f"{label} commit must be nonzero exact lowercase 40-hex",
            errors,
        )
    if isinstance(executables, dict) and isinstance(protocol, dict):
        _exact(supervisor.get("source_commit"), producer.get("source_commit"), "supervisor and producer source commit", errors)
        _exact(supervisor.get("embedded_protocol_commit"), protocol.get("commit"), "supervisor embedded protocol commit", errors)
        _exact(supervisor.get("embedded_supervisor_commit"), supervisor.get("source_commit"), "supervisor embedded supervisor commit", errors)
        _exact(supervisor.get("embedded_verifier_commit"), verifier.get("verifier_commit"), "supervisor embedded verifier commit", errors)
        _exact(supervisor.get("embedded_build_profile"), "release", "supervisor embedded build profile", errors)
        _exact(supervisor.get("embedded_supervisor_dirty"), False, "supervisor embedded dirty flag", errors)
        _exact(supervisor.get("embedded_git_metadata_present"), True, "supervisor embedded Git metadata flag", errors)
        _exact(producer.get("embedded_protocol_commit"), protocol.get("commit"), "producer embedded protocol commit", errors)
        _exact(producer.get("embedded_source_commit"), producer.get("source_commit"), "producer embedded source commit", errors)
        _exact(verifier.get("embedded_verifier_commit"), verifier.get("verifier_commit"), "verifier embedded commit", errors)

    run_id = run.get("run_id") if isinstance(run, dict) else None
    run_dir_text = run.get("run_dir") if isinstance(run, dict) else None
    _require(
        isinstance(run_id, str) and ROLE1_RUN_ID_RE.fullmatch(run_id) is not None,
        "run id must be a newly allocated RUN-SCURVE-six-lower-hex identifier",
        errors,
    )
    run_path = _normalized_absolute_path(run_dir_text, "decision run_dir", errors)
    if run_path is not None:
        _exact(run_path.name, run_id, "run directory basename", errors)
        if isinstance(run_id, str):
            expected_run_path = (
                repository_root / "experiments/EXP-SCURVE-1a8daf/runs" / run_id
            )
            _exact(run_path, expected_run_path, "canonical experiment run directory", errors)
        linked = _symlink_component(run_path)
        _require(linked is None, f"run directory contains symlink component: {linked}", errors)
        if phase == "pre-dispatch":
            _require(not os.path.lexists(run_path), "pre-dispatch run directory already exists", errors)
            parent = run_path.parent
            while not os.path.lexists(parent) and parent != parent.parent:
                parent = parent.parent
            try:
                parent_metadata = os.lstat(parent)
                _require(stat.S_ISDIR(parent_metadata.st_mode), "nearest run directory ancestor is not a directory", errors)
                _require(not stat.S_ISLNK(parent_metadata.st_mode), "nearest run directory ancestor may not be a symlink", errors)
                _require(os.access(parent, os.W_OK | os.X_OK), "nearest run directory ancestor is not writable/searchable", errors)
            except OSError as exc:
                errors.append(f"run directory ancestor: {exc}")
        else:
            _require(supplied_run_dir is not None, "post-run requires --run-dir", errors)
            if supplied_run_dir is not None:
                _exact(str(supplied_run_dir), run_dir_text, "post-run supplied run directory", errors)
            try:
                metadata = os.lstat(run_path)
                _require(stat.S_ISDIR(metadata.st_mode), "post-run path is not a directory", errors)
                _require(not stat.S_ISLNK(metadata.st_mode), "post-run directory may not be a symlink", errors)
            except OSError as exc:
                errors.append(f"post-run directory: {exc}")

    if isinstance(run_dir_text, str):
        expected_producer, expected_verifier = _resolved_argv(run_dir_text)
        _exact(authorization.get("producer_argv"), expected_producer, "decision resolved producer argv", errors)
        _exact(authorization.get("verifier_argv"), expected_verifier, "decision resolved verifier argv", errors)
    _exact(
        authorization.get("supervisor_argv"),
        _resolved_supervisor_argv(authorization),
        "decision resolved supervisor argv",
        errors,
    )
    audit_record = authorization.get("dependency_audit", {})
    audit_record = audit_record if isinstance(audit_record, dict) else {}
    audit_path = _normalized_absolute_path(
        audit_record.get("path"), "decision dependency audit path", errors,
    )
    if audit_path is not None and run_path is not None:
        _exact(
            audit_path,
            run_path / "dependency-audit.json",
            "RUN_DIR-contained dependency audit path",
            errors,
        )
        if phase == "pre-dispatch":
            _require(not os.path.lexists(audit_path), "pre-dispatch dependency audit already exists", errors)
        else:
            try:
                audit_metadata = os.lstat(audit_path)
                _require(stat.S_ISREG(audit_metadata.st_mode), "post-run dependency audit is not regular", errors)
                _require(not stat.S_ISLNK(audit_metadata.st_mode), "post-run dependency audit may not be a symlink", errors)
            except OSError as exc:
                errors.append(f"post-run dependency audit: {exc}")
    decided_at = decision.get("decided_at")
    decision_id = decision.get("id")
    if isinstance(decided_at, str) and isinstance(decision_id, str):
        _exact(decision_id[4:12], decided_at.replace("-", ""), "decision id/date binding", errors)
    evidence_refs = decision.get("evidence_refs", [])
    evidence_refs = evidence_refs if isinstance(evidence_refs, list) else []
    _require(ADDENDUM_RELATIVE in evidence_refs, "decision evidence_refs omits Role-1 addendum", errors)
    _require(INTERFACE_MANIFEST_RELATIVE in evidence_refs, "decision evidence_refs omits interface manifest", errors)

    binary_paths: list[Path] = []
    binary_hashes: list[Any] = []
    if isinstance(executables, dict):
        for role in ("supervisor", "producer", "verifier"):
            record = executables.get(role, {})
            path = _hash_admitted_binary(record, role, errors)
            if path is not None:
                binary_paths.append(path)
            if isinstance(record, dict):
                digest = record.get("binary_sha256")
                binary_hashes.append(digest)
                _require(digest != "0" * 64, f"{role} binary hash may not be zero-filled", errors)
    _require(len(binary_paths) == 3 and len(set(binary_paths)) == 3, "supervisor, producer, and verifier binary paths must be distinct", errors)
    _require(
        len(binary_hashes) == 3
        and all(isinstance(digest, str) for digest in binary_hashes)
        and len(set(binary_hashes)) == 3,
        "supervisor, producer, and verifier binary hashes must be distinct",
        errors,
    )
    package_paths = [
        _validate_source_checkout(
            supervisor, "source_commit", "supervisor", errors,
            check_git=check_source_git,
        ),
        _validate_source_checkout(
            producer, "source_commit", "producer", errors,
            check_git=check_source_git,
        ),
        _validate_source_checkout(
            verifier, "verifier_commit", "verifier", errors,
            check_git=check_source_git,
        ),
    ]
    _require(
        package_paths[1] is not None and package_paths[2] is not None
        and package_paths[1] != package_paths[2],
        "producer and verifier package paths must be distinct",
        errors,
    )
    if package_paths[1] is not None and package_paths[2] is not None:
        try:
            pre_dispatch_screen = compute_source_clone_screen(
                package_paths[1] / "src", package_paths[2] / "src",
            )
            _exact(
                pre_dispatch_screen.get("overall_status"), "PASS",
                "decision source clone-screen precondition", errors,
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"decision source clone-screen precondition: {exc}")
    return authorization, run_path


def _validate_post_run_bindings(
    run_dir: Path, authorization: dict[str, Any], decision: dict[str, Any],
    decision_bytes: bytes, decision_commit: str, decision_relative: str,
    repository_root: Path, errors: list[str],
) -> None:
    required = (
        "verification.json", "independent-verification.json",
        "independent-verifier-receipt.json", "dependency-audit.json",
        "environment.json", "raw-result.json", "manifest.yaml", "command.txt",
    )
    if any(not (run_dir / name).is_file() for name in required):
        return
    documents = {
        name: _load_canonical_json(run_dir / name, name, errors)
        for name in required if name != "command.txt"
    }
    executable_records = authorization.get("executables", {})
    executable_records = executable_records if isinstance(executable_records, dict) else {}
    producer_record = executable_records.get("producer", {})
    verifier_record = executable_records.get("verifier", {})
    supervisor_record = executable_records.get("supervisor", {})
    producer_record = producer_record if isinstance(producer_record, dict) else {}
    verifier_record = verifier_record if isinstance(verifier_record, dict) else {}
    supervisor_record = supervisor_record if isinstance(supervisor_record, dict) else {}
    protocol_record = authorization.get("protocol", {})
    protocol_record = protocol_record if isinstance(protocol_record, dict) else {}
    protocol_commit = protocol_record.get("commit")
    producer_commit = producer_record.get("source_commit")
    verifier_commit = verifier_record.get("verifier_commit")
    producer = documents["verification.json"]
    verifier = documents["independent-verification.json"]
    receipt = documents["independent-verifier-receipt.json"]
    dependency_audit = documents["dependency-audit.json"]
    environment = documents["environment.json"]
    raw_result = documents["raw-result.json"]
    manifest = documents["manifest.yaml"].get("run", {})
    manifest = manifest if isinstance(manifest, dict) else {}
    decision_binding = _mapping(receipt.get("decision_binding"))
    _exact(decision_binding.get("decision_id"), decision.get("id"), "decision binding retained decision id", errors)
    _exact(
        decision_binding.get("decision_path"),
        str(repository_root / decision_relative),
        "decision binding retained decision path",
        errors,
    )
    _exact(decision_binding.get("decision_commit"), decision_commit, "decision binding retained decision commit", errors)
    _exact(
        decision_binding.get("decision_sha256"),
        hashlib.sha256(decision_bytes).hexdigest(),
        "decision binding retained decision bytes",
        errors,
    )
    _exact(decision_binding.get("decision_git_mode"), "100644", "decision binding retained decision Git mode", errors)
    _exact(
        decision_binding.get("protocol_repository_path"),
        str(repository_root),
        "decision binding retained protocol repository",
        errors,
    )
    _exact(decision_binding.get("protocol_checkout_head"), decision_commit, "decision binding retained protocol HEAD", errors)
    _exact(decision_binding.get("protocol_worktree_clean_before_run"), True, "decision binding retained clean pre-run checkout", errors)
    _exact(decision_binding.get("protocol_commit_is_strict_ancestor"), True, "decision binding retained protocol ancestry", errors)
    _exact(decision_binding.get("protected_protocol_paths_unchanged"), True, "decision binding retained protected paths", errors)
    _exact(
        raw_result.get("receipt_sha256"),
        sha256_file(run_dir / "independent-verifier-receipt.json"),
        "decision binding raw-result receipt hash chain",
        errors,
    )
    for label in (
        "verification.json", "independent-verification.json",
        "independent-verifier-receipt.json", "environment.json",
        "raw-result.json",
    ):
        document = documents[label]
        _exact(document.get("protocol_commit"), protocol_commit, f"decision binding {label} protocol commit", errors)
        _exact(document.get("source_commit"), producer_commit, f"decision binding {label} source commit", errors)
    _exact(verifier.get("verifier_commit"), verifier_commit, "decision binding verifier commit", errors)
    _exact(receipt.get("verifier_commit"), verifier_commit, "decision binding receipt verifier commit", errors)
    _exact(producer.get("producer_binary_sha256"), producer_record.get("binary_sha256"), "decision binding producer verification binary", errors)
    _exact(verifier.get("verifier_binary_sha256"), verifier_record.get("binary_sha256"), "decision binding independent verification binary", errors)
    run_record = authorization.get("run", {})
    run_record = run_record if isinstance(run_record, dict) else {}
    _exact(receipt.get("run_dir"), run_record.get("run_dir"), "decision binding receipt run_dir", errors)
    receipt_wrapper = _mapping(receipt.get("wrapper"))
    _exact(receipt_wrapper.get("binary_sha256"), supervisor_record.get("binary_sha256"), "decision binding supervisor binary", errors)
    _exact(receipt_wrapper.get("contains_curve_arithmetic"), False, "decision binding supervisor arithmetic exclusion", errors)
    child_producer = _mapping(receipt.get("producer"))
    child_verifier = _mapping(receipt.get("verifier"))
    _exact(child_producer.get("binary_sha256"), producer_record.get("binary_sha256"), "decision binding producer child binary", errors)
    _exact(child_producer.get("commit"), producer_commit, "decision binding producer child commit", errors)
    _exact(child_producer.get("argv"), authorization.get("producer_argv"), "decision binding producer child argv", errors)
    _exact(child_verifier.get("binary_sha256"), verifier_record.get("binary_sha256"), "decision binding verifier child binary", errors)
    _exact(child_verifier.get("commit"), verifier_commit, "decision binding verifier child commit", errors)
    _exact(child_verifier.get("argv"), authorization.get("verifier_argv"), "decision binding verifier child argv", errors)
    for role, child in (("producer", child_producer), ("verifier", child_verifier)):
        _exact(child.get("build_profile"), "release", f"decision binding {role} release profile", errors)
        _exact(child.get("worktree_clean"), True, f"decision binding {role} clean tree", errors)
        _exact(child.get("exit_code"), 0, f"decision binding {role} exit code", errors)
    receipt_audit = _mapping(receipt.get("dependency_audit"))
    _exact(receipt_audit.get("verifier_crypto_lib_found"), False, "decision binding verifier dependency audit", errors)
    _exact(receipt_audit.get("shared_implementation_components"), [], "decision binding shared components", errors)
    _exact(receipt.get("overall_status"), "PASS", "decision binding receipt status", errors)
    expected_supervisor_argv = authorization.get("supervisor_argv")
    _exact(
        (run_dir / "command.txt").read_bytes(),
        _canonical_json_bytes(expected_supervisor_argv),
        "decision binding command.txt exact supervisor argv bytes",
        errors,
    )
    authorization_audit = _mapping(authorization.get("dependency_audit"))
    audit_path = authorization_audit.get("path")
    _exact(audit_path, str(run_dir / "dependency-audit.json"), "decision binding audit path", errors)
    _exact(
        sha256_file(run_dir / "dependency-audit.json"),
        receipt_audit.get("audit_output_sha256"),
        "decision binding dependency audit hash",
        errors,
    )
    recomputed_source_rows: dict[str, list[dict[str, str]]] = {}
    for role, record, commit_field in (
        ("producer", producer_record, "source_commit"),
        ("verifier", verifier_record, "verifier_commit"),
    ):
        git_record = dependency_audit.get(f"{role}_git", {})
        git_record = git_record if isinstance(git_record, dict) else {}
        _exact(git_record.get("git_top_level"), record.get("repository_path"), f"decision binding {role} audit repository path", errors)
        _exact(git_record.get("package_root"), record.get("package_path"), f"decision binding {role} audit package path", errors)
        _exact(git_record.get("git_head"), record.get(commit_field), f"decision binding {role} audit commit", errors)
        package_path = record.get("package_path")
        if isinstance(package_path, str):
            try:
                rows = _collect_rust_hash_rows(Path(package_path))
                recomputed_source_rows[role] = rows
                _exact(
                    dependency_audit.get(f"{role}_rust_sources"), rows,
                    f"decision binding {role} Rust source hashes",
                    errors,
                )
                cargo_toml = Path(package_path) / "Cargo.toml"
                _exact(
                    dependency_audit.get(f"{role}_cargo_toml_sha256"),
                    sha256_file(cargo_toml),
                    f"decision binding {role} Cargo.toml hash",
                    errors,
                )
                if role == "verifier":
                    _exact(
                        dependency_audit.get("verifier_cargo_lock_sha256"),
                        sha256_file(Path(package_path) / "Cargo.lock"),
                        "decision binding verifier Cargo.lock hash",
                        errors,
                    )
            except (OSError, ValueError) as exc:
                errors.append(f"decision binding {role} source audit recomputation: {exc}")
    if set(recomputed_source_rows) == {"producer", "verifier"}:
        producer_digests = {
            row["sha256"] for row in recomputed_source_rows["producer"]
        }
        identical = [
            row for row in recomputed_source_rows["verifier"]
            if row["sha256"] in producer_digests
        ]
        _exact(
            dependency_audit.get("identical_source_hashes"), identical,
            "decision binding identical Rust source hashes",
            errors,
        )
    clone_screen = dependency_audit.get("source_clone_screen", {})
    clone_screen = clone_screen if isinstance(clone_screen, dict) else {}
    _exact(clone_screen.get("producer_root"), str(Path(str(producer_record.get("package_path"))) / "src"), "decision binding clone producer root", errors)
    _exact(clone_screen.get("verifier_root"), str(Path(str(verifier_record.get("package_path"))) / "src"), "decision binding clone verifier root", errors)
    producer_package = producer_record.get("package_path")
    verifier_package = verifier_record.get("package_path")
    if isinstance(producer_package, str) and isinstance(verifier_package, str):
        try:
            recomputed_clone_screen = compute_source_clone_screen(
                Path(producer_package) / "src", Path(verifier_package) / "src",
            )
            _exact(
                clone_screen, recomputed_clone_screen,
                "decision binding independently recomputed source clone screen",
                errors,
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"decision binding source clone recomputation: {exc}")
    _exact(raw_result.get("protocol_commit"), protocol_commit, "decision binding raw-result protocol commit", errors)
    _exact(raw_result.get("source_commit"), producer_commit, "decision binding raw-result source commit", errors)
    _exact(raw_result.get("verifier_commit"), verifier_commit, "decision binding raw-result verifier commit", errors)
    _exact(raw_result.get("run_id"), run_record.get("run_id"), "decision binding raw-result run id", errors)
    _exact(raw_result.get("run_dir"), run_record.get("run_dir"), "decision binding raw-result run_dir", errors)
    _exact(environment.get("supervisor_binary_sha256"), supervisor_record.get("binary_sha256"), "decision binding environment supervisor binary", errors)
    _exact(environment.get("producer_binary_sha256"), producer_record.get("binary_sha256"), "decision binding environment producer binary", errors)
    _exact(environment.get("verifier_binary_sha256"), verifier_record.get("binary_sha256"), "decision binding environment verifier binary", errors)
    supervisor_build = environment.get("supervisor_build", {})
    supervisor_build = supervisor_build if isinstance(supervisor_build, dict) else {}
    for field in SUPERVISOR_BUILD_KEYS:
        _exact(
            supervisor_build.get(field), supervisor_record.get(field),
            f"decision binding environment supervisor build {field}", errors,
        )
    manifest_code = manifest.get("code", {})
    manifest_code = manifest_code if isinstance(manifest_code, dict) else {}
    _exact(manifest_code.get("repository"), supervisor_record.get("repository"), "decision binding manifest supervisor repository", errors)
    _exact(manifest_code.get("commit"), supervisor_record.get("source_commit"), "decision binding manifest supervisor commit", errors)
    _exact(manifest_code.get("supervisor_binary_sha256"), supervisor_record.get("binary_sha256"), "decision binding manifest supervisor binary", errors)


def validate_dispatch_decision(
    decision_path: Path, decision_commit: str, phase: str,
    run_dir: Path | None = None, *, repository_root: Path = ROOT,
    check_git: bool = True,
) -> list[str]:
    """Validate a committed Role-1-only decision without launching a child."""

    errors: list[str] = []
    _require(phase in {"pre-dispatch", "post-run"}, "decision phase must be pre-dispatch or post-run", errors)
    if phase not in {"pre-dispatch", "post-run"}:
        return errors
    actual_path = decision_path if decision_path.is_absolute() else repository_root / decision_path
    try:
        decision_bytes = actual_path.read_bytes()
        document = load_yaml_strict(actual_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"decision load: {exc}"]
    try:
        schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
        import jsonschema
        validation_errors = sorted(
            jsonschema.Draft202012Validator(schema).iter_errors(document),
            key=lambda item: item.json_path,
        )
        for error in validation_errors:
            errors.append(f"decision schema {error.json_path}: {error.message}")
    except (ImportError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"decision schema unavailable: {exc}")
        return errors
    if validation_errors:
        return errors
    if not isinstance(document, dict):
        return errors + ["decision document must be a mapping"]
    decision = document.get("coordinator_decision", {})
    if not isinstance(decision, dict):
        return errors + ["coordinator_decision must be a mapping"]
    relative = _decision_relative_path(
        decision_path, decision.get("id"), repository_root, errors,
    )
    authorization, resolved_run_dir = _validate_decision_semantics(
        decision, decision_commit, phase, run_dir, repository_root, errors,
        check_source_git=check_git,
    )
    if check_git and relative is not None and isinstance(authorization, dict):
        _validate_git_decision_binding(
            repository_root, relative, decision_bytes, decision_commit,
            authorization, phase, errors,
        )
    if phase == "post-run" and resolved_run_dir is not None and relative is not None:
        _validate_post_run_bindings(
            resolved_run_dir, authorization, decision, decision_bytes,
            decision_commit, relative, repository_root, errors,
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, help="read-only validation of an existing Role-1 directory")
    parser.add_argument("--decision", type=Path, help="fresh committed Role-1 Coordinator decision")
    parser.add_argument("--decision-commit", help="exact 40-hex commit containing --decision")
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument("--pre-dispatch", action="store_true", help="validate admission and require a fresh absent RUN_DIR")
    phase.add_argument("--post-run", action="store_true", help="validate admission, receipt, and existing RUN_DIR")
    arguments = parser.parse_args(argv)
    any_decision_argument = (
        arguments.decision is not None or arguments.decision_commit is not None
        or arguments.pre_dispatch or arguments.post_run
    )
    if any_decision_argument:
        if arguments.decision is None or arguments.decision_commit is None:
            parser.error("--decision and --decision-commit are required together")
        if not arguments.pre_dispatch and not arguments.post_run:
            parser.error("a decision requires exactly one of --pre-dispatch or --post-run")
        if arguments.pre_dispatch and arguments.run_dir is not None:
            parser.error("--pre-dispatch forbids --run-dir; the decision binds its fresh path")
        if arguments.post_run and arguments.run_dir is None:
            parser.error("--post-run requires --run-dir")
    elif arguments.run_dir is not None:
        parser.error("--run-dir is accepted only with --decision, --decision-commit, and --post-run")
    errors = validate_contract()
    if arguments.run_dir is not None:
        errors.extend(validate_run_directory(arguments.run_dir))
    if arguments.decision is not None:
        errors.extend(validate_dispatch_decision(
            arguments.decision,
            arguments.decision_commit,
            "pre-dispatch" if arguments.pre_dispatch else "post-run",
            arguments.run_dir,
        ))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: immutable v2 binding and exact role-1 interface contract")
    print("PASS: REF-0 is fixed at 1025 records and remains non-scientific")
    print("PASS: the immutable addendum keeps execution authorization false; this checker launched no run")
    if arguments.run_dir is not None:
        print(f"PASS: existing Role-1 artifacts validated read-only at {arguments.run_dir}")
    if arguments.pre_dispatch:
        print("PASS: fresh Coordinator decision authorizes only one Role-1 REF-0 preflight")
        print("PASS: pre-dispatch binaries, argv, commits, and absent RUN_DIR are bound")
    if arguments.post_run:
        print("PASS: post-run artifacts and supervisor receipt are bound to the decision")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
