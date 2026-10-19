#!/usr/bin/env python3
"""Integration tests for legacy-ledger and knowledge validation coverage."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
INVENTORY = REPO / "tools" / "legacy_ledger_inventory.yaml"
RUN_INVENTORY = REPO / "tools" / "legacy_run_inventory.yaml"


class LedgerCoverageTests(unittest.TestCase):
    def test_legacy_inventory_covers_and_freezes_every_root_record(self) -> None:
        document = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "legacy-ledger-inventory-v1")
        expected = document["records"]
        observed = {
            path.relative_to(REPO).as_posix()
            for pattern in ("RQ-*.yaml", "H-*.yaml", "EV-*.yaml", "DEC-*.yaml")
            for path in (REPO / "ledger").glob(pattern)
        }
        self.assertEqual(set(expected), observed)
        for relative, digest in expected.items():
            actual = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, relative)

    def test_repository_validator_indexes_legacy_and_knowledge_records(self) -> None:
        """The validator RUNS and indexes the legacy and knowledge corpora.

        This asserts COVERAGE -- that validate_ledger.py reaches the end of a
        full sweep and reports having indexed the frozen root-level records --
        and deliberately NOT that the repository is currently error-free.

        It used to assert returncode == 0, i.e. absolute repository health, and
        that coupling is why it is being changed. validate_ledger.py exits 1
        for ANY outstanding validation error anywhere in the repository, so a
        single malformed record on main failed this test on EVERY branch
        equally, whatever that branch changed. That is exactly the coupling the
        rest of the CI configuration removes on purpose: validate.yml scopes
        its own "Validate ledger" step to errors NEW since the base branch, and
        check_merge_hygiene.py scopes parseability to the files a branch
        touched, both with comments explaining that breakage already on main
        must not be every campaign's problem. This test was the one place the
        absolute check still leaked into per-PR gating, and it left main red
        continuously from 2026-08-16.

        Nothing is now unguarded. A branch that introduces a validation error is
        still caught by validate.yml's base-diffed step; a branch that breaks
        parseability is still caught by check_merge_hygiene.py; and absolute
        repository health remains asserted by .github/workflows/main-health.yml,
        which sweeps everything hourly and files an issue against the owning
        campaign. Those are the correct scopes for each question.

        A CRASH is still a failure here: a traceback means the validator could
        not complete its sweep, which is a real defect in the tool and would
        silently void every check above. Exit 1 (validation errors found) is
        tolerated; any other non-zero exit, or a missing indexing note, is not.
        """
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "validate_ledger.py")],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertIn(
            result.returncode, (0, 1),
            "validate_ledger.py did not complete its sweep (crash, not a "
            "validation finding):\n" + result.stdout + result.stderr,
        )
        self.assertNotIn("Traceback (most recent call last)", result.stderr,
                         result.stdout + result.stderr)
        self.assertIn("frozen root-level ledger records were indexed", result.stdout)
        if result.returncode == 0:
            self.assertIn("no new violations", result.stdout)
        else:
            # Outstanding errors are reported, not asserted away: the sweep must
            # still say what it found, so a silent exit 1 cannot pass. The FAIL
            # summary is written to stderr while the indexing notes go to
            # stdout, so this looks at both streams rather than assuming one.
            self.assertIn("new validation error(s)",
                          result.stdout + result.stderr)

    def test_legacy_run_inventory_freezes_imported_manifests(self) -> None:
        document = yaml.safe_load(RUN_INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "legacy-run-inventory-v1")
        self.assertTrue(document["records"])
        for relative, digest in document["records"].items():
            path = REPO / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             digest, relative)

    def test_legacy_id_remaps_resolve_to_canonical_records(self) -> None:
        document = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        for source, target_id in document.get("remapped_ids", {}).items():
            self.assertIn(source, document["records"])
            target = REPO / "ledger" / "decisions" / f"{target_id}.yaml"
            self.assertTrue(target.is_file(), target_id)
            body = yaml.safe_load(target.read_text(encoding="utf-8"))
            self.assertEqual(body["coordinator_decision"]["id"], target_id)


if __name__ == "__main__":
    unittest.main()


class ExternalVerificationTests(unittest.TestCase):
    """The receipt block a network verifier leaves on an evidence record, and
    the invariant that a verdict which did not settle backs nothing."""

    def setUp(self) -> None:
        sys.path.insert(0, str(REPO / "tools"))
        import validate_ledger  # noqa: WPS433
        self.module = validate_ledger

    class _Ctx:
        def __init__(self) -> None:
            self.errors: list[str] = []
            self.legacy_paths: set[str] = set()
            self.legacy_warnings: list[str] = []

        def err(self, path: str, msg: str, *, force: bool = False) -> None:
            self.errors.append(msg)

    def _check(self, body: dict) -> list[str]:
        ctx = self._Ctx()
        self.module.check_external_verification("ledger/evidence/EV-X-000001.yaml", body, ctx)
        return ctx.errors

    def test_an_accepted_receipt_is_clean_and_an_absent_block_is_ignored(self) -> None:
        self.assertEqual(self._check({"proof_refs": []}), [])
        self.assertEqual(self._check({
            "proof_status": "certificate",
            "proof_refs": ["sha256:claim"],
            "external_verification": [{
                "network": "cairn", "objective_id": "sha256:o", "claim_id": "sha256:claim",
                "verdict": "accept", "node": "http://node:8080", "log_head": "sha256:h",
                "settled": True, "checker_sha256": "ab" * 32,
            }],
        }), [])

    def test_a_non_settling_verdict_may_back_neither_a_proof_nor_a_direction(self) -> None:
        errors = self._check({
            "proof_status": "certificate",
            "proof_refs": ["sha256:claim"],
            "external_verification": [{
                "network": "cairn", "objective_id": "sha256:o", "claim_id": "sha256:claim",
                "verdict": "unavailable", "node": "http://node:8080", "backs_direction": True,
            }],
        })
        self.assertTrue(any("only an accepted claim backs a proof" in e for e in errors), errors)
        self.assertTrue(any("may not back a direction" in e for e in errors), errors)
        self.assertTrue(any("backs nothing" in e for e in errors), errors)

    def test_a_reject_cited_as_proof_is_refused_but_a_reject_on_its_own_is_a_fact(self) -> None:
        reject = {"network": "cairn", "objective_id": "sha256:o", "claim_id": "sha256:c",
                  "verdict": "reject", "node": "http://node:8080"}
        self.assertEqual(self._check({"external_verification": [reject]}), [])
        errors = self._check({"certificate_refs": ["sha256:c"], "external_verification": [reject]})
        self.assertEqual(len(errors), 1, errors)

    def test_shape_errors_are_named(self) -> None:
        errors = self._check({"external_verification": {"not": "a list"}})
        self.assertEqual(errors, ["external_verification must be a list of receipt blocks"])
        errors = self._check({"external_verification": [
            {"network": "cairn", "verdict": "maybe", "settled": "yes"}, "junk",
        ]})
        self.assertTrue(any("missing 'objective_id'" in e for e in errors), errors)
        self.assertTrue(any("verdict must be one of" in e for e in errors), errors)
        self.assertTrue(any("must be a mapping" in e for e in errors), errors)


class ConfoundControlTests(unittest.TestCase):
    """docs/confound-control.md: variable ledger, prediction provenance,
    transfer obligations, and the review gate on evidence."""

    def setUp(self) -> None:
        sys.path.insert(0, str(REPO / "tools"))
        import validate_ledger  # noqa: WPS433
        self.module = validate_ledger

    class _Ctx:
        def __init__(self) -> None:
            self.errors: list[str] = []
            self.advisories: list[str] = []
            self.legacy_paths: set[str] = set()
            self.records: dict = {}
            self.record_types: dict = {}
            self.ids: dict = {}

        def err(self, path: str, msg: str, *, force: bool = False) -> None:
            self.errors.append(msg)

        def advise(self, path: str, msg: str) -> None:
            self.advisories.append(msg)

    @staticmethod
    def _body(**over) -> dict:
        body = {
            "designed_at": "2026-10-18", "status": "approved",
            "success_criterion": "C-main holds and P2 holds",
            "falsification_criterion": "C-main fails",
            "preregistered_predictions": [{"id": "P1"}, {"id": "P2"}],
            "variable_ledger": {
                "independent": [{"name": "m", "levels": [3, 4]}],
                "factors": [
                    {"name": "solver", "treatment": "fixed", "how": "one build"},
                    {"name": "seed", "treatment": "randomized", "how": "frozen rule"},
                    {"name": "basis", "treatment": "fixed", "how": "polynomial"},
                ],
                "comparisons": [
                    {"id": "C-main", "arms": ["m3", "m4"], "differs_in": ["m"],
                     "design": "one_factor"},
                    {"id": "C-aa", "arms": ["s1", "s2"], "differs_in": ["seed"],
                     "design": "aa"},
                    {"id": "C-mix", "arms": ["a", "b"], "differs_in": ["m", "solver"],
                     "design": "confounded", "reason": "solver exists for one arm"},
                ],
                "crosses_map": False,
            },
            "prediction_provenance": [
                {"prediction": "P1", "first_recorded_in": "AGENTS.md",
                 "written_at": "2026-10-17", "data_seen": [{"path": "x"}],
                 "sample_status": "in_sample"},
                {"prediction": "P2", "first_recorded_in": "AGENTS.md",
                 "written_at": "2026-10-17", "data_seen": [],
                 "sample_status": "out_of_sample"},
            ],
        }
        body.update(over)
        return body

    def _check(self, body: dict) -> "ConfoundControlTests._Ctx":
        ctx = self._Ctx()
        self.module.check_confound_control("experiments/EXP-X-000001/specification.yaml",
                                           body, ctx)
        return ctx

    def test_a_complete_contract_is_clean(self) -> None:
        ctx = self._check(self._body())
        self.assertEqual(ctx.errors, [])

    def test_criteria_may_not_rest_on_in_sample_predictions_or_confounded_comparisons(self) -> None:
        errors = self._check(self._body(success_criterion="P1 and C-mix hold")).errors
        self.assertTrue(any("P1 is in_sample" in e for e in errors), errors)
        self.assertTrue(any("C-mix is confounded" in e for e in errors), errors)

    def test_comparison_designs_are_enforced(self) -> None:
        body = self._body()
        comps = body["variable_ledger"]["comparisons"]
        comps[0]["differs_in"] = ["m", "solver"]
        comps[1]["differs_in"] = ["m"]
        errors = self._check(body).errors
        self.assertTrue(any("one_factor but differs in 2" in e for e in errors), errors)
        self.assertTrue(any("A/A comparison" in e for e in errors), errors)

    def test_an_aa_arm_or_a_reason_is_required(self) -> None:
        body = self._body()
        body["variable_ledger"]["comparisons"] = body["variable_ledger"]["comparisons"][:1]
        self.assertTrue(any("needs an A/A comparison" in e for e in self._check(body).errors))
        body["variable_ledger"]["aa_not_applicable"] = "exact census, no noise"
        self.assertEqual(self._check(body).errors, [])

    def test_every_preregistered_prediction_needs_provenance(self) -> None:
        body = self._body(preregistered_predictions=[{"id": "P1"}, {"id": "P2"}, {"id": "P3"}])
        self.assertTrue(any("P3 has no prediction_provenance" in e
                            for e in self._check(body).errors))

    def test_crossing_a_map_requires_transfer_obligations_with_controls(self) -> None:
        body = self._body()
        body["variable_ledger"]["crosses_map"] = True
        self.assertTrue(any("transfer_obligations is required" in e
                            for e in self._check(body).errors))
        body["transfer_obligations"] = [{
            "map": "polynomial to normal basis", "kind": "coordinate_change",
            "source": "F_2^n, polynomial basis", "destination": "F_2^n, normal basis",
            "preserves": ["field", "curve"], "changes": ["system support"],
            "controls": [{"kind": "coordinate_isomorphism", "comparison": "C-aa"}],
            "assessment": ".claude/skills/transfer/assets/assessment-template.json",
        }]
        errors = self._check(body).errors
        self.assertEqual([e for e in errors if "matched_random" in e] != [], True, errors)
        body["transfer_obligations"][0]["controls"].append(
            {"kind": "matched_random", "comparison": "C-main"})
        self.assertEqual(self._check(body).errors, [])

    def test_the_rule_is_date_gated_and_drafts_only_advise(self) -> None:
        bare = {"designed_at": "2026-10-18", "status": "approved"}
        self.assertEqual(len(self._check(bare).errors), 2)
        draft = {"designed_at": "2026-10-18", "status": "review_required"}
        ctx = self._check(draft)
        self.assertEqual((ctx.errors, len(ctx.advisories)), ([], 2))
        old = {"designed_at": "2026-10-16", "status": "approved"}
        ctx = self._check(old)
        self.assertEqual((ctx.errors, ctx.advisories), ([], []))

    def test_evidence_on_a_ledgered_experiment_grades_every_comparison(self) -> None:
        ctx = self._Ctx()
        ctx.records = {"EXP-X-000001": self._body(),
                       "EV-X-000001": {"experiment_ids": ["EXP-X-000001"],
                                       "strength": "replicated",
                                       "confound_assessment": [
                                           {"comparison": "C-main", "verdict": "not_isolated",
                                            "basis": "solver differed in practice"}]}}
        ctx.record_types = {"EXP-X-000001": "experiment", "EV-X-000001": "evidence"}
        ctx.ids = {k: k for k in ctx.records}
        self.module.check_confound_assessments(ctx)
        self.assertTrue(any("does not grade comparison C-aa" in e for e in ctx.errors), ctx.errors)
        self.assertTrue(any("capped at preliminary" in e for e in ctx.errors), ctx.errors)
