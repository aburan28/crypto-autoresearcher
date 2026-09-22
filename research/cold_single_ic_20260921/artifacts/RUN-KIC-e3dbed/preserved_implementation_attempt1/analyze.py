#!/usr/bin/env python3
"""Frozen deterministic analysis stub; refuses before admitted scientific receipts exist."""
import json, random, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    rows=[json.loads(x) for x in (ROOT/"processes.jsonl").read_text().splitlines() if x]
    held=[r for r in rows if r.get("phase")=="heldout"]
    if len(held)!=48: raise SystemExit("REFUSED: requires exactly 48 heldout receipts")
    # Selection and pairing are intentionally performed only after admission.
    raise SystemExit("REFUSED: analysis requires committed measurement admission and complete valid receipt schema")
if __name__=="__main__": main()
