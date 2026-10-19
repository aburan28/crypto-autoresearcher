"""Independent Sage replay of the two 475-point prime-field control bases."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from sage.all import EllipticCurve, GF, PolynomialRing, version

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = ROOT / "research/icperf_prime_475_controls_20261017/controls.json"
FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
SCAN = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point_sha(points: list[list[int]]) -> str:
    digest = hashlib.sha256()
    for x, y in points:
        digest.update(x.to_bytes(8, "big"))
        digest.update(y.to_bytes(8, "big"))
    return digest.hexdigest()


def replay() -> dict:
    record = json.loads(CONTROLS.read_bytes())
    fixture, scan = json.loads(FIXTURE.read_bytes()), json.loads(SCAN.read_bytes())
    assert record["schema"] == "icperf-prime-475-controls-v1"
    assert record["source_sha256"] == sha(ROOT / "tools/icperf_prime_475_controls.py")
    assert record["factor_base_source_sha256"] == sha(ROOT / "src/crypto_autoresearcher/index_calculus/factor_base.py")
    assert record["fixture_sha256"] == sha(FIXTURE) and record["scan_sha256"] == sha(SCAN)
    assert record["curve"] == fixture["curve"] == scan["curve"]
    assert record["size"] == scan["selected_realized_size"] == 475
    selected = next(a for a in scan["attempts"]
                    if a["base_parameters"]["seed"] == scan["selected_seed"])
    assert record["coset_reference"]["point_sha256"] == point_sha(selected["points"])
    p, a, b = (record["curve"][key] for key in ("p", "a", "b"))
    field = GF(p)
    curve = EllipticCurve(field, [a, b])
    ring = PolynomialRing(field, "X")
    X = ring.gen()
    seen_kinds, checked = set(), []
    for control in record["controls"]:
        kind = control["kind"]
        assert kind in ("random", "small_x") and kind not in seen_kinds
        seen_kinds.add(kind)
        assert control["size"] == 475 and len(control["points"]) == 475
        assert control["point_sha256"] == point_sha(control["points"])
        if kind == "random":
            assert control["parameters"]["seed"] == record["random_seed"]
            rng = random.Random(f"fb-random|{p}|{a}|{b}|475|{record['random_seed']}")
        else:
            assert control["parameters"]["bound"] == len(control["draw_stream"])
        seen, accepted = set(), []
        counters = {"accepted": 0, "nonliftable": 0, "repeat": 0}
        for i, event in enumerate(control["draw_stream"]):
            x = rng.randrange(p) if kind == "random" else i
            assert x == event["x"]
            if kind == "random" and x in seen:
                status = "repeat"
            else:
                seen.add(x)
                rhs = field(x) ** 3 + field(a) * field(x) + field(b)
                status = "accepted" if rhs != 0 and rhs.is_square() else "nonliftable"
            assert event["status"] == status
            counters[status] += 1
            if status == "accepted":
                accepted.append(x)
        assert len(accepted) == 475
        assert accepted == [x for x, _ in control["points"]]
        assert control["draw_count"] == len(control["draw_stream"])
        assert all(control[f"{key}_count"] == value for key, value in counters.items())
        assert all(curve(field(x), field(y)) != curve(0) for x, y in control["points"])
        poly = ring.one()
        for x in accepted:
            poly *= X - field(x)
        expected = {str(e): int(c) for e, c in enumerate(poly.list()) if c}
        assert expected == control["membership_coefficients"]
        assert control["membership_degree"] == poly.degree() == 475
        assert control["membership_nonzero_terms"] == len(expected)
        assert control["x_overlap_with_coset"] == len(set(accepted) &
                                                       {point[0] for point in selected["points"]})
        checked.append({"kind": kind, "size": len(accepted),
                        "draw_count": len(control["draw_stream"]),
                        "nonliftable_count": counters["nonliftable"],
                        "repeat_count": counters["repeat"],
                        "membership_degree": int(poly.degree()),
                        "membership_nonzero_terms": len(expected),
                        "x_overlap_with_coset": control["x_overlap_with_coset"]})
    assert seen_kinds == {"random", "small_x"}
    return {"schema": "icperf-prime-475-controls-sage-replay-v1",
            "scope": "independent draw, point and full membership-polynomial check; no solver or ECDLP cost claim",
            "controls_sha256": sha(CONTROLS), "source_sha256": sha(Path(__file__)),
            "scan_sha256": sha(SCAN), "sage_version": version(),
            "controls_checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = replay()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result["controls_checked"], sort_keys=True))


if __name__ == "__main__":
    main()
