"""Regression tests for token-efficient subagent context construction."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("langgraph", reason="api_direct runtime needs requirements-agent.txt")

from orchestration import role_registry  # noqa: E402
from orchestration.agent import runner as runner_module  # noqa: E402
from orchestration.agent import tools as file_tools  # noqa: E402
from orchestration.agent.tools import TaskScope, ToolJournal, build_tools  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def test_executor_system_prompt_uses_compact_core_not_full_agents():
    roles = role_registry.load_roles()
    prompt = runner_module.system_prompt("executor", roles, repo_root=REPO)
    core = (REPO / "docs/agent-runtime-core.md").read_text()
    executor = (REPO / "agents/executor.md").read_text()
    full = (REPO / "AGENTS.md").read_text()

    assert core in prompt
    assert executor in prompt
    assert len(prompt) == len(core) + len(executor) + len("\n\n---\n\n")
    assert len(prompt) < len(full)
    assert "Goal closure quorum — SUSPENDED" not in prompt


def test_context_paths_are_explicit_and_do_not_scan_state():
    task = {
        "id": "TASK-X",
        "role": "executor",
        "context_paths": [
            "experiments/EXP-X/specification.yaml",
            "ledger/handoffs/TASK-X.yaml",
        ],
        "handoff": {"objective": "run frozen protocol"},
    }
    assert runner_module._context_paths(task) == [
        "experiments/EXP-X/specification.yaml",
        "ledger/handoffs/TASK-X.yaml",
    ]


def test_executor_brief_forbids_full_corpus_scan():
    task = {
        "id": "TASK-X",
        "role": "executor",
        "context_paths": ["experiments/EXP-X/specification.yaml"],
        "handoff": {
            "objective": "execute EXP-X",
            "inputs": ["experiments/EXP-X/specification.yaml"],
            "artifact_paths": ["experiments/EXP-X/execution-report.yaml"],
        },
    }
    scope = TaskScope(
        repo_root=REPO,
        task_id="TASK-X",
        write_scope=("experiments/EXP-X",),
    )
    brief = runner_module.task_brief(task, scope, ["read_file", "run_command"])
    assert "Explicit context files" in brief
    assert "experiments/EXP-X/specification.yaml" in brief
    assert "Do not scan the full ledger, knowledge corpus, or AGENTS.md" in brief


def test_scoped_default_search_never_walks_unrelated_corpus(tmp_path, monkeypatch):
    (tmp_path / "active").mkdir()
    (tmp_path / "active/code.py").write_text("needle = 1\n")
    (tmp_path / "archive").mkdir()
    (tmp_path / "archive/record.md").write_text("needle from another task\n")
    scope = TaskScope(repo_root=tmp_path, task_id="test", read_scope=("active",))
    walked = []
    original = file_tools.os.walk
    def walk(root, **kwargs):
        walked.append(Path(root))
        assert Path(root) == tmp_path / "active"
        yield from original(root, **kwargs)
    monkeypatch.setattr(file_tools.os, "walk", walk)
    journal = ToolJournal()
    result = build_tools(scope, journal, ["search_files"])[0].invoke({"regex": "needle"})
    assert "active/code.py" in result and "archive" not in result
    assert walked == [tmp_path / "active"]
    assert journal.entries[-1]["files_scanned"] == 1


def test_default_discovery_is_narrow_even_with_a_broad_declared_scope(tmp_path):
    (tmp_path / "current.md").write_text("needle current")
    (tmp_path / "other.md").write_text("needle other")
    scope = TaskScope(repo_root=tmp_path, task_id="test", read_scope=(".",),
                      discovery_scope=("current.md",))
    tool = build_tools(scope, ToolJournal(), ["search_files"])[0]
    default = tool.invoke({"regex": "needle"})
    assert "current.md" in default and "other.md" not in default
    explicit = tool.invoke({"regex": "needle", "pattern": "other.md"})
    assert "other.md" in explicit


def test_recursive_pattern_includes_top_level_and_nested_files(tmp_path):
    (tmp_path / "a.py").write_text("needle")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested/b.py").write_text("needle")
    (tmp_path / "nested/c.md").write_text("needle")
    tool = build_tools(TaskScope(tmp_path, "test"), ToolJournal(), ["list_files"])[0]
    assert set(tool.invoke({"pattern": "**/*.py"}).splitlines()) == {"a.py", "nested/b.py"}
    assert tool.invoke({"pattern": "*.py"}) == "a.py"


def test_model_cannot_raise_list_or_search_result_caps(tmp_path):
    for index in range(230):
        (tmp_path / f"file-{index:03d}.txt").write_text("needle\n")
    scope = TaskScope(tmp_path, "test")
    journal = ToolJournal()
    listing, searching = build_tools(scope, journal, ["list_files", "search_files"])
    listing.invoke({"limit": 1000000})
    assert journal.entries[-1]["matches"] == 200
    assert journal.entries[-1]["partial"] is True
    searching.invoke({"regex": "needle", "limit": 1000000})
    assert journal.entries[-1]["matches"] == 100
    assert journal.entries[-1]["partial"] is True


def test_no_match_after_scan_cap_is_explicitly_partial(tmp_path):
    for index in range(6):
        (tmp_path / f"{index}.md").write_text("not the requested word")
    (tmp_path / "z.md").write_text("needle")
    scope = TaskScope(tmp_path, "test", max_search_files=3)
    journal = ToolJournal()
    result = build_tools(scope, journal, ["search_files"])[0].invoke({"regex": "needle"})
    assert "partial search" in result
    assert journal.entries[-1]["files_scanned"] == 3
    assert journal.entries[-1]["matches"] == 0


def test_large_file_search_does_not_read_entire_file(tmp_path):
    (tmp_path / "data.txt").write_text("a" * 4000 + "needle")
    scope = TaskScope(tmp_path, "test", max_search_file_bytes=500)
    journal = ToolJournal()
    result = build_tools(scope, journal, ["search_files"])[0].invoke({"regex": "needle"})
    assert "partial search" in result
    assert journal.entries[-1]["bytes_read"] <= 501


def test_byte_capped_unicode_pages_preserve_all_content(tmp_path):
    body = "α🙂" * 500
    (tmp_path / "long.txt").write_text(body + "\nsecond line\n")
    scope = TaskScope(tmp_path, "test", max_read_bytes=512)
    journal = ToolJournal()
    tool = build_tools(scope, journal, ["read_file"])[0]
    line, column = 1, 1
    recovered = []
    for _ in range(30):
        result = tool.invoke({"path": "long.txt", "start_line": line,
                              "start_column": column, "max_lines": 999999})
        assert len(result.encode("utf-8")) <= 512
        recovered.extend(s.split("\t", 1)[1] for s in result.splitlines() if "\t" in s)
        cursor = journal.entries[-1]["continuation"]
        if cursor is None:
            break
        assert tuple(cursor) > (line, column)
        line, column = cursor
    else:
        pytest.fail("bounded read pages did not finish")
    assert "".join(recovered) == body + "second line"


def test_read_line_limit_is_a_cap_and_cursor_can_resume(tmp_path):
    (tmp_path / "lines.txt").write_text("one\ntwo\nthree\nfour\n")
    scope = TaskScope(tmp_path, "test", max_read_lines=2)
    journal = ToolJournal()
    tool = build_tools(scope, journal, ["read_file"])[0]
    first = tool.invoke({"path": "lines.txt", "max_lines": 100000})
    assert "1\tone" in first and "3\tthree" not in first
    assert journal.entries[-1]["continuation"] == (3, 1)
    second = tool.invoke({"path": "lines.txt", "start_line": 3})
    assert "3\tthree" in second and "4\tfour" in second


def test_explicit_glob_cannot_read_through_an_external_symlink(tmp_path):
    (tmp_path / "escape").symlink_to(tmp_path.parent, target_is_directory=True)
    scope = TaskScope(tmp_path, "test")
    result = build_tools(scope, ToolJournal(), ["list_files"])[0].invoke({"pattern": "escape/*"})
    assert result.startswith("DENIED:")


def test_runner_receives_configured_limits_and_context_defaults(tmp_path):
    task = runner_module.load_task({"to": "executor", "id": "test",
        "inputs": ["src/code.py"], "artifact_paths": ["out/report.md"]})
    scope = runner_module.task_scope(task, repo_root=tmp_path,
        api_config={"retrieval_limits": {"max_search_results": 12}})
    assert scope.max_search_results == 12
    assert "src/code.py" in scope.read_scope
    assert "src/code.py" in scope.discovery_scope
    assert "." not in scope.read_scope


@pytest.mark.parametrize("limits", [{"unknown": 4}, {"max_search_files": 0},
                                    {"max_output_bytes": True}, {"max_read_bytes": 40}])
def test_invalid_runtime_limits_fail_before_launch(tmp_path, limits):
    task = runner_module.load_task({"to": "executor", "id": "test"})
    with pytest.raises(ValueError, match="invalid retrieval limit"):
        runner_module.task_scope(task, repo_root=tmp_path, api_config={"retrieval_limits": limits})
