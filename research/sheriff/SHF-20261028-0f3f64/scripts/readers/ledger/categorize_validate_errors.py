#!/usr/bin/env python3
"""Disjoint categorisation of tools/validate_ledger.py 'new error' lines from
saved outputs. Sheriff case SHF-20261028-0f3f64, B7 ledger reader.

Usage: categorize_validate_errors.py <out.json> label=path [label=path ...]
First matching category wins, so counts add up to the total.
"""
from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict

CATEGORIES = [
    ("prior_art", re.compile(r"prior_art|novelty|frontier_map")),
    ("citation_provenance", re.compile(r"verified_by|citation|provenance")),
    ("review_plan", re.compile(r"review_plan")),
    ("run_manifest_schema", re.compile(r"^experiments/[^/]+/runs/[^/]+/manifest")),
    ("specification_schema", re.compile(r"^experiments/[^/]+/specification\.yaml")),
    ("handoff_budget", re.compile(r"missing required field 'budget'")),
    ("decision_knowledge_promotion", re.compile(r"knowledge_promotion")),
    ("unknown_reference", re.compile(r"unknown")),
]


def categorize(lines):
    cats = OrderedDict((name, {"count": 0, "records": {}}) for name, _ in CATEGORIES)
    cats["other"] = {"count": 0, "records": {}}
    for line in lines:
        path = line.split(": ", 1)[0]
        name = next((n for n, rx in CATEGORIES if rx.search(line)), "other")
        cats[name]["count"] += 1
        cats[name]["records"][path] = cats[name]["records"].get(path, 0) + 1
    return cats


def main():
    out = {}
    for arg in sys.argv[2:]:
        label, path = arg.split("=", 1)
        text = open(path, encoding="utf-8").read().splitlines()
        lines = [l[4:] for l in text if l.startswith("  - ")]
        out[label] = {"source": path, "total_new_errors": len(lines),
                      "categories": categorize(lines)}
    json.dump(out, open(sys.argv[1], "w"), indent=2)
    names = [n for n, _ in CATEGORIES] + ["other"]
    print("category".ljust(30) + "".join(l[:16].rjust(17) for l in out))
    for n in names:
        print(n.ljust(30) + "".join(str(v["categories"][n]["count"]).rjust(17) for v in out.values()))
    print("TOTAL".ljust(30) + "".join(str(v["total_new_errors"]).rjust(17) for v in out.values()))


if __name__ == "__main__":
    main()
