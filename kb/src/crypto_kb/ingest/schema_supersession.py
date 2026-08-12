"""Fail-closed routing for immutable schema-supersession records.

The registry is part of the source-of-truth repository, not the derived KB.
Repository ingestion therefore verifies both sides of every registered binding
before it substitutes replacement bytes for an immutable legacy path.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import yaml

REGISTRY_PATH = PurePosixPath("tools/schema_supersession_registry.yaml")
REGISTRY_SCHEMA = "schema-supersession-registry-v1"
REPLACEMENT_ROOT = PurePosixPath("ledger/corrections/schema-supersessions")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_KINDS = {
    "ledger": re.compile(
        r"^ledger/(?:questions|proposals|hypotheses|evidence|decisions|handoffs)/[^/]+\.yaml$"
    ),
    "experiment": re.compile(r"^experiments/[^/]+/specification\.yaml$"),
    "knowledge": re.compile(
        r"^knowledge/(?:literature|techniques|findings|open-problems)/[^/]+\.md$"
    ),
    "goal_checkpoint": re.compile(
        r"^ledger/goals/[^/]+/checkpoints/[^/]+\.yaml$"
    ),
}
_REQUIRED = {
    "kind",
    "superseded_path",
    "superseded_sha256",
    "superseding_path",
    "superseding_sha256",
    "defect",
    "registered",
}


class SchemaSupersessionError(ValueError):
    """The registry or one of its immutable hash bindings is invalid."""


@dataclass(frozen=True)
class SchemaSupersession:
    kind: str
    superseded_path: str
    superseded_sha256: str
    superseding_path: str
    superseding_sha256: str
    defect: str
    registered: str
    replacement_id: str | None = None
    redirect_id: str | None = None


@dataclass(frozen=True)
class RoutedSource:
    discovered_path: Path
    content_path: Path
    data: bytes
    supersession: SchemaSupersession | None = None


def load_schema_supersessions(repo_root: Path) -> dict[str, SchemaSupersession]:
    """Load and verify every registry binding, or raise without staging data."""
    root = repo_root.resolve()
    registry = _confined(root, str(REGISTRY_PATH))
    if not registry.exists():
        return {}
    try:
        document = yaml.safe_load(registry.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SchemaSupersessionError(f"cannot read schema supersession registry: {exc}") from exc
    if not isinstance(document, dict) or document.get("schema") != REGISTRY_SCHEMA:
        raise SchemaSupersessionError(f"registry must declare schema {REGISTRY_SCHEMA!r}")
    records = document.get("records")
    if not isinstance(records, list):
        raise SchemaSupersessionError("registry records must be a list")

    loaded: dict[str, SchemaSupersession] = {}
    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            raise SchemaSupersessionError(f"registry record {index} must be a mapping")
        missing = sorted(_REQUIRED - raw.keys())
        if missing:
            raise SchemaSupersessionError(f"registry record {index} missing {missing}")
        kind = _required_string(raw["kind"], index, "kind")
        if kind not in _KINDS:
            raise SchemaSupersessionError(
                f"registry record {index} has invalid kind {kind!r}"
            )
        source = _relative(raw["superseded_path"], index, "superseded_path")
        replacement = _relative(raw["superseding_path"], index, "superseding_path")
        discovered_kind = _kind_for_path(source)
        if discovered_kind != kind:
            raise SchemaSupersessionError(
                f"registry record {index} kind {kind!r} does not match "
                f"discovered source kind {discovered_kind!r}: {source}"
            )
        source_hash = _digest(raw["superseded_sha256"], index, "superseded_sha256")
        replacement_hash = _digest(raw["superseding_sha256"], index, "superseding_sha256")
        redirect_id = _optional_string(raw.get("redirect_id"), index, "redirect_id")
        replacement_id = _optional_string(raw.get("replacement_id"), index, "replacement_id")
        if redirect_id and replacement_id:
            raise SchemaSupersessionError(
                f"registry record {index} cannot declare both redirect_id and replacement_id"
            )
        if not redirect_id and not PurePosixPath(replacement).is_relative_to(REPLACEMENT_ROOT):
            raise SchemaSupersessionError(
                f"registry record {index} replacement must live below {REPLACEMENT_ROOT}"
            )
        replacement_kind = _kind_for_path(replacement)
        if redirect_id and replacement_kind != kind:
            raise SchemaSupersessionError(
                f"registry record {index} redirect target kind {replacement_kind!r} "
                f"does not match source kind {kind!r}: {replacement}"
            )
        if not redirect_id and replacement_kind is not None:
            raise SchemaSupersessionError(
                f"registry record {index} replacement must not match a source "
                f"discovery pattern: {replacement}"
            )
        if source in loaded:
            raise SchemaSupersessionError(f"duplicate superseded_path {source!r}")
        entry = SchemaSupersession(
            kind=kind,
            superseded_path=source,
            superseded_sha256=source_hash,
            superseding_path=replacement,
            superseding_sha256=replacement_hash,
            defect=_required_string(raw["defect"], index, "defect"),
            registered=_required_string(raw["registered"], index, "registered"),
            replacement_id=replacement_id,
            redirect_id=redirect_id,
        )
        _verify_file(_confined(root, source), source_hash, source)
        _verify_file(_confined(root, replacement), replacement_hash, replacement)
        loaded[source] = entry
    return loaded


def route_repository_source(
    repo_root: Path,
    discovered_path: Path,
    registry: Mapping[str, SchemaSupersession],
) -> RoutedSource:
    """Return verified effective bytes for replacement and redirect validation."""
    root = repo_root.resolve()
    try:
        relative = discovered_path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise SchemaSupersessionError(f"source escapes repository root: {discovered_path}") from exc
    entry = registry.get(relative)
    if entry is None:
        return RoutedSource(discovered_path, discovered_path, discovered_path.read_bytes())
    _verify_file(discovered_path, entry.superseded_sha256, entry.superseded_path)
    target = _confined(root, entry.superseding_path)
    data = _verify_file(target, entry.superseding_sha256, entry.superseding_path)
    return RoutedSource(discovered_path, target, data, entry)


def _relative(value: Any, index: int, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaSupersessionError(f"registry record {index} {field} must be a string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or value != pure.as_posix():
        raise SchemaSupersessionError(f"registry record {index} {field} is not a confined POSIX path")
    return value


def _digest(value: Any, index: int, field: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise SchemaSupersessionError(f"registry record {index} {field} must be lowercase SHA-256")
    return value


def _optional_string(value: Any, index: int, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise SchemaSupersessionError(f"registry record {index} {field} must be a nonempty string")
    return value.strip()


def _required_string(value: Any, index: int, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaSupersessionError(
            f"registry record {index} {field} must be a nonempty string"
        )
    return value.strip()


def _kind_for_path(relative: str) -> str | None:
    for kind, pattern in _KINDS.items():
        if pattern.fullmatch(relative):
            return kind
    return None


def _confined(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SchemaSupersessionError(f"registry path escapes repository root: {relative}") from exc
    return candidate


def _verify_file(path: Path, expected: str, label: str) -> bytes:
    try:
        if not path.is_file():
            raise SchemaSupersessionError(f"registered path is not a file: {label}")
        data = path.read_bytes()
    except OSError as exc:
        raise SchemaSupersessionError(f"cannot read registered path {label}: {exc}") from exc
    observed = hashlib.sha256(data).hexdigest()
    if observed != expected:
        raise SchemaSupersessionError(
            f"schema supersession hash mismatch for {label}: expected {expected}, observed {observed}"
        )
    return data
