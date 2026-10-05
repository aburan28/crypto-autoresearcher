#!/usr/bin/env python3
"""masks (N M, lines 't m1..mt') -> msolve-format .ms text in the style of the twelve files (x1_i / x2_j names, field lines appended)."""
import sys
src, dst = sys.argv[1], sys.argv[2]
L = open(src).read().split('\n')
N, M = map(int, L[0].split())
k = N // 2
names = ['x1_%d' % i for i in range(k)] + ['x2_%d' % i for i in range(N - k)]
def mstr(m):
    if m == 0: return '1'
    return '*'.join(names[j] for j in range(N) if (m >> j) & 1)
lines = []
for e in range(M):
    t = list(map(int, L[1 + e].split()))[1:]
    lines.append('+'.join(mstr(m) for m in t) + ',')
for j in range(N):
    lines.append('%s^2+%s%s' % (names[j], names[j], ',' if j < N - 1 else ''))
open(dst, 'w').write(','.join(names) + '\n2\n' + '\n'.join(lines) + '\n')
