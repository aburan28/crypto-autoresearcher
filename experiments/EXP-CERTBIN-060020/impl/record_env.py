#!/usr/bin/env python3
"""Write RUN_DIR/environment.json once (git revision and dirty state, tool
versions, host, resource settings). Refuses to overwrite."""
from __future__ import annotations

import json
import os
import platform
import resource
import subprocess
import sys
from pathlib import Path

import common as C


def sh(*cmd):
    try:
        return subprocess.run(list(cmd), cwd=C.ROOT, capture_output=True, text=True).stdout.strip()
    except Exception as exc:
        return f"error: {exc}"


def main():
    out = Path(sys.argv[1]) / "environment.json"
    if out.exists():
        print("environment.json exists; not overwritten")
        return 0
    import numpy
    import mpmath
    import yaml
    status = sh("git", "status", "--porcelain")
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    env = {
        "recorded_utc": C.utc_now(),
        "git_head": sh("git", "rev-parse", "HEAD"),
        "git_branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(status),
        "git_status": status.splitlines(),
        "git_dirty_note": "untracked files are the executor's own impl/, verifier/, trial plan and run directory (write scope)",
        "python": sys.version, "numpy": numpy.__version__, "mpmath": mpmath.__version__, "pyyaml": yaml.__version__,
        "platform": platform.platform(), "machine": platform.machine(), "nproc": os.cpu_count(),
        "meminfo_total_kib": next((l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemTotal")), None),
        "cc": sh("cc", "--version").splitlines()[:1],
        "env": {k: os.environ.get(k) for k in ("CRYPTO_AR_GF2_BACKEND", "CRYPTO_AR_GF2_THREADS", "OPENBLAS_NUM_THREADS",
                                               "OMP_NUM_THREADS", "PYTHONDONTWRITEBYTECODE", "CRYPTO_AR_GF2_CACHE")},
        "rlimit_as_bytes": {"soft": soft, "hard": hard},
        "watchdogs": {"run_seconds": 172800, "per_system_closure_seconds": 3600, "rss_guard_mib": 3072},
        "concurrency_note": "one other CERTBIN executor (EXP-CERTBIN-ddfe75) shares the 4-core, 15 GB host "
                            "(dispatch note); CRYPTO_AR_GF2_THREADS=2 as directed",
    }
    C.write_json(out, env)
    return 0


if __name__ == "__main__":
    sys.exit(main())
