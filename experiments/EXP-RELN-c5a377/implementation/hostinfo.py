"""C-7 machine-protection precondition (AMD-20260926-a7d25d, user instruction
2026-09-26): 15-minute load <= 14, system volume >= 5 GiB free, repository
volume >= 20 GiB free. Readings are recorded; any reading that cannot be
taken or parsed fails closed.
"""

from __future__ import annotations

import datetime as dt
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

LOAD_MAX = 14.0
SYS_FREE_MIN_GIB = 5.0
REPO_FREE_MIN_GIB = 20.0


def parse_loadavg(text: str) -> float:
    """15-minute load from macOS 'sysctl -n vm.loadavg' ('{ 1.0 2.0 3.0 }') or
    Linux /proc/loadavg ('1.0 2.0 3.0 1/200 123')."""
    nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", text or "")
    if len(nums) < 3:
        raise ValueError(f"cannot parse load average: {text!r}")
    return float(nums[2])


def _load_raw() -> str:
    if sys.platform == "darwin":
        return subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True,
                              timeout=10).stdout
    return Path("/proc/loadavg").read_text()


def _free_gib(path) -> float:
    return shutil.disk_usage(str(path)).free / 2 ** 30


def readings(repo_root: Path, load_reader=_load_raw, free_reader=_free_gib) -> dict:
    r = {"read_at": dt.datetime.now(dt.timezone.utc).isoformat(), "platform": sys.platform,
         "errors": []}
    try:
        raw = load_reader()
        r["loadavg_raw"] = (raw or "").strip()
        r["load_15min"] = parse_loadavg(raw)
    except Exception as e:  # fail closed
        r["load_15min"] = None
        r["errors"].append(f"load: {e}")
    for key, path in (("system_volume_free_gib", "/"), ("repo_volume_free_gib", repo_root)):
        try:
            r[key] = free_reader(path)
            r[key.replace("_free_gib", "_path")] = str(path)
        except Exception as e:
            r[key] = None
            r["errors"].append(f"{key}: {e}")
    return r


def check(r: dict) -> tuple[bool, list]:
    reasons = list(r.get("errors") or [])
    ld, sv, rv = r.get("load_15min"), r.get("system_volume_free_gib"), r.get("repo_volume_free_gib")
    if not isinstance(ld, (int, float)) or not ld <= LOAD_MAX:
        reasons.append(f"15-min load {ld} not <= {LOAD_MAX}")
    if not isinstance(sv, (int, float)) or not sv >= SYS_FREE_MIN_GIB:
        reasons.append(f"system volume free {sv} GiB not >= {SYS_FREE_MIN_GIB}")
    if not isinstance(rv, (int, float)) or not rv >= REPO_FREE_MIN_GIB:
        reasons.append(f"repository volume free {rv} GiB not >= {REPO_FREE_MIN_GIB}")
    return not reasons, reasons


def host_identity() -> dict:
    ident = {"hostname": socket.gethostname(), "platform": platform.platform(),
             "machine": platform.machine(), "python": sys.version.split()[0],
             "ncpu": os.cpu_count()}
    try:
        import psutil
        ident["psutil"] = psutil.__version__
        ident["mem_total_gib"] = round(psutil.virtual_memory().total / 2 ** 30, 1)
    except ImportError:
        ident["psutil"] = None
    return ident
