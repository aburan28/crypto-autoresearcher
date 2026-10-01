#!/usr/bin/env python3
"""Independently re-verify gf2_131_mul_bench.c against the pure-Python field.

The benchmark's --selftest prints  a b c  (hex, 131-bit) per line; this script
recomputes a*b in F_2[z]/(z^131+z^13+z^2+z+1) with the same GF class the
measurement instrument uses and refuses any mismatch.  The timing number is
only usable if the thing being timed is the right operation.

    ./gf2_131_mul_bench --selftest | python3 check_mul_bench.py
"""
import sys
from solve_cost_ladder import GF

F = GF(131)
n = 0
for line in sys.stdin:
    parts = line.split()
    if len(parts) != 3:
        continue
    a, b, c = (int(p, 16) for p in parts)
    assert a < F.hi and b < F.hi and c < F.hi, "operand out of field"
    got = F.mul(a, b)
    assert got == c, f"MISMATCH a={a:x} b={b:x} C={c:x} python={got:x}"
    n += 1
assert n > 0, "no vectors read"
print(f"OK: {n} vectors, C benchmark agrees with the Python F_2^131 used by the instrument")
