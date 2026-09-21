#!/usr/bin/env python3
"""D4 / A5 / C-PROBE: exercise the environment probe in the configuration that hung.

The child is launched with stdin inherited from AN OPEN PIPE THAT IS NEVER WRITTEN TO, so
stdin is open and readable but delivers neither a byte nor an EOF. That is the configuration
RUN-ICPERF-c9590f died in; a terminal whose stdin happens to be closed, or /dev/null, would
not exercise the defect at all.

Two children are launched, in this order:
  1. the REPAIRED environment() from experiments/EXP-ICPERF-e21835/code/bench.py;
  2. the FROZEN `ver` body, copied verbatim, as a comparison control -- the contract asks
     the acceptance report to explain (or record as unexplained) why the frozen code's 60 s
     per-engine timeout did not save RUN-ICPERF-c9590f, and this measures what it does here.

Each child is additionally bounded by a driver-side hard limit and killed BY PROCESS GROUP,
so a hang cannot consume the task's wall clock. The hard limit is far larger than any timeout
inside the code under test, so it never masks the behaviour being measured.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

from common import CODE, LOGS, RUN_DIR, emit, host_state

sys.path.insert(0, str(CODE))
import bench  # noqa: E402

REPAIRED_CHILD = """
import json, sys, time
sys.path.insert(0, %r)
import bench
t0 = time.monotonic()
env = bench.environment()
print("ENVJSON " + json.dumps({"seconds": round(time.monotonic() - t0, 3), "env": env}))
""" % str(CODE)

FROZEN_CHILD = """
import json, subprocess, time
# Verbatim copy of the FROZEN probe body (EXP-ICPERF-66fd51/code/bench.py, environment().ver)
def ver(argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=60).stdout.strip().splitlines()[0]
    except Exception as e:
        return f"unavailable: {e}"
t0 = time.monotonic()
line = ver(["Singular", "--version"])
print("FROZENJSON " + json.dumps({"seconds": round(time.monotonic() - t0, 3), "Singular": line}))
"""


def launch_with_inherited_stdin(argv, tag: str, hard_limit_s: float) -> dict:
    r_fd, w_fd = os.pipe()
    out_p, err_p = LOGS / f"{tag}.out", LOGS / f"{tag}.err"
    t0 = time.monotonic()
    killed = False
    with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
        p = subprocess.Popen(argv, stdin=r_fd, stdout=fo, stderr=fe, start_new_session=True)
        os.close(r_fd)
        while True:
            rc = p.poll()
            if rc is not None:
                break
            if time.monotonic() - t0 > hard_limit_s:
                killed = True
                bench.kill_group(p.pid, p)
                rc = None
                break
            time.sleep(0.25)
    os.close(w_fd)
    return {"argv": argv, "returncode": rc, "wall_s": round(time.monotonic() - t0, 3),
            "killed_by_driver_hard_limit": killed, "driver_hard_limit_s": hard_limit_s,
            "stdin": "inherited read end of an open pipe never written to and never closed",
            "stdout": str(out_p.relative_to(RUN_DIR)), "stderr": str(err_p.relative_to(RUN_DIR)),
            "stdout_text": out_p.read_text(errors="replace"),
            "stderr_tail": err_p.read_text(errors="replace")[-2000:]}


def main():
    out = {"host_at_start": host_state(), "children": {}}

    rec = launch_with_inherited_stdin([sys.executable, "-c", REPAIRED_CHILD],
                                      "probe_repaired", hard_limit_s=300)
    for ln in rec["stdout_text"].splitlines():
        if ln.startswith("ENVJSON "):
            rec["parsed"] = json.loads(ln[len("ENVJSON "):])
    out["children"]["repaired_environment"] = rec

    rec2 = launch_with_inherited_stdin([sys.executable, "-c", FROZEN_CHILD],
                                       "probe_frozen_control", hard_limit_s=300)
    for ln in rec2["stdout_text"].splitlines():
        if ln.startswith("FROZENJSON "):
            rec2["parsed"] = json.loads(ln[len("FROZENJSON "):])
    out["children"]["frozen_ver_control"] = rec2

    parsed = out["children"]["repaired_environment"].get("parsed")
    if parsed:
        env = parsed["env"]
        (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=1, default=str))
        out["environment_json_written"] = "environment.json"
        out["measured"] = {
            "environment_returned": True,
            "environment_seconds": parsed["seconds"],
            "per_engine_probe_seconds": env.get("version_probe_seconds"),
            "singular_line": env.get("Singular"),
            "singular_is_version_string": bool(env.get("Singular"))
            and not str(env.get("Singular")).startswith("unavailable:"),
            "engines_unavailable": {k: v for k, v in env.items()
                                    if isinstance(v, str) and v.startswith("unavailable:")},
        }
    else:
        out["measured"] = {"environment_returned": False,
                           "why": "the repaired child produced no ENVJSON line; see its logs"}
    out["host_at_end"] = host_state()
    emit("probe_check", out)


if __name__ == "__main__":
    main()
