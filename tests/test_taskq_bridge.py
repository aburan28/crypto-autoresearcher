"""Offline tests for harness/taskq_bridge.py (no Redis, no taskq package).

Results are fabricated to the vendored taskq.task-result/v1 schema and their
artifacts are real files whose sha256 the bridge must check before use.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest
import yaml

from harness import runner
from harness import taskq_bridge as bridge
from harness.toycurve import EllipticCurve

EXP = "EXP-TEST-0a1b2c"
RUN = "RUN-TEST-0a1b2c-01"
COMMIT = "0123456789abcdef0123456789abcdef01234567"

# y^2 = x^3 + 2x + 3 over F_97.
CURVE = {"p": 97, "a": 2, "b": 3}
E = EllipticCurve(97, 2, 3)
P = next((x, y) for x in range(97) for y in range(1, 97) if E.is_on_curve((x, y)))
K = 13
Q = E.mul(K, P)


def _dl_cert(k: int = K, *, wire_top_level_curve: bool = True) -> dict:
    """A discrete_log certificate in the shared taskq wire form."""
    st = {"P": list(P), "Q": list(Q), "k": k}
    if wire_top_level_curve:
        return {"kind": "discrete_log", "curve": {"field": "prime", **CURVE},
                "statement": st}
    return {"kind": "discrete_log", "statement": {**st, "curve": dict(CURVE)}}


def _spec(**kw) -> dict:
    return bridge.build_spec(EXP, RUN, ["python3", "harness/run_x.py", "--seed", "7"],
                             COMMIT, **kw)


def _run(index: int = 0, *, warmup: bool = False, exit_code: int = 0,
         timed_out: bool = False, metrics: dict | None = None, **extra) -> dict:
    return {"index": index, "warmup": warmup, "exit_code": exit_code, "signal": None,
            "wall_seconds": 1.5, "user_cpu_seconds": 1.2, "sys_cpu_seconds": 0.1,
            "max_rss_kb": 2048, "timed_out": timed_out, "stopped": None,
            "metrics": metrics if metrics is not None else {"steps": 42}, **extra}


class Store:
    """Artifact files on disk, standing in for the worker's artifact volume."""

    def __init__(self, root: Path):
        self.root = root

    def artifact(self, path: str, data: bytes) -> dict:
        target = self.root / "T-x" / "attempt-1" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return {"path": path, "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data), "uri": str(target)}


def _result(spec: dict, store: Store, *, status: str = "succeeded",
            runs: list[dict] | None = None, certs: dict[str, dict] | None = None,
            resolved: bool = True, error: str | None = None, **extra) -> dict:
    arts = [store.artifact("_taskq_logs/stdout.log", b"solved\n"),
            store.artifact("_taskq_logs/stderr.log", b"")]
    for path, cert in (certs or {}).items():
        arts.append(store.artifact(path, json.dumps(cert).encode()))
    return {
        "schema": "taskq.task-result/v1", "task_id": "T-x", "attempt": 1, "fence": 1,
        "spec_sha256": bridge.spec_sha256(spec), "status": status,
        "outcome_class": "completed" if status in ("succeeded", "failed") else "not_completed",
        "error": error,
        "worker": {"id": "w-1", "hostname": "pod-1", "labels": {"pool": "cpu"}},
        "environment": {"platform": "Linux-6.1-x86_64", "machine": "x86_64",
                        "python": "3.12.3", "cpu_model": "test"},
        "source": {"repo": "crypto-autoresearcher", "commit": COMMIT,
                   "resolved_commit": COMMIT if resolved else None},
        "timing": {"queued_at": 1_790_000_000.0, "started_at": 1_790_000_010.0,
                   "finished_at": 1_790_000_012.0, "setup_wall_seconds": 0.0},
        "setup": [], "runs": [_run()] if runs is None else runs,
        "summary": None, "artifacts": arts, "labels": spec["labels"], **extra,
    }


def _load(run_dir: str) -> tuple[dict, dict]:
    with open(os.path.join(run_dir, "manifest.yaml")) as fh:
        manifest = yaml.safe_load(fh)["run"]
    with open(os.path.join(run_dir, "raw-result.json")) as fh:
        raw = json.load(fh)
    return manifest, raw


@pytest.fixture
def env(tmp_path):
    exp_dir = tmp_path / "experiments" / EXP
    exp_dir.mkdir(parents=True)
    return exp_dir, Store(tmp_path / "artifacts")


# -- spec --------------------------------------------------------------------

def test_spec_shape_and_idempotency_key():
    spec = _spec()
    assert spec["idempotency_key"] == f"{EXP}/{RUN}"
    assert spec["source"] == {"repo": "crypto-autoresearcher", "commit": COMMIT}
    assert spec["labels"] == {"experiment": EXP, "run": RUN, "submitted_by": "executor"}
    assert spec["kind"] == "command" and "benchmark" not in spec
    bench = _spec(repetitions=5, warmups=2, queue="cpu-exclusive")
    assert bench["kind"] == "benchmark"
    assert bench["benchmark"] == {"warmups": 2, "repetitions": 5}
    # The same run always yields the same key, so a re-dispatch deduplicates.
    assert _spec()["idempotency_key"] == spec["idempotency_key"]


def test_spec_validates_against_vendored_schema():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(_spec(repetitions=3, setup=[["make"]], env={"A": "1"}),
                        bridge.SPEC_SCHEMA)


@pytest.mark.parametrize("bad", [
    dict(commit="main"), dict(commit="abc123"), dict(exp_id="EXP"), dict(run_id="R-1"),
])
def test_spec_refuses_bad_identity(bad):
    args = dict(exp_id=EXP, run_id=RUN, argv=["true"], commit=COMMIT) | bad
    with pytest.raises(bridge.BridgeError):
        bridge.build_spec(**args)


def test_spec_labels_cannot_override_provenance():
    with pytest.raises(bridge.BridgeError):
        _spec(labels={"experiment": "EXP-OTHER-000000"})
    assert _spec(labels={"goal": "GOAL-X-1"})["labels"]["goal"] == "GOAL-X-1"


def test_subset_validator_matches_schema_on_bad_spec(monkeypatch):
    # Without jsonschema the subset validator must still refuse a branch name.
    monkeypatch.setitem(sys.modules, "jsonschema", None)
    spec = _spec()
    spec["source"]["commit"] = "main"
    with pytest.raises(bridge.BridgeError, match="source/commit"):
        bridge.validate_spec(spec)
    spec = _spec()
    spec["surprise"] = 1
    with pytest.raises(bridge.BridgeError, match="unexpected property"):
        bridge.validate_spec(spec)


def test_submit_without_taskq_is_a_clear_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "taskq", None)
    monkeypatch.setitem(sys.modules, "taskq.config", None)
    with pytest.raises(bridge.TaskqUnavailable):
        bridge.submit(_spec())


def test_submit_and_wait_use_the_given_store():
    class FakeStore:
        def __init__(self):
            self.states = iter(["queued", "running", "succeeded"])

        def submit(self, spec):
            return {"task_id": "T-1", "spec_sha256": bridge.spec_sha256(spec),
                    "deduplicated": False}

        def wait(self, task_id, timeout):
            return {"task_id": task_id, "state": next(self.states)}

    fs = FakeStore()
    assert bridge.submit(_spec(), store=fs)["task_id"] == "T-1"
    assert bridge.wait("T-1", store=fs, chunk_seconds=0)["state"] == "succeeded"


# -- results -> run packages -------------------------------------------------

def test_fixture_results_validate_against_vendored_schema(env):
    jsonschema = pytest.importorskip("jsonschema")
    _, store = env
    spec = _spec()
    for status in ("succeeded", "failed", "timeout", "cancelled", "infra_error"):
        jsonschema.validate(_result(spec, store, status=status), bridge.RESULT_SCHEMA)


def test_succeeded_with_verified_certificate(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store, certs={"certificate.json": _dl_cert()})
    run_dir = bridge.write_run_package(result, spec, {"task_id": "T-x"}, str(exp_dir),
                                       RUN, inputs={"curve_id": "TOY-P7-x", "seed": 7,
                                                    "parameters": {"field_bits": 7}})
    assert sorted(os.listdir(run_dir)) == sorted(
        ["manifest.yaml", "command.txt", "environment.json", "stdout.log",
         "stderr.log", "raw-result.json"])
    m, raw = _load(run_dir)
    assert m["id"] == RUN and m["experiment_id"] == EXP
    assert m["status"] == "completed_valid"
    assert m["result"]["valid"] is True and m["result"]["invalid_reason"] is None
    assert m["result"]["certificate"]["kind"] == "discrete_log"
    assert m["result"]["certificate"]["verified"] is True
    assert m["result"]["certificate"]["verifier"] == "independent-recompute"
    assert m["result"]["metrics"] == {"steps": 42}
    assert m["code"]["commit"] == COMMIT and m["code"]["dirty"] is False
    # timing is the worker's measurement, not a caller bracket
    assert m["timing"]["wall_seconds"] == 1.5
    assert m["timing"]["timing_source"] == "taskq-worker"
    assert m["resources"] == {"peak_rss_bytes": 2048 * 1024, "cpu_seconds": 1.3}
    tq = m["taskq"]
    assert (tq["task_id"], tq["attempt"], tq["fence"]) == ("T-x", 1, 1)
    assert tq["spec_sha256"] == bridge.spec_sha256(spec)
    assert tq["worker"]["id"] == "w-1" and tq["queue"] == "cpu"
    assert raw["certificate"]["verified"] is True
    assert raw["certificate"]["verifier_commit"] == runner.git_state()[0]
    assert Path(run_dir, "stdout.log").read_text() == "solved\n"
    cmd = Path(run_dir, "command.txt").read_text()
    assert COMMIT in cmd and cmd.rstrip().endswith("python3 harness/run_x.py --seed 7")
    envj = json.loads(Path(run_dir, "environment.json").read_text())
    assert envj["worker"]["id"] == "w-1" and envj["cpu_model"] == "test"


def test_statement_nested_curve_also_verifies(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store, certs={
        "certificate.json": _dl_cert(wire_top_level_curve=False)})
    m, _ = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    assert m["status"] == "completed_valid"


def test_refuted_certificate_is_invalid_measurement(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store, certs={"certificate.json": _dl_cert(k=K + 1)})
    m, raw = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    # exactly runner.write_run's rule
    assert m["status"] == "completed_invalid"
    assert m["result"]["valid"] is False
    assert m["result"]["invalid_reason"] == "certificate failed independent verification"
    assert m["result"]["certificate"]["verified"] is False
    assert raw["certificate"]["verified"] is False


def test_worker_verification_is_advisory(env):
    exp_dir, store = env
    spec = _spec()
    # The worker (wrongly) says verified; this repo's verifier refutes. The
    # repo's verdict decides and the disagreement is recorded.
    result = _result(spec, store, certs={"certificate.json": _dl_cert(k=K + 1)},
                     runs=[_run(verification={"status": "verified",
                                              "verifier": "taskq.verify"})],
                     verification={"status": "verified", "counts": {"verified": 1}})
    m, raw = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    assert m["status"] == "completed_invalid"
    wv = m["taskq"]["worker_verification"]
    assert wv["rollup"]["status"] == "verified"
    assert wv["disagrees_with_repo_verifier"] == [0]
    assert raw["raw"]["certificates"][0]["worker_verification_disagrees"] is True


@pytest.mark.parametrize("status", ["timeout", "cancelled", "infra_error"])
def test_not_completed_is_never_negative_evidence(env, status):
    exp_dir, store = env
    spec = _spec()
    runs = [] if status == "infra_error" else [_run(exit_code=None, timed_out=True)]
    result = _result(spec, store, status=status, runs=runs,
                     resolved=status != "infra_error", error=f"{status} happened")
    if status == "infra_error":
        result["artifacts"] = []
    m, _ = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    assert m["status"] == "failed_infrastructure"
    assert m["status"] not in ("completed_valid", "negative_observation")
    assert m["result"]["valid"] is False
    assert "rule 3" in m["result"]["invalid_reason"]
    assert status in m["result"]["invalid_reason"]
    assert m["taskq"]["outcome_class"] == "not_completed"
    if status == "infra_error":
        assert m["code"]["dirty"] is None
        assert m["timing"]["wall_seconds"] is None


def test_failed_run_is_not_a_result(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store, status="failed", runs=[_run(exit_code=1)],
                     error="run 0 exited 1 (signal None)")
    m, _ = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    assert m["status"] == "failed" and m["result"]["valid"] is False
    assert "rule 3" in m["result"]["invalid_reason"]


def test_sha256_mismatch_refuses_before_writing(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store, certs={"certificate.json": _dl_cert()})
    # Tamper with the stored certificate after the worker hashed it.
    cert_entry = next(a for a in result["artifacts"] if a["path"] == "certificate.json")
    Path(cert_entry["uri"]).write_text(json.dumps(_dl_cert(k=K + 1)))
    with pytest.raises(bridge.ArtifactIntegrityError, match="sha256"):
        bridge.write_run_package(result, spec, None, str(exp_dir), RUN)
    assert not (exp_dir / "runs" / RUN).exists()


def test_log_hash_mismatch_refuses(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store)
    result["artifacts"][0]["sha256"] = "0" * 64
    with pytest.raises(bridge.ArtifactIntegrityError):
        bridge.write_run_package(result, spec, None, str(exp_dir), RUN)
    assert not (exp_dir / "runs" / RUN).exists()


def test_existing_run_dir_refuses(env):
    exp_dir, store = env
    spec = _spec()
    (exp_dir / "runs" / RUN).mkdir(parents=True)
    (exp_dir / "runs" / RUN / "manifest.yaml").write_text("run: {}\n")
    with pytest.raises(FileExistsError, match="immutable"):
        bridge.write_run_package(_result(spec, store), spec, None, str(exp_dir), RUN)
    assert (exp_dir / "runs" / RUN / "manifest.yaml").read_text() == "run: {}\n"


def test_second_package_of_same_run_refuses(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store)
    bridge.write_run_package(result, spec, None, str(exp_dir), RUN)
    with pytest.raises(FileExistsError):
        bridge.write_run_package(result, spec, None, str(exp_dir), RUN)


@pytest.mark.parametrize("mutate, match", [
    (lambda r, s: r.update(spec_sha256="f" * 64), "spec sha256"),
    (lambda r, s: s["labels"].update(run="RUN-TEST-other"), "labels"),
    (lambda r, s: r.update(outcome_class="not_completed"), "inconsistent"),
    (lambda r, s: r["source"].update(resolved_commit="f" * 40), "resolved"),
])
def test_binding_refusals(env, mutate, match):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store)
    mutate(result, spec)
    if match == "labels":  # keep the digest consistent so the label check fires
        result["spec_sha256"] = bridge.spec_sha256(spec)
    with pytest.raises(bridge.BridgeError, match=match):
        bridge.write_run_package(result, spec, None, str(exp_dir), RUN)
    assert not (exp_dir / "runs" / RUN).exists()


def test_benchmark_repetitions_certificates_per_run(env):
    exp_dir, store = env
    spec = _spec(repetitions=2, warmups=1)
    runs = [_run(0, warmup=True), _run(1), _run(2)]
    certs = {"run-1/certificate.json": _dl_cert(), "run-2/certificate.json": _dl_cert()}
    result = _result(spec, store, runs=runs, certs=certs,
                     summary={"n": 2, "wall_seconds": {"median": 1.5}})
    m, raw = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    assert m["status"] == "completed_valid"
    assert m["timing"]["wall_seconds"] == 3.0  # warmup excluded
    assert m["result"]["metrics"]["per_run"] == [{"steps": 42}, {"steps": 42}]
    assert len(raw["certificate"]["per_run"]) == 2
    # one bad repetition invalidates the package
    exp2 = exp_dir.parent / "EXP-TEST-0a1b2d"
    exp2.mkdir()
    spec2 = bridge.build_spec("EXP-TEST-0a1b2d", RUN, ["true"], COMMIT,
                              repetitions=2, warmups=1)
    certs["run-2/certificate.json"] = _dl_cert(k=K + 1)
    result2 = _result(spec2, store, runs=runs, certs=certs)
    m2, _ = _load(bridge.write_run_package(result2, spec2, None, str(exp2), RUN))
    assert m2["status"] == "completed_invalid"
    assert m2["result"]["certificate"]["failing_checks"] == ["run-2"]


def test_no_certificate_means_no_claim(env):
    exp_dir, store = env
    spec = _spec()
    m, raw = _load(bridge.write_run_package(_result(spec, store), spec, None,
                                            str(exp_dir), RUN))
    assert m["status"] == "completed_valid"
    assert m["result"]["certificate"] == {"kind": "none", "verified": True,
                                          "verifier": "no-claim"}


def test_unverifiable_certificate_is_invalid_not_a_crash(env):
    exp_dir, store = env
    spec = _spec()
    binary = {"kind": "discrete_log",
              "curve": {"field": "binary", "m": 7, "modulus": [7, 1, 0], "a": 1, "b": 1},
              "statement": {"P": [1, 2], "Q": [3, 4], "k": 5}}
    m, raw = _load(bridge.write_run_package(
        _result(spec, store, certs={"certificate.json": binary}), spec, None,
        str(exp_dir), RUN))
    assert m["status"] == "completed_invalid"
    assert raw["certificate"]["verifier"].startswith("error:")


def test_package_passes_repo_run_validator(env):
    """The written manifest satisfies tools/validate_ledger.check_run."""
    from tools import validate_ledger as vl
    exp_dir, store = env
    spec = _spec()
    run_dir = bridge.write_run_package(
        _result(spec, store, certs={"certificate.json": _dl_cert()}), spec, None,
        str(exp_dir), RUN)
    ctx = vl.Ctx(set())
    vl.check_run(os.path.join(run_dir, "manifest.yaml"), ctx)
    assert ctx.errors == []
    assert RUN in ctx.ids


def test_cli_spec_and_offline_package(env, tmp_path, capsys):
    from tools import taskq_run
    exp_dir, store = env
    assert taskq_run.main(["spec", EXP, RUN, "--commit", COMMIT, "--repetitions", "3",
                           "--", "python3", "x.py"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["idempotency_key"] == f"{EXP}/{RUN}"
    spec = _spec()
    result = _result(spec, store)
    (tmp_path / "r.json").write_text(json.dumps(result))
    (tmp_path / "t.json").write_text(json.dumps({"task_id": "T-x", "spec": spec}))
    rc = taskq_run.main(["package", EXP, RUN, "--experiments-root",
                         str(exp_dir.parent), "--result-file", str(tmp_path / "r.json"),
                         "--task-file", str(tmp_path / "t.json")])
    assert rc == 0
    assert (exp_dir / "runs" / RUN / "manifest.yaml").exists()
    # re-packaging the same RUN is refused, not overwritten
    rc = taskq_run.main(["package", EXP, RUN, "--experiments-root",
                         str(exp_dir.parent), "--result-file", str(tmp_path / "r.json"),
                         "--task-file", str(tmp_path / "t.json")])
    assert rc == 2


def test_worker_verify_flag_is_opt_in():
    assert "verify" not in _spec()
    spec = _spec(worker_verify=True)
    assert spec["verify"] == {"builtin": "certificate"}


def test_worker_certificate_hash_is_cross_checked(env):
    exp_dir, store = env
    spec = _spec()
    result = _result(spec, store, certs={"certificate.json": _dl_cert()})
    cert_sha = next(a["sha256"] for a in result["artifacts"]
                    if a["path"] == "certificate.json")
    result["runs"][0]["verification"] = {
        "status": "verified", "verifier": "taskq.verify", "exit_code": 0,
        "wall_seconds": 0.01, "certificate_sha256": cert_sha,
        "detail": {"kind": "discrete_log", "status": "verified"}}
    result["verification"] = {"status": "verified",
                              "counts": {"verified": 1, "refuted": 0,
                                         "no_claim": 0, "error": 0}}
    m, raw = _load(bridge.write_run_package(result, spec, None, str(exp_dir), RUN))
    assert m["status"] == "completed_valid"
    assert m["taskq"]["worker_verification"]["disagrees_with_repo_verifier"] == []
    entry = raw["raw"]["certificates"][0]
    assert entry["worker_certificate_sha256_matches"] is True
    assert entry["worker_verification_disagrees"] is False


@pytest.mark.parametrize("cert", [
    {"kind": "none"},
    _dl_cert(wire_top_level_curve=False),
    _dl_cert(k=K + 1, wire_top_level_curve=False),
])
def test_certificate_rule_matches_runner_write_run(tmp_path, cert):
    """Drift guard: the bridge's mirror of write_run's certificate block gives
    the same status, validity, reason and certificate summary as write_run."""
    rr = runner.RunResult(run_suffix="drift", curve_id="TOY-P7-x", seed=1,
                          parameters={}, metrics={}, certificate=copy.deepcopy(cert))
    run_id = runner.write_run(EXP, "TEST", rr, status="completed_valid",
                              command="x", started=0.0, finished=1.0,
                              out_root=str(tmp_path / "wr"))
    m, _ = _load(str(tmp_path / "wr" / "runs" / run_id))
    c, verified, cairn = bridge.verify_certificate(copy.deepcopy(cert), "c" * 40)
    status, valid, reason = bridge.apply_certificate_verdict(
        "completed_valid", True, None, c, verified)
    assert (status, valid, reason) == (m["status"], m["result"]["valid"],
                                       m["result"]["invalid_reason"])
    assert bridge.certificate_summary(c, cairn) == m["result"]["certificate"]



def test_worker_verify_spec_validates_and_oneof_is_enforced():
    """The vendored schemas carry crypto#1091's `verify`. The offline fallback
    validator must be no laxer than jsonschema: exactly one of builtin/argv."""
    spec = bridge.build_spec("EXP-X-abcdef", "RUN-1", ["python3", "x.py"], "a" * 40,
                             worker_verify=True)
    assert spec["verify"] == {"builtin": "certificate"}
    bridge.validate_spec(spec)
    bridge._subset_validate(spec, bridge.SPEC_SCHEMA)
    for bad in ({"builtin": "certificate", "argv": ["x"]}, {}):
        with pytest.raises(bridge.BridgeError):
            bridge._subset_validate(dict(spec, verify=bad), bridge.SPEC_SCHEMA)
        with pytest.raises(bridge.BridgeError):
            bridge.validate_spec(dict(spec, verify=bad))
