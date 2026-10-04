"""Task context projections do not scan or mutate the research corpus."""
from copy import deepcopy
from pathlib import Path

import pytest

from orchestration import task_context as context


def task(**fields):
    return context.load_task({"handoff": {
        "id": "TASK-test", "to": "executor",
        "inputs": ["experiments/example/specification.yaml", "EXP-EXAMPLE",
                   "Read the prior result", "https://example.invalid/paper",
                   {"path": "src/helper.py"}],
        "artifact_paths": ["experiments/example/runs/report.json"],
        **fields,
    }})


def test_derives_context_and_scope_without_scanning_or_mutating(tmp_path, monkeypatch):
    original = task()
    before = deepcopy(original)
    def no_scan(*args, **kwargs):
        raise AssertionError("context derivation must not scan the repository")
    monkeypatch.setattr(Path, "rglob", no_scan)
    monkeypatch.setattr(Path, "glob", no_scan)
    result = context.prepare_task(original, repo_root=tmp_path)
    assert original == before
    assert result["context_paths"] == ["experiments/example/specification.yaml",
        "src/helper.py", "docs/agent-runtime-core.md", "agents/executor.md"]
    assert result["read_scope"] == result["context_paths"] + ["experiments/example/runs"]
    assert result["_read_scope_derived"] is True


def test_nested_scopes_are_preserved_and_top_level_scopes_win(tmp_path):
    original = task(read_scope=["experiments/example"], write_scope=["outputs"])
    projected = context.prepare_task(original, repo_root=tmp_path)
    assert projected["read_scope"] == ["experiments/example"]
    assert projected["write_scope"] == ["outputs"]
    assert projected["_read_scope_derived"] is False
    original["read_scope"] = ["."]
    assert context.prepare_task(original, repo_root=tmp_path)["read_scope"] == ["."]


def test_load_preserves_envelope_metadata_without_top_level_id():
    loaded = context.load_task({"read_scope": ["src"], "write_scope": ["out"],
        "handoff": {"id": "TASK-test", "to": "executor"}})
    assert loaded["read_scope"] == ["src"]
    assert loaded["write_scope"] == ["out"]


def test_input_cannot_relabel_an_explicit_scope_as_derived(tmp_path):
    loaded = context.load_task({"_read_scope_derived": True, "read_scope": ["src"],
        "handoff": {"id": "test", "to": "executor", "inputs": ["ledger/record.yaml"]}})
    result = context.prepare_task(loaded, repo_root=tmp_path)
    assert result["read_scope"] == ["src"]
    assert result["_read_scope_derived"] is False


def test_source_handoff_in_context_without_inlining_file_contents(tmp_path):
    source = tmp_path / "task.yaml"
    source.write_text("handoff:\n  id: TASK-test\n  to: executor\n")
    result = context.prepare_task(context.load_task(source), repo_root=tmp_path)
    assert "task.yaml" in result["context_paths"]


def test_extra_dependency_does_not_widen_explicit_read_scope(tmp_path):
    with pytest.raises(ValueError, match="outside the declared read_scope"):
        context.prepare_task(task(read_scope=["experiments/example"]),
            repo_root=tmp_path, extra_context=("knowledge/unrelated.md",))
    first = context.prepare_task(task(), repo_root=tmp_path)
    second = context.prepare_task(first, repo_root=tmp_path, extra_context=("src/dependency.py",))
    assert "src/dependency.py" in second["read_scope"]


@pytest.mark.parametrize("path", ["../outside", "/tmp/input", "src/*", "src/../outside",
                                      ".git/config", "src\n/other", ""])
def test_explicit_context_rejects_nonliteral_or_external_paths(tmp_path, path):
    with pytest.raises(ValueError):
        context.prepare_task(task(context_paths=[path]), repo_root=tmp_path)
