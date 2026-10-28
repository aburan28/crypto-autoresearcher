"""Synthetic mechanical checks; no cohort generation or candidate calls."""
import importlib.util
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("transfer_mapper", Path(__file__).with_name("analysis.py"))
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class MechanicalMapping(unittest.TestCase):
    def test_cold_setup_reused_and_zero_undefined(self):
        result = M.cost_ratios({"group_add_call": 10}, {"group_add_call": 20}, 2)
        self.assertEqual(result["cold"]["group_add_call"], {"numerator": 40, "denominator": 2})
        self.assertEqual(result["batch"]["group_add_call"], {"numerator": 30, "denominator": 2})
        self.assertEqual(result["online_over_q"]["group_add_call"], {"numerator": 20, "denominator": 2})
        self.assertEqual(M.cost_ratios({"group_add_call": 10}, {"group_add_call": 20}, 0),
                         {"cold": None, "batch": None, "online_over_q": None})
        self.assertGreater(M.wilson95(0, 4)[1], 0)
        self.assertIsNone(M.wilson95(0, 0))

    def test_success_events_unique_targets_prefix_and_intents(self):
        arm, curve = "circuit1.a1", "synthetic"
        fixture = {"curve_id": curve, "targets": [{"target_id": "q1"}, {"target_id": "q2"}]}
        setup = {"curve_id": curve, "arm_id": arm, "counts": {"base_transform": {"group_add_call": 10}, "constructor_setup": {}, "reference_setup": {}}}
        rows, intents = [], []
        for target, costs in (("q1", [5, 7, 11, 13]), ("q2", [2, 3, 5, 7])):
            for rep, cost in enumerate(costs):
                identifier = f"{curve}/{target}/{arm}/rep{rep}"
                status = "RECOVERED" if target == "q1" and rep in (1, 3) else "FAILED"
                rows.append({"attempt_id": identifier, "curve_id": curve, "arm_id": arm, "target_id": target,
                             "replicate_index": rep, "result": {"status": status, "reason": None, "counts": {"evaluate": {"group_add_call": cost}}}})
                intents.append({"attempt_id": identifier})
        report = {"pass": True, "per_curve_arm_outcomes": [{"curve_id": curve, "arm_id": arm,
                   "attempts": 8, "successes": 2, "source_setup_counters_once": {"group_add_call": 10},
                   "source_online_counters_all_attempts": {"group_add_call": 53}}]}
        cells, accounting, findings = M.aggregate({"fixtures": [fixture]}, rows, [setup], [], intents, report)
        cell = next(c for c in cells if c["arm_id"] == arm)
        self.assertEqual(findings, [])
        self.assertEqual((cell["verified_attempt_successes"], cell["unique_target_ids_recovered"]), (2, 1))
        self.assertEqual(cell["first_success_prefix_group_work"], 29)  # 5+7, plus all 2+3+5+7 failures.
        self.assertEqual(cell["cold_restart_model_group_work"], {"numerator": 73, "denominator": 2})
        self.assertEqual(cell["batch_work_per_success_event"], {"numerator": 63, "denominator": 2})
        self.assertIsNone(cell["small_full_bit_gate_passes"])  # N/A, not a failed diagnostic.
        self.assertEqual(accounting["unresolved_attempt_ids"], [])
        partial, acc, _ = M.aggregate({"fixtures": [fixture]}, rows[:-1], [setup], [], intents, None)
        incomplete = next(c for c in partial if c["arm_id"] == arm)
        self.assertEqual(incomplete["unresolved_attempts"], 1)
        self.assertIsNone(incomplete["verified_attempt_successes"])
        self.assertIsNone(incomplete["cold_restart_model_group_work"])
        self.assertEqual(len(acc["unresolved_attempt_ids"]), 1)

    def test_partial_physical_line_retained_as_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempts.jsonl"
            path.write_bytes(b'{"complete":true}\n{"truncated":')
            rows, errors = M.load_jsonl(path)
            self.assertEqual(rows, [{"complete": True}])
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["line"], 2)

    def test_sealed_interruption_without_final_summary_is_located(self):
        spec = importlib.util.spec_from_file_location("interrupted_transfer", Path(__file__).with_name("run_postrun.v2.py"))
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "modal/collected/tree/raw"; raw.mkdir(parents=True)
            (raw / "attempt-intents.jsonl").write_text('{"attempt_id":"synthetic"}\n')
            self.assertEqual(module.locate_raw(root), raw.resolve())
            (raw / "attempt-intents.jsonl").unlink()
            (raw.parent / "output-manifest.json").write_text('{}\n')
            self.assertEqual(module.locate_raw(raw), raw.resolve())

    def test_noninteger_or_negative_counter_refused(self):
        for value in (1.0, -1, True):
            with self.assertRaises(ValueError):
                M.merge_phases({"phase": {"group_add_call": value}})

    def test_standard_export_shape_preserves_440_zero_success_cells(self):
        # Pure synthetic mapping/schema check; no cohort or arithmetic module imported.
        parent = Path(__file__).parent
        spec = importlib.util.spec_from_file_location("transfer_postrun", parent / "run_postrun.v2.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        repo = Path("/workspace/classical-ecdlp-validation-ready")
        sys.path.insert(0, str(repo / "tools"))
        import experiment_protocol as ep
        draft = Path("/workspace/classical-ecdlp-endpoint-reuse/transfer-study-20261028/coordinator/package/experiments/EXP-ECDLP-ef7323/protocol.draft.json")
        protocol = json.loads(draft.read_text())
        protocol["freeze"]["protocol_sha256"] = "0" * 64
        prototype = {"curve_id": "synthetic", "arm_id": "circuit1.a1", "actual_setup_observed": True,
            "observed_attempts": 4, "planned_attempts": 4, "unresolved_attempts": 0, "unattempted_attempts": 0,
            "verified_attempt_successes": 0, "unique_target_ids_recovered": 0, "small_full_bit_gate_passes": None,
            "online_group_add_calls": 20, "setup_group_add_calls": 10, "first_success_prefix_group_work": 20,
            "q_numerator": 0, "q_denominator": 4, "batch_work_per_success_event": None,
            "cold_restart_model_group_work": None, "reported_success_events": 0,
            "unique_target_ids_reported_recovered": 0, "setup_phase_counters": {"setup": {"group_add_call": 10}},
            "online_phase_counters": {"online": {"group_add_call": 20}}, "diagnostic_counters": {},
            "first_success_prefix_counters": {"group_add_call": 20}, "attempt_status_counts": {"FAILED:synthetic": 4},
            "q_wilson95": M.wilson95(0, 4), "counter_cost_over_q": None, "cold_restart_counter_model": None,
            "batch_counter_cost_per_success": None, "complete": True, "independently_verified": True}
        cells = []
        for curve in range(40):
            for arm in M.ARMS:
                cell = copy.deepcopy(prototype)
                cell.update(curve_id=f"synthetic-{curve}", arm_id=arm)
                cells.append(cell)
        census = {"source_revision_c": "0" * 40, "per_curve_arm_metrics": cells,
            "attempt_accounting": {"synthetic": True}, "common_work": {"synthetic": True},
            "compute_summary": None, "parse_and_mapping_findings": []}
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            for name in ("protocol.json", "compute-plan.json", "source-manifest.json", "prior-exclusions.json", "provider-context.json", "summary-census.json"):
                (out / name).write_text("{}\n")
            (out / "compute-plan.json").write_text(json.dumps({"expected": {"total_attempts_planned": 102828}}) + "\n")
            protocol["extensions"]["transfer_study"]["compute_plan_sha256"] = M.sha(out / "compute-plan.json")
            protocol["extensions"]["transfer_study"]["expected"]["total_attempts_planned"] = 102828
            source = out / "source"; source.mkdir()
            for name in module.SOURCE_NAMES:
                (source / name).write_text("# synthetic schema input\n")
            bundle = module.make_export(ep, protocol, out / "protocol.json", source, out, out, out, "synthetic-mapping-only",
                out / "summary-census.json", out / "no-report.json", census, [], {"sandbox_id": "sb-synthetic"})
            self.assertEqual(ep.schema_errors(bundle, "experiment.export/v1"), [])
            self.assertEqual(ep.lint_export(bundle, None, out, True), [])
            self.assertEqual(len(bundle["runs"]), 440)
            self.assertEqual({r["instance_id"] for r in bundle["runs"]}, {f"synthetic-{i}" for i in range(40)})
            for row in bundle["runs"]:
                self.assertEqual(row["measurements"]["counted"]["verified_attempt_successes"], 0)
                self.assertNotIn("cold_restart_model_group_work", row["measurements"]["counted"])
                self.assertNotIn("small_full_bit_gate_passes", row["measurements"]["counted"])
                self.assertNotIn("common_fixture_work", row["measurements"]["counted"])
            self.assertEqual(bundle["backend_record"]["common_fixture_work"], {"synthetic": True})
            self.assertEqual(bundle["backend_record"]["planned_primary_attempts"], 102828)

    def test_planned_attempts_follow_exact_bound_plan_and_refuse_drift(self):
        spec = importlib.util.spec_from_file_location("planned_transfer_v2", Path(__file__).with_name("run_postrun.v2.py"))
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compute-plan.json"
            for count in (102992, 102828):
                path.write_text(json.dumps({"expected": {"total_attempts_planned": count}}) + "\n")
                protocol = {"extensions": {"transfer_study": {"compute_plan_sha256": M.sha(path),
                    "expected": {"total_attempts_planned": count}}}}
                self.assertEqual(module.bound_planned_attempts(protocol, path), count)
                protocol["extensions"]["transfer_study"]["expected"]["total_attempts_planned"] += 1
                with self.assertRaises(ValueError):
                    module.bound_planned_attempts(protocol, path)
                protocol["extensions"]["transfer_study"]["expected"]["total_attempts_planned"] = count
                path.write_text(path.read_text() + " ")
                with self.assertRaises(ValueError):
                    module.bound_planned_attempts(protocol, path)


if __name__ == "__main__":
    unittest.main()
