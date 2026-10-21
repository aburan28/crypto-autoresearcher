"""Prepare one target-blind affine-subspace factor-base candidate and control.

On the certified ordinary-binary GF(2^61) curve, scan four fixed 11-dimensional
affine F_2 subspaces of x coordinates. Keep only x with a lifted point in the
prime-order subgroup, including both signs implicitly. Select the realized
size nearest the m=8 default and generate an equal-size random-x control.
This prepares inputs; it does not run index calculus or measure degree of
regularity, relation yield, rank, or ECDLP cost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from crypto_autoresearcher.index_calculus.factor_base import default_fb_size  # noqa: E402
from tools.icperf_koblitz_subgroup_fixture import mul  # noqa: E402
from tools.icperf_koblitz_size_screen import prime64  # noqa: E402
from tools.icperf_ordinary_binary_fixture import (FIELD_DEGREE, FIELD_POLYNOMIAL,
                                                   lift_x, on_curve, scale)  # noqa: E402

FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
K = 11
OFFSETS = tuple(j << K for j in range(1, 5))
CONTROL_SEED = 20261017
DOMAIN = b"icperf-binary-random-control-v1"


def field_mul(a: int, b: int) -> int:
    return mul(a, b, FIELD_POLYNOMIAL)


def field_square(a: int) -> int:
    return field_mul(a, a)


def linearized_coefficients() -> list[int]:
    coeffs = [1]  # Q_0(X)=X.
    for i in range(K):
        basis = 1 << i
        w = linearized_eval(coeffs, basis)
        assert w != 0
        next_coeffs = [0] * (len(coeffs) + 1)
        for j, c in enumerate(coeffs):
            next_coeffs[j] ^= field_mul(w, c)
            next_coeffs[j + 1] ^= field_square(c)
        coeffs = next_coeffs
    assert coeffs[-1] == 1
    return coeffs


def linearized_eval(coeffs: list[int], x: int) -> int:
    result = 0
    power = x
    for c in coeffs:
        result ^= field_mul(c, power)
        power = field_square(power)
    return result


def point_digest(points: list[list[int]]) -> str:
    digest = hashlib.sha256()
    for x, y in points:
        digest.update(x.to_bytes(8, "big"))
        digest.update(y.to_bytes(8, "big"))
    return digest.hexdigest()


def eligible_point(x: int, b: int, r: int):
    p = lift_x(x, b)
    if p is None:
        return None, "nonliftable"
    if scale(r, p, b) is not None:
        return None, "outside_subgroup"
    assert on_curve(p, b)
    return p, "accepted"


def scan_offset(offset: int, b: int, r: int, coeffs: list[int]) -> dict:
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    constant = linearized_eval(coeffs, offset)
    assert constant != 0
    points = []
    counts = {"nonliftable": 0, "outside_subgroup": 0, "accepted": 0}
    for v in range(1 << K):
        x = offset ^ v
        assert x != 0 and linearized_eval(coeffs, x) == constant
        p, status = eligible_point(x, b, r)
        counts[status] += 1
        if p is not None:
            points.append(list(p))
    assert sum(counts.values()) == 1 << K
    return {"offset": offset, "affine_membership_constant": constant,
            "attempted_x": 1 << K, "counts": counts,
            "realized_size": len(points), "point_sha256": point_digest(points),
            "points": points,
            "wall_seconds": time.perf_counter() - start_wall,
            "cpu_seconds": time.process_time() - start_cpu}


def control_draw(counter: int) -> int:
    digest = hashlib.sha256(DOMAIN + CONTROL_SEED.to_bytes(8, "big") +
                            counter.to_bytes(8, "big")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << FIELD_DEGREE) - 1)


def random_control(size: int, b: int, r: int) -> dict:
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    seen = set()
    counts = {"zero": 0, "duplicate": 0, "nonliftable": 0,
              "outside_subgroup": 0, "accepted": 0}
    points = []
    draws = 0
    while len(points) < size:
        assert draws < 100_000
        x = control_draw(draws)
        draws += 1
        if x == 0:
            counts["zero"] += 1
            continue
        if x in seen:
            counts["duplicate"] += 1
            continue
        seen.add(x)
        p, status = eligible_point(x, b, r)
        counts[status] += 1
        if p is not None:
            points.append(list(p))
    assert sum(counts.values()) == draws
    return {"seed": CONTROL_SEED, "domain": DOMAIN.decode(), "draws": draws,
            "counts": counts, "realized_size": size,
            "point_sha256": point_digest(points), "points": points,
            "wall_seconds": time.perf_counter() - start_wall,
            "cpu_seconds": time.process_time() - start_cpu}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture_bytes = FIXTURE.read_bytes()
    fixture = json.loads(fixture_bytes)
    assert fixture["field_degree"] == FIELD_DEGREE
    assert fixture["field_polynomial"] == FIELD_POLYNOMIAL
    b, r = fixture["b_polynomial_bits"], fixture["prime_order"]
    field_multiplicative_order = (1 << FIELD_DEGREE) - 1
    assert prime64(field_multiplicative_order)
    target_size = default_fb_size(r, 8)
    assert target_size == 287
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    coeffs = linearized_coefficients()
    assert len(coeffs) == K + 1
    for v in range(1 << K):
        assert linearized_eval(coeffs, v) == 0
    scans = [scan_offset(offset, b, r, coeffs) for offset in OFFSETS]
    winner = min(scans, key=lambda row: (abs(row["realized_size"] - target_size), row["offset"]))
    control = random_control(winner["realized_size"], b, r)
    record = {"schema": "icperf-binary-subspace-base-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "arithmetic_source_sha256": hashlib.sha256((ROOT / "tools/icperf_ordinary_binary_fixture.py").read_bytes()).hexdigest(),
              "default_size_source_sha256": hashlib.sha256((ROOT / "src/crypto_autoresearcher/index_calculus/factor_base.py").read_bytes()).hexdigest(),
              "curve": {"field_degree": FIELD_DEGREE, "field_polynomial": FIELD_POLYNOMIAL,
                        "b_polynomial_bits": b, "prime_order": r},
              "field_multiplicative_group": {"order": field_multiplicative_order,
                                             "prime64": True,
                                             "prime_check_source_sha256": hashlib.sha256((ROOT / "tools/icperf_koblitz_size_screen.py").read_bytes()).hexdigest()},
              "predeclared_selection": {"arity": 8, "subspace_dimension": K,
                                        "basis_bits": [1 << i for i in range(K)],
                                        "offsets": list(OFFSETS),
                                        "target_size": target_size,
                                        "rule": "minimize absolute realized-size gap; tie by smaller offset"},
              "linearized_membership_coefficients": coeffs,
              "linearized_nonzero_terms": sum(c != 0 for c in coeffs),
              "candidate_scans": scans, "selected_offset": winner["offset"],
              "random_control": control,
              "preparation": {"wall_seconds": time.perf_counter() - start_wall,
                              "cpu_seconds": time.process_time() - start_cpu,
                              "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                                (1 if sys.platform == "darwin" else 1024),
                              "loadavg_end": list(os.getloadavg()),
                              "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                         capture_output=True, text=True, check=True).stdout.strip(),
                              "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                      capture_output=True, text=True, check=True).stdout.splitlines(),
                              "python_version": sys.version},
              "scope": "target-blind base and equal-size control construction; no relation, solver, or ECDLP cost claim"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "selected_offset": winner["offset"],
                      "realized_size": winner["realized_size"],
                      "control_size": control["realized_size"]}, sort_keys=True))


if __name__ == "__main__":
    main()
