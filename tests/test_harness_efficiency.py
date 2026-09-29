"""harness/efficiency.py: the wrapper-measured efficiency block in run records."""
from __future__ import annotations

import hashlib
import http.server
import json
import os
import threading
from pathlib import Path

import pytest
import yaml

from harness import efficiency
from harness.runner import RunResult

REPO = Path(__file__).resolve().parent.parent
GPUEFF = REPO / "third_party" / "gpueff"
DCGM_TEXT = """\
# TYPE DCGM_FI_PROF_SM_ACTIVE gauge
DCGM_FI_PROF_SM_ACTIVE{gpu="0",UUID="GPU-0",Hostname="h"} 0.9
DCGM_FI_PROF_SM_OCCUPANCY{gpu="0",UUID="GPU-0",Hostname="h"} 0.27
DCGM_FI_PROF_PIPE_INT_ACTIVE{gpu="0",UUID="GPU-0",Hostname="h"} 0.8
DCGM_FI_DEV_SM_CLOCK{gpu="0",UUID="GPU-0",Hostname="h"} 2250
"""


def _result(suffix: str, metrics: dict) -> RunResult:
    return RunResult(run_suffix=suffix, curve_id="TOY", seed=1, parameters={"field_bits": 8},
                     metrics=metrics, certificate={"kind": "none"})


def _manifest(out: Path, run_id: str) -> dict:
    return yaml.safe_load((out / "runs" / run_id / "manifest.yaml").read_text())["run"]


def _busy(n: int = 200_000) -> int:
    return sum(i * i for i in range(n))


def test_cpu_block_is_always_recorded(tmp_path):
    def fn():
        _busy()
        return _result("eff-cpu", {"answer": 42})
    run_id = efficiency.run_wrapped_measured("EXP-TEST-001", "TEST", fn, status="completed_valid",
                                             command="pytest", out_root=str(tmp_path))
    metrics = _manifest(tmp_path, run_id)["result"]["metrics"]
    assert metrics["answer"] == 42
    block = metrics["efficiency"]
    assert block["schema"] == "harness.efficiency/1"
    cpu = block["cpu"]
    assert cpu["wall_seconds"] > 0 and cpu["allocated_cores"] >= 1
    assert cpu["parallelism"] == pytest.approx(
        (cpu["cpu_seconds_self"] + cpu["cpu_seconds_children"]) / cpu["wall_seconds"], rel=1e-3)
    assert cpu["utilization"] == pytest.approx(cpu["parallelism"] / cpu["allocated_cores"], rel=1e-3)
    assert "roofline" not in block


def test_roofline_uses_the_wrappers_wall_clock(tmp_path):
    spec = {"machine": "rtx-pro-6000-blackwell-server", "workload": "ecc2k130-packed-walk",
            "work_units_metric": "iterations", "devices": 1}
    run_id = efficiency.run_wrapped_measured(
        "EXP-TEST-001", "TEST", lambda: _result("eff-roof", {"iterations": 1_000_000}),
        status="completed_valid", command="pytest", out_root=str(tmp_path), efficiency=spec)
    block = _manifest(tmp_path, run_id)["result"]["metrics"]["efficiency"]
    roof = block["roofline"]
    assert roof["status"] == "scored"
    assert roof["achieved"] == pytest.approx(1_000_000 / block["cpu"]["wall_seconds"], rel=1e-3)
    assert roof["roofline_efficiency"] == pytest.approx(roof["achieved"] / roof["attainable"])
    assert roof["bound"]["resource"] == "alu:iadd3+ffma"
    assert roof["gpueff"]["repository"] == "aburan28/cryptanalysis"
    raw = (GPUEFF / "profiles" / "ecc2k130-packed-walk.json").read_bytes()
    assert roof["workload_profile"] == {"path": "third_party/gpueff/profiles/ecc2k130-packed-walk.json",
                                        "sha256": hashlib.sha256(raw).hexdigest()}
    # No DCGM source was given: the GPU components are missing, not invented.
    assert roof["components"]["sm_active"]["status"] == "missing"


def test_dcgm_is_scraped_at_start_and_end(tmp_path):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = DCGM_TEXT.encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        spec = {"machine": "rtx-pro-6000-blackwell-server", "workload": "ecc2k130-packed-walk",
                "work_units_metric": "iterations",
                "dcgm_url": "http://127.0.0.1:%d/metrics" % server.server_port}
        run_id = efficiency.run_wrapped_measured(
            "EXP-TEST-001", "TEST", lambda: _result("eff-dcgm", {"iterations": 10}),
            status="completed_valid", command="pytest", out_root=str(tmp_path), efficiency=spec)
    finally:
        server.shutdown()
    roof = _manifest(tmp_path, run_id)["result"]["metrics"]["efficiency"]["roofline"]
    assert roof["devices"] == 1
    assert roof["components"]["sm_active"]["value"] == pytest.approx(0.9)
    assert roof["components"]["bound_pipe"]["value"] == pytest.approx(0.8)
    assert roof["decomposition"]["factors"]["sm_active"] == pytest.approx(0.9)


def test_unreachable_sources_are_recorded_and_the_run_is_still_written(tmp_path):
    spec = {"machine": "rtx-pro-6000-blackwell-server", "workload": "ecc2k130-packed-walk",
            "work_units_metric": "iterations", "dcgm_url": "http://127.0.0.1:9/metrics",
            "prometheus_url": "http://127.0.0.1:9"}
    run_id = efficiency.run_wrapped_measured(
        "EXP-TEST-001", "TEST", lambda: _result("eff-down", {"iterations": 10}),
        status="completed_valid", command="pytest", out_root=str(tmp_path), efficiency=spec)
    roof = _manifest(tmp_path, run_id)["result"]["metrics"]["efficiency"]["roofline"]
    assert {"dcgm_start", "dcgm_end", "prometheus"} <= set(roof["missing"])
    assert roof["status"] == "scored"


def test_missing_work_units_leave_a_hardware_proxy(tmp_path):
    spec = {"machine": "rtx-pro-6000-blackwell-server", "workload": "ecc2k130-packed-walk",
            "work_units_metric": "iterations"}
    run_id = efficiency.run_wrapped_measured(
        "EXP-TEST-001", "TEST", lambda: _result("eff-nounits", {}),
        status="completed_valid", command="pytest", out_root=str(tmp_path), efficiency=spec)
    roof = _manifest(tmp_path, run_id)["result"]["metrics"]["efficiency"]["roofline"]
    assert roof["basis"] == "hardware-proxy"
    assert roof["roofline_efficiency"] is None
    assert "metrics.iterations" in roof["missing"]["throughput"]


def test_a_bad_profile_is_an_error_in_the_block_not_a_lost_run(tmp_path):
    spec = {"machine": "no-such-machine", "workload": "ecc2k130-packed-walk",
            "work_units_metric": "iterations"}
    run_id = efficiency.run_wrapped_measured(
        "EXP-TEST-001", "TEST", lambda: _result("eff-badprof", {"iterations": 1}),
        status="completed_valid", command="pytest", out_root=str(tmp_path), efficiency=spec)
    roof = _manifest(tmp_path, run_id)["result"]["metrics"]["efficiency"]["roofline"]
    assert roof["status"] == "error" and roof["error"].startswith("profile:")


def test_an_experiment_metric_named_efficiency_is_never_overwritten(tmp_path):
    with pytest.raises(ValueError, match="already reports"):
        efficiency.run_wrapped_measured(
            "EXP-TEST-001", "TEST", lambda: _result("eff-clash", {"efficiency": 0.5}),
            status="completed_valid", command="pytest", out_root=str(tmp_path))
    assert not (tmp_path / "runs").exists()


def test_vendored_gpueff_matches_its_upstream_manifest():
    upstream = json.loads((GPUEFF / "UPSTREAM.json").read_text())
    on_disk = sorted(str(p.relative_to(GPUEFF)) for p in GPUEFF.rglob("*")
                     if p.is_file() and p.name != "UPSTREAM.json" and "__pycache__" not in p.parts)
    assert on_disk == sorted(upstream["files"])
    for rel, digest in upstream["files"].items():
        assert hashlib.sha256((GPUEFF / rel).read_bytes()).hexdigest() == digest, rel


def test_vendored_gpueff_is_pinned_in_run_provenance(tmp_path):
    run_id = efficiency.run_wrapped_measured(
        "EXP-TEST-001", "TEST", lambda: _result("eff-prov", {}),
        status="completed_valid", command="pytest", out_root=str(tmp_path))
    files = _manifest(tmp_path, run_id)["code"]["source"]["files"]
    for module in ("harness/efficiency.py", "third_party/gpueff/gpueff/score.py"):
        assert module in files
        assert files[module]["sha256"] == hashlib.sha256((REPO / module).read_bytes()).hexdigest()


def test_harness_runner_and_manifest_schema_are_untouched():
    # Locked plans pin these by hash; this module must not require edits to them.
    import harness.finite_yaml_locked_v3 as locked
    for rel in ("harness/runner.py", "schemas/run-manifest.schema.json"):
        assert hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == locked.ORIGINAL_SOURCE_PINS[rel]
    assert os.path.exists(REPO / "harness" / "efficiency.py")
