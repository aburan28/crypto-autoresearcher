#!/usr/bin/env python3
"""Write experiments/EXP-FROB-30006a/trial-plan.json (schema crypto.autoresearch.trial_plan.v1).

The plan enumerates every trial of the frozen protocol with its pre-minted RUN id
(tools/allocate_id.py --next run --area FROB, --check'ed before use), the exact argv, the
independent check command, the artifacts every run must carry, and the machine-protection
watchdogs declared in run_trial.py.  source_sha256 binds every implementation file; the
specification hash binds the exact bytes of the approved contract.

    python3 experiments/EXP-FROB-30006a/implementation/make_trial_plan.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
sys.path.insert(0, str(HERE))
import run_trial  # noqa: E402

RUN_IDS = {
    "regression-gate": "RUN-FROB-5016e7",
    "pipeline-control": "RUN-FROB-520e19",
    "n41-stable-1": "RUN-FROB-1b45b0",
    "n41-stable-2": "RUN-FROB-7ffd2d",
    "n41-stable-3": "RUN-FROB-47429f",
    "n41-random-1": "RUN-FROB-0be765",
    "n41-random-2": "RUN-FROB-31d33a",
    "n41-random-3": "RUN-FROB-ba422f",
    "n43-stable-f0": "RUN-FROB-c77c53",
    "regression-gate-final-code": "RUN-FROB-360b10",
}
SUPERSEDED_RUNS = {
    "RUN-FROB-bb2096": "pipeline-control attempt aborted by an instance-generator refusal (implementation_error); "
                       "preserved unchanged; superseded by RUN-FROB-520e19",
    "RUN-FROB-d172b5": "pipeline-control attempt: 10 rows completed, then the driver raised on a row with no certified-UNSAT "
                       "candidate among 32 (n = 23, m = 3, l = 11 random V; ml > n) and lost the structured rows "
                       "(implementation_error; process logs, instances and certificates on disk are intact); superseded by RUN-FROB-520e19",
}
COMMON_ARTIFACTS = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    src = {str(p.relative_to(REPO)): sha(p) for p in sorted(HERE.iterdir()) if p.is_file()}
    src[str((HERE / "bin" / "pdp_enum").relative_to(REPO))] = sha(HERE / "bin" / "pdp_enum")
    trials = []
    for trial_id, t in run_trial.TRIALS.items():
        ids = [trial_id] + (["regression-gate-final-code"] if trial_id == "regression-gate" else [])
        for plan_id in ids:
            run_id = RUN_IDS[plan_id]
            run_rel = f"experiments/EXP-FROB-30006a/runs/{run_id}"
            entry = {
                "id": plan_id,
                "trial": trial_id,
                "run_id": run_id,
                "argv": ["python3", "experiments/EXP-FROB-30006a/implementation/run_trial.py", "--trial", trial_id,
                         "--run-id", run_id, "--run-dir", run_rel],
                "stdout_stderr": "redirected by the caller to {run_dir}/stdout.log and {run_dir}/stderr.log",
                "check_argv": ["python3", "experiments/EXP-FROB-30006a/implementation/check_run.py", run_rel],
                "artifacts": list(COMMON_ARTIFACTS),
                "memory_mb": int(run_trial.RSS_LIMIT_GB * 1024),
                "watchdog_seconds": None,
                "depends_on": [],
                "parameters": {k: v for k, v in t.items() if k != "kind"},
            }
            if t["kind"] == "cell":
                entry["artifacts"] += ["candidates/candidate-*/instance.anf", "candidates/candidate-*/instance.json",
                                       "candidates/candidate-*/certificate.json", "builds/*/config_used.json", "logs/*"]
                entry["depends_on"] = ["regression-gate", "pipeline-control"]
                entry["null_conflicts_exact"] = run_trial.null_conflicts(t["m"], t["l"]).__str__()
                entry["configurations"] = ({"gauss_elim": {"flag": "-x", "watchdog_seconds": run_trial.N43_WATCHDOG_S,
                                                           "watchdog_reason": run_trial.N43_WATCHDOG_REASON}}
                                           if t.get("decisive") else
                                           {"gauss_elim": {"flag": "-x", "watchdog_seconds": None},
                                            "default": {"flag": None, "watchdog_seconds": run_trial.DEFAULT_CFG_WATCHDOG_S,
                                                        "watchdog_reason": run_trial.DEFAULT_CFG_WATCHDOG_REASON}})
                if t.get("decisive"):
                    entry["capacity_gate"] = ("spec inputs.decisive_cell.capacity_gate: one stable-V attempt; wall-clock or memory "
                                              "exhaustion is recorded as resource_exhaustion (impediment), never scored")
            elif t["kind"] == "regression":
                entry["artifacts"] += ["shipped/*", "builds/*/config_used.json", "logs/*"]
                entry["gate"] = "C-REG: conflicts on Xn15l5-11-U within 2x of the archived reference per configuration"
                if plan_id == "regression-gate-final-code":
                    entry["depends_on"] = ["regression-gate"]
                    entry["note"] = ("re-run of the gate with the final implementation hashes listed in source_sha256 "
                                     "(the driver was edited after RUN-FROB-5016e7 for non-scientific reasons; see implementation.md)")
            else:
                entry["artifacts"] += ["instances/*/candidate-*/instance.anf", "instances/*/candidate-*/certificate.json",
                                       "builds/*/config_used.json", "logs/*"]
                entry["depends_on"] = ["regression-gate"]
                entry["watchdog_seconds_per_process"] = run_trial.SMALL_WATCHDOG_S
            trials.append(entry)
    plan = {
        "schema": "crypto.autoresearch.trial_plan.v1",
        "experiment_id": "EXP-FROB-30006a",
        "task_id": "TASK-20260920-66a30e",
        "frozen": True,
        "approved_by": "DEC-20260920-cf8ded",
        "specification": "experiments/EXP-FROB-30006a/specification.yaml",
        "specification_sha256": sha(EXP / "specification.yaml"),
        "queue": None,
        "queue_note": "GOAL-FROB-6333a9 has no batch dispatch queue; trials were run by the Executor with run_trial.py under the card's write scope",
        "source_sha256": src,
        "seeds": {"primary_targets": run_trial.PRIMARY_SEEDS, "random_V": run_trial.RANDOM_V_SEED, "n43_target": run_trial.N43_SEED},
        "machine_protection": {"rss_limit_gb": run_trial.RSS_LIMIT_GB, "one_wdsat_process_at_a_time": True,
                               "note": "declared machine protection, not a research budget (CLAUDE.md research budgets policy)"},
        "superseded_runs": SUPERSEDED_RUNS,
        "trials": trials,
    }
    out = EXP / "trial-plan.json"
    out.write_text(json.dumps(plan, indent=1) + "\n")
    print(out, len(trials), "trials")


if __name__ == "__main__":
    main()
