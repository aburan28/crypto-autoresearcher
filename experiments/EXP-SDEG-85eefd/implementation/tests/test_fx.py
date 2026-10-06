"""AMD-20260928-d3ed9e FX-1..FX-5. Never runs a protocol-labelled query."""

import json
from pathlib import Path

import pytest

import backends
import cellrun
import decks
import driver
import fixtures
import hostinfo
import labels
import make_trial_plan
import semaev

HERE = Path(__file__).resolve().parent.parent
REPO = HERE.parent.parent.parent


def _dec(tmp_path, dec_id, body):
    d = tmp_path / "ledger" / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{dec_id}.yaml").write_text(body)


ADMITTED = ("coordinator_decision:\n  id: {id}\n  target_ids: [{t}]\n"
            "  execution_admission:\n    currently_admitted: {a}\n")


# ---------------------------------------------------------------- FX-1
@pytest.mark.parametrize("dec_id", ["DEC-20260928-6b03c5", "DEC-20260928-48a648"])
def test_fx1_real_non_admitting_decisions_refused(dec_id):
    assert (REPO / "ledger" / "decisions" / f"{dec_id}.yaml").exists()
    ok, why = driver.check_decision(REPO, dec_id)
    assert not ok, why


def test_fx1_future_admission_decision_absent_today():
    ok, why = driver.check_decision(REPO, "DEC-20260928-ad6451")
    assert not ok and "does not exist" in why


def test_fx1_only_explicit_true_for_this_experiment(tmp_path):
    i = "DEC-20260928-aaaaaa"
    _dec(tmp_path, i, ADMITTED.format(id=i, t="EXP-SDEG-85eefd", a="true"))
    assert driver.check_decision(tmp_path, i)[0]
    for body in (ADMITTED.format(id=i, t="EXP-SDEG-85eefd", a="false"),
                 ADMITTED.format(id=i, t="EXP-SDEG-85eefd", a="'true'"),
                 ADMITTED.format(id=i, t="EXP-OTHER-000000", a="true"),
                 ADMITTED.format(id="DEC-20260928-bbbbbb", t="EXP-SDEG-85eefd", a="true"),
                 "coordinator_decision:\n  id: %s\n  target_ids: [EXP-SDEG-85eefd]\n" % i,
                 "note: EXP-SDEG-85eefd currently_admitted: true\n",
                 ": : not yaml ["):
        _dec(tmp_path, i, body)
        assert not driver.check_decision(tmp_path, i)[0], body


def test_fx1_charged_and_full_refuse_today(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "admission_readings", lambda root, vol=None: {
        "host_kind": "macos", "load_15min": 1.0, "system_volume_free_gib": 50, "repo_volume_free_gib": 50})
    runs = tmp_path / "runs"
    for mode in ("charged", "full", "sage", "merge"):
        for dec in ("DEC-20260928-6b03c5", "DEC-20260928-48a648", "DEC-20260928-ad6451"):
            code = driver.main(["--mode", mode, "--run-id", "RUN-fx1", "--admission-decision", dec,
                                "--repo-root", str(REPO), "--runs-dir", str(runs)])
            assert code == driver.EXIT_REFUSED_DECISION, (mode, dec)
    assert not runs.exists()


# ---------------------------------------------------------------- FX-2
@pytest.mark.parametrize("content", [None, "", "garbage", "max", "0 100000", "100000 0", "abc 100000"])
def test_fx2_linux_cpu_max_fails_closed(monkeypatch, tmp_path, content):
    cpu = tmp_path / "cpu.max"
    if content is not None:
        cpu.write_text(content)
    load = tmp_path / "loadavg"
    load.write_text("0.10 0.20 0.30 1/100 1\n")
    monkeypatch.setattr(hostinfo, "host_kind", lambda: "linux")
    monkeypatch.setattr(hostinfo, "CPU_MAX", cpu)
    monkeypatch.setattr(hostinfo, "LOADAVG", load)
    r = hostinfo.admission_readings(tmp_path, tmp_path)
    ok, reasons = hostinfo.check_admission(r)
    assert not ok and any("fail closed" in x for x in reasons), (content, r)


def test_fx2_linux_valid_cpu_max_admits(monkeypatch, tmp_path):
    (tmp_path / "cpu.max").write_text("2380000 100000\n")
    (tmp_path / "loadavg").write_text("0.10 0.20 0.30 1/100 1\n")
    monkeypatch.setattr(hostinfo, "host_kind", lambda: "linux")
    monkeypatch.setattr(hostinfo, "CPU_MAX", tmp_path / "cpu.max")
    monkeypatch.setattr(hostinfo, "LOADAVG", tmp_path / "loadavg")
    monkeypatch.setattr(hostinfo, "LINUX_RUN_FREE_MIN_GIB", 0.0)
    monkeypatch.setattr(hostinfo, "LINUX_ROOT_FREE_MIN_GIB", 0.0)
    r = hostinfo.admission_readings(tmp_path, tmp_path)
    assert r["load_limit"] == 23 and hostinfo.check_admission(r)[0]


# ---------------------------------------------------------------- FX-3
def test_fx3_hit_triple_mismatch_is_defect_and_stops(monkeypatch):
    fx = fixtures.fixture(8, 1)
    sem = semaev.SemaevFp(fx["p"], fx["a"], fx["b"], semaev.load_terms())
    deck = decks.build_all(fx, labels.SMOKE_NS)["subgroup_x"]
    real = backends.b1_query

    def tampered(*a, **k):
        r = real(*a, **k)
        if r["hits"]:  # keep the decision, drop one hit triple
            r["hits"] = r["hits"][:-1] if len(r["hits"]) > 1 else r["hits"]
            r["hit_triples"] = r["hit_triples"][:-1] if len(r["hit_triples"]) > 1 else []
            r["member"] = bool(r["hit_triples"]) or True
        return r

    monkeypatch.setattr(backends, "b1_query", tampered)
    cell = cellrun.run_cell(fx, deck, sem, labels.SMOKE_NS, 3, 0, stop_on_defect=True, log=lambda s: None,
                            b2_split=False)
    assert any("hit-triple set mismatch" in d for d in cell["defects"]), cell["defects"]
    assert cell.get("stopped_on_defect") and len(cell["queries"]) < 3


# ---------------------------------------------------------------- FX-4
def test_fx4_fresh_process_per_task_and_per_task_peak(tmp_path):
    specs = [{"kind": "rho", "task_id": f"rho-{i}", "L": 8, "seed": s, "ns": labels.SMOKE_NS, "n_targets": 1,
              "out": str(tmp_path / f"r{i}.json")} for i, s in enumerate((1, 2, 3))]
    for workers in (1, 2):
        res = {}
        driver._schedule(specs, workers, lambda s, r: res.__setitem__(s["task_id"], r), lambda: False)
        pids = [r["pid"] for r in res.values()]
        assert len(set(pids)) == len(pids) == 3, (workers, pids)
        assert all(r["peak_rss_bytes"] > 0 for r in res.values())


# ---------------------------------------------------------------- FX-5
KEYS = ("requested_policy", "resolved_model_id", "reasoning_effort", "fallback_used", "degraded_requirements")


def test_fx5_unset_env_gives_null_unverified(monkeypatch):
    import os
    for k in list(os.environ):
        if k.startswith("AUTORESEARCH_"):
            monkeypatch.delenv(k)
    b = driver.inference_block()
    assert b["requested_policy"] is None and b["resolved_model_id"] == "unverified"
    assert b["reasoning_effort"] is None and b["fallback_used"] is None
    assert b["degraded_requirements"] is None and b["model_verified"] is False


def test_fx5_env_values_recorded_verbatim(monkeypatch):
    monkeypatch.setenv("AUTORESEARCH_POLICY", "executor-implementation")
    monkeypatch.setenv("AUTORESEARCH_RESOLVED_MODEL_ID", "model-x")
    monkeypatch.setenv("AUTORESEARCH_REASONING_EFFORT", "medium")
    monkeypatch.setenv("AUTORESEARCH_FALLBACK_USED", "true")
    monkeypatch.setenv("AUTORESEARCH_DEGRADED_REQUIREMENTS", '["reasoning_effort"]')
    b = driver.inference_block()
    assert [b[k] for k in KEYS] == ["executor-implementation", "model-x", "medium", True, ["reasoning_effort"]]


def test_fx5_part_manifest_carries_inference(monkeypatch, tmp_path):
    for k in ("AUTORESEARCH_POLICY", "AUTORESEARCH_RESOLVED_MODEL_ID", "AUTORESEARCH_MODEL_ID"):
        monkeypatch.delenv(k, raising=False)

    class A:
        run_id, admission_decision, repo_root, source_commit = "DRYRUN-x", None, str(REPO), None
        plan = str(HERE / "trial-plan-v2.json")
    import sys
    out, err = sys.stdout, sys.stderr
    try:
        part = driver.Part(A, tmp_path / "p", "charged", {}, "x", json.loads(Path(A.plan).read_text()),
                           None, with_sage=False)
        part.finish("completed", "test")
    finally:
        sys.stdout, sys.stderr = out, err
    import yaml
    m = yaml.safe_load((tmp_path / "p" / "manifest.yaml").read_text())
    for k in KEYS:
        assert k in m and k in m["inference"]
    assert m["resolved_model_id"] == "unverified" and m["protocol_version"] == 4


def test_protocol_version_4_in_plan_and_driver():
    plan = make_trial_plan.build()
    assert driver.PROTOCOL_VERSION == 4 and plan["protocol_version"] == 4
    ok, bad = driver.check_plan(plan)
    assert ok, bad
    assert not driver.check_plan(dict(plan, protocol_version=3))[0]
