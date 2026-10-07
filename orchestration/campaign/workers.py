"""Agent-CLI drivers the autopilot can put behind one action.

Three runtimes already have role bindings in this repository (`.opencode/`,
`.claude/agents/`, `.codex/agents/`) and `orchestration/providers.yaml`
declares which backends each one can speak to.  This module turns a resolved
binding into the exact command line, environment, and event grammar of one
runtime, so the supervisor in `autopilot.py` can treat "which CLI" as a
parameter rather than a fork of the loop.

What a driver does NOT decide: which model.  That is the resolver's job, from
the committed bindings and the operator overlay.  A driver only renders the
resolved id the way its CLI expects to read it.
"""
from __future__ import annotations

import json
import os
import shlex
from pathlib import Path
from typing import Any

from ..adapter.config import Config, ConfigError

# OpenCode routes `provider/model`; the provider ids it knows differ from this
# repository's backend names where `opencode.json` registers a custom
# provider (`vllm` for `local`) or where OpenCode's catalogue uses another
# spelling (`fireworks-ai`).
OPENCODE_PROVIDER_IDS = {"local": "vllm", "fireworks": "fireworks-ai"}

RUNTIMES: dict[str, dict[str, Any]] = {
    "opencode": {"binary": "opencode", "extra_args_env": None},
    "claude_code": {"binary": "claude", "extra_args_env": "AUTORESEARCH_CLAUDE_ARGS",
                    # Non-interactive Claude Code cannot answer a permission
                    # prompt, so a denied tool is a failed action. `acceptEdits`
                    # lets the worker write under the checkout; widen it with
                    # the env var (for example `--allowedTools 'Bash(git:*)'`),
                    # which is the operator's decision, not this module's.
                    "default_extra_args": ["--permission-mode", "acceptEdits"]},
    "codex_cli": {"binary": "codex", "extra_args_env": "AUTORESEARCH_CODEX_ARGS",
                  "default_extra_args": ["--sandbox", "workspace-write"]},
}

# A backend the runtime authenticates to on its own (the CLI reads its own
# credential and talks to its own vendor): exporting the credential under the
# runtime's proxy variable would change the auth scheme, not just the value.
NATIVE_BACKEND = {"claude_code": "anthropic", "codex_cli": "openai"}


class WorkerError(ValueError):
    """The runtime, backend, or binary combination cannot run an action."""


def runtime_names() -> list[str]:
    return sorted(RUNTIMES)


def binary_for(runtime: str) -> str:
    try:
        return RUNTIMES[runtime]["binary"]
    except KeyError:
        raise WorkerError(f"unknown worker runtime {runtime!r}; one of "
                          f"{', '.join(runtime_names())}") from None


def compatible_backends(config: Config, runtime: str) -> list[str]:
    binary_for(runtime)
    try:
        declared = config.runtime(runtime)
    except ConfigError as exc:
        raise WorkerError(str(exc)) from None
    return list(declared.get("compatible_backends") or [])


def check_compatibility(config: Config, runtime: str, backends: list[str]) -> list[str]:
    """Return the backends this runtime can speak to, refusing a mixed list.

    A wire mismatch is not a failover case: the CLI would send an Anthropic
    request to an OpenAI endpoint and fail on every model in turn, which the
    supervisor would then record as "all models down" and retry forever.
    """
    allowed = compatible_backends(config, runtime)
    rejected = [b for b in backends if b not in allowed]
    if rejected:
        raise WorkerError(
            f"runtime {runtime} cannot use backend(s) {', '.join(rejected)}; "
            f"compatible: {', '.join(allowed)}")
    return list(backends)


def model_reference(runtime: str, backend: str, model_id: str) -> str:
    """How the CLI's `--model` flag names the resolved model."""
    binary_for(runtime)
    if runtime == "opencode":
        return f"{OPENCODE_PROVIDER_IDS.get(backend, backend)}/{model_id}"
    return model_id


def extra_args(runtime: str, env: dict[str, str] | None = None) -> list[str]:
    env = os.environ if env is None else env
    spec = RUNTIMES[runtime]
    var = spec.get("extra_args_env")
    if var and env.get(var) is not None:
        return shlex.split(env[var])
    return list(spec.get("default_extra_args") or [])


def build_command(runtime: str, prompt: str, model_ref: str, *,
                  attach: str | None = None,
                  env: dict[str, str] | None = None) -> list[str]:
    binary = binary_for(runtime)
    if runtime == "opencode":
        command = [binary, "run"]
        if attach:
            command.extend(["--attach", attach])
        # `build` is the top-level dispatcher agent: it may invoke the role
        # subagents, which the role agents themselves may not.
        command.extend(["--format", "json", "--agent", "build",
                        "--model", model_ref, prompt])
        return command
    if attach:
        raise WorkerError("--attach is an OpenCode server URL; "
                          f"runtime {runtime} has no equivalent")
    if runtime == "claude_code":
        return [binary, "-p", prompt, "--output-format", "stream-json", "--verbose",
                "--model", model_ref, *extra_args(runtime, env)]
    if runtime == "codex_cli":
        return [binary, "exec", "--json", "-m", model_ref,
                *extra_args(runtime, env), prompt]
    raise WorkerError(f"no command builder for runtime {runtime}")  # pragma: no cover


def runtime_env(config: Config, runtime: str, backend: str, model_id: str, *,
                env: dict[str, str] | None = None) -> dict[str, str]:
    """Variables that point a CLI runtime at the resolved backend.

    OpenCode takes its routing from `opencode.json`, so it gets nothing here;
    the other two read the vendor variables declared in providers.yaml.
    """
    env = os.environ if env is None else env
    binary_for(runtime)
    names = config.runtime(runtime).get("env") or {}
    if not names or runtime == "opencode":
        return {}
    exports: dict[str, str] = {}
    if names.get("base_url"):
        exports[names["base_url"]] = config.base_url(backend, env)
    if names.get("model"):
        exports[names["model"]] = model_id
    native = NATIVE_BACKEND.get(runtime) == backend
    key_env = config.backend(backend).get("api_key_env")
    if names.get("api_key") and key_env and env.get(key_env) and not native:
        exports[names["api_key"]] = env[key_env]
    if names.get("small_model") and not native:
        # A proxy serves the models it serves; the runtime's default small
        # model is a vendor id the proxy has probably never heard of.
        exports[names["small_model"]] = model_id
    return exports


# --------------------------------------------------------------------------
# event streams
# --------------------------------------------------------------------------
def _lines(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict):
                yield event


def _opencode_part(event: dict) -> dict:
    part = event.get("part") or (event.get("properties") or {}).get("part") or {}
    return part if isinstance(part, dict) else {}


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def usage(runtime: str, event_file: Path) -> dict[str, float | int | None]:
    """Sum what the runtime reported; unknown usage stays null, never zero."""
    binary_for(runtime)
    tokens_in = tokens_out = 0
    cost = 0.0
    seen_input = seen_output = seen_cost = False
    for event in _lines(event_file):
        tokens: Any = None
        event_cost: Any = None
        if runtime == "opencode":
            part = _opencode_part(event)
            if part.get("type") != "step-finish":
                continue
            tokens, event_cost = part.get("tokens"), part.get("cost")
            keys = ("input", "output")
        elif runtime == "claude_code":
            if event.get("type") != "result":
                continue
            tokens, event_cost = event.get("usage"), event.get("total_cost_usd")
            keys = ("input_tokens", "output_tokens")
        else:  # codex_cli
            if event.get("type") != "turn.completed":
                continue
            tokens = event.get("usage")
            keys = ("input_tokens", "output_tokens")
        if isinstance(tokens, dict):
            if _number(tokens.get(keys[0])):
                tokens_in += int(tokens[keys[0]])
                seen_input = True
            if _number(tokens.get(keys[1])):
                tokens_out += int(tokens[keys[1]])
                seen_output = True
        if _number(event_cost):
            cost += float(event_cost)
            seen_cost = True
    return {"input_tokens": tokens_in if seen_input else None,
            "output_tokens": tokens_out if seen_output else None,
            "cost_usd": round(cost, 8) if seen_cost else None}


_CODEX_TOOL_ITEMS = {"command_execution", "file_change", "mcp_tool_call",
                     "web_search", "patch_apply"}


def has_tool_events(runtime: str, path: Path) -> bool:
    """Whether the worker observably acted, which is what forbids failover."""
    binary_for(runtime)
    for event in _lines(path):
        if runtime == "opencode":
            kind = str(_opencode_part(event).get("type", ""))
            if "tool" in kind.lower() or "tool" in str(event.get("type", "")).lower():
                return True
        elif runtime == "claude_code":
            if event.get("type") in ("tool_use", "tool_result"):
                return True
            message = event.get("message") or {}
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, list) and any(
                    isinstance(c, dict) and c.get("type") in ("tool_use", "tool_result")
                    for c in content):
                return True
        else:  # codex_cli
            item = event.get("item") or {}
            if (str(event.get("type", "")).startswith("item.")
                    and isinstance(item, dict)
                    and item.get("type") in _CODEX_TOOL_ITEMS):
                return True
    return False


def has_error_events(runtime: str, path: Path) -> bool:
    """A zero exit with an error event is still a failed action."""
    binary_for(runtime)
    for event in _lines(path):
        kind = event.get("type")
        if runtime == "opencode":
            if kind == "error":
                return True
        elif runtime == "claude_code":
            if kind == "result" and (event.get("is_error") is True
                                     or str(event.get("subtype", "")).startswith("error")):
                return True
        else:  # codex_cli
            if kind in ("error", "turn.failed"):
                return True
    return False
