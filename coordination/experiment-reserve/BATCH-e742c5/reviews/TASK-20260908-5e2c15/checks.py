#!/usr/bin/env python3
"""Bounded static/arithmetic/synthetic/mock checks for TASK-20260908-5e2c15.

This checker never invokes the frozen fixture search, a pairing calibration,
an experimental control, the timing panel, or a future run.  Source hashing
and Git ancestry checks are administrative and are reported separately from
the fixed unittest cases.
"""
from __future__ import annotations

import base64
import hashlib
import inspect
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[5]
TASK_ID = "TASK-20260908-5e2c15"
AUTHORITY_COMMIT = "bfa1380dedd8998056ef5cb4ddc4d9e04fa41007"
CLAIM_COMMIT = "e65b4131f490dfd921debd0417152504b90a3429"
SOURCE_SNAPSHOT = "063ea527d88e4515b266d012ce70d5087bb20ff9"
PRIOR_REVIEW_ARCHIVE = "ef9ba9a303209894d7735ed8d4de6072fd1e5b55"
HANDOFF_REL = "ledger/handoffs/TASK-20260908-5e2c15.yaml"
DRIVER_REL = "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260908-ccfc14/driver.py"
DRIVER_DIR = ROOT / Path(DRIVER_REL).parent
sys.path.insert(0, str(DRIVER_DIR))
import driver  # noqa: E402


def _git_bytes(*args: str, check: bool = True) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, check=check
    ).stdout


def _git_text(*args: str, check: bool = True) -> str:
    return _git_bytes(*args, check=check).decode("utf-8").strip()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def administrative_source_checks() -> dict[str, object]:
    """Verify all frozen source bytes and both declared archive chains."""
    handoff = yaml.safe_load((ROOT / HANDOFF_REL).read_text(encoding="utf-8"))["handoff"]
    sources: list[dict[str, object]] = []
    for binding in handoff["source_bindings"]:
        rel = binding["path"]
        expected = binding["sha256"]
        live = _sha((ROOT / rel).read_bytes())
        if live == expected:
            source = "working_tree"
            authority = None
        else:
            authority = _sha(_git_bytes("show", f"{AUTHORITY_COMMIT}:{rel}"))
            if authority != expected:
                raise AssertionError(
                    f"{rel}: neither live bytes ({live}) nor authority bytes ({authority}) match {expected}"
                )
            source = f"authority_commit:{AUTHORITY_COMMIT}"
        sources.append(
            {
                "path": rel,
                "expected_sha256": expected,
                "live_sha256": live,
                "reviewed_from": source,
                "authority_sha256": authority,
            }
        )

    if _git_bytes("show", f"{AUTHORITY_COMMIT}:{HANDOFF_REL}") != (ROOT / HANDOFF_REL).read_bytes():
        raise AssertionError("live handoff bytes differ from the authority commit")
    plan_rel = handoff["review_plan_path"]
    if _git_bytes("show", f"{AUTHORITY_COMMIT}:{plan_rel}") != (ROOT / plan_rel).read_bytes():
        raise AssertionError("live review-plan bytes differ from the authority commit")

    claim_parent = _git_text("show", "-s", "--format=%P", CLAIM_COMMIT)
    if claim_parent != AUTHORITY_COMMIT:
        raise AssertionError(f"claim parent {claim_parent} != authority {AUTHORITY_COMMIT}")
    claim_paths = _git_text("diff-tree", "--no-commit-id", "--name-only", "-r", CLAIM_COMMIT).splitlines()
    expected_claim_path = f"coordination/experiment-reserve/BATCH-e742c5/claims/{TASK_ID}.1.claim.json"
    if claim_paths != [expected_claim_path]:
        raise AssertionError(f"claim commit changed unexpected paths: {claim_paths}")

    snapshot_rel = "coordination/experiment-reserve/BATCH-e742c5/archives/TASK-20260908-16ec11/snapshot.json"
    snapshot = json.loads(_git_bytes("show", f"{SOURCE_SNAPSHOT}:{snapshot_rel}"))
    snapshot_paths = sorted(
        _git_text("diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT).splitlines()
    )
    expected_snapshot_paths = sorted([snapshot_rel, *snapshot["source_path_sha256"]])
    if snapshot_paths != expected_snapshot_paths:
        raise AssertionError("corrected source snapshot changed paths outside its receipt")
    for rel, expected in snapshot["source_path_sha256"].items():
        if _sha(_git_bytes("show", f"{SOURCE_SNAPSHOT}:{rel}")) != expected:
            raise AssertionError(f"corrected snapshot hash mismatch: {rel}")

    prior_rel = "coordination/experiment-reserve/BATCH-e742c5/archives/TASK-20260907-c52fd1/snapshot.json"
    prior = json.loads(_git_bytes("show", f"{PRIOR_REVIEW_ARCHIVE}:{prior_rel}"))
    prior_paths = sorted(
        _git_text("diff-tree", "--no-commit-id", "--name-only", "-r", PRIOR_REVIEW_ARCHIVE).splitlines()
    )
    expected_prior_paths = sorted([prior_rel, *prior["source_path_sha256"]])
    if prior_paths != expected_prior_paths:
        raise AssertionError("prior review archive changed paths outside its receipt")
    for rel, expected in prior["source_path_sha256"].items():
        if _sha(_git_bytes("show", f"{PRIOR_REVIEW_ARCHIVE}:{rel}")) != expected:
            raise AssertionError(f"prior review archive hash mismatch: {rel}")

    head = _git_text("rev-parse", "HEAD")
    for commit in (AUTHORITY_COMMIT, CLAIM_COMMIT, SOURCE_SNAPSHOT, PRIOR_REVIEW_ARCHIVE):
        subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, head],
            check=True,
            capture_output=True,
        )
    return {
        "declared_sources": len(sources),
        "matched": len(sources),
        "drifted_sources_reviewed_at_authority": [
            row for row in sources if row["reviewed_from"] != "working_tree"
        ],
        "authority_commit": AUTHORITY_COMMIT,
        "claim_commit": CLAIM_COMMIT,
        "source_snapshot": SOURCE_SNAPSHOT,
        "prior_review_archive": PRIOR_REVIEW_ARCHIVE,
        "head_at_check": head,
        "archive_and_ancestry_checks": "PASS",
    }


def fixture(*, bits: int = 8, bin_name: str = "1") -> dict[str, object]:
    return {
        "p": 5,
        "A": 1,
        "B": 1,
        "N": 9,
        "r": 4,
        "k": 1,
        "bit_block": bits,
        "bin": bin_name,
    }


def context() -> dict[str, object]:
    return {
        "p": 5,
        "k": 1,
        "r": 4,
        "modulus": [2],
        "A": [1],
        "B": [1],
        "G": [[1], [2]],
        "T": [[1], [2]],
        "shift": [[2], [1]],
        "chi_g": [2],
    }


def public_item(*, order: str = "curve_first", q: int = 1) -> driver.PublicEvaluatorInput:
    queries = [{"query_id": index, "Q": [[1], [2]]} for index in range(q)]
    return driver.PublicEvaluatorInput(
        fixture=fixture(),
        batch_id=1,
        q=q,
        block=0,
        repetition=0,
        order=order,
        queries=queries,
        context=context(),
    )


def complete_cells(panel: list[dict[str, object]]) -> list[dict[str, object]]:
    controls = {
        "exact_character": {"all_powers": True},
        "null_and_injection": {"dishonest_encoder": {"passed": True}},
        "full_decoder": {"curve_verified": True},
    }
    return [
        {"fixture": item, "seed": seed, "controls": controls}
        for item in panel
        for seed in driver.TARGET_SEEDS
    ]


def minimal_calibration() -> dict[str, object]:
    return {
        "status": "completed_valid",
        "controls": {
            "exact_character": {"all_powers": True},
            "null_and_injection": {"dishonest_encoder": {"passed": True}},
        },
    }


def mock_lock() -> dict[str, object]:
    return {
        "runtime": {"provider": "local", "model_verified": True},
        "implementation_commit": "b" * 40,
        "source_closure": {"synthetic": "mock"},
        "review_archive": {},
        "nonce": "n" * 32,
        "machine_protection": {"watchdog_seconds": 10},
    }


class IndependentChecks(unittest.TestCase):
    def test_01_degree_one_rabin_reduces_both_sides(self) -> None:
        cert = driver.rabin_irreducibility_certificate(5, (1,))
        self.assertTrue(cert.irreducible)
        self.assertEqual(cert.reduced_x, (4,))
        self.assertEqual(cert.frobenius_x, (4,))

    def test_02_explicit_bsgs_and_trivial_character_boundaries_hold(self) -> None:
        field = driver.PolynomialField(5, (2,))
        self.assertEqual(driver.bounded_multiplicative_bsgs(field.element(2), field.element(3), 4, field), 3)
        with self.assertRaises(driver.NoSolution):
            driver.prepare_multiplicative_bsgs(field.one, 4, field)

    def test_03_parent_rejects_unknown_nested_public_key(self) -> None:
        value = public_item().mapping()
        value["context"] = {**value["context"], "withheld": 3}
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(driver.canonical_json(value))

    def test_04_child_rejects_unknown_nested_public_key(self) -> None:
        value = public_item().mapping()
        value["queries"][0]["withheld"] = 3
        with self.assertRaises(driver.PublicSchemaError):
            driver._evaluate_public_payload(driver.canonical_json(value))

    def test_05_parent_rejects_nested_duplicate_json_key(self) -> None:
        payload = public_item().serialize().replace(b'"p":5', b'"p":5,"p":5', 1)
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(payload)

    def test_06_child_rejects_nested_duplicate_json_key(self) -> None:
        payload = public_item().serialize().replace(b'"p":5', b'"p":5,"p":5', 1)
        with self.assertRaises(driver.PublicSchemaError):
            driver._evaluate_public_payload(payload)

    def test_07_noncanonical_field_coefficient_is_accepted_as_a_covert_channel(self) -> None:
        value = public_item().mapping()
        value["context"]["G"][0][0] = 1 + 5 * 3
        # The field value remains 1 mod 5, while the raw public bytes carry 3.
        driver.audit_public_payload(driver.canonical_json(value))
        self.assertEqual(driver.validate_public_payload(driver.canonical_json(value))["context"]["G"][0][0], 16)

    def test_08_fixture_context_curve_mismatch_is_accepted(self) -> None:
        value = public_item().mapping()
        value["context"]["B"] = [2]
        driver.audit_public_payload(driver.canonical_json(value))

    def test_09_one_curve_can_be_selected_for_multiple_bins(self) -> None:
        orders = {251: 1, 241: 2}
        with mock.patch.object(driver.prior, "first_primes_from", return_value=[257]), \
             mock.patch.object(driver.prior, "count_short_weierstrass_points", return_value=272), \
             mock.patch.object(driver.prior, "factor_integer", return_value=[(251, 1), (241, 1)]), \
             mock.patch.object(driver.prior, "multiplicative_order_mod", side_effect=lambda _p, r: orders[r]):
            with self.assertRaises(driver.SearchExhausted) as raised:
                driver.build_future_fixtures()
        selected = [row for row in raised.exception.fixture_history if row["status"] == "selected"]
        same_curve = [(row["bit_block"], row["p"], row["B"]) for row in selected]
        self.assertLess(len(set(same_curve)), len(same_curve))

    def test_10_field_x_rng_omits_the_required_r_component(self) -> None:
        field = driver.PolynomialField(5, (2,))
        curve = driver.ShortWeierstrassCurve(field, field.element(1), field.element(1))
        seen: list[tuple[int, ...]] = []
        def draw(**kwargs):
            seen.append(tuple(kwargs["parameters"]))
            return 0, kwargs["counter"] + 1
        with mock.patch.object(driver.prior, "rejection_draw", side_effect=draw), \
             mock.patch.object(driver, "extension_sqrt", return_value=None):
            driver.extension_point_attempts(field, curve, p=5, A=1, B=1, k=1, seed=606211, cap=1)
        self.assertEqual(seen[0], (5, 1, 1, 0, 1, 0, 0))
        self.assertNotIn("r", inspect.signature(driver.extension_point_attempts).parameters)

    def test_11_setup_order_does_not_follow_declared_arm_order(self) -> None:
        def events_for(order: str) -> list[str]:
            events: list[str] = []
            table = types.SimpleNamespace(baby={"x": 0})
            with mock.patch.object(driver, "prepare_multiplicative_bsgs", side_effect=lambda *a: events.append("field_setup") or table), \
                 mock.patch.object(driver, "prepare_additive_bsgs", side_effect=lambda *a: events.append("curve_setup") or table), \
                 mock.patch.object(driver, "solve_additive_bsgs", side_effect=lambda *a: events.append("curve_query") or 1), \
                 mock.patch.object(driver, "evaluate_shifted_tate", side_effect=lambda *a: (events.append("character_query") or (2,), 1)), \
                 mock.patch.object(driver, "solve_multiplicative_bsgs", side_effect=lambda *a: events.append("field_query") or 1):
                driver._evaluate_public_payload(public_item(order=order).serialize())
            return events
        self.assertEqual(events_for("curve_first")[:2], ["field_setup", "curve_setup"])
        self.assertEqual(events_for("character_first")[:2], ["field_setup", "curve_setup"])

    def test_12_q1_is_literal_prefix_of_one_fixed_q64_private_list(self) -> None:
        labels, _counter = driver.fixed_q64_labels(fixture(), 606223)
        self.assertEqual(len(labels), 64)
        self.assertEqual(labels[:1], [labels[0]])

    def test_13_resolution_gate_aggregates_all_q_and_blocks(self) -> None:
        source = inspect.getsource(driver._future_cell)
        self.assertIn("elapsed_cpu += costs[\"total_cpu_seconds\"]", source)
        self.assertIn("if elapsed_cpu >= 0.1", source)
        self.assertNotIn("elapsed_cpu_by_q", source)
        self.assertNotIn("resolution_by_block", source)

    def test_14_generator_search_is_charged_only_as_character_field_setup(self) -> None:
        source = inspect.getsource(driver._future_cell)
        self.assertLess(source.index("first_subgroup_generator_with_attempts"), source.index("field_cpu ="))
        self.assertIn("field_construction=field_cpu", source)
        self.assertIn("shared_selection=shared_selection_cpu", source)

    def test_15_accepted_chi_g_evaluation_is_inside_t_search_not_chi_g(self) -> None:
        source = inspect.getsource(driver._future_cell)
        self.assertLess(source.index("bounded_t_search"), source.index("t_cpu ="))
        chi_slice = source[source.index("chi_started ="):source.index("public_context =")]
        self.assertNotIn("evaluate_shifted_tate", chi_slice)
        self.assertIn("field.pow(chi_g, r)", chi_slice)

    def test_16_incomplete_matrix_can_emit_the_frozen_negative_predicate(self) -> None:
        item = fixture()
        key = f"{item['bit_block']}:{item['bin']}:{item['p']}:{item['B']}:{item['r']}"
        matrix = driver.decision_matrix(
            [{"fixture_key": key, "seed": 606223, "q": 64, "ratio_curve_over_character": 0.5}],
            [item],
        )
        self.assertTrue(matrix["negative_predicate"]["all_cells_both_seeds_le_1_00"])

    def test_17_duplicate_arithmetic_fixture_can_fill_all_eight_slots(self) -> None:
        panel = [fixture(bits=bits, bin_name=bin_name) for bits in (8, 10) for bin_name in ("1", "2", "3_6", "7_12")]
        result = driver.validate_panel_coverage(panel, complete_cells(panel), minimal_calibration())
        self.assertTrue(result["complete"])
        arithmetic = {(row["p"], row["A"], row["B"], row["r"], row["k"]) for row in panel}
        self.assertEqual(len(arithmetic), 1)

    def test_18_coverage_gate_does_not_require_q_blocks_repeats_or_cost_rows(self) -> None:
        panel = [fixture(bits=bits, bin_name=bin_name) for bits in (8, 10) for bin_name in ("1", "2", "3_6", "7_12")]
        cells = complete_cells(panel)
        self.assertTrue(all("raw" not in cell and "cost_rows" not in cell for cell in cells))
        self.assertTrue(driver.validate_panel_coverage(panel, cells, minimal_calibration())["complete"])

    def test_19_weil_self_pairing_control_is_absent(self) -> None:
        source = inspect.getsource(driver._future_cell).casefold()
        self.assertNotIn("weil", source)

    def test_20_target_certificates_omit_character_value_and_collision_indices(self) -> None:
        source = inspect.getsource(driver._future_cell)
        certificate = source[source.index("certificate ="):]
        self.assertNotIn("collision", certificate)
        self.assertNotIn("chi_q", certificate)
        self.assertNotIn("public_payload", certificate)

    def test_21_search_exhaustion_is_invalid_and_loses_t_point_attempts(self) -> None:
        error = driver.SearchExhausted("bounded T search exhausted")
        error.fixture_history = [{"status": "selected_then_failed"}]
        error.t_attempts = [{"ordinal": 0, "status": "rejected_pole"}]
        error.point_attempts = [{"ordinal": 0, "status": "rejected_nonsquare"}]
        with tempfile.TemporaryDirectory() as name, \
             mock.patch.object(driver, "verify_launch_lock", return_value=mock_lock()), \
             mock.patch.object(driver, "_set_as_limit"), \
             mock.patch.object(driver, "install_cancellation_handlers", return_value={}), \
             mock.patch.object(driver, "restore_cancellation_handlers"), \
             mock.patch.object(driver, "build_future_fixtures", side_effect=error):
            root = Path(name)
            driver.execute_authorized_run(Path("lock"), Path("key"), Path("plan"), "RUN-MOCK-SEARCH", root)
            raw_result = json.loads((root / "runs/RUN-MOCK-SEARCH/raw-result.json").read_text())
            fixtures = json.loads((root / "runs/RUN-MOCK-SEARCH/fixtures.json").read_text())
        self.assertEqual(raw_result["status"], "completed_invalid")
        self.assertEqual(raw_result["failures"][0]["classification"], "partial_search_exhausted")
        self.assertNotIn("t_attempts", fixtures)
        self.assertNotIn("point_attempts", fixtures)

    def test_22_exact_control_failure_is_misclassified_as_implementation_failure(self) -> None:
        item = fixture()
        with tempfile.TemporaryDirectory() as name, \
             mock.patch.object(driver, "verify_launch_lock", return_value=mock_lock()), \
             mock.patch.object(driver, "_set_as_limit"), \
             mock.patch.object(driver, "install_cancellation_handlers", return_value={}), \
             mock.patch.object(driver, "restore_cancellation_handlers"), \
             mock.patch.object(driver, "build_future_fixtures", return_value=([item], [])), \
             mock.patch.object(driver, "_future_cell", side_effect=RuntimeError("exact character control failed")):
            root = Path(name)
            driver.execute_authorized_run(Path("lock"), Path("key"), Path("plan"), "RUN-MOCK-CONTROL", root)
            raw_result = json.loads((root / "runs/RUN-MOCK-CONTROL/raw-result.json").read_text())
        self.assertEqual(raw_result["status"], "failed_implementation")
        self.assertEqual(raw_result["failures"][0]["classification"], "implementation_error")

    def test_23_manifest_start_timestamp_is_created_only_after_work_finishes(self) -> None:
        source = inspect.getsource(driver.execute_authorized_run)
        self.assertLess(source.index("started_wall"), source.index("build_future_fixtures"))
        self.assertGreater(source.index('"started_at": utc_now()'), source.index("finally:"))
        self.assertNotIn("started_at =", source)

    def test_24_manifest_omits_aggregate_child_cpu(self) -> None:
        source = inspect.getsource(driver.execute_authorized_run)
        resources = source[source.index('"resources":'):source.index('"metrics": metrics')]
        self.assertIn('"cpu_seconds_parent"', resources)
        self.assertNotIn("cpu_seconds_children", resources)
        self.assertNotIn("cpu_seconds_total", resources)

    def _future_lock(self, plan: Path, root: Path, run_id: str) -> dict[str, object]:
        closure = {
            str(Path(driver.__file__).resolve()): driver.sha256_file(Path(driver.__file__)),
            str(driver._prior_path.resolve()): driver.PREDECESSOR_SHA256,
        }
        return {
            "kind": "genuine_runtime_code_execution_lock",
            "experiment_id": driver.EXPERIMENT_ID,
            "frozen_approval_decision_id": driver.FROZEN_APPROVAL_ID,
            "implementation_approval_decision_id": driver.IMPLEMENTATION_APPROVAL_ID,
            "spec_sha256": driver.SPEC_SHA256,
            "execution_plan_sha256": driver.sha256_file(plan),
            "source_closure": closure,
            "review_archive": {
                "snapshot_task_id": driver.REVIEWED_SNAPSHOT_TASK_ID,
                "reviewed_snapshot_commit": "c" * 40,
                "reviewed_source_closure": closure,
                "review_task_id": "TASK-FORGED-PASS",
                "review_commit": "a" * 40,
                "verdict": "PASS",
            },
            "runtime": {"provider": "local", "resolved_model_id": "reviewed", "model_verified": True},
            "implementation_commit": "b" * 40,
            "dirty_tree": False,
            "run_id": run_id,
            "nonce": "n" * 32,
            "output_path": str(next(iter(driver.canonical_run_paths(root, run_id).values())).parent),
            "resource_limits": driver.RESOURCE_LIMITS,
            "machine_protection": {
                "parent_rlimit_as": True,
                "child_rlimit_as": True,
                "serial_worker": True,
                "process_group_termination": True,
                "watchdog_seconds": 10,
                "watchdog_justification": "synthetic machine-protection mock",
            },
            "signature_b64": base64.b64encode(b"synthetic signature").decode("ascii"),
        }

    def test_25_unreachable_forged_review_archive_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n", encoding="utf-8")
            key.write_text("synthetic key\n", encoding="utf-8")
            lock = self._future_lock(plan, root, "RUN-MOCK-FORGED-REVIEW")
            lock_path.write_bytes(driver.canonical_json(lock))
            with mock.patch.object(driver, "repository_git_state", return_value=("b" * 40, False)), \
                 mock.patch.object(driver, "_verify_detached_signature") as verify:
                accepted = driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-FORGED-REVIEW", root)
            self.assertEqual(accepted["review_archive"]["review_task_id"], "TASK-FORGED-PASS")
            verify.assert_called_once()

    def test_26_altered_executed_source_closure_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n", encoding="utf-8")
            key.write_text("synthetic key\n", encoding="utf-8")
            lock = self._future_lock(plan, root, "RUN-MOCK-ALTERED")
            lock["source_closure"][str(Path(driver.__file__).resolve())] = "0" * 64
            lock_path.write_bytes(driver.canonical_json(lock))
            with self.assertRaises(driver.LaunchRefused):
                driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-ALTERED", root)

    def test_27_symlinked_runs_directory_escapes_canonical_root(self) -> None:
        with tempfile.TemporaryDirectory() as root_name, tempfile.TemporaryDirectory() as outside_name:
            root, outside = Path(root_name), Path(outside_name)
            (root / "runs").symlink_to(outside, target_is_directory=True)
            path = next(iter(driver.canonical_run_paths(root, "RUN-MOCK-SYMLINK").values()))
            self.assertTrue(path.resolve().is_relative_to(outside.resolve()))

    def test_28_progress_receipt_is_not_declared_in_canonical_artifacts(self) -> None:
        self.assertNotIn("progress.json", driver.RUN_FILES)
        source = inspect.getsource(driver.execute_authorized_run)
        self.assertIn("canonical_run_paths(root, run_id).items()", source)


if __name__ == "__main__":
    print("ADMIN " + json.dumps(administrative_source_checks(), sort_keys=True))
    unittest.main(verbosity=2)
