"""Count exact Boolean ANF input support for two m=8 binary chain forms.

This constructs the input equations only. It performs no Groebner, SAT,
Macaulay, relation, rank, or ECDLP solve.
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
from tools.icperf_koblitz_subgroup_fixture import mul  # noqa: E402
from tools.icperf_ordinary_binary_fixture import FIELD_POLYNOMIAL  # noqa: E402

PHI_BASE = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
X_BASE = ROOT / "research/icperf_binary_projected_base_20261017/base.json"
CHAIN = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
N = 61
TRIAL_SEED = 20261020
TRIALS = 8


def fmul(a: int, b: int) -> int:
    return mul(a, b, FIELD_POLYNOMIAL)


def add(*polys: dict[int, int]) -> dict[int, int]:
    out = {}
    for poly in polys:
        for mask, coeff in poly.items():
            value = out.get(mask, 0) ^ coeff
            if value:
                out[mask] = value
            else:
                out.pop(mask, None)
    return out


def times(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
    if len(a) > len(b):
        a, b = b, a
    out = {}
    for mask_a, coeff_a in a.items():
        for mask_b, coeff_b in b.items():
            mask = mask_a | mask_b  # Boolean quotient: v_i^2 = v_i
            value = out.get(mask, 0) ^ fmul(coeff_a, coeff_b)
            if value:
                out[mask] = value
            else:
                out.pop(mask, None)
    return out


def square(a: dict[int, int]) -> dict[int, int]:
    return {mask: fmul(coeff, coeff) for mask, coeff in a.items()}


def multiply_constant(a: dict[int, int], c: int) -> dict[int, int]:
    return {mask: fmul(coeff, c) for mask, coeff in a.items()}


def constant(c: int) -> dict[int, int]:
    return {0: c} if c else {}


def variable(offset: int, width: int, first_bit: int) -> dict[int, int]:
    poly = constant(offset)
    for j in range(width):
        poly[1 << (first_bit + j)] = 1 << j
    return poly


def phi3(a: dict[int, int], b: dict[int, int], c: dict[int, int], gamma: int):
    linearized = [add(square(v), v) for v in (a, b, c)]
    product = times(times(linearized[0], linearized[1]), linearized[2])
    return add(product, multiply_constant(square(add(a, b, c)), gamma))


def semaev3(a: dict[int, int], b: dict[int, int], c: dict[int, int], curve_b: int):
    e2 = add(times(a, b), times(a, c), times(b, c))
    return add(square(e2), times(times(a, b), c), constant(curve_b))


def equations(kind: str, k: int, offset: int, target: int, gamma: int):
    base = [variable(offset, k, i*k) for i in range(8)]
    full = [variable(0, N, 8*k + i*N) for i in range(6)]
    triple = [[base[0], base[1], full[0]]]
    triple += [[full[i-1], base[i+1], full[i]] for i in range(1, 6)]
    triple += [[full[-1], base[-1], constant(target)]]
    build = (lambda values: phi3(*values, gamma)) if kind == "torsion_phi" else (lambda values: semaev3(*values, 31))
    return [build(values) for values in triple]


def support_digest(poly: dict[int, int], nvars: int) -> str:
    h = hashlib.sha256()
    mask_bytes = (nvars + 7) // 8
    for mask, coeff in sorted(poly.items()):
        h.update(mask.to_bytes(mask_bytes, "big"))
        h.update(coeff.to_bytes(8, "big"))
    return h.hexdigest()


def support_stats(poly: dict[int, int], nvars: int) -> dict:
    per_bit = [0] * N
    by_degree = {}
    for mask, coeff in poly.items():
        degree = mask.bit_count()
        bits = coeff.bit_count()
        by_degree[degree] = by_degree.get(degree, 0) + bits
        for j in range(N):
            per_bit[j] += (coeff >> j) & 1
    assert sum(per_bit) == sum(by_degree.values())
    return {"unique_field_monomials": len(poly),
            "coefficient_bit_terms": sum(per_bit),
            "boolean_degree_bit_terms": {str(k): v for k, v in sorted(by_degree.items())},
            "max_boolean_input_degree": max(by_degree, default=0),
            "per_output_bit_terms": per_bit,
            "support_sha256": support_digest(poly, nvars)}


def trial_mask(kind: str, index: int, nvars: int) -> int:
    domain = b"icperf-binary-anf-support-v1:" + kind.encode() + b":"
    digest = hashlib.shake_256(domain + TRIAL_SEED.to_bytes(8, "big") +
                                  index.to_bytes(4, "big")).digest((nvars+7)//8)
    return int.from_bytes(digest, "big") & ((1 << nvars)-1)


def eval_anf(poly: dict[int, int], assignment: int) -> int:
    result = 0
    for mask, coeff in poly.items():
        if mask & assignment == mask:
            result ^= coeff
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    phi_bytes, x_bytes, chain_bytes = (path.read_bytes() for path in
                                       (PHI_BASE, X_BASE, CHAIN))
    phi_base, x_base, chain = (json.loads(blob) for blob in
                               (phi_bytes, x_bytes, chain_bytes))
    assert phi_base["curve"] == x_base["curve"] == chain["curve"]
    assert chain["base_sha256"] == hashlib.sha256(phi_bytes).hexdigest()
    gamma = phi_base["coordinate"]["gamma"]
    target = chain["raw_sum"]
    configs = [
        ("torsion_phi", 10, phi_base["selected_offset"],
         chain["target_channel_phi"][chain["selected_channel"]]),
        ("classical_raw_x", 9, x_base["selected_offset"], target[0]),
    ]
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    arms = []
    for kind, k, offset, target_coordinate in configs:
        nvars = 8*k + 6*N
        start_wall, start_cpu = time.perf_counter(), time.process_time()
        polys = equations(kind, k, offset, target_coordinate, gamma)
        assert len(polys) == 7
        stats = [support_stats(poly, nvars) for poly in polys]
        trial_rows = []
        for trial in range(TRIALS):
            mask = trial_mask(kind, trial, nvars)
            trial_rows.append({"assignment_hex": hex(mask),
                               "field_equation_values": [eval_anf(poly, mask) for poly in polys]})
        arms.append({"kind": kind, "base_dimension": k,
                     "selected_offset": offset, "target_coordinate": target_coordinate,
                     "boolean_variables": nvars, "field_equations": 7,
                     "boolean_coefficient_equations": 7*N,
                     "equation_stats": stats,
                     "total_coefficient_bit_terms": sum(row["coefficient_bit_terms"] for row in stats),
                     "trial_rows": trial_rows,
                     "wall_seconds": time.perf_counter() - start_wall,
                     "cpu_seconds": time.process_time() - start_cpu})
    record = {"schema": "icperf-binary-boolean-support-v1",
              "scope": "exact input ANF support; no solver, degree of regularity, relation or speed claim",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "phi_base_sha256": hashlib.sha256(phi_bytes).hexdigest(),
              "x_base_sha256": hashlib.sha256(x_bytes).hexdigest(),
              "chain_sha256": hashlib.sha256(chain_bytes).hexdigest(),
              "curve": chain["curve"], "target_raw_sum": target,
              "formulae": {"torsion_phi": "prod_i(t_i^2+t_i)+gamma*(sum_i t_i)^2",
                            "classical_raw_x": "(x1*x2+x1*x3+x2*x3)^2+x1*x2*x3+b"},
              "boolean_quotient": "v_i^2=v_i; monomial masks OR under multiplication",
              "support_encoding": "sorted monomial mask as ceil(nvars/8) big-endian bytes followed by 8-byte big-endian GF(2^61) coefficient",
              "trial_seed": TRIAL_SEED, "arms": arms,
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
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "terms": {a["kind"]: a["total_coefficient_bit_terms"] for a in arms}}, sort_keys=True))


if __name__ == "__main__":
    main()
