#!/usr/bin/env python3
"""Supplementary (NOT part of the assigned quantity): 40 random non-singular
curves and random x_R per prime, same (m,d,s)=(2,2,3) construction, to see
whether the blind (5,4) is forced by the construction or is a property of the
12 declared instances.  My own RNG, seed recorded."""
import sys, random, collections
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5")
from v1_blind_rederive import ell, S3_in_B, profile

RNG = random.Random(902642)
for p in (4099, 65537):
    tally = collections.Counter()
    for _ in range(40):
        while True:
            a = RNG.randrange(1, p); b = RNG.randrange(1, p)
            if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p:
                break
        xR = RNG.randrange(p)
        St = S3_in_B(ell(0, p), ell(1, p), xR, a, b, p)
        prof, d_ff = profile(St, p)
        tally[(d_ff, prof[d_ff]["fall_dim"],
               tuple((prof[D]["full_rank"], prof[D]["top_rank"]) for D in (4, 5, 6)))] += 1
    print("p =", p, "rng_seed=902642, 40 random curves+targets:")
    for k, v in tally.items():
        print("   (d_ff, fall_dim) =", k[0], k[1], " profile D4,D5,D6 =", k[2], " count =", v)
