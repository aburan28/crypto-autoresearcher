"""Tests for per-subagent reasoning effort and policy-tier role variants.

Effort is the dominant cost and latency term in this program, and
`orchestration/model-policies.yaml` calibrates it per policy for stated
reasons. Once a runtime binding can carry that number, it can also disagree
with it -- silently, and in the dangerous direction: a review that thinks less
than its policy requires still returns a signed-off verdict.

These tests assert the two properties that make the arrangement safe: a binding
states exactly the effort its policy asks for, and a policy-tier variant may
change nothing except how hard the model thinks.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from orchestration.role_registry import (REPO, check, load_policies,
                                         load_roles, parse_frontmatter,
                                         resolved_effort, role_effort,
                                         role_spec, runtime_effort_field,
                                         runtime_effort_levels)

RUNTIME = "claude_code"


class EffortBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roles_doc = load_roles()
        cls.policies_doc = load_policies()
        cls.field = runtime_effort_field(cls.roles_doc, RUNTIME)
        cls.levels = runtime_effort_levels(cls.roles_doc, RUNTIME)

    def _claude_bindings(self):
        for role, spec in self.roles_doc["roles"].items():
            binding = (spec.get("runtime_bindings") or {}).get(RUNTIME)
            if binding:
                yield role, spec, REPO / binding

    def test_the_runtime_declares_how_it_carries_effort(self) -> None:
        """Without this map the check below silently passes on every role."""
        self.assertEqual(self.field, "effort")
        self.assertEqual(self.levels, ["low", "medium", "high", "xhigh", "max"])

    def test_every_binding_states_the_effort_its_policy_asks_for(self) -> None:
        for role, spec, path in self._claude_bindings():
            with self.subTest(role=role):
                declared = parse_frontmatter(path).get(self.field)
                wanted = resolved_effort(self.policies_doc,
                                         spec["default_policy"])
                self.assertIsNotNone(wanted,
                                     f"policy {spec['default_policy']} states no effort")
                self.assertEqual(declared, wanted)
                self.assertIn(declared, self.levels)

    def test_no_binding_names_a_model(self) -> None:
        """Effort is expressible here; a model identifier still is not."""
        for role, _spec, path in self._claude_bindings():
            with self.subTest(role=role):
                self.assertEqual(parse_frontmatter(path).get("model"),
                                 "inherit")

    def test_the_agent_set_spans_the_whole_effort_lattice(self) -> None:
        """Calibration means DIFFERENT levels, not one level written five times.

        The point of per-role effort is that a frozen protocol is not re-derived
        at review depth and a claimed break is not reviewed at execution depth.
        A set that collapses to one or two levels has lost that, and it would
        otherwise fail silently -- every individual binding would still match
        its policy.
        """
        declared = {parse_frontmatter(path).get(self.field)
                    for _role, _spec, path in self._claude_bindings()}
        self.assertEqual(declared, set(self.levels))

    def test_review_roles_think_at_least_as_hard_as_producers(self) -> None:
        """An independent review must not be cheaper than the work it reviews."""
        order = {level: index for index, level in enumerate(self.levels)}
        producers = [order[role_effort(self.roles_doc, self.policies_doc, role)]
                     for role, spec in self.roles_doc["roles"].items()
                     if not spec["authority"].get("independent_of_producer")]
        reviewers = [order[role_effort(self.roles_doc, self.policies_doc, role)]
                     for role, spec in self.roles_doc["roles"].items()
                     if spec["authority"].get("independent_of_producer")]
        self.assertTrue(producers and reviewers)
        self.assertGreaterEqual(min(reviewers), max(producers))

    def test_breakthrough_tier_exists_and_is_reachable(self) -> None:
        """`review-breakthrough` is degradable: false, so it needs a binding.

        Without one it could not be honoured on this runtime at all: the harness
        would have to downgrade the review (forbidden) or pause the goal.
        """
        for role in ("validator-breakthrough", "red-team-breakthrough"):
            with self.subTest(role=role):
                spec = role_spec(self.roles_doc, role)
                self.assertEqual(spec["default_policy"], "review-breakthrough")
                self.assertEqual(
                    role_effort(self.roles_doc, self.policies_doc, role), "max")
                self.assertTrue(
                    (REPO / spec["runtime_bindings"][RUNTIME]).exists())
        self.assertFalse(
            self.policies_doc["policies"]["review-breakthrough"].get("degradable",
                                                                     True))


class VariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roles_doc = load_roles()
        cls.policies_doc = load_policies()

    def _variants(self):
        for role, spec in self.roles_doc["roles"].items():
            if spec.get("variant_of"):
                yield role, spec, role_spec(self.roles_doc, spec["variant_of"])

    def test_there_is_at_least_one_variant(self) -> None:
        self.assertTrue(list(self._variants()))

    def test_a_variant_changes_only_its_policy_tier(self) -> None:
        for role, spec, base in self._variants():
            with self.subTest(role=role):
                self.assertEqual(spec["contract"], base["contract"])
                self.assertEqual(spec["authority"], base["authority"])
                self.assertEqual(sorted(spec["capabilities"]),
                                 sorted(base["capabilities"]))
                self.assertNotEqual(spec["default_policy"],
                                    base["default_policy"])

    def test_a_variant_of_a_variant_is_rejected(self) -> None:
        doc = load_roles()
        doc["roles"]["executor-mechanical"]["variant_of"] = "validator-breakthrough"
        problems = check(doc, self.policies_doc)
        self.assertTrue(any("itself a variant" in problem
                            or "different authority" in problem
                            or "different capabilities" in problem
                            or "share its contract" in problem
                            for problem in problems), problems)


class DriftDetectionTests(unittest.TestCase):
    """The checks must BITE. A guard nobody has seen fail is not a guard."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.policies_doc = load_policies()

    def _doc_with_binding(self, text: str) -> dict:
        binding = self.tmp / "validator.md"
        binding.write_text(text, encoding="utf-8")
        doc = load_roles()
        doc["roles"]["validator"]["runtime_bindings"][RUNTIME] = str(
            binding.relative_to(REPO)) if binding.is_relative_to(REPO) else str(binding)
        # `check` resolves bindings against REPO; an absolute path survives that
        # join unchanged, which is what makes a temp file usable here.
        return doc

    def _problems(self, effort_line: str) -> list[str]:
        text = ("---\n"
                "name: validator\n"
                "description: test fixture\n"
                "tools: Read, Grep, Glob, Write, Edit, Bash\n"
                "model: inherit\n"
                f"{effort_line}"
                "---\n\nbody\n")
        return [problem for problem in check(self._doc_with_binding(text),
                                             self.policies_doc)
                if problem.startswith("validator/")]

    def test_a_missing_effort_is_an_error(self) -> None:
        self.assertTrue(any("states no 'effort'" in problem
                            for problem in self._problems("")))

    def test_an_effort_below_its_policy_is_an_error(self) -> None:
        problems = self._problems("effort: low\n")
        self.assertTrue(any("asks for 'xhigh'" in problem
                            for problem in problems), problems)

    def test_an_invented_level_is_an_error(self) -> None:
        problems = self._problems("effort: extreme\n")
        self.assertTrue(any("is not one of" in problem
                            for problem in problems), problems)

    def test_a_named_model_is_an_error(self) -> None:
        text = ("---\n"
                "name: validator\n"
                "description: test fixture\n"
                "tools: Read, Grep, Glob, Write, Edit, Bash\n"
                "model: claude-opus-5\n"
                "effort: xhigh\n"
                "---\n\nbody\n")
        problems = [problem for problem in check(self._doc_with_binding(text),
                                                 self.policies_doc)
                    if problem.startswith("validator/")]
        self.assertTrue(any("never a model identifier" in problem
                            for problem in problems), problems)

    def test_the_real_bindings_are_clean(self) -> None:
        self.assertEqual(check(load_roles(), self.policies_doc), [])


if __name__ == "__main__":
    unittest.main()
