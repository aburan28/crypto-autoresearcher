#!/usr/bin/env python3
"""Transcription checker for COST-SEMBIN-e9960c.yaml.

Extends the approach of experiments/EXP-SEMBIN-f4a17b/code/verify_record_transcription.py:
every mapped figure in the YAML record is re-read from the record file and compared
against the value re-read from the named JSON artifact, by an independent walk of both
files (this script shares no in-memory state with generate_cost_record.py). Numeric
figures must agree to 1e-9; non-numeric figures must be equal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

import yaml

TOKEN = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def yaml_get(obj, dotted):
    """Resolve 'a.b.c[2]' against the YAML, allowing keys that themselves contain dots
    or slashes by trying progressively longer prefixes."""
    parts = dotted.split(".")
    i = 0
    cur = obj
    while i < len(parts):
        matched = False
        for j in range(len(parts), i, -1):
            key = ".".join(parts[i:j])
            idx = None
            m = re.match(r"^(.*)\[(\d+)\]$", key)
            if m:
                key, idx = m.group(1), int(m.group(2))
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
                if idx is not None:
                    cur = cur[idx]
                i = j
                matched = True
                break
        if not matched:
            raise KeyError(dotted)
    return cur


def json_get(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--record-id", default="COST-SEMBIN-e9960c")
    args = ap.parse_args()
    rd = args.run_dir
    rec = yaml.safe_load(open(os.path.join(rd, f"{args.record_id}.yaml")))["concrete_cost"]
    figmap = json.load(open(os.path.join(rd, f"{args.record_id}.figure-map.json")))
    cache = {}
    failures, checked = [], 0
    for ypath, src in figmap.items():
        if src["file"] not in cache:
            cache[src["file"]] = json.load(open(os.path.join(rd, src["file"])))
        try:
            yv = yaml_get(rec, ypath)
        except KeyError:
            failures.append({"yaml_path": ypath, "error": "missing in record"})
            continue
        jv = json_get(cache[src["file"]], src["path"])
        checked += 1
        if isinstance(yv, (int, float)) and not isinstance(yv, bool) and isinstance(jv, (int, float)) and not isinstance(jv, bool):
            ok = abs(float(yv) - float(jv)) <= 1e-9
        else:
            ok = (yv == jv)
        if not ok:
            failures.append({"yaml_path": ypath, "record": yv, "artifact": jv, "source": src})
    report = {"record": f"{args.record_id}.yaml", "figures_checked": checked, "failures": failures,
              "passed": not failures, "tolerance_numeric": 1e-9,
              "method": "independent re-read of the YAML record and of each named JSON artifact; no shared state with the generator"}
    with open(os.path.join(rd, f"{args.record_id}.verification.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "failures"}), f"failures={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
