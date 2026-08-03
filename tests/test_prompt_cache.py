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
        namespace="executor:tree-1", model="m", system="stable", tools=[left]) == \
        adapter.prompt_cache_key(
            namespace="executor:tree-1", model="m", system="stable", tools=[right])


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
    policy = adapter.PromptCachePolicy(namespace="review:tree-abc")
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


def test_cache_efficiency_and_write_without_read():
    assert adapter.cache_efficiency({
        "input_tokens": 100, "cache_read_input_tokens": 80,
        "cache_creation_input_tokens": 0}) == 0.8
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
