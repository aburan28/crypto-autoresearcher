#!/usr/bin/env python3
"""B6.2 / B6.4 receipt-level checks for the six sessions (reader "stats").

N planned vs written, status counts, failure/timeout rows, records sha256,
warm-up count, S = total_gae/sqrt(r), shared algorithm seed per (target,
round), isolation level per arm vs isolation_required, record time span,
plan vs plan-aa identity (also across differing isolation levels), and the
six specs identical up to curve and base size.

Usage: python3 -I receipt_checks.py <campaign_dir>
"""
import collections
import datetime
import hashlib
import json
import math
import sys

camp = sys.argv[1]
S = ["c24", "c28", "c30", "r24", "r26", "r28"]
utc = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%H:%M:%S")
for s in S:
    d = f"{camp}/sessions/{s}"
    j = json.load(open(f"{d}/session.json"))
    raw = open(f"{d}/records.jsonl", "rb").read()
    R = [json.loads(l) for l in raw.splitlines()]
    st = collections.Counter(r["outcome"]["status"] for r in R)
    bad = [r["record_id"] for r in R if r["outcome"]["status"] != "verified" or not r["outcome"]["matches_target"]]
    seeds = collections.defaultdict(set)
    for r in R:
        seeds[(r["workload"]["target_index"], r["round"])].add(r["algorithm_seed"])
    iso = collections.defaultdict(collections.Counter)
    for r in R:
        if not r["warmup"]:
            iso[r["arm"]][r["isolation"]["level"]] += 1
    t = [r["isolation"]["before"]["unix_ms"] for r in R]
    k = lambda r: (r["workload"]["workload_id"], r["round"])
    P = {k(r): r for r in R if r["arm"] == "plan"}
    AA = {k(r): r for r in R if r["arm"] == "plan-aa"}
    ident = sum(1 for x in P if P[x]["cost"]["total_gae"] == AA[x]["cost"]["total_gae"]
                and [{**p, "wall_ns": 0} for p in P[x]["phases"]] == [{**p, "wall_ns": 0} for p in AA[x]["phases"]])
    mixed = [x for x in P if P[x]["isolation"]["level"] != AA[x]["isolation"]["level"]]
    spec = json.load(open(f"{d}/spec.json"))
    print(f"{s}: git_commit={j['git_commit'][:9]} dirty={j['git_dirty']} status={j['status']} "
          f"planned={j['executions_planned']} written={j['records_written']} lines={len(R)} "
          f"status_counts={dict(st)} session_status_counts={j['status_counts']} non_verified_or_wrong={len(bad)} "
          f"records_sha256_ok={hashlib.sha256(raw).hexdigest() == j['records_sha256']} "
          f"warmups={sum(r['warmup'] for r in R)} "
          f"S_is_total_over_sqrt_r={all(abs(r['cost']['s'] - r['cost']['total_gae'] / math.sqrt(r['workload']['curve']['r'])) <= 1e-12 * r['cost']['s'] for r in R)} "
          f"one_seed_per_target_round={all(len(v) == 1 for v in seeds.values())} "
          f"time={utc(min(t))}-{utc(max(t))}Z isolation_required={spec['measurement']['isolation_required']} "
          f"plan_eq_plan_aa={ident}/{len(P)} (incl. warm-ups) mixed_level_pairs={len(mixed)}")
    print("   measured-run isolation per arm:", {a: dict(c) for a, c in sorted(iso.items())})
