#!/usr/bin/env python3
"""Toy ECDLP instance generator and baby-step giant-step solver.

The trial driver of the runbook conformance example. One call is one trial:
it derives the instance from the arguments alone, solves it, counts group
operations, and writes `raw-result.json` and `manifest.yaml` into --run-dir.

    solve.py --trial-id ID --mode search  --seed S --curve curve.json --run-dir D
    solve.py --trial-id ID --mode known-k --k K    --curve curve.json --run-dir D
    solve.py --trial-id ID --mode off-curve        --curve curve.json --run-dir D

Instance derivation (the checker re-derives it with its own code):
  search:    k = 1 + int(sha256("toy-ecdlp-bsgs/k/<seed>")[:16], 16) mod (n - 1)
  known-k:   k = K (positive control: the solver must return K)
  off-curve: Q = (G.x, G.y + 1 mod p), not on the curve (negative control: the
             solver must refuse the instance rather than return a logarithm)

Counting: m = isqrt(n - 1) + 1. The baby-step table holds j*G for 0 <= j < m
(m entries, `baby_steps`); giant step i tests Q - i*(m*G) for i = 0, 1, ...
(`giant_steps` = i + 1 at the hit). `group_ops` = baby_steps + giant_steps;
computing m*G once is `setup_ops` and is reported separately. Every k < m*m is
k = i*m + j with i, j < m, so the search is complete
(formal/CryptoResearch/Runbook/BsgsCoverage.lean).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

O = None  # the point at infinity


def add(P, Q, p, a):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return O
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def neg(P, p):
    return O if P is O else (P[0], (-P[1]) % p)


def mul(k, P, p, a):
    """Double-and-add; returns (k*P, group operations used)."""
    result, addend, ops = O, P, 0
    while k:
        if k & 1:
            result = add(result, addend, p, a)
            ops += 1
        addend = add(addend, addend, p, a)
        ops += 1
        k >>= 1
    return result, ops


def on_curve(P, p, a, b):
    return P is O or (P[1] * P[1] - (P[0] ** 3 + a * P[0] + b)) % p == 0


def bsgs(G, Q, n, p, a):
    m = math.isqrt(n - 1) + 1
    table, R = {}, O
    for j in range(m):
        table.setdefault(R, j)
        R = add(R, G, p, a)
    mG, setup_ops = mul(m, G, p, a)
    step, gamma = neg(mG, p), Q
    for i in range(m):
        if gamma in table:
            return (i * m + table[gamma]) % n, {"m": m, "baby_steps": m, "giant_steps": i + 1,
                                                "setup_ops": setup_ops}
        gamma = add(gamma, step, p, a)
    return None, {"m": m, "baby_steps": m, "giant_steps": m, "setup_ops": setup_ops}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--mode", choices=("search", "known-k", "off-curve"), required=True)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--k", type=int)
    parser.add_argument("--curve", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    curve = json.loads(Path(args.curve).read_text())
    p, a, b, n, G = curve["p"], curve["a"], curve["b"], curve["n"], tuple(curve["G"])
    if args.mode == "search":
        k = 1 + int(hashlib.sha256(f"toy-ecdlp-bsgs/k/{args.seed}".encode()).hexdigest()[:16], 16) % (n - 1)
        Q, _ = mul(k, G, p, a)
    elif args.mode == "known-k":
        Q, _ = mul(args.k, G, p, a)
    else:
        Q = (G[0], (G[1] + 1) % p)
    started = time.perf_counter()
    result = {"schema": "example.toy_ecdlp_bsgs.result.v1", "trial_id": args.trial_id,
              "mode": args.mode, "seed": args.seed, "k_input": args.k,
              "curve": {"p": p, "a": a, "b": b, "n": n, "G": list(G)}, "Q": list(Q)}
    if not on_curve(Q, p, a, b):
        result.update(status="rejected_input", k_found=None, verified=False, m=None,
                      baby_steps=0, giant_steps=0, group_ops=0, setup_ops=0)
    else:
        k_found, counts = bsgs(G, Q, n, p, a)
        verified = k_found is not None and mul(k_found, G, p, a)[0] == Q
        result.update(status="solved" if verified else "not_found", k_found=k_found, verified=verified,
                      **counts, group_ops=counts["baby_steps"] + counts["giant_steps"])
    result["elapsed_ms"] = round((time.perf_counter() - started) * 1000)
    out = Path(args.run_dir)
    (out / "raw-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out / "manifest.yaml").write_text(f"trial_id: {args.trial_id}\nstatus: {result['status']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
