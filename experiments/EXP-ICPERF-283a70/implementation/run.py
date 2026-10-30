#!/usr/bin/env python3
"""Stage-0 instrument, version 2, for EXP-ICPERF-283a70 (successor of EXP-ICPERF-b2f2d0).

Sixty-four geometric draws at success probability 1/50 from xorshift32. The
recurrence is stated in specification.yaml (/experiment/sampler): left, right,
left shifts mod 2^32, step then test, trial counts with support {1, 2, ...},
each draw continues from the state where the previous one stopped, and the
seed itself is never tested.

The primary trial draws the frozen sample. Two planted negative controls draw
with a wrong shift triple and with the support-{0, 1, ...} reading; each must
fail the exact match with the preregistered integers 2943 / 289567 / 28.

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
from pathlib import Path

EXPERIMENT_ID = "EXP-ICPERF-283a70"
SCHEMA = "crypto.autoresearch.exp-icperf-283a70.stage0.v2"
SEED = 20261017
P_DEN = 50
N_TARGETS = 64
MASK = 0xFFFFFFFF
PREREGISTERED = {"sample_sum": 2943, "sum_squares": 289567, "median": 28}
CV_SQ_BAND = ((81, 100), (121, 100))
MEDIAN_RATIO_BAND = ((3, 5), (4, 5))
TRIALS = {
    "geometric-probe-sample": {"role": "primary", "shifts": (13, 17, 5), "support_min": 1},
    "ctl-neg-wrong-triple": {"role": "negative_control", "shifts": (1, 2, 14), "support_min": 1},
    "ctl-neg-support-zero": {"role": "negative_control", "shifts": (13, 17, 5), "support_min": 0},
}
CLAIM_BOUNDARY = (
    "one seeded geometric sample at p = 1/50; not a host latency "
    "measurement and not a statement about any deployed curve"
)


def step(state: int, shifts: tuple[int, int, int]) -> int:
    a, b, c = shifts
    x = state
    x ^= (x << a) & MASK
    x ^= x >> b
    x ^= (x << c) & MASK
    return x & MASK


def draw(state: int, shifts: tuple[int, int, int], support_min: int) -> tuple[int, int]:
    """One geometric count: step, then test; the starting state is never tested."""
    tests = 0
    x = state
    while True:
        x = step(x, shifts)
        tests += 1
        if x % P_DEN == 0:
            return tests - 1 + support_min, x


def sample(seed: int, shifts: tuple[int, int, int], support_min: int) -> list[int]:
    state = seed & MASK
    draws = []
    for _ in range(N_TARGETS):
        count, state = draw(state, shifts, support_min)
        draws.append(count)
    return draws


def moments(draws: list[int]) -> dict:
    ordered = sorted(draws)
    sample_sum = sum(draws)
    sum_squares = sum(value * value for value in draws)
    median = ordered[N_TARGETS // 2 - 1]
    cv_sq_num = N_TARGETS * sum_squares - sample_sum * sample_sum
    cv_sq_den = sample_sum * sample_sum
    median_ratio_num = median * N_TARGETS
    median_ratio_den = sample_sum
    (lo_n, lo_d), (hi_n, hi_d) = CV_SQ_BAND
    cv_in_band = cv_sq_num * lo_d >= cv_sq_den * lo_n and cv_sq_num * hi_d <= cv_sq_den * hi_n
    (lo_n, lo_d), (hi_n, hi_d) = MEDIAN_RATIO_BAND
    median_ratio_in_band = (median_ratio_num * lo_d >= median_ratio_den * lo_n
                            and median_ratio_num * hi_d <= median_ratio_den * hi_n)
    return {
        "sample_sum": sample_sum,
        "sum_squares": sum_squares,
        "median": median,
        "median_split": ordered[N_TARGETS // 2] != median,
        "cv_sq_num": cv_sq_num,
        "cv_sq_den": cv_sq_den,
        "median_ratio_num": median_ratio_num,
        "median_ratio_den": median_ratio_den,
        "cv_in_band": cv_in_band,
        "median_ratio_in_band": median_ratio_in_band,
        "exact_match": (sample_sum, sum_squares, median) == (
            PREREGISTERED["sample_sum"], PREREGISTERED["sum_squares"], PREREGISTERED["median"]),
    }


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
    spec = TRIALS[args.trial_id]
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    started_at = iso_now()
    started = time.perf_counter()
    draws = sample(SEED, spec["shifts"], spec["support_min"])
    observed = moments(draws)
    if spec["role"] == "primary" and observed["median_split"]:
        # Invalidation rule carried from version 1: the median is undefined.
        raise RuntimeError("the two central order statistics differ")
    elapsed = time.perf_counter() - started
    payload = {
        "schema": SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": plan["hypothesis_id"],
        "trial_id": args.trial_id,
        "run_id": trial["run_id"],
        "role": spec["role"],
        "stage": 0,
        "seed": SEED,
        "p_den": P_DEN,
        "n_targets": N_TARGETS,
        "shifts": list(spec["shifts"]),
        "support_min": spec["support_min"],
        "preregistered": dict(PREREGISTERED),
        **observed,
        "attack_claimed": False,
        "interpreter": interpreter(),
        "elapsed_seconds": elapsed,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = [
        f"# {EXPERIMENT_ID} stage 0 observations: {args.trial_id} ({spec['role']})",
        "",
        "This file records one seeded sample. It does not measure host latency.",
        "",
        f"- seed {SEED}, p = 1/{P_DEN}, n = {N_TARGETS}, shifts {spec['shifts']}, "
        f"support starts at {spec['support_min']}",
    ]
    for key in ("sample_sum", "sum_squares", "median", "median_split", "exact_match",
                "cv_in_band", "median_ratio_in_band"):
        text.append(f"- {key}: {observed[key]}")
    text += [f"- elapsed_seconds: {elapsed}", ""]
    (run_dir / "RESULTS.md").write_text("\n".join(text), encoding="utf-8")
    metrics = {key: observed[key] for key in ("sample_sum", "sum_squares", "median", "cv_in_band",
                                              "median_ratio_in_band", "exact_match")}
    finished_at = iso_now()
    document = manifest(run_dir, args.trial_plan, plan, trial, metrics, started_at, finished_at,
                        time.perf_counter() - started)
    # JSON is YAML: the bytes stay exactly as written, and a runbook assertion can read them.
    (run_dir / "manifest.yaml").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
