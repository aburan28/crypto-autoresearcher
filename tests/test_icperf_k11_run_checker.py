"""Replay archived planted k11 models and reject altered retained solver bytes."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from tools.icperf_binary_root_certificate import certificate


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "experiments/EXP-ICPERF-018b0c/implementation/verify_run.py"
EXECUTE_PATH = ROOT / "experiments/EXP-ICPERF-018b0c/implementation/execute.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("label,base_name", [("weighted", "weighted"),
                                             ("local_random", "local_control")])
def test_archived_planted_model_is_replayed_and_tamper_is_rejected(tmp_path, label, base_name):
    checker = load_module(CHECKER_PATH, f"k11_checker_{label}")
    positive = checker.read(checker.HERE / "inputs/positive_manifest.json")
    chain = checker.read(ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json")
    base = checker.read(ROOT / f"research/icperf_binary_torsion_k11_{base_name}_20261017/base.json")
    raw, arm, bound = checker.call_input("positive", label, None, 0, positive, {}, {}, chain)
    model = (ROOT / positive["controls"][label]["known_model_path"]).read_bytes()
    nvars, clauses, xors = checker.parse_xcnf(raw)
    values = checker.parse_sat_model(model.decode(), nvars)
    checker.verify_xcnf(values, clauses, xors)
    assignment = sum(1 << (j - 1) for j in range(1, 455) if values[j])
    assert assignment == int(positive["controls"][label]["source_row"]
                             ["synthetic_control"]["assignment_hex"], 16)
    assert len(checker.exact_point_rows(assignment, base, bound, arm)) == 1
    assert checker.exact_point_rows(assignment ^ 1, base, bound, arm) == []

    run_dir = tmp_path / "runs" / "RUN-ICPERF-fixture01"
    call_dir = run_dir / "calls" / f"positive_{label}"
    attempt_dir = call_dir / "attempt-0001"
    attempt_dir.mkdir(parents=True)
    input_path = attempt_dir / "input.xcnf"
    input_path.write_bytes(raw)
    (attempt_dir / "stdout.txt").write_bytes(model)
    (attempt_dir / "stderr.txt").write_bytes(b"")
    cert = {"schema": "icperf-k11-full-point-check-v1",
            "experiment_id": checker.EXPERIMENT, "base_kind": label,
            "target_index": None, "channel": 0,
            "assignment_hex": hex(assignment),
            "result": certificate(assignment, base, bound, arm)}
    cert_path = attempt_dir / "certificate.json"
    cert_path.write_text(json.dumps(cert) + "\n")
    attempt = {"command": ["/opt/homebrew/bin/cryptominisat5", "--verb", "0",
                            "--threads", "1", "--maxsol", "1", "--random", "20261017",
                            "--maxtime", "300", str(input_path)],
               "input_sha256": checker.sha(raw), "blocked_primary": 0,
               "process": {"returncode": 10, "wall_timeout": False,
                           "rss_watchdog_tripped": False,
                           "stdout_sha256": checker.sha(model),
                           "stderr_sha256": checker.sha(b"")},
               "solver_status_lines": ["s SATISFIABLE"],
               "primary_assignment_hex": hex(assignment),
               "full_xcnf_model_verified": True,
               "certificate_sha256": checker.sha(cert_path.read_bytes()),
               "outcome": "point_relation_certified"}
    (attempt_dir / "attempt.json").write_text(json.dumps(attempt) + "\n")
    host = {"load_average_before": [0.0, 0.0, 0.0]}
    summary = {"status": "point_relation_certified", "input_sha256": checker.sha(raw),
               "base_kind": label, "target_index": None, "channel": 0,
               "host": host, "limits": {"wall_seconds": 300, **checker.LIMITS},
               "total_wall_seconds": 1.0, "call_wrapper_wall_seconds": 1.1,
               "point_filter_wall_seconds": 0.1, "point_filter_cpu_seconds": 0.1,
               "blocked_primary_count": 0, "attempts": [attempt]}
    summary_path = call_dir / "summary.json"
    summary_path.write_text(json.dumps(summary) + "\n")
    row = {"status": "point_relation_certified", "base_kind": label,
           "host": host, "call_dir": str(call_dir.relative_to(run_dir)),
           "summary_sha256": checker.sha(summary_path.read_bytes()),
           "attempts": 1, "total_wall_seconds": 1.0}
    assert len(checker.check_call(run_dir, row, "positive", base, arm, bound, raw)) == 1

    (attempt_dir / "stdout.txt").write_bytes(model.replace(b"v -1 ", b"v 1 ", 1))
    with pytest.raises(AssertionError):
        checker.check_call(run_dir, row, "positive", base, arm, bound, raw)


def test_direct_runner_refuses_review_required_protocol(tmp_path):
    runner = load_module(EXECUTE_PATH, "k11_execute_gate")
    run_dir = tmp_path / "runs" / "RUN-ICPERF-fixture01"
    run_dir.mkdir(parents=True)
    (run_dir / "launch.json").write_text("{}\n")
    (run_dir / "environment.json").write_text("{}\n")
    with pytest.raises(ValueError, match="not frozen and authorized"):
        runner.approved_launch(run_dir, "positive")
