"""Pure container binding and exact cgroup-path checks for TASK-20260908-692ab6.

This module deliberately has no Docker client, socket, subprocess, or filesystem
side effect.  A future, separately approved host-side operation must create and
inspect the container and pass the resulting ``ContainerInspection`` to the
supervisor.  The helper accepts no short ID, label lookup, or substring lookup.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping


TASK_ID = "TASK-20260908-692ab6"
PINNED_IMAGE = (
    "docker.io/library/python@sha256:"
    "c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
)
FULL_CONTAINER_ID = re.compile(r"^[0-9a-f]{64}$")


class ContainerBindingError(ValueError):
    """Raised before any prospective cgroup action on an unsafe binding."""


@dataclass(frozen=True)
class PlannedMount:
    """The published mount request; its live availability is intentionally unknown."""

    type: str
    source: str
    target: str
    read_only: bool
    availability: str


@dataclass(frozen=True)
class PlannedContainer:
    """The future host-side create profile, kept data-only in this source task."""

    image: str
    platform: str
    user: str
    network: str
    read_only_root: bool
    cap_drop: tuple[str, ...]
    cap_add: tuple[str, ...]
    no_new_privileges: bool
    cgroup_namespace: str
    pid_namespace: str
    pids_limit: int
    cpu_quota_cores: int
    outer_memory_bytes: int
    outer_memory_swap_total_bytes: int
    tmpfs: Mapping[str, str]
    labels: Mapping[str, str]
    mounts: tuple[PlannedMount, ...]


@dataclass(frozen=True)
class ContainerInspection:
    """Minimal, independently collected inspection facts required by the helper."""

    container_id: str
    image: str
    platform: str
    labels: Mapping[str, str]
    user: str
    network: str
    read_only_root: bool
    cap_drop: tuple[str, ...]
    cap_add: tuple[str, ...]
    no_new_privileges: bool
    cgroup_namespace: str
    pid_namespace: str
    pids_limit: int
    cpu_quota_cores: int
    outer_memory_bytes: int
    outer_memory_swap_total_bytes: int
    tmpfs: Mapping[str, str]
    mounts: tuple[PlannedMount, ...]
    privileged: bool


def planned_container(task_id: str = TASK_ID) -> PlannedContainer:
    """Return the exact future create profile without contacting Docker."""

    if task_id != TASK_ID:
        raise ContainerBindingError("wrong_task_id")
    return PlannedContainer(
        image=PINNED_IMAGE,
        platform="linux/arm64",
        user="0:0",
        network="none",
        read_only_root=True,
        cap_drop=("ALL",),
        cap_add=("SETUID", "SETGID"),
        no_new_privileges=True,
        cgroup_namespace="host",
        pid_namespace="private",
        pids_limit=32,
        cpu_quota_cores=1,
        outer_memory_bytes=8 * 1024 * 1024 * 1024,
        outer_memory_swap_total_bytes=8 * 1024 * 1024 * 1024,
        tmpfs={"/tmp": "rw,size=16m"},
        labels={"crypto.autoresearch.task": task_id},
        mounts=(
            PlannedMount(
                type="bind",
                source="/sys/fs/cgroup",
                target="/host-cgroup",
                read_only=False,
                availability="must_be_checked_live; not assumed by source or fixed mocks",
            ),
        ),
    )


def require_full_container_id(container_id: str) -> str:
    """Reject short, uppercase, malformed, and non-string identifiers."""

    if not isinstance(container_id, str) or not FULL_CONTAINER_ID.fullmatch(container_id):
        raise ContainerBindingError("expected_exact_64_lowercase_hex_container_id")
    return container_id


def allowed_cgroup_relative_paths(container_id: str) -> tuple[str, str]:
    """Return exactly the two documented cgroup-v2 locations for a full ID."""

    cid = require_full_container_id(container_id)
    return (f"docker/{cid}", f"system.slice/docker-{cid}.scope")


def require_exact_cgroup_relative_path(container_id: str, path: str) -> str:
    """Accept only an exact documented descendant; refuse root, parent and traversal."""

    cid = require_full_container_id(container_id)
    if not isinstance(path, str) or path.startswith("/") or "\\" in path:
        raise ContainerBindingError("invalid_cgroup_relative_path")
    pieces = path.split("/")
    if not path or any(piece in {"", ".", ".."} for piece in pieces):
        raise ContainerBindingError("cgroup_path_traversal_or_root")
    if path not in allowed_cgroup_relative_paths(cid):
        raise ContainerBindingError("cgroup_path_not_exact_inspected_container_subtree")
    return path


def require_inspection_matches(
    inspection: ContainerInspection, expected_container_id: str, task_id: str = TASK_ID
) -> None:
    """Validate the independently inspected exact container before cgroup access."""

    expected = require_full_container_id(expected_container_id)
    profile = planned_container(task_id)
    if inspection.container_id != expected:
        raise ContainerBindingError("inspection_container_id_mismatch")
    checks = {
        "image": inspection.image == profile.image,
        "platform": inspection.platform == profile.platform,
        "task_label": inspection.labels.get("crypto.autoresearch.task") == task_id,
        "user": inspection.user == profile.user,
        "network": inspection.network == profile.network,
        "read_only_root": inspection.read_only_root is True,
        "cap_drop": tuple(inspection.cap_drop) == profile.cap_drop,
        "cap_add": tuple(inspection.cap_add) == profile.cap_add,
        "no_new_privileges": inspection.no_new_privileges is True,
        "cgroup_namespace": inspection.cgroup_namespace == profile.cgroup_namespace,
        "pid_namespace": inspection.pid_namespace == profile.pid_namespace,
        "pids_limit": inspection.pids_limit == profile.pids_limit,
        "cpu_quota_cores": inspection.cpu_quota_cores == profile.cpu_quota_cores,
        "outer_memory_bytes": inspection.outer_memory_bytes == profile.outer_memory_bytes,
        "outer_memory_swap_total_bytes": (
            inspection.outer_memory_swap_total_bytes == profile.outer_memory_swap_total_bytes
        ),
        "tmpfs": dict(inspection.tmpfs) == dict(profile.tmpfs),
        "mounts": tuple(inspection.mounts) == profile.mounts,
        "not_privileged": inspection.privileged is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ContainerBindingError("inspection_profile_mismatch:" + ",".join(failed))

