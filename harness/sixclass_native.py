"""Run a native six-class GLV rho worker and record an auditable receipt.

The walk lives in crypto's Rust worker. Python here only launches a pinned
binary, checks its bounded output, and independently verifies any proposed
discrete log. The receipt makes a null result explicit; a throughput result
from this BigUint research worker is not a secp256k1 campaign cost claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

SCHEMA = "crypto.autoresearch.sixclass-native.v1"
WALK = "six-class-rho-secp-tight-v2/rust1"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def add(p: int, a: int, left: tuple[int, int] | None,
        right: tuple[int, int] | None) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        den = 2 * y1 % p
        num = (3 * x1 * x1 + a) % p
    else:
        den = (x2 - x1) % p
        num = (y2 - y1) % p
    slope = num * pow(den, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def multiply(p: int, a: int, point: tuple[int, int], k: int):
    acc = None
    while k:
        if k & 1:
            acc = add(p, a, acc, point)
        point = add(p, a, point, point)
        k >>= 1
    return acc


def verify_log(job: dict, log: str) -> bool:
    curve = job["curve"]
    p, a, n = (int(curve[key], 16) for key in ("p", "a", "order"))
    g = tuple(int(curve["generator"][key], 16) for key in ("x", "y"))
    q = tuple(int(curve["target"][key], 16) for key in ("x", "y"))
    k = int(log, 16)
    return 0 <= k < n and multiply(p, a, g, k) == q


def verify_first_dp(job: dict, result: dict) -> bool:
    dp = result.get("first_dp")
    if dp is None:
        return result["distinguished"] == 0
    configured_cap = job["curve"]["max_steps_per_walker"]
    step_cap = min(configured_cap or (20 << job["curve"]["dp_bits"]), 1_000_000)
    if (result["distinguished"] < 1 or dp["job_id"] != result["job_id"]
            or not 0 <= dp["walker"] < result["walkers"]
            or not 0 <= dp["steps"] < step_cap):
        return False
    curve = job["curve"]
    p, a, n = (int(curve[key], 16) for key in ("p", "a", "order"))
    g = tuple(int(curve["generator"][key], 16) for key in ("x", "y"))
    q = tuple(int(curve["target"][key], 16) for key in ("x", "y"))
    x, y, u, v = (int(dp[key], 16) for key in ("x", "y", "a", "b"))
    if not (0 <= x < p and 0 <= y < p and 0 <= u < n and 0 <= v < n):
        return False
    beta = int(job["beta"], 16)
    if x != min(x, beta * x % p, beta * beta * x % p) or y > p - y:
        return False
    branches = curve["num_branches"]
    if branches < 2 or branches & (branches - 1):
        return False
    branch_bits = branches.bit_length() - 1
    if (y >> branch_bits) & ((1 << curve["dp_bits"]) - 1):
        return False
    return add(p, a, multiply(p, a, g, u), multiply(p, a, q, v)) == (x, y)


def receipt_for_result(job_path: Path, worker: Path, walkers: int,
                       elapsed_ns: int, result: dict) -> dict:
    job = json.loads(job_path.read_text())
    if walkers < 1 or elapsed_ns < 0:
        raise ValueError("walkers must be positive and elapsed time nonnegative")
    required = {"job_id", "walkers", "class_visits", "distinguished",
                "short_cycle_escapes", "log"}
    if (not required.issubset(result) or not 0 <= result["walkers"] <= walkers
            or not 0 <= result["distinguished"] <= result["walkers"]):
        raise ValueError("worker output lacks six-class campaign fields")
    if not verify_first_dp(job, result):
        raise ValueError("worker returned an invalid first distinguished point")
    proposed = result["log"]
    if proposed is not None and not verify_log(job, proposed):
        raise ValueError("worker returned an invalid discrete logarithm")
    return {"schema": SCHEMA, "walk": WALK, "job_sha256": digest(job_path),
            "worker_sha256": digest(worker), "requested_walkers": walkers,
            "elapsed_ns": elapsed_ns, "result": result,
            "independent_dp_check": result.get("first_dp") is not None,
            "independent_log_check": proposed is not None,
            "scope": "native BigUint toy/research worker; no secp256k1 throughput claim"}


def validate_trail_audit(job: Path, record: Path, result: dict, audit: dict) -> None:
    if (audit.get("schema") != "crypto.sixclass.trail-audit.v1"
            or audit.get("job_sha256") != digest(job)
            or audit.get("record_sha256") != digest(record)
            or audit.get("verified") is not True
            or audit.get("walker") != result["walker"]
            or audit.get("steps") != result["steps"]):
        raise ValueError("native trail audit is not bound to the record and job")


def execute(job_path: Path, worker: Path, walkers: int, timeout: int) -> dict:
    if walkers < 1 or timeout < 1:
        raise ValueError("walkers and timeout must be positive")
    start = time.monotonic_ns()
    completed = subprocess.run([str(worker), str(job_path), str(walkers)],
                               check=True, capture_output=True, text=True,
                               timeout=timeout)
    elapsed = time.monotonic_ns() - start
    receipt = receipt_for_result(job_path, worker, walkers, elapsed,
                                 json.loads(completed.stdout))
    dp = receipt["result"].get("first_dp")
    if dp is not None:
        with tempfile.TemporaryDirectory(prefix="sixclass-audit-") as directory:
            record = Path(directory) / "dp.json"
            record.write_text(json.dumps(dp, sort_keys=True))
            audit = subprocess.run([str(worker), "audit", str(job_path), str(record)],
                                   check=True, capture_output=True, text=True,
                                   timeout=timeout)
            native = json.loads(audit.stdout)
            validate_trail_audit(job_path, record, dp, native)
            receipt["native_trail_audit"] = native
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--walkers", type=int, required=True)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = execute(args.job.resolve(), args.worker.resolve(),
                      args.walkers, args.timeout)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=args.out.parent,
                                     prefix=".sixclass-", delete=False) as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2)
        stream.write("\n")
        name = stream.name
    os.replace(name, args.out)
    print(json.dumps({"receipt": str(args.out), "result": receipt["result"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
