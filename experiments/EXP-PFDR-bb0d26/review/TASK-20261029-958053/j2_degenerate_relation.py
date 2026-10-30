#!/usr/bin/env python3
"""J2 diagnostic: why the 4 degenerate jobs of b20-r3-n4096 exhausted their half-box.

usage: j2_degenerate_relation.py <toy-main-jobs.jsonl> <out.json>

For each degenerate record, regenerates the seeded base points P1, P2, P3 (same stream as j3_recount.py) and
searches d in [-2T, 2T]^3, first nonzero entry positive, for relations d1 P1 + d2 P2 + d3 P3 = O with this
directory's own curve arithmetic (j3_recount.Curve). A short relation makes x(c.P) = x(c'.P) whenever
c - c' or c + c' is a relation, so many half-box vectors repeat a label. Diagnostic only, no counting.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j3_recount as m  # noqa: E402


def main(jobs_path, out_path):
    recs = [json.loads(l) for l in open(jobs_path) if l.strip()]
    out = []
    for rec in recs:
        if rec["status"] != "degenerate":
            continue
        E = m.Curve(rec["p"], rec["a"], rec["b_coef"])
        rng = m.stream("gap", rec["block"], rec["cell"], rec["c"])
        pts = [E.random_point(rng) for _ in range(rec["r"])]
        T = rec["gap_meta"]["T"]
        B = 2 * T
        tabs = [{k: E.mul(k, P) for k in range(-B, B + 1)} for P in pts]
        rels = []
        for d in m.half_box(rec["r"], B):
            Q = None
            for t, di in zip(tabs, d):
                Q = E.add(Q, t[di])
            if Q is None:
                rels.append(list(d))
        out.append({"cell": rec["cell"], "c": rec["c"], "p": rec["p"], "N": rec["N"], "T": T,
                    "recorded_duplicate_skips": rec["gap_meta"]["duplicate_skips"],
                    "recorded_infinity_skips": rec["gap_meta"]["infinity_skips"],
                    "relations_in_box_2T": rels[:12], "relation_count": len(rels),
                    "shortest_relation_maxnorm": min((max(abs(x) for x in d) for d in rels), default=None)})
    with open(out_path, "w") as f:
        json.dump({"python": sys.version, "jobs": out}, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
