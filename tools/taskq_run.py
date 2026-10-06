#!/usr/bin/env python3
"""Run an approved experiment's planned run on the taskq queue and write its
run package. Execution plumbing only: it approves nothing, allocates no id and
writes no ledger record. See docs/taskq-execution.md.

    # print the spec (offline)
    python3 tools/taskq_run.py spec EXP-... RUN-... [--commit SHA] -- python3 harness/run_x.py --seed 7
    # submit it (needs the `taskq` package and TASKQ_REDIS_URL)
    python3 tools/taskq_run.py submit EXP-... RUN-... -- python3 harness/run_x.py --seed 7
    # wait, then write experiments/EXP-.../runs/RUN-.../
    python3 tools/taskq_run.py wait T-...
    python3 tools/taskq_run.py package T-... EXP-... RUN-... [--artifact-root DIR]
    # or offline, from a result mirror and the task record saved as JSON
    python3 tools/taskq_run.py package --result-file r.json --task-file t.json EXP-... RUN-...
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import taskq_bridge as bridge  # noqa: E402


def _head_commit(allow_dirty: bool) -> str:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()
    commit = git("rev-parse", "HEAD")
    if not allow_dirty and git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit(
            "error: tracked files differ from HEAD; the worker runs the COMMIT, "
            "not this tree. Commit and push first, or pass --allow-dirty to "
            "submit HEAD anyway.")
    return commit


def _spec_from_args(a: argparse.Namespace) -> dict:
    argv = a.argv
    commit = a.commit or _head_commit(a.allow_dirty)
    return bridge.build_spec(
        a.experiment, a.run, argv, commit, queue=a.queue,
        repetitions=a.repetitions, warmups=a.warmups,
        setup=[s.split() for s in a.setup], cwd=a.cwd,
        env=dict(kv.split("=", 1) for kv in a.env), timeout=a.timeout,
        memory_mb=a.memory_mb, cpus=a.cpus, submitted_by=a.submitted_by,
        labels=dict(kv.split("=", 1) for kv in a.label),
        worker_verify=a.worker_verify)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("spec", "submit"):
        s = sub.add_parser(name)
        s.add_argument("experiment")
        s.add_argument("run")
        s.add_argument("--commit", help="full pushed sha (default: HEAD)")
        s.add_argument("--allow-dirty", action="store_true")
        s.add_argument("--queue", default="cpu")
        s.add_argument("--repetitions", type=int)
        s.add_argument("--warmups", type=int, default=1)
        s.add_argument("--setup", action="append", default=[],
                       help="setup step, whitespace-split (repeatable)")
        s.add_argument("--cwd", default=".")
        s.add_argument("--env", action="append", default=[], metavar="K=V")
        s.add_argument("--label", action="append", default=[], metavar="K=V")
        s.add_argument("--timeout", type=float, default=3600)
        s.add_argument("--memory-mb", type=int)
        s.add_argument("--cpus", type=int)
        s.add_argument("--submitted-by", default="executor")
        s.add_argument("--worker-verify", action="store_true",
                       help="ask the worker for an ADVISORY certificate check")

    w = sub.add_parser("wait")
    w.add_argument("task_id")
    w.add_argument("--timeout", type=float)
    k = sub.add_parser("package")
    k.add_argument("task_id", nargs="?")
    k.add_argument("experiment")
    k.add_argument("run")
    k.add_argument("--experiments-root", default=os.path.join(REPO, "experiments"))
    k.add_argument("--artifact-root", help="local copy of the worker --artifact-dir")
    k.add_argument("--result-file")
    k.add_argument("--task-file")
    k.add_argument("--inputs-file", help="JSON for run.inputs (curve_id, seed, parameters)")
    argv = sys.argv[1:] if argv is None else list(argv)
    # Everything after the first `--` is the command, verbatim.
    command: list[str] = []
    if "--" in argv:
        cut = argv.index("--")
        argv, command = argv[:cut], argv[cut + 1:]
    a = p.parse_args(argv)
    a.argv = command
    if a.cmd in ("spec", "submit") and not command:
        p.error("give the command after `--`")

    try:
        if a.cmd == "spec":
            print(json.dumps(_spec_from_args(a), indent=2, sort_keys=True))
        elif a.cmd == "submit":
            print(json.dumps(bridge.submit(_spec_from_args(a)), indent=2))
        elif a.cmd == "wait":
            task = bridge.wait(a.task_id, a.timeout)
            print(json.dumps({"task_id": a.task_id,
                              "state": (task or {}).get("state")}, indent=2))
            return 0 if task and task.get("state") in bridge.TASKQ_TERMINAL_STATES else 1
        elif a.cmd == "package":
            inputs = None
            if a.inputs_file:
                with open(a.inputs_file, encoding="utf-8") as fh:
                    inputs = json.load(fh)
            exp_dir = os.path.join(a.experiments_root, a.experiment)
            if a.result_file:
                with open(a.result_file, encoding="utf-8") as fh:
                    result = json.load(fh)
                task = None
                if a.task_file:
                    with open(a.task_file, encoding="utf-8") as fh:
                        task = json.load(fh)
                fetch = (bridge.dir_fetch(a.artifact_root, result["task_id"],
                                          result["attempt"])
                         if a.artifact_root else bridge.uri_fetch)
                run_dir = bridge.write_run_package(result, None, task, exp_dir,
                                                   a.run, fetch, inputs=inputs)
            else:
                if not a.task_id:
                    raise SystemExit("error: give a task id or --result-file")
                fetch = bridge.uri_fetch
                if a.artifact_root:
                    _, result = bridge.fetch(a.task_id)
                    if result is None:
                        raise SystemExit(f"error: {a.task_id} has no result yet")
                    fetch = bridge.dir_fetch(a.artifact_root, a.task_id, result["attempt"])
                run_dir = bridge.package_task(a.task_id, exp_dir, a.run,
                                              artifact_fetch=fetch, inputs=inputs)
            print(os.path.relpath(run_dir, REPO))
    except (bridge.BridgeError, bridge.TaskqUnavailable, FileExistsError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
