"""Time source-to-finalist point transport using only public G,Q coordinates.

Run with ``sage -python``. The scalar and verifier root are never accepted as
inputs; they remain in the custodian-side preparation process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

from sage.all import EllipticCurve, GF, PolynomialRing
from sage.version import version as sage_version

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(STUDY / "preparation"))
from prepare_graph_input import scale_component
from research.isogeny_relation_yield_scan_20261016.path_transport.transport_path import map_one

WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed_points(generator: list[int], target: list[int]) -> bytes:
    return json.dumps({"G": generator, "Q": target}, sort_keys=True,
                      separators=(",", ":")).encode()


def load_edges(walk: Path, index: int) -> tuple[dict, list[dict]]:
    lines = walk.read_text(encoding="utf-8").splitlines()
    header = json.loads(lines[0])
    if header.get("kind") != "header" or not 0 <= index <= header.get("requested_edges", -1):
        raise ValueError("transfer endpoint is outside the saved walk")
    if index == 0:
        return header, []
    edges = []
    for line in lines[1:]:
        record = json.loads(line)
        if record.get("kind") == "complete":
            break
        if record.get("kind") != "edge" or record.get("index") != len(edges) + 1:
            raise ValueError("saved walk has a missing or discontinuous edge")
        edges.append(record)
        if len(edges) == index:
            break
    if len(edges) != index:
        raise ValueError("saved walk does not reach the requested endpoint")
    return header, edges


def run(stratum: str, index: int, source_manifest_path: Path,
        endpoint_manifest_path: Path) -> dict:
    if stratum not in WALKS:
        raise ValueError("unsupported stratum")
    walk = WALKS[stratum]
    header, edges = load_edges(walk, index)
    source = json.loads(source_manifest_path.read_text())
    endpoint = json.loads(endpoint_manifest_path.read_text())
    if (source.get("schema") != "isogeny-relation-input/v1" or
            source.get("stage") != "solve" or source.get("stratum") != stratum or
            endpoint.get("schema") != "isogeny-relation-input/v1" or
            endpoint.get("stage") != "solve" or endpoint.get("stratum") != stratum or
            endpoint.get("index") != index):
        raise ValueError("source or endpoint manifest has the wrong stage identity")
    generator = source.get("source_generator")
    target = source.get("source_Q")
    if (not isinstance(generator, list) or len(generator) != 2 or
            not isinstance(target, list) or len(target) != 2 or
            source.get("source_points_sha256") != hashlib.sha256(
                packed_points(generator, target)).hexdigest()):
        raise ValueError("source public G,Q binding is missing or invalid")
    if (source.get("source_model") != header.get("canonical_source") or
            source.get("p") != header.get("p") or source.get("r") != header.get("r")):
        raise ValueError("source point curve differs from the archived walk")

    points = [list(generator), list(target)]
    edge_results = []
    p = header["p"]
    field = GF(p)
    setup_total = 0.0
    map_total = 0.0
    verify_total = 0.0
    model = header["canonical_source"]
    for edge in edges:
        if edge.get("source") != model:
            raise ValueError("saved edge source differs from current curve")
        t0 = time.monotonic()
        source_curve = EllipticCurve(field, [model["a"], model["b"]])
        ring = PolynomialRing(field, "x")
        phi = source_curve.isogeny(ring(edge["kernel_polynomial"]))
        if str(phi.kernel_polynomial()) != edge["kernel_polynomial"] or int(phi.degree()) != 7:
            raise ValueError("saved degree-7 isogeny differs")
        if int(phi.scaling_factor()) != 1:
            raise ValueError("saved isogeny normalization differs")
        raw = phi.codomain()
        next_model = edge["canonical_codomain"]
        canonical = EllipticCurve(field, [next_model["a"], next_model["b"]])
        iso = raw.isomorphism_to(canonical)
        isomorphism = str(iso.rational_maps())
        if isomorphism != edge["codomain_isomorphism"]:
            raise ValueError("saved canonical codomain map differs")
        xexpr, yexpr = isomorphism.strip()[1:-1].split(",")
        sx, sy = scale_component(xexpr, "x", p), scale_component(yexpr, "y", p)
        xmap = phi.x_rational_map()
        numerator = [int(value) for value in xmap.numerator().list()]
        denominator = [int(value) for value in xmap.denominator().list()]
        setup_seconds = time.monotonic() - t0

        t1 = time.monotonic()
        mapped = [map_one(point, numerator, denominator, sx, sy, p) for point in points]
        map_seconds = time.monotonic() - t1
        if mapped[0] != edge.get("image_generator"):
            raise ValueError("transported G differs from archived image generator")

        t2 = time.monotonic()
        for before, after in zip(points, mapped):
            sage_before = source_curve(field(before[0]), field(before[1]))
            sage_after = iso(phi(sage_before))
            if sage_after.is_zero() or [int(sage_after[0]), int(sage_after[1])] != after:
                raise ValueError("fast point map differs from independent Sage evaluation")
        verify_seconds = time.monotonic() - t2
        setup_total += setup_seconds
        map_total += map_seconds
        verify_total += verify_seconds
        edge_results.append({
            "index": edge["index"],
            "source_j": model["j"],
            "destination_j": next_model["j"],
            "source_points": points,
            "destination_points": mapped,
            "setup_seconds": setup_seconds,
            "point_map_seconds": map_seconds,
            "map_verification_seconds": verify_seconds,
        })
        points, model = mapped, next_model

    expected_g, expected_q = endpoint.get("generator"), endpoint.get("Q")
    if points != [expected_g, expected_q]:
        raise ValueError("transported source G,Q differ from the exact prepared finalist pair")
    return {
        "schema": "ectd.graph-path-transfer-result/v1",
        "status": "output_validated",
        "runner_sha256": sha(Path(__file__)),
        "stratum": stratum,
        "index": index,
        "j": model["j"],
        "walk_sha256": sha(walk),
        "source_manifest_sha256": sha(source_manifest_path),
        "endpoint_manifest_sha256": sha(endpoint_manifest_path),
        "source_points_sha256": source["source_points_sha256"],
        "endpoint_generator": points[0],
        "endpoint_Q": points[1],
        "edge_count": len(edge_results),
        "path_setup_seconds": setup_total,
        "path_point_map_seconds": map_total,
        "path_map_verification_seconds": verify_total,
        "sage_version": str(sage_version),
        "python": sys.version,
        "platform": platform.platform(),
        "edges": edge_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stratum", choices=sorted(WALKS), required=True)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--endpoint-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.stratum, args.index, args.source_manifest, args.endpoint_manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in (
        "schema", "status", "stratum", "index", "edge_count",
        "path_setup_seconds", "path_point_map_seconds")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
