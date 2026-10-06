"""Driver: admission (v4 FX-1), fail-closed C-7, trial plan and protocol v4
binding, run record and failure handling (FX-2/FX-3), snapshot pinning (FX-6),
inference block (FX-7). No cell, no Sage and no frozen label is evaluated."""

import argparse
import json
import os
import shutil
import signal
import subprocess
from pathlib import Path

import pytest
import yaml

import common
import driver
import make_trial_plan

GOOD = {"host_kind": "macos", "vm_loadavg_raw": "{ 1.0 2.0 3.0 }", "load_15min": 3.0,
        "system_volume_free_gib": 50.0, "repo_volume_free_gib": 100.0, "read_at": "x"}
ADMIT = {"decision": "admit_execution", "target_ids": ["EXP-ICEX-aaccfc"],
         "execution_admission": {"currently_admitted": True}}


# ------------------------------------------------------------------ helpers
def _git(root, *a):
    subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True)


def _fresh_repo(base: Path, name: str) -> Path:
    root = base / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    _git(root, "config", "commit.gpgsign", "false")
    return root


def _write_dec(root: Path, dec_id: str, body: dict, top: dict | None = None):
    d = root / "ledger" / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{dec_id}.yaml").write_text(yaml.safe_dump({"coordinator_decision": {"id": dec_id, **body},
                                                      **(top or {})}))


def _commit(root):
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "x")


# ------------------------------------------------------------------ FX-1
def test_real_ledger_decisions_are_refused():
    for dec in ("DEC-20260929-f45bf1", "DEC-20260929-a8d594", "DEC-20260929-986b4c"):
        ok, why = driver.check_decision(common.REPO_ROOT, dec)
        assert not ok, dec


def test_decision_rules(tmp_root):
    root = _fresh_repo(tmp_root, "fx1_repo")
    good = "DEC-20990101-aaaaaa"
    _write_dec(root, good, ADMIT)
    _write_dec(root, "DEC-20990101-a0a0a0", {**ADMIT, "superseded_by": None, "status": "decided"},
               top={"superseded_by": None})
    cases = {
        "DEC-20990101-bbbbbb": {**ADMIT, "target_ids": ["EXP-OTHER"]},
        "DEC-20990101-cccccc": {**ADMIT, "execution_admission": {"currently_admitted": "true"}},
        "DEC-20990101-c1c1c1": {**ADMIT, "status": "superseded"},
        "DEC-20990101-c2c2c2": {**ADMIT, "status": "Withdrawn"},
        "DEC-20990101-c3c3c3": {**ADMIT, "superseded_by": "DEC-20990102-ffffff"},
        "DEC-20990101-c4c4c4": {**ADMIT, "decision": "pause"},
        "DEC-20990101-c5c5c5": {**ADMIT, "decision": "approve_amendment"},
        "DEC-20990101-c6c6c6": {**ADMIT, "execution_admission": {"currently_admitted": True,
                                                                 "superseded_by": "DEC-20990102-ffffff"}},
        "DEC-20990101-c8c8c8": {**ADMIT, "decision": None},
        # v4b A-2: only `admit_execution` admits
        "DEC-20990101-c9c9c9": {**ADMIT, "decision": "approve_execution"},
        "DEC-20990101-cacaca": {**ADMIT, "decision": "admit"},
        "DEC-20990101-cbcbcb": {**ADMIT, "decision": "approve"},
    }
    for dec_id, body in cases.items():
        _write_dec(root, dec_id, body)
    _write_dec(root, "DEC-20990101-c7c7c7", ADMIT, top={"status": "superseded"})
    _write_dec(root, "DEC-20990101-dddddd", ADMIT)
    (root / "ledger" / "decisions" / "DEC-20990101-dddddd.yaml").write_text(
        yaml.safe_dump({"coordinator_decision": {"id": "DEC-20990101-eeeeee", **ADMIT}}))
    # superseded by a later decision (string form and list form)
    _write_dec(root, "DEC-20990101-111111", ADMIT)
    _write_dec(root, "DEC-20990101-222222", ADMIT)
    _write_dec(root, "DEC-20990102-333333", {"decision": "supersede", "supersedes": "DEC-20990101-111111"})
    _write_dec(root, "DEC-20990102-444444", {"decision": "supersede", "supersedes": ["DEC-20990101-222222"]})
    # a decision that merely mentions the id in prose does not supersede it
    _write_dec(root, "DEC-20990102-555555", {"decision": "note", "rationale": f"see {good}", "supersedes": []})
    _commit(root)
    assert driver.check_decision(root, good) == (True, str(root / "ledger/decisions" / f"{good}.yaml"))
    assert driver.check_decision(root, "DEC-20990101-a0a0a0")[0], "superseded_by: null must not refuse"
    for dec_id in list(cases) + ["DEC-20990101-c7c7c7", "DEC-20990101-dddddd",
                                 "DEC-20990101-111111", "DEC-20990101-222222"]:
        assert not driver.check_decision(root, dec_id)[0], dec_id
    assert "superseded by" in driver.check_decision(root, "DEC-20990101-111111")[1]
    for bad in ("DEC-20990101-ffffff", None, "DEC-001", "../x"):
        assert not driver.check_decision(root, bad)[0]
    # uncommitted decision
    _write_dec(root, "DEC-20990103-666666", ADMIT)
    ok, why = driver.check_decision(root, "DEC-20990103-666666")
    assert not ok and "not tracked" in why
    # committed but dirty (unstaged, then staged)
    p = root / "ledger" / "decisions" / f"{good}.yaml"
    p.write_text(p.read_text() + "# edit\n")
    ok, why = driver.check_decision(root, good)
    assert not ok and "differs from HEAD" in why
    _git(root, "add", str(p))
    assert not driver.check_decision(root, good)[0]
    _git(root, "reset", "-q", "--hard")
    assert driver.check_decision(root, good)[0]
    # an uncommitted later superseding decision also refuses (fail closed)
    _write_dec(root, "DEC-20990104-777777", {"decision": "supersede", "supersedes": [good]})
    assert not driver.check_decision(root, good)[0]
    shutil.rmtree(root)


def test_c7_fail_closed():
    assert driver.check_c7(GOOD)[0]
    assert not driver.check_c7({**GOOD, "load_15min": 14.01})[0]
    assert driver.check_c7({**GOOD, "load_15min": 14.0})[0]
    assert not driver.check_c7({**GOOD, "system_volume_free_gib": 4.99})[0]
    assert not driver.check_c7({**GOOD, "repo_volume_free_gib": 19.9})[0]
    assert not driver.check_c7({**GOOD, "load_15min": None})[0]
    assert not driver.check_c7({"host_kind": "macos", "error": "sysctl failed"})[0]
    assert not driver.check_c7({**GOOD, "host_kind": "linux"})[0]


def test_main_refuses_on_current_readings_or_decision(monkeypatch, tmp_root):
    runs = tmp_root / "runs_should_stay_empty"
    monkeypatch.setattr(driver, "admission_readings", lambda root: dict(GOOD))
    code = driver.main(["--run-id", "RUN-test-refusal", "--admission-decision", "DEC-20260929-f45bf1",
                        "--runs-dir", str(runs)])
    assert code == driver.EXIT_REFUSED_DECISION
    monkeypatch.setattr(driver, "admission_readings", lambda root: {**GOOD, "system_volume_free_gib": 1.0})
    code = driver.main(["--run-id", "RUN-test-refusal", "--admission-decision", "DEC-20260929-f45bf1",
                        "--runs-dir", str(runs)])
    assert code == driver.EXIT_REFUSED_ADMISSION
    assert driver.main(["--run-id", "RUN-x", "--workers", "2", "--runs-dir", str(runs)]) == driver.EXIT_REFUSED_HOST
    assert not runs.exists()


def test_main_requires_snapshot_receipt(monkeypatch, tmp_root):
    runs = tmp_root / "runs_snapshot_refusal"
    monkeypatch.setattr(driver, "admission_readings", lambda root: dict(GOOD))
    monkeypatch.setattr(driver, "check_decision", lambda root, d: (True, "stub"))
    code = driver.main(["--run-id", "RUN-test-snap", "--admission-decision", "DEC-20990101-aaaaaa",
                        "--runs-dir", str(runs)])
    assert code == driver.EXIT_REFUSED_SNAPSHOT
    code = driver.main(["--run-id", "RUN-test-snap", "--admission-decision", "DEC-20990101-aaaaaa",
                        "--runs-dir", str(runs), "--snapshot-receipt", str(tmp_root / "no_such_receipt.json")])
    assert code == driver.EXIT_REFUSED_SNAPSHOT
    assert not runs.exists()


def test_smoke_dry_run_confined(tmp_root):
    assert driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-smoke-x", "--runs-dir", str(tmp_root)]) \
        == driver.EXIT_REFUSED_PLAN
    assert driver.main(["--smoke-dry-run", "--run-id", "DRYRUN-x",
                        "--runs-dir", str(common.HERE / "smoke" / "t")]) == driver.EXIT_REFUSED_EXISTS
    assert not (common.HERE / "smoke" / "t").exists()


def test_smoke_fixture_is_never_frozen():
    fx = driver.smoke_fixture(0)
    assert not common.is_frozen_fixture(fx) and fx["bits"] not in (16, 20)
    for f in common.load_fixtures():
        assert common.is_frozen_fixture(dict(f))


# ------------------------------------------------------------------ plan and protocol v4 binding
def test_trial_plan_is_current_and_deterministic():
    plan_path = common.HERE / "trial-plan-v2.json"
    on_disk = plan_path.read_text()
    rebuilt = json.dumps(make_trial_plan.build_plan(), indent=1, sort_keys=True) + "\n"
    assert on_disk == rebuilt
    plan = json.loads(on_disk)
    ok, bad = driver.check_plan(plan)
    assert ok, bad
    assert plan["protocol_version"] == 4
    for k in ("amendment_sha256", "amendment_v3_sha256", "amendment_v4_sha256", "decision_v3_sha256",
              "decision_v4_sha256"):
        assert len(plan["protocol"][k]) == 64
    assert {(c["bits"], c["seed"]) for c in plan["cells"]} == {(b, s) for b in (16, 20) for s in (21, 22, 23)}
    assert sorted({c["kind"] for c in plan["cells"]}) == sorted(make_trial_plan.CELL_KINDS)
    for k in ("amendment_sha256", "amendment_v4_sha256", "decision_v4_sha256"):
        tampered = json.loads(on_disk)
        tampered["protocol"][k] = "0" * 64
        assert not driver.check_plan(tampered)[0]
    tampered = json.loads(on_disk)
    tampered["protocol_version"] = 3
    assert not driver.check_plan(tampered)[0]


def _fake_governing_root(tmp_root, name):
    root = tmp_root / name
    if root.exists():
        shutil.rmtree(root)
    for rel, _, _ in driver.GOVERNING.values():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(common.REPO_ROOT / rel, root / rel)
    return root


def test_protocol_binding_v4(tmp_root):
    b = driver.protocol_binding(common.REPO_ROOT)
    assert b["protocol_version"] == 4
    assert set(b["records"]) >= {"amendment_v2", "amendment_v3", "amendment_v4", "decision_v3", "decision_v4"}
    assert b["records"]["amendment_v3"]["sha256"] == common.AMENDMENT_V3_SHA256
    assert b["records"]["amendment_v4"]["sha256"] == common.AMENDMENT_V4_SHA256
    assert driver.check_protocol_binding(common.REPO_ROOT, b) == (True, [])
    # decision's amendment_sha256_at_decision differs from the amendment -> refuse
    for key in ("decision_v3", "decision_v4"):
        root = _fake_governing_root(tmp_root, f"gov_{key}")
        p = root / driver.GOVERNING[key][0]
        doc = yaml.safe_load(p.read_text())
        doc["coordinator_decision"]["amendment_sha256_at_decision"] = "0" * 64
        p.write_text(json.dumps(doc))
        ok, bad = driver.check_protocol_binding(root, driver.protocol_binding(root))
        assert not ok and any("amendment_sha256_at_decision" in x for x in bad)
        shutil.rmtree(root)
    # an amendment edited after its decision -> refuse (pin and decision hash both differ)
    root = _fake_governing_root(tmp_root, "gov_amd")
    p = root / driver.GOVERNING["amendment_v4"][0]
    p.write_text(p.read_text() + "# edit\n")
    ok, bad = driver.check_protocol_binding(root, driver.protocol_binding(root))
    assert not ok and len(bad) == 2
    os.remove(p)
    assert not driver.check_protocol_binding(root, driver.protocol_binding(root))[0]
    shutil.rmtree(root)


# ------------------------------------------------------------------ FX-6
def _impl_repo(tmp_root):
    root = _fresh_repo(tmp_root, "fx6_repo")
    impl = root / common.IMPL_REL
    (impl / "tests").mkdir(parents=True)
    (impl / "a.py").write_text("A = 1\n")
    (impl / "tests" / "test_a.py").write_text("def test(): pass\n")
    (impl / "trial-plan-v2.json").write_text("{}\n")
    (impl / "notes.md").write_text("notes\n")
    _commit(root)
    return root, impl


ARCH = "coordination/goals/GOAL-X/batches/BATCH-x/archives"


def _receipt(root, task, files, extra=None, kind="snapshot", task_id=None, commit=True):
    """A dispatcher-style receipt committed at ARCH/<task>/snapshot-receipt.json."""
    path = root / ARCH / task / "snapshot-receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    pins = {str(f.relative_to(root)): common.sha256_file(f) for f in files}
    pins.update(extra or {})
    path.write_text(json.dumps({"task_id": task_id or task, "kind": kind, "path_sha256": pins}))
    if commit:
        _commit(root)
    return path


def test_verify_snapshot(tmp_root):
    root, impl = _impl_repo(tmp_root)
    files = [impl / "a.py", impl / "tests" / "test_a.py", impl / "trial-plan-v2.json"]
    rc = _receipt(root, "TASK-20990101-000001", files)
    ok, info = driver.verify_snapshot(root, rc)
    assert ok and info["checked"] == 3, info
    assert not driver.verify_snapshot(root, None)[0]
    assert not driver.verify_snapshot(root, tmp_root / "missing.json")[0]
    # unpinned test / plan / .py files
    for i, missing in enumerate(files):
        rcx = _receipt(root, f"TASK-20990101-00001{i}", [f for f in files if f != missing])
        ok, info = driver.verify_snapshot(root, rcx)
        assert not ok and info["unpinned"] == [str(missing.relative_to(root))]
    # hash mismatch
    rcm = _receipt(root, "TASK-20990101-000002", files, {str((impl / "a.py").relative_to(root)): "0" * 64})
    ok, info = driver.verify_snapshot(root, rcm)
    assert not ok and info["mismatches"]
    # pinned file missing from the tree
    rcg = _receipt(root, "TASK-20990101-000003", files, {common.IMPL_REL + "/gone.py": "0" * 64})
    ok, info = driver.verify_snapshot(root, rcg)
    assert not ok and info["missing"] == [common.IMPL_REL + "/gone.py"]
    # dirty: modified tracked file, then an untracked non-code file
    (impl / "a.py").write_text("A = 2\n")
    ok, info = driver.verify_snapshot(root, rc)
    assert not ok and info["dirty"]
    _git(root, "checkout", "-q", "--", ".")
    (impl / "scratch.txt").write_text("x\n")
    ok, info = driver.verify_snapshot(root, rc)
    assert not ok and info["dirty"]
    os.remove(impl / "scratch.txt")
    # a new committed .py file that the receipt does not pin
    (impl / "b.py").write_text("B = 1\n")
    _commit(root)
    ok, info = driver.verify_snapshot(root, rc)
    assert not ok and info["unpinned"] == [common.IMPL_REL + "/b.py"]
    shutil.rmtree(root)


def test_snapshot_receipt_must_be_committed_dispatcher_receipt(tmp_root):
    """v4b G-3: kind snapshot, .../archives/TASK-*/snapshot-receipt.json inside
    the repository, tracked, clean, identical to HEAD; copies and hand-written
    receipts refused."""
    root, impl = _impl_repo(tmp_root)
    files = [impl / "a.py", impl / "tests" / "test_a.py", impl / "trial-plan-v2.json"]
    good = _receipt(root, "TASK-20990101-aaaaaa", files)
    assert driver.verify_snapshot(root, good)[0]
    body = good.read_bytes()

    def refused(path, needle):
        ok, info = driver.verify_snapshot(root, path)
        assert not ok and needle in info.get("error", ""), info.get("error")

    # a byte-identical copy outside the repository, and one inside at another path
    outside = tmp_root / "fx6_copy" / "archives" / "TASK-20990101-aaaaaa" / "snapshot-receipt.json"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_bytes(body)
    refused(outside, "outside the repository")
    for rel in ("snapshot-receipt.json", common.IMPL_REL + "/snapshot-receipt.json",
                ARCH + "/TASK-20990101-aaaaaa/receipt.json", ARCH + "/misc/snapshot-receipt.json"):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
        _commit(root)
        refused(p, "is not .../archives/TASK-*/snapshot-receipt.json")
        _git(root, "rm", "-q", rel)
        _commit(root)
    # committed copy under another TASK directory: task_id does not match
    other = root / ARCH / "TASK-20990101-bbbbbb" / "snapshot-receipt.json"
    other.parent.mkdir(parents=True)
    other.write_bytes(body)
    _commit(root)
    refused(other, "!= archive directory")
    # hand-written: wrong or missing kind
    refused(_receipt(root, "TASK-20990101-cccccc", files, kind="ledger"), "is not 'snapshot'")
    refused(_receipt(root, "TASK-20990101-dddddd", files, kind=None), "is not 'snapshot'")
    # untracked, staged-only, modified after commit
    refused(_receipt(root, "TASK-20990101-eeeeee", files, commit=False), "not tracked")
    _git(root, "add", "-A")
    refused(root / ARCH / "TASK-20990101-eeeeee" / "snapshot-receipt.json", "not clean")
    _commit(root)
    assert driver.verify_snapshot(root, root / ARCH / "TASK-20990101-eeeeee" / "snapshot-receipt.json")[0]
    good.write_text(good.read_text().replace('"snapshot"', '"snapshot" '))
    refused(good, "not clean")
    _git(root, "add", "-A")
    refused(good, "not clean")
    _git(root, "reset", "-q", "--hard")
    # symlink to a committed receipt
    link = tmp_root / "fx6_link.json"
    link.unlink(missing_ok=True)
    link.symlink_to(good)
    refused(link, "symlink")
    link.unlink()
    shutil.rmtree(tmp_root / "fx6_copy")
    shutil.rmtree(root)


def test_real_snapshot_receipt_passes_file_checks():
    p = common.REPO_ROOT / ("coordination/goals/GOAL-ICEX-001/batches/BATCH-227e0d/archives/"
                            "TASK-20260929-8428ad/snapshot-receipt.json")
    ok, why = driver.check_receipt_file(common.REPO_ROOT, p, json.loads(p.read_text()))
    assert ok, why


def test_implementation_files_cover_code_tests_and_plan():
    rels = {str(p.relative_to(common.HERE)) for p in driver.implementation_files()}
    assert {"driver.py", "cellrun.py", "synthetic.py", "trial-plan-v2.json", "tests/test_driver.py",
            "tests/conftest.py"} <= rels
    assert all(r.endswith((".py", ".json")) for r in rels)


# ------------------------------------------------------------------ FX-7
def test_inference_block_reads_adapter_exports(monkeypatch):
    for k in list(os.environ):
        if k.startswith("AUTORESEARCH_"):
            monkeypatch.delenv(k)
    b = driver.inference_block()
    assert b["requested_policy"] is None and b["model_verified"] is False and b["resolved_model_id"] == "unverified"
    monkeypatch.setenv("AUTORESEARCH_POLICY", "executor-implementation")
    monkeypatch.setenv("AUTORESEARCH_BACKEND", "cursor")
    monkeypatch.setenv("AUTORESEARCH_FALLBACK_ALLOWED", "1")
    monkeypatch.setenv("AUTORESEARCH_DEGRADED_ALLOWED", "0")
    monkeypatch.setenv("AUTORESEARCH_INDEPENDENT_SESSION", "true")
    monkeypatch.setenv("AUTORESEARCH_RESOLVED_MODEL_ID", "claimed-model")  # not exported by the adapter; ignored
    b = driver.inference_block()
    assert (b["requested_policy"], b["backend"]) == ("executor-implementation", "cursor")
    assert (b["fallback_allowed"], b["degraded_allowed"], b["independent_session"]) == (True, False, True)
    assert b["model_verified"] is False and b["resolved_model_id"] == "unverified"


# ------------------------------------------------------------------ FX-2 / FX-3 (stubbed cells)
PLAN = {"namespace": common.FROZEN_NS,
        "cells": [{"cell_id": "b16-s22:primary", "bits": 16, "seed": 22, "kind": "primary", "params": {}},
                  {"cell_id": "b16-s22:rho", "bits": 16, "seed": 22, "kind": "rho", "params": {}}]}


def _args(tmp_root, run_id):
    return argparse.Namespace(run_id=run_id, admission_decision="DEC-20990101-aaaaaa",
                              plan=str(common.HERE / "trial-plan-v2.json"), repo_root=str(common.REPO_ROOT),
                              runs_dir=str(tmp_root / "fx23_runs"))


def _stub(monkeypatch, cell_status=None, repro=None, fxa=None, seen=None):
    import analysis
    import audit
    monkeypatch.setattr(common, "reproduce_fixtures",
                        repro or (lambda out: {"byte_identical": True, "reproduced_sha256": "x"}))

    def cell(task, cell_dir, env=None):
        if seen is not None:
            seen.append((yaml.safe_load((cell_dir.parent.parent / "manifest.yaml").read_text())["run"]["status"],
                         env.get(driver.ADMISSION_ENV) if env else None))
        cell_dir.mkdir(parents=True)
        st = (cell_status or {}).get(task["kind"], "ok")
        if st == "signal":
            os.kill(os.getpid(), signal.SIGTERM)
        out = {"task": task, "status": st, "result": {"kind": task["kind"], "stub": True},
               "peak_rss_bytes": 1, "seconds": 0.0}
        (cell_dir / "result.json").write_text(json.dumps(out))
        return out
    monkeypatch.setattr(driver, "run_cell_process", cell)
    monkeypatch.setattr(audit, "audit_run", lambda receipts: {"accepted": True})
    monkeypatch.setattr(analysis, "analyse", lambda prim, **kw: {"verdict": "inconclusive", "stub": True})
    monkeypatch.setattr(analysis, "fxa_report", fxa or (lambda prim: [{"fixture_id": "b16-s22", "x": 1}]))


def _load(run_dir):
    return yaml.safe_load((run_dir / "manifest.yaml").read_text())


def _execute(tmp_root, run_id):
    return driver.execute(_args(tmp_root, run_id), PLAN, dict(GOOD), "stub-path", None, "cmd",
                          driver.protocol_binding(common.REPO_ROOT), {"receipt": "r", "verified": True})


def test_run_record_schema_and_completed(monkeypatch, tmp_root):
    seen = []
    _stub(monkeypatch, seen=seen)
    run_dir = tmp_root / "fx23_runs" / "RUN-test-ok"
    shutil.rmtree(run_dir, ignore_errors=True)
    assert _execute(tmp_root, "RUN-test-ok") == 0
    assert seen == [("running", "DEC-20990101-aaaaaa")] * 2
    m = _load(run_dir)
    run = m["run"]
    for k in ("id", "experiment_id", "status", "code", "environment", "inputs", "timing", "resources", "result",
              "inference"):
        assert k in run, k
    assert run["id"] == "RUN-test-ok" and run["experiment_id"] == "EXP-ICEX-aaccfc"
    assert run["status"] == "completed_valid" and run["result"]["valid"] is True
    assert run["protocol_version"] == 4
    recs = run["inputs"]["protocol"]["records"]
    for k in ("amendment_v2", "amendment_v3", "amendment_v4", "decision_v3", "decision_v4"):
        assert len(recs[k]["sha256"]) == 64
    assert run["inputs"]["admission_decision_pinning"] and run["inputs"]["snapshot_verification"]["verified"]
    assert {"commit", "dirty", "command"} <= set(run["code"])
    assert run["result"]["certificate"]["kind"] == "discrete_log"
    for f in ("command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json", "metrics.json",
              "fxa_nonverdict.json"):
        assert (run_dir / f).exists(), f
    raw = json.loads((run_dir / "raw-result.json").read_text())
    assert len(raw["cells"]) == 2 and all(c["result_sha256"] for c in raw["cells"])
    shutil.rmtree(run_dir)


@pytest.mark.parametrize("case,status,cls", [
    ("defect", "invalid", "procedure_defect"),
    ("infra", "failed_infrastructure", "cell_implementation_error"),
    ("repro_exc", "failed_infrastructure", "exception"),
    ("repro_mismatch", "invalid", "procedure_defect"),
    ("signal", "failed_infrastructure", "signal"),
])
def test_failures_are_recorded(monkeypatch, tmp_root, case, status, cls):
    kw = {}
    if case == "defect":
        kw["cell_status"] = {"primary": "procedure_defect"}
    elif case == "infra":
        kw["cell_status"] = {"rho": "implementation_error"}
    elif case == "signal":
        kw["cell_status"] = {"primary": "signal"}
    elif case == "repro_exc":
        def boom(out):
            raise subprocess.TimeoutExpired("sage", 1)
        kw["repro"] = boom
    elif case == "repro_mismatch":
        kw["repro"] = lambda out: {"byte_identical": False}
    _stub(monkeypatch, **kw)
    run_id = f"RUN-test-{case}"
    run_dir = tmp_root / "fx23_runs" / run_id
    shutil.rmtree(run_dir, ignore_errors=True)
    code = _execute(tmp_root, run_id)
    assert code in (driver.EXIT_PROCEDURE_DEFECT, driver.EXIT_INFRASTRUCTURE)
    run = _load(run_dir)["run"]
    assert run["status"] == status and run["failure_class"] == cls, run["failure_class"]
    assert run["timing"]["finished_at"] and run["result"]["valid"] is False and run["result"]["invalid_reason"]
    assert (run_dir / "raw-result.json").exists() and not (run_dir / "metrics.json").exists()
    shutil.rmtree(run_dir)


@pytest.mark.parametrize("how", ["exception", "signal"])
def test_stub_manifest_precedes_environment_probe(monkeypatch, tmp_root, how):
    """v4b G-4: a stub (status running) exists before the environment / Sage
    probe; a failure there still leaves failed_infrastructure + raw-result.json."""
    _stub(monkeypatch)
    run_id = f"RUN-test-stub-{how}"
    run_dir = tmp_root / "fx23_runs" / run_id
    shutil.rmtree(run_dir, ignore_errors=True)
    seen = {}

    def probe():
        seen["run"] = _load(run_dir)["run"]
        seen["raw"] = json.loads((run_dir / "raw-result.json").read_text())
        if how == "signal":
            os.kill(os.getpid(), signal.SIGTERM)
        raise OSError("sage probe failed")
    monkeypatch.setattr(driver, "environment_info", probe)
    assert _execute(tmp_root, run_id) == driver.EXIT_INFRASTRUCTURE
    s = seen["run"]
    assert s["status"] == "running" and s["stub"] is True and s["timing"]["finished_at"] is None
    assert s["inputs"]["driver_pid"] == os.getpid() and len(s["inputs"]["run_token_sha256"]) == 64
    assert seen["raw"]["status"] == "running"
    m = _load(run_dir)
    run = m["run"]
    assert run["status"] == "failed_infrastructure" and run["stub"] is True
    assert run["failure_class"] == how and run["timing"]["finished_at"] and run["result"]["valid"] is False
    assert run["failure_reason"] and m["driver"]["traceback"]
    raw = json.loads((run_dir / "raw-result.json").read_text())
    assert raw["status"] == "failed_infrastructure" and raw["cells"] == []
    assert not (run_dir / "environment.json").exists()
    shutil.rmtree(run_dir)


def test_manifest_binds_driver_pid_and_run_token(monkeypatch, tmp_root):
    """v4b G-2: the full record carries this driver's pid and the sha256 of
    the per-run token that only the cell environment holds."""
    _stub(monkeypatch)
    envs = []

    def cell(task, cell_dir, env=None):
        envs.append(dict(env))
        m = _load(cell_dir.parent.parent)["run"]
        envs[-1]["_manifest"] = m
        cell_dir.mkdir(parents=True)
        out = {"task": task, "status": "ok", "result": {"kind": task["kind"]}, "peak_rss_bytes": 1, "seconds": 0.0}
        (cell_dir / "result.json").write_text(json.dumps(out))
        return out
    monkeypatch.setattr(driver, "run_cell_process", cell)
    monkeypatch.setenv(driver.RUN_TOKEN_ENV, "inherited-must-not-leak")
    run_dir = tmp_root / "fx23_runs" / "RUN-test-token"
    shutil.rmtree(run_dir, ignore_errors=True)
    assert _execute(tmp_root, "RUN-test-token") == 0
    tokens = {e[driver.RUN_TOKEN_ENV] for e in envs}
    assert len(tokens) == 1
    token = tokens.pop()
    assert token != "inherited-must-not-leak" and len(token) == 64
    for e in envs:
        inp = e["_manifest"]["inputs"]
        assert not e["_manifest"].get("stub")
        assert inp["run_token_sha256"] == driver.token_sha256(token) and inp["driver_pid"] == os.getpid()
    assert token not in (run_dir / "manifest.yaml").read_text()
    shutil.rmtree(run_dir)
    # a second run draws a fresh token
    envs.clear()
    assert _execute(tmp_root, "RUN-test-token") == 0
    assert envs[0][driver.RUN_TOKEN_ENV] != token
    shutil.rmtree(run_dir)


def test_main_refuses_runs_dir_other_than_experiment_runs(monkeypatch, tmp_root):
    """v4b G-2: a scientific run is written only under runs/RUN-*."""
    runs = tmp_root / "runs_elsewhere"
    monkeypatch.setattr(driver, "admission_readings", lambda root: dict(GOOD))
    monkeypatch.setattr(driver, "check_decision", lambda root, d: (True, "stub"))
    monkeypatch.setattr(driver, "verify_snapshot", lambda root, r: (True, {"verified": True}))
    monkeypatch.setattr(driver, "execute", lambda *a, **k: pytest.fail("execute must not be reached"))
    code = driver.main(["--run-id", "RUN-test-runsdir", "--admission-decision", "DEC-20990101-aaaaaa",
                        "--runs-dir", str(runs), "--snapshot-receipt", "x"])
    assert code == driver.EXIT_REFUSED_RUNS_DIR and not runs.exists()


def test_fxa_defect_after_metrics_does_not_touch_metrics(monkeypatch, tmp_root):
    import pipeline

    def bad_fxa(prim):
        raise pipeline.ProcedureDefect("FX-A: attempt 0 rj_ops > logged pt_ops")
    _stub(monkeypatch, fxa=bad_fxa)
    run_dir = tmp_root / "fx23_runs" / "RUN-test-fxa"
    shutil.rmtree(run_dir, ignore_errors=True)
    assert _execute(tmp_root, "RUN-test-fxa") == driver.EXIT_PROCEDURE_DEFECT
    metrics = json.loads((run_dir / "metrics.json").read_text())
    assert metrics == {"verdict": "inconclusive", "stub": True}
    run = _load(run_dir)["run"]
    assert run["status"] == "invalid" and run["failure_class"] == "procedure_defect_fxa"
    assert run["result"]["metrics_sha256"] == common.sha256_file(run_dir / "metrics.json")
    assert "error" in json.loads((run_dir / "fxa_nonverdict.json").read_text())
    shutil.rmtree(run_dir)
