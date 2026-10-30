#!/usr/bin/env python3
"""Stage-0 instrument, version 2, for EXP-ICPERF-284bc4 (successor of EXP-ICPERF-e467a5).

Exact rational arithmetic on the Bernstein-Lange online-time model stated in
specification.yaml (/experiment/online_time_model):

    precomputation_steps = states * c_state / c_step          (= 525)
    bl_steps             = bl_num * r / (bl_den * A * precomputation_steps)
    bl_online_ns         = bl_steps * c_step
    probes               = r / (A * states)
    ic_online_ns         = probes * c_probe
    price ratio          = c_probe * c_state * bl_den / (bl_num * c_step^2)

The factor 10 of the BL constant 21/10 is bl_den. Because r and A cancel in
ic_online / bl_online, the r-change, A-change and probe-count comparisons are
arithmetic-consistency checks. The probe count is compared with a baby-step
giant-step lookup count found by enumeration, not by the formula. Two planted
negative controls (a perturbed probe price, and an online model whose
precomputation is not states * c_state / c_step) must give a reduced ratio
other than 925/4.

Writes observations only: raw-result.json, a complete run manifest that passes
tools/validate_ledger.py check_run as written (attack_claimed false), and
RESULTS.md. The pass or fail of the instrument is decided by the runbook's
assertions, not by this exit code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

EXPERIMENT_ID = "EXP-ICPERF-284bc4"
SCHEMA = "crypto.autoresearch.exp-icperf-284bc4.stage0.v2"
C_PROBE_NS = 370
C_STATE_NS = 2100
C_STEP_NS = 40
BL_NUM = 21
BL_DEN = 10
STATES = 10
CELLS = (
    ("r1000_a2", 1000, 2),
    ("r4000_a2", 4000, 2),
    ("r1000_a4", 1000, 4),
)
PREREGISTERED_RATIO = Fraction(925, 4)
PERTURBED_C_PROBE_NS = 371
WRONG_PRECOMPUTATION_STEPS = STATES
TRIALS = {
    "price-ratio-identity": "primary",
    "ctl-consistency-a-change": "arithmetic_consistency",
    "ctl-consistency-r-change": "arithmetic_consistency",
    "ctl-bsgs-enumeration": "arithmetic_consistency",
    "ctl-neg-perturbed-price": "negative_control",
    "ctl-neg-precomputation-model": "negative_control",
}
CLAIM_BOUNDARY = (
    "integer identity on three toy price cells; not a measurement "
    "of the n=83 Bernstein-Lange arm and not a statement about any deployed curve"
)


def exact(value: Fraction, label: str) -> int:
    """Version 1's invalidation rule: an inexact division invalidates the run."""
    if value.denominator != 1:
        raise RuntimeError(f"{label} is not an integer: {value}")
    return value.numerator


def as_json(value: Fraction) -> int | dict:
    return value.numerator if value.denominator == 1 else {"num": value.numerator,
                                                           "den": value.denominator}


def price_ratio(c_probe: int = C_PROBE_NS) -> Fraction:
    return Fraction(c_probe * C_STATE_NS * BL_DEN, BL_NUM * C_STEP_NS * C_STEP_NS)


def precomputation_steps() -> Fraction:
    return Fraction(STATES * C_STATE_NS, C_STEP_NS)


def online(r: int, classes: int, c_probe: int, precomputation: Fraction) -> dict[str, Fraction]:
    probes = Fraction(r, classes * STATES)
    bl_steps = Fraction(BL_NUM * r, BL_DEN * classes) / precomputation
    bl_online = bl_steps * C_STEP_NS
    ic_online = probes * c_probe
    return {"probes": probes, "bl_steps": bl_steps, "bl_online_ns": bl_online,
            "ic_online_ns": ic_online, "ratio": ic_online / bl_online}


def bsgs_max_lookups(order: int, table: int) -> int:
    """Worst-case table lookups of baby-step giant-step in Z/order with baby
    steps {0, ..., table-1} and giant step -table, found by trying every target."""
    baby = set(range(table))
    worst = 0
    for target in range(order):
        lookups, point = 1, target
        while point not in baby:
            point = (point - table) % order
            lookups += 1
            if lookups > order:
                raise RuntimeError("baby-step giant-step enumeration did not terminate")
        worst = max(worst, lookups)
    return worst


def primary_cell(name: str, r: int, classes: int) -> dict:
    values = online(r, classes, C_PROBE_NS, precomputation_steps())
    probes = exact(values["probes"], f"{name} probes")
    if r % classes:
        raise RuntimeError(f"{name}: r is not a multiple of A")
    bsgs = bsgs_max_lookups(r // classes, STATES)
    ratio = values["ratio"]
    return {
        "name": name, "r": r, "A": classes, "states": STATES,
        "probes": probes,
        "bsgs_probes": bsgs,
        "matches_bsgs_probes": probes == bsgs,
        "bl_steps": exact(values["bl_steps"], f"{name} BL steps"),
        "bl_online_ns": exact(values["bl_online_ns"], f"{name} BL online time"),
        "ic_online_ns": exact(values["ic_online_ns"], f"{name} IC online time"),
        "ratio_num": ratio.numerator, "ratio_den": ratio.denominator,
        "matches_price_ratio": ratio == price_ratio(),
    }


def model_cell(name: str, r: int, classes: int, c_probe: int, precomputation: Fraction) -> dict:
    values = online(r, classes, c_probe, precomputation)
    row = {"name": name, "r": r, "A": classes, "states": STATES}
    row.update({key: as_json(values[key]) for key in ("probes", "bl_steps", "bl_online_ns",
                                                       "ic_online_ns")})
    row.update({"ratio_num": values["ratio"].numerator, "ratio_den": values["ratio"].denominator})
    return row


def common_ratio(rows: list[dict]) -> Fraction | None:
    ratios = {Fraction(row["ratio_num"], row["ratio_den"]) for row in rows}
    return ratios.pop() if len(ratios) == 1 else None


def observe(trial_id: str) -> dict:
    cells = {name: (r, a) for name, r, a in CELLS}
    if trial_id == "price-ratio-identity":
        rows = [primary_cell(name, r, a) for name, r, a in CELLS]
        price = price_ratio()
        ratio = common_ratio(rows)
        return {
            "c_probe_ns": C_PROBE_NS, "precomputation_steps": exact(precomputation_steps(),
                                                                    "precomputation steps"),
            "price_ratio_num": price.numerator, "price_ratio_den": price.denominator,
            "cells": rows,
            "ratios_agree": ratio is not None and ratio == price,
            "all_match_bsgs": all(row["matches_bsgs_probes"] for row in rows),
            "matches_preregistered": price == PREREGISTERED_RATIO and ratio == PREREGISTERED_RATIO,
        }
    if trial_id in ("ctl-consistency-a-change", "ctl-consistency-r-change"):
        changed = "r1000_a4" if trial_id.endswith("a-change") else "r4000_a2"
        rows = [primary_cell(name, *cells[name]) for name in ("r1000_a2", changed)]
        ratio = common_ratio(rows)
        return {
            "c_probe_ns": C_PROBE_NS, "cells": rows,
            "same_reduced_ratio": ratio is not None,
            "matches_preregistered": ratio == PREREGISTERED_RATIO,
        }
    if trial_id == "ctl-bsgs-enumeration":
        rows = []
        for name, r, a in CELLS:
            formula = exact(Fraction(r, a * STATES), f"{name} probes")
            enumerated = bsgs_max_lookups(r // a, STATES)
            rows.append({"name": name, "r": r, "A": a, "states": STATES, "formula_probes": formula,
                         "enumerated_probes": enumerated, "match": formula == enumerated})
        return {
            "c_probe_ns": C_PROBE_NS, "cells": rows,
            "all_match": all(row["match"] for row in rows),
            "matches_preregistered": all(row["match"] for row in rows),
        }
    if trial_id == "ctl-neg-perturbed-price":
        price = price_ratio(PERTURBED_C_PROBE_NS)
        rows = [model_cell(name, r, a, PERTURBED_C_PROBE_NS, precomputation_steps())
                for name, r, a in CELLS]
        ratio = common_ratio(rows)
        return {
            "c_probe_ns": PERTURBED_C_PROBE_NS,
            "price_ratio_num": price.numerator, "price_ratio_den": price.denominator,
            "cells": rows,
            "online_ratio_num": ratio.numerator if ratio else None,
            "online_ratio_den": ratio.denominator if ratio else None,
            "matches_preregistered": price == PREREGISTERED_RATIO or ratio == PREREGISTERED_RATIO,
        }
    if trial_id == "ctl-neg-precomputation-model":
        wrong = Fraction(WRONG_PRECOMPUTATION_STEPS)
        rows = [model_cell(name, r, a, C_PROBE_NS, wrong) for name, r, a in CELLS]
        ratio = common_ratio(rows)
        return {
            "c_probe_ns": C_PROBE_NS, "precomputation_steps": WRONG_PRECOMPUTATION_STEPS,
            "cells": rows,
            "online_ratio_num": ratio.numerator if ratio else None,
            "online_ratio_den": ratio.denominator if ratio else None,
            "matches_preregistered": ratio == PREREGISTERED_RATIO,
        }
    raise SystemExit(f"trial id {trial_id!r} is not one of the preregistered trials")


def interpreter() -> dict:
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "executable": sys.executable,
    }


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_head() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                             check=False, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def manifest(run_dir: Path, plan_arg: str, plan: dict, trial: dict, metrics: dict,
             started_at: str, finished_at: str, wall_seconds: float) -> dict:
    """The full run envelope (tools/validate_ledger.py check_run), written by the driver.

    Launch facts come from the files the supervisor writes before the driver
    starts (environment.json, command.txt) and from the frozen plan, so no
    value contradicts tools/experiment_execution.py complete_manifest. Without
    them (an audit replay directory), the envelope says so and takes the commit
    from git."""
    env_file, command_file = run_dir / "environment.json", run_dir / "command.txt"
    supervisor_env = json.loads(env_file.read_text(encoding="utf-8")) if env_file.is_file() else None
    if command_file.is_file():
        command = command_file.read_text(encoding="utf-8").strip()
    else:
        command = json.dumps(["python3", *sys.argv])
    checker = [arg.replace("{run_dir}", str(run_dir)) for arg in trial["check_argv"]]
    environment = {"file": "environment.json" if supervisor_env is not None else None,
                   **interpreter(), "python": platform.python_version()}
    if supervisor_env is not None:
        for key in ("commit", "source_sha256", "specification_sha256", "runtime_lock",
                    "runtime_lock_sha256"):
            if key in supervisor_env:
                environment[key] = supervisor_env[key]
    else:
        environment["note"] = "no supervisor environment.json in this directory (audit replay)"
    commit = (supervisor_env or {}).get("commit") or git_head()
    body = {
        "id": trial["run_id"],
        "experiment_id": plan["experiment_id"],
        "hypothesis_id": plan["hypothesis_id"],
        "task_id": plan["task_id"],
        "trial_id": trial["id"],
        "approved_by": plan["approved_by"],
        "status": "completed",
        "status_note": "Written by run.py when the driver finished. Completed is not a validity ruling.",
        "attack_claimed": False,
        "code": {
            "commit": commit,
            "commit_meaning": ("launch authority commit (environment.json)" if supervisor_env is not None
                               else "git HEAD of the replay checkout"),
            "command_file": "command.txt",
            "command": command,
            "check_command": json.dumps(checker),
        },
        "environment": environment,
        "inputs": {
            "trial_plan": plan_arg,
            "plan_sha256": hashlib.sha256(Path(plan_arg).read_bytes()).hexdigest(),
            "trial_id": trial["id"],
        },
        "timing": {
            "started_at": started_at,
            "finished_at": finished_at,
            "wall_seconds": wall_seconds,
            "source": "driver clock (run.py)",
        },
        "metrics": metrics,
        "result": {
            "raw_result": "raw-result.json",
            "metrics": dict(metrics),
            "certificate": {
                "kind": "none",
                "verified": None,
                "note": "attack_claimed false in manifest.yaml and raw-result.json; "
                        "no discrete_log, decomposition or key_recovery claim",
            },
            "executor_receipt": "execution-receipt.json",
        },
        "artifacts": {
            "stdout": "stdout.log",
            "stderr": "stderr.log",
            "check_stdout": "check.stdout.log",
            "check_stderr": "check.stderr.log",
        },
    }
    return {"run": body}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage != 0:
        raise SystemExit("this runner implements stage 0 only")
    if args.trial_id not in TRIALS:
        raise SystemExit(f"trial id {args.trial_id!r} is not one of the preregistered trials")
    plan = json.loads(Path(args.trial_plan).read_text(encoding="utf-8"))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        raise SystemExit("the trial plan is not this experiment's")
    trial = next((t for t in plan.get("trials", []) if t.get("id") == args.trial_id), None)
    if trial is None:
        raise SystemExit("the trial id is not in the trial plan")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    started_at = iso_now()
    started = time.perf_counter()
    observed = observe(args.trial_id)
    elapsed = time.perf_counter() - started
    payload = {
        "schema": SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": plan["hypothesis_id"],
        "trial_id": args.trial_id,
        "run_id": trial["run_id"],
        "role": TRIALS[args.trial_id],
        "stage": 0,
        "c_state_ns": C_STATE_NS,
        "c_step_ns": C_STEP_NS,
        "bl_num": BL_NUM,
        "bl_den": BL_DEN,
        "states": STATES,
        "preregistered_ratio": {"num": PREREGISTERED_RATIO.numerator,
                                "den": PREREGISTERED_RATIO.denominator},
        **observed,
        "attack_claimed": False,
        "interpreter": interpreter(),
        "elapsed_seconds": elapsed,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        f"# {EXPERIMENT_ID} stage 0 observations: {args.trial_id} ({TRIALS[args.trial_id]})",
        "",
        "This file records the integer identity. It does not confirm the n=83 measurement.",
        "",
    ]
    for key in ("price_ratio_num", "price_ratio_den", "ratios_agree", "all_match_bsgs",
                "same_reduced_ratio", "all_match", "online_ratio_num", "online_ratio_den",
                "matches_preregistered"):
        if key in observed:
            lines.append(f"- {key}: {observed[key]}")
    for row in observed["cells"]:
        lines.append(f"- {row['name']}: " + ", ".join(
            f"{key} {row[key]}" for key in row if key not in ("name", "r", "A", "states")))
    lines += [f"- elapsed_seconds: {elapsed}", ""]
    (run_dir / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    metrics = {key: observed[key] for key in ("price_ratio_num", "price_ratio_den", "ratios_agree",
                                              "all_match_bsgs", "matches_preregistered")
               if key in observed}
    finished_at = iso_now()
    document = manifest(run_dir, args.trial_plan, plan, trial, metrics, started_at, finished_at,
                        time.perf_counter() - started)
    # JSON is YAML: the bytes stay exactly as written, and a runbook assertion can read them.
    (run_dir / "manifest.yaml").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
