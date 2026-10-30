"""Independently replay a timed path transfer with Sage's point maps."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, PolynomialRing

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
RUNNER = Path(__file__).with_name("path_transfer.py")
WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed_points(generator: list[int], target: list[int]) -> bytes:
    return json.dumps({"G": generator, "Q": target}, sort_keys=True,
                      separators=(",", ":")).encode()


def replay(stratum: str, index: int, source_path: Path,
           endpoint_path: Path, result_path: Path) -> dict:
    result = json.loads(result_path.read_text())
    source = json.loads(source_path.read_text())
    endpoint = json.loads(endpoint_path.read_text())
    walk = WALKS[stratum]
    if (result.get("schema") != "ectd.graph-path-transfer-result/v1" or
            result.get("status") != "output_validated" or
            result.get("stratum") != stratum or result.get("index") != index or
            result.get("runner_sha256") != sha(RUNNER) or
            result.get("walk_sha256") != sha(walk) or
            result.get("source_manifest_sha256") != sha(source_path) or
            result.get("endpoint_manifest_sha256") != sha(endpoint_path)):
        raise ValueError("transfer result identity or source digest differs")
    header, *lines = walk.read_text(encoding="utf-8").splitlines()
    header = json.loads(header)
    edges = []
    for line in ([] if index == 0 else lines):
        row = json.loads(line)
        if row.get("kind") == "complete":
            break
        if row.get("kind") != "edge":
            raise ValueError("unexpected walk row")
        edges.append(row)
        if len(edges) == index:
            break
    if len(edges) != index or result.get("edge_count") != index:
        raise ValueError("transfer edge count differs from the archived path")
    if (source.get("schema") != "isogeny-relation-input/v1" or
            source.get("stratum") != stratum or source.get("stage") != "solve" or
            endpoint.get("schema") != "isogeny-relation-input/v1" or
            endpoint.get("stratum") != stratum or endpoint.get("stage") != "solve" or
            endpoint.get("index") != index):
        raise ValueError("prepared point manifests do not name this path")
    generator, target = source.get("source_generator"), source.get("source_Q")
    if result.get("source_points_sha256") != hashlib.sha256(
            packed_points(generator, target)).hexdigest():
        raise ValueError("source public point digest differs")
    points = [generator, target]
    model = header["canonical_source"]
    field = GF(header["p"])
    rows = result.get("edges")
    if not isinstance(rows, list) or len(rows) != index:
        raise ValueError("per-edge measurements are incomplete")
    for edge, measurement in zip(edges, rows):
        for key in ("setup_seconds", "point_map_seconds", "map_verification_seconds"):
            value = measurement.get(key)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError("edge timing is missing, negative, or nonfinite")
        if (measurement.get("index") != edge["index"] or
                measurement.get("source_j") != model["j"] or
                measurement.get("destination_j") != edge["canonical_codomain"]["j"] or
                measurement.get("source_points") != points):
            raise ValueError("edge transcript identity or input points differ")
        source_curve = EllipticCurve(field, [model["a"], model["b"]])
        phi = source_curve.isogeny(PolynomialRing(field, "x")(edge["kernel_polynomial"]))
        codomain = edge["canonical_codomain"]
        canonical = EllipticCurve(field, [codomain["a"], codomain["b"]])
        iso = phi.codomain().isomorphism_to(canonical)
        mapped = []
        for x, y in points:
            mapped_point = iso(phi(source_curve(field(x), field(y))))
            if mapped_point.is_zero():
                raise ValueError("public point unexpectedly maps to identity")
            mapped.append([int(mapped_point[0]), int(mapped_point[1])])
        if (measurement.get("destination_points") != mapped or
                mapped[0] != edge.get("image_generator")):
            raise ValueError("independent Sage path replay differs from timed output")
        points, model = mapped, codomain
    if points != [endpoint.get("generator"), endpoint.get("Q")]:
        raise ValueError("replayed path endpoints differ from prepared finalist input")
    if result.get("endpoint_generator") != points[0] or result.get("endpoint_Q") != points[1]:
        raise ValueError("result endpoint points differ")
    for result_key, phase_key in (("path_setup_seconds", "setup_seconds"),
                                  ("path_point_map_seconds", "point_map_seconds"),
                                  ("path_map_verification_seconds", "map_verification_seconds")):
        total = sum(row[phase_key] for row in rows)
        if not math.isclose(result.get(result_key, -1), total, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("path phase total differs from per-edge timings")
    return {"schema": "ectd.graph-path-transfer-check/v1", "status": "pass",
            "stratum": stratum, "index": index, "edges_replayed": len(edges),
            "result_sha256": sha(result_path), "runner_sha256": sha(RUNNER),
            "checker_sha256": sha(Path(__file__))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stratum", choices=sorted(WALKS), required=True)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--endpoint-manifest", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    check = replay(args.stratum, args.index, args.source_manifest,
                   args.endpoint_manifest, args.result)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(check, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(check, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
