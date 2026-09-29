"""Protocol v4 (AMD-20260929-cc7226) required fixes FX-1..FX-7."""

import json
import os
import signal
import subprocess
import types
from pathlib import Path

import pytest
import yaml

import analysis
import celltask
import driver
import fixtures
import hostinfo
import labels
import smoke

REPO = driver.REPO_ROOT_DEFAULT
PASSING = {"load_15min": 1.0, "system_volume_free_gib": 50.0, "repo_volume_free_gib": 500.0,
           "errors": []}
PLAN = json.loads((driver.HERE / "trial-plan-v2.json").read_text())


# ---------------------------------------------------------------- FX-1 / FX-7

def _args(tmp_path, run_id="DRYRUN-t"):
    return types.SimpleNamespace(run_id=run_id, runs_dir=str(tmp_path), plan=str(driver.HERE / "trial-plan-v2.json"),
                                 repo_root=str(REPO), admission_decision=None)


def _dry(fid="b16-s13"):
    return {"fixtures": [fid], "a1": 3, "a2": 5, "replicates": 1, "rho_targets": 1}


@pytest.fixture
def fast_env(monkeypatch):
    monkeypatch.setattr(driver, "sage_version", lambda: {"version": "SageMath test", "executable": "x"})


def _fake_cell(result_status=0, defects=(), raise_exc=None, seen=None):
    def run_cell(cmd, log_dir, name, psutil, env=None):
        run_dir = log_dir.parent
        man = yaml.safe_load((run_dir / "manifest.yaml").read_text())
        if seen is not None:
            seen.append(man["run"]["status"])
        if raise_exc is not None:
            raise raise_exc
        out = Path(cmd[cmd.index("--out") + 1])
        out.write_text(json.dumps({"fixture_id": name, "procedure_defects": list(defects), "ns": cmd[cmd.index("--ns") + 1]}))
        return {"returncode": result_status, "peak_rss_bytes": 1000, "peak_rss_polled_bytes": 0,
                "killed_by_memory_watchdog": False, "wall_seconds": 0.1, "cpu_user_seconds": 0.05,
                "cpu_system_seconds": 0.01}
    return run_cell


def test_fx1_canonical_manifest_written_before_first_cell_and_updated(tmp_path, monkeypatch, fast_env):
    seen = []
    monkeypatch.setattr(driver, "run_cell", _fake_cell(seen=seen))
    code = driver.execute(_args(tmp_path), PLAN, dict(PASSING), "smoke", _dry(), "python3 driver.py --x",
                          driver.protocol_binding(REPO), None, object())
    assert code == 0 and seen == ["running"]
    rd = tmp_path / "DRYRUN-t"
    for f in ("manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json"):
        assert (rd / f).is_file(), f
    man = yaml.safe_load((rd / "manifest.yaml").read_text())
    run = man["run"]
    for k in ("id", "experiment_id", "status", "code", "environment", "inputs", "timing", "result"):
        assert k in run
    assert run["status"] == "completed_valid" and run["result"]["valid"] is True
    assert run["id"] == "DRYRUN-t" and run["experiment_id"] == "EXP-RELN-c5a377"
    assert run["code"]["command"] == "python3 driver.py --x"
    assert run["result"]["certificate"]["kind"] == "decomposition"
    assert run["timing"]["finished_at"] and man["driver"]["cells"][0]["status"] == "completed"
    assert "cell b16-s13" in (rd / "stdout.log").read_text()
    env = json.loads((rd / "environment.json").read_text())
    assert set(env["dependencies"]) >= {"pyyaml", "scipy", "networkx", "psutil"}
    assert env["dependencies"]["pyyaml"] and env["sage_version"] == "SageMath test"


def test_fx1_exception_recorded_as_failed_infrastructure(tmp_path, monkeypatch, fast_env):
    monkeypatch.setattr(driver, "run_cell", _fake_cell(raise_exc=RuntimeError("boom")))
    code = driver.execute(_args(tmp_path), PLAN, dict(PASSING), "smoke", _dry(), "cmd",
                          driver.protocol_binding(REPO), None, object())
    assert code == driver.EXIT_INFRASTRUCTURE
    run = yaml.safe_load((tmp_path / "DRYRUN-t" / "manifest.yaml").read_text())["run"]
    assert run["status"] == "failed_infrastructure" and run["failure_class"] == "exception"
    assert "boom" in run["failure_reason"] and run["result"]["valid"] is False
    assert "RuntimeError" in (tmp_path / "DRYRUN-t" / "stderr.log").read_text()


def test_fx1_signal_recorded_as_failed_infrastructure(tmp_path, monkeypatch, fast_env):
    def sig_cell(cmd, log_dir, name, psutil, env=None):
        os.kill(os.getpid(), signal.SIGTERM)
        raise AssertionError("signal handler did not raise")
    before = signal.getsignal(signal.SIGTERM)
    monkeypatch.setattr(driver, "run_cell", sig_cell)
    code = driver.execute(_args(tmp_path), PLAN, dict(PASSING), "smoke", _dry(), "cmd",
                          driver.protocol_binding(REPO), None, object())
    assert code == driver.EXIT_INFRASTRUCTURE
    run = yaml.safe_load((tmp_path / "DRYRUN-t" / "manifest.yaml").read_text())["run"]
    assert run["status"] == "failed_infrastructure" and run["failure_class"] == "signal"
    assert "SIGTERM" in run["failure_reason"]
    assert signal.getsignal(signal.SIGTERM) == before


def test_fx1_procedure_defect_is_invalid(tmp_path, monkeypatch, fast_env):
    monkeypatch.setattr(driver, "run_cell", _fake_cell(result_status=7, defects=["x"]))
    code = driver.execute(_args(tmp_path), PLAN, dict(PASSING), "smoke", _dry(), "cmd",
                          driver.protocol_binding(REPO), None, object())
    assert code == driver.EXIT_PROCEDURE_DEFECT
    run = yaml.safe_load((tmp_path / "DRYRUN-t" / "manifest.yaml").read_text())["run"]
    assert run["status"] == "invalid" and run["result"]["certificate"]["verified"] is False


def test_fx7_command_txt_records_driver_argv(monkeypatch):
    got = {}

    def fake_execute(args, plan, readings, dp, dry, command, binding, snapshot, psutil):
        got["command"] = command
        return 0
    monkeypatch.setattr(driver, "execute", fake_execute)
    argv = ["--smoke-dry-run", "--run-id", "DRYRUN-argv", "--runs-dir", str(driver.HERE / "smoke" / "never"),
            "--dry-a1", "10", "--dry-a2", "20"]
    assert driver.main(argv) == 0
    assert got["command"].endswith("driver.py " + " ".join(argv))
    assert not (driver.HERE / "smoke" / "never").exists()


def test_fx7_watchdog_fails_closed_without_psutil(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "import_psutil", lambda: None)
    monkeypatch.setattr(hostinfo, "readings", lambda root: dict(PASSING))
    assert driver.main(["--run-id", "RUN-t", "--runs-dir", str(tmp_path)]) == driver.EXIT_REFUSED_WATCHDOG
    assert driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-t", "--runs-dir",
                        str(driver.HERE / "smoke" / "never")]) == driver.EXIT_REFUSED_WATCHDOG
    assert not any(tmp_path.iterdir())
    with pytest.raises(RuntimeError):
        driver.run_cell(["true"], tmp_path, "x", None)


# ---------------------------------------------------------------- FX-2

def test_fx2_protocol_binding_v4():
    b = driver.protocol_binding(REPO)
    assert b["protocol_version"] == 4 == driver.PROTOCOL_VERSION
    recs = b["records"]
    for k in ("amendment_v2", "amendment_v3", "amendment_v4", "decision_v3", "decision_v4"):
        p = REPO / recs[k]["path"]
        assert recs[k]["sha256"] == fixtures.sha256_file(p)
    assert recs["amendment_v4"]["path"].endswith("AMD-20260929-cc7226.yaml")
    assert recs["decision_v3"]["path"].endswith("DEC-20260929-3d166b.yaml")
    assert recs["decision_v4"]["path"].endswith("DEC-20260929-7a62cc.yaml")
    ok, bad = driver.check_protocol_binding(REPO, b)
    assert ok, bad


def test_fx2_binding_refuses_tampered_or_missing():
    b = driver.protocol_binding(REPO)
    b["records"]["amendment_v4"]["sha256"] = "0" * 64
    ok, bad = driver.check_protocol_binding(REPO, b)
    assert not ok and any("cc7226" in x for x in bad)
    b = driver.protocol_binding(REPO)
    b["records"]["decision_v4"]["sha256"] = None
    assert not driver.check_protocol_binding(REPO, b)[0]


def test_fx2_trial_plan_unchanged():
    assert fixtures.sha256_file(driver.HERE / "trial-plan-v2.json") == \
        "7fb5e40dffa543feb25ea97fc62a8be16baf2db170df6025ec5f1cb7bbef29cf"
    assert driver.check_plan(PLAN)[0]


# ---------------------------------------------------------------- FX-3 (F-4, celltask)

@pytest.mark.parametrize("L,vmin", [(2, 2), (6, 5), (7, 5), (10, 7), (12, 8), (14, 10)])
def test_fx3_gate_min_v(L, vmin):
    assert celltask.planted_gate_min_v(L) == vmin
    assert celltask.planted_gate_min_v(1) is None


def test_fx3_known_positive_not_exercised_below_gate():
    defects = []
    kp = celltask.known_positive(4, 6, labels.SMOKE_NS + "|test", "ctx", "A1", defects)
    assert kp["status"] == "not_exercised" and kp["gate_min_V"] == 5 and not kp["power_confirmed"]
    assert defects == []
    kp = celltask.known_positive(50, 1, labels.SMOKE_NS + "|test", "ctx", "A1", defects)
    assert kp["status"] == "not_exercised" and kp["gate_min_V"] is None and defects == []
    kp = celltask.known_positive(1, 6, labels.SMOKE_NS + "|test", "ctx", "A1", defects)
    assert kp["status"] == "not_exercised" and defects == []


def test_fx3_known_positive_pass_at_gate():
    defects = []
    kp = celltask.known_positive(5, 6, labels.SMOKE_NS + "|test", "ctx", "A1", defects)
    assert kp["status"] == "pass" and kp["exercised"] and kp["power_confirmed"] and defects == []


def test_fx3_known_positive_fail_when_reachable_is_defect(monkeypatch):
    def tree(n, ns, ctx):
        return {"n": n, "edges": [(i - 1, i) for i in range(1, n)], "planted_cycle_rank": 0}
    monkeypatch.setattr(celltask.nulls, "planted_dense", tree)
    defects = []
    kp = celltask.known_positive(20, 6, labels.SMOKE_NS + "|test", "ctx", "A1", defects)
    assert kp["status"] == "FAIL" and len(defects) == 1


# ---------------------------------------------------------------- FX-3 (F-3, F-4) / FX-4, analysis

def cell(bits, seed, dp, er_dp, er_feasible=True, kp="pass", kf="fails_verification", giant=0.5, cr=None, cyc=1):
    L = 6
    cr = cr if cr is not None else (round(L ** (dp + 1)) if dp is not None else 0)

    def blk(bu):
        return {"budget": bu,
                "graph": {"delta_proof": dp, "delta_ratio": None, "cycle_rank": cr, "E": 100, "V": 50,
                          "giant_component_fraction": giant, "components_with_cycle": cyc},
                "null_er": {"replicates": [{"delta_proof": er_dp} if er_feasible else None] * 32},
                "null_rewire": {"replicates": [{"delta_proof": er_dp}] * 32},
                "known_positive": {"status": kp}, "known_false": {"status": kf},
                "recovery": {"lp_recovery_fraction": 0.5},
                "charged": {"charged_work_over_sqrt_q": 10.0}}
    return {"fixture_id": f"b{bits}-s{seed}", "fixture": {"bits": bits, "seed": seed},
            "ns": "EXP-RELN-c5a377/v2", "budgets": [blk("A1"), blk("A2")]}


def grid(f):
    return [f(b, s) for b in (16, 20, 24) for s in (11, 12, 13)]


def _dp(b, s):
    return 0.6 + 0.01 * (s - 12) + 0.001 * b


def test_fx3_er_infeasible_everywhere_blocks_supercritical():
    assert analysis.verdict(grid(lambda b, s: cell(b, s, _dp(b, s), 0.1)))["verdict"] == "supercritical-enriched"
    v = analysis.verdict(grid(lambda b, s: cell(b, s, _dp(b, s), 0.1, er_feasible=False)))
    assert v["verdict"] == "inconclusive" and "F-3" in v["reason"]
    assert v["clauses"]["supercritical_rule"] == "undetermined"
    assert len(v["clauses"]["er_null_undetermined_cells"]) == 6
    assert all(c["er_feasible_replicates"] == 0 and c["er_exceeds_quarter"] == "undetermined"
               for c in v["per_cell"].values())


def test_fx3_one_infeasible_cell_blocks_supercritical():
    v = analysis.verdict(grid(lambda b, s: cell(b, s, _dp(b, s), 0.1, er_feasible=(b != 20))))
    assert v["verdict"] == "inconclusive"
    assert v["clauses"]["er_null_undetermined_cells"] == ["20-A1", "20-A2"]
    assert v["per_cell"]["16-A1"]["er_feasible_replicates"] == 96


def test_fx3_partially_feasible_cell_is_determined():
    def mk(b, s):
        c = cell(b, s, _dp(b, s), 0.1)
        if b == 20 and s != 11:
            for blk in c["budgets"]:
                blk["null_er"]["replicates"] = [None] * 32
        return c
    v = analysis.verdict(grid(mk))
    assert v["verdict"] == "supercritical-enriched"
    assert v["per_cell"]["20-A1"]["er_feasible_replicates"] == 32


def test_fx3_er_infeasible_does_not_change_other_verdicts():
    v = analysis.verdict(grid(lambda b, s: cell(b, s, None, None, er_feasible=False, giant=0.01, cr=2, cyc=1)))
    assert v["verdict"] == "certified-subcritical"
    v = analysis.verdict(grid(lambda b, s: cell(b, s, {11: 0.3, 12: 1.2, 13: 0.26}[s], 0.0, er_feasible=False)))
    assert v["verdict"] == "inconclusive" and v["reason"] == "neither C-5 rule holds"


def test_fx3_known_positive_not_exercised_listed_verdict_unchanged():
    base = analysis.verdict(grid(lambda b, s: cell(b, s, None, None, giant=0.01, cr=2, cyc=1)))
    v = analysis.verdict(grid(lambda b, s: cell(b, s, None, None, giant=0.01, cr=2, cyc=1,
                                                kp="not_exercised" if b == 16 else "pass")))
    assert v["verdict"] == base["verdict"] == "certified-subcritical"
    assert v["known_positive"]["cells_lacking_power_confirmation"] == ["16-A1", "16-A2"]
    assert "16-A1" not in v["known_positive"]["negative_conclusion_scope_cells"]
    assert len(v["known_positive"]["negative_conclusion_scope_cells"]) == 4
    assert v["per_cell"]["16-A1"]["known_positive_power_confirmed"] is False


def test_fx4_recovery_fraction_undetermined_when_known_false_not_exercised():
    tab = analysis.table(grid(lambda b, s: cell(b, s, 0.8, 0.0, kf="not_exercised" if s == 11 else "fails_verification")))
    for rows in tab.values():
        for r in rows:
            if r["seed"] == 11:
                assert r["lp_recovery_fraction"] == "undetermined"
            else:
                assert r["lp_recovery_fraction"] == 0.5


# ---------------------------------------------------------------- FX-5

def _write_dec(root: Path, dec_id, doc_extra=None, **over):
    d = {"id": dec_id, "decision": "approve", "target_ids": ["EXP-RELN-c5a377"],
         "execution_admission": {"currently_admitted": True}}
    d.update(over)
    p = root / "ledger" / "decisions"
    p.mkdir(parents=True, exist_ok=True)
    doc = {"coordinator_decision": d, **(doc_extra or {})}
    (p / f"{dec_id}.yaml").write_text(yaml.safe_dump(doc))


def test_fx5_superseded_or_withdrawn_decisions_refused(tmp_path):
    _write_dec(tmp_path, "DEC-20990101-a00001")
    assert driver.check_decision(tmp_path, "DEC-20990101-a00001")[0]
    _write_dec(tmp_path, "DEC-20990101-a00002", status="superseded")
    _write_dec(tmp_path, "DEC-20990101-a00003", status="Withdrawn")
    _write_dec(tmp_path, "DEC-20990101-a00004", superseded_by="DEC-20990102-bbbbbb")
    _write_dec(tmp_path, "DEC-20990101-a00005", doc_extra={"status": "superseded"})
    _write_dec(tmp_path, "DEC-20990101-a00006",
               execution_admission={"currently_admitted": True, "superseded_by": "DEC-20990102-cccccc"})
    for i in range(2, 7):
        ok, why = driver.check_decision(tmp_path, f"DEC-20990101-a0000{i}")
        assert not ok, i
    _write_dec(tmp_path, "DEC-20990101-a00007", superseded_by=None)
    assert driver.check_decision(tmp_path, "DEC-20990101-a00007")[0]


def test_fx5_decision_superseded_by_later_decision_refused(tmp_path):
    _write_dec(tmp_path, "DEC-20990101-b00001")
    _write_dec(tmp_path, "DEC-20990102-b00002", supersedes=["DEC-20990101-b00001"],
               execution_admission={"currently_admitted": False})
    ok, why = driver.check_decision(tmp_path, "DEC-20990101-b00001")
    assert not ok and "superseded by" in why


def _git(root, *a):
    subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


@pytest.fixture
def snap_repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    impl = root / driver.IMPL_REL
    (impl / "tests").mkdir(parents=True)
    (impl / "a.py").write_text("A = 1\n")
    (impl / "tests" / "test_a.py").write_text("def test(): pass\n")
    (impl / "trial-plan-v2.json").write_text("{}\n")
    _git(root, "init", "-q")
    monkeypatch.setattr(driver, "HERE", impl)

    def receipt(extra=None, where=None):
        pins = {f"{driver.IMPL_REL}/{p}": fixtures.sha256_file(impl / p)
                for p in ("a.py", "tests/test_a.py", "trial-plan-v2.json")}
        rp = where or (root / "coordination" / "receipt.json")
        rp.parent.mkdir(parents=True, exist_ok=True)
        pins.update(extra or {})
        rp.write_text(json.dumps({"task_id": "TASK-x", "path_sha256": pins}))
        return rp
    return root, impl, receipt


def test_fx5_snapshot_receipt_match_and_clean(snap_repo):
    root, impl, receipt = snap_repo
    rp = receipt()
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "x")
    ok, info = driver.verify_snapshot(root, rp)
    assert ok, info
    assert info["checked"] == 3 and info["dirty"] is False


def test_fx5_snapshot_receipt_excludes_itself(snap_repo):
    root, impl, receipt = snap_repo
    rp = impl / "receipt.json"
    receipt(extra={f"{driver.IMPL_REL}/receipt.json": "0" * 64}, where=rp)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "x")
    ok, info = driver.verify_snapshot(root, rp)
    assert ok, info


def test_fx5_snapshot_refuses_mismatch_dirty_unpinned(snap_repo):
    root, impl, receipt = snap_repo
    rp = receipt()
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "x")
    (impl / "a.py").write_text("A = 2\n")
    ok, info = driver.verify_snapshot(root, rp)
    assert not ok and info["mismatches"] == [f"{driver.IMPL_REL}/a.py"] and info["dirty"]
    _git(root, "checkout", "--", ".")
    (impl / "b.py").write_text("B = 1\n")
    ok, info = driver.verify_snapshot(root, rp)
    assert not ok and info["unpinned"] == [f"{driver.IMPL_REL}/b.py"] and info["dirty"]
    (impl / "b.py").unlink()
    (impl / "notes.txt").write_text("x")
    ok, info = driver.verify_snapshot(root, rp)
    assert not ok and not info["mismatches"] and info["dirty"]
    (impl / "notes.txt").unlink()
    assert driver.verify_snapshot(root, rp)[0]
    assert not driver.verify_snapshot(root, None)[0]
    assert not driver.verify_snapshot(root, root / "missing.json")[0]


def test_fx5_main_requires_snapshot_receipt(monkeypatch, tmp_path):
    monkeypatch.setattr(hostinfo, "readings", lambda root: dict(PASSING))
    monkeypatch.setattr(driver, "check_decision", lambda root, d: (True, "synthetic"))
    monkeypatch.setattr(driver, "check_protocol_binding", lambda root, b: (True, []))
    monkeypatch.setattr(driver, "execute", lambda *a, **k: pytest.fail("execute reached"))
    base = ["--run-id", "RUN-t", "--admission-decision", "DEC-20990101-aaaaaa", "--runs-dir", str(tmp_path)]
    assert driver.main(base) == driver.EXIT_REFUSED_SNAPSHOT
    old = REPO / "coordination/goals/GOAL-RELN-001/batches/BATCH-229ce4/archives/TASK-20260929-03d6bf/snapshot-receipt.json"
    if old.exists():
        assert driver.main(base + ["--snapshot-receipt", str(old)]) == driver.EXIT_REFUSED_SNAPSHOT
    assert not any(tmp_path.iterdir())


def test_fx5_celltask_refuses_frozen_namespace_without_admitted_driver(monkeypatch, tmp_path):
    for k in (driver.ADMISSION_ENV, driver.REPO_ENV, driver.RUN_DIR_ENV):
        monkeypatch.delenv(k, raising=False)
    assert celltask.admission_guard(labels.SMOKE_NS)[0]
    ok, why = celltask.admission_guard(labels.FROZEN_NS)
    assert not ok and "not launched" in why
    out = tmp_path / "c.json"
    assert celltask.main(["--bits", "16", "--seed", "13", "--ns", labels.FROZEN_NS, "--a1", "1", "--a2", "2",
                          "--out", str(out)]) == 3
    with pytest.raises(PermissionError):
        celltask.run(16, 13, labels.FROZEN_NS, 1, 2, 1, 1, out)
    assert not out.exists() and not out.with_suffix(".attempts.jsonl").exists()
    monkeypatch.setenv(driver.ADMISSION_ENV, "DEC-20260929-7a62cc")
    monkeypatch.setenv(driver.REPO_ENV, str(REPO))
    monkeypatch.setenv(driver.RUN_DIR_ENV, str(tmp_path))
    ok, why = celltask.admission_guard(labels.FROZEN_NS)
    assert not ok and "currently_admitted" in why


def test_fx5_celltask_guard_accepts_running_admitted_manifest(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "check_decision", lambda root, d: (True, "synthetic"))
    monkeypatch.setenv(driver.ADMISSION_ENV, "DEC-20990101-aaaaaa")
    monkeypatch.setenv(driver.REPO_ENV, str(tmp_path))
    monkeypatch.setenv(driver.RUN_DIR_ENV, str(tmp_path))
    man = {"run": {"id": "RUN-t", "status": "running",
                   "inputs": {"admission_decision": "DEC-20990101-aaaaaa", "namespace": labels.FROZEN_NS}}}
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump(man))
    assert celltask.admission_guard(labels.FROZEN_NS)[0]
    man["run"]["status"] = "completed_valid"
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump(man))
    assert not celltask.admission_guard(labels.FROZEN_NS)[0]


# ---------------------------------------------------------------- FX-6

def test_fx6_driver_refuses_frozen_budgets():
    target = driver.HERE / "smoke" / "never"
    for fid, a1, a2 in (("b16-s11", 249, 751), ("b16-s13", 10, 574), ("b16-s13", 3627, 5000)):
        code = driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-x", "--runs-dir", str(target),
                            "--dry-fixture", fid, "--dry-a1", str(a1), "--dry-a2", str(a2)])
        assert code == driver.EXIT_REFUSED_PLAN
    assert not target.exists()


def test_fx6_smoke_configs_avoid_frozen_budgets():
    assert smoke.check_budgets(PLAN) == []
    assert smoke.check_budgets(PLAN, {"X": (249, 751, 1, 1)}) == [("X", 249), ("X", 751)]
    assert smoke.FIXTURE == min(PLAN["fixtures"], key=lambda f: f["q"])["fixture_id"]
    assert smoke.SMOKE_DIR != driver.HERE / "smoke"
