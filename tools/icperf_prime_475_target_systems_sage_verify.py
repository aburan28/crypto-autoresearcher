"""Independent Sage replay of common targets and exact three-arm systems."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from sage.all import EllipticCurve, GF, PolynomialRing, version

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "research/icperf_prime_475_target_systems_20261017/systems.json.gz"
FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
CONTROLS = ROOT / "research/icperf_prime_475_controls_20261017/controls.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_poly(terms: list[dict], ring):
    result = ring(0)
    generators = ring.gens()
    for term in terms:
        monomial = ring(term["coefficient"])
        for i, exponent in term["powers"]:
            monomial *= generators[i] ** exponent
        result += monomial
    return result


def s3(x, y, z, a, b):
    return (x-y)**2*z**2 - 2*((x+y)*(x*y+a)+2*b)*z + (x*y-a)**2 - 4*b*(x+y)


def check_direct(row, target_x, expected_coeffs, field, curve_a, curve_b):
    m = row["m"]
    data = row["encodings"]["direct"]
    names = data["variables"]
    assert len(names) == data["variable_count"] == 2*m-1
    assert len(data["equations"]) == data["equation_count"] == 2*m
    ring = PolynomialRing(field, names=names)
    vars_ = ring.gens()
    x = vars_[:m]
    u = vars_[m:-1]
    a, b = field(curve_a), field(curve_b)
    membership = sum((field(coefficient)*x[0]**int(power)
                      for power, coefficient in expected_coeffs.items()), ring(0))
    for i in range(m):
        expected = membership.subs({x[0]: x[i]})
        assert as_poly(data["equations"][i], ring) == expected
    if m == 2:
        expected_s3 = [s3(x[0], x[1], field(target_x), a, b)]
    else:
        expected_s3 = [s3(x[0], x[1], u[0], a, b)]
        expected_s3.extend(s3(u[k-1], x[k+1], u[k], a, b)
                           for k in range(1, m-2))
        expected_s3.append(s3(u[-1], x[-1], field(target_x), a, b))
    for i, expected in enumerate(expected_s3, m):
        assert as_poly(data["equations"][i], ring) == expected
    form = as_poly(data["equations"][-1], ring)
    assert form.degree() == 1 and form.derivative(vars_[-1]) == 1
    assert form.subs({variable: 0 for variable in vars_}) == 0
    assert data["monomial_occurrences"] == sum(len(eq) for eq in data["equations"])
    assert data["max_total_degree"] == max(
        sum(power for _, power in term["powers"])
        for eq in data["equations"] for term in eq)
    return m


def check_lift(row, field, constant):
    m = row["m"]
    direct = row["encodings"]["direct"]
    lifted = row["encodings"]["quadratic_lift"]
    assert lifted["variable_count"] == (2*m-1) + 11*m
    assert lifted["equation_count"] == 13*m
    ring = PolynomialRing(field, names=lifted["variables"])
    names = {name: variable for name, variable in zip(lifted["variables"], ring.gens())}
    chain = [(2,1,1),(3,2,1),(6,3,3),(7,6,1),(14,7,7),
             (28,14,14),(56,28,28),(112,56,56),(224,112,112),
             (448,224,224),(896,448,448)]
    for i in range(m):
        powers = {1: names[f"x{i+1}"]}
        for j, (out, left, right) in enumerate(chain):
            powers[out] = names[f"q{i+1}_{out}"]
            assert as_poly(lifted["equations"][12*i+j], ring) == (powers[out] - powers[left]*powers[right])
        assert as_poly(lifted["equations"][12*i+11], ring) == powers[896] - field(constant)
    for i, equation in enumerate(direct["equations"][m:]):
        assert lifted["equations"][12*m+i] == equation
    assert lifted["monomial_occurrences"] == sum(len(eq) for eq in lifted["equations"])


def replay() -> dict:
    with gzip.open(SYSTEMS, "rt") as stream:
        data = json.load(stream)
    fixture, scan, controls = (json.loads(path.read_bytes())
                               for path in (FIXTURE, SCAN, CONTROLS))
    assert data["schema"] == "icperf-prime-475-target-systems-v1"
    for key, path in (("fixture_sha256", FIXTURE), ("scan_sha256", SCAN),
                      ("controls_sha256", CONTROLS),
                      ("source_sha256", ROOT / "tools/icperf_prime_475_target_systems.py"),
                      ("encoder_sha256", ROOT / "tools/icperf_prime_coset_quadratic.py"),
                      ("msolve_source_sha256", ROOT / "src/crypto_autoresearcher/index_calculus/msolve.py")):
        assert data[key] == sha(path)
    c = data["curve"]
    assert c == fixture["curve"] == scan["curve"] == controls["curve"]
    field = GF(c["p"])
    curve = EllipticCurve(field, [c["a"], c["b"]])
    generator = curve(*data["generator"])
    assert data["generator"] == fixture["witness"] and c["order"]*generator == curve(0)
    selected = next(a for a in scan["attempts"]
                    if a["base_parameters"]["seed"] == scan["selected_seed"])
    base_points = {"coset": selected["points"]}
    expected_coeffs = {"coset": {"0": -pow(selected["base_parameters"]["coset"],896,c["p"]) % c["p"], "896": 1}}
    for control in controls["controls"]:
        base_points[control["kind"]] = control["points"]
        expected_coeffs[control["kind"]] = control["membership_coefficients"]
    assert set(base_points) == {"coset", "random", "small_x"}
    for points in base_points.values():
        assert len(points) == 475
        assert all(curve(*point) != curve(0) for point in points)
    assert len(data["targets"]) == 7 and len(data["systems"]) == 21
    checked = []
    for target in data["targets"]:
        m = target["m"]
        assert m in range(2, 9)
        digest = hashlib.sha256(f"{data['target_domain']}|{sha(FIXTURE)}|{m}".encode()).digest()
        scalar = 1 + int.from_bytes(digest, "big") % (c["order"]-1)
        assert target["derivation_sha256"] == digest.hex() and target["scalar"] == scalar
        point = scalar*generator
        assert target["point"] == [int(point[0]), int(point[1])]
        rows = [row for row in data["systems"] if row["m"] == m]
        assert {row["arm"] for row in rows} == set(base_points)
        for row in rows:
            assert row["target_point"] == target["point"]
            arm = row["arm"]
            check_direct(row, target["point"][0], expected_coeffs[arm],
                         field, c["a"], c["b"])
            if arm == "coset":
                check_lift(row, field, pow(selected["base_parameters"]["coset"],896,c["p"]))
            else:
                assert set(row["encodings"]) == {"direct"}
            checked.append({"m": m, "arm": arm,
                            "direct_terms": row["encodings"]["direct"]["monomial_occurrences"],
                            "direct_max_degree": row["encodings"]["direct"]["max_total_degree"]})
    return {"schema": "icperf-prime-475-target-systems-sage-replay-v1",
            "scope": "independent arithmetic, membership, S3 and gate-equation replay of public input systems",
            "systems_sha256": sha(SYSTEMS), "source_sha256": sha(Path(__file__)),
            "sage_version": version(), "targets_checked": 7, "systems_checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = replay()
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"targets": result["targets_checked"],
                      "systems": len(result["systems_checked"])}, sort_keys=True))


if __name__ == "__main__":
    main()
