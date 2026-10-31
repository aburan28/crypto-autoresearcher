"""Fail-closed controls for the historical Semaev closure certificate checker."""

import os
import subprocess
import sys
from pathlib import Path


CHECKER = (
    Path(__file__).resolve().parents[1]
    / "analysis/semaev-m2-last-fall-degree/verify/cert_check.py"
)
LOAD_ONLY = "import runpy,sys; runpy.run_path(sys.argv[1], run_name='checker_import')"
REJECTION = "cert_check.py requires assertions; optimized Python is unsupported"


def run_checker(*flags, optimize_env=None):
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    if optimize_env is not None:
        env["PYTHONOPTIMIZE"] = optimize_env
    return subprocess.run(
        [sys.executable, *flags, "-c", LOAD_ONLY, str(CHECKER)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_normal_import_remains_available():
    result = run_checker()
    assert result.returncode == 0, result.stderr
    assert REJECTION not in result.stderr


def test_dash_o_rejected_before_certificate_validation():
    result = run_checker("-O")
    assert result.returncode != 0
    assert REJECTION in result.stderr
    assert "VALID:" not in result.stdout


def test_optimize_environment_rejected_before_certificate_validation():
    result = run_checker(optimize_env="1")
    assert result.returncode != 0
    assert REJECTION in result.stderr
    assert "VALID:" not in result.stdout
