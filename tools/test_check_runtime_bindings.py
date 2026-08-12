"""Tests for the role/runtime binding consistency check."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO))

import check_runtime_bindings as checker  # noqa: E402
# `over_granted` is not part of the checker's re-exported surface;
# generate_runtime_agents.py reaches for the registry directly the same way.
from orchestration import role_registry  # noqa: E402


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


def test_optional_capability_is_granted_where_the_runtime_supports_it(roles):
    tools = checker.expected_tools(roles, "coordinator", "claude_code")
    assert "SendMessage" in tools


def test_optional_capability_is_absent_where_it_is_not_supported(roles):
    """Silently absent, NOT a refusal. This is the whole point of the tier."""
    for runtime in ("codex_cli", "opencode"):
        tools = checker.expected_tools(roles, "coordinator", runtime)
        assert tools is not None, f"{runtime} was refused over an optional capability"
        assert "SendMessage" not in tools


def test_optional_capability_never_makes_a_runtime_unhostable(roles):
    """The regression this tier exists to prevent.

    `send_messages` is mapped for claude_code alone. Declared as a REQUIRED
    capability it would make every role unhostable on codex_cli and opencode --
    five roles times two runtimes -- because expected_tools returns None for any
    capability the runtime cannot map. Declared optional, every role still runs
    everywhere it ran before.
    """
    assert checker.check(roles) == []
    for role in roles["roles"]:
        for runtime in ("codex_cli", "opencode"):
            assert checker.expected_tools(roles, role, runtime) is not None


def test_making_messaging_required_would_break_the_other_runtimes(roles, policies):
    """Pins WHY it is optional, so nobody 'tidies' it into the required list."""
    doc = copy.deepcopy(roles)
    for spec in doc["roles"].values():
        spec.get("optional_capabilities", []).clear()
        spec["capabilities"].append("send_messages")
    problems = checker.check(doc, policies)
    broken = [p for p in problems if "cannot express every capability" in p]
    # Derived, not hardcoded: the policy-tier roles bind claude_code only, and
    # claude_code is the one runtime that HAS SendMessage, so they would survive.
    # Every role/runtime pair bound to a runtime without it would not.
    at_risk = [(role, runtime)
               for role, spec in doc["roles"].items()
               for runtime in (spec.get("runtime_bindings") or {})
               if runtime not in doc["capabilities"]["send_messages"]]
    assert at_risk, "fixture no longer has a runtime that lacks SendMessage"
    assert len(broken) == len(at_risk), (
        f"expected {len(at_risk)} role/runtime pairs to become unhostable "
        f"({at_risk}); got {problems}")


def test_optional_capability_is_not_reported_as_an_over_grant(roles):
    """It was asked for, just conditionally -- an over-grant is the opposite."""
    assert "send_messages" not in role_registry.over_granted(
        roles, "coordinator", "claude_code")


def test_missing_contract_file_is_caught(roles):
    doc = copy.deepcopy(roles)
    doc["roles"]["coordinator"]["contract"] = "agents/does-not-exist.md"
    assert any("missing role contract" in p for p in checker.check(doc))
