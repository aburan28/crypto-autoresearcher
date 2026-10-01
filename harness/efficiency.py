"""Wrapper-measured compute efficiency for harness run records.

`run_wrapped_measured` is `runner.run_wrapped` plus one addition: the run's
`result.metrics.efficiency` block, measured here around the experiment
function rather than reported by it (the same discipline that makes
`wall_seconds` wrapper-measured, DEC-20260810-1163ec F-4(e)).

It is OPT-IN and changes nothing else. `harness/runner.py` and
`schemas/run-manifest.schema.json` are pinned by content hash in locked
execution plans (finite_yaml_locked_v2/v3 ORIGINAL_SOURCE_PINS) and listed as
`reused_unmodified` in frozen contracts, so this module does not edit them:
the block rides in `result.metrics`, which the schema leaves open, and an
experiment whose frozen protocol does not call this entry point records
exactly what it recorded before.

The block has two parts.

cpu (always)
    process-tree CPU seconds (this process plus waited-for children) over wall
    seconds: `parallelism` in cores, and `utilization` against the cores this
    process may run on. Measured, never estimated.

roofline (when the experiment supplies an `efficiency` spec)
    the gpueff score (third_party/gpueff, vendored from aburan28/cryptanalysis
    at the commit in its UPSTREAM.json): achieved over attainable throughput
    for a machine profile and a workload profile, the loss decomposition,
    component scores and findings. Throughput is `work_units` (read from the
    run's own metrics) over the WRAPPER's wall seconds. GPU components come
    from a DCGM exporter scraped at the start and end of the run, or a
    Prometheus range query over the run window, when a URL is given.

Missing inputs are recorded as missing with the reason, never filled in, and
a scoring failure is recorded in the block rather than failing the run:
efficiency describes how the run used the machine, not whether its result is
valid. Per docs/claims-and-verification.md it is a cost observation scoped to
this machine and this run, never mathematical evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import sys
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path

from harness import runner

REPO = Path(runner.REPO)
GPUEFF_ROOT = REPO / "third_party" / "gpueff"
BLOCK_SCHEMA = "harness.efficiency/1"
SCRAPE_TIMEOUT_SECONDS = 10

if str(GPUEFF_ROOT) not in sys.path:
    sys.path.insert(0, str(GPUEFF_ROOT))
from gpueff import metrics as gpueff_metrics  # noqa: E402
from gpueff import observe as gpueff_observe  # noqa: E402
from gpueff import profiles as gpueff_profiles  # noqa: E402
from gpueff import prom as gpueff_prom  # noqa: E402
from gpueff import score as gpueff_score  # noqa: E402


def allocated_cores() -> int:
    try:
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):          # macOS has no affinity API
        return os.cpu_count() or 1


def _snapshot() -> dict:
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"monotonic": time.monotonic(), "time": time.time(),
            "self": own.ru_utime + own.ru_stime,
            "children": children.ru_utime + children.ru_stime}


def cpu_block(before: dict, after: dict, cores: int) -> dict:
    wall = after["monotonic"] - before["monotonic"]
    own = after["self"] - before["self"]
    children = after["children"] - before["children"]
    total = own + children
    block = {"wall_seconds": round(wall, 6), "cpu_seconds_self": round(own, 6),
             "cpu_seconds_children": round(children, 6), "allocated_cores": cores,
             "parallelism": None, "utilization": None,
             "basis": "getrusage(SELF)+getrusage(CHILDREN) deltas over the wrapper's "
                      "monotonic wall clock; children count only once waited for"}
    if wall > 0:
        block["parallelism"] = round(total / wall, 6)
        block["utilization"] = round(total / wall / cores, 6)
    return block


def _profile(name_or_path: str) -> tuple[dict, dict]:
    path = Path(name_or_path)
    if not path.is_absolute() and not path.exists():
        path = GPUEFF_ROOT / "profiles" / (name_or_path if path.suffix else name_or_path + ".json")
    raw = path.read_bytes()
    try:
        shown = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        shown = str(path)
    return json.loads(raw), {"path": shown, "sha256": hashlib.sha256(raw).hexdigest()}


def _scrape(url: str) -> tuple[list, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=SCRAPE_TIMEOUT_SECONDS) as reply:
            return gpueff_metrics.parse_text(reply.read().decode(), time.time()), None
    except Exception as exc:                       # recorded, never fatal
        return [], f"{type(exc).__name__}: {exc}"


def _upstream() -> dict:
    try:
        upstream = json.loads((GPUEFF_ROOT / "UPSTREAM.json").read_text())
        return {"repository": upstream["repository"], "commit": upstream["commit"]}
    except (OSError, ValueError, KeyError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def _summary(report: dict) -> dict:
    keep = ("score", "basis", "coverage", "roofline_efficiency", "achieved", "attainable",
            "headroom", "work_unit", "devices", "decomposition", "findings", "next_roof",
            "power_watts", "joules_per_unit")
    out = {k: report.get(k) for k in keep}
    out["bound"] = {k: report["bound"][k] for k in ("demand", "resource", "units_per_second")}
    out["components"] = {name: {k: c.get(k) for k in ("value", "raw", "weight", "status", "why")
                                if c.get(k) is not None}
                         for name, c in report["components"].items()}
    return out


def roofline_block(spec: dict, metrics: dict, wall_seconds: float,
                   samples: list, missing: dict) -> dict:
    block: dict = {"status": "scored", "gpueff": _upstream(), "missing": dict(missing)}
    try:
        machine, block["machine_profile"] = _profile(spec["machine"])
        workload, block["workload_profile"] = _profile(spec["workload"])
        gpueff_profiles.check_machine(machine)
        gpueff_profiles.check_workload(workload, machine)
    except (OSError, ValueError, KeyError) as exc:
        block.update(status="error", error=f"profile: {type(exc).__name__}: {exc}")
        return block

    throughput = None
    key = spec.get("work_units_metric")
    if key is not None:
        units = metrics.get(key)
        if isinstance(units, (int, float)) and not isinstance(units, bool) and wall_seconds > 0:
            throughput = units / wall_seconds
            block["throughput_source"] = f"metrics.{key} / wrapper wall_seconds"
        else:
            block["missing"]["throughput"] = f"metrics.{key} is {units!r}, not a number of work units"
    else:
        block["missing"]["throughput"] = "no work_units_metric in the efficiency spec"

    observations = gpueff_observe.observe(samples, workload, throughput=throughput)
    for name, why in observations.pop("missing", {}).items():
        block["missing"].setdefault(name, why)
    if spec.get("devices"):
        observations["devices"] = spec["devices"]
    try:
        block.update(_summary(gpueff_score.score(observations, machine, workload, spec.get("weights"))))
    except (ValueError, KeyError, ZeroDivisionError) as exc:
        block.update(status="error", error=f"score: {type(exc).__name__}: {exc}")
    return block


def run_wrapped_measured(exp_id: str, exp_area: str, fn: Callable[[], "runner.RunResult"], *,
                         status: str, command: str, out_root: str | None = None,
                         efficiency: dict | None = None) -> str:
    """`runner.run_wrapped`, with `result.metrics.efficiency` measured around `fn`.

    `efficiency` (optional) asks for a roofline score as well as the CPU block:

        machine            gpueff machine profile: a name under
                           third_party/gpueff/profiles or a path
        workload           gpueff workload profile, likewise
        work_units_metric  key of the run's own metrics holding the number of
                           work units done (iterations, relations, tokens)
        dcgm_url           optional DCGM exporter /metrics URL, scraped at the
                           start and end of the run
        prometheus_url     optional Prometheus base URL, range-queried over the
                           run window (needs the run to outlast a few scrapes)
        devices            optional device count when no per-GPU series exist
        weights            optional gpueff weight overrides

    The block is written under the key "efficiency"; an experiment metric of
    that name is refused rather than overwritten.
    """
    spec = dict(efficiency or {})
    cores = allocated_cores()

    def measured() -> runner.RunResult:
        samples, missing = [], {}
        if spec.get("dcgm_url"):
            got, error = _scrape(spec["dcgm_url"])
            samples += got
            if error:
                missing["dcgm_start"] = error
        before = _snapshot()
        result = fn()
        after = _snapshot()
        if "efficiency" in result.metrics:
            raise ValueError("the experiment already reports a metric named 'efficiency'; "
                             "run_wrapped_measured will not overwrite a result")
        if spec.get("dcgm_url"):
            got, error = _scrape(spec["dcgm_url"])
            samples += got
            if error:
                missing["dcgm_end"] = error
        if spec.get("prometheus_url"):
            try:
                machine, _ = _profile(spec["machine"])
                workload, _ = _profile(spec["workload"])
                window = "%.3fs" % max(after["time"] - before["time"], 1.0)
                samples += gpueff_prom.fetch(spec["prometheus_url"], machine, workload,
                                             window=window, end=after["time"])
            except Exception as exc:               # recorded, never fatal
                missing["prometheus"] = f"{type(exc).__name__}: {exc}"
        block = {"schema": BLOCK_SCHEMA, "measured_by": "harness/efficiency.py",
                 "cpu": cpu_block(before, after, cores)}
        if spec:
            block["roofline"] = roofline_block(spec, result.metrics,
                                               block["cpu"]["wall_seconds"], samples, missing)
        result.metrics = {**result.metrics, "efficiency": block}
        return result

    return runner.run_wrapped(exp_id, exp_area, measured, status=status, command=command,
                              out_root=out_root)
