#!/usr/bin/env python3
"""Tests for the focused autoresearch queue selector."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import autoresearch_focus as focus


def candidate(identifier: str, impact: int, status: str = "queued") -> dict:
    outcome_state = {
        "completed_positive": "positive",
        "completed_negative": "negative",
        "inconclusive": "inconclusive",
    }.get(status, "untested")
    return {
        "id": identifier,
        "title": identifier,
        "status": status,
        "uncertainty": "A decisive uncertainty.",
        "positive_decision": "Expand only after verification.",
        "negative_decision": "Close the tested scope.",
        "next_action": "Run one frozen experiment.",
        "dependencies": [],
        "expansion_of": None,
        "ambiguities": [
            {
                "question": "Which deterministic convention applies?",
                "resolution": "Use the lexicographically first valid convention.",
                "basis": "The choice is target-independent and auditable.",
                "confidence": "high",
            }
        ],
        "scores": {
            "decision_impact": impact,
            "falsifiability": 4,
            "mechanism_novelty": 3,
            "reproduction_readiness": 3,
            "cost_efficiency": 4,
        },
        "outcome": {
            "state": outcome_state,
            "independently_verified": status in focus.TERMINAL_STATES,
            "artifacts": ["receipt.json"] if status in focus.TERMINAL_STATES else [],
        },
        "attention_contract": {
            "decisive_evidence": "One exact frozen result changes the decision.",
            "inconclusive_decision": "Keep the lane closed and rerank the queue.",
            "local_ambiguity_rule": "Resolve only target-independent conventions.",
            "peripheral_exclusions": ["No parameter sweep."],
            "rerank_trigger": "A signed terminal receipt is available.",
        },
        "resource_estimate": {
            "wall_clock_seconds": 60,
            "cpu_hours": 0.1,
            "maximum_memory_gb": 1,
            "maximum_runs": 1,
            "dominant_cost": "One deterministic exact replay.",
            "complexity_hypothesis": "Constant work for the fixture.",
            "sharding_plan": "Run as one shard.",
            "stop_rule": "Stop after the frozen replay.",
            "dominant_stage_id": "exact-replay",
            "stages": [
                {
                    "id": "exact-replay",
                    "purpose": "Execute and check the frozen fixture.",
                    "wall_clock_seconds": 60,
                    "cpu_hours": 0.1,
                    "maximum_memory_gb": 1,
                    "parallel_shards": 1,
                    "dominant_operation": "One exact replay.",
                    "stop_rule": "Stop after the exact check.",
                }
            ],
        },
    }


def queue(*candidates: dict, max_active: int = 2) -> dict:
    return {
        "schema": focus.SCHEMA,
        "objective": "Beat the generic rho/Shoup boundary with full accounting.",
        "max_active": max_active,
        "candidates": list(candidates),
        "claims": [],
        "runs": [],
        "corrections": [],
    }


def completed_run(identifier: str, experiment_id: str) -> dict:
    return {
        "id": identifier,
        "experiment_id": experiment_id,
        "purpose": "Reproduce one frozen claim.",
        "status": "completed",
        "depends_on_runs": [],
        "artifacts": [f"{identifier}.json"],
        "failure_reason": None,
    }


def reproduced_claim(identifier: str, experiment_id: str, run_id: str) -> dict:
    return {
        "id": identifier,
        "statement": "The exact fixture identity holds.",
        "scope": "One frozen toy fixture.",
        "target_result": "Exact equality.",
        "observed_result": "Exact equality on the frozen fixture.",
        "verdict": "reproduced",
        "independently_verified": True,
        "evidence_artifacts": [f"{run_id}.json"],
        "evidence_runs": [run_id],
        "linked_experiments": [experiment_id],
        "scope_deviations": [],
        "blockers": [],
    }


class FocusHarnessTests(unittest.TestCase):
    def test_selects_only_highest_scoring_candidates_under_cap(self) -> None:
        plan = focus.select(
            queue(candidate("LOW", 1), candidate("HIGH", 4), candidate("MID", 3))
        )
        self.assertEqual(
            [item["id"] for item in plan["critical_experiments"]],
            ["HIGH", "MID"],
        )
        self.assertTrue(plan["gates"]["focus_cap_respected"])

    def test_nonterminal_dependency_blocks_selection(self) -> None:
        parent = candidate("PARENT", 1)
        child = candidate("CHILD", 4)
        child["dependencies"] = ["PARENT"]
        plan = focus.select(queue(parent, child, max_active=1))
        self.assertEqual(plan["critical_experiments"][0]["id"], "PARENT")
        deferred = {item["id"]: item for item in plan["deferred"]}
        self.assertEqual(
            deferred["CHILD"]["reason"], ["dependency_not_terminal:PARENT"]
        )

    def test_unverified_positive_parent_blocks_expansion(self) -> None:
        parent = candidate("PARENT", 1, "completed_positive")
        parent["outcome"]["independently_verified"] = False
        child = candidate("CHILD", 4)
        child["expansion_of"] = "PARENT"
        plan = focus.select(queue(parent, child, max_active=1))
        self.assertEqual(plan["critical_experiments"], [])
        self.assertIn(
            "positive_parent_not_independently_verified:PARENT",
            plan["deferred"][0]["reason"],
        )

    def test_expansion_edge_kind_preserves_parent_disposition(self) -> None:
        parent = candidate("PARENT", 1, "inconclusive")
        child = candidate("CHILD", 4)
        child["dependencies"] = ["PARENT"]
        child["expansion_of"] = "PARENT"
        plan = focus.select(queue(parent, child, max_active=1))
        expansion_edges = [
            edge
            for edge in plan["experiment_graph"]["candidate_edges"]
            if edge["kind"].endswith("_expansion")
        ]
        self.assertEqual(expansion_edges[0]["kind"], "inconclusive_scope_expansion")

        positive_parent = candidate("POSITIVE", 1, "completed_positive")
        positive_child = candidate("SUCCESSOR", 4)
        positive_child["dependencies"] = ["POSITIVE"]
        positive_child["expansion_of"] = "POSITIVE"
        positive_plan = focus.select(
            queue(positive_parent, positive_child, max_active=1)
        )
        positive_edges = [
            edge
            for edge in positive_plan["experiment_graph"]["candidate_edges"]
            if edge["kind"].endswith("_expansion")
        ]
        self.assertEqual(
            positive_edges[0]["kind"], "verified_positive_expansion"
        )

    def test_active_candidate_cannot_bypass_dependency_gate(self) -> None:
        parent = candidate("PARENT", 1)
        child = candidate("CHILD", 4, "active")
        child["dependencies"] = ["PARENT"]
        with self.assertRaises(focus.QueueError):
            focus.validate_queue(queue(parent, child, max_active=1))

    def test_rejects_ambiguity_without_resolution(self) -> None:
        broken = candidate("BROKEN", 4)
        broken["ambiguities"][0]["resolution"] = ""
        with self.assertRaises(focus.QueueError):
            focus.validate_queue(queue(broken))

    def test_plan_is_deterministic_and_hash_bound(self) -> None:
        source = queue(candidate("A", 4), candidate("B", 3))
        first = focus.select(source)
        second = focus.select(copy.deepcopy(source))
        self.assertEqual(first, second)
        self.assertEqual(first["source_queue_sha256"], focus.digest(source))

    def test_emits_claim_matrix_run_dag_and_estimate(self) -> None:
        experiment = candidate("EXP", 4)
        source = queue(experiment, max_active=1)
        source["runs"] = [completed_run("RUN-1", "EXP")]
        source["claims"] = [reproduced_claim("CLAIM-1", "EXP", "RUN-1")]
        plan = focus.select(source)
        self.assertEqual(plan["claim_matrix"][0]["verdict"], "reproduced")
        self.assertEqual(plan["experiment_graph"]["run_nodes"][0]["id"], "RUN-1")
        self.assertEqual(
            plan["critical_experiments"][0]["resource_estimate"]["maximum_runs"],
            1,
        )
        self.assertTrue(plan["gates"]["claim_evidence_uses_completed_runs_only"])
        self.assertTrue(plan["gates"]["all_selected_have_attention_contracts"])
        self.assertTrue(
            plan["gates"]["stage_estimates_are_advisory"]
        )
        report = focus.render_markdown(plan)
        self.assertIn("## Attention Contracts", report)
        self.assertIn("## Optional Stage Estimates", report)
        self.assertIn("## Claim Matrix", report)
        self.assertIn("`CLAIM-1`", report)
        self.assertIn("## Run Table", report)
        self.assertIn("`RUN-1`", report)
        self.assertIn("## Corrections", report)

    def test_failed_run_cannot_support_claim(self) -> None:
        source = queue(candidate("EXP", 4))
        run = completed_run("RUN-1", "EXP")
        run.update({"status": "failed", "artifacts": [], "failure_reason": "crash"})
        source["runs"] = [run]
        source["claims"] = [reproduced_claim("CLAIM-1", "EXP", "RUN-1")]
        with self.assertRaisesRegex(focus.QueueError, "noncompleted runs"):
            focus.validate_queue(source)

    def test_reproduced_claim_requires_independent_verification(self) -> None:
        source = queue(candidate("EXP", 4))
        source["runs"] = [completed_run("RUN-1", "EXP")]
        claim = reproduced_claim("CLAIM-1", "EXP", "RUN-1")
        claim["independently_verified"] = False
        source["claims"] = [claim]
        with self.assertRaisesRegex(focus.QueueError, "independent verification"):
            focus.validate_queue(source)

    def test_claim_artifacts_must_be_bound_to_cited_runs(self) -> None:
        source = queue(candidate("EXP", 4))
        source["runs"] = [completed_run("RUN-1", "EXP")]
        claim = reproduced_claim("CLAIM-1", "EXP", "RUN-1")
        claim["evidence_artifacts"] = ["unbound.json"]
        source["claims"] = [claim]
        with self.assertRaisesRegex(focus.QueueError, "not bound to cited runs"):
            focus.validate_queue(source)

    def test_correction_preserves_prior_and_corrected_values(self) -> None:
        source = queue(candidate("EXP", 4))
        source["candidates"][0]["next_action"] = "Run a broad sweep."
        source["corrections"] = [
            {
                "id": "CORR-1",
                "recorded_at": "2026-07-17T00:00:00Z",
                "record_type": "candidate",
                "record_id": "EXP",
                "field": "next_action",
                "prior_value": "Run a broad sweep.",
                "corrected_value": "Run one frozen experiment.",
                "reason": "The broader wording exceeded the approved scope.",
                "evidence_artifacts": ["contract.md"],
            }
        ]
        plan = focus.select(source)
        self.assertEqual(plan["corrections"][0]["prior_value"], "Run a broad sweep.")
        self.assertEqual(
            plan["critical_experiments"][0]["next_action"],
            "Run one frozen experiment.",
        )

    def test_corrections_materialize_before_dependency_selection(self) -> None:
        parent = candidate("PARENT", 1)
        child = candidate("CHILD", 4)
        child["dependencies"] = ["PARENT"]
        source = queue(parent, child, max_active=1)
        source["corrections"] = [
            {
                "id": "CORR-STATUS",
                "recorded_at": "2026-07-18T00:00:00Z",
                "record_type": "candidate",
                "record_id": "PARENT",
                "field": "status",
                "prior_value": "queued",
                "corrected_value": "inconclusive",
                "reason": "The theorem audit reached a terminal scoped disposition.",
                "evidence_artifacts": ["receipt.json"],
            },
            {
                "id": "CORR-OUTCOME",
                "recorded_at": "2026-07-18T00:00:01Z",
                "record_type": "candidate",
                "record_id": "PARENT",
                "field": "outcome.state",
                "prior_value": "untested",
                "corrected_value": "inconclusive",
                "reason": "Bind the terminal scoped outcome.",
                "evidence_artifacts": ["receipt.json"],
            },
            {
                "id": "CORR-ARTIFACTS",
                "recorded_at": "2026-07-18T00:00:02Z",
                "record_type": "candidate",
                "record_id": "PARENT",
                "field": "outcome.artifacts",
                "prior_value": [],
                "corrected_value": ["receipt.json"],
                "reason": "Bind the terminal receipt.",
                "evidence_artifacts": ["receipt.json"],
            },
        ]
        plan = focus.select(source)
        self.assertEqual(plan["critical_experiments"][0]["id"], "CHILD")
        receipts = {item["id"]: item for item in plan["completed_receipts"]}
        self.assertEqual(receipts["PARENT"]["status"], "inconclusive")

    def test_rejects_correction_with_stale_prior_value(self) -> None:
        source = queue(candidate("EXP", 4))
        source["corrections"] = [
            {
                "id": "CORR-STALE",
                "recorded_at": "2026-07-18T00:00:00Z",
                "record_type": "candidate",
                "record_id": "EXP",
                "field": "next_action",
                "prior_value": "A stale action.",
                "corrected_value": "Run one narrow experiment.",
                "reason": "Attempt a stale correction.",
                "evidence_artifacts": ["contract.md"],
            }
        ]
        with self.assertRaisesRegex(focus.QueueError, "prior_value does not match"):
            focus.validate_queue(source)

    def test_materializes_indexed_correction_path(self) -> None:
        source = queue(candidate("EXP", 4), max_active=1)
        old_resolution = source["candidates"][0]["ambiguities"][0]["resolution"]
        source["corrections"] = [
            {
                "id": "CORR-INDEXED",
                "recorded_at": "2026-07-18T00:00:00Z",
                "record_type": "candidate",
                "record_id": "EXP",
                "field": "ambiguities[0].resolution",
                "prior_value": old_resolution,
                "corrected_value": "Use the first valid convention by canonical hash.",
                "reason": "Make the deterministic convention explicit.",
                "evidence_artifacts": ["contract.md"],
            }
        ]
        plan = focus.select(source)
        self.assertEqual(
            plan["critical_experiments"][0]["ambiguity_resolutions"][0][
                "resolution"
            ],
            "Use the first valid convention by canonical hash.",
        )

    def test_rejects_candidate_and_run_cycles(self) -> None:
        first = candidate("A", 4)
        second = candidate("B", 3)
        first["dependencies"] = ["B"]
        second["dependencies"] = ["A"]
        with self.assertRaisesRegex(focus.QueueError, "candidate graph contains a cycle"):
            focus.validate_queue(queue(first, second))

        source = queue(candidate("EXP", 4))
        run_a = completed_run("RUN-A", "EXP")
        run_b = completed_run("RUN-B", "EXP")
        run_a["depends_on_runs"] = ["RUN-B"]
        run_b["depends_on_runs"] = ["RUN-A"]
        source["runs"] = [run_a, run_b]
        with self.assertRaisesRegex(focus.QueueError, "run graph contains a cycle"):
            focus.validate_queue(source)

    def test_v3_requires_attention_contract(self) -> None:
        experiment = candidate("EXP", 4)
        experiment.pop("attention_contract")
        with self.assertRaisesRegex(focus.QueueError, "attention_contract"):
            focus.validate_queue(queue(experiment))

    def test_v3_accepts_unreconciled_advisory_stage_estimate(self) -> None:
        experiment = candidate("EXP", 4)
        experiment["resource_estimate"]["stages"][0]["wall_clock_seconds"] = 59
        focus.validate_queue(queue(experiment))

    def test_null_estimates_and_no_stage_table_are_runnable(self):
        experiment = candidate("EXP", 4)
        estimate = experiment["resource_estimate"]
        estimate.update(wall_clock_seconds=None, cpu_hours=None,
                        maximum_runs=None, stages=None)
        estimate.pop("dominant_stage_id")
        plan = focus.select(queue(experiment))
        self.assertEqual(len(plan["critical_experiments"]), 1)
        self.assertIn("Optional Stage Estimates", focus.render_markdown(plan))

    def test_v2_queue_remains_readable(self) -> None:
        source = queue(candidate("LEGACY-V2", 4))
        source["schema"] = focus.SCHEMA_V2
        source["candidates"][0].pop("attention_contract")
        source["candidates"][0]["resource_estimate"].pop("dominant_stage_id")
        source["candidates"][0]["resource_estimate"].pop("stages")
        plan = focus.select(source)
        self.assertEqual(plan["critical_experiments"][0]["id"], "LEGACY-V2")

    def test_v1_queue_remains_readable(self) -> None:
        source = queue(candidate("LEGACY", 4))
        source["schema"] = focus.SCHEMA_V1
        source.pop("claims")
        source.pop("runs")
        source.pop("corrections")
        source["candidates"][0].pop("attention_contract")
        source["candidates"][0].pop("resource_estimate")
        plan = focus.select(source)
        self.assertEqual(plan["critical_experiments"][0]["id"], "LEGACY")


if __name__ == "__main__":
    unittest.main()
