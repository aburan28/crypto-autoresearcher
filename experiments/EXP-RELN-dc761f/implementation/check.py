#!/usr/bin/env python3
"""Non-protocol implementation checks for EXP-RELN-dc761f.

This checker is intentionally safe before admission: it validates the frozen
F-2/P-5 tables, plan structure, fail-closed machine checks with injected test
readings, and the driver's absent-admission refusal.  It never evaluates a
protocol label and never creates an experiment run directory.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import run_reln  # noqa: E402


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_frozen_inputs(plan: dict) -> None:
    expect(plan["experiment_id"] == "EXP-RELN-dc761f", "experiment id")
    expect(plan["execution_state"] == "ready", "plan readiness")
    expect(plan["execution_authorized"] is False, "plan must not authorize execution")
    expect(plan["protocol_label_draws_performed"] is False, "plan draw marker")
    expect(plan["frozen_p5_columns"] == list(run_reln.P5_COLUMNS), "P-5 columns")
    expect(plan["frozen_p5_values"] == run_reln.expected_frozen_rows(), "P-5 values")
    expect(len(plan["fixtures"]) == 12, "fixture count")
    expect(len(plan["cells"]) == 48, "cell count")
    for fixture in plan["fixtures"]:
        p5 = fixture["p5"]
        expect(fixture["budgets"]["1/4"] == p5["A_1/4"], f"{fixture['id']} A_1/4")
        expect(fixture["budgets"]["1/2"] == p5["A_1/2"], f"{fixture['id']} A_1/2")
        expect(fixture["budgets"]["1"] == p5["A_1"], f"{fixture['id']} A_1")
        expect(fixture["budgets"]["2"] == p5["A_2"], f"{fixture['id']} A_2")


def check_machine_fail_closed() -> None:
    good = {"errors": [], "load_15min": 0.0, "system_volume_free_gib": 6.0,
            "repository_volume_free_gib": 21.0, "workers": 1, "nice_required": 10,
            "rss_watchdog_available": True, "tmpdir_writable": True}
    ok, reasons = run_reln.check_machine(good)
    expect(ok and not reasons, "passing machine readings")
    for field, value in (("load_15min", None), ("system_volume_free_gib", 4.99),
                         ("repository_volume_free_gib", 19.99), ("rss_watchdog_available", False),
                         ("tmpdir_writable", False), ("workers", 2), ("nice_required", 0)):
        bad = dict(good)
        bad[field] = value
        ok, reasons = run_reln.check_machine(bad)
        expect(not ok and reasons, f"fail-closed machine field {field}")


def check_no_protocol_draws() -> None:
    # The plan and readiness path may construct label templates, but must not
    # invoke the protocol sampler.  Monkeypatching catches accidental future
    # calls without changing any repository state.
    old = run_reln.protocol_uniform
    calls = []
    run_reln.protocol_uniform = lambda label, n: calls.append((label, n)) or 0
    try:
        plan = run_reln.build_plan(ROOT)
        result = run_reln.readiness(ROOT, HERE / ".." / "trial-plan-v1.json")
    finally:
        run_reln.protocol_uniform = old
    expect(plan["protocol_label_draws_performed"] is False, "plan draw marker")
    expect(result["execution_state"] == "ready", "readiness result")
    expect(not calls, f"protocol sampler called during non-protocol checks: {calls}")


def check_absent_admission_refuses() -> None:
    with tempfile.TemporaryDirectory(prefix="reln-check-") as td:
        env = dict(os.environ)
        env["TMPDIR"] = td
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        # --readiness is the only non-admission driver mode.  A requested run
        # without a decision must refuse before any run directory is made.
        proc = subprocess.run([sys.executable, "-B", str(HERE / "run_reln.py"),
                               "--plan", str(HERE.parent / "trial-plan-v1.json"),
                               "--repo-root", str(ROOT), "--run-id", "RUN-no-admission"],
                              cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
        expect(proc.returncode != 0, "absent admission must refuse")
        expect("REFUSED:" in proc.stderr, "refusal should be explicit")
        expect(not (ROOT / "experiments/EXP-RELN-dc761f/runs/RUN-no-admission").exists(),
               "absent admission created a run directory")


def main() -> int:
    plan_path = HERE.parent / "trial-plan-v1.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors = run_reln.validate_plan(plan, ROOT)
    expect(not errors, "plan validation: " + "; ".join(errors))
    check_frozen_inputs(plan)
    check_machine_fail_closed()
    check_no_protocol_draws()
    check_absent_admission_refuses()
    print(json.dumps({"status": "pass", "protocol_label_draws_performed": False,
                      "scientific_execution": False, "run_directories_created": []}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
