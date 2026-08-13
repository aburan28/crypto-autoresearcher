"""Per-subagent reasoning effort is derived from policy, and drift is a failure.

`model-policies.yaml` calibrates how hard each role should think. Until a
runtime could express that per agent, one session ran every subagent at
whatever depth it was launched with -- an Executor replaying a frozen protocol
thought as hard as a Validator, and a Validator dispatched from an Executor
session thought as little as one. Claude Code's agent frontmatter can express it
(`effort:`), so the binding now carries it and `check()` fails the build when it
disagrees with the policy.

These tests cover the two ways that guarantee dies quietly: a binding that stops
matching its policy, and a checker that stops looking.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from orchestration import role_registry

REPO = Path(__file__).resolve().parents[1]

CLAUDE = "claude_code"


@pytest.fixture(scope="module")
def roles_doc():
    return role_registry.load_roles()


@pytest.fixture(scope="module")
def policies_doc():
    return role_registry.load_policies()


def _effort_order(policies_doc):
    return policies_doc["adapter"]["reasoning_effort_order"]


# --------------------------------------------------------------------------
# The live repository
# --------------------------------------------------------------------------

def test_repository_bindings_agree_with_their_policies(roles_doc, policies_doc):
    assert role_registry.check(roles_doc, policies_doc) == []


def test_every_claude_subagent_declares_its_policy_effort(roles_doc, policies_doc):
    """The property the frontmatter exists for, asserted without the checker."""
    for role, spec in roles_doc["roles"].items():
        path = REPO / spec["runtime_bindings"][CLAUDE]
        declared = role_registry.read_declared_effort(CLAUDE, path)
        wanted = role_registry.expected_effort(
            roles_doc, policies_doc, role, CLAUDE)
        assert declared == wanted, f"{role}: {declared!r} != policy {wanted!r}"


def test_subagent_efforts_are_calibrated_rather_than_uniform(roles_doc, policies_doc):
    """Effort differs per role, and in the direction the contract argues for.

    Not "all five differ": the Validator and the Red Team are one adversarial
    gate attacked from two angles, and `review-adversarial` deliberately serves
    both. What must hold is that review outranks execution -- the ordering that
    keeps a bad certificate from being waved through by a cheap review, and the
    one a well-meaning "make everything faster" edit would invert.
    """
    order = _effort_order(policies_doc)
    effort = {
        role: role_registry.expected_effort(roles_doc, policies_doc, role, CLAUDE)
        for role in roles_doc["roles"]
    }
    assert len(set(effort.values())) >= 3, f"efforts collapsed to {effort}"

    rank = {level: index for index, level in enumerate(order)}
    for reviewer in ("validator", "red-team"):
        assert rank[effort[reviewer]] > rank[effort["executor"]]
        assert rank[effort[reviewer]] > rank[effort["coordinator"]]
    assert rank[effort["coordinator"]] > rank[effort["executor"]]


def test_declared_efforts_are_levels_the_runtime_accepts(roles_doc, policies_doc):
    levels = role_registry.effort_support(roles_doc, CLAUDE)["levels"]
    for role in roles_doc["roles"]:
        assert role_registry.expected_effort(
            roles_doc, policies_doc, role, CLAUDE) in levels


def test_runtimes_that_cannot_express_effort_are_recorded_not_omitted(roles_doc):
    """`null` is an answer; a missing key would be an assumption."""
    table = roles_doc["runtime_reasoning_effort"]
    for runtime in ("codex_cli", "opencode"):
        assert runtime in table
        assert table[runtime] is None
        assert role_registry.effort_support(roles_doc, runtime) is None
        assert role_registry.expected_effort(
            roles_doc, role_registry.load_policies(), "coordinator", runtime) is None


# --------------------------------------------------------------------------
# The checker, on documents built to break it
# --------------------------------------------------------------------------

def _check_one(roles_doc, policies_doc, role, tmp_path, effort, monkeypatch):
    """Run `check` over one role whose real Claude binding was copied and edited.

    The binding is the repository's own file with only its `effort:` line
    changed, so these cases exercise the shipped frontmatter rather than a
    hand-written stand-in that could stay green while the real file rots.
    """
    doc = copy.deepcopy(roles_doc)
    doc["roles"] = {role: copy.deepcopy(roles_doc["roles"][role])}

    source = REPO / roles_doc["roles"][role]["runtime_bindings"][CLAUDE]
    original = role_registry.read_declared_effort(CLAUDE, source)
    replacement = "\n" if effort is None else f"\neffort: {effort}\n"
    text = source.read_text(encoding="utf-8").replace(
        f"\neffort: {original}\n", replacement, 1)

    binding = tmp_path / f"{role}.md"
    binding.write_text(text, encoding="utf-8")
    (tmp_path / "contract.md").write_text("stub\n", encoding="utf-8")
    doc["roles"][role]["runtime_bindings"] = {CLAUDE: binding.name}
    doc["roles"][role]["contract"] = "contract.md"

    # `check` resolves binding paths against REPO; point it at the temp tree.
    monkeypatch.setattr(role_registry, "REPO", tmp_path)
    return role_registry.check(doc, policies_doc)


def test_missing_effort_is_reported(roles_doc, policies_doc, tmp_path, monkeypatch):
    problems = _check_one(roles_doc, policies_doc, "validator", tmp_path,
                          None, monkeypatch)
    assert any("declares no `effort`" in problem for problem in problems), problems


def test_wrong_effort_is_reported(roles_doc, policies_doc, tmp_path, monkeypatch):
    problems = _check_one(roles_doc, policies_doc, "validator", tmp_path,
                          "low", monkeypatch)
    assert any("declares effort: 'low'" in problem for problem in problems), problems


def test_matching_effort_passes(roles_doc, policies_doc, tmp_path, monkeypatch):
    wanted = role_registry.expected_effort(
        roles_doc, policies_doc, "validator", CLAUDE)
    assert _check_one(roles_doc, policies_doc, "validator", tmp_path,
                      wanted, monkeypatch) == []


def test_inexpressible_policy_effort_is_reported(roles_doc, policies_doc,
                                                 tmp_path, monkeypatch):
    """A policy asking for depth the runtime has no word for must not pass.

    `none` is in the program's lattice and not in Claude Code's, so it is the
    real instance of this, not a hypothetical one.
    """
    policies = copy.deepcopy(policies_doc)
    policies["policies"]["review-adversarial"]["reasoning_effort"] = "none"
    problems = _check_one(roles_doc, policies, "validator", tmp_path,
                          "xhigh", monkeypatch)
    assert any("cannot express" in problem for problem in problems), problems


def test_requested_effort_defaults_to_the_floor(policies_doc):
    """`reasoning_effort` omitted means "the floor", exactly as the adapter reads it."""
    policies = copy.deepcopy(policies_doc)
    policy = policies["policies"]["executor-implementation"]
    floor = policy["requires"]["reasoning_effort"]
    policy.pop("reasoning_effort")
    assert role_registry.policy_reasoning_effort(
        policies, "executor-implementation") == floor


def test_policy_with_no_effort_at_all_raises(policies_doc):
    policies = copy.deepcopy(policies_doc)
    policy = policies["policies"]["executor-implementation"]
    policy.pop("reasoning_effort")
    policy["requires"].pop("reasoning_effort")
    with pytest.raises(ValueError, match="reasoning_effort"):
        role_registry.policy_reasoning_effort(policies, "executor-implementation")


def test_declared_effort_runtime_without_a_reader_raises(tmp_path):
    """Silence must not read as agreement for a runtime nobody wired up."""
    with pytest.raises(ValueError, match="no effort reader"):
        role_registry.read_declared_effort("some_new_runtime", tmp_path / "x.md")
