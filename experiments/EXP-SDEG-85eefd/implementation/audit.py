"""C-8 accounting audit: independent recomputation of W from the operation log
of 10% of queries selected by SHA256, rejecting any receipt that zeroes
aborted triples, table construction or hash probes.

Selection: rank query_ids by SHA256('<ns>|audit|<query_id>') and take the
lowest ceil(10%) (the label is not fixed by the protocol; implementation.md).
Op-log entry: [tag, mul, inv, gcd_steps, probes]; W = mul + inv + gcd_steps + probes.
Protocol v3: W (decision cost), W_full and W_triple are each recomputed from
the log and compared with the receipt.
"""

from __future__ import annotations

import math

import labels


def select(query_ids, ns: str, fraction: float = 0.10) -> list:
    ranked = sorted(query_ids, key=lambda q: labels.h(labels.lab(ns, "audit", q)))
    return sorted(ranked[: math.ceil(fraction * len(ranked))])


def check_receipt(rec: dict) -> dict:
    """rec: backend result with op_log, W_query, n_triples, table_ops, n_queries_in_cell, W."""
    problems = []
    log = rec.get("op_log")
    if not log:
        return {"query_id": rec.get("query_id"), "backend": rec.get("backend"), "accepted": False,
                "problems": ["missing op log"]}
    W = sum(e[1] + e[2] + e[3] + e[4] for e in log)
    if W != rec["W_query"]:
        problems.append(f"W_query {rec['W_query']} != recomputed {W}")
    tri = [e for e in log if e[0].count(",") == 2]
    if len(tri) != rec["n_triples"]:
        problems.append(f"{len(tri)} triple entries, expected {rec['n_triples']}")
    zero = [e[0] for e in tri if e[1] + e[2] + e[3] + e[4] == 0]
    if zero:
        problems.append(f"{len(zero)} triples charged zero work (e.g. {zero[:3]})")
    if rec["backend"] == "B0":
        bad = [e[0] for e in tri if e[4] != 8]
        if bad:
            problems.append(f"{len(bad)} B0 triples without exactly 8 hash probes")
    if rec["backend"] == "B1":
        bad = [e[0] for e in tri if e[1] == 0]
        if bad:
            problems.append(f"{len(bad)} B1 triples with zero multiplications")
    t = rec.get("table_ops") or {}
    if t.get("W", 0) <= 0 or t.get("probes", 0) <= 0:
        problems.append("table construction or its insert probes charged zero")
    if rec["backend"] == "B1" and t.get("mul", 0) <= 0:
        problems.append("B1 table has no F_T multiplications")
    fb = rec.get("deck_construction_ops") or {}
    amort = (t.get("W", 0) + fb.get("W", 0)) / rec["n_queries_in_cell"]
    # protocol v3: primary W = work through the first hit triple in the
    # lexicographic order (full enumeration without a hit); W_full = all
    # triples; W_triple = W minus B1's per-query specialization at x(R).
    hits = sorted(tuple(h) for h in rec.get("hit_triples", []))
    first = ",".join(map(str, hits[0])) if hits else None
    W_dec, run = None, 0
    for e in log:
        run += e[1] + e[2] + e[3] + e[4]
        if first is not None and e[0] == first:
            W_dec = run
            break
    if first is not None and W_dec is None:
        problems.append(f"first hit triple {first} missing from op log")
        W_dec = W
    if first is None:
        W_dec = W
    fixed = sum(e[1] + e[2] + e[3] + e[4] for e in log if e[0] == "specialize_R")
    expected = {"W_full": W + amort, "W": W_dec + amort}
    if "W_fixed_xR" in rec:
        expected["W_fixed_xR"] = fixed
        expected["W_triple"] = W_dec + amort - fixed
    elif "W_full" not in rec:  # pre-v3 receipt shape: W was full enumeration
        expected = {"W": W + amort}
    for k, v in expected.items():
        if k not in rec or abs(v - rec[k]) > 1e-6 * max(1.0, v):
            problems.append(f"{k} {rec.get(k)} != recomputed {v}")
    return {"query_id": rec.get("query_id"), "backend": rec["backend"], "accepted": not problems,
            "problems": problems, "W_recomputed": W, "W_decision_recomputed": W_dec,
            "W_fixed_xR_recomputed": fixed}
