"""The `api_direct` tool loop, as a LangGraph state machine.

Two nodes -- call the model, run the tools it asked for -- with the budget
checked before each model call rather than after the fact. A run that stops
because it ran out of steps or wall clock exits with that reason recorded:
under `AGENTS.md` rule 5 an exhausted budget is infrastructure signal, and a
report that cannot distinguish it from a completed task is worse than no
report.

The checkpointer is what makes a long research task survivable. State is
persisted after every node, keyed by the task id, so a crashed or interrupted
run resumes from the last completed tool call instead of restarting and
re-doing side effects.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any, Callable, Sequence, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

STEP_BUDGET = "step_budget_exhausted"
CLOCK_BUDGET = "wall_clock_budget_exhausted"
COMPLETED = "completed"


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    steps: int
    stop_reason: str | None


def build_agent(model: Any, tools: Sequence[Any], *, max_steps: int = 40,
                deadline: float | None = None,
                checkpointer: Any = None,
                clock: Callable[[], float] = time.monotonic) -> Any:
    """Compile the loop. `deadline` is a `clock()`-comparable instant."""
    bound = model.bind_tools(list(tools)) if tools else model

    def call_model(state: AgentState) -> dict[str, Any]:
        if state["steps"] >= max_steps:
            return {"stop_reason": STEP_BUDGET}
        if deadline is not None and clock() >= deadline:
            return {"stop_reason": CLOCK_BUDGET}
        response = bound.invoke(state["messages"])
        return {"messages": [response], "steps": state["steps"] + 1}

    def route(state: AgentState) -> str:
        if state.get("stop_reason"):
            return END
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_edge(START, "model")
    if tools:
        graph.add_node("tools", ToolNode(list(tools)))
        graph.add_edge("tools", "model")
        graph.add_conditional_edges("model", route, {"tools": "tools", END: END})
    else:
        graph.add_conditional_edges("model", route, {END: END})
    return graph.compile(checkpointer=checkpointer)


def open_checkpointer(path: str | Path | None) -> tuple[Any, Any]:
    """Return (checkpointer, closeable). `None` path -> in-memory."""
    if path is None:
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver(), None
    from langgraph.checkpoint.sqlite import SqliteSaver
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(target), check_same_thread=False)
    saver = SqliteSaver(connection)
    saver.setup()
    return saver, connection


def final_stop_reason(state: dict[str, Any]) -> str:
    return state.get("stop_reason") or COMPLETED
