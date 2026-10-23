#!/usr/bin/env python3
"""EXP-ECDLP-8c41d7 AMD-03 launcher: the m = 4, L = 4 cell with a prime msolve 0.6.5 can read.

msolve 0.6.5 segfaults on systems over primes with exactly 17 bits (2^16 < p < 2^17; reproduced at
p = 65551, 66047 and 70039, m = 2, 3 and 4). The frozen prime rule ("smallest p > 2^(mL) with
p = 3 mod 4, 2^L | p+1") gives p = 65551 for (m, L) = (4, 4). This wrapper changes ONLY that choice, for
(4, 4): p = 262271 (19 bits, 16 | p+1; the same prime msolve solved at m = 3, L = 6). Everything else
(chain construction, targets, arms, instruments, controls) is block_order_m4.py / block_order_grid.py.
"""
import block_order_m4 as base

_orig = base.pkm.find_prime


def find_prime(m, L):
    return 262271 if (m, L) == (4, 4) else _orig(m, L)


base.pkm.find_prime = find_prime

if __name__ == "__main__":
    base.bog.main()
