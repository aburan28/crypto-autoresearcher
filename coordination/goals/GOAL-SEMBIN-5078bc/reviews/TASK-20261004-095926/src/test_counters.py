#!/usr/bin/env python3
"""W2: validate count_solutions (modes A, C; both role assignments) against brute force on small random systems and a hand-checkable system."""
import os, sys, random, subprocess, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from msparse import eval_B
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'count_solutions')
TMP = os.environ.get('TMPDIR', '/tmp')

def write_masks(path, N, polys):
    with open(path, 'w') as f:
        f.write('%d %d\n' % (N, len(polys)))
        for p in polys:
            ms = sorted(p); f.write('%d %s\n' % (len(ms), ' '.join(map(str, ms))))

def brute(N, polys):
    return sum(1 for a in range(1 << N) if all(eval_B(p, a) == 0 for p in polys))

def run(mode, path, e0, ne, dump=None, maxdump=0):
    cmd = [EXE, mode, path, str(e0), str(ne)] + ([dump, str(maxdump)] if dump else [])
    out = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='2'))
    if out.returncode != 0: return None, out.stderr
    tot = int(out.stdout.split('total=')[1].split()[0])
    return tot, out.stdout

def rand_bilinear(rng, k, M, dens=0.5):
    N = 2 * k; polys = []
    for _ in range(M):
        p = set()
        if rng.random() < .5: p ^= {0}
        for i in range(N):
            if rng.random() < dens: p ^= {1 << i}
        for i in range(k):
            for j in range(k, N):
                if rng.random() < dens: p ^= {(1 << i) | (1 << j)}
        polys.append(frozenset(p))
    return N, polys

rng = random.Random(20261004)
fails = 0; ntest = 0
# hand-checkable system: x1+x2 = 0 ; x1*x2 + x1 = 0 -> x1=x2, x1*x1 + x1 = 0 (always): V={00,11}: count 2 ;  N=2 k=1
polys = [frozenset({1, 2}), frozenset({3, 1})]
p = os.path.join(TMP, 'hand.txt'); write_masks(p, 2, polys)
hb = brute(2, polys)
res = [run('A', p, 0, 1)[0], run('A', p, 1, 1)[0], run('C', p, 0, 1)[0], run('C', p, 1, 1)[0]]
print('hand-checkable: brute', hb, 'counters', res, 'expected 2'); ntest += 1
if not (hb == 2 and all(r == 2 for r in res)): fails += 1
# random bilinear systems, counts around the interesting range (M<=N)
for trial in range(120):
    k = rng.randint(2, 8); N = 2 * k
    M = rng.randint(max(1, N - 6), N + 1)
    N, polys = rand_bilinear(rng, k, M, dens=rng.choice([.1, .3, .5]))
    p = os.path.join(TMP, 'rb.txt'); write_masks(p, N, polys)
    bf = brute(N, polys)
    rs = [run('A', p, 0, k)[0], run('A', p, k, k)[0], run('C', p, 0, k)[0], run('C', p, k, k)[0]]
    ntest += 1
    if any(r != bf for r in rs):
        fails += 1; print('MISMATCH trial', trial, 'k', k, 'M', M, 'brute', bf, rs)
# general (non-bilinear) systems for mode C: E-degree up to 3, Y linear
for trial in range(60):
    N = rng.randint(6, 13); ne = N // 2; M = rng.randint(2, N)
    Ym = ((1 << N) - 1) & ~((1 << ne) - 1)  # E=low bits
    polys = []
    for _ in range(M):
        p_ = set()
        for _ in range(rng.randint(1, 10)):
            d = rng.randint(0, 4); mask = 0
            for _ in range(d): mask |= 1 << rng.randrange(N)
            # keep at most 1 Y var
            ys = [j for j in range(ne, N) if (mask >> j) & 1]
            for j in ys[1:]: mask &= ~(1 << j)
            p_ ^= {mask}
        polys.append(frozenset(p_))
    p = os.path.join(TMP, 'rg.txt'); write_masks(p, N, polys)
    bf = brute(N, polys); r = run('C', p, 0, ne)[0]; ntest += 1
    if r != bf: fails += 1; print('MISMATCH general', trial, bf, r)
print('tests', ntest, 'fails', fails)
sys.exit(1 if fails else 0)
