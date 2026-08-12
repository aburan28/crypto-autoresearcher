"""A LangChain chat model backed by this repository's own transport.

Why not `langchain-openai` / `langchain-anthropic`: routing through them would
mean a second HTTP path with its own retry policy, its own credential
handling, and its own idea of which model it is talking to -- and a manifest
whose `resolved_model_id` came from one place while the request came from
another. Wrapping our transport instead keeps a single recorded path for every
backend, and keeps the dependency at `langchain-core` alone: no provider
package per vendor, so adding a backend stays a `providers.yaml` edit.

Import this module only where LangGraph is actually used; the adapter core has
no LangChain dependency.
"""
from __future__ import annotations

from typing import Any, Callable, Iterator, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolMessage)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import ConfigDict, Field

from . import transport as transport_module
from .config import Config
from .resolver import Resolution


def _text(content: Any) -> str:
    """LangChain content may be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content)
    return "" if content is None else str(content)


def to_canonical(messages: Sequence[BaseMessage]
                 ) -> tuple[str | None, list[transport_module.Message]]:
    """LangChain messages -> (system, canonical turns).

    Consecutive `ToolMessage`s collapse into one `tool_results` turn: the
    Anthropic protocol requires every result for a turn in a single message,
    and the OpenAI renderer splits them back out.
    """
    system_parts: list[str] = []
    turns: list[transport_module.Message] = []
    for message in messages:
        if isinstance(message, SystemMessage):
            system_parts.append(_text(message.content))
        elif isinstance(message, HumanMessage):
            turns.append(transport_module.Message("user", _text(message.content)))
        elif isinstance(message, AIMessage):
            turns.append(transport_module.Message(
                "assistant", _text(message.content),
                tool_calls=[transport_module.ToolCall(
                    id=call.get("id") or "", name=call.get("name") or "",
                    arguments=call.get("args") or {})
                    for call in (message.tool_calls or [])]))
        elif isinstance(message, ToolMessage):
            result = transport_module.ToolResult(
                id=message.tool_call_id, name=getattr(message, "name", "") or "",
                content=_text(message.content),
                is_error=getattr(message, "status", "success") == "error")
            if turns and turns[-1].role == "tool_results":
                turns[-1].tool_results.append(result)
            else:
                turns.append(transport_module.Message(
                    "tool_results", tool_results=[result]))
        else:
            turns.append(transport_module.Message("user", _text(message.content)))
    return ("\n\n".join(p for p in system_parts if p) or None), turns


def to_canonical_tools(tools: Sequence[Any]) -> list[transport_module.Tool]:
    """Any LangChain tool form -> our wire-neutral declaration."""
    canonical = []
    for tool in tools:
        spec = convert_to_openai_tool(tool)["function"]
        canonical.append(transport_module.Tool(
            name=spec["name"], description=spec.get("description", ""),
            input_schema=spec.get("parameters") or {"type": "object", "properties": {}}))
    return canonical


class ResolvedChatModel(BaseChatModel):
    """A chat model pinned to one `Resolution`.

    The model identity is fixed at construction by the resolver, not chosen
    here: there is deliberately no way to swap models on an instance, because
    a task's manifest has already recorded which model answered it.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    adapter_config: Config
    resolution: Resolution
    max_tokens: int | None = None
    request_env: dict[str, str] | None = None
    opener: Callable[..., Any] | None = None
    on_completion: Callable[[transport_module.Completion], None] | None = None
    completions: list[transport_module.Completion] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return f"autoresearch:{self.resolution.backend}"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {
            "backend": self.resolution.backend,
            "model": self.resolution.resolved_model_id,
            "policy": self.resolution.policy,
            "reasoning_effort": self.resolution.reasoning_effort,
            "config_digest": self.resolution.config_digest,
        }

    def bind_tools(self, tools: Sequence[Any], *, tool_choice: str | None = None,
                   **kwargs: Any) -> Runnable:
        return self.bind(tools=to_canonical_tools(tools), **kwargs)

    def _generate(self, messages: list[BaseMessage],
                  stop: list[str] | None = None,
                  run_manager: CallbackManagerForLLMRun | None = None,
                  **kwargs: Any) -> ChatResult:
        system, turns = to_canonical(messages)
        completion = transport_module.complete(
            self.adapter_config, self.resolution,
            system=system, messages=turns,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            tools=kwargs.get("tools"),
            env=self.request_env, opener=self.opener)
        self.completions.append(completion)
        if self.on_completion is not None:
            self.on_completion(completion)
        return ChatResult(generations=[ChatGeneration(
            message=self._to_ai_message(completion))])

    def _to_ai_message(self, completion: transport_module.Completion) -> AIMessage:
        usage = completion.usage or {}
        return AIMessage(
            content=completion.text,
            tool_calls=[{"name": call.name, "args": call.arguments,
                         "id": call.id, "type": "tool_call"}
                        for call in completion.tool_calls],
            usage_metadata={
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            },
            response_metadata={
                "model_name": completion.model,
                "resolved_model_id": self.resolution.resolved_model_id,
                # A backend answering as a different model than the one we
                # resolved is an evidence problem, so carry both and let the
                # receipt compare them rather than assuming they agree.
                "model_matches_resolution": (
                    completion.model == self.resolution.resolved_model_id
                    if completion.model else None),
                "backend": self.resolution.backend,
                "stop_reason": completion.stop_reason,
                "latency_seconds": completion.latency_seconds,
            })

    def usage_totals(self) -> dict[str, int]:
        totals = {"input_tokens": 0, "output_tokens": 0, "requests": 0}
        for completion in self.completions:
            totals["input_tokens"] += completion.usage.get("input_tokens", 0)
            totals["output_tokens"] += completion.usage.get("output_tokens", 0)
            totals["requests"] += 1
        return totals

    def model_disagreements(self) -> list[str]:
        """Models the backend actually answered as, when they differed."""
        return sorted({
            c.model for c in self.completions
            if c.model and c.model != self.resolution.resolved_model_id})
