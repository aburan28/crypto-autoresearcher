import json
from pathlib import Path

import pytest
import yaml

import driver
import hostinfo

REPO = driver.REPO_ROOT_DEFAULT
PASSING = {"load_15min": 1.0, "system_volume_free_gib": 50.0, "repo_volume_free_gib": 500.0,
           "errors": []}


def test_ee5b8a_does_not_admit():
    ok, why = driver.check_decision(REPO, "DEC-20260929-ee5b8a")
    assert not ok
    assert "currently_admitted" in why


@pytest.mark.parametrize("dec", [None, "", "DEC-1", "DEC-20260101-000000", "../x"])
def test_bad_or_missing_decisions_refused(dec):
    assert not driver.check_decision(REPO, dec)[0]


def _write_dec(root: Path, dec_id, **over):
    d = {"id": dec_id, "decision": "approve", "target_ids": ["EXP-RELN-c5a377"],
         "execution_admission": {"currently_admitted": True}}
    d.update(over)
    p = root / "ledger" / "decisions"
    p.mkdir(parents=True, exist_ok=True)
    (p / f"{dec_id}.yaml").write_text(yaml.safe_dump({"coordinator_decision": d}))


def test_synthetic_admitting_decision(tmp_path):
    _write_dec(tmp_path, "DEC-20990101-aaaaaa")
    assert driver.check_decision(tmp_path, "DEC-20990101-aaaaaa")[0]
    _write_dec(tmp_path, "DEC-20990101-bbbbbb", execution_admission={"currently_admitted": "true"})
    assert not driver.check_decision(tmp_path, "DEC-20990101-bbbbbb")[0]
    _write_dec(tmp_path, "DEC-20990101-cccccc", target_ids=["EXP-SDEG-85eefd"])
    assert not driver.check_decision(tmp_path, "DEC-20990101-cccccc")[0]
    _write_dec(tmp_path, "DEC-20990101-dddddd", id="DEC-20990101-eeeeee")
    assert not driver.check_decision(tmp_path, "DEC-20990101-dddddd")[0]


def test_c7_thresholds_and_fail_closed():
    assert hostinfo.check(PASSING)[0]
    assert not hostinfo.check({**PASSING, "load_15min": 14.01})[0]
    assert hostinfo.check({**PASSING, "load_15min": 14.0})[0]
    assert not hostinfo.check({**PASSING, "system_volume_free_gib": 4.99})[0]
    assert not hostinfo.check({**PASSING, "repo_volume_free_gib": 19.99})[0]
    assert not hostinfo.check({**PASSING, "load_15min": None})[0]
    assert not hostinfo.check({**PASSING, "errors": ["x"]})[0]


def test_readings_fail_closed_on_unreadable_sources():
    def boom(*a):
        raise OSError("unreadable")
    r = hostinfo.readings(REPO, load_reader=boom, free_reader=boom)
    ok, reasons = hostinfo.check(r)
    assert not ok and r["load_15min"] is None and len(r["errors"]) == 3
    r = hostinfo.readings(REPO, load_reader=lambda: "garbage", free_reader=lambda p: 100.0)
    assert not hostinfo.check(r)[0]
    assert hostinfo.parse_loadavg("{ 1.50 2.25 3.75 }") == 3.75
    assert hostinfo.parse_loadavg("0.1 0.2 0.3 1/200 1") == 0.3


def test_main_refuses_on_c7(monkeypatch, tmp_path):
    monkeypatch.setattr(hostinfo, "readings", lambda root: {**PASSING, "load_15min": 40.0})
    code = driver.main(["--run-id", "RUN-test", "--admission-decision", "DEC-20260929-ee5b8a",
                        "--runs-dir", str(tmp_path)])
    assert code == driver.EXIT_REFUSED_ADMISSION
    assert not any(tmp_path.iterdir())


def test_main_refuses_ee5b8a_even_when_c7_passes(monkeypatch, tmp_path):
    monkeypatch.setattr(hostinfo, "readings", lambda root: dict(PASSING))
    code = driver.main(["--run-id", "RUN-test", "--admission-decision", "DEC-20260929-ee5b8a",
                        "--runs-dir", str(tmp_path)])
    assert code == driver.EXIT_REFUSED_DECISION
    assert not any(tmp_path.iterdir())
    code = driver.main(["--run-id", "RUN-test", "--runs-dir", str(tmp_path)])
    assert code == driver.EXIT_REFUSED_DECISION


def test_plan_hash_check():
    plan = json.loads((driver.HERE / "trial-plan-v2.json").read_text())
    ok, bad = driver.check_plan(plan)
    assert ok, bad
    plan["protocol"]["amendment_sha256"] = "0" * 64
    assert not driver.check_plan(plan)[0]


def test_trial_plan_covers_both_budgets_at_all_fixtures():
    plan = json.loads((driver.HERE / "trial-plan-v2.json").read_text())
    cells = {(c["fixture_id"], c["budget"]) for c in plan["cells"]}
    fids = {f"b{b}-s{s}" for b in (16, 20, 24) for s in (11, 12, 13)}
    assert cells == {(f, bu) for f in fids for bu in ("A1", "A2")}
    for c in plan["cells"]:
        assert len(c["controls"]["rewire_labels"]) == 32 and len(c["controls"]["er_labels"]) == 32
        assert all("smoke" not in s for s in c["controls"]["rewire_labels"])
    for f in plan["fixtures"]:
        assert len(f["rho_target_labels"]) == 64 and f["A1"] < f["A2"]
    assert plan["namespace"] == "EXP-RELN-c5a377/v2"


def test_smoke_dry_run_confined(tmp_path):
    code = driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-x", "--runs-dir", str(tmp_path)])
    assert code == driver.EXIT_REFUSED_PLAN
    code = driver.main(["--smoke-dry-run", "--run-id", "RUN-x",
                        "--runs-dir", str(driver.HERE / "smoke" / "never")])
    assert code == driver.EXIT_REFUSED_EXISTS
