"""Fail-closed comparison of complete ledger-validator reports.

Inherited schema errors are not a PR regression. A crashed validator, a
truncated report, or an unrecognised output format is not a clean report.
This gate compares error identities only after both executions have proved
that they produced the validator's normal, complete reporting format.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


class InvalidReport(ValueError):
    """The process did not produce a complete, supported validation report."""


SUCCESS = re.compile(r"^OK: validated \d+ records, no new violations$", re.MULTILINE)
FAILURE = re.compile(
    r"^FAIL: (\d+) new validation error\(s\):$", re.MULTILINE)


def parse_report(output: str, status: int, *, label: str) -> frozenset[str]:
    errors = [line[4:] for line in output.splitlines() if line.startswith("  - ")]
    successes = SUCCESS.findall(output)
    failures = FAILURE.findall(output)
    failure_lines = [line for line in output.splitlines() if line.startswith("FAIL:")]
    if "Traceback (most recent call last):" in output:
        raise InvalidReport(f"{label}: validator raised an exception")
    if status == 0:
        if len(successes) != 1 or failure_lines or errors:
            raise InvalidReport(f"{label}: exit 0 without one clean validation report")
        return frozenset()
    if status != 1:
        raise InvalidReport(f"{label}: unexpected validator exit status {status}")
    if successes or len(failures) != 1 or len(failure_lines) != 1:
        raise InvalidReport(f"{label}: failed without one normal error summary")
    count = int(failures[0])
    if count < 1 or len(errors) != count or any(not error.strip() for error in errors):
        raise InvalidReport(
            f"{label}: incomplete report (declared {count}, received {len(errors)} errors)")
    return frozenset(errors)


def compare_reports(head: str, head_status: int,
                    base: str, base_status: int) -> list[str]:
    head_errors = parse_report(head, head_status, label="head")
    base_errors = parse_report(base, base_status, label="base")
    return sorted(head_errors - base_errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for side in ("head", "base"):
        parser.add_argument(f"--{side}-log", type=Path, required=True)
        parser.add_argument(f"--{side}-status", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        new = compare_reports(
            args.head_log.read_text(encoding="utf-8"), args.head_status,
            args.base_log.read_text(encoding="utf-8"), args.base_status)
    except (OSError, UnicodeError, InvalidReport) as exc:
        print(f"FAIL: ledger CI comparison could not establish integrity: {exc}",
              file=sys.stderr)
        return 2
    if new:
        print(f"FAIL: {len(new)} validation error(s) introduced by this PR:",
              file=sys.stderr)
        for error in new:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("PASS: both validators produced complete reports; no new errors vs base")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
