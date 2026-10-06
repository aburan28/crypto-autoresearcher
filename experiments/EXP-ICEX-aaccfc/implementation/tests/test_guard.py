"""v4 FX-4 (cellrun / pipeline frozen-namespace guard) and FX-5 (smoke refuses
frozen fixtures and emits no cost fields). Every refusal happens before any
frozen label is evaluated."""

import json
import os
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


ENV_KEYS = ("ADMISSION_ENV", "REPO_ENV", "RUN_DIR_ENV", "RUN_TOKEN_ENV", "DRIVER_PID_ENV")


@pytest.fixture
def no_admission_env(monkeypatch):
    for k in ENV_KEYS:
        monkeypatch.delenv(getattr(cellrun, k), raising=False)


def test_env_names_agree():
    assert [getattr(cellrun, k) for k in ENV_KEYS] == [getattr(driver, k) for k in ENV_KEYS]
    assert cellrun.RUNS_ROOT == driver.RUNS_ROOT


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


DEC = "DEC-20990101-aaaaaa"
TOKEN = "ab" * 32
DPID = 424242


def _manifest(run_dir, head, **over):
    run = {"id": run_dir.name, "status": "running", "code": {"commit": head},
           "inputs": {"admission_decision": DEC, "namespace": common.FROZEN_NS,
                      "run_token_sha256": driver.token_sha256(TOKEN), "driver_pid": DPID}}
    inputs = over.pop("inputs", {})
    run.update(over)
    run["inputs"].update(inputs)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump({"run": run}))


def _guard_env(monkeypatch, tmp_root):
    import subprocess
    repo = tmp_root / "guard_repo"
    shutil.rmtree(repo, ignore_errors=True)
    runs = repo / "runs"
    runs.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", "-c",
                    "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "x"], check=True)
    head = driver._git(repo, "rev-parse", "HEAD")
    run_dir = runs / "RUN-guard-x"
    monkeypatch.setattr(cellrun, "RUNS_ROOT", runs)
    monkeypatch.setenv(cellrun.ADMISSION_ENV, DEC)
    monkeypatch.setenv(cellrun.REPO_ENV, str(repo))
    monkeypatch.setenv(cellrun.RUN_DIR_ENV, str(run_dir))
    monkeypatch.setenv(cellrun.RUN_TOKEN_ENV, TOKEN)
    monkeypatch.setenv(cellrun.DRIVER_PID_ENV, str(DPID))
    return repo, runs, run_dir, head


def test_frozen_guard_binds_to_real_driver(monkeypatch, tmp_root):
    """v4b G-2."""
    repo, runs, run_dir, head = _guard_env(monkeypatch, tmp_root)
    g = lambda: cellrun.admission_guard(common.FROZEN_NS)  # noqa: E731
    ok, why = g()
    assert not ok and "admission decision refused" in why  # the tmp repo has no such decision
    monkeypatch.setattr(driver, "check_decision", lambda root, d: (True, "stub"))
    assert not g()[0]  # no manifest
    parents = []
    monkeypatch.setattr(cellrun, "parent_is_driver", lambda pid: (parents.append(pid) or True, "stub parent"))
    _manifest(run_dir, head)
    ok, why = g()
    assert ok and DEC in why and parents == [DPID]
    # hand-written manifests: every binding field is checked
    bad = {"stub": dict(stub=True), "status": dict(status="completed_valid"), "id": dict(id="RUN-other"),
           "decision": dict(inputs={"admission_decision": "DEC-20990101-bbbbbb"}),
           "namespace": dict(inputs={"namespace": common.SMOKE_NS}),
           "token": dict(inputs={"run_token_sha256": driver.token_sha256("guessed")}),
           "no_token": dict(inputs={"run_token_sha256": None}),
           "pid": dict(inputs={"driver_pid": DPID + 1}), "no_pid": dict(inputs={"driver_pid": None}),
           "commit": dict(code={"commit": "0" * 40})}
    for name, over in bad.items():
        _manifest(run_dir, head, **over)
        assert not g()[0], name
    _manifest(run_dir, head)
    # the parent check itself is real: this test process's parent is not driver.py
    monkeypatch.setattr(cellrun, "parent_is_driver", lambda pid: (False, "real check refused"))
    assert not g()[0]
    monkeypatch.setattr(cellrun, "parent_is_driver", lambda pid: (True, "stub parent"))
    # run directory must be RUNS_ROOT/RUN-*
    for rd in (tmp_root / "guard_elsewhere" / "RUN-guard-x", runs / "DRYRUN-x", runs / "RUN-guard-x" / "RUN-y"):
        _manifest(rd, head)
        monkeypatch.setenv(cellrun.RUN_DIR_ENV, str(rd))
        assert not g()[0], rd
    monkeypatch.setenv(cellrun.RUN_DIR_ENV, str(run_dir))
    assert g()[0]
    # missing token or driver pid in the environment
    for k in (cellrun.RUN_TOKEN_ENV, cellrun.DRIVER_PID_ENV):
        v = os.environ[k]
        monkeypatch.delenv(k)
        assert not g()[0], k
        monkeypatch.setenv(k, v)
    monkeypatch.setenv(cellrun.RUN_TOKEN_ENV, "cd" * 32)
    assert not g()[0]
    shutil.rmtree(repo)
    shutil.rmtree(tmp_root / "guard_elsewhere", ignore_errors=True)


def test_default_runs_root_is_the_experiment_runs_dir():
    assert cellrun.RUNS_ROOT == common.EXP_DIR / "runs"


def test_parent_is_driver_real_processes(tmp_root):
    """v4b G-2: a real parent named driver.py in the expected directory passes;
    wrong directory, wrong pid, or a non-driver parent fails."""
    ok, why = cellrun.parent_is_driver(os.getppid())
    assert not ok and "is not" in why  # pytest's parent is not driver.py
    assert not cellrun.parent_is_driver(os.getpid())[0]
    assert not cellrun.parent_is_driver("1")[0]
    d = tmp_root / "fake_driver_dir"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
    child = ("import json, os, sys; from pathlib import Path; sys.path.insert(0, %r); import cellrun; "
             "print(json.dumps([cellrun.parent_is_driver(os.getppid(), impl_dir=Path(%r))[0], "
             "cellrun.parent_is_driver(os.getppid())[0], cellrun.parent_is_driver(os.getppid() + 1, "
             "impl_dir=Path(%r))[0]]))") % (str(common.HERE), str(d), str(d))
    (d / "driver.py").write_text("import subprocess, sys\n"
                                 f"r = subprocess.run([sys.executable, '-c', {child!r}], capture_output=True, "
                                 "text=True)\nsys.stdout.write(r.stdout)\nsys.stderr.write(r.stderr)\n")
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(d / "driver.py")], capture_output=True, text=True, timeout=120,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert json.loads(r.stdout) == [True, False, False], r.stderr[-500:]
    shutil.rmtree(d)


def test_watch_parent_exits_on_reparent():
    import time
    fired, ppid = [], [100]
    cellrun.watch_parent(100, interval=0.01, exit_fn=lambda: fired.append(1), getppid=lambda: ppid[0])
    time.sleep(0.05)
    assert not fired
    ppid[0] = 1
    for _ in range(100):
        if fired:
            break
        time.sleep(0.01)
    assert fired == [1]


def test_cellrun_with_wrong_driver_pid_exits_without_writing(tmp_root):
    """v4b G-1: a cell whose announced driver is not its parent writes nothing."""
    import subprocess
    import sys
    fx = synthetic.synthetic_fixture(0)
    task = tmp_root / "orphan_task.json"
    out = tmp_root / "orphan_out.json"
    out.unlink(missing_ok=True)
    task.write_text(json.dumps({"cell_id": "x:rho", "kind": "rho", "fixture": fx, "bits": fx["bits"],
                                "seed": fx["seed"], "namespace": common.SMOKE_NS + "|g1", "params": {"n_targets": 1}}))
    r = subprocess.run([sys.executable, str(common.HERE / "cellrun.py"), "--task", str(task), "--out", str(out)],
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", ICEX_AACCFC_DRIVER_PID="1"),
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == cellrun.EXIT_ORPHANED and not out.exists()
    task.unlink()


def test_smoke_task_naming_frozen_fixture_refused(no_admission_env, tmp_root):
    """v4b A-1: cellrun persists its result, so a smoke task may never name a
    frozen fixture (by bits/seed or inline); refused before any label."""
    for bits, seed in ((16, 21), (20, 23)):
        for ns in (common.SMOKE_NS, pipeline.TESTS_NS_PREFIX):
            with pytest.raises(cellrun.AdmissionRefused, match="A-1"):
                cellrun.task_fixture({"bits": bits, "seed": seed, "namespace": ns})
    task = tmp_root / "a1_task.json"
    out = tmp_root / "a1_out.json"
    task.write_text(json.dumps({"cell_id": "b16-s21:rho", "bits": 16, "seed": 21, "kind": "rho",
                                "namespace": common.SMOKE_NS, "params": {"n_targets": 1}}))
    assert cellrun.main(["--task", str(task), "--out", str(out)]) == cellrun.EXIT_REFUSED
    r = json.loads(out.read_text())
    assert r["status"] == "refused" and "result" not in r
    task.unlink()
    out.unlink()


def test_pipeline_frozen_fixture_only_in_unit_test_namespace():
    """v4b A-1: pipeline refuses a frozen fixture in any smoke namespace except
    the in-process unit-test prefix (which persists nothing)."""
    fx = common.fixture(16, 21)
    for ns in (common.SMOKE_NS, common.SMOKE_NS + "|x", common.SMOKE_NS + "|tes"):
        with pytest.raises(pipeline.NamespaceRefused, match="frozen fixture"):
            pipeline.run_rho_cell(fx, ns, n_targets=1)
    pipeline._ns_guard(pipeline.TESTS_NS_PREFIX, fx)
    pipeline._ns_guard(pipeline.TESTS_NS_PREFIX + "-fxa", fx)
    pipeline._ns_guard(common.SMOKE_NS, synthetic.synthetic_fixture(0))


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


FROZEN_FIXTURE_TEST_MODULES = ("conftest", "test_charging", "test_controls", "test_fxa", "test_fixtures")


def test_frozen_fixture_test_modules_disable_assertion_rewriting(tmp_root):
    """v4b A-3: modules that evaluate frozen fixtures carry PYTEST_DONT_REWRITE,
    and under it a failing comparison reports no computed value."""
    import importlib
    import subprocess
    import sys
    for name in FROZEN_FIXTURE_TEST_MODULES:
        assert "PYTEST_DONT_REWRITE" in (importlib.import_module(name).__doc__ or ""), name
    d = tmp_root / "a3_probe"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
    body = "def test_hidden():\n    x = 7919 * 7907\n    assert x == 1, 'withheld'\n"
    (d / "test_rewritten.py").write_text(body)
    (d / "test_plain.py").write_text('"""PYTEST_DONT_REWRITE"""\n' + body)
    hidden = str(7919 * 7907)
    outs = {}
    for f in ("test_rewritten.py", "test_plain.py"):
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(d / f)],
                           capture_output=True, text=True, timeout=120, cwd=str(d),
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert r.returncode == 1
        outs[f] = r.stdout + r.stderr
    assert hidden in outs["test_rewritten.py"]  # the probe is sensitive
    assert hidden not in outs["test_plain.py"] and "withheld" in outs["test_plain.py"]
    shutil.rmtree(d)


def test_smoke_summary_cell_ids_are_values_not_keys():
    kinds = ("primary", "null_randfb", "stage_cost_m6", "stage_cost_m8", "rho")
    smoke.assert_no_cost_fields({"cells": [{"cell": f"b13-s900:{k}", "status": "ok"} for k in kinds],
                                 "fxa_file_written": True, "scientific_output": "none: no C-5 analysis in smoke"})
