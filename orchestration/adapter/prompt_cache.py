"""Provider-neutral prompt-cache policy and request instrumentation.

The cache layer deliberately lives above the wire transport.  It preserves the
existing adapter API while making stable-prefix caching explicit, deterministic,
and measurable for Anthropic Messages and OpenAI-compatible requests.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .transport import Completion, Message, Tool, build_request, parse_response, post_json


@dataclass(frozen=True)
class PromptCachePolicy:
    """Controls provider-side prompt caching for one request.

    ``namespace`` should identify the stable workload (for example a role plus
    repository snapshot), not an individual run.  Volatile values such as a
    timestamp or run id must never be included in it.
    """

    enabled: bool = True
    namespace: str = "autoresearch"
    anthropic_ttl: str = "5m"
    openai_retention: str | None = None
    cache_tools: bool = True
    cache_system: bool = True

    def __post_init__(self) -> None:
        if self.anthropic_ttl not in {"5m", "1h"}:
            raise ValueError("anthropic_ttl must be '5m' or '1h'")
        if self.openai_retention not in {None, "24h"}:
            raise ValueError("openai_retention must be None or '24h'")


def canonical_json(value: Any) -> str:
    """Stable JSON used for cache identity and deterministic tool arguments."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def prompt_cache_key(*, namespace: str, model: str, system: str | None,
                     tools: Sequence[Tool] | None = None,
                     schema_version: str = "v1") -> str:
    """Return a content-addressed key for the stable prompt prefix.

    Messages are intentionally excluded: the key describes the shared prefix,
    while provider prefix matching handles the task-specific suffix.
    """
    tool_payload = [
        {"name": tool.name, "description": tool.description,
         "input_schema": tool.input_schema}
        for tool in (tools or [])
    ]
    digest = hashlib.sha256(canonical_json({
        "schema_version": schema_version,
        "namespace": namespace,
        "model": model,
        "system": system or "",
        "tools": tool_payload,
    }).encode("utf-8")).hexdigest()
    return f"{namespace}:{digest[:48]}"


def apply_prompt_cache(body: Mapping[str, Any], *, wire: str, model: str,
                       system: str | None, tools: Sequence[Tool] | None,
                       policy: PromptCachePolicy) -> dict[str, Any]:
    """Return a copied request body with provider cache controls attached."""
    rendered = dict(body)
    if not policy.enabled:
        return rendered

    if wire == "anthropic_messages":
        if policy.cache_system and system:
            rendered["system"] = [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral", "ttl": policy.anthropic_ttl},
            }]
        if policy.cache_tools and rendered.get("tools"):
            cached_tools = [dict(tool) for tool in rendered["tools"]]
            cached_tools[-1]["cache_control"] = {
                "type": "ephemeral", "ttl": policy.anthropic_ttl,
            }
            rendered["tools"] = cached_tools
        return rendered

    if wire == "openai_chat":
        rendered["prompt_cache_key"] = prompt_cache_key(
            namespace=policy.namespace, model=model, system=system, tools=tools)
        if policy.openai_retention:
            rendered["prompt_cache_retention"] = policy.openai_retention
        return rendered

    return rendered


def build_cached_request(config, resolution, *, system: str | None,
                         messages: list[Message], max_tokens: int | None = None,
                         tools: list[Tool] | None = None,
                         cache_policy: PromptCachePolicy | None = None,
                         env: dict[str, str] | None = None):
    """Build a normal adapter request and attach deterministic cache controls."""
    url, headers, body = build_request(
        config, resolution, system=system, messages=messages,
        max_tokens=max_tokens, tools=tools, env=env)
    policy = cache_policy or PromptCachePolicy()
    return url, headers, apply_prompt_cache(
        body, wire=resolution.wire, model=resolution.resolved_model_id,
        system=system, tools=tools, policy=policy)


def normalize_usage(wire: str, payload: Mapping[str, Any]) -> dict[str, int]:
    """Expose cache reads/writes without losing the adapter's common counters."""
    usage = payload.get("usage") or {}
    if wire == "anthropic_messages":
        return {
            "input_tokens": int(usage.get("input_tokens", 0)),
            "output_tokens": int(usage.get("output_tokens", 0)),
            "cache_read_input_tokens": int(usage.get("cache_read_input_tokens", 0)),
            "cache_creation_input_tokens": int(usage.get("cache_creation_input_tokens", 0)),
        }
    details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
    return {
        "input_tokens": int(usage.get("prompt_tokens", usage.get("input_tokens", 0))),
        "output_tokens": int(usage.get("completion_tokens", usage.get("output_tokens", 0))),
        "cached_tokens": int(details.get("cached_tokens", 0)),
        "cache_write_tokens": int(details.get("cache_write_tokens", 0)),
    }


def attach_cache_usage(completion: Completion, wire: str,
                       payload: Mapping[str, Any]) -> Completion:
    completion.usage = normalize_usage(wire, payload)
    return completion


def cache_efficiency(usage: Mapping[str, int]) -> float:
    """Fraction of all input/cache traffic served by cache reads."""
    reads = int(usage.get("cache_read_input_tokens", usage.get("cached_tokens", 0)))
    writes = int(usage.get("cache_creation_input_tokens", usage.get("cache_write_tokens", 0)))
    uncached = max(int(usage.get("input_tokens", 0)) - reads, 0)
    denominator = reads + writes + uncached
    return reads / denominator if denominator else 0.0


def cache_write_without_read(usage: Mapping[str, int]) -> bool:
    reads = int(usage.get("cache_read_input_tokens", usage.get("cached_tokens", 0)))
    writes = int(usage.get("cache_creation_input_tokens", usage.get("cache_write_tokens", 0)))
    return writes > 0 and reads == 0
