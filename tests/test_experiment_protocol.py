"""experiment.protocol/v1, experiment.export/v1 and experiment.review/v1: schema,
lints, freeze hash, seed derivation, blinding, flow, adapters and write-once
records. No scientific program is run; the ecbench fixture is a committed
subset of a public smoke session."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("experiment_protocol", ROOT / "tools/experiment_protocol.py")
ep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ep)

EXAMPLE = ROOT / "examples/experiment-protocol/ecbench-l2-smoke-subset"


def load(name: str):
    return ep.read_json(EXAMPLE / name)


class SchemaAndLintTests(unittest.TestCase):
    def test_example_protocol_validates_and_is_frozen(self):
        p = load("protocol.json")
        self.assertEqual(ep.schema_errors(p, "experiment.protocol/v1"), [])
        self.assertEqual(ep.lint_protocol(p, EXAMPLE), [])
        self.assertEqual(p["freeze"]["status"], "frozen")
        self.assertEqual(p["freeze"]["protocol_sha256"], ep.protocol_hash(p))

    def test_edit_after_freeze_is_caught(self):
        p = load("protocol.json")
        p["sample_size"]["replicates"] += 1
        self.assertTrue(any("changed after it was frozen" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_comparative_claim_needs_decisive_comparison(self):
        p = load("protocol.json")
        p["claims"][1]["decided_by"] = ["C-aa"]
        self.assertTrue(any("decides nothing" in x for x in ep.lint_protocol(p, EXAMPLE)))
        p["claims"][1]["decided_by"] = []
        self.assertTrue(any("names no deciding comparison" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_missing_controls_need_reasons(self):
        p = load("protocol.json")
        p["controls"]["positive"]["not_applicable_reason"] = None
        self.assertTrue(any("positive control" in x for x in ep.lint_protocol(p, EXAMPLE)))
        p = load("protocol.json")
        p["controls"]["aa"] = {"present": False, "comparison": None, "not_applicable_reason": None}
        p["variable_ledger"]["comparisons"] = [c for c in p["variable_ledger"]["comparisons"] if c["design"] != "aa"]
        self.assertTrue(any("A/A" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_one_factor_comparison_differs_in_exactly_one_factor(self):
        p = load("protocol.json")
        p["variable_ledger"]["comparisons"][0]["differs_in"] = ["method", "curve"]
        self.assertTrue(any("one_factor" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_timed_primary_metric_needs_justification_and_isolation(self):
        p = load("protocol.json")
        p["metrics"]["primary"][0]["kind"] = "timed"
        f = ep.lint_protocol(p, EXAMPLE)
        self.assertTrue(any("timed_primary_justification" in x for x in f))
        p["measurement"]["timed_primary_justification"] = "wall is the deliverable"
        p["measurement"]["isolation_required"] = "L1"
        self.assertTrue(any("isolation_required is L1" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_in_sample_prediction_may_not_be_decisive(self):
        p = load("protocol.json")
        p["hypotheses"][0]["predictions"][0]["role"] = "decisive"
        self.assertTrue(any("in_sample" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_fixed_arm_order_needs_reason_and_criu_measurement_is_refused(self):
        p = load("protocol.json")
        p["randomization"]["arm_order"] = "fixed"
        self.assertTrue(any("arm_order is fixed" in x for x in ep.lint_protocol(p, EXAMPLE)))
        p = load("protocol.json")
        p["execution"]["checkpoint"].update(policy="criu", interval_seconds=300, grace_seconds=90, restore_validation="criu_selfcheck")
        self.assertTrue(any("CRIU-checkpointed" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_power_arithmetic(self):
        self.assertFalse(ep.power_check(39, 0.05, 1)["passes"])
        self.assertTrue(ep.power_check(40, 0.05, 1)["passes"])
        self.assertFalse(ep.power_check(100, 0.05, 3)["passes"])
        p = load("protocol.json")
        p["sample_size"]["power"].update(method="rank_test", rank_test_n=39, passes=True)
        self.assertTrue(any("2/(N+1)" in x for x in ep.lint_protocol(p, EXAMPLE)))

    def test_freeze_refuses_twice_and_hash_excludes_freeze_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "protocol.json"
            p = load("protocol.json")
            p["freeze"] = {"status": "draft", "protocol_sha256": None, "commit": None, "frozen_at": None, "filed_before_affected_data": None}
            path.write_text(json.dumps(p))
            fr = ep.freeze(path, None, True)
            self.assertEqual(fr["protocol_sha256"], ep.protocol_hash(p))
            with self.assertRaises(ep.Refused):
                ep.freeze(path, None, True)


class SeedAndBlindTests(unittest.TestCase):
    def test_seed_derivation_is_deterministic_and_distinct(self):
        sha = "0" * 64
        a = ep.derive_seed(sha, "rho", "0", 0)
        self.assertEqual(a, ep.derive_seed(sha, "rho", "0", 0))
        self.assertNotEqual(a, ep.derive_seed(sha, "rho", "0", 1))
        self.assertNotEqual(a, ep.derive_seed(sha, "bsgs", "0", 0))
        self.assertNotEqual(a, ep.derive_seed("1" * 64, "rho", "0", 0))
        p = load("protocol.json")
        p["randomization"]["seed_derivation"] = {"method": "protocol_hash_sha256"}
        rows = ep.seeds_table(p)
        self.assertEqual(len(rows), 3 * 2 * 3)
        self.assertEqual(len({r["seed"] for r in rows}), len(rows))

    def test_blinding_hides_arm_ids_and_roles(self):
        e = load("export.json")
        out, mapping = ep.blind(e, "feedface")
        self.assertEqual(set(mapping), {a["id"] for a in e["arms"]})
        self.assertTrue(all(a["id"].startswith("arm-") for a in out["arms"]))
        self.assertNotIn("reference", {a["role"] for a in out["arms"]})
        self.assertTrue(out["analysis"]["blinded"])
        again, _ = ep.blind(e, "feedface")
        self.assertEqual(out["analysis"]["blinding_key_sha256"], again["analysis"]["blinding_key_sha256"])
        other, _ = ep.blind(e, "deadbeef")
        self.assertNotEqual(out["analysis"]["blinding_key_sha256"], other["analysis"]["blinding_key_sha256"])


class ExportTests(unittest.TestCase):
    def test_example_export_binds_protocol_and_files(self):
        e, p = load("export.json"), load("protocol.json")
        self.assertEqual(ep.schema_errors(e, "experiment.export/v1"), [])
        self.assertEqual(ep.lint_export(e, p, EXAMPLE, verify_files=True), [])
        self.assertEqual(e["flow"], ep.compute_flow(e["runs"]))
        self.assertEqual(e["flow"]["planned"], 24)
        self.assertTrue(all(not r["measurements"]["wall_valid"] for r in e["runs"]), "every row earned L0 < L2")
        self.assertTrue(all(r["verification"]["status"] == "verified" for r in e["runs"]))

    def test_resumed_row_cannot_carry_a_valid_clock(self):
        e, p = load("export.json"), load("protocol.json")
        e["runs"][1]["resumed"] = 1
        e["runs"][1]["measurements"]["wall_valid"] = True
        self.assertTrue(any("wall_valid must be false" in x for x in ep.lint_export(e, p, EXAMPLE, False)))

    def test_refuted_certificate_must_be_excluded(self):
        e, p = load("export.json"), load("protocol.json")
        e["runs"][2]["verification"]["status"] = "refuted"
        self.assertTrue(any("not excluded" in x for x in ep.lint_export(e, p, EXAMPLE, False)))

    def test_protocol_mismatch_and_shortfall_are_findings(self):
        e, p = load("export.json"), load("protocol.json")
        e["protocol"]["sha256"] = "f" * 64
        self.assertTrue(any("frozen protocol" in x for x in ep.lint_export(e, p, EXAMPLE, False)))
        e = load("export.json")
        e["runs"] = e["runs"][:-1]
        e["flow"] = ep.compute_flow(e["runs"])
        self.assertTrue(any("measured rows" in x for x in ep.lint_export(e, p, EXAMPLE, False)))

    def test_changed_file_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "ex"
            shutil.copytree(EXAMPLE, dst)
            (dst / "session/session.json").write_text("{}")
            e, p = ep.read_json(dst / "export.json"), ep.read_json(dst / "protocol.json")
            self.assertTrue(any("file changed" in x for x in ep.lint_export(e, p, dst, True)))

    def test_from_ecbench_rebuilds_the_example(self):
        p = load("protocol.json")
        e = ep.from_ecbench(EXAMPLE / "session", p, "protocol.json", "rebuilt", files_prefix="session")
        committed = load("export.json")
        for key in ("arms", "runs", "flow", "files", "host", "backend_record"):
            self.assertEqual(e[key], committed[key], key)

    def test_from_taskq_maps_statuses_and_verification(self):
        p = load("protocol.json")
        result = {"schema": "taskq.task-result/v1", "task_id": "T-1", "attempt": 2, "fence": 2, "spec_sha256": "a" * 64,
                  "status": "succeeded", "outcome_class": "completed", "worker": {"id": "w1", "hostname": "h"},
                  "environment": {"cpu_model": "x", "kernel": "k"}, "source": {"repo": "crypto", "commit": "b" * 40, "resolved_commit": "b" * 40},
                  "timing": {"queued_at": "t", "started_at": "t", "finished_at": "t", "setup_wall_seconds": 1.0},
                  "runs": [{"index": 0, "warmup": True, "exit_code": 0, "wall_seconds": 1.0, "user_cpu_seconds": 1.0, "sys_cpu_seconds": 0.0, "max_rss_kb": 10, "timed_out": False, "metrics": {"s": 1.2}},
                           {"index": 1, "warmup": False, "exit_code": 0, "wall_seconds": 1.1, "user_cpu_seconds": 1.0, "sys_cpu_seconds": 0.0, "max_rss_kb": 10, "timed_out": False,
                            "metrics": {"s": 1.3}, "verification": {"status": "refuted", "verifier": "taskq.verify"}},
                           {"index": 2, "warmup": False, "exit_code": 0, "wall_seconds": 100, "user_cpu_seconds": 1, "sys_cpu_seconds": 0, "max_rss_kb": 10, "timed_out": True, "metrics": None}],
                  "artifacts": [{"path": "_taskq_logs/stdout.log", "sha256": "c" * 64, "bytes": 3}]}
        e = ep.from_taskq(result, p, "protocol.json", "rho-neg", "0", "t1")
        self.assertEqual(ep.schema_errors(e, "experiment.export/v1"), [])
        self.assertEqual([r["status"] for r in e["runs"]], ["succeeded", "succeeded", "timeout"])
        self.assertTrue(e["runs"][1]["exclusion"]["excluded"])
        self.assertEqual(e["runs"][2]["outcome_class"], "not_completed")
        self.assertEqual(e["runs"][1]["measurements"]["max_rss_bytes"], 10240)
        self.assertEqual(e["flow"]["not_completed"], 1)

    def test_from_rows_reads_csv(self):
        p = load("protocol.json")
        with tempfile.TemporaryDirectory() as tmp:
            rows = Path(tmp) / "rows.csv"
            rows.write_text("run_id,arm,instance_id,seed,replicate,warmup,status,s,total_gae,tier\n"
                            "r1,rho-neg,0,7,0,false,succeeded,1.25,900,L2\n"
                            "r2,bsgs-neg,0,7,0,false,timeout,,,L2\n")
            e = ep.from_rows(rows, p, "protocol.json", "rows", {}, files_prefix="")
            self.assertEqual(ep.schema_errors(e, "experiment.export/v1"), [])
            self.assertEqual(e["runs"][0]["measurements"]["counted"], {"s": 1.25, "total_gae": 900})
            self.assertEqual(e["runs"][1]["outcome_class"], "not_completed")

    def test_export_is_write_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "export.json"
            ep.write_once(path, {"a": 1})
            with self.assertRaises(ep.Refused):
                ep.write_once(path, {"a": 2})


class ReviewTests(unittest.TestCase):
    def test_example_review_validates(self):
        reviews = sorted((EXAMPLE / "reviews").glob("REV-*.json"))
        self.assertEqual(len(reviews), 1)
        r = ep.read_json(reviews[0])
        self.assertEqual(ep.schema_errors(r, "experiment.review/v1"), [])
        self.assertEqual(ep.lint_review(r, EXAMPLE), [])
        self.assertIn("official research status", r["asserts_nothing_about"])

    def test_scaffold_runs_the_deterministic_checks(self):
        e, p = load("export.json"), load("protocol.json")
        r = ep.review_scaffold(EXAMPLE / "export.json", e, p, "validator", "test", None, None)
        kinds = {c["kind"]: c["result"] for c in r["checks"]}
        self.assertEqual(kinds["hashes"], "pass")
        self.assertEqual(kinds["protocol_adherence"], "pass")
        self.assertEqual(kinds["controls"], "not_covered")
        self.assertEqual(ep.schema_errors(r, "experiment.review/v1"), [])
        self.assertTrue(any("scaffold" in x for x in ep.lint_review(r, EXAMPLE)), "a scaffold is not a review")

    def test_positive_judgment_after_failed_hashes_is_refused(self):
        r = ep.read_json(sorted((EXAMPLE / "reviews").glob("REV-*.json"))[0])
        r["checks"][0]["result"] = "fail"
        r["judgments"][1]["verdict"] = "supported_within_scope"
        self.assertTrue(any("although hashes" in x for x in ep.lint_review(r, EXAMPLE)))

    def test_replay_bookkeeping(self):
        r = ep.read_json(sorted((EXAMPLE / "reviews").glob("REV-*.json"))[0])
        r["replay"].update(performed=True, units_sampled=4, identical=3, mismatched=0, nonce="ab", miss_probability=ep.miss_table(4))
        self.assertTrue(any("identical + mismatched" in x for x in ep.lint_review(r, EXAMPLE)))

    def test_cli_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "ex"
            shutil.copytree(EXAMPLE, dst)
            self.assertEqual(ep.main(["validate", str(dst / "protocol.json")]), 0)
            self.assertEqual(ep.main(["check-export", str(dst / "export.json"), "--protocol", str(dst / "protocol.json"), "--verify-files"]), 0)
            self.assertEqual(ep.main(["flow", str(dst / "export.json")]), 0)
            self.assertEqual(ep.main(["review", "validate", str(next((dst / "reviews").glob("REV-*.json")))]), 0)
            self.assertEqual(ep.main(["review", "new", str(dst / "export.json"), "--out-dir", str(dst / "r2"), "--role", "red-team"]), 0)
            self.assertEqual(len(list((dst / "r2").glob("REV-*.json"))), 1)
            self.assertEqual(ep.main(["blind", str(dst / "export.json"), "--out", str(dst / "blinded.json"), "--nonce", "00"]), 0)
            self.assertEqual(oct(os.stat(dst / "blinded.key.json").st_mode & 0o777), "0o600")
            self.assertEqual(ep.main(["seeds", str(dst / "protocol.json"), "--arm", "rho-neg", "--instance", "0"]), 2)


class AdmissionRegressionTests(unittest.TestCase):
    def test_export_recomputes_the_frozen_protocol_hash(self):
        e, p = load("export.json"), load("protocol.json")
        p["execution"]["timeout_seconds"] += 1
        self.assertTrue(any("changed after it was frozen" in f for f in ep.lint_export(e, p, EXAMPLE, True)))

    def test_duplicate_rows_and_execution_cells_are_rejected(self):
        e, p = load("export.json"), load("protocol.json")
        e["runs"][7] = copy.deepcopy(e["runs"][6])
        e["flow"] = ep.compute_flow(e["runs"])
        self.assertTrue(any("duplicate run_id" in f for f in ep.lint_export(e, p, EXAMPLE, False)))
        e["runs"][7]["run_id"] = "independently-named-duplicate"
        self.assertTrue(any("duplicate execution cell" in f for f in ep.lint_export(e, p, EXAMPLE, False)))

    def test_measured_cells_cannot_replace_a_missing_instance(self):
        e, p = load("export.json"), load("protocol.json")
        for r in e["runs"]:
            if not r["warmup"]:
                r["instance_id"] = "one-instance"
        self.assertTrue(any("instances, expected" in f for f in ep.lint_export(e, p, EXAMPLE, False)))

    def test_missing_isolation_cannot_admit_a_clock(self):
        e, p = load("export.json"), load("protocol.json")
        row = next(r for r in e["runs"] if not r["warmup"])
        row["isolation"].update(tier=None, contended=None)
        row["measurements"]["wall_valid"] = True
        self.assertTrue(any("below the protocol" in f for f in ep.lint_export(e, p, EXAMPLE, False)))

    def test_absent_pinned_binary_is_not_a_match(self):
        e, p = load("export.json"), load("protocol.json")
        e["arms"][0]["binary_sha256"] = None
        self.assertTrue(any("binary_sha256" in f for f in ep.lint_export(e, p, EXAMPLE, False)))

    def test_schema_valid_but_semantically_invalid_protocol_is_not_frozen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "protocol.json"
            p = load("protocol.json")
            p["freeze"].update(status="draft", protocol_sha256=None)
            p["claims"][1]["decided_by"] = ["C-aa"]
            path.write_text(json.dumps(p)); original = path.read_bytes()
            with self.assertRaises(ep.Refused):
                ep.freeze(path, None, True)
            self.assertEqual(path.read_bytes(), original)

    def test_duplicate_protocol_identities_are_rejected(self):
        p = load("protocol.json")
        p["arms"].append(copy.deepcopy(p["arms"][0]))
        p["freeze"]["protocol_sha256"] = ep.protocol_hash(p)
        self.assertTrue(any("duplicate identities" in f for f in ep.lint_protocol(p)))

    def test_missing_derived_seed_is_not_a_match(self):
        e, p = load("export.json"), load("protocol.json")
        p["randomization"]["seed_derivation"] = {"method": "protocol_hash_sha256"}
        p["freeze"]["protocol_sha256"] = ep.protocol_hash(p)
        e["protocol"]["sha256"] = p["freeze"]["protocol_sha256"]
        row = next(r for r in e["runs"] if not r["warmup"])
        row.update(instance_id="0", replicate=0, seed=None)
        self.assertTrue(any("seed None" in f for f in ep.lint_export(e, p, EXAMPLE, False)))

    def test_adapter_records_observed_binary_and_does_not_copy_the_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp) / "session"
            shutil.copytree(EXAMPLE / "session", session)
            records = [json.loads(line) for line in (session / "records.jsonl").read_text().splitlines()]
            for r in records:
                r["binary_sha256"] = "f" * 64
            (session / "records.jsonl").write_text("\n".join(json.dumps(r) for r in records) + "\n")
            p = load("protocol.json")
            e = ep.from_ecbench(session, p, "protocol.json", "changed-instrument")
            self.assertEqual({a["binary_sha256"] for a in e["arms"]}, {"f" * 64})
            self.assertTrue(any("binary_sha256" in f for f in ep.lint_export(e, p, None, False)))

    def test_taskq_does_not_invent_seeds_or_isolation(self):
        p = load("protocol.json")
        p["randomization"]["seed_derivation"] = {"method": "protocol_hash_sha256"}
        result = {"schema": "taskq.task-result/v1", "task_id": "T-1", "status": "succeeded",
                  "runs": [{"index": 0, "exit_code": 0, "wall_seconds": 1.0, "seed": 7}]}
        e = ep.from_taskq(result, p, "protocol.json", "rho-neg", "0", "observations")
        self.assertEqual(e["runs"][0]["seed"], 7)
        self.assertFalse(e["runs"][0]["measurements"]["wall_valid"])
        self.assertIsNone(e["arms"][0]["binary_sha256"])
        del result["runs"][0]["seed"]
        self.assertIsNone(ep.from_taskq(result, p, "protocol.json", "rho-neg", "0", "missing")["runs"][0]["seed"])

    def test_review_cli_checks_its_export_from_the_review_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "example"
            shutil.copytree(EXAMPLE, dst)
            review = next((dst / "reviews").glob("REV-*.json"))
            (dst / "export.json").write_text("{}")
            self.assertEqual(ep.main(["review", "validate", str(review)]), 1)

    def test_nonfinite_input_and_output_leave_no_partial_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text('{"value":1e999}')
            with self.assertRaises(ep.Refused):
                ep.read_json(path)
            path.unlink()
            with self.assertRaises(ep.Refused):
                ep.write_once(path, {"value": float("inf")})
            self.assertFalse(path.exists())

    def test_blinded_view_withholds_explicit_identity_and_raw_artifact_links(self):
        e = load("export.json")
        e["runs"][0]["backend_ref"] = "rho-neg-original"
        e["runs"][0]["verification"]["verifier"] = "rho-neg-verifier"
        e["notes"] = [{"kind": "observation", "text": "rho-neg source identity"}]
        out, _ = ep.blind(e, "test-nonce")
        rendered = json.dumps(out)
        for a in e["arms"]:
            self.assertNotIn(a["id"], rendered)
        self.assertNotIn(e["runs"][0]["run_id"], rendered)
        self.assertEqual(out["files"], [])
        self.assertEqual(out["flow"], ep.compute_flow(out["runs"]))
        self.assertEqual(ep.schema_errors(out, "experiment.export/v1"), [])

    def test_single_seed_uses_the_declared_explicit_rule(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            p = load("protocol.json")
            p["randomization"]["seed_derivation"] = {"method": "explicit_list", "seeds": [7, 11]}
            path = Path(tmp) / "protocol.json"; path.write_text(json.dumps(p))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(ep.main(["seeds", str(path), "--arm", "rho-neg", "--instance", "0", "--replicate", "1"]), 0)
            self.assertEqual(output.getvalue().strip(), "11")

    def test_power_boundary_reports_the_first_admissible_n(self):
        result = ep.power_check(40, 0.05, 1)
        self.assertEqual(result["n_needed"], 40)
        self.assertTrue(result["passes"])


class ProvenanceRegressionTests(unittest.TestCase):
    def test_missing_pinned_analysis_is_rejected(self):
        e, p = load("export.json"), load("protocol.json")
        p["analysis_plan"]["script"] = {"path": "analysis.py", "sha256": "f" * 64}
        p["freeze"]["protocol_sha256"] = ep.protocol_hash(p)
        e["protocol"]["sha256"] = p["freeze"]["protocol_sha256"]
        self.assertTrue(any("analysis.script.sha256" in f for f in ep.lint_export(e, p, EXAMPLE, False)))

    def test_analysis_artifact_hashes_are_verified_even_outside_files_list(self):
        e, p = load("export.json"), load("protocol.json")
        e["analysis"]["outputs"] = [{"path": "unavailable-analysis.json", "sha256": "f" * 64, "bytes": 0}]
        self.assertTrue(any("file missing: unavailable-analysis.json" in f for f in ep.lint_export(e, p, EXAMPLE, True)))

    def test_cancelled_task_keeps_its_completed_prefix(self):
        p = load("protocol.json")
        result = {"schema": "taskq.task-result/v1", "task_id": "T-1", "status": "cancelled",
                  "runs": [{"index": 0, "exit_code": 0, "wall_seconds": 1},
                           {"index": 1, "exit_code": None, "wall_seconds": None}]}
        e = ep.from_taskq(result, p, "protocol.json", "rho-neg", "0", "partial")
        self.assertEqual([r["status"] for r in e["runs"]], ["succeeded", "cancelled"])
        self.assertEqual(e["flow"]["completed"], 1)
        self.assertEqual(e["flow"]["not_completed"], 1)


class ExternalNonceRegressionTests(unittest.TestCase):
    def test_external_nonce_is_bound_in_export_without_editing_frozen_protocol(self):
        e, p = load("export.json"), load("protocol.json")
        p["randomization"]["seed_derivation"] = {"method": "external_nonce"}
        p["freeze"].update(status="draft", protocol_sha256=None)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "protocol.json"; path.write_text(json.dumps(p))
            ep.freeze(path, None, True)
            frozen_bytes = path.read_bytes(); p = ep.read_json(path)
            table = {(r["arm"], r["instance"], r["replicate"]): r["seed"] for r in ep.seeds_table(p, "public-nonce")}
            e["protocol"].update(sha256=p["freeze"]["protocol_sha256"], seed_nonce="public-nonce")
            instances = {value: str(i) for i, value in enumerate(sorted({r["instance_id"] for r in e["runs"]}))}
            for row in e["runs"]:
                if not row["warmup"]:
                    row["instance_id"] = instances[row["instance_id"]]
                    row["replicate"] -= 1
                    row["seed"] = table[(row["arm"], row["instance_id"], row["replicate"])]
            self.assertEqual(ep.schema_errors(e, "experiment.export/v1"), [])
            self.assertEqual(ep.lint_export(e, p, EXAMPLE, True), [])
            e["protocol"]["seed_nonce"] = "different-nonce"
            self.assertTrue(any("not the protocol-derived seed" in f for f in ep.lint_export(e, p, EXAMPLE, False)))
            del e["protocol"]["seed_nonce"]
            self.assertTrue(any("missing protocol.seed_nonce" in f for f in ep.lint_export(e, p, EXAMPLE, False)))
            self.assertEqual(path.read_bytes(), frozen_bytes)


if __name__ == "__main__":
    unittest.main()
