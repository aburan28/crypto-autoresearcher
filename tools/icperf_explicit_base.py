"""Prepare and check a target-blind prime-field coset factor-base candidate.

This is input preparation, not an index-calculus experiment. It records the
realized point set and setup resources. Complete IC comparisons must rerun and
charge preparation under a frozen protocol on unseen same-point targets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.index_calculus.curve import Curve, factorize  # noqa: E402
from crypto_autoresearcher.index_calculus.factor_base import FactorBase  # noqa: E402
from tools.icperf_prime_fixture import verify_record as verify_curve_record  # noqa: E402

SCHEMA = "icperf-explicit-coset-base-v1"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point_digest(points: list[tuple[int, int]]) -> str:
    digest = hashlib.sha256()
    for x, y in points:
        digest.update(x.to_bytes(8, "big"))
        digest.update(y.to_bytes(8, "big"))
    return digest.hexdigest()


def verify_base_record(record: dict, fixture_path: Path) -> None:
    if record.get("schema") != SCHEMA:
        raise ValueError("unknown base record schema")
    if record["curve_fixture_sha256"] != sha256_file(fixture_path):
        raise ValueError("curve fixture hash mismatch")
    fixture = json.loads(fixture_path.read_text())
    verify_curve_record(fixture)
    c = fixture["curve"]
    if record["curve"] != c:
        raise ValueError("curve identity mismatch")
    p = c["p"]
    params = record["base_parameters"]
    d, g, zeta = (params[name] for name in ("d", "coset", "zeta"))
    if any(type(v) is not int for v in (d, g, zeta)):
        raise ValueError("base parameters must be integers")
    if d < 1 or (p - 1) % d or not (1 <= g < p and 1 <= zeta < p):
        raise ValueError("invalid coset parameters")
    if pow(zeta, d, p) != 1 or any(pow(zeta, d // q, p) == 1 for q in factorize(d)):
        raise ValueError("zeta lacks exact order d")
    if params["divisor_source"] != "explicit" or params["root_draws"] < 1:
        raise ValueError("missing explicit-divisor preparation receipt")
    kind = record["kind"]
    if kind not in ("subgroup", "dickson"):
        raise ValueError("unknown base kind")
    if kind == "dickson" and params.get("c_draws", 0) < 1:
        raise ValueError("missing Dickson-parameter draw count")
    curve = Curve(p, c["a"], c["b"], c["order"])
    expected = []
    u = g
    for _ in range(d):
        if kind == "subgroup":
            x = u
        else:
            cc = params["c"]
            x = (u + cc * pow(u, -1, p)) % p
        point = curve.lift_x(x)
        if point is not None and point[1] != 0:
            expected.append(list(point))
        u = u * zeta % p
    if expected != record["points"]:
        raise ValueError("stored points differ from complete coset enumeration")
    if len({point[0] for point in expected}) != len(expected):
        raise ValueError("factor-base x coordinates repeat")
    if record["realized_size"] != len(expected):
        raise ValueError("realized size mismatch")
    if record["point_sha256"] != point_digest([tuple(point) for point in expected]):
        raise ValueError("point digest mismatch")


def prepare(fixture_path: Path, kind: str, d: int, target_size: int,
            seed: int) -> dict:
    fixture = json.loads(fixture_path.read_text())
    verify_curve_record(fixture)
    c = fixture["curve"]
    curve = Curve(c["p"], c["a"], c["b"], c["order"])
    source = Path(__file__)
    base_source = ROOT / "src/crypto_autoresearcher/index_calculus/factor_base.py"
    source_sha256 = sha256_file(source)
    base_source_sha256 = sha256_file(base_source)
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    if kind == "subgroup":
        base = FactorBase.subgroup(curve, target_size, seed, divisor=d)
    elif kind == "dickson":
        base = FactorBase.dickson(curve, target_size, seed, divisor=d)
    else:
        raise ValueError("kind must be subgroup or dickson")
    elapsed_wall = time.perf_counter() - start_wall
    elapsed_cpu = time.process_time() - start_cpu
    points = [list(point) for point in base.points]
    record = {
        "schema": SCHEMA,
        "kind": kind,
        "curve": c,
        "curve_fixture_sha256": sha256_file(fixture_path),
        "base_parameters": base.params,
        "realized_size": len(points),
        "points": points,
        "point_sha256": point_digest([tuple(point) for point in points]),
        "preparation": {
            "wall_seconds": elapsed_wall,
            "cpu_seconds": elapsed_cpu,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                              (1 if sys.platform == "darwin" else 1024),
            "loadavg_end": list(os.getloadavg()),
            "source_sha256": source_sha256,
            "factor_base_source_sha256": base_source_sha256,
            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       capture_output=True, text=True, check=True).stdout.strip(),
            "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"],
                                                 cwd=ROOT, capture_output=True,
                                                 text=True, check=True).stdout.splitlines(),
            "python_version": platform.python_version(),
        },
        "scope": "target-blind base construction and exact membership only; no relation or complete-cost claim",
    }
    verify_base_record(record, fixture_path)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("prepare")
    make.add_argument("--fixture", type=Path, required=True)
    make.add_argument("--kind", choices=("subgroup", "dickson"), required=True)
    make.add_argument("--divisor", type=int, required=True)
    make.add_argument("--target-size", type=int, required=True)
    make.add_argument("--seed", type=int, required=True)
    make.add_argument("--out", type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("--fixture", type=Path, required=True)
    check.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        record = prepare(args.fixture, args.kind, args.divisor,
                         args.target_size, args.seed)
        with args.out.open("x") as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
        print(json.dumps({"path": str(args.out), "realized_size": record["realized_size"],
                          "point_sha256": record["point_sha256"],
                          "status": "verified"}, sort_keys=True))
    else:
        verify_base_record(json.loads(args.path.read_text()), args.fixture)
        print(json.dumps({"path": str(args.path), "status": "verified"}, sort_keys=True))


if __name__ == "__main__":
    main()
