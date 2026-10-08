from __future__ import annotations

from orchestration import adapter


def _tool():
    return adapter.Tool(
        "read_file", "Read a repository file",
        {"type": "object", "properties": {"path": {"type": "string"}}},
    )


def test_cache_key_is_stable_across_mapping_order():
    left = adapter.Tool("x", "d", {"type": "object", "properties": {
        "b": {"type": "integer"}, "a": {"type": "string"}}})
    right = adapter.Tool("x", "d", {"properties": {
        "a": {"type": "string"}, "b": {"type": "integer"}}, "type": "object"})
    assert adapter.prompt_cache_key(
        namespace="executor:prefix-v1", model="m", system="stable", tools=[left]) == \
        adapter.prompt_cache_key(
            namespace="executor:prefix-v1", model="m", system="stable", tools=[right])


def test_anthropic_cache_marks_stable_system_and_last_tool():
    body = {"model": "m", "system": "stable", "messages": [], "tools": [
        {"name": "a", "description": "a", "input_schema": {}},
        {"name": "b", "description": "b", "input_schema": {}},
    ]}
    cached = adapter.apply_prompt_cache(
        body, wire="anthropic_messages", model="m", system="stable",
        tools=[_tool()], policy=adapter.PromptCachePolicy(anthropic_ttl="1h"))
    assert cached["system"][0]["text"] == "stable"
    assert cached["system"][0]["cache_control"] == {
        "type": "ephemeral", "ttl": "1h"}
    assert "cache_control" not in cached["tools"][0]
    assert cached["tools"][-1]["cache_control"]["ttl"] == "1h"
    assert body["system"] == "stable"


def test_openai_cache_key_excludes_volatile_messages():
    policy = adapter.PromptCachePolicy(namespace="review:prefix-v1")
    common = dict(wire="openai_chat", model="gpt-test", system="ROLE",
                  tools=[_tool()], policy=policy)
    one = adapter.apply_prompt_cache(
        {"model": "gpt-test", "messages": [{"role": "user", "content": "task 1"}]},
        **common)
    two = adapter.apply_prompt_cache(
        {"model": "gpt-test", "messages": [{"role": "user", "content": "task 2"}]},
        **common)
    assert one["prompt_cache_key"] == two["prompt_cache_key"]


def test_openai_extended_retention_is_opt_in():
    cached = adapter.apply_prompt_cache(
        {"model": "m", "messages": []}, wire="openai_chat", model="m",
        system="ROLE", tools=None,
        policy=adapter.PromptCachePolicy(openai_retention="24h"))
    assert cached["prompt_cache_retention"] == "24h"


def test_usage_normalization_preserves_provider_cache_counters():
    anthropic = adapter.normalize_usage("anthropic_messages", {"usage": {
        "input_tokens": 100, "output_tokens": 10,
        "cache_read_input_tokens": 80, "cache_creation_input_tokens": 20}})
    assert anthropic["cache_read_input_tokens"] == 80
    assert anthropic["cache_creation_input_tokens"] == 20

    openai = adapter.normalize_usage("openai_chat", {"usage": {
        "prompt_tokens": 100, "completion_tokens": 10,
        "prompt_tokens_details": {"cached_tokens": 80}}})
    assert openai["cached_tokens"] == 80
    assert "cache_write_tokens" not in openai


def test_usage_normalization_omits_absent_cache_counters():
    anthropic = adapter.normalize_usage("anthropic_messages", {"usage": {
        "input_tokens": 10, "output_tokens": 5}})
    assert anthropic == {"input_tokens": 10, "output_tokens": 5}

    openai = adapter.normalize_usage("openai_chat", {"usage": {
        "prompt_tokens": 10, "completion_tokens": 5}})
    assert openai == {"input_tokens": 10, "output_tokens": 5}


def test_cache_efficiency_respects_anthropic_accounting():
    assert adapter.cache_efficiency({
        "input_tokens": 20, "cache_read_input_tokens": 80,
        "cache_creation_input_tokens": 0}) == 0.8
    assert adapter.cache_efficiency({
        "input_tokens": 20, "cache_read_input_tokens": 80,
        "cache_creation_input_tokens": 20}) == 2 / 3


def test_cache_efficiency_respects_openai_accounting():
    assert adapter.cache_efficiency({
        "input_tokens": 100, "cached_tokens": 80}) == 0.8
    assert adapter.cache_efficiency({
        "input_tokens": 100, "cached_tokens": 80,
        "cache_write_tokens": 20}) == 0.8


def test_cache_write_without_read():
    assert adapter.cache_write_without_read({
        "input_tokens": 100, "cache_creation_input_tokens": 100})
    assert not adapter.cache_write_without_read({
        "input_tokens": 100, "cache_read_input_tokens": 80,
        "cache_creation_input_tokens": 20})


def test_invalid_ttls_are_rejected():
    import pytest
    with pytest.raises(ValueError, match="anthropic_ttl"):
        adapter.PromptCachePolicy(anthropic_ttl="2h")
    with pytest.raises(ValueError, match="openai_retention"):
        adapter.PromptCachePolicy(openai_retention="7d")


# --------------------------------------------------------------------------
# conversation caching, TTL policy, and the shared cached call path
# --------------------------------------------------------------------------
import io
import json
from pathlib import Path

import pytest

from orchestration.adapter import cli as cli_module
from orchestration.adapter import prompt_cache as prompt_cache_module
from orchestration.adapter import transport as transport_module


def _anthropic_body():
    return {"model": "m", "system": "ROLE", "max_tokens": 10,
            "messages": [{"role": "user", "content": "q"},
                         {"role": "assistant", "content": "a"},
                         {"role": "user", "content": "q2"}],
            "tools": [{"name": "a", "description": "a", "input_schema": {}}]}


def test_agent_loop_caches_the_prefix_for_an_hour_and_the_transcript_for_five_minutes():
    cached = adapter.apply_prompt_cache(
        _anthropic_body(), wire="anthropic_messages", model="m", system="ROLE",
        tools=[_tool()], policy=prompt_cache_module.AGENT_LOOP_CACHE)
    assert cached["system"][0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert cached["tools"][-1]["cache_control"]["ttl"] == "1h"
    # top-level automatic caching moves the breakpoint along the transcript
    assert cached["cache_control"] == {"type": "ephemeral", "ttl": "5m"}
    # the messages themselves are untouched: the API places the marker
    assert cached["messages"] == _anthropic_body()["messages"]
    breakpoints = 1 + 1 + 1
    assert breakpoints <= 4


def test_single_turn_and_batch_requests_never_mark_the_unique_tail():
    for policy in (adapter.PromptCachePolicy(),
                   adapter.PromptCachePolicy(anthropic_ttl="1h")):
        cached = adapter.apply_prompt_cache(
            _anthropic_body(), wire="anthropic_messages", model="m",
            system="ROLE", tools=None, policy=policy)
        assert "cache_control" not in cached


def test_longer_ttl_must_come_first():
    with pytest.raises(ValueError, match="longer-lived"):
        adapter.PromptCachePolicy(anthropic_ttl="5m", cache_messages=True,
                                  messages_ttl="1h")
    adapter.PromptCachePolicy(anthropic_ttl="1h", cache_messages=True,
                              messages_ttl="1h")


def test_openai_wire_gets_no_anthropic_markers():
    cached = adapter.apply_prompt_cache(
        {"model": "m", "messages": [{"role": "user", "content": "q"}]},
        wire="openai_chat", model="m", system="ROLE", tools=None,
        policy=prompt_cache_module.AGENT_LOOP_CACHE)
    assert "cache_control" not in cached
    assert cached["prompt_cache_key"]


class _Recorder:
    def __init__(self, usage):
        self.sent = []
        self.usage = usage

    def __call__(self, request, timeout=None):
        body = json.loads(request.data.decode())
        self.sent.append(body)
        return io.BytesIO(json.dumps({
            "model": body["model"], "stop_reason": "end_turn",
            "content": [{"type": "text", "text": "ok"}],
            "usage": self.usage}).encode())


def test_cached_complete_marks_first_party_and_leaves_gateways_alone():
    cfg = adapter.load()
    usage = {"input_tokens": 5, "output_tokens": 2,
             "cache_read_input_tokens": 900, "cache_creation_input_tokens": 0}
    first_party = adapter.resolve(cfg, "research-deep", backend="anthropic", env={})
    opener = _Recorder(usage)
    completion = prompt_cache_module.cached_complete(
        cfg, first_party, system="ROLE", messages=[adapter.Message("user", "q")],
        env={"ANTHROPIC_API_KEY": "k"}, opener=opener)
    assert opener.sent[0]["system"][0]["cache_control"]["type"] == "ephemeral"
    assert "cache_control" not in opener.sent[0]          # unique prompt, unmarked
    assert completion.usage["cache_read_input_tokens"] == 900

    gateway = adapter.resolve(cfg, "research-deep", backend="zai-anthropic", env={})
    opener = _Recorder({"input_tokens": 5, "output_tokens": 2})
    prompt_cache_module.cached_complete(
        cfg, gateway, system="ROLE", messages=[adapter.Message("user", "q")],
        env={"ZAI_API_KEY": "k"}, opener=opener)
    assert opener.sent[0]["system"] == "ROLE"             # plain string, no marker
    assert "cache_control" not in json.dumps(opener.sent[0])


def test_adapter_complete_caches_by_default_and_honours_no_cache(monkeypatch, tmp_path,
                                                                 capsys):
    recorder = _Recorder({"input_tokens": 5, "output_tokens": 2})
    monkeypatch.setattr(transport_module, "_default_opener", lambda cfg: recorder)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    prompt, system = tmp_path / "q.md", tmp_path / "s.md"
    prompt.write_text("question")
    system.write_text("ROLE CONTRACT")
    base = ["complete", "--policy", "research-deep", "--backend", "anthropic",
            "--prompt-file", str(prompt), "--system-file", str(system)]
    assert cli_module.main(base) == 0
    assert recorder.sent[-1]["system"][0]["cache_control"]["type"] == "ephemeral"
    assert cli_module.main(base + ["--no-cache"]) == 0
    assert recorder.sent[-1]["system"] == "ROLE CONTRACT"
    assert "ok" in capsys.readouterr().out
