"""Fail-closed process-group RSS watchdog with exit/reap race handling.

The caller starts one private process group. Samples count resident bytes of all
visible group members. An unreadable *live* member is an infrastructure fault;
no sampled RSS value is manufactured for that interval. Exited/zombie members
are skipped only after a fresh lifecycle check, while group sampling continues.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from phase import TraceWriter, inspect


class MonitorFault(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}:{detail}")
        self.code = code
        self.detail = detail


def _root_lifecycle(child, psutil, retries=4, delay=0.01) -> str:
    """Resolve poll-before-reap races without calling an exited child live."""
    for attempt in range(retries):
        if child.poll() is not None:
            return "exited"
        try:
            status = psutil.Process(child.pid).status()
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            status = "missing"
        except psutil.AccessDenied as exc:
            raise MonitorFault("unreadable_live_root", repr(exc)) from exc
        if status == psutil.STATUS_ZOMBIE:
            # Popen.poll reaps the child on the next call on supported hosts.
            child.poll()
            return "zombie_or_exited"
        if status != "missing":
            return "live"
        if attempt + 1 < retries:
            time.sleep(delay)
    # A vanished root that Popen could not reap is ambiguous, not live RSS=0.
    raise MonitorFault("ambiguous_root_exit", "root absent but poll still pending")


def sample_group(child, psutil=None) -> dict:
    if psutil is None:
        import psutil as psutil_module
        psutil = psutil_module
    root_state = _root_lifecycle(child, psutil)
    members = []
    missing = []
    rss = 0
    if root_state != "live":
        # The private process group is terminated before this call returns;
        # a reparented descendant must not survive an exited root.
        return {"rss_bytes": None, "root_state": root_state,
                "members": [], "vanished_members": []}
    try:
        root = psutil.Process(child.pid)
        processes = [root] + root.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        state = _root_lifecycle(child, psutil)
        if state != "live":
            return {"rss_bytes": None, "root_state": state,
                    "members": [], "vanished_members": []}
        raise MonitorFault("unreadable_live_root", "root vanished during tree discovery")
    except psutil.AccessDenied as exc:
        raise MonitorFault("unreadable_live_root", repr(exc)) from exc
    for proc in processes:
        try:
            status = proc.status()
            if status == psutil.STATUS_ZOMBIE:
                missing.append({"pid": proc.pid, "state": "zombie"})
                continue
            value = proc.memory_info().rss
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            # A descendant may exit between discovery, status and RSS.
            try:
                again = proc.status()
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                again = "exited"
            if again == psutil.STATUS_ZOMBIE or again == "exited":
                missing.append({"pid": proc.pid, "state": again})
                continue
            if proc.pid == child.pid and _root_lifecycle(child, psutil) != "live":
                missing.append({"pid": proc.pid, "state": "root_exited"})
                continue
            raise MonitorFault("unreadable_live_member", f"pid={proc.pid} status={again}")
        except psutil.AccessDenied as exc:
            if proc.pid == child.pid and _root_lifecycle(child, psutil) != "live":
                missing.append({"pid": proc.pid, "state": "root_exited"})
                continue
            raise MonitorFault("unreadable_live_member", f"pid={proc.pid} {exc}") from exc
        if value < 0:
            raise MonitorFault("invalid_rss", f"pid={proc.pid} rss={value}")
        rss += value
        members.append({"pid": proc.pid, "rss_bytes": value})
    if not members:
        root_state = _root_lifecycle(child, psutil)
        if root_state == "live":
            raise MonitorFault("unreadable_live_root", "no readable process-tree member")
        return {"rss_bytes": None, "root_state": root_state,
                "members": [], "vanished_members": missing}
    return {"rss_bytes": rss, "root_state": root_state,
            "members": members, "vanished_members": missing}


def scratch_bytes(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except FileNotFoundError:
            continue
    return total


def _terminate_group(child) -> None:
    # If the root is already reaped, discover surviving members before
    # signaling its old group ID; otherwise a stale group ID is unsafe.
    if child.poll() is not None:
        import psutil
        remaining = []
        try:
            for proc in psutil.process_iter():
                try:
                    if os.getpgid(proc.pid) == child.pid:
                        remaining.append(proc.pid)
                except ProcessLookupError:
                    continue
                except PermissionError as exc:
                    raise MonitorFault("group_teardown_unverified",
                                       f"cannot_read_group_pid={proc.pid}: {exc}") from exc
        except (PermissionError, psutil.AccessDenied) as exc:
            raise MonitorFault("group_teardown_unverified", repr(exc)) from exc
        if not remaining:
            return
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except PermissionError as exc:
        raise MonitorFault("group_teardown_unverified", repr(exc)) from exc
    try:
        child.wait(timeout=0.2)
    except subprocess.TimeoutExpired:
        pass
    # A descendant may ignore TERM after the root reaps.
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError as exc:
        raise MonitorFault("group_teardown_unverified", repr(exc)) from exc
    if child.poll() is None:
        child.wait(timeout=2)


def supervise(command: list[str], output_dir: Path, *, seconds: float,
              rss_cap_bytes: int, scratch_cap_bytes: int,
              minimum_free_bytes: int = 0, poll_seconds: float = 0.02,
              env: dict | None = None, probe=None, phase_trace: Path | None = None) -> dict:
    """Run a bounded child. All raw files and trace remain after any stop.

    ``probe`` is an injectable synthetic fault seam; production uses
    ``sample_group``. This API is not a scientific trial launcher.
    """
    if not command or min(seconds, rss_cap_bytes, scratch_cap_bytes, poll_seconds) <= 0:
        raise ValueError("positive command and limits required")
    output_dir.mkdir(parents=True, exist_ok=False)
    stdout_path, stderr_path = output_dir / "stdout.raw", output_dir / "stderr.raw"
    trace = phase_trace or output_dir / "phase.jsonl"
    trace.touch(exist_ok=False)
    writer = TraceWriter(trace, Path(__file__), "supervisor")
    writer.emit("launch", "start", command=command, rss_cap_bytes=rss_cap_bytes,
                scratch_cap_bytes=scratch_cap_bytes, seconds=seconds)
    peak_rss = None
    peak_scratch = 0
    min_free = None
    child = None
    start = time.monotonic()
    deadline = start + seconds
    stop = None
    fault = None
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                     env=env, start_new_session=True)
            writer.emit("launch", "child_started", child_pid=child.pid)
            while True:
                if time.monotonic() >= deadline:
                    stop = "timeout_censored"
                    break
                try:
                    sample = (probe or sample_group)(child)
                    used = scratch_bytes(output_dir)
                    free = shutil.disk_usage(output_dir).free
                    row = {"rss_bytes": sample["rss_bytes"],
                           "root_state": sample["root_state"],
                           "members": sample["members"],
                           "vanished_members": sample["vanished_members"],
                           "scratch_bytes": used, "free_bytes": free}
                    writer.emit("resource", "sample", **row)
                except MonitorFault as exc:
                    fault = {"code": exc.code, "detail": exc.detail}
                    writer.emit("resource", "sample_unavailable", rss_bytes=None,
                                fault=fault, child_poll=child.poll())
                    stop = "infrastructure_monitor_error"
                    break
                except Exception as exc:
                    fault = {"code": "monitor_exception", "detail": f"{type(exc).__name__}:{exc}"}
                    writer.emit("resource", "sample_unavailable", rss_bytes=None,
                                fault=fault, child_poll=child.poll())
                    stop = "infrastructure_monitor_error"
                    break
                if sample["rss_bytes"] is not None:
                    peak_rss = max(peak_rss or 0, sample["rss_bytes"])
                peak_scratch = max(peak_scratch, used)
                min_free = free if min_free is None else min(min_free, free)
                if sample["rss_bytes"] is not None and sample["rss_bytes"] > rss_cap_bytes:
                    stop = "memory_censored"
                elif used > scratch_cap_bytes or free < minimum_free_bytes:
                    stop = "scratch_censored"
                elif child.poll() is not None and sample["rss_bytes"] is None:
                    stop = "exited"
                if stop:
                    break
                time.sleep(min(poll_seconds, max(0, deadline - time.monotonic())))
            if stop != "exited":
                writer.emit("watchdog", "terminate", stop=stop, fault=fault)
                _terminate_group(child)
            else:
                _terminate_group(child)
                child.wait(timeout=1)
        except Exception as exc:
            if isinstance(exc, MonitorFault):
                fault = {"code": exc.code, "detail": exc.detail}
            else:
                fault = {"code": "supervisor_exception",
                         "detail": f"{type(exc).__name__}:{exc}"}
            stop = "infrastructure_monitor_error"
            writer.emit("watchdog", "exception", fault=fault)
            if child is not None and child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError) as cleanup_exc:
                    writer.emit("watchdog", "group_cleanup_unverified",
                                error=f"{type(cleanup_exc).__name__}:{cleanup_exc}")
                try:
                    child.kill()
                    child.wait(timeout=2)
                except (ProcessLookupError, subprocess.TimeoutExpired) as cleanup_exc:
                    writer.emit("watchdog", "root_cleanup_unverified",
                                error=f"{type(cleanup_exc).__name__}:{cleanup_exc}")
    writer.emit("watchdog", "terminal", stop=stop, exit_code=child.returncode if child else None)
    trace_info = inspect(trace)
    return {"stop": stop, "fault": fault, "exit_code": child.returncode if child else None,
            "wall_seconds": time.monotonic() - start,
            "peak_tree_rss_bytes_sampled": peak_rss,
            "peak_scratch_bytes_sampled": peak_scratch,
            "minimum_free_bytes_sampled": min_free,
            "trace": trace_info,
            "stdout_sha256": hashlib.sha256(stdout_path.read_bytes()).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr_path.read_bytes()).hexdigest()}
