#!/usr/bin/env python3
"""Summarize measured Sage isogeny receipts; no inferred hardness claims."""
import argparse
import json
from collections import Counter
from pathlib import Path

def summarize(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    counts = Counter(r.get("kind") for r in rows)
    failed = [r for r in rows if r.get("homomorphism_verified") is False]
    return {"records": len(rows), "counts": dict(counts),
            "verification_failures": len(failed),
            "odd_edge_degrees": sorted(set(r["ell"] for r in rows if r.get("kind")=="odd_isogeny")),
            "conductor_gap_verified": False,
            "ecdlp_cost_separation_measured": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    args = p.parse_args()
    print(json.dumps(summarize(args.input), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
