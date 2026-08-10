"""A policy-tier variant changes how hard a role thinks, and nothing else.

`tests/test_subagent_reasoning_effort.py` covers the binding of a role's DEFAULT
policy to its agent file. This covers the second half: a role whose tasks are
sometimes routed elsewhere -- a claimed breakthrough to `review-breakthrough`, a
frozen re-run to `executor-mechanical` -- needs a second binding, because one
agent file carries one effort.

That second binding is the risk these tests exist for. `variant_of` is
otherwise a way to mint a role with a familiar name, a familiar description, and
quietly different authority; nothing on the dispatch path would notice. So the
invariant is narrow and mechanical: same contract, same authority, same
capabilities, different policy. Nothing else may differ, and the checker must be
shown to catch each way it could.
"""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from orchestration import role_registry

REPO = Path(__file__).resolve().parents[1]
CLAUDE = "claude_code"


class VariantContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roles_doc = role_registry.load_roles()
        cls.policies_doc = role_registry.load_policies()

    def variants(self):
        for role, spec in self.roles_doc["roles"].items():
            if spec.get("variant_of"):
                yield role, spec, self.roles_doc["roles"][spec["variant_of"]]

    def test_the_repository_declares_variants_at_all(self) -> None:
        """Otherwise every assertion below passes vacuously."""
        self.assertTrue(list(self.variants()))

    def test_a_variant_differs_from_its_base_only_in_policy(self) -> None:
        for role, spec, base in self.variants():
            with self.subTest(role=role):
                self.assertEqual(spec["contract"], base["contract"])
                self.assertEqual(spec["authority"], base["authority"])
                self.assertEqual(sorted(spec["capabilities"]),
                                 sorted(base["capabilities"]))
                self.assertNotEqual(spec["default_policy"],
                                    base["default_policy"])

    def test_a_variant_binds_only_runtimes_that_express_effort(self) -> None:
        """A variant exists to carry a different effort per agent.

        Where effort comes from the session instead, the escalation arrives via
        `adapter env` and a second binding would be a second name for the same
        file's worth of contract.
        """
        for role, spec, _base in self.variants():
            for runtime in (spec.get("runtime_bindings") or {}):
                with self.subTest(role=role, runtime=runtime):
                    self.assertIsNotNone(
                        role_registry.effort_support(self.roles_doc, runtime))

    def test_a_variant_binding_declares_its_own_tier_effort(self) -> None:
        for role, spec, base in self.variants():
            binding = (spec.get("runtime_bindings") or {}).get(CLAUDE)
            if not binding:
                continue
            with self.subTest(role=role):
                declared = role_registry.read_declared_effort(
                    CLAUDE, REPO / binding)
                self.assertEqual(declared, role_registry.expected_effort(
                    self.roles_doc, self.policies_doc, role, CLAUDE))
                self.assertNotEqual(
                    declared,
                    role_registry.policy_reasoning_effort(
                        self.policies_doc, base["default_policy"]),
                    "a variant that thinks exactly as hard as its base is a "
                    "duplicate, not a tier")

    def test_the_escalated_review_tier_is_reachable(self) -> None:
        """`review-breakthrough` is `degradable: false`.

        With no binding for it, an unrecoverable-decision review on this runtime
        could only be downgraded -- which the policy forbids -- or pause the
        goal. That is the gap the variants close, so it is asserted rather than
        left to inspection.
        """
        self.assertFalse(
            self.policies_doc["policies"]["review-breakthrough"].get(
                "degradable", True))
        bound = {role for role, spec in self.roles_doc["roles"].items()
                 if spec["default_policy"] == "review-breakthrough"
                 and CLAUDE in (spec.get("runtime_bindings") or {})}
        self.assertEqual(bound, {"validator-breakthrough",
                                 "red-team-breakthrough"})
        for role in bound:
            with self.subTest(role=role):
                spec = self.roles_doc["roles"][role]
                self.assertTrue(spec["authority"]["independent_of_producer"])
                self.assertEqual(
                    role_registry.expected_effort(
                        self.roles_doc, self.policies_doc, role, CLAUDE),
                    "max")

    def test_the_agent_set_spans_the_effort_lattice(self) -> None:
        """Calibration means different levels, not one level written eight times.

        Each binding matching its own policy is not enough on its own: a set
        that collapsed to a single tier would satisfy every per-binding check
        and quietly lose the property the tiers exist for.
        """
        levels = role_registry.effort_support(self.roles_doc, CLAUDE)["levels"]
        declared = {
            role_registry.expected_effort(self.roles_doc, self.policies_doc,
                                          role, CLAUDE)
            for role, spec in self.roles_doc["roles"].items()
            if CLAUDE in (spec.get("runtime_bindings") or {})}
        self.assertEqual(declared, set(levels))

    def test_no_review_tier_thinks_less_than_a_producer_tier(self) -> None:
        order = {level: index for index, level in enumerate(
            role_registry.effort_support(self.roles_doc, CLAUDE)["levels"])}
        producers, reviewers = [], []
        for role, spec in self.roles_doc["roles"].items():
            if CLAUDE not in (spec.get("runtime_bindings") or {}):
                continue
            rank = order[role_registry.expected_effort(
                self.roles_doc, self.policies_doc, role, CLAUDE)]
            target = (reviewers if spec["authority"]["independent_of_producer"]
                      else producers)
            target.append(rank)
        self.assertTrue(producers and reviewers)
        self.assertGreaterEqual(min(reviewers), max(producers))


class VariantDriftTests(unittest.TestCase):
    """The checker must BITE. A guard nobody has seen fail is not a guard."""

    def setUp(self) -> None:
        self.roles_doc = role_registry.load_roles()
        self.policies_doc = role_registry.load_policies()

    def _problems(self, mutate) -> list[str]:
        doc = copy.deepcopy(self.roles_doc)
        mutate(doc["roles"]["validator-breakthrough"], doc)
        return [problem for problem in role_registry.check(doc, self.policies_doc)
                if problem.startswith("validator-breakthrough:")]

    def test_the_unmutated_table_is_clean(self) -> None:
        self.assertEqual(
            role_registry.check(self.roles_doc, self.policies_doc), [])

    def test_widened_authority_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec["authority"].__setitem__(
                "may_change_official_state", True))
        self.assertTrue(any("different authority" in problem
                            for problem in problems), problems)

    def test_dropped_independence_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec["authority"].__setitem__(
                "independent_of_producer", False))
        self.assertTrue(any("different authority" in problem
                            for problem in problems), problems)

    def test_extra_capability_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec["capabilities"].append("web_search"))
        self.assertTrue(any("different capabilities" in problem
                            for problem in problems), problems)

    def test_foreign_contract_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec.__setitem__("contract",
                                                "agents/red-team.md"))
        self.assertTrue(any("share its contract" in problem
                            for problem in problems), problems)

    def test_same_policy_as_the_base_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec.__setitem__("default_policy",
                                                "review-adversarial"))
        self.assertTrue(any("duplicate rather than a tier" in problem
                            for problem in problems), problems)

    def test_unknown_base_role_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec.__setitem__("variant_of", "nonexistent"))
        self.assertTrue(any("unknown role" in problem
                            for problem in problems), problems)

    def test_a_variant_of_a_variant_is_reported(self) -> None:
        problems = self._problems(
            lambda spec, _doc: spec.__setitem__("variant_of",
                                                "executor-mechanical"))
        self.assertTrue(any("itself a variant" in problem
                            for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()
