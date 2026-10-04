#!/usr/bin/env python3
"""Shared paths and recording helpers for the RUN-ICPERF-a4a24b acceptance invocations.

These scripts are NOT part of the instrument. They live under the run directory, call the
repaired tree in experiments/EXP-ICPERF-e21835/code/ through its own entry points, and add
no measurement logic beyond recording the host state at each launch (C-LOAD).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
EXP_DIR = RUN_DIR.parents[1]
CODE = EXP_DIR / "code"
EXPERIMENTS = EXP_DIR.parent
REPO = EXPERIMENTS.parent
FROZEN_CODE = EXPERIMENTS / "EXP-ICPERF-66fd51" / "code"
FROZEN_RUN = EXPERIMENTS / "EXP-ICPERF-66fd51" / "runs" / "RUN-ICPERF-305ca3"
REVIEW = (REPO / "coordination" / "review" / "icperf-20260913-66fd51"
          / "TASK-20260913-6c5729" / "artifacts")
LOGS = RUN_DIR / "logs"
WD = RUN_DIR / "watchdog_control"

sys.path.insert(0, str(CODE))


def mem_available_kb() -> int:
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1])
    return -1


def host_state() -> dict:
    """C-LOAD: the 1-minute load average at this invocation, with memory headroom."""
    return {"loadavg1": round(os.getloadavg()[0], 2), "loadavg": [round(x, 2) for x in os.getloadavg()],
            "mem_available_kb": mem_available_kb(),
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def emit(name: str, payload: dict) -> dict:
    payload["invocation"] = name
    (LOGS / f"{name}.json").write_text(json.dumps(payload, indent=1, default=str))
    print(json.dumps(payload, indent=1, default=str)[:4000])
    return payload
