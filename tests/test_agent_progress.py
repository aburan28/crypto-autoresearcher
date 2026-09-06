"""Offline controls for operational token waste, not mathematical progress."""
from __future__ import annotations

import pytest

pytest.importorskip("langgraph", reason="api_direct runtime needs requirements-agent.txt")

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402

from orchestration.agent import graph, runner  # noqa: E402
from orchestration.agent.progress import repeated_tool_failure  # noqa: E402
from orchestration.agent.tools import TaskScope, ToolJournal, build_tools  # noqa: E402


def round_messages(index, *, path="missing.md", content="ERROR: missing.md is not a file",
                   status="success", name="read_file"):
    call_id = f"call-{index}"
    return [
        AIMessage(content="", tool_calls=[{
            "id": call_id, "name": name, "args": {"path": path}, "type": "tool_call",
        }]),
        ToolMessage(content=content, tool_call_id=call_id, name=name, status=status),
    ]


def history(**kwargs):
    return [message for i in range(3) for message in round_messages(i, **kwargs)]


def test_changed_call_ids_do_not_hide_identical_failures():
    detail = repeated_tool_failure(history())
    assert detail["consecutive_rounds"] == 3
    assert detail["tool_names"] == ["read_file"]
    assert detail["classification"] == "operational_tool_failure"


@pytest.mark.parametrize("content", [
    "1\tERROR: this is file content, not a tool failure",
    "still running: job-123",
    "TIMEOUT after 30s. This is an infrastructure outcome.",
    "exit_code: 1\n--- stdout ---\nnegative control rejected\n--- stderr ---\n",
    "exit_code: 0\n--- stdout ---\nERROR: application log\n--- stderr ---\n",
])
def test_observations_and_polling_are_not_stalls(content):
    assert repeated_tool_failure(history(content=content)) is None


def test_structured_tool_errors_are_recognised():
    assert repeated_tool_failure(history(content="invalid arguments", status="error"))


def test_changing_arguments_or_error_output_resets_the_streak():
    before = round_messages(0) + round_messages(1)
    assert repeated_tool_failure(before + round_messages(2, path="other.md")) is None
    assert repeated_tool_failure(before + round_messages(2, content="ERROR: different")) is None


def test_success_or_new_user_input_resets_the_streak():
    before = round_messages(0) + round_messages(1)
    assert repeated_tool_failure(before + round_messages(2, content="1\tdata")) is None
    assert repeated_tool_failure(before + [HumanMessage("new instructions")]
                                 + round_messages(2)) is None


def test_incomplete_tool_round_cannot_establish_a_stall():
    assert repeated_tool_failure(history()[:-1]) is None


def test_parallel_order_does_not_matter_but_one_success_prevents_a_stall():
    messages = []
    for i in range(3):
        calls = [round_messages(f"{i}-{j}", path=f"{j}.md") for j in range(2)]
        messages.append(AIMessage(content="", tool_calls=[c[0].tool_calls[0] for c in calls]))
        messages.extend([c[1] for c in (calls if i % 2 else reversed(calls))])
    assert repeated_tool_failure(messages)
    messages[-1] = messages[-1].model_copy(update={"content": "1\tdata"})
    assert repeated_tool_failure(messages) is None


class ScriptedModel:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = 0

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        self.calls += 1
        return next(self.replies)


def test_loop_stops_before_fourth_paid_request(tmp_path):
    model = ScriptedModel([round_messages(i)[0] for i in range(3)])
    journal = ToolJournal()
    tools = build_tools(TaskScope(tmp_path, "TASK-FIXTURE"), journal, ["read_file"])
    agent = graph.build_agent(model, tools, max_steps=40)
    state = agent.invoke({"messages": [HumanMessage("read")], "steps": 0,
                          "stop_reason": None})
    assert model.calls == state["steps"] == 3
    assert graph.final_stop_reason(state) == graph.TOOL_FAILURE
    assert state["stop_detail"]["consecutive_rounds"] == 3
    assert len(journal.denials) == 3
    run = runner.TaskRun(task_id="TASK-FIXTURE", role="executor",
                         stop_reason=graph.TOOL_FAILURE, steps=3, final_text="",
                         resolution=None, stop_detail=state["stop_detail"])
    assert not run.completed


def test_a_corrected_tool_call_can_finish(tmp_path):
    (tmp_path / "exists.md").write_text("useful evidence\n", encoding="utf-8")
    model = ScriptedModel([round_messages(0)[0], round_messages(1)[0],
                           round_messages(2, path="exists.md")[0],
                           AIMessage(content="finished")])
    tools = build_tools(TaskScope(tmp_path, "TASK-FIXTURE"), ToolJournal(), ["read_file"])
    state = graph.build_agent(model, tools, max_steps=10).invoke({
        "messages": [HumanMessage("read")], "steps": 0, "stop_reason": None})
    assert graph.final_stop_reason(state) == graph.COMPLETED
    assert model.calls == 4


def test_transcript_preserves_tool_status_and_per_response_usage():
    error = ToolMessage(content="invalid args", tool_call_id="c", status="error")
    assert runner._serialise(error)["status"] == "error"
    message = AIMessage(content="done", usage_metadata={
        "input_tokens": 10, "output_tokens": 2, "total_tokens": 12})
    assert runner._serialise(message)["usage_metadata"] == message.usage_metadata
    assert runner._serialise(error)["usage_metadata"] is None
