#!/usr/bin/env python3
"""Tests for generated runtime agent bindings.

The point of generating bindings is that a role cannot hold a different tool
surface in one runtime than in another. These tests assert that property
directly, plus the two rules that keep the generated files honest: no contract
prose is copied, and no model identifier is named.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tomllib

import generate_runtime_agents as generator
from orchestration.role_registry import (REPO, check, effective_capabilities,
                                         expected_tools, load_policies,
                                         load_roles, over_granted,
                                         read_binding, role_spec)


class GeneratedBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roles_doc = load_roles()
        cls.files = generator.render(cls.roles_doc)

    def test_on_disk_bindings_match_the_generator(self) -> None:
        """`make check-harness` fails on drift; so does this, with the path."""
        for path, content in self.files.items():
            with self.subTest(path=path.relative_to(REPO)):
                self.assertTrue(path.exists(), "binding was never generated")
                self.assertEqual(
                    path.read_text(encoding="utf-8"), content,
                    "regenerate: python3 tools/generate_runtime_agents.py")

    def test_registry_reports_no_problems(self) -> None:
        self.assertEqual(check(self.roles_doc, load_policies()), [])

    def test_every_binding_reads_back_to_its_contract_surface(self) -> None:
        """The round trip that matters: what we wrote is what a checker sees."""
        for role, spec in self.roles_doc["roles"].items():
            for runtime, binding in (spec.get("runtime_bindings") or {}).items():
                with self.subTest(role=role, runtime=runtime):
                    name, granted = read_binding(runtime, REPO / binding)
                    self.assertEqual(name, role)
                    self.assertEqual(
                        granted, set(expected_tools(self.roles_doc, role, runtime)))

    def test_codex_files_are_valid_toml_with_only_known_keys(self) -> None:
        """Codex rejects unknown keys outright, so an invented one is fatal."""
        allowed = {"name", "description", "nickname_candidates", "sandbox_mode",
                   "developer_instructions", "model", "approval_policy", "tools"}
        for path in self.files:
            if path.suffix != ".toml" or path.name == "config.toml":
                continue
            with self.subTest(path=path.relative_to(REPO)):
                document = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertLessEqual(set(document), allowed)
                self.assertIn(document["sandbox_mode"],
                              {"read-only", "workspace-write",
                               "danger-full-access"})

    def test_codex_config_registers_every_role(self) -> None:
        document = tomllib.loads(
            (REPO / ".codex" / "config.toml").read_text(encoding="utf-8"))
        registry = document["agents"]
        for role, spec in self.roles_doc["roles"].items():
            binding = (spec.get("runtime_bindings") or {}).get("codex_cli")
            if not binding:
                continue
            with self.subTest(role=role):
                self.assertIn(role, registry)
                # Codex resolves config_file relative to the config.toml.
                referenced = (REPO / ".codex" / registry[role]["config_file"])
                self.assertEqual(referenced.resolve(), (REPO / binding).resolve())

    def test_bindings_do_not_copy_contract_prose(self) -> None:
        """A binding points at the contract; duplicated prose would drift."""
        for role, spec in self.roles_doc["roles"].items():
            contract_lines = [
                line.strip()
                for line in (REPO / spec["contract"]).read_text(
                    encoding="utf-8").splitlines()
                # Long lines only: short ones ("## Mission") collide by chance.
                if len(line.strip()) > 60
            ]
            for runtime, binding in (spec.get("runtime_bindings") or {}).items():
                if (REPO / binding) not in self.files:
                    continue  # hand-written binding, not this script's rule
                text = (REPO / binding).read_text(encoding="utf-8")
                for line in contract_lines:
                    with self.subTest(role=role, runtime=runtime):
                        self.assertNotIn(line, text,
                                         "contract prose copied into a binding")

    def test_bindings_name_no_model(self) -> None:
        """Model choice belongs to the policy layer, not to a binding file."""
        for path, content in self.files.items():
            with self.subTest(path=path.relative_to(REPO)):
                if path.suffix == ".toml":
                    document = tomllib.loads(content)
                    self.assertNotIn("model", document)
                else:
                    frontmatter = content.split("---")[1]
                    self.assertNotIn("\nmodel:", frontmatter)

    def test_a_binding_grants_no_capability_beyond_the_runtime_floor(self) -> None:
        """Over-grants come from the runtime, never from a generator choice."""
        for role, spec in self.roles_doc["roles"].items():
            for runtime in (spec.get("runtime_bindings") or {}):
                with self.subTest(role=role, runtime=runtime):
                    forced = set(over_granted(self.roles_doc, role, runtime))
                    effective = set(
                        effective_capabilities(self.roles_doc, role, runtime))
                    # "Contracted" means everything the role asked for, and an
                    # optional capability is asked for -- just conditionally on
                    # the runtime having it. Counting only the required ones
                    # would report `send_messages` on Claude Code as forced by
                    # the runtime, when the role requested it.
                    spec_doc = role_spec(self.roles_doc, role)
                    contracted = (set(spec_doc["capabilities"])
                                  | set(spec_doc.get("optional_capabilities") or []))
                    self.assertEqual(effective - contracted, forced)

    def test_an_over_grant_is_stated_in_the_binding_it_affects(self) -> None:
        """If the harness cannot enforce it, the role must at least be told."""
        for role, spec in self.roles_doc["roles"].items():
            for runtime, binding in (spec.get("runtime_bindings") or {}).items():
                if (REPO / binding) not in self.files:
                    continue
                forced = over_granted(self.roles_doc, role, runtime)
                if not forced:
                    continue
                text = (REPO / binding).read_text(encoding="utf-8")
                for capability in forced:
                    with self.subTest(role=role, runtime=runtime,
                                      capability=capability):
                        self.assertIn(capability, text)

    def test_coupled_write_overgrant_still_allows_new_artifact_creation(self) -> None:
        """A write-only role must not be told to avoid the shared write primitive."""
        for runtime, binding in self.roles_doc["roles"]["idea-generator"][
                "runtime_bindings"].items():
            if runtime not in {"codex_cli", "opencode"}:
                continue
            text = (REPO / binding).read_text(encoding="utf-8")
            with self.subTest(runtime=runtime):
                self.assertIn("only\nto create new files", text)
                self.assertIn("edit_files", text)
                self.assertNotIn("not: edit_files", text)

    def test_independent_review_roles_are_told_they_are_independent(self) -> None:
        for role, spec in self.roles_doc["roles"].items():
            if not spec["authority"].get("independent_of_producer"):
                continue
            for binding in (spec.get("runtime_bindings") or {}).values():
                if (REPO / binding) not in self.files:
                    continue
                with self.subTest(role=role, binding=binding):
                    self.assertIn(
                        "independent review role",
                        (REPO / binding).read_text(encoding="utf-8"))


class DriftDetectionTests(unittest.TestCase):
    """The checker must actually fail on the drift it exists to catch."""

    def setUp(self) -> None:
        self.roles_doc = load_roles()

    def test_a_widened_codex_sandbox_is_caught(self) -> None:
        import copy
        doc = copy.deepcopy(self.roles_doc)
        # Take write away from the Executor's contract; its binding on disk
        # still says workspace-write, so the check must object.
        doc["roles"]["executor"]["capabilities"] = ["read_files", "search_files",
                                                    "run_commands"]
        problems = check(doc, load_policies())
        self.assertTrue(any("executor/codex_cli" in problem
                            for problem in problems), problems)

    def test_an_opencode_permission_flipped_to_allow_is_caught(self) -> None:
        import copy
        doc = copy.deepcopy(self.roles_doc)
        # The Coordinator's binding denies bash; claiming it needs commands
        # without regenerating must fail rather than pass quietly.
        doc["roles"]["coordinator"]["capabilities"].append("run_commands")
        problems = check(doc, load_policies())
        self.assertTrue(any("coordinator/opencode" in problem
                            for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()
