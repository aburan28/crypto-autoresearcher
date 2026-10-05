#!/usr/bin/env python3
"""permute_masks.py IN.masks OUT.masks SEED [IN_SOLUTIONS OUT_SOLUTIONS]: relabel variables by a seeded random permutation (bit j -> bit pi(j)) in a system and optionally its zero set."""
import sys, random
src, dst, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
L = open(src).read().split('\n'); N, M = map(int, L[0].split())
pi = list(range(N)); random.Random(seed).shuffle(pi)
def perm(m):
    r = 0
    for j in range(N):
        if (m >> j) & 1: r |= 1 << pi[j]
    return r
out = ['%d %d' % (N, M)]
for e in range(M):
    t = list(map(int, L[1 + e].split()))
    out.append('%d %s' % (t[0], ' '.join(str(perm(m)) for m in t[1:])))
open(dst, 'w').write('\n'.join(out) + '\n')
if len(sys.argv) > 5:
    open(sys.argv[5], 'w').write(''.join('%d\n' % perm(int(x)) for x in open(sys.argv[4]).read().split()))
