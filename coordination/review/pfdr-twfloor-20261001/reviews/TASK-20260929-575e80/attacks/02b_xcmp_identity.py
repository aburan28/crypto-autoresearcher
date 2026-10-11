"""02b -- check of the compared-encoding identity used in F4 b and DN D7 (no randomness):
X_cmp := table_entries + B + encodings_recorded equals 2*S_3 - degenerate (h = 2) and
2*S_3 - B^2 - degenerate (h = 3) on every row with a harvest block.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402

xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
c = Counter()
bad = []
for x in xs:
    if "enc_rec" not in x:
        continue
    X = x["table_entries"] + x["B"] + x["enc_rec"]
    want = 2 * x["S"] - x["degenerate"] - (x["B"] ** 2 if x["h"] == 3 else 0)
    ok = X == want and X <= 2 * x["S"]
    c[f"h{x['h']}:{ok}"] += 1
    if not ok:
        bad.append([x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"], X, want])
dump("02b_xcmp_identity.json", {"counts": dict(c), "failures": bad[:50]})
print(dict(c), len(bad))
