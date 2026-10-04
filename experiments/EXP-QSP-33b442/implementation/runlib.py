#!/usr/bin/env python3
"""EXP-QSP-33b442 run wrapper: creates one immutable run directory per stage
invocation and writes every AGENTS.md artifact-policy field into its manifest.

Written for this experiment.  Nothing here reads analysis/qsp-ecc2k130/.

Layout produced (docs/evidence-and-reproducibility.md):
  experiments/EXP-QSP-33b442/runs/<RUN-ID>/
      manifest.yaml  command.txt  environment.json
      stdout.log     stderr.log   raw-result.json
      (+ certificates/ for Stage 3)
"""
from __future__ import annotations

import datetime
import json
import os
import platform
import resource
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
EXP_DIR = os.path.join(REPO, "experiments", "EXP-QSP-33b442")
RUNS_DIR = os.environ.get("QSP_RUNS_DIR") or os.path.join(EXP_DIR, "runs")
# QSP_RUNS_DIR exists ONLY so implementation smoke tests write to the session
# scratchpad instead of the immutable runs/ tree. Every reported run below
# uses the default path; each manifest records the directory it was written to.

EXPERIMENT_ID = "EXP-QSP-33b442"
HYPOTHESIS_ID = "H-QSP-5540d7"
TASK_ID = "TASK-20260917-892420"
BASE_SEED = 20260917


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout.strip()


def git_state() -> dict:
    status = git("status", "--porcelain")
    return {
        "commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(status),
        "dirty_paths": [l[3:] for l in status.splitlines()] if status else [],
    }


def compiler_info() -> dict:
    try:
        v = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    except Exception as exc:                                   # pragma: no cover
        v = "unavailable: %s" % exc
    return {"compiler": v, "flags": "-O2", "helper_source": "implementation/gf2rc.c",
            "helper_binary": "implementation/gf2rc (built at run time, not committed)"}


def environment() -> dict:
    deps = {}
    for mod in ("sympy",):
        try:
            deps[mod] = __import__(mod).__version__
        except Exception:
            deps[mod] = "not installed"
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "hostname_class": "container (4 cores, 15 GB RAM, no CAS installed)",
        "cpu_count": os.cpu_count(),
        "dependencies": deps,
        "external_engines": {
            "sage": "not installed", "magma": "not installed",
            "macaulay2": "not installed", "singular": "not installed",
            "msolve": "not installed", "ntl_or_flint": "not installed",
        },
        "compiler": compiler_info(),
        "randomness_sources": (
            "Python random.Random only, always explicitly seeded; every stream label "
            "recorded in inputs.seeds. Stages 0, 1, 2, 3 and every control are "
            "seed-free in their candidate sets: the only random.Random used there "
            "drives Cantor-Zassenhaus equal-degree splitting, whose OUTPUT (the set "
            "of irreducible factors) is unique and independent of the stream. "
            "No os.urandom, no time-derived seed, no hash randomisation dependence "
            "(PYTHONHASHSEED recorded below)."
        ),
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "unset (irrelevant: no set/dict "
                                         "iteration order affects any recorded number)"),
    }


INFERENCE = {
    "requested_policy": "executor-implementation",
    "requested_policy_source": "ledger/handoffs/%s.yaml inference.policy" % TASK_ID,
    "reasoning_effort": "medium",
    "reasoning_effort_source": "handoff inference.reasoning_effort; "
                               "orchestration/model-policies.yaml executor-implementation",
    "backend": "anthropic (Claude Code runtime, claude_code binding)",
    "adapter_resolved_binding": "anthropic:claude-sonnet-5",
    "adapter_resolve_command": "python3 -m orchestration.adapter resolve --role executor",
    "resolved_model_id": "claude-opus-5",
    "model_provenance": (
        "Self-reported by the serving runtime in the session system prompt. The "
        "adapter binding for policy executor-implementation on this backend is "
        "anthropic:claude-sonnet-5, so the SERVING model differs from the adapter "
        "binding. Recorded here rather than silently substituted (AGENTS.md rule 11 "
        "and the handoff's manifest constraint). The divergence is upward (a "
        "stronger model than the policy binding), the Executor did not select it, "
        "and no degradation applies."
    ),
    "probe_verified": False,
    "probe_status": "not probe-verified: no model probe was run in this session",
    "fallback_used": False,
    "fallback_reason": None,
    "degraded_requirements": [],
    "model_in_the_measurement_loop": False,
    "model_in_the_measurement_loop_note": (
        "Every number produced by these runs comes from deterministic Python/C "
        "arithmetic in experiments/EXP-QSP-33b442/implementation/. No model output "
        "enters any count, ratio, histogram or certificate."
    ),
}


class Run:
    def __init__(self, run_id: str, stage: str, command: str, inputs: dict,
                 certificate_kind: str = "none"):
        self.run_id = run_id
        self.stage = stage
        self.command = command
        self.inputs = inputs
        self.certificate_kind = certificate_kind
        self.dir = os.path.join(RUNS_DIR, run_id)
        if os.path.exists(self.dir):
            raise SystemExit(
                "REFUSING to reuse run directory %s: run records are immutable; "
                "a corrected run takes a NEW run id." % self.dir)
        os.makedirs(self.dir)
        self.t0 = time.time()
        self.started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.git = git_state()
        self.env = environment()
        self.stdout_lines: list[str] = []
        self.stderr_lines: list[str] = []
        with open(os.path.join(self.dir, "command.txt"), "w") as fh:
            fh.write(command + "\n")
        with open(os.path.join(self.dir, "environment.json"), "w") as fh:
            json.dump(self.env, fh, indent=1, sort_keys=True)

    def log(self, *parts) -> None:
        line = " ".join(str(p) for p in parts)
        self.stdout_lines.append(line)
        print(line, flush=True)

    def warn(self, *parts) -> None:
        line = " ".join(str(p) for p in parts)
        self.stderr_lines.append(line)
        print(line, file=sys.stderr, flush=True)

    def path(self, *parts) -> str:
        p = os.path.join(self.dir, *parts)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def finish(self, raw: dict, status: str, validity_reason: str,
               certificate: dict | None = None, deviations: list | None = None,
               anomalies: list | None = None) -> None:
        wall = time.time() - self.t0
        ru = resource.getrusage(resource.RUSAGE_SELF)
        ruc = resource.getrusage(resource.RUSAGE_CHILDREN)
        with open(os.path.join(self.dir, "raw-result.json"), "w") as fh:
            json.dump(raw, fh, indent=1, sort_keys=True)
        with open(os.path.join(self.dir, "stdout.log"), "w") as fh:
            fh.write("\n".join(self.stdout_lines) + "\n")
        with open(os.path.join(self.dir, "stderr.log"), "w") as fh:
            fh.write("\n".join(self.stderr_lines) + ("\n" if self.stderr_lines else ""))
        manifest = {
            "run": {
                "id": self.run_id,
                "experiment_id": EXPERIMENT_ID,
                "hypothesis_id": HYPOTHESIS_ID,
                "task_id": TASK_ID,
                "stage": self.stage,
                "status": status,
                "specification_version": 1,
                "amendments_in_force": ["AMD-20260917-001"],
                "code": {
                    "command": self.command,
                    "commit": self.git["commit"],
                    "branch": self.git["branch"],
                    "dirty": self.git["dirty"],
                    "dirty_paths": self.git["dirty_paths"],
                    "dirty_tree_note": (
                        "The working tree carries this task's own write scope "
                        "(experiments/EXP-QSP-33b442/implementation, runs, amendments, "
                        "execution-report.yaml) uncommitted: the Executor does not commit. "
                        "The Coordinator's snapshot archive commits the package."),
                    "implementation_paths": [
                        "experiments/EXP-QSP-33b442/implementation/qspcore.py",
                        "experiments/EXP-QSP-33b442/implementation/runlib.py",
                        "experiments/EXP-QSP-33b442/implementation/gf2rc.c",
                        "experiments/EXP-QSP-33b442/implementation/%s" % self.stage_script(),
                    ],
                },
                "inference": INFERENCE,
                "environment": self.env,
                "inputs": self.inputs,
                "timing": {
                    "started_at": self.started_at,
                    "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "wall_seconds": round(wall, 3),
                    "budget_wall_clock_seconds": 7200,
                    "budget_exceeded": wall > 7200,
                },
                "resources": {
                    "peak_rss_bytes": max(ru.ru_maxrss, ruc.ru_maxrss) * 1024,
                    "peak_rss_bytes_note": "ru_maxrss (KiB on Linux) x 1024, self and children",
                    "cpu_seconds": round(ru.ru_utime + ru.ru_stime + ruc.ru_utime + ruc.ru_stime, 3),
                    "workers": 1,
                    "memory_cap_gb": 4,
                },
                "result": {
                    "valid": status == "completed_valid",
                    "validity_status": status,
                    "validity_reason": validity_reason,
                    "certificate": certificate or {
                        "kind": self.certificate_kind,
                        "verified": None,
                        "verifier": None,
                    },
                    "raw_result": "raw-result.json",
                },
                "protocol_deviations": deviations or [],
                "anomalies": anomalies or [],
                "artifacts": {
                    "command": "command.txt",
                    "environment": "environment.json",
                    "stdout": "stdout.log",
                    "stderr": "stderr.log",
                    "raw_result": "raw-result.json",
                },
                "provenance_declaration": (
                    "Every number in raw-result.json was produced by this invocation. "
                    "No value was read from analysis/qsp-ecc2k130/explore/ (explore.json, "
                    "explore_fast.json, shape_census_131.json, or its README tables). "
                    "Code adapted from that directory is declared in the header of "
                    "implementation/qspcore.py and implementation/gf2rc.c."
                ),
            }
        }
        extra = {}
        certdir = os.path.join(self.dir, "certificates")
        if os.path.isdir(certdir):
            extra["certificates_dir"] = "certificates/"
            extra["certificate_count"] = len(os.listdir(certdir))
        manifest["run"]["artifacts"].update(extra)
        manifest["run"]["artifacts"]["run_directory"] = self.dir
        with open(os.path.join(self.dir, "manifest.yaml"), "w") as fh:
            fh.write(_yaml(manifest))
        print("\n[run %s] %s  wall=%.1fs  peak_rss=%.0f MiB  -> %s" % (
            self.run_id, status, wall,
            manifest["run"]["resources"]["peak_rss_bytes"] / 1048576, self.dir), flush=True)

    def stage_script(self) -> str:
        return {"stage_1": "stage1.py", "stage_1b": "stage1b.py", "stage_2": "stage2.py",
                "stage_3": "stage3.py", "stage_4": "stage4.py"}.get(self.stage, "unknown")


# --- minimal, dependency-free YAML emitter (block style, safe quoting) ------

def _scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if s == "":
        return "''"
    if ("\n" in s or len(s) > 90 or s[0] in "&*!|>%@`{}[]#-?," or ": " in s
            or s.endswith(":") or s.strip() != s or s.lower() in ("yes", "no", "true", "false", "null", "on", "off")):
        return json.dumps(s)
    return s


def _yaml(obj, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(obj, dict):
        if not obj:
            return pad + "{}\n"
        out = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append("%s%s:\n%s" % (pad, k, _yaml(v, indent + 2)))
            elif isinstance(v, (dict, list)):
                out.append("%s%s: %s\n" % (pad, k, "{}" if isinstance(v, dict) else "[]"))
            else:
                out.append("%s%s: %s\n" % (pad, k, _scalar(v)))
        return "".join(out)
    if isinstance(obj, list):
        if not obj:
            return pad + "[]\n"
        out = []
        for v in obj:
            if isinstance(v, (dict, list)) and v:
                # render the item body at indent + 2 and replace the first
                # line's leading pad with "- ", so CONTINUATION lines line up
                # with the first key instead of sitting two columns deeper
                # (which is not valid YAML).
                body = _yaml(v, indent + 2)
                out.append("%s- %s" % (pad, body[indent + 2:]))
            else:
                out.append("%s- %s\n" % (pad, _scalar(v)))
        return "".join(out)
    return pad + _scalar(obj) + "\n"
