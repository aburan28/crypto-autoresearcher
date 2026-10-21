"""Prepare an all-liftable affine binary base with exact cofactor projection.

Every raw point with x in the selected affine F_2 space is a factor-base
representative. Its unknown log is that of [4]P in the prime subgroup. Four
explicit torsion target channels give all raw preimages of a subgroup target
under [4]. This is deterministic input and correctness preparation, not an
ECDLP performance trial.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
from tools.icperf_ordinary_binary_fixture import (FIELD_DEGREE, FIELD_POLYNOMIAL,
                                                   add, lift_x, on_curve, scale)  # noqa: E402

FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
K = 9
OFFSETS = tuple(j << K for j in range(1, 5))
CONTROL_SEED = 20261018
DOMAIN = b"icperf-binary-projected-random-v1"


def field_mul(a: int, b: int) -> int:
    return mul(a, b, FIELD_POLYNOMIAL)


def linearized_eval(coeffs: list[int], value: int) -> int:
    result = 0
    power = value
    for c in coeffs:
        result ^= field_mul(c, power)
        power = field_mul(power, power)
    return result


def linearized_coefficients() -> list[int]:
    coeffs = [1]
    for i in range(K):
        w = linearized_eval(coeffs, 1 << i)
        assert w
        next_coeffs = [0] * (len(coeffs) + 1)
        for j, c in enumerate(coeffs):
            next_coeffs[j] ^= field_mul(w, c)
            next_coeffs[j + 1] ^= field_mul(c, c)
        coeffs = next_coeffs
    assert len(coeffs) == K + 1 and coeffs[-1] == 1
    return coeffs


def digest_points(points: list[list[int]]) -> str:
    digest = hashlib.sha256()
    for x, y in points:
        digest.update(x.to_bytes(8, "big"))
        digest.update(y.to_bytes(8, "big"))
    return digest.hexdigest()


def scan(offset: int, b: int, coeffs: list[int]) -> dict:
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    constant = linearized_eval(coeffs, offset)
    assert constant
    raw_points = []
    for v in range(1 << K):
        x = offset ^ v
        assert x and linearized_eval(coeffs, x) == constant
        point = lift_x(x, b)
        if point is not None:
            assert on_curve(point, b)
            raw_points.append(list(point))
    assert len({p[0] for p in raw_points}) == len(raw_points)
    return {"offset": offset, "affine_membership_constant": constant,
            "attempted_x": 1 << K, "nonliftable": (1 << K) - len(raw_points),
            "realized_size": len(raw_points), "raw_point_sha256": digest_points(raw_points),
            "raw_points": raw_points,
            "wall_seconds": time.perf_counter() - start_wall,
            "cpu_seconds": time.process_time() - start_cpu}


def projected(points: list[list[int]], b: int, r: int) -> list[list[int]]:
    output = []
    for raw in points:
        point = scale(4, tuple(raw), b)
        assert point is not None and on_curve(point, b)
        assert scale(r, point, b) is None
        output.append(list(point))
    assert len({p[0] for p in output}) == len(output)  # no sign-folded collision
    return output


def control_draw(counter: int) -> int:
    digest = hashlib.sha256(DOMAIN + CONTROL_SEED.to_bytes(8, "big") +
                            counter.to_bytes(8, "big")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << FIELD_DEGREE) - 1)


def random_control(size: int, b: int, r: int) -> dict:
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    counts = {"zero": 0, "duplicate": 0, "nonliftable": 0, "accepted": 0}
    seen = set()
    raw_points = []
    draws = 0
    while len(raw_points) < size:
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
        point = lift_x(x, b)
        if point is None:
            counts["nonliftable"] += 1
        else:
            raw_points.append(list(point))
            counts["accepted"] += 1
    assert sum(counts.values()) == draws
    projected_points = projected(raw_points, b, r)
    return {"seed": CONTROL_SEED, "domain": DOMAIN.decode(), "draws": draws,
            "counts": counts, "realized_size": size, "raw_points": raw_points,
            "raw_point_sha256": digest_points(raw_points),
            "projected_points": projected_points,
            "projected_point_sha256": digest_points(projected_points),
            "wall_seconds": time.perf_counter() - start_wall,
            "cpu_seconds": time.process_time() - start_cpu}


def negative(point: tuple[int, int] | None):
    return None if point is None else (point[0], point[0] ^ point[1])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture_bytes = FIXTURE.read_bytes()
    fixture = json.loads(fixture_bytes)
    assert fixture["field_degree"] == FIELD_DEGREE
    assert fixture["field_polynomial"] == FIELD_POLYNOMIAL
    b, r = fixture["b_polynomial_bits"], fixture["prime_order"]
    target_size = default_fb_size(r, 8)
    assert target_size == 287 and fixture["cofactor"] == 4
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    coeffs = linearized_coefficients()
    assert all(linearized_eval(coeffs, v) == 0 for v in range(1 << K))
    scans = [scan(offset, b, coeffs) for offset in OFFSETS]
    winner = min(scans, key=lambda row: (abs(row["realized_size"] - target_size), row["offset"]))
    raw_points = winner["raw_points"]
    projected_points = projected(raw_points, b, r)
    control = random_control(len(raw_points), b, r)

    source = tuple(fixture["source_point"])
    torsion = scale(r, source, b)
    assert torsion is not None and scale(2, torsion, b) is not None
    assert scale(4, torsion, b) is None
    torsion_points = [None, torsion, scale(2, torsion, b), scale(3, torsion, b)]
    assert len({p for p in torsion_points}) == 4
    inv4 = pow(4, -1, r)
    generator = tuple(fixture["generator"])
    assert scale(4, scale(inv4, generator, b), b) == generator

    # Known-answer channel control: every raw preimage projects to the same
    # subgroup target, and a planted raw sum occupies exactly one channel.
    q_public = scale(17, generator, b)
    target = add(scale(7, generator, b), scale(11, q_public, b), b)
    root = scale(inv4, target, b)
    channels = [add(root, t, b) for t in torsion_points]
    assert len(set(channels)) == 4
    assert all(scale(4, channel, b) == target for channel in channels)
    planted_raw = None
    planted_projected = None
    for raw, projected_point in zip(raw_points[:3], projected_points[:3]):
        planted_raw = add(planted_raw, tuple(raw), b)
        planted_projected = add(planted_projected, tuple(projected_point), b)
    assert scale(4, planted_raw, b) == planted_projected
    planted_root = scale(inv4, planted_projected, b)
    planted_channels = [add(planted_root, t, b) for t in torsion_points]
    assert planted_channels.count(planted_raw) == 1
    planted_index = planted_channels.index(planted_raw)

    record = {"schema": "icperf-binary-projected-base-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "arithmetic_source_sha256": hashlib.sha256((ROOT / "tools/icperf_ordinary_binary_fixture.py").read_bytes()).hexdigest(),
              "default_size_source_sha256": hashlib.sha256((ROOT / "src/crypto_autoresearcher/index_calculus/factor_base.py").read_bytes()).hexdigest(),
              "curve": {"field_degree": FIELD_DEGREE, "field_polynomial": FIELD_POLYNOMIAL,
                        "b_polynomial_bits": b, "prime_order": r, "cofactor": 4},
              "predeclared_selection": {"arity": 8, "subspace_dimension": K,
                                        "basis_bits": [1 << i for i in range(K)],
                                        "offsets": list(OFFSETS), "target_size": target_size,
                                        "rule": "minimize absolute realized-size gap; tie by smaller offset"},
              "linearized_membership_coefficients": coeffs,
              "linearized_nonzero_terms": sum(c != 0 for c in coeffs),
              "candidate_scans": scans, "selected_offset": winner["offset"],
              "selected_projected_points": projected_points,
              "selected_projected_point_sha256": digest_points(projected_points),
              "random_control": control,
              "torsion": {"generator": list(torsion),
                          "points": [None if t is None else list(t) for t in torsion_points],
                          "order": 4, "inverse_cofactor_mod_r": inv4},
              "channel_controls": {"known_scalar": 17, "a": 7, "b": 11,
                                   "public_q": list(q_public), "target": list(target),
                                   "root": list(root),
                                   "channels": [list(p) for p in channels],
                                   "planted_raw_sum": list(planted_raw),
                                   "planted_projected_sum": list(planted_projected),
                                   "planted_channel_index": planted_index},
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
              "scope": "raw affine base, cofactor projection and channel correctness only; no IC performance claim"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "selected_offset": winner["offset"],
                      "realized_size": winner["realized_size"],
                      "planted_channel": planted_index}, sort_keys=True))


if __name__ == "__main__":
    main()
