#!/usr/bin/env python3
"""Tests for model-policy capability resolution."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_policy


def capabilities(
    model_id: str = "gpt-5.6-sol-high",
    resolved_model_id: str = "gpt-5.6-sol-high",
    efforts: list[str] | None = None,
) -> dict:
    return {
        "schema": model_policy.CAPABILITY_SCHEMA,
        "adapter_version": "cursor-test-adapter/1",
        "models": [
            {
                "model_id": model_id,
                "resolved_model_id": resolved_model_id,
                "available_reasoning_efforts": efforts or ["high"],
            }
        ],
    }


class ModelPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = model_policy.load_catalog()

    def test_exact_effort_resolution_is_not_fallback(self) -> None:
        receipt = model_policy.resolve(
            "executor-terra",
            capabilities(
                model_id="gpt-5.6-terra",
                resolved_model_id="gpt-5.6-terra",
            ),
            catalog=self.catalog,
        )
        self.assertEqual(receipt["requested_model_id"], "gpt-5.6-terra")
        self.assertEqual(receipt["requested_reasoning_effort"], "high")
        self.assertEqual(receipt["resolved_reasoning_effort"], "high")
        self.assertFalse(receipt["fallback_used"])
        self.assertEqual(receipt["authorization"]["type"], "policy_exact")

    def test_unavailable_profile_uses_declared_model_alternative(self) -> None:
        receipt = model_policy.resolve(
            "research-sol-max", capabilities(), catalog=self.catalog
        )
        self.assertEqual(receipt["requested_model_id"], "gpt-5.6-sol-max")
        self.assertEqual(receipt["resolved_model_id"], "gpt-5.6-sol-high")
        self.assertTrue(receipt["fallback_used"])

    def test_explicit_legacy_handoff_authorization_takes_precedence(self) -> None:
        handoff = {
            "policy": "research-sol-max",
            "fallback_allowed": True,
            "fallback_model": "gpt-5.6-sol-high",
            "authorization_ref": "DEC-20260722-004",
            "required_resolution": {
                "requested_policy": "research-sol-max",
                "resolved_model_id": "gpt-5.6-sol-high",
                "reasoning_effort": "high",
                "fallback_used": True,
            },
            "independent_session_required": False,
        }
        receipt = model_policy.resolve(
            "research-sol-max",
            capabilities(),
            catalog=self.catalog,
            handoff_inference=handoff,
        )
        self.assertEqual(receipt["authorization"]["type"], "handoff")
        self.assertEqual(receipt["authorization"]["ref"], "DEC-20260722-004")

    def test_required_handoff_fallback_precedes_available_policy_exact(self) -> None:
        available = capabilities()
        available["models"].append(
            {
                "model_id": "gpt-5.6-sol-max",
                "resolved_model_id": "gpt-5.6-sol-max",
                "available_reasoning_efforts": ["high"],
            }
        )
        handoff = {
            "policy": "research-sol-max",
            "fallback_allowed": True,
            "fallback_model": "gpt-5.6-sol-high",
            "authorization_ref": "DEC-20260722-004",
            "required_resolution": {
                "requested_policy": "research-sol-max",
                "resolved_model_id": "gpt-5.6-sol-high",
                "reasoning_effort": "high",
                "fallback_used": True,
            },
            "independent_session_required": False,
        }
        receipt = model_policy.resolve(
            "research-sol-max",
            available,
            catalog=self.catalog,
            handoff_inference=handoff,
        )
        self.assertEqual(receipt["resolved_model_id"], "gpt-5.6-sol-high")
        self.assertTrue(receipt["fallback_used"])
        self.assertEqual(receipt["authorization"]["type"], "handoff")

    def test_required_handoff_fallback_does_not_silently_use_policy_exact(self) -> None:
        handoff = {
            "policy": "research-sol-max",
            "fallback_allowed": True,
            "fallback_model": "gpt-5.6-sol-high",
            "authorization_ref": "DEC-20260722-004",
            "required_resolution": {
                "requested_policy": "research-sol-max",
                "resolved_model_id": "gpt-5.6-sol-high",
                "reasoning_effort": "high",
                "fallback_used": True,
            },
            "independent_session_required": False,
        }
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "required handoff fallback"
        ):
            model_policy.resolve(
                "research-sol-max",
                capabilities(
                    model_id="gpt-5.6-sol-max",
                    resolved_model_id="gpt-5.6-sol-max",
                ),
                catalog=self.catalog,
                handoff_inference=handoff,
            )

    def test_handoff_cannot_silently_override_policy_model_or_effort(self) -> None:
        base = {
            "policy": "review-xhigh",
            "requested_model_id": "gpt-5.6-terra",
            "requested_reasoning_effort": "high",
            "fallback_allowed": False,
            "independent_session_required": False,
        }
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "cannot override the policy model"
        ):
            model_policy.resolve(
                "review-xhigh",
                capabilities(
                    model_id="gpt-5.6-terra",
                    resolved_model_id="gpt-5.6-terra",
                ),
                catalog=self.catalog,
                handoff_inference=base,
            )
        effort_only = {**base, "requested_model_id": None}
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "cannot override the policy effort"
        ):
            model_policy.validate_handoff_inference(effort_only, self.catalog)

    def test_review_xhigh_uses_declared_high_alternative_auditably(self) -> None:
        handoff = {
            "policy": "review-xhigh",
            "fallback_allowed": False,
            "independent_session_required": True,
        }
        receipt = model_policy.resolve(
            "review-xhigh",
            capabilities(),
            catalog=self.catalog,
            handoff_inference=handoff,
        )
        self.assertEqual(receipt["requested_reasoning_effort"], "xhigh")
        self.assertEqual(receipt["resolved_model_id"], "gpt-5.6-sol-high")
        self.assertEqual(receipt["resolved_reasoning_effort"], "high")
        self.assertEqual(receipt["available_reasoning_efforts"], ["high"])
        self.assertTrue(receipt["fallback_used"])
        self.assertEqual(
            receipt["authorization"]["type"], "policy_declared_alternative"
        )
        self.assertTrue(receipt["independent_session_required"])

    def test_exact_xhigh_remains_preferred_when_available(self) -> None:
        receipt = model_policy.resolve(
            "review-xhigh",
            capabilities(
                model_id="gpt-5.6-sol",
                resolved_model_id="gpt-5.6-sol-xhigh", efforts=["xhigh"]
            ),
            catalog=self.catalog,
        )
        self.assertEqual(receipt["resolved_reasoning_effort"], "xhigh")
        self.assertFalse(receipt["fallback_used"])

    def test_effort_specific_runtime_identifiers_coexist(self) -> None:
        available = capabilities()
        available["models"].append(
            {
                "model_id": "gpt-5.6-sol",
                "resolved_model_id": "gpt-5.6-sol-xhigh",
                "available_reasoning_efforts": ["xhigh"],
            }
        )
        research = model_policy.resolve(
            "research-sol-max", available, catalog=self.catalog
        )
        review = model_policy.resolve(
            "review-xhigh", available, catalog=self.catalog
        )
        self.assertEqual(research["resolved_model_id"], "gpt-5.6-sol-high")
        self.assertEqual(review["resolved_model_id"], "gpt-5.6-sol-xhigh")
        self.assertTrue(research["fallback_used"])
        self.assertFalse(review["fallback_used"])

    def test_unavailable_undeclared_effort_stops(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["policies"]["review-xhigh"]["allowed_alternatives"] = []
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "no authorized available resolution"
        ):
            model_policy.resolve(
                "review-xhigh", capabilities(), catalog=catalog
            )

    def test_capability_cannot_invent_provider_effort(self) -> None:
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "advertises unsupported efforts"
        ):
            model_policy.resolve(
                "review-xhigh",
                capabilities(efforts=["low"]),
                catalog=self.catalog,
            )

    def test_malformed_catalog_and_capability_shapes_fail_closed(self) -> None:
        malformed_catalog = copy.deepcopy(self.catalog)
        malformed_catalog["reasoning_efforts"] = []
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "reasoning_efforts must be an object"
        ):
            model_policy.validate_catalog(malformed_catalog)
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "runtime capabilities must be an object"
        ):
            model_policy.validate_capabilities([], self.catalog)  # type: ignore[arg-type]

    def test_legacy_handoff_defaults_effort_from_policy(self) -> None:
        handoff = {
            "policy": "research-sol-max",
            "requested_model_id": None,
            "requested_reasoning_effort": None,
            "fallback_allowed": False,
            "independent_session_required": False,
        }
        receipt = model_policy.resolve(
            "research-sol-max",
            capabilities(),
            catalog=self.catalog,
            handoff_inference=handoff,
        )
        self.assertEqual(receipt["requested_model_id"], "gpt-5.6-sol-max")
        self.assertEqual(receipt["requested_reasoning_effort"], "high")
        self.assertTrue(receipt["fallback_used"])

    def test_resolution_receipt_validation_rejects_schema_and_auth_tampering(
        self,
    ) -> None:
        receipt = model_policy.resolve(
            "review-xhigh",
            capabilities(),
            catalog=self.catalog,
        )
        model_policy.validate_resolution_receipt(receipt, self.catalog)

        bad_schema = copy.deepcopy(receipt)
        bad_schema["metadata_schema"] = "crypto.autoresearch.model_resolution.v3"
        with self.assertRaisesRegex(model_policy.ModelPolicyError, "metadata_schema"):
            model_policy.validate_resolution_receipt(bad_schema, self.catalog)

        bad_authorization = copy.deepcopy(receipt)
        bad_authorization["authorization"]["ref"] = "unrelated-authorization"
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "authorization is not declared"
        ):
            model_policy.validate_resolution_receipt(
                bad_authorization, self.catalog
            )

    def test_resolution_receipt_preserves_policy_independence(self) -> None:
        receipt = model_policy.resolve(
            "review-xhigh",
            capabilities(),
            catalog=self.catalog,
        )
        receipt["independent_session_required"] = False
        with self.assertRaisesRegex(
            model_policy.ModelPolicyError, "cannot disable"
        ):
            model_policy.validate_resolution_receipt(receipt, self.catalog)


if __name__ == "__main__":
    unittest.main()
