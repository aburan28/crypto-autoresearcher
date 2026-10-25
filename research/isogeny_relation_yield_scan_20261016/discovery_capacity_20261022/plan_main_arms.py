"""Enumerate the prospective three native-base discovery arms, without targets.

This is a planning artifact, not an EXP approval, seed commitment, or runner.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY / "preparation"))
from prepare_graph_input import SCHEDULE, source_generator
from verify_collector import Curve, certify_group

WALKS = {"P29": "walk-p29-2048-attempt2.jsonl", "P37": "walk-p37-256.jsonl"}
ARMS = ("low_x", "mid_x", "random_x")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


archive = json.loads((STUDY / "manifest-v2.json").read_text())
rows = []
inputs = {}
for stratum, filename in WALKS.items():
    path = STUDY / filename
    if archive["files"][filename]["sha256"] != digest(path):
        raise ValueError(f"{stratum} walk differs from archived graph")
    verification_name = f"verification-{stratum.lower()}-full.json"
    verification_path = STUDY / verification_name
    if archive["files"][verification_name]["sha256"] != digest(verification_path):
        raise ValueError(f"{stratum} independent graph receipt differs")
    verified = json.loads(verification_path.read_text())[0]
    with path.open() as stream:
        header = json.loads(next(stream))
        if header["stratum"] != stratum or header["requested_edges"] != verified["checked_edges"] or not verified["complete"]:
            raise ValueError(f"{stratum} graph is incomplete")
        models = [(header["canonical_source"], source_generator(header))]
        seen = {models[0][0]["j"]}
        previous = models[0][0]
        complete = None
        for item in map(json.loads, stream):
            if item["kind"] == "edge":
                index = len(models)
                model = item["canonical_codomain"]
                if item["index"] != index or item["source"] != previous or model["j"] in seen:
                    raise ValueError(f"{stratum} path index, continuity, or j uniqueness differs")
                seen.add(model["j"])
                models.append((model, tuple(item["image_generator"])))
                previous = model
            elif item["kind"] == "complete" and complete is None:
                complete = item
            else:
                raise ValueError(f"{stratum} unexpected graph record")
    if len(models) != header["requested_edges"] + 1 or complete is None or complete["distinct_vertices"] != len(seen):
        raise ValueError(f"{stratum} path extent differs")
    quota = SCHEDULE[stratum]["discovery"]
    stride = SCHEDULE[stratum]["power_stride"]
    for index, (model, generator) in enumerate(models):
        curve = Curve(header["p"], model["a"], model["b"], header["r"])
        certify_group(curve, generator)
        for arm in ARMS:
            rows.append({"arm_key": f"{stratum}-v{index:04d}-{arm}",
                         "stratum": stratum, "path_index": index,
                         "p": header["p"], "r": header["r"], "model": model,
                         "generator": list(generator), "base_rule": arm,
                         "base_x_orbits": SCHEDULE[stratum]["B"],
                         "discovery_targets": quota, "check_vertex": index % stride == 0})
    inputs[stratum] = {"walk": filename, "walk_sha256": digest(path),
                       "verification": verification_name,
                       "verification_sha256": digest(verification_path),
                       "vertices": len(models), "arms": len(models) * len(ARMS),
                       "target_probes": len(models) * len(ARMS) * quota,
                       "source_D_K": header["D_K"], "source_f_pi": header["f_pi"],
                       "source_f_E": header["f_E"]}

if len(rows) != 6918 or len({row["arm_key"] for row in rows}) != len(rows):
    raise ValueError("main discovery inventory differs from fixed draft")
payload = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
output = HERE / "main-arms.jsonl"
output.write_text(payload)
summary = {"schema": "ectd-discovery-main-arm-plan/v1", "status": "prospective_unapproved",
           "limits": "three main bases only; no check-arm quotas, seeds, target points, collector run, or outcome",
           "arms": len(rows), "target_probes": sum(row["discovery_targets"] for row in rows),
           "arm_order": list(ARMS), "stratum_order": list(WALKS),
           "graph_manifest_sha256": digest(STUDY / "manifest-v2.json"),
           "source_sha256": digest(Path(__file__)), "main_arms_sha256": digest(output),
           "inputs": inputs}
(HERE / "main-arms-manifest.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps({"arms": summary["arms"], "target_probes": summary["target_probes"],
                  "main_arms_sha256": summary["main_arms_sha256"]}, sort_keys=True))
