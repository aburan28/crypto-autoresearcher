"""Controls for prospective phase-aware independence; no scientific trials."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import check_review_independence as C
from review_phase_seals import SCHEMA, check_sealed_phases

TASK = "TASK-20261025-abcdef"


def at(second):
    return f"2026-10-25T00:00:{second:02d}+00:00"


class SealedPhaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "inputs").mkdir()
        (self.root / "producer").mkdir()
        (self.root / "review").mkdir()
        (self.root / "inputs/statement.json").write_text('{"n":3}')
        (self.root / "producer/result.json").write_text('{"n":3}')
        self.plan = {
            "recorded_at": at(0), "coordinator_prior": "Recompute before comparison.",
            "joints": [{"joint": "J1", "assigned_to": TASK, "attack_plan": "derive n"}],
            "blindness": {"mutual": True, "lifted_for": []},
            "proves_too_much": {"objects": ["n+1"], "failure_signature": "reject n+1"},
            "blind_rederivation": {
                "required": True, "assigned_to": TASK, "quantity": "n",
                "blind_from": ["producer/"],
                "phased_release": {
                    "schema": SCHEMA, "plan_path": "plan.yaml",
                    "phase1_allowed": ["inputs/", "plan.yaml"],
                    "phase2_allowed": ["producer/", "inputs/"],
                    "derivation_path": "review/derivation.json",
                    "seal_path": "review/seal.json", "release_path": "review/release.json",
                },
            },
        }
        self.derivation = {"task_id": TASK, "generated_at": at(3),
                           "sources_read": ["plan.yaml", "inputs/statement.json"],
                           "quantities": {"n": 3}}
        self.attestation = {
            "task_id": TASK, "joints_owned": ["J1"], "verdicts": {"J1": "holds"},
            "blind_from_respected": True, "read_sibling_reports": False,
            "sources_read": ["plan.yaml", "inputs/statement.json", "producer/result.json"],
            "phased_release": {"schema": SCHEMA, "events": [
                {"seq": 1, "kind": "read", "at": at(1), "source": "plan.yaml"},
                {"seq": 2, "kind": "read", "at": at(2), "source": "inputs/statement.json"},
                {"seq": 3, "kind": "seal", "at": at(4), "artifact": "review/seal.json"},
                {"seq": 4, "kind": "unblind", "at": at(5), "artifact": "review/release.json"},
                {"seq": 5, "kind": "read", "at": at(6), "source": "producer/result.json"},
            ]},
        }
        self.write_evidence()

    def write_json(self, path, value):
        (self.root / path).write_text(json.dumps(value, sort_keys=True) + "\n")

    def sha(self, path):
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()

    def write_evidence(self):
        (self.root / "plan.yaml").write_text(yaml.safe_dump({"review_plan": self.plan}))
        self.write_json("review/derivation.json", self.derivation)
        self.seal = {"schema": SCHEMA, "task_id": TASK, "recorded_at": at(4),
                     "plan_sha256": self.sha("plan.yaml"),
                     "derivation_path": "review/derivation.json",
                     "derivation_sha256": self.sha("review/derivation.json")}
        self.write_json("review/seal.json", self.seal)
        self.release = dict(self.seal, recorded_at=at(5), seal_path="review/seal.json",
                            seal_sha256=self.sha("review/seal.json"))
        self.write_json("review/release.json", self.release)
        self.events[2]["sha256"] = self.sha("review/seal.json")
        self.events[3]["sha256"] = self.sha("review/release.json")

    @property
    def events(self):
        return self.attestation["phased_release"]["events"]

    @property
    def contract(self):
        return self.plan["blind_rederivation"]["phased_release"]

    def errors(self):
        with patch.object(C, "REPO", str(self.root)):
            return C.check(self.plan, [(str(self.root / "review/report.json"), self.attestation)])

    def rejected(self, text):
        errors = self.errors()
        self.assertTrue(any(text in error for error in errors), errors)

    def test_valid_content_bound_sealed_then_unblind_passes(self):
        self.assertEqual(self.errors(), [])

    def test_cli_reads_real_bound_artifacts(self):
        # CLI root is the real checkout: absolute temporary paths are refused,
        # so test the module entry through the same plan/report parser instead.
        self.write_json("review/report.json", {"review_attestation": self.attestation})
        with patch.object(C, "REPO", str(self.root)), patch.object(sys, "argv", [
                "check_review_independence.py", "--no-addenda", "--plan",
                str(self.root / "plan.yaml"), "--reports", str(self.root / "review/report.json")]):
            self.assertEqual(C.main(), 0)

    def test_protected_read_before_seal_rejected_even_when_repeated_after_release(self):
        self.events[1]["source"] = "producer/result.json"
        self.derivation["sources_read"][1] = "producer/result.json"
        self.write_evidence()
        self.rejected("protected or unauthorized pre-seal read")

    def test_read_between_seal_and_unblind_rejected(self):
        self.events.insert(3, {"seq": 4, "kind": "read", "at": at(4),
                               "source": "inputs/statement.json"})
        for seq, event in enumerate(self.events, 1):
            event["seq"] = seq
        self.rejected("before unblind release")

    def test_protected_read_at_release_boundary_rejected(self):
        self.events[-1]["at"] = at(5)
        self.rejected("at its boundary")

    def test_derivation_written_after_seal_rejected(self):
        self.derivation["generated_at"] = at(7)
        self.write_evidence()
        self.rejected("plan < derivation < seal")

    def test_input_read_after_derivation_rejected(self):
        self.events[1]["at"] = at(3)
        self.derivation["generated_at"] = "2026-10-25T00:00:02.5Z"
        self.write_evidence()
        self.rejected("after derivation or seal")

    def test_wrong_actual_derivation_bytes_rejected(self):
        self.derivation["quantities"]["n"] = 4
        self.write_json("review/derivation.json", self.derivation)
        self.rejected("derivation path/hash mismatch")

    def test_forged_seal_digest_rejected(self):
        self.events[2]["sha256"] = "0" * 64
        self.rejected("seal event timestamp/path/hash mismatch")

    def test_release_must_bind_actual_seal_bytes(self):
        self.release["seal_sha256"] = "0" * 64
        self.write_json("review/release.json", self.release)
        self.rejected("release seal path/hash mismatch")

    def test_changed_plan_bytes_rejected(self):
        with (self.root / "plan.yaml").open("a") as stream:
            stream.write("# changed after sealing\n")
        self.rejected("plan hash mismatch")

    def test_scalar_type_difference_in_bound_plan_rejected(self):
        disk = copy.deepcopy(self.plan)
        disk["blind_rederivation"]["required"] = 1
        (self.root / "plan.yaml").write_text(yaml.safe_dump({"review_plan": disk}))
        self.seal["plan_sha256"] = self.sha("plan.yaml")
        self.write_json("review/seal.json", self.seal)
        self.release.update(plan_sha256=self.sha("plan.yaml"), seal_sha256=self.sha("review/seal.json"))
        self.write_json("review/release.json", self.release)
        self.events[2]["sha256"] = self.sha("review/seal.json")
        self.events[3]["sha256"] = self.sha("review/release.json")
        self.rejected("differs from the bound prospective plan")

    def test_duplicate_yaml_plan_wrappers_rejected(self):
        path = self.root / "plan.yaml"
        path.write_text("review_plan: {blind_rederivation: {required: true}}\n" + path.read_text())
        self.rejected("duplicate YAML key")

    def test_cli_loader_cannot_hide_a_duplicate_wrapper(self):
        path = self.root / "plan.yaml"
        path.write_text("review_plan: {blind_rederivation: {required: true}}\n" + path.read_text())
        with self.assertRaises(ValueError):
            C._load(str(path))

    def test_cli_loader_rejects_duplicate_source_inside_report_event(self):
        content = json.dumps({"review_attestation": self.attestation})
        content = content.replace('"source": "inputs/statement.json"',
                                  '"source": "producer/result.json", "source": "inputs/statement.json"', 1)
        path = self.root / "review/report.json"
        path.write_text(content)
        with self.assertRaises(ValueError):
            C._load(str(path))

    def test_cli_reports_duplicate_plan_as_invalid(self):
        path = self.root / "plan.yaml"
        path.write_text("review_plan: {}\n" + path.read_text())
        with patch.object(sys, "argv", ["check_review_independence.py", "--no-addenda",
                                      "--plan", str(path)]):
            self.assertEqual(C.main(), 2)

    def test_escaped_phase_key_cannot_shadow_sibling_blindness_flag(self):
        content = json.dumps({"review_attestation": self.attestation})
        content = content.replace('"phased_release"', '"phased\\u005frelease"')
        content = content.replace('"read_sibling_reports": false',
                                  '"read_sibling_reports": true, "read_sibling_reports": false')
        self.assertNotIn('"phased_release"', content)
        path = self.root / "review/report.json"
        path.write_text(content)
        with self.assertRaises(ValueError):
            C._load(str(path))

    def test_directory_scan_cannot_discard_invalid_phased_report(self):
        content = json.dumps({"review_attestation": self.attestation})
        content = content.replace('"read_sibling_reports": false',
                                  '"read_sibling_reports": true, "read_sibling_reports": false')
        # Directory collection currently searches YAML suffixes; JSON is valid YAML.
        (self.root / "review/report.yaml").write_text(content)
        with self.assertRaises(ValueError):
            C._collect_reports([str(self.root / "review")])

    def test_hardlink_to_protected_source_rejected(self):
        os.link(self.root / "producer/result.json", self.root / "inputs/alias.json")
        self.events[1]["source"] = "inputs/alias.json"
        self.derivation["sources_read"][1] = "inputs/alias.json"
        self.attestation["sources_read"][1] = "inputs/alias.json"
        self.write_evidence()
        self.rejected("multiply linked phase1 input")

    def test_read_exactly_at_derivation_boundary_rejected(self):
        self.events[1]["at"] = self.derivation["generated_at"]
        self.rejected("after derivation or seal")

    def test_claimed_plan_must_match_file(self):
        self.plan["coordinator_prior"] = "Changed after seal"
        self.rejected("differs from the bound prospective plan")

    def test_unknown_schema_rejected(self):
        self.contract["schema"] = "sealed-blind-review/v999"
        self.write_evidence()
        self.rejected("unknown phased_release schema")

    def test_wrong_seal_identity_rejected(self):
        self.seal["task_id"] = "TASK-20261025-fedcba"
        self.write_json("review/seal.json", self.seal)
        self.rejected("seal task_id mismatch")

    def test_release_before_seal_rejected(self):
        self.release["recorded_at"] = at(3)
        self.write_json("review/release.json", self.release)
        self.rejected("seal < unblind release")

    def test_missing_blind_contract_flag_cannot_use_phase_exception(self):
        self.plan["blind_rederivation"]["required"] = False
        self.rejected("phased_release requires blind_rederivation.required=true")

    def test_false_blindness_attestation_rejected(self):
        self.attestation["blind_from_respected"] = False
        self.rejected("must explicitly attest phase1 blindness")

    def test_nonfile_read_rejected(self):
        self.events[-1]["source"] = "producer/"
        self.rejected("not an existing file")

    def test_duplicate_boundary_rejected(self):
        extra = dict(self.events[2], seq=4)
        self.events.insert(3, extra)
        for index, event in enumerate(self.events, 1):
            event["seq"] = index
        self.rejected("duplicate or disordered seal/unblind")

    def test_duplicate_json_seal_key_rejected(self):
        path = self.root / "review/seal.json"
        original = path.read_text().rstrip()
        path.write_text(original[:-1] + ', "task_id": "extra"}')
        self.rejected("duplicate JSON key")

    def test_unknown_contract_field_rejected(self):
        self.contract["ignore_earlier_reads"] = True
        self.write_evidence()
        self.rejected("unknown contract fields")

    def test_naive_timestamp_rejected(self):
        self.events[-1]["at"] = "2026-10-25T00:00:06"
        self.rejected("aware UTC timestamp")

    def test_duplicate_sequence_rejected(self):
        self.events[-1]["seq"] = 4
        self.rejected("contiguous unique seq")

    def test_disordered_timestamp_rejected(self):
        self.events[-1]["at"] = at(1)
        self.rejected("timestamps are disordered")

    def test_missing_timeline_read_rejected(self):
        self.events.pop()
        self.rejected("timeline read coverage differs")

    def test_missing_attested_source_rejected(self):
        self.attestation["sources_read"].pop()
        self.rejected("timeline read coverage differs")

    def test_sealed_phase1_sources_must_match_timeline(self):
        self.derivation["sources_read"].pop()
        self.write_evidence()
        self.rejected("phase1 read coverage differs")

    def test_missing_seal_file_rejected(self):
        (self.root / "review/seal.json").unlink()
        self.rejected("sealed review:")

    def test_missing_release_event_rejected(self):
        self.events.pop(3)
        self.events[-1]["seq"] = 4
        self.rejected("before unblind release")

    def test_missing_release_record_rejected(self):
        (self.root / "review/release.json").unlink()
        self.rejected("sealed review:")

    def test_missing_phase_record_never_falls_back_to_pass(self):
        del self.attestation["phased_release"]
        self.rejected("missing or unknown attested phase schema")

    def test_broad_phase1_allowlist_cannot_include_protected(self):
        self.contract["phase1_allowed"].append("producer/")
        self.write_evidence()
        self.rejected("phase1_allowed overlaps")

    def test_postrelease_allowlist_enforced(self):
        self.contract["phase2_allowed"] = ["inputs/"]
        self.write_evidence()
        self.rejected("outside phase2_allowed")

    def test_traversal_absolute_backslash_and_empty_paths_rejected(self):
        for value in ("../escape.json", str(self.root / "plan.yaml"), "", ".", "..\\escape"):
            with self.subTest(value=value):
                plan = copy.deepcopy(self.plan)
                plan["blind_rederivation"]["phased_release"]["plan_path"] = value
                self.assertTrue(check_sealed_phases(plan, self.attestation, self.root))

    def test_symlink_escape_rejected(self):
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        self.contract["plan_path"] = "escape/plan.yaml"
        self.rejected("escapes repository")

    def test_symlink_cycle_is_an_error_instead_of_exception(self):
        (self.root / "loop").symlink_to("loop")
        self.contract["plan_path"] = "loop"
        self.rejected("cannot resolve repository path")

    def test_consistently_future_transcript_rejected(self):
        # Rehash all records to isolate chronology from hash failures.
        self.plan["recorded_at"] = at(0).replace("2026", "2099")
        self.derivation["generated_at"] = at(3).replace("2026", "2099")
        self.write_evidence()
        self.seal["recorded_at"] = at(4).replace("2026", "2099")
        self.write_json("review/seal.json", self.seal)
        self.release.update(recorded_at=at(5).replace("2026", "2099"),
                            seal_sha256=self.sha("review/seal.json"))
        self.write_json("review/release.json", self.release)
        for event in self.events:
            event["at"] = event["at"].replace("2026", "2099")
        self.events[2]["sha256"] = self.sha("review/seal.json")
        self.events[3]["sha256"] = self.sha("review/release.json")
        self.rejected("in the future")

    def test_forged_derivation_path_rejected(self):
        self.seal["derivation_path"] = "inputs/statement.json"
        self.write_json("review/seal.json", self.seal)
        self.rejected("derivation path/hash mismatch")

    def test_duplicate_sources_rejected(self):
        self.attestation["sources_read"].append("inputs/statement.json")
        self.rejected("contains duplicate paths")

    def test_legacy_plan_with_protected_reads_still_fails(self):
        del self.plan["blind_rederivation"]["phased_release"]
        self.rejected("blind_from path(s)")
        self.rejected("no matching prospective blind task contract")

    def test_legacy_clean_plan_still_passes(self):
        del self.plan["blind_rederivation"]["phased_release"]
        del self.attestation["phased_release"]
        self.attestation["sources_read"] = ["inputs/statement.json"]
        self.assertEqual(self.errors(), [])

    def test_addendum_cannot_retroactively_insert_release(self):
        base = copy.deepcopy(self.plan)
        del base["blind_rederivation"]["phased_release"]
        composed, _ = C.compose_plan(base, [("fake-addendum.yaml", {
            "blind_rederivation": {"phased_release": self.contract}})])
        self.assertTrue(any("phased_release" in item for item in composed["_composition_errors"]))
        self.assertNotIn("phased_release", composed["blind_rederivation"])

    def test_historical_failed_review_remains_failed(self):
        plan = C._plan_of(yaml.safe_load((REPO / "ledger/handoffs/TASK-20261025-5145ac.yaml").read_text()))
        path = REPO / "experiments/EXP-ECDLP-d6d8e8/reviews/TASK-20261025-5145ac/report.json"
        attestation = C._attestation_of(json.loads(path.read_text()))
        problems = C.check(plan, [(str(path), attestation)])
        self.assertTrue(any("blind_from path(s)" in item for item in problems), problems)


if __name__ == "__main__":
    unittest.main(verbosity=2)
