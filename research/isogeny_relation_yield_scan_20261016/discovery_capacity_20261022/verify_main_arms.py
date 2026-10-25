"""Independently bind the main-arm plan to walk models and group arithmetic."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(ROOT))
from harness.toycurve import EllipticCurve

WALKS = {"P29": ("walk-p29-2048-attempt2.jsonl", 256, 8192, 8),
         "P37": ("walk-p37-256.jsonl", 1600, 2048, 4)}
ARMS = ("low_x", "mid_x", "random_x")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scale(expr: str, variable: str, p: int) -> int:
    expr = expr.strip().replace(" ", "")
    if expr == variable:
        return 1
    if expr == "-" + variable:
        return p - 1
    if match := re.fullmatch(r"(-?\d+)\*" + variable, expr):
        return int(match.group(1)) % p
    if match := re.fullmatch(variable + r"/(\d+)", expr):
        return pow(int(match.group(1)), -1, p)
    raise ValueError("source scaling is not in the frozen grammar")


plan = HERE / "main-arms.jsonl"
manifest = json.loads((HERE / "main-arms-manifest.json").read_text())
if manifest["main_arms_sha256"] != digest(plan):
    raise ValueError("main-arm file differs from manifest")
rows = [json.loads(line) for line in plan.read_text().splitlines()]
if len(rows) != 6918 or len({row["arm_key"] for row in rows}) != len(rows):
    raise ValueError("main-arm extent or keys differ")

position = 0
vertices_checked = 0
images_checked = 0
for stratum, (filename, base_size, quota, stride) in WALKS.items():
    with (STUDY / filename).open() as stream:
        header = json.loads(next(stream))
        edges = [json.loads(line) for line in stream]
    p, r = header["p"], header["r"]
    map_text = header["source_isomorphism"].strip()
    if not map_text.startswith("(") or not map_text.endswith(")"):
        raise ValueError("source isomorphism tuple differs")
    xpart, ypart = map_text[1:-1].split(",")
    sx, sy = scale(xpart, "x", p), scale(ypart, "y", p)
    source_g = (header["source_generator"][0] * sx % p,
                header["source_generator"][1] * sy % p)
    old, source = header["original_source"], header["canonical_source"]
    if sy * sy % p != sx * sx * sx % p or old["a"] * sx * sx % p != source["a"] or old["b"] * sy * sy % p != source["b"]:
        raise ValueError("source-model isomorphism differs")
    expected = [(source, source_g)]
    previous = source
    complete = None
    for item in edges:
        if item["kind"] == "edge":
            if item["index"] != len(expected) or item["source"] != previous:
                raise ValueError("walk continuity differs")
            previous = item["canonical_codomain"]
            expected.append((previous, tuple(item["image_generator"])))
        elif item["kind"] == "complete" and complete is None:
            complete = item
        else:
            raise ValueError("unexpected graph record")
    if len(expected) != header["requested_edges"] + 1 or complete is None or complete["edges"] != header["requested_edges"]:
        raise ValueError("walk extent differs")
    if manifest["inputs"][stratum]["walk_sha256"] != digest(STUDY / filename):
        raise ValueError("walk digest differs")
    for index, (model, generator) in enumerate(expected):
        checker = EllipticCurve(p, model["a"], model["b"])
        if not checker.is_on_curve(generator) or checker.mul(r, generator) is not None:
            raise ValueError("generator identity or subgroup differs")
        for arm in ARMS:
            row = rows[position]
            position += 1
            if (row["arm_key"] != f"{stratum}-v{index:04d}-{arm}" or
                row["stratum"] != stratum or row["path_index"] != index or
                row["p"] != p or row["r"] != r or row["model"] != model or
                tuple(row["generator"]) != generator or row["base_rule"] != arm or
                row["base_x_orbits"] != base_size or row["discovery_targets"] != quota or
                row["check_vertex"] != (index % stride == 0)):
                raise ValueError(f"arm binding differs at {stratum} vertex {index}, {arm}")
        vertices_checked += 1
        images_checked += 1
if position != len(rows) or sum(row["discovery_targets"] for row in rows) != 51935232:
    raise ValueError("arm count or target-probe sum differs")
receipt = {"schema": "ectd-main-arm-plan-verification/v1", "status": "pass",
           "arms_checked": position, "vertices_checked": vertices_checked,
           "generator_group_checks": images_checked, "target_probes": 51935232,
           "main_arms_sha256": digest(plan),
           "checks": ["walk continuity", "canonical model and generator identity",
                      "independent point membership and prime-order subgroup multiplication",
                      "fixed arm order and discovery quotas"],
           "limit": "plan identity only; no target seed, base instance, relation yield, rank, or ECDLP result"}
(HERE / "main-arms-verification.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps(receipt, sort_keys=True))
