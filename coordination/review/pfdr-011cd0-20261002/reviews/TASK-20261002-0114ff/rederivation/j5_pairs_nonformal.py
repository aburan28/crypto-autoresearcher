#!/usr/bin/env python3
"""J5 (c) addendum: pairs_nonformal (the counter H1a/H1b read) vs pairs_raw and the own row-derived pair count.
TASK-20261002-0114ff. Standard library only."""
import collections, gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
R = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e/experiments/EXP-PFDR-011cd0/runs/"
own = {}
with gzip.open(os.path.join(HERE, "outputs", "relcount.jsonl.gz"), "rt") as fh:
    for l in fh:
        r = json.loads(l); own[tuple(r["key"])] = r
c = collections.Counter()
for rd, mode in (("RUN-PFDR-011cd0-table", "table"), ("RUN-PFDR-011cd0-search", "search")):
    for l in gzip.open(R + rd + "/rows.jsonl.gz", "rt"):
        r = json.loads(l)
        k = (r["bits"], r["curve"], int(r["method"][4:]), r["arm"], r["mode"])
        kl = r["arm"] == "known_log"
        for cls, sc in ((("TT", "at_stop"), ("TB", "at_stop")) if mode == "table" else (("SS", "at_X_fix"),)):
            hb = r["harvest"][cls][sc]
            ok = hb["pairs_nonformal"] == hb["pairs_raw"] - hb["pairs_formal"]
            zero_formal = hb["pairs_formal"] == 0
            eq_own = hb["pairs_nonformal"] == own[k][cls]["pairs"]
            c[f"{mode}|{cls}|{'known_log' if kl else 'generic'}|nonformal=raw-formal:{ok}|formal==0:{zero_formal}|nonformal==own_pairs:{eq_own}"] += 1
json.dump(dict(sorted(c.items())), open(sys.argv[1], "w"), indent=1)
print(json.dumps(dict(sorted(c.items())), indent=1))
