#!/usr/bin/env python3
"""Descriptive follow-up on existing raw rows; not part of the frozen test."""
import json
import statistics
import sys
from analyze import read_rows, spearman

if len(sys.argv) != 3:
    sys.exit("usage: posthoc.py pristine.csv instrumented.csv")
pristine, instrumented = (read_rows(p) for p in sys.argv[1:])
lookup = {(r["round"], r["key"]): r for r in instrumented}
count = [lookup[(r["round"], r["key"])]["loop2_iterations"] for r in pristine]
pristine_ns = [r["sign_ns"] for r in pristine]
paired_instrumented_ns = [lookup[(r["round"], r["key"])]["sign_ns"] for r in pristine]
print(json.dumps({
    "interpretation": "post-hoc descriptive only; no significance claim",
    "loop_count_vs_pristine_time_spearman": spearman(count, pristine_ns),
    "pristine_vs_instrumented_time_spearman": spearman(
        pristine_ns, paired_instrumented_ns),
    "instrumented_sign_median_ms": statistics.median(
        ns / 1e6 for ns in paired_instrumented_ns),
}, indent=2, sort_keys=True))
