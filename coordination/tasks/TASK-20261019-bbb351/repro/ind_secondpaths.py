"""Run the producer's second code paths (count.coverage_by_set / coverage_by_sort) and primary count_coverage on
every C16 base (member + random bases 1..3 of all 28 C16 items) and compare with the recorded coverages."""
import sys, time
sys.path.insert(0, '/home/user/crypto-autoresearcher/experiments/EXP-CMFB-cea1d2/implementation'); sys.path.insert(0, '.')
import count
from indlib import *
mem = []
for t in ('t4', 't5', 't6', 't7'): mem += load(t)['members']
ctrl = load('t3')['members']
items = [m for m in mem + ctrl if m['cell'] == 'C16']
nset = bad = 0
for m in items:
    N = m['N']; B = count.base_size(N)
    bases = [('member', m['labels'], m['member_seen'])] + [(f'rand{k}', rand_labels(N, B, m['cell'], m['arm'], m['index'], k + 1), m['random_seen'][k - 1]) for k in (1, 2, 3)]
    for name, lb, rec in bases:
        s = count.coverage_by_set(lb, N); so = count.coverage_by_sort(lb, N); pr, en = count.count_coverage(lb, N); nset += 1
        if not (s == so == pr == rec): bad += 1
print('C16 items', len(items), 'bases', nset, 'coverage_by_set == coverage_by_sort == count_coverage == recorded: mismatches', bad)
