"""Tests for the api_direct LangGraph runtime.

No test touches the network: model responses are canned HTTP payloads fed
through the real transport, so the whole stack -- rendering, protocol,
parsing, tool loop, journal, receipt -- is exercised without a backend.

The scope tests are the important ones. `AGENTS.md` promises that a dispatched
task writes only inside its own `write_scope`; here that promise is executable,
so it gets adversarial cases rather than a happy path.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

pytest.importorskip("langgraph", reason="api_direct runtime needs requirements-agent.txt")

from langchain_core.messages import (AIMessage, HumanMessage,  # noqa: E402
                                     SystemMessage, ToolMessage)

from orchestration import adapter, role_registry  # noqa: E402
from orchestration.adapter import langchain_model, transport  # noqa: E402
from orchestration.agent import graph as graph_module  # noqa: E402
from orchestration.agent import runner as runner_module  # noqa: E402
from orchestration.agent.tools import (TaskScope, ToolDenied,  # noqa: E402
                                       ToolJournal, build_tools)

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cfg():
    return adapter.load()


@pytest.fixture
def scope(tmp_path):
    (tmp_path / "coordination/tasks/TASK-1").mkdir(parents=True)
    (tmp_path / "ledger").mkdir()
    (tmp_path / "ledger/H-A-001.yaml").write_text("hypothesis: {}\n")
    return TaskScope(repo_root=tmp_path, task_id="TASK-1",
                     write_scope=("coordination/tasks/TASK-1",),
                     allowed_commands=("ls",))


@pytest.fixture
def journal():
    return ToolJournal()


# --------------------------------------------------------------------------
# scope enforcement
# --------------------------------------------------------------------------
def test_write_inside_scope_is_allowed(scope, journal):
    write = build_tools(scope, journal, ["write_file"])[0]
    result = write.invoke({"path": "coordination/tasks/TASK-1/report.md",
                           "content": "# report\n"})
    assert "wrote" in result
    assert (scope.repo_root / "coordination/tasks/TASK-1/report.md").exists()
    assert journal.writes == ["coordination/tasks/TASK-1/report.md"]


@pytest.mark.parametrize("path", [
    "ledger/H-A-001.yaml",                              # another task's record
    "coordination/tasks/TASK-2/report.md",              # a sibling task
    "../outside.md",                                    # traversal
    "coordination/tasks/TASK-1/../../../outside.md",    # traversal, disguised
    "/etc/passwd",                                      # absolute
])
def test_writes_outside_scope_are_denied(scope, journal, path):
    write = build_tools(scope, journal, ["write_file"])[0]
    result = write.invoke({"path": path, "content": "x"})
    assert result.startswith("DENIED")
    assert not (scope.repo_root / "outside.md").exists()
    assert journal.denials, "a refusal must be recorded, not just returned"


def test_symlink_out_of_the_repository_is_denied(scope, journal, tmp_path):
    outside = tmp_path.parent / "outside_target"
    outside.mkdir(exist_ok=True)
    (scope.repo_root / "coordination/tasks/TASK-1/escape").symlink_to(outside)
    write = build_tools(scope, journal, ["write_file"])[0]
    result = write.invoke({"path": "coordination/tasks/TASK-1/escape/loot.md",
                           "content": "x"})
    assert result.startswith("DENIED")
    assert not (outside / "loot.md").exists()


def test_a_task_with_no_write_scope_can_write_nothing(tmp_path, journal):
    scope = TaskScope(repo_root=tmp_path, task_id="TASK-0")
    write = build_tools(scope, journal, ["write_file"])[0]
    assert write.invoke({"path": "anything.md", "content": "x"}).startswith("DENIED")


def test_existing_artifacts_are_never_overwritten(scope, journal):
    write = build_tools(scope, journal, ["write_file"])[0]
    write.invoke({"path": "coordination/tasks/TASK-1/r.md", "content": "first"})
    second = write.invoke({"path": "coordination/tasks/TASK-1/r.md", "content": "second"})
    assert "DENIED" in second and "immutable" in second
    assert (scope.repo_root / "coordination/tasks/TASK-1/r.md").read_text() == "first"


def test_read_scope_is_enforced_when_declared(tmp_path, journal):
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge/KN-1.md").write_text("visible\n")
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets/keys.md").write_text("hidden\n")
    scope = TaskScope(repo_root=tmp_path, task_id="TASK-1",
                      read_scope=("knowledge",))
    read = build_tools(scope, journal, ["read_file"])[0]
    assert "visible" in read.invoke({"path": "knowledge/KN-1.md"})
    assert read.invoke({"path": "secrets/keys.md"}).startswith("DENIED")


def test_edit_requires_a_unique_match(scope, journal):
    target = scope.repo_root / "coordination/tasks/TASK-1/n.md"
    target.write_text("alpha\nalpha\n")
    edit = build_tools(scope, journal, ["edit_file"])[0]
    result = edit.invoke({"path": "coordination/tasks/TASK-1/n.md",
                          "old_text": "alpha", "new_text": "beta"})
    assert "ambiguous" in result or "appears 2 times" in result
    assert target.read_text() == "alpha\nalpha\n"


# --------------------------------------------------------------------------
# command execution
# --------------------------------------------------------------------------
def test_commands_outside_the_allowlist_are_denied(scope, journal):
    run = build_tools(scope, journal, ["run_command"])[0]
    result = run.invoke({"command": ["curl", "https://example.invalid"]})
    assert result.startswith("DENIED") and "curl" in result


def test_allow_listed_command_runs(scope, journal):
    run = build_tools(scope, journal, ["run_command"])[0]
    assert "exit_code: 0" in run.invoke({"command": ["ls"]})


def test_mutating_git_is_denied_even_though_git_is_allow_listed(tmp_path, journal):
    scope = TaskScope(repo_root=tmp_path, task_id="TASK-1",
                      write_scope=("x",), allowed_commands=("git",))
    run = build_tools(scope, journal, ["run_command"])[0]
    denied = run.invoke({"command": ["git", "commit", "-m", "sneak"]})
    assert denied.startswith("DENIED") and "Coordinator archival task" in denied
    assert "exit_code" in run.invoke({"command": ["git", "status"]})


def test_only_the_named_tools_exist(scope, journal):
    tools = build_tools(scope, journal, ["read_file"])
    assert [t.name for t in tools] == ["read_file"]


# --------------------------------------------------------------------------
# message translation for multi-turn tool conversations
# --------------------------------------------------------------------------
def _conversation():
    return [
        SystemMessage("CONTRACT"),
        HumanMessage("do the task"),
        AIMessage(content="reading", tool_calls=[
            {"name": "read_file", "args": {"path": "a.md"}, "id": "c1",
             "type": "tool_call"}]),
        ToolMessage(content="file body", tool_call_id="c1", name="read_file"),
    ]


def test_tool_conversation_renders_for_anthropic():
    system, turns = langchain_model.to_canonical(_conversation())
    rendered = transport.render_messages(turns, "anthropic_messages")
    assert system == "CONTRACT"
    assert rendered[1]["content"][1]["type"] == "tool_use"
    # Anthropic requires results inside a user turn.
    assert rendered[2]["role"] == "user"
    assert rendered[2]["content"][0]["tool_use_id"] == "c1"


def test_tool_conversation_renders_for_openai():
    system, turns = langchain_model.to_canonical(_conversation())
    rendered = transport.render_messages(turns, "openai_chat", system)
    assert rendered[0] == {"role": "system", "content": "CONTRACT"}
    assert rendered[2]["tool_calls"][0]["function"]["name"] == "read_file"
    # OpenAI gives results their own role.
    assert rendered[3]["role"] == "tool" and rendered[3]["tool_call_id"] == "c1"


def test_consecutive_tool_results_collapse_into_one_turn():
    messages = [
        AIMessage(content="", tool_calls=[
            {"name": "read_file", "args": {}, "id": "a", "type": "tool_call"},
            {"name": "read_file", "args": {}, "id": "b", "type": "tool_call"}]),
        ToolMessage(content="1", tool_call_id="a", name="read_file"),
        ToolMessage(content="2", tool_call_id="b", name="read_file"),
    ]
    _, turns = langchain_model.to_canonical(messages)
    assert turns[1].role == "tool_results" and len(turns[1].tool_results) == 2
    assert len(transport.render_messages(turns, "anthropic_messages")) == 2


def test_langchain_tools_translate_to_canonical_declarations(scope, journal):
    tools = build_tools(scope, journal, ["read_file", "write_file"])
    canonical = langchain_model.to_canonical_tools(tools)
    assert [t.name for t in canonical] == ["read_file", "write_file"]
    assert canonical[0].input_schema["type"] == "object"


# --------------------------------------------------------------------------
# the chat model, over canned HTTP payloads
# --------------------------------------------------------------------------
class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def scripted_opener(payloads):
    """A urlopen stand-in returning canned bodies, recording each request."""
    sent = []

    def opener(request, timeout=None):
        sent.append(json.loads(request.data.decode()))
        return _Response(json.dumps(payloads[len(sent) - 1]).encode())

    opener.sent = sent
    return opener


def anthropic_tool_use(tool, args, call_id="c1", model="claude-opus-5"):
    return {"model": model, "stop_reason": "tool_use",
            "content": [{"type": "tool_use", "id": call_id, "name": tool,
                         "input": args}],
            "usage": {"input_tokens": 10, "output_tokens": 5}}


def anthropic_text(text, model="claude-opus-5"):
    return {"model": model, "stop_reason": "end_turn",
            "content": [{"type": "text", "text": text}],
            "usage": {"input_tokens": 8, "output_tokens": 4}}


def test_chat_model_returns_tool_calls_and_usage(cfg):
    resolution = adapter.resolve(cfg, "executor-implementation",
                                 backend="anthropic", env={})
    opener = scripted_opener([anthropic_tool_use("read_file", {"path": "a.md"})])
    model = langchain_model.ResolvedChatModel(
        adapter_config=cfg, resolution=resolution,
        request_env={"ANTHROPIC_API_KEY": "test"}, opener=opener)
    reply = model.invoke([HumanMessage("hello")])
    assert reply.tool_calls[0]["name"] == "read_file"
    assert reply.usage_metadata["input_tokens"] == 10
    assert model.usage_totals() == {"input_tokens": 10, "output_tokens": 5,
                                    "requests": 1}
    assert opener.sent[0]["model"] == resolution.resolved_model_id


def test_chat_model_flags_a_backend_answering_as_another_model(cfg):
    resolution = adapter.resolve(cfg, "executor-implementation",
                                 backend="anthropic", env={})
    opener = scripted_opener([anthropic_text("hi", model="something-else")])
    model = langchain_model.ResolvedChatModel(
        adapter_config=cfg, resolution=resolution,
        request_env={"ANTHROPIC_API_KEY": "test"}, opener=opener)
    reply = model.invoke([HumanMessage("hello")])
    assert reply.response_metadata["model_matches_resolution"] is False
    assert model.model_disagreements() == ["something-else"]


# --------------------------------------------------------------------------
# the graph
# --------------------------------------------------------------------------
def _model(cfg, payloads, backend="anthropic"):
    resolution = adapter.resolve(cfg, "executor-implementation", backend=backend,
                                 env={})
    return langchain_model.ResolvedChatModel(
        adapter_config=cfg, resolution=resolution,
        request_env={"ANTHROPIC_API_KEY": "test"},
        opener=scripted_opener(payloads))


def test_graph_runs_tools_then_finishes(cfg, scope, journal):
    tools = build_tools(scope, journal, ["write_file"])
    model = _model(cfg, [
        anthropic_tool_use("write_file",
                           {"path": "coordination/tasks/TASK-1/out.md",
                            "content": "done"}),
        anthropic_text("wrote coordination/tasks/TASK-1/out.md"),
    ])
    agent = graph_module.build_agent(model, tools, max_steps=5)
    state = agent.invoke({"messages": [HumanMessage("go")], "steps": 0,
                          "stop_reason": None})
    assert graph_module.final_stop_reason(state) == "completed"
    assert state["steps"] == 2
    assert (scope.repo_root / "coordination/tasks/TASK-1/out.md").read_text() == "done"


def test_step_budget_stops_the_loop_and_says_so(cfg, scope, journal):
    tools = build_tools(scope, journal, ["read_file"])
    model = _model(cfg, [anthropic_tool_use("read_file", {"path": "ledger/H-A-001.yaml"})] * 4)
    agent = graph_module.build_agent(model, tools, max_steps=2)
    state = agent.invoke({"messages": [HumanMessage("go")], "steps": 0,
                          "stop_reason": None})
    assert graph_module.final_stop_reason(state) == graph_module.STEP_BUDGET
    assert state["steps"] == 2


def test_wall_clock_budget_stops_the_loop(cfg, scope, journal):
    # The model keeps asking for tools, so only the clock can end this run.
    ticks = iter([0.0, 100.0, 100.0])
    model = _model(cfg, [anthropic_tool_use("read_file",
                                            {"path": "ledger/H-A-001.yaml"})] * 3)
    agent = graph_module.build_agent(
        model, build_tools(scope, journal, ["read_file"]),
        max_steps=10, deadline=50.0, clock=lambda: next(ticks))
    state = agent.invoke({"messages": [HumanMessage("go")], "steps": 0,
                          "stop_reason": None})
    assert graph_module.final_stop_reason(state) == graph_module.CLOCK_BUDGET


def test_checkpointer_persists_state_for_resuming(cfg, scope, journal, tmp_path):
    checkpointer, connection = graph_module.open_checkpointer(tmp_path / "cp.sqlite")
    try:
        model = _model(cfg, [anthropic_text("done")])
        agent = graph_module.build_agent(model, [], max_steps=5,
                                         checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "TASK-1"}}
        agent.invoke({"messages": [HumanMessage("go")], "steps": 0,
                      "stop_reason": None}, config=config)
        restored = agent.get_state(config)
        assert restored.values["steps"] == 1
        assert any(m.content == "done" for m in restored.values["messages"])
    finally:
        connection.close()
    assert (tmp_path / "cp.sqlite").exists()


# --------------------------------------------------------------------------
# the runner
# --------------------------------------------------------------------------
def _mini_repo(tmp_path):
    (tmp_path / "agents").mkdir()
    (tmp_path / "AGENTS.md").write_text("# contract\n")
    (tmp_path / "agents/executor.md").write_text("# executor\n")
    (tmp_path / "coordination/tasks/TASK-9").mkdir(parents=True)
    return tmp_path


def _handoff(tmp_path):
    return {"handoff": {
        "id": "TASK-9", "from": "coordinator", "to": "executor",
        "objective": "Measure the thing.",
        "inputs": [], "constraints": [], "deliverables": ["report.md"],
        "artifact_paths": ["coordination/tasks/TASK-9/report.md"],
        "completion_gate": ["report exists"],
        "inference": {"policy": "executor-terra", "fallback_allowed": False},
        "budget": {"wall_clock_seconds": 600, "memory_gb": 2, "maximum_runs": 1}}}


def test_runner_refuses_a_role_this_runtime_cannot_host(cfg, tmp_path):
    handoff = _handoff(tmp_path)
    handoff["handoff"]["to"] = "idea-generator"
    handoff["handoff"]["inference"]["policy"] = "research-deep"
    with pytest.raises(runner_module.UnsupportedRole, match="web_search"):
        runner_module.run_task(handoff, config=cfg, repo_root=_mini_repo(tmp_path))


def test_runner_derives_write_scope_from_the_declared_artifact_paths(tmp_path):
    task = runner_module.load_task(_handoff(tmp_path))
    scope = runner_module.task_scope(task, repo_root=tmp_path, api_config={})
    assert scope.write_scope == ("coordination/tasks/TASK-9",)


def test_runner_executes_a_task_and_records_an_immutable_receipt(cfg, tmp_path,
                                                                 monkeypatch):
    repo = _mini_repo(tmp_path)
    opener = scripted_opener([
        anthropic_tool_use("write_file",
                           {"path": "coordination/tasks/TASK-9/report.md",
                            "content": "# findings\n"}),
        anthropic_text("wrote coordination/tasks/TASK-9/report.md"),
    ])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    run = runner_module.run_task(_handoff(tmp_path), config=cfg, repo_root=repo,
                                 backend="anthropic", opener=opener)

    assert run.completed and run.role == "executor"
    assert run.files_written == ["coordination/tasks/TASK-9/report.md"]
    assert (repo / "coordination/tasks/TASK-9/report.md").read_text() == "# findings\n"
    assert run.resolution.requested_policy == "executor-terra"    # legacy alias
    assert run.usage["requests"] == 2

    written = runner_module.write_artifacts(run, tmp_path / "out", config=cfg)
    receipt = json.loads(written["receipt"].read_text())["inference_receipt"]
    assert receipt["runtime"] == "api_direct"
    assert receipt["execution"]["stop_reason"] == "completed"
    assert receipt["execution"]["files_written"] == run.files_written
    assert receipt["resolution"]["resolved_model_id"]
    with pytest.raises(FileExistsError):
        runner_module.write_artifacts(run, tmp_path / "out", config=cfg)


def test_runner_records_denied_writes_rather_than_failing_silently(cfg, tmp_path,
                                                                  monkeypatch):
    repo = _mini_repo(tmp_path)
    opener = scripted_opener([
        anthropic_tool_use("write_file", {"path": "ledger/DEC-1.yaml",
                                          "content": "official!"}),
        anthropic_text("could not write there"),
    ])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    run = runner_module.run_task(_handoff(tmp_path), config=cfg, repo_root=repo,
                                 backend="anthropic", opener=opener)
    assert run.files_written == []
    assert not (repo / "ledger").exists()
    assert any(e["denied"] for e in run.journal if "denied" in e)

    written = runner_module.write_artifacts(run, tmp_path / "out", config=cfg)
    receipt = json.loads(written["receipt"].read_text())["inference_receipt"]
    assert receipt["execution"]["denied_tool_calls"], "a denial must reach the receipt"


def test_task_brief_states_the_limits_that_are_actually_enforced(tmp_path):
    task = runner_module.load_task(_handoff(tmp_path))
    scope = runner_module.task_scope(
        task, repo_root=tmp_path,
        api_config={"command_allowlist": ["python3"]})
    brief = runner_module.task_brief(task, scope, ["write_file"])
    assert "coordination/tasks/TASK-9" in brief
    assert "python3" in brief
    assert "immutable" in brief


def test_every_api_direct_tool_name_has_an_implementation(scope, journal):
    """roles.yaml must never promise a tool the runtime cannot build."""
    roles_doc = role_registry.load_roles()
    for role in roles_doc["roles"]:
        names = role_registry.expected_tools(roles_doc, role, "api_direct")
        if names is not None:
            assert len(build_tools(scope, journal, names)) == len(names)


def test_model_supplied_string_numeric_args_do_not_crash_the_tool_loop(scope,
                                                                        journal):
    """Regression: glm-5.2 (zai backend, 2026-08-22) passed a string `limit`
    to search_files and the tool loop crashed with TypeError
    ('>=' not supported between instances of 'int' and 'str'). Per this
    module's contract a malformed tool call degrades to the declared
    default or an ERROR string the model can correct -- never a crash."""
    from orchestration.agent.tools import _as_int

    search = build_tools(scope, journal, ["search_files"])[0]
    # string numeric args are coerced; no exception escapes
    assert isinstance(search.invoke({"regex": "hypothesis", "limit": "3"}),
                      str)
    # an uncoercible value falls back to the default, also without raising
    assert isinstance(search.invoke({"regex": "hypothesis", "limit": "many"}),
                      str)
    listing = build_tools(scope, journal, ["list_files"])[0]
    assert isinstance(listing.invoke({"pattern": "ledger/*", "limit": "2"}),
                      str)
    reading = build_tools(scope, journal, ["read_file"])[0]
    out = reading.invoke({"path": "ledger/H-A-001.yaml", "start_line": "1",
                          "max_lines": "2"})
    assert out.startswith("1\t")
    runner = build_tools(scope, journal, ["run_command"])[0]
    assert "ERROR" in runner.invoke({"command": "not-a-list"})
    assert _as_int("50", 100) == 50
    assert _as_int("many", 100) == 100
    assert _as_int(True, 100) == 100


def test_model_supplied_string_json_array_command_is_coerced(scope, journal):
    """Regression: glm-5.2 (zai backend, 2026-08-22) sent run_command's
    `command` as a JSON array *serialized as a string* ('["python3",
    "--version"]'). The old isinstance check rejected every such call with
    an unjournaled ERROR, so a validator burned its step budget on retries
    and then misattributed the failure to non-functional tooling. The
    observed shape is now coerced (and the coercion journaled); a bare shell
    string is never split, so the allow-list on command[0] stays the
    authority on what may run."""
    runner = build_tools(scope, journal, ["run_command"])[0]
    assert "ERROR" not in runner.invoke({"command": '["ls"]'})
    assert any(e.get("tool") == "run_command"
               and e.get("coerced_from") == "string"
               for e in journal.entries)
    # a bare shell string is not shell-split
    assert "ERROR" in runner.invoke({"command": "ls -la"})
    # non-list JSON and non-string elements are rejected, not coerced
    assert "ERROR" in runner.invoke({"command": '{"a": 1}'})
    assert "ERROR" in runner.invoke({"command": '["ls", 1]'})
    # a correctly-typed list runs without a coercion note
    journal.entries.clear()
    assert "ERROR" not in runner.invoke({"command": ["ls"]})
    assert not any(e.get("coerced_from") for e in journal.entries)
