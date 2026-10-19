"""Checkpoint source low-x base transport through a saved degree-7 walk.

Each output edge contains the full ordered signed base, so a stopped process
can resume without replaying earlier edges. This is map preparation only;
relation collection and scientific targets belong to an admitted experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from sage.all import EllipticCurve as SageCurve, GF, PolynomialRing
from sage.version import version as sage_version

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(STUDY / "preparation"))
from prepare_graph_input import SCHEDULE, base_points, digest, load_vertex, scale_component
from harness.toycurve import EllipticCurve as CheckCurve

WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}
SCHEMA = "ectd.path-base-transport.v1"


def packed(points):
    return json.dumps(points, separators=(",", ":")).encode()


def points_digest(points):
    return hashlib.sha256(packed(points)).hexdigest()


def horner(coeffs, x, p):
    value = 0
    for coefficient in reversed(coeffs):
        value = (value * x + coefficient) % p
    return value


def batch_inverse(values, p):
    prefixes = [1]
    for value in values:
        if value % p == 0:
            raise ValueError("factor-base point meets isogeny kernel")
        prefixes.append(prefixes[-1] * value % p)
    suffix_inverse = pow(prefixes[-1], -1, p)
    result = [0] * len(values)
    for index in range(len(values) - 1, -1, -1):
        result[index] = suffix_inverse * prefixes[index] % p
        suffix_inverse = suffix_inverse * values[index] % p
    return result


def map_orbits(points, numerator, denominator, sx, sy, p, chunk_size=256):
    """Map signed pairs using X=N/D and normalized Y=y*dX/dx."""
    if len(points) % 2:
        raise ValueError("signed factor base has odd length")
    nd = [i * c % p for i, c in enumerate(numerator)][1:]
    dd = [i * c % p for i, c in enumerate(denominator)][1:]
    output = []
    for start in range(0, len(points), 2 * chunk_size):
        pairs = [points[i:i + 2] for i in range(start, min(start + 2 * chunk_size, len(points)), 2)]
        values = []
        for positive, negative in pairs:
            x, y = positive
            if negative != [x, (-y) % p]:
                raise ValueError("base sign pair changed")
            n = horner(numerator, x, p)
            d = horner(denominator, x, p)
            derivative_n = horner(nd, x, p)
            derivative_d = horner(dd, x, p)
            values.append((x, y, n, d, derivative_n, derivative_d))
        inverses = batch_inverse([row[3] for row in values], p)
        for (_, y, n, d, derivative_n, derivative_d), inv_d in zip(values, inverses):
            x_out = sx * n * inv_d % p
            derivative = (derivative_n * d - n * derivative_d) * inv_d * inv_d % p
            y_out = sy * y * derivative % p
            output.extend(([x_out, y_out], [x_out, (-y_out) % p]))
    return output


def map_one(point, numerator, denominator, sx, sy, p):
    x, y = point
    n, d = horner(numerator, x, p), horner(denominator, x, p)
    inv_d = pow(d, -1, p)
    nd = [i * c % p for i, c in enumerate(numerator)][1:]
    dd = [i * c % p for i, c in enumerate(denominator)][1:]
    derivative = (horner(nd, x, p) * d - n * horner(dd, x, p)) * inv_d * inv_d % p
    return [sx * n * inv_d % p, sy * y * derivative % p]


def point_pair(point):
    return [int(point[0]), int(point[1])]


def atomic_new(path, record):
    temp = path.with_name(path.name + ".partial")
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with temp.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.link(temp, path)  # fails rather than replacing an existing checkpoint
    temp.unlink()
    return hashlib.sha256(payload).hexdigest()


def checkpoint_path(directory, index):
    return directory / f"edge-{index:04d}.json"


def load_chain(directory, header, graph_hash, script_hash):
    manifest = json.loads((directory / "manifest.json").read_text())
    expected = {"schema": SCHEMA, "stratum": header["stratum"],
                "graph_sha256": graph_hash, "script_sha256": script_hash}
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("checkpoint manifest differs from frozen inputs")
    files = sorted(directory.glob("edge-????.json"))
    if not files or any(path.name != f"edge-{i:04d}.json" for i, path in enumerate(files)):
        raise ValueError("missing or discontinuous checkpoint")
    previous_digest = None
    last = None
    for path in files:
        raw = path.read_bytes()
        record = json.loads(raw)
        if record["previous_checkpoint_sha256"] != previous_digest:
            raise ValueError("checkpoint hash chain differs")
        if record["base_sha256"] != points_digest(record["base"]):
            raise ValueError("base digest differs")
        previous_digest = hashlib.sha256(raw).hexdigest()
        last = record
    return last, previous_digest


def run(stratum, max_edges, directory, resume=False):
    walk = WALKS[stratum]
    header, model, curve, generator = load_vertex(walk, 0)
    if not 1 <= max_edges <= header["requested_edges"]:
        raise ValueError("max_edges outside archived walk")
    graph_hash, script_hash = digest(walk), digest(__file__)
    p, r = header["p"], header["r"]
    field = GF(p)
    if resume:
        state, previous_digest = load_chain(directory, header, graph_hash, script_hash)
        start = state["index"] + 1
        base, generator = state["base"], state["generator"]
        model = state["model"]
    else:
        directory.mkdir(mode=0o700, parents=False, exist_ok=False)
        atomic_new(directory / "manifest.json", {"schema": SCHEMA, "stratum": stratum,
                    "graph_sha256": graph_hash, "script_sha256": script_hash,
                    "sage_version": str(sage_version), "p": p, "r": r,
                    "signed_base_points": 2 * SCHEDULE[stratum]["B"],
                    "check_stride": SCHEDULE[stratum]["power_stride"]})
        base, _ = base_points(curve, SCHEDULE[stratum]["B"], "low_x", b"B" * 32,
                              stratum, model["j"])
        base = [list(point) for point in base]
        generator = list(generator)
        state = {"index": 0, "model": model, "base": base, "base_sha256": points_digest(base),
                 "generator": generator, "previous_checkpoint_sha256": None,
                 "check_vertex": True, "map": None}
        previous_digest = atomic_new(checkpoint_path(directory, 0), state)
        start = 1
    with walk.open(encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            edge = json.loads(line)
            if edge["kind"] != "edge":
                break
            index = edge["index"]
            if index < start:
                continue
            if index > max_edges:
                break
            begun = time.monotonic()
            if edge["source"] != model:
                raise ValueError("checkpoint source differs from saved walk")
            source = SageCurve(field, [model["a"], model["b"]])
            ring = PolynomialRing(field, "x")
            polynomial = ring(edge["kernel_polynomial"])
            phi = source.isogeny(polynomial)
            if str(phi.kernel_polynomial()) != edge["kernel_polynomial"] or int(phi.degree()) != 7:
                raise ValueError("kernel or degree differs")
            if int(phi.scaling_factor()) != 1:
                raise ValueError("expected normalized isogeny")
            raw = phi.codomain()
            if [int(raw.a4()), int(raw.a6()), int(raw.j_invariant())] != [edge["raw_codomain"][key] for key in ("a", "b", "j")]:
                raise ValueError("raw codomain differs")
            next_model = edge["canonical_codomain"]
            canonical = SageCurve(field, [next_model["a"], next_model["b"]])
            iso = raw.isomorphism_to(canonical)
            maps = str(iso.rational_maps())
            if maps != edge["codomain_isomorphism"]:
                raise ValueError("codomain isomorphism differs")
            xexpr, yexpr = maps.strip()[1:-1].split(",")
            sx, sy = scale_component(xexpr, "x", p), scale_component(yexpr, "y", p)
            xmap = phi.x_rational_map()
            numerator = [int(c) for c in xmap.numerator().list()]
            denominator = [int(c) for c in xmap.denominator().list()]
            next_base = map_orbits(base, numerator, denominator, sx, sy, p)
            next_generator = map_one(generator, numerator, denominator, sx, sy, p)
            if next_generator != edge["image_generator"]:
                raise ValueError("saved image generator differs")
            dual = phi.dual()
            for sample in [generator, *base[:16]]:
                sage_point = source(field(sample[0]), field(sample[1]))
                mapped = iso(phi(sage_point))
                if point_pair(mapped) != map_one(sample, numerator, denominator, sx, sy, p):
                    raise ValueError("fast map differs from Sage")
                if dual(phi(sage_point)) != 7 * sage_point:
                    raise ValueError("dual identity differs")
            check_vertex = index % SCHEDULE[stratum]["power_stride"] == 0
            if check_vertex or index == max_edges:
                checker = CheckCurve(p, next_model["a"], next_model["b"])
                if len({point[0] for point in next_base}) != SCHEDULE[stratum]["B"]:
                    raise ValueError("transported base lost x-orbit")
                if not all(checker.is_on_curve(tuple(point)) for point in next_base):
                    raise ValueError("transported base left codomain")
            state = {"index": index, "model": next_model, "base": next_base,
                     "base_sha256": points_digest(next_base), "generator": next_generator,
                     "previous_checkpoint_sha256": previous_digest,
                     "check_vertex": check_vertex, "terminal_control": index == max_edges,
                     "map": {"kernel_polynomial": edge["kernel_polynomial"],
                             "numerator": numerator, "denominator": denominator,
                             "x_scale": sx, "y_scale": sy},
                     "sage_sample_and_dual_checks": 17,
                     "elapsed_seconds": time.monotonic() - begun}
            previous_digest = atomic_new(checkpoint_path(directory, index), state)
            base, generator, model = next_base, next_generator, next_model
            print(json.dumps({"stratum": stratum, "index": index, "j": model["j"],
                              "base_sha256": state["base_sha256"],
                              "elapsed_seconds": state["elapsed_seconds"]}), flush=True)
    return {"stratum": stratum, "last_index": min(max_edges, header["requested_edges"]),
            "checkpoints": max_edges + 1, "output": str(directory),
            "last_checkpoint_sha256": previous_digest}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stratum", choices=sorted(WALKS), required=True)
    parser.add_argument("--max-edges", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.stratum, args.max_edges, args.output_dir, args.resume), sort_keys=True))
