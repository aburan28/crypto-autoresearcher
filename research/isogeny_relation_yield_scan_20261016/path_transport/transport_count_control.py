"""Prepare and compare public targetwise count controls at first check vertices.

The fixed targets in this file are implementation controls, not discovery or
confirmation samples.  The C++ ordered-count oracle is run separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "conductor_relation_yield_20261014"))
from verify_collector import Curve, add, certify_group, multiply, on_curve, parse_input  # noqa: E402
from verify_chain import verify  # noqa: E402

CHECK = {"P29": ("p29-twoedge-attempt1", 8), "P37": ("p37-twoedge-attempt1", 4)}
COUNT = 128
DOMAIN = b"ectd-transport-count-control-v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checkpoint(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scalar_targets(stratum: str, r: int) -> list[tuple[int, int, int]]:
    """Public, deterministic distinct scalars; no sampling inference follows."""
    targets = []
    seen = set()
    attempt = 0
    while len(targets) < COUNT:
        material = DOMAIN + b"|" + stratum.encode() + b"|" + str(attempt).encode()
        scalar = 1 + int.from_bytes(hashlib.sha256(material).digest(), "big") % (r - 1)
        attempt += 1
        if scalar in seen:
            continue
        seen.add(scalar)
        beta = 1 + len(targets) % 7
        alpha = (scalar - 7 * beta) % r
        targets.append((alpha, beta, scalar))
    return targets


def make_input(record: dict, p: int, r: int, targets: list[tuple[int, int, int]]) -> bytes:
    model = record["model"]
    curve = Curve(p, model["a"], model["b"], r)
    generator = tuple(record["generator"])
    certify_group(curve, generator)
    base = [tuple(point) for point in record["base"]]
    if len(base) % 2 or len({point[0] for point in base}) != len(base) // 2:
        raise ValueError("base orbit count differs")
    if any(not on_curve(point, curve) for point in base):
        raise ValueError("base point off curve")
    lines = [f"curve {p} {curve.a} {curve.b} {r} {len(base)} {len(targets)}"]
    lines.extend(f"base {index} {x} {y}" for index, (x, y) in enumerate(base))
    for index, (alpha, beta, scalar) in enumerate(targets):
        point = multiply(scalar, generator, curve)
        if point is None:
            raise ValueError("control target is identity")
        lines.append(f"target {index} {alpha} {beta} {point[0]} {point[1]}")
    return ("\n".join(lines) + "\n").encode()


def prepare(stratum: str, output: Path) -> dict:
    checkpoint_dir = HERE / "controls" / CHECK[stratum][0]
    terminal = CHECK[stratum][1]
    replay = verify(stratum, checkpoint_dir)
    if replay["edges_checked"] != terminal or replay["status"] != "pass":
        raise ValueError("checkpoint has unexpected extent or verification status")
    source_path = checkpoint_dir / "edge-0000.json"
    destination_path = checkpoint_dir / f"edge-{terminal:04d}.json"
    source, destination = checkpoint(source_path), checkpoint(destination_path)
    if source["index"] != 0 or destination["index"] != terminal:
        raise ValueError("checkpoint indices differ")
    walk = HERE.parent / ("walk-p29-2048-attempt2.jsonl" if stratum == "P29" else "walk-p37-256.jsonl")
    header = json.loads(walk.open(encoding="utf-8").readline())
    targets = scalar_targets(stratum, header["r"])
    output.mkdir(parents=True, exist_ok=False)
    inputs = {}
    for label, record in (("source", source), ("transported", destination)):
        path = output / f"{label}.txt"
        with path.open("xb") as stream:
            stream.write(make_input(record, header["p"], header["r"], targets))
        inputs[label] = {"path": path.name, "sha256": digest(path), "model_j": record["model"]["j"]}
    result = {
        "schema": "ectd-transport-count-control/v1", "stratum": stratum,
        "mode": "public_implementation_control", "targets": COUNT,
        "target_rule": "fixed SHA-256 scalar labels; alpha=(s-7*beta) mod r, Q=[7]G",
        "domain_utf8": DOMAIN.decode(), "source_index": 0, "destination_index": terminal,
        "checkpoint_replay": replay, "source_checkpoint_sha256": digest(source_path),
        "destination_checkpoint_sha256": digest(destination_path),
        "producer_sha256": digest(Path(__file__)), "inputs": inputs,
    }
    with (output / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    return result


def count_lines(path: Path, curve: Curve, nbase: int, expected: int) -> list[int]:
    rows = [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines()]
    header = ["count-v1", str(curve.p), str(curve.r), str(nbase), str(expected)]
    if len(rows) != expected + 1 or rows[0] != header:
        raise ValueError("count output header or length differs")
    counts = []
    for index, row in enumerate(rows[1:]):
        if len(row) != 3 or row[:2] != ["target", str(index)]:
            raise ValueError("count output target order differs")
        count = int(row[2])
        if count < 0:
            raise ValueError("negative count")
        counts.append(count)
    return counts


def compare(output: Path) -> dict:
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    if manifest["schema"] != "ectd-transport-count-control/v1":
        raise ValueError("manifest schema differs")
    stratum = manifest["stratum"]
    checkpoint_dir = HERE / "controls" / CHECK[stratum][0]
    replay = verify(stratum, checkpoint_dir)
    if replay != manifest["checkpoint_replay"]:
        raise ValueError("checkpoint replay differs")
    if manifest["producer_sha256"] != digest(Path(__file__)):
        raise ValueError("producer hash differs")
    input_data = {}
    for label, item in manifest["inputs"].items():
        if digest(output / item["path"]) != item["sha256"]:
            raise ValueError("input digest differs")
        index = 0 if label == "source" else CHECK[stratum][1]
        saved = checkpoint(checkpoint_dir / f"edge-{index:04d}.json")
        if [digest(checkpoint_dir / f"edge-{index:04d}.json"), item["model_j"]] != [
            manifest[f"{label if label == 'source' else 'destination'}_checkpoint_sha256"], saved["model"]["j"]
        ]:
            raise ValueError("checkpoint identity differs")
        curve, base, targets = parse_input(output / item["path"])
        generator = tuple(saved["generator"])
        certify_group(curve, generator)
        if base != [tuple(point) for point in saved["base"]]:
            raise ValueError("prepared base differs from checkpoint")
        q = multiply(7, generator, curve)
        if any(add(multiply(alpha, generator, curve), multiply(beta, q, curve), curve) != point
               for alpha, beta, point in targets):
            raise ValueError("prepared target equation differs")
        input_data[label] = (curve, base, targets)
    if [(alpha, beta) for alpha, beta, _ in input_data["source"][2]] != [
        (alpha, beta) for alpha, beta, _ in input_data["transported"][2]
    ]:
        raise ValueError("paired coefficient stream differs")
    source_path, transported_path = output / "source.count", output / "transported.count"
    source = count_lines(source_path, input_data["source"][0], len(input_data["source"][1]), manifest["targets"])
    transported = count_lines(transported_path, input_data["transported"][0], len(input_data["transported"][1]), manifest["targets"])
    if source != transported:
        first = next(i for i, pair in enumerate(zip(source, transported)) if pair[0] != pair[1])
        raise ValueError(f"targetwise count differs at {first}: {source[first]} versus {transported[first]}")
    result = {
        "schema": "ectd-transport-count-comparison/v1", "stratum": manifest["stratum"],
        "targets_compared": len(source), "targets_with_ordered_relations": sum(value > 0 for value in source),
        "total_ordered_relations": sum(source), "source_count_sha256": digest(source_path),
        "transported_count_sha256": digest(transported_path), "status": "pass",
        "scope": "fixed public implementation control; no discovery yield or cost inference",
    }
    path = output / "comparison.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "compare"))
    parser.add_argument("--stratum", choices=tuple(CHECK))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare" and args.stratum is None:
        parser.error("prepare needs --stratum")
    print(json.dumps(prepare(args.stratum, args.output) if args.command == "prepare" else compare(args.output), sort_keys=True))
