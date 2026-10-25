#!/usr/bin/env python3
"""Operator capture for static/mocked tests only; original execution is blocked."""
import contextlib, datetime, hashlib, io, json, platform, subprocess, sys, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[5]
BATCH = Path(__file__).resolve().parent
IMPL = ROOT / "experiments/EXP-NISTSEED-6886da/implementation"
COMPAT = ROOT / "research/nist_seed_ecpp_compat_20261024"
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
argv = [sys.executable, "-m", "py_compile", *(str(IMPL / n) for n in ["cohort_runner.py", "cohort_checker.py", "test_cohort_runner.py"])]
compiled = subprocess.run(argv, capture_output=True, cwd=ROOT)
(BATCH / "executor-implementation-v4.compile.stdout").write_bytes(compiled.stdout)
(BATCH / "executor-implementation-v4.compile.stderr").write_bytes(compiled.stderr)
sys.path.insert(0, str(COMPAT))
import qemu_controls
blocked = []
def forbidden(*args, **kwargs):
    blocked.append("original legacy boundary or subprocess attempted")
    raise AssertionError("ZERO-RUN operator guard: original legacy/subprocess execution forbidden")
qemu_controls.vm = forbidden
import cohort_case
cohort_case.execute_case = forbidden
capture = io.StringIO()
with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture), mock.patch("subprocess.Popen", side_effect=forbidden), mock.patch("os.system", side_effect=forbidden):
    suite = unittest.defaultTestLoader.discover(str(IMPL), pattern="test_cohort_runner.py")
    result = unittest.TextTestRunner(stream=capture, verbosity=2).run(suite)
log = capture.getvalue()
(BATCH / "executor-implementation-v4.tests.log").write_text(log)
receipt = {"scope": "static and fully mocked implementation tests only", "started_at": started, "ended_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "python": sys.version, "platform": platform.platform(), "source_sha256": {n: hashlib.sha256((IMPL/n).read_bytes()).hexdigest() for n in ["cohort_runner.py", "cohort_checker.py", "test_cohort_runner.py", "trace_schema.json"]}, "compile_argv": argv, "compile_returncode": compiled.returncode, "unittest_driver": "unittest discovery and TextTestRunner inside operator-static-tests-v4.py with legacy/subprocess guards", "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "successful": compiled.returncode == 0 and result.wasSuccessful() and not blocked, "blocked_original_call_attempts": blocked, "named_orders_executed": 0, "legacy_program_executed": False}
(BATCH / "executor-implementation-v4.test-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
print(log[-22000:])
raise SystemExit(0 if receipt["successful"] else 1)
