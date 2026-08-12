from __future__ import annotations

import ast
import copy
import hashlib
import json
import resource
import runpy
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
EXPERIMENT = REPO_ROOT / "experiments" / "EXP-SGCP-EMBED-001"
BUILDER_PATH = EXPERIMENT / "src" / "sgcp_embed.py"
VERIFIER_PATH = EXPERIMENT / "src" / "verify_sgcp_embed.py"
SCALAR_ORACLE_PATH = EXPERIMENT / "src" / "verify_sgcp_scalar_index.py"
SCALAR_ORACLE_ARTIFACT = EXPERIMENT / "oracles" / "scalar-index-oracle-v1.json"
REGISTRY_PATH = EXPERIMENT / "control-registry-v2.json"
SPECIFICATION_PATH = EXPERIMENT / "specification.json"
CONTRACT_PATH = REPO_ROOT / "notes" / "sgcp_embed_001_contract_20260717.md"
LITERATURE_PATH = (
    REPO_ROOT / "notes" / "structured_group_coordinate_predicates_literature_20260717.md"
)
REGISTRY_SHA256 = "cf07a4dedcc7d7895df7959aa809bee9fc8aefeff04a1ef643e7bf211173e5ca"
BUILDER = runpy.run_path(str(BUILDER_PATH))
VERIFIER = runpy.run_path(str(VERIFIER_PATH))


class SgcpEmbedBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ops = BUILDER["BuildOps"]()
        cls.curve = BUILDER["Curve"](19, 2, 9, cls.ops)
        cls.points = BUILDER["enumerate_points"](cls.curve)
        cls.registry = BUILDER["load_control_registry"]()
        cls.controls = BUILDER["run_controls"](
            cls.curve, cls.points, cls.ops, cls.registry
        )
        cls.rows = {
            size: BUILDER["build_row"](
                cls.curve, cls.points, size, cls.ops, cls.controls
            )
            for size in (4, 6, 8)
        }

    def test_registry_is_hash_bound_and_every_builder_control_passes(self) -> None:
        self.assertEqual(hashlib.sha256(REGISTRY_PATH.read_bytes()).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.controls), 12)
        self.assertTrue(all(control["builder_passed"] for control in self.controls))
        deferred = {
            control["name"]: control["deferred_predicates"]
            for control in self.controls
            if control["deferred_predicates"]
        }
        self.assertEqual(
            deferred,
            {
                "PC-EC-FOREST": ["compatibility_scalars"],
                "NC-COMPAT-MUTATION": ["compatibility_scalars"],
                "NC-B8-CANONICAL-LOSS": ["compatibility_scalars"],
            },
        )

    def test_balanced_universe_keeps_the_registered_alternate(self) -> None:
        row = self.rows[8]
        universe = row["private_audit"]["raw_witnesses"]["balanced_candidate_universe"]
        by_multiset = {tuple(item["multiset"]): item for item in universe}
        self.assertIn((0, 0, 0, 4), by_multiset)
        self.assertIn((1, 6, 6, 6), by_multiset)
        self.assertEqual(by_multiset[(0, 0, 0, 4)]["point"], "6:3")
        self.assertEqual(by_multiset[(1, 6, 6, 6)]["point"], "6:3")

    def test_candidate_and_exact_subset_counts_match_recount(self) -> None:
        expected = {
            4: (31, 12, 4096, 20),
            6: (68, 8, 256, 4),
            8: (124, 14, 16384, 53),
        }
        for size, values in expected.items():
            with self.subTest(size=size):
                proof = self.rows[size]["private_audit"]["optimizer_proof"]
                self.assertEqual(
                    (
                        proof["candidate_count"],
                        proof["eligible_candidate_count"],
                        proof["direct_subset_comparisons"],
                        proof["conflict_count"],
                    ),
                    values,
                )
                self.assertEqual(proof["graph_direct_mismatch_count"], 0)
                self.assertEqual(
                    proof["direct_subset_comparisons"],
                    1 << proof["eligible_candidate_count"],
                )

    def test_optimizer_outcome_digest_uses_frozen_lexicographic_order(self) -> None:
        expected = {
            4: "8f95f52fd06e7c636b017f8f1b720985a797d871982274596b4c078dffb15257",
            6: "c571d463baf72995f5b34df987771302e847029d192a10339c07429433f76b72",
            8: "38f0c54a812f47913bde99808f779590c7f2cad46f5e5fb670d3d728c8e70c37",
        }
        for size, digest in expected.items():
            with self.subTest(size=size):
                proof = self.rows[size]["private_audit"]["optimizer_proof"]
                self.assertEqual(
                    proof["graph_direct_outcomes_order"],
                    "lexicographic_subset_universe_indices",
                )
                self.assertEqual(proof["graph_direct_outcomes_sha256"], digest)

    def test_optimizer_objectives_are_frozen_development_expectations(self) -> None:
        expected = {
            4: (13, 5, 20, 26),
            6: (7, 4, 17, 20),
            8: (7, 4, 14, 21),
        }
        for size, values in expected.items():
            with self.subTest(size=size):
                objective = self.rows[size]["private_audit"]["optimizer_proof"][
                    "optimal_objective"
                ]
                self.assertEqual(
                    (
                        objective["retained_final_support"],
                        objective["retained_degree4_formal_multisets"],
                        objective["constrained_count"],
                        objective["unordered_nonidentity_edges"],
                    ),
                    values,
                )

    def test_public_model_excludes_optimizer_and_final_pair_sum_audit(self) -> None:
        for size, row in self.rows.items():
            with self.subTest(size=size):
                public = row["public_model"]
                private = row["private_audit"]
                self.assertNotIn("optimizer_proof", public)
                self.assertNotIn("retention", public)
                self.assertIn("optimizer_proof", private)
                self.assertIn("retention", private)
                self.assertTrue(public["axioms"]["direct_final_edge_excluded"]["valid"])
                self.assertEqual(
                    private["retention"]["raw_absolute_group_coverage"],
                    {"numerator": 1, "denominator": 1},
                )

    def test_private_audit_preserves_targets_identity_and_charged_costs(self) -> None:
        for size, row in self.rows.items():
            with self.subTest(size=size):
                private = row["private_audit"]
                retention = private["retention"]
                raw = private["raw_witnesses"]
                self.assertEqual(
                    set(retention["raw_target_witness_counts"]),
                    set(retention["raw_support_labels"]),
                )
                self.assertEqual(
                    set(retention["retained_target_witness_counts"]),
                    set(retention["retained_support_labels"]),
                )
                self.assertEqual(
                    {
                        target: len(witnesses)
                        for target, witnesses in retention[
                            "raw_target_witness_map"
                        ].items()
                    },
                    retention["raw_target_witness_counts"],
                )
                self.assertEqual(
                    {
                        target: len(witnesses)
                        for target, witnesses in retention[
                            "retained_target_witness_map"
                        ].items()
                    },
                    retention["retained_target_witness_counts"],
                )
                self.assertTrue(raw["degree2_identity_witnesses"])
                self.assertEqual(
                    private["charged_canonical_json_bytes"],
                    len(BUILDER["stable_json"](private)),
                )
                self.assertTrue(
                    all(value >= 0 for value in private["charged_operations"].values())
                )
                self.assertIn(
                    "distinct_balanced_candidates_per_constrained_label",
                    row["accounting"],
                )
                self.assertIn(
                    "raw_balanced_parent_pairs_per_constrained_label",
                    row["accounting"],
                )

    def test_policy_branches_remain_distinct(self) -> None:
        for size, row in self.rows.items():
            with self.subTest(size=size):
                p0, p1 = row["private_audit"]["baseline_policies"]
                self.assertEqual(p0["name"], "P0-BALANCED-ONLY")
                self.assertFalse(p0["axioms"]["associativity"]["valid"])
                self.assertEqual(p1["name"], "P1-CANONICAL-CLOSURE")
                self.assertFalse(p1["embedding_defined"])
                self.assertTrue(
                    row["public_model"]["axioms"]["associativity"]["valid"]
                )

    def test_candidate_universe_hash_has_one_definition(self) -> None:
        for size, row in self.rows.items():
            with self.subTest(size=size):
                raw = row["private_audit"]["raw_witnesses"]
                proof = row["private_audit"]["optimizer_proof"]
                self.assertEqual(
                    raw["balanced_candidate_universe_sha256"],
                    proof["candidate_universe_sha256"],
                )

    def test_builder_has_no_scalar_multiplication_or_table_definition(self) -> None:
        tree = ast.parse(BUILDER_PATH.read_text(encoding="utf-8"))
        names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assigned = {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
        }
        self.assertNotIn("mul", names)
        self.assertNotIn("scalar_table", names | assigned)
        self.assertNotIn("discrete_log_table", names | assigned)

    def test_strict_json_and_integer_boundaries(self) -> None:
        with self.assertRaises(ValueError):
            BUILDER["loads_json_strict"]('{"x":1,"x":2}', "duplicate")
        with self.assertRaises(ValueError):
            BUILDER["loads_json_strict"]('{"x":NaN}', "nonfinite")
        for value in (False, True, 1.0):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    BUILDER["require_exact_int"](value, "value")


class SgcpEmbedVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.curve, cls.labels, cls.scalar_table, cls.scalar_by_point = VERIFIER[
            "independently_build_curve"
        ]()
        registry_document, _ = VERIFIER["read_strict_json"](REGISTRY_PATH)
        cls.controls, cls.control_reports = VERIFIER[
            "independently_verify_controls"
        ](
            registry_document["registry"],
            cls.curve,
            cls.labels,
            cls.scalar_by_point,
        )
        cls.expected_rows = {
            size: VERIFIER["expected_builder_row"](
                cls.curve,
                cls.labels,
                cls.scalar_by_point,
                size,
                cls.controls,
            )[0]
            for size in (4, 6, 8)
        }
        command_argv = [
            sys.executable,
            str(BUILDER_PATH),
            "--contract",
            str(CONTRACT_PATH),
            "--literature",
            str(LITERATURE_PATH),
            "--toy-bits",
            "5",
            "--factor-base-sizes",
            "4",
            "6",
            "8",
        ]
        cls.certificate = BUILDER["build_document"](
            CONTRACT_PATH,
            LITERATURE_PATH,
            [4, 6, 8],
            command_argv=command_argv,
            timestamp_utc="2026-07-17T12:00:00Z",
        )

    def verify(self, certificate: dict) -> dict:
        raw = VERIFIER["canonical_json_bytes"](certificate)
        return VERIFIER["verify_certificate_document"](
            certificate,
            certificate_sha256=hashlib.sha256(raw).hexdigest(),
            input_path=Path("/private/tmp/sgcp-embed-development-in-memory.json"),
            contract_path=CONTRACT_PATH,
            literature_path=LITERATURE_PATH,
            enforce_execution_context=False,
        )

    def test_verifier_strict_json_and_exact_integer_boundaries(self) -> None:
        with self.assertRaises(VERIFIER["StrictJSONError"]):
            VERIFIER["strict_json_load_bytes"](b'{"x":1,"x":2}', "duplicate")
        with self.assertRaises(VERIFIER["StrictJSONError"]):
            VERIFIER["strict_json_load_bytes"](b'{"x":NaN}', "nonfinite")
        parsed = VERIFIER["strict_json_load_bytes"](b'{"x":1.5}', "float")
        errors: list[str] = []
        VERIFIER["validate_json_number_types"](parsed, "parsed", errors)
        self.assertEqual(errors, ["parsed.x: floating-point JSON numbers are forbidden"])
        for value in (False, True, 1.0):
            with self.subTest(value=value):
                errors = []
                self.assertIsNone(
                    VERIFIER["require_exact_int"](value, "value", errors)
                )
                self.assertTrue(errors)

    def test_verifier_does_not_import_or_execute_builder(self) -> None:
        self.assertEqual(VERIFIER["source_independence_errors"](), [])
        tree = ast.parse(VERIFIER_PATH.read_text(encoding="utf-8"))
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported_modules.append(node.module or "")
        self.assertNotIn("runpy", imported_modules)
        self.assertFalse(
            any(name.rsplit(".", 1)[-1] == "sgcp_embed" for name in imported_modules)
        )

    def test_scalar_table_digest_and_claim_scope_are_frozen(self) -> None:
        digest = VERIFIER["digest_json"](
            [VERIFIER["point_registry_text"](point) for point in self.scalar_table]
        )
        self.assertEqual(
            digest,
            "c73fdf6300e4d83ac581a07935a31dbaf6c4af3fb6b3cbe762f4266170c3f44c",
        )
        report = self.verify(self.certificate)
        self.assertTrue(report["valid"], report["errors"])
        ground_truth = report["independent_ground_truth"]
        self.assertTrue(
            ground_truth["certificate_forbidden_scalar_named_fields_absent"]
        )
        self.assertFalse(ground_truth["covert_scalar_encoding_excluded"])
        self.assertIn("no general information-flow", ground_truth["scope"])
        self.assertNotIn("scalar_table", ground_truth)
        for row in self.certificate["rows"]:
            self.assertEqual(
                row["public_model"]["labeling"]["scalar_material_attestation"],
                {
                    "forbidden_named_fields_absent_by_construction": True,
                    "covert_encoding_excluded": False,
                },
            )

        in_range_channel = copy.deepcopy(self.certificate)
        in_range_channel["resource_metrics"]["wall_clock_ns"] = 23
        in_range_channel["artifact_digests"]["execution_receipt_sha256"] = VERIFIER[
            "digest_json"
        ](
            {
                "implementation": in_range_channel["implementation"],
                "resource_metrics": in_range_channel["resource_metrics"],
            }
        )
        in_range_report = self.verify(in_range_channel)
        self.assertTrue(in_range_report["valid"], in_range_report["errors"])
        self.assertFalse(
            in_range_report["independent_ground_truth"][
                "covert_scalar_encoding_excluded"
            ]
        )

    def test_independent_rows_exactly_match_builder_rows(self) -> None:
        for row in self.certificate["rows"]:
            size = row["factor_base"]["B"]
            with self.subTest(size=size):
                errors: list[str] = []
                VERIFIER["compare_exact"](
                    self.expected_rows[size], row, f"rows[{size}]", errors
                )
                self.assertEqual(errors, [])

    def test_mutations_are_rejected(self) -> None:
        mutations = {}

        candidate_hash = copy.deepcopy(self.certificate)
        candidate_hash["rows"][0]["private_audit"]["raw_witnesses"][
            "balanced_candidate_universe_sha256"
        ] = "0" * 64
        mutations["candidate universe hash"] = candidate_hash

        selected_witness = copy.deepcopy(self.certificate)
        selected_witness["rows"][0]["public_model"]["selected_formal_family"][
            "maximal_multisets"
        ][0][0] += 1
        mutations["selected witness"] = selected_witness

        star_edge = copy.deepcopy(self.certificate)
        star_edge["rows"][0]["public_model"]["star"][
            "unordered_nonidentity_edges"
        ][0][2] = "O"
        mutations["star edge"] = star_edge

        scalar_placeholder = copy.deepcopy(self.certificate)
        forest_control = next(
            control
            for control in scalar_placeholder["rows"][0]["controls"]
            if control["name"] == "PC-EC-FOREST"
        )
        forest_control["observed"]["predicates"]["compatibility_scalars"] = "true"
        mutations["scalar placeholder"] = scalar_placeholder

        deterministic_digest = copy.deepcopy(self.certificate)
        deterministic_digest["artifact_digests"][
            "deterministic_payload_sha256"
        ] = "f" * 64
        mutations["deterministic digest"] = deterministic_digest

        forged_metrics = copy.deepcopy(self.certificate)
        forged_metrics["resource_metrics"]["builder_operations"] = {
            key: 0
            for key in forged_metrics["resource_metrics"]["builder_operations"]
        }
        forged_metrics["artifact_digests"]["execution_receipt_sha256"] = VERIFIER[
            "digest_json"
        ](
            {
                "implementation": forged_metrics["implementation"],
                "resource_metrics": forged_metrics["resource_metrics"],
            }
        )
        mutations["forged metrics with recomputed receipt"] = forged_metrics

        scalar_argv = copy.deepcopy(self.certificate)
        scalar_argv["implementation"]["command_argv"].append(
            "scalar_table=O,0:3,0:16"
        )
        scalar_argv["artifact_digests"]["execution_receipt_sha256"] = VERIFIER[
            "digest_json"
        ](
            {
                "implementation": scalar_argv["implementation"],
                "resource_metrics": scalar_argv["resource_metrics"],
            }
        )
        mutations["unknown scalar argv with recomputed receipt"] = scalar_argv

        covert_metric = copy.deepcopy(self.certificate)
        covert_metric["resource_metrics"]["wall_clock_ns"] = 10**100
        covert_metric["artifact_digests"]["execution_receipt_sha256"] = VERIFIER[
            "digest_json"
        ](
            {
                "implementation": covert_metric["implementation"],
                "resource_metrics": covert_metric["resource_metrics"],
            }
        )
        mutations["oversized covert diagnostic integer"] = covert_metric

        for name, mutated in mutations.items():
            with self.subTest(name=name):
                report = self.verify(mutated)
                self.assertFalse(report["valid"])
                self.assertTrue(report["errors"])

    def test_contract_substitution_is_rejected_by_both_programs(self) -> None:
        readme = REPO_ROOT / "README.md"
        with self.assertRaises(AssertionError):
            BUILDER["build_document"](
                readme,
                LITERATURE_PATH,
                [4, 6, 8],
            )
        report = VERIFIER["verify_certificate_document"](
            self.certificate,
            certificate_sha256="0" * 64,
            input_path=Path("/private/tmp/sgcp-contract-substitution.json"),
            contract_path=readme,
            literature_path=LITERATURE_PATH,
            enforce_execution_context=False,
        )
        self.assertFalse(report["valid"])
        self.assertTrue(any("contract path mismatch" in error for error in report["errors"]))

    def test_scalar_results_are_validity_gates(self) -> None:
        corrupted = dict(self.scalar_by_point)
        corrupted[(0, 3)] = (corrupted[(0, 3)] + 1) % 23
        reports = [
            VERIFIER["expected_builder_row"](
                self.curve,
                self.labels,
                corrupted,
                size,
                self.controls,
            )[1]
            for size in (4, 6, 8)
        ]
        errors = VERIFIER["scalar_gate_errors"](reports)
        self.assertEqual(len(errors), 6)
        self.assertTrue(all("scalar_compatibility_valid" in error for error in errors))

    def test_scalar_index_oracle_is_hash_bound_independent_and_gating(self) -> None:
        self.assertEqual(
            hashlib.sha256(SCALAR_ORACLE_PATH.read_bytes()).hexdigest(),
            VERIFIER["SCALAR_INDEX_ORACLE_SOURCE_SHA256"],
        )
        self.assertEqual(
            hashlib.sha256(SCALAR_ORACLE_ARTIFACT.read_bytes()).hexdigest(),
            VERIFIER["SCALAR_INDEX_ORACLE_ARTIFACT_SHA256"],
        )
        tree = ast.parse(SCALAR_ORACLE_PATH.read_text(encoding="utf-8"))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        self.assertFalse(
            any(
                name.rsplit(".", 1)[-1]
                in {"sgcp_embed", "verify_sgcp_embed"}
                for name in imported
            )
        )
        oracle = VERIFIER["load_scalar_index_oracle"]()
        self.assertEqual(
            VERIFIER["canonical_json_bytes"](oracle),
            VERIFIER["canonical_json_bytes"](
                json.loads(SCALAR_ORACLE_ARTIFACT.read_text(encoding="ascii"))
            ),
        )
        report = self.verify(self.certificate)
        self.assertTrue(report["valid"], report["errors"])
        self.assertTrue(
            report["scalar_index_differential"][
                "runtime_matches_frozen_artifact"
            ]
        )
        self.assertTrue(
            all(
                row["valid"]
                for row in report["scalar_index_differential"]["rows"]
            )
        )

        mutated = copy.deepcopy(self.certificate["rows"][0])
        mutated["private_audit"]["retention"]["retained_target_witness_counts"][
            "O"
        ] += 1
        differential = VERIFIER["scalar_index_oracle_row_check"](
            mutated,
            oracle["rows"][0],
            self.scalar_table,
            4,
        )
        self.assertFalse(differential["valid"])
        self.assertTrue(
            any("retained_target_witness_counts" in error for error in differential["errors"])
        )

        map_mutation = copy.deepcopy(self.certificate["rows"][0])
        map_mutation["private_audit"]["retention"][
            "retained_target_witness_map"
        ]["O"][0].reverse()
        map_differential = VERIFIER["scalar_index_oracle_row_check"](
            map_mutation,
            oracle["rows"][0],
            self.scalar_table,
            4,
        )
        self.assertFalse(map_differential["valid"])
        self.assertTrue(
            any(
                "retained_target_witness_map" in error
                for error in map_differential["errors"]
            )
        )

    def test_protected_and_existing_output_targets_are_rejected(self) -> None:
        protected = (
            BUILDER_PATH,
            VERIFIER_PATH,
            REGISTRY_PATH,
            CONTRACT_PATH,
            LITERATURE_PATH,
        )
        for path in protected:
            with self.subTest(path=path, program="builder"):
                with self.assertRaises(ValueError):
                    BUILDER["ensure_output_path"](path, REPO_ROOT)
            with self.subTest(path=path, program="verifier"):
                with self.assertRaises(ValueError):
                    VERIFIER["ensure_report_output"](path)
        with mock.patch.object(Path, "exists", return_value=True):
            with self.assertRaises(FileExistsError):
                BUILDER["ensure_output_path"](
                    BUILDER["CERTIFICATE_PATH"], REPO_ROOT
                )
            with self.assertRaises(FileExistsError):
                VERIFIER["ensure_report_output"](VERIFIER["REPORT_PATH"])

    def test_semantic_oracle_accepts_each_unmodified_row(self) -> None:
        for size, row in zip((4, 6, 8), self.certificate["rows"]):
            with self.subTest(size=size):
                report = VERIFIER["semantic_differential_check"](
                    row,
                    self.curve,
                    self.labels,
                    self.scalar_by_point,
                    size,
                )
                self.assertTrue(report["valid"], report["errors"])

    def test_locked_runner_stdout_roles_compose_without_descendants(self) -> None:
        specification = json.loads(SPECIFICATION_PATH.read_text(encoding="utf-8"))[
            "experiment"
        ]
        plans = {
            plan["role"]: plan for plan in specification["execution_plan"]["runs"]
        }
        generator_plan = plans["generator"]
        verifier_plan = plans["verifier"]
        run_id = generator_plan["run_id"]
        run_dir = EXPERIMENT / "runs" / run_id
        if run_dir.exists():
            # This replay writes manifest.json, runner-receipt.json and
            # raw-result.json into run_dir and rmtree()s it afterwards. Once a
            # real run is committed under the plan's reserved id, running the
            # replay would overwrite and then delete an immutable run record,
            # so the guard is doing its job and the id is simply consumed.
            # A directory that is NOT committed is stray state from an aborted
            # replay and still has to fail loudly.
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(run_dir)],
                cwd=REPO_ROOT, capture_output=True, text=True, check=False,
            ).returncode == 0
            if not tracked:
                self.fail(f"stray uncommitted run directory: {run_dir}")
            self.skipTest(
                f"{run_id} is now a committed run record; the execution plan "
                f"needs a fresh reserved run id before this replay can run "
                f"again without destroying it")
        run_dir.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, run_dir, True)

        def forbid_descendants() -> None:
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))

        builder_command = list(generator_plan["argv"])
        # The frozen plan pins an absolute interpreter path from the machine
        # that authorized it. Replaying it elsewhere is not possible, and
        # substituting sys.executable would stop testing the frozen argv.
        if not Path(builder_command[0]).exists():
            self.skipTest(
                f"execution plan pins interpreter {builder_command[0]}, "
                f"absent on this host")
        self.assertTrue(Path(builder_command[0]).samefile(sys.executable))
        builder_process = subprocess.run(
            builder_command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            preexec_fn=forbid_descendants,
        )
        self.assertEqual(builder_process.returncode, 0, builder_process.stderr)
        wrapper = json.loads(builder_process.stdout)
        self.assertIs(wrapper["valid"], True)
        self.assertEqual(
            wrapper["certificate"]["implementation"]["command_argv"],
            builder_command,
        )
        raw_path = run_dir / "raw-result.json"
        raw_path.write_text(
            json.dumps(wrapper, sort_keys=True, indent=2) + "\n",
            encoding="ascii",
        )
        raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        timestamp = wrapper["certificate"]["implementation"]["timestamp_utc"]
        artifact = {"sha256": raw_sha256}
        manifest = {
            "run": {
                "id": run_id,
                "experiment_id": "EXP-SGCP-EMBED-001",
                "status": "completed_valid",
                "code": {"dirty": False},
                "timing": {"started_at": timestamp, "finished_at": timestamp},
                "result": {"valid": True},
                "artifacts": {"raw-result.json": artifact},
            }
        }
        receipt = {
            "runner_receipt": {
                "run_id": run_id,
                "role": "generator",
                "status": "completed_valid",
                "argv": builder_command,
                "approved_base_commit": "a" * 40,
                "launch_commit": "a" * 40,
                "process_group": {
                    "quiescent": True,
                    "descendant_policy": "forbidden-via-rlimit-nproc-zero",
                },
                "post_run_checks": {"test_fixture": True},
                "predecessor": None,
                "artifacts": {"raw-result.json": artifact},
            }
        }
        (run_dir / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n",
            encoding="ascii",
        )
        (run_dir / "runner-receipt.json").write_text(
            json.dumps(receipt, sort_keys=True, indent=2) + "\n",
            encoding="ascii",
        )

        verifier_command = list(verifier_plan["argv"])
        self.assertTrue(Path(verifier_command[0]).samefile(sys.executable))
        verifier_process = subprocess.run(
            verifier_command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            preexec_fn=forbid_descendants,
        )
        self.assertEqual(
            verifier_process.returncode,
            0,
            verifier_process.stderr + verifier_process.stdout,
        )
        report = json.loads(verifier_process.stdout)
        self.assertIs(report["valid"], True, report["errors"])
        self.assertEqual(report["input"]["sha256"], raw_sha256)
        self.assertEqual(report["external_runner_provenance"]["run_id"], run_id)

        certificate, predecessor_raw, provenance = VERIFIER[
            "load_locked_runner_predecessor"
        ](raw_path)
        absolute_path_provenance = copy.deepcopy(provenance)
        absolute_path_provenance["argv"][4] = str(BUILDER_PATH)
        mismatch_report = VERIFIER["verify_certificate_document"](
            certificate,
            certificate_sha256=hashlib.sha256(predecessor_raw).hexdigest(),
            input_path=raw_path,
            contract_path=CONTRACT_PATH,
            literature_path=LITERATURE_PATH,
            enforce_execution_context=True,
            external_runner_provenance=absolute_path_provenance,
        )
        self.assertFalse(mismatch_report["valid"])
        self.assertTrue(
            any(
                "external_runner_provenance.argv" in error
                for error in mismatch_report["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
