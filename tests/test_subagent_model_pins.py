"""Claude Code subagent model pins are derived from the bindings, never chosen.

Every subagent runs on the session's model unless its file names one. The
executor roles name the model their own policy is bound to, so a frozen
protocol re-run does not bill at the session's tier; every other role must
inherit, so the operator's choice of model for coordination and review holds.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from orchestration import role_registry

REPO = Path(__file__).resolve().parents[1]


def _docs():
    roles = role_registry.load_roles()
    bindings = yaml.safe_load((REPO / "orchestration/model-bindings.yaml").read_text())
    return roles, bindings


def test_repository_subagents_match_their_pins():
    roles = role_registry.load_roles()
    problems = (role_registry.check_model_pin_table(roles)
                + role_registry.check(roles, role_registry.load_policies()))
    assert not [p for p in problems if "model" in p], problems


def test_executor_pins_follow_the_anthropic_bindings():
    roles, bindings = _docs()
    for role in ("executor", "executor-mechanical"):
        policy = roles["roles"][role]["default_policy"]
        assert role_registry.expected_model(roles, bindings, role, "claude_code") == \
            bindings["bindings"]["anthropic"][policy]["model"]
    # review and coordination stay on the session's model
    for role in ("coordinator", "validator", "red-team", "validator-breakthrough"):
        assert role_registry.expected_model(roles, bindings, role, "claude_code") == "inherit"


def test_a_binding_change_is_a_build_failure_until_the_agent_file_follows(tmp_path):
    roles, bindings = _docs()
    moved = deepcopy(bindings)
    moved["bindings"]["anthropic"]["executor-implementation"]["model"] = "claude-sonnet-9"
    agent = REPO / ".claude/agents/executor.md"
    problems = role_registry._check_model(roles, moved, "executor", "claude_code", agent)
    assert problems and "claude-sonnet-9" in problems[0]


def test_an_unpinned_role_may_not_name_a_model(tmp_path):
    roles, bindings = _docs()
    text = (REPO / ".claude/agents/validator.md").read_text().replace(
        "model: inherit", "model: claude-haiku-4-5-20251001", 1)
    fake = tmp_path / "validator.md"
    fake.write_text(text)
    problems = role_registry._check_model(roles, bindings, "validator", "claude_code", fake)
    assert problems and "inherit" in problems[0]


def test_the_pin_table_rejects_unknown_roles():
    roles, _ = _docs()
    bad = deepcopy(roles)
    bad["runtime_model_pins"]["claude_code"]["roles"].append("ghost")
    assert any("unknown role 'ghost'" in p for p in role_registry.check_model_pin_table(bad))
