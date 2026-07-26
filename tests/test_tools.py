"""Tests for the harness tooling (validator + knowledge index).

These guard the validator's own correctness: it must catch real defects
(unparseable YAML, duplicate IDs, an unverified certificate on a claimed solve)
while NOT failing builds over conventions that foreign tooling never adopted.
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(REPO, "tools", "validate_ledger.py")
sys.path.insert(0, os.path.join(REPO, "tools"))
import validate_ledger as V  # noqa: E402


def test_id_patterns_accept_digits_in_area_codes():
    # R6, FB3, TTN2 are legitimate area codes in this repo.
    assert V.ID_PATTERNS["experiment"].match("EXP-R6-001")
    assert V.ID_PATTERNS["hypothesis"].match("H-FB3-001")
    assert V.ID_PATTERNS["research_question"].match("RQ-DREG-001")
    assert V.ID_PATTERNS["research_goal"].match("GOAL-ECDLP-001")
    # but the shape is still enforced
    assert not V.ID_PATTERNS["experiment"].match("EXP-lower-001")
    assert not V.ID_PATTERNS["experiment"].match("EXP-R6-1")


def test_new_record_types_are_known():
    for t in ("correction", "research_goal"):
        assert t in V.LEDGER_TYPES and t in V.ID_PATTERNS and t in V.REQUIRED
    assert V.ID_PATTERNS["correction"].match("CORR-20260722-001")


def test_unparseable_yaml_is_an_error(tmp_path):
    bad = tmp_path / "H-X-001.yaml"
    bad.write_text("hypothesis:\n  id: H-X-001\n  statement: a: b: c\n")
    ctx = V.Ctx()
    assert V.load_yaml(str(bad), ctx) is None
    assert ctx.errors and "invalid YAML" in ctx.errors[0]


def test_duplicate_id_is_an_error():
    ctx = V.Ctx()
    ctx.register("H-X-001", "/a.yaml", {})
    ctx.register("H-X-001", "/b.yaml", {})
    assert any("duplicate ID" in e for e in ctx.errors)


def test_warn_and_err_are_separate_channels():
    ctx = V.Ctx()
    ctx.warn("/a.yaml", "convention thing")
    ctx.err("/b.yaml", "real defect")
    assert len(ctx.warnings) == 1 and len(ctx.errors) == 1


def test_foreign_run_schema_warns_but_harness_schema_errors(tmp_path):
    import yaml
    def run_dir(name, body):
        d = tmp_path / name / "runs" / "RUN-X-1"
        d.mkdir(parents=True)
        (d / "manifest.yaml").write_text(yaml.safe_dump({"run": body}))
        return str(d / "manifest.yaml")

    # foreign: no certificate block -> incompleteness is a warning
    foreign = run_dir("EXP-A-001", {"id": "RUN-X-1", "experiment_id": "EXP-A-001"})
    ctx = V.Ctx(); V.check_run(foreign, ctx)
    assert ctx.warnings and not ctx.errors

    # declares this harness's contract -> same incompleteness is an error
    native = run_dir("EXP-B-001", {"id": "RUN-X-1", "experiment_id": "EXP-B-001",
                                   "result": {"certificate": {"kind": "none"}}})
    ctx = V.Ctx(); V.check_run(native, ctx)
    assert ctx.errors


def test_unverified_certificate_on_claimed_solve_is_always_an_error(tmp_path):
    import yaml
    d = tmp_path / "EXP-C-001" / "runs" / "RUN-Y-1"; d.mkdir(parents=True)
    (d / "manifest.yaml").write_text(yaml.safe_dump({"run": {
        "id": "RUN-Y-1", "experiment_id": "EXP-C-001",
        "result": {"certificate": {"kind": "discrete_log", "verified": False}}}}))
    ctx = V.Ctx(); V.check_run(str(d / "manifest.yaml"), ctx)
    assert any("certificate.verified" in e for e in ctx.errors)


def test_validator_runs_and_reports_both_channels():
    r = subprocess.run([sys.executable, VALIDATOR], capture_output=True, text=True)
    combined = r.stdout + r.stderr
    assert "warning(s)" in combined
    assert r.returncode in (0, 1)


def test_authorized_removals_are_recorded_and_parse():
    import yaml
    p = os.path.join(REPO, "ledger", "authorized-removals.yaml")
    doc = yaml.safe_load(open(p))
    entries = doc["authorized_removals"]
    assert entries, "authorization file must not be silently empty"
    for e in entries:
        # every exemption must be auditable: who, why, and where recoverable
        for field in ("path_prefix", "authorized_by", "date", "reason",
                      "recoverable_at"):
            assert e.get(field), f"authorization missing {field}"


def test_immutability_check_exempts_only_recorded_prefixes():
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import check_run_immutability as C
    allowed = C.authorized_prefixes()
    assert any(a.startswith("experiments/EXP-SEMAEV-") for a in allowed)
    # an unrelated run path is NOT exempt
    assert not any("experiments/EXP-DREG-001/runs/".startswith(a) for a in allowed)
