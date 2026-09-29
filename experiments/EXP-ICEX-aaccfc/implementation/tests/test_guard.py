"""v4 FX-4 (cellrun / pipeline frozen-namespace guard) and FX-5 (smoke refuses
frozen fixtures and emits no cost fields). Every refusal happens before any
frozen label is evaluated."""

import json
import shutil

import pytest
import yaml

import cellrun
import common
import driver
import pipeline
import smoke
import synthetic

FROZEN_TASK = {"cell_id": "b16-s22:rho", "bits": 16, "seed": 22, "kind": "rho", "params": {},
               "namespace": common.FROZEN_NS}


@pytest.fixture
def no_admission_env(monkeypatch):
    for k in (cellrun.ADMISSION_ENV, cellrun.REPO_ENV, cellrun.RUN_DIR_ENV):
        monkeypatch.delenv(k, raising=False)


def test_env_names_agree():
    assert (cellrun.ADMISSION_ENV, cellrun.REPO_ENV, cellrun.RUN_DIR_ENV) == \
        (driver.ADMISSION_ENV, driver.REPO_ENV, driver.RUN_DIR_ENV)


def test_frozen_namespace_refused_without_driver(no_admission_env, tmp_root):
    with pytest.raises(cellrun.AdmissionRefused, match="admission environment absent"):
        cellrun.run_task(dict(FROZEN_TASK))
    task = tmp_root / "guard_task.json"
    out = tmp_root / "guard_out.json"
    task.write_text(json.dumps(FROZEN_TASK))
    assert cellrun.main(["--task", str(task), "--out", str(out)]) == cellrun.EXIT_REFUSED
    r = json.loads(out.read_text())
    assert r["status"] == "refused" and "result" not in r


def test_other_namespaces_refused(no_admission_env):
    for ns in ("validator|x", "EXP-ICEX-aaccfc/v3", "", "xsmoke|EXP-ICEX-aaccfc/v2"):
        ok, why = cellrun.admission_guard(ns)
        assert not ok, ns
    assert cellrun.admission_guard(common.SMOKE_NS)[0]


def _running_manifest(run_dir, dec, ns, status="running"):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(
        {"run": {"id": "RUN-x", "status": status, "inputs": {"admission_decision": dec, "namespace": ns}}}))


def test_frozen_namespace_needs_live_decision_and_running_manifest(monkeypatch, tmp_root):
    run_dir = tmp_root / "guard_run"
    dec = "DEC-20990101-aaaaaa"
    monkeypatch.setenv(cellrun.ADMISSION_ENV, dec)
    monkeypatch.setenv(cellrun.REPO_ENV, str(common.REPO_ROOT))
    monkeypatch.setenv(cellrun.RUN_DIR_ENV, str(run_dir))
    # decision re-checked: the real ledger has no such decision
    ok, why = cellrun.admission_guard(common.FROZEN_NS)
    assert not ok and "admission decision refused" in why
    monkeypatch.setattr(driver, "check_decision", lambda root, d: (True, "stub"))
    assert not cellrun.admission_guard(common.FROZEN_NS)[0]  # no manifest
    _running_manifest(run_dir, dec, common.FROZEN_NS, status="completed_valid")
    assert not cellrun.admission_guard(common.FROZEN_NS)[0]
    _running_manifest(run_dir, "DEC-20990101-bbbbbb", common.FROZEN_NS)
    assert not cellrun.admission_guard(common.FROZEN_NS)[0]
    _running_manifest(run_dir, dec, common.SMOKE_NS)
    assert not cellrun.admission_guard(common.FROZEN_NS)[0]
    _running_manifest(run_dir, dec, common.FROZEN_NS)
    ok, why = cellrun.admission_guard(common.FROZEN_NS)
    assert ok and dec in why
    shutil.rmtree(run_dir)


def test_pipeline_refuses_frozen_namespace_directly():
    fx = common.fixture(16, 22)
    assert pipeline.FROZEN_ADMITTED is False
    for call in (lambda: pipeline.run_rho_cell(fx, common.FROZEN_NS, n_targets=1),
                 lambda: pipeline.run_primary(fx, common.FROZEN_NS, n_descents=0, n_heldout=0),
                 lambda: pipeline.run_null_randfb(fx, common.FROZEN_NS),
                 lambda: pipeline.run_stage_cost(fx, common.FROZEN_NS, 6, n_heldout=0)):
        with pytest.raises(pipeline.NamespaceRefused):
            call()


def test_inline_fixture_only_in_smoke_and_never_frozen(no_admission_env):
    syn = synthetic.synthetic_fixture(0)
    with pytest.raises(cellrun.AdmissionRefused):
        cellrun.task_fixture({"fixture": syn, "namespace": "validator|x"})
    with pytest.raises(cellrun.AdmissionRefused, match="frozen"):
        cellrun.task_fixture({"fixture": dict(common.fixture(16, 21)), "namespace": common.SMOKE_NS})
    assert cellrun.task_fixture({"fixture": syn, "namespace": common.SMOKE_NS}) == syn


def test_synthetic_fixture_properties():
    from verify import VCurve
    fx = synthetic.synthetic_fixture(0)
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    assert vc.on_curve(tuple(fx["G"])) and vc.mul(fx["N"], tuple(fx["G"])) is None
    assert synthetic._is_prime(fx["N"]) and fx["N"] != fx["p"] and fx["N"] == synthetic._order(vc)
    assert synthetic._L(vc, 5) >= 3 and synthetic._L(vc, 6) >= 1 and synthetic._L(vc, 8) >= 1
    assert not common.is_frozen_fixture(fx) and synthetic.synthetic_fixture(0) == fx


def test_smoke_refuses_frozen_fixture():
    with pytest.raises(smoke.FrozenFixtureRefused):
        smoke.refuse_frozen(dict(common.fixture(16, 21)))
    with pytest.raises(smoke.FrozenFixtureRefused):
        smoke.refuse_frozen({"bits": 20, "seed": 23})
    smoke.refuse_frozen(synthetic.synthetic_fixture(0))


def test_smoke_summary_rejects_cost_fields():
    smoke.assert_no_cost_fields({"cells": {"x": {"logs_verified": True, "full_replay_audit_accepted": True}}})
    for bad in ({"complete_units": 1}, {"cells": {"x": {"stage1": {"n_attempts": 3}}}}, {"ratio": 1},
                {"a": [{"exponent": 0.5}]}, {"verdict": "x"}, {"peak_rss_bytes": 1}, {"cost": {}}):
        with pytest.raises(ValueError):
            smoke.assert_no_cost_fields(bad)


def test_smoke_summarize_refuses_frozen_receipt(tmp_root):
    run_dir = tmp_root / "guard_smoke_run"
    shutil.rmtree(run_dir, ignore_errors=True)
    (run_dir / "cells" / "c").mkdir(parents=True)
    rp = run_dir / "cells" / "c" / "result.json"
    rp.write_text(json.dumps({"task": {"cell_id": "b16-s21:rho", "bits": 16, "seed": 21}, "status": "ok",
                              "result": {"kind": "rho"}}))
    (run_dir / "raw-result.json").write_text(json.dumps({"cells": [
        {"cell_id": "b16-s21:rho", "result_path": "cells/c/result.json", "result_sha256": common.sha256_file(rp)}]}))
    with pytest.raises(smoke.FrozenFixtureRefused):
        smoke.summarize(run_dir, 0)
    shutil.rmtree(run_dir)


def test_smoke_summary_cell_ids_are_values_not_keys():
    kinds = ("primary", "null_randfb", "stage_cost_m6", "stage_cost_m8", "rho")
    smoke.assert_no_cost_fields({"cells": [{"cell": f"b13-s900:{k}", "status": "ok"} for k in kinds],
                                 "fxa_file_written": True, "scientific_output": "none: no C-5 analysis in smoke"})
