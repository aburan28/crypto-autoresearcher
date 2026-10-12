"""Fixed public measurement queue with immutable field outputs."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Avoid implicit BLAS parallelism competing with the explicit worker budget.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

from measure import (decode_coordinates, describe_curve, encode_coordinates, exact_weights,
                     field_arrays, identity, make_probes, scalar_weight, seed_for)
from prepare import write_preparation


def json_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False)
        stream.write("\n")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sqrt_mod(x, p):
    """Tonelli-Shanks, used only to retain public coordinate check examples."""
    if not x:
        return 0
    if pow(x, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(x, (p + 1) // 4, p)
    s, d = 0, p - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    c, r, t, m = pow(z, d, p), pow(x, (d + 1) // 2, p), pow(x, d, p), s
    while t != 1:
        i, v = 0, t
        while v != 1:
            v = v * v % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        r, t, c, m = r * b % p, t * b * b % p, b * b % p, i
    return r


def measure_one(model, task, config, field_data=None):
    p, a, b = model["p"], model["A"], model["B"]
    uid = identity(p, a, b)
    if model.get("curve_id", uid) != uid:
        raise ValueError("curve identity mismatch")
    probes, start, window = make_probes(p, config["seed"], uid, config["uniform_probes"], config["window_probes"])
    census = None
    if field_data is not None:
        x, roots = field_data
        census = exact_weights(p, a, b, x, roots)
        n = 1 + int(census.sum())
        uniform_weights = census[probes]
        window_weights = census[window]
    else:
        n = model["N"]
        uniform_weights = np.fromiter((scalar_weight(p, a, b, q) for q in probes), dtype=np.uint8, count=len(probes))
        window_weights = np.fromiter((scalar_weight(p, a, b, q) for q in window), dtype=np.uint8, count=len(window))
    result = describe_curve(p, a, b, n, uid, probes, uniform_weights, start, window_weights, config, census)
    result["index"] = model["index"]
    result["count_provenance"] = "new exact census" if census is not None else "RUN-ECDLP-d0e449 PARI source input"
    points = []
    for q, weight in zip(probes, uniform_weights):
        if weight and len(points) < 8:
            rhs = (q * q % p * q + a * q + b) % p
            y = int(field_data[1][rhs]) if field_data is not None else sqrt_mod(rhs, p)
            if y is None or y * y % p != rhs:
                raise ValueError("point coordinate check failed")
            points.append([q, y])
    result["public_point_examples"] = points
    encoded = encode_coordinates(probes, p)
    if decode_coordinates(encoded) != probes:
        raise ValueError("probe serialization failed")
    arrays = {"uniform_x_bytes": encoded, "uniform_weights": uniform_weights, "window_weights": window_weights}
    if census is not None:
        arrays["census_liftability_packed"] = np.packbits(census > 0, bitorder="little")
    return result, arrays, census, probes


def measure_field(task, config, directory):
    path = Path(directory)
    start_wall, start_cpu = time.monotonic(), time.process_time()
    p = task["p"]
    field_data = field_arrays(p) if task["kind"] == "census" else None
    rows, raw = [], {}
    first_census = first_probes = None
    for model in task["models"]:
        row, arrays, census, probes = measure_one(model, task, config, field_data)
        rows.append(row)
        for key, array in arrays.items():
            raw.setdefault(key, []).append(array)
        if len(rows) == 1:
            first_census, first_probes = census, probes
    first = task["models"][0]
    # A fixed public change of coordinates, not an additional independent model.
    import random
    u = random.Random(seed_for(config["seed"], task["id"], "isomorphism")).randrange(1, p)
    u2, u4, u6 = pow(u, 2, p), pow(u, 4, p), pow(u, 6, p)
    companion = {"index": 0, "p": p, "A": first["A"] * u4 % p,
                 "B": first["B"] * u6 % p, "N": rows[0]["N"]}
    comp, comp_arrays, comp_census, _ = measure_one(companion, task, config, field_data)
    if comp["N"] != rows[0]["N"]:
        raise ValueError("isomorphism changed cardinality")
    if first_census is not None:
        mapped = field_data[0] * u2 % p
        if not np.array_equal(comp_census[mapped], first_census):
            raise ValueError("full isomorphism weight map failed")
        checked = p
    else:
        for q in first_probes:
            old_rhs = (q**3 + first["A"] * q + first["B"]) % p
            mapped_x = u2 * q % p
            new_rhs = (mapped_x**3 + companion["A"] * mapped_x + companion["B"]) % p
            if new_rhs != u6 * old_rhs % p:
                raise ValueError("mapped polynomial identity failed")
        for q in first_probes[:32]:
            if scalar_weight(p, companion["A"], companion["B"], u2 * q % p) != scalar_weight(p, first["A"], first["B"], q):
                raise ValueError("mapped character identity failed")
        checked = len(first_probes)
    comp["isomorphism"] = {"source_curve_id": rows[0]["curve_id"], "u": u,
                            "map": "x'=u^2*x; y'=u^3*y", "mapped_coordinates_checked": checked,
                            "independent_character_checks": p if first_census is not None else 32}
    for key, array in comp_arrays.items():
        if key != "census_liftability_packed":
            raw["companion_" + key] = array
    raw = {key: np.stack(value) if isinstance(value, list) else value for key, value in raw.items()}
    raw["window_start_bytes"] = encode_coordinates([row["window_start"] for row in rows], p)
    raw_path = path / (task["id"] + ".npz")
    with raw_path.open("xb") as stream:
        np.savez_compressed(stream, **raw)
    result = {"field_id": task["id"], "case": task["case"], "arm": task["arm"], "block": task["block"],
              "p": p, "bits": task["bits"], "naf_weight": task["naf_weight"], "kind": task["kind"],
              "curves": rows, "isomorphic_companion": comp,
              "wall_seconds": time.monotonic() - start_wall, "cpu_seconds": time.process_time() - start_cpu,
              "raw_file": raw_path.name, "raw_sha256": digest(raw_path), "raw_bytes": raw_path.stat().st_size}
    json_path = path / (task["id"] + ".json")
    json_new(json_path, result)
    return {"field_id": task["id"], "case": task["case"], "curves": len(rows), "raw_bytes": result["raw_bytes"],
            "cpu_seconds": result["cpu_seconds"], "wall_seconds": result["wall_seconds"],
            "json_sha256": digest(json_path), "raw_sha256": result["raw_sha256"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    task_dir = Path(__file__).resolve().parent
    repo = task_dir.parent.parent
    config = json.loads((task_dir / "config.json").read_text())
    run = Path(args.output).resolve()
    run.mkdir(parents=True, exist_ok=True)
    outputs = run / "fields"
    outputs.mkdir(exist_ok=True)
    if (run / "receipt.json").exists():
        raise SystemExit("completed receipt exists; immutable run cannot be overwritten")
    if (run / "inputs.json").exists():
        preparation = json.loads((run / "inputs.json").read_text())
        if preparation["config"] != config:
            raise SystemExit("configuration differs from frozen preparation")
    else:
        preparation = write_preparation(repo, config, run)
    sources = {path.name: digest(path) for path in sorted(task_dir.glob("*.py"))}
    sources.update({name: digest(task_dir / name) for name in ("config.json", "PROTOCOL.md")})
    if (run / "environment.json").exists():
        env = json.loads((run / "environment.json").read_text())
        if env["source_sha256"] != sources:
            raise SystemExit("measurement source differs from frozen launch")
    else:
        json_new(run / "environment.json", {"python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
                 "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
                 "workers": config["workers"], "source_sha256": sources, "input_sha256": digest(run / "inputs.json"),
                 "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    completed, remaining = [], []
    for task in preparation["tasks"]:
        output = outputs / (task["id"] + ".json")
        if output.exists():
            row = json.loads(output.read_text())
            if digest(outputs / row["raw_file"]) != row["raw_sha256"]:
                raise SystemExit("existing raw checksum failed")
            completed.append({"field_id": task["id"], "case": task["case"], "curves": len(row["curves"]),
                              "raw_bytes": row["raw_bytes"], "cpu_seconds": row["cpu_seconds"],
                              "wall_seconds": row["wall_seconds"], "json_sha256": digest(output), "raw_sha256": row["raw_sha256"]})
        else:
            if (outputs / (task["id"] + ".npz")).exists():
                raise SystemExit("incomplete raw field output exists; record/review failure before a new run")
            remaining.append(task)
    started = time.monotonic()
    failures = []

    def progress():
        view = {"total_fields": len(preparation["tasks"]), "complete_fields": len(completed),
                "total_curves": preparation["curves"], "complete_curves": sum(row["curves"] for row in completed),
                "by_case": {case: {"fields": sum(r["case"] == case for r in completed),
                                    "curves": sum(r["curves"] for r in completed if r["case"] == case)} for case in config["primary_cases"]},
                "wall_seconds_this_launch": time.monotonic() - started, "failures": failures}
        temp = run / "progress.tmp"
        temp.write_text(json.dumps(view, sort_keys=True) + "\n")
        temp.replace(run / "progress.json")
        print(json.dumps(view, sort_keys=True), flush=True)

    progress()
    with concurrent.futures.ProcessPoolExecutor(max_workers=config["workers"]) as pool:
        futures = {pool.submit(measure_field, task, config, str(outputs)): task for task in remaining}
        last_progress = time.monotonic()
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                completed.append(future.result())
            except Exception:
                failure = {"field_id": task["id"], "traceback": traceback.format_exc()}
                failures.append(failure)
                json_new(run / ("failure-" + task["id"] + ".json"), failure)
            if time.monotonic() - last_progress > 20:
                progress()
                last_progress = time.monotonic()
    progress()
    json_new(run / "receipt.json", {"schema": 1, "status": "complete" if not failures else "measurement_failures",
             "environment_sha256": digest(run / "environment.json"), "input_sha256": digest(run / "inputs.json"),
             "fields": sorted(completed, key=lambda row: row["field_id"]), "failures": failures,
             "wall_seconds_this_launch": time.monotonic() - started,
             "total_worker_cpu_seconds": sum(row["cpu_seconds"] for row in completed)})
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
