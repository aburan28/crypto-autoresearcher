"""Minimal multi-protocol transport: Anthropic Messages and OpenAI Chat.

Standard library only — the research harness must stay installable from
`requirements-dev.txt` and reproducible from a pinned Python, so no vendor SDKs
are pulled in. Adding a vendor is normally a `providers.yaml` entry; it needs
code here only when a genuinely new wire shape appears.

Requests carry no repository content by themselves: the caller supplies the
system prompt and messages, and the resolution supplies the endpoint.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

from .config import ConfigError, REQUEST_TARGET_SELECTOR_FIELDS
from .resolver import Resolution

RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}


class TransportError(RuntimeError):
    """The request could not be completed against the configured backend."""


class _TargetCheckingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Validate every default-urllib redirect destination before following it."""

    def __init__(self, config):
        super().__init__()
        self._config = config

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self._config.assert_inference_target_allowed(
            newurl, context="redirected inference endpoint")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _default_opener(config) -> Callable[..., Any]:
    """Build a standard opener whose redirects remain inside the cost policy."""
    return urllib.request.build_opener(
        _TargetCheckingRedirectHandler(config)).open


@dataclass
class ToolCall:
    """A tool the model asked to run."""
    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """What running it produced. `is_error` is carried, never hidden."""
    id: str
    name: str
    content: str
    is_error: bool = False


@dataclass
class Message:
    """One turn, in wire-neutral form.

    `role` is "user", "assistant", or "tool_results". The two protocols
    disagree about where tool results live -- Anthropic puts them in a user
    turn, OpenAI gives them their own role -- so the canonical form keeps them
    separate and each renderer places them correctly.
    """
    role: str
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)


@dataclass
class Tool:
    """Wire-neutral tool declaration; translated per protocol."""
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class Completion:
    text: str
    model: str
    stop_reason: str | None
    usage: dict[str, int]
    tool_calls: list[ToolCall] = field(default_factory=list)
    latency_seconds: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


def translate_tools(tools: list[Tool], wire: str) -> list[dict[str, Any]]:
    if wire == "anthropic_messages":
        return [{"name": t.name, "description": t.description,
                 "input_schema": t.input_schema} for t in tools]
    if wire == "openai_chat":
        return [{"type": "function",
                 "function": {"name": t.name, "description": t.description,
                              "parameters": t.input_schema}} for t in tools]
    raise TransportError(f"cannot translate tools for wire protocol {wire!r}")


def auth_headers(protocol: dict[str, Any], backend: dict[str, Any],
                 api_key: str) -> dict[str, str]:
    """Auth headers for a backend, letting it override its protocol's default.

    A wire protocol implies an auth scheme, but not always: a provider can
    speak the Anthropic Messages format while authenticating with its own
    header, so that a user's real Anthropic key sitting in the environment
    cannot be picked up instead. Fireworks does exactly this. Keeping the
    override in `providers.yaml` means such a provider stays a config entry
    rather than a code change.
    """
    if not api_key:
        return {}
    auth = backend.get("auth") or protocol["auth"]
    if auth["style"] == "bearer":
        return {auth["header"]: f"Bearer {api_key}"}
    return {auth["header"]: api_key}


def render_messages(messages: list[Message], wire: str,
                    system: str | None = None) -> list[dict[str, Any]]:
    """Canonical turns -> one protocol's message list.

    This is where a multi-turn tool conversation stops being portable by
    accident and becomes portable on purpose: the same transcript replays
    against either protocol, so a role's behaviour is not a property of the
    vendor it happened to run on.
    """
    if wire == "anthropic_messages":
        rendered: list[dict[str, Any]] = []
        for message in messages:
            if message.role == "tool_results":
                rendered.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": r.id,
                     "content": r.content, "is_error": r.is_error}
                    for r in message.tool_results]})
            elif message.tool_calls:
                blocks: list[dict[str, Any]] = []
                if message.content:
                    blocks.append({"type": "text", "text": message.content})
                blocks.extend({"type": "tool_use", "id": c.id, "name": c.name,
                               "input": c.arguments} for c in message.tool_calls)
                rendered.append({"role": message.role, "content": blocks})
            else:
                rendered.append({"role": message.role, "content": message.content})
        return rendered

    if wire == "openai_chat":
        rendered = [{"role": "system", "content": system}] if system else []
        for message in messages:
            if message.role == "tool_results":
                rendered.extend({"role": "tool", "tool_call_id": r.id,
                                 "content": r.content}
                                for r in message.tool_results)
            elif message.tool_calls:
                rendered.append({
                    "role": message.role,
                    "content": message.content or None,
                    "tool_calls": [
                        {"id": c.id, "type": "function",
                         "function": {"name": c.name,
                                      "arguments": json.dumps(c.arguments)}}
                        for c in message.tool_calls]})
            else:
                rendered.append({"role": message.role, "content": message.content})
        return rendered

    raise TransportError(f"cannot render messages for wire protocol {wire!r}")


def build_request(config, resolution: Resolution, *, system: str | None,
                  messages: list[Message], max_tokens: int | None = None,
                  tools: list[Tool] | None = None,
                  env: dict[str, str] | None = None
                  ) -> tuple[str, dict[str, str], dict[str, Any]]:
    """Return (url, headers, body) for this resolution. No network I/O."""
    env = os.environ if env is None else env
    config.assert_inference_target_allowed(
        resolution.backend, resolution.provider, resolution.base_url,
        resolution.resolved_model_id, context="resolved inference target")
    protocol = config.wire_protocol(resolution.wire)
    backend = config.backend(resolution.backend)
    url = resolution.base_url + protocol["path"]
    config.assert_inference_target_allowed(
        url, context="resolved inference endpoint")

    api_key = env.get(resolution.api_key_env, "")
    if not api_key and not backend.get("api_key_optional"):
        raise TransportError(
            f"backend {resolution.backend} needs credentials in "
            f"${resolution.api_key_env}, which is unset")

    headers = {"content-type": "application/json"}
    headers.update({k: str(v) for k, v in (protocol.get("static_headers") or {}).items()})
    headers.update(auth_headers(protocol, backend, api_key))

    request_cfg = dict(resolution.request)
    config.assert_inference_target_allowed(
        request_cfg, *request_cfg.values(), context="resolved inference request")
    selectors = sorted(REQUEST_TARGET_SELECTOR_FIELDS.intersection(request_cfg))
    if selectors:
        raise ConfigError(
            "resolved inference request may not override transport target "
            f"selector(s): {', '.join(selectors)}")
    reasoning = request_cfg.pop("reasoning", None) or {}
    limit = max_tokens or request_cfg.pop("max_tokens", None) or 4096
    request_cfg.pop("max_tokens", None)
    temperature = request_cfg.pop("temperature", None)
    # OpenAI's newer model families reject `max_tokens` and require the limit
    # under `max_completion_tokens`. A backend declares its wire's parameter
    # name with `token_limit_param`; the default keeps the historical name so
    # every existing OpenAI-compatible backend behaves exactly as before.
    token_param = request_cfg.pop("token_limit_param", None)
    if not isinstance(token_param, str) or not token_param:
        token_param = "max_tokens"

    if resolution.wire == "anthropic_messages":
        body: dict[str, Any] = {
            "model": resolution.resolved_model_id,
            "max_tokens": limit,
            "messages": render_messages(messages, resolution.wire),
        }
        if system:
            body["system"] = system
        budget = _thinking_budget(reasoning, resolution.reasoning_effort, limit)
        if budget:
            body["thinking"] = {"type": "enabled", "budget_tokens": budget}
        elif temperature is not None:
            # Extended thinking pins temperature; only set it when off -- which
            # is exactly the case for the calibrated-low tiers.
            body["temperature"] = temperature
    elif resolution.wire == "openai_chat":
        body = {
            "model": resolution.resolved_model_id,
            token_param: limit,
            "messages": render_messages(messages, resolution.wire, system),
        }
        if temperature is not None:
            body["temperature"] = temperature
        if reasoning.get("mode") == "openai_effort":
            effort_map = reasoning.get("effort_map") or {}
            mapped = effort_map.get(resolution.reasoning_effort)
            if mapped:
                body["reasoning_effort"] = mapped
    else:
        raise TransportError(f"unsupported wire protocol {resolution.wire!r}")

    if tools:
        body["tools"] = translate_tools(tools, resolution.wire)
    body.update(request_cfg)  # any remaining provider-specific knobs
    config.assert_inference_target_allowed(
        url,
        *(body.get(field) for field in REQUEST_TARGET_SELECTOR_FIELDS),
        context="final inference request")
    return url, headers, body


def _thinking_budget(reasoning: dict[str, Any], effort: str,
                     max_tokens: int) -> int:
    """Anthropic thinking budget for the effort this policy asked for.

    A binding maps effort -> budget, so calibrating a role's effort actually
    changes what is sent rather than only what is recorded. A budget of 0 (the
    `low` tier) disables extended thinking entirely.
    """
    if reasoning.get("mode") != "anthropic_thinking":
        return 0
    by_effort = reasoning.get("budget_by_effort") or {}
    budget = by_effort.get(effort, reasoning.get("budget_tokens", 0))
    if not budget:
        return 0
    # The API requires budget < max_tokens, leaving room for the answer itself.
    return min(int(budget), max(max_tokens - 1024, 1024))


def parse_response(wire: str, payload: dict[str, Any]) -> Completion:
    if wire == "anthropic_messages":
        blocks = payload.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        calls = [ToolCall(id=b.get("id", ""), name=b.get("name", ""),
                          arguments=b.get("input") or {})
                 for b in blocks if b.get("type") == "tool_use"]
        usage = payload.get("usage") or {}
        return Completion(
            text=text, model=payload.get("model", ""),
            stop_reason=payload.get("stop_reason"),
            usage={"input_tokens": usage.get("input_tokens", 0),
                   "output_tokens": usage.get("output_tokens", 0)},
            tool_calls=calls, raw=payload)
    if wire == "openai_chat":
        choices = payload.get("choices") or [{}]
        message = choices[0].get("message") or {}
        calls = []
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            arguments = function.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"__unparsed_arguments__": arguments}
            calls.append(ToolCall(id=call.get("id", ""), name=function.get("name", ""),
                                  arguments=arguments or {}))
        usage = payload.get("usage") or {}
        return Completion(
            text=message.get("content") or "", model=payload.get("model", ""),
            stop_reason=choices[0].get("finish_reason"),
            usage={"input_tokens": usage.get("prompt_tokens", 0),
                   "output_tokens": usage.get("completion_tokens", 0)},
            tool_calls=calls, raw=payload)
    raise TransportError(f"unsupported wire protocol {wire!r}")


def post_json(config, url: str, headers: dict[str, str], body: dict[str, Any], *,
              timeout: float, max_retries: int,
              opener: Callable[..., Any] | None = None,
              sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """POST a preflighted request with bounded retries.

    This is deliberately another guard boundary rather than trusting callers
    to have passed through ``build_request``.  Keeping it here closes future
    direct-call regressions before a ``urllib`` request object is constructed.
    """
    config.assert_inference_target_allowed(
        url,
        *(body.get(field) for field in REQUEST_TARGET_SELECTOR_FIELDS),
        context="outbound inference request")
    opener = opener or _default_opener(config)
    data = json.dumps(body).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(max_retries):
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with opener(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:               # noqa: PERF203
            detail = exc.read().decode("utf-8", "replace")[:2000]
            last_error = TransportError(f"HTTP {exc.code} from {url}: {detail}")
            if exc.code not in RETRY_STATUS:
                raise last_error from exc
        except urllib.error.URLError as exc:
            last_error = TransportError(f"network error contacting {url}: {exc.reason}")
        if attempt < max_retries - 1:
            sleep(2.0 ** attempt)
    raise last_error or TransportError(f"request to {url} failed")


def complete(config, resolution: Resolution, *, system: str | None,
             messages: list[Message], max_tokens: int | None = None,
             tools: list[Tool] | None = None,
             env: dict[str, str] | None = None,
             opener: Callable[..., Any] | None = None,
             sleep: Callable[[float], None] = time.sleep) -> Completion:
    defaults = config.providers.get("defaults", {})
    url, headers, body = build_request(
        config, resolution, system=system, messages=messages,
        max_tokens=max_tokens, tools=tools, env=env)
    started = time.time()
    payload = post_json(
        config, url, headers, body,
        timeout=float(defaults.get("request_timeout_seconds", 600)),
        max_retries=int(defaults.get("max_retries", 3)),
        opener=opener, sleep=sleep)
    completion = parse_response(resolution.wire, payload)
    completion.latency_seconds = round(time.time() - started, 3)
    return completion


def list_models(config, backend_name: str, *, env: dict[str, str] | None = None,
                opener: Callable[..., Any] | None = None,
                timeout: float = 60.0) -> list[str]:
    """Ask the backend what it actually serves. The only source of truth for ids."""
    env = os.environ if env is None else env
    backend = config.backend(backend_name)
    if not backend.get("supports_models_probe"):
        raise TransportError(
            f"backend {backend_name} declares no model-listing endpoint; verify "
            f"its identifiers against the provider's own documentation")
    protocol = config.wire_protocol(backend["wire"])
    url = config.base_url(backend_name, env) + protocol["models_path"]
    config.assert_inference_target_allowed(
        url, context="resolved model-probe endpoint")
    api_key = env.get(backend["api_key_env"], "")
    if not api_key and not backend.get("api_key_optional"):
        raise TransportError(
            f"backend {backend_name} needs credentials in "
            f"${backend['api_key_env']}, which is unset")
    headers = {k: str(v) for k, v in (protocol.get("static_headers") or {}).items()}
    headers.update(auth_headers(protocol, backend, api_key))

    opener = opener or _default_opener(config)
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with opener(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise TransportError(
            f"HTTP {exc.code} listing models at {url}: "
            f"{exc.read().decode('utf-8', 'replace')[:500]}") from exc
    except urllib.error.URLError as exc:
        raise TransportError(f"network error listing models at {url}: {exc.reason}") from exc
    return sorted(
        str(entry.get("id")) for entry in (payload.get("data") or []) if entry.get("id"))
