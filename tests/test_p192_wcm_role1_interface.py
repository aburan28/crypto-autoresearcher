from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py"
ADDENDUM_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml"
SCHEMA_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json"
DECISION_SCHEMA_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-dispatch-decision.schema.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("p192_role1_interface_checker", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


def load_addendum() -> dict:
    return yaml.safe_load(ADDENDUM_PATH.read_text(encoding="utf-8"))


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_decision_schema() -> dict:
    return json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _binary_record(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def make_decision_fixture(
    root: Path, asset_root: Path | None = None,
) -> tuple[dict, Path, Path, str]:
    decision_id = "DEC-20261007-abcdef"
    run_id = "RUN-SCURVE-abcdef"
    protocol_commit = "a" * 40
    source_commit = "b" * 40
    verifier_commit = "c" * 40
    decision_commit = "d" * 40
    assets = root if asset_root is None else asset_root
    native_repository = assets / "native"
    package_paths = {
        role: native_repository / relative
        for role, relative in CHECKER.PACKAGE_RELATIVES.items()
    }
    for package in package_paths.values():
        (package / "src").mkdir(parents=True)
        (package / "Cargo.toml").write_text("[package]\nname='fixture'\nversion='0.0.0'\n", encoding="utf-8")
        (package / "src/lib.rs").write_text("pub fn fixture() {}\n", encoding="utf-8")
    binary_dir = assets / "bin"
    binary_dir.mkdir()
    binary_paths = {}
    for role, payload in (
        ("supervisor", b"supervisor-fixture"),
        ("producer", b"producer-fixture"),
        ("verifier", b"verifier-fixture"),
    ):
        path = binary_dir / role
        path.write_bytes(payload)
        path.chmod(0o755)
        binary_paths[role] = path
    run_dir = root / "experiments/EXP-SCURVE-1a8daf/runs" / run_id
    run_dir.parent.mkdir(parents=True)
    decision_path = root / "ledger/decisions" / f"{decision_id}.yaml"
    decision_path.parent.mkdir(parents=True)

    supervisor_length, supervisor_hash = _binary_record(binary_paths["supervisor"])
    producer_length, producer_hash = _binary_record(binary_paths["producer"])
    verifier_length, verifier_hash = _binary_record(binary_paths["verifier"])
    authorization = {
        "schema": "p192-wcm-role1-preflight-authorization-v1",
        "execution_authorized": True,
        "scientific_execution_authorized": False,
        "scientific_result_recording_authorized": False,
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "decision_path": str(decision_path),
        "stage": {
            "label": "P192-WCM-PREFLIGHT",
            "ordinal": 1,
            "role": "composite_producer_and_isolated_verifier",
            "composite_invocations": 1,
            "retry_authorized": False,
            "resume_authorized": False,
            "advance_to_later_role_authorized": False,
            "unauthorized_stage_labels": CHECKER.UNAUTHORIZED_STAGE_LABELS,
            "custody_outputs": CHECKER.CUSTODY_OUTPUTS,
        },
        "run": {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "must_be_fresh": True,
            "existing_path_refused": True,
        },
        "protocol": {
            "repository": "https://github.com/aburan28/crypto-autoresearcher",
            "repository_path": str(root),
            "commit": protocol_commit,
            "must_be_ancestor_of_decision_commit": True,
            "protected_paths_unchanged_through_decision_commit": True,
            "protected_paths": CHECKER.PROTECTED_PROTOCOL_PATHS,
            "addendum": {
                "path": CHECKER.ADDENDUM_RELATIVE,
                "byte_length": 1,
                "sha256": "1" * 64,
            },
            "interface_manifest": {
                "path": CHECKER.INTERFACE_MANIFEST_RELATIVE,
                "byte_length": 1,
                "sha256": "2" * 64,
            },
        },
        "executables": {
            "supervisor": {
                "repository": "https://github.com/aburan28/crypto",
                "source_commit": source_commit,
                "repository_path": str(native_repository),
                "package_path": str(package_paths["supervisor"]),
                "binary_path": str(binary_paths["supervisor"]),
                "byte_length": supervisor_length,
                "binary_sha256": supervisor_hash,
                "build_profile": "release",
                "worktree_clean": True,
                "contains_curve_arithmetic": False,
                "embedded_protocol_commit": protocol_commit,
                "embedded_supervisor_commit": source_commit,
                "embedded_verifier_commit": verifier_commit,
                "embedded_build_profile": "release",
                "embedded_supervisor_dirty": False,
                "embedded_git_metadata_present": True,
            },
            "producer": {
                "repository": "https://github.com/aburan28/crypto",
                "source_commit": source_commit,
                "embedded_protocol_commit": protocol_commit,
                "embedded_source_commit": source_commit,
                "repository_path": str(native_repository),
                "package_path": str(package_paths["producer"]),
                "binary_path": str(binary_paths["producer"]),
                "byte_length": producer_length,
                "binary_sha256": producer_hash,
                "build_profile": "release",
                "worktree_clean": True,
            },
            "verifier": {
                "repository": "https://github.com/aburan28/crypto",
                "verifier_commit": verifier_commit,
                "embedded_verifier_commit": verifier_commit,
                "repository_path": str(native_repository),
                "package_path": str(package_paths["verifier"]),
                "binary_path": str(binary_paths["verifier"]),
                "byte_length": verifier_length,
                "binary_sha256": verifier_hash,
                "build_profile": "release",
                "worktree_clean": True,
                "crypto_lib_found": False,
                "shared_implementation_components": [],
            },
        },
        "dependency_audit": {
            "path": str(run_dir / "dependency-audit.json"),
            "schema": "p192-wcm-dependency-audit-v1",
            "must_be_fresh": True,
            "receipt_hash_field": "dependency_audit.audit_output_sha256",
            "hash_scope": "exact_raw_file_bytes",
        },
        "supervisor_argv": [],
        "producer_argv": CHECKER._resolved_argv(str(run_dir))[0],
        "verifier_argv": CHECKER._resolved_argv(str(run_dir))[1],
        "launch": {
            "no_path_search_for_any_executable": True,
            "runtime_commit_override_forbidden": True,
            "producer_before_verifier": True,
            "close_and_rehash_producer_outputs_before_verifier": True,
            "supervisor_writes_only_run_directory_artifacts": True,
            "verify_protocol_checkout_before_run_directory": True,
            "derive_and_retain_decision_binding": True,
        },
    }
    authorization["supervisor_argv"] = CHECKER._resolved_supervisor_argv(authorization)
    document = {
        "coordinator_decision": {
            "id": decision_id,
            "context": "Authorize only the frozen non-scientific Role-1 preflight.",
            "decision": "approve",
            "target_ids": ["EXP-SCURVE-1a8daf"],
            "rationale": ["All closed pre-dispatch bindings are present."],
            "evidence_refs": [CHECKER.ADDENDUM_RELATIVE, CHECKER.INTERFACE_MANIFEST_RELATIVE],
            "limitations": ["No scientific search or later role is authorized."],
            "next_actions": ["Run the closed pre-dispatch checker once."],
            "authorization": authorization,
            "knowledge_promotion": {
                "promoted": [],
                "not_warranted": "A non-scientific preflight is not research evidence.",
            },
            "decided_by": "coordinator",
            "decided_at": "2026-10-07",
        }
    }
    decision_path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return document, decision_path, run_dir, decision_commit


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return result.stdout.strip()


def identity_fixture() -> dict:
    return {
        "schema": "p192-wcm-identity-v1",
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "protocol_commit": "1" * 40,
        "source_commit": "2" * 40,
        "curve": {
            "name": "NIST P-192 / secp192r1",
            "model": "short Weierstrass y^2 = x^3 + a*x + b over F_p",
            "p": "6277101735386680763835789423207666416083908700390324961279",
            "a": "6277101735386680763835789423207666416083908700390324961276",
            "b": "2455155546008943817740293915197451784769108058161191238065",
            "generator_x_hex": "188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012",
            "generator_y_hex": "07192B95FFC8DA78631011ED6B24CDD573F977A11E794811",
            "n": "6277101735386680763835789423176059013767194773182842284081",
            "cofactor": 1,
            "trace_t": "31607402316713927207482677199",
            "icv1": "icv1-fp192-t31607402316713927207482677199-52e4af59",
            "ec1": "EC1P192Cp192h5531c4a08bdb",
            "curve_uid": "urn:ec-record:1:sha256:5531c4a08bdb64b6e86a6e30e9a08aa57edef7af15ac5f6d4d2a83a53bf2f646",
        },
        "derived": {
            "group_order": "6277101735386680763835789423176059013767194773182842284081",
            "frobenius_discriminant": "-24109379060336110122544161233113975664949272517896865359515",
        },
        "checks": [{"check_id": check_id, "status": "PASS"} for check_id in CHECKER.IDENTITY_CHECKS],
        "overall_status": "PASS",
    }


class Role1InterfaceContractTests(unittest.TestCase):
    def test_current_contract_passes(self) -> None:
        self.assertEqual(CHECKER.validate_contract(), [])

    def test_authorization_or_result_mutation_fails(self) -> None:
        document = load_addendum()
        amendment = document["role1_interface_addendum"]
        amendment["execution_authorized"] = True
        amendment["scientific_results"] = [{"fabricated": True}]
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("execution authorization" in error for error in errors))
        self.assertTrue(any("scientific results" in error for error in errors))

    def test_malformed_static_contract_fails_without_exception(self) -> None:
        for field in ("stage_binding", "canonical_v2_custody", "json_artifacts"):
            with self.subTest(field=field):
                document = load_addendum()
                document["role1_interface_addendum"][field] = 0
                errors = CHECKER.validate_contract(
                    addendum_document=document,
                    check_files=False,
                )
                self.assertTrue(any("static contract structure" in error for error in errors), errors)

    def test_argv_and_output_mutations_fail(self) -> None:
        document = load_addendum()
        stage = document["role1_interface_addendum"]["stage_binding"]
        stage["producer_argv_template"][4:6] = ["--sieve-bound", "65519"]
        stage["immutable_v2_required_outputs"].append("implicit-default.json")
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("producer argv" in error for error in errors))
        self.assertTrue(any("v2 output list" in error for error in errors))

    def test_ref0_literal_boundaries_and_bytes(self) -> None:
        pairs = CHECKER.ref0_pairs()
        self.assertEqual(len(pairs), 1025)
        self.assertEqual(pairs[0], (1, 1))
        self.assertEqual(pairs[511], (1, 1023))
        self.assertEqual(pairs[512], (2, 0))
        self.assertEqual(pairs[1024], (2, 1024))
        records = CHECKER.candidate_record_bytes()
        self.assertEqual(len(records), 16400)
        self.assertEqual(records[:16].hex(), "00000000000000010000000000000001")
        self.assertEqual(records[-16:].hex(), "00000000000000020000000000000400")

    def test_ref0_order_mutation_fails(self) -> None:
        document = load_addendum()
        mapping = document["role1_interface_addendum"]["reference_box"]["literal_index_mapping"]
        mapping[1]["x"] = "2*(1024-i)"
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("REF literal order" in error for error in errors))

    def test_control_subset_mutation_fails(self) -> None:
        document = load_addendum()
        controls = document["role1_interface_addendum"]["role1_control_subset"]["controls_in_order"]
        controls.pop()
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("role-1 controls" in error for error in errors))

    def test_role1_uses_in_memory_regeneration_not_external_rebuild(self) -> None:
        document = load_addendum()
        addendum = document["role1_interface_addendum"]
        resume_scope = addendum["reference_box"]["resume_scope"]
        self.assertIn("no external second-build or two-RUN_DIR comparison", resume_scope)
        self.assertIn("does not inject or claim recovery", resume_scope)
        determinism = addendum["reference_box"]["determinism_control"]
        self.assertEqual(determinism["regenerations_per_implementation"], 2)
        self.assertEqual(len(determinism["streams_compared_in_order"]), 3)
        self.assertEqual(len(determinism["roots_compared_in_order"]), 4)
        self.assertEqual(len(determinism["counters_compared_in_order"]), 7)
        self.assertIs(determinism["external_process_or_run_directory_comparison_claimed"], False)
        self.assertIs(determinism["crash_or_resume_claimed"], False)
        direction = next(
            item for item in addendum["role1_control_subset"]["controls_in_order"]
            if item["control_id"] == "REF0-DIRECTION-WORKERS"
        )
        expected_assertion = "independent_in_memory_ref0_regenerations_streams_roots_counters_equal"
        self.assertEqual(direction["assertions"][-1], expected_assertion)
        schema = load_schema()
        schema_assertions = schema["$defs"]["controls"]["properties"]["controls"]["prefixItems"][7]["allOf"][1]["properties"]["assertions"]["prefixItems"]
        self.assertEqual(
            schema_assertions[-1]["allOf"][1]["properties"]["assertion_id"]["const"],
            expected_assertion,
        )

    def test_identity_schema_is_closed_and_hashes_are_lowercase(self) -> None:
        schema = load_schema()
        fixture = identity_fixture()
        jsonschema.validate(fixture, schema)
        with_extra = copy.deepcopy(fixture)
        with_extra["unexpected"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(with_extra, schema)
        bad_hash = copy.deepcopy(fixture)
        bad_hash["protocol_commit"] = "A" * 40
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad_hash, schema)

    def test_reference_schema_forbids_family_root_fields(self) -> None:
        schema = load_schema()
        properties = schema["$defs"]["referenceBox"]["properties"]
        self.assertNotIn("candidate_family_sha256", properties)
        self.assertNotIn("disposition_family_sha256", properties)
        self.assertIs(schema["$defs"]["referenceBox"]["additionalProperties"], False)

    def test_recursive_pocklington_factor_forbids_authoritative_provenance(self) -> None:
        schema = load_schema()
        nested_authoritative = {
            "method": "authoritative_standard",
            "value": "3",
            "standard_id": "SEC2",
            "edition": "2.0",
            "section": "2.2.2",
            "document_url": "https://www.secg.org/sec2-v2.pdf",
            "document_sha256": "87b8f3703364ed5b21ba8582e411cc0cbf477bcaa3f4f45e0d6580d1c00d9952",
            "document_byte_length": 306784,
            "parameter_name": "secp192r1",
        }
        factor = {"prime": "3", "exponent": 1, "proof": nested_authoritative}
        factor_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": "#/$defs/pocklingtonFactor",
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(factor, factor_schema)

    def test_build_time_commit_bindings_are_frozen(self) -> None:
        binding = load_addendum()["role1_interface_addendum"]["source_commit_binding"]
        self.assertIn("P192_WCM_PROTOCOL_COMMIT", binding["protocol_commit"])
        self.assertIn("P192_WCM_SOURCE_COMMIT", binding["source_commit"])
        self.assertIn("P192_WCM_VERIFIER_COMMIT", binding["verifier_commit"])
        self.assertIn("runtime", binding["protocol_commit"])
        self.assertIn("Runtime", binding["verifier_commit"])
        self.assertIn("sole build receipts", binding["binary_binding"])
        self.assertIn("no additional unnamed build-receipt", binding["binary_binding"])
        supervisor = load_decision_schema()["$defs"]["supervisorBinary"]
        for field in CHECKER.SUPERVISOR_BUILD_KEYS:
            self.assertIn(field, supervisor["required"])

    def test_exact_control_fixture_mutation_fails(self) -> None:
        document = load_addendum()
        fixture = document["role1_interface_addendum"]["role1_control_fixtures"]["D23-ORDER3"]
        fixture["norm"] = "4"
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("D23 fixture norm" in error for error in errors))

    def test_sqrt_d_subgroup_scalar_is_independently_frozen(self) -> None:
        document = load_addendum()
        fixture = document["role1_interface_addendum"]["role1_control_fixtures"]["P192-SQRT-D"]
        self.assertEqual(fixture, CHECKER.SQRT_D_FIXTURE)
        fixture["derived_alpha_scalar_mod_n"] = "1"
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("P192 sqrt(D) fixture" in error for error in errors))

    def test_d23_mutation_target_path_drift_fails(self) -> None:
        document = load_addendum()
        mutations = document["role1_interface_addendum"]["role1_control_fixtures"]["MUTATION-REJECTION"]["mutations_in_order"]
        root = next(item for item in mutations if item["id"] == "root")
        root["target_field_path"] = "/role1_interface_addendum/role1_control_fixtures/D23-ORDER3/roots_mod_2/0"
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("semantic mutation fixtures" in error for error in errors))
        self.assertTrue(any("mutation root target before value" in error for error in errors))

    def test_lp_endpoint_mutation_is_exact_and_closed(self) -> None:
        document = load_addendum()
        fixtures = document["role1_interface_addendum"]["role1_control_fixtures"]
        mutation = next(
            item for item in fixtures["MUTATION-REJECTION"]["mutations_in_order"]
            if item["id"] == "lp_smaller_root"
        )
        self.assertEqual(mutation["before_value"], 1109020142)
        self.assertEqual(mutation["after_value"], 1109020143)
        self.assertEqual(
            [(item["value"]) for item in mutation["unchanged_field_values"]],
            [2147483647, 2025854371, 1, 1],
        )
        mutation["after_value"] = 1109020144
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("semantic mutation fixtures" in error for error in errors))

    def test_mutation_hash_carrier_is_exact_and_staged(self) -> None:
        document = load_addendum()
        mutation = document["role1_interface_addendum"]["role1_control_fixtures"]["MUTATION-REJECTION"]
        carrier = mutation["implementation_private_hash_carrier"]
        self.assertEqual(carrier["exact_internal_counts"], CHECKER.MUTATION_INTERNAL_COUNTS)
        self.assertIn("P192-WCM-MUTATION-RECORD-v1\\0", carrier["record_hash"])
        self.assertIn("P192-WCM-MUTATION-FILE-v1\\0", carrier["file_hash"])
        carrier["exact_internal_counts"]["semantic_rejections_after_hash_acceptance"] = 8
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("mutation carrier internal counts" in error for error in errors))

    def test_disposition_parser_enforces_indices_and_flags(self) -> None:
        data = b"".join(bytes([4]) + struct.pack(">Q", index) + b"\x00" for index in range(1025))
        errors: list[str] = []
        certificates, statuses = CHECKER._parse_dispositions(data, errors)
        self.assertEqual(errors, [])
        self.assertEqual(certificates, {})
        self.assertEqual(statuses, [4] * 1025)

        mutated = bytearray(data)
        mutated[1:9] = struct.pack(">Q", 1)
        errors = []
        CHECKER._parse_dispositions(bytes(mutated), errors)
        self.assertTrue(any("where 0 required" in error for error in errors))

    def test_unresolved_status_is_never_admission_eligible(self) -> None:
        statuses = [4] * 1024 + [6]
        status_counts = {
            "nonprimitive_duplicate": 0,
            "complete": 0,
            "one_large_prime": 0,
            "two_large_prime": 0,
            "rejected": 1024,
            "invalid": 0,
            "unresolved": 1,
        }
        errors: list[str] = []
        CHECKER._validate_status_completion(
            {"status_counts": status_counts, "complete": False}, statuses, errors,
        )
        self.assertTrue(any("reference admission unresolved count" in error for error in errors))
        self.assertTrue(any("reference admission complete" in error for error in errors))

    def test_empty_certificate_store_is_exactly_35_bytes(self) -> None:
        store = b"P192-WCM-REF-CERT-STORE-v1\0" + struct.pack(">Q", 0)
        self.assertEqual(len(store), 35)
        errors: list[str] = []
        self.assertEqual(CHECKER._parse_certificate_store(store, {}, errors), 0)
        self.assertEqual(errors, [])

    def test_path_schema_rejects_terminal_dot_segments(self) -> None:
        schema = load_schema()
        artifact_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": "#/$defs/artifact",
        }
        for path in (".", "..", "reference-box/.", "reference-box/../x"):
            with self.subTest(path=path), self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate({"path": path, "byte_length": 0, "sha256": hashlib.sha256(b"").hexdigest()}, artifact_schema)

    def test_filename_specific_schema_rejects_document_swap(self) -> None:
        schema = load_schema()
        fixture = identity_fixture()
        errors: list[str] = []
        CHECKER._validate_schema_definition(fixture, "identity", schema, "identity.json", errors)
        self.assertEqual(errors, [])
        CHECKER._validate_schema_definition(
            fixture, "maximalOrder", schema, "maximal-order.json", errors,
        )
        self.assertTrue(any("maximal-order.json: schema" in error for error in errors))

    def test_schema_invalid_verdict_list_fails_without_exception(self) -> None:
        document = {"checks": 0, "overall_status": "PASS"}
        errors: list[str] = []
        CHECKER._validate_verdicts(document, CHECKER.IDENTITY_CHECKS, "identity", errors)
        self.assertTrue(any("ordered check ids" in error for error in errors), errors)

    def test_schema_invalid_control_assertions_fail_without_exception(self) -> None:
        record = {"control_id": "D23-ORDER3", "assertions": 0, "status": "PASS"}
        assertions = record.get("assertions", [])
        assertions = assertions if isinstance(assertions, list) else []
        self.assertEqual(assertions, [])

    def test_nonstandard_json_numeric_constant_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "identity.json"
            path.write_bytes(b'{"curve":NaN}')
            errors: list[str] = []
            self.assertEqual(CHECKER._load_canonical_json(path, "identity.json", errors), {})
            self.assertTrue(any("nonstandard JSON constant" in error for error in errors), errors)

    def test_factor_base_schema_and_cross_field_rules_are_closed(self) -> None:
        schema = load_schema()
        factor_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": "#/$defs/factorBase",
        }
        document = {
            "schema": "p192-wcm-factor-base-v1",
            "curve_uid": "urn:ec-record:1:sha256:5531c4a08bdb64b6e86a6e30e9a08aa57edef7af15ac5f6d4d2a83a53bf2f646",
            "p": "6277101735386680763835789423207666416083908700390324961279",
            "t": "31607402316713927207482677199",
            "D": "-24109379060336110122544161233113975664949272517896865359515",
            "algebraic_bound": 65521,
            "mappable_bound": 113,
            "source_commit": "b" * 40,
            "entry_count": 1,
            "entries": [
                {"ell": 5, "kind": 1, "kronecker": 0, "roots": [2], "positive_root_index": 0}
            ],
        }
        jsonschema.validate(document, factor_schema)
        errors: list[str] = []
        CHECKER._validate_factor_base_document(document, errors)
        self.assertEqual(errors, [])
        for field, value in (
            ("p", 6277101735386680763835789423207666416083908700390324961279),
            ("algebraic_bound", "65521"),
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(document)
                mutated[field] = value
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(mutated, factor_schema)
        mutated = copy.deepcopy(document)
        mutated["entries"][0]["roots"] = [5]
        errors = []
        CHECKER._validate_factor_base_document(mutated, errors)
        self.assertTrue(any("roots violate kind/range/order" in error for error in errors), errors)

    def test_framed_stream_custody_is_exact(self) -> None:
        producer = b"producer stdout\n"
        verifier = b"verifier stdout\n"
        framed = (
            CHECKER.STDOUT_LOG_DOMAIN
            + struct.pack(">Q", len(producer)) + producer
            + struct.pack(">Q", len(verifier)) + verifier
        )
        errors: list[str] = []
        self.assertEqual(
            CHECKER._parse_framed_stream_log(
                framed, CHECKER.STDOUT_LOG_DOMAIN, "stdout.log", errors,
            ),
            (producer, verifier),
        )
        self.assertEqual(errors, [])
        errors = []
        CHECKER._parse_framed_stream_log(
            framed + b"extra", CHECKER.STDOUT_LOG_DOMAIN, "stdout.log", errors,
        )
        self.assertTrue(any("exact framing length" in error for error in errors))

    def test_source_clone_screen_rejects_renamed_commented_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            producer_root = root / "producer/src"
            verifier_root = root / "verifier/src"
            producer_root.mkdir(parents=True)
            verifier_root.mkdir(parents=True)
            producer_source = "\n".join(
                f"fn producer_{index}(input_{index}: u64) -> u64 {{ let value_{index} = input_{index} + {index}; value_{index} }}"
                for index in range(24)
            )
            verifier_source = "\n".join(
                f"/* renamed {index} */ fn verifier_{index}(argument_{index}: u64) -> u64 {{ let result_{index} = argument_{index} + {1000 + index}; result_{index} }}"
                for index in range(24)
            )
            (producer_root / "original.rs").write_text(producer_source, encoding="utf-8")
            nested = verifier_root / "moved"
            nested.mkdir()
            (nested / "renamed.rs").write_text(verifier_source, encoding="utf-8")
            screen = CHECKER.compute_source_clone_screen(producer_root, verifier_root)
            self.assertGreaterEqual(screen["max_match_tokens"], 128)
            self.assertEqual(screen["overall_status"], "FAIL")
            self.assertEqual(screen["matches"][0]["producer_path"], "original.rs")
            self.assertEqual(screen["matches"][0]["verifier_path"], "moved/renamed.rs")

    def test_dependency_source_rows_are_objects_not_tuple_arrays(self) -> None:
        schema = load_schema()
        source_record_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": "#/$defs/sourceHashRecord",
        }
        digest = "1" * 64
        jsonschema.validate({"path": "src/lib.rs", "sha256": digest}, source_record_schema)
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(["src/lib.rs", digest], source_record_schema)

    def test_valid_closed_pre_dispatch_decision_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document, decision_path, _, decision_commit = make_decision_fixture(root)
            jsonschema.validate(document, load_decision_schema())
            supervisor_argv = document["coordinator_decision"]["authorization"]["supervisor_argv"]
            self.assertEqual(len(supervisor_argv), 23)
            self.assertEqual(supervisor_argv[9:13:2], ["--protocol-repository", "--decision"])
            errors = CHECKER.validate_dispatch_decision(
                decision_path, decision_commit, "pre-dispatch",
                repository_root=root, check_git=False,
            )
            self.assertEqual(errors, [])

    def test_pre_dispatch_requires_clean_head_decision_and_unchanged_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            protocol_root = base / "protocol"
            assets = base / "assets"
            protocol_root.mkdir()
            assets.mkdir()
            git(protocol_root, "init", "-q")
            git(protocol_root, "config", "user.email", "fixture@example.invalid")
            git(protocol_root, "config", "user.name", "Fixture")
            for relative in CHECKER.PROTECTED_PROTOCOL_PATHS:
                path = protocol_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"protected fixture {relative}\n", encoding="utf-8")
            git(protocol_root, "add", *CHECKER.PROTECTED_PROTOCOL_PATHS)
            git(protocol_root, "commit", "-q", "-m", "protocol anchor")
            protocol_commit = git(protocol_root, "rev-parse", "HEAD")

            document, decision_path, _, _ = make_decision_fixture(protocol_root, assets)
            native = assets / "native"
            git(native, "init", "-q")
            git(native, "config", "user.email", "fixture@example.invalid")
            git(native, "config", "user.name", "Fixture")
            git(native, "add", ".")
            git(native, "commit", "-q", "-m", "native source")
            native_commit = git(native, "rev-parse", "HEAD")

            authorization = document["coordinator_decision"]["authorization"]
            protocol = authorization["protocol"]
            protocol["commit"] = protocol_commit
            for key, relative in (
                ("addendum", CHECKER.ADDENDUM_RELATIVE),
                ("interface_manifest", CHECKER.INTERFACE_MANIFEST_RELATIVE),
            ):
                raw = (protocol_root / relative).read_bytes()
                protocol[key] = {
                    "path": relative,
                    "byte_length": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            supervisor = authorization["executables"]["supervisor"]
            producer = authorization["executables"]["producer"]
            verifier = authorization["executables"]["verifier"]
            supervisor["source_commit"] = native_commit
            supervisor["embedded_protocol_commit"] = protocol_commit
            supervisor["embedded_supervisor_commit"] = native_commit
            supervisor["embedded_verifier_commit"] = native_commit
            producer["source_commit"] = native_commit
            producer["embedded_protocol_commit"] = protocol_commit
            producer["embedded_source_commit"] = native_commit
            verifier["verifier_commit"] = native_commit
            verifier["embedded_verifier_commit"] = native_commit
            authorization["supervisor_argv"] = CHECKER._resolved_supervisor_argv(authorization)
            decision_path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            relative_decision = decision_path.relative_to(protocol_root).as_posix()
            git(protocol_root, "add", relative_decision)
            git(protocol_root, "commit", "-q", "-m", "role1 dispatch decision")
            decision_commit = git(protocol_root, "rev-parse", "HEAD")

            errors = CHECKER.validate_dispatch_decision(
                decision_path, decision_commit, "pre-dispatch",
                repository_root=protocol_root, check_git=True,
            )
            self.assertEqual(errors, [])
            (protocol_root / CHECKER.ADDENDUM_RELATIVE).write_text(
                "post-anchor drift\n", encoding="utf-8",
            )
            errors = CHECKER.validate_dispatch_decision(
                decision_path, decision_commit, "pre-dispatch",
                repository_root=protocol_root, check_git=True,
            )
            self.assertTrue(any("protocol worktree cleanliness" in error for error in errors))
            self.assertTrue(any("current protected bytes" in error for error in errors))

    def test_decision_rejects_package_path_and_embedded_commit_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document, decision_path, _, decision_commit = make_decision_fixture(root)
            authorization = document["coordinator_decision"]["authorization"]
            authorization["executables"]["producer"]["package_path"] = str(root / "native")
            authorization["executables"]["supervisor"]["embedded_verifier_commit"] = "e" * 40
            authorization["decision_path"] = str(root / "ledger/decisions/DEC-20261007-deadbe.yaml")
            authorization["supervisor_argv"] = CHECKER._resolved_supervisor_argv(authorization)
            decision_path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            errors = CHECKER.validate_dispatch_decision(
                decision_path, decision_commit, "pre-dispatch",
                repository_root=root, check_git=False,
            )
            self.assertTrue(any("producer canonical package path" in error for error in errors))
            self.assertTrue(any("supervisor embedded verifier commit" in error for error in errors))
            self.assertTrue(any("decision authorization canonical path" in error for error in errors))

    def test_decision_schema_is_closed_and_run_id_is_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            document, _, _, _ = make_decision_fixture(Path(temporary))
            schema = load_decision_schema()
            mutated = copy.deepcopy(document)
            authorization = mutated["coordinator_decision"]["authorization"]
            authorization["unexpected"] = True
            authorization["run"]["run_id"] = "RUN-arbitrary"
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(mutated, schema)

    def test_retained_decision_binding_schema_is_closed(self) -> None:
        schema = load_schema()
        binding_schema = {
            "$schema": schema["$schema"],
            "$defs": schema["$defs"],
            "$ref": "#/$defs/decisionBinding",
        }
        binding = {
            "decision_id": "DEC-20261007-abcdef",
            "decision_path": "/protocol/ledger/decisions/DEC-20261007-abcdef.yaml",
            "decision_commit": "d" * 40,
            "decision_sha256": "1" * 64,
            "decision_git_mode": "100644",
            "protocol_repository_path": "/protocol",
            "protocol_checkout_head": "d" * 40,
            "protocol_worktree_clean_before_run": True,
            "protocol_commit_is_strict_ancestor": True,
            "protected_protocol_paths_unchanged": True,
        }
        jsonschema.validate(binding, binding_schema)
        for mutation in ("remove_path", "extra_key"):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(binding)
                if mutation == "remove_path":
                    del changed["decision_path"]
                else:
                    changed["unbound"] = True
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(changed, binding_schema)

    def test_cli_accepts_only_three_closed_modes(self) -> None:
        invalid_argv = [
            ["--run-dir", "/tmp/RUN-SCURVE-abcdef"],
            ["--decision", "ledger/decisions/DEC-20261007-abcdef.yaml", "--decision-commit", "d" * 40],
            [
                "--decision", "ledger/decisions/DEC-20261007-abcdef.yaml",
                "--decision-commit", "d" * 40, "--pre-dispatch",
                "--run-dir", "/tmp/RUN-SCURVE-abcdef",
            ],
        ]
        for argv in invalid_argv:
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    CHECKER.main(argv)
                self.assertEqual(raised.exception.code, 2)

    def test_decision_yaml_duplicate_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "decision.yaml"
            path.write_text("coordinator_decision:\n  id: one\n  id: two\n", encoding="utf-8")
            with self.assertRaises(yaml.YAMLError):
                CHECKER.load_yaml_strict(path)

    def test_nonmapping_decision_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "decision.yaml"
            path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")
            errors = CHECKER.validate_dispatch_decision(
                path,
                "d" * 40,
                "pre-dispatch",
                check_git=False,
            )
            self.assertTrue(
                any("expected mapping" in error for error in errors),
                errors,
            )

    def test_schema_invalid_decision_scalar_fails_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document, path, _, decision_commit = make_decision_fixture(root)
            document["coordinator_decision"]["authorization"]["supervisor_argv"][0] = float("nan")
            path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            errors = CHECKER.validate_dispatch_decision(
                path,
                decision_commit,
                "pre-dispatch",
                repository_root=root,
                check_git=False,
            )
            self.assertTrue(any("decision schema" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
