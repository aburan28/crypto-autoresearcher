"""J7(a): no emitted row of a generic (main-panel, non-known_log) curve is formal; no emitted row is the
zero relation; pairs_formal == 0 and rows_formal == 0 in every generic harvest block (at stop and,
for SS, at A_fix).  Streams every main-panel and Stage R harvest-rows file with a regex (no JSON
parse of the payload).  No randomness.  Output: attacks/out/12_formal_scan.json
"""
import glob, gzip, json, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import OUT, P, RUNS, canonical_rows, iter_jsonl, m_of

ARM = re.compile(r'"arm": "([a-z0-9_]+)"')
files = [os.path.join(RUNS, P + "census-m3", "harvest-rows.jsonl.gz"), os.path.join(RUNS, P + "census-m4", "harvest-rows.jsonl.gz")]
files += sorted(glob.glob(os.path.join(RUNS, P + "census-m4", "attempt-2", "jobs", "*", "harvest-rows.jsonl.gz")))
files += sorted(glob.glob(os.path.join(RUNS, P + "census-m5", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
files += sorted(glob.glob(os.path.join(RUNS, P + "stage-r", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
formal_true, zero_rows, rows_seen = Counter(), Counter(), Counter()
for f in files:
    with gzip.open(f, "rt") as fh:
        for line in fh:
            arm = ARM.search(line).group(1)
            rows_seen[arm] += 1
            if '"formal": true' in line:
                formal_true[arm] += 1
            if '"coeffs": [], "kcoef": 0, "rhs": 0' in line:
                zero_rows[arm] += 1
blk = Counter()
rows = canonical_rows("census-m3") + canonical_rows("census-m4") + canonical_rows("census-m5") + list(iter_jsonl(os.path.join(RUNS, P + "stage-r", "rows.jsonl.gz")))
for r in rows:
    if not r.get("harvest") or r.get("arm") == "known_log":
        continue
    h = r["harvest"]
    for c in ("TT", "TB", "SS"):
        st = h[c]["at_stop"]
        blk["pairs_formal_nonzero"] += st["pairs_formal"] != 0
        blk["rows_formal_nonzero"] += st["rows_formal"] != 0
    a = h["SS"]["at_A_fix"]
    blk["ss_at_A_fix_pairs_formal_nonzero"] += a["pairs_formal"] != 0
    blk["instances"] += 1
out = {"rows_seen_by_arm": dict(rows_seen), "formal_true_rows_by_arm": dict(formal_true),
       "zero_relation_rows_by_arm": dict(zero_rows), "generic_harvest_blocks": dict(blk)}
json.dump(out, open(os.path.join(OUT, "out", "12_formal_scan.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1))
