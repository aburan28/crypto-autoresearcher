"""Create a private-answer Curve Smash secp256k1 challenge for the native worker.

The committed upstream target profile defines the distribution. This module is
only harness orchestration and point generation; the rho walk runs in Rust.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets

from harness.sixclass_native import multiply, verify_log

PROFILE = Path(__file__).resolve().parent / "fixtures/curvesmash_secp256k1_profile.json"
PROFILE_SHA256 = "18c3338de676f1909715814325bffdb1513f1621d678b942e8a7a9563b8fd086"
SOURCE_REVISION = "1f084c1914c81a0cdc830b176453adba5dc19ab9"
BETA = "7ae96a2b657c07106e64479eac3434e99cf0497512f58995c1396c28719501ee"
LAMBDA = "5363ad4cc05c30e0a5261c028812645a122e22ea20816678df02967c1b23bd72"


def profile() -> dict:
    raw = PROFILE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROFILE_SHA256:
        raise ValueError("Curve Smash secp256k1 target profile changed")
    return json.loads(raw)


def draw_scalar(order: int) -> int:
    """Exact 256-bit rejection sampling, including the possible zero draw."""
    while True:
        value = int.from_bytes(secrets.token_bytes(32), "big")
        if value < order:
            return value


def make_job(scalar: int, *, seed: int, dp_bits: int = 8,
             max_steps: int = 2048) -> dict:
    target = profile()
    p = int(target["field_modulus"], 16)
    n = int(target["subgroup_order"], 16)
    if not 0 < scalar < n:
        raise ValueError("native worker requires a nonidentity target and scalar < order")
    if not 0 <= seed < 2**64 or not 1 <= dp_bits < 64 or max_steps < 1:
        raise ValueError("invalid bounded native-walk parameters")
    g = target["generator_P"]
    point = multiply(p, 0, (int(g["x"], 16), int(g["y"], 16)), scalar)
    assert point is not None
    q = {"x": f"{point[0]:064x}", "y": f"{point[1]:064x}"}
    job = {
        "curve": {
            "version": 1, "name": "curvesmash-secp256k1-ecdlp", "p": target["field_modulus"],
            "a": "0", "b": "7", "generator": g, "target": q,
            "order": target["subgroup_order"], "dp_bits": dp_bits,
            "num_branches": 32, "negation_map": False, "unit_size": 256,
            "max_steps_per_walker": max_steps, "seed": seed,
        },
        "beta": BETA, "lambda": LAMBDA,
    }
    assert verify_log(job, f"{scalar:x}")
    return job


def write_exclusive(path: Path, obj: dict, *, private: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600 if private else 0o644)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path, help="public Rust worker job")
    parser.add_argument("--audit", required=True, type=Path, help="private scalar record")
    parser.add_argument("--seed", type=int, default=7, help="public walk seed")
    parser.add_argument("--dp-bits", type=int, default=8)
    parser.add_argument("--max-steps", type=int, default=2048)
    args = parser.parse_args()
    if args.job.resolve() == args.audit.resolve():
        parser.error("public job and private audit paths must differ")
    if args.audit.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        parser.error("private audit path must be outside the repository")
    n = int(profile()["subgroup_order"], 16)
    scalar = draw_scalar(n)
    if scalar == 0:
        raise ValueError("uniform draw was zero; native worker has no infinity target")
    job = make_job(scalar, seed=args.seed, dp_bits=args.dp_bits,
                   max_steps=args.max_steps)
    raw_job = (json.dumps(job, indent=2, sort_keys=True) + "\n").encode()
    audit = {
        "schema": "crypto.autoresearch.sixclass-private-challenge.v1",
        "source_revision": SOURCE_REVISION, "target_profile_sha256": PROFILE_SHA256,
        "public_job_sha256": hashlib.sha256(raw_job).hexdigest(),
        "scalar": f"{scalar:064x}",
    }
    if args.job.exists() or args.audit.exists():
        raise FileExistsError("challenge outputs must be new paths")
    write_exclusive(args.audit, audit, private=True)
    write_exclusive(args.job, job, private=False)
    print(json.dumps({"job": str(args.job), "audit": str(args.audit),
                      "job_sha256": audit["public_job_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
