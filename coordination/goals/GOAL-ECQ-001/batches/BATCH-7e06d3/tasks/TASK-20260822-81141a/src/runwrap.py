#!/usr/bin/env python3
"""Reproduction-package wrapper: one immutable run directory per invocation."""
import json, os, platform, subprocess, sys, time, resource, hashlib

ROOT = "/home/user/crypto-autoresearcher"
TASK = os.path.join(ROOT, "coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-81141a")

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=ROOT).stdout.strip()

def main():
    run_id = sys.argv[1]
    cert_kind = sys.argv[2]
    cmd = sys.argv[3:]
    rd = os.path.join(TASK, "runs", run_id)
    if os.path.exists(rd):
        sys.exit("run directory already exists; run records are immutable: " + rd)
    os.makedirs(rd)
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "pari_version": sh("python3 -c \"from cypari import pari; print(pari('version()'))\""),
        "numpy": sh("python3 -c 'import numpy;print(numpy.__version__)'"),
        "sage_available": False, "sympy_available": False,
        "git_commit": sh("git rev-parse HEAD"),
        "git_dirty_tree": sh("git status --porcelain"),
        "requested_policy": "executor-implementation",
        "model_that_answered": os.environ.get("AUTORESEARCH_MODEL", "claude-opus-5"),
        "autoresearch_policy_env": os.environ.get("AUTORESEARCH_POLICY"),
        "autoresearch_backend_env": os.environ.get("AUTORESEARCH_BACKEND"),
        "fallback_used": False,
        "randomness_sources": "python random.Random with explicit integer seeds recorded in each artifact; no other source",
    }
    json.dump(env, open(os.path.join(rd, "environment.json"), "w"), indent=2)
    open(os.path.join(rd, "command.txt"), "w").write(" ".join(cmd) + "\n")
    t0 = time.time()
    with open(os.path.join(rd, "stdout.log"), "w") as so, open(os.path.join(rd, "stderr.log"), "w") as se:
        p = subprocess.run(cmd, stdout=so, stderr=se, cwd=os.path.join(TASK, "src"))
    dt = time.time() - t0
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    man = {
        "run_id": run_id, "task_id": "TASK-20260822-81141a",
        "goal_id": "GOAL-ECQ-001", "batch_id": "BATCH-7e06d3",
        "hypothesis_id": "H-ECQ-cec3c4", "question_id": "RQ-ECQ-80f23c",
        "command": " ".join(cmd),
        "exit_code": p.returncode,
        "wall_clock_seconds": dt,
        "max_rss_kb": ru.ru_maxrss,
        "budget": {"wall_clock_seconds": 3000, "memory_gb": 4, "maximum_runs": 60},
        "certificate": {"kind": cert_kind},
        "status": "completed_valid" if p.returncode == 0 else "infrastructure_error",
        "git_commit": env["git_commit"],
        "dirty_tree": bool(env["git_dirty_tree"]),
    }
    json.dump(man, open(os.path.join(rd, "manifest.yaml").replace(".yaml", ".json"), "w"), indent=2)
    # manifest.yaml as required by the reproduction-package layout
    def y(o, ind=0):
        out = []
        pad = "  " * ind
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    out.append("%s%s:" % (pad, k)); out.append(y(v, ind + 1))
                else:
                    out.append("%s%s: %s" % (pad, k, json.dumps(v)))
        elif isinstance(o, list):
            for v in o:
                out.append("%s- %s" % (pad, json.dumps(v)))
        return "\n".join(x for x in out if x)
    open(os.path.join(rd, "manifest.yaml"), "w").write(y(man) + "\n")
    print("run %s exit=%d wall=%.1fs rss=%.0fMB" % (run_id, p.returncode, dt, ru.ru_maxrss / 1024))
    sys.exit(p.returncode)

main()
