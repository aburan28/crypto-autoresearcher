"""Read-only projections of committed legacy goal records.

Research Loop v2 must be able to observe a goal without choosing a convenient
subset of its state.  In particular, a sharded goal has a mutable ``goal.yaml``
head plus write-once batch-checkpoint shards that are materialized by
``tools/validate_ledger.py``.  This module mirrors only that documented merge
rule; it deliberately has no writer and never treats its projection as a
research record.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ProjectionError(ValueError):
    """Raised when a read-only legacy projection cannot be built safely."""


# Accept both legacy ``-001`` and current random six-hex suffixes.  The value
# is used only to select a pre-existing path; it is never an allocator for a
# new durable identifier.
GOAL_ID = re.compile(r"^GOAL-[A-Za-z0-9][A-Za-z0-9-]*$")
SCHEMA_SUPERSESSION_ROOT = "ledger/corrections/schema-supersessions/"


def canonical_json(value: Any) -> bytes:
    """Return the stable representation used for derived projection hashes."""

    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


@dataclass(frozen=True)
class SourceFile:
    """One source file that a projection read, bound by content hash."""

    path: str
    sha256: str


@dataclass(frozen=True)
class MaterializedGoal:
    """A derived, hash-bound logical goal view.

    ``record`` is intentionally ordinary immutable data rather than a mutable
    runtime object.  A caller that wants to create a new official checkpoint
    must go through the existing Coordinator/archive path instead.
    """

    goal_id: str
    layout: str
    record: dict[str, Any]
    source_files: tuple[SourceFile, ...]
    source_commit: str | None
    projection_hash: str

    @property
    def status(self) -> str | None:
        value = self.record.get("status")
        return value if isinstance(value, str) else None

    @property
    def next_action(self) -> str | None:
        value = self.record.get("next_action")
        return value if isinstance(value, str) else None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "crypto.autoresearch.goal_projection.v1",
            "goal_id": self.goal_id,
            "layout": self.layout,
            "source_commit": self.source_commit,
            "source_files": [
                {"path": source.path, "sha256": source.sha256}
                for source in self.source_files
            ],
            "record": copy.deepcopy(self.record),
            "projection_hash": self.projection_hash,
        }


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ProjectionError(f"cannot read {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise ProjectionError(f"{path} must contain a YAML mapping")
    return document


def _research_goal(path: Path) -> dict[str, Any]:
    record = _read_yaml(path).get("research_goal")
    if not isinstance(record, dict):
        raise ProjectionError(f"{path} is missing top-level research_goal mapping")
    return copy.deepcopy(record)


def _assert_plain_source_path(repo_root: Path, path: Path) -> Path:
    """Reject a source that escapes the checkout through a symlink.

    Git can track symlinks, and ``Path.read_*`` follows them.  A clean
    worktree therefore is not by itself enough to bind a projection to
    ``HEAD``: an unchanged tracked symlink could cause this observer to parse
    arbitrary outside-checkout bytes.  Goal sources are expected to be plain
    files below the repository root, so fail closed for every symlink component
    on that path.
    """

    try:
        relative = path.relative_to(repo_root)
    except ValueError as exc:
        raise ProjectionError(f"goal projection source escapes repository root: {path}") from exc
    current = repo_root
    for part in relative.parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise ProjectionError(f"cannot inspect goal projection source {current}: {exc}") from exc
        if stat.S_ISLNK(mode):
            raise ProjectionError(
                f"goal projection source may not traverse symlink component {current}"
            )
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise ProjectionError(f"cannot inspect goal projection source {path}: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise ProjectionError(f"goal projection source must be a regular file: {path}")
    return relative


def _plain_file_exists(repo_root: Path, path: Path) -> bool:
    """Return whether a candidate exists as a safe regular source file."""

    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise ProjectionError(f"cannot inspect goal projection source {path}: {exc}") from exc
    if stat.S_ISLNK(mode):
        raise ProjectionError(f"goal projection source may not be a symlink: {path}")
    if not stat.S_ISREG(mode):
        return False
    _assert_plain_source_path(repo_root, path)
    return True


def _source_file(repo_root: Path, path: Path) -> SourceFile:
    try:
        relative = _assert_plain_source_path(repo_root, path).as_posix()
        content = path.read_bytes()
    except OSError as exc:
        raise ProjectionError(f"cannot hash {path}: {exc}") from exc
    return SourceFile(path=relative, sha256=hashlib.sha256(content).hexdigest())


def _append_source_once(
    repo_root: Path, sources: list[SourceFile], path: Path
) -> None:
    """Append one hash-bound source, retaining a deterministic unique list."""

    source = _source_file(repo_root, path)
    if not any(existing.path == source.path for existing in sources):
        sources.append(source)


def _schema_supersession_target(
    repo_root: Path, path: Path
) -> tuple[Path, Path] | None:
    """Return the registry and replacement for one corrected checkpoint source.

    The authoritative validator routes immutable schema corrections through
    ``tools/schema_supersession_registry.yaml``.  This derived observer must
    follow the same registered replacement to avoid making a corrected goal
    unreadable.  It remains fail-closed: both the original and replacement
    hashes must match the registry, and the registry itself is returned so it
    becomes part of the hash-bound, pinned projection input.
    """

    registry = repo_root / "tools" / "schema_supersession_registry.yaml"
    if not _plain_file_exists(repo_root, registry):
        return None
    document = _read_yaml(registry)
    if document.get("schema") != "schema-supersession-registry-v1":
        raise ProjectionError(f"{registry} has an invalid schema supersession registry")
    records = document.get("records") or []
    if not isinstance(records, list):
        raise ProjectionError(f"{registry} records must be a list")

    relative = path.relative_to(repo_root).as_posix()
    matches = []
    for entry in records:
        if not isinstance(entry, dict):
            raise ProjectionError(f"{registry} records must contain mappings")
        if entry.get("superseded_path") == relative:
            matches.append(entry)
    if not matches:
        return None
    if len(matches) != 1:
        raise ProjectionError(f"{registry} registers {relative} more than once")

    entry = matches[0]
    if entry.get("kind") != "goal_checkpoint":
        raise ProjectionError(
            f"{registry} has an invalid checkpoint replacement kind for {relative}"
        )
    # The authoritative validator does not replace source bytes for an
    # alias-only redirect.  Preserve that distinction here: a redirect points
    # a record identifier at a canonical record, while a schema supersession
    # substitutes a parseable representation of this checkpoint.
    if entry.get("redirect_id"):
        return None
    replacement = entry.get("superseding_path")
    expected_source = str(entry.get("superseded_sha256", "")).lower()
    expected_replacement = str(entry.get("superseding_sha256", "")).lower()
    if not isinstance(replacement, str) or not replacement:
        raise ProjectionError(f"{registry} has an invalid replacement for {relative}")
    if Path(replacement).is_absolute() or ".." in replacement.split("/"):
        raise ProjectionError(
            f"{registry} replacement must be repository-relative without '..': "
            f"{replacement}"
        )
    if not replacement.startswith(SCHEMA_SUPERSESSION_ROOT):
        raise ProjectionError(
            f"{registry} replacement must live below {SCHEMA_SUPERSESSION_ROOT}: "
            f"{replacement}"
        )
    if not re.fullmatch(r"[0-9a-f]{64}", expected_source):
        raise ProjectionError(f"{registry} has an invalid source hash for {relative}")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_replacement):
        raise ProjectionError(f"{registry} has an invalid replacement hash for {relative}")
    replacement_path = repo_root / replacement
    if not _plain_file_exists(repo_root, replacement_path):
        raise ProjectionError(
            f"registered schema replacement is missing: {replacement}"
        )
    actual_source = hashlib.sha256(path.read_bytes()).hexdigest()
    actual_replacement = hashlib.sha256(replacement_path.read_bytes()).hexdigest()
    if actual_source != expected_source:
        raise ProjectionError(
            f"registered superseded source hash does not match: {relative}"
        )
    if actual_replacement != expected_replacement:
        raise ProjectionError(
            f"registered superseding source hash does not match: {replacement}"
        )
    return registry, replacement_path


def _head_commit(repo_root: Path) -> str | None:
    """Read the current local source commit without changing repository state."""

    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        return None
    result = completed.stdout.strip()
    return result or None


def _assert_committed_sources(repo_root: Path, sources: list[SourceFile]) -> str | None:
    """Bind each local source byte-for-byte to one pinned ``HEAD`` tree.

    A clean status is insufficient: it neither proves that a path is tracked
    nor protects against an unchanged tracked symlink.  For a Git worktree we
    pin ``HEAD`` once, reject symlink source paths, and compare each live file
    to its exact ``HEAD:<path>`` blob.  Unit fixtures that are not Git
    worktrees still support a source-commit-free read-only projection.
    """

    probe = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
        check=False,
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return None
    commit = _head_commit(repo_root)
    if commit is None:
        raise ProjectionError("cannot bind goal projection sources: Git worktree has no HEAD commit")
    for source in sources:
        path = repo_root / source.path
        _assert_plain_source_path(repo_root, path)
        try:
            local = path.read_bytes()
        except OSError as exc:
            raise ProjectionError(f"cannot read goal projection source {path}: {exc}") from exc
        expected = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{commit}:{source.path}"],
            check=False,
            capture_output=True,
        )
        if expected.returncode != 0:
            raise ProjectionError(
                f"goal projection source is not a tracked HEAD blob: {source.path}"
            )
        if local != expected.stdout:
            raise ProjectionError(
                "goal projection source does not byte-match its pinned HEAD blob; "
                "archive or discard the local change before observing committed state"
            )
        if hashlib.sha256(local).hexdigest() != source.sha256:
            raise ProjectionError(f"goal projection source changed while being read: {source.path}")
    return commit


def _validate_goal_id(goal_id: str) -> str:
    if not isinstance(goal_id, str) or not GOAL_ID.fullmatch(goal_id):
        raise ProjectionError("goal_id must be a safe GOAL-* identifier")
    return goal_id


def load_materialized_goal(repo_root: str | Path, goal_id: str) -> MaterializedGoal:
    """Load a flat or sharded goal using the validator's documented semantics.

    The function refuses an ambiguous layout instead of silently preferring one
    source.  It performs no schema/state validation beyond the read boundary;
    callers should keep using ``tools/validate_ledger.py`` for the authoritative
    validation pass.
    """

    root = Path(repo_root).expanduser().resolve()
    if not root.is_dir():
        raise ProjectionError(f"repository root does not exist: {root}")
    identifier = _validate_goal_id(goal_id)
    goals = root / "ledger" / "goals"
    flat_path = goals / f"{identifier}.yaml"
    shard_dir = goals / identifier
    head_path = shard_dir / "goal.yaml"
    flat_exists = _plain_file_exists(root, flat_path)
    sharded_exists = _plain_file_exists(root, head_path)
    if flat_exists and sharded_exists:
        raise ProjectionError(
            f"ambiguous legacy goal layout for {identifier}: both {flat_path} and {head_path}"
        )
    if not flat_exists and not sharded_exists:
        raise ProjectionError(f"goal record not found for {identifier}")

    sources: list[SourceFile] = []
    if flat_exists:
        record = _research_goal(flat_path)
        sources.append(_source_file(root, flat_path))
        layout = "flat"
    else:
        record = _research_goal(head_path)
        sources.append(_source_file(root, head_path))
        layout = "sharded"
        checkpoints_dir = shard_dir / "checkpoints"
        entries: list[dict[str, Any]] = []
        if checkpoints_dir.is_dir():
            for shard in sorted(checkpoints_dir.glob("*.yaml")):
                _assert_plain_source_path(root, shard)
                source = shard
                registry: Path | None = None
                supersession = _schema_supersession_target(root, shard)
                if supersession is not None:
                    registry, source = supersession
                document = _read_yaml(source)
                entry = document.get("batch_checkpoint")
                if not isinstance(entry, dict):
                    raise ProjectionError(
                        f"{shard} is missing top-level batch_checkpoint mapping"
                    )
                entries.append(copy.deepcopy(entry))
                _append_source_once(root, sources, shard)
                if registry is not None:
                    _append_source_once(root, sources, registry)
                if source != shard:
                    _append_source_once(root, sources, source)
        if entries:
            existing = record.get("batch_checkpoints", [])
            if existing is None:
                existing = []
            if not isinstance(existing, list):
                raise ProjectionError(f"{head_path}.research_goal.batch_checkpoints must be a list")
            record["batch_checkpoints"] = list(existing) + entries

    record_id = record.get("id")
    if record_id != identifier:
        raise ProjectionError(
            f"goal record id {record_id!r} does not match requested {identifier!r}"
        )
    payload = {
        "schema": "crypto.autoresearch.goal_projection.v1",
        "goal_id": identifier,
        "layout": layout,
        "source_files": [
            {"path": source.path, "sha256": source.sha256} for source in sources
        ],
        "record": record,
    }
    source_commit = _assert_committed_sources(root, sources)
    return MaterializedGoal(
        goal_id=identifier,
        layout=layout,
        record=record,
        source_files=tuple(sources),
        source_commit=source_commit,
        projection_hash=sha256(payload),
    )
