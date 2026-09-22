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
SOURCES = ["costmodel.py", "arity.py", "pdp.py", "driver.py", "launch.py"]


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


def _summarise(d):
    """Verdicts on the preregistered predictions, read off the raw result."""
    bt, dl, sl = d["budget_table"], d["degree_law"], d["solver_ladder"]
    rows = bt["with_frobenius"]
    def cells(m):
        return [c for r in rows for c in r["cells"] if c.get("m") == m]
    m2 = cells(2); m3 = cells(3)
    q1 = all(c.get("free_oracle_loses") or c.get("log2_budget", 0) <= 10
             for c in m2 + m3)
    q2 = all(c.get("log2_budget") is not None and c["log2_budget"] <= -20 for c in m2)
    q3 = bool(dl["law_holds"])
    dens = dl.get("anf_density_range")
    q4 = bool(dens and dens[0] >= 0.125)
    def best(r):
        live = [c for c in r["cells"] if c.get("log2_budget") is not None
                and c["log2_budget"] > 0]
        return min(live, key=lambda c: c["log2_anf_deficit"]) if live else None
    anf = {r["n"]: (best(r)["log2_anf_deficit"] if best(r) else None) for r in rows}
    q5 = (all(v is not None and v > 0 for n, v in anf.items() if n <= 283)
          and all(v is not None and v < 0 for n, v in anf.items() if n in (409, 571)))
    fit = sl.get("2", {}).get("fits", {}).get("sat", {})
    lo, hi = (fit.get("ci95") or [None, None])
    q6 = bool(lo is not None and 0.45 <= lo and hi <= 0.70
              and lo <= 0.5805 and hi >= 0.5359)
    return dict(
        experiment="EXP-ICPERF-783e9e",
        preregistered_verdicts=dict(Q1_no_low_arity_headroom=q1, Q2_m2_dead_everywhere=q2,
                                    Q3_degree_law=q3, Q4_anf_dense=q4,
                                    Q5_anf_crossover=q5, Q6_solver_exponent=q6),
        all_predictions_held=all([q1, q2, q3, q4, q5, q6]),
        minimum_viable_arity=bt["minimum_viable_arity"],
        minimum_viable_arity_no_frobenius=bt["minimum_viable_arity_no_frobenius"],
        anf_deficit_at_best_arity=anf,
        anf_density_range=dens,
        degree_law_cells=dl["cells_measured"],
        solver_exponent_fits={k: v["fits"] for k, v in sl.items()},
    )


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
        metrics = _summarise(json.loads((rd / "raw-result.json").read_text()))
        (rd / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True))

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
            "seed": plan["panel"].get("seed", 3),
            "parameters": {k: plan["panel"][k] for k in
                           ("q", "m_values", "targets", "degree_cells",
                            "ladders", "ladder_timeout_seconds")},
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
