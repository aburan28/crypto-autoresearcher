"""Provider-neutral prompt-cache policy and request instrumentation.

The cache layer deliberately lives above the wire transport. It preserves the
existing adapter API while making stable-prefix caching explicit, deterministic,
and measurable for Anthropic Messages and OpenAI-compatible requests.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from . import transport as transport_module
from .transport import Completion, Message, Tool, build_request

# Cache controls are provider-specific, not wire-format capabilities. An
# OpenAI-compatible gateway or local server must not receive first-party cache
# parameters merely because it speaks the same protocol.
CACHE_CAPABLE_BACKENDS = frozenset({"anthropic", "openai"})


@dataclass(frozen=True)
class PromptCachePolicy:
    """Controls provider-side prompt caching for one request.

    ``namespace`` should identify the stable workload (for example a role plus
    the content hash of its shared policy/tool prefix), not an individual run.
    Volatile values such as a timestamp or run id must never be included in it.
    """

    enabled: bool = True
    namespace: str = "autoresearch"
    anthropic_ttl: str = "5m"
    openai_retention: str | None = None
    cache_tools: bool = True
    cache_system: bool = True
    # Cache the conversation itself, not only the fixed prefix. Right for a
    # multi-turn tool loop, where every turn re-sends the whole transcript;
    # wrong for a one-off prompt or a batch item, where the tail is unique and
    # marking it pays the write premium on bytes nothing ever reads back.
    cache_messages: bool = False
    messages_ttl: str = "5m"

    def __post_init__(self) -> None:
        if self.anthropic_ttl not in {"5m", "1h"}:
            raise ValueError("anthropic_ttl must be '5m' or '1h'")
        if self.messages_ttl not in {"5m", "1h"}:
            raise ValueError("messages_ttl must be '5m' or '1h'")
        if self.openai_retention not in {None, "24h"}:
            raise ValueError("openai_retention must be None or '24h'")
        if (self.cache_messages and self.messages_ttl == "1h"
                and self.anthropic_ttl == "5m"
                and (self.cache_system or self.cache_tools)):
            # The API requires longer-lived entries to precede shorter ones.
            raise ValueError("a 1h messages TTL cannot follow a 5m prefix TTL; "
                             "longer-lived cache entries must come first")


# The agent loop: the system prompt (role contract) and tools are large and
# never change within a role, so they hold a 1-hour entry that survives slow
# tool calls and long thinking turns and is shared across tasks of the same
# role. The transcript grows every turn and is re-read on the next one within
# seconds or minutes, so the cheaper 5-minute write is enough for it.
AGENT_LOOP_CACHE = PromptCachePolicy(anthropic_ttl="1h", cache_messages=True,
                                     messages_ttl="5m")


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
        if policy.cache_messages and rendered.get("messages"):
            # Top-level automatic caching: the API places the breakpoint on the
            # last cacheable block and moves it forward as the transcript
            # grows, so each turn reads everything before it and writes only
            # the delta. One slot, after the system and tool markers.
            rendered["cache_control"] = {"type": "ephemeral",
                                         "ttl": policy.messages_ttl}
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


def cached_complete(config, resolution, *, system: str | None,
                    messages: list[Message], max_tokens: int | None = None,
                    tools: list[Tool] | None = None,
                    cache_policy: PromptCachePolicy | None = None,
                    env: dict[str, str] | None = None,
                    opener: Callable[..., Any] | None = None,
                    sleep: Callable[[float], None] = time.sleep) -> Completion:
    """`transport.complete`, with provider prompt caching where it is safe.

    The one synchronous call path for every caller that wants caching: the
    agent loop, `adapter complete`, and the interactive lane of `batch
    submit`. A backend outside `CACHE_CAPABLE_BACKENDS` gets the plain request
    unchanged. The usage block keeps the provider's cache counters, so a
    receipt shows what was read from cache and what was written to it.
    """
    if resolution.backend not in CACHE_CAPABLE_BACKENDS:
        return transport_module.complete(
            config, resolution, system=system, messages=messages,
            max_tokens=max_tokens, tools=tools, env=env, opener=opener,
            sleep=sleep)
    url, headers, body = build_cached_request(
        config, resolution, system=system, messages=messages,
        max_tokens=max_tokens, tools=tools, cache_policy=cache_policy, env=env)
    defaults = config.providers.get("defaults", {})
    started = time.time()
    payload = transport_module.post_json(
        config, url, headers, body,
        timeout=float(defaults.get("request_timeout_seconds", 600)),
        max_retries=int(defaults.get("max_retries", 3)),
        opener=opener, sleep=sleep)
    completion = transport_module.parse_response(resolution.wire, payload)
    completion = attach_cache_usage(completion, resolution.wire, payload)
    completion.latency_seconds = round(time.time() - started, 3)
    return completion


def normalize_usage(wire: str, payload: Mapping[str, Any]) -> dict[str, int]:
    """Expose cache reads/writes without losing the adapter's common counters.

    Cache counters are retained only when the provider reported them. Missing
    fields stay absent so aggregators such as ``usage_totals`` do not invent
    zeroed cache traffic.
    """
    usage = payload.get("usage") or {}
    if wire == "anthropic_messages":
        normalized = {
            "input_tokens": int(usage.get("input_tokens", 0)),
            "output_tokens": int(usage.get("output_tokens", 0)),
        }
        if "cache_read_input_tokens" in usage:
            normalized["cache_read_input_tokens"] = int(
                usage["cache_read_input_tokens"])
        if "cache_creation_input_tokens" in usage:
            normalized["cache_creation_input_tokens"] = int(
                usage["cache_creation_input_tokens"])
        return normalized
    details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
    normalized = {
        "input_tokens": int(usage.get("prompt_tokens", usage.get("input_tokens", 0))),
        "output_tokens": int(usage.get("completion_tokens", usage.get("output_tokens", 0))),
    }
    if "cached_tokens" in details:
        normalized["cached_tokens"] = int(details["cached_tokens"])
    if "cache_write_tokens" in details:
        normalized["cache_write_tokens"] = int(details["cache_write_tokens"])
    return normalized


def attach_cache_usage(completion: Completion, wire: str,
                       payload: Mapping[str, Any]) -> Completion:
    completion.usage = normalize_usage(wire, payload)
    return completion


def cache_efficiency(usage: Mapping[str, int]) -> float:
    """Fraction of provider-accounted input traffic served by cache reads.

    Anthropic reports ``input_tokens`` separately from cache reads/writes, while
    OpenAI reports ``input_tokens``/``prompt_tokens`` as the total input and puts
    cache reads in a detail field. The denominator must therefore follow the
    provider accounting shape instead of subtracting cache reads unconditionally.
    """
    reads = int(usage.get("cache_read_input_tokens", usage.get("cached_tokens", 0)))
    if "cache_read_input_tokens" in usage or "cache_creation_input_tokens" in usage:
        writes = int(usage.get("cache_creation_input_tokens", 0))
        denominator = int(usage.get("input_tokens", 0)) + reads + writes
    else:
        denominator = int(usage.get("input_tokens", 0))
    return reads / denominator if denominator else 0.0


def cache_write_without_read(usage: Mapping[str, int]) -> bool:
    reads = int(usage.get("cache_read_input_tokens", usage.get("cached_tokens", 0)))
    writes = int(usage.get("cache_creation_input_tokens", usage.get("cache_write_tokens", 0)))
    return writes > 0 and reads == 0
