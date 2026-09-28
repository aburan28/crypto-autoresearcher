"""Driver refusal paths, C-9 admission parsing, labels, trial plan. Never runs the driver."""

import json

import driver
import labels
import make_trial_plan


def _r(load, sysfree, repofree):
    return {"load_15min": load, "system_volume_free_gib": sysfree, "repo_volume_free_gib": repofree}


def test_parse_loadavg_macos_format():
    assert driver.parse_loadavg("{ 10.38 13.36 15.33 }") == 15.33
    assert driver.parse_loadavg("{ 1.00 2.00 3 }") == 3.0


def test_admission_thresholds():
    assert driver.check_admission(_r(14.0, 5.0, 20.0))[0]
    assert not driver.check_admission(_r(14.01, 50, 50))[0]
    assert not driver.check_admission(_r(1, 4.99, 50))[0]
    assert not driver.check_admission(_r(1, 50, 19.9))[0]
    ok, reasons = driver.check_admission(_r(16.6, 1, 1))
    assert not ok and len(reasons) == 3


def test_refuses_on_admission_without_creating_run_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "admission_readings", lambda root, vol=None: dict(_r(20.0, 50, 50), vm_loadavg_raw="x",
                                                                         read_at="t"))
    runs = tmp_path / "runs"
    code = driver.main(["--run-id", "RUN-test", "--admission-decision", "DEC-20260928-000000",
                        "--runs-dir", str(runs), "--repo-root", str(tmp_path)])
    assert code == driver.EXIT_REFUSED_ADMISSION and not runs.exists()


def test_refuses_without_decision(tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "admission_readings", lambda root, vol=None: dict(_r(1.0, 50, 50), vm_loadavg_raw="x",
                                                                         read_at="t"))
    runs = tmp_path / "runs"
    assert driver.main(["--run-id", "RUN-test", "--runs-dir", str(runs),
                        "--repo-root", str(tmp_path)]) == driver.EXIT_REFUSED_DECISION
    assert driver.main(["--run-id", "RUN-test", "--admission-decision", "DEC-20260928-abcdef",
                        "--runs-dir", str(runs), "--repo-root", str(tmp_path)]) == driver.EXIT_REFUSED_DECISION
    assert driver.main(["--admission-decision", "DEC-20260928-abcdef", "--runs-dir", str(runs),
                        "--repo-root", str(tmp_path)]) == driver.EXIT_REFUSED_DECISION
    assert not runs.exists()


def test_refuses_existing_run_dir_and_bad_plan(tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "admission_readings", lambda root, vol=None: dict(_r(1.0, 50, 50), vm_loadavg_raw="x",
                                                                         read_at="t"))
    dec = tmp_path / "ledger" / "decisions"
    dec.mkdir(parents=True)
    (dec / "DEC-20260928-abcdef.yaml").write_text("target: EXP-SDEG-85eefd\n")
    plan = make_trial_plan.build()
    pf = tmp_path / "plan.json"
    pf.write_text(json.dumps(plan))
    runs = tmp_path / "runs"
    (runs / "RUN-test" / "charged").mkdir(parents=True)
    common = ["--admission-decision", "DEC-20260928-abcdef", "--runs-dir", str(runs),
              "--repo-root", str(tmp_path), "--plan", str(pf)]
    assert driver.main(["--run-id", "RUN-test"] + common) == driver.EXIT_REFUSED_EXISTS
    assert driver.main(["--mode", "charged", "--run-id", "RUN-test"] + common) == driver.EXIT_REFUSED_EXISTS
    v3 = dict(plan, protocol=dict(plan["protocol"], amendment_v3_sha256="0" * 64))
    pf.write_text(json.dumps(v3))
    assert driver.main(["--run-id", "RUN-other"] + common) == driver.EXIT_REFUSED_PLAN
    bad = dict(plan, protocol=dict(plan["protocol"], amendment_sha256="0" * 64))
    pf.write_text(json.dumps(bad))
    assert driver.main(["--run-id", "RUN-other"] + common) == driver.EXIT_REFUSED_PLAN
    assert not (runs / "RUN-other").exists()


def test_label_shapes_verbatim():
    ns = labels.FROZEN_NS
    assert labels.cell_lab(ns, "random_x", 8, 1, 0) == "EXP-SDEG-85eefd/v2|random_x|L8|1|0"
    assert labels.cell_lab(ns, "planted", 16, 2, "interval_x", 3, 4) == \
        "EXP-SDEG-85eefd/v2|planted|L16|2|interval_x|3|4"
    assert labels.lab(ns, "bootstrap") == "EXP-SDEG-85eefd/v2|bootstrap"
    assert labels.SMOKE_NS.startswith("smoke")


def test_uniform_in_range():
    for i in range(200):
        assert 0 <= labels.uniform(f"smoke|t|{i}", 17) < 17


def test_trial_plan_counts():
    plan = make_trial_plan.build()
    t = plan["totals"]
    assert t["fixtures"] == 9 and t["cells"] == 36 and t["primary_cells"] == 27
    assert t["primary_queries_per_backend"] == 864 and t["control_queries_per_backend"] == 288
    assert t["rho_targets"] == 576
    ids = [q["query_id"] for c in plan["cells"] for q in c["queries"]]
    assert len(ids) == len(set(ids)) == 1152
    for c in plan["cells"]:
        assert sum(q["kind"] == "planted" for q in c["queries"]) == 16
        for q in c["queries"]:
            assert all(lb.startswith("EXP-SDEG-85eefd/v2|") for lb in q["labels"])
    assert plan["protocol_version"] == 3 and plan["protocol"]["amendment_v3_sha256"]
    assert plan["execution_hosts"]["charged"]["maximum_workers"] == 16
    assert plan["protocol"]["fixtures_sha256"] == \
        "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"
