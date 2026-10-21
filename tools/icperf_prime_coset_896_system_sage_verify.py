"""Independent Sage field and curve replay of frozen m=2..8 d=896 systems."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sage.all import EllipticCurve, GF, version

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "research/icperf_prime_coset_896_system_20261017/systems.json"
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eval_terms(terms: list[dict], values: list, field):
    total = field(0)
    for term in terms:
        value = field(term["coefficient"])
        for i, power in term["powers"]:
            value *= values[i] ** power
        total += value
    return total


def replay() -> dict:
    data = json.loads(SYSTEMS.read_bytes())
    scan = json.loads(SCAN.read_bytes())
    assert data["schema"] == "icperf-prime-coset-896-systems-v1"
    assert data["scan_sha256"] == sha(SCAN)
    assert data["source_sha256"] == sha(ROOT / "tools/icperf_prime_coset_896_system.py")
    assert data["encoder_sha256"] == sha(ROOT / "tools/icperf_prime_coset_quadratic.py")
    assert data["selected_seed"] == scan["selected_seed"]
    assert data["selected_point_sha256"] == scan["selected_point_sha256"]
    selected = next(a for a in scan["attempts"]
                    if a["base_parameters"]["seed"] == data["selected_seed"])
    c = data["curve"]
    assert c == scan["curve"] and data["base_size"] == len(selected["points"]) == 475
    field = GF(c["p"])
    curve = EllipticCurve(field, [c["a"], c["b"]])
    constant = field(data["coset_constant"])
    chain = data["addition_chain"]
    assert len(chain) == 11 and chain[-1]["out"] == 896
    known = {1}
    for step in chain:
        assert step["left"] in known and step["right"] in known
        assert step["out"] == step["left"] + step["right"]
        known.add(step["out"])
    checked = []
    assert [row["m"] for row in data["arities"]] == list(range(2, 9))
    for row in data["arities"]:
        m = row["m"]
        assert row["planted_input_points"] == selected["points"][:m]
        points = [curve(field(x), field(y)) for x, y in row["planted_input_points"]]
        target = sum(points, curve(0))
        assert [int(target[0]), int(target[1])] == row["planted_target"]
        values = [field(value) for value in row["planted_assignment"]]
        nd = row["direct"]["variable_count"]
        assert len(values) == row["lifted"]["variable_count"]
        assert all(field(x) ** 896 == constant for x, _ in row["planted_input_points"])
        for i, (x, _) in enumerate(row["planted_input_points"]):
            assert values[i] == field(x)
            for step in chain:
                name = f"q{i + 1}_{step['out']}"
                index = row["lifted"]["variables"].index(name)
                assert values[index] == field(x) ** step["out"]
        direct = [eval_terms(poly, values[:nd], field)
                  for poly in row["direct"]["equations"]]
        lifted = [eval_terms(poly, values, field)
                  for poly in row["lifted"]["equations"]]
        assert all(value == 0 for value in direct + lifted)
        altered = values[:]
        altered[nd] += field(1)
        rejected = sum(eval_terms(poly, altered, field) != 0
                       for poly in row["lifted"]["equations"])
        assert rejected == row["changed_auxiliary_nonzero_equations"] > 0
        checked.append({"m": m, "points_checked": len(points),
                        "direct_equations_zero": len(direct),
                        "lifted_equations_zero": len(lifted),
                        "changed_auxiliary_nonzero_equations": int(rejected)})
    return {"schema": "icperf-prime-coset-896-systems-sage-replay-v1",
            "scope": "independent planted field/curve checks at m2-m8; no Groebner run or ECDLP cost claim",
            "systems_sha256": sha(SYSTEMS), "source_sha256": sha(Path(__file__)),
            "scan_sha256": sha(SCAN), "sage_version": version(),
            "arities_checked": checked,
            "total_direct_equations_zero": sum(row["direct_equations_zero"] for row in checked),
            "total_lifted_equations_zero": sum(row["lifted_equations_zero"] for row in checked)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = replay()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"m_checked": [row["m"] for row in result["arities_checked"]],
                      "direct_zero": result["total_direct_equations_zero"],
                      "lifted_zero": result["total_lifted_equations_zero"]}, sort_keys=True))


if __name__ == "__main__":
    main()
