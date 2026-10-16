"""Independent integer-arithmetic replay of path-transport checkpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.toycurve import EllipticCurve
from research.isogeny_relation_yield_scan_20261016.verify_walk import kernel_coefficients
from tools.isogeny_dreg_search import velu_from_kernel_polynomial

WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}
SIZES = {"P29": 256, "P37": 1600}
STRIDES = {"P29": 8, "P37": 4}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def point_hash(points):
    return sha(json.dumps(points, separators=(",", ":")).encode())


def poly(coefficients, x, p):
    return sum(coefficient * pow(x, power, p) for power, coefficient in enumerate(coefficients)) % p


def replay_point(point, mapping, p):
    x, y = point
    n, d = mapping["numerator"], mapping["denominator"]
    nv, dv = poly(n, x, p), poly(d, x, p)
    if dv == 0:
        raise ValueError("point maps through a pole")
    derivative_n = sum(i * c * pow(x, i - 1, p) for i, c in enumerate(n) if i) % p
    derivative_d = sum(i * c * pow(x, i - 1, p) for i, c in enumerate(d) if i) % p
    inverse = pow(dv, -1, p)
    x_out = mapping["x_scale"] * nv * inverse % p
    y_out = mapping["y_scale"] * y * (derivative_n * dv - nv * derivative_d) * inverse * inverse % p
    return [x_out, y_out]


def check_source(base, header):
    p, model = header["p"], header["canonical_source"]
    curve = EllipticCurve(p, model["a"], model["b"])
    if len(base) != 2 * SIZES[header["stratum"]]:
        raise ValueError("source base size differs")
    expected_x = []
    x = 0
    while len(expected_x) < SIZES[header["stratum"]]:
        value = (x**3 + curve.a * x + curve.b) % p
        if value and pow(value, (p - 1) // 2, p) == 1:
            expected_x.append(x)
        x += 1
    if [base[i][0] for i in range(0, len(base), 2)] != expected_x:
        raise ValueError("source base is not first liftable x")
    for positive, negative in zip(base[::2], base[1::2]):
        if not curve.is_on_curve(tuple(positive)) or negative != [positive[0], (-positive[1]) % p]:
            raise ValueError("source sign pair or curve membership differs")
        if positive[1] > p // 2:
            raise ValueError("source sign convention differs")


def verify(stratum, directory):
    walk = WALKS[stratum]
    with walk.open() as handle:
        header = json.loads(next(handle))
        edges = [row for row in (json.loads(line) for line in handle) if row["kind"] == "edge"]
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["graph_sha256"] != sha(walk.read_bytes()) or manifest["stratum"] != stratum:
        raise ValueError("graph identity differs")
    paths = sorted(directory.glob("edge-????.json"))
    if not paths or any(path.name != f"edge-{i:04d}.json" for i, path in enumerate(paths)):
        raise ValueError("checkpoint gap")
    previous = None
    previous_hash = None
    checked_points = 0
    for index, path in enumerate(paths):
        raw = path.read_bytes()
        record = json.loads(raw)
        if record["index"] != index or record["previous_checkpoint_sha256"] != previous_hash:
            raise ValueError("checkpoint index or hash chain differs")
        if record["base_sha256"] != point_hash(record["base"]):
            raise ValueError("stored base digest differs")
        model = header["canonical_source"] if index == 0 else edges[index - 1]["canonical_codomain"]
        if record["model"] != model:
            raise ValueError("canonical model differs")
        curve = EllipticCurve(header["p"], model["a"], model["b"])
        if not curve.is_on_curve(tuple(record["generator"])) or curve.mul(header["r"], tuple(record["generator"])) is not None:
            raise ValueError("generator subgroup differs")
        if index == 0:
            check_source(record["base"], header)
        else:
            edge = edges[index - 1]
            if edge["source"] != previous["model"] or record["map"]["kernel_polynomial"] != edge["kernel_polynomial"]:
                raise ValueError("saved edge differs")
            kernel = kernel_coefficients(edge["kernel_polynomial"], header["p"])
            raw_model = edge["raw_codomain"]
            if velu_from_kernel_polynomial(edge["source"]["a"], edge["source"]["b"], header["p"], kernel) != (raw_model["a"], raw_model["b"]):
                raise ValueError("raw codomain differs from independent Vélu formula")
            mapping = record["map"]
            p = header["p"]
            sx, sy = mapping["x_scale"], mapping["y_scale"]
            if sy * sy % p != sx * sx * sx % p or model["a"] != raw_model["a"] * sx * sx % p or model["b"] != raw_model["b"] * sy * sy % p:
                raise ValueError("canonical isomorphism differs")
            if [replay_point(point, mapping, p) for point in previous["base"]] != record["base"]:
                raise ValueError("independent full-base map replay differs")
            if replay_point(previous["generator"], mapping, p) != record["generator"]:
                raise ValueError("independent generator map replay differs")
            checked_points += len(record["base"])
        if record["check_vertex"] != (index % STRIDES[stratum] == 0):
            raise ValueError("check-vertex schedule differs")
        if record["check_vertex"] or record.get("terminal_control"):
            if len({point[0] for point in record["base"]}) != SIZES[stratum] or not all(curve.is_on_curve(tuple(point)) for point in record["base"]):
                raise ValueError("check-vertex base differs")
        previous, previous_hash = record, sha(raw)
    return {"stratum": stratum, "edges_checked": len(paths) - 1,
            "points_replayed": checked_points, "last_checkpoint_sha256": previous_hash,
            "graph_sha256": manifest["graph_sha256"], "status": "pass",
            "limit": "point-map and stored-base replay only; no relation collection"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stratum", choices=sorted(WALKS), required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.stratum, args.checkpoint_dir), sort_keys=True))
