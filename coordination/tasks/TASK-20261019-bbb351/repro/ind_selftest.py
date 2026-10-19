"""Validator self-test: the validator's own counters against literal itertools enumeration (126 small cases)."""
import sys; sys.path.insert(0, '.')
import itertools, random
from math import comb
from indlib import *
rnd = random.Random(5)
bad = n = 0
for N in (211, 307, 401, 503, 1009, 2003, 4099):
    for B in (3, 5, 8, 13, 20, 31):
        for kind in range(3):
            if kind == 0: lab = rnd.sample(range(1, N), B)
            elif kind == 1: lab = list(range(1, B + 1))
            else:
                a = rnd.randrange(2, N); lab = [a * i % N for i in range(1, B + 1)]
            h = {}
            for t in itertools.combinations_with_replacement(lab, 3): h[sum(t) % N] = h.get(sum(t) % N, 0) + 1
            cov = len(h); tot = sum(h.values()); coll = sum(v * (v - 1) // 2 for v in h.values()); mx = max(h.values())
            c1, e = cov_prefix_scatter(lab, N); c2 = cov_fft_support(lab, N); hs = histogram_stats(lab, N)
            n += 1
            if not (c1 == cov == c2 and e == comb(B + 2, 3) == tot and hs == (tot, cov, coll, mx)): bad += 1
print('validator counters vs literal itertools: cases', n, 'mismatch', bad)
