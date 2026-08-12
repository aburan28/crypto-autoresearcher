#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import resource
import time
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
BASE_PATH = SCRIPT_PATH.with_name("d4_membership_recovery.py")
PREDECESSOR_VERIFICATION = SCRIPT_PATH.parent.parent / "development" / "D4-MEMBERSHIP-RECOVERY-V1" / "RUN-001" / "verification.json"


def load_base():
    spec = importlib.util.spec_from_file_location("d4_membership_recovery_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load predecessor route")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


BASE = load_base()


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def target_schedules(curve, record: dict[str, Any], family: dict[str, Any], d4_points: list[Any], maximum: int) -> tuple[dict[str, list[Any]], dict[str, int]]:
    a_points = [BASE.as_point(value) for value in family["progression"]["points"]]
    planted = BASE.as_point(family["relations"]["target_transcript"][0]["target"])
    generator = BASE.as_point(record["generator"])
    translated = []
    supported = []
    translated_ops = BASE.empty_ops(); supported_ops = BASE.empty_ops(); current = planted
    for index in range(maximum):
        translated.append(current)
        current = curve.add(current, generator, translated_ops)
        supported.append(curve.add(a_points[index % len(a_points)], d4_points[index % len(d4_points)], supported_ops))
    return {"translated_control": translated, "supported_batch": supported}, {"translated_control": sum(translated_ops.values()), "supported_batch": sum(supported_ops.values())}


def route(curve, a_points, sources, d2, d4, target):
    d2_ops = BASE.empty_ops(); d4_ops = BASE.empty_ops(); member_ops = BASE.empty_ops()
    recursive_hits, recursive_metrics = BASE.query_recursive(curve, a_points, sources, d2, target, d2_ops)
    materialized_hits, materialized_metrics = BASE.query_materialized(curve, a_points, sources, d4, target, d4_ops)
    member_hits, member_metrics = BASE.query_membership_recovery(curve, a_points, sources, d2, set(d4), target, member_ops)
    d2_adv = BASE.advice_d2(d2); d4_records = sum(len(value) for value in d4.values())
    member_adv = {"d2_base": d2_adv, "support_state_count": len(d4), "support_key_field_elements": 2 * len(d4), "logical_advice_words": d2_adv["logical_advice_words"] + 2 * len(d4)}
    d4_adv = {"state_count": len(d4), "witness_records": d4_records, "key_field_elements": 2 * len(d4), "witness_index_words": 4 * d4_records, "logical_advice_words": 2 * len(d4) + 4 * d4_records}
    routes = {
        "recursive_d2": {"hits": sorted([list(item) for item in recursive_hits]), "metrics": recursive_metrics, "ops": d2_ops, "advice": d2_adv},
        "materialized_d4": {"hits": sorted([list(item) for item in materialized_hits]), "metrics": materialized_metrics, "ops": d4_ops, "advice": d4_adv},
        "membership_recovery": {"hits": sorted([list(item) for item in member_hits]), "metrics": member_metrics, "ops": member_ops, "advice": member_adv},
    }
    for item in routes.values():
        online = sum(item["ops"].values()); words = item["advice"]["logical_advice_words"]
        item["frontier"] = {"online_work": online, "advice_words": words, "success": bool(item["hits"])}
    return routes


def run_row(record: dict[str, Any], family: dict[str, Any], batch_sizes: list[int]) -> dict[str, Any]:
    curve = BASE.AffineCurve(record["p"], record["a"], record["b"]); a_points = [BASE.as_point(value) for value in family["progression"]["points"]]; sources = [BASE.as_point(value) for value in family["factor_base"]["points"]]
    d2_build = BASE.empty_ops(); d4_build = BASE.empty_ops(); d2 = BASE.states(curve, sources, 2, d2_build); d4 = BASE.states(curve, sources, 4, d4_build); d4_points = sorted(d4, key=BASE.point_key)
    schedules, schedule_ops = target_schedules(curve, record, family, d4_points, max(batch_sizes)); batches = []
    advice = {"d2": BASE.advice_d2(d2), "d4": {"state_count": len(d4), "witness_records": sum(len(value) for value in d4.values()), "logical_advice_words": 2 * len(d4) + 4 * sum(len(value) for value in d4.values())}, "membership_recovery": {"d2_base": BASE.advice_d2(d2), "support_state_count": len(d4), "support_key_field_elements": 2 * len(d4), "logical_advice_words": BASE.advice_d2(d2)["logical_advice_words"] + 2 * len(d4)}}
    for schedule_name, schedule in schedules.items():
        for batch_size in batch_sizes:
            target_rows = []
            for index, target in enumerate(schedule[:batch_size]):
                routes = route(curve, a_points, sources, d2, d4, target)
                target_rows.append({"index": index, "target": BASE.point_json(target), "routes": routes, "all_routes_equal": all(item["hits"] == routes["recursive_d2"]["hits"] for item in routes.values())})
            aggregates = {}
            for route_name in ("recursive_d2", "materialized_d4", "membership_recovery"):
                values = [row["routes"][route_name] for row in target_rows]; successful = sum(int(item["frontier"]["success"]) for item in values); total_work = sum(item["frontier"]["online_work"] for item in values); epsilon = successful / batch_size
                aggregates[route_name] = {"advice_words": advice["d2" if route_name == "recursive_d2" else "d4" if route_name == "materialized_d4" else "membership_recovery"]["logical_advice_words"], "successful_targets": successful, "epsilon": epsilon, "total_online_work": total_work, "amortized_online_work": total_work / batch_size, "S_T2_over_epsilon_q": None if epsilon == 0 else advice["d2" if route_name == "recursive_d2" else "d4" if route_name == "materialized_d4" else "membership_recovery"]["logical_advice_words"] * (total_work / batch_size) ** 2 / (epsilon * record["q"])}
            batches.append({"schedule": schedule_name, "batch_size": batch_size, "target_digest": digest([row["target"] for row in target_rows]), "targets": target_rows, "aggregates": aggregates, "all_routes_equal": all(row["all_routes_equal"] for row in target_rows)})
    return {"curve_id": record["id"], "family": family["family"], "p": record["p"], "q": record["q"], "a_size": len(a_points), "r_size": len(sources), "supports": {"d2": len(d2), "d4": len(d4)}, "state_digests": {"d2": digest(BASE.serialize_states(d2)), "d4": digest(BASE.serialize_states(d4))}, "advice": advice, "build_ops": {"d2": d2_build, "d4": d4_build}, "schedule_ops": schedule_ops, "batches": batches}


def replay(input_path: Path, families: list[str], batch_sizes: list[int]) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8")); rows = []
    for instance in source["instances"]:
        by_family = {item["family"]: item for item in instance["families"]}
        for family_name in families:
            rows.append(run_row(instance["curve"], by_family[family_name], batch_sizes))
    return {"protocol": "EXP-ECDLP-COORD-EXPANSION-001-d4-membership-batch-v1", "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND"], "source": {"producer_sha256": sha256_file(SCRIPT_PATH), "base_route_sha256": sha256_file(BASE_PATH), "predecessor_verification_sha256": sha256_file(PREDECESSOR_VERIFICATION), "input_sha256": sha256_file(input_path)}, "config": {"input_result": str(input_path.resolve()), "families": families, "batch_sizes": batch_sizes, "schedules": ["supported_batch", "translated_control"], "routes": ["recursive_d2", "materialized_d4", "membership_recovery"], "frontier": "shared logical advice, total/amortized online operation proxy, empirical epsilon, and S*(T/k)^2/(epsilon*q) diagnostic only", "predecessor": "D4-MEMBERSHIP-RECOVERY-V1/RUN-001"}, "rows": rows, "summary": {"cells": len(rows), "batches": sum(len(row["batches"]) for row in rows), "all_batches_exact": all(batch["all_routes_equal"] for row in rows for batch in row["batches"]), "algorithm_promotion_gate": False, "breakthrough_claim": False, "boundary": "Exact fixed-curve batch aggregation for D4 membership recovery; no generic ECDLP claim."}, "accounting": {"d2_build_adds": sum(row["build_ops"]["d2"]["point_add_calls"] for row in rows), "d4_build_adds": sum(row["build_ops"]["d4"]["point_add_calls"] for row in rows), "target_schedule_adds": sum(sum(row["schedule_ops"].values()) for row in rows)}}


def run(input_path: Path, families: list[str], batch_sizes: list[int]) -> dict[str, Any]:
    started = time.perf_counter(); result = replay(input_path, families, batch_sizes); result["peak_rss_bytes"] = rss_bytes(); result["total_wall_seconds"] = time.perf_counter() - started; return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("--families", nargs="+", required=True); parser.add_argument("--batch-sizes", nargs="+", type=int, default=[1, 4, 16, 64]); args = parser.parse_args()
    if any(size <= 0 for size in args.batch_sizes) or sorted(set(args.batch_sizes)) != args.batch_sizes:
        raise SystemExit("batch sizes must be positive and sorted")
    print(json.dumps(run(args.input, args.families, args.batch_sizes), sort_keys=True, separators=(",", ":"))); return 0


if __name__ == "__main__":
    raise SystemExit(main())
