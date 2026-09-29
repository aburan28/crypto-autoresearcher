import json, time, sys
sys.path.insert(0, '.')
from twist_family_local import profile, DEFAULT_SUPPORT

POOL_PATH = '/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/pool.json'
pool = json.load(open(POOL_PATH))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
t0 = time.time()
for i, c in enumerate(pool[:n]):
    ai = c['ai']
    (A, B), prof = profile(ai, DEFAULT_SUPPORT, 3)
    cert = [e['certified'] for e in prof]
    print(i, ai, 'sum_cert=%d max_cert=%d n_timeout=%d elapsed=%.1fs' % (
        sum(cert), max(cert), sum(1 for e in prof if e['timed_out']), time.time() - t0))
print('TOTAL %.1fs for %d curves -> %.2fs/curve, projected 507 curves = %.0fs' % (
    time.time() - t0, n, (time.time() - t0) / n, (time.time() - t0) / n * 507))
