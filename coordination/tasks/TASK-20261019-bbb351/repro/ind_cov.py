"""Validator recomputation of the m=3 coverage (and the M0 identity) from the recorded labels / regenerated
random bases. Usage: ind_cov.py <cell> <n_random>  (n_random = how many of the 200 random bases to redo)"""
import sys, time, json, collections
import numpy as np
from math import comb
from indlib import *

cell_sel = sys.argv[1]
n_rand = int(sys.argv[2])
hist_all = len(sys.argv) > 3 and sys.argv[3] == 'hist'
mem = []
for t in ('t4', 't5', 't6', 't7'):
    mem += load(t)['members']
ctrl = load('t3')['members']
items = [m for m in mem + ctrl if m['cell'] == cell_sel]
print('cell', cell_sel, 'items', len(items), 'random bases redone per item', n_rand)
t0 = time.time()
n_checked = n_bad = n_enum_bad = n_fft = n_fft_bad = 0
bad = []
hist_bad = []
n_hist = 0
for m in items:
    N = m['N']
    B = cube_base(N)
    size = m['member_base_size']
    labs = m['labels']
    # member (or planted) base
    c, e = cov_prefix_scatter(labs, N)
    n_checked += 1
    if e != comb(size + 2, 3):
        n_enum_bad += 1
    if c != m['member_seen']:
        n_bad += 1
        bad.append((m['arm'], m['index'], 'member', c, m['member_seen']))
    if cell_sel == 'C16' or m['index'] % 4 == 0:
        c2 = cov_fft_support(labs, N)
        n_fft += 1
        if c2 != m['member_seen']:
            n_fft_bad += 1
            bad.append((m['arm'], m['index'], 'member-fft', c2, m['member_seen']))
    for k in range(1, n_rand + 1):
        lb = rand_labels(N, B, m['cell'], m['arm'], m['index'], k + 1)
        c, e = cov_prefix_scatter(lb, N)
        n_checked += 1
        if e != comb(B + 2, 3):
            n_enum_bad += 1
        if c != m['random_seen'][k - 1]:
            n_bad += 1
            bad.append((m['arm'], m['index'], f'rand{k}', c, m['random_seen'][k - 1]))
        if cell_sel == 'C16' and k <= 20:
            c2 = cov_fft_support(lb, N)
            n_fft += 1
            if c2 != m['random_seen'][k - 1]:
                n_fft_bad += 1
                bad.append((m['arm'], m['index'], f'rand{k}-fft', c2, m['random_seen'][k - 1]))
    # recorded full-histogram records vs my own bincount histogram (member, rand1, rand2)
    if m['hist'] and (hist_all or cell_sel == 'C16'):
        for h in m['hist']:
            if h['base'] == 'member':
                lb, T = labs, comb(size + 2, 3)
            else:
                k = int(h['base'][-1])
                lb, T = rand_labels(N, B, m['cell'], m['arm'], m['index'], k + 1), comb(B + 2, 3)
            tot, nz, coll, mx = histogram_stats(lb, N)
            n_hist += 1
            if (tot, nz, coll, mx) != (h['total'], h['nonzero'], h['collisions'], h['max_c']) or tot != T:
                hist_bad.append((m['arm'], m['index'], h['base'], (tot, nz, coll, mx), (h['total'], h['nonzero'], h['collisions'], h['max_c'])))
print('bases recounted', n_checked, 'coverage mismatches', n_bad, 'enumeration-count != comb(B+2,3):', n_enum_bad)
print('fft-support recounts', n_fft, 'mismatches', n_fft_bad)
print('full histograms recomputed', n_hist, 'mismatches (total,nonzero,collisions,max_c) or total != binom:', len(hist_bad))
print('mismatch detail:', bad[:10], hist_bad[:5])
print('secs', round(time.time() - t0, 1))
