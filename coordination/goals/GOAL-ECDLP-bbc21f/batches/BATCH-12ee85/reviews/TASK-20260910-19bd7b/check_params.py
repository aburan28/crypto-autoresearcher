import sys, time
sys.path.insert(0, 'coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/TASK-20260910-19bd7b')
import rederive as R
import numpy as np

a = np.arange(10000, dtype=np.uint64)
assert all(R.mix64_arr(a)[i] == R.mix64(int(a[i])) for i in range(10000))
print('mix64 vector==scalar: OK')

rows = [(1 << 20, 64, 1, 16, 256), (1 << 20, 64, 1, 8, 363),
        (1 << 20, 64, 3, 16, 444), (1 << 20, 64, 1, 4, 512),
        (1 << 24, 256, 1, 16, 512), (1 << 24, 256, 1, 8, 725),
        (1 << 24, 256, 3, 16, 887), (1 << 24, 256, 1, 4, 1024)]
for (N, T, an, ad, exp_cap) in rows:
    d, c, ws, wf = R.exact_params(N, T, an, ad)
    print(N, f'{an}/{ad}', 'cap', c, 'expect', exp_cap,
          'OK' if c == exp_cap else 'MISMATCH', 'W', repr(wf))

t = time.perf_counter()
K = R.mix64(0x9E3779B97F4A7C15 + 1)
Kd = R.mix64(K ^ 0xD1B54A32D192ED03)
f, dm = R.build_graph(1 << 20, K, Kd, R.exact_params(1 << 20, 64, 1, 4)[0])
p = R.exact_partition(1 << 20, f, dm, 512)
print('N=2^20 partition time', round(time.perf_counter() - t, 2), 's;',
      'n_dps', p['n_dps'], 'cyc', p['cycle_mass'], 'capd', p['capped_mass'],
      'id', p['identity'], 'minb', p['min_basin_size'])
