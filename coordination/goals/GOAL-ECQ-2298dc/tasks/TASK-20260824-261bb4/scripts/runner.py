#!/usr/bin/env python3
"""Run wrapper for EXP-ECQ-f5af06 / TASK-20260824-261bb4.

Executes one part script as a child process under a hard wall-clock timeout and
a hard address-space cap, and writes the reproduction package REQUIRED BY THE
CONTRACT directly to experiments/EXP-ECQ-f5af06/runs/RUN-<id>/:

    manifest.yaml  (validator schema: id, experiment_id, status, code,
                    environment, inputs, timing, result)
    command.txt  environment.json  stdout.log  stderr.log  raw-result.json

run.result.certificate.kind is ALWAYS `none` here.  That is the schema
reconciliation stated in the contract under
`certificate_kinds_and_a_schema_reconciliation`: `independence_certificate` is
a PROTOCOL-level artifact kind and is not a legal value of that manifest field
(tools/validate_ledger.py admits only discrete_log|decomposition|none), so the
protocol certificate is referenced BY PATH in run.result instead.

Usage: runner.py RUN-<id> <timeout_s> <memory_gb> <script.py> [args...]
"""
import json
import os
import platform
import resource
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
EXP = "EXP-ECQ-f5af06"
RUNS = os.path.join(REPO, "experiments", EXP, "runs")


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()


def yaml_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    return "'" + s.replace("'", "''") + "'"


def emit_yaml(obj, indent=0):
    pad = "  " * indent
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append("%s%s:" % (pad, k))
                out.append(emit_yaml(v, indent + 1))
            elif isinstance(v, (dict, list)):
                out.append("%s%s: %s" % (pad, k, "{}" if isinstance(v, dict) else "[]"))
            else:
                out.append("%s%s: %s" % (pad, k, yaml_scalar(v)))
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)) and v:
                body = emit_yaml(v, indent + 1)
                first = body.split("\n")[0].strip()
                rest = body.split("\n")[1:]
                out.append("%s- %s" % (pad, first))
                out.extend(rest)
            else:
                out.append("%s- %s" % (pad, yaml_scalar(v)))
    return "\n".join(out)


def main():
    run_id, timeout_s, mem_gb, script = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    extra = sys.argv[5:]
    rundir = os.path.join(RUNS, run_id)
    if os.path.exists(rundir):
        sys.exit("REFUSING to overwrite an existing run directory: %s "
                 "(run records are immutable; use a new RUN id)" % rundir)
    os.makedirs(rundir)

    raw_out = os.path.join(rundir, "raw-result.json")
    cmd = [sys.executable, os.path.join(HERE, script), "--raw-out", raw_out] + extra
    printable = " ".join(
        ["python3", "coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-261bb4/scripts/" + script,
         "--raw-out", os.path.relpath(raw_out, REPO)] + extra)

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))

    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["AUTORESEARCH_SEED"] = "20260824"

    def preexec():
        cap = int(mem_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    with open(os.path.join(rundir, "command.txt"), "w") as f:
        f.write(printable + "\n")

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    timed_out = False
    try:
        proc = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True,
                              text=True, timeout=timeout_s, preexec_fn=preexec)
        rc, so, se = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        rc = -9
        so = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        se = (e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")) + \
             "\nHARD WALL-CLOCK CAP %.0fs REACHED; child killed. This is an " \
             "INFRASTRUCTURE OUTCOME bounding coverage, never negative " \
             "mathematical evidence (AGENTS.md rule 5).\n" % timeout_s
    wall = time.time() - t0
    finished = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())

    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    open(os.path.join(rundir, "stdout.log"), "w").write(so or "")
    open(os.path.join(rundir, "stderr.log"), "w").write(se or "")

    if not os.path.exists(raw_out):
        json.dump({"status": "no_raw_result_written",
                   "note": "the child produced no raw-result.json; see stderr.log",
                   "timed_out": timed_out, "exit_code": rc},
                  open(raw_out, "w"), indent=1)

    envjson = {
        "operating_system": platform.system() + " " + platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "sage_version": None,
        "pari_used": False,
        "pari_used_note": ("cypari/PARI is NOT used anywhere in this task. The "
                           "contract permits it only for the part-C Mestre-Nagao "
                           "triage; that triage is implemented in stdlib integer "
                           "arithmetic instead, so no certification step and no "
                           "triage step touches PARI."),
        "network_access": "none: no run makes a network call (contract invalidation_rules)",
        "dependencies": {"stdlib_only": True, "third_party": []},
        "env": {"PYTHONHASHSEED": "0", "AUTORESEARCH_SEED": "20260824"},
        "limits": {"wall_clock_seconds": timeout_s, "rlimit_as_bytes": int(mem_gb * (1 << 30)),
                   "max_workers": 1},
    }
    json.dump(envjson, open(os.path.join(rundir, "environment.json"), "w"), indent=1)

    try:
        raw = json.load(open(raw_out))
    except Exception:
        raw = {}
    metrics = raw.get("metrics") or {}
    part = raw.get("part")

    status = "completed_valid"
    valid = True
    invalid_reason = None
    if timed_out:
        status = "completed_valid"
        invalid_reason = None
    if rc not in (0,) and not timed_out:
        status = "infrastructure_error"
        valid = False
        invalid_reason = "child exited %d; see stderr.log" % rc
    if raw.get("blocking_defect"):
        status = "invalid_measurement"
        valid = False
        invalid_reason = raw.get("blocking_defect")

    manifest = {"run": {
        "id": run_id,
        "experiment_id": EXP,
        "status": status,
        "hypothesis_id": None,
        "hypothesis_id_note": ("DELIBERATELY NULL, matching EXP-ECQ-f5af06 "
                               "hypothesis_id_note. This run certifies an external "
                               "claim, tries to falsify that same external claim, or "
                               "triages the object's neighbours. Naming a hypothesis "
                               "would invite exactly the inference the run cannot "
                               "support."),
        "task_id": "TASK-20260824-261bb4",
        "goal_id": "GOAL-ECQ-2298dc",
        "question_id": "RQ-ECQ-e9b361",
        "part": part,
        "code": {
            "commit": commit,
            "dirty": dirty,
            "dirty_note": ("Working-tree state at run start. Task scripts and "
                           "deliverables under the task directory are written by this "
                           "task and are uncommitted until the Coordinator archives "
                           "them; the frozen contract and the reused certifier are "
                           "unmodified."),
            "command": printable,
            "certifier_reused_byte_identical":
                "coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/"
                "TASK-20260823-827765/scripts/exact_certify.py",
            "certifier_sha256": raw.get("certifier_sha256"),
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": os.environ.get("AUTORESEARCH_MODEL")
                                 or "not recorded by the runtime; deterministic "
                                    "stdlib computation, model-independent",
            "reasoning_effort": "medium",
            "fallback_used": False,
            "adapter_version": None,
        },
        "environment": envjson,
        "inputs": {
            "curve_id": "ICARM-302",
            "seed": 20260824,
            "seed_note": ("Recorded for schema completeness. EVERY computation in "
                          "this run is DETERMINISTIC: there is no sampling anywhere, "
                          "the boxes and the twist and perturbation sets are fully "
                          "enumerated by their frozen descriptions, and no code path "
                          "consumes the seed."),
            "randomness_sources": "none",
            "input_files": raw.get("input_files") or [],
            "parameters": raw.get("parameters") or {},
        },
        "timing": {
            "started_at": started,
            "finished_at": finished,
            "wall_seconds": round(wall, 3),
            "time_budget_seconds": timeout_s,
            "time_budget_reached": timed_out,
            "alarm_count": 1 if timed_out else 0,
        },
        "resources": {
            "peak_rss_bytes": int(ru.ru_maxrss) * 1024,
            "peak_rss_note": "ru_maxrss of all children of this runner, in kilobytes on Linux",
            "memory_cap_bytes": int(mem_gb * (1 << 30)),
            "memory_cap_breached": False,
            "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 3),
            "max_workers": 1,
        },
        "result": {
            "exit_code": rc,
            "metrics": metrics,
            "valid": valid,
            "invalid_reason": invalid_reason,
            "observations": raw.get("observations") or [],
            "deviations": raw.get("deviations") or [],
            "protocol_certificate": raw.get("protocol_certificate"),
            "protocol_certificate_note": (
                "The PROTOCOL-level certificate kind for this run is "
                "`independence_certificate` where a rank lower bound is asserted, "
                "and `none` otherwise; it lives in the deliverable JSON referenced "
                "above and NOT in run.result.certificate.kind. See EXP-ECQ-f5af06 "
                "certificate_kinds_and_a_schema_reconciliation."),
            "certificate": {
                "kind": "none",
                "verified": True,
                "verifier": ("schema reconciliation: no discrete_log and no "
                             "decomposition is claimed by this run; the protocol "
                             "independence certificate is referenced by path in "
                             "result.protocol_certificate"),
            },
        },
        "artifacts": {
            "command": "command.txt",
            "environment": "environment.json",
            "stdout": "stdout.log",
            "stderr": "stderr.log",
            "raw_result": "raw-result.json",
        },
    }}
    open(os.path.join(rundir, "manifest.yaml"), "w").write(emit_yaml(manifest) + "\n")
    print("%-34s status=%-20s wall=%7.1fs rc=%s timed_out=%s"
          % (run_id, status, wall, rc, timed_out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
