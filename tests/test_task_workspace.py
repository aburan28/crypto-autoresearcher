"""Exercise real sparse Git worktrees using small, local fixture repositories."""
import json
from pathlib import Path
import subprocess

import pytest

from orchestration import task_context, task_workspace as workspace


def git(repo, *args):
    return subprocess.check_output(["git", "-c", "core.hooksPath=/dev/null", "-C", str(repo),
        "-c", "user.name=Context Test", "-c", "user.email=context@example.invalid", *args], text=True).strip()


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init", "-q")
    files = {
        "docs/agent-runtime-core.md": "core", "agents/executor.md": "executor",
        "experiments/chosen/specification.yaml": "frozen: true\n",
        "experiments/other/report.md": "irrelevant",
        "knowledge/one.md": "dependency", "knowledge/two.md": "irrelevant",
        "ledger/handoffs/one.yaml": "handoff", "ledger/handoffs/two.yaml": "irrelevant",
        "src/helper.py": "print('helper')", "AGENTS.md": "contract",
    }
    for path, content in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "first")
    (repo / "experiments/chosen/specification.yaml").write_text("frozen: true\nversion: 2\n")
    git(repo, "add", "experiments/chosen/specification.yaml")
    git(repo, "commit", "-qm", "second")
    return repo


def task():
    return task_context.load_task({"id": "TASK-example", "role": "executor",
        "context_paths": ["experiments/chosen/specification.yaml", "ledger/handoffs/one.yaml"],
        "read_scope": ["experiments/chosen", "ledger/handoffs/one.yaml", "knowledge"],
        "write_scope": ["experiments/chosen/runs"], "handoff": {"inputs": []}})


def test_sparse_workspace_omits_siblings_keeps_history_and_source(repo, tmp_path):
    destination = tmp_path / "execution"
    source_head = git(repo, "rev-parse", "HEAD")
    # Unrelated in-progress work is preserved and does not block preparation.
    (repo / "knowledge/two.md").write_text("uncommitted unrelated work")
    (repo / "knowledge/draft.md").write_text("untracked unrelated work")
    before = git(repo, "status", "--porcelain")
    plan = workspace.prepare_workspace(task(), repo_root=repo, destination=destination)
    assert plan["source_commit"] == source_head
    assert (destination / "experiments/chosen/specification.yaml").read_text().endswith("version: 2\n")
    assert (destination / "ledger/handoffs/one.yaml").is_file()
    assert not (destination / "ledger/handoffs/two.yaml").exists()
    assert not (destination / "experiments/other").exists()
    assert not (destination / "knowledge").exists()
    assert git(destination, "rev-list", "--count", "HEAD") == "2"
    assert git(destination, "show", "HEAD~1:experiments/chosen/specification.yaml") == "frozen: true"
    assert git(repo, "status", "--porcelain") == before
    assert (repo / "experiments/other/report.md").is_file()
    assert git(repo, "rev-parse", "HEAD") == source_head
    assert json.loads(workspace._metadata_path(destination).read_text()) == plan


def test_expand_only_materializes_requested_allowed_dependency(repo, tmp_path):
    destination = tmp_path / "execution"
    workspace.prepare_workspace(task(), repo_root=repo, destination=destination)
    plan = workspace.expand_workspace(destination, ["knowledge/one.md"])
    assert (destination / "knowledge/one.md").read_text() == "dependency"
    assert not (destination / "knowledge/two.md").exists()
    assert len(plan["expansions"]) == 1
    assert workspace.expand_workspace(destination, ["knowledge/one.md"]) == plan
    with pytest.raises(workspace.WorkspaceError, match="outside the declared"):
        workspace.expand_workspace(destination, ["experiments/other/report.md"])


def test_git_environment_cannot_redirect_workspace_operations(repo, tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "wrong-git-directory"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path / "wrong-worktree"))
    destination = tmp_path / "execution"
    plan = workspace.prepare_workspace(task(), repo_root=repo, destination=destination)
    assert plan["source_repository"] == str(repo)
    assert (destination / "experiments/chosen/specification.yaml").is_file()


def test_changed_head_refuses_expansion(repo, tmp_path):
    destination = tmp_path / "execution"
    workspace.prepare_workspace(task(), repo_root=repo, destination=destination)
    git(destination, "checkout", "-q", "HEAD~1")
    with pytest.raises(workspace.WorkspaceError, match="HEAD changed"):
        workspace.expand_workspace(destination, ["knowledge/one.md"])


@pytest.mark.parametrize("change", ["modified", "untracked", "staged"])
def test_dirty_selected_paths_are_refused_before_workspace_creation(repo, tmp_path, change):
    path = repo / "src/helper.py"
    if change == "untracked":
        path = repo / "src/new.py"
    path.write_text("new content")
    if change == "staged":
        git(repo, "add", "src/helper.py")
    destination = tmp_path / "execution"
    with pytest.raises(workspace.WorkspaceError, match="uncommitted changes"):
        workspace.prepare_workspace(task(), repo_root=repo, destination=destination)
    assert not destination.exists()


def test_missing_dependency_refuses_instead_of_silently_omitting_it(repo, tmp_path):
    source = task()
    source["context_paths"].append("missing/input.dat")
    with pytest.raises(workspace.WorkspaceError, match="absent from commit"):
        workspace.prepare_workspace(source, repo_root=repo, destination=tmp_path / "execution")


def test_review_task_cannot_accidentally_receive_sparse_coverage(repo):
    source = task()
    source["role"] = "validator"
    with pytest.raises(workspace.WorkspaceError, match="only for execution tasks"):
        workspace.workspace_plan(source, repo_root=repo)


def test_preexisting_destination_is_never_modified(repo, tmp_path):
    destination = tmp_path / "execution"
    destination.mkdir()
    (destination / "keep").write_text("data")
    with pytest.raises(workspace.WorkspaceError, match="already exists"):
        workspace.prepare_workspace(task(), repo_root=repo, destination=destination)
    assert (destination / "keep").read_text() == "data"


def test_shallow_source_is_refused(repo, tmp_path):
    shallow = tmp_path / "shallow"
    git(tmp_path, "clone", "-q", "--depth=1", repo.as_uri(), str(shallow))
    with pytest.raises(workspace.WorkspaceError, match="complete history"):
        workspace.workspace_plan(task(), repo_root=shallow)


def test_plan_cli_does_not_create_a_worktree_or_need_agent_dependencies(repo, tmp_path, capsys):
    source = tmp_path / "task.json"
    source.write_text(json.dumps(task()))
    before = git(repo, "worktree", "list", "--porcelain")
    assert workspace.main(["plan", "--repo", str(repo), "--task", str(source)]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["source_commit"] == git(repo, "rev-parse", "HEAD")
    assert git(repo, "worktree", "list", "--porcelain") == before
