"""Exact check of the stark v1 doc formula: spot_check_queries(n, bits) is
'the least q with (1 - 1/n)^q <= 2^-bits'.  Ports the Rust f64 expression
ceil(bits / -log2(1 - 1/n)) and compares it with the exact integer minimum.
Limitation: Python's math.log2 stands in for Rust's f64::log2 (both libm)."""
import json, math, sys

def rust_q(n, bits):
    per = -math.log2(1.0 - 1.0 / n)
    return math.ceil(bits / per)

def ok(n, q, bits):  # (n-1)^q * 2^bits <= n^q, exactly
    return (n - 1) ** q * (1 << bits) <= n ** q

rows, bad = [], []
for e in range(1, 11):
    n = 1 << e
    for bits in list(range(1, 33)) + [40, 48, 64, 80, 96, 128]:
        q = rust_q(n, bits)
        holds = ok(n, q, bits)
        minimal = q == 0 or not ok(n, q - 1, bits)
        rows.append({"n": n, "bits": bits, "q": q, "bound_holds": holds, "minimal": minimal})
        if not (holds and minimal):
            bad.append(rows[-1])
print(json.dumps({"cells": len(rows), "violations": bad,
                  "examples": [r for r in rows if (r["n"], r["bits"]) in {(8, 64), (8, 4), (32, 8), (2, 5)}]}, indent=1))
