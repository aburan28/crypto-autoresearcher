"""Bounded positive control: transport the source low-x base over two saved edges.

Run under Sage's Python. Planted targets are implementation controls only.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
import sys
import time

from sage.all import EllipticCurve as SageCurve, GF
from sage.version import version as sage_version

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from harness.toycurve import EllipticCurve as IndependentCurve
from prepare_graph_input import SCHEDULE, base_points, digest, source_generator

STUDY = Path(__file__).resolve().parents[1]
WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}
TRIPLES = ((0, 2, 4), (1, 3, 6), (0, 5, 10), (2, 7, 14))


def pair(point):
    return None if point.is_zero() else (int(point[0]), int(point[1]))


def point_digest(points):
    payload = json.dumps([pair(point) for point in points], separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def independent_counts(model, base, targets):
    curve = IndependentCurve(model.base_field().cardinality(), int(model.a4()), int(model.a6()))
    subset = [pair(point) for point in base[:16]]
    sums = Counter()
    for i, j, k in combinations_with_replacement(range(len(subset)), 3):
        total = curve.add(curve.add(subset[i], subset[j]), subset[k])
        sums[total] += 1
    return [sums[pair(target)] for target in targets]


def run(stratum):
    started = time.monotonic()
    print(f"{stratum}: loading source and base", file=sys.stderr, flush=True)
    walk = WALKS[stratum]
    with walk.open(encoding="utf-8") as handle:
        header, edge1, edge2 = [json.loads(next(handle)) for _ in range(3)]
    assert [edge1["index"], edge2["index"]] == [1, 2]
    field = GF(header["p"])
    source = SageCurve(field, [header["canonical_source"]["a"], header["canonical_source"]["b"]])
    source_base, _ = base_points(
        type("Curve", (), dict(p=header["p"], a=int(source.a4()), b=int(source.a6())))(),
        SCHEDULE[stratum]["B"], "low_x", b"B" * 32, stratum, header["canonical_source"]["j"])
    base = [source(field(x), field(y)) for x, y in source_base]
    gx, gy = source_generator(header)
    generator = source(field(gx), field(gy))
    targets = [sum((base[i] for i in triple), source(0)) for triple in TRIPLES]
    expected_counts = independent_counts(source, base, targets)
    assert all(count > 0 for count in expected_counts)
    result = {"stratum": stratum, "graph_sha256": digest(walk), "sage_version": str(sage_version),
              "base_orbits": SCHEDULE[stratum]["B"], "signed_base_points": len(base),
              "source_base_sha256": point_digest(base), "source_control_counts": expected_counts,
              "control_triples": TRIPLES, "edges": []}
    current = source
    for edge in (edge1, edge2):
        edge_started = time.monotonic()
        print(f"{stratum}: constructing edge {edge['index']}", file=sys.stderr, flush=True)
        assert edge["source"] == {"a": int(current.a4()), "b": int(current.a6()),
                                  "j": int(current.j_invariant())}
        matching = [phi for phi in current.isogenies_prime_degree(7)
                    if str(phi.kernel_polynomial()) == edge["kernel_polynomial"]
                    and int(phi.codomain().j_invariant()) == edge["raw_codomain"]["j"]]
        assert len(matching) == 1, "saved kernel does not select one map"
        phi = matching[0]
        raw = phi.codomain()
        assert (int(raw.a4()), int(raw.a6())) == (edge["raw_codomain"]["a"], edge["raw_codomain"]["b"])
        next_model = edge["canonical_codomain"]
        next_curve = SageCurve(field, [next_model["a"], next_model["b"]])
        iso = raw.isomorphism_to(next_curve)
        assert str(iso.rational_maps()) == edge["codomain_isomorphism"]
        dual = phi.dual()
        raw_base = []
        for n, point in enumerate(base, 1):
            raw_base.append(phi(point))
            if n % 512 == 0:
                print(f"{stratum}: edge {edge['index']} mapped {n}/{len(base)} base points",
                      file=sys.stderr, flush=True)
        raw_targets = [phi(point) for point in targets]
        raw_generator = phi(generator)
        dual_samples = [(generator, raw_generator), *zip(base[:16], raw_base[:16]),
                        *zip(targets, raw_targets)]
        assert all(dual(mapped) == 7 * original for original, mapped in dual_samples)
        next_base = [iso(point) for point in raw_base]
        next_targets = [iso(point) for point in raw_targets]
        next_generator = iso(raw_generator)
        assert pair(next_generator) == tuple(edge["image_generator"])
        assert len(set(next_base)) == len(next_base)
        assert all(not point.is_zero() for point in next_base)
        counts = independent_counts(next_curve, next_base, next_targets)
        assert counts == expected_counts, "transported targetwise count differs"
        result["edges"].append({"index": edge["index"], "j": next_model["j"],
                                "kernel_polynomial": edge["kernel_polynomial"],
                                "dual_points_checked": len(dual_samples),
                                "base_sha256": point_digest(next_base),
                                "control_counts": counts, "targetwise_equal": True,
                                "elapsed_seconds": time.monotonic() - edge_started})
        current, base, targets, generator = next_curve, next_base, next_targets, next_generator
    result["elapsed_seconds"] = time.monotonic() - started
    return result


if __name__ == "__main__":
    print(json.dumps({"schema": "ectd.two-edge-transport-control.v1",
                      "results": [run(stratum) for stratum in ("P29", "P37")]},
                     sort_keys=True, indent=2))
