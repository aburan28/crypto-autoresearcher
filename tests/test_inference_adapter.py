"""Tests for the runtime-neutral inference adapter.

These guard the properties the research contract depends on: a committed
handoff always resolves, a downgrade is never silent, an unverified model id is
never presented as verified, and the wire translation is faithful for every
supported protocol. No test touches the network.
"""
from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path

import pytest
import yaml

from orchestration import adapter
from orchestration.adapter import config as config_module
from orchestration.adapter import manifest as manifest_module
from orchestration.adapter import resolver as resolver_module
from orchestration.adapter import transport as transport_module

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cfg():
    return adapter.load()


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------
def test_repository_configuration_is_valid(cfg):
    assert cfg.digest.startswith("sha256:")
    assert cfg.policy_table and cfg.backend_table and cfg.binding_table


def test_every_backend_binding_covers_every_policy(cfg):
    """A half-filled backend silently routes tasks elsewhere; make it visible."""
    for backend, table in cfg.binding_table.items():
        missing = set(cfg.policy_table) - set(table)
        assert not missing, f"backend {backend} has no binding for {sorted(missing)}"


def test_config_rejects_alias_collisions(tmp_path):
    policies = yaml.safe_load((REPO / "orchestration/model-policies.yaml").read_text())
    ids = list(policies["policies"])
    policies["policies"][ids[1]]["aliases"] = list(
        policies["policies"][ids[0]].get("aliases") or [])
    path = tmp_path / "policies.yaml"
    path.write_text(yaml.safe_dump(policies))
    with pytest.raises(config_module.ConfigError, match="claimed by both"):
        adapter.load(policies_path=path)


def test_config_rejects_binding_for_unknown_backend(tmp_path):
    bindings = yaml.safe_load((REPO / "orchestration/model-bindings.yaml").read_text())
    bindings["bindings"]["no-such-vendor"] = {}
    path = tmp_path / "bindings.yaml"
    path.write_text(yaml.safe_dump(bindings))
    with pytest.raises(config_module.ConfigError, match="unknown backend"):
        adapter.load(bindings_path=path)


# --------------------------------------------------------------------------
# the alias contract: committed handoffs must keep resolving forever
# --------------------------------------------------------------------------
def test_legacy_policy_aliases_still_resolve(cfg):
    legacy = ["coordinator-ultra-code", "coordinator-sol-max", "research-sol-max",
              "review-xhigh", "executor-terra"]
    for alias in legacy:
        assert cfg.canonical_policy(alias) in cfg.policy_table


def test_every_committed_handoff_names_a_resolvable_policy(cfg):
    checked = 0
    for path in sorted((REPO / "ledger" / "handoffs").glob("TASK-*.yaml")):
        try:
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(record, dict):
            continue
        body = record.get("handoff") or {}
        policy = (body.get("inference") or {}).get("policy")
        if not policy:
            continue
        cfg.canonical_policy(policy)   # raises if an alias were ever dropped
        checked += 1
    assert checked > 0, "no committed handoffs carried an inference policy"


def test_unknown_policy_is_an_error(cfg):
    with pytest.raises(config_module.ConfigError, match="unknown inference policy"):
        cfg.canonical_policy("research-sol-maxx")


# --------------------------------------------------------------------------
# strict resolution
# --------------------------------------------------------------------------
def test_resolves_to_a_concrete_model_on_the_default_backend(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="anthropic", env={})
    assert resolution.resolved_model_id
    assert resolution.fallback_used is False
    assert resolution.degraded_requirements == []
    assert resolution.reasoning_effort == "high"


def test_unmet_requirement_is_refused_without_permission(cfg):
    with pytest.raises(resolver_module.ResolutionError) as excinfo:
        adapter.resolve(cfg, "review-adversarial", backend="zai",
                        independent_session=True, env={})
    assert "reasoning_effort" in str(excinfo.value)


def test_degraded_resolution_is_permitted_only_explicitly_and_is_recorded(cfg):
    resolution = adapter.resolve(cfg, "review-adversarial", backend="zai",
                                 independent_session=True, degraded_allowed=True,
                                 env={})
    assert resolution.fallback_used is True
    assert resolution.degraded_requirements, "a downgrade must be recorded"
    assert resolution.requested_reasoning_effort == "xhigh"
    assert resolution.reasoning_effort == "high"     # never overstated


def test_unbound_model_cannot_be_waved_through(cfg):
    """`model: null` is a hard stop: there is nothing to call."""
    with pytest.raises(resolver_module.ResolutionError, match="unbound"):
        adapter.resolve(cfg, "research-deep", backend="openai",
                        degraded_allowed=True, env={})


def test_cross_backend_fallback_records_what_it_replaced(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="openai",
                                 fallback_allowed=True, env={})
    assert resolution.fallback_used is True
    assert resolution.backend != "openai"
    assert "openai" in resolution.fallback_reason
    assert resolution.degraded_requirements == []    # fallback never downgrades


def test_backend_env_var_selects_the_backend(cfg):
    resolution = adapter.resolve(cfg, "research-deep",
                                 env={"AUTORESEARCH_BACKEND": "zai"})
    assert resolution.backend == "zai"


def test_base_url_override_is_honoured(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="zai",
                                 env={"ZAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4"})
    assert resolution.base_url == "https://open.bigmodel.cn/api/paas/v4"


def test_operator_supplied_model_is_not_reported_as_verified(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="zai", env={})
    assert resolution.model_provenance == "operator-supplied"
    assert resolution.verified_model is False
    assert "unverified" in resolution.summary()


# --------------------------------------------------------------------------
# governance gates
# --------------------------------------------------------------------------
def test_review_policy_requires_an_asserted_independent_session(cfg):
    with pytest.raises(resolver_module.GovernanceError, match="independent session"):
        adapter.resolve(cfg, "review-adversarial", backend="anthropic", env={})


def test_reviewer_may_not_be_the_originating_agent(cfg):
    with pytest.raises(resolver_module.GovernanceError, match="own claim"):
        adapter.resolve(cfg, "review-adversarial", backend="anthropic",
                        independent_session=True,
                        originating_agent="executor", assigned_agent="executor",
                        env={})


def test_resolve_handoff_reads_permissions_from_the_ledger_record(cfg):
    handoff = {"handoff": {
        "id": "TASK-20260726-001", "from": "coordinator", "to": "idea-generator",
        "inference": {"policy": "research-sol-max", "fallback_allowed": True,
                      "independent_session_required": False}}}
    resolution = adapter.resolve_handoff(cfg, handoff, backend="anthropic", env={})
    assert resolution.policy == "research-deep"
    assert resolution.requested_policy == "research-sol-max"


def test_resolve_handoff_without_a_policy_is_an_error(cfg):
    with pytest.raises(config_module.ConfigError, match="no inference.policy"):
        adapter.resolve_handoff(cfg, {"handoff": {"id": "TASK-X", "inference": {}}})


# --------------------------------------------------------------------------
# wire translation
# --------------------------------------------------------------------------
def test_anthropic_request_shape(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="anthropic", env={})
    url, headers, body = adapter.build_request(
        cfg, resolution, system="ROLE", messages=[adapter.Message("user", "hi")],
        env={"ANTHROPIC_API_KEY": "k"})
    assert url.endswith("/v1/messages")
    assert headers["x-api-key"] == "k"
    assert headers["anthropic-version"]
    assert body["system"] == "ROLE"                  # top level, not a message
    assert body["messages"] == [{"role": "user", "content": "hi"}]
    assert body["thinking"]["budget_tokens"] < body["max_tokens"]
    assert "temperature" not in body                 # pinned while thinking is on


def test_openai_request_shape(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="zai", env={})
    url, headers, body = adapter.build_request(
        cfg, resolution, system="ROLE", messages=[adapter.Message("user", "hi")],
        env={"ZAI_API_KEY": "k"})
    assert url.endswith("/chat/completions")
    assert headers["Authorization"] == "Bearer k"
    assert body["messages"][0] == {"role": "system", "content": "ROLE"}
    assert body["reasoning_effort"] == "high"
    assert body["model"] == resolution.resolved_model_id


def test_request_refuses_to_build_without_credentials(cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="zai", env={})
    with pytest.raises(transport_module.TransportError, match="ZAI_API_KEY"):
        adapter.build_request(cfg, resolution, system=None,
                              messages=[adapter.Message("user", "hi")], env={})


def test_tool_declarations_translate_per_protocol():
    tool = adapter.Tool("read_file", "read a file",
                        {"type": "object", "properties": {"path": {"type": "string"}}})
    anthropic = adapter.translate_tools([tool], "anthropic_messages")[0]
    openai = adapter.translate_tools([tool], "openai_chat")[0]
    assert anthropic["input_schema"] == tool.input_schema
    assert openai["type"] == "function"
    assert openai["function"]["parameters"] == tool.input_schema


def test_response_parsing_is_uniform_across_protocols():
    anthropic = adapter.parse_response("anthropic_messages", {
        "model": "m", "stop_reason": "end_turn",
        "content": [{"type": "text", "text": "answer"},
                    {"type": "tool_use", "id": "t1", "name": "read_file",
                     "input": {"path": "a.md"}}],
        "usage": {"input_tokens": 10, "output_tokens": 3}})
    openai = adapter.parse_response("openai_chat", {
        "model": "m", "choices": [{"finish_reason": "stop", "message": {
            "content": "answer",
            "tool_calls": [{"id": "t1", "function": {
                "name": "read_file", "arguments": '{"path": "a.md"}'}}]}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 3}})
    for parsed in (anthropic, openai):
        assert parsed.text == "answer"
        assert parsed.usage == {"input_tokens": 10, "output_tokens": 3}
        assert parsed.tool_calls[0].name == "read_file"
        assert parsed.tool_calls[0].arguments == {"path": "a.md"}


# --------------------------------------------------------------------------
# transport retries
# --------------------------------------------------------------------------
class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def test_transient_failures_retry_then_succeed():
    attempts = []

    def opener(request, timeout=None):
        attempts.append(request)
        if len(attempts) < 3:
            raise urllib.error.HTTPError(request.full_url, 503, "busy", {},
                                         io.BytesIO(b"overloaded"))
        return _Response(json.dumps({"ok": True}).encode())

    payload = transport_module.post_json(
        "https://example.invalid/v1/messages", {}, {"model": "m"},
        timeout=1, max_retries=3, opener=opener, sleep=lambda _: None)
    assert payload == {"ok": True} and len(attempts) == 3


def test_client_errors_are_not_retried():
    attempts = []

    def opener(request, timeout=None):
        attempts.append(request)
        raise urllib.error.HTTPError(request.full_url, 401, "unauthorized", {},
                                     io.BytesIO(b"bad key"))

    with pytest.raises(transport_module.TransportError, match="401"):
        transport_module.post_json("https://example.invalid/v1/messages", {},
                                   {"model": "m"}, timeout=1, max_retries=3,
                                   opener=opener, sleep=lambda _: None)
    assert len(attempts) == 1


# --------------------------------------------------------------------------
# manifest blocks and receipts
# --------------------------------------------------------------------------
def test_manifest_block_carries_the_contractual_fields(cfg):
    resolution = adapter.resolve(cfg, "executor-terra", backend="zai", env={})
    block = adapter.inference_block(resolution)
    for field in ("requested_policy", "resolved_model_id", "reasoning_effort",
                  "fallback_used", "adapter_version", "backend",
                  "model_provenance", "model_verified", "config_digest"):
        assert field in block
    assert block["requested_policy"] == "executor-terra"   # as the handoff wrote it
    assert block["canonical_policy"] == "executor-implementation"


def test_run_without_a_policy_is_recorded_as_deterministic():
    block = manifest_module.block_from_env(env={})
    assert block["resolved_model_id"] is None
    assert block["fallback_used"] is False
    assert "no model in the loop" in block["note"]


def test_independence_is_never_asserted_on_the_runs_behalf():
    """A review policy must fail to resolve unless the launcher states it."""
    block = manifest_module.block_from_env(
        env={"AUTORESEARCH_POLICY": "review-xhigh", "AUTORESEARCH_BACKEND": "anthropic"})
    assert "resolution_error" in block and "independent session" in block["resolution_error"]

    asserted = manifest_module.block_from_env(
        env={"AUTORESEARCH_POLICY": "review-xhigh", "AUTORESEARCH_BACKEND": "anthropic",
             "AUTORESEARCH_INDEPENDENT_SESSION": "true"})
    assert asserted["independent_session"] is True
    assert "resolution_error" not in asserted


def test_unresolvable_policy_is_recorded_not_swallowed():
    block = manifest_module.block_from_env(
        env={"AUTORESEARCH_POLICY": "no-such-policy"})
    assert "resolution_error" in block
    assert block["model_verified"] is False


def test_receipts_are_immutable(tmp_path, cfg):
    resolution = adapter.resolve(cfg, "research-deep", backend="anthropic", env={})
    target = tmp_path / "receipt.json"
    adapter.write_receipt(target, adapter.receipt(resolution, task_id="TASK-1"))
    assert json.loads(target.read_text())["inference_receipt"]["task_id"] == "TASK-1"
    with pytest.raises(FileExistsError):
        adapter.write_receipt(target, adapter.receipt(resolution))


def test_harness_runs_record_an_inference_block():
    from harness.runner import _inference_block
    block = _inference_block()
    assert "requested_policy" in block and "fallback_used" in block


# --------------------------------------------------------------------------
# reasoning-effort calibration
# --------------------------------------------------------------------------
def test_effort_is_calibrated_per_role_not_uniformly_high(cfg):
    """The Executor runs a frozen protocol; it should not think like a reviewer."""
    effort = {}
    for policy in ("coordinator-orchestration-code", "research-deep",
                   "review-adversarial", "executor-implementation",
                   "executor-mechanical"):
        resolution = adapter.resolve(cfg, policy, backend="anthropic",
                                     independent_session=True, env={})
        effort[policy] = resolution.reasoning_effort
    order = cfg.effort_order
    assert order.index(effort["executor-mechanical"]) < order.index(
        effort["executor-implementation"])
    assert order.index(effort["executor-implementation"]) < order.index(
        effort["coordinator-orchestration-code"])
    assert order.index(effort["coordinator-orchestration-code"]) < order.index(
        effort["review-adversarial"])


def test_the_capability_floor_and_the_request_are_separate(cfg):
    """Asking for less than the model can do is calibration, not a downgrade."""
    resolution = adapter.resolve(cfg, "executor-implementation",
                                 backend="anthropic", env={})
    binding = cfg.binding("anthropic", "executor-implementation")
    ceiling = binding["capabilities"]["max_reasoning_effort"]
    order = cfg.effort_order
    assert order.index(resolution.reasoning_effort) < order.index(ceiling)
    assert resolution.degraded_requirements == []      # not a downgrade
    assert resolution.fallback_used is False


def test_a_handoff_may_calibrate_effort_for_one_task(cfg):
    handoff = {"handoff": {
        "id": "TASK-1", "from": "coordinator", "to": "executor",
        "inference": {"policy": "executor-implementation",
                      "reasoning_effort": "low"}}}
    resolution = adapter.resolve_handoff(cfg, handoff, backend="anthropic", env={})
    assert resolution.reasoning_effort == "low"
    assert resolution.reasoning_effort_overridden is True
    assert resolution.policy_reasoning_effort == "medium"
    assert "overriding medium" in resolution.summary()


def test_an_unknown_effort_override_is_refused(cfg):
    with pytest.raises(resolver_module.ResolutionError, match="unknown reasoning effort"):
        adapter.resolve(cfg, "executor-implementation", backend="anthropic",
                        reasoning_effort="ludicrous", env={})


def test_effort_is_capped_by_the_backend_and_says_so(cfg):
    """Asking for more than the binding supports is recorded, never silent."""
    resolution = adapter.resolve(cfg, "executor-implementation", backend="zai",
                                 reasoning_effort="xhigh", env={})
    assert resolution.requested_reasoning_effort == "xhigh"
    assert resolution.reasoning_effort == "high"        # the zai ceiling
    assert resolution.reasoning_effort_capped is True
    assert "CAPPED" in resolution.summary()


def test_calibration_reaches_the_anthropic_wire(cfg):
    """A lower tier must change the request, not only the manifest."""
    def thinking(policy: str) -> int:
        resolution = adapter.resolve(cfg, policy, backend="anthropic",
                                     independent_session=True, env={})
        _, _, body = adapter.build_request(
            cfg, resolution, system=None,
            messages=[adapter.Message("user", "x")],
            env={"ANTHROPIC_API_KEY": "k"})
        return body.get("thinking", {}).get("budget_tokens", 0)

    assert thinking("executor-mechanical") == 0          # thinking off entirely
    assert 0 < thinking("executor-implementation") < thinking("review-adversarial")


def test_thinking_off_lets_temperature_through(cfg):
    """Extended thinking pins temperature; the mechanical tier wants it at 0."""
    resolution = adapter.resolve(cfg, "executor-mechanical", backend="anthropic",
                                 env={})
    _, _, body = adapter.build_request(
        cfg, resolution, system=None, messages=[adapter.Message("user", "x")],
        env={"ANTHROPIC_API_KEY": "k"})
    assert "thinking" not in body
    assert body["temperature"] == 0.0


def test_calibration_reaches_the_openai_wire(cfg):
    resolution = adapter.resolve(cfg, "executor-mechanical", backend="zai", env={})
    _, _, body = adapter.build_request(
        cfg, resolution, system=None, messages=[adapter.Message("user", "x")],
        env={"ZAI_API_KEY": "k"})
    assert body["reasoning_effort"] == "low"


def test_the_manifest_records_both_the_request_and_what_was_sent(cfg):
    resolution = adapter.resolve(cfg, "executor-implementation", backend="zai",
                                 reasoning_effort="xhigh", env={})
    block = adapter.inference_block(resolution)
    assert block["requested_reasoning_effort"] == "xhigh"
    assert block["reasoning_effort"] == "high"
