"""Host identity and the host-aware C-9 machine-protection precondition
(AMD-20260926-3479cf C-9 as restated for the pod by AMD-20260928-7ce387).

macOS (repository Mac; Sage steps): 15-min load <= 14, system volume >= 5 GiB
free, repository volume >= 20 GiB free.
Linux (RunPod pod; charged cells): 15-min load <= floor(cgroup CPU quota)
from /sys/fs/cgroup/cpu.max (limit = floor(quota / period); os.cpu_count()
when the quota is 'max'), run volume >= 20 GiB free, / >= 5 GiB free.
"""

from __future__ import annotations

import datetime as dt
import math
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

MAC_LOAD_MAX = 14.0
MAC_SYS_FREE_MIN_GIB = 5.0
MAC_REPO_FREE_MIN_GIB = 20.0
LINUX_RUN_FREE_MIN_GIB = 20.0
LINUX_ROOT_FREE_MIN_GIB = 5.0

CPU_MAX = Path("/sys/fs/cgroup/cpu.max")
LOADAVG = Path("/proc/loadavg")


def parse_loadavg(text: str) -> float:
    """15-minute load from macOS `sysctl -n vm.loadavg` ('{ 1.0 2.0 3.0 }') or
    Linux /proc/loadavg ('1.0 2.0 3.0 1/200 123')."""
    nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", text)
    if len(nums) < 3:
        raise ValueError(f"cannot parse load average: {text!r}")
    return float(nums[2])


def parse_cpu_max(text: str, ncpu: int | None = None) -> dict:
    """cgroup v2 cpu.max: '<quota|max> <period>'. limit = floor(quota/period)."""
    parts = text.split()
    if len(parts) != 2:
        raise ValueError(f"cannot parse cpu.max: {text!r}")
    period = int(parts[1])
    if period <= 0:
        raise ValueError(f"non-positive cpu.max period: {text!r}")
    if parts[0] == "max":
        n = ncpu if ncpu is not None else (os.cpu_count() or 1)
        return {"quota": None, "period": period, "cpus": float(n), "load_limit": n,
                "source": "cpu.max unlimited; os.cpu_count()"}
    quota = int(parts[0])
    if quota <= 0:
        raise ValueError(f"non-positive cpu.max quota: {text!r}")
    return {"quota": quota, "period": period, "cpus": quota / period,
            "load_limit": math.floor(quota / period), "source": "cpu.max"}


def _read(path) -> str | None:
    try:
        return Path(path).read_text()
    except OSError:
        return None


def container_id() -> str | None:
    """Best effort: a 64-hex docker id in mountinfo/cgroup, else a 12-hex
    hostname (docker's default), else RUNPOD_POD_ID."""
    for src in ("/proc/self/mountinfo", "/proc/self/cgroup"):
        t = _read(src) or ""
        m = re.search(r"(?:docker|containers|containerd)[/-]([0-9a-f]{64})", t)
        if m:
            return m.group(1)
    hn = socket.gethostname()
    if re.fullmatch(r"[0-9a-f]{12}", hn):
        return hn
    return os.environ.get("RUNPOD_POD_ID")


def host_kind() -> str:
    return {"darwin": "macos", "linux": "linux"}.get(sys.platform, sys.platform)


def host_identity(sage_version: str | None = None) -> dict:
    import numpy
    ident = {"hostname": socket.gethostname(), "host_kind": host_kind(),
             "platform": platform.platform(), "machine": platform.machine(),
             "python": sys.version.split()[0], "python_full": sys.version,
             "numpy": numpy.__version__, "ncpu": os.cpu_count(),
             "container_id": container_id() if host_kind() == "linux" else None,
             "runpod_pod_id": os.environ.get("RUNPOD_POD_ID"),
             "cpu_quota": None, "sage": sage_version}
    if host_kind() == "linux":
        t = _read(CPU_MAX)
        try:
            ident["cpu_quota"] = parse_cpu_max(t) if t else None
        except ValueError as e:
            ident["cpu_quota"] = {"error": str(e)}
    try:
        import psutil
        ident["psutil"] = psutil.__version__
        ident["mem_total_gib"] = round(psutil.virtual_memory().total / 2 ** 30, 1)
    except ImportError:
        ident["psutil"] = None
    return ident


def admission_readings(repo_root: Path, run_volume: Path | None = None) -> dict:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    kind = host_kind()
    if kind == "linux":
        raw = _read(LOADAVG) or ""
        cpu_raw = _read(CPU_MAX)
        cq, cpu_err = None, None
        if cpu_raw is None:  # FX-2: fail closed
            cpu_err = f"{CPU_MAX} unreadable"
        else:
            try:
                cq = parse_cpu_max(cpu_raw)
            except (ValueError, TypeError) as e:
                cpu_err = f"{CPU_MAX} unparseable: {e}"
        try:
            load15 = parse_loadavg(raw)
        except ValueError as e:
            load15, cpu_err = None, (cpu_err or "") + f"; {LOADAVG}: {e}"
        vol = Path(run_volume or repo_root)
        while not vol.exists():
            vol = vol.parent
        return {"host_kind": kind, "loadavg_raw": raw.strip(), "load_15min": load15,
                "cpu_max_raw": None if cpu_raw is None else cpu_raw.strip(),
                "load_limit": cq["load_limit"] if cq else None, "cpu_quota": cq,
                "cpu_max_error": cpu_err, "run_volume": str(vol),
                "run_volume_free_gib": shutil.disk_usage(str(vol)).free / 2 ** 30,
                "root_volume_free_gib": shutil.disk_usage("/").free / 2 ** 30, "read_at": now}
    raw = subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True).stdout
    return {"host_kind": kind, "vm_loadavg_raw": raw.strip(), "load_15min": parse_loadavg(raw),
            "system_volume_free_gib": shutil.disk_usage("/").free / 2 ** 30,
            "repo_volume_free_gib": shutil.disk_usage(str(repo_root)).free / 2 ** 30,
            "read_at": now}


def check_admission(r: dict) -> tuple[bool, list]:
    reasons = []
    if r.get("host_kind") == "linux":
        if r.get("cpu_max_error") or r.get("load_limit") is None or r.get("load_15min") is None:
            reasons.append(f"cgroup CPU limit or load unavailable (fail closed): {r.get('cpu_max_error')}")
        elif not r["load_15min"] <= r["load_limit"]:
            reasons.append(f"15-min load {r['load_15min']} > cgroup limit {r['load_limit']}")
        if not r["run_volume_free_gib"] >= LINUX_RUN_FREE_MIN_GIB:
            reasons.append(f"run volume free {r['run_volume_free_gib']:.1f} GiB < {LINUX_RUN_FREE_MIN_GIB}")
        if not r["root_volume_free_gib"] >= LINUX_ROOT_FREE_MIN_GIB:
            reasons.append(f"/ free {r['root_volume_free_gib']:.1f} GiB < {LINUX_ROOT_FREE_MIN_GIB}")
        return not reasons, reasons
    if not r["load_15min"] <= MAC_LOAD_MAX:
        reasons.append(f"15-min load {r['load_15min']} > {MAC_LOAD_MAX}")
    if not r["system_volume_free_gib"] >= MAC_SYS_FREE_MIN_GIB:
        reasons.append(f"system volume free {r['system_volume_free_gib']:.1f} GiB < {MAC_SYS_FREE_MIN_GIB}")
    if not r["repo_volume_free_gib"] >= MAC_REPO_FREE_MIN_GIB:
        reasons.append(f"repo volume free {r['repo_volume_free_gib']:.1f} GiB < {MAC_REPO_FREE_MIN_GIB}")
    return not reasons, reasons
