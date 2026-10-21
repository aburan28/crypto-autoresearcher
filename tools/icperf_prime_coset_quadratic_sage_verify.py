"""Independent Sage field and curve replay of the archived quadratic-coset input."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sage.all import EllipticCurve, GF, version

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = ROOT / "research/icperf_prime_coset_quadratic_20261017/system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_terms(terms: list[dict], assignment: list, field):
    result = field(0)
    for term in terms:
        value = field(term["coefficient"])
        for i, power in term["powers"]:
            value *= assignment[i] ** power
        result += value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = json.loads(SYSTEM.read_bytes())
    p, a, b = (record["curve"][name] for name in ("p", "a", "b"))
    field = GF(p)
    curve = EllipticCurve(field, [a, b])
    points = [curve(field(x), field(y)) for x, y in record["planted_input_points"]]
    target = sum(points, curve(0))
    assert [int(target[0]), int(target[1])] == record["planted_target"]
    values = [field(value) for value in record["planted_assignment"]]
    direct_values = values[:record["direct"]["variable_count"]]
    direct_residuals = [evaluate_terms(poly, direct_values, field)
                        for poly in record["direct"]["equations"]]
    lifted_residuals = [evaluate_terms(poly, values, field)
                        for poly in record["lifted"]["equations"]]
    assert all(value == 0 for value in direct_residuals + lifted_residuals)
    altered = values[:]
    gate_index = record["direct"]["variable_count"]
    altered[gate_index] += field(1)
    rejected = sum(evaluate_terms(poly, altered, field) != 0
                   for poly in record["lifted"]["equations"])
    assert rejected > 0
    d, c = record["coset_order"], field(record["coset_constant"])
    assert all(field(x) ** d == c for x, _ in record["planted_input_points"])
    result = {"schema": "icperf-prime-coset-quadratic-sage-replay-v1",
              "scope": "independent planted input field/curve check; no Groebner run",
              "system_sha256": sha(SYSTEM), "source_sha256": sha(Path(__file__)),
              "sage_version": version(), "field_characteristic": int(field.characteristic()),
              "m": record["m"], "curve_points_checked": len(points),
              "direct_equations_zero": len(direct_residuals),
              "lifted_equations_zero": len(lifted_residuals),
              "changed_auxiliary_nonzero_equations": int(rejected),
              "point_sum_matches_planted_target": True}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"direct_zero": len(direct_residuals),
                      "lifted_zero": len(lifted_residuals),
                      "changed_auxiliary_rejected": rejected}, sort_keys=True))


if __name__ == "__main__":
    main()
