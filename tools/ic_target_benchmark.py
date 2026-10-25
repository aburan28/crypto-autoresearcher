"""Frozen, isolated toy-IC comparison; run through experiment_execution.py.

The timer surrounds the entire native solve, including factor-base and both
tables, unsuccessful attempts, elimination, and final verification. Public
instance generation, process startup, trace hashing and the independent
checker are outside that timer and are recorded as harness overhead.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/ic-target-benchmark.json"
ARITHMETIC_KEYS = ("k", "verified", "m", "engine", "accelerated", "factor_base",
                   "relations", "rank", "attempts", "s3_solves", "membership_tests",
                   "la_ops", "la_pivot", "msolve_calls", "censored_attempts",
                   "table_arity", "table_entries", "table_s3_solves", "harvest")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def write_once(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def worker(instance, seed, arm, config):
    from crypto_autoresearcher.index_calculus import Curve
    from crypto_autoresearcher.index_calculus import solver

    E = Curve(instance["p"], instance["a"], instance["b"], instance["order"])
    P, Q = tuple(instance["P"]), tuple(instance["Q"])
    targets, relations = [], []
    decompose = solver.decompose
    build_base = solver.build_factor_base
    bases = []

    def record_base(*args, **kwargs):
        base = build_base(*args, **kwargs)
        bases.append(base)
        return base

    def record(curve, fb, target, *args, **kwargs):
        relation = decompose(curve, fb, target, *args, **kwargs)
        targets.append(target)
        relations.append(relation)
        return relation

    solver.decompose = record
    solver.build_factor_base = record_base
    cpu0, wall0 = time.process_time_ns(), time.perf_counter_ns()
    try:
        result = solver.solve_index_calculus(
            E, P, Q, m=config["m"], fb_kind=config["factor_base"], seed=seed,
            engine=config["engine"], accelerate=config["accelerate"],
            harvest=config["harvest"], target_window=config["window"],
            target_engine="fixed_window" if arm == "fixed_window" else "reference")
    finally:
        solver.decompose = decompose
        solver.build_factor_base = build_base
    elapsed = time.perf_counter_ns() - wall0
    cpu = time.process_time_ns() - cpu0
    return {"status": "completed", "seconds_full_solve": elapsed / 1e9,
            "cpu_seconds_full_solve": cpu / 1e9,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "full_curve_group_ops": E.ops.group_ops, "result": result.to_dict(),
            "targets_sha256": digest(targets), "relations_sha256": digest(relations),
            "factor_base_points": bases[0].points,
            "factor_base_sha256": digest(bases[0].points),
            "recorded_targets": len(targets)}


def run(out):
    from crypto_autoresearcher.index_calculus import generate_prime_order_curve

    config = json.loads(CONFIG.read_text())
    out.mkdir(parents=True, exist_ok=True)
    journal = (out / "arms.jsonl").open("x", encoding="utf-8")
    started = time.perf_counter()
    instances = {}
    for bits, curve_seed in itertools.product(config["bits"], config["curve_seeds"]):
        E, P = generate_prime_order_curve(bits, curve_seed)
        k = random.Random(f"target|{bits}|{curve_seed}|0").randrange(1, E.order)
        Q = E.mul(k, P)
        instances[f"{bits}:{curve_seed}"] = dict(
            p=E.p, a=E.a, b=E.b, order=E.order, P=P, Q=Q,
            bits=bits, curve_seed=curve_seed, public_expected_k=k)
    write_once(out / "instances.json", instances)
    rows = []
    grid = itertools.product(config["bits"], config["curve_seeds"],
                             config["solver_seeds"], range(config["repetitions"]))
    for index, (bits, curve_seed, seed, repetition) in enumerate(grid):
        instance_key = f"{bits}:{curve_seed}"
        pair = f"{instance_key}:{seed}:{repetition}"
        arms = config["arms"] if index % 2 == 0 else list(reversed(config["arms"]))
        for order, arm in enumerate(arms):
            key = dict(pair=pair, instance_key=instance_key, bits=bits,
                       curve_seed=curve_seed, solver_seed=seed, repetition=repetition,
                       arm=arm, order=order)
            argv = [sys.executable, str(Path(__file__).resolve()), "worker",
                    "--instances", str(out / "instances.json"), "--instance", instance_key,
                    "--seed", str(seed), "--arm", arm]
            try:
                child = subprocess.run(argv, capture_output=True, text=True,
                                       timeout=config["worker_timeout_seconds"])
                if child.returncode:
                    value = dict(status="error", returncode=child.returncode,
                                 stdout=child.stdout, stderr=child.stderr)
                else:
                    value = json.loads(child.stdout)
            except subprocess.TimeoutExpired as error:
                value = dict(status="timed_out", timeout_seconds=config["worker_timeout_seconds"],
                             stdout=str(error.stdout or ""), stderr=str(error.stderr or ""))
            row = key | value
            journal.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            journal.flush()
            rows.append(row)
            print(f"{pair} {arm}: {row['status']}", flush=True)
    journal.close()
    raw = dict(schema="crypto.autoresearch.ic_target_benchmark.v1", attack_claimed=False,
               config=config, config_sha256=digest(config), instances=instances, rows=rows,
               harness_seconds=time.perf_counter() - started,
               environment=dict(python=sys.version, platform=platform.platform(),
                                machine=platform.machine(), processor=platform.processor(),
                                cpu_count=os.cpu_count(), load_average=os.getloadavg(),
                                numpy=__import__("numpy").__version__),
               timing_scope="complete native solve including final verification; excludes public "
                            "instance generation, process startup, trace hashing and independent checker")
    write_once(out / "raw-result.json", raw)
    # The supervisor completes the reproducibility envelope from its own
    # launch facts, preserving the driver's original bytes in its receipt.
    with (out / "manifest.yaml").open("x") as stream:
        stream.write("run:\n  attack_claimed: false\n  metrics:\n    arm_executions: "
                     f"{len(rows)}\n  result:\n    certificate:\n      kind: none\n")


# Checker arithmetic deliberately imports neither Curve nor the target table.
def add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u:
        if (y + v) % p == 0:
            return None
        slope = (3 * x * x + a) * pow(2 * y, -1, p) % p
    else:
        slope = (v - y) * pow(u - x, -1, p) % p
    z = (slope * slope - x - u) % p
    return (z, (slope * (x - z) - y) % p)


def mul(k, P, p, a):
    # Left-to-right arithmetic is independent of the implementation's
    # right-to-left reference path and positional-window candidate.
    result = None
    for bit in bin(k)[2:]:
        result = add(result, result, p, a)
        if bit == "1":
            result = add(result, P, p, a)
    return result


def require(test, message):
    if not test:
        raise ValueError(message)


def verify_instance(instance):
    p, a, b, N = (instance[k] for k in ("p", "a", "b", "order"))
    for n in (p, N):
        require(n >= 3 and all(n % d for d in range(2, math.isqrt(n) + 1)), "non-prime instance")
    require(p != N and (4 * a**3 + 27 * b**2) % p != 0, "invalid toy curve")
    count = 1
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        count += 1 if rhs == 0 else (2 if pow(rhs, (p - 1) // 2, p) == 1 else 0)
    require(count == N, "independent curve order mismatch")
    for key in ("P", "Q"):
        x, y = instance[key]
        require(0 <= x < p and 0 <= y < p and (y*y - x**3 - a*x - b) % p == 0,
                "point outside curve")
        require(mul(N, (x, y), p, a) is None, "point outside subgroup")
    require(mul(instance["public_expected_k"], tuple(instance["P"]), p, a)
            == tuple(instance["Q"]), "public target certificate mismatch")


def check(raw):
    config = json.loads(CONFIG.read_text())
    require(raw["config"] == config and raw["config_sha256"] == digest(config), "workload changed")
    require(raw["attack_claimed"] is False, "unexpected attack claim")
    expected_instances = {f"{b}:{c}" for b, c in itertools.product(config["bits"], config["curve_seeds"])}
    require(set(raw["instances"]) == expected_instances, "instance grid mismatch")
    base_cache = {}
    for key, instance in raw["instances"].items():
        require(key == f"{instance['bits']}:{instance['curve_seed']}" and
                instance["p"].bit_length() == instance["bits"], "instance identity changed")
        verify_instance(instance)
        p, a, b, N = (instance[k] for k in ("p", "a", "b", "order"))
        roots = {y * y % p: y for y in range(1, (p + 1) // 2)}
        points = []
        size = max(4, math.ceil(math.sqrt(N) / 2))
        for x in range(p):
            y = roots.get((x**3 + a*x + b) % p)
            if y is not None:
                points.append([x, y])
            if len(points) == size:
                break
        base_cache[key] = points
    expected = {(b, c, s, r, arm) for b, c, s, r, arm in itertools.product(
        config["bits"], config["curve_seeds"], config["solver_seeds"],
        range(config["repetitions"]), config["arms"])}
    actual = [(r["bits"], r["curve_seed"], r["solver_seed"], r["repetition"], r["arm"])
              for r in raw["rows"]]
    require(len(actual) == len(expected) and set(actual) == expected, "missing/duplicate arm")
    pairs = {}
    target_cache = {}
    for row in raw["rows"]:
        require(row["instance_key"] == f"{row['bits']}:{row['curve_seed']}" and
                row["pair"] == f"{row['instance_key']}:{row['solver_seed']}:{row['repetition']}",
                "arm identity changed")
        require(row["status"] == "completed", "failed/censored arm retained; comparison not qualified")
        result = row["result"]
        instance = raw["instances"][row["instance_key"]]
        p, a, N = (instance[k] for k in ("p", "a", "order"))
        P, Q = tuple(instance["P"]), tuple(instance["Q"])
        k = result["k"]
        require(type(k) is int and 0 <= k < N and result["verified"], "unverified solve")
        require(mul(k, P, p, a) == Q, "independent recovered-log certificate failed")
        require(row["recorded_targets"] == result["attempts"], "target accounting mismatch")
        require(row["factor_base_sha256"] == digest(row["factor_base_points"]), "FB digest mismatch")
        points = row["factor_base_points"]
        size = len(base_cache[row["instance_key"]])
        require(len(points) == size == result["factor_base"]["size"], "FB size changed")
        require([point[0] for point in points] == sorted({point[0] for point in points}),
                "FB ordering changed")
        require(points == base_cache[row["instance_key"]], "small-x FB points/signs changed")
        cache_key = (row["instance_key"], row["solver_seed"], result["attempts"])
        if cache_key not in target_cache:
            rng = random.Random(f"ic|{p}|{a}|{instance['b']}|2|small_x|{row['solver_seed']}")
            targets, reference_ops, window_ops = [], 0, 0
            for _ in range(result["attempts"]):
                alpha, beta = rng.randrange(N), rng.randrange(1, N)
                targets.append(add(mul(alpha, P, p, a), mul(beta, Q, p, a), p, a))
                reference_ops += alpha.bit_length() + alpha.bit_count() + beta.bit_length() + beta.bit_count() + 1
                for scalar in (alpha, beta):
                    while scalar:
                        window_ops += bool(scalar & ((1 << config["window"]) - 1))
                        scalar >>= config["window"]
                window_ops += 1
            target_cache[cache_key] = (digest(targets), reference_ops, window_ops)
        target_hash, reference_ops, window_ops = target_cache[cache_key]
        require(row["targets_sha256"] == target_hash, "target stream changed")
        if row["arm"] == "fixed_window":
            remaining, additions, slots = N - 1, 0, 0
            while remaining:
                largest = min((1 << config["window"]) - 1, remaining)
                additions += largest - 1
                slots += largest + 1
                remaining >>= config["window"]
                if remaining:
                    additions += config["window"]
            require(result["target_setup_ops"] == 2 * additions and
                    result["target_table_entries"] == 2 * slots, "table accounting changed")
            require(result["target_ops"] == 2 * additions + window_ops, "target setup omitted")
        else:
            require(result["target_ops"] == reference_ops, "reference cost changed")
        for metric in ("seconds_full_solve", "cpu_seconds_full_solve", "peak_rss_bytes"):
            require(math.isfinite(row[metric]) and row[metric] > 0, "invalid measured metric")
        require(row["seconds_full_solve"] >= result["seconds_total"] > 0, "partial solve timing")
        pairs.setdefault(row["pair"], {})[row["arm"]] = row
    for pair, arms in pairs.items():
        old = arms["reference_a"]
        for other in (arms["reference_b"], arms["fixed_window"]):
            require(all(old["result"][k] == other["result"][k] for k in ARITHMETIC_KEYS),
                    f"arithmetic workload differs: {pair}")
            require(old["targets_sha256"] == other["targets_sha256"] and
                    old["relations_sha256"] == other["relations_sha256"], "relation stream differs")
            require(old["full_curve_group_ops"] - old["result"]["target_ops"] ==
                    other["full_curve_group_ops"] - other["result"]["target_ops"],
                    "non-target group work changed")
        for arm, row in arms.items():
            result = row["result"]
            require(result["target_engine"] == ("fixed_window" if arm == "fixed_window" else "reference"),
                    "wrong target arm")
            require(0 <= result["target_setup_ops"] <= result["target_ops"], "uncharged setup")
            if arm == "fixed_window":
                require(result["target_window"] == config["window"] and
                        result["target_setup_ops"] > 0 and result["target_table_entries"] > 0,
                        "missing fixed-base setup")
            else:
                require(result["target_setup_ops"] == result["target_table_entries"] == 0,
                        "reference gained a cache")
    return dict(schema="crypto.autoresearch.ic_target_validation.v1", valid=True,
                arm_executions=len(actual), matched_pairs=len(pairs),
                independent_checks=["prime field/order and exhaustive point count", "kP=Q",
                                    "every attempted target from frozen RNG", "paired relations and costs"],
                raw_sha256=digest(raw))


def summarize(raw):
    """Exactly the predeclared comparison; never filter slow/failed rows."""
    config = raw["config"]
    pairs = {}
    for row in raw["rows"]:
        require(row["status"] == "completed" and row["result"]["verified"], "unqualified summary")
        pairs.setdefault(row["pair"], {})[row["arm"]] = row
    logs, aa_logs, references, candidates, clusters = [], [], [], [], {}
    by_bits = {}
    for pair, arms in sorted(pairs.items()):
        A, B, C = (arms[name]["seconds_full_solve"] for name in
                   ("reference_a", "reference_b", "fixed_window"))
        reference = (A + B) / 2
        value = math.log(reference / C)
        logs.append(value)
        aa_logs.append(math.log(A / B))
        references.append(reference)
        candidates.append(C)
        row = arms["fixed_window"]
        clusters.setdefault((row["bits"], row["curve_seed"]), []).append(value)
        by_bits.setdefault(row["bits"], []).append(value)
    geomean = lambda values: math.exp(sum(math.log(v) for v in values) / len(values))
    speedup = math.exp(sum(logs) / len(logs))
    aa_factor = math.exp(abs(sum(aa_logs) / len(aa_logs)))
    rng = random.Random(config["bootstrap_seed"])
    boot = []
    for _ in range(config["bootstrap_replicates"]):
        values = []
        for bits in config["bits"]:
            for _ in config["curve_seeds"]:
                values.extend(clusters[(bits, rng.choice(config["curve_seeds"]))])
        boot.append(math.exp(sum(values) / len(values)))
    boot.sort()
    low = boot[math.floor(0.025 * (len(boot) - 1))]
    high = boot[math.ceil(0.975 * (len(boot) - 1))]
    return dict(matched_pairs=len(pairs), geometric_mean_speedup=speedup,
                reference_geomean_seconds=geomean(references),
                candidate_geomean_seconds=geomean(candidates),
                aa_factor=aa_factor, clustered_bootstrap_95_interval=[low, high],
                protocol_criterion_met=speedup > max(1.05, aa_factor) and low > 1,
                per_bits_speedup={str(bits): math.exp(sum(v) / len(v)) for bits, v in by_bits.items()})


def check_directory(directory):
    raw = json.loads((directory / "raw-result.json").read_text())
    report = check(raw)
    arm_rows = [json.loads(line) for line in (directory / "arms.jsonl").read_text().splitlines()]
    require(sorted(arm_rows, key=lambda r: (r["pair"], r["arm"])) ==
            sorted(raw["rows"], key=lambda r: (r["pair"], r["arm"])), "arm receipts disagree")
    # A known-false recovered log must be rejected by the same checker.
    import copy
    false = copy.deepcopy(raw)
    bad = false["rows"][0]
    N = false["instances"][bad["instance_key"]]["order"]
    bad["result"]["k"] = (bad["result"]["k"] + 1) % N
    try:
        check(false)
    except ValueError as error:
        require("recovered-log certificate" in str(error), "negative control failed for wrong reason")
    else:
        raise ValueError("checker accepted a known-false log")
    report["known_false_log_rejected"] = True
    report["summary"] = summarize(raw)
    # A synthetic known-false advantage must fail the very same criterion.
    equal = copy.deepcopy(raw)
    pairs = {}
    for row in equal["rows"]:
        pairs.setdefault(row["pair"], {})[row["arm"]] = row
    for arms in pairs.values():
        arms["fixed_window"]["seconds_full_solve"] = sum(
            arms[a]["seconds_full_solve"] for a in ("reference_a", "reference_b")) / 2
    require(not summarize(equal)["protocol_criterion_met"], "accepted known-false speedup")
    report["known_false_speedup_rejected"] = True
    path = directory / "validation.json"
    if path.exists():
        require(json.loads(path.read_text()) == report, "immutable validation receipt changed")
    else:
        write_once(path, report)
    print(json.dumps(report, sort_keys=True))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check")
    p.add_argument("--run-dir", type=Path, required=True)
    p = sub.add_parser("worker")
    p.add_argument("--instances", type=Path, required=True)
    p.add_argument("--instance", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--arm", choices=("reference_a", "fixed_window", "reference_b"), required=True)
    args = parser.parse_args(argv)
    if args.command == "run":
        run(args.out)
    elif args.command == "check":
        check_directory(args.run_dir)
    else:
        instance = json.loads(args.instances.read_text())[args.instance]
        print(json.dumps(worker(instance, args.seed, args.arm, json.loads(CONFIG.read_text()))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
