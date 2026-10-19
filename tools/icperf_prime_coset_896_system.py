"""Freeze planted m=2..8 chained-S3 inputs for the selected d=896 base.

The systems are correctness/control inputs, not solver results or natural
relations. Every coefficient, exponent, planted assignment and point sum is
serialized in one write-once record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from crypto_autoresearcher.index_calculus.curve import Curve  # noqa: E402
from crypto_autoresearcher.index_calculus.factor_base import FactorBase  # noqa: E402
from crypto_autoresearcher.index_calculus.msolve import evaluate  # noqa: E402
from tools.icperf_prime_coset_quadratic import (  # noqa: E402
    lift_system, planted_values, serialize,
)

SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
ENCODER = ROOT / "tools/icperf_prime_coset_quadratic.py"
SEED = 20261017


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_record() -> dict:
    scan = json.loads(SCAN.read_bytes())
    assert scan["schema"] == "icperf-prime-coset-896-search-v1"
    selected = next(item for item in scan["attempts"]
                    if item["base_parameters"]["seed"] == scan["selected_seed"])
    assert selected["realized_size"] == scan["selected_realized_size"] == 475
    c = scan["curve"]
    curve = Curve(c["p"], c["a"], c["b"], c["order"])
    base = FactorBase("subgroup", [tuple(point) for point in selected["points"]],
                      dict(selected["base_parameters"]), curve.p)
    assert base.params["d"] == 896 and len(base) == 475
    rows = []
    target = None
    for m in range(2, 9):
        if m == 2:
            target = curve.add(base.points[0], base.points[1])
        else:
            target = curve.add(target, base.points[m - 1])
        if target is None:
            raise ValueError(f"planted m={m} sum is infinity")
        lifted, direct, chain, indices = lift_system(curve, base, target[0], m, SEED)
        points, checked_target, values = planted_values(
            curve, base, lifted, direct, chain, indices, m)
        assert checked_target == target
        assert all(evaluate(poly, values, curve.p) == 0 for poly in lifted.polys)
        assert all(evaluate(poly, values[:len(direct.names)], curve.p) == 0
                   for poly in direct.polys)
        altered = values[:]
        altered[len(direct.names)] = (altered[len(direct.names)] + 1) % curve.p
        rejected = sum(evaluate(poly, altered, curve.p) != 0 for poly in lifted.polys)
        assert rejected > 0
        rows.append({"m": m, "planted_input_points": [list(point) for point in points],
                     "planted_target": list(target), "planted_assignment": values,
                     "direct": serialize(direct), "lifted": serialize(lifted),
                     "changed_auxiliary_nonzero_equations": rejected})
    assert len(chain) == 11
    return {"schema": "icperf-prime-coset-896-systems-v1",
            "scope": "exact planted m2-m8 input systems; no Groebner run, relation yield or ECDLP cost claim",
            "source_sha256": sha(Path(__file__)), "encoder_sha256": sha(ENCODER),
            "scan_sha256": sha(SCAN), "curve": c, "coset_order": 896,
            "coset_constant": pow(base.params["coset"], 896, curve.p),
            "base_size": len(base), "selected_seed": scan["selected_seed"],
            "selected_point_sha256": scan["selected_point_sha256"],
            "separating_form_seed": SEED,
            "addition_chain": [{"out": out, "left": left, "right": right}
                               for out, left, right in chain],
            "arities": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = build_record()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"arities": [row["m"] for row in record["arities"]],
                      "m8_lifted_variables": record["arities"][-1]["lifted"]["variable_count"],
                      "m8_lifted_equations": record["arities"][-1]["lifted"]["equation_count"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
