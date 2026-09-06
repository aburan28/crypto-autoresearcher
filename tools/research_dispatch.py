#!/usr/bin/env python3
"""Validate and render a bounded, artifact-driven subagent dispatch queue."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Protocol, Sequence


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orchestration.research_budget import enforce_research_budget, agent_wall_limit

SCHEMA = "crypto.autoresearch.dispatch_queue.v1"
PLAN_SCHEMA = "crypto.autoresearch.dispatch_plan.v1"

# Hard ceiling on queue.max_concurrent. REMOVED (None = uncapped) on the
# user's EXPLICIT DIRECTION of 2026-08-05: "remove the concurrent limit from
# the code rules." Previously fixed at 3. THE AUTHORIZATION IS THE USER'S AND
# IT IS NOT A COORDINATOR SELF-GRANT, same footing as the maximum_batches
# amendment on GOAL-AES-003's campaign_budget.
#
# What this does NOT relax: a queue must still declare a positive integer
# max_concurrent; write_scope conflict detection and archive-must-run-alone
# isolation are unaffected; nothing here waives per-task budgets or the
# review requirement on claim-changing results.
#
# The risk this ceiling existed to bound is on the record, not removed by
# removing the check: GOAL-AES-003 BATCH-002 ran three producers on a 4-core
# machine against the goal's own instruction that a batch wait rather than
# run degraded, load average reached 13, one producer's entire first segment
# produced zero numbers and another lost five of eight trials to timeouts
# (DEC-20260802-b226fb budget_accounting). A queue that raises
# max_concurrent above the machine's real headroom will reproduce that
# failure; the Coordinator dispatching it is responsible for sizing it to
# the environment, the same way sizing was always the Coordinator's job
# within the old ceiling.
MAX_CONCURRENT_CEILING: int | None = None
ROLES = {
    "coordinator",
    "executor",
    "reviewer",
    "validator",
    "red-team",
    "idea-generator",
}
INDEPENDENT_REVIEW_ROLES = {"reviewer", "validator", "red-team"}
TERMINAL_STATES = {"completed", "failed", "invalid", "cancelled"}
STATES = {"queued", "running", "blocked"} | TERMINAL_STATES
ARCHIVE_KINDS = {"snapshot", "ledger"}
ARCHIVE_BINDING_MODES = {"commit", "content_first"}
FAILURE_PROVENANCE_ARCHIVE_KIND = "terminal_failure_provenance_archive"
SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{7,64}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class DispatchError(ValueError):
    """Raised when a dispatch queue cannot be safely scheduled."""


class RepositoryVerifier(Protocol):
    """Verifies the Git receipt for a completed archival task."""

    def verify_archive(self, task: dict[str, Any], expected_paths: Sequence[str]) -> None:
        """Raise DispatchError unless ``task`` has the required archive commit."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "ascii"
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def require_text(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DispatchError(f"{location}.{field} must be nonempty text")


def require_text_list(
    record: dict[str, Any], field: str, location: str, *, allow_empty: bool = False
) -> None:
    value = record.get(field)
    if not isinstance(value, list) or (not allow_empty and not value) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        qualifier = "a text list" if allow_empty else "a nonempty text list"
        raise DispatchError(f"{location}.{field} must be {qualifier}")


def require_positive_number(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise DispatchError(f"{location}.{field} must be a positive number")


def declares_zero_compute(budget: dict[str, Any]) -> bool:
    """True when a handoff budget DECLARES that its task runs no experiments.

    Coordinator archive tasks, and the review tasks that only read committed
    artifacts, consume no experiment compute. They said so -- GOAL-ECDLP-001's
    BATCH-e6c1c9 sets `experiment_maximum_runs: 0` and GOAL-MD5-001's
    BATCH-ebac02 sets `maximum_runs: 0`, each with a note citing the committed
    campaign-budget amendment that authorised it -- and then failed validation
    anyway, because `wall_clock_seconds` and `memory_gb` were unconditionally
    required to be positive. Both goals sat in `needs_repair`, undispatchable,
    over a compute ceiling for compute that is never spent.

    The declaration is the contract, and it is checkable: a task claiming zero
    runs may omit the wall-clock and memory ceilings that bound runs. A task
    that runs anything at all is bounded exactly as it always was.
    """

    for field in ("experiment_maximum_runs", "maximum_runs"):
        value = budget.get(field)
        if isinstance(value, int) and not isinstance(value, bool) and value == 0:
            return True
    return False


def parse_timestamp(value: Any, location: str) -> datetime:
    """Parse an ISO-8601 timestamp, tz-aware output always.

    A naive input (no offset) is rejected rather than assumed UTC: this
    queue is read by whichever worktree's session picks it up next, and a
    naive timestamp compared against another timezone silently compares the
    wrong instants. Every other timestamp in this program's records is
    explicit for the same reason (docs/evidence-and-reproducibility.md).
    """
    if not isinstance(value, str) or not value:
        raise DispatchError(f"{location} must be an ISO-8601 timestamp string")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as error:
        raise DispatchError(f"{location} is not a valid ISO-8601 timestamp: {error}") from None
    if parsed.tzinfo is None:
        raise DispatchError(f"{location} must carry an explicit UTC offset (or 'Z')")
    return parsed.astimezone(timezone.utc)


def validate_lease(task: dict[str, Any], location: str) -> None:
    """Validate the optional lease a `running` task may carry.

    A lease is never required -- every task record written before this field
    existed has none, and that must keep meaning exactly what it always did:
    a `running` task with no lease never expires under this mechanism. Only a
    task that opts in by carrying one can be reclaimed automatically.

    Presence outside `running` is refused rather than ignored: a lease left on
    a task after it was manually reset to `queued`/a terminal state is stale
    data nobody will notice, which is the exact failure mode a lease exists to
    catch -- and it should not be able to hide inside the field meant to fix
    it.
    """
    lease = task.get("lease")
    if lease is None:
        return
    if task["state"] != "running":
        raise DispatchError(f"{location}.lease is set but state is not \"running\"")
    if not isinstance(lease, dict):
        raise DispatchError(f"{location}.lease must be an object")
    require_text(lease, "owner", f"{location}.lease")
    epoch = lease.get("epoch")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
        raise DispatchError(f"{location}.lease.epoch must be a positive integer")
    acquired_at = parse_timestamp(lease.get("acquired_at"), f"{location}.lease.acquired_at")
    expires_at = parse_timestamp(lease.get("expires_at"), f"{location}.lease.expires_at")
    if expires_at <= acquired_at:
        raise DispatchError(f"{location}.lease.expires_at must be after lease.acquired_at")


def lease_is_expired(task: dict[str, Any], now: datetime) -> bool:
    lease = task.get("lease")
    if lease is None:
        return False
    return now >= parse_timestamp(lease["expires_at"], "lease.expires_at")


def _validate_path_text(path: str, location: str) -> tuple[PurePosixPath, str]:
    if not isinstance(path, str) or not path or path != path.strip():
        raise DispatchError(f"{location} must be a safe repository-relative path")
    if any(character in path for character in ("\x00", "\n", "\r", "\t")):
        raise DispatchError(f"{location} must be a safe repository-relative path")
    candidate = PurePosixPath(path)
    normalized = candidate.as_posix()
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or normalized in {"", "."}
        or path.startswith("./")
    ):
        raise DispatchError(f"{location} must be a safe repository-relative path")
    return candidate, normalized


def validate_scope(path: str, location: str) -> str:
    """Return a canonical repository-relative scope, allowing a trailing slash."""

    source = path[:-1] if isinstance(path, str) and path.endswith("/") else path
    _, normalized = _validate_path_text(source, location)
    return normalized


def validate_artifact_path(path: str, location: str) -> str:
    """Validate one exact, non-directory repository-relative artifact path."""

    if not isinstance(path, str) or path.endswith("/"):
        raise DispatchError(f"{location} must be an exact safe repository-relative file path")
    _, normalized = _validate_path_text(path, location)
    if normalized != path:
        raise DispatchError(f"{location} must be an exact safe repository-relative file path")
    return normalized


def path_within_scope(path: str, scope: str) -> bool:
    return path == scope or path.startswith(scope + "/")


def paths_within_scopes(paths: Sequence[str], scopes: Sequence[str]) -> bool:
    return all(any(path_within_scope(path, scope) for scope in scopes) for path in paths)


def scope_overlaps(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def is_archive(task: dict[str, Any]) -> bool:
    return "archive" in task


def _completed_failure_successor_exists(
    failed_id: str,
    task: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
) -> bool:
    """Return whether an archived failed task has a completed successor chain."""

    source_ids = set(task["archive"]["source_task_ids"])
    frontier = [failed_id]
    visited: set[str] = set()
    while frontier:
        predecessor = frontier.pop()
        if predecessor in visited:
            continue
        visited.add(predecessor)
        for candidate in by_id.values():
            if (
                candidate["id"] in source_ids
                and candidate.get("supersedes_failed_task") == predecessor
            ):
                if (
                    candidate["state"] == "completed"
                    and candidate["role"] in INDEPENDENT_REVIEW_ROLES
                ):
                    return True
                frontier.append(candidate["id"])
    return False


def _failure_provenance_dependencies(
    task: dict[str, Any], by_id: dict[str, dict[str, Any]]
) -> set[str]:
    """Return terminal failures an isolated archive may preserve without unblocking work."""

    exception = task.get("dispatch_exception")
    if not isinstance(exception, dict) or exception.get("kind") != FAILURE_PROVENANCE_ARCHIVE_KIND:
        return set()
    if not is_archive(task) or task["archive"]["kind"] != "ledger":
        raise DispatchError(
            f"task {task['id']} may use {FAILURE_PROVENANCE_ARCHIVE_KIND} only on a ledger archive"
        )
    if task["role"] != "coordinator":
        raise DispatchError(f"failure-provenance archive {task['id']} must be coordinator-owned")
    if (
        exception.get("scientific_effect") != "none"
        or exception.get("failed_tasks_reclassified_completed") is not False
        or exception.get("successor_review_completed_independently") is not True
    ):
        raise DispatchError(
            f"failure-provenance archive {task['id']} has an invalid dispatch_exception boundary"
        )
    failed = {
        dependency
        for dependency in task["depends_on"]
        if by_id[dependency]["state"] in {"failed", "invalid", "cancelled"}
    }
    if not failed:
        raise DispatchError(
            f"failure-provenance archive {task['id']} must name a terminal failed dependency"
        )
    source_ids = set(task["archive"]["source_task_ids"])
    if not failed.issubset(source_ids):
        raise DispatchError(
            f"failure-provenance archive {task['id']} may exempt only archived source tasks"
        )
    missing_successors = sorted(
        dependency
        for dependency in failed
        if not _completed_failure_successor_exists(dependency, task, by_id)
    )
    if missing_successors:
        raise DispatchError(
            f"failure-provenance archive {task['id']} lacks a completed independent successor "
            f"for {missing_successors}"
        )
    return failed


def assert_acyclic(graph: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise DispatchError(f"task dependency graph has a cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def validate_inference(handoff: dict[str, Any], role: str | None,
                       location: str) -> None:
    """Check the optional `inference` block against the policy contract.

    A task may omit the block (many predate it), but a policy that IS named
    must exist, and an independent-review role must not be routed to a policy
    that permits changing official state. A typo here would otherwise surface
    only when the task was already running.
    """
    inference = handoff.get("inference")
    if inference is None:
        return
    if not isinstance(inference, dict):
        raise DispatchError(f"{location}.inference must be an object")
    policy_id = inference.get("policy")
    if policy_id is None:
        return
    try:
        from orchestration.adapter import load as load_inference_config
    except Exception:                      # adapter unavailable: nothing to check
        return
    try:
        config = load_inference_config()
        canonical = config.canonical_policy(policy_id)
    except Exception as exc:
        raise DispatchError(f"{location}.inference.policy: {exc}") from None
    policy = config.policy_table[canonical]

    effort = inference.get("reasoning_effort")
    if effort is not None:
        if effort not in config.effort_order:
            raise DispatchError(
                f"{location}.inference.reasoning_effort {effort!r} is not in the "
                f"lattice {config.effort_order}")
        # Calibrating a review down is the one trade this program never makes
        # silently: it is the gate protecting every claim in the ledger.
        floor = (policy.get("requires") or {}).get("reasoning_effort")
        if (policy.get("independent_session_required")
                and config.effort_order.index(effort)
                < config.effort_order.index(floor)):
            raise DispatchError(
                f"{location}.inference.reasoning_effort {effort!r} is below the "
                f"{floor!r} floor for review policy {policy_id!r}; a review may "
                f"not be calibrated down to save budget")

    if role in INDEPENDENT_REVIEW_ROLES and not policy.get(
            "independent_session_required"):
        raise DispatchError(
            f"{location}.inference.policy {policy_id!r} does not require an "
            f"independent session, but role {role!r} is an independent reviewer")
    if role not in (None, "coordinator") and policy.get("may_change_official_state"):
        raise DispatchError(
            f"{location}.inference.policy {policy_id!r} may change official "
            f"state, which role {role!r} may not")


def validate_handoff(task: dict[str, Any], location: str) -> None:
    handoff = task.get("handoff")
    if not isinstance(handoff, dict):
        raise DispatchError(f"{location}.handoff must be an object")
    validate_inference(handoff, task.get("role"), f"{location}.handoff")
    for field in ("objective", "uncertainty_reduced"):
        require_text(handoff, field, f"{location}.handoff")
    for field in ("inputs", "constraints", "deliverables", "completion_gate"):
        require_text_list(handoff, field, f"{location}.handoff")
    budget = handoff.get("budget")
    if not isinstance(budget, dict):
        raise DispatchError(f"{location}.handoff.budget must be an object")
    try:
        enforced = enforce_research_budget(
            budget, repo_root=Path(__file__).resolve().parents[1], target_id=handoff.get("id"))
        agent_wall_limit(handoff, repo_root=Path(__file__).resolve().parents[1])
    except ValueError as exc:
        raise DispatchError(f"{location}: {exc}") from exc
    zero_compute = declares_zero_compute(budget)
    for field in ("wall_clock_seconds", "memory_gb"):
        # Null time estimates are advisory. Memory remains machine protection;
        # a declared zero-compute task may leave both estimates null.
        if budget.get(field) is None and (zero_compute or (field == "wall_clock_seconds" and not enforced)):
            continue
        require_positive_number(budget, field, f"{location}.handoff.budget")
    maximum_runs = budget.get("maximum_runs")
    minimum_runs = 0 if zero_compute else 1
    if maximum_runs is None and not enforced:
        return
    if (not isinstance(maximum_runs, int) or isinstance(maximum_runs, bool)
            or maximum_runs < minimum_runs):
        qualifier = (
            "a non-negative integer" if zero_compute else "a positive integer")
        raise DispatchError(
            f"{location}.handoff.budget.maximum_runs must be {qualifier}")


def _require_optional_sha(value: Any, location: str) -> None:
    if value is not None and (not isinstance(value, str) or not SHA_PATTERN.fullmatch(value)):
        raise DispatchError(f"{location} must be null or a Git commit SHA")


def validate_archive_shape(task: dict[str, Any], location: str) -> None:
    archive = task.get("archive")
    if not isinstance(archive, dict):
        raise DispatchError(f"{location}.archive must be an object")
    if task["role"] != "coordinator":
        raise DispatchError(f"{location} archive tasks must have the coordinator role")
    if task["review_required"]:
        raise DispatchError(f"{location} archive tasks cannot be claim-relevant producers")
    for field in (
        "kind",
        "source_task_ids",
        "commit_sha",
        "parent_sha",
        "path_sha256",
        "record_ids",
    ):
        if field not in archive:
            raise DispatchError(f"{location}.archive.{field} is required")
    if archive["kind"] not in ARCHIVE_KINDS:
        raise DispatchError(f"{location}.archive.kind must be snapshot or ledger")
    # Legacy archives are commit-bound.  `content_first` is intentionally
    # opt-in: it is for source packages committed before their archive task
    # ran, where one exact changed-path commit cannot express intact custody.
    # Never infer this from a failed commit-scope check.
    binding_mode = archive.get("binding_mode", "commit")
    if binding_mode not in ARCHIVE_BINDING_MODES:
        raise DispatchError(
            f"{location}.archive.binding_mode must be commit or content_first"
        )
    require_text_list(archive, "source_task_ids", f"{location}.archive")
    if len(archive["source_task_ids"]) != len(set(archive["source_task_ids"])):
        raise DispatchError(f"{location}.archive.source_task_ids contains duplicates")
    require_text_list(archive, "record_ids", f"{location}.archive", allow_empty=True)
    if len(archive["record_ids"]) != len(set(archive["record_ids"])):
        raise DispatchError(f"{location}.archive.record_ids contains duplicates")
    _require_optional_sha(archive["commit_sha"], f"{location}.archive.commit_sha")
    _require_optional_sha(archive["parent_sha"], f"{location}.archive.parent_sha")
    hashes = archive["path_sha256"]
    if not isinstance(hashes, dict):
        raise DispatchError(f"{location}.archive.path_sha256 must be an object")
    normalized_hashes: dict[str, str] = {}
    for path, value in hashes.items():
        normalized = validate_artifact_path(path, f"{location}.archive.path_sha256 path")
        if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            raise DispatchError(
                f"{location}.archive.path_sha256[{path!r}] must be a lowercase SHA-256"
            )
        normalized_hashes[normalized] = value
    archive["path_sha256"] = normalized_hashes


def _ledger_record_matches_path(record_ids: Sequence[str], path: str) -> bool:
    """Ledger record identifiers must be visible in their immutable artifact names."""

    filename = PurePosixPath(path).name
    return any(record_id in filename for record_id in record_ids)


def _validate_ledger_archive(task: dict[str, Any]) -> None:
    archive = task["archive"]
    if archive["kind"] != "ledger":
        return
    evidence = [path for path in task["artifact_paths"] if path.startswith("ledger/evidence/")]
    decisions = [path for path in task["artifact_paths"] if path.startswith("ledger/decisions/")]
    if not decisions:
        raise DispatchError(
            f"ledger archive {task['id']} must own exact artifacts under "
            "ledger/decisions/"
        )
    # CORR-20260822-7e98b5 HD-1: a ledger archive's entire content can BE the
    # decision (a REVISE/block, a supersede, an infra pause, a protocol
    # amendment, a correction) -- it does not always promote an evidence
    # record. Only require an evidence path when the archive's own record_ids
    # actually name an EV-* record (the dangling-reference catch below still
    # applies once evidence is expected).
    if any(rid.startswith("EV-") for rid in archive["record_ids"]) and not evidence:
        raise DispatchError(
            f"ledger archive {task['id']} names an EV-* record_id but owns no "
            "artifact under ledger/evidence/"
        )
    if not archive["record_ids"]:
        raise DispatchError(f"ledger archive {task['id']} must include relevant ledger record IDs")
    for path in evidence + decisions:
        if not _ledger_record_matches_path(archive["record_ids"], path):
            raise DispatchError(
                f"ledger archive {task['id']} record_ids must include the record ID for {path}"
            )


def _validate_review_chains(
    tasks: Sequence[dict[str, Any]],
    assignments: dict[str, dict[str, Any]],
) -> None:
    """Preserve independent review while forcing the archival claim lifecycle."""

    for producer in tasks:
        if not producer["review_required"]:
            continue
        reviews = [
            successor
            for successor in tasks
            if producer["id"] in successor["depends_on"]
            and successor["role"] in INDEPENDENT_REVIEW_ROLES
        ]
        if not reviews:
            raise DispatchError(
                f"{producer['id']} requires an independent reviewer, validator, or red-team successor"
            )
        snapshot = assignments[producer["id"]]
        if snapshot["archive"]["kind"] != "snapshot":
            raise DispatchError(
                f"claim-relevant producer {producer['id']} must have a snapshot archive successor"
            )
        for review in reviews:
            if snapshot["id"] not in review["depends_on"]:
                raise DispatchError(
                    f"independent review {review['id']} for {producer['id']} must depend on "
                    f"snapshot archive {snapshot['id']}"
                )
        review_archives = {assignments[review["id"]]["id"] for review in reviews}
        if len(review_archives) != 1:
            raise DispatchError(
                f"claim-relevant producer {producer['id']} requires one ledger archive successor "
                "for every direct independent review"
            )
        ledger = assignments[reviews[0]["id"]]
        if ledger["archive"]["kind"] != "ledger":
            raise DispatchError(
                f"claim-relevant producer {producer['id']} requires a ledger archive after review"
            )
        review_ids = {review["id"] for review in reviews}
        if not review_ids.issubset(set(ledger["depends_on"])):
            raise DispatchError(
                f"ledger archive {ledger['id']} must directly depend on every independent review "
                f"of {producer['id']}"
            )


def validate_queue(
    queue: Any, *, repository_verifier: RepositoryVerifier | None = None
) -> dict[str, dict[str, Any]]:
    if not isinstance(queue, dict):
        raise DispatchError("queue must be an object")
    if queue.get("schema") != SCHEMA:
        raise DispatchError(f"queue.schema must be {SCHEMA}")
    require_text(queue, "objective", "queue")
    if "goal_id" in queue:
        require_text(queue, "goal_id", "queue")
    maximum = queue.get("max_concurrent")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
        raise DispatchError("queue.max_concurrent must be a positive integer")
    if MAX_CONCURRENT_CEILING is not None and maximum > MAX_CONCURRENT_CEILING:
        raise DispatchError(
            f"queue.max_concurrent must be an integer 1..{MAX_CONCURRENT_CEILING}"
        )
    tasks = queue.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise DispatchError("queue.tasks must be a nonempty list")

    ids: list[str] = []
    artifact_owners: dict[str, str] = {}
    for index, task in enumerate(tasks):
        location = f"tasks[{index}]"
        if not isinstance(task, dict):
            raise DispatchError(f"{location} must be an object")
        for field in ("id", "title"):
            require_text(task, field, location)
        if task.get("role") not in ROLES:
            raise DispatchError(f"{location}.role is invalid")
        if task.get("state") not in STATES:
            raise DispatchError(f"{location}.state is invalid")
        if not isinstance(task.get("review_required"), bool):
            raise DispatchError(f"{location}.review_required must be boolean")
        priority = task.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 100:
            raise DispatchError(f"{location}.priority must be an integer 0..100")
        require_text_list(task, "depends_on", location, allow_empty=True)
        if len(task["depends_on"]) != len(set(task["depends_on"])):
            raise DispatchError(f"{location}.depends_on contains duplicates")
        for field in ("read_scope", "write_scope"):
            require_text_list(task, field, location)
        task["read_scope"] = [
            validate_scope(path, f"{location}.read_scope") for path in task["read_scope"]
        ]
        task["write_scope"] = [
            validate_scope(path, f"{location}.write_scope") for path in task["write_scope"]
        ]
        if len(task["read_scope"]) != len(set(task["read_scope"])):
            raise DispatchError(f"{location}.read_scope contains duplicates")
        if len(task["write_scope"]) != len(set(task["write_scope"])):
            raise DispatchError(f"{location}.write_scope contains duplicates")
        require_text_list(task, "artifact_paths", location)
        task["artifact_paths"] = [
            validate_artifact_path(path, f"{location}.artifact_paths")
            for path in task["artifact_paths"]
        ]
        if len(task["artifact_paths"]) != len(set(task["artifact_paths"])):
            raise DispatchError(f"{location}.artifact_paths contains duplicates")
        if not paths_within_scopes(task["artifact_paths"], task["write_scope"]):
            raise DispatchError(f"{location}.artifact_paths must be inside its write_scope")
        for path in task["artifact_paths"]:
            previous_owner = artifact_owners.get(path)
            if previous_owner is not None:
                raise DispatchError(
                    f"artifact path {path} is owned by both {previous_owner} and {task['id']}"
                )
            artifact_owners[path] = task["id"]
        validate_handoff(task, location)
        validate_lease(task, location)
        if is_archive(task):
            validate_archive_shape(task, location)
        ids.append(task["id"])

    if len(ids) != len(set(ids)):
        raise DispatchError("task IDs must be unique")
    by_id = {task["id"]: task for task in tasks}
    for task in tasks:
        for dependency in task["depends_on"]:
            if dependency not in by_id:
                raise DispatchError(f"{task['id']} has unknown dependency {dependency}")
            if dependency == task["id"]:
                raise DispatchError(f"{task['id']} depends on itself")
    assert_acyclic({task["id"]: task["depends_on"] for task in tasks})

    archives = [task for task in tasks if is_archive(task)]
    non_archives = [task for task in tasks if not is_archive(task)]
    assignments: dict[str, dict[str, Any]] = {}
    archive_expected_paths: dict[str, list[str]] = {}
    for archive_task in archives:
        archive = archive_task["archive"]
        source_paths: list[str] = []
        for source_id in archive["source_task_ids"]:
            source = by_id.get(source_id)
            if source is None:
                raise DispatchError(f"archive task {archive_task['id']} has unknown source {source_id}")
            if is_archive(source):
                raise DispatchError(
                    f"archive task {archive_task['id']} may only archive non-archive source tasks"
                )
            if source_id not in archive_task["depends_on"]:
                raise DispatchError(
                    f"archive task {archive_task['id']} must directly depend on source {source_id}"
                )
            if source_id in assignments:
                raise DispatchError(
                    f"non-archive task {source_id} is assigned to both "
                    f"{assignments[source_id]['id']} and {archive_task['id']}"
                )
            assignments[source_id] = archive_task
            source_paths.extend(source["artifact_paths"])
        if not paths_within_scopes(source_paths, archive_task["read_scope"]):
            raise DispatchError(
                f"archive task {archive_task['id']} read_scope must cover every source artifact path"
            )
        expected_paths = sorted(set(archive_task["artifact_paths"]) | set(source_paths))
        archive_expected_paths[archive_task["id"]] = expected_paths
        hash_paths = set(archive["path_sha256"])
        expected_set = set(expected_paths)
        if not hash_paths.issubset(expected_set):
            raise DispatchError(
                f"archive task {archive_task['id']} path_sha256 contains paths outside its commit scope"
            )
        if archive_task["state"] == "completed":
            if archive["commit_sha"] is None:
                raise DispatchError(
                    f"completed archive task {archive_task['id']} requires archive.commit_sha"
                )
            if hash_paths != expected_set:
                raise DispatchError(
                    f"completed archive task {archive_task['id']} path_sha256 must cover every "
                    "archive and source artifact"
                )

    for task in non_archives:
        if task["id"] not in assignments:
            raise DispatchError(
                f"non-archive task {task['id']} must be assigned exactly once to an archive task"
            )
    for archive_task in archives:
        _validate_ledger_archive(archive_task)
    _validate_review_chains(tasks, assignments)

    for archive_task in archives:
        if archive_task["state"] != "completed":
            continue
        if repository_verifier is None:
            raise DispatchError(
                f"completed archive task {archive_task['id']} requires a repository verifier"
            )
        repository_verifier.verify_archive(
            archive_task, archive_expected_paths[archive_task["id"]]
        )

    for task in tasks:
        if task["state"] == "running":
            incomplete = blockers(task, by_id)
            if incomplete:
                raise DispatchError(
                    f"running task {task['id']} has incomplete dependencies {incomplete}"
                )

    running = [task for task in tasks if task["state"] == "running"]
    if len(running) > maximum:
        raise DispatchError("running task count exceeds queue.max_concurrent")
    running_archives = [task for task in running if is_archive(task)]
    if running_archives and len(running) != 1:
        raise DispatchError(f"running archive task {running_archives[0]['id']} must run alone")
    for index, left in enumerate(running):
        for right in running[index + 1 :]:
            if any(
                scope_overlaps(left_scope, right_scope)
                for left_scope in left["write_scope"]
                for right_scope in right["write_scope"]
            ):
                raise DispatchError(
                    f"running tasks {left['id']} and {right['id']} have overlapping write scopes"
                )
    return by_id


def blockers(task: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> list[str]:
    output: list[str] = []
    preserved_failures = _failure_provenance_dependencies(task, by_id)
    for dependency in task["depends_on"]:
        state = by_id[dependency]["state"]
        if state != "completed" and dependency not in preserved_failures:
            output.append(f"dependency_not_completed:{dependency}:{state}")
    if task["state"] == "blocked":
        output.append("task_marked_blocked")
    return output


def conflicts(task: dict[str, Any], selected: Sequence[dict[str, Any]]) -> list[str]:
    conflicting_ids = []
    for other in selected:
        if any(
            scope_overlaps(task_scope, other_scope)
            for task_scope in task["write_scope"]
            for other_scope in other["write_scope"]
        ):
            conflicting_ids.append(other["id"])
    return sorted(conflicting_ids)


def _defer(
    deferred: dict[str, list[str]], task_id: str, reasons: Sequence[str]
) -> None:
    current = deferred.setdefault(task_id, [])
    for reason in reasons:
        if reason not in current:
            current.append(reason)


def _ready_queued(
    queue: dict[str, Any], by_id: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    queued = [
        task
        for task in queue["tasks"]
        if task["state"] == "queued" and not blockers(task, by_id)
    ]
    return sorted(queued, key=lambda task: (-task["priority"], task["id"]))


CLAIM_OVERLAY_STATES = {"live", "expired", "released", "orphan_release"}


def apply_claims(
    queue: dict[str, Any],
    claims: dict[str, dict[str, Any]] | None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Overlay write-once task claims (tools/goal_lanes.py) on a queue copy.

    The queue file is the Coordinator's record and is never edited here. The
    overlay only changes what this plan ADMITS, so several sessions reading
    the same committed queue see each other's holds without any of them
    writing it:

      live claim on a queued task      -> treated as `running` with a lease
                                          derived from the claim (scope held,
                                          counts toward max_concurrent)
      expired claim on a queued task   -> left `queued` (scope free, so the
                                          task is offered again and the next
                                          session claims it at epoch+1), and
                                          listed under `expired_leases` so the
                                          owner's silence is on the record
      release `completed` (producer)   -> treated as `completed`, so its
                                          successors become ready for whoever
                                          claims them next
      release `completed` (archive)    -> NOT overlaid: an archive is complete
                                          only when its commit verifies, and
                                          that binding lives in the queue's own
                                          archive block, written by the
                                          Coordinator at archive time
      release failed|abandoned         -> left `queued`, scope free, reported
      any claim on a non-queued task   -> ignored; the queue already records
                                          more than the claim does

    Returns the overlaid copy and a per-task report for the plan.
    """
    overlaid = copy.deepcopy(queue)
    report: dict[str, dict[str, Any]] = {}
    if not claims:
        return overlaid, report
    by_id = {task["id"]: task for task in overlaid["tasks"] if isinstance(task, dict) and "id" in task}
    # Two passes: completions first, so a hold on a successor is judged against
    # the successor's dependencies AS THIS READER SEES THEM. A claim made from a
    # worktree that had already fetched a completion this one has not is not an
    # error in the queue; it is a fact this plan cannot yet admit, and it is
    # reported as such rather than crashing the render.
    for task in overlaid["tasks"]:
        claim = claims.get(task["id"])
        if claim is None:
            continue
        status = claim.get("status")
        if status not in CLAIM_OVERLAY_STATES:
            raise DispatchError(f"claim for {task['id']} has unknown status {status!r}")
        entry = {
            "status": status,
            "owner": claim.get("owner"),
            "epoch": claim.get("epoch"),
            "expires_at": claim.get("expires_at"),
            "branch": claim.get("branch"),
            "outcome": (claim.get("release") or {}).get("outcome"),
            "applied": None,
        }
        report[task["id"]] = entry
        if task["state"] != "queued":
            entry["applied"] = f"ignored:queue_state_{task['state']}"
        elif status == "released" and entry["outcome"] == "completed" and not is_archive(task):
            task["state"] = "completed"
            entry["applied"] = "completed"
    for task in overlaid["tasks"]:
        entry = report.get(task["id"])
        if entry is None or entry["applied"] is not None:
            continue
        claim = claims[task["id"]]
        status = entry["status"]
        if status == "expired":
            entry["applied"] = "queued_after_expiry"
        elif status == "live":
            unmet = [
                dependency for dependency in task.get("depends_on", [])
                if dependency in by_id and by_id[dependency].get("state") != "completed"
            ]
            if unmet:
                entry["applied"] = "ignored:dependencies_incomplete_from_this_view:" + ",".join(unmet)
                continue
            task["state"] = "running"
            task["lease"] = {
                "owner": claim["owner"],
                "acquired_at": claim["acquired_at"],
                "expires_at": claim["expires_at"],
                "epoch": int(claim["epoch"]),
            }
            entry["applied"] = "running_with_lease"
        elif status == "released" and entry["outcome"] == "completed":
            entry["applied"] = "ignored:archive_completion_requires_queue_record"
        else:
            entry["applied"] = "queued_scope_free"
    return overlaid, report


def select(
    queue: dict[str, Any],
    *,
    repository_verifier: RepositoryVerifier | None = None,
    now: datetime | None = None,
    claims: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Select the tasks a dispatch plan admits.

    `now`, when given, is the only clock this function reads -- it is never
    sampled internally, so the same queue always produces the same plan for
    the same `now`. Passing it lets a `running` task past its own declared
    `lease.expires_at` stop being treated as holding its `write_scope`: a
    lease is opt-in (`validate_lease`), so a task with none behaves exactly
    as it always has, live or not. The task itself is left in state
    `running` in the input -- this function only ever reads the queue, and
    reverting a stale task to `queued` in the record itself is still a
    Coordinator decision, made once and recorded, not an inference redrawn on
    every dispatch run.
    """
    queue, claim_report = apply_claims(queue, claims)
    by_id = validate_queue(queue, repository_verifier=repository_verifier)
    all_running = [task for task in queue["tasks"] if task["state"] == "running"]
    expired = (
        [task for task in all_running if lease_is_expired(task, now)]
        if now is not None
        else []
    )
    expired_ids = {task["id"] for task in expired}
    running = [task for task in all_running if task["id"] not in expired_ids]
    expired_claims = [
        {
            "id": task["id"],
            "role": task["role"],
            "owner": claim_report[task["id"]]["owner"],
            "write_scope": task["write_scope"],
            "expires_at": claim_report[task["id"]]["expires_at"],
            "source": "claim",
        }
        for task in queue["tasks"]
        if claim_report.get(task["id"], {}).get("applied") == "queued_after_expiry"
    ]
    ready = _ready_queued(queue, by_id)
    ready_archives = [task for task in ready if is_archive(task)]
    selected: list[dict[str, Any]] = list(running)
    deferred: dict[str, list[str]] = {}

    running_archives = [task for task in running if is_archive(task)]
    if running_archives:
        archive_id = running_archives[0]["id"]
        for task in ready:
            _defer(deferred, task["id"], [f"archive_isolation_running:{archive_id}"])
    elif ready_archives:
        chosen = ready_archives[0]
        if running:
            running_ids = ",".join(sorted(task["id"] for task in running))
            _defer(
                deferred,
                chosen["id"],
                [f"archive_requires_isolation:running:{running_ids}"],
            )
            for task in ready_archives[1:]:
                _defer(deferred, task["id"], [f"archive_priority_deferred:{chosen['id']}"])
            for task in ready:
                if not is_archive(task):
                    _defer(
                        deferred,
                        task["id"],
                        [f"archive_pending_isolation:{chosen['id']}"],
                    )
        else:
            selected = [chosen]
            for task in ready_archives[1:]:
                _defer(deferred, task["id"], [f"archive_priority_deferred:{chosen['id']}"])
            for task in ready:
                if not is_archive(task):
                    _defer(
                        deferred,
                        task["id"],
                        [f"archive_requires_isolation:{chosen['id']}"],
                    )
    else:
        for task in ready:
            if len(selected) == queue["max_concurrent"]:
                _defer(deferred, task["id"], ["concurrency_cap"])
                continue
            conflicting = conflicts(task, selected)
            if conflicting:
                _defer(
                    deferred,
                    task["id"],
                    [f"write_scope_conflict:{identifier}" for identifier in conflicting],
                )
                continue
            selected.append(task)

    selected_ids = {task["id"] for task in selected}
    for task in queue["tasks"]:
        if task["id"] in selected_ids or task["state"] in TERMINAL_STATES:
            continue
        if task["state"] == "queued":
            task_blockers = blockers(task, by_id)
            if task_blockers:
                _defer(deferred, task["id"], task_blockers)
        elif task["state"] == "blocked":
            _defer(deferred, task["id"], ["task_marked_blocked"])

    dispatches = [
        {
            "id": task["id"],
            "title": task["title"],
            "role": task["role"],
            "state": task["state"],
            "priority": task["priority"],
            "review_required": task["review_required"],
            "depends_on": task["depends_on"],
            "read_scope": task["read_scope"],
            "write_scope": task["write_scope"],
            "artifact_paths": task["artifact_paths"],
            "handoff": task["handoff"],
            **({"archive": task["archive"]} if is_archive(task) else {}),
            "claim": (
                {key: claim_report[task["id"]][key] for key in ("status", "owner", "epoch", "expires_at")}
                if task["id"] in claim_report
                and claim_report[task["id"]]["applied"] == "running_with_lease"
                else None
            ),
        }
        for task in selected
    ]
    plan = {
        "schema": PLAN_SCHEMA,
        "source_schema": SCHEMA,
        "objective": queue["objective"],
        **({"goal_id": queue["goal_id"]} if "goal_id" in queue else {}),
        "source_queue_sha256": digest(queue),
        "max_concurrent": queue["max_concurrent"],
        "dispatches": dispatches,
        "deferred": [
            {"id": task_id, "reason": reasons}
            for task_id, reasons in sorted(deferred.items())
        ],
        "terminal": [
            {"id": task["id"], "state": task["state"]}
            for task in queue["tasks"]
            if task["state"] in TERMINAL_STATES
        ],
        "expired_leases": [
            {
                "id": task["id"],
                "role": task["role"],
                "owner": task["lease"]["owner"],
                "write_scope": task["write_scope"],
                "expires_at": task["lease"]["expires_at"],
            }
            for task in expired
        ] + expired_claims,
        "claims": claim_report,
        "gates": {
            "claimed_tasks_are_not_offered_to_others": all(
                task["state"] == "running" or task["id"] not in claim_report
                or claim_report[task["id"]]["applied"] != "running_with_lease"
                for task in selected
            ),
            "concurrency_cap_respected": (
                len(selected) <= queue["max_concurrent"]
                and (
                    MAX_CONCURRENT_CEILING is None
                    or queue["max_concurrent"] <= MAX_CONCURRENT_CEILING
                )
            ),
            "all_selected_dependencies_completed": all(
                not blockers(task, by_id) for task in selected
            ),
            "selected_write_scopes_do_not_overlap": all(
                not conflicts(task, selected[:index])
                for index, task in enumerate(selected)
            ),
            "archive_tasks_run_in_isolation": all(
                not is_archive(task) or len(selected) == 1 for task in selected
            ),
            "all_artifact_paths_are_exact_and_scoped": all(
                paths_within_scopes(task["artifact_paths"], task["write_scope"])
                for task in queue["tasks"]
            ),
            "archive_artifact_coverage_complete": {
                source_id
                for task in queue["tasks"]
                if is_archive(task)
                for source_id in task["archive"]["source_task_ids"]
            } == {
                task["id"] for task in queue["tasks"] if not is_archive(task)
            },
            "completed_archive_commits_verified": all(
                task["state"] != "completed"
                or (task["archive"]["commit_sha"] is not None
                    and bool(task["archive"]["path_sha256"]))
                for task in queue["tasks"]
                if is_archive(task)
            ),
            "archive_tasks_are_coordinator_owned": all(
                task["role"] == "coordinator"
                for task in queue["tasks"]
                if is_archive(task)
            ),
            "terminal_noncompleted_tasks_do_not_unblock_successors": all(
                not blockers(task, by_id)
                for task in selected
            ),
            "claim_relevant_tasks_have_independent_review": all(
                any(
                    task["id"] in successor["depends_on"]
                    and successor["role"] in INDEPENDENT_REVIEW_ROLES
                    for successor in queue["tasks"]
                )
                for task in queue["tasks"]
                if task["review_required"]
            ),
        },
    }
    # Keep declared and legacy content-only bindings visible in the canonical
    # plan (and therefore its digest), rather than adding them only during CLI
    # rendering after the plan has been hashed.
    content_only = getattr(repository_verifier, "content_only_archives", None)
    if content_only:
        plan["content_only_archives"] = content_only
    plan["plan_sha256"] = digest(plan)
    return plan


def markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Dynamic Subagent Dispatch Plan",
        "",
        plan["objective"],
        "",
        "## Ready Tasks",
        "",
        "| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |",
        "|---|---|---|---:|---|---|---|",
    ]
    if not plan["dispatches"]:
        lines.append("| none | - | - | - | - | - | - |")
    for task in plan["dispatches"]:
        lines.append(
            f"| `{task['id']}` | {task['role']} | {task['state']} | {task['priority']} | "
            f"{', '.join(task['depends_on']) or '-'} | {', '.join(task['artifact_paths'])} | "
            f"{', '.join(task['write_scope'])} |"
        )
    lines.extend(["", "## Deferred or Blocked", ""])
    if not plan["deferred"]:
        lines.append("None.")
    for task in plan["deferred"]:
        lines.append(f"- `{task['id']}`: {', '.join(task['reason'])}")
    expired_leases = plan.get("expired_leases") or []
    if expired_leases:
        lines.extend(["", "## Expired Leases", "",
                      "These tasks are still `running` in the queue, but their lease expired",
                      "before `--now` -- their write_scope is no longer treated as held, so a",
                      "queued successor over the same scope was admitted instead. The task",
                      "itself is untouched: a Coordinator still records the actual terminal",
                      "state (most likely `failed`) the next time the queue is edited.",
                      "An entry marked `claim` is an expired write-once claim instead: the task",
                      "stays queued and is offered again; claim it at the next epoch.", ""])
        for item in expired_leases:
            lines.append(
                f"- `{item['id']}` ({item['role']}, {'claim' if item.get('source') == 'claim' else 'lease'} "
                f"by `{item['owner']}`, expired {item['expires_at']}): {', '.join(item['write_scope'])}"
            )
    claims = plan.get("claims") or {}
    if claims:
        lines.extend(["", "## Claims (write-once, tools/goal_lanes.py)", "",
                      "A `live` claim is another session's hold on that task's write_scope:",
                      "it is listed under Ready Tasks as `running` so you do not start it.",
                      "Start only Ready Tasks whose `claim` is null, and claim them first.", ""])
        for task_id, item in sorted(claims.items()):
            lines.append(
                f"- `{task_id}`: {item['status']} (owner `{item.get('owner')}`, epoch {item.get('epoch')}, "
                f"expires {item.get('expires_at')}) -> {item['applied']}"
            )
    degraded = plan.get("content_only_archives") or []
    if degraded:
        lines.extend(["", "## Archives verified on CONTENT only", "",
                      "These archives' commit bindings could not be reached, so they were",
                      "verified against their declared `path_sha256` instead. The content",
                      "binding held in every case below -- a mismatch would have failed.",
                      "This is the expected state after a squash merge; see",
                      "`ledger/corrections/CORR-20260802-a1f151.yaml`.", ""])
        for item in degraded:
            lines.append(f"- `{item['task_id']}`: {item['reason']} "
                         f"({item['paths_verified']} path hashes verified)")

    lines.extend(["", "## Dispatch Gates", ""])
    for gate, passed in plan["gates"].items():
        lines.append(f"- `{gate}`: {'passed' if passed else 'failed'}")
    lines.extend(["", f"Plan SHA-256: `{plan['plan_sha256']}`", ""])
    return "\n".join(lines)


# Generated artifacts, mirrored from .gitignore. An archive that declared one of
# these before they were untracked cannot have its binding to that path checked
# any more, and that is a POLICY change rather than corruption of the archive.
GENERATED_ARTIFACTS = ("knowledge/INDEX.md", "dispatch_plan.json", "dispatch_plan.md")


def _is_generated_path(path: str) -> bool:
    return any(path == g or path.endswith("/" + g) for g in GENERATED_ARTIFACTS)


class GitRepositoryVerifier:
    """Verify archive receipts using Git at one explicit repository root."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        # Archives whose commit binding was gone and which verified on content
        # alone. Surfaced in the plan so a degraded verification is never
        # silently indistinguishable from a full one.
        self.content_only_archives: list[dict[str, Any]] = []

    def _run(self, arguments: Sequence[str]) -> bytes:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except OSError as error:
            raise DispatchError(f"unable to execute git for archive verification: {error}") from error
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise DispatchError(
                f"git archive verification failed ({' '.join(arguments)}): {detail or 'unknown error'}"
            )
        return result.stdout

    def _resolve_commit(self, reference: str, task_id: str, field: str) -> str:
        try:
            return self._run(["rev-parse", "--verify", f"{reference}^{{commit}}"]).decode(
                "ascii"
            ).strip()
        except DispatchError as error:
            raise DispatchError(
                f"archive task {task_id} {field} does not resolve to a commit: {reference}"
            ) from error

    def _changed_paths(self, commit_sha: str, task_id: str) -> list[str]:
        raw = self._run(
            [
                "diff-tree",
                "--no-commit-id",
                "--no-renames",
                "--name-status",
                "-r",
                "--root",
                "-z",
                commit_sha,
            ]
        )
        fields = raw.split(b"\0")
        paths: list[str] = []
        index = 0
        while index < len(fields) - 1:
            status = fields[index]
            index += 1
            if not status:
                continue
            if index >= len(fields):
                raise DispatchError(f"archive task {task_id} has malformed Git diff output")
            path = fields[index].decode("utf-8", "surrogateescape")
            index += 1
            if status[:1] == b"D":
                raise DispatchError(
                    f"archive task {task_id} commit deletes artifact path {path}; archives require content"
                )
            paths.append(path)
        return paths

    def _verify_content_only(
        self,
        task_id: str,
        archive: dict[str, Any],
        reason: str,
        *,
        expected_paths: Sequence[str] | None = None,
        allow_generated_skip: bool = True,
    ) -> None:
        """Verify an archive against CONTENT when its commit binding is gone.

        THE COMMIT BINDING IS NOT DURABLE AND THE CONTENT BINDING IS. A squash
        merge replaces a branch with one new commit, so every `commit_sha` an
        archive receipt recorded becomes unreachable and every `parent_sha`
        becomes wrong -- while every `path_sha256` still matches the bytes on
        main. Five goals carried unresolvable commits for exactly this reason
        (CORR-20260802-a1f151); the same records' content hashes all still
        verified.

        Failing on that punishes an archive for the repository's merge strategy,
        which is not a property of the research. So when the commit cannot be
        reached, this verifies the declared path hashes against the current tree
        and records the degradation instead of raising. A CONTENT MISMATCH IS
        STILL FATAL -- what is relaxed is the binding to a commit, never the
        binding to bytes.
        """

        hashes = archive.get("path_sha256")
        if not isinstance(hashes, dict) or not hashes:
            raise DispatchError(
                f"archive task {task_id} commit binding is unverifiable ({reason}) and it "
                f"declares no path_sha256 to fall back on"
            )
        if expected_paths is not None and set(hashes) != set(expected_paths):
            raise DispatchError(
                f"archive task {task_id} declared content_first binding must provide "
                "path_sha256 for every archive and source artifact"
            )
        skipped: list[str] = []
        for path in sorted(hashes):
            # Read the COMMITTED content at HEAD, not the working tree. A dirty
            # tree is not evidence about an archive, and generated files in
            # particular are rebuilt locally on demand -- comparing against them
            # would fail an archive for a file the repository deliberately no
            # longer tracks.
            blob = subprocess.run(
                ["git", "-C", str(self.repo_root), "show", f"HEAD:{path}"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
            if blob.returncode != 0:
                if allow_generated_skip and _is_generated_path(path):
                    # The archive bound a generated artifact that this repository
                    # has since stopped tracking (.gitignore). The binding cannot
                    # be checked and its absence is policy, not corruption.
                    skipped.append(path)
                    continue
                raise DispatchError(
                    f"archive task {task_id} commit binding is unverifiable ({reason}) and "
                    f"declared artifact {path} is absent from HEAD"
                )
            observed = hashlib.sha256(blob.stdout).hexdigest()
            if observed != hashes[path]:
                if allow_generated_skip and _is_generated_path(path):
                    skipped.append(path)
                    continue
                raise DispatchError(
                    f"archive task {task_id} content hash mismatch for {path}: "
                    f"expected {hashes[path]}, observed {observed}"
                )
        self.content_only_archives.append({
            "task_id": task_id, "reason": reason,
            "paths_verified": len(hashes) - len(skipped),
            "generated_paths_skipped": skipped})

    def verify_archive(self, task: dict[str, Any], expected_paths: Sequence[str]) -> None:
        archive = task["archive"]
        task_id = task["id"]
        declared_commit = archive["commit_sha"]
        if not isinstance(declared_commit, str):
            raise DispatchError(f"completed archive task {task_id} requires archive.commit_sha")
        binding_mode = archive.get("binding_mode", "commit")
        try:
            commit_sha = self._resolve_commit(declared_commit, task_id, "archive.commit_sha")
        except DispatchError:
            if binding_mode == "content_first":
                raise DispatchError(
                    f"archive task {task_id} declared content_first binding requires "
                    "archive.commit_sha to resolve to a commit"
                )
            self._verify_content_only(
                task_id, archive, f"commit {declared_commit} does not resolve")
            return

        try:
            ancestor = subprocess.run(
                ["git", "-C", str(self.repo_root), "merge-base", "--is-ancestor", commit_sha, "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except OSError as error:
            raise DispatchError(f"unable to execute git for archive verification: {error}") from error
        if ancestor.returncode == 1:
            if binding_mode == "content_first":
                raise DispatchError(
                    f"archive task {task_id} declared content_first binding requires "
                    "archive.commit_sha to be an ancestor of HEAD"
                )
            self._verify_content_only(
                task_id, archive, f"commit {commit_sha[:12]} is not an ancestor of HEAD")
            return
        if ancestor.returncode != 0:
            detail = ancestor.stderr.decode("utf-8", "replace").strip()
            raise DispatchError(
                f"git archive verification failed (merge-base): {detail or 'unknown error'}"
            )

        parents = self._run(["show", "-s", "--format=%P", commit_sha]).decode("ascii").split()
        declared_parent = archive["parent_sha"]
        if not parents:
            if declared_parent is not None:
                raise DispatchError(
                    f"archive task {task_id} parent_sha must be null for a root commit"
                )
        else:
            if declared_parent is None:
                raise DispatchError(
                    f"archive task {task_id} parent_sha must match first parent {parents[0]}"
                )
            parent_sha = self._resolve_commit(declared_parent, task_id, "archive.parent_sha")
            if parent_sha != parents[0]:
                raise DispatchError(
                    f"archive task {task_id} parent_sha does not match first parent {parents[0]}"
                )

        if binding_mode == "content_first":
            # This mode deliberately binds every declared artifact byte at HEAD
            # instead of insisting that one commit changed the entire source
            # package. A real, reachable commit, its declared parent, and the
            # archival message IDs remain mandatory.
            self._verify_content_only(
                task_id,
                archive,
                "declared content_first binding mode",
                expected_paths=expected_paths,
                allow_generated_skip=False,
            )
            message = self._run(["log", "-1", "--format=%B", commit_sha]).decode(
                "utf-8", "replace"
            )
            missing_ids = [
                identifier
                for identifier in [task_id, *archive["record_ids"]]
                if identifier not in message
            ]
            if missing_ids:
                raise DispatchError(
                    f"archive task {task_id} commit message is missing IDs {missing_ids}"
                )
            return

        actual_paths = self._changed_paths(commit_sha, task_id)
        expected = set(expected_paths)
        actual = set(actual_paths)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing or extra or len(actual_paths) != len(actual):
            details: list[str] = []
            if missing:
                details.append(f"missing {missing}")
            if extra:
                details.append(f"extra {extra}")
            if len(actual_paths) != len(actual):
                details.append("duplicate changed path")
            raise DispatchError(
                f"archive task {task_id} commit must change exactly declared archive and source "
                f"artifacts ({'; '.join(details)})"
            )

        for path in sorted(expected):
            object_type = self._run(["cat-file", "-t", f"{commit_sha}:{path}"]).decode("ascii").strip()
            if object_type != "blob":
                raise DispatchError(f"archive task {task_id} artifact {path} is not a file blob")
            content = self._run(["show", f"{commit_sha}:{path}"])
            observed = hashlib.sha256(content).hexdigest()
            if observed != archive["path_sha256"][path]:
                raise DispatchError(
                    f"archive task {task_id} content hash mismatch for {path}: "
                    f"expected {archive['path_sha256'][path]}, observed {observed}"
                )

        message = self._run(["log", "-1", "--format=%B", commit_sha]).decode(
            "utf-8", "replace"
        )
        missing_ids = [
            identifier
            for identifier in [task_id, *archive["record_ids"]]
            if identifier not in message
        ]
        if missing_ids:
            raise DispatchError(
                f"archive task {task_id} commit message is missing IDs {missing_ids}"
            )


def discover_repository_root(start: Path) -> Path:
    """Resolve a repository root once so CLI verification cannot drift by cwd."""

    try:
        result = subprocess.run(
            ["git", "-C", str(start.resolve()), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise DispatchError(f"unable to execute git while finding repository root: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise DispatchError(f"unable to find repository root: {detail or 'unknown git error'}")
    return Path(result.stdout.decode("utf-8").strip()).resolve()


NONAUTHORITATIVE_ERROR = "POLICY_NONAUTHORITATIVE"
RECONCILIATION_ID = "RECON-20260802-001"
RECONCILIATION_HISTORY_SCHEMAS = {
    "crypto.autoresearch.reconciliation_history_index.v1",
    "crypto.autoresearch.reconciliation_history_view.v1",
}
RECONCILIATION_VARIANT_ROOTS = (
    "coordination/reconciliation/RECON-20260802-001/variants/local-a9664afb",
    "coordination/reconciliation/RECON-20260802-001/variants/reanchor-717d932c",
)
RECONCILIATION_PROTECTED_QUEUES = tuple(
    f"coordination/goals/GOAL-ECDLP-001/batches/BATCH-{number:03d}/dispatch_queue.json"
    for number in range(20, 25)
)


def _relative_to_repository(path: Path, repo_root: Path) -> str | None:
    """Return a canonical repository-relative path, or ``None`` if outside."""

    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return None

def enforce_reconciliation_queue_authority(queue_path: Path, repo_root: Path) -> None:
    """Reject preserved and inherited RECON-20260802-001 queues before parsing.

    Both the lexical path and the resolved target are checked so absolute,
    relative, and symlink aliases cannot reach readiness evaluation.
    """

    root = repo_root.resolve()
    lexical = queue_path if queue_path.is_absolute() else Path.cwd() / queue_path
    candidates = {lexical.absolute(), lexical.resolve(strict=False)}
    for candidate in candidates:
        relative = _relative_to_repository(candidate, root)
        if relative is None:
            continue
        if relative in RECONCILIATION_PROTECTED_QUEUES or any(
            relative == variant or relative.startswith(variant + "/")
            for variant in RECONCILIATION_VARIANT_ROOTS
        ):
            raise DispatchError(
                f"{NONAUTHORITATIVE_ERROR}: {relative} is historical reconciliation material"
            )


def enforce_reconciliation_document_authority(queue: Any) -> None:
    """Reject non-authorizing reconciliation envelopes before validation."""

    if not isinstance(queue, dict):
        return
    authority = queue.get("authority")
    nonauthorizing = isinstance(authority, dict) and (
        authority.get("code") == "NONAUT"
        or authority.get("dispatch_authority") == "NONAUT"
        or authority.get("live_dispatch_semantics") == "none"
    )
    if queue.get("schema") in RECONCILIATION_HISTORY_SCHEMAS or nonauthorizing:
        raise DispatchError(
            f"{NONAUTHORITATIVE_ERROR}: reconciliation history indexes have no live dispatch semantics"
        )


class RepositoryVerifier(Protocol):
    """Verifies the Git receipt for a completed archival task."""

    def verify_archive(self, task: dict[str, Any], expected_paths: Sequence[str]) -> None:
        """Raise DispatchError unless ``task`` has the required archive commit."""




def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path, help="dispatch queue JSON")
    parser.add_argument("--output", type=Path, required=True, help="dispatch plan JSON")
    parser.add_argument("--report", type=Path, required=True, help="dispatch plan Markdown")
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="repository root used to verify completed archive commits (defaults to queue repository)",
    )
    parser.add_argument(
        "--now",
        help="ISO-8601 instant to check running-task leases against (omit: leases never expire, "
             "matching every queue written before leases existed). Explicit rather than sampled "
             "from the clock, so a dispatch plan stays a pure function of its inputs -- "
             "e.g. --now \"$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)\".",
    )
    parser.add_argument(
        "--claims",
        choices=("off", "local", "refs"),
        default="local",
        help="overlay write-once task claims from <queue dir>/claims/ (tools/goal_lanes.py): "
             "'local' reads the working tree, 'refs' also scans every git ref so claims pushed "
             "from other worktrees count, 'off' ignores claims. Claims are evaluated at --now "
             "(or the wall clock when --now is omitted).",
    )
    args = parser.parse_args()
    try:
        repo_root = args.repo_root.resolve() if args.repo_root else discover_repository_root(args.queue.parent)
        enforce_reconciliation_queue_authority(args.queue, repo_root)
        queue = json.loads(args.queue.read_text(encoding="utf-8"))
        enforce_reconciliation_document_authority(queue)
        verifier = GitRepositoryVerifier(repo_root)
        now = parse_timestamp(args.now, "--now") if args.now is not None else None
        claims = None
        if args.claims != "off":
            import goal_lanes  # sibling module; imported lazily so the planner stays importable alone

            # Claims carry expiries, so a plan that reads them is clock-dependent
            # whether or not --now was given: without a clock an expired hold
            # would be admitted as `running` and never surface under
            # expired_leases. Sample the wall clock once and use it for both.
            if now is None:
                now = goal_lanes.utcnow()
            try:
                claims = goal_lanes.claim_summary(
                    repo_root, args.queue.resolve(), include_refs=(args.claims == "refs"), now=now,
                )
            except goal_lanes.LaneError as error:
                raise DispatchError(f"claims overlay: {error}") from error
        plan = select(queue, repository_verifier=verifier, now=now, claims=claims)
    except (OSError, json.JSONDecodeError, DispatchError) as error:
        print(f"dispatch error: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(markdown(plan), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
