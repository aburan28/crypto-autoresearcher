"""Recheck the fixed pair identities against hash-bound archived specs.

The ring-conductor classification is conditional on the independently checked
class polynomial H_{-19}(X)=X+884736. This does not evaluate an isogeny map.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd, isqrt
from pathlib import Path

from verify_collector import Curve, certify_group, is_prime_exact

HERE = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduced_forms(discriminant):
    assert discriminant < 0 and discriminant % 4 in (0, 1)
    forms = []
    for a in range(1, isqrt(abs(discriminant) // 3) + 1):
        for b in range(-a, a + 1):
            numerator = b * b - discriminant
            if numerator % (4 * a):
                continue
            c = numerator // (4 * a)
            if a > c or gcd(a, gcd(abs(b), c)) != 1:
                continue
            if (abs(b) == a or a == c) and b < 0:
                continue
            forms.append((a, b, c))
    return forms


def j_invariant(curve):
    numerator = 1728 * 4 * curve.a**3
    denominator = (4 * curve.a**3 + 27 * curve.b**2) % curve.p
    assert denominator
    return numerator * pow(denominator, -1, curve.p) % curve.p


def same_model(left, right):
    return all(left[name] == right[other] for name, other in (
        ("a", "a"), ("b", "b"), ("gx", "gx"), ("gy", "gy"),
    ))


def certify(plan, crypto_root):
    assert reduced_forms(-19) == [(1, 1, 5)]
    source_base = crypto_root / "research"
    results = []
    for panel in plan["primary_panel"]:
        panel_id = panel["id"]
        filename = "ell8209-q29.json" if panel_id == "P29" else "ell131101-q37.json"
        source = source_base / "ecbench_conductor_gap_20261012" / "specs" / filename
        assert sha256(source) == panel["source_spec_sha256"]
        archived = json.loads(source.read_text())
        source_curves = archived["workloads"]["curves"]
        assert len(source_curves) == 2
        assert is_prime_exact(panel["edge_degree"])
        trace = panel["p"] + 1 - panel["r"]
        assert trace * trace - 4 * panel["p"] == -19 * panel["f_pi"] ** 2
        assert panel["f_pi"] == panel["edge_degree"]
        for index, role in enumerate(("crater", "floor")):
            model = panel[role]
            assert same_model(model, source_curves[index])
            assert source_curves[index]["p"] == panel["p"]
            assert source_curves[index]["group_order"] == panel["r"]
            curve = Curve(panel["p"], model["a"], model["b"], panel["r"])
            certify_group(curve, (model["gx"], model["gy"]))
            j = j_invariant(curve)
            if role == "crater":
                assert model["f_E"] == 1 and j == (-884736) % curve.p
            else:
                assert model["f_E"] == panel["f_pi"] and j != (-884736) % curve.p
            results.append({"endpoint": f"{panel_id}-{role}", "p": curve.p, "r": curve.r,
                            "trace": trace, "j": j, "f_pi": panel["f_pi"],
                            "f_E_given_class_polynomial": model["f_E"],
                            "source_spec_sha256": sha256(source)})
    secondary = plan["secondary_same_conductor_panel"]
    source = source_base / "conductor_gap_cm_pairs_20261010" / "specs" / "gap-ell8209-q29.json"
    assert sha256(source) == secondary["source_spec_sha256"]
    source_curves = json.loads(source.read_text())["workloads"]["curves"]
    assert len(source_curves) == 4
    for index, model in enumerate(secondary["models"], start=2):
        assert same_model(model, source_curves[index])
        curve = Curve(secondary["p"], model["a"], model["b"], secondary["r"])
        certify_group(curve, (model["gx"], model["gy"]))
        j = j_invariant(curve)
        assert j != (-884736) % curve.p
        results.append({"endpoint": model["id"], "p": curve.p, "r": curve.r,
                        "trace": curve.p + 1 - curve.r, "j": j,
                        "f_pi": 8209, "f_E_given_class_polynomial": 8209,
                        "source_spec_sha256": sha256(source)})
    return {"schema": "conductor-panel-certificate/v1", "status": "valid",
            "reduced_forms_D_minus_19": reduced_forms(-19),
            "class_polynomial_assumption": "H_-19(X)=X+884736; check with Sage independently",
            "models": results,
            "scope": "group orders exact; conductor labels conditional on class polynomial; no explicit isogeny map"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--crypto-root", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads((HERE / "plan.json").read_text())
    print(json.dumps(certify(plan, args.crypto_root), sort_keys=True))


if __name__ == "__main__":
    main()
