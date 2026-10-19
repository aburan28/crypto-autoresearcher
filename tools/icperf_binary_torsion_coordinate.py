"""Prepare a torsion-adapted affine input base on the certified binary curve.

This records deterministic factor-base inputs and group identities only. It
does not run a decomposition solver or measure an ECDLP speedup.
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
from tools.icperf_koblitz_subgroup_fixture import inv, mul  # noqa: E402
from tools.icperf_ordinary_binary_fixture import (FIELD_DEGREE, FIELD_POLYNOMIAL,
                                                   add, lift_x, on_curve, scale)  # noqa: E402

FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
K = 10
OFFSETS = tuple(j << K for j in range(1, 5))
CONTROL_SEED = 20261019
DOMAIN = b"icperf-binary-torsion-paired-control-v1"


def field_mul(a: int, b: int) -> int:
    return mul(a, b, FIELD_POLYNOMIAL)


def square(a: int) -> int:
    return field_mul(a, a)


def gamma_for(b: int) -> int:
    gamma = b
    for _ in range(FIELD_DEGREE - 2):
        gamma = square(gamma)
    assert square(square(gamma)) == b
    return gamma


def x_from_phi(value: int, gamma: int) -> int:
    assert value
    return field_mul(gamma, 1 ^ inv(value, FIELD_POLYNOMIAL))


def phi_from_x(x: int, gamma: int) -> int:
    assert x != gamma
    return field_mul(gamma, inv(x ^ gamma, FIELD_POLYNOMIAL))


def linearized_eval(coeffs: list[int], value: int) -> int:
    out, power = 0, value
    for coeff in coeffs:
        out ^= field_mul(coeff, power)
        power = square(power)
    return out


def linearized_coefficients() -> list[int]:
    coeffs = [1]
    for i in range(K):
        w = linearized_eval(coeffs, 1 << i)
        assert w
        next_coeffs = [0] * (len(coeffs) + 1)
        for j, coeff in enumerate(coeffs):
            next_coeffs[j] ^= field_mul(w, coeff)
            next_coeffs[j + 1] ^= square(coeff)
        coeffs = next_coeffs
    assert coeffs[-1] == 1
    return coeffs


def negative(point: tuple[int, int]) -> tuple[int, int]:
    return point[0], point[0] ^ point[1]


def digest(rows: list) -> str:
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def pphi3(t1: int, t2: int, t3: int, gamma: int) -> int:
    e1 = t1 ^ t2 ^ t3
    s3 = field_mul(field_mul(square(t1) ^ t1, square(t2) ^ t2), square(t3) ^ t3)
    return s3 ^ field_mul(gamma, square(e1))


def semaev3(x1: int, x2: int, x3: int, b: int) -> int:
    e2 = field_mul(x1, x2) ^ field_mul(x1, x3) ^ field_mul(x2, x3)
    return square(e2) ^ field_mul(field_mul(x1, x2), x3) ^ b


def scan(offset: int, coeffs: list[int], gamma: int, b: int, r: int,
         t2_point: tuple[int, int]) -> dict:
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    constant = linearized_eval(coeffs, offset)
    assert constant
    raw = {}
    exceptional = 0
    for v in range(1 << K):
        t = offset ^ v
        assert linearized_eval(coeffs, t) == constant
        x = x_from_phi(t, gamma)
        if not x or x == gamma:
            exceptional += 1
            continue
        assert phi_from_x(x, gamma) == t
        point = lift_x(x, b)
        if point is not None:
            raw[t] = point
    representatives = []
    projected = []
    pair_signs = []
    for t in sorted(raw):
        if t & 1:
            continue
        assert (t ^ 1) in raw
        p, p_pair = raw[t], raw[t ^ 1]
        assert add(p, t2_point, b) in (p_pair, negative(p_pair))
        image, paired_image = scale(4, p, b), scale(4, p_pair, b)
        assert image is not None and paired_image is not None
        assert scale(r, image, b) is None
        sign = 1 if paired_image == image else -1
        assert paired_image == (image if sign == 1 else negative(image))
        representatives.append([t, p[0], p[1]])
        projected.append(list(image))
        pair_signs.append(sign)
    assert len(raw) == 2 * len(representatives)
    assert len({p[0] for p in projected}) == len(projected)
    assert len({p[0] for p in raw.values()}) == len(raw)
    accepted_t = sorted(raw)
    return {"offset": offset, "attempted_phi": 1 << K,
            "affine_membership_constant": constant,
            "exceptional": exceptional, "nonliftable": (1 << K) - exceptional - len(raw),
            "raw_representatives": len(raw), "projected_columns": len(projected),
            "accepted_phi": accepted_t, "accepted_phi_sha256": digest(accepted_t),
            "selected_representatives": representatives,
            "selected_representatives_sha256": digest(representatives),
            "projected_points": projected, "projected_points_sha256": digest(projected),
            "pair_signs": pair_signs,
            "wall_seconds": time.perf_counter() - start_wall,
            "cpu_seconds": time.process_time() - start_cpu}


def control_draw(counter: int) -> int:
    blob = hashlib.sha256(DOMAIN + CONTROL_SEED.to_bytes(8, "big") +
                          counter.to_bytes(8, "big")).digest()
    return int.from_bytes(blob[:8], "big") & ((1 << FIELD_DEGREE) - 1)


def paired_random_control(size: int, gamma: int, b: int, t2_point: tuple[int, int]) -> dict:
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    counts = {"zero": 0, "exceptional": 0, "nonliftable": 0, "duplicate": 0,
              "projected_duplicate": 0, "accepted": 0}
    seen_x = set()
    seen_projected_x = set()
    representatives = []
    pair_signs = []
    draws = 0
    while len(representatives) < size:
        assert draws < 100_000
        x = control_draw(draws)
        draws += 1
        if x == 0:
            counts["zero"] += 1
            continue
        if x == gamma:
            counts["exceptional"] += 1
            continue
        if x in seen_x:
            counts["duplicate"] += 1
            continue
        p = lift_x(x, b)
        if p is None:
            counts["nonliftable"] += 1
            continue
        image = scale(4, p, b)
        assert image is not None
        if image[0] in seen_projected_x:
            counts["projected_duplicate"] += 1
            continue
        paired = add(p, t2_point, b)
        assert paired is not None and paired[0] != x
        canonical_paired = lift_x(paired[0], b)
        assert canonical_paired is not None
        paired_image = scale(4, canonical_paired, b)
        sign = 1 if paired_image == image else -1
        assert paired_image == (image if sign == 1 else negative(image))
        seen_x.update((x, paired[0]))
        seen_projected_x.add(image[0])
        representatives.append([x, p[1], paired[0], canonical_paired[1], image[0], image[1]])
        pair_signs.append(sign)
        counts["accepted"] += 1
    assert sum(counts.values()) == draws
    return {"seed": CONTROL_SEED, "domain": DOMAIN.decode(), "draws": draws,
            "counts": counts, "projected_columns": size, "raw_representatives": 2 * size,
            "paired_representatives": representatives, "pair_signs": pair_signs,
            "paired_representatives_sha256": digest(representatives),
            "wall_seconds": time.perf_counter() - start_wall,
            "cpu_seconds": time.process_time() - start_cpu}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture_bytes = FIXTURE.read_bytes()
    fixture = json.loads(fixture_bytes)
    b, r = fixture["b_polynomial_bits"], fixture["prime_order"]
    assert b == 31 and fixture["cofactor"] == 4
    gamma = gamma_for(b)
    t2_point = (0, square(gamma))
    assert on_curve(t2_point, b) and scale(2, t2_point, b) is None
    target_size = default_fb_size(r, 8)
    assert target_size == 287
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    coeffs = linearized_coefficients()
    assert all(linearized_eval(coeffs, v) == 0 for v in range(1 << K))
    scans = [scan(offset, coeffs, gamma, b, r, t2_point) for offset in OFFSETS]
    winner = min(scans, key=lambda row: (abs(row["projected_columns"] - target_size),
                                          row["offset"]))
    paired_control = paired_random_control(winner["projected_columns"], gamma, b, t2_point)

    reps = winner["selected_representatives"]
    true_checks, false_checks = [], []
    for i in range(32):
        p = tuple(reps[i][1:]); q = tuple(reps[i + 32][1:])
        third = add(p, q, b)
        assert third is not None and third[0] != gamma
        ts = [phi_from_x(point[0], gamma) for point in (p, q, third)]
        assert pphi3(*ts, gamma) == 0
        assert semaev3(p[0], q[0], third[0], b) == 0
        true_checks.append([reps[i][0], reps[i + 32][0], ts[2], third[0]])
        third_false = tuple(reps[i + 64][1:])
        tf = [phi_from_x(point[0], gamma) for point in (p, q, third_false)]
        assert pphi3(*tf, gamma) != 0
        assert semaev3(p[0], q[0], third_false[0], b) != 0
        false_checks.append([reps[i][0], reps[i + 32][0], reps[i + 64][0]])

    record = {"schema": "icperf-binary-torsion-coordinate-v1",
              "scope": "torsion-coordinate input and S3 identity only; no solver or ECDLP cost claim",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "curve": {"field_degree": FIELD_DEGREE, "field_polynomial": FIELD_POLYNOMIAL,
                        "b_polynomial_bits": b, "prime_order": r, "cofactor": 4},
              "coordinate": {"gamma": gamma, "gamma_squared": square(gamma),
                             "two_torsion": list(t2_point),
                             "definition": "phi(P)=gamma/(x(P)+gamma); x=gamma*(1+1/phi)",
                             "torsion_action": "phi(P+T2)=phi(P)+1"},
              "predeclared_selection": {"arity": 8, "subspace_dimension": K,
                                        "basis_bits": [1 << i for i in range(K)],
                                        "offsets": list(OFFSETS), "target_columns": target_size,
                                        "rule": "minimize absolute unique projected-column gap; tie by smaller offset"},
              "linearized_membership_coefficients": coeffs,
              "linearized_nonzero_terms": sum(c != 0 for c in coeffs),
              "candidate_scans": scans, "selected_offset": winner["offset"],
              "paired_random_control": paired_control,
              "three_point_controls": {"true": true_checks, "false": false_checks,
                                       "formula": "prod_i(phi_i^2+phi_i)+gamma*(sum_i phi_i)^2"},
              "preparation": {"wall_seconds": time.perf_counter() - start_wall,
                              "cpu_seconds": time.process_time() - start_cpu,
                              "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                                (1 if sys.platform == "darwin" else 1024),
                              "loadavg_end": list(os.getloadavg()),
                              "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                         capture_output=True, text=True, check=True).stdout.strip(),
                              "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                      capture_output=True, text=True, check=True).stdout.splitlines(),
                              "python_version": sys.version}}
    with args.out.open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "selected_offset": winner["offset"],
                      "raw_representatives": winner["raw_representatives"],
                      "projected_columns": winner["projected_columns"]}, sort_keys=True))


if __name__ == "__main__":
    main()
