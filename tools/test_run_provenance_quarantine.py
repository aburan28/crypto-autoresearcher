"""Missing historical provenance is accounted for, never made valid by repair."""
import copy
from unittest.mock import patch

from tools.test_run_supersession import SupersessionFixture, manifest_body, sha256_of, vl


class ProvenanceQuarantineTests(SupersessionFixture):
    def setUp(self):
        super().setUp()
        self.addCleanup(patch.stopall)
        patch.object(vl, "REPO", str(self.tmp)).start()
        self.decision_id = "DEC-20260907-abcdef"
        self.write_manifest("manifest.yaml", manifest_body(
            code={"command": "python3 driver.py"}))
        self.body = manifest_body(
            status="completed_invalid",
            code={"commit": None, "dirty": None, "command": "python3 driver.py"},
            result={"valid": False, "invalid_reason": "Executing revision not recorded",
                    "certificate": {"kind": "none"}},
            provenance_gap={
                "missing_fields": ["code.commit", "code.dirty"],
                "reason": "Original manifest and companions omit executing revision",
                "evidence_eligible": False,
                "decision_id": self.decision_id,
                "searched_source_sha256": {
                    str(self.superseded.relative_to(self.tmp)): sha256_of(self.superseded)
                },
            },
        )

    def context(self):
        ctx = vl.Ctx(set())
        ctx.register(self.decision_id, "decision.yaml", {
            "id": self.decision_id, "decided_by": "coordinator",
            "scope": "administrative_integrity_only", "target_ids": ["RUN-SUP-001"],
        }, "coordinator_decision")
        return ctx

    def registry(self, **over):
        return super().registry(supersession_kind="provenance_quarantine",
                                decision_id=self.decision_id, **over)

    def validate(self, body=None, registry=True):
        self.write_manifest("manifest_v2.yaml", body or self.body)
        ctx = self.context()
        if registry:
            entries = self.registry()
            vl.check_run_supersessions(ctx, entries)
            vl.check_run(str(self.superseded), ctx, entries)
        else:
            vl.check_run(str(self.superseding), ctx)
        return ctx

    def test_registered_invalid_record_is_accounted_for_without_fake_commit(self):
        ctx = self.validate()
        self.assertEqual(ctx.errors, [])
        self.assertIsNone(ctx.records["RUN-SUP-001"]["code"]["commit"])

    def test_new_unregistered_missing_commit_still_fails(self):
        ctx = self.validate(registry=False)
        self.assertTrue(any("run.code.commit missing" in e for e in ctx.errors))

    def test_cannot_promote_invalid_record_or_hide_gap(self):
        for mutation in [
            lambda b: b.update(status="completed_valid"),
            lambda b: b["result"].update(valid=True),
            lambda b: b["result"].update(validity_status="valid"),
            lambda b: b["result"].update(certificate={"kind": "discrete_log", "verified": True}),
            lambda b: b["provenance_gap"].update(evidence_eligible=True),
            lambda b: b["provenance_gap"].update(reason=""),
            lambda b: b["code"].update(commit="unknown"),
            lambda b: b["code"].update(dirty=False),
            lambda b: b["provenance_gap"].update(decision_id="DEC-20260907-000000"),
            lambda b: b["provenance_gap"].update(searched_source_sha256={}),
        ]:
            body = copy.deepcopy(self.body)
            mutation(body)
            self.assertTrue(self.validate(body).errors, body)

    def test_source_and_replacement_hashes_cannot_drift(self):
        self.write_manifest("manifest_v2.yaml", self.body)
        entries = self.registry()
        self.superseding.write_text(self.superseding.read_text() + "\n")
        ctx = self.context()
        vl.check_run(str(self.superseded), ctx, entries)
        self.assertTrue(any("superseding hash binding" in e for e in ctx.errors))
        body = copy.deepcopy(self.body)
        body["provenance_gap"]["searched_source_sha256"] = {"../escape": "0" * 64}
        self.assertTrue(self.validate(body).errors)

    def test_companions_remain_mandatory(self):
        (self.run_dir / "raw-result.json").unlink()
        ctx = self.validate()
        self.assertTrue(any("missing artifact 'raw-result.json'" in e for e in ctx.errors))

    def test_cannot_erase_provenance_already_recorded_in_original(self):
        self.write_manifest("manifest.yaml", manifest_body())
        self.body["provenance_gap"]["searched_source_sha256"] = {
            str(self.superseded.relative_to(self.tmp)): sha256_of(self.superseded)}
        ctx = self.validate()
        self.assertTrue(any("already records execution provenance" in e for e in ctx.errors))

    def test_ordinary_supersession_does_not_authorize_a_quarantine(self):
        self.write_manifest("manifest_v2.yaml", self.body)
        entries = self.registry()
        next(iter(entries.values()))["supersession_kind"] = "additive_schema_completion"
        ctx = self.context()
        vl.check_run(str(self.superseded), ctx, entries)
        self.assertTrue(any("registered provenance_quarantine" in e for e in ctx.errors))

    def test_directional_evidence_cannot_launder_quarantined_run(self):
        for direction, disclosure, allowed in [
            ("support", {"RUN-SUP-001": "missing revision"}, False),
            ("weaken", {"RUN-SUP-001": "missing revision"}, False),
            ("neutral", {}, False),
            ("neutral", {"RUN-SUP-001": "missing revision"}, True),
            ("inconclusive", {"RUN-SUP-001": "missing revision"}, True),
        ]:
            ctx = self.validate()
            ctx.register("EV-SUP-abcdef", "evidence.yaml", {
                "id": "EV-SUP-abcdef", "run_ids": ["RUN-SUP-001"],
                "direction": direction, "unresolved_run_provenance": disclosure,
                "strength": "unverified", "proof_status": "empirical_only", "proof_refs": [],
            }, "evidence")
            vl.check_cross_refs(ctx)
            self.assertEqual(not ctx.errors, allowed, ctx.errors)
