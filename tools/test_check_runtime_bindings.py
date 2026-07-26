"""Tests for the role/runtime binding consistency check."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_runtime_bindings as checker  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def roles():
    return checker.load_roles()


@pytest.fixture
def policies():
    return yaml.safe_load(
        (REPO / "orchestration" / "model-policies.yaml").read_text(encoding="utf-8"))


def test_repository_bindings_are_consistent(roles, policies):
    assert checker.check(roles, policies) == []


def test_extra_tool_in_a_runtime_binding_is_caught(roles, policies, tmp_path):
    """A subagent that quietly gains a capability must fail the build."""
    doc = copy.deepcopy(roles)
    doc["roles"]["coordinator"]["capabilities"].remove("edit_files")
    problems = checker.check(doc, policies)
    assert any("coordinator/claude_code" in p and "do not match" in p
               for p in problems)


def test_review_role_routed_to_a_non_independent_policy_is_caught(roles, policies):
    doc = copy.deepcopy(roles)
    doc["roles"]["validator"]["default_policy"] = "research-deep"
    problems = checker.check(doc, policies)
    assert any("independent session" in p for p in problems)


def test_non_coordinator_routed_to_a_state_changing_policy_is_caught(roles, policies):
    doc = copy.deepcopy(roles)
    doc["roles"]["executor"]["default_policy"] = "coordinator-orchestration"
    problems = checker.check(doc, policies)
    assert any("permitted to" in p for p in problems)


def test_runtime_without_a_needed_capability_cannot_host_the_role(roles):
    doc = copy.deepcopy(roles)
    del doc["capabilities"]["run_commands"]["claude_code"]
    assert checker.expected_tools(doc, "executor", "claude_code") is None
    problems = checker.check(doc)
    assert any("cannot express every capability" in p for p in problems)


def test_missing_contract_file_is_caught(roles):
    doc = copy.deepcopy(roles)
    doc["roles"]["coordinator"]["contract"] = "agents/does-not-exist.md"
    assert any("missing role contract" in p for p in checker.check(doc))
