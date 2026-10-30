#!/usr/bin/env python3
"""J1 comparison of a replayed run directory against the recorded one (TASK-20261029-958053).

usage: compare_outputs.py <recorded_run_dir> <replay_run_dir> <trial_plan.json> <trial_id> [--out x.json]

1. File sets: the recorded directory, the replay directory, the plan's declared artifacts, and the
   supervisor-only names (written by the supervisor, never by run.py, so not reproducible by a replay).
2. Every file present on both sides is compared byte for byte (sha256).
3. Where bytes differ and the file is JSON or YAML, every leaf is compared: key sets, list lengths and
   types exactly; non-float leaves exactly; float leaves first exactly, then by ULP distance and by the
   DEC-20261029-5554ee tolerance (math.isclose rel_tol=1e-9, abs_tol=1e-12) -> exact |
   matched_within_tolerance | beyond. Text files that differ get a line diff.
4. manifest.yaml leaves are additionally tagged provenance (execution-record fields that differ by
   construction between any two executions) or unexpected.
Own code; shares nothing with run.py or check.py.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import math
import os
import struct
import sys

SUPERVISOR_ONLY = {"command.txt", "environment.json", "launch.json", "execution-receipt.json"}
CAPTURED_STREAMS = {"stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log"}
PROVENANCE_PREFIXES = (
    "/run/timing/", "/run/resources/", "/run/code/commit", "/run/code/dirty", "/run/code/command",
    "/run/code/working_directory", "/run/environment/host", "/run/environment/operating_system",
    "/run/environment/python_version", "/run/environment/gcc_version", "/run/environment/processor_count",
    "/run/recorded_at",
)


def sha(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ordered(x: float) -> int:
    i = struct.unpack("<q", struct.pack("<d", x))[0]
    return i if i >= 0 else -(i & 0x7FFFFFFFFFFFFFFF)


def ulps(a: float, b: float) -> int:
    return abs(ordered(a) - ordered(b))


def kind(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    return type(v).__name__


def walk(a, b, ptr: str, out: list, counts: dict) -> None:
    ka, kb = kind(a), kind(b)
    if ka != kb:
        out.append({"pointer": ptr, "class": "non_float_type", "recorded": repr(a)[:80], "replay": repr(b)[:80]})
        return
    if ka == "dict":
        if set(a) != set(b):
            out.append({"pointer": ptr, "class": "non_float_keyset",
                        "only_recorded": sorted(set(a) - set(b)), "only_replay": sorted(set(b) - set(a))})
        for k in sorted(set(a) & set(b)):
            walk(a[k], b[k], f"{ptr}/{k}", out, counts)
        return
    if ka == "list":
        if len(a) != len(b):
            out.append({"pointer": ptr, "class": "non_float_list_length", "recorded": len(a), "replay": len(b)})
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{ptr}/{i}", out, counts)
        return
    counts["leaves"] += 1
    if ka == "float":
        counts["float_leaves"] += 1
        if a == b or (math.isnan(a) and math.isnan(b)):
            return
        u = ulps(a, b)
        rel = abs(a - b) / max(abs(a), abs(b))
        tol = math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
        out.append({"pointer": ptr, "class": "float_matched_within_tolerance" if tol else "float_beyond_tolerance",
                    "recorded": a, "replay": b, "abs": abs(a - b), "rel": rel, "ulps": u})
        return
    if a != b:
        out.append({"pointer": ptr, "class": f"non_float_{ka}", "recorded": a, "replay": b})


def load(path: str):
    if path.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    if path.endswith((".yaml", ".yml")):
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    return None


def main(argv: list[str]) -> int:
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        out_path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    rec_dir, rep_dir, plan_path, trial_id = argv
    with open(plan_path) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == trial_id)
    declared = set(trial["artifacts"]) | {"raw-result.json"}
    rec_files = set(os.listdir(rec_dir))
    rep_files = set(os.listdir(rep_dir))
    report = {
        "recorded_dir": rec_dir, "replay_dir": rep_dir, "trial_id": trial_id, "run_id": trial["run_id"],
        "file_sets": {
            "declared_artifacts_plus_raw_result": sorted(declared),
            "recorded": sorted(rec_files), "replay": sorted(rep_files),
            "declared_missing_in_replay": sorted(declared - rep_files),
            "declared_missing_in_recorded": sorted(declared - rec_files),
            "replay_only": sorted(rep_files - rec_files),
            "recorded_only": sorted(rec_files - rep_files),
            "recorded_only_explained_supervisor_written": sorted((rec_files - rep_files) & SUPERVISOR_ONLY),
            "recorded_only_unexplained": sorted((rec_files - rep_files) - SUPERVISOR_ONLY),
        },
        "files": [],
    }
    fatal = []
    for name in sorted(rec_files & rep_files):
        a, b = os.path.join(rec_dir, name), os.path.join(rep_dir, name)
        ra, rb = sha(a), sha(b)
        ent = {"file": name, "recorded_sha256": ra, "replay_sha256": rb, "bytes_equal": ra == rb,
               "role": ("declared_artifact" if name in declared else
                        "captured_stream" if name in CAPTURED_STREAMS else "other")}
        if ra != rb:
            da, db = load(a), load(b)
            if da is not None:
                diffs, counts = [], {"leaves": 0, "float_leaves": 0}
                walk(da, db, "", diffs, counts)
                if name == "manifest.yaml":
                    for d in diffs:
                        d["manifest_tag"] = ("provenance" if any(d["pointer"].startswith(p) for p in PROVENANCE_PREFIXES)
                                             else "unexpected")
                ent["leaf_counts"] = counts
                ent["differing_leaves"] = len(diffs)
                by = {}
                for d in diffs:
                    by[d["class"]] = by.get(d["class"], 0) + 1
                ent["differing_by_class"] = by
                ent["diffs"] = diffs if len(diffs) <= 40 else diffs[:40]
                ent["diffs_truncated"] = len(diffs) > 40
                if diffs:
                    fl = [d for d in diffs if d["class"].startswith("float_")]
                    if fl:
                        ent["float_max_rel"] = max(d["rel"] for d in fl)
                        ent["float_max_abs"] = max(d["abs"] for d in fl)
                        ent["float_max_ulps"] = max(d["ulps"] for d in fl)
                for d in diffs:
                    if name == "manifest.yaml" and d.get("manifest_tag") == "provenance":
                        continue
                    if not d["class"].startswith("float_matched"):
                        fatal.append(f"{name}{d['pointer']}: {d['class']}")
            else:
                with open(a, errors="replace") as fa, open(b, errors="replace") as fb:
                    ent["line_diff"] = list(difflib.unified_diff(fa.read().splitlines(), fb.read().splitlines(),
                                                                 "recorded", "replay", lineterm="", n=0))[:40]
                ent["text_differs"] = True
                if ent["role"] != "captured_stream":
                    fatal.append(f"{name}: text differs")
                else:
                    fatal.append(f"{name}: captured stream differs")
        report["files"].append(ent)
    report["non_provenance_differences"] = fatal
    report["measurement_artifacts_bytes_equal"] = all(
        e["bytes_equal"] for e in report["files"] if e["role"] == "declared_artifact" and e["file"] != "manifest.yaml")
    report["captured_streams_bytes_equal"] = all(
        e["bytes_equal"] for e in report["files"] if e["role"] == "captured_stream")
    s = json.dumps(report, indent=1, sort_keys=False, default=str)
    if out_path:
        with open(out_path, "w") as f:
            f.write(s + "\n")
    print(s[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
