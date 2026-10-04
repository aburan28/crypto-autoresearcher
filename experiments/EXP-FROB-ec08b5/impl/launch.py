#!/usr/bin/env python3
"""Launcher for EXP-FROB-ec08b5: runs the driver and records the run manifest.

Everything recorded here is observed, never assumed: argv as executed, captured
stdout/stderr, the resolved interpreter, the sha256 of every source file that
ran, and the timings actually measured.  Nothing is written for a phase that did
not run.
"""
import argparse, json, hashlib, os, platform, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
IMPL = Path(__file__).resolve().parent
SOURCES = ["lattice.py", "orbits.py", "analysis.py", "verify_field.py",
           "curve_panel.py", "driver.py", "report.py", "launch.py"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    try:
        return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True,
                              text=True, timeout=120).stdout.strip()
    except Exception:
        return ""


def tracked_status(rel):
    out = git("status", "--porcelain", "--", rel)
    if not out:
        return "clean"
    return "untracked" if out.startswith("??") else "modified"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()

    rd = Path(a.run_dir).resolve()
    rd.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(a.plan).read_text())

    sage = shutil.which("sage") or "/opt/conda-sage/bin/sage"
    argv = [sage, "-python", str(IMPL / "driver.py"),
            "--run-dir", str(rd), "--plan", str(Path(a.plan).resolve())]
    if a.resume:
        argv.append("--resume")
    (rd / "command.txt").write_text(json.dumps(argv) + "\n")

    sage_version = subprocess.run([sage, "--version"], capture_output=True,
                                  text=True, timeout=600).stdout.strip()
    deps = {}
    for mod in ("sympy", "yaml"):
        try:
            deps[mod] = __import__(mod).__version__
        except Exception:
            deps[mod] = None
    env = dict(operating_system=platform.platform(), architecture=platform.machine(),
               python_version=platform.python_version(), sage_version=sage_version,
               sage_path=sage, dependencies=deps, cpu_count=os.cpu_count())
    (rd / "environment.json").write_text(json.dumps(env, indent=1, sort_keys=True))

    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    proc = subprocess.run(argv, capture_output=True, text=True)
    wall = time.perf_counter() - t0
    finished = datetime.now(timezone.utc)
    (rd / "stdout.log").write_text(proc.stdout)
    (rd / "stderr.log").write_text(proc.stderr)

    ok = proc.returncode == 0 and (rd / "raw-result.json").exists()
    metrics = {}
    if ok:
        subprocess.run([sys.executable, str(IMPL / "report.py"), "--run-dir", str(rd)],
                       check=True, capture_output=True, text=True)
        metrics = json.loads((rd / "metrics.json").read_text())

    src = {}
    for s in SOURCES:
        rel = os.path.relpath(IMPL / s, REPO)
        src[rel] = dict(sha256=sha(IMPL / s), status=tracked_status(rel))
    rel_plan = os.path.relpath(Path(a.plan).resolve(), REPO)
    src[rel_plan] = dict(sha256=sha(a.plan), status=tracked_status(rel_plan))

    manifest = {"run": {
        "id": plan["run_id"],
        "experiment_id": plan["experiment_id"],
        "hypothesis_id": plan["hypothesis_id"],
        "task_id": plan["task_id"],
        "status": "completed_valid" if ok else "failed",
        "code": {
            "commit": git("rev-parse", "HEAD"),
            "dirty": bool(git("status", "--porcelain")),
            "command": " ".join(argv),
            "source": {"files": src, "file_count": len(src),
                       "all_pinned": True,
                       "all_clean": all(v["status"] == "clean" for v in src.values()),
                       "note": ("Every executed source file is pinned by sha256. The "
                                "commit alone does not identify this run's code while "
                                "these files are new; the hashes do, and stay valid "
                                "after the files are committed.")},
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "none (deterministic harness execution)",
            "reasoning_effort": None, "fallback_used": False, "adapter_version": None,
        },
        "environment": env,
        "inputs": {
            "trial_plan": rel_plan,
            "trial_plan_sha256": sha(a.plan),
            "seed": plan["panel"]["seed"],
            "parameters": {k: plan["panel"][k] for k in
                           ("lattice_cells", "census_cells", "curve_cells",
                            "targets", "m_values", "m_cap",
                            "exhaustive_max_field_size")},
        },
        "timing": {
            "started_at": started.isoformat(), "finished_at": finished.isoformat(),
            "wall_seconds": round(wall, 3), "timing_source": "wrapper",
        },
        "result": {
            "metrics": {k: v for k, v in metrics.items()
                        if k not in ("headline", "preregistered_verdicts")},
            "preregistered_verdicts": metrics.get("preregistered_verdicts"),
            "headline": metrics.get("headline"),
            "valid": bool(ok),
            "invalid_reason": None if ok else
                f"driver exit {proc.returncode}; see stderr.log. Execution status only -- "
                "never negative mathematical evidence (AGENTS.md rule 3).",
            "certificate": {
                "kind": "none",
                "note": ("No discrete logarithm is solved and no relation is claimed; "
                         "every measurement is an exact structural census, so the "
                         "solution-certificate gate does not apply."),
            },
        },
    }}
    import yaml
    (rd / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, width=88))
    print(proc.stdout)
    print("run", plan["run_id"], "->", manifest["run"]["status"], f"({wall:.1f}s)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
