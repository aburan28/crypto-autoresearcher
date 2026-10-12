"""AMD-20261002-c7ccde B-3 (5) harness (TASK-20261002-7cf711).

Implements B-3 (2): the v3 comparison of the ARCHIVED A-3 exercise log
(amd-280481/fixtures/exercise-log-a3.json) against fixtures/exercise-log-after-D7.json.

Rules applied, and nothing else:
  * B-1 for step 31: exit code 1 and the A-1 (b) stop message
    "P0 stop (AMD-20261002-280481 A-1 (b)):" in the stderr tail (B-3 (2) wording).
  * A-3 + B-2 for every other step: identity of every recorded field of the step except
    the exclusions B-2 enumerates -- timestamps, paths, and host timing and memory
    figures (wall seconds, CPU seconds, peak RSS).  Paths include the scratch fixture
    directory and the A-3 copy's path (the retargeting).
Nothing is excluded by judgment.  Any residual difference is reported as a failure of the
step, with the exact differing lines.  For information only (never used in the verdict),
the residual lines are also re-compared with process ids masked, so that the Coordinator
can see whether process ids are the only residual.

Only the B-3 (2) mode is implemented: the task stops at the first failing B-3 check, so
the B-3 (3)/(4) modes were not written (no untested code is archived).

Usage: <PY> check_exercise_v3.py archived --old LOG --new LOG --out JSON
Standard library only.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys

TS = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+00:00|Z)?")
STAMP = re.compile(r"\d{8}T\d{6}Z")
WALL = re.compile(r"\bwall \d+(\.\d+)? s\b")
CPU = re.compile(r"\bcpu \d+(\.\d+)? s\b", re.I)
RSS = re.compile(r"\bpeak_rss \d+\b")
A3_PATH = "experiments/EXP-PFDR-011cd0/amd-280481/analyze_relcensus.py"
ORIG_PATH = "experiments/EXP-PFDR-011cd0/analyze_relcensus.py"
PID = re.compile(r"\bpid \d+\b")
FIELDS = ("step", "cmd", "exit_code", "expected_exit", "check", "expectation_met",
          "stdout_tail", "stderr_tail")
STOP_MSG = "P0 stop (AMD-20261002-280481 A-1 (b)):"


def norm(value, fx):
    s = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    s = s.replace(fx, "<FX>").replace(A3_PATH, ORIG_PATH)
    s = TS.sub("<TS>", s)
    s = STAMP.sub("<STAMP>", s)
    s = WALL.sub("wall <SEC> s", s)
    s = CPU.sub("cpu <SEC> s", s)
    s = RSS.sub("peak_rss <RSS>", s)
    return s


def diff_lines(x, y):
    return [l for l in difflib.ndiff(x.splitlines(), y.splitlines()) if l[:1] in "+-"]


def archived(a):
    old, new = json.load(open(a.old)), json.load(open(a.new))
    steps = []
    for i, (o, n) in enumerate(zip(old["steps"], new["steps"]), 1):
        ent = {"step": i, "label_new": n.get("step")}
        if i == 31:
            b1 = {"i_exit_code_1": n.get("exit_code") == 1,
                  "ii_stop_message_in_stderr_tail": STOP_MSG in (n.get("stderr_tail") or ""),
                  "p0_stop_json_in_stderr_tail": '"p0_stop": "AMD-20261002-280481 A-1 (b)"' in (n.get("stderr_tail") or ""),
                  "expected_rungs_22_24_in_stderr_tail": '"expected_rungs": [22, 24]' in (n.get("stderr_tail") or "")}
            ent.update({"rule": "B-1 (B-3 (2): exit 1 and stop message)", "b1_checks": b1,
                        "pass": b1["i_exit_code_1"] and b1["ii_stop_message_in_stderr_tail"]})
        else:
            fd, info = {}, {}
            for k in FIELDS:
                x, y = norm(o.get(k), old["fx"]), norm(n.get(k), new["fx"])
                if x != y:
                    dl = diff_lines(x, y)
                    fd[k] = dl
                    info[k] = {"residual_lines_equal_with_pids_masked": PID.sub("pid <PID>", x) == PID.sub("pid <PID>", y)}
            ent.update({"rule": "A-3 identity under B-2 exclusions (timestamps, paths, wall/CPU seconds, peak RSS)",
                        "differing_fields": sorted(fd), "residual_differences": fd,
                        "information_only_not_a_verdict": info, "pass": not fd})
        steps.append(ent)
    res = {"what": "AMD-20261002-c7ccde B-3 (2): archived exercise-log-a3.json vs exercise-log-after-D7.json",
           "old_log": a.old, "new_log": a.new, "steps_old": len(old["steps"]), "steps_new": len(new["steps"]),
           "exclusions_applied": ["ISO timestamps", "run stamps YYYYMMDDTHHMMSSZ", "scratch fixture path (fx)",
                                  "A-3 copy path retargeting", "wall <n> s", "cpu <n> s", "peak_rss <n>"],
           "steps": steps,
           "failing_steps": [s["step"] for s in steps if not s["pass"]],
           "pass": len(old["steps"]) == len(new["steps"]) == 38 and all(s["pass"] for s in steps)}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("steps_old", "steps_new", "failing_steps", "pass")}))
    return 0 if res["pass"] else 1


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    p = sp.add_parser("archived")
    p.add_argument("--old", required=True)
    p.add_argument("--new", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    return archived(a)


if __name__ == "__main__":
    sys.exit(main())
