"""Validator check: sieve, instance validity (I4), labelling (I5), M0 base sizes, per-arm window/p bookkeeping.
Uses only indlib.py (validator-owned)."""
import json, math, random, sys, collections
import numpy as np
from math import comb
from indlib import *

t1 = load('t1')
mem = []
for t in ('t4', 't5', 't6', 't7'):
    mem += load(t)['members']
ctrl = load('t3')['members']
print('members', len(mem), 'ctrl', len(ctrl))

# ---- 1. independent FAM sieve and cell counts
fam = [t for t in range(3, 2601, 2) if is_prime(5 * t * t + 19 * t + 19) and is_prime(5 * t * t + 18 * t + 20)]
rec = [m['t'] for m in t1['inventory']['fam_members']]
print('sieve equal:', fam == rec, 'n_total', len(fam))
cnt = {c: sum(1 for t in fam if CELLS[c][0] < 5 * t * t + 19 * t + 19 <= CELLS[c][1]) for c in CELLS}
print('cell counts mine', cnt, 'recorded', t1['inventory']['counts'])
fam_by_cell = {c: [t for t in fam if CELLS[c][0] < 5 * t * t + 19 * t + 19 <= CELLS[c][1]] for c in CELLS}
for c in CELLS:
    got = sorted(m['t'] for m in mem if m['arm'] == 'FAM' and m['cell'] == c)
    print(' FAM', c, 't list equal sieve:', got == fam_by_cell[c], got)
fam_primes = {5 * t * t + 19 * t + 19 for t in range(3, 2701, 2)}

# ---- 2. instance validity
L = squarefree_list()
bad = []
by_arm_cell = collections.defaultdict(list)
for m in mem + ctrl:
    p, N, A, B, arm, cell = m['p'], m['N'], m['A'], m['B'], m['arm'], m['cell']
    tag = f"{arm}/{cell}/{m['index']}"
    lo, hi = CELLS[cell]
    if arm == 'N-B-ctrl':
        hi = 2 * lo
    ok = {}
    ok['p_prime'] = is_prime(p)
    ok['N_prime'] = is_prime(N)
    ok['hasse'] = (N - p - 1) ** 2 <= 4 * p
    ok['band'] = lo < p <= hi
    ok['N_odd'] = N % 2 == 1
    ok['nonsingular'] = (4 * A ** 3 + 27 * B * B) % p != 0
    rr = random.Random(p * 7919 + N)
    pts = []
    while len(pts) < 3:
        x = rr.randrange(p)
        f = (x ** 3 + A * x + B) % p
        if f and pow(f, (p - 1) // 2, p) == 1:
            pts.append((x, sqrt_mod(f, p)))
    ok['order_kills_3pts'] = all(mul(N, P, A, p) is None for P in pts) and all(P is not None for P in pts)
    # N | #E, N prime, Hasse => #E == N when N > (p+1+2sqrt p)/2
    ok['group_order_is_N'] = N > (p + 1 + 2 * math.isqrt(p) + 1) / 2
    j_num = (1728 * 4 * A ** 3) % p
    j_den = (4 * A ** 3 + 27 * B * B) % p
    jt = (j_num - ((-96 ** 3) % p) * j_den) % p == 0
    if arm in ('FAM', 'N-A'):
        a, b, d = m['a'], m['b'], m['d']
        ok['j_target'] = jt
        ok['trace'] = 4 * p == a * a + 19 * b * b and N == p + 1 - a
        ok['chart'] = (A, B) == (-152 * d * d, 722 * d ** 3)
        # twist rule: d==1 iff [N]P0=O on the d=1 chart at smallest liftable x0; else d = first of L with (d/p) = -1
        A1, B1 = -152, 722
        x0 = 0
        while True:
            f = (x0 ** 3 + A1 * x0 + B1) % p
            if f and pow(f, (p - 1) // 2, p) == 1:
                break
            x0 += 1
        P0 = (x0, sqrt_mod(f, p))
        killed = mul(N, P0, A1, p) is None
        if killed:
            ok['twist_rule'] = d == 1
        else:
            dd = next(c for c in L if legendre(c, p) == -1)
            ok['twist_rule'] = d == dd
        ok['twisted_flag'] = m['twisted'] == (d != 1)
        if arm == 'FAM':
            t = m['t']
            ok['fam_formulas'] = (t % 2 == 1 and p == 5 * t * t + 19 * t + 19 and N == 5 * t * t + 18 * t + 20 and a == t and b == t + 2)
        else:
            ok['na_conditions'] = (b != a + 2 and a % 2 == 1 and b % 2 == 1 and b >= 1 and p not in fam_primes)
            if m['stratum'] == 'theta':
                ok['theta_stratum'] = a > 0 and 0.20 <= a / (2 * math.sqrt(p)) <= 0.25
    else:
        ok['j_not_target'] = not jt
        ok['not_anomalous'] = N != p
        ok['coef_range'] = abs(A) <= 1000 and abs(B) <= 1000
    ok['p_mod_120'] = m['p_mod_120'] == p % 120
    ok['base_size_B'] = m['base_size'] == cube_base(N) and m['T'] == comb(cube_base(N) + 2, 3)
    if not all(ok.values()):
        bad.append((tag, [k for k, v in ok.items() if not v]))
    if arm in ('N-A', 'N-B'):
        by_arm_cell[(arm, cell)].append(p)
    by_arm_cell[('all', arm, cell)].append(p)
print('instance validity failures:', bad)
for k, v in by_arm_cell.items():
    if k[0] != 'all':
        print(' repeated primes in', k, len(v) - len(set(v)))
# ctrl disjoint from N-B of same cell
for cell in CELLS:
    s1 = {(m['p'], m['A'], m['B']) for m in mem if m['arm'] == 'N-B' and m['cell'] == cell}
    s2 = {(m['p'], m['A'], m['B']) for m in ctrl if m['cell'] == cell}
    print(' ctrl/N-B disjoint', cell, not (s1 & s2))
print('arm/cell counts', sorted(collections.Counter((m['arm'], m['cell']) for m in mem + ctrl).items()))
print('mean log2 p per arm/cell:')
for k in sorted(k for k in by_arm_cell if k[0] == 'all'):
    v = by_arm_cell[k]
    print('  ', k[1], k[2], len(v), round(sum(math.log2(x) for x in v) / len(v), 3))

# ---- 3. labelling: [l(Q)] g == Q for ALL base points, labels[0]==1, distinct classes; window W
bad_lab = []
for m in mem + ctrl:
    p, N, A, B = m['p'], m['N'], m['A'], m['B']
    size = m['member_base_size']
    pts, W = small_x_points(A, B, p, size)
    lab = m['labels']
    g = pts[0]
    okl = (len(lab) == size and lab[0] == 1 and W == m['window_W'] and W < p
           and len({min(x, N - x) for x in lab}) == size
           and all(mul(l, g, A, p) == Q for l, Q in zip(lab, pts)))
    if not okl:
        bad_lab.append((m['arm'], m['cell'], m['index']))
print('labelling failures (my [l]g==Q on every base point, B or B+1 per member):', bad_lab, 'checked', len(mem + ctrl))
print('M0 recorded loop/hist failures:', sum(m['m0']['loop_failures'] + m['m0']['hist_failures'] for m in mem + ctrl))
print('random_distinct_failures:', sum(m['random_distinct_failures'] for m in mem + ctrl), 'n random bases per member:', collections.Counter(len(m['random_seen']) for m in mem + ctrl))
