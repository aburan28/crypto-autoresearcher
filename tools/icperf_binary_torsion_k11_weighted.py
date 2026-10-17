"""Prepare a target-blind k=11 torsion base with a paired Hamming cut.

Frozen before generation: offsets 2048, 4096, 6144, 8192; keep t=c+v
when the ten bits v>>1 have Hamming weight <=5. The low bit is unrestricted
so t and t+1 remain paired. Choose the offset whose realized projected
column count is closest to the exact m=8 signed-multiset saturation threshold
for the certified prime subgroup, breaking ties by smaller offset. This is
input preparation, not a solver experiment or an ECDLP speed claim.
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
from tools.icperf_binary_torsion_coordinate import (digest, field_mul, gamma_for,
                                                    linearized_eval, negative,
                                                    paired_random_control,
                                                    phi_from_x, pphi3, semaev3,
                                                    square, x_from_phi)  # noqa: E402
from tools.icperf_ordinary_binary_fixture import (FIELD_DEGREE, FIELD_POLYNOMIAL,
                                                   add, lift_x, on_curve, scale)  # noqa: E402

FIXTURE = ROOT / "research/icperf_ordinary_binary_fixture_20261017/fixture.json"
PARENT = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
K = 11
WEIGHT_LIMIT = 5
OFFSETS = (2048, 4096, 6144, 8192)


def linearized_coefficients(k: int) -> list[int]:
    coeffs = [1]
    for i in range(k):
        w = linearized_eval(coeffs, 1 << i)
        assert w
        nxt = [0] * (len(coeffs) + 1)
        for j, coeff in enumerate(coeffs):
            nxt[j] ^= field_mul(w, coeff)
            nxt[j + 1] ^= square(coeff)
        coeffs = nxt
    assert coeffs[-1] == 1
    return coeffs


def scan(offset: int, coeffs: list[int], gamma: int, b: int, r: int,
         t2: tuple[int, int]) -> dict:
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    constant = linearized_eval(coeffs, offset)
    assert constant
    accepted = {}
    exceptional = nonliftable = 0
    for v in range(1 << K):
        if (v >> 1).bit_count() > WEIGHT_LIMIT:
            continue
        t = offset ^ v
        assert linearized_eval(coeffs, t) == constant
        x = x_from_phi(t, gamma)
        if x == 0 or x == gamma:
            exceptional += 1
            continue
        assert phi_from_x(x, gamma) == t
        p = lift_x(x, b)
        if p is None:
            nonliftable += 1
        else:
            accepted[t] = p
    reps, projected, pair_signs = [], [], []
    for t in sorted(accepted):
        if t & 1:
            continue
        assert (t ^ 1) in accepted
        p, p_pair = accepted[t], accepted[t ^ 1]
        assert add(p, t2, b) in (p_pair, negative(p_pair))
        image, paired_image = scale(4, p, b), scale(4, p_pair, b)
        assert image is not None and paired_image is not None
        assert scale(r, image, b) is None
        sign = 1 if paired_image == image else -1
        assert paired_image == (image if sign == 1 else negative(image))
        reps.append([t, p[0], p[1]])
        projected.append(list(image))
        pair_signs.append(sign)
    assert len(accepted) == 2 * len(reps)
    assert len({p[0] for p in projected}) == len(projected)
    assert len({p[0] for p in accepted.values()}) == len(accepted)
    attempted = 2 * sum(math.comb(10, j) for j in range(WEIGHT_LIMIT + 1))
    assert attempted == 1276
    assert len(accepted) + nonliftable + exceptional == attempted
    return {"offset": offset, "affine_membership_constant": constant,
            "affine_space_size": 1 << K, "hamming_cut_attempts": attempted,
            "hamming_cut_rejected": (1 << K) - attempted,
            "exceptional": exceptional, "nonliftable": nonliftable,
            "raw_representatives": len(accepted), "projected_columns": len(projected),
            "accepted_phi": sorted(accepted), "accepted_phi_sha256": digest(sorted(accepted)),
            "selected_representatives": reps,
            "selected_representatives_sha256": digest(reps),
            "projected_points": projected, "projected_points_sha256": digest(projected),
            "pair_signs": pair_signs,
            "wall_seconds": time.perf_counter() - started_wall,
            "cpu_seconds": time.process_time() - started_cpu}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture_blob, parent_blob = FIXTURE.read_bytes(), PARENT.read_bytes()
    fixture, parent = json.loads(fixture_blob), json.loads(parent_blob)
    b, r = fixture["b_polynomial_bits"], fixture["prime_order"]
    assert b == 31 and fixture["cofactor"] == 4
    gamma = gamma_for(b)
    t2 = (0, square(gamma))
    assert on_curve(t2, b) and scale(2, t2, b) is None
    threshold = next(B for B in range(1, 1000) if math.comb(2 * B + 7, 8) >= r)
    assert threshold == 311
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    coeffs = linearized_coefficients(K)
    assert all(linearized_eval(coeffs, v) == 0 for v in range(1 << K))
    scans = [scan(offset, coeffs, gamma, b, r, t2) for offset in OFFSETS]
    selected = min(scans, key=lambda row: (abs(row["projected_columns"] - threshold), row["offset"]))
    control = paired_random_control(selected["projected_columns"], gamma, b, t2)
    reps = selected["selected_representatives"]
    true, false = [], []
    for i in range(32):
        p, q = tuple(reps[i][1:]), tuple(reps[i + 32][1:])
        third = add(p, q, b)
        assert third is not None and third[0] != gamma
        ts = [phi_from_x(point[0], gamma) for point in (p, q, third)]
        assert pphi3(*ts, gamma) == 0
        assert semaev3(p[0], q[0], third[0], b) == 0
        true.append([reps[i][0], reps[i + 32][0], ts[2], third[0]])
        other = tuple(reps[i + 64][1:])
        tf = [phi_from_x(point[0], gamma) for point in (p, q, other)]
        assert pphi3(*tf, gamma) != 0
        assert semaev3(p[0], q[0], other[0], b) != 0
        false.append([reps[i][0], reps[i + 32][0], reps[i + 64][0]])
    output = {"schema": "icperf-binary-torsion-k11-weighted-v1",
              "scope": "target-blind factor-base input and point/formula checks; no relation yield, solver or speed claim",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_blob).hexdigest(),
              "parent_base_sha256": hashlib.sha256(parent_blob).hexdigest(),
              "parent_source_sha256": parent["source_sha256"],
              "curve": {"field_degree": FIELD_DEGREE, "field_polynomial": FIELD_POLYNOMIAL,
                        "b_polynomial_bits": b, "prime_order": r, "cofactor": 4},
              "coordinate": {"gamma": gamma, "two_torsion": list(t2),
                             "definition": "phi(P)=gamma/(x(P)+gamma)",
                             "torsion_action": "phi(P+T2)=phi(P)+1"},
              "predeclared_selection": {"arity": 8, "subspace_dimension": K,
                                        "basis_bits": [1 << i for i in range(K)],
                                        "offsets": list(OFFSETS), "weight_bits": "v>>1 (10 bits)",
                                        "weight_limit": WEIGHT_LIMIT,
                                        "rule": "closest realized projected columns to exact m8 saturation threshold; tie by smaller offset",
                                        "target_columns": threshold,
                                        "target_origin": "first B with binomial(2B+7,8) >= prime subgroup order"},
              "linearized_membership_coefficients": coeffs,
              "linearized_nonzero_terms": sum(c != 0 for c in coeffs),
              "candidate_scans": scans, "selected_offset": selected["offset"],
              "paired_random_control": control,
              "three_point_controls": {"true": true, "false": false,
                                       "formula": "prod_i(phi_i^2+phi_i)+gamma*(sum_i phi_i)^2"},
              "preparation": {"wall_seconds": time.perf_counter() - started_wall,
                              "cpu_seconds": time.process_time() - started_cpu,
                              "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                                (1 if sys.platform == "darwin" else 1024),
                              "loadavg_end": list(os.getloadavg()),
                              "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                         capture_output=True, text=True, check=True).stdout.strip(),
                              "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                      capture_output=True, text=True, check=True).stdout.splitlines(),
                              "python_version": sys.version}}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"selected_offset": selected["offset"],
                      "projected_columns": selected["projected_columns"],
                      "offset_columns": {row["offset"]: row["projected_columns"] for row in scans},
                      "threshold": threshold}, sort_keys=True))


if __name__ == "__main__":
    main()
