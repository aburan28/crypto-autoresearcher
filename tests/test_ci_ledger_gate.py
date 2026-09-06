"""The differential CI gate must never turn validator failure into success."""
from __future__ import annotations

import pytest

from tools.ci_ledger_gate import InvalidReport, compare_reports, main, parse_report

CLEAN = "OK: validated 12 records, no new violations\n"


def failed(*errors):
    return (f"FAIL: {len(errors)} new validation error(s):\n\n"
            + "".join(f"  - {error}\n" for error in errors))


@pytest.mark.parametrize("head,head_status,base,base_status,expected", [
    (CLEAN, 0, CLEAN, 0, []),
    (failed("old"), 1, failed("old"), 1, []),
    (CLEAN, 0, failed("old"), 1, []),
    (failed("old", "new"), 1, failed("old"), 1, ["new"]),
    (failed("different"), 1, failed("old"), 1, ["different"]),
    (failed("new"), 1, CLEAN, 0, ["new"]),
])
def test_compares_identities_not_just_counts(head, head_status, base, base_status, expected):
    assert compare_reports(head, head_status, base, base_status) == expected


@pytest.mark.parametrize("output,status", [
    ("", 0),
    ("", 1),
    (CLEAN, 1),
    (CLEAN, 2),
    (failed("one"), 0),
    (failed("one"), -9),
    ("FAIL: cannot load schema supersession registry: corrupt\n", 1),
    ("FAIL: 2 new validation error(s):\n  - only one\n", 1),
    ("FAIL: 0 new validation error(s):\n", 1),
    (failed(""), 1),
    (CLEAN + CLEAN, 0),
    (failed("one") + CLEAN, 1),
    (CLEAN + "Traceback (most recent call last):\nboom\n", 0),
    (failed("one") + "Traceback (most recent call last):\nboom\n", 1),
])
def test_rejects_crashes_and_incomplete_reports(output, status):
    with pytest.raises(InvalidReport):
        parse_report(output, status, label="fixture")


def test_crashed_base_is_not_an_exemption_for_head():
    with pytest.raises(InvalidReport, match="base"):
        compare_reports(CLEAN, 0, "", 1)


def test_notes_and_multiline_yaml_diagnostics_are_supported():
    report = failed("record.yaml: invalid YAML") + "    while parsing a collection\n"
    report += "note: 12 grandfathered legacy error(s) suppressed\n"
    assert parse_report(report, 1, label="head") == {"record.yaml: invalid YAML"}


def test_cli_missing_report_is_an_operational_failure(tmp_path):
    absent = str(tmp_path / "missing.log")
    assert main(["--head-log", absent, "--head-status", "0",
                 "--base-log", absent, "--base-status", "0"]) == 2


@pytest.mark.parametrize("head,status,expected", [(CLEAN, 0, 0), (failed("new"), 1, 1)])
def test_cli_exit_code(tmp_path, head, status, expected):
    head_log, base_log = tmp_path / "head.log", tmp_path / "base.log"
    head_log.write_text(head, encoding="utf-8")
    base_log.write_text(CLEAN, encoding="utf-8")
    assert main(["--head-log", str(head_log), "--head-status", str(status),
                 "--base-log", str(base_log), "--base-status", "0"]) == expected
