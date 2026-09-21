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

import json
import fnmatch
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Sequence

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
    discovery_scope: tuple[str, ...] = ()  # starting roots for a default search
    write_scope: tuple[str, ...] = ()       # empty = nothing is writable
    allowed_commands: tuple[str, ...] = ()
    command_timeout_seconds: int = 300
    max_read_bytes: int = 20_000
    max_output_bytes: int = 20_000
    max_read_lines: int = 400
    max_list_results: int = 200
    max_search_results: int = 100
    max_search_files: int = 2_000
    max_search_file_bytes: int = 1_000_000
    max_search_bytes: int = 8_000_000

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
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    marker = "\n[... truncated; request a narrower excerpt]"
    remaining = max(0, limit - len(marker.encode("utf-8")))
    if not remaining:
        return marker.encode()[:limit].decode()
    return encoded[:remaining].decode("utf-8", errors="ignore") + marker


_SKIP_DIRECTORIES = {".git", ".worktrees", "worktrees", ".venv", "venv",
                     "node_modules", "__pycache__", ".pytest_cache", ".tmp"}


def _matches_glob(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return (_matches_glob(parts, pattern[1:])
                or bool(parts) and _matches_glob(parts[1:], pattern))
    return (bool(parts) and fnmatch.fnmatchcase(parts[0], pattern[0])
            and _matches_glob(parts[1:], pattern[1:]))


def _iter_files(scope: TaskScope, pattern: str) -> Iterator[Path]:
    """Walk only the intersection of readable roots and the glob's prefix.

    Never sort a recursive repository-wide glob before applying the scope or
    result limit. Explicitly named cache directories remain inspectable.
    """
    if not isinstance(pattern, str) or not pattern:
        raise ToolDenied("pattern must be a nonempty repository-relative glob")
    parsed = PurePosixPath(pattern)
    if parsed.is_absolute() or ".." in parsed.parts or ".git" in parsed.parts:
        raise ToolDenied("pattern must stay inside the repository and outside .git")
    prefix_parts = []
    for part in parsed.parts:
        if any(c in part for c in "*?["):
            break
        prefix_parts.append(part)
    prefix = Path(*prefix_parts)
    roots = []
    search_roots = (scope.discovery_scope if pattern == "**/*" and scope.discovery_scope
                    else scope.read_scope)
    for name in search_roots or (".",):
        readable = Path(name)
        if prefix.is_relative_to(readable):
            candidate = prefix
        elif readable.is_relative_to(prefix):
            candidate = readable
        else:
            continue
        if not any(candidate.is_relative_to(p) for p in roots):
            roots = [p for p in roots if not p.is_relative_to(candidate)] + [candidate]
    seen = set()
    for relative in sorted(roots):
        root = scope.resolve(relative.as_posix(), write=False)
        if root.is_file():
            candidates = iter([root])
        else:
            def walk(start: Path) -> Iterator[Path]:
                for directory, dirs, files in os.walk(start, followlinks=False):
                    dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRECTORIES
                                     and not (Path(directory) / d).is_symlink())
                    for name in sorted(files):
                        yield Path(directory) / name
            candidates = walk(root)
        for path in candidates:
            try:
                resolved = scope.resolve(path.relative_to(scope.repo_root.resolve()).as_posix(), write=False)
            except (ToolDenied, ValueError):
                continue
            if resolved in seen or not resolved.is_file():
                continue
            seen.add(resolved)
            if _matches_glob(path.relative_to(scope.repo_root.resolve()).parts, parsed.parts):
                yield path


def _retrieval_result(scope: TaskScope, journal: ToolJournal, tool: str,
                      text: str, details: dict[str, Any], *, limit: int | None = None) -> str:
    limit = scope.max_output_bytes if limit is None else limit
    truncated = len(text.encode("utf-8")) > limit
    result = _truncate(text, limit)
    journal.record(tool, {**details, "bytes_returned": len(result.encode("utf-8")),
                          "output_truncated": truncated})
    return result


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


def _as_command_list(value: Any) -> list[str] | None:
    """Coerce a model-supplied command argument into a list of strings.

    Models (observed: glm-5.2 via the zai backend, 2026-08-22) sometimes pass
    the command as a JSON-array *string* — ``'["python3", "--version"]'`` —
    where the schema declares an array of strings. That shape is coerced, and
    nothing else: a bare shell string is never split, so the allow-list check
    on ``command[0]`` stays the authority on what may run. A malformed value
    returns None; the caller replies with a correctable message, never a crash.
    """
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            return None
        value = parsed
    if isinstance(value, (list, tuple)) and value:
        if all(isinstance(part, str) for part in value):
            return list(value)
    return None


# --------------------------------------------------------------------------
# tool implementations
# --------------------------------------------------------------------------
def _read_file(scope: TaskScope, journal: ToolJournal, path: str,
               start_line: int = 1, max_lines: int = 400, start_column: int = 1) -> str:
    start_line = _as_int(start_line, 1)
    start_column = _as_int(start_column, 1)
    max_lines = min(_as_int(max_lines, 400), scope.max_read_lines)
    try:
        target = scope.resolve(path, write=False)
    except ToolDenied as exc:
        journal.record("read_file", {"path": path}, denied=str(exc))
        return f"DENIED: {exc}"
    if not target.is_file():
        journal.record("read_file", {"path": path}, denied="not a file")
        return f"ERROR: {path} is not a file"
    start = max(1, start_line)
    selected = []
    size = 0
    continuation = None
    # Reserve space for a continuation cursor so truncation cannot hide how
    # to obtain the omitted text. Tiny configured caps still use _truncate.
    content_limit = max(1, scope.max_read_bytes - 180)
    # Stream lines rather than loading an entire run log into memory.
    with target.open(encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, 1):
            if number < start:
                continue
            column = start_column if number == start else 1
            if len(selected) >= max_lines:
                continuation = (number, column)
                break
            line = line.rstrip("\n")[column - 1:]
            prefix = f"{number}\t"
            remaining = content_limit - size - len(prefix.encode("utf-8")) - 1
            if len(line.encode("utf-8")) > remaining:
                if selected:
                    continuation = (number, column)
                else:
                    excerpt = line.encode("utf-8")[:max(0, remaining)].decode("utf-8", errors="ignore")
                    selected.append(prefix + excerpt)
                    continuation = (number, column + len(excerpt))
                break
            selected.append(prefix + line)
            size += len(selected[-1].encode("utf-8")) + 1
    suffix = (f"\n[... more content; continue with start_line={continuation[0]}, "
              f"start_column={continuation[1]}]" if continuation else "")
    return _retrieval_result(scope, journal, "read_file", "\n".join(selected) + suffix,
        {"path": scope.relative(target), "lines": len(selected), "start_line": start,
         "start_column": start_column, "continuation": continuation,
         "partial": continuation is not None}, limit=scope.max_read_bytes)


def _list_files(scope: TaskScope, journal: ToolJournal,
                pattern: str = "**/*", limit: int = 200) -> str:
    limit = min(_as_int(limit, 200), scope.max_list_results)
    found = []
    try:
        for path in _iter_files(scope, pattern):
            found.append(path.relative_to(scope.repo_root.resolve()).as_posix())
            if len(found) >= limit:
                break
    except ToolDenied as exc:
        journal.record("list_files", {"pattern": pattern}, denied=str(exc))
        return f"DENIED: {exc}"
    partial = len(found) >= limit
    result = "\n".join(found) or f"no readable files match {pattern!r}"
    if partial:
        result += "\n[... result limit reached; narrow the pattern for additional files]"
    return _retrieval_result(scope, journal, "list_files", result,
        {"pattern": pattern, "matches": len(found), "partial": partial})


def _search_files(scope: TaskScope, journal: ToolJournal, regex: str,
                  pattern: str = "**/*", limit: int = 100) -> str:
    limit = min(_as_int(limit, 100), scope.max_search_results)
    if not isinstance(regex, str):
        return "ERROR: regex must be a string pattern"
    try:
        compiled = re.compile(regex)
    except re.error as exc:
        return f"ERROR: invalid regular expression: {exc}"
    hits: list[str] = []
    scanned = bytes_read = skipped = 0
    partial = False
    try:
        for path in _iter_files(scope, pattern):
            if len(hits) >= limit or scanned >= scope.max_search_files or bytes_read >= scope.max_search_bytes:
                partial = True
                break
            scanned += 1
            try:
                cap = min(scope.max_search_file_bytes, scope.max_search_bytes - bytes_read)
                with path.open("rb") as handle:
                    raw = handle.read(cap + 1)
                bytes_read += len(raw)
                if len(raw) > cap:
                    partial = True
                    raw = raw[:cap]
                content = raw.decode("utf-8")
                if "\x00" in content:
                    skipped += 1
                    continue
            except (UnicodeDecodeError, OSError):
                skipped += 1
                continue
            relative = path.relative_to(scope.repo_root.resolve())
            for number, line in enumerate(content.splitlines(), start=1):
                if compiled.search(line):
                    hits.append(f"{relative}:{number}: {line.strip()[:200]}")
                    if len(hits) >= limit:
                        partial = True
                        break
    except ToolDenied as exc:
        journal.record("search_files", {"regex": regex, "pattern": pattern}, denied=str(exc))
        return f"DENIED: {exc}"
    partial = partial or bool(skipped)
    result = "\n".join(hits) or f"no matches in searched content for {regex!r}"
    if partial:
        result += "\n[... partial search: a result/scan limit or unreadable file was encountered; narrow the pattern or read a specific file]"
    return _retrieval_result(scope, journal, "search_files", result,
        {"regex": regex, "pattern": pattern, "matches": len(hits),
         "files_scanned": scanned, "bytes_read": bytes_read, "files_skipped": skipped,
         "partial": partial})


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
    coerced = _as_command_list(command)
    if coerced is None:
        return ("ERROR: command must be a non-empty argument list "
                "(a JSON array of strings)")
    if not isinstance(command, (list, tuple)):
        journal.record("run_command", {"command": coerced,
                                       "coerced_from": "string"})
    command = coerced
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
            func=lambda path, start_line=1, max_lines=400, start_column=1: _read_file(
                scope, journal, path, start_line, max_lines, start_column),
            name="read_file",
            description="Read a bounded repository-relative text excerpt with line numbers. "
                        "Use the returned line/column cursor for the next page."),
        "list_files": lambda: StructuredTool.from_function(
            func=lambda pattern="**/*", limit=200: _list_files(
                scope, journal, pattern, limit),
            name="list_files",
            description="List a bounded set of readable files matching a glob. "
                        "Default search starts in task context paths; specify a "
                        "repository-relative pattern for another declared readable path."),
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
