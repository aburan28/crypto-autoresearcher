#!/usr/bin/env python3
"""Fail-closed verifier for an exact, pre-reviewed two-parent merge.

The verifier has two modes and never performs a merge or writes to the target
repository:

``pre``
    Validate the frozen manifest and candidate, exact source commits and merge
    base, the complete changed-path set across every commit after the repair
    authoring base, unchanged canonical conflict-path objects, and the exact
    structural conflict set.

``post``
    Repeat the pre-merge contract checks, then require an exact two-parent
    merge commit, reconstruct and compare its complete expected tree, check
    candidate byte equality, reject conflict markers or dirty/unmerged state,
    and require either a bound successful ledger-validation receipt or an
    explicitly requested run of the allow-listed ledger validator.

The first-parent path allowlist is deliberately explicit command input.  It is
part of the certificate, just like the expected parent hashes; deriving it
from the observed range would make the Red Team's disjoint-path counterexample
pass by construction.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any, Iterable

import yaml


HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MANIFEST_SCHEMA = "crypto.autoresearch.merge_resolution_manifest.v1"
LEDGER_RESULT_SCHEMA = "crypto.autoresearch.ledger_validation_result.v1"
MARKER_PATTERNS = ("^<<<<<<< ", "^>>>>>>> ", "^|||||||")


class VerificationError(RuntimeError):
    """A fail-closed certificate rejection."""


class StrictLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _strict_mapping(loader: StrictLoader, node: yaml.MappingNode,
                    deep: bool = False) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise VerificationError(f"duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_mapping)


def _strict_yaml(data: bytes, source: str) -> Any:
    try:
        documents = list(yaml.load_all(data.decode("utf-8"), Loader=StrictLoader))
    except (UnicodeDecodeError, yaml.YAMLError, VerificationError) as exc:
        raise VerificationError(f"malformed YAML in {source}: {exc}") from exc
    if len(documents) != 1:
        raise VerificationError(f"{source} must contain exactly one YAML document")
    return documents[0]


def _strict_json(data: bytes, source: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise VerificationError(f"duplicate JSON key in {source}: {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"malformed JSON in {source}: {exc}") from exc


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{label} must be a mapping")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{label} must be a list")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{label} must be a non-empty string")
    return value


def _require_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VerificationError(f"{label} must be an integer")
    return value


def _require_hex(value: Any, pattern: re.Pattern[str], label: str) -> str:
    text = _require_string(value, label)
    if not pattern.fullmatch(text):
        raise VerificationError(f"{label} must be a lowercase full-length hex digest")
    return text


def _repo_path(value: Any, label: str) -> str:
    text = _require_string(value, label)
    path = PurePosixPath(text)
    if path.is_absolute() or text != path.as_posix() or ".." in path.parts:
        raise VerificationError(f"{label} must be a normalized repository-relative path")
    if not path.parts or path.parts[0] in ("", "."):
        raise VerificationError(f"{label} is not a valid repository-relative path")
    return text


def _inside_repo(repo: Path, path: Path, label: str) -> str:
    try:
        relative = path.resolve(strict=True).relative_to(repo)
    except (OSError, ValueError) as exc:
        raise VerificationError(f"{label} must be an existing file inside the repository") from exc
    return _repo_path(relative.as_posix(), label)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_oid(data: bytes) -> str:
    framed = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(framed).hexdigest()


@dataclasses.dataclass(frozen=True, order=True)
class TreeEntry:
    mode: str
    oid: str
    object_type: str = "blob"


@dataclasses.dataclass(frozen=True)
class Resolution:
    path: str
    mode: str
    selection: str
    destination_oid: str
    expected_conflict_class: str


@dataclasses.dataclass(frozen=True)
class Contract:
    correction_id: str
    repair_base: str
    second_parent: str
    merge_base: str
    manifest_path: str
    manifest_sha256: str
    candidate_path: str
    candidate_sha256: str
    candidate_size: int
    candidate_oid: str
    resolutions: tuple[Resolution, ...]


class GitRepository:
    """Small read-only Git command surface used by the verifier."""

    def __init__(self, root: Path):
        self.root = root
        probe = self.run("rev-parse", "--show-toplevel")
        try:
            observed = Path(probe.decode("utf-8").strip()).resolve(strict=True)
        except (UnicodeDecodeError, OSError) as exc:
            raise VerificationError(f"cannot resolve repository root: {exc}") from exc
        if observed != root:
            raise VerificationError(
                f"repository argument is not the Git toplevel: expected {root}, got {observed}")

    def run(self, *args: str, allowed_returncodes: Iterable[int] = (0,)) -> bytes:
        env = os.environ.copy()
        env.update({"GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C", "LANG": "C"})
        proc = subprocess.run(
            ["git", "-C", os.fspath(self.root), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        allowed = set(allowed_returncodes)
        if proc.returncode not in allowed:
            stderr = proc.stderr.decode("utf-8", errors="replace").strip()
            raise VerificationError(
                f"git {' '.join(args)} failed with exit {proc.returncode}: {stderr}")
        return proc.stdout

    def exact_commit(self, value: str, label: str) -> str:
        expected = _require_hex(value, HEX40, label)
        observed = self.run("rev-parse", "--verify", f"{expected}^{{commit}}")
        try:
            resolved = observed.decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise VerificationError(f"non-ASCII commit identity for {label}") from exc
        if resolved != expected:
            raise VerificationError(f"{label} did not resolve to itself exactly")
        return expected

    def head(self) -> str:
        return self.run("rev-parse", "HEAD").decode("ascii").strip()

    def tree(self, commit: str) -> dict[str, TreeEntry]:
        raw = self.run("ls-tree", "-rz", "--full-tree", "-r", commit)
        result: dict[str, TreeEntry] = {}
        for record in raw.split(b"\0"):
            if not record:
                continue
            try:
                metadata, raw_path = record.split(b"\t", 1)
                mode_b, type_b, oid_b = metadata.split(b" ", 2)
                path = raw_path.decode("utf-8", errors="strict")
                entry = TreeEntry(
                    mode_b.decode("ascii"), oid_b.decode("ascii"),
                    type_b.decode("ascii"))
            except (ValueError, UnicodeDecodeError) as exc:
                raise VerificationError(f"malformed or non-UTF-8 ls-tree record: {record!r}") from exc
            _repo_path(path, "Git tree path")
            if path in result:
                raise VerificationError(f"duplicate Git tree path: {path}")
            if entry.object_type not in {"blob", "commit"} or not HEX40.fullmatch(entry.oid):
                raise VerificationError(f"unsupported tree entry at {path}: {entry}")
            result[path] = entry
        return result

    def merge_bases(self, first: str, second: str) -> list[str]:
        raw = self.run("merge-base", "--all", first, second)
        return [line for line in raw.decode("ascii").splitlines() if line]

    def require_ancestor(self, ancestor: str, descendant: str) -> None:
        self.run("merge-base", "--is-ancestor", ancestor, descendant)

    def changed_paths_across_range(self, base: str, tip: str) -> tuple[set[str], int]:
        """Union every commit's first-parent diff, not only the final tree diff.

        `rev-list base..tip` includes side commits introduced by any merge.  A
        side commit is therefore checked independently, while each merge commit
        is compared with its ordered first parent.  This catches both disjoint
        additions and paths that were later reverted before `tip`.
        """
        commits = self.run("rev-list", "--topo-order", "--reverse", f"{base}..{tip}")
        commit_ids = [line for line in commits.decode("ascii").splitlines() if line]
        changed: set[str] = set()
        for commit in commit_ids:
            parent_line = self.run("rev-list", "--parents", "-n", "1", commit)
            fields = parent_line.decode("ascii").strip().split()
            if not fields or fields[0] != commit or len(fields) < 2:
                raise VerificationError(f"commit {commit} has no usable ordered first parent")
            parent = fields[1]
            raw = self.run(
                "diff", "--name-only", "-z", "--no-renames", parent, commit, "--")
            for encoded in raw.split(b"\0"):
                if not encoded:
                    continue
                try:
                    path = encoded.decode("utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    raise VerificationError("non-UTF-8 path in first-parent range") from exc
                changed.add(_repo_path(path, "first-parent changed path"))
        return changed, len(commit_ids)

    def require_clean_at(self, expected_head: str) -> None:
        if self.head() != expected_head:
            raise VerificationError(
                f"repository HEAD is not the expected inspected commit {expected_head}")
        unmerged = self.run("ls-files", "-u", "-z")
        if unmerged:
            raise VerificationError("repository index contains unmerged entries")
        status = self.run("status", "--porcelain=v1", "-z", "--untracked-files=all")
        if status:
            raise VerificationError("repository worktree or index is dirty")


def _load_contract(repo: Path, manifest_path: Path, candidate_path: Path,
                   expected_manifest_sha256: str,
                   expected_second_parent: str) -> Contract:
    manifest_rel = _inside_repo(repo, manifest_path, "manifest")
    candidate_rel = _inside_repo(repo, candidate_path, "candidate")
    manifest_data = manifest_path.resolve().read_bytes()
    candidate_data = candidate_path.resolve().read_bytes()
    expected_manifest_hash = _require_hex(
        expected_manifest_sha256, HEX64, "expected manifest SHA-256")
    observed_manifest_hash = _sha256(manifest_data)
    if observed_manifest_hash != expected_manifest_hash:
        raise VerificationError(
            f"manifest SHA-256 mismatch: expected {expected_manifest_hash}, "
            f"got {observed_manifest_hash}")

    document = _require_mapping(_strict_yaml(manifest_data, manifest_rel), "manifest")
    body = _require_mapping(document.get("merge_resolution_manifest"),
                            "merge_resolution_manifest")
    if body.get("schema") != MANIFEST_SCHEMA:
        raise VerificationError(f"manifest schema must be {MANIFEST_SCHEMA}")
    correction_id = _require_string(body.get("correction_id"), "correction_id")

    source = _require_mapping(body.get("frozen_source_projection"),
                              "frozen_source_projection")
    repair_base = _require_hex(source.get("repair_authoring_base"), HEX40,
                               "repair_authoring_base")
    second_parent = _require_hex(source.get("required_second_parent"), HEX40,
                                 "required_second_parent")
    merge_base = _require_hex(source.get("merge_base"), HEX40, "merge_base")
    if second_parent != expected_second_parent:
        raise VerificationError("manifest second parent differs from explicit expected second parent")

    summary = _require_mapping(body.get("conflict_summary"), "conflict_summary")
    conflict_count = _require_int(summary.get("exact_conflict_count"),
                                  "exact_conflict_count")
    immutable_count = _require_int(summary.get("immutable_add_add_count"),
                                   "immutable_add_add_count")
    mutable_count = _require_int(summary.get("mutable_goal_projection_count"),
                                 "mutable_goal_projection_count")
    if conflict_count <= 0 or immutable_count < 0 or mutable_count < 0:
        raise VerificationError("manifest conflict counts must be non-negative and non-empty")
    if immutable_count + mutable_count != conflict_count:
        raise VerificationError("manifest conflict class counts do not sum to exact count")

    raw_resolutions = _require_list(body.get("canonical_resolutions"),
                                    "canonical_resolutions")
    if len(raw_resolutions) != conflict_count:
        raise VerificationError("canonical resolution count differs from exact conflict count")

    resolutions: list[Resolution] = []
    paths: set[str] = set()
    seen_immutable = 0
    seen_mutable = 0
    candidate_oid: str | None = None
    candidate_sha256: str | None = None
    candidate_size: int | None = None
    for index, raw_resolution in enumerate(raw_resolutions, 1):
        item = _require_mapping(raw_resolution, f"canonical_resolutions[{index}]")
        path = _repo_path(item.get("path"), f"canonical_resolutions[{index}].path")
        if path in paths:
            raise VerificationError(f"duplicate canonical resolution path: {path}")
        paths.add(path)
        mode = _require_string(item.get("mode"), f"resolution mode for {path}")
        if mode != "100644":
            raise VerificationError(f"unsupported frozen resolution mode for {path}: {mode}")
        selection = _require_string(item.get("selection"), f"selection for {path}")
        oid = _require_hex(item.get("source_git_blob_oid_sha1"), HEX40,
                           f"source OID for {path}")
        if selection == "frozen_origin_main_body_for_namespace_serialization_only":
            source_commit = _require_hex(item.get("source_commit"), HEX40,
                                         f"source commit for {path}")
            if source_commit != second_parent:
                raise VerificationError(f"immutable resolution {path} uses an alternate source commit")
            conflict_class = "add/add"
            seen_immutable += 1
        elif selection == "pre_reviewed_neutral_third_body":
            source_path = _repo_path(item.get("source_path"), f"source path for {path}")
            if source_path != candidate_rel:
                raise VerificationError("explicit candidate path differs from manifest candidate path")
            candidate_sha256 = _require_hex(item.get("source_sha256"), HEX64,
                                            "candidate SHA-256")
            candidate_size = _require_int(item.get("size_bytes"), "candidate size")
            candidate_oid = oid
            conflict_class = "content"
            seen_mutable += 1
        else:
            raise VerificationError(f"unsupported resolution selection for {path}: {selection}")
        resolutions.append(Resolution(path, mode, selection, oid, conflict_class))

    if seen_immutable != immutable_count or seen_mutable != mutable_count:
        raise VerificationError("canonical resolution selections disagree with conflict summary")
    if candidate_oid is None or candidate_sha256 is None or candidate_size is None:
        raise VerificationError("manifest must contain exactly one reviewed candidate resolution")
    if seen_mutable != 1:
        raise VerificationError("frozen exact verifier requires exactly one candidate resolution")
    if len(candidate_data) != candidate_size:
        raise VerificationError("candidate byte size differs from manifest")
    if _sha256(candidate_data) != candidate_sha256:
        raise VerificationError("candidate SHA-256 differs from manifest")
    if _git_blob_oid(candidate_data) != candidate_oid:
        raise VerificationError("candidate Git blob OID differs from manifest")

    return Contract(
        correction_id=correction_id,
        repair_base=repair_base,
        second_parent=second_parent,
        merge_base=merge_base,
        manifest_path=manifest_rel,
        manifest_sha256=observed_manifest_hash,
        candidate_path=candidate_rel,
        candidate_sha256=candidate_sha256,
        candidate_size=candidate_size,
        candidate_oid=candidate_oid,
        resolutions=tuple(resolutions),
    )


def _structural_conflicts(base: dict[str, TreeEntry], first: dict[str, TreeEntry],
                          second: dict[str, TreeEntry]) -> dict[str, str]:
    """Return all non-identical two-sided changes and their conflict class.

    The frozen contract contains only add/add and content cases.  Treating any
    other non-identical two-sided state as a conflict is deliberately
    fail-closed; it cannot be silently accepted as an auto-merge extension.
    """
    result: dict[str, str] = {}
    for path in sorted(set(base) | set(first) | set(second)):
        base_entry = base.get(path)
        first_entry = first.get(path)
        second_entry = second.get(path)
        if first_entry == base_entry or second_entry == base_entry or first_entry == second_entry:
            continue
        if base_entry is None and first_entry is not None and second_entry is not None:
            conflict_class = "add/add"
        elif base_entry is not None and first_entry is None and second_entry is not None:
            conflict_class = "delete/modify"
        elif base_entry is not None and second_entry is None and first_entry is not None:
            conflict_class = "modify/delete"
        elif base_entry is not None and first_entry is not None and second_entry is not None:
            conflict_class = "content"
        else:
            conflict_class = "unsupported"
        result[path] = conflict_class
    return result


def _expected_tree(contract: Contract, base: dict[str, TreeEntry],
                   first: dict[str, TreeEntry],
                   second: dict[str, TreeEntry]) -> dict[str, TreeEntry]:
    resolutions = {
        item.path: TreeEntry(item.mode, item.destination_oid, "blob")
        for item in contract.resolutions
    }
    expected: dict[str, TreeEntry] = {}
    for path in sorted(set(base) | set(first) | set(second)):
        if path in resolutions:
            chosen = resolutions[path]
        else:
            base_entry = base.get(path)
            first_entry = first.get(path)
            second_entry = second.get(path)
            if first_entry == second_entry:
                chosen = first_entry
            elif first_entry == base_entry:
                chosen = second_entry
            elif second_entry == base_entry:
                chosen = first_entry
            else:
                raise VerificationError(f"undeclared two-sided merge change at {path}")
        if chosen is not None:
            expected[path] = chosen
    return expected


def _verify_frozen_inputs(git: GitRepository, contract: Contract,
                          first_parent: str, second_parent: str,
                          allowed_first_parent_paths: Iterable[str]) -> dict[str, Any]:
    first = git.exact_commit(first_parent, "expected first parent")
    second = git.exact_commit(second_parent, "expected second parent")
    git.exact_commit(contract.repair_base, "manifest repair authoring base")
    git.exact_commit(contract.merge_base, "manifest merge base")
    if second != contract.second_parent:
        raise VerificationError("explicit second parent differs from frozen manifest")

    git.require_ancestor(contract.repair_base, first)
    bases_now = git.merge_bases(first, second)
    if bases_now != [contract.merge_base]:
        raise VerificationError(
            f"first/second merge base mismatch: expected only {contract.merge_base}, got {bases_now}")
    bases_at_repair = git.merge_bases(contract.repair_base, second)
    if bases_at_repair != [contract.merge_base]:
        raise VerificationError("repair-base/second-parent merge base differs from manifest")

    allowed_list = [_repo_path(value, "allowed first-parent path")
                    for value in allowed_first_parent_paths]
    if not allowed_list:
        raise VerificationError("at least one explicit allowed first-parent path is required")
    if len(set(allowed_list)) != len(allowed_list):
        raise VerificationError("duplicate allowed first-parent path")
    allowed = set(allowed_list)
    observed, commit_count = git.changed_paths_across_range(contract.repair_base, first)
    if observed != allowed:
        extra = sorted(observed - allowed)
        missing = sorted(allowed - observed)
        raise VerificationError(
            f"complete first-parent changed-path allowlist mismatch; "
            f"unexpected={extra}, declared_but_unchanged={missing}")

    repair_tree = git.tree(contract.repair_base)
    merge_base_tree = git.tree(contract.merge_base)
    first_tree = git.tree(first)
    second_tree = git.tree(second)
    for resolution in contract.resolutions:
        repair_entry = repair_tree.get(resolution.path)
        first_entry = first_tree.get(resolution.path)
        if repair_entry is None or first_entry != repair_entry:
            raise VerificationError(
                f"canonical conflict path drifted after repair authoring base: {resolution.path}")
        if resolution.selection == "frozen_origin_main_body_for_namespace_serialization_only":
            expected = TreeEntry(resolution.mode, resolution.destination_oid, "blob")
            if second_tree.get(resolution.path) != expected:
                raise VerificationError(
                    f"second-parent source OID or mode mismatch at {resolution.path}")

    observed_conflicts = _structural_conflicts(merge_base_tree, first_tree, second_tree)
    expected_conflicts = {
        resolution.path: resolution.expected_conflict_class
        for resolution in contract.resolutions
    }
    if observed_conflicts != expected_conflicts:
        raise VerificationError(
            f"predicted conflict set/classes mismatch; expected={expected_conflicts}, "
            f"observed={observed_conflicts}")

    return {
        "first_parent": first,
        "second_parent": second,
        "repair_authoring_base": contract.repair_base,
        "merge_base": contract.merge_base,
        "first_parent_range_commit_count": commit_count,
        "first_parent_changed_paths": sorted(observed),
        "conflicts": [
            {"path": path, "class": observed_conflicts[path]}
            for path in sorted(observed_conflicts)
        ],
        "trees": (merge_base_tree, first_tree, second_tree),
    }


def verify_pre(repository: Path, manifest: Path, candidate: Path,
               expected_manifest_sha256: str, expected_first_parent: str,
               expected_second_parent: str,
               allowed_first_parent_paths: Iterable[str]) -> dict[str, Any]:
    repo = repository.resolve(strict=True)
    git = GitRepository(repo)
    expected_second = _require_hex(expected_second_parent, HEX40,
                                   "expected second parent")
    contract = _load_contract(repo, manifest, candidate,
                              expected_manifest_sha256, expected_second)
    details = _verify_frozen_inputs(
        git, contract, expected_first_parent, expected_second,
        allowed_first_parent_paths)
    git.require_clean_at(details["first_parent"])
    details.pop("trees")
    return {
        "schema": "crypto.autoresearch.exact_merge_certificate.v1",
        "mode": "pre",
        "status": "PASS",
        "repository": os.fspath(repo),
        "manifest_path": contract.manifest_path,
        "manifest_sha256": contract.manifest_sha256,
        "candidate_path": contract.candidate_path,
        "candidate_sha256": contract.candidate_sha256,
        "candidate_size_bytes": contract.candidate_size,
        "candidate_git_blob_oid_sha1": contract.candidate_oid,
        **details,
        "repository_clean": True,
        "experiment_runs": 0,
    }


def _check_ledger_result(path: Path, merge_commit: str) -> dict[str, Any]:
    try:
        data = path.resolve(strict=True).read_bytes()
    except OSError as exc:
        raise VerificationError(f"cannot read ledger-validation result: {exc}") from exc
    result = _require_mapping(_strict_json(data, os.fspath(path)),
                              "ledger-validation result")
    if result.get("schema") != LEDGER_RESULT_SCHEMA:
        raise VerificationError(f"ledger-validation result schema must be {LEDGER_RESULT_SCHEMA}")
    if result.get("merge_commit") != merge_commit:
        raise VerificationError("ledger-validation result is not bound to the merge commit")
    command = result.get("command")
    if command not in (
        ["python3", "tools/validate_ledger.py"],
        [sys.executable, "tools/validate_ledger.py"],
    ):
        raise VerificationError("ledger-validation result names a non-allow-listed command")
    exit_code = _require_int(result.get("exit_code"), "ledger-validation exit_code")
    new_violations = _require_int(
        result.get("new_violations"), "ledger-validation new_violations")
    if exit_code != 0 or new_violations != 0:
        raise VerificationError("ledger-validation result is not a zero-new-violation success")
    return {
        "source": "caller_supplied_result",
        "path": os.fspath(path.resolve()),
        "sha256": _sha256(data),
        "exit_code": 0,
        "new_violations": 0,
    }


def _run_ledger_validator(repo: Path) -> dict[str, Any]:
    validator = repo / "tools" / "validate_ledger.py"
    if not validator.is_file():
        raise VerificationError("allow-listed ledger validator is missing")
    env = os.environ.copy()
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C", "LANG": "C"})
    command = [sys.executable, "tools/validate_ledger.py"]
    proc = subprocess.run(command, cwd=repo, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env, check=False)
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise VerificationError(
            f"allow-listed ledger validator failed with exit {proc.returncode}: {stderr}")
    return {
        "source": "allow_listed_validator_run",
        "command": command,
        "exit_code": 0,
        "stdout_sha256": _sha256(proc.stdout),
        "stderr_sha256": _sha256(proc.stderr),
    }


def verify_post(repository: Path, manifest: Path, candidate: Path,
                expected_manifest_sha256: str, expected_first_parent: str,
                expected_second_parent: str, merge_commit: str,
                allowed_first_parent_paths: Iterable[str],
                ledger_validation_result: Path | None = None,
                run_ledger_validator: bool = False) -> dict[str, Any]:
    repo = repository.resolve(strict=True)
    git = GitRepository(repo)
    expected_second = _require_hex(expected_second_parent, HEX40,
                                   "expected second parent")
    contract = _load_contract(repo, manifest, candidate,
                              expected_manifest_sha256, expected_second)
    details = _verify_frozen_inputs(
        git, contract, expected_first_parent, expected_second,
        allowed_first_parent_paths)
    merge = git.exact_commit(merge_commit, "merge commit")
    parent_line = git.run("rev-list", "--parents", "-n", "1", merge)
    parents = parent_line.decode("ascii").strip().split()
    expected_parents = [merge, details["first_parent"], details["second_parent"]]
    if parents != expected_parents:
        raise VerificationError(
            f"merge must have exactly two ordered parents {expected_parents[1:]}; "
            f"got {parents[1:]}")

    merge_base_tree, first_tree, second_tree = details.pop("trees")
    expected_tree = _expected_tree(contract, merge_base_tree, first_tree, second_tree)
    observed_tree = git.tree(merge)
    if observed_tree != expected_tree:
        changed = sorted(
            path for path in set(observed_tree) | set(expected_tree)
            if observed_tree.get(path) != expected_tree.get(path))
        raise VerificationError(f"merge tree differs from exact reconstructed tree at {changed}")

    candidate_data = (repo / contract.candidate_path).read_bytes()
    candidate_resolution = next(
        item for item in contract.resolutions
        if item.selection == "pre_reviewed_neutral_third_body")
    merged_candidate = git.run("cat-file", "blob", f"{merge}:{candidate_resolution.path}")
    if merged_candidate != candidate_data:
        raise VerificationError("canonical merged goal is not byte-identical to candidate")

    marker_args: list[str] = ["grep", "-n", "-I"]
    for marker in MARKER_PATTERNS:
        marker_args.extend(["-e", marker])
    marker_args.extend([merge, "--"])
    markers = git.run(*marker_args, allowed_returncodes=(0, 1))
    if markers:
        first_match = markers.decode("utf-8", errors="replace").splitlines()[0]
        raise VerificationError(f"merge tree contains a conflict marker: {first_match}")

    git.require_clean_at(merge)
    if (ledger_validation_result is None) == (not run_ledger_validator):
        raise VerificationError(
            "post mode requires exactly one of a ledger-validation result or "
            "--run-ledger-validator")
    if ledger_validation_result is not None:
        ledger = _check_ledger_result(ledger_validation_result, merge)
    else:
        ledger = _run_ledger_validator(repo)

    return {
        "schema": "crypto.autoresearch.exact_merge_certificate.v1",
        "mode": "post",
        "status": "PASS",
        "repository": os.fspath(repo),
        "manifest_path": contract.manifest_path,
        "manifest_sha256": contract.manifest_sha256,
        "candidate_path": contract.candidate_path,
        "candidate_sha256": contract.candidate_sha256,
        "candidate_size_bytes": contract.candidate_size,
        "candidate_git_blob_oid_sha1": contract.candidate_oid,
        **details,
        "merge_commit": merge,
        "ordered_parents": expected_parents[1:],
        "merge_tree_entry_count": len(observed_tree),
        "candidate_bytes_equal": True,
        "unmerged_entries": 0,
        "conflict_markers": 0,
        "repository_clean": True,
        "ledger_validation": ledger,
        "experiment_runs": 0,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("pre", "post"))
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--expected-first-parent", required=True)
    parser.add_argument("--expected-second-parent", required=True)
    parser.add_argument(
        "--first-parent-path", action="append", default=[],
        help="one exact reviewed path changed after the repair base; repeat for every path")
    parser.add_argument("--merge-commit", help="required in post mode")
    ledger = parser.add_mutually_exclusive_group()
    ledger.add_argument("--ledger-validation-result", type=Path)
    ledger.add_argument("--run-ledger-validator", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.mode == "pre":
            if args.merge_commit or args.ledger_validation_result or args.run_ledger_validator:
                raise VerificationError("post-only arguments are forbidden in pre mode")
            result = verify_pre(
                args.repository, args.manifest, args.candidate,
                args.expected_manifest_sha256, args.expected_first_parent,
                args.expected_second_parent, args.first_parent_path)
        else:
            if not args.merge_commit:
                raise VerificationError("--merge-commit is required in post mode")
            result = verify_post(
                args.repository, args.manifest, args.candidate,
                args.expected_manifest_sha256, args.expected_first_parent,
                args.expected_second_parent, args.merge_commit,
                args.first_parent_path, args.ledger_validation_result,
                args.run_ledger_validator)
    except (VerificationError, OSError) as exc:
        print(json.dumps({
            "schema": "crypto.autoresearch.exact_merge_certificate.v1",
            "mode": args.mode,
            "status": "FAIL",
            "error": str(exc),
            "experiment_runs": 0,
        }, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
