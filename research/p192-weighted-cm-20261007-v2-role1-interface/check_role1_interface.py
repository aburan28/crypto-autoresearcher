#!/usr/bin/env python3
"""Static checker for the non-executing P-192 role-1 interface addendum.

The checker binds the immutable v2 archive and validates only schemas, argv,
artifact names, REF-0 arithmetic, and pending state.  It does not factor a norm,
run a sieve, construct a relation, or launch either native binary.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
ADDENDUM_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml"
OVERLAY_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/run-family.role1-interface.yaml"
SCHEMA_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json"
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
    "controls.json": "controls",
    "reference-box.json": "referenceBox",
    "verification.json": "producerVerification",
    "independent-verification.json": "independentVerification",
    "independent-agreement.json": "independentAgreement",
    "independent-verifier-receipt.json": "verifierReceipt",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
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


def validate_contract(
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
        addendum = addendum_root["role1_interface_addendum"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
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
    _exact(stage.get("immutable_v2_required_outputs"), V2_OUTPUTS, "v2 output list", errors)
    _exact(stage.get("addendum_required_children"), CHILD_OUTPUTS, "addendum child list", errors)
    ownership = stage.get("ownership", {})
    _exact(ownership.get("producer"), PRODUCER_OWNED, "producer ownership", errors)
    _exact(ownership.get("independent_verifier"), ["independent-verification.json"], "verifier ownership", errors)
    _exact(ownership.get("non_arithmetic_supervisor"), ["independent-agreement.json", "independent-verifier-receipt.json"], "supervisor ownership", errors)

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
    _exact(overlay.get("immutable_v2_required_outputs"), V2_OUTPUTS, "overlay v2 outputs", errors)
    _exact(overlay.get("addendum_required_children"), CHILD_OUTPUTS, "overlay children", errors)
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
    d23 = fixtures.get("D23-ORDER3", {})
    for key, expected in D23_FIXTURE.items():
        _exact(d23.get(key), expected, f"D23 fixture {key}", errors)
    mutation_fixture = fixtures.get("MUTATION-REJECTION", {})
    _exact(set(mutation_fixture), {
        "default_base_fixture", "hash_rule", "target_path_rule",
        "mutations_in_order", "expected",
    }, "mutation fixture keys", errors)
    _exact(mutation_fixture.get("default_base_fixture"), "D23-ORDER3", "default mutation base fixture", errors)
    _exact(mutation_fixture.get("hash_rule"), MUTATION_HASH_RULE, "mutation hash rule", errors)
    _exact(mutation_fixture.get("target_path_rule"), MUTATION_TARGET_PATH_RULE, "mutation target path rule", errors)
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

    _exact(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema", "JSON Schema draft", errors)
    definitions = schema.get("$defs", {})
    for definition in ("identity", "maximalOrder", "controls", "referenceBox", "producerVerification", "independentVerification", "independentAgreement", "verifierReceipt"):
        _require(definition in definitions, f"JSON Schema missing $defs/{definition}", errors)
    schema_consts = {
        "identity": "p192-wcm-identity-v1",
        "maximalOrder": "p192-wcm-maximal-order-v1",
        "controls": "p192-wcm-controls-v1",
        "referenceBox": "p192-wcm-reference-box-v1",
        "producerVerification": "p192-wcm-verification-v1",
        "independentVerification": "p192-wcm-independent-verification-v1",
        "independentAgreement": "p192-wcm-independent-agreement-v1",
        "verifierReceipt": "p192-wcm-independent-verifier-receipt-v1",
    }
    for definition, expected in schema_consts.items():
        actual = definitions.get(definition, {}).get("properties", {}).get("schema", {}).get("const")
        _exact(actual, expected, f"JSON Schema {definition} discriminator", errors)
        _exact(definitions.get(definition, {}).get("additionalProperties"), False, f"JSON Schema {definition} closed keys", errors)
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
    except ImportError:
        pass
    except Exception as exc:  # jsonschema raises a hierarchy of schema errors.
        errors.append(f"JSON Schema meta-validation: {exc}")

    source_binding = addendum.get("source_commit_binding", {})
    for key in ("protocol_commit", "source_commit", "verifier_commit", "binary_binding"):
        _require(isinstance(source_binding.get(key), str) and source_binding[key], f"source binding missing {key}", errors)
    _require("P192_WCM_PROTOCOL_COMMIT" in source_binding.get("protocol_commit", ""), "protocol build variable missing", errors)
    _require("P192_WCM_SOURCE_COMMIT" in source_binding.get("source_commit", ""), "source build variable missing", errors)
    _require("P192_WCM_VERIFIER_COMMIT" in source_binding.get("verifier_commit", ""), "verifier build variable missing", errors)
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


def _canonical_json_bytes(value: Any) -> bytes:
    """RFC-8785 bytes for this contract's integer/string-only JSON subset."""

    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


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
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
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


def _artifact_record(run_dir: Path, relative: str) -> dict[str, Any]:
    data = (run_dir / relative).read_bytes()
    return {"path": relative, "byte_length": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _validate_verdicts(
    document: dict[str, Any], expected_ids: list[str], label: str,
    errors: list[str],
) -> None:
    checks = document.get("checks", [])
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
    if len(candidate_shards) == 1:
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
    if len(disposition_shards) == 1:
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


def validate_run_directory(run_dir: Path) -> list[str]:
    """Validate an already-produced Role-1 directory; never launches a run."""

    errors: list[str] = []
    required = set(V2_OUTPUTS) | set(CHILD_OUTPUTS)
    for relative in sorted(required):
        path = run_dir / relative
        _require(path.is_file(), f"run artifact missing: {relative}", errors)
        _require(not path.is_symlink(), f"run artifact may not be a symlink: {relative}", errors)
    if errors:
        return errors
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    documents: dict[str, dict[str, Any]] = {}
    try:
        import jsonschema
    except ImportError:
        return ["runtime validation requires jsonschema"]
    for relative in SCHEMA_FILES:
        document = _load_canonical_json(run_dir / relative, relative, errors)
        documents[relative] = document
        try:
            jsonschema.validate(document, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{relative}: schema: {exc.message}")

    factor_base = _load_canonical_json(run_dir / "factor-base.json", "factor-base.json", errors)
    factor_keys = [
        "schema", "curve_uid", "p", "t", "D", "algebraic_bound",
        "mappable_bound", "source_commit", "entry_count", "entries",
    ]
    _exact(set(factor_base), set(factor_keys), "factor-base exact top-level keys", errors)
    _exact(factor_base.get("schema"), "p192-wcm-factor-base-v1", "factor-base schema", errors)
    entries = factor_base.get("entries", [])
    _exact(factor_base.get("entry_count"), len(entries), "factor-base entry count", errors)
    if isinstance(entries, list):
        ells = [item.get("ell") for item in entries if isinstance(item, dict)]
        _require(ells == sorted(set(ells)), "factor-base entries not strictly increasing", errors)
        for index, entry in enumerate(entries):
            _exact(set(entry), {"ell", "kind", "kronecker", "roots", "positive_root_index"}, f"factor-base entry {index} keys", errors)
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
    receipt = documents["independent-verifier-receipt.json"]

    _validate_verdicts(identity, IDENTITY_CHECKS, "identity", errors)
    _validate_verdicts(maximal, ORDER_CHECKS, "maximal-order", errors)
    _validate_verdicts(producer, PRODUCER_CHECKS, "producer verification", errors)
    _validate_verdicts(verifier, VERIFIER_CHECKS, "independent verification", errors)

    control_records = controls.get("controls", [])
    observed_controls: list[tuple[str | None, list[str | None]]] = []
    for record in control_records:
        assertions = record.get("assertions", []) if isinstance(record, dict) else []
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
        record.get("status") == "PASS" for record in control_records
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
    _exact([record.get("field") for record in comparison_records], COMPARISONS, "agreement field order", errors)
    for record in comparison_records:
        field = record.get("field")
        if field in expected_bindings:
            _exact(record.get("producer"), expected_bindings[field], f"agreement {field} producer", errors)
            _exact(record.get("verifier"), expected_bindings[field], f"agreement {field} verifier", errors)
            _exact(record.get("equal"), True, f"agreement {field} equality", errors)
    expected_agreement_status = "PASS" if len(comparison_records) == len(COMPARISONS) and all(
        record.get("equal") is True for record in comparison_records
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
    _require(len(set(commits)) == 1, "protocol_commit differs across artifacts", errors)
    sources = [
        identity.get("source_commit"), maximal.get("source_commit"),
        controls.get("source_commit"), reference.get("source_commit"),
        producer.get("source_commit"), verifier.get("source_commit"),
        agreement.get("source_commit"), receipt.get("source_commit"),
        factor_base.get("source_commit"),
    ]
    _require(len(set(sources)) == 1, "source_commit differs across artifacts", errors)
    _exact(receipt.get("verifier_commit"), verifier.get("verifier_commit"), "receipt verifier commit", errors)
    _exact(receipt.get("producer_artifacts_before"), expected_verifier_inventory, "receipt before inventory", errors)
    _exact(receipt.get("producer_artifacts_after"), expected_verifier_inventory, "receipt after inventory", errors)
    _exact(receipt.get("producer_artifacts_before"), receipt.get("producer_artifacts_after"), "receipt before/after byte stability", errors)
    _exact(receipt.get("agreement_sha256"), sha256_file(run_dir / "independent-agreement.json"), "receipt agreement hash", errors)
    _exact(receipt.get("agreement_path"), "independent-agreement.json", "receipt agreement path", errors)
    child_producer = receipt.get("producer", {})
    child_verifier = receipt.get("verifier", {})
    _exact(child_producer.get("binary_sha256"), producer.get("producer_binary_sha256"), "producer binary binding", errors)
    _exact(child_producer.get("commit"), sources[0], "producer child commit", errors)
    _exact(child_verifier.get("binary_sha256"), verifier.get("verifier_binary_sha256"), "verifier binary binding", errors)
    _exact(child_verifier.get("commit"), verifier.get("verifier_commit"), "verifier child commit", errors)
    run_dir_text = receipt.get("run_dir", "")
    resolved_producer_argv = [run_dir_text if item == "RUN_DIR" else item.replace("RUN_DIR/", run_dir_text.rstrip("/") + "/") for item in PRODUCER_ARGV]
    resolved_verifier_argv = [run_dir_text if item == "RUN_DIR" else item.replace("RUN_DIR/", run_dir_text.rstrip("/") + "/") for item in VERIFIER_ARGV]
    _exact(child_producer.get("argv"), resolved_producer_argv, "receipt producer argv", errors)
    _exact(child_verifier.get("argv"), resolved_verifier_argv, "receipt verifier argv", errors)
    sequence = [
        child_producer.get("started_sequence"), child_producer.get("completed_sequence"),
        child_verifier.get("started_sequence"), child_verifier.get("completed_sequence"),
    ]
    _require(all(isinstance(value, int) for value in sequence) and sequence == sorted(set(sequence)), "receipt child sequence is not strictly ordered", errors)
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
        and receipt.get("dependency_audit", {}).get("verifier_crypto_lib_found") is False
        and receipt.get("dependency_audit", {}).get("shared_implementation_components") == []
    )
    _exact(receipt.get("overall_status"), "PASS" if receipt_pass else "FAIL", "receipt status logic", errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, help="read-only validation of an existing Role-1 directory")
    arguments = parser.parse_args(argv)
    errors = validate_contract()
    if arguments.run_dir is not None:
        errors.extend(validate_run_directory(arguments.run_dir))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: immutable v2 binding and exact role-1 interface contract")
    print("PASS: REF-0 is fixed at 1025 records and remains non-scientific")
    print("PASS: execution authorization is false; no run was launched")
    if arguments.run_dir is not None:
        print(f"PASS: existing Role-1 artifacts validated read-only at {arguments.run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
