#!/usr/bin/env python3
"""For each in-scope Lean file: which committed receipts (json/log/txt under
docs/reports and research/) contain its CURRENT sha256, and which receipts name
the file but record a different hash (stale binding)."""
import hashlib, json, os, re, sys, glob
ROOT = sys.argv[1]
scan = json.load(open(sys.argv[2]))["scan"]
cur = {rel: v["sha256"] for rel, v in scan.items()}
cands = []
for pat in ("docs/reports/2026-10-2*/**/*", "research/binstd_yield_ceiling_20261022/*", "research/endosweep_dk_exact_batch4_20261022/**/*"):
    cands += [p for p in glob.glob(os.path.join(ROOT, pat), recursive=True) if os.path.isfile(p) and p.endswith((".json", ".log", ".txt", ".md", ".jsonl", ".yaml", "SHA256SUMS"))]
cands = sorted(set(cands))
res = {}
for rel, h in cur.items():
    base = os.path.basename(rel)
    hits, named_other = [], []
    for p in cands:
        try:
            t = open(p, errors="ignore").read()
        except Exception:
            continue
        if h in t:
            hits.append(os.path.relpath(p, ROOT))
        elif base in t and p.endswith(".json"):
            # look for a sha256 adjacent to the filename
            try:
                d = json.load(open(p))
            except Exception:
                continue
            found = []
            def walk(x):
                if isinstance(x, dict):
                    keys = " ".join(map(str, x.keys())) + " " + " ".join(str(v) for v in x.values() if isinstance(v, str))
                    if base in keys:
                        for k, v in x.items():
                            if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v):
                                found.append((k, v))
                    for v in x.values(): walk(v)
                elif isinstance(x, list):
                    for v in x: walk(v)
            walk(d)
            if found:
                named_other.append((os.path.relpath(p, ROOT), sorted(set(found))))
    res[rel] = dict(current_sha256=h, receipts_with_current_hash=hits, receipts_naming_file_with_other_hash=named_other)
print(json.dumps(res, indent=1))
