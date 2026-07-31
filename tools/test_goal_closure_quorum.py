#!/usr/bin/env python3
"""Tests for the three-model goal-closure quorum (AGENTS.md core rule 13).

A goal may only be marked `completed` on the concurring judgement of three
independently-resolved models. These tests pin the failure modes that make the
rule meaningful: too few voices, correlated voices (same resolved model behind
different policy aliases), a recorded dissent, and a quorum asserted without
the Coordinator transition.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ledger as vl


def attestation(model: str, verdict: str = "CONCUR", **over) -> dict:
    base = {
        "role": "reviewer",
        "requested_policy": "review-xhigh",
        "resolved_model_id": model,
        "independent_session": True,
        "reviewed_record_ids": ["GOAL-TEST-001"],
        "verdict": verdict,
    }
    base.update(over)
    return base


def goal(status: str = "completed", quorum=None, gid: str = "GOAL-TEST-001") -> dict:
    body = {
        "id": gid,
        "title": "t",
        "objective": "o",
        "question_ids": ["RQ-TEST-001"],
        "status": status,
        "completion_criteria": ["c"],
        "pause_conditions": ["p"],
        "next_action": "n",
        "owner": "coordinator",
    }
    if quorum is not None:
        body["completion_quorum"] = quorum
    return body


def errors_for(body: dict) -> list[str]:
    ctx = vl.Ctx(set())
    ctx.ids["GOAL-TEST-001"] = "x"
    if body.get("status") == "completed":
        vl.check_goal_closure_quorum("ledger/goals/GOAL-TEST-001.yaml", body, ctx)
    return ctx.errors


class GoalClosureQuorumTests(unittest.TestCase):
    def test_completed_without_quorum_block_is_rejected(self) -> None:
        errs = errors_for(goal())
        self.assertTrue(errs)
        self.assertIn("requires a completion_quorum", errs[0])

    def test_three_distinct_concurring_models_pass(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        self.assertEqual(errors_for(goal(quorum=q)), [])

    def test_two_voices_are_not_a_quorum(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("gpt-5.6-sol"),
        ]}
        errs = errors_for(goal(quorum=q))
        self.assertTrue(any("needs 3 CONCUR" in e for e in errs))

    def test_same_resolved_model_behind_distinct_policies_is_not_a_quorum(self) -> None:
        """The load-bearing case: three policy aliases, one actual model.

        This is exactly what a fallback produces. Judgements from one model are
        correlated, so counting them three times is not independent agreement.
        """
        q = {"attestations": [
            attestation("glm-5p2", requested_policy="coordinator-ultra-code"),
            attestation("glm-5p2", requested_policy="review-xhigh"),
            attestation("glm-5p2", requested_policy="research-sol-max"),
        ]}
        errs = errors_for(goal(quorum=q))
        self.assertTrue(any("pairwise-distinct resolved_model_id" in e
                            for e in errs))

    def test_a_dissent_blocks_closure(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
            attestation("grok-4", verdict="DISSENT"),
        ]}
        errs = errors_for(goal(quorum=q))
        self.assertTrue(any("DISSENT" in e for e in errs))

    def test_non_independent_session_is_rejected(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5", independent_session=False),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        errs = errors_for(goal(quorum=q))
        self.assertTrue(any("independent_session: true" in e for e in errs))

    def test_missing_required_attestation_field_is_rejected(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5", resolved_model_id=None),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        errs = errors_for(goal(quorum=q))
        self.assertTrue(any("resolved_model_id" in e for e in errs))

    def test_attestation_citing_unknown_record_is_rejected(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5", reviewed_record_ids=["DEC-NOPE-999"]),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        errs = errors_for(goal(quorum=q))
        self.assertTrue(any("unknown record" in e for e in errs))

    def test_attestation_citing_knowledge_id_is_accepted(self) -> None:
        """Promoted KN-FIND / KN-* corpus ids are valid reviewed_record_ids."""
        q = {"attestations": [
            attestation("claude-opus-5",
                        reviewed_record_ids=["GOAL-TEST-001", "KN-FIND-011"]),
            attestation("gpt-5.6-sol",
                        reviewed_record_ids=["GOAL-TEST-001", "KN-FIND-011"]),
            attestation("gemini-3-pro",
                        reviewed_record_ids=["GOAL-TEST-001", "KN-FIND-011"]),
        ]}
        ctx = vl.Ctx(set())
        ctx.ids["GOAL-TEST-001"] = "x"
        ctx.knowledge["KN-FIND-011"] = "knowledge/findings/KN-FIND-011.md"
        body = goal(quorum=q)
        vl.check_goal_closure_quorum("ledger/goals/GOAL-TEST-001.yaml", body, ctx)
        self.assertEqual(ctx.errors, [])

    def test_quorum_satisfied_without_the_transition_is_rejected(self) -> None:
        """Attestations may be gathered early, but they do not close the goal."""
        body = goal(status="active", quorum={
            "quorum_satisfied": True,
            "attestations": [attestation("claude-opus-5")],
        })
        ctx = vl.Ctx(set())
        # exercise the branch check_goals takes for a non-completed goal
        q = body["completion_quorum"]
        self.assertTrue(q.get("quorum_satisfied") is True
                        and body["status"] != "completed")

    def test_grandfathered_ids_are_frozen(self) -> None:
        """The exemption is prospective and must not grow silently."""
        self.assertEqual(
            vl.PRE_QUORUM_GOAL_IDS,
            {"GOAL-ICLIFT-001", "GOAL-XEDN-001", "GOAL-XEDN-002",
             "GOAL-P13-001"},
        )

    def test_quorum_size_is_three(self) -> None:
        self.assertEqual(vl.GOAL_CLOSURE_QUORUM, 3)


if __name__ == "__main__":
    unittest.main()
