"""Required checks fail for detector errors and incorrectly skipped work."""
from pathlib import Path
import os
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


def run_step(script, values):
    return subprocess.run(["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", script],
                          env={**os.environ, **values}, capture_output=True, text=True).returncode


def default_results():
    values = {"SCOPE_RESULT": "success", "HYGIENE_RESULT": "success"}
    for part in ("LEDGER", "STATIC", "TESTS", "RUNTIME"):
        values[part + "_REQUIRED"] = "true"
        values[part + "_RESULT"] = "success"
    return values


def aggregate():
    return workflow("validate.yml")["jobs"]["ledger-and-harness"]["steps"][0]["run"]


def test_documentation_only_keeps_required_check_green_after_every_scope_guard():
    values = default_results()
    for part in ("LEDGER", "STATIC", "TESTS", "RUNTIME"):
        values[part + "_REQUIRED"] = "false"
        values[part + "_RESULT"] = "success" if part in {"TESTS", "RUNTIME"} else "skipped"
    assert run_step(aggregate(), values) == 0


@pytest.mark.parametrize("upstream", ["SCOPE_RESULT", "HYGIENE_RESULT"])
@pytest.mark.parametrize("result", ["failure", "cancelled", "skipped", ""])
def test_failed_detector_or_hygiene_never_passes_the_required_gate(upstream, result):
    values = default_results()
    values[upstream] = result
    assert run_step(aggregate(), values) != 0


@pytest.mark.parametrize("part", ["LEDGER", "STATIC", "TESTS", "RUNTIME"])
def test_every_part_rejects_failure_cancelled_missing_or_unexpected_skips(part):
    for required in ("true", "false", ""):
        for result in ("success", "failure", "cancelled", "skipped"):
            values = default_results()
            values[part + "_REQUIRED"] = required
            values[part + "_RESULT"] = result
            expected = "success" if required == "true" or part in {"TESTS", "RUNTIME"} else "skipped"
            should_pass = required in {"true", "false"} and result == expected
            assert (run_step(aggregate(), values) == 0) == should_pass, (part, required, result)


@pytest.mark.parametrize("file,job,flag", [
    ("validate.yml", "runtime-regressions", "RUN_RUNTIME"),
    ("validate.yml", "harness-tests", "RUN_TESTS"),
    ("lean-verification.yml", "kernel-controls", "RUN_KERNEL"),
    ("lean-verification.yml", "formal-workspace", "BUILD_WORKSPACE"),
])
def test_each_unchanged_required_context_still_requires_a_valid_scope_decision(file, job, flag):
    definition = workflow(file)["jobs"][job]
    guard = definition["steps"][0]["run"]
    for status in ("success", "failure", "cancelled", "skipped", ""):
        for enabled in ("true", "false", ""):
            should_pass = status == "success" and enabled in {"true", "false"}
            assert (run_step(guard, {"SCOPE_RESULT": status, flag: enabled}) == 0) == should_pass


def test_progress_fidelity_never_succeeds_on_a_missing_scope_output():
    job = workflow("progress-fidelity.yml")["jobs"]["progress-fidelity"]
    guard = next(step["run"] for step in job["steps"] if step.get("name") == "Require a complete CI scope decision")
    for status in ("success", "failure", "cancelled", "skipped", ""):
        for enabled in ("true", "false", ""):
            should_pass = status == "success" and enabled in {"true", "false"}
            assert (run_step(guard, {"SCOPE_RESULT": status, "RUN_PROGRESS": enabled}) == 0) == should_pass


@pytest.mark.parametrize("job,flag", [("ledger", "RUN_LEDGER"), ("static-checks", "RUN_STATIC")])
def test_single_job_contexts_fail_on_detector_failure_or_missing_output(job, flag):
    definition = workflow("validate.yml")["jobs"][job]
    guard = definition["steps"][0]["run"]
    for status in ("success", "failure", "cancelled", "skipped", ""):
        for enabled in ("true", "false", ""):
            should_pass = status == "success" and enabled == "true"
            assert (run_step(guard, {"SCOPE_RESULT": status, flag: enabled}) == 0) == should_pass
