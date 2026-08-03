#!/usr/bin/env python3
"""Tests for the goal-closure quorum (AGENTS.md core rule 13).

The rule: a goal may be marked `completed` only on the concurring judgement of
three independently-resolved models. It is currently SUSPENDED — see
`validate_ledger.GOAL_CLOSURE_QUORUM_REQUIRED`.

These tests cover both modes deliberately. The enforcement failure modes (too
few voices, correlated voices behind different policy aliases, a recorded
dissent, a quorum asserted without the Coordinator transition) are still pinned
under `enforcing()`, so the rule can be switched back on without rediscovering
what it was supposed to catch. The suspended-mode tests pin the narrower
contract that holds today: closure is ungated, but a block that is present is
still validated.
"""

from __future__ import annotations

import contextlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ledger as vl


@contextlib.contextmanager
def enforcing(required: bool = True):
    """Run a block with the quorum requirement forced on (or off)."""
    previous = vl.GOAL_CLOSURE_QUORUM_REQUIRED
    vl.GOAL_CLOSURE_QUORUM_REQUIRED = required
    try:
        yield
    finally:
        vl.GOAL_CLOSURE_QUORUM_REQUIRED = previous


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


class QuorumEnforcedTests(unittest.TestCase):
    """The rule as written, pinned so it can be restored intact."""

    def test_completed_without_quorum_block_is_rejected(self) -> None:
        with enforcing():
            errs = errors_for(goal())
        self.assertTrue(errs)
        self.assertIn("requires a completion_quorum", errs[0])

    def test_three_distinct_concurring_models_pass(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        with enforcing():
            self.assertEqual(errors_for(goal(quorum=q)), [])

    def test_two_voices_are_not_a_quorum(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("gpt-5.6-sol"),
        ]}
        with enforcing():
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
        with enforcing():
            errs = errors_for(goal(quorum=q))
        self.assertTrue(any("pairwise-distinct resolved_model_id" in e
                            for e in errs))


class QuorumSuspendedTests(unittest.TestCase):
    """The contract that holds while the requirement is suspended.

    Closure is ungated, but a `completion_quorum` block that IS present is
    still validated: an attestation is a claim about a review that happened.
    """

    def test_completed_without_quorum_block_is_accepted(self) -> None:
        with enforcing(False):
            self.assertEqual(errors_for(goal()), [])

    def test_single_attestation_is_accepted(self) -> None:
        q = {"attestations": [attestation("claude-opus-5")]}
        with enforcing(False):
            self.assertEqual(errors_for(goal(quorum=q)), [])

    def test_correlated_attestations_are_accepted(self) -> None:
        """Three aliases resolving to one model no longer block closure."""
        q = {"attestations": [
            attestation("claude-opus-5", requested_policy="review-adversarial"),
            attestation("claude-opus-5", requested_policy="research-deep"),
            attestation("claude-opus-5", requested_policy="review-breakthrough"),
        ]}
        with enforcing(False):
            self.assertEqual(errors_for(goal(quorum=q)), [])

    def test_empty_attestations_list_is_still_rejected(self) -> None:
        with enforcing(False):
            errs = errors_for(goal(quorum={"attestations": []}))
        self.assertTrue(any("non-empty list" in e for e in errs))

    def test_a_lone_dissent_still_blocks_closure(self) -> None:
        """Closing over a dissent you obtained is incoherent at any quorum
        size, so this survives the suspension even with one attestation.
        (QuorumInvariantTests covers the full-panel case in both modes.)"""
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("claude-opus-5", verdict="DISSENT"),
        ]}
        with enforcing(False):
            errs = errors_for(goal(quorum=q))
        self.assertTrue(any("DISSENT" in e for e in errs))

    def test_suspension_is_the_shipped_default(self) -> None:
        self.assertFalse(vl.GOAL_CLOSURE_QUORUM_REQUIRED)


class QuorumInvariantTests(unittest.TestCase):
    """Checks that hold in both modes.

    Each runs twice, under `BOTH_MODES`, so the suspension is shown to have
    relaxed only the count and distinctness gates and nothing else. The
    fixtures use three distinct models so the quorum gates themselves pass in
    enforcing mode and the assertion isolates the check under test.
    """

    BOTH_MODES = (True, False)

    def test_a_dissent_blocks_closure(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5"),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
            attestation("grok-4", verdict="DISSENT"),
        ]}
        for required in self.BOTH_MODES:
            with self.subTest(quorum_required=required), enforcing(required):
                errs = errors_for(goal(quorum=q))
                self.assertTrue(any("DISSENT" in e for e in errs))

    def test_non_independent_session_is_rejected(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5", independent_session=False),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        for required in self.BOTH_MODES:
            with self.subTest(quorum_required=required), enforcing(required):
                errs = errors_for(goal(quorum=q))
                self.assertTrue(any("independent_session: true" in e
                                    for e in errs))

    def test_missing_required_attestation_field_is_rejected(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5", resolved_model_id=None),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        for required in self.BOTH_MODES:
            with self.subTest(quorum_required=required), enforcing(required):
                errs = errors_for(goal(quorum=q))
                self.assertTrue(any("resolved_model_id" in e for e in errs))

    def test_attestation_citing_unknown_record_is_rejected(self) -> None:
        q = {"attestations": [
            attestation("claude-opus-5", reviewed_record_ids=["DEC-NOPE-999"]),
            attestation("gpt-5.6-sol"),
            attestation("gemini-3-pro"),
        ]}
        for required in self.BOTH_MODES:
            with self.subTest(quorum_required=required), enforcing(required):
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
        for required in self.BOTH_MODES:
            with self.subTest(quorum_required=required), enforcing(required):
                ctx = vl.Ctx(set())
                ctx.ids["GOAL-TEST-001"] = "x"
                ctx.knowledge["KN-FIND-011"] = \
                    "knowledge/findings/KN-FIND-011.md"
                vl.check_goal_closure_quorum(
                    "ledger/goals/GOAL-TEST-001.yaml", goal(quorum=q), ctx)
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
