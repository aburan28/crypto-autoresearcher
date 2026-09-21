"""Optional sparse execution worktrees, preserving complete Git history.

Preparation is explicit and has no model, dispatch, or scientific-state side
effects. Keep archive and repository-wide checks in the complete checkout.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from . import task_context

# Shared executable dependencies, not the research corpus. Optional paths
# absent from a repository snapshot are harmless; task-declared inputs are not.
SHARED_PATHS = (
    "orchestration", "src", "tools", "pyproject.toml", "AGENTS.md", "CLAUDE.md",
    ".gitignore", ".gitattributes", ".python-version", "Makefile",
    "requirements.txt", "requirements-agent.txt", "requirements-dev.txt",
    ".claude/agents", ".codex/agents", ".opencode/agent",
)
METADATA = "harness-context.json"


class WorkspaceError(ValueError):
    pass


def _git(repo: Path, *args: str, stdin: str | None = None) -> str:
    environment = {k: v for k, v in os.environ.items() if k not in {
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX"}}
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=stdin, capture_output=True, text=True, check=False,
        env={**environment, "GIT_TERMINAL_PROMPT": "0"})
    if result.returncode:
        raise WorkspaceError(f"git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout


def _present(repo: Path, revision: str, path: str) -> bool:
    return bool(_git(repo, "ls-tree", "--name-only", revision, "--", path).strip())


def _literal_patterns(paths: list[str]) -> str:
    # Non-cone selection avoids materializing thousands of sibling handoffs
    # just to include one file. Inputs are literal paths, never Git patterns.
    return "".join("/" + p.replace("]", "\\]") + "\n" for p in paths)


def _metadata_path(workspace: Path) -> Path:
    path = Path(_git(workspace, "rev-parse", "--git-path", METADATA).strip())
    return path if path.is_absolute() else workspace / path


def load_workspace(workspace: Path) -> dict[str, Any] | None:
    """Read metadata for our linked worktrees; ordinary checkouts return None."""
    if not (workspace / ".git").is_file():
        return None
    metadata = _metadata_path(workspace)
    if not metadata.exists():
        return None
    plan = json.loads(metadata.read_text(encoding="utf-8"))
    if (not isinstance(plan, dict) or plan.get("schema") != "task-workspace-v1"
            or Path(plan.get("workspace", "")).resolve() != workspace.resolve()):
        raise WorkspaceError("workspace context metadata does not match this checkout")
    required = ("source_repository", "source_commit", "task_id", "context_paths",
                "read_scope", "write_scope", "selected_paths", "expansions")
    if any(key not in plan for key in required):
        raise WorkspaceError("workspace context metadata is incomplete")
    if not Path(plan["source_repository"]).is_dir():
        raise WorkspaceError("the workspace's full source repository is unavailable")
    if _git(workspace, "rev-parse", "HEAD").strip() != plan["source_commit"]:
        raise WorkspaceError("workspace HEAD changed; prepare a new workspace for the new snapshot")
    return plan


def workspace_plan(task: dict[str, Any], *, repo_root: Path,
                   revision: str = "HEAD") -> dict[str, Any]:
    repo_root = repo_root.resolve()
    if Path(_git(repo_root, "rev-parse", "--show-toplevel").strip()).resolve() != repo_root:
        raise WorkspaceError("repo_root must be the repository's top-level directory")
    if _git(repo_root, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise WorkspaceError("sparse workspaces require a source repository with complete history")
    commit = _git(repo_root, "rev-parse", "--verify", "--end-of-options",
                  f"{revision}^{{commit}}").strip()
    prepared = task_context.prepare_task(task, repo_root=repo_root)
    # Repository-wide roles need a complete view. Opt-in sparsity is for
    # executors only; it never changes review coverage or archive validation.
    if prepared.get("role") not in ("executor", "executor-mechanical") or prepared.get("archive"):
        raise WorkspaceError("sparse workspaces are supported only for execution tasks")
    extra = task_context.paths(
        prepared.get("workspace_paths", prepared["handoff"].get("workspace_paths")),
        "workspace_paths")
    required = list(dict.fromkeys(prepared["context_paths"] + extra))
    for path in required:
        if path == ".":
            raise WorkspaceError("a sparse workspace needs specific context paths, not '.'")
        if not _present(repo_root, commit, path):
            raise WorkspaceError(f"required context path {path!r} is absent from commit {commit}")
    shared = [p for p in SHARED_PATHS if _present(repo_root, commit, p)]
    selected = list(dict.fromkeys(required + prepared["write_scope"] + shared))
    if "." in selected:
        raise WorkspaceError("sparse execution needs a write_scope below the repository root")
    # A sparse worktree starts at a commit. Never silently drop dirty or
    # untracked inputs/outputs from the source checkout when doing so.
    dirty = _git(repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                 "--", *(f":(literal){p}" for p in selected))
    if dirty:
        raise WorkspaceError("selected workspace paths contain uncommitted changes; "
                             "use the current checkout or a committed snapshot")
    return {
        "schema": "task-workspace-v1", **task_context.context_manifest(prepared),
        "source_repository": str(repo_root), "source_commit": commit,
        "shared_paths": shared, "selected_paths": selected,
        "history": "complete", "expansions": [],
    }


def prepare_workspace(task: dict[str, Any], *, repo_root: Path,
                      destination: Path, revision: str = "HEAD") -> dict[str, Any]:
    destination = destination.resolve()
    if destination.exists():
        raise WorkspaceError(f"workspace destination already exists: {destination}")
    plan = workspace_plan(task, repo_root=repo_root, revision=revision)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _git(repo_root, "worktree", "add", "--detach", "--no-checkout",
         str(destination), plan["source_commit"])
    # Keep a partially prepared worktree on failure; do not destroy evidence
    # or attempt a second launch with different checkout semantics.
    try:
        _git(destination, "sparse-checkout", "set", "--no-cone", "--stdin",
             stdin=_literal_patterns(plan["selected_paths"]))
        # --no-checkout leaves an empty index on some supported Git versions.
        _git(destination, "read-tree", "-mu", "HEAD")
        plan["workspace"] = str(destination)
        with _metadata_path(destination).open("x", encoding="utf-8") as handle:
            json.dump(plan, handle, indent=2)
            handle.write("\n")
    except (WorkspaceError, OSError) as exc:
        raise WorkspaceError(f"workspace preparation failed; retained {destination}: {exc}") from exc
    return plan


def expand_workspace(workspace: Path, paths: list[str]) -> dict[str, Any]:
    """Materialize a known dependency already inside the declared read scope."""
    metadata = _metadata_path(workspace)
    plan = load_workspace(workspace)
    if plan is None:
        raise WorkspaceError("this checkout is not a prepared task workspace")
    requested = task_context.paths(paths, "paths")
    for path in requested:
        if path == "." or not task_context.within(path, plan["read_scope"]):
            raise WorkspaceError(f"dependency {path!r} is outside the declared read_scope")
        if not _present(workspace, plan["source_commit"], path):
            raise WorkspaceError(f"dependency {path!r} is absent from the workspace snapshot")
    added = [p for p in requested if not task_context.within(p, plan["selected_paths"])]
    if added:
        _git(workspace, "sparse-checkout", "add", "--stdin", stdin=_literal_patterns(added))
        plan["selected_paths"] += added
        plan["expansions"].append({"paths": added, "at": datetime.now(timezone.utc).isoformat()})
        # Operational workspace metadata, not an immutable research record.
        metadata.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "prepare"):
        p = sub.add_parser(command)
        p.add_argument("--repo", type=Path, default=Path.cwd())
        p.add_argument("--task", required=True)
        p.add_argument("--revision", default="HEAD")
        p.add_argument("--context-path", action="append", default=[])
        if command == "prepare":
            p.add_argument("--destination", type=Path, required=True)
    p = sub.add_parser("expand")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--path", action="append", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "expand":
            result = expand_workspace(args.workspace, args.path)
        else:
            task = task_context.prepare_task(task_context.load_task(args.task),
                repo_root=args.repo, extra_context=tuple(args.context_path))
            if args.command == "plan":
                result = workspace_plan(task, repo_root=args.repo, revision=args.revision)
            else:
                result = prepare_workspace(task, repo_root=args.repo,
                    destination=args.destination, revision=args.revision)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
