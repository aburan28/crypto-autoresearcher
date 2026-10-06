"""Dummy census job for the pre-pin exercise of run_jobs.py (EXP-PFDR-011cd0, card PINNED
BEFORE DATA: before pinning, run_jobs.py runs only dummy commands).

Writes rows.jsonl / harvest-rows.jsonl / staircase.jsonl / solve-certs.jsonl into --job-dir
for the given expected keys, with a planted behaviour:
  ok | invalid (one row invalid) | fi (one row failed_infrastructure) | missing (one key
  dropped) | crash (exit 2, no rows) | sleep (sleeps 3 s) | badcert (one certificate k+1) |
  g4 (one row with cert_fail 1)
No solver and no engine module; the certificates use a tiny prime-order curve found here by
naive point counting.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time


def tiny_curve():
    p = 1009
    for a in range(1, 50):
        for b in range(1, 50):
            if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                continue
            sq = {}
            for y in range(p):
                sq.setdefault(y * y % p, []).append(y)
            n = 1 + sum(len(sq.get((x ** 3 + a * x + b) % p, [])) for x in range(p))
            if n > 2 and all(n % q for q in range(2, int(n ** 0.5) + 1)):
                for x in range(p):
                    ys = sq.get((x ** 3 + a * x + b) % p)
                    if ys and ys[0] != 0:
                        return p, a, b, n, (x, ys[0])
    raise RuntimeError("no curve")


def add(p, a, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0:
        return None
    if P == Q:
        lam = (3 * P[0] * P[0] + a) * pow(2 * P[1], -1, p) % p
    else:
        lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x = (lam * lam - P[0] - Q[0]) % p
    return (x, (lam * (P[0] - x) - P[1]) % p)


def mul(p, a, k, P):
    R = None
    while k:
        if k & 1:
            R = add(p, a, R, P)
        P = add(p, a, P, P)
        k >>= 1
    return R


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--behaviour", default="ok")
    ap.add_argument("--keys", required=True)
    a = ap.parse_args()
    keys = json.loads(a.keys)
    beh = a.behaviour
    if beh == "crash":
        print("dummy crash", file=sys.stderr)
        return 2
    if beh == "sleep":
        time.sleep(3)
    if beh == "missing":
        keys = keys[1:]
    os.makedirs(a.job_dir, exist_ok=True)
    p, ca, cb, n, P = tiny_curve()
    rows, hrows, stairs, certs = [], [], [], []
    for i, (bits, c, m, arm, mode) in enumerate(keys):
        st, why = "completed_valid", None
        if beh == "invalid" and i == 0:
            st, why = "invalid", "dummy invalid"
        if beh == "fi" and i == 0:
            st, why = "failed_infrastructure", "dummy instance watchdog"
        cert_fail = 1 if (beh == "g4" and i == 0) else 0
        blk = {"at_stop": {"cert_fail": cert_fail, "cert_pass": 2 - cert_fail, "rows_emitted": 2}}
        solved = mode in ("census", "on")
        rows.append({"bits": bits, "curve": c, "m": m, "method": f"ic_m{m}", "panel": "main",
                     "arm": arm, "mode": mode, "status": st, "status_reason": why,
                     "k_found": solved, "k_verified": solved, "checks": {},
                     "harvest": {"TT": blk, "TB": blk, "SS": blk,
                                 "ss_store": {"identity_ok": True}}})
        hrows.append({"bits": bits, "curve": c, "m": m, "arm": arm, "mode": mode, "class": "TT"})
        stairs.append({"bits": bits, "curve": c, "m": m, "arm": arm, "mode": mode, "class": "TT"})
        if solved:
            k = (17 * (i + 1)) % n or 1
            Q = mul(p, ca, k, P)
            kk = (k + 1) % n if (beh == "badcert" and i == 0) else k
            certs.append({"key": {"bits": bits, "curve": c, "m": m, "arm": arm, "mode": mode},
                          "p": p, "a": ca, "b": cb, "N": n, "P": list(P), "Q": list(Q), "k": kk})
    for name, data in (("rows.jsonl", rows), ("harvest-rows.jsonl", hrows),
                       ("staircase.jsonl", stairs), ("solve-certs.jsonl", certs)):
        if name == "solve-certs.jsonl" and not certs:
            continue
        with open(os.path.join(a.job_dir, name), "w") as fh:
            for r in data:
                fh.write(json.dumps(r) + "\n")
    print(json.dumps({"rows": len(rows), "behaviour": beh}))
    return 1 if beh == "invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
