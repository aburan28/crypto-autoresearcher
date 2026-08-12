#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
RELATION_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-COORD-EXPANSION-001" / "src" / "typed_tt_batched_relation_transcript.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RELATION = load("rank_completion_relation_baseline", RELATION_SOURCE)
TF = RELATION.TF


def target_transcript(curve_record: dict[str, Any], family: dict[str, Any], relation_target_count: int) -> list[dict[str, Any]]:
    curve = TF.Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    generator = TF.point_from_json(curve_record["generator"])
    a_points = [TF.point_from_json(value) for value in family["progression"]["points"]]
    r_points = [TF.point_from_json(value) for value in family["factor_base"]["points"]]
    materialized = TF.compile_r_support(curve, r_points)
    target_ops = TF.Ops()
    seed = family["run_seed"] ^ 0x13198A2E
    targets: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for index, scalar in enumerate(TF.nonzero_scalar_stream(curve_record["q"], seed)):
        if index == relation_target_count:
            break
        target = curve.mul(scalar, generator, target_ops)
        target_json = TF.point_json(target)
        baseline = TF.query_d4_all(curve, a_points, r_points, materialized["d4_internal"], target)
        target_tuple = (int(target_json[0]), int(target_json[1]))
        seen.add(target_tuple)
        targets.append({"target_index": index, "scalar": int(scalar), "target": target_json, "label": f"relation_{index}", "held_out_supported": False, "expected_witness": None, "baseline_hits": baseline["hits"]})
    held_out_added = 0
    for item in family["held_out_descent"]["transcript"]:
        if held_out_added == 4:
            break
        if not (item["materialized_d4"]["success"] and item["r_scan_plus_d3"]["success"]):
            continue
        target_json = item["target"]
        target_tuple = (int(target_json[0]), int(target_json[1]))
        if target_tuple in seen:
            continue
        target = TF.point_from_json(target_json)
        baseline = TF.query_d4_all(curve, a_points, r_points, materialized["d4_internal"], target)
        targets.append({"target_index": len(targets), "scalar": int(item["scalar"]), "target": target_json, "label": f"held_out_supported_{held_out_added}", "held_out_supported": True, "expected_witness": {"a_index": item["r_scan_plus_d3"]["a_index"], "r_witness": item["r_scan_plus_d3"]["r_witness"]}, "baseline_hits": baseline["hits"]})
        seen.add(target_tuple)
        held_out_added += 1
    return targets


def write_fixture_record(output_path: Path, fixture_path: Path, curve_id: str, families: list[str], relation_target_count: int = 29) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    instance = next(item for item in fixture["instances"] if item["curve"]["id"] == curve_id)
    by_family = {item["family"]: item for item in instance["families"]}
    rows = [{"curve_id": curve_id, "family": family, "shared_candidate": {"transcripts": target_transcript(instance["curve"], by_family[family], relation_target_count)}} for family in families]
    record = {"protocol": "EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001-input-v1", "curve_id": curve_id, "families": families, "relation_target_count": relation_target_count, "rows": rows}
    output_path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return record
