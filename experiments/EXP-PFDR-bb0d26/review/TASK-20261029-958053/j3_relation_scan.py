#!/usr/bin/env python3
"""J3 follow-up probe: short relations among the seeded log-GAP base points of every r >= 2 census job.

usage: j3_relation_scan.py <toy-main-jobs.jsonl> <out.json> [--workers 4]

Motivation (observation, not a plan item): no ok record has duplicate_skips > 0, while the expected number of
nonzero relations d1 P1 + ... + dr Pr = O with |d_i| <= 2T (each such relation forces at least one repeated
label inside the half-box) summed over the ok r >= 2 jobs is about 4.8. A relation present in a job whose
record shows duplicate_skips == 0 would be a builder discrepancy; none present means the zero is chance.
Meet in the middle with this directory's own curve arithmetic (j3_recount.Curve); no producer code.
For every job where a relation is found, the half-box build of j3_recount.gap_set is rerun and its
duplicate/infinity skips are compared with the record.
"""
import json
import multiprocessing as mp
import os
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j3_recount as m  # noqa: E402


def scan(rec):
    E = m.Curve(rec["p"], rec["a"], rec["b_coef"])
    rng = m.stream("gap", rec["block"], rec["cell"], rec["c"])
    r, T = rec["r"], rec["gap_meta"]["T"]
    pts = [E.random_point(rng) for _ in range(r)]
    B = 2 * T
    mult = [{k: E.mul(k, P) if k else None for k in range(-B, B + 1)} for P in pts]
    rels = []
    if r == 2:
        left = {}
        for d1 in range(-B, B + 1):
            left.setdefault(mult[0][d1], []).append(d1)
        for d2 in range(-B, B + 1):
            for d1 in left.get(E.neg(mult[1][d2]), []):
                if (d1, d2) != (0, 0) and (d1 > 0 or (d1 == 0 and d2 > 0)):
                    rels.append([d1, d2])
    else:
        left = {}
        for d1 in range(-B, B + 1):
            for d2 in range(-B, B + 1):
                left.setdefault(E.add(mult[0][d1], mult[1][d2]), []).append((d1, d2))
        for d3 in range(-B, B + 1):
            for d1, d2 in left.get(E.neg(mult[2][d3]), []):
                d = (d1, d2, d3)
                nz = next((x for x in d if x), 0)
                if nz > 0:
                    rels.append(list(d))
    out = {"cell": rec["cell"], "c": rec["c"], "status": rec["status"], "relations": rels[:6],
           "relation_count": len(rels), "recorded_duplicate_skips": rec["gap_meta"]["duplicate_skips"],
           "recorded_infinity_skips": rec["gap_meta"]["infinity_skips"]}
    if rels:
        _, meta, st, _ = m.gap_set(E, r, rec["n"], m.stream("gap", rec["block"], rec["cell"], rec["c"]))
        out["own_duplicate_skips"], out["own_infinity_skips"], out["own_status"] = meta["duplicate_skips"], meta["infinity_skips"], st
    return out


def main(argv):
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 4
    recs = [json.loads(l) for l in open(argv[0]) if l.strip()]
    todo = [x for x in recs if x["r"] >= 2]
    expected = sum((((4 * x["gap_meta"]["T"] + 1) ** x["r"] - 1) // 2) / x["N"] for x in todo)
    t0 = time.time()
    with mp.Pool(workers) as pool:
        res = pool.map(scan, todo, chunksize=8)
    hits = [x for x in res if x["relation_count"]]
    discrepancies = [x for x in hits if x.get("own_duplicate_skips") != x["recorded_duplicate_skips"]
                     or x.get("own_infinity_skips") != x["recorded_infinity_skips"]]
    silent = [x for x in res if x["relation_count"] and x["recorded_duplicate_skips"] == 0 and x["recorded_infinity_skips"] == 0]
    out = {"jobs_scanned": len(res), "expected_relation_vectors_H_over_N": round(expected, 3),
           "jobs_with_relation": len(hits), "hits": hits,
           "jobs_with_relation_but_no_recorded_skip": [(x["cell"], x["c"]) for x in silent],
           "skip_discrepancies_own_vs_recorded": discrepancies,
           "wall_seconds": round(time.time() - t0, 1), "python": sys.version}
    with open(argv[1], "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "hits"}, indent=1))
    print("hits:", [(x["cell"], x["c"], x["relations"][:2], x["recorded_duplicate_skips"]) for x in hits])


if __name__ == "__main__":
    main(sys.argv[1:])
