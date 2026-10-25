"""EXP-SEMAEV-93d5cc trial driver: one cell, both arms, run as a matched pair.

    python3 launch.py --cell <cell> --run-dir <dir> --run-id <RUN-ID>
                      --plan <trial-plan.json> [--dep <cell>=<RUN-ID> ...]

Starts ``worker.py`` for the legacy and the repaired arm at the same time, so
the two arms of a cell share the machine and its load (the per-solve and
cumulative caps of the archived programs are wall-clock caps).  Each arm writes
only under ``<run-dir>/arms/<arm>/``.  When both exit, ``compare.compare``
builds the frozen per-cell table and this driver writes ``raw-result.json`` and
``manifest.yaml``.  It interprets nothing: the table is extraction and the
frozen CTRL-LEGACY-REPRO rule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP_ID = "EXP-SEMAEV-93d5cc"
sys.path.insert(0, str(HERE))

import arms  # noqa: E402
import compare  # noqa: E402

ARCHIVED_RUNS = {
    "icinv-m4": ["experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class"],
    "fib-004": ["experiments/EXP-FIB-001/runs/RUN-FIB-004"],
    "fib-005": ["experiments/EXP-FIB-001/runs/RUN-FIB-005"],
    "fib-decision": ["experiments/EXP-FIB-001/runs/RUN-FIB-006C",
                     "experiments/EXP-FIB-001/runs/RUN-FIB-007",
                     "experiments/EXP-FIB-001/runs/RUN-FIB-008"],
    "mtic-007": ["experiments/EXP-MTIC-001/runs/RUN-MTIC-007"],
    "mtic-008": ["experiments/EXP-MTIC-001/runs/RUN-MTIC-008"],
    "mtic-010b": ["experiments/EXP-MTIC-001/runs/RUN-MTIC-010b"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pack(run_dir: Path) -> dict:
    """arms/ -> arms.tar.gz (sorted members, zeroed mtimes) + per-member sha256."""
    members = sorted(p for p in (run_dir / "arms").rglob("*") if p.is_file())
    digests = {str(p.relative_to(run_dir)): sha256(p) for p in members}
    with tarfile.open(run_dir / "arms.tar.gz", "x:gz") as tar:
        for p in members:
            info = tar.gettarinfo(str(p), arcname=str(p.relative_to(run_dir)))
            info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, "", ""
            with p.open("rb") as stream:
                tar.addfile(info, stream)
    with (run_dir / "arms-manifest.json").open("x") as f:
        json.dump({"archive": "arms.tar.gz", "members": digests}, f, indent=1, sort_keys=True)
        f.write("\n")
    return digests


def unpack_dependency(dep_run: Path, into: Path) -> Path:
    """Extract a finished dependency's arms.tar.gz (checked against its
    arms-manifest.json) so this cell's workers can read its arm outputs."""
    manifest = json.loads((dep_run / "arms-manifest.json").read_text())["members"]
    into.mkdir(parents=True)
    with tarfile.open(dep_run / "arms.tar.gz", "r:gz") as tar:
        tar.extractall(into, filter="data")
    for rel, digest in manifest.items():
        if sha256(into / rel) != digest:
            raise RuntimeError(f"dependency member hash mismatch: {dep_run.name}/{rel}")
    return into


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True)
    ap.add_argument("--run-dir", required=True, type=Path)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--dep", action="append", default=[], help="cell=RUN-ID")
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    plan = json.loads((REPO / args.plan).read_text())
    deps = {}
    for d in args.dep:
        cell, rid = d.split("=", 1)
        deps[cell] = str(unpack_dependency(REPO / "experiments" / EXP_ID / "runs" / rid,
                                           run_dir / "deps" / cell))
    started = datetime.now(timezone.utc)
    t0 = time.time()
    procs = {}
    for arm in arms.ARMS:
        argv = [sys.executable, str(HERE / "worker.py"), "--arm", arm, "--cell", args.cell,
                "--out", str(run_dir / "arms" / arm)]
        for cell, path in deps.items():
            argv += ["--dep", f"{cell}={path}"]
        out = (run_dir / f"arm-{arm}.stdout.log").open("x")
        err = (run_dir / f"arm-{arm}.stderr.log").open("x")
        procs[arm] = (subprocess.Popen(argv, cwd=REPO, stdout=out, stderr=err,
                                       stdin=subprocess.DEVNULL), argv, out, err)
        print(f"started {arm}: pid {procs[arm][0].pid}", flush=True)
    rcs = {}
    for arm, (p, argv, out, err) in procs.items():
        rcs[arm] = p.wait()
        out.close()
        err.close()
        print(f"{arm} exited {rcs[arm]} after {time.time() - t0:.1f}s", flush=True)
    finished = datetime.now(timezone.utc)
    arm_results = {}
    for arm in arms.ARMS:
        f = run_dir / "arms" / arm / "arm-result.json"
        arm_results[arm] = json.loads(f.read_text()) if f.exists() else None
    table, error = None, None
    if all(rc == 0 for rc in rcs.values()):
        try:
            table = compare.compare(args.cell, run_dir)
        except Exception as e:  # noqa: BLE001 -- recorded, never hidden
            error = f"comparison failed: {e!r}"
    else:
        error = f"arm exit codes {rcs}"
    status = "completed" if table is not None else "failed_infrastructure"
    members = pack(run_dir) if (run_dir / "arms").exists() else {}
    shutil.rmtree(run_dir / "arms", ignore_errors=True)
    shutil.rmtree(run_dir / "deps", ignore_errors=True)
    raw = {"experiment_id": EXP_ID, "run_id": args.run_id, "cell": args.cell,
           "archived_runs": ARCHIVED_RUNS[args.cell], "arm_returncodes": rcs,
           "arm_results": arm_results, "comparison": table, "error": error,
           "arms_archive_members": len(members),
           "scientific_conclusion": None}
    with (run_dir / "raw-result.json").open("x") as f:
        json.dump(raw, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    ctrl = (table or {}).get("ctrl_legacy_repro", {}).get("pass")
    manifest = {"run": {
        "id": args.run_id, "experiment_id": EXP_ID, "status": status,
        "code": {"commit": git("rev-parse", "HEAD"),
                 "dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
                 "command": [sys.executable, "experiments/EXP-SEMAEV-93d5cc/implementation/launch.py",
                             "--cell", args.cell, "--run-dir", str(run_dir), "--run-id", args.run_id,
                             "--plan", args.plan] + sum((["--dep", d] for d in args.dep), []),
                 "source_sha256": plan["source_sha256"],
                 "arm_s4_sources": {"legacy": {"path": str(arms.LEGACY_PATH.relative_to(REPO)),
                                               "sha256": arms.LEGACY_SHA256},
                                    "repaired": {"path": str(arms.REPAIRED_PATH.relative_to(REPO)),
                                                 "sha256": arms.REPAIRED_SHA256}}},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                        "machine": platform.machine(), "cpu_count": os.cpu_count(),
                        "sympy": __import__("sympy").__version__,
                        "singular": (arm_results.get("repaired") or {}).get("singular_version")},
        "inputs": {"parameters": {"cell": args.cell, "arms": list(arms.ARMS),
                                  "arm_pairing": "both arms concurrently, one process each",
                                  "dependencies": dict(d.split("=", 1) for d in args.dep),
                                  "archived_runs": ARCHIVED_RUNS[args.cell]},
                   "seeds": "archived seeds and frozen instances of the archived programs, unchanged"},
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(),
                   "wall_seconds": time.time() - t0},
        "result": {"raw_result": "raw-result.json",
                   "outcome": ("both_arms_completed" if table is not None else "arm_or_comparison_failure"),
                   "ctrl_legacy_repro_pass": ctrl,
                   "certificate": {"kind": "none", "verified": False},
                   "scope": ("matched legacy/repaired s4_expr rerun of an archived toy-tier run; "
                             "observations only, no ECDLP cost claim")},
        "validity": {"valid": table is not None, "reason": error}}}
    with (run_dir / "manifest.yaml").open("x") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    return 0 if table is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
