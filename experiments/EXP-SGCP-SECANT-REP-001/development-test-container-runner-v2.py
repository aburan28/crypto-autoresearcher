"""Hermetic one-shot runner for the five SGCP secant public tests."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
import unittest


EXPECTED_SOURCE_SHA256 = (
    "8b8781d688188afa41e87f33e15a306fc5a9f5326b8e93316247263ee8f933bd"
)
EXPECTED_TEST_SHA256 = (
    "2b0e34524f22cf5d2dd70c3eff857b186c10c9d8882bb2893999febc1352417a"
)
EXPECTED_TEST_IDS = (
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore."
    "test_chart_scalar_congruence_and_least_slope_selection",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore."
    "test_chart_witnesses_fibers_representatives_diagnostics_and_ops",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore."
    "test_every_reachable_domain_error_and_charged_prefix",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore."
    "test_first_error_precedence",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore."
    "test_public_results_and_inputs_are_immutable",
)
EXPECTED_SYS_PATH = (
    "/usr/local/lib/python311.zip",
    "/usr/local/lib/python3.11",
    "/usr/local/lib/python3.11/lib-dynload",
)


class CanonicalResult(unittest.TestResult):
    """Record one terminal event for every test without formatting ambiguity."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[dict[str, str]] = []

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self.events.append({"id": test.id(), "outcome": "ok"})

    def addFailure(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:
        super().addFailure(test, err)
        self.events.append({"id": test.id(), "outcome": "failure"})

    def addError(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:
        super().addError(test, err)
        self.events.append({"id": test.id(), "outcome": "error"})

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self.events.append({"id": test.id(), "outcome": "skipped"})

    def addExpectedFailure(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:
        super().addExpectedFailure(test, err)
        self.events.append({"id": test.id(), "outcome": "expected_failure"})

    def addUnexpectedSuccess(self, test: unittest.case.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self.events.append({"id": test.id(), "outcome": "unexpected_success"})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")), flush=True)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"no import spec for {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _flatten(suite: unittest.TestSuite) -> list[unittest.case.TestCase]:
    tests: list[unittest.case.TestCase] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            tests.extend(_flatten(item))
        else:
            tests.append(item)
    return tests


def _preflight(source_path: Path, test_path: Path) -> None:
    if (
        sys.flags.isolated != 1
        or sys.flags.no_site != 1
        or not sys.flags.safe_path
        or sys.flags.dont_write_bytecode != 1
    ):
        raise RuntimeError("required Python isolation flags are not active")
    if tuple(sys.path) != EXPECTED_SYS_PATH:
        raise RuntimeError(f"unexpected sys.path: {sys.path!r}")
    if os.getuid() != 65534 or os.getgid() != 65534:
        raise RuntimeError("container is not running as uid/gid 65534")
    if Path("/sys/fs/cgroup/memory.max").read_text(encoding="ascii").strip() != (
        "1073741824"
    ):
        raise RuntimeError("memory cgroup is not exactly 1 GiB")
    if Path("/sys/fs/cgroup/pids.max").read_text(encoding="ascii").strip() != "64":
        raise RuntimeError("pids cgroup is not exactly 64")
    for path, expected_hash in (
        (source_path, EXPECTED_SOURCE_SHA256),
        (test_path, EXPECTED_TEST_SHA256),
    ):
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"input is not a regular non-symlink file: {path}")
        if _sha256(path) != expected_hash:
            raise RuntimeError(f"input digest mismatch: {path}")


def main() -> int:
    if len(sys.argv) != 3:
        _emit(
            {
                "classification": "PREFLIGHT_FAILURE",
                "detail": "expected source and test argv",
            }
        )
        return 70

    source_path = Path(sys.argv[1])
    test_path = Path(sys.argv[2])

    try:
        _preflight(source_path, test_path)
    except BaseException as exc:
        _emit(
            {
                "classification": "PREFLIGHT_FAILURE",
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
        return 70

    try:
        core_module = _load_module("sgcp_secant_math_core", source_path)
        if Path(core_module.__file__).resolve() != source_path.resolve():
            raise RuntimeError("protected core import origin mismatch")
        if _sha256(Path(core_module.__file__)) != EXPECTED_SOURCE_SHA256:
            raise RuntimeError("protected core changed during import")

        test_module = _load_module("test_sgcp_secant_math_core", test_path)
        suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
        loaded_ids = tuple(test.id() for test in _flatten(suite))
        if loaded_ids != EXPECTED_TEST_IDS:
            raise RuntimeError(f"unexpected test IDs: {loaded_ids!r}")
    except BaseException as exc:
        traceback.print_exc(file=sys.stderr)
        _emit(
            {
                "classification": "INFRASTRUCTURE_FAILURE",
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
        return 71

    result = CanonicalResult()
    try:
        suite.run(result)
    except BaseException as exc:
        traceback.print_exc(file=sys.stderr)
        _emit(
            {
                "classification": "INFRASTRUCTURE_FAILURE",
                "detail": f"{type(exc).__name__}: {exc}",
                "events": result.events,
                "tests_started": result.testsRun,
            }
        )
        return 71

    payload = {
        "classification": (
            "VALID_DEVELOPMENT_TEST" if result.wasSuccessful() else "TEST_FAILURE"
        ),
        "errors": len(result.errors),
        "events": result.events,
        "expected_failures": len(result.expectedFailures),
        "failures": len(result.failures),
        "skipped": len(result.skipped),
        "tests_started": result.testsRun,
        "unexpected_successes": len(result.unexpectedSuccesses),
    }
    _emit(payload)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
