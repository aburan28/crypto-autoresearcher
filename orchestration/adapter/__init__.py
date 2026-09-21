"""Runtime-neutral inference adapter.

`AGENTS.md` has always described an adapter layer that resolves a role's
inference *policy* to a concrete model, records what actually answered, and
refuses to downgrade silently. This package is that layer.

Nothing in it is specific to Claude Code, the Codex CLI, or any vendor: those
are runtimes and backends declared in `orchestration/providers.yaml`.

    from orchestration.adapter import load, resolve
    cfg = load()
    r = resolve(cfg, "research-sol-max", backend="zai")   # legacy alias still resolves
    r.resolved_model_id, r.fallback_used
"""
from .config import ADAPTER_VERSION, Config, ConfigError, load, validate
from .manifest import (block_from_env, deterministic_block, inference_block,
                       receipt, write_receipt)
from .prompt_cache import (PromptCachePolicy, apply_prompt_cache,
                           build_cached_request, cache_efficiency,
                           cache_write_without_read, canonical_json,
                           normalize_usage, prompt_cache_key)
from .resolver import (Attempt, GovernanceError, Resolution, ResolutionError,
                      resolve, resolve_handoff)
from .transport import (Completion, Message, Tool, ToolCall, ToolResult,
                        TransportError, build_request, complete, list_models,
                        parse_response, render_messages, translate_tools)

__all__ = [
    "ADAPTER_VERSION", "Attempt", "Completion", "Config", "ConfigError",
    "GovernanceError", "Message", "PromptCachePolicy", "Resolution",
    "ResolutionError", "Tool", "ToolCall", "ToolResult", "TransportError",
    "apply_prompt_cache", "block_from_env", "build_cached_request",
    "build_request", "cache_efficiency", "cache_write_without_read",
    "canonical_json", "complete", "deterministic_block", "inference_block",
    "list_models", "load", "normalize_usage", "parse_response",
    "prompt_cache_key", "receipt", "render_messages", "resolve",
    "resolve_handoff", "translate_tools", "validate", "write_receipt",
]
