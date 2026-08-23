"""Repository tools for the `api_direct` runtime, bounded by the task's scope.

`AGENTS.md` says each dispatched task owns non-overlapping repository-relative
`write_scope` paths and that workers do not commit into a shared worktree.
Under Claude Code that is a rule an agent is asked to follow. Here it is
enforced: a write outside the declared scope fails, and the refusal is recorded
in the journal rather than being retried somewhere else.

Every tool refusal returns a message to the model instead of crashing the run.
A model that is told "denied, and here is the scope you actually own" can
correct itself; one that gets an opaque failure usually cannot.
"""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from langchain_core.tools import StructuredTool

# Read-only git subcommands. Committing is a Coordinator archival task with a
# verified post-commit receipt (AGENTS.md, "Durable research commits"), never
# something a worker does mid-run.
GIT_READ_ONLY = {"status", "diff", "log", "show", "rev-parse", "ls-files",
                 "blame", "describe", "cat-file"}


class ToolDenied(Exception):
    """A tool call fell outside what this task is permitted to do."""


@dataclass
class ToolJournal:
    """Audit trail: what the agent actually touched, including refusals."""
    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(self, tool: str, detail: dict[str, Any], *,
               denied: str | None = None) -> None:
        entry = {"tool": tool, **detail}
        if denied:
            entry["denied"] = denied
        self.entries.append(entry)

    @property
    def writes(self) -> list[str]:
        return [e["path"] for e in self.entries
                if e["tool"] in ("write_file", "edit_file") and "denied" not in e]

    @property
    def denials(self) -> list[dict[str, Any]]:
        return [e for e in self.entries if "denied" in e]


@dataclass(frozen=True)
class TaskScope:
    """What one dispatched task may read, write, and run."""
    repo_root: Path
    task_id: str
    read_scope: tuple[str, ...] = ()        # empty = the whole repository
    write_scope: tuple[str, ...] = ()       # empty = nothing is writable
    allowed_commands: tuple[str, ...] = ()
    command_timeout_seconds: int = 300
    max_read_bytes: int = 200_000
    max_output_bytes: int = 20_000

    # -- path admission ----------------------------------------------------
    def resolve(self, raw: str, *, write: bool) -> Path:
        if not raw or not raw.strip():
            raise ToolDenied("empty path")
        candidate = PurePosixPath(raw)
        if candidate.is_absolute():
            raise ToolDenied(
                f"{raw!r} is absolute; paths are repository-relative")
        if any(part == ".." for part in candidate.parts):
            raise ToolDenied(f"{raw!r} contains '..'")

        root = self.repo_root.resolve()
        # .resolve() collapses symlinks in the existing prefix, so a symlink
        # pointing outside the repository is caught here rather than followed.
        target = (root / candidate).resolve()
        try:
            relative = target.relative_to(root)
        except ValueError:
            raise ToolDenied(
                f"{raw!r} resolves outside the repository ({target})") from None

        scopes = self.write_scope if write else self.read_scope
        if write and not scopes:
            raise ToolDenied(
                f"task {self.task_id} declares no write_scope; it may not "
                f"write any file")
        if scopes and not any(_within(relative, scope) for scope in scopes):
            raise ToolDenied(
                f"{raw!r} is outside this task's "
                f"{'write' if write else 'read'}_scope: {', '.join(scopes)}")
        return target

    def relative(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.repo_root.resolve()))


def _within(relative: Path, scope: str) -> bool:
    scope_path = PurePosixPath(scope)
    parts = PurePosixPath(relative.as_posix()).parts
    return parts[:len(scope_path.parts)] == scope_path.parts


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n[... truncated, {len(text) - limit} more characters]"


def _as_int(value: Any, default: int, *, minimum: int = 1) -> int:
    """Coerce a model-supplied numeric argument.

    Models (observed: glm-5.2 via the zai backend, 2026-08-22) sometimes
    pass a string where the schema says integer. Per this module's
    contract a bad tool call returns a message the model can correct,
    never a crash: an uncoercible value falls back to the declared
    default rather than raising TypeError out of the tool loop.
    """
    if isinstance(value, bool):
        return default
    try:
        result = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, result)


# --------------------------------------------------------------------------
# tool implementations
# --------------------------------------------------------------------------
def _read_file(scope: TaskScope, journal: ToolJournal, path: str,
               start_line: int = 1, max_lines: int = 400) -> str:
    start_line = _as_int(start_line, 1)
    max_lines = _as_int(max_lines, 400)
    try:
        target = scope.resolve(path, write=False)
    except ToolDenied as exc:
        journal.record("read_file", {"path": path}, denied=str(exc))
        return f"DENIED: {exc}"
    if not target.is_file():
        journal.record("read_file", {"path": path}, denied="not a file")
        return f"ERROR: {path} is not a file"
    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    start = max(1, start_line)
    selected = lines[start - 1:start - 1 + max(1, max_lines)]
    journal.record("read_file", {"path": scope.relative(target),
                                 "lines": len(selected)})
    numbered = "\n".join(f"{start + i}\t{line}" for i, line in enumerate(selected))
    suffix = ("" if start - 1 + len(selected) >= len(lines)
              else f"\n[... {len(lines) - (start - 1) - len(selected)} more lines]")
    return _truncate(numbered + suffix, scope.max_read_bytes)


def _list_files(scope: TaskScope, journal: ToolJournal,
                pattern: str = "**/*", limit: int = 200) -> str:
    limit = _as_int(limit, 200)
    root = scope.repo_root.resolve()
    found = []
    for path in sorted(root.glob(pattern)):
        if not path.is_file():
            continue
        try:
            relative = path.resolve().relative_to(root)
        except ValueError:
            continue
        if scope.read_scope and not any(_within(relative, s) for s in scope.read_scope):
            continue
        found.append(str(relative))
        if len(found) >= limit:
            break
    journal.record("list_files", {"pattern": pattern, "matches": len(found)})
    return "\n".join(found) or f"no readable files match {pattern!r}"


def _search_files(scope: TaskScope, journal: ToolJournal, regex: str,
                  pattern: str = "**/*", limit: int = 100) -> str:
    limit = _as_int(limit, 100)
    if not isinstance(regex, str):
        return "ERROR: regex must be a string pattern"
    try:
        compiled = re.compile(regex)
    except re.error as exc:
        return f"ERROR: invalid regular expression: {exc}"
    root = scope.repo_root.resolve()
    hits: list[str] = []
    for path in sorted(root.glob(pattern)):
        if not path.is_file() or len(hits) >= limit:
            continue
        try:
            relative = path.resolve().relative_to(root)
        except ValueError:
            continue
        if scope.read_scope and not any(_within(relative, s) for s in scope.read_scope):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(content.splitlines(), start=1):
            if compiled.search(line):
                hits.append(f"{relative}:{number}: {line.strip()[:200]}")
                if len(hits) >= limit:
                    break
    journal.record("search_files", {"regex": regex, "matches": len(hits)})
    return "\n".join(hits) or f"no matches for {regex!r}"


def _write_file(scope: TaskScope, journal: ToolJournal, path: str,
                content: str) -> str:
    try:
        target = scope.resolve(path, write=True)
    except ToolDenied as exc:
        journal.record("write_file", {"path": path}, denied=str(exc))
        return f"DENIED: {exc}"
    if target.exists():
        # Research artifacts are immutable; a correction is a new record.
        journal.record("write_file", {"path": path}, denied="would overwrite")
        return (f"DENIED: {path} already exists. Artifacts are immutable — "
                f"use edit_file for an in-progress draft, or write a new "
                f"superseding path.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    journal.record("write_file", {"path": scope.relative(target),
                                  "bytes": len(content.encode("utf-8"))})
    return f"wrote {scope.relative(target)} ({len(content)} characters)"


def _edit_file(scope: TaskScope, journal: ToolJournal, path: str,
               old_text: str, new_text: str) -> str:
    try:
        target = scope.resolve(path, write=True)
    except ToolDenied as exc:
        journal.record("edit_file", {"path": path}, denied=str(exc))
        return f"DENIED: {exc}"
    if not target.is_file():
        journal.record("edit_file", {"path": path}, denied="not a file")
        return f"ERROR: {path} is not a file"
    content = target.read_text(encoding="utf-8")
    occurrences = content.count(old_text)
    if occurrences == 0:
        journal.record("edit_file", {"path": path}, denied="old_text not found")
        return f"ERROR: old_text not found in {path}"
    if occurrences > 1:
        journal.record("edit_file", {"path": path}, denied="old_text ambiguous")
        return (f"ERROR: old_text appears {occurrences} times in {path}; "
                f"include enough surrounding context to make it unique")
    target.write_text(content.replace(old_text, new_text), encoding="utf-8")
    journal.record("edit_file", {"path": scope.relative(target),
                                 "replaced_characters": len(old_text)})
    return f"edited {scope.relative(target)}"


def _run_command(scope: TaskScope, journal: ToolJournal, command: list[str],
                 timeout_seconds: int | None = None) -> str:
    if timeout_seconds is not None:
        timeout_seconds = _as_int(timeout_seconds,
                                  scope.command_timeout_seconds)
    if not isinstance(command, (list, tuple)) or not command:
        return ("ERROR: command must be a non-empty argument list "
                "(a JSON array of strings)")
    if not all(isinstance(part, str) for part in command):
        return "ERROR: every argument in the command list must be a string"
    program = command[0]
    if program not in scope.allowed_commands:
        journal.record("run_command", {"command": command},
                       denied=f"{program!r} not in allowed_commands")
        return (f"DENIED: {program!r} is not permitted for this task. "
                f"Allowed: {', '.join(scope.allowed_commands) or 'none'}")
    if program == "git" and (len(command) < 2 or command[1] not in GIT_READ_ONLY):
        journal.record("run_command", {"command": command},
                       denied="mutating git subcommand")
        return ("DENIED: only read-only git subcommands are permitted "
                f"({', '.join(sorted(GIT_READ_ONLY))}). Committing is a "
                f"Coordinator archival task, not a worker action.")
    timeout = min(timeout_seconds or scope.command_timeout_seconds,
                  scope.command_timeout_seconds)
    try:
        finished = subprocess.run(
            command, cwd=scope.repo_root, capture_output=True, text=True,
            timeout=timeout, check=False,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    except subprocess.TimeoutExpired:
        journal.record("run_command", {"command": command, "timeout": timeout},
                       denied="timed out")
        # A timeout is infrastructure signal, never a negative result.
        return (f"TIMEOUT after {timeout}s. This is an infrastructure outcome, "
                f"not evidence about the hypothesis.")
    except (OSError, ValueError) as exc:
        journal.record("run_command", {"command": command}, denied=str(exc))
        return f"ERROR: {exc}"
    journal.record("run_command", {"command": command,
                                   "exit_code": finished.returncode})
    return _truncate(
        f"exit_code: {finished.returncode}\n"
        f"--- stdout ---\n{finished.stdout}\n--- stderr ---\n{finished.stderr}",
        scope.max_output_bytes)


# --------------------------------------------------------------------------
# capability -> tools
# --------------------------------------------------------------------------
def build_tools(scope: TaskScope, journal: ToolJournal,
                tool_names: Sequence[str]) -> list[StructuredTool]:
    """Instantiate exactly the tools a role's capabilities allow, no more."""
    factories = {
        "read_file": lambda: StructuredTool.from_function(
            func=lambda path, start_line=1, max_lines=400: _read_file(
                scope, journal, path, start_line, max_lines),
            name="read_file",
            description="Read a repository-relative text file, with line numbers."),
        "list_files": lambda: StructuredTool.from_function(
            func=lambda pattern="**/*", limit=200: _list_files(
                scope, journal, pattern, limit),
            name="list_files",
            description="List readable repository files matching a glob pattern."),
        "search_files": lambda: StructuredTool.from_function(
            func=lambda regex, pattern="**/*", limit=100: _search_files(
                scope, journal, regex, pattern, limit),
            name="search_files",
            description="Search readable files for a regular expression; "
                        "returns path:line: text."),
        "write_file": lambda: StructuredTool.from_function(
            func=lambda path, content: _write_file(scope, journal, path, content),
            name="write_file",
            description="Create a new file inside this task's write_scope. "
                        "Refuses to overwrite: artifacts are immutable."),
        "edit_file": lambda: StructuredTool.from_function(
            func=lambda path, old_text, new_text: _edit_file(
                scope, journal, path, old_text, new_text),
            name="edit_file",
            description="Replace one unique occurrence of old_text in a file "
                        "inside this task's write_scope."),
        "run_command": lambda: StructuredTool.from_function(
            func=lambda command, timeout_seconds=None: _run_command(
                scope, journal, command, timeout_seconds),
            name="run_command",
            description="Run an allow-listed command as an argument list "
                        "(no shell) from the repository root."),
    }
    unknown = [name for name in tool_names if name not in factories]
    if unknown:
        raise ValueError(f"no implementation for tool(s): {', '.join(unknown)}")
    return [factories[name]() for name in tool_names]
