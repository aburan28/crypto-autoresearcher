#!/usr/bin/env python3
"""Compare a recorded jobs file with its audit replay as keyed records. Read-only.

Usage: jobs_compare.py RECORDED.jsonl REPLAY.jsonl
Keys records by (cell, block, c). Reports: line counts, duplicate keys, whether the key sets are
equal, whether the line order is equal, how many records differ in any field other than
`seconds` (the spec's determinism_excluded_fields are [seconds, jobs record order]), the status
tally, and the non-ok records.
"""
import collections
import json
import sys


def load(p):
    with open(p) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def key(r):
    return (r["cell"], r["block"], r["c"])


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    ka, kb = [key(r) for r in a], [key(r) for r in b]
    da = {k: r for k, r in zip(ka, a)}
    db = {k: r for k, r in zip(kb, b)}
    strip = lambda r: {k: v for k, v in r.items() if k != "seconds"}  # noqa: E731
    diff = [k for k in da if k in db and strip(da[k]) != strip(db[k])]
    same_pos = sum(x == y for x, y in zip(ka, kb))
    out = {
        "lines": [len(a), len(b)],
        "duplicate_keys": [len(ka) - len(set(ka)), len(kb) - len(set(kb))],
        "key_sets_equal": set(ka) == set(kb),
        "line_order_equal": ka == kb,
        "lines_at_same_position": same_pos,
        "records_differing_beyond_seconds": len(diff),
        "first_differing": diff[:5],
        "status_recorded": dict(collections.Counter(r["status"] for r in a)),
        "status_replay": dict(collections.Counter(r["status"] for r in b)),
        "non_ok_recorded": sorted([list(key(r)) + [r["status"]] for r in a if r["status"] != "ok"]),
        "non_ok_replay": sorted([list(key(r)) + [r["status"]] for r in b if r["status"] != "ok"]),
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
