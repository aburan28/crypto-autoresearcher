"""Materialize the proposed full discovery arm schedule without target seeds.

This is a candidate execution identity, not Coordinator approval or a trial plan.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CAPACITY = STUDY / "discovery_capacity_20261022"
sys.path.insert(0, str(STUDY / "preparation"))
from prepare_graph_input import CHECKPOINTS, SCHEDULE  # noqa: E402

MAIN = ("low_x", "mid_x", "random_x")
CHECK = ("power_x", "graph_transport", "u2_native", "u2_transport")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"write-once output differs: {path}")
    else:
        path.write_bytes(payload)


def main() -> None:
    old_manifest_path = CAPACITY / "main-arms-manifest.json"
    old_manifest = json.loads(old_manifest_path.read_text())
    old_verify_path = CAPACITY / "main-arms-verification.json"
    old_verify = json.loads(old_verify_path.read_text())
    main_path = CAPACITY / "main-arms.jsonl"
    if (old_manifest["main_arms_sha256"] != sha(main_path) or
            old_verify["status"] != "pass" or
            old_verify["main_arms_sha256"] != sha(main_path) or
            old_manifest["graph_manifest_sha256"] != sha(STUDY / "manifest-v2.json")):
        raise ValueError("the independently checked main-arm inventory differs")
    main_rows = [json.loads(line) for line in main_path.read_text().splitlines()]
    if len(main_rows) != 6918:
        raise ValueError("main-arm extent differs")
    rows: list[dict] = []
    checkpoint_bindings: dict[str, dict] = {}
    counts: dict[str, dict] = {}
    pos = 0
    for stratum in ("P29", "P37"):
        config = SCHEDULE[stratum]
        vertex_count = old_manifest["inputs"][stratum]["vertices"]
        walk_path = STUDY / old_manifest["inputs"][stratum]["walk"]
        checkpoint_dir = CHECKPOINTS[stratum]
        checkpoint_manifest_path = checkpoint_dir / "manifest.json"
        terminal_path = checkpoint_dir / f"edge-{vertex_count - 1:04d}.json"
        checkpoint_manifest = json.loads(checkpoint_manifest_path.read_text())
        if (checkpoint_manifest["graph_sha256"] != sha(walk_path) or
                checkpoint_manifest["check_stride"] != config["power_stride"]):
            raise ValueError(f"{stratum} checkpoint manifest differs")
        checkpoint_bindings[stratum] = {
            "manifest": str(checkpoint_manifest_path.relative_to(STUDY)),
            "manifest_sha256": sha(checkpoint_manifest_path),
            "terminal": str(terminal_path.relative_to(STUDY)),
            "terminal_sha256": sha(terminal_path),
        }
        check_count = 0
        for index in range(vertex_count):
            native = main_rows[pos:pos + 3]
            pos += 3
            if [row["base_rule"] for row in native] != list(MAIN) or any(
                    row["stratum"] != stratum or row["path_index"] != index or
                    row["discovery_targets"] != config["discovery"] for row in native):
                raise ValueError(f"{stratum} native arm order or quota differs at {index}")
            rows.extend(native)
            if index % config["power_stride"]:
                continue
            check_count += 1
            source = native[0]
            p = source["p"]
            canonical = source["model"]
            gx, gy = source["generator"]
            u2_model = {"a": 16 * canonical["a"] % p,
                        "b": 64 * canonical["b"] % p,
                        "j": canonical["j"]}
            u2_generator = [4 * gx % p, 8 * gy % p]
            checkpoint_path = checkpoint_dir / f"edge-{index:04d}.json"
            checkpoint = json.loads(checkpoint_path.read_text())
            if (checkpoint["index"] != index or checkpoint["check_vertex"] is not True or
                    checkpoint["model"] != canonical or checkpoint["generator"] != source["generator"]):
                raise ValueError(f"{stratum} checkpoint differs at {index}")
            for arm in CHECK:
                row = dict(source)
                row["arm_key"] = f"{stratum}-v{index:04d}-{arm}"
                row["base_rule"] = arm
                row["control_reference"] = (
                    f"{stratum}-v0000-low_x" if arm == "graph_transport" else
                    source["arm_key"] if arm == "u2_transport" else None)
                if arm in ("u2_native", "u2_transport"):
                    row["output_model"] = u2_model
                    row["output_generator"] = u2_generator
                if arm == "graph_transport":
                    row["checkpoint_sha256"] = sha(checkpoint_path)
                    row["checkpoint_path"] = str(checkpoint_path.relative_to(STUDY))
                rows.append(row)
        counts[stratum] = {"vertices": vertex_count, "check_vertices": check_count,
                           "main_arms": 3 * vertex_count, "check_arms": 4 * check_count,
                           "arms": 3 * vertex_count + 4 * check_count,
                           "discovery_targets_per_arm": config["discovery"],
                           "target_probes": (3 * vertex_count + 4 * check_count) * config["discovery"]}
    if pos != len(main_rows) or len(rows) != 8206 or len({row["arm_key"] for row in rows}) != len(rows):
        raise ValueError("full discovery inventory differs")
    schedule = HERE / "discovery-arms.jsonl"
    payload = b"".join((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode() for row in rows)
    write_once(schedule, payload)
    manifest = {
        "schema": "ectd-graph-discovery-schedule/v1", "status": "candidate_unapproved",
        "mode": "four separate full-quota check arms at every fixed check vertex",
        "arm_order": [*MAIN, *CHECK], "stratum_order": ["P29", "P37"],
        "u2_transport_rule": "transport each vertex's native low_x base and same target by (x,y)->(4x,8y)",
        "graph_transport_rule": "transport source low_x base and source target along the archived path",
        "arms": len(rows), "target_probes": sum(value["target_probes"] for value in counts.values()),
        "counts": counts, "checkpoint_bindings": checkpoint_bindings,
        "main_arms_sha256": sha(main_path), "main_manifest_sha256": sha(old_manifest_path),
        "main_verification_sha256": sha(old_verify_path),
        "graph_manifest_sha256": sha(STUDY / "manifest-v2.json"),
        "planner_sha256": sha(Path(__file__)), "schedule_sha256": sha(schedule),
        "limits": "No root, target, relation, rank, solve, approval, or execution claim",
    }
    write_once(HERE / "manifest.json", (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps({"arms": manifest["arms"], "target_probes": manifest["target_probes"],
                      "schedule_sha256": manifest["schedule_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
