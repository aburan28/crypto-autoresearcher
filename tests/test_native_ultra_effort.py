"""Literal ultra requests retain their tier without inventing backend support.

Supporting bindings below are test-only configurations, not model probes or
changes to any repository binding. Native resolution must still refuse caps.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest

from orchestration import adapter
from orchestration.adapter import codex_runtime
from orchestration.adapter import config as config_module
from orchestration.adapter import resolver as resolver_module


@pytest.fixture
def cfg():
    return adapter.load()


def _with_ceiling(cfg, ceiling, policy="research-deep"):
    bindings = deepcopy(cfg.bindings)
    binding = deepcopy(bindings["bindings"]["openai"][policy])
    bindings["bindings"]["openai"][policy] = binding
    binding["model"] = "test-native-effort-model"
    binding["provenance"] = "operator-supplied"
    binding["last_probed"] = None
    binding["capabilities"]["max_reasoning_effort"] = ceiling
    result = replace(cfg, bindings=bindings)
    config_module.validate(result)
    return result


def test_ultra_is_above_max_in_shared_and_default_vocabulary(cfg):
    assert cfg.effort_order == config_module.DEFAULT_EFFORT_ORDER
    assert cfg.effort_order.index("ultra") > cfg.effort_order.index("max")
    policies = deepcopy(cfg.policies)
    policies["adapter"].pop("reasoning_effort_order")
    default_cfg = replace(cfg, policies=policies)
    config_module.validate(default_cfg)
    assert default_cfg.effort_order == cfg.effort_order


def test_supporting_binding_preserves_ultra_handoff_and_manifest(cfg):
    supported = _with_ceiling(cfg, "ultra")
    handoff = {"handoff": {"to": "idea-generator", "inference": {
        "policy": "research-deep", "reasoning_effort": "ultra",
        "fallback_allowed": False, "degraded_allowed": False,
    }}}
    resolution = adapter.resolve_handoff(
        supported, handoff, backend="openai", env={})
    assert resolution.requested_reasoning_effort == "ultra"
    assert resolution.reasoning_effort == "ultra"
    assert resolution.reasoning_effort_overridden
    assert not resolution.reasoning_effort_capped
    assert not resolution.fallback_used
    assert resolution.degraded_requirements == []
    manifest = adapter.inference_block(resolution)
    assert manifest["requested_reasoning_effort"] == "ultra"
    assert manifest["reasoning_effort"] == "ultra"
    assert manifest["model_verified"] is False


def test_native_resolution_accepts_ultra_only_with_supporting_ceiling(cfg):
    resolution = codex_runtime._strict_resolution(
        cfg=_with_ceiling(cfg, "ultra"), policy="research-deep",
        role="idea-generator", backend="openai", effort="ultra",
        independent_session=True)
    receipt = codex_runtime._public_resolution(resolution)
    assert receipt["requested_reasoning_effort"] == "ultra"
    assert receipt["reasoning_effort"] == "ultra"
    assert receipt["reasoning_effort_capped"] is False
    assert receipt["global_backend_verified"] is False


def test_max_only_binding_records_cap_and_native_resolution_refuses_it(cfg):
    capped_cfg = _with_ceiling(cfg, "max")
    resolution = adapter.resolve(
        capped_cfg, "research-deep", backend="openai",
        reasoning_effort="ultra", env={})
    assert resolution.requested_reasoning_effort == "ultra"
    assert resolution.reasoning_effort == "max"
    assert resolution.reasoning_effort_capped
    assert "CAPPED from ultra" in resolution.summary()
    receipt = codex_runtime._public_resolution(resolution)
    assert receipt["requested_reasoning_effort"] == "ultra"
    assert receipt["reasoning_effort"] == "max"
    assert receipt["reasoning_effort_capped"] is True
    with pytest.raises(codex_runtime._ProbeFailure) as failure:
        codex_runtime._strict_resolution(
            cfg=capped_cfg, policy="research-deep", role="idea-generator",
            backend="openai", effort="ultra", independent_session=True)
    assert failure.value.codes == ("policy_resolution_failed",)


def test_unknown_effort_remains_rejected(cfg):
    with pytest.raises(resolver_module.ResolutionError,
                       match="unknown reasoning effort"):
        adapter.resolve(cfg, "research-deep", backend="openai",
                        reasoning_effort="ultra-typo", env={})


@pytest.mark.parametrize("policy", ["review-adversarial", "review-breakthrough"])
def test_ultra_review_still_requires_independence_and_distinct_reviewer(cfg, policy):
    supported = _with_ceiling(cfg, "ultra", policy)
    with pytest.raises(resolver_module.GovernanceError, match="independent session"):
        adapter.resolve(supported, policy, backend="openai",
                        reasoning_effort="ultra", env={})
    with pytest.raises(resolver_module.GovernanceError, match="own claim"):
        adapter.resolve(
            supported, policy, backend="openai", reasoning_effort="ultra",
            independent_session=True, originating_agent="producer",
            assigned_agent="producer", env={})


def test_breakthrough_floor_and_no_degradation_survive_ultra_request(cfg):
    policy = cfg.policy("review-breakthrough")
    assert policy["requires"]["reasoning_effort"] == "max"
    assert policy["reasoning_effort"] == "max"
    assert policy["degradable"] is False
    insufficient = _with_ceiling(cfg, "xhigh", "review-breakthrough")
    with pytest.raises(resolver_module.ResolutionError):
        adapter.resolve(
            insufficient, "review-breakthrough", backend="openai",
            reasoning_effort="ultra", independent_session=True, env={})
    with pytest.raises(resolver_module.GovernanceError, match="not degradable"):
        adapter.resolve(
            insufficient, "review-breakthrough", backend="openai",
            reasoning_effort="ultra", independent_session=True,
            degraded_allowed=True, env={})


def test_ultra_does_not_bypass_bedrock_target_prohibition(cfg):
    with pytest.raises(config_module.ConfigError, match="forbidden by cost policy"):
        adapter.resolve(
            _with_ceiling(cfg, "ultra"), "research-deep", backend="openai",
            reasoning_effort="ultra",
            env={"OPENAI_BASE_URL": "https://bedrock-runtime.example.invalid"})
