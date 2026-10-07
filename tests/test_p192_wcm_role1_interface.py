from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import struct
import unittest
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py"
ADDENDUM_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml"
SCHEMA_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json"


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

    def test_exact_control_fixture_mutation_fails(self) -> None:
        document = load_addendum()
        fixture = document["role1_interface_addendum"]["role1_control_fixtures"]["D23-ORDER3"]
        fixture["norm"] = "4"
        errors = CHECKER.validate_contract(document, check_files=False)
        self.assertTrue(any("D23 fixture norm" in error for error in errors))

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


if __name__ == "__main__":
    unittest.main()
