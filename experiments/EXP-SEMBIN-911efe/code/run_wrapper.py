#!/usr/bin/env python3
"""Wrapper: environment, command, logs, then parity_split_run.py."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time

RUN = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                      "/workspace/experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036")
CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(RUN, exist_ok=True)

cmd = [
    sys.executable, os.path.join(CODE, "parity_split_run.py"),
    "--out-dir", RUN,
    "--per-r",
    "/workspace/experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/per-R-counts.json",
    "--cbd770",
    "/workspace/experiments/EXP-SEMBIN-92724f/runs/RUN-SEMBIN-cbd770",
]
with open(os.path.join(RUN, "command.txt"), "w") as fh:
    fh.write(" ".join(cmd) + "\n")
    fh.write(f"working_directory: {CODE}\n")

env = {
    "python_executable": sys.executable,
    "python_version": platform.python_version(),
    "python_implementation": platform.python_implementation(),
    "operating_system": platform.platform(),
    "architecture": platform.machine(),
    "processor_count": os.cpu_count(),
    "hostname": platform.node(),
    "cwd": CODE,
}
try:
    import numpy
    env["numpy_version"] = numpy.__version__
except Exception:
    env["numpy_version"] = None
try:
    import yaml
    env["pyyaml_version"] = getattr(yaml, "__version__", None)
except Exception:
    env["pyyaml_version"] = None
with open(os.path.join(RUN, "environment.json"), "w") as fh:
    json.dump(env, fh, indent=2, sort_keys=True)
    fh.write("\n")

stdout_path = os.path.join(RUN, "stdout.log")
stderr_path = os.path.join(RUN, "stderr.log")
t0 = time.time()
with open(stdout_path, "w") as so, open(stderr_path, "w") as se:
    proc = subprocess.run(cmd, cwd=CODE, stdout=so, stderr=se)
print(f"wrapper_exit={proc.returncode} wall={time.time()-t0:.1f}s")
sys.exit(proc.returncode)
