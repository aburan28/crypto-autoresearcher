"""Admission refusal (FX-1), fail-closed C-7 (FX-2), trial plan integrity."""

import json
from pathlib import Path

import yaml

import common
import driver
import make_trial_plan

GOOD = {"host_kind": "macos", "vm_loadavg_raw": "{ 1.0 2.0 3.0 }", "load_15min": 3.0,
        "system_volume_free_gib": 50.0, "repo_volume_free_gib": 100.0, "read_at": "x"}


def test_dec_20260929_f45bf1_is_refused():
    ok, why = driver.check_decision(common.REPO_ROOT, "DEC-20260929-f45bf1")
    assert not ok and "currently_admitted" in why


def _write_dec(root: Path, dec_id: str, body: dict):
    d = root / "ledger" / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{dec_id}.yaml").write_text(yaml.safe_dump({"coordinator_decision": body}))


def test_decision_rules(tmp_root):
    root = tmp_root / "fake_repo"
    _write_dec(root, "DEC-20990101-aaaaaa", {"id": "DEC-20990101-aaaaaa", "target_ids": ["EXP-ICEX-aaccfc"],
                                             "execution_admission": {"currently_admitted": True}})
    _write_dec(root, "DEC-20990101-bbbbbb", {"id": "DEC-20990101-bbbbbb", "target_ids": ["EXP-OTHER"],
                                             "execution_admission": {"currently_admitted": True}})
    _write_dec(root, "DEC-20990101-cccccc", {"id": "DEC-20990101-cccccc", "target_ids": ["EXP-ICEX-aaccfc"],
                                             "execution_admission": {"currently_admitted": "true"}})
    _write_dec(root, "DEC-20990101-dddddd", {"id": "DEC-20990101-eeeeee", "target_ids": ["EXP-ICEX-aaccfc"],
                                             "execution_admission": {"currently_admitted": True}})
    assert driver.check_decision(root, "DEC-20990101-aaaaaa")[0]
    assert not driver.check_decision(root, "DEC-20990101-bbbbbb")[0]
    assert not driver.check_decision(root, "DEC-20990101-cccccc")[0]
    assert not driver.check_decision(root, "DEC-20990101-dddddd")[0]
    assert not driver.check_decision(root, "DEC-20990101-ffffff")[0]
    assert not driver.check_decision(root, None)[0]
    assert not driver.check_decision(root, "DEC-001")[0]


def test_c7_fail_closed():
    assert driver.check_c7(GOOD)[0]
    assert not driver.check_c7({**GOOD, "load_15min": 14.01})[0]
    assert driver.check_c7({**GOOD, "load_15min": 14.0})[0]
    assert not driver.check_c7({**GOOD, "system_volume_free_gib": 4.99})[0]
    assert not driver.check_c7({**GOOD, "repo_volume_free_gib": 19.9})[0]
    assert not driver.check_c7({**GOOD, "load_15min": None})[0]
    assert not driver.check_c7({"host_kind": "macos", "error": "sysctl failed"})[0]
    assert not driver.check_c7({**GOOD, "host_kind": "linux"})[0]


def test_main_refuses_on_current_readings_or_decision(monkeypatch, tmp_root, capsys):
    runs = tmp_root / "runs_should_stay_empty"
    # current machine readings (whatever they are) must decide first; with good
    # readings, DEC-20260929-f45bf1 must still be refused.
    monkeypatch.setattr(driver, "admission_readings", lambda root: dict(GOOD))
    code = driver.main(["--run-id", "RUN-test-refusal", "--admission-decision", "DEC-20260929-f45bf1",
                        "--runs-dir", str(runs)])
    assert code == driver.EXIT_REFUSED_DECISION
    assert not (runs / "RUN-test-refusal").exists()
    monkeypatch.setattr(driver, "admission_readings", lambda root: {**GOOD, "system_volume_free_gib": 1.0})
    code = driver.main(["--run-id", "RUN-test-refusal", "--admission-decision", "DEC-20260929-f45bf1",
                        "--runs-dir", str(runs)])
    assert code == driver.EXIT_REFUSED_ADMISSION
    code = driver.main(["--run-id", "RUN-x", "--workers", "2", "--runs-dir", str(runs)])
    assert code == driver.EXIT_REFUSED_HOST
    assert not runs.exists()


def test_smoke_dry_run_confined(tmp_root):
    assert driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-smoke-x", "--runs-dir", str(tmp_root)]) \
        == driver.EXIT_REFUSED_PLAN
    assert driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-x",
                        "--runs-dir", str(common.HERE / "smoke" / "t")]) == driver.EXIT_REFUSED_EXISTS


def test_trial_plan_is_current_and_deterministic():
    plan_path = common.HERE / "trial-plan-v2.json"
    on_disk = plan_path.read_text()
    rebuilt = json.dumps(make_trial_plan.build_plan(), indent=1, sort_keys=True) + "\n"
    assert on_disk == rebuilt
    plan = json.loads(on_disk)
    ok, bad = driver.check_plan(plan)
    assert ok, bad
    assert {(c["bits"], c["seed"]) for c in plan["cells"]} == {(b, s) for b in (16, 20) for s in (21, 22, 23)}
    assert sorted({c["kind"] for c in plan["cells"]}) == sorted(make_trial_plan.CELL_KINDS)
    tampered = json.loads(on_disk)
    tampered["protocol"]["amendment_sha256"] = "0" * 64
    assert not driver.check_plan(tampered)[0]
