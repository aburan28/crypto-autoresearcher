import sys, time
from math import comb
from indlib import *
shard, nshard = int(sys.argv[1]), int(sys.argv[2])
mem = []
for t in ('t3', 't5', 't6', 't7'):
    mem += load(t)['members']
items = sorted([m for m in mem if m['cell'] == 'C24'], key=lambda m: (m['arm'], m['index']))
items = [m for i, m in enumerate(items) if i % nshard == shard]
bad = n = 0
t0 = time.time()
for m in items:
    N = m['N']; B = cube_base(N)
    c, e = cov_prefix_scatter(m['labels'], N); n += 1
    if c != m['member_seen'] or e != comb(m['member_base_size'] + 2, 3): bad += 1
    for k in range(1, 201):
        c, e = cov_prefix_scatter(rand_labels(N, B, m['cell'], m['arm'], m['index'], k + 1), N)
        n += 1
        if c != m['random_seen'][k - 1] or e != comb(B + 2, 3):
            bad += 1
print(f'shard {shard}: items {len(items)} bases recounted {n} mismatches {bad} secs {time.time()-t0:.0f}', flush=True)
