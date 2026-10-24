"""Independently check every proposed graph discovery arm and control binding."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(ROOT))
from harness.toycurve import EllipticCurve  # noqa: E402

FIXED = {
    "P29": {"vertices": 2049, "stride": 8, "quota": 8192, "B": 256,
            "walk": "walk-p29-2048-attempt2.jsonl",
            "checkpoints": "path_transport/controls/p29-twoedge-attempt1"},
    "P37": {"vertices": 257, "stride": 4, "quota": 2048, "B": 1600,
            "walk": "walk-p37-256.jsonl",
            "checkpoints": "path_transport/controls/p37-twoedge-attempt1"},
}
MAIN = ("low_x", "mid_x", "random_x")
CHECK = ("power_x", "graph_transport", "u2_native", "u2_transport")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    schedule_path = HERE / "discovery-arms.jsonl"
    manifest = json.loads((HERE / "manifest.json").read_text())
    main_path = STUDY / "discovery_capacity_20261022/main-arms.jsonl"
    main_manifest_path = STUDY / "discovery_capacity_20261022/main-arms-manifest.json"
    main_verification_path = STUDY / "discovery_capacity_20261022/main-arms-verification.json"
    main_manifest = json.loads(main_manifest_path.read_text())
    main_verification = json.loads(main_verification_path.read_text())
    original = [json.loads(line) for line in main_path.read_text().splitlines()]
    rows = [json.loads(line) for line in schedule_path.read_text().splitlines()]
    check(manifest["schema"] == "ectd-graph-discovery-schedule/v1" and
          manifest["status"] == "candidate_unapproved", "schedule status")
    check(manifest["planner_sha256"] == sha(HERE / "plan.py") and
          manifest["main_arms_sha256"] == sha(main_path) and
          manifest["main_manifest_sha256"] == sha(main_manifest_path) and
          manifest["main_verification_sha256"] == sha(main_verification_path) and
          manifest["schedule_sha256"] == sha(schedule_path) and
          manifest["graph_manifest_sha256"] == sha(STUDY / "manifest-v2.json"),
          "source or schedule digest differs")
    check(main_manifest["main_arms_sha256"] == sha(main_path) and
          main_verification["status"] == "pass" and
          main_verification["main_arms_sha256"] == sha(main_path),
          "underlying main-arm verification differs")
    check(len(original) == 6918 and len(rows) == 8206, "row extent differs")
    pos = old_pos = group_checks = checkpoint_checks = 0
    counts = {}
    for stratum, setting in FIXED.items():
        walk_path = STUDY / setting["walk"]
        with walk_path.open() as stream:
            header = json.loads(next(stream))
            edges = [json.loads(line) for line in stream]
        check(header["stratum"] == stratum and header["requested_edges"] + 1 == setting["vertices"],
              "walk extent differs")
        check(manifest["graph_manifest_sha256"] == sha(STUDY / "manifest-v2.json"), "graph manifest")
        check(manifest["checkpoint_bindings"][stratum]["manifest_sha256"] ==
              sha(STUDY / setting["checkpoints"] / "manifest.json"), "checkpoint manifest digest")
        terminal = STUDY / setting["checkpoints"] / f"edge-{setting['vertices'] - 1:04d}.json"
        check(manifest["checkpoint_bindings"][stratum]["terminal_sha256"] == sha(terminal),
              "terminal checkpoint digest")
        checkpoint_manifest = json.loads((STUDY / setting["checkpoints"] / "manifest.json").read_text())
        check(checkpoint_manifest["graph_sha256"] == sha(walk_path) and
              checkpoint_manifest["check_stride"] == setting["stride"], "checkpoint walk/stride")
        xmap, ymap = header["source_isomorphism"].strip()[1:-1].split(",")
        def scale(expr: str, var: str) -> int:
            expr = expr.strip()
            if expr == var:
                return 1
            if expr == "-" + var:
                return header["p"] - 1
            if expr.startswith(var + "/"):
                return pow(int(expr.split("/", 1)[1]), -1, header["p"])
            return int(expr.split("*", 1)[0]) % header["p"]
        sx, sy = scale(xmap, "x"), scale(ymap, "y")
        check((sy * sy - sx * sx * sx) % header["p"] == 0, "source isomorphism scaling")
        generator = (header["source_generator"][0] * sx % header["p"],
                     header["source_generator"][1] * sy % header["p"])
        models = [(header["canonical_source"], generator)]
        previous = models[0][0]
        for edge in edges:
            if edge["kind"] == "complete":
                check(edge["edges"] == setting["vertices"] - 1, "graph completion")
                continue
            check(edge["kind"] == "edge" and edge["source"] == previous and
                  edge["index"] == len(models), "edge continuity")
            previous = edge["canonical_codomain"]
            models.append((previous, tuple(edge["image_generator"])))
        check(len(models) == setting["vertices"], "model count")
        start = pos
        for index, (model, generator) in enumerate(models):
            curve = EllipticCurve(header["p"], model["a"], model["b"])
            check(curve.is_on_curve(generator) and curve.mul(header["r"], generator) is None,
                  f"generator equation/order at {stratum} vertex {index}")
            group_checks += 1
            for arm in MAIN:
                row, baseline = rows[pos], original[old_pos]
                pos += 1
                old_pos += 1
                check(row == baseline and row["arm_key"] == f"{stratum}-v{index:04d}-{arm}" and
                      row["model"] == model and tuple(row["generator"]) == generator and
                      row["discovery_targets"] == setting["quota"] and
                      row["base_x_orbits"] == setting["B"], "main arm differs")
            if index % setting["stride"]:
                continue
            checkpoint_path = STUDY / setting["checkpoints"] / f"edge-{index:04d}.json"
            checkpoint = json.loads(checkpoint_path.read_text())
            check(checkpoint["index"] == index and checkpoint["check_vertex"] is True and
                  checkpoint["model"] == model and checkpoint["generator"] == list(generator) and
                  len(checkpoint["base"]) == 2 * setting["B"], "transport checkpoint identity")
            base_hash = hashlib.sha256(json.dumps(checkpoint["base"], separators=(",", ":")).encode()).hexdigest()
            check(checkpoint["base_sha256"] == base_hash, "transported base digest")
            checkpoint_checks += 1
            for arm in CHECK:
                row = rows[pos]
                pos += 1
                check(row["arm_key"] == f"{stratum}-v{index:04d}-{arm}" and
                      row["base_rule"] == arm and row["stratum"] == stratum and
                      row["path_index"] == index and row["model"] == model and
                      tuple(row["generator"]) == generator and
                      row["discovery_targets"] == setting["quota"] and
                      row["base_x_orbits"] == setting["B"], "check arm identity/quota")
                expected_ref = (f"{stratum}-v0000-low_x" if arm == "graph_transport" else
                                f"{stratum}-v{index:04d}-low_x" if arm == "u2_transport" else None)
                check(row["control_reference"] == expected_ref, "control reference")
                if arm.startswith("u2_"):
                    check(row["output_model"] == {"a": 16 * model["a"] % header["p"],
                                                  "b": 64 * model["b"] % header["p"], "j": model["j"]} and
                          row["output_generator"] == [4 * generator[0] % header["p"],
                                                      8 * generator[1] % header["p"]], "u2 map")
                else:
                    check("output_model" not in row and "output_generator" not in row, "unexpected output model")
                if arm == "graph_transport":
                    check(row["checkpoint_path"] == str(checkpoint_path.relative_to(STUDY)) and
                          row["checkpoint_sha256"] == sha(checkpoint_path), "checkpoint arm digest")
                else:
                    check("checkpoint_path" not in row and "checkpoint_sha256" not in row,
                          "unexpected checkpoint binding")
        arm_count = pos - start
        expected_check = (setting["vertices"] - 1) // setting["stride"] + 1
        check(arm_count == 3 * setting["vertices"] + 4 * expected_check, "stratum arm count")
        counts[stratum] = {"vertices": setting["vertices"], "check_vertices": expected_check,
                           "main_arms": 3 * setting["vertices"], "check_arms": 4 * expected_check,
                           "arms": arm_count, "discovery_targets_per_arm": setting["quota"],
                           "target_probes": arm_count * setting["quota"]}
    check(pos == len(rows) and old_pos == len(original), "unconsumed rows")
    check(counts == manifest["counts"] and sum(v["target_probes"] for v in counts.values()) == 60889088,
          "count or probe total")
    check(len({row["arm_key"] for row in rows}) == len(rows), "duplicate arm key")
    receipt = {"schema": "ectd-graph-discovery-schedule-verification/v1", "status": "pass",
               "schedule_sha256": sha(schedule_path), "arms_checked": pos,
               "vertices_checked": group_checks, "checkpoint_bindings_checked": checkpoint_checks,
               "target_probes": 60889088, "counts": counts,
               "checks": ["main-arm byte-equivalent rows", "archived walk continuity",
                          "independent group-order point arithmetic", "fixed check indices and quotas",
                          "source and vertex oracle references", "u2 model/generator formulas",
                          "checkpoint identity and digest bindings"],
               "limit": "Schedule identity only; no targets, relations, rank, solves, or approval"}
    path = HERE / "verification.json"
    encoded = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
    if path.exists() and path.read_bytes() != encoded:
        raise ValueError("verification receipt is write-once")
    if not path.exists():
        path.write_bytes(encoded)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
