#!/usr/bin/env python3
"""Seeded generators of small Boolean systems (frozenset-of-bitmask polynomials) for the W1/W3/PT tests.
Every system is a pure function of (family, N, M, params, seed) so any finding can be reproduced from its seed."""
import random, itertools

def popcount(x): return bin(x).count('1')

def rand_poly(rng, N, degs, dens, const_p=0.5, plant=None):
    """random polynomial: each monomial of each size in `degs` is present with probability dens[size]."""
    p = set()
    if rng.random() < const_p: p ^= {0}
    for d in degs:
        pr = dens[d]
        for c in itertools.combinations(range(N), d):
            if rng.random() < pr:
                p ^= {sum(1 << j for j in c)}
    return p

def system(family, N, M, seed, **kw):
    rng = random.Random(hash((family, N, M, seed)) & 0xffffffff if False else (seed * 1000003 + N * 101 + M * 7 + sum(map(ord, family))))
    polys = []
    if family == 'quad':           # random quadrics: dense-ish in quadratic part
        q = kw.get('q', 0.5)
        for _ in range(M):
            polys.append(frozenset(rand_poly(rng, N, (1, 2), {1: .5, 2: q})))
    elif family == 'sparsequad':   # sparse random quadrics
        q = kw.get('q', 0.15)
        for _ in range(M):
            polys.append(frozenset(rand_poly(rng, N, (1, 2), {1: .3, 2: q})))
    elif family == 'cubic':        # mix of cubics and quadrics
        c = kw.get('c', 0.05); q = kw.get('q', 0.3)
        for i in range(M):
            if i % 2 == 0:
                polys.append(frozenset(rand_poly(rng, N, (1, 2, 3), {1: .4, 2: q, 3: c})))
            else:
                polys.append(frozenset(rand_poly(rng, N, (1, 2), {1: .4, 2: q})))
    elif family == 'bilinear':     # window-like: two halves k=N/2, bilinear + linear + const
        k = N // 2; q = kw.get('q', 0.5)
        for _ in range(M):
            p = set()
            if rng.random() < .5: p ^= {0}
            for i in range(N):
                if rng.random() < .5: p ^= {1 << i}
            for i in range(k):
                for j in range(k, N):
                    if rng.random() < q: p ^= {(1 << i) | (1 << j)}
            polys.append(frozenset(p))
    elif family == 'toeplitz':     # window-like with Hankel structure per equation (shift pattern as in the files)
        k = N // 2
        for _ in range(M):
            p = set()
            if rng.random() < .5: p ^= {0}
            for i in range(N):
                if rng.random() < .5: p ^= {1 << i}
            base = [rng.random() < .5 for _ in range(2 * k)]
            for i in range(k):
                for j in range(k):
                    if base[i + j]: p ^= {(1 << i) | (1 << (k + j))}
            polys.append(frozenset(p))
    elif family == 'planted':      # quadrics all vanishing at a planted point
        a = rng.getrandbits(N); q = kw.get('q', 0.4)
        for _ in range(M):
            p = set(rand_poly(rng, N, (1, 2), {1: .4, 2: q}, const_p=0))
            v = 0
            for m in p:
                if (m & a) == m: v ^= 1
            if v: p ^= {0}
            polys.append(frozenset(p))
    else:
        raise ValueError(family)
    return [p for p in polys if len(p)]
