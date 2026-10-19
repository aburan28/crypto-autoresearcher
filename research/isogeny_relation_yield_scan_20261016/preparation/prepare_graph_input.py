"""Prepare one graph vertex/base arm for the existing exact triple collector.

The CLI requires post-freeze seed commitments and fixed discovery/confirmation
quotas. Import ``prepare`` for small implementation controls only. This module
does not launch relation collection or infer an ECDLP cost.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "research" / "conductor_relation_yield_20261014"
sys.path.insert(0, str(LEGACY))
from prepare_input import lift  # exact square-root and sign convention
from verify_collector import Curve, certify_group, multiply, negative, on_curve

SCHEMA = "isogeny-relation-input/v1"
ARMS = ("low_x", "mid_x", "random_x", "power_x", "u2_native", "u2_transport")
SCHEDULE = {"P29": {"B": 256, "discovery": 8192, "confirmation": 32768, "power_stride": 8},
            "P37": {"B": 1600, "discovery": 2048, "confirmation": 32768, "power_stride": 4}}
SOURCES = [Path(__file__), LEGACY / "prepare_input.py", LEGACY / "verify_collector.py"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scale_component(expr, variable, p):
    expr = expr.strip().replace(" ", "")
    if expr == variable:
        return 1
    if expr == "-" + variable:
        return p - 1
    match = re.fullmatch(r"(-?\d+)\*" + variable, expr)
    if match:
        return int(match.group(1)) % p
    match = re.fullmatch(variable + r"/(\d+)", expr)
    if match:
        return pow(int(match.group(1)), -1, p)
    raise ValueError("unexpected source isomorphism format: " + expr)


def source_generator(header):
    p = header["p"]
    text = header["source_isomorphism"].strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError("unexpected source isomorphism tuple")
    xexpr, yexpr = text[1:-1].split(",")
    sx, sy = scale_component(xexpr, "x", p), scale_component(yexpr, "y", p)
    if (sy * sy - sx * sx * sx) % p:
        raise ValueError("source isomorphism scaling is invalid")
    original, canonical = header["original_source"], header["canonical_source"]
    if canonical["a"] != original["a"] * sx * sx % p or canonical["b"] != original["b"] * sy * sy % p:
        raise ValueError("source models disagree with recorded isomorphism")
    gx, gy = header["source_generator"]
    return gx * sx % p, gy * sy % p


def load_vertex(walk_path, index):
    with Path(walk_path).open(encoding="utf-8") as source:
        header = json.loads(next(source))
        if header.get("schema") != "ectd.degree7.walk.v1" or header["stratum"] not in SCHEDULE:
            raise ValueError("unsupported graph header")
        if not 0 <= index <= header["requested_edges"]:
            raise ValueError("vertex index outside fixed walk")
        selected = None
        previous = header["canonical_source"]
        seen = {previous["j"]}
        edges = 0
        complete = None
        for line in source:
            row = json.loads(line)
            if row["kind"] == "edge":
                edges += 1
                if row["index"] != edges or row["source"] != previous:
                    raise ValueError("graph path continuity failed")
                previous = row["canonical_codomain"]
                if previous["j"] in seen:
                    raise ValueError("graph repeated j")
                seen.add(previous["j"])
                if edges == index:
                    selected = row
            elif row["kind"] == "complete" and complete is None:
                complete = row
            else:
                raise ValueError("unexpected graph record")
        if complete is None or edges != header["requested_edges"] or complete["edges"] != edges or complete["distinct_vertices"] != len(seen):
            raise ValueError("incomplete graph walk")
    model = header["canonical_source"] if index == 0 else selected["canonical_codomain"]
    generator = source_generator(header) if index == 0 else tuple(selected["image_generator"])
    curve = Curve(header["p"], model["a"], model["b"], header["r"])
    certify_group(curve, generator)
    return header, model, curve, generator


def draw(root, domain, modulus):
    if len(root) != 32 or modulus < 1:
        raise ValueError("draw requires a 256-bit root and positive modulus")
    retry = 0
    cap = (1 << 256) // modulus * modulus
    while True:
        packed = json.dumps([SCHEMA, *domain, retry], separators=(",", ":")).encode()
        value = int.from_bytes(hashlib.sha256(root + b"\0" + packed).digest(), "big")
        if value < cap:
            return value % modulus, retry
        retry += 1


def prime_factors(value):
    factors = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    return factors


def least_primitive_root(p):
    factors = prime_factors(p - 1)
    return next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in factors))


def base_points(curve, count, arm, base_root, stratum, vertex_j):
    selected = []
    seen = set()
    rejections = {"nonliftable": 0, "repeated_x": 0, "modulo": 0}
    if arm == "low_x" or arm == "u2_native":
        candidates = (x for x in range(curve.p))
    elif arm == "mid_x":
        candidates = ((curve.p // 2 + offset) % curve.p for offset in range(curve.p))
    elif arm == "power_x":
        generator = least_primitive_root(curve.p)
        candidates = (pow(generator, exponent, curve.p) for exponent in range(curve.p - 1))
    elif arm == "random_x":
        def random_candidates():
            attempt = 0
            while True:
                x, skipped = draw(base_root, [stratum, vertex_j, "random_x", attempt], curve.p)
                rejections["modulo"] += skipped
                attempt += 1
                yield x
        candidates = random_candidates()
    else:
        raise ValueError("unsupported native base rule")
    for x in candidates:
        if x in seen:
            rejections["repeated_x"] += 1
            continue
        point = lift(x, curve)
        if point is None:
            rejections["nonliftable"] += 1
            continue
        seen.add(x)
        selected.extend((point, negative(point, curve)))
        if len(seen) == count:
            return selected, rejections
    raise ValueError("insufficient liftable x-values")


def target_coefficients(root, stratum, stage, r, count):
    k, _ = draw(root, [stratum, stage, "q_scalar"], r - 1)
    k += 1
    accepted, seen = [], set()
    rejects = {"identity": 0, "duplicate": 0, "modulo": 0}
    for index in range(count):
        retry = 0
        while True:
            alpha, ra = draw(root, [stratum, stage, "alpha", index, retry], r)
            beta, rb = draw(root, [stratum, stage, "beta", index, retry], r - 1)
            beta += 1
            rejects["modulo"] += ra + rb
            scalar = (alpha + beta * k) % r
            if scalar == 0:
                rejects["identity"] += 1
            elif scalar in seen:
                rejects["duplicate"] += 1
            else:
                seen.add(scalar)
                accepted.append((alpha, beta, scalar))
                break
            retry += 1
    return k, accepted, rejects


def transform(point, p):
    return point[0] * 4 % p, point[1] * 8 % p


def prepare(walk_path, index, arm, stage, base_root, target_root, target_count):
    header, model, curve, generator = load_vertex(walk_path, index)
    stratum = header["stratum"]
    config = SCHEDULE[stratum]
    if arm not in ARMS or stage not in ("discovery", "confirmation"):
        raise ValueError("unsupported arm or stage")
    if arm == "power_x" and index % config["power_stride"]:
        raise ValueError("power_x is only defined on prespecified path indices")
    k, coefficients, target_rejections = target_coefficients(target_root, stratum, stage, curve.r, target_count)
    q = multiply(k, generator, curve)
    if q is None:
        raise AssertionError("selected Q is identity")
    targets = [(a, b, multiply(s, generator, curve)) for a, b, s in coefficients]
    if any(point is None for _, _, point in targets):
        raise AssertionError("target construction failed")
    if arm in ("u2_native", "u2_transport"):
        result_curve = Curve(curve.p, 16 * curve.a % curve.p, 64 * curve.b % curve.p, curve.r)
        result_generator, result_q = transform(generator, curve.p), transform(q, curve.p)
        targets = [(a, b, transform(point, curve.p)) for a, b, point in targets]
        if arm == "u2_transport":
            source_base, base_rejections = base_points(curve, config["B"], "low_x", base_root, stratum, model["j"])
            base = [transform(point, curve.p) for point in source_base]
        else:
            base, base_rejections = base_points(result_curve, config["B"], "u2_native", base_root, stratum, model["j"])
    else:
        result_curve, result_generator, result_q = curve, generator, q
        base, base_rejections = base_points(curve, config["B"], arm, base_root, stratum, model["j"])
    if len({point[0] for point in base}) != config["B"] or not all(on_curve(point, result_curve) for point in base):
        raise AssertionError("invalid factor base")
    rows = [f"curve {result_curve.p} {result_curve.a} {result_curve.b} {result_curve.r} {len(base)} {len(targets)}"]
    rows.extend(f"base {i} {x} {y}" for i, (x, y) in enumerate(base))
    rows.extend(f"target {i} {a} {b} {point[0]} {point[1]}" for i, (a, b, point) in enumerate(targets))
    payload = ("\n".join(rows) + "\n").encode()
    metadata = {"schema": SCHEMA, "stratum": stratum, "index": index, "j": model["j"],
                "arm": arm, "stage": stage, "target_count": target_count,
                "schedule_conformant": target_count == config[stage], "base_abscissae": config["B"],
                "generator": result_generator, "Q": result_q,
                "base_rejections": base_rejections, "target_rejections": target_rejections,
                "base_root_sha256": hashlib.sha256(base_root).hexdigest(),
                "target_root_sha256": hashlib.sha256(target_root).hexdigest(),
                "graph_sha256": digest(walk_path), "source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in SOURCES},
                "input_sha256": hashlib.sha256(payload).hexdigest(),
                "base_sha256": hashlib.sha256(json.dumps(base, separators=(",", ":")).encode()).hexdigest(),
                "target_vector_sha256": hashlib.sha256(json.dumps(targets, separators=(",", ":")).encode()).hexdigest(),
                "limits": "prepared input only; no relation yield or ECDLP cost claim"}
    return payload, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--walk", type=Path, required=True)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--stage", choices=("discovery", "confirmation"), required=True)
    parser.add_argument("--base-root-file", type=Path, required=True)
    parser.add_argument("--target-root-file", type=Path, required=True)
    parser.add_argument("--commitment", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    base_root = bytes.fromhex(args.base_root_file.read_text().strip())
    target_root = bytes.fromhex(args.target_root_file.read_text().strip())
    if len(base_root) != 32 or len(target_root) != 32 or base_root == target_root:
        parser.error("distinct 256-bit base and target roots are required")
    commitment = json.loads(args.commitment.read_text())
    if commitment.get("schema") != "isogeny-relation-seed-commitment/v1":
        parser.error("invalid commitment schema")
    graph_manifest = STUDY / "manifest-v2.json"
    frozen_manifest = json.loads(graph_manifest.read_text())
    graph_entry = frozen_manifest["files"].get(args.walk.name)
    if graph_entry is None or graph_entry["sha256"] != digest(args.walk):
        parser.error("graph differs from the archived verified walk")
    verification_name = "verification-" + json.loads(args.walk.open().readline())["stratum"].lower() + "-full.json"
    if frozen_manifest["files"].get(verification_name, {}).get("sha256") != digest(STUDY / verification_name):
        parser.error("graph verification receipt differs from the archive")
    verification = json.loads((STUDY / verification_name).read_text())[0]
    if not verification["complete"] or verification["checked_edges"] != json.loads(args.walk.open().readline())["requested_edges"]:
        parser.error("full graph verification receipt is absent or incomplete")
    expected = {"base_root_sha256": hashlib.sha256(base_root).hexdigest(),
                "target_root_sha256": hashlib.sha256(target_root).hexdigest(),
                "graph_sha256": digest(args.walk),
                "graph_manifest_sha256": digest(graph_manifest)}
    if any(commitment.get(key) != value for key, value in expected.items()):
        parser.error("seed or graph commitment mismatch")
    for path in SOURCES:
        name = str(path.relative_to(ROOT))
        if commitment.get("source_sha256", {}).get(name) != digest(path):
            parser.error("source hash mismatch: " + name)
    header = json.loads(args.walk.open().readline())
    count = SCHEDULE[header["stratum"]][args.stage]
    payload, metadata = prepare(args.walk, args.index, args.arm, args.stage, base_root, target_root, count)
    metadata["commitment_sha256"] = digest(args.commitment)
    args.output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    with (args.output_dir / "prepared.txt").open("xb") as output:
        output.write(payload)
        output.flush()
    with (args.output_dir / "manifest.json").open("x") as output:
        json.dump(metadata, output, indent=2, sort_keys=True)
        output.write("\n")
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
