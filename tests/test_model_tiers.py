"""Model tiers: a capability-class floor per policy, enforced by the resolver.

`docs/model-tiers.md` is the design. Effort says how hard a model thinks; the
tier says which class of model may do the thinking at all. These tests pin the
properties the topology rests on: every policy states a floor, every committed
model is classified, a model below the floor is refused (and the frontier gate
refuses one nobody classified), exempt backends record rather than refuse, an
overlay can classify but never promote, and the Anthropic chain is
frontier/core -> director (Sonnet) -> mechanical (Haiku).
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from orchestration import adapter, role_registry
from orchestration.adapter import config as config_module
from orchestration.adapter import resolver as resolver_module

REPO = Path(__file__).resolve().parents[1]
BINDINGS = REPO / "orchestration" / "model-bindings.yaml"


@pytest.fixture(scope="module")
def cfg():
    return adapter.load(env={"AUTORESEARCH_BINDINGS_OVERLAY": ""})


def _bindings() -> dict:
    return yaml.safe_load(BINDINGS.read_text(encoding="utf-8"))


def _load(tmp_path: Path, bindings: dict):
    path = tmp_path / "bindings.yaml"
    path.write_text(yaml.safe_dump(bindings), encoding="utf-8")
    return adapter.load(bindings_path=path, env={"AUTORESEARCH_BINDINGS_OVERLAY": ""})


def test_every_policy_states_a_known_tier_floor(cfg):
    order = cfg.model_tier_order
    assert order == ["mechanical", "director", "core", "frontier"]
    for pid, policy in cfg.policy_table.items():
        assert policy["requires"].get("model_tier") in order, pid


def test_every_committed_model_is_classified(cfg):
    for backend, table in cfg.binding_table.items():
        for pid, binding in table.items():
            if binding.get("model"):
                assert cfg.model_tier(binding["model"]), f"{backend}.{pid}: {binding['model']}"


def test_the_floor_refuses_nothing_another_requirement_would_admit(cfg):
    """Introducing tiers changed no routing: every committed binding below its
    floor on an enforcing backend was already refused for another reason."""
    for backend, table in cfg.binding_table.items():
        if cfg.tier_exempt(backend):
            continue
        for pid, binding in table.items():
            if not binding.get("model"):
                continue
            policy = cfg.policy_table[pid]
            gap, enforced = resolver_module._below_tier(cfg, policy, binding)
            if not enforced:
                continue
            others = [g for g in resolver_module._shortfalls(cfg, policy, binding, backend)
                      if not g.startswith("model_tier")]
            assert others, f"{backend}.{pid} is refused only by its tier: {gap}"


def test_the_anthropic_chain_is_frontier_core_director_mechanical(cfg):
    tiers = {pid: cfg.model_tier(cfg.binding("anthropic", pid)["model"])
             for pid in cfg.policy_table}
    assert tiers["review-breakthrough"] == tiers["research-synthesis"] == "frontier"
    assert tiers["coordinator-orchestration-code"] == tiers["review-adversarial"] == "core"
    assert tiers["director-runbook"] == "director"
    assert tiers["executor-mechanical"] == "mechanical"
    assert cfg.binding("anthropic", "director-runbook")["model"] == "claude-sonnet-5-5"
    assert cfg.binding("anthropic", "executor-mechanical")["model"] == "claude-haiku-5-5"


def test_frontier_backends_route_the_frontier_policies(cfg):
    for backend, model in (("anthropic-mythos", "claude-mythos-5"),
                           ("anthropic-fable", "claude-fable-5-1")):
        resolution = adapter.resolve(cfg, "review-breakthrough", backend=backend,
                                     independent_session=True, env={})
        assert resolution.resolved_model_id == model
        assert resolution.model_tier == "frontier" and not resolution.below_model_tier


def test_a_mechanical_model_is_refused_on_a_frontier_policy(tmp_path):
    bindings = _bindings()
    gate = bindings["bindings"]["anthropic"]["review-breakthrough"]
    gate["model"] = "claude-haiku-5-5"
    cfg = _load(tmp_path, bindings)
    with pytest.raises(resolver_module.ResolutionError, match="model_tier: policy requires frontier"):
        adapter.resolve(cfg, "review-breakthrough", independent_session=True, env={})


def test_a_below_tier_binding_resolves_only_degraded_and_says_so(tmp_path):
    bindings = _bindings()
    bindings["bindings"]["anthropic"]["coordinator-orchestration"]["model"] = "claude-sonnet-5-5"
    cfg = _load(tmp_path, bindings)
    with pytest.raises(resolver_module.ResolutionError):
        adapter.resolve(cfg, "coordinator-orchestration", env={})
    resolution = adapter.resolve(cfg, "coordinator-orchestration",
                                 degraded_allowed=True, env={})
    assert any(g.startswith("model_tier") for g in resolution.degraded_requirements)
    assert resolution.below_model_tier


def test_an_unclassified_model_is_recorded_not_refused_except_on_the_frontier_gate(tmp_path):
    bindings = _bindings()
    bindings["bindings"]["anthropic"]["research-deep"]["model"] = "vendor/new-model"
    bindings["bindings"]["anthropic"]["review-breakthrough"]["model"] = "vendor/new-model"
    cfg = _load(tmp_path, bindings)
    resolution = adapter.resolve(cfg, "research-deep", env={})
    assert resolution.model_tier is None and not resolution.below_model_tier
    assert "unclassified" in resolution.summary()
    with pytest.raises(resolver_module.ResolutionError, match="unclassified"):
        adapter.resolve(cfg, "review-breakthrough", independent_session=True, env={})


def test_an_exempt_backend_records_the_gap_instead_of_refusing(cfg):
    assert cfg.tier_exempt("local")
    resolution = adapter.resolve(cfg, "coordinator-orchestration", backend="local", env={})
    assert resolution.below_model_tier and resolution.model_tier == "mechanical"
    assert "BELOW TIER" in resolution.summary()
    assert resolution.to_dict()["policy_model_tier"] == "core"


def test_config_rejects_an_unknown_tier(tmp_path):
    bindings = _bindings()
    bindings["model_tiers"]["claude-haiku-5-5"] = "superhuman"
    with pytest.raises(config_module.ConfigError, match="unknown tier"):
        _load(tmp_path, bindings)


def test_an_overlay_may_classify_a_new_model_but_never_promote_one():
    base = _bindings()
    merged = config_module.merge_bindings(base, {"bindings": {}, "model_tiers": {"vendor/x": "core"}})
    assert merged["model_tiers"]["vendor/x"] == "core"
    with pytest.raises(config_module.ConfigError, match="may not reclassify"):
        config_module.merge_bindings(
            base, {"bindings": {}, "model_tiers": {"claude-haiku-5-5": "frontier"}})


def test_delegation_flows_downward_only(cfg):
    order = cfg.model_tier_order
    delegation = cfg.policies["model_tiers"]["delegation"]
    assert delegation["director"] == [] and delegation["mechanical"] == []
    for tier, targets in delegation.items():
        for target in targets:
            assert order.index(target) < order.index(tier), (tier, target)


def test_the_director_role_is_pinned_to_its_binding_and_cannot_execute():
    roles = role_registry.load_roles()
    spec = roles["roles"]["experiment-director"]
    assert spec["default_policy"] == "director-runbook"
    assert spec["authority"]["may_execute_experiments"] is False
    assert spec["authority"]["may_approve_experiments"] is False
    assert role_registry.expected_model(roles, _bindings(), "experiment-director",
                                        "claude_code") == "claude-sonnet-5-5"
    assert adapter.load(env={"AUTORESEARCH_BINDINGS_OVERLAY": ""}).role_default_policy(
        "experiment-director") == "director-runbook"
