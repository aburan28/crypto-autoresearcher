#!/usr/bin/env python3
"""Native launch entry point; per-arm watchdogs preserve partial proof journals."""
import argparse
from collections import Counter
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import engine


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def artifact(output, path):
    path = Path(path)
    return {"artifact": str(path.relative_to(output)), "sha256": digest(path), "bytes": path.stat().st_size}


def select_cells(config):
    """Input-only selector. No decomposition or SAT outcome is consulted."""
    cells, costs = [], Counter()
    for curve in config["curves"]:
        p, a, b = (curve[k] for k in ("p", "a", "b"))
        if p <= 3 or any(p % d == 0 for d in range(2, __import__("math").isqrt(p) + 1)):
            raise ValueError("fixture modulus must be prime")
        if (4 * a**3 + 27 * b*b) % p == 0:
            raise ValueError("singular fixture curve")
        targets = []
        for x in range(p):
            for y in range(1, p):
                costs["curve_equation_tests"] += 1
                if (y*y - x**3 - a*x - b) % p == 0:
                    targets.append([x, y])
                    break
            if len(targets) == config["target_selection"]["count_per_curve"]:
                break
        if len(targets) != config["target_selection"]["count_per_curve"]:
            raise ValueError("not enough targets under frozen selector")
        for s in config["digits"]:
            if not 1 <= s or 1 << s > p:
                raise ValueError("invalid digit width")
            for target in targets:
                cells.append({"id": f"c{len(cells):02d}", **curve, "s": s, "target": target})
    return cells, dict(costs)


def jobs(config, cells):
    for index, cell in enumerate(cells):
        for enc_index, encoding in enumerate(config["encodings"]):
            strategies = config["strategies"]
            shift = (index + enc_index) % len(strategies)
            for strategy in strategies[shift:] + strategies[:shift]:
                yield {"id": f"{cell['id']}-{encoding}-{strategy}", "cell_id": cell["id"],
                       "input": cell, "encoding": encoding, "strategy": strategy, "limits": config["limits"]}


def control_jobs(config):
    for name in ("positive", "negative", "empty_clause"):
        for strategy in config["strategies"]:
            yield {"id": f"control-{name}-{strategy}", "cell_id": "control-" + name,
                   "input": config["controls"][name], "encoding": "synthetic", "strategy": strategy,
                   "limits": config["limits"]}


def run_control(job, checkpoint=None):
    inp = job["input"]
    ring = engine.legacy.CountedRing(inp["n"], inp["p"])
    polys = [{int(k): v for k, v in poly.items()} for poly in inp["polynomials"]]
    domain = inp.get("domain", [])
    answer = engine.solve(ring, polys, domain, inp["projected_bits"], job["limits"], job["strategy"],
                          inp["prefix_depths"], checkpoint)
    checked = engine.adapter.verify_transcript(inp["p"], inp["n"], inp["projected_bits"], polys,
                                               domain, answer, aux_bound=inp.get("aux_bound"))
    result = {k: checked[k] for k in ("declared_status", "projected_models", "cover_complete",
                                     "projected_model_set_complete")}
    result["stop_reason"] = answer["stop_reason"]
    phases = {k: answer["costs"][k] for k in
              ("search_arithmetic", "search_events", "online_certificate_check", "sat_native")}
    phases.update(construction={}, offline_verification=checked["costs"], reconstruction={})
    return {"answer": answer, "result": result, "phases": phases}


def worker(job, output):
    started, cpu = time.monotonic(), time.process_time()
    transcript = output / "transcripts" / (job["id"] + ".json")
    partial = transcript.with_suffix(".partial.json")
    # A watchdog before construction still leaves an explicitly incomplete record.
    write(partial, {"status": "censored", "models": [], "learned": [], "stop_reason": "before_construction"})
    if job["encoding"] == "synthetic":
        package = run_control(job, lambda answer: write(partial, answer))
    else:
        package = engine.run_cell(job["input"], job["encoding"], job["strategy"], job["limits"],
                                  lambda answer: write(partial, answer))
    write(transcript, package.pop("answer"))
    row = {k: job[k] for k in ("id", "cell_id", "input", "encoding", "strategy")}
    row.update(package, transcript=artifact(output, transcript), environment=engine.environment(),
               censoring={"watchdog": False, "native_limit": package["result"]["stop_reason"] == "native_limit"},
               descriptive={"wall_seconds": time.monotonic() - started,
                            "cpu_seconds": time.process_time() - cpu,
                            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                            "wall_comparison_valid": False})
    write(output / "rows" / (job["id"] + ".json"), row)


def bounded_arm(job, output, watchdog):
    started = time.monotonic()
    for directory in ("transcripts", "rows", "logs"):
        (output / directory).mkdir(exist_ok=True)
    stdout = output / "logs" / (job["id"] + ".stdout.txt")
    stderr = output / "logs" / (job["id"] + ".stderr.txt")
    argv = [sys.executable, "-B", str(HERE / "driver.py"), "--worker-json", json.dumps(job),
            "--output", str(output)]
    timed_out = False
    with stdout.open("x") as out, stderr.open("x") as err:
        try:
            completed = subprocess.run(argv, stdout=out, stderr=err, timeout=watchdog,
                                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out, returncode = True, None
    row_path = output / "rows" / (job["id"] + ".json")
    if returncode == 0 and row_path.exists():
        row = json.loads(row_path.read_text())
    else:
        partial = output / "transcripts" / (job["id"] + ".partial.json")
        row = {k: job[k] for k in ("id", "cell_id", "input", "encoding", "strategy")}
        row.update(result={"declared_status": "censored" if timed_out else "failed",
                           "stop_reason": "process_watchdog" if timed_out else "worker_error"},
                   transcript=artifact(output, partial) if partial.exists() else None,
                   phases=None, environment=engine.environment(),
                   censoring={"watchdog": timed_out, "native_limit": False})
    row["worker"] = {"argv": argv, "returncode": returncode, "timed_out": timed_out,
                      "stdout": artifact(output, stdout), "stderr": artifact(output, stderr),
                      "parent_observed_wall_seconds": time.monotonic() - started,
                      "includes_process_startup": True, "wall_comparison_valid": False}
    write(row_path, row)
    return row


def reference_one(cell):
    producer = engine.load("research/prime_sat_costbridge_20261029/reference.py", "psearch_reference")
    checker = engine.load("research/prime_sat_costbridge_20261029/check_reference.py", "psearch_reference_check")
    domain = {"kind": "interval", "offset": 0, "size": 1 << cell["s"]}
    inp = {k: cell[k] for k in ("p", "a", "b", "target")}
    inp.update(D1=domain, D2=domain)
    # Count actual calls without changing the frozen implementations. These are
    # semantic events, not a total of field operations or CPU instructions.
    def instrument(function):
        counts = Counter()
        files = {producer.__file__, checker.__file__}
        old = sys.getprofile()
        def profile(frame, event, arg):
            if frame.f_code.co_filename in files:
                if event == "call":
                    counts["python_call:" + frame.f_code.co_name] += 1
                elif event == "c_call" and getattr(arg, "__name__", None) == "pow":
                    counts["builtin_pow_calls"] += 1
        try:
            sys.setprofile(profile)
            result = function()
        finally:
            sys.setprofile(old)
        return result, dict(counts)
    answer, costs = instrument(lambda: producer.solve(inp, "all"))
    checked, checking = instrument(lambda: checker.verify(inp, answer))
    return {"cell_id": cell["id"], "input": inp, "answer": answer, "check": checked,
            "source_events": costs, "checking_source_events": checking,
            "cost_scope": "function and builtin pow events only; not field-operation totals"}


def execute(config_path, output):
    import yaml
    import check
    if (output / "raw-result.json").exists():
        raise ValueError("refuse overwriting prior run")
    launch = json.loads((output / "launch.json").read_text())
    host = json.loads((output / "environment.json").read_text())
    config = json.loads(config_path.read_text())
    raw = {"schema": "prime-prefix-search-result/v1", "attack_claimed": False, "status": "running",
           "config": config, "config_sha256": digest(config_path), "environment": engine.environment(),
           "packages": {}, "flow": {}, "metrics": {}, "check_status": "pending"}
    manifest = {"run": {"id": launch["run_id"], "experiment_id": config["experiment_id"],
                         "status": "running", "attack_claimed": False,
                         "code": {"commit": launch["authority"]["commit"], "command": json.dumps(launch["argv"])},
                         "environment": host, "inputs": {"plan_sha256": launch["plan_sha256"], "trial_id": launch["trial_id"]},
                         "timing": {"started_at": launch["started_at"]}, "metrics": {},
                         "result": {"raw_result": "raw-result.json", "certificate": {"kind": "none", "verified": None}}}}
    write(output / "raw-result.json", raw)
    (output / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    search, controls, references = [], [], []
    try:
        cells, selection = select_cells(config)
        raw["input_selection"] = {"cells": cells, "costs": selection}
        raw["planned_search_ids"] = [job["id"] for job in jobs(config, cells)]
        raw["planned_control_ids"] = [job["id"] for job in control_jobs(config)]
        write(output / "raw-result.json", raw)
        for name, inventory, rows in (("controls", control_jobs(config), controls),
                                       ("search", jobs(config, cells), search)):
            with (output / (name + "-rows.jsonl")).open("x") as journal:
                for job in inventory:
                    row = bounded_arm(job, output, config["limits"]["arm_watchdog_seconds"])
                    rows.append(row)
                    journal.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    journal.flush()
                    os.fsync(journal.fileno())
                    print(json.dumps({"event": "arm_finished", "id": row["id"], "status": row["result"]["declared_status"]}), flush=True)
        # The correctness reference runs only after the last search arm.
        references = [reference_one(cell) for cell in cells]
        mutations = check.mutation_controls()
        write(output / "search.json", {"config": config, "rows": search})
        write(output / "controls.json", {"config": config, "rows": controls, "mutations": mutations})
        write(output / "reference.json", {"config": config, "rows": references})
        for name in ("search", "controls", "reference"):
            raw["packages"][name] = artifact(output, output / (name + ".json"))
        for name, rows, planned in (("search", search, len(raw["planned_search_ids"])),
                                     ("controls", controls, len(raw["planned_control_ids"]))):
            states = Counter(row["result"]["declared_status"] for row in rows)
            raw["flow"][name] = {"planned": planned, "attempted": len(rows),
                                  "complete": states["complete"], "censored": states["censored"],
                                  "failed": states["failed"],
                                  "interrupted": sum(row["censoring"]["watchdog"] for row in rows)}
        raw["status"] = "completed"
        raw["metrics"] = {"search_rows": len(search), "control_rows": len(controls), "reference_rows": len(references)}
        write(output / "raw-result.json", raw)
        checked = check.verify(output / "raw-result.json")
        raw["check_status"] = "valid" if checked["valid"] else "invalid"
        write(output / "check-result.json", checked)
    except Exception:
        raw.update(status="failed", check_status="error", error=traceback.format_exc())
        # Partial journals and per-arm files are never removed or overwritten.
        print(raw["error"], file=sys.stderr)
    write(output / "raw-result.json", raw)
    manifest["run"].update(status="completed" if raw["status"] == "completed" else "failed", metrics=raw["metrics"])
    (output / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    return 0 if raw["status"] == "completed" and raw["check_status"] == "valid" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--worker-json")
    args = parser.parse_args()
    if args.verify:
        import check
        result = check.verify(args.verify)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["valid"] else 1
    if args.worker_json:
        worker(json.loads(args.worker_json), args.output)
        return 0
    if not args.config or not args.output:
        parser.error("--config and --output required")
    return execute(args.config, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
