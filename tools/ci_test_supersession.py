"""Execute an explicit hash-bound successor for a frozen test fixture.

A corrected test replaces exactly one collected node; no item is dropped or
marked skipped. The node retains its id and reports successor provenance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import types

import pytest

REPO = Path(__file__).resolve().parents[1]
RECORD = "tests/fixtures/p192_role1_replay_correction/supersession.json"


def verified_bytes(repo: Path, binding: dict) -> tuple[Path, bytes]:
    relative = binding.get("path")
    expected = binding.get("sha256")
    if (not isinstance(relative, str) or not relative
            or Path(relative).is_absolute() or ".." in Path(relative).parts
            or not isinstance(expected, str)
            or re.fullmatch(r"[0-9a-f]{64}", expected) is None):
        raise ValueError("invalid test supersession path/hash binding")
    root = repo.resolve()
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError("test supersession source escapes repository or is a symlink")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"test supersession source hash mismatch: {relative}")
    return path, data


def verify_sources(repo: Path, bindings: list[dict]) -> None:
    for binding in bindings:
        verified_bytes(repo, binding)


def load_verified_module(repo: Path, binding: dict, name: str):
    path, data = verified_bytes(repo, binding)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def apply_supersession(items: list, repo: Path = REPO, record_path: str = RECORD) -> None:
    record = json.loads((repo / record_path).read_text(encoding="utf-8"))
    if record.get("schema") != "ci-test-supersession-v1":
        raise pytest.UsageError("unsupported CI test supersession schema")
    target = record.get("original_nodeid")
    if not isinstance(target, str) or target.count("::") != 1:
        raise pytest.UsageError("CI test supersession must name one exact function node")
    matches = [(index, item) for index, item in enumerate(items) if item.nodeid == target]
    if not matches:
        return  # This shard or explicit test selection did not collect the node.
    if len(matches) != 1:
        raise pytest.UsageError("CI test supersession target was collected more than once")
    index, original = matches[0]
    try:
        verified_bytes(repo, {"path": target.split("::", 1)[0], "sha256": record["original_sha256"]})
        verify_sources(repo, record["helpers"])
        module = load_verified_module(repo, record["replacement"], "ci_test_successor")
        replacement = getattr(module, record["replacement"]["callable"])
        if not callable(replacement):
            raise ValueError("test successor is not callable")
        corrected = pytest.Function.from_parent(original.parent, name=original.name, callobj=replacement)
        if corrected.nodeid != original.nodeid:
            raise ValueError("test successor changed the collected node identity")
    except (OSError, KeyError, ValueError, AttributeError, TypeError) as exc:
        raise pytest.UsageError(f"CI test supersession refused: {exc}") from exc
    corrected.user_properties.extend(original.user_properties)
    corrected.user_properties.extend([
        ("superseded_test_sha256", record["original_sha256"]),
        ("test_successor_path", record["replacement"]["path"]),
        ("test_successor_sha256", record["replacement"]["sha256"]),
    ])
    items[index] = corrected
