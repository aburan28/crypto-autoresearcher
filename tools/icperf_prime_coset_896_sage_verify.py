"""Independent Sage replay of all d=896 coset candidates and selection."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from sage.all import EllipticCurve, GF, version

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay() -> dict:
    record = json.loads(SCAN.read_bytes())
    fixture = json.loads(FIXTURE.read_bytes())
    assert record["fixture_sha256"] == sha(FIXTURE)
    assert record["base_preparer_sha256"] == sha(ROOT / "tools/icperf_explicit_base.py")
    assert record["source_sha256"] == sha(ROOT / "tools/icperf_prime_coset_896_scan.py")
    assert record["curve"] == fixture["curve"]
    p, a, b, order = (record["curve"][key] for key in ("p", "a", "b", "order"))
    field = GF(p)
    curve = EllipticCurve(field, [a, b])
    assert record["divisor"] == 896 and record["target_size"] == 441
    assert record["seeds"] == list(range(20261017, 20261033))
    assert len(record["attempts"]) == len(record["seeds"])
    checked = []
    for seed, attempt in zip(record["seeds"], record["attempts"]):
        params = attempt["base_parameters"]
        assert attempt["curve"] == record["curve"]
        assert attempt["curve_fixture_sha256"] == record["fixture_sha256"]
        assert params["seed"] == seed and params["d"] == 896
        g, zeta = field(params["coset"]), field(params["zeta"])
        assert zeta ** 896 == 1 and zeta ** 448 != 1 and zeta ** 128 != 1
        coset = [g * zeta ** j for j in range(896)]
        assert len(set(coset)) == 896
        expected_x = []
        for x in coset:
            rhs = x ** 3 + field(a) * x + field(b)
            if rhs != 0 and rhs.is_square():
                expected_x.append(int(x))
        given = attempt["points"]
        assert [int(x) for x, _ in given] == expected_x
        assert len(given) == attempt["realized_size"]
        assert all(curve(field(x), field(y)) != curve(0) for x, y in given)
        assert all(field(x) ** 896 == g ** 896 for x, _ in given)
        digest = hashlib.sha256()
        for x, y in given:
            digest.update(x.to_bytes(8, "big"))
            digest.update(y.to_bytes(8, "big"))
        assert digest.hexdigest() == attempt["point_sha256"]
        assert attempt["signed_m8_multiset_upper_count"] == math.comb(2 * len(given) + 7, 8)
        assert attempt["signed_m8_count_reaches_order"] == (attempt["signed_m8_multiset_upper_count"] >= order)
        checked.append({"seed": seed, "realized_size": len(given),
                        "point_sha256": attempt["point_sha256"]})
    winner = max(checked, key=lambda item: (item["realized_size"], -item["seed"]))
    assert winner["seed"] == record["selected_seed"]
    assert winner["realized_size"] == record["selected_realized_size"]
    assert winner["point_sha256"] == record["selected_point_sha256"]
    assert math.comb(2 * 440 + 7, 8) < order <= math.comb(2 * 441 + 7, 8)
    return {"schema": "icperf-prime-coset-896-sage-replay-v1",
            "scope": "independent all-coset point-list and selection replay; no solver or ECDLP cost claim",
            "scan_sha256": sha(SCAN), "source_sha256": sha(Path(__file__)),
            "sage_version": version(), "curve_points_checked": sum(c["realized_size"] for c in checked),
            "coset_x_checked": len(checked) * 896, "attempts_checked": checked,
            "selected_seed": winner["seed"], "selected_realized_size": winner["realized_size"],
            "m8_threshold": 441}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = replay()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"selected_seed": result["selected_seed"],
                      "selected_realized_size": result["selected_realized_size"],
                      "coset_x_checked": result["coset_x_checked"]}, sort_keys=True))


if __name__ == "__main__":
    main()
