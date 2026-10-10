#!/usr/local/bin/python3
"""S0 gate driver for EXP-ICEX-153c34.

This driver is intentionally fail-closed.  It records the C-7 machine
protection reading before any fixture derivation or smoke computation.  A
failed reading is an infrastructure stop for every gate, never a scientific
result and never a reason to lower the guard.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP = "EXP-ICEX-153c34"
TASK = "TASK-20261001-4862b6"
OWNER = "executor-codex"
EPOCH = 1
SMOKE_NAMESPACE = "smoke|EXP-ICEX-153c34/v1"
GATES = {
    "G0-1": "v4 fixtures reproduce and panel_fixtures.py byte-reproduces independently",
    "G0-2": "f4 and f5 agree between Bareiss and subset-DP determinant reconstruction",
    "G0-3": "specialised f6 has the required signed-sum/non-sum smoke checks",
    "G0-4": "G1 agrees with O5 on 200 smoke attempts per size, including L=8",
    "G0-5": "frozen power analysis reproduces the committed rates within 3 MC standard errors",
    "G0-6": "independent counter checker exactly recomputes S,G,X,V on 20 smoke queries",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def free_gib(path: Path):
    return shutil.disk_usage(path).free / (1024 ** 3)


def machine_reading():
    load15 = float(os.getloadavg()[2])
    system = Path("/")
    repo_volume = Path("/Volumes/SSD990")
    return {
        "read_at": now(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "loadavg_15m": load15,
        "load_limit": 14.0,
        "root_free_gib": round(free_gib(system), 6),
        "root_free_min_gib": 5.0,
        "repository_volume": str(repo_volume),
        "repository_free_gib": round(free_gib(repo_volume), 6),
        "repository_free_min_gib": 20.0,
        "rss_limit_gib": 8.0,
        "workers": 1,
        "nice_required": 10,
    }


def c7_ok(reading):
    return (
        reading["loadavg_15m"] <= reading["load_limit"]
        and reading["root_free_gib"] >= reading["root_free_min_gib"]
        and reading["repository_free_gib"] >= reading["repository_free_min_gib"]
    )


def git_state():
    def run(*args):
        p = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
        return p.stdout.strip() if p.returncode == 0 else None
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "status_porcelain": (run("status", "--porcelain") or "").splitlines(),
    }


def write_reports(reading, status, command, error=None):
    report = {
        "schema": "crypto.autoresearch.exp_s0_gates.v1",
        "task_id": TASK,
        "experiment_id": EXP,
        "goal_id": "GOAL-ICEX-001",
        "owner": OWNER,
        "epoch": EPOCH,
        "smoke_namespace": SMOKE_NAMESPACE,
        "execution_scope": "S0 gates G0-1..G0-6 only; no frozen/protocol run",
        "started_at": reading["read_at"],
        "finished_at": now(),
        "command": command,
        "git": git_state(),
        "machine_protection": reading,
        "machine_protection_passed": c7_ok(reading),
        "runner_status": status,
        "infrastructure_error": error,
        "gates": [
            {
                "id": gid,
                "description": desc,
                "pass": False,
                "fail": False,
                "blocked": True,
                "classification": "infrastructure_error",
                "evidence_paths": [],
                "observation": "not started because C-7 machine protection failed at launch",
            }
            for gid, desc in GATES.items()
        ],
        "protocol_deviations": [],
        "forbidden_actions_not_taken": [
            "no panel fixture generation",
            "no G1 smoke query",
            "no charged or protocol-labelled draw",
            "no frozen fixture cost field",
            "no experiments/EXP-ICEX-153c34/runs/RUN-* directory",
            "no specification, fixture, hypothesis or ledger edit",
        ],
        "observation_only": True,
    }
    (HERE / "s0_gates_report.yaml").write_text(yaml.safe_dump(report, sort_keys=False))

    files = []
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name != "implementation_report.yaml":
            files.append({"path": str(path.relative_to(REPO)), "sha256": sha256(path)})
    impl_report = {
        "schema": "crypto.autoresearch.implementation_report.v1",
        "task_id": TASK,
        "experiment_id": EXP,
        "implementation_commit": git_state()["commit"],
        "owner": OWNER,
        "epoch": EPOCH,
        "write_scope": ["experiments/EXP-ICEX-153c34/implementation/"],
        "files": files + [{
            "path": "experiments/EXP-ICEX-153c34/implementation/implementation_report.yaml",
            "sha256": "self; final content is bound by the Coordinator snapshot receipt",
        }],
        "commands": [command],
        "results": {
            "runner_status": status,
            "s0_gates_report": "experiments/EXP-ICEX-153c34/implementation/s0_gates_report.yaml",
            "machine_protection_passed": c7_ok(reading),
        },
        "infrastructure_impediment": error,
        "protocol_complete": False,
        "requires_rerun": True,
        "scientific_interpretation": "none; executor observations only",
    }
    (HERE / "implementation_report.yaml").write_text(yaml.safe_dump(impl_report, sort_keys=False))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-gates", action="store_true", required=True)
    ap.add_argument("--owner", default=OWNER)
    ap.add_argument("--epoch", type=int, default=EPOCH)
    ap.add_argument("--launch-command", default=None,
                    help="original supervisor command to preserve in the report")
    args = ap.parse_args(argv)
    if args.owner != OWNER or args.epoch != EPOCH:
        raise SystemExit("refused: owner/epoch must be executor-codex/1")
    command = args.launch_command or " ".join([sys.executable, *sys.argv])
    reading = machine_reading()
    if not c7_ok(reading):
        error = {
            "class": "infrastructure_error",
            "reason": "C-7 machine protection failed closed at launch",
            "readings": reading,
        }
        write_reports(reading, "refused_infrastructure", command, error)
        print(json.dumps({"status": "refused_infrastructure", "machine_protection": reading}, indent=2))
        return 8
    write_reports(reading, "not_started", command, None)
    print("C-7 passed; S0 implementation body is intentionally not launched by this command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
