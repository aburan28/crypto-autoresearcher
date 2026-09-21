"""Frozen container profile, Docker-inspection decoder, and native entry path.

Imports and constructors are inert.  ``main`` is intended only for a later,
separately governed Docker invocation.  The source checks inject fixed command
results and never call Docker, cgroups, privilege changes, or pressure paths.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
import sys
from typing import Any, BinaryIO, Mapping, Sequence


TASK_ID = "TASK-20260910-89d2df"
RESULT_SCHEMA = "crypto.autoresearch.group_oom_container_result.v2"
PINNED_IMAGE = (
    "docker.io/library/python@sha256:"
    "c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
)
PINNED_IMAGE_DIGEST = "sha256:c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
FULL_CONTAINER_ID = re.compile(r"^[0-9a-f]{64}$")
CASES = ("exact_profile", "group_zero_refused", "small_group_oom")
MAX_STARTUP_BYTES = 4096


class ContainerBindingError(ValueError):
    """Raised before any prospective container or cgroup action."""


@dataclass(frozen=True)
class PlannedMount:
    type: str
    source: str
    target: str
    read_only: bool
    availability: str


@dataclass(frozen=True)
class PlannedContainer:
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
    open_stdin: bool
    attach_stdin: bool
    tty: bool
    auto_remove: bool


@dataclass(frozen=True)
class ContainerInspection:
    """Facts decoded from the actual full Docker inspect and image inspect JSON."""

    container_id: str
    image_reference: str
    image_id: str
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
    open_stdin: bool
    attach_stdin: bool
    tty: bool
    auto_remove: bool
    command: tuple[str, ...]
    running: bool
    source: str = "actual_docker_inspect_json"


@dataclass(frozen=True)
class StartupIdentity:
    task_id: str
    expected_container_id: str
    case_id: str


def planned_container(task_id: str = TASK_ID) -> PlannedContainer:
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
                availability="must_be_verified_live; never inferred from source checks",
            ),
        ),
        open_stdin=True,
        attach_stdin=True,
        tty=False,
        auto_remove=False,
    )


def require_full_container_id(container_id: str) -> str:
    if not isinstance(container_id, str) or not FULL_CONTAINER_ID.fullmatch(container_id):
        raise ContainerBindingError("expected_exact_64_lowercase_hex_container_id")
    return container_id


def allowed_cgroup_relative_paths(container_id: str) -> tuple[str, str]:
    cid = require_full_container_id(container_id)
    return (f"docker/{cid}", f"system.slice/docker-{cid}.scope")


def require_exact_cgroup_relative_path(container_id: str, path: str) -> str:
    cid = require_full_container_id(container_id)
    if not isinstance(path, str) or path.startswith("/") or "\\" in path:
        raise ContainerBindingError("invalid_cgroup_relative_path")
    if not path or any(part in {"", ".", ".."} for part in path.split("/")):
        raise ContainerBindingError("cgroup_path_traversal_or_root")
    if path not in allowed_cgroup_relative_paths(cid):
        raise ContainerBindingError("cgroup_path_not_exact_inspected_container_subtree")
    return path


def _one_json_object(raw: str, description: str) -> Mapping[str, Any]:
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ContainerBindingError(f"malformed_{description}_json") from exc
    if isinstance(parsed, list):
        if len(parsed) != 1 or not isinstance(parsed[0], Mapping):
            raise ContainerBindingError(f"ambiguous_{description}_json")
        parsed = parsed[0]
    if not isinstance(parsed, Mapping):
        raise ContainerBindingError(f"malformed_{description}_json")
    return parsed


def _tuple_upper(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ContainerBindingError("malformed_capability_inspection")
    return tuple(str(item).upper() for item in value)


def inspection_from_docker_json(
    container_json: str,
    image_json: str,
    expected_container_id: str,
) -> ContainerInspection:
    """Decode independently returned Docker JSON; no caller-supplied facts survive."""

    cid = require_full_container_id(expected_container_id)
    raw = _one_json_object(container_json, "container_inspect")
    image = _one_json_object(image_json, "image_inspect")
    if raw.get("Id") != cid:
        raise ContainerBindingError("inspection_container_id_mismatch")
    image_id = str(image.get("Id", ""))
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
        raise ContainerBindingError("malformed_image_id")
    repo_digests = image.get("RepoDigests") or []
    if PINNED_IMAGE_DIGEST not in {str(item).split("@", 1)[-1] for item in repo_digests}:
        raise ContainerBindingError("pinned_image_digest_not_cached")
    if raw.get("Image") != image_id:
        raise ContainerBindingError("container_image_id_mismatch")
    config = raw.get("Config")
    host = raw.get("HostConfig")
    state = raw.get("State")
    if not isinstance(config, Mapping) or not isinstance(host, Mapping) or not isinstance(state, Mapping):
        raise ContainerBindingError("incomplete_container_inspection")
    mounts: list[PlannedMount] = []
    for mount in raw.get("Mounts") or []:
        if not isinstance(mount, Mapping):
            raise ContainerBindingError("malformed_mount_inspection")
        mounts.append(
            PlannedMount(
                type=str(mount.get("Type", "")),
                source=str(mount.get("Source", "")),
                target=str(mount.get("Destination", "")),
                read_only=not bool(mount.get("RW")),
                availability="must_be_verified_live; never inferred from source checks",
            )
        )
    security = tuple(str(item).lower() for item in (host.get("SecurityOpt") or []))
    cgroupns = str(host.get("CgroupnsMode") or "private")
    pid_mode = str(host.get("PidMode") or "private")
    nano_cpus = int(host.get("NanoCpus") or 0)
    if nano_cpus % 1_000_000_000:
        raise ContainerBindingError("fractional_cpu_quota_not_frozen_profile")
    return ContainerInspection(
        container_id=cid,
        image_reference=str(config.get("Image", "")),
        image_id=image_id,
        platform=f"{image.get('Os', '')}/{image.get('Architecture', '')}",
        labels=dict(config.get("Labels") or {}),
        user=str(config.get("User", "")),
        network=str(host.get("NetworkMode", "")),
        read_only_root=bool(host.get("ReadonlyRootfs")),
        cap_drop=_tuple_upper(host.get("CapDrop")),
        cap_add=_tuple_upper(host.get("CapAdd")),
        no_new_privileges=any(value.startswith("no-new-privileges") for value in security),
        cgroup_namespace=cgroupns,
        pid_namespace=pid_mode,
        pids_limit=int(host.get("PidsLimit") or 0),
        cpu_quota_cores=nano_cpus // 1_000_000_000,
        outer_memory_bytes=int(host.get("Memory") or 0),
        outer_memory_swap_total_bytes=int(host.get("MemorySwap") or 0),
        tmpfs=dict(host.get("Tmpfs") or {}),
        mounts=tuple(mounts),
        privileged=bool(host.get("Privileged")),
        open_stdin=bool(config.get("OpenStdin")),
        attach_stdin=bool(config.get("AttachStdin")),
        tty=bool(config.get("Tty")),
        auto_remove=bool(host.get("AutoRemove")),
        command=tuple(str(item) for item in (config.get("Cmd") or [])),
        running=bool(state.get("Running")),
    )


def require_inspection_matches(
    inspection: ContainerInspection,
    expected_container_id: str,
    expected_image_id: str,
    expected_nonce: str,
    task_id: str = TASK_ID,
) -> None:
    if not isinstance(expected_nonce, str) or re.fullmatch(r"[0-9a-f]{12}", expected_nonce) is None:
        raise ContainerBindingError("invalid_expected_nonce")
    expected = require_full_container_id(expected_container_id)
    plan = planned_container(task_id)
    command = ("python3", "-B", "/opt/group-oom/container.py")
    checks = {
        "inspection_source": inspection.source == "actual_docker_inspect_json",
        "container_id": inspection.container_id == expected,
        "image_reference": inspection.image_reference == plan.image,
        "image_id": inspection.image_id == expected_image_id,
        "platform": inspection.platform == plan.platform,
        "task_label": inspection.labels.get("crypto.autoresearch.task") == task_id,
        "nonce_label": inspection.labels.get("crypto.autoresearch.nonce") == expected_nonce,
        "user": inspection.user == plan.user,
        "network": inspection.network == plan.network,
        "read_only_root": inspection.read_only_root is plan.read_only_root,
        "cap_drop": inspection.cap_drop == plan.cap_drop,
        "cap_add": inspection.cap_add == plan.cap_add,
        "no_new_privileges": inspection.no_new_privileges is plan.no_new_privileges,
        "cgroup_namespace": inspection.cgroup_namespace == plan.cgroup_namespace,
        "pid_namespace": inspection.pid_namespace == plan.pid_namespace,
        "pids_limit": inspection.pids_limit == plan.pids_limit,
        "cpu_quota_cores": inspection.cpu_quota_cores == plan.cpu_quota_cores,
        "outer_memory": inspection.outer_memory_bytes == plan.outer_memory_bytes,
        "outer_swap": inspection.outer_memory_swap_total_bytes == plan.outer_memory_swap_total_bytes,
        "tmpfs": dict(inspection.tmpfs) == dict(plan.tmpfs),
        "mounts": inspection.mounts == plan.mounts,
        "not_privileged": inspection.privileged is False,
        "open_stdin": inspection.open_stdin is plan.open_stdin,
        "attach_stdin": inspection.attach_stdin is plan.attach_stdin,
        "tty": inspection.tty is plan.tty,
        "auto_remove": inspection.auto_remove is plan.auto_remove,
        "command": inspection.command == command,
        "created_not_running": inspection.running is False,
    }
    failed = sorted(key for key, ok in checks.items() if not ok)
    if failed:
        raise ContainerBindingError("inspection_profile_mismatch:" + ",".join(failed))


def parse_startup_stdin(stream: BinaryIO) -> StartupIdentity:
    raw = stream.readline(MAX_STARTUP_BYTES + 1)
    if not raw or len(raw) > MAX_STARTUP_BYTES or not raw.endswith(b"\n"):
        raise ContainerBindingError("startup_identity_missing_or_truncated")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContainerBindingError("startup_identity_malformed") from exc
    if not isinstance(value, Mapping) or set(value) != {"task_id", "expected_container_id", "case_id"}:
        raise ContainerBindingError("startup_identity_shape_mismatch")
    identity = StartupIdentity(
        task_id=str(value["task_id"]),
        expected_container_id=require_full_container_id(value["expected_container_id"]),
        case_id=str(value["case_id"]),
    )
    if identity.task_id != TASK_ID:
        raise ContainerBindingError("wrong_task_id")
    if identity.case_id not in CASES:
        raise ContainerBindingError("unknown_fixed_case")
    return identity


def source_result(identity: StartupIdentity, outcome: Mapping[str, Any]) -> Mapping[str, Any]:
    """The production wire envelope, also exercised by host integration controls."""
    return {
        "schema": RESULT_SCHEMA,
        "startup_identity": {
            "task_id": identity.task_id,
            "expected_container_id": identity.expected_container_id,
            "case_id": identity.case_id,
        },
        "outcome": dict(outcome),
    }


def source_startup_failure(exc: BaseException) -> Mapping[str, Any]:
    return {"schema": RESULT_SCHEMA, "startup_failure": {"type": type(exc).__name__, "message": str(exc)}}


def run_native_entry(stream: BinaryIO) -> Mapping[str, Any]:
    """Construct native adapters only after the trusted startup line is parsed."""

    identity = parse_startup_stdin(stream)
    from supervisor import (
        DescriptorCgroupTransport,
        GroupOomSupervisor,
        PosixProcessTransport,
        SupervisorRequest,
        make_posix_runtime_factory,
    )

    cgroups = DescriptorCgroupTransport()
    processes = PosixProcessTransport(make_posix_runtime_factory(cgroups, identity.expected_container_id))
    request = SupervisorRequest.fixed(identity.case_id, identity.expected_container_id)
    outcome = GroupOomSupervisor(cgroups, processes).run(request)
    return source_result(identity, outcome.as_dict())


def main() -> int:
    try:
        result = run_native_entry(sys.stdin.buffer)
        outcome = result["outcome"]
    except BaseException as exc:
        result = source_startup_failure(exc)
        outcome = {"status": "failed", "cleanup_complete": False}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if outcome.get("status") == "inner_complete" and outcome.get("cleanup_complete") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
