#!/usr/bin/env python3
"""Record the original checker-format failure and passing addenda check."""

import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parent.parent
tool = repo / "tools/check_review_independence.py"
plan = here / "review-plan.yaml"
j1 = here / "reports/TASK-20261026-538444"
j2 = here / "reports/TASK-20261026-7ab9cb"
base = ["python3", str(tool), "--plan", str(plan), "--reports"]
checks = {}
for label, paths, expected_exit in (
    ("sealed_original_format", [j1 / "review_attestation.yaml",
                                j2 / "review_attestation.yaml"], 2),
    ("checker_addenda", [j1, j2], 0),
):
    command = base + [str(p) for p in paths]
    run = subprocess.run(command, cwd=repo, capture_output=True, text=True)
    checks[label] = {"command": command, "exit_code": run.returncode,
                     "stdout": run.stdout, "stderr": run.stderr}
    if label == "sealed_original_format":
        assert "no review_attestation blocks found" in run.stdout + run.stderr
        assert run.returncode != 0
    else:
        assert run.returncode == expected_exit
        assert "PASS: 2 report(s)" in run.stdout
(here / "independence-check.json").write_text(json.dumps(checks, indent=2) + "\n")
print(checks["checker_addenda"]["stdout"].strip())
