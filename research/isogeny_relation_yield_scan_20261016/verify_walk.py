#!/usr/bin/env python3
"""Independent arithmetic checks for the saved degree-7 walk JSONL.

This checks the kernel/codomain algebra and transported point certificates
without using Sage's isogeny implementation. It does not recompute the full
point-map formula, so the producer's map/dual checks remain a separate layer.
"""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.isogeny_dreg_search import DivisionPolynomials, pdivmod, velu_from_kernel_polynomial
from harness.toycurve import EllipticCurve


def kernel_coefficients(text, p):
    terms = text.replace("-", "+-").split("+")
    coeffs = [0, 0, 0, 0]
    for term in terms:
        term = term.strip().replace(" ", "")
        if not term:
            continue
        if "x" not in term:
            degree, coefficient = 0, int(term)
        else:
            left, _, right = term.partition("x")
            left = left.rstrip("*")
            coefficient = int(left) if left not in ("", "+", "-") else (-1 if left == "-" else 1)
            degree = int(right[1:]) if right.startswith("^") else 1
        if not 0 <= degree <= 3:
            raise ValueError(f"unexpected kernel degree {degree}")
        coeffs[degree] = coefficient % p
    if coeffs[3] != 1:
        raise ValueError("degree-7 kernel is not monic cubic")
    return coeffs


def j_invariant(a, b, p):
    aa, bb = 4 * pow(a, 3, p) % p, 27 * pow(b, 2, p) % p
    return 1728 * aa * pow((aa + bb) % p, -1, p) % p


def verify(path):
    with open(path, encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle]
    header, *rest = records
    assert header["kind"] == "header" and header["degree"] == 7
    p, r = header["p"], header["r"]
    edges = [item for item in rest if item["kind"] == "edge"]
    complete = [item for item in rest if item["kind"] == "complete"]
    assert len(rest) == len(edges) + len(complete) and len(complete) <= 1
    seen = {header["canonical_source"]["j"]}
    previous = header["canonical_source"]
    for index, edge in enumerate(edges, 1):
        assert edge["index"] == index and edge["source"] == previous
        source, raw, canonical = edge["source"], edge["raw_codomain"], edge["canonical_codomain"]
        assert all(j_invariant(m["a"], m["b"], p) == m["j"] for m in (source, raw, canonical))
        kernel = kernel_coefficients(edge["kernel_polynomial"], p)
        quotient, remainder = pdivmod(DivisionPolynomials(source["a"], source["b"], p)(7), kernel, p)
        assert not remainder and quotient
        assert velu_from_kernel_polynomial(source["a"], source["b"], p, kernel) == (raw["a"], raw["b"])
        assert raw["j"] == canonical["j"] and canonical["j"] not in seen
        curve = EllipticCurve(p, canonical["a"], canonical["b"])
        g = tuple(edge["image_generator"])
        q = tuple(edge["image_smoke_target"])
        assert curve.is_on_curve(g) and curve.is_on_curve(q)
        assert curve.mul(r, g) is None
        assert curve.mul(header["smoke_scalar"], g) == q
        assert all(edge["checks"].values())
        previous = canonical
        seen.add(canonical["j"])
    if complete:
        assert complete[0]["edges"] == len(edges) == header["requested_edges"]
        assert complete[0]["distinct_vertices"] == len(seen)
    return {"path": path, "checked_edges": len(edges), "distinct_vertices": len(seen),
            "requested_edges": header["requested_edges"], "complete": bool(complete),
            "checks": ["continuity", "unique_j", "j_arithmetic", "kernel_divides_psi7",
                       "velu_codomain", "point_on_curve", "r_torsion", "smoke_scalar"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    print(json.dumps([verify(path) for path in args.paths], sort_keys=True, indent=2))
