"""Derive a small task context without scanning the ledger or changing records.

This module has no agent/backend dependency; native runtimes and workspace
preparation use the same projection as api_direct.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from . import role_registry

RUNTIME_CORE = "docs/agent-runtime-core.md"


def load_task(source: str | Path | dict[str, Any]) -> dict[str, Any]:
    """Accept a queue task, a handoff envelope, or a bare handoff."""
    source_path = None
    if isinstance(source, (str, Path)):
        source_path = str(Path(source).resolve())
        text = Path(source).read_text(encoding="utf-8")
        source = (json.loads(text) if str(source).endswith(".json")
                  else yaml.safe_load(text))
    if not isinstance(source, dict):
        raise ValueError("task source must be a mapping")
    task = copy.deepcopy(source if "handoff" in source else {"handoff": source})
    # These fields describe our in-memory projection, never input authority.
    task.pop("_read_scope_derived", None)
    task.pop("_source_path", None)
    handoff = task["handoff"]
    if not isinstance(handoff, dict):
        raise ValueError("task.handoff must be a mapping")
    task.setdefault("id", handoff.get("id"))
    task.setdefault("role", handoff.get("to"))
    if source_path:
        task["_source_path"] = source_path
    return task


def paths(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be a list of repository-relative paths")
    return list(dict.fromkeys(normalize_path(p, field) for p in value))


def normalize_path(value: Any, field: str = "path") -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{field} contains an empty or non-text path")
    path = PurePosixPath(value)
    if (path.is_absolute() or ".." in path.parts
            or any(c in value for c in "\x00\r\n\\*?[:")
            or ".git" in path.parts):
        raise ValueError(f"{field} must contain literal repository-relative paths: {value!r}")
    return path.as_posix()


def within(path: str, scopes: list[str] | tuple[str, ...]) -> bool:
    return any(PurePosixPath(path).is_relative_to(PurePosixPath(s)) for s in scopes)


def _field(task: dict[str, Any], name: str) -> Any:
    return task[name] if name in task else task["handoff"].get(name)


def _input_paths(task: dict[str, Any], repo_root: Path) -> list[str]:
    """Recognize literal inputs, never guess a path from an experiment ID.

    Descriptive strings and citations remain in the handoff. Structured
    {path: ...} inputs are unambiguous and are validated even when absent.
    """
    inputs = task["handoff"].get("inputs") or []
    if isinstance(inputs, str):
        inputs = [inputs]
    result = []
    for item in inputs:
        if isinstance(item, dict) and "path" in item:
            result.append(normalize_path(item["path"], "inputs.path"))
        elif isinstance(item, str) and "://" not in item:
            try:
                path = normalize_path(item, "inputs")
            except ValueError:
                continue
            # Unknown prose is not a missing file. Exact existing paths and
            # whitespace-free paths with a directory component are pointers.
            if (repo_root / path).exists() or ("/" in path and not any(c.isspace() for c in path)):
                result.append(path)
    return result


def prepare_task(task: dict[str, Any], *, repo_root: Path,
                 roles_doc: dict[str, Any] | None = None,
                 extra_context: tuple[str, ...] = ()) -> dict[str, Any]:
    """Return an ephemeral projection; explicit scopes are never widened.

    An absent/empty read scope used to imply the whole repository. It now
    derives from declared context, literal inputs, role contracts and outputs.
    A deliberate ['.'] still requests the whole repository.
    """
    result = copy.deepcopy(task)
    if not result.get("role"):
        raise ValueError("task names no role")
    roles_doc = roles_doc if roles_doc is not None else role_registry.load_roles()
    role = role_registry.role_spec(roles_doc, result.get("role"))
    explicit_context = paths(_field(result, "context_paths"), "context_paths")
    context = explicit_context + _input_paths(result, repo_root)
    if result.get("_source_path"):
        try:
            context.append(Path(result["_source_path"]).relative_to(repo_root.resolve()).as_posix())
        except ValueError:
            pass  # external handoff content is still present in the brief
    context += [RUNTIME_CORE, role["contract"]]
    context += paths(extra_context, "extra_context")
    result["context_paths"] = paths(context, "context_paths")
    write_scope = paths(_field(result, "write_scope"), "write_scope")
    if not write_scope:
        write_scope = list(dict.fromkeys(
            str(PurePosixPath(p).parent)
            for p in paths(_field(result, "artifact_paths"), "artifact_paths")))
    result["write_scope"] = write_scope
    declared_read = paths(_field(result, "read_scope"), "read_scope")
    # Remember the provenance if an already prepared task is passed through
    # again (plan, workspace creation, and execution share this function).
    derived = result.get("_read_scope_derived", not bool(declared_read))
    result["read_scope"] = (list(dict.fromkeys(result["context_paths"] + write_scope))
                            if derived else declared_read)
    result["_read_scope_derived"] = derived
    if extra_context and not derived:
        for path in paths(extra_context, "extra_context"):
            if not within(path, declared_read):
                raise ValueError(f"extra context {path!r} is outside the declared read_scope")
    return result


def context_manifest(task: dict[str, Any]) -> dict[str, Any]:
    """Small, serializable execution metadata; never a research conclusion."""
    return {
        "task_id": task.get("id"),
        "context_paths": task["context_paths"],
        "read_scope": task["read_scope"],
        "read_scope_source": "derived" if task["_read_scope_derived"] else "declared",
        "write_scope": task["write_scope"],
    }
