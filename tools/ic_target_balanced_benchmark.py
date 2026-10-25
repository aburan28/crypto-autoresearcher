"""Held-out IC trial with treatment crossed with every execution slot.

The original EXP-ICPERF-3065f9 remains unchanged. This successor reuses its
arithmetic worker/checker, adds a balanced schedule, pins all workers to the
same allowed CPU, and binds the pre-run environment. Launch only through the
successor's approved experiment_execution.py trial plan.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib.metadata
import itertools
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import ic_target_benchmark as base

CONFIG = ROOT / "config/ic-target-balanced-benchmark.json"


def environment():
    return dict(python=platform.python_version(), implementation=platform.python_implementation(),
                platform=platform.platform(), machine=platform.machine(), cpu_count=os.cpu_count(),
                allowed_affinity=sorted(os.sched_getaffinity(0)),
                packages=sorted((d.metadata.get("Name", "unknown").lower(), d.version)
                                for d in importlib.metadata.distributions()),
                cpu_model=next((line.split(":", 1)[1].strip() for line in
                                Path("/proc/cpuinfo").read_text().splitlines()
                                if line.startswith("model name")), "unavailable"))


def process_census():
    """Names and cumulative CPU ticks, without command arguments or environment."""
    rows = []
    for entry in sorted(Path("/proc").iterdir()):
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
            rest = stat[stat.rfind(")") + 2:].split()
            rows.append(dict(pid=int(entry.name), name=(entry / "comm").read_text().strip(),
                             user_ticks=int(rest[11]), system_ticks=int(rest[12])))
        except (OSError, ValueError, IndexError):
            continue
    return rows


def order_for(config, seed, repetition):
    arms = list(config["arms"])
    if config["solver_seeds"].index(seed) % 2:
        arms.reverse()
    offset = repetition % len(arms)
    return arms[offset:] + arms[:offset]


def check_balance(raw):
    config = json.loads(CONFIG.read_text())
    base.require(raw["config"] == config, "balanced workload changed")
    expected_lock = json.loads((ROOT / config["environment_lock"]).read_text())
    base.require(raw["environment_lock"] == expected_lock and
                 raw["environment_sha256"] == base.digest(expected_lock), "environment lock changed")
    slots = {}
    for row in raw["rows"]:
        expected = order_for(config, row["solver_seed"], row["repetition"])
        base.require(type(row["order"]) is int and 0 <= row["order"] < len(expected) and
                     expected[row["order"]] == row["arm"], "execution slot changed")
        base.require(row["worker_affinity"] == [min(expected_lock["allowed_affinity"])],
                     "worker CPU affinity changed")
        base.require(row["environment_sha256"] == raw["environment_sha256"],
                     "worker dependency/environment changed")
        for metric in ("load_before", "load_after"):
            base.require(len(row[metric]) == 3 and all(type(x) in (int, float) and x >= 0
                                                      for x in row[metric]), "missing host load")
        key = (row["bits"], row["curve_seed"], row["solver_seed"], row["arm"])
        slots.setdefault(key, []).append(row["order"])
    expected_count = len(config["bits"]) * len(config["curve_seeds"]) * len(config["solver_seeds"]) * 3
    base.require(len(slots) == expected_count and all(sorted(v) == [0, 1, 2] for v in slots.values()),
                 "treatment is not crossed with all execution slots")
    return dict(schema="crypto.autoresearch.ic_target_balance.v1", valid=True,
                arm_cell_groups=len(slots), positions_per_arm_cell=[0, 1, 2],
                environment_sha256=raw["environment_sha256"], raw_sha256=base.digest(raw))


@contextmanager
def successor_config():
    # The original checker is reused byte-for-byte. Its CONFIG selects the
    # exact workload, so override only that Path within this single-threaded
    # checker process, restore it afterwards, and bind both source files.
    prior = base.CONFIG
    try:
        base.CONFIG = CONFIG
        yield
    finally:
        base.CONFIG = prior


def run(out):
    from crypto_autoresearcher.index_calculus import generate_prime_order_curve

    config = json.loads(CONFIG.read_text())
    lock = json.loads((ROOT / config["environment_lock"]).read_text())
    base.require(base.digest(environment()) == base.digest(lock), "pre-run environment differs from lock")
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    before = dict(load_average=os.getloadavg(), processes=process_census())
    instances = {}
    for bits, curve_seed in itertools.product(config["bits"], config["curve_seeds"]):
        E, P = generate_prime_order_curve(bits, curve_seed)
        k = random.Random(f"target|{bits}|{curve_seed}|0").randrange(1, E.order)
        instances[f"{bits}:{curve_seed}"] = dict(p=E.p, a=E.a, b=E.b, order=E.order,
            P=P, Q=E.mul(k, P), bits=bits, curve_seed=curve_seed, public_expected_k=k)
    base.write_once(out / "instances.json", instances)
    rows = []
    with (out / "arms.jsonl").open("x", encoding="utf-8") as journal:
        grid = itertools.product(config["bits"], config["curve_seeds"],
                                 config["solver_seeds"], range(config["repetitions"]))
        for bits, curve_seed, seed, repetition in grid:
            instance_key = f"{bits}:{curve_seed}"
            pair = f"{instance_key}:{seed}:{repetition}"
            for order, arm in enumerate(order_for(config, seed, repetition)):
                argv = [sys.executable, str(Path(__file__).resolve()), "worker", "--instances",
                        str(out / "instances.json"), "--instance", instance_key,
                        "--seed", str(seed), "--arm", arm]
                key = dict(pair=pair, instance_key=instance_key, bits=bits, curve_seed=curve_seed,
                           solver_seed=seed, repetition=repetition, arm=arm, order=order)
                try:
                    child = subprocess.run(argv, capture_output=True, text=True,
                                           timeout=config["worker_timeout_seconds"])
                    value = json.loads(child.stdout) if child.returncode == 0 else dict(
                        status="error", returncode=child.returncode, stdout=child.stdout, stderr=child.stderr)
                except subprocess.TimeoutExpired as error:
                    value = dict(status="timed_out", timeout_seconds=config["worker_timeout_seconds"],
                                 stdout=str(error.stdout or ""), stderr=str(error.stderr or ""))
                row = key | value
                rows.append(row)
                journal.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
                journal.flush()
                print(f"{pair} slot{order} {arm}: {row['status']}", flush=True)
    raw = dict(schema="crypto.autoresearch.ic_target_balanced_benchmark.v1", attack_claimed=False,
               config=config, config_sha256=base.digest(config), environment_lock=lock,
               environment_sha256=base.digest(lock), environment_before=before,
               environment_after=dict(load_average=os.getloadavg(), processes=process_census()),
               instances=instances, rows=rows, harness_seconds=time.perf_counter() - started,
               environment=lock,
               timing_scope="same complete solve boundary as original worker; setup, misses, LA and "
                            "final verification included; startup/telemetry/hashing/checker excluded")
    base.write_once(out / "raw-result.json", raw)
    with (out / "manifest.yaml").open("x") as stream:
        stream.write(f"run:\n  attack_claimed: false\n  metrics:\n    arm_executions: {len(rows)}\n"
                     "  result:\n    certificate:\n      kind: none\n")


def check_directory(directory):
    raw = json.loads((directory / "raw-result.json").read_text())
    report = check_balance(raw)
    with successor_config():
        base.check_directory(directory)
    # The same schedule checker must reject the original middle-only design.
    import copy
    false = copy.deepcopy(raw)
    for row in false["rows"]:
        row["order"] = {"reference_a": 0, "fixed_window": 1, "reference_b": 2}[row["arm"]]
    try:
        check_balance(false)
    except ValueError:
        report["known_confounded_schedule_rejected"] = True
    else:
        raise ValueError("accepted known-confounded execution schedule")
    path = directory / "balance-validation.json"
    if path.exists():
        base.require(json.loads(path.read_text()) == report, "balance receipt changed")
    else:
        base.write_once(path, report)
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run"); p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check"); p.add_argument("--run-dir", type=Path, required=True)
    p = sub.add_parser("worker")
    p.add_argument("--instances", type=Path, required=True)
    p.add_argument("--instance", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--arm", choices=("reference_a", "fixed_window", "reference_b"), required=True)
    args = parser.parse_args()
    if args.command == "run":
        run(args.out)
    elif args.command == "check":
        check_directory(args.run_dir)
    else:
        lock = json.loads((ROOT / json.loads(CONFIG.read_text())["environment_lock"]).read_text())
        actual = environment()
        base.require(base.digest(actual) == base.digest(lock), "worker environment differs from lock")
        os.sched_setaffinity(0, {min(lock["allowed_affinity"])})
        before = os.getloadavg()
        result = base.worker(json.loads(args.instances.read_text())[args.instance], args.seed,
                             args.arm, json.loads(CONFIG.read_text()))
        result.update(worker_affinity=sorted(os.sched_getaffinity(0)), load_before=before,
                      load_after=os.getloadavg(), environment_sha256=base.digest(actual))
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
